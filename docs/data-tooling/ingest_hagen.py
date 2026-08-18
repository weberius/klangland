#!/usr/bin/env python3
"""
Ingest-Skript für das Philharmonische Orchester Hagen, Spielzeit 2026/27.

Quelle:  Kalender  https://www.theaterhagen.de/kalender/alle-termine/  (TYPO3,
         monatsweise via tx_theatre_kalender[month]=<ts> geladen)
         Detail    https://www.theaterhagen.de/veranstaltung/<slug>/<uid>/show/Play/

Vorgehen:
  1. Alle Monatsseiten der Saison 2026/27 laden (Monats-Links mit cHash von der Kalenderseite).
  2. `event-item`-Blöcke parsen: Datum/Uhrzeit, Titel, Ort (Name + Adresse), Ticket-Link,
     Detail-Link. **Ort:** Stadt aus der Adresse (PLZ + Ort); nur Hagen wird aufgenommen,
     Gastspiele außerhalb (z. B. Parktheater Iserlohn) werden ausgelassen.
  3. Konzert-Kandidaten (Titel enthält konzert/orchester/philharmon/sinfonie) → Detailseite
     laden: Programm (`div.play-intro`: <strong>Komponist</strong><br>Werk) und Besetzung
     (`ul.actors`: role/actor). Aufgenommen nur, wenn das Philharmonische Orchester Hagen
     mitwirkt. Programm wird in `program[].workId` normalisiert.

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host theaterhagen.de und Ensemble
philharmonisches-orchester-hagen und legt sie neu an; Stammdaten werden dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_hagen.py
"""

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = "https://www.theaterhagen.de/"
CALENDAR = BASE + "kalender/alle-termine/"
SOURCE_HOST = "theaterhagen.de"
SOURCE_NAME = "Theater Hagen / Philharmonisches Orchester Hagen"
ENSEMBLE_ID = "philharmonisches-orchester-hagen"
CITY_ID = "hagen"
RETRIEVED_AT = "2026-08-18"
SEASON_START, SEASON_END = "2026-08-01", "2027-08-31"

MONTHS_DE = {1: "Jan", 2: "Feb", 3: "Mär", 4: "Apr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Aug",
             9: "Sep", 10: "Okt", 11: "Nov", 12: "Dez"}
