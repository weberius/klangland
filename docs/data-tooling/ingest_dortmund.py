#!/usr/bin/env python3
"""
Ingest-Skript für die Dortmunder Philharmoniker, Spielzeit 2026/27.

Quelle:  Kalender  https://www.theaterdo.de/kalender/  (Solr-Paging, server-gerendert)
         Detail    https://www.theaterdo.de/produktionen/detail/<slug>/

Vorgehen:
  1. Kalender durchpagen (`?tx_solr[page]=N`), nur Events der Sparte „Philharmoniker"
     behalten → je Aufführung Datum, Uhrzeit, Ort und Ticket-URL (Eventim-Webshop).
  2. Je Produktion die Detailseite laden → Programm (Komponist/Werk) und Besetzung
     (Dirigent:innen/Solist:innen). Termine/Tickets stehen NICHT im Detail-HTML
     (Eventim-Widget), daher stammen sie aus dem Kalender.
  3. Programm wird in `program[].workId` normalisiert (works/composers werden ergänzt),
     damit es auf der Event-Seite dargestellt wird.

Ausgeschlossen: „Öffentliche Probe …" (offene Proben, keine eigenständigen Konzerte).

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host theaterdo.de und
Ensemble dortmunder-philharmoniker und legt sie neu an; Stammdaten (Venues, Personen,
Komponist:innen, Werke) werden dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_dortmund.py
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = "https://www.theaterdo.de"
CALENDAR = f"{BASE}/kalender/?tx_solr%5Bpage%5D="
DETAIL_BASE = f"{BASE}/produktionen/detail/"
SOURCE_HOST = "theaterdo.de"
SOURCE_NAME = "Theater Dortmund / Dortmunder Philharmoniker"
ENSEMBLE_ID = "dortmunder-philharmoniker"
CITY_ID = "dortmund"
RETRIEVED_AT = "2026-08-18"
SEASON_START, SEASON_END = "2026-08-01", "2027-08-31"

MONTHS = {"Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
          "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}

# Spielstätten: Kalender-Text → Venue-Datensatz (Konzerthaus existiert bereits).
VENUE_MAP: Dict[str, Dict[str, Any]] = {
    "Konzerthaus": {"id": "konzerthaus-dortmund"},
    "Opernfoyer": {"id": "opernhaus-dortmund", "name": "Opernhaus Dortmund", "type": "opera_house"},
    "Kokerei Hansa (Salzlager)": {"id": "kokerei-hansa-dortmund", "name": "Kokerei Hansa (Salzlager)", "type": "other"},
    "Gartensaal, Baukunstarchiv NRW, Ostwall": {"id": "baukunstarchiv-nrw-dortmund", "name": "Baukunstarchiv NRW (Gartensaal)", "type": "other"},
    "Akademie für Theater und Digitalität (Speicherstraße 17)": {"id": "akademie-theater-digitalitaet-dortmund", "name": "Akademie für Theater und Digitalität", "type": "other"},
    "Deutsches Fußballmuseum Dortmund (Platz der Deutschen Einheit)": {"id": "deutsches-fussballmuseum-dortmund", "name": "Deutsches Fußballmuseum Dortmund", "type": "other"},
    "Phoenix des Lumières (Phoenixplatz 4)": {"id": "phoenix-des-lumieres-dortmund", "name": "Phoenix des Lumières Dortmund", "type": "other"},
    "Thier-Galerie (3. Etage)": {"id": "thier-galerie-dortmund", "name": "Thier-Galerie Dortmund", "type": "other"},
    "domicil Jazzclub (Hansastraße 7-11)": {"id": "domicil-dortmund", "name": "domicil Dortmund", "type": "other"},
}

CONDUCTOR_ROLE_HINTS = ("dirigent", "dirigentin", "leitung", "musikalische leitung", "dirigat")
SOLOIST_ROLE_HINTS = (
    "sopran", "mezzosopran", "mezzo", "alt", "countertenor", "tenor", "bariton", "bass",
    "violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel", "cembalo",
    "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete", "posaune", "tuba",
    "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion", "akkordeon", "marimba",
    "vibraphon", "gesang", "sprecher", "moderation", "rezitation",
)
SKIP_CAST = ("orchester", "philharmoniker", "chor", "ensemble", "band")


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
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(t))).strip()


# --- Kalender-Pass ----------------------------------------------------------

def collect_calendar() -> List[Dict[str, Any]]:
    """Alle Philharmoniker-Aufführungen aus dem Kalender."""
    perfs: List[Dict[str, Any]] = []
    page = 1
    while page <= 40:
        s = http_get(CALENDAR + str(page))
        if not s:
            break
        starts = [m.start() for m in re.finditer(r'id="event-\d+" class="grid event', s)]
        if not starts:
            break
        starts.append(len(s))
        for i in range(len(starts) - 1):
            b = s[starts[i]:starts[i + 1]]
            div = re.search(r'class="event__division"[^>]*>(.*?)</', b, re.DOTALL)
            if not div or "philharmon" not in strip_html(div.group(1)).lower():
                continue
            slug_m = re.search(r'/produktionen/detail/([^/"]+)/', b)
            title_m = re.search(r"<h2[^>]*>(.*?)</h2>", b, re.DOTALL)
            title = strip_html(title_m.group(1)) if title_m else ""
            if title.lower().startswith("öffentliche probe"):
                continue
            mon = re.search(r'event__month">([^<]+)</span>', b)
            day = re.search(r'event__day">([^<]+)</span>', b)
            det = re.search(r'class="event__details">(.*?)</div>', b, re.DOTALL)
            det_html = det.group(1) if det else ""
            venue_m = re.search(r"<span>([^<]+)</span>", det_html)
            time_m = re.search(r"(\d{1,2}:\d{2})\s*Uhr", strip_html(det_html))
            ticket_m = re.search(r'href="(https://ticket\.theaterdo\.de/eventim\.webshop/webticket/shop\?event=\d+)"', b)
            date = ""
            if mon and day:
                parts = strip_html(mon.group(1)).split()
                if len(parts) == 2 and parts[0] in MONTHS:
                    date = f"{parts[1]}-{MONTHS[parts[0]]:02d}-{int(day.group(1)):02d}"
            if not (slug_m and date):
                continue
            perfs.append({
                "slug": slug_m.group(1),
                "title": title,
                "date": date,
                "time": time_m.group(1) if time_m else None,
                "venue": strip_html(venue_m.group(1)) if venue_m else "Konzerthaus",
                "ticket": ticket_m.group(1) if ticket_m else None,
            })
        page += 1
        time.sleep(0.1)
    return perfs


# --- Detail-Pass: Programm + Besetzung -------------------------------------

def _split_br(inner: str) -> List[str]:
    return re.split(r"<br\s*/?>", inner)


_NON_COMPOSER = ("theater", "orchester", "philharmoniker", "chor", "ensemble", "dortmund")


def _looks_like_address(text: str) -> bool:
    return bool(re.search(r"\d{4,5}\s", text)) or "theaterkarree" in text.lower()


def parse_program(detail_html: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Programm-Absatz nach `orange-line--right` (<strong>Komponist</strong> Werk<br>…)."""
    # Kandidaten: jeder <p> unmittelbar nach einem 'orange-line--right'-Marker.
    candidates = []
    for m in re.finditer(r"orange-line--right(.*?)(?:<p>(.*?)</p>)", detail_html, re.DOTALL):
        candidates.append(m.group(2))
    # Fallback: alle <p> mit mehreren <strong>
    if not candidates:
        candidates = [m.group(1) for m in re.finditer(r"<p>(.*?)</p>", detail_html, re.DOTALL)
                      if m.group(1).count("<strong>") >= 2]

    for inner in candidates:
        if "<strong>" not in inner:
            continue
        segs = _split_br(inner)
        pairs: List[Tuple[str, str]] = []
        ok = True
        for seg in segs:
            if not seg.strip():
                continue  # führende/leere Segmente (z. B. <p><br>…) überspringen
            sm = re.match(r"\s*<strong>(.*?)</strong>(.*)", seg, re.DOTALL)
            if not sm:
                if pairs and not re.search(r"<a\b", seg):
                    pairs[-1] = (pairs[-1][0], f"{pairs[-1][1]} {strip_html(seg)}".strip())
                    continue
                ok = False
                break
            rest = sm.group(2)
            if re.match(r"\s*<a\b", rest):  # Besetzung (Rolle + Namenslink) → kein Programm
                ok = False
                break
            comp = strip_html(sm.group(1))
            work = strip_html(rest)
            low = comp.lower()
            # „Komponist" darf keine Werk-Merkmale tragen (Typ C: fette Werke ohne Komponist)
            if (not comp or any(k in low for k in _NON_COMPOSER) or _looks_like_address(work)
                    or re.search(r"\d|op\.", comp) or any(k in low for k in WORK_KEYWORDS)):
                ok = False
                break
            pairs.append((comp, work))
        if ok and pairs and all(len(c.split()) <= 5 for c, _ in pairs):
            return pairs, []
    return [], []


