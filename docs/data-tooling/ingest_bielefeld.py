#!/usr/bin/env python3
"""
Ingest-Skript für die Bielefelder Philharmoniker, Spielzeit 2026/27.

Quelle:  Kalender  https://www.buo-bielefeld.de/philharmoniker/kalender  (TYPO3,
         server-gerendert, „Mehr laden"-Paging über tx_uibuoproductions_calendar)
         Detail    https://www.buo-bielefeld.de/<venue>/veranstaltung/<slug>

Vorgehen:
  1. Kalender durchpagen (der „Mehr laden"-Link trägt den jeweils gültigen cHash) und alle
     Termine sammeln: Datum, Uhrzeit, Ort, Ticket-URL (Eventim-Inhouse), Detail-Pfad, Sparte.
  2. Nur Orchesterkonzerte behalten – Detailpfad unter /philharmoniker/ oder
     /rudolf-oetker-halle/. Szenische Produktionen (Oper/Ballett/Musiktheater unter /theater/,
     z. B. Tosca, Die Zauberflöte, The Birds) werden ausgelassen.
  3. Je Produktion die Detailseite laden → Programm (aus `<meta itemprop="description">`,
     Format „Komponist (Lebensdaten)Werk", zeilenweise) und Besetzung (aus den /person/-Links
     im Abschnitt „Auf der Bühne"). Programm wird in `program[].workId` normalisiert.

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host buo-bielefeld.de und
Ensemble bielefelder-philharmoniker und legt sie neu an; Stammdaten werden dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_bielefeld.py
"""

import json
import re
import sys
import time
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = "https://www.buo-bielefeld.de"
CALENDAR = f"{BASE}/philharmoniker/kalender"
SOURCE_HOST = "buo-bielefeld.de"
SOURCE_NAME = "Bielefelder Philharmoniker / Theater Bielefeld"
ENSEMBLE_ID = "bielefelder-philharmoniker"
CITY_ID = "bielefeld"
RETRIEVED_AT = "2026-08-18"
SEASON_START, SEASON_END = "2026-08-01", "2027-08-31"

# Nur diese Detailpfad-Präfixe sind Orchesterkonzerte (kein szenisches /theater/).
INCLUDE_PREFIXES = ("/philharmoniker/", "/rudolf-oetker-halle/")

# Spielstätten: Teilstring (lower) des Kalender-Orts → Venue-Datensatz.
BIELEFELD_VENUES: List[Tuple[str, Dict[str, Any]]] = [
    ("rudolf-oetker-halle", {"id": "rudolf-oetker-halle-bielefeld", "name": "Rudolf-Oetker-Halle Bielefeld", "type": "concert_hall"}),
    ("stadttheater", {"id": "stadttheater-buehne-bielefeld", "name": "Stadttheater Bielefeld", "type": "theatre"}),
    ("assapheum", {"id": "assapheum-bethel-bielefeld", "name": "Assapheum (Bethel) Bielefeld", "type": "other"}),
    ("universität", {"id": "universitaet-bielefeld", "name": "Universität Bielefeld (Audimax)", "type": "other"}),
    ("audimax", {"id": "universitaet-bielefeld", "name": "Universität Bielefeld (Audimax)", "type": "other"}),
    ("zionskirche", {"id": "zionskirche-bethel-bielefeld", "name": "Zionskirche Bethel Bielefeld", "type": "other"}),
]
FALLBACK_VENUE = {"id": "bielefeld-umgebung", "name": "Bielefeld und Umgebung", "type": "other"}

CONDUCTOR_ROLE_HINTS = ("leitung", "dirigent", "dirigentin", "musikalische leitung")
SOLOIST_ROLE_HINTS = ("violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel",
                      "cembalo", "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete",
                      "posaune", "tuba", "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion",
                      "sopran", "mezzosopran", "countertenor", "alt", "tenor", "bariton", "bass",
                      "gesang", "akkordeon", "moderation", "sprecher", "rezitation")
SKIP_ROLE_HINTS = ("orchester", "chor", "ensemble", "philharmoniker")


def http_get(url: str, ajax: bool = False) -> Optional[str]:
    headers = {"User-Agent": "Mozilla/5.0"}
    if ajax:
        headers["X-Requested-With"] = "XMLHttpRequest"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  ! Fehler {url}: {e}")
        return None


