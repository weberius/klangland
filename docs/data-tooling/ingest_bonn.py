#!/usr/bin/env python3
"""
Ingest-Skript für das Beethoven Orchester Bonn, Spielzeit 2026/27.

Quelle:  Archiv/Spielplan  https://www.beethoven-orchester.de/archiv/26-27/
         Detailseiten      https://www.beethoven-orchester.de/konzerte/<slug>/

Vorgehen:
  1. Archivseite parsen: je Konzert-Element Slug, Titel, Datum (_sdate), Uhrzeit, Ort und
     Ticket-URL (Ticket-Button-Link; Host variiert: derticketservice, beethovenfest.de …).
  2. Nur Heimkonzerte in Bonn behalten (Beethovenhalle, Beethoven-Haus, Alter Bundesrat,
     Kreuzkirche, Opernhaus, KUNST!RASEN, BaseCamp). Auswärtige Tourneen (Toblach, Bad Honnef,
     Koblenz, Warschau, Oslo, Kopenhagen, Helsingborg, Elbphilharmonie, Amsterdam …) werden
     ausgelassen, da Venue/City nicht im Bestand sind.
  3. Je Konzert die Detailseite laden → Programm (Komponist/Werk) und Besetzung
     (Dirigent:innen/Solist:innen). Programm wird in `program[].workId` normalisiert.

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host beethoven-orchester.de und
Ensemble beethoven-orchester-bonn und legt sie neu an; Stammdaten werden dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_bonn.py
"""

import json
import re
import sys
import time
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = "https://www.beethoven-orchester.de"
ARCHIVE = f"{BASE}/archiv/26-27/"
DETAIL_BASE = f"{BASE}/konzerte/"
CALENDAR_URL = f"{BASE}/konzerte/"
SOURCE_HOST = "beethoven-orchester.de"
SOURCE_NAME = "Beethoven Orchester Bonn"
ENSEMBLE_ID = "beethoven-orchester-bonn"
CITY_ID = "bonn"
RETRIEVED_AT = "2026-08-18"
SEASON_START, SEASON_END = "2026-06-01", "2027-08-31"

# Bonn-Spielstätten: Kalender-Text (Teilstring, lower) → Venue-Datensatz.
BONN_VENUES: List[Tuple[str, Dict[str, Any]]] = [
    ("beethovenhalle studio", {"id": "beethovenhalle-studio-bonn", "name": "Beethovenhalle Bonn (Studio)", "type": "concert_hall"}),
    ("beethovenhalle", {"id": "beethovenhalle-bonn", "name": "Beethovenhalle Bonn (Großer Saal)", "type": "concert_hall"}),
    ("beethoven-haus", {"id": "beethoven-haus-bonn", "name": "Beethoven-Haus Bonn (Kammermusiksaal)", "type": "concert_hall"}),
    ("alter bundesrat", {"id": "alter-bundesrat-bonn", "name": "Alter Bundesrat Bonn", "type": "other"}),
    ("kreuzkirche", {"id": "kreuzkirche-bonn", "name": "Kreuzkirche Bonn", "type": "other"}),
    ("opernhaus bonn", {"id": "opernhaus-bonn", "name": "Opernhaus Bonn", "type": "opera_house"}),
    ("kunst!rasen", {"id": "kunstrasen-bonn", "name": "KUNST!RASEN Bonn", "type": "other"}),
    ("basecamp", {"id": "basecamp-bonn", "name": "BaseCamp Hostel Bonn", "type": "other"}),
]


def resolve_bonn_venue(label: str) -> Optional[Dict[str, Any]]:
    low = label.lower()
    for key, spec in BONN_VENUES:
        if key in low:
            return spec
    return None  # auswärts / nicht im Bestand → auslassen


# --- HTTP -------------------------------------------------------------------

