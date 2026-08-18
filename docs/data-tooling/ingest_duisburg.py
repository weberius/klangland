#!/usr/bin/env python3
"""
Ingest-Skript für die Duisburger Philharmoniker, Spielzeit 2026/27.

Quelle:  Kalender  https://duisburger-philharmoniker.de/konzertkalender/  (WordPress)
         Detail    https://duisburger-philharmoniker.de/Konzerte/<slug>/

Vorgehen:
  1. Kalenderseite parsen → alle Konzert-Detail-Slugs.
  2. Je Detailseite: Titel, Kategorie, Besetzung (`p.dpInterpreten`), Programm (`div.dpWerke`,
     Format <strong>Komponist</strong><br>Werk), Termine (`dpInfos`), Beginn/Ort (konzertInfos),
     Ticket-Links (`a.kartenLink` → Eventim, mit Wochentag-Label je Aufführung).
  3. Nur Konzerte behalten, bei denen die **Duisburger Philharmoniker** (bzw. deren Mitglieder)
     auftreten (Besetzung enthält „Duisburger Philharmoniker"). Gast-Recitals/Fremdveranstaltungen
     (viele Kammerkonzerte, Orgel-Recitals u. Ä.) werden ausgelassen.
  4. Programm wird in `program[].workId` normalisiert.

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host duisburger-philharmoniker.de
und Ensemble duisburger-philharmoniker und legt sie neu an; Stammdaten werden dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_duisburg.py
"""

import json
import re
import sys
import time
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = "https://duisburger-philharmoniker.de"
CALENDAR = f"{BASE}/konzertkalender/"
DETAIL_BASE = f"{BASE}/Konzerte/"
SOURCE_HOST = "duisburger-philharmoniker.de"
SOURCE_NAME = "Duisburger Philharmoniker"
ENSEMBLE_ID = "duisburger-philharmoniker"
CITY_ID = "duisburg"
RETRIEVED_AT = "2026-08-18"
SEASON_START, SEASON_END = "2026-08-01", "2027-08-31"