def strip_html(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(t))).strip()


# --- Kalender-Pass ----------------------------------------------------------

def collect_calendar() -> List[Dict[str, Any]]:
    seen = set()
    items: List[Dict[str, Any]] = []
    url: Optional[str] = CALENDAR
    pages = 0
    while url and pages < 40:
        s = http_get(url, ajax=(pages > 0))
        if not s:
            break
        pages += 1
        starts = [m.start() for m in re.finditer(r"data-calender-result-item", s)]
        starts.append(len(s))
        for i in range(len(starts) - 1):
            b = s[starts[i]:starts[i + 1]]
            det = re.search(r'href="(/[^"]*/veranstaltung/[^"]+)"', b)
            if not det or not det.group(1).startswith(INCLUDE_PREFIXES):
                continue
            date = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", b)
            tm = re.search(r"(\d{1,2}:\d{2})", b)
            tk = re.search(r"(https://theater-bielefeld\.eventim-inhouse\.de/webshop/webticket/shop\?event=\d+)", b)
            title = re.search(r'/veranstaltung/[^"]+"\s*>\s*<p>([^<]+)</p>', b)
            ven = re.search(r'text-accent-color font-bold">\s*(.*?)</p>', b, re.DOTALL)
            if not date:
                continue
            iso = f"{date.group(3)}-{date.group(2)}-{date.group(1)}"
            time_str = tm.group(1) if tm else None
            key = (det.group(1), iso, time_str)
            if key in seen:
                continue
            seen.add(key)
            items.append({
                "detail": det.group(1),
                "slug": det.group(1).rsplit("/", 1)[-1],
                "date": iso,
                "time": time_str,
                "ticket": tk.group(1) if tk else None,
                "title": strip_html(title.group(1)) if title else "",
                "venue": strip_html(ven.group(1)) if ven else "",
            })
        m = re.search(r'title="Mehr laden"[^>]*href="([^"]+)"', s)
        url = BASE + unescape(m.group(1)) if m else None
        time.sleep(0.15)
    return items


# --- Detail-Pass: Programm (Meta) + Besetzung (Personenlinks) --------------

def parse_program(detail_html: str) -> List[Tuple[str, str]]:
    m = re.search(r'<meta\s+itemprop="description"\s+content="([\s\S]*?)"', detail_html)
    if not m:
        return []
    desc = unescape(m.group(1))
    pairs: List[Tuple[str, str]] = []
    for line in desc.split("\n"):
        line = line.replace("\xa0", " ").strip()
        if not line:
            break  # Leerzeile → danach beginnt der Fließtext
        mm = re.match(r"^(.+?)\s*\(\*?\d{4}(?:\s*[–\-]\s*\d{4})?\)\s*(.+)$", line)
        if not mm:
            break
        comp = mm.group(1).strip(" ,;")
        work = mm.group(2).strip(" ,;")
        if comp and work:
            pairs.append((comp, work))
    return pairs


def title_program(title: str, surname_index: Dict[str, str]) -> List[Tuple[str, str]]:
    """Programm aus Titeln der Form „Komponist – Werk" ableiten (nur bekannte Komponist:innen)."""
    parts = re.split(r"\s[–-]\s", title, 1)
    if len(parts) != 2:
        return []
    comp_part, work = parts[0].strip(), parts[1].strip()
    key = "".join(FOLD.get(c, c) for c in comp_part.split()[-1].lower()) if comp_part.split() else ""
    full_name = surname_index.get(key)
    if not full_name or len(work) < 3 or not work[:1].isupper():
        return []
    return [(full_name, work)]