def http_get(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  ! Fehler {url}: {e}")
        return None


def strip_html(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", unescape(t))).strip()


# --- Archiv-Pass ------------------------------------------------------------

def collect_archive() -> List[Dict[str, Any]]:
    s = http_get(ARCHIVE)
    if not s:
        return []
    starts = [m.start() for m in re.finditer(r"_segment__cpatterns__element ", s)]
    starts.append(len(s))
    evs = []
    for i in range(len(starts) - 1):
        b = s[starts[i]:starts[i + 1]]
        slug = re.search(r"data-uri_details='konzerte/([^']+)'", b)
        title = re.search(r"data-_title='([^']*)'", b)
        sdate = re.search(r"_sdate__(\d{8})", b)
        tk = re.search(r"<a href='([^']+)'[^>]*>\s*<button[^>]*ticketbutton", b)
        tm = re.search(r"(\d{1,2}:\d{2})\s*Uhr", b)
        info = re.search(r"__content__info'>(.*?)</div>", b, re.DOTALL)
        venue = ""
        if info:
            ps = [strip_html(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", info.group(1), re.DOTALL)]
            ps = [p for p in ps if p]
            venue = ps[-1] if ps else ""
        if not (slug and sdate):
            continue
        d = sdate.group(1)
        evs.append({
            "slug": slug.group(1),
            "title": unescape(title.group(1)) if title else "",
            "date": f"{d[0:4]}-{d[4:6]}-{d[6:8]}",
            "time": tm.group(1) if tm else None,
            "ticket": tk.group(1) if tk else None,
            "venue": venue,
        })
    return evs


# --- Detail-Pass: Programm + Besetzung -------------------------------------

ROLE_COND = ("dirigent", "dirigentin", "leitung")
ROLE_SOL = ("violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel", "cembalo",
            "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete", "posaune", "tuba",
            "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion", "sopran", "mezzosopran",
            "countertenor", "alt", "tenor", "bariton", "bass", "gesang", "akkordeon", "panflöte")
ROLE_SKIP = ("einstudierung", "konzept", "schauspiel", "moderator", "moderation", "regie", "choreo",
             "tanz", "sprecher", "kostüm", "licht", "dramaturg", "video", "buch", "erzähler")
WORK_KW = ("sinfonie", "symphonie", "sinfonia", "konzert", "ouvertüre", "ouverture", "vorspiel",
           "suite", "quartett", "quintett", "sextett", "septett", "oktett", "trio", "sonate",
           "fantasie", "fantaisie", "variationen", "rhapsodie", "serenade", "messe", "requiem",
           "oratorium", "ballett", "walzer", "tanz", "divertimento", "poem", "lied", "arie",
           "nocturne", "pavane", "fuge", "partita", "kantate", "burleske", "notturno", "toccata")
NOTE_KW = ("veröffentlicht", "komponiert", "entstanden", "uraufführung", "erstaufführung",
           "bearbeitung", "fassung", "orchestrierung")


def _has_kw(t: str) -> bool:
    low = t.lower()
    # Wortgrenze: „Konzert für …" matcht, Reihen-Kompositum „Freitagskonzert" nicht.
    return any(re.search(rf"\b{re.escape(k)}\b", low) for k in WORK_KW)


def _is_year(t: str) -> bool:
    return bool(re.fullmatch(r"[\d—–/\s.]+", t))


def _is_scoring(t: str) -> bool:
    low = t.lower()
    return (t.startswith("(") or low.startswith("für ") or low.startswith("aus ")
            or "auszüge" in low or "ausschnitte" in low or "community" in low
            or any(k in low for k in NOTE_KW) or len(t) > 120)


def _is_comp(t: str) -> bool:
    return (not _has_kw(t) and not _is_year(t) and not _is_scoring(t)
            and 1 <= len(t.split()) <= 4 and t[:1].isupper() and ":" not in t)


def _detail_groups(detail_html: str) -> List[List[Tuple[str, Optional[str]]]]:
    m = (re.search(r"_segment__cdetails__infos[^>]*>(.*?)</div>\s*</div>", detail_html, re.DOTALL)
         or re.search(r"_segment__cdetails__infos[^>]*>(.*)", detail_html, re.DOTALL))
    inner = m.group(1) if m else ""
    grps: List[List[Tuple[str, Optional[str]]]] = [[]]
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", inner, re.DOTALL):
        raw = pm.group(1)
        em = re.search(r"<em>(.*?)</em>", raw)
        txt = strip_html(raw)
        if not txt or txt == "\xa0":
            if grps[-1]:
                grps.append([])
            continue
        grps[-1].append((txt, strip_html(em.group(1)) if em else None))
    return [g for g in grps if g]


def _role_has(role_str: str, hints) -> bool:
    rl = role_str.lower()
    # Rollenwort als ganzes Wort inkl. femininer/Plural-Endungen (Dirigentin, Schauspielerin, Violinen).
    return any(re.search(rf"\b{re.escape(h)}(?:erin|innen|erinnen|er|in|en|n|e|s)?\b", rl) for h in hints)


def _valid_name(name: str) -> bool:
    n = name.strip()
    if not n or len(n) > 45 or not (1 <= len(n.split()) <= 5) or n.endswith((".", "!", ":")):
        return False
    return not re.fullmatch(r"n\.?\s*n\.?(\s.*)?", n.lower())  # „N. N." (noch offen)


def _extract_cast_line(t: str, em: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """(Name, Rolle) aus einer Besetzungszeile – Formate: 'Name → Rolle', 'Name <em>Rolle</em>',
    'Name Rolle' (Rollenwort am Ende)."""
    if "→" in t:
        parts = [x.strip() for x in t.split("→", 1)]
        return parts[0], parts[1]
    if em and len(em.split()) <= 4 and _role_has(em, ROLE_COND + ROLE_SOL + ROLE_SKIP):
        return (t[:t.rfind(em)].strip() if em in t else t), em
    low = t.lower()
    best = None
    for r in ROLE_COND + ROLE_SOL + ROLE_SKIP:
        mm = re.search(rf"\b{re.escape(r)}\b", low)
        if mm and (best is None or mm.start() < best):
            best = mm.start()
    if best is not None and best > 0:
        return t[:best].strip(), t[best:].strip()
    return None, None


def _is_program_group(g: List[Tuple[str, Optional[str]]]) -> bool:
    """Programm-Gruppe: erste Zeile ist ein Komponist (Personenname ohne Rolle/Ensemble)."""
    if len(g) < 2:
        return False
    first, first_em = g[0]
    low = first.lower()
    if not _is_comp(first) or "→" in first:
        return False
    if _role_has(first, ROLE_COND + ROLE_SOL + ROLE_SKIP):
        return False
    if first_em and _role_has(first_em, ROLE_COND + ROLE_SOL + ROLE_SKIP):
        return False
    if any(k in low for k in ("orchester", "chor", "ensemble", "quartett")):
        return False
    return True


def parse_detail(detail_html: str) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    groups = _detail_groups(detail_html)
    # Programm-Gruppe: erste Gruppe (nach Titel/Datum) mit Komponist + Werk-Struktur.
    prog_gi = next((gi for gi, g in enumerate(groups) if gi >= 1 and _is_program_group(g)), None)

    cond: List[str] = []
    sol: List[str] = []
    cast_groups = groups[:prog_gi] if prog_gi is not None else groups
    for g in cast_groups[2:] if len(cast_groups) > 2 else cast_groups:  # Header/Datum überspringen
        for t, em in g:
            name, role = _extract_cast_line(t, em)
            if not (name and role and _valid_name(name)):
                continue
            if _role_has(role, ROLE_SKIP):
                continue
            if _role_has(role, ROLE_COND):
                cond.append(name)
            elif _role_has(role, ROLE_SOL):
                sol.append(name)

    works: List[Tuple[str, str]] = []
    if prog_gi is not None:
        g = groups[prog_gi]
        blocks: List[List[Tuple[str, Optional[str]]]] = [[]]
        for t, em in g:
            if t == "+":
                blocks.append([])
                continue
            blocks[-1].append((t, em))
        for blk in blocks:
            if not blk or not _is_comp(blk[0][0]):
                continue
            comp = blk[0][0]
            cur: Optional[List[str]] = None
            for t, em in blk[1:]:
                if _is_year(t):
                    cur = None
                    continue
                if _is_scoring(t):
                    continue
                if em and em == t and cur is not None:
                    cur[1] += f" »{t}«"
                    continue
                if _has_kw(t) or cur is None:
                    works.append([comp, t])
                    cur = works[-1]
                else:
                    cur[1] += " " + t
    # Dedupe (Name-Reihenfolge erhalten)
    cond = list(dict.fromkeys(cond))
    sol = list(dict.fromkeys(sol))
    return cond, sol, [(c, w) for c, w in works]


# --- Normalisierung (wie Bochum/Dortmund) -----------------------------------

FOLD = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a", "ç": "c", "č": "c", "ć": "c",
        "è": "e", "é": "e", "ê": "e", "ë": "e", "ì": "i", "í": "i", "î": "i", "ï": "i",
        "ñ": "n", "ń": "n", "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ø": "oe",
        "ù": "u", "ú": "u", "û": "u", "š": "s", "ś": "s", "ž": "z", "ź": "z", "ż": "z",
        "ł": "l", "đ": "d", "ð": "d", "þ": "th", "ř": "r", "ě": "e", "ā": "a", "ē": "e",
        "ī": "i", "ō": "o", "ū": "u"}
COMPOSER_ALIAS = {"sergei rachmaninow": "sergej-rachmaninow", "sergei prokofjew": "sergej-prokofjew",
                  "rachmaninoff": "sergej-rachmaninow", "igor strawinski": "igor-strawinsky",
                  "pjotr tschaikowsky": "peter-iljitsch-tschaikowsky", "antonin dvorak": "antonin-dvorak"}


def _fold(s: str) -> str:
    return "".join(FOLD.get(c, c) for c in s)


def slugify(name: str) -> str:
    s = "".join(c if (c.isalnum() or c == " ") else " " for c in _fold(name.strip().lower()))
    return re.sub(r"\s+", "-", s.strip())


def clean_composer_name(name: str) -> str:
    name = re.sub(r"\s*\((Sohn|Vater)\)", "", name).strip().strip(":").strip()
    return re.sub(r"\s+", " ", name)


def infer_genre(title: str) -> str:
    t = title.lower()
    if "requiem" in t:
        return "requiem"
    if any(k in t for k in ("oratorium", "messe", "messa", "passion", "te deum", "gloria", "kantate")):
        return "oratorio"
    if any(k in t for k in ("streichquartett", "quartett", "quintett", "sextett", "septett", "oktett",
                            "streichtrio", "klaviertrio", "trio", "sonate", "kammer")):
        return "chamber_music"
    if any(k in t for k in ("sinfonie", "symphonie", "sinfonia")):
        return "symphony"
    if any(k in t for k in ("konzert für", "klavierkonzert", "violinkonzert", "cellokonzert", "concerto", "doppelkonzert")):
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


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    print("=== Beethoven Orchester Bonn – Ingest 2026/27 ===\n")
    print("1. Archivseite laden ...")
    arch = collect_archive()
    print(f"   {len(arch)} Konzert-Elemente")

    bonn = [e for e in arch if resolve_bonn_venue(e["venue"])]
    away = [e for e in arch if not resolve_bonn_venue(e["venue"])]
    print(f"   {len(bonn)} Heimkonzerte in Bonn, {len(away)} auswärts ausgelassen")

    events_doc = load(data / "events.json")
    venues_doc = load(data / "venues.json")
    people_doc = load(data / "people.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")

    venue_ids = {v["id"] for v in venues_doc["venues"]}

    def ensure_venue(label: str) -> str:
        spec = resolve_bonn_venue(label)
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

    # Detailseiten je Produktion (Slug kann mehrfach vorkommen → cachen)
    print("\n2. Detailseiten (Programm/Besetzung) ...")
    detail_cache: Dict[str, Dict[str, Any]] = {}
    uniq = sorted({e["slug"] for e in bonn})
    for i, slug in enumerate(uniq, 1):
        html_text = http_get(DETAIL_BASE + slug + "/")
        if not html_text:
            detail_cache[slug] = {"program": [], "conductors": [], "soloists": []}
            continue
        cond, sol, works = parse_detail(html_text)
        prog = []
        for comp, title in works:
            wid = resolve_work(comp, title)
            if wid:
                prog.append({"workId": wid})
        detail_cache[slug] = {
            "program": prog,
            "conductors": [pid for pid in (ensure_person(n) for n in cond) if pid],
            "soloists": [pid for pid in (ensure_person(n) for n in sol) if pid],
        }
        if i % 10 == 0:
            print(f"   [{i}/{len(uniq)}] ...")
        time.sleep(0.1)

    # Events bauen
    print("\n3. Events bauen ...")
    new_events: List[Dict[str, Any]] = []
    for e in bonn:
        if not (SEASON_START <= e["date"] <= SEASON_END):
            continue
        info = detail_cache.get(e["slug"], {})
        vid = ensure_venue(e["venue"])
        short = re.sub(r"[^a-z0-9]+", "-", e["slug"].lower()).strip("-")[:34]
        eid = f"event-{e['date']}-bonn-{short}"
        if e["time"]:
            eid = f"{eid}-{e['time'].replace(':', '')}"
        new_events.append({
            "id": eid, "title": e["title"], "eventType": "concert", "date": e["date"],
            "startTime": e["time"], "endTime": None, "status": "scheduled",
            "ensembleIds": [ENSEMBLE_ID], "venueId": vid, "cityId": CITY_ID,
            "conductorPersonIds": info.get("conductors", []),
            "soloistPersonIds": info.get("soloists", []),
            "program": info.get("program", []), "seriesId": None, "description": None,
            "source": {"url": DETAIL_BASE + e["slug"] + "/", "calendarUrl": CALENDAR_URL, "name": SOURCE_NAME, "retrievedAt": RETRIEVED_AT},
            "ticketUrl": e["ticket"], "lastVerified": RETRIEVED_AT,
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
    print(f"   Alte Bonn-Events entfernt: {before - len(events_doc['events'])}")
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