def parse_besetzung(detail_html: str) -> Tuple[List[str], List[str]]:
    """Besetzung-Abschnitt (<strong>Rolle</strong> <a>Name</a>) → (conductors, soloists)."""
    h = detail_html.find("Besetzung</h2>")
    if h < 0:
        return [], []
    scope = detail_html[h:h + 4000]
    conductors: List[str] = []
    soloists: List[str] = []
    # Rolle-Blöcke: <strong>Rolle</strong> ... bis zum nächsten <strong> oder Abschnittsende
    blocks = re.split(r"<strong>", scope)
    for blk in blocks[1:]:
        rm = re.match(r"(.*?)</strong>(.*)", blk, re.DOTALL)
        if not rm:
            continue
        role = strip_html(rm.group(1)).lower()
        body = rm.group(2)
        body = body.split("</p>")[0].split("</div>")[0]
        names = [strip_html(a) for a in re.findall(r"<a\b[^>]*>(.*?)</a>", body, re.DOTALL)]
        if not names:
            txt = strip_html(body)
            names = [txt] if txt and len(txt) > 2 else []
        names = [n for n in names if n and not any(k in n.lower() for k in SKIP_CAST)]
        if not names:
            continue
        if any(k in role for k in CONDUCTOR_ROLE_HINTS):
            conductors.extend(names)
        elif any(k in role for k in SOLOIST_ROLE_HINTS):
            soloists.extend(names)
    return conductors, soloists