def parse_cast(detail_html: str) -> Tuple[List[str], List[str]]:
    a = detail_html.find("Auf der Bühne")
    if a < 0:
        return [], []
    b = detail_html.find("Das Team", a)
    seg = detail_html[a: b if b > a else a + 6000]
    cond: List[str] = []
    sol: List[str] = []
    for href, inner in re.findall(r'<a[^>]*href="(/person/[^"]+)"[^>]*>(.*?)</a>', seg, re.DOTALL):
        text = strip_html(inner)
        if not text:
            continue
        low = text.lower()
        # erste Rollenangabe finden (Rollen stehen kleingeschrieben am Ende)
        best = None
        for r in CONDUCTOR_ROLE_HINTS + SOLOIST_ROLE_HINTS + SKIP_ROLE_HINTS:
            mm = re.search(rf"\b{re.escape(r)}\b", low)
            if mm and (best is None or mm.start() < best[0]):
                best = (mm.start(), r)
        if not best or best[0] == 0:
            continue
        name = text[:best[0]].strip(" ,;:-")
        role = text[best[0]:].strip()
        if not name or len(name) < 3:
            continue
        if any(re.search(rf"\b{re.escape(h)}\b", role) for h in SKIP_ROLE_HINTS):
            continue
        if any(re.search(rf"\b{re.escape(h)}\b", role) for h in CONDUCTOR_ROLE_HINTS):
            cond.append(name)
        elif any(re.search(rf"\b{re.escape(h)}\b", role) for h in SOLOIST_ROLE_HINTS):
            sol.append(name)
    return list(dict.fromkeys(cond)), list(dict.fromkeys(sol))


# --- Normalisierung (wie Bochum/Dortmund/Bonn) ------------------------------

FOLD = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a", "ç": "c", "č": "c", "ć": "c",
        "è": "e", "é": "e", "ê": "e", "ë": "e", "ì": "i", "í": "i", "î": "i", "ï": "i",
        "ñ": "n", "ń": "n", "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ø": "oe",
        "ù": "u", "ú": "u", "û": "u", "š": "s", "ś": "s", "ž": "z", "ź": "z", "ż": "z",
        "ł": "l", "đ": "d", "ð": "d", "þ": "th", "ř": "r", "ě": "e", "ā": "a", "ē": "e",
        "ī": "i", "ō": "o", "ū": "u"}
COMPOSER_ALIAS = {"sergei rachmaninow": "sergej-rachmaninow", "sergei prokofjew": "sergej-prokofjew",
                  "igor strawinski": "igor-strawinsky", "antonin dvorak": "antonin-dvorak"}
WORK_KEYWORDS = ("sinfonie", "symphonie", "sinfonia", "konzert", "ouvertüre", "ouverture", "vorspiel",
                 "suite", "streichquartett", "quartett", "quintett", "sextett", "trio", "sonate",
                 "fantasie", "variationen", "rhapsodie", "serenade", "messe", "requiem", "oratorium",
                 "ballett", "walzer", "divertimento", "poem", "lied", "kantate")


def _fold(s: str) -> str:
    return "".join(FOLD.get(c, c) for c in s)


def slugify(name: str) -> str:
    s = "".join(c if (c.isalnum() or c == " ") else " " for c in _fold(name.strip().lower()))
    return re.sub(r"\s+", "-", s.strip())


def clean_composer_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\s*\((Sohn|Vater)\)", "", name)).strip(" ,;:")


def infer_genre(title: str) -> str:
    t = title.lower()
    if "requiem" in t:
        return "requiem"
    if any(k in t for k in ("oratorium", "messe", "messa", "passion", "te deum", "gloria", "kantate")):
        return "oratorio"
    if any(k in t for k in ("streichquartett", "quartett", "quintett", "sextett", "streichtrio",
                            "klaviertrio", "trio", "sonate", "kammer", "oktett")):
        return "chamber_music"
    if any(k in t for k in ("sinfonie", "symphonie", "sinfonia")):
        return "symphony"
    if any(k in t for k in ("konzert für", "klavierkonzert", "violinkonzert", "cellokonzert",
                            "violoncello und orchester", "concerto", "doppelkonzert")):
        return "concerto"
    if any(k in t for k in ("ouvertüre", "ouverture", "vorspiel", "overture")):
        return "overture"
    if "oper" in t and not any(k in t for k in ("aus der oper", "aus dem", "interlud", "auszug", "auszüge", "suite", "arie")):
        return "opera"
    return "other"


_CAT_PATTERNS = [("Opus", r"\bop(?:us|\.)\s*(?:posth\.?\s*)?([\d]+[a-z]?(?:\s*Nr\.?\s*\d+)?)"),
                 ("KV", r"\bKV\.?\s*([\d./a-z]+)"), ("BWV", r"\bBWV\.?\s*([\d./a-z]+)"),
                 ("WoO", r"\bWoO\.?\s*([\d]+)"), ("Hob", r"\bHob\.?\s*([\dIVXLC:.]+)"),
                 ("D", r"\bD\.?\s*(\d{2,4})")]