MONTHS = {"januar": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5, "juni": 6,
          "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12}
WEEKDAYS = ("mo", "di", "mi", "do", "fr", "sa", "so")

# Duisburger Spielstätten: Teilstring (lower) → Venue-Datensatz. Alle liegen in Duisburg.
DUISBURG_VENUES: List[Tuple[str, Dict[str, Any]]] = [
    ("mercatorhalle", {"id": "mercatorhalle-duisburg", "name": "Philharmonie Mercatorhalle Duisburg", "type": "concert_hall"}),
    ("theater duisburg", {"id": "theater-duisburg", "name": "Theater Duisburg", "type": "opera_house"}),
    ("küppersmühle", {"id": "kueppersmuehle-duisburg", "name": "Museum Küppersmühle Duisburg", "type": "other"}),
    ("kueppersmühle", {"id": "kueppersmuehle-duisburg", "name": "Museum Küppersmühle Duisburg", "type": "other"}),
    ("lehmbruck", {"id": "lehmbruck-museum-duisburg", "name": "Lehmbruck-Museum Duisburg", "type": "other"}),
    ("landschaftspark", {"id": "landschaftspark-duisburg-nord", "name": "Landschaftspark Duisburg-Nord", "type": "other"}),
    ("salvatorkirche", {"id": "salvatorkirche-duisburg", "name": "Salvatorkirche Duisburg", "type": "other"}),
    ("wambachsee", {"id": "naturwerkstatt-wambachsee-duisburg", "name": "Naturwerkstatt am Forsthaus Wambachsee (Duisburg)", "type": "other"}),
    ("forsthaus wambach", {"id": "naturwerkstatt-wambachsee-duisburg", "name": "Naturwerkstatt am Forsthaus Wambachsee (Duisburg)", "type": "other"}),
]

CONDUCTOR_ROLE_HINTS = ("dirigent", "dirigentin", "leitung", "musikalische leitung")
SOLOIST_ROLE_HINTS = ("violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel",
                      "cembalo", "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete",
                      "posaune", "tuba", "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion",
                      "sopran", "mezzosopran", "countertenor", "alt", "tenor", "bariton", "bass",
                      "gesang", "akkordeon", "moderation", "sprecher", "rezitation", "violine solo")


def http_get(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  ! Fehler {url}: {e}")
        return None


def strip_html(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(t))).strip()


def collect_slugs() -> List[str]:
    s = http_get(CALENDAR)
    if not s:
        return []
    return sorted(set(re.findall(r"https://duisburger-philharmoniker\.de/Konzerte/([^\"/]+)/", s)))


# --- Detail-Parsing ---------------------------------------------------------

def _block(html: str, cls: str) -> str:
    m = re.search(r'class=["\'][^"\']*' + cls + r'[^"\']*["\'][^>]*>(.*?)</div>', html, re.DOTALL)
    return m.group(1) if m else ""


def parse_dates(dpinfos: str) -> List[Tuple[str, str]]:
    """'Mi. 25. / Do. 26. November 2026' → [('2026-11-25','Mi'), ('2026-11-26','Do')]."""
    text = strip_html(dpinfos)
    mmonth = re.search(r"([A-Za-zäöü]+)\s+(\d{4})", text)
    if not mmonth:
        return []
    month = MONTHS.get(mmonth.group(1).lower())
    year = int(mmonth.group(2))
    if not month:
        return []
    out: List[Tuple[str, str]] = []
    for m in re.finditer(r"(Mo|Di|Mi|Do|Fr|Sa|So)\.?\s*(\d{1,2})\.", text):
        wd, day = m.group(1), int(m.group(2))
        out.append((f"{year:04d}-{month:02d}-{day:02d}", wd))
    return out


def parse_cast(cast_html: str) -> Tuple[bool, List[str], List[str]]:
    orchestra = False
    cond: List[str] = []
    sol: List[str] = []
    for p in re.findall(r'<p[^>]*class=["\'][^"\']*dpInterpreten[^"\']*["\'][^>]*>(.*?)</p>', cast_html, re.DOTALL):
        sm = re.search(r"<strong>(.*?)</strong>", p, re.DOTALL)
        name = strip_html(sm.group(1)) if sm else ""
        role = strip_html(re.sub(r"<strong>.*?</strong>", "", p, count=1, flags=re.DOTALL))
        low = name.lower()
        if "philharmoniker" in low or "orchester" in low:
            orchestra = True
            continue
        if not name or len(name) < 3 or not role:
            continue
        rl = role.lower()
        if any(h in rl for h in CONDUCTOR_ROLE_HINTS):
            cond.append(name)
        elif any(h in rl for h in SOLOIST_ROLE_HINTS):
            sol.append(name)
    return orchestra, list(dict.fromkeys(cond)), list(dict.fromkeys(sol))


def parse_program(werke_html: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    current: Optional[str] = None
    for seg in re.split(r"<br\s*/?>", werke_html):
        is_comp = "<strong>" in seg
        text = strip_html(seg)
        if not text:
            continue
        if is_comp:
            current = text
        elif current:
            pairs.append((current, text.strip(" „“”\"")))
    return pairs


def parse_detail(html: str) -> Dict[str, Any]:
    title = strip_html(_block(html, "dpKonzert") .split("</h1>")[0]) or strip_html(_block(html, "dpKonzert"))
    m = re.search(r"dpKonzert[^>]*>\s*<h1>(.*?)</h1>", html, re.DOTALL)
    if m:
        title = strip_html(m.group(1))
    cast_region = ""
    cm = re.search(r'class="post-descr dpKonzert">(.*?)<div class="[^"]*dpWerke', html, re.DOTALL)
    if cm:
        cast_region = cm.group(1)
    orchestra, cond, sol = parse_cast(cast_region)
    werke_block = _block(html, "dpWerke")
    program = parse_program(werke_block)
    werke_text = strip_html(werke_block)
    dates = parse_dates(_block(html, "dpInfos"))
    tm = re.search(r"Beginn:\s*(\d{1,2}[:.]\d{2})", strip_html(html))
    time_str = tm.group(1).replace(".", ":") if tm else None
    # Ort
    om = re.search(r"Ort\s*(?:</[^>]+>\s*)*([A-Za-zÄÖÜäöü0-9 .\-]+?)(?:Konzertführer|Förderer|Preise|<)", strip_html(html))
    venue = strip_html(om.group(1)) if om else "Philharmonie Mercatorhalle"
    # Tickets: weekday -> url
    tickets: Dict[str, str] = {}
    ticket_list: List[str] = []
    for mt in re.finditer(r'<a[^>]*href="(https://[^"]*eventim-inhouse[^"]*shop\?event=\d+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        url = mt.group(1)
        label = strip_html(mt.group(2))
        ticket_list.append(url)
        wd = re.search(r"\b(Mo|Di|Mi|Do|Fr|Sa|So)\b", label)
        if wd:
            tickets.setdefault(wd.group(1), url)
    return {
        "title": title, "orchestra": orchestra, "conductors": cond, "soloists": sol,
        "program": program, "werke_text": werke_text, "dates": dates, "time": time_str,
        "venue": venue, "tickets_by_wd": tickets, "ticket_list": ticket_list,
    }


# --- Normalisierung ---------------------------------------------------------

FOLD = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a", "ç": "c", "č": "c", "ć": "c",
        "è": "e", "é": "e", "ê": "e", "ë": "e", "ì": "i", "í": "i", "î": "i", "ï": "i",
        "ñ": "n", "ń": "n", "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ø": "oe",
        "ù": "u", "ú": "u", "û": "u", "š": "s", "ś": "s", "ž": "z", "ź": "z", "ż": "z",
        "ł": "l", "đ": "d", "ð": "d", "þ": "th", "ř": "r", "ě": "e", "ā": "a", "ē": "e",
        "ī": "i", "ō": "o", "ū": "u"}
COMPOSER_ALIAS = {"sergei rachmaninow": "sergej-rachmaninow", "sergei prokofjew": "sergej-prokofjew",
                  "igor strawinski": "igor-strawinsky", "antonin dvorak": "antonin-dvorak"}


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
                            "violine und orchester", "violoncello und orchester", "concerto", "doppelkonzert")):
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
    return cat, re.sub(r"\s+", " ", cleaned).strip(" ,;„“\"")