# --- Normalisierung Werke/Komponist:innen/Personen (wie Bochum) -------------

FOLD = {
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue",
    "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a", "ç": "c", "č": "c", "ć": "c",
    "è": "e", "é": "e", "ê": "e", "ë": "e", "ì": "i", "í": "i", "î": "i", "ï": "i",
    "ñ": "n", "ń": "n", "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ø": "oe",
    "ù": "u", "ú": "u", "û": "u", "š": "s", "ś": "s", "ž": "z", "ź": "z", "ż": "z",
    "ł": "l", "đ": "d", "ð": "d", "þ": "th", "ř": "r", "ě": "e", "ā": "a",
    "ē": "e", "ī": "i", "ō": "o", "ū": "u",
}

COMPOSER_ALIAS = {
    "sergei rachmaninow": "sergej-rachmaninow", "sergei prokofjew": "sergej-prokofjew",
    "igor strawinski": "igor-strawinsky", "pjotr tschaikowsky": "peter-iljitsch-tschaikowsky",
    "piotr tschaikowsky": "peter-iljitsch-tschaikowsky",
}

WORK_KEYWORDS = (
    "sinfonie", "symphonie", "symphony", "sinfonia", "konzert", "concerto", "ouvertüre",
    "ouverture", "vorspiel", "suite", "streichquartett", "quartett", "quintett", "sextett",
    "trio", "sonate", "sonata", "fantasie", "fantaisie", "variationen", "rhapsodie",
    "serenade", "lied", "gesang", "messe", "messa", "requiem", "oratorium", "ballett",
    "poem", "walzer", "tanz", "divertimento", "konzertstück", "toccata", "partita",
    "passacaglia", "fanfare", "valse", "prélude", "nocturne",
)


def _fold(s: str) -> str:
    return "".join(FOLD.get(c, c) for c in s)


def person_id(name: str) -> str:
    s = _fold(name.strip().lower())
    s = "".join(c if (c.isalnum() or c == " ") else " " for c in s)
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
    if any(k in t for k in ("streichquartett", "quartett", "quintett", "sextett", "streichtrio",
                            "klaviertrio", "trio", "sonate", "kammer", "oktett")):
        return "chamber_music"
    if any(k in t for k in ("sinfonie", "symphonie", "symphony", "sinfonia")):
        return "symphony"
    if any(k in t for k in ("konzert für", "klavierkonzert", "violinkonzert", "cellokonzert",
                            "violoncellokonzert", "concerto", "doppelkonzert")):
        return "concerto"
    if any(k in t for k in ("ouvertüre", "ouverture", "vorspiel", "overture")):
        return "overture"
    # „Oper" nur für ganze Opern, nicht für Auszüge/Interludien/Suiten daraus
    if "oper" in t and not any(k in t for k in ("aus der oper", "aus dem", "interlud", "auszug",
                                                "auszüge", "suite", "arie", "szene", "fantasie")):
        return "opera"
    return "other"


_CAT_PATTERNS = [
    ("Opus", r"\bop(?:us|\.)\s*(?:posth\.?\s*)?([\d]+(?:\s*Nr\.?\s*\d+)?[a-z]?)"),
    ("KV", r"\bKV\.?\s*([\d./a-z]+)"),
    ("BWV", r"\bBWV\.?\s*([\d./a-z]+)"),
    ("Hob", r"\bHob\.?\s*([\dIVXLC:.]+)"),
]