MON_ABBR = {"jan": 1, "feb": 2, "mär": 3, "maer": 3, "mrz": 3, "apr": 4, "mai": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dez": 12}

# Konzert-Titel-Stichwörter (Vorfilter); szenische Oper/Schauspiel/Tanz haben diese nicht.
CONCERT_KEYWORDS = ("konzert", "orchester", "philharmon", "sinfonie", "symphonie")

# Hagener Spielstätten: Venue-Name (lower, Teilstring) → Venue-Datensatz.
HAGEN_VENUES: List[Tuple[str, Dict[str, Any]]] = [
    ("großes haus", {"id": "theater-hagen", "name": "Theater Hagen", "type": "theatre"}),
    ("grosses haus", {"id": "theater-hagen", "name": "Theater Hagen", "type": "theatre"}),
    ("kunstquartier", {"id": "kunstquartier-hagen", "name": "Kunstquartier Hagen", "type": "other"}),
    ("lutz", {"id": "lutz-hagen", "name": "Lutz Theater Hagen", "type": "other"}),
    ("theatercafé", {"id": "theatercafe-hagen", "name": "Theatercafé Hagen", "type": "other"}),
    ("theatercafe", {"id": "theatercafe-hagen", "name": "Theatercafé Hagen", "type": "other"}),
]

CONDUCTOR_ROLE_HINTS = ("dirigent", "dirigentin", "leitung", "musikalische leitung", "am pult")
SOLOIST_ROLE_HINTS = ("violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel",
                      "cembalo", "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete",
                      "posaune", "tuba", "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion",
                      "sopran", "mezzosopran", "countertenor", "alt", "tenor", "bariton", "bass",
                      "gesang", "akkordeon", "bandoneon", "moderation", "sprecher", "rezitation")
SKIP_ROLE_HINTS = ("orchester", "chor", "ensemble", "philharmon")


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


# --- Kalender-Pass ----------------------------------------------------------

def month_links(cal_html: str) -> List[str]:
    """Monats-Links (mit cHash) für die Saison 2026/27."""
    out: Dict[int, str] = {}
    for href, ts in re.findall(r'href="(kalender/alle-termine/\?tx_theatre_kalender%5Bmonth%5D=(\d+)[^"]*)"', cal_html):
        ts = int(ts)
        d = datetime.fromtimestamp(ts, tz=timezone.utc)
        if (2026, 8) <= (d.year, d.month) <= (2027, 8):
            out[ts] = unescape(href)
    return [BASE + out[ts] for ts in sorted(out)]


def parse_date(date_text: str, data_date: str) -> Optional[str]:
    """'Sa 05. Sep' + data-date='9-2026' → '2026-09-05'."""
    m = re.search(r"(\d{1,2})\.\s*([A-Za-zäöü]{3,})", date_text)
    dm = re.match(r"(\d{1,2})-(\d{4})", data_date or "")
    if m:
        day = int(m.group(1))
        mon = MON_ABBR.get(m.group(2)[:3].lower())
        year = int(dm.group(2)) if dm else None
        if mon and year:
            return f"{year:04d}-{mon:02d}-{day:02d}"
    if dm:
        dnum = re.search(r"(\d{1,2})\.", date_text)
        if dnum:
            return f"{int(dm.group(2)):04d}-{int(dm.group(1)):02d}-{int(dnum.group(1)):02d}"
    return None


def collect_events(cal_html: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for url in month_links(cal_html):
        s = http_get(url)
        if not s:
            continue
        starts = [m.start() for m in re.finditer(r'class="event-item clearfix"', s)]
        starts.append(len(s))
        for i in range(len(starts) - 1):
            b = s[starts[i]:starts[i + 1]]
            dd = re.search(r'data-date="([^"]*)"', b)
            dtxt = re.search(r'data-date="[^"]*">\s*(.*?)<br', b, re.DOTALL)
            tm = re.search(r'class="time">\s*(\d{1,2}[:.]\d{2})', b)
            title = re.search(r'event-title">\s*<a[^>]*>(.*?)</a>', b, re.DOTALL)
            sub = re.search(r'event-title-sub">(.*?)</div>', b, re.DOTALL)
            det = re.search(r'href="(veranstaltung/[^"]+?/show/[A-Za-z]+/)"', b)
            venm = re.search(r'fa-map-marker[^>]*></i>\s*<b>(.*?)</b>\s*<small>(.*?)</small>', b, re.DOTALL)
            tk = re.search(r'(https://theaterhagen\.eventim-inhouse\.de/webshop/webticket/shop\?[^"]*event=\d+[^"]*)', b)
            if not (det and dd):
                continue
            date = parse_date(strip_html(dtxt.group(1)) if dtxt else "", dd.group(1))
            if not date:
                continue
            venue_name = strip_html(venm.group(1)) if venm else ""
            venue_addr = strip_html(venm.group(2)) if venm else ""
            city_m = re.search(r"\d{5}\s+([A-Za-zäöüÄÖÜ\-]+)", venue_addr)
            city = city_m.group(1) if city_m else ""
            key = (det.group(1), date, tm.group(1) if tm else None)
            if key in seen:
                continue
            seen.add(key)
            items.append({
                "detail": det.group(1),
                "slug": re.search(r"veranstaltung/([^/]+)/", det.group(1)).group(1),
                "date": date, "time": (tm.group(1).replace(".", ":") if tm else None),
                "title": strip_html(title.group(1)) if title else "",
                "sub": strip_html(sub.group(1)) if sub else "",
                "venue_name": venue_name, "city": city,
                "ticket": tk.group(1) if tk else None,
            })
        time.sleep(0.12)
    return items


# --- Detail-Pass ------------------------------------------------------------

def parse_program(detail_html: str) -> List[Tuple[str, str]]:
    m = re.search(r'class="play-intro[^"]*">(.*?)</div>', detail_html, re.DOTALL)
    if not m:
        return []
    pairs: List[Tuple[str, str]] = []
    for p in re.findall(r"<p>(.*?)</p>", m.group(1), re.DOTALL):
        sm = re.search(r"<strong>(.*?)</strong>", p, re.DOTALL)
        if not sm:
            continue
        rest = p[sm.end():]
        # Zeichen zwischen </strong> und erstem <br> gehören zum Namen (Markup-Glitch,
        # z. B. „Detlev Glaner</strong>t" → „Detlev Glanert").
        parts = re.split(r"<br\s*/?>", rest, maxsplit=1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else ""
        comp = strip_html(sm.group(1) + head).strip()
        lines = [strip_html(x) for x in re.split(r"<br\s*/?>", tail)]
        lines = [x for x in lines if len(x) > 2]
        if not comp or not lines:
            continue
        pairs.append((comp, lines[0]))
    return pairs


def parse_ticket_map(detail_html: str) -> Dict[Tuple[int, int], str]:
    """Termin-Liste der Detailseite → {(Monat, Tag): Ticket-URL}."""
    m = re.search(r"Vorstellungen / Termine(.*?)ZusatzAngebote", detail_html, re.DOTALL)
    seg = m.group(1) if m else detail_html
    out: Dict[Tuple[int, int], str] = {}
    for li in re.findall(r"<li[^>]*>(.*?)</li>", seg, re.DOTALL):
        dm = re.search(r"(\d{1,2})\.\s*(\d{1,2})\.", li)
        tk = re.search(r"(https://theaterhagen\.eventim-inhouse\.de/webshop/webticket/shop\?[^\"]*event=\d+)", li)
        if dm and tk:
            out[(int(dm.group(2)), int(dm.group(1)))] = tk.group(1)  # (Monat, Tag)
    return out


def parse_cast(detail_html: str) -> Tuple[bool, List[str], List[str]]:
    orchestra = False
    cond: List[str] = []
    sol: List[str] = []
    m = re.search(r'<ul class="actors">(.*?)</ul>', detail_html, re.DOTALL)
    if not m:
        return False, [], []
    for li in re.findall(r"<li>(.*?)</li>", m.group(1), re.DOTALL):
        role = strip_html(re.search(r'class="role">(.*?)</span>', li, re.DOTALL).group(1)) if re.search(r'class="role">', li) else ""
        actor = strip_html(re.search(r'class="actor">(.*?)</span>', li, re.DOTALL).group(1)) if re.search(r'class="actor">', li) else ""
        low_actor = actor.lower()
        if "philharmonisches orchester hagen" in low_actor or "orchester hagen" in low_actor:
            orchestra = True
            continue
        rl = role.lower()
        if not actor or len(actor) < 3:
            continue
        if any(h in rl for h in SKIP_ROLE_HINTS):
            continue
        if any(h in rl for h in CONDUCTOR_ROLE_HINTS):
            cond.append(actor)
        elif any(h in rl for h in SOLOIST_ROLE_HINTS):
            sol.append(actor)
    return orchestra, list(dict.fromkeys(cond)), list(dict.fromkeys(sol))


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
                            "violine und orchester", "bandoneon und orchester", "concerto", "doppelkonzert")):
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


def resolve_venue(name: str, city: str) -> Optional[Dict[str, Any]]:
    """Venue-Datensatz für Hagener Orte; None für Auswärts-/Gastspiele oder ungeklärte Orte.
    Unbekannte Orte werden NUR angelegt, wenn die Stadt eindeutig Hagen ist – leere/andere
    Städte (z. B. Kölner Philharmonie, Parktheater Iserlohn) werden ausgeschlossen."""
    low = name.lower()
    for key, spec in HAGEN_VENUES:  # bekannte Hagener Spielstätten (per Name)
        if key in low:
            return spec
    if name and (city or "").lower() == "hagen":  # generische Hagener Spielstätte
        vid = re.sub(r"[^a-z0-9]+", "-", _fold(low)).strip("-")[:44]
        if not vid.endswith("hagen"):
            vid += "-hagen"
        return {"id": vid, "name": re.sub(r"\s+", " ", name).strip(), "type": "other"}
    return None


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    print("=== Philharmonisches Orchester Hagen – Ingest 2026/27 ===\n")
    print("1. Kalenderseite + Monate laden ...")
    cal = http_get(CALENDAR)
    if not cal:
        print("Kalender nicht erreichbar")
        return 1
    items = collect_events(cal)
    print(f"   {len(items)} Termine gesamt im Kalender (Saison 2026/27)")

    # Kandidaten: Konzert-Stichwort im Titel/Sub UND Ort in Hagen.
    def is_concert(it: Dict[str, Any]) -> bool:
        t = it["title"].lower()
        if t.startswith(("offene probe", "treffen", "campusfest")):
            return False
        # „konzert" im Titel kennzeichnet die Konzertformate des Orchesters
        # (Sinfonie-/Kammer-/Familien-/Krabbel-/Advents-/Neujahrs-/Mitsingkonzert …);
        # szenische Oper/Schauspiel/Tanz tragen es nicht.
        return "konzert" in t or t.startswith(("philharmon", "sinfonie", "orchester unterwegs"))

    cand = [it for it in items if is_concert(it) and resolve_venue(it["venue_name"], it["city"])]
    print(f"   {len(cand)} Konzert-Kandidaten in Hagen")

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

    # Detailseiten je Produktion (einmal je Slug).
    print("\n2. Konzert-Detailseiten laden ...")
    detail_cache: Dict[str, Dict[str, Any]] = {}
    for i, detail in enumerate(sorted({c["detail"] for c in cand}), 1):
        html_text = http_get(BASE + detail)
        if not html_text:
            detail_cache[detail] = {"orchestra": False}
            continue
        orch, cond, sol = parse_cast(html_text)
        program = parse_program(html_text)
        prog = []
        for comp, wtitle in program:
            wid = resolve_work(comp, wtitle)
            if wid:
                prog.append({"workId": wid})
        detail_cache[detail] = {
            "orchestra": orch,
            "conductors": [pid for pid in (ensure_person(n) for n in cond) if pid],
            "soloists": [pid for pid in (ensure_person(n) for n in sol) if pid],
            "program": prog,
            "tickets": parse_ticket_map(html_text),
        }
        if i % 10 == 0:
            print(f"   [{i}] ...")
        time.sleep(0.1)

    print("\n3. Events bauen ...")
    new_events: List[Dict[str, Any]] = []
    for it in cand:
        info = detail_cache.get(it["detail"], {})
        if not (SEASON_START <= it["date"] <= SEASON_END):
            continue
        vid = ensure_venue(resolve_venue(it["venue_name"], it["city"]))
        y, mo, dy = (int(x) for x in it["date"].split("-"))
        ticket = info.get("tickets", {}).get((mo, dy)) or it["ticket"]
        short = re.sub(r"[^a-z0-9]+", "-", it["slug"].lower()).strip("-")[:40]
        eid = f"event-{it['date']}-hagen-{short}"
        if it["time"]:
            eid = f"{eid}-{it['time'].replace(':', '')}"
        new_events.append({
            "id": eid, "title": it["title"], "eventType": "concert", "date": it["date"],
            "startTime": it["time"], "endTime": None, "status": "scheduled",
            "ensembleIds": [ENSEMBLE_ID], "venueId": vid, "cityId": CITY_ID,
            "conductorPersonIds": info.get("conductors", []),
            "soloistPersonIds": info.get("soloists", []),
            "program": info.get("program", []), "seriesId": None, "description": None,
            "source": {"url": BASE + it["detail"], "name": SOURCE_NAME, "retrievedAt": RETRIEVED_AT},
            "ticketUrl": ticket, "lastVerified": RETRIEVED_AT,
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
    print(f"   Alte Hagen-Events entfernt: {before - len(events_doc['events'])}")
    events_doc["events"].extend(new_events)
    events_doc.setdefault("metadata", {})["lastUpdated"] = RETRIEVED_AT

    save(data / "events.json", events_doc)
    save(data / "venues.json", venues_doc)
    save(data / "people.json", people_doc)
    save(data / "composers.json", composers_doc)
    save(data / "works.json", works_doc)

    prog_ev = sum(1 for e in new_events if e["program"])
    tix = sum(1 for e in new_events if e["ticketUrl"])
    print(f"\n✓ Ingest abgeschlossen: {len(new_events)} Events "
          f"({prog_ev} mit Programm, {tix} mit Ticket).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