def norm_title(title: str) -> str:
    t = _fold(title.lower()).replace("symphonie", "sinfonie")
    t = re.sub(r"\bop(?:us|\.)?\s*[\dA-Za-z/]+", "", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, d: Dict[str, Any]) -> None:
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_location(label: str) -> Optional[Dict[str, Any]]:
    """Venue-Datensatz für Duisburger Spielstätten; None für Auswärts-/Gastspiele
    (Ort außerhalb Duisburgs → wird ausgelassen, nicht fälschlich Duisburg zugeordnet)."""
    low = label.lower()
    for key, spec in DUISBURG_VENUES:
        if key in low:
            return spec
    if "duisburg" in low:  # z. B. Marienkirche Duisburg, St. Maximilian in Duisburg-Ruhrort
        vid = re.sub(r"[^a-z0-9]+", "-", _fold(low)).strip("-")[:48]
        return {"id": vid, "name": re.sub(r"\s+", " ", label).strip(), "type": "other"}
    return None


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    print("=== Duisburger Philharmoniker – Ingest 2026/27 ===\n")
    print("1. Kalender laden ...")
    slugs = collect_slugs()
    print(f"   {len(slugs)} Konzert-Detailseiten")

    events_doc = load(data / "events.json")
    venues_doc = load(data / "venues.json")
    people_doc = load(data / "people.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")

    venue_ids = {v["id"] for v in venues_doc["venues"]}

    def ensure_venue(spec: Dict[str, Any]) -> str:
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
        title = re.sub(r"\s+", " ", raw_title).strip(" ,;„“\"")
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

    print("\n2. Detailseiten (Programm/Besetzung/Termine) ...")
    new_events: List[Dict[str, Any]] = []
    included = skipped = skipped_away = 0
    for i, slug in enumerate(slugs, 1):
        html = http_get(DETAIL_BASE + slug + "/")
        if not html:
            continue
        d = parse_detail(html)
        if not d["orchestra"]:
            skipped += 1  # kein Orchester → Gast-Recital/Fremdveranstaltung
            continue
        if not d["dates"]:
            skipped += 1
            continue
        venue_spec = resolve_location(d["venue"])
        if venue_spec is None:  # Auswärts-/Gastspiel außerhalb Duisburgs → auslassen
            skipped_away += 1
            continue
        included += 1
        cond_ids = [pid for pid in (ensure_person(n) for n in d["conductors"]) if pid]
        sol_ids = [pid for pid in (ensure_person(n) for n in d["soloists"]) if pid]
        prog = []
        for comp, wtitle in d["program"]:
            wid = resolve_work(comp, wtitle)
            if wid:
                prog.append({"workId": wid})
        # Fallback: „Werke von …"-Text als description, damit die App das Programm zeigt.
        description = None
        if not prog and re.match(r"^(Werke|Musik) von\b", d["werke_text"]):
            description = d["werke_text"]
        vid = ensure_venue(venue_spec)
        for date, wd in d["dates"]:
            if not (SEASON_START <= date <= SEASON_END):
                continue
            ticket = d["tickets_by_wd"].get(wd)
            if not ticket and len(d["ticket_list"]) == 1 and len(d["dates"]) == 1:
                ticket = d["ticket_list"][0]
            short = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:40]
            eid = f"event-{date}-duisburg-{short}"
            new_events.append({
                "id": eid, "title": d["title"], "eventType": "concert", "date": date,
                "startTime": d["time"], "endTime": None, "status": "scheduled",
                "ensembleIds": [ENSEMBLE_ID], "venueId": vid, "cityId": CITY_ID,
                "conductorPersonIds": cond_ids, "soloistPersonIds": sol_ids,
                "program": prog, "seriesId": None, "description": description,
                "source": {"url": DETAIL_BASE + slug + "/", "name": SOURCE_NAME, "retrievedAt": RETRIEVED_AT},
                "ticketUrl": ticket, "lastVerified": RETRIEVED_AT,
            })
        if i % 20 == 0:
            print(f"   [{i}/{len(slugs)}] ... (aufgenommen {included}, ausgelassen {skipped})")
        time.sleep(0.08)

    # eindeutige IDs
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
    print(f"\n   Alte Duisburg-Events entfernt: {before - len(events_doc['events'])}")
    events_doc["events"].extend(new_events)
    events_doc.setdefault("metadata", {})["lastUpdated"] = RETRIEVED_AT

    save(data / "events.json", events_doc)
    save(data / "venues.json", venues_doc)
    save(data / "people.json", people_doc)
    save(data / "composers.json", composers_doc)
    save(data / "works.json", works_doc)

    prog_ev = sum(1 for e in new_events if e["program"])
    tix = sum(1 for e in new_events if e["ticketUrl"])
    print(f"\n✓ Ingest abgeschlossen: {len(new_events)} Events aus {included} Produktionen "
          f"({prog_ev} mit Programm, {tix} mit Ticket); {skipped} Nicht-Orchester-Seiten, "
          f"{skipped_away} Auswärts-/Gastspiele ausgelassen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