def parse_catalogue(title: str) -> Tuple[List[Dict[str, str]], str]:
    cat: List[Dict[str, str]] = []
    cleaned = title
    for system, pat in _CAT_PATTERNS:
        m = re.search(pat, cleaned, re.IGNORECASE)
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

    print("=== Dortmunder Philharmoniker – Ingest 2026/27 ===\n")
    print("1. Kalender laden ...")
    perfs = collect_calendar()
    slugs = sorted({p["slug"] for p in perfs})
    print(f"   {len(perfs)} Philharmoniker-Aufführungen, {len(slugs)} Produktionen")

    events_doc = load(data / "events.json")
    venues_doc = load(data / "venues.json")
    people_doc = load(data / "people.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")

    # --- Venues sicherstellen ---
    venue_ids = {v["id"] for v in venues_doc["venues"]}

    def ensure_venue(label: str) -> str:
        spec = VENUE_MAP.get(label)
        if not spec:
            vid = re.sub(r"[^a-z0-9]+", "-", _fold(label.lower())).strip("-")[:40] + "-dortmund"
            spec = {"id": vid, "name": label, "type": "other"}
        vid = spec["id"]
        if vid not in venue_ids and "name" in spec:
            venues_doc["venues"].append({
                "id": vid, "name": spec["name"], "cityIds": [CITY_ID], "region": None,
                "address": None, "coordinates": None, "website": None,
                "type": spec.get("type", "other"), "institutionId": None,
            })
            venue_ids.add(vid)
        return vid

    # --- Personen / Komponist:innen / Werke ---
    person_ids = {p["id"] for p in people_doc["people"]}

    def ensure_person(name: str) -> Optional[str]:
        clean = re.sub(r"\s+", " ", name).strip(" ,;:.-")
        if not clean or len(clean) < 3:
            return None
        pid = person_id(clean)
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
        cid = person_id(clean)
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

    # --- Detailseiten pro Produktion: Programm + Besetzung ---
    print("\n2. Detailseiten (Programm/Besetzung) laden ...")
    prod: Dict[str, Dict[str, Any]] = {}
    for i, slug in enumerate(slugs, 1):
        html_text = http_get(DETAIL_BASE + slug + "/")
        if not html_text:
            prod[slug] = {"program": [], "conductors": [], "soloists": []}
            continue
        pairs, _ = parse_program(html_text)
        conductors, soloists = parse_besetzung(html_text)
        prog = []
        for comp, title in pairs:
            wid = resolve_work(comp, title)
            if wid:
                prog.append({"workId": wid})
        prod[slug] = {
            "program": prog,
            "conductors": [pid for pid in (ensure_person(n) for n in conductors) if pid],
            "soloists": [pid for pid in (ensure_person(n) for n in soloists) if pid],
        }
        if i % 10 == 0:
            print(f"   [{i}/{len(slugs)}] ...")
        time.sleep(0.1)

    # --- Events bauen ---
    print("\n3. Events bauen ...")
    new_events: List[Dict[str, Any]] = []
    for p in perfs:
        if not (SEASON_START <= p["date"] <= SEASON_END):
            continue
        info = prod.get(p["slug"], {})
        vid = ensure_venue(p["venue"])
        short = re.sub(r"[^a-z0-9]+", "-", p["slug"].lower()).strip("-")[:34]
        eid = f"event-{p['date']}-dortmund-{short}"
        if p["time"]:
            eid = f"{eid}-{p['time'].replace(':', '')}"
        new_events.append({
            "id": eid,
            "title": p["title"],
            "eventType": "concert",
            "date": p["date"],
            "startTime": p["time"],
            "endTime": None,
            "status": "scheduled",
            "ensembleIds": [ENSEMBLE_ID],
            "venueId": vid,
            "cityId": CITY_ID,
            "conductorPersonIds": info.get("conductors", []),
            "soloistPersonIds": info.get("soloists", []),
            "program": info.get("program", []),
            "seriesId": None,
            "description": None,
            "source": {"url": DETAIL_BASE + p["slug"] + "/", "name": SOURCE_NAME, "retrievedAt": RETRIEVED_AT},
            "ticketUrl": p["ticket"],
            "lastVerified": RETRIEVED_AT,
        })

    # eindeutige IDs absichern
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
    print(f"   Alte Dortmund-Events entfernt: {before - len(events_doc['events'])}")
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