def parse_catalogue(title: str) -> Tuple[List[Dict[str, str]], str]:
    cat: List[Dict[str, str]] = []
    cleaned = title
    for system, pat in _CAT_PATTERNS:
        m = re.search(pat, cleaned)
        if m:
            cat.append({"system": system, "number": m.group(1).strip()})
            cleaned = (cleaned[: m.start()] + cleaned[m.end():]).strip(" ,;")
    return cat, re.sub(r"\s+", " ", cleaned).strip(" ,;")


def norm_title(title: str) -> str:
    t = _fold(title.lower()).replace("symphonie", "sinfonie")
    t = re.sub(r"\bop(?:us|\.)?\s*[\dA-Za-z/]+", "", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, d: Dict[str, Any]) -> None:
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_venue(label: str) -> Dict[str, Any]:
    low = label.lower()
    for key, spec in BIELEFELD_VENUES:
        if key in low:
            return spec
    return FALLBACK_VENUE


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    print("=== Bielefelder Philharmoniker – Ingest 2026/27 ===\n")
    print("1. Kalender laden ...")
    items = collect_calendar()
    slugs = sorted({it["detail"] for it in items})
    print(f"   {len(items)} Konzert-Aufführungen, {len(slugs)} Produktionen")

    events_doc = load(data / "events.json")
    venues_doc = load(data / "venues.json")
    people_doc = load(data / "people.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")

    venue_ids = {v["id"] for v in venues_doc["venues"]}

    def ensure_venue(label: str) -> str:
        spec = resolve_venue(label)
        vid = spec["id"]
        if vid not in venue_ids:
            venues_doc["venues"].append({
                "id": vid, "name": spec["name"], "cityIds": [CITY_ID], "region": None,
                "address": None, "coordinates": None, "website": None,
                "type": spec.get("type", "other"), "institutionId": None,
            })
            venue_ids.add(vid)
        return vid

    person_ids = {p["id"] for p in people_doc["people"]}

    def ensure_person(name: str) -> Optional[str]:
        clean = re.sub(r"\s+", " ", name).strip(" ,;:.-")
        if not clean or len(clean) < 3:
            return None
        pid = slugify(clean)
        if pid and pid not in person_ids:
            people_doc["people"].append({"id": pid, "name": clean})
            person_ids.add(pid)
        return pid or None

    composer_ids = {c["id"] for c in composers_doc["composers"]}
    composer_by_norm = {_fold(c["name"].lower()): c["id"] for c in composers_doc["composers"]}

    def ensure_composer(name: str) -> Optional[str]:
        clean = clean_composer_name(name)
        if not clean:
            return None
        if clean.lower() in COMPOSER_ALIAS:
            return COMPOSER_ALIAS[clean.lower()]
        key = _fold(clean.lower())
        if key in composer_by_norm:
            return composer_by_norm[key]
        cid = slugify(clean)
        if cid not in composer_ids:
            composers_doc["composers"].append({"id": cid, "name": clean, "life": None})
            composer_ids.add(cid)
        composer_by_norm[key] = cid
        return cid

    work_ids = {w["id"] for w in works_doc["works"]}
    work_by_key = {(w["composerId"], norm_title(w["title"])): w["id"] for w in works_doc["works"]}

    def resolve_work(comp_name: str, raw_title: str) -> Optional[str]:
        cid = ensure_composer(comp_name)
        title = re.sub(r"\s+", " ", raw_title).strip(" ,;")
        if not cid or not title:
            return None
        catalogue, cleaned = parse_catalogue(title)
        cleaned = cleaned or title
        key = (cid, norm_title(cleaned))
        if key in work_by_key:
            return work_by_key[key]
        stem = cid.split("-")[-1]
        slug = re.sub(r"[^a-z0-9]+", "-", norm_title(cleaned)).strip("-")[:40]
        wid = f"{stem}-{slug}" if slug else stem
        base, n = wid, 2
        while wid in work_ids and work_by_key.get(key) != wid:
            wid = f"{base}-{n}"; n += 1
        if wid not in work_ids:
            works_doc["works"].append({
                "id": wid, "composerId": cid, "title": cleaned, "catalogue": catalogue,
                "yearComposed": None, "genre": infer_genre(cleaned), "durationMinutes": None,
                "version": None, "scoring": None, "description": None,
            })
            work_ids.add(wid)
        work_by_key[key] = wid
        return wid

    # Nachnamen → kanonischer Komponistenname (kürzeste Namensvariante), für Titel-Ableitung.
    surname_index: Dict[str, str] = {}
    for c in composers_doc["composers"]:
        parts = c["name"].split()
        if not parts:
            continue
        key = _fold(parts[-1].lower())
        if key not in surname_index or len(parts) < len(surname_index[key].split()):
            surname_index[key] = c["name"]
    detail_title = {it["detail"]: it["title"] for it in items}

    print("\n2. Detailseiten (Programm/Besetzung) ...")
    detail_cache: Dict[str, Dict[str, Any]] = {}
    for i, detail in enumerate(slugs, 1):
        html_text = http_get(BASE + detail)
        if not html_text:
            detail_cache[detail] = {"program": [], "conductors": [], "soloists": []}
            continue
        pairs = parse_program(html_text)
        if not pairs:  # Fallback: Programm aus „Komponist – Werk"-Titel ableiten
            pairs = title_program(detail_title.get(detail, ""), surname_index)
        cond, sol = parse_cast(html_text)
        prog = []
        for comp, title in pairs:
            wid = resolve_work(comp, title)
            if wid:
                prog.append({"workId": wid})
        detail_cache[detail] = {
            "program": prog,
            "conductors": [pid for pid in (ensure_person(n) for n in cond) if pid],
            "soloists": [pid for pid in (ensure_person(n) for n in sol) if pid],
        }
        if i % 10 == 0:
            print(f"   [{i}/{len(slugs)}] ...")
        time.sleep(0.1)

    print("\n3. Events bauen ...")
    new_events: List[Dict[str, Any]] = []
    for it in items:
        if not (SEASON_START <= it["date"] <= SEASON_END):
            continue
        info = detail_cache.get(it["detail"], {})
        vid = ensure_venue(it["venue"])
        short = re.sub(r"[^a-z0-9]+", "-", it["slug"].lower()).strip("-")[:34]
        eid = f"event-{it['date']}-bielefeld-{short}"
        if it["time"]:
            eid = f"{eid}-{it['time'].replace(':', '')}"
        new_events.append({
            "id": eid, "title": it["title"], "eventType": "concert", "date": it["date"],
            "startTime": it["time"], "endTime": None, "status": "scheduled",
            "ensembleIds": [ENSEMBLE_ID], "venueId": vid, "cityId": CITY_ID,
            "conductorPersonIds": info.get("conductors", []),
            "soloistPersonIds": info.get("soloists", []),
            "program": info.get("program", []), "seriesId": None, "description": None,
            "source": {"url": BASE + it["detail"], "calendarUrl": CALENDAR, "name": SOURCE_NAME, "retrievedAt": RETRIEVED_AT},
            "ticketUrl": it["ticket"], "lastVerified": RETRIEVED_AT,
        })

    seen: Dict[str, int] = {}
    for e in new_events:
        if e["id"] in seen:
            seen[e["id"]] += 1
            e["id"] = f"{e['id']}-{seen[e['id']]}"
        else:
            seen[e["id"]] = 1

    def is_ours(e: Dict[str, Any]) -> bool:
        src = (e.get("source") or {}).get("url", "") or ""
        return SOURCE_HOST in src and ENSEMBLE_ID in e.get("ensembleIds", [])

    before = len(events_doc["events"])
    events_doc["events"] = [e for e in events_doc["events"] if not is_ours(e)]
    print(f"   Alte Bielefeld-Events entfernt: {before - len(events_doc['events'])}")
    events_doc["events"].extend(new_events)
    events_doc.setdefault("metadata", {})["lastUpdated"] = RETRIEVED_AT

    save(data / "events.json", events_doc)
    save(data / "venues.json", venues_doc)
    save(data / "people.json", people_doc)
    save(data / "composers.json", composers_doc)
    save(data / "works.json", works_doc)

    prog_ev = sum(1 for e in new_events if e["program"])
    tix = sum(1 for e in new_events if e["ticketUrl"])
    print(f"\n✓ Ingest abgeschlossen: {len(new_events)} Events ({prog_ev} mit Programm, {tix} mit Ticket), "
          f"{len(works_doc['works'])} Werke, {len(composers_doc['composers'])} Komponist:innen gesamt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
