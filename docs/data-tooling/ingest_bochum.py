#!/usr/bin/env python3
"""
Ingest-Skript für die Bochumer Symphoniker, Spielzeit 2026/27.

Quelle:  https://www.bochumer-symphoniker.de/programm/search////0//1  (Paging)
         Daten-Endpunkt: POST /programm?type=1691066967  → JSON {events, pages, ...}
         Detailseiten:   https://www.bochumer-symphoniker.de/programm/detail/<slug>

Umfang: alle Eigenkonzerte der Bochumer Symphoniker (orchestrale Reihen, Kammermusik-
Reihen Camera/Quartett sowie Familien-/Kinderkonzerte). Ausgeschlossen sind Sparten,
die NICHT vom Orchester bestritten werden bzw. nicht am Stammhaus stattfinden:
  - Musikschule (Musikschule Bochum)
  - Musikvermittlung (Saisonvorstellung, Orchesterkurs-Abschluss der Nachwuchsgruppen)
  - Zu Gast (Gastspiele fremder Künstler:innen, z. B. Klavier-Festival Ruhr)
  - BOSY on Tour (auswärtige Gastspiele; Venues nicht im Bestand)
  - Hörprobe (offene Proben/Preview-Formate, keine eigenständigen Konzerte)

Je Aufführungstermin ein Event; Ticket-URLs (Reservix) werden je Termin gesetzt.
Das Programm wird als Freitext in `description` gehalten (keine Werk-ID-Normalisierung),
analog zum Essener-Ingest. Dirigent:innen und Solist:innen werden als Personen angelegt.

Idempotent: entfernt vor dem Schreiben alle Events mit Quell-Host bochumer-symphoniker.de
und Ensemble bochumer-symphoniker und legt sie neu an; Personen werden dublettenfrei
über ihre IDs ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_bochum.py
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

BASE = "https://www.bochumer-symphoniker.de"
SEARCH_ENDPOINT = f"{BASE}/programm?type=1691066967"
DETAIL_BASE = f"{BASE}/programm/detail/"
SOURCE_HOST = "bochumer-symphoniker.de"
SOURCE_NAME = "Bochumer Symphoniker"
ENSEMBLE_ID = "bochumer-symphoniker"
CITY_ID = "bochum"
VENUE_ID = "zeughauskultur-bochum"  # Anneliese Brost Musikforum Ruhr
RETRIEVED_AT = "2026-08-18"

# Sparten, die NICHT aufgenommen werden (Kleinschreibung, Teilstring-Match auf Badge).
EXCLUDE_CATEGORIES = {
    "musikschule",
    "musikvermittlung",
    "zu gast",
    "bosy on tour",
    "hörprobe",
    "hoerprobe",
}

SEASON_START = "2026-08-01"
SEASON_END = "2027-08-31"

MONTHS = {
    "jan": 1, "feb": 2, "mär": 3, "maer": 3, "mrz": 3, "märz": 3, "apr": 4, "mai": 5,
    "jun": 6, "juni": 6, "jul": 7, "juli": 7, "aug": 8, "sep": 9, "sept": 9,
    "okt": 10, "nov": 11, "dez": 12,
}

# Rollen-Erkennung in der Besetzung ("Name, Rolle").
CONDUCTOR_ROLE_HINTS = ("dirigent", "dirigentin", "leitung", "musikalische leitung")
SOLOIST_ROLE_HINTS = (
    "sopran", "mezzosopran", "mezzo", "alt", "countertenor", "tenor", "bariton", "bass",
    "violine", "viola", "violoncello", "cello", "kontrabass", "klavier", "orgel", "cembalo",
    "hammerklavier", "flöte", "floete", "oboe", "klarinette", "fagott", "horn", "trompete",
    "posaune", "tuba", "harfe", "gitarre", "schlagzeug", "schlagwerk", "percussion",
    "akkordeon", "marimba", "vibraphon", "gesang", "sopranistin", "panflöte", "songs",
)
# Tokens, die keine individuellen Solist:innen sind → in description bzw. ignorieren.
SKIP_CAST_HINTS = (
    "symphoniker", "orchester", "chor", "ensemble", "quartett", "band", "compagnie",
    "moderation", "sprecher", "sprecherin", "regie", "choreinstudierung", "choreografie",
    "konzept", "kinderchor", "jugendchor", "tanz",
)


def http_post_json(page: int) -> Dict[str, Any]:
    data = urllib.parse.urlencode({
        "detailPage": "16", "day": "18", "month": "08", "year": "2026",
        "page": str(page), "viewType": "list", "search": "",
    }).encode()
    req = urllib.request.Request(
        SEARCH_ENDPOINT, data=data,
        headers={"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def http_get(url: str) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  ! Fehler {url}: {e}")
        return None


def strip_html(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(t))).strip()


def collect_teasers() -> List[Dict[str, str]]:
    """Alle Listenseiten paginieren; je Teaser (slug, category, title) zurückgeben."""
    first = http_post_json(1)
    pages = first.get("pages") or [1]
    max_page = max(pages) if pages else 1
    seen: Dict[str, Dict[str, str]] = {}

    def parse_fragment(ev: str) -> None:
        for m in re.finditer(
            r'<a href="/programm/detail/([^"]+)"[^>]*class="event-teaser-l">(.*?)</a>',
            ev, re.DOTALL,
        ):
            slug = unescape(m.group(1))
            inner = m.group(2)
            badge = re.search(r'class="badge[^"]*">(.*?)</', inner, re.DOTALL)
            headline = re.search(r'class="headline[^"]*">(.*?)</', inner, re.DOTALL)
            category = strip_html(badge.group(1)) if badge else ""
            title = strip_html(headline.group(1)) if headline else ""
            if slug not in seen:
                seen[slug] = {
                    "slug": slug, "category": category, "title": title,
                    "text": strip_html(inner),
                }

    parse_fragment(first.get("events", ""))
    for p in range(2, max_page + 1):
        d = http_post_json(p)
        parse_fragment(d.get("events", ""))
        time.sleep(0.15)
    return list(seen.values())


def parse_date_time(text: str) -> Optional[Tuple[str, Optional[str]]]:
    """'Do 24. Sept 26 | 20:00 Uhr' → ('2026-09-24', '20:00')."""
    dm = re.search(r"(\d{1,2})\.\s*([A-Za-zäöüÄÖÜ]+)\.?\s*(\d{2})", text)
    if not dm:
        return None
    day = int(dm.group(1))
    mon = MONTHS.get(dm.group(2).lower())
    if not mon:
        return None
    year = 2000 + int(dm.group(3))
    tm = re.search(r"(\d{1,2}):(\d{2})", text)
    time_str = f"{int(tm.group(1)):02d}:{tm.group(2)}" if tm else None
    return f"{year:04d}-{mon:02d}-{day:02d}", time_str


ORCHESTRA_LINE_HINTS = ("bochumer symphoniker", "sinfonieorchester", "symphoniker")
ENSEMBLE_KEYWORDS = (
    "chor", "chöre", "orchester", "quartett", "quintett", "sextett", "trio", "ensemble",
    "band", "consort", "collegium", "capella", "philharmoniker", "sinfoniker", "sinfonietta",
)


def _is_ensemble_line(text: str) -> bool:
    return any(k in text.lower() for k in ENSEMBLE_KEYWORDS)


def _richtext_columns(s: str) -> Dict[str, str]:
    """Labels (Programm/Mit/Beschreibung) → richtext-HTML aus #ceventTextColumns."""
    cols: Dict[str, str] = {}
    block = re.search(r'id="ceventTextColumns"(.*?)(?:id="cevent|<footer|\Z)', s, re.DOTALL)
    scope = block.group(1) if block else s
    for m in re.finditer(
        r'<span>([^<]+)</span></h2></div>\s*<div class="richtext">(.*?)</div>',
        scope, re.DOTALL,
    ):
        cols[strip_html(m.group(1))] = m.group(2)
    return cols


def _split_lines(richtext_html: str) -> List[Tuple[str, bool]]:
    """richtext → Liste (Textzeile, war_strong)."""
    parts = re.split(r'<br\s*/?>|</p>\s*<p>|</p>|<p[^>]*>', richtext_html)
    out: List[Tuple[str, bool]] = []
    for p in parts:
        is_strong = "<strong>" in p
        text = strip_html(p)
        if text and text != "\xa0":
            out.append((text, is_strong))
    return out


def _split_names(field: str) -> List[str]:
    """'Esiona Stefani und Jiwon Kim' → ['Esiona Stefani', 'Jiwon Kim']."""
    parts = re.split(r"\s+und\s+|\s*&\s*|\s*/\s*", field.strip())
    return [p.strip(" ,;:.-") for p in parts if p.strip(" ,;:.-")]


def _role_hit(text: str, hints: Tuple[str, ...]) -> bool:
    """Rollenwort als ganzes Wort (inkl. Plural 'en/n/s') in text finden."""
    tl = text.lower()
    return any(re.search(rf"\b{re.escape(h)}(?:en|n|s)?\b", tl) for h in hints)


def _seg_is_role(seg: str) -> bool:
    """True, wenn ein Komma-Segment eine Rolle (Instrument/Stimme/Leitung) ist."""
    return _role_hit(seg, CONDUCTOR_ROLE_HINTS + SOLOIST_ROLE_HINTS)


def parse_detail(html_text: str) -> Dict[str, Any]:
    s = html_text

    # Aufführungen: primär aus dem #ceventTickets-Block (mehrere Termine), sonst aus dem
    # Hero-Ticket-Button mit title="… | … Uhr" (Kammerkonzerte mit nur einem Termin).
    perf_by_url: Dict[str, Tuple[str, Optional[str]]] = {}
    tickets = re.search(r'id="ceventTickets"(.*?)(?:id="cevent|<footer|\Z)', s, re.DOTALL)
    if tickets:
        for m in re.finditer(
            r'<a\s+href="(https://[^"]*reservix[^"]+)"[^>]*class="date"[^>]*>(.*?)</a>',
            tickets.group(1), re.DOTALL,
        ):
            href, inner = m.group(1), m.group(2)
            dm = re.search(r'class="date">([^<]+)</div>', inner)
            tm = re.search(r'class="time">([^<]+)</div>', inner)
            dt = parse_date_time(f"{strip_html(dm.group(1)) if dm else ''} {strip_html(tm.group(1)) if tm else ''}")
            if dt and href not in perf_by_url:
                perf_by_url[href] = dt
    # Fallback / Ergänzung: Hero-Buttons mit title-Attribut
    for m in re.finditer(r'<a\s+href="(https://[^"]*reservix[^"]+)"[^>]*title="([^"]+)"', s):
        href = m.group(1)
        if href in perf_by_url:
            continue
        dt = parse_date_time(unescape(m.group(2)))
        if dt:
            perf_by_url[href] = dt

    perfs: List[Tuple[str, str, Optional[str]]] = [
        (u, d, t) for u, (d, t) in perf_by_url.items()
    ]

    is_saal = ("Kleiner Saal" in s) or ("Großer Saal" in s)
    venue_hint = "Kleiner Saal" if "Kleiner Saal" in s else "Großer Saal"

    cols = _richtext_columns(s)

    program_pairs, program_notes, postponed = _parse_program(cols.get("Programm", ""))

    # Besetzung ("Mit"): Zeilen "Name[, Name…], Rolle[, Rolle…]" bzw. Ensemble-Zeilen.
    conductors: List[str] = []
    soloists: List[str] = []
    extra_ensembles: List[str] = []
    for text, _ in _split_lines(cols.get("Mit", "")):
        low = text.lower()
        if low.startswith("tischgespräch") or low.startswith("einführung"):
            continue
        segs = [x.strip() for x in text.split(",") if x.strip()]
        # Index des ersten Rollen-Segments (Wortgrenzen, um Treffer wie 'alt' in 'Walter' zu meiden)
        role_idx = next((i for i, seg in enumerate(segs) if _seg_is_role(seg)), None)
        if role_idx and role_idx > 0:
            role_all = " ".join(segs[role_idx:]).lower()
            names: List[str] = []
            for ns in segs[:role_idx]:
                if any(h in ns.lower() for h in ORCHESTRA_LINE_HINTS):
                    continue
                names.extend(_split_names(ns))
            is_cond = _role_hit(role_all, CONDUCTOR_ROLE_HINTS)
            is_sol = _role_hit(role_all, SOLOIST_ROLE_HINTS)
            if is_cond:
                conductors.extend(names)
            if is_sol:
                soloists.extend(names)
        else:
            # keine erkennbare Rolle → nur echte Ensembles (Chor/Quartett/…) übernehmen
            if any(h in low for h in ORCHESTRA_LINE_HINTS):
                continue
            if text and _is_ensemble_line(text):
                extra_ensembles.append(text.strip(" :"))

    return {
        "perfs": perfs,
        "is_saal": is_saal,
        "venue_hint": venue_hint,
        "program_pairs": program_pairs,
        "program_notes": program_notes,
        "postponed": postponed,
        "conductors": conductors,
        "soloists": soloists,
        "extra_ensembles": extra_ensembles,
    }


# --- ID-Erzeugung für Personen ---------------------------------------------

FOLD = {
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue",
    "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a", "ç": "c", "č": "c", "ć": "c",
    "è": "e", "é": "e", "ê": "e", "ë": "e", "ì": "i", "í": "i", "î": "i", "ï": "i",
    "ñ": "n", "ń": "n", "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ø": "oe",
    "ù": "u", "ú": "u", "û": "u", "š": "s", "ś": "s", "ž": "z", "ź": "z", "ż": "z",
    "ł": "l", "đ": "d", "ð": "d", "þ": "th", "ř": "r", "ě": "e", "ų": "u", "ā": "a",
    "ē": "e", "ī": "i", "ō": "o", "ū": "u",
}


def person_id(name: str) -> str:
    s = name.strip().lower()
    s = "".join(FOLD.get(c, c) for c in s)
    s = "".join(c if (c.isalnum() or c == " ") else " " for c in s)
    return re.sub(r"\s+", "-", s.strip())


# --- Programm-Parsing & Werk-/Komponist-Normalisierung ---------------------

# Schreibvarianten → bestehende Komponist:innen-IDs.
COMPOSER_ALIAS = {
    "igor strawinski": "igor-strawinsky",
    "sergei rachmaninow": "sergej-rachmaninow",
    "sergei prokofjew": "sergej-prokofjew",
}

# Sätze, die fälschlich als Komponist (fett) erscheinen → keine Werke, ggf. Notiz/Status.
def _is_program_note(text: str) -> bool:
    low = text.lower()
    return (
        len(text.split()) > 6
        or "„" in text
        or any(k in low for k in ("werke von", "musik von", "arrangements", "wird ", "verschoben"))
    )


# Werktyp-Stichwörter: eine Folgezeile OHNE solches Wort ist eine Titel-Fortsetzung
# (Tonart, Beiname, Umbruch), MIT solchem Wort ein eigenständiges Zweitwerk.
WORK_KEYWORDS = (
    "sinfonie", "symphonie", "symphony", "sinfonia", "konzert", "concerto", "ouvertüre",
    "ouverture", "vorspiel", "suite", "streichquartett", "quartett", "quintett", "sextett",
    "trio", "sonate", "sonata", "fantasie", "fantaisie", "variationen", "rhapsodie",
    "rhapsody", "serenade", "lied", "gesang", "messe", "messa", "requiem", "oratorium",
    "ballett", "poem", "poème", "walzer", "tanz", "tänze", "divertimento", "konzertstück",
    "kanon", "präludium", "prelude", "nocturne", "notturno", "arie", "marsch", "polka",
    "capriccio", "elegie", "ballade", "toccata", "partita", "passacaglia", "burleske",
    "images", "danses", "dances", "pièce", "stück", "fanfare", "valse",
)


def _has_work_keyword(text: str) -> bool:
    low = "".join(FOLD.get(c, c) for c in text.lower())
    return any(k in low for k in (("".join(FOLD.get(c, c) for c in w)) for w in WORK_KEYWORDS))


def _parse_program(richtext_html: str) -> Tuple[List[Tuple[str, str]], List[str], bool]:
    """richtext → (Liste (Komponist, Werk), Notizen, verschoben?)."""
    pairs: List[Tuple[str, str]] = []
    notes: List[str] = []
    postponed = False
    current: Optional[str] = None
    has_work = False  # bereits ein Werk für die aktuelle Komponistin/den aktuellen Komponisten?
    for text, is_strong in _split_lines(richtext_html):
        if is_strong:
            if _is_program_note(text):
                notes.append(text)
                if "verschoben" in text.lower():
                    postponed = True
                current = None
            else:
                current = text.strip().strip(":").strip()
                has_work = False
        else:
            is_continuation = pairs and (
                text.startswith("(")
                or re.fullmatch(r"[»„][^»«“”]*[«“”]", text.strip())
                or (has_work and not _has_work_keyword(text))
            )
            if is_continuation:
                pairs[-1] = (pairs[-1][0], f"{pairs[-1][1]} {text}".strip())
            elif current:
                pairs.append((current, text.strip()))
                has_work = True
            elif _is_program_note(text):
                notes.append(text)
                if "verschoben" in text.lower():
                    postponed = True
    return pairs, notes, postponed


def clean_composer_name(name: str) -> str:
    name = re.sub(r"\s*\((Sohn|Vater)\)", "", name).strip().strip(":").strip()
    return re.sub(r"\s+", " ", name)


# Genre-Heuristik (kontrollierte Werte) aus dem Werktitel.
def infer_genre(title: str) -> str:
    t = title.lower()
    if "requiem" in t:
        return "requiem"
    if any(k in t for k in ("oratorium", "weihnachtsoratorium", "messe", "messa", "passion",
                            "te deum", "gloria", "stabat mater", "kantate")):
        return "oratorio"
    if any(k in t for k in ("streichquartett", "quartett", "quintett", "sextett", "streichtrio",
                            "klaviertrio", "trio", "sonate", "kammer", "oktett", "nonett")):
        return "chamber_music"
    if any(k in t for k in ("sinfonie", "symphonie", "symphony")):
        return "symphony"
    if any(k in t for k in ("konzert für", "klavierkonzert", "violinkonzert", "cellokonzert",
                            "concerto", "konzert nr", "doppelkonzert")):
        return "concerto"
    if any(k in t for k in ("ouvertüre", "ouverture", "vorspiel", "overture")):
        return "overture"
    if "oper" in t:
        return "opera"
    return "other"


# Katalog-Nummern (nur eindeutige Systeme) aus dem Titel ziehen + aus Titel entfernen.
_CAT_PATTERNS = [
    ("Opus", r"\bop(?:us|\.)\s*(?:posth\.?\s*)?([\dA-Za-z/]+(?:\s*Nr\.?\s*\d+)?)"),
    ("KV", r"\bKV\.?\s*([\d./a-z]+)"),
    ("BWV", r"\bBWV\.?\s*([\d./a-z]+)"),
]


def parse_catalogue(title: str) -> Tuple[List[Dict[str, str]], str]:
    cat: List[Dict[str, str]] = []
    cleaned = title
    for system, pat in _CAT_PATTERNS:
        m = re.search(pat, cleaned, re.IGNORECASE)
        if m:
            cat.append({"system": system, "number": m.group(1).strip()})
            cleaned = (cleaned[: m.start()] + cleaned[m.end():]).strip(" ,;")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;")
    return cat, cleaned


def norm_title(title: str) -> str:
    t = title.lower()
    t = "".join(FOLD.get(c, c) for c in t)
    t = t.replace("symphonie", "sinfonie")
    t = re.sub(r"\bop(?:us|\.)?\s*[\dA-Za-z/]+", "", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    print("=== Bochumer Symphoniker – Ingest 2026/27 ===\n")
    print("1. Listenseiten laden ...")
    teasers = collect_teasers()
    print(f"   {len(teasers)} Einträge im Kalender")

    included = [t for t in teasers if t["category"].strip().lower() not in EXCLUDE_CATEGORIES]
    excluded = [t for t in teasers if t not in included]
    print(f"   {len(included)} aufgenommen, {len(excluded)} ausgeschlossen "
          f"(Sparten: {sorted({t['category'] for t in excluded})})")

    events_doc = load(data / "events.json")
    people_doc = load(data / "people.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")
    person_ids = {p["id"] for p in people_doc["people"]}

    def ensure_person(name: str) -> Optional[str]:
        clean = re.sub(r"\s+", " ", name).strip(" ,;:.-")
        if not clean or len(clean) < 3:
            return None
        pid = person_id(clean)
        if not pid:
            return None
        if pid not in person_ids:
            people_doc["people"].append({"id": pid, "name": clean})
            person_ids.add(pid)
        return pid

    # Komponist:innen: Name→ID (Bestand + Alias); neue werden mit life=null angelegt.
    composer_ids = {c["id"] for c in composers_doc["composers"]}
    composer_by_norm = {
        "".join(FOLD.get(ch, ch) for ch in c["name"].lower()): c["id"]
        for c in composers_doc["composers"]
    }

    def ensure_composer(name: str) -> Optional[str]:
        clean = clean_composer_name(name)
        if not clean:
            return None
        low = clean.lower()
        if low in COMPOSER_ALIAS:
            return COMPOSER_ALIAS[low]
        key = "".join(FOLD.get(ch, ch) for ch in low)
        if key in composer_by_norm:
            return composer_by_norm[key]
        cid = person_id(clean)
        if cid not in composer_ids:
            composers_doc["composers"].append({"id": cid, "name": clean, "life": None})
            composer_ids.add(cid)
        composer_by_norm[key] = cid
        return cid

    # Werke: (composerId, norm_title)→ID; Bestand indexieren, neue anlegen.
    work_ids = {w["id"] for w in works_doc["works"]}
    work_by_key = {
        (w["composerId"], norm_title(w["title"])): w["id"] for w in works_doc["works"]
    }

    def resolve_work(comp_name: str, raw_title: str) -> Optional[str]:
        cid = ensure_composer(comp_name)
        title = re.sub(r"\s+", " ", raw_title).strip(" ,;")
        if not cid or not title:
            return None
        catalogue, cleaned_title = parse_catalogue(title)
        cleaned_title = cleaned_title or title
        key = (cid, norm_title(cleaned_title))
        if key in work_by_key:
            return work_by_key[key]
        stem = cid.split("-")[-1]
        slug = re.sub(r"[^a-z0-9]+", "-", norm_title(cleaned_title)).strip("-")[:40]
        wid = f"{stem}-{slug}" if slug else stem
        base, n = wid, 2
        while wid in work_ids and work_by_key.get(key) != wid:
            wid = f"{base}-{n}"; n += 1
        if wid not in work_ids:
            works_doc["works"].append({
                "id": wid,
                "composerId": cid,
                "title": cleaned_title,
                "catalogue": catalogue,
                "yearComposed": None,
                "genre": infer_genre(cleaned_title),
                "durationMinutes": None,
                "version": None,
                "scoring": None,
                "description": None,
            })
            work_ids.add(wid)
        work_by_key[key] = wid
        return wid

    print("\n2. Detailseiten parsen ...")
    new_events: List[Dict[str, Any]] = []
    skipped_no_date: List[str] = []

    for i, t in enumerate(included, 1):
        slug = t["slug"]
        html_text = http_get(DETAIL_BASE + slug)
        if not html_text:
            continue
        info = parse_detail(html_text)
        perfs = info["perfs"]
        if not perfs:
            # Kein Reservix-Ticket: Konzerte im Musikforum-Saal dennoch mit Datum aus dem
            # Teaser aufnehmen (ticketUrl=None). Externe Orte (z. B. Open-Air) überspringen.
            dt = parse_date_time(t.get("text", "")) if info["is_saal"] else None
            if dt:
                perfs = [(None, dt[0], dt[1])]
            else:
                skipped_no_date.append(slug)
                continue

        conductor_ids = [pid for pid in (ensure_person(n) for n in info["conductors"]) if pid]
        soloist_ids = [pid for pid in (ensure_person(n) for n in info["soloists"]) if pid]

        # Programm strukturiert (program[].workId)
        program = []
        for comp, title in info["program_pairs"]:
            wid = resolve_work(comp, title)
            if wid:
                program.append({"workId": wid})
        status = "postponed" if info["postponed"] else "scheduled"

        # description: Zusatz-Ensembles (Chöre etc.) + Notizen (z. B. Verschiebung)
        desc_parts = []
        if info["extra_ensembles"]:
            uniq = ", ".join(dict.fromkeys(info["extra_ensembles"]))
            desc_parts.append(f"Mitwirkende Ensembles: {uniq}")
        for note in info["program_notes"]:
            desc_parts.append(note.strip())
        description = " · ".join(desc_parts) or None

        for href, date, start_time in perfs:
            if not (SEASON_START <= date <= SEASON_END):
                continue
            short = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:28]
            eid = f"event-{date}-bochum-{short}"
            if start_time and any(e["id"] == eid for e in new_events):
                eid = f"{eid}-{start_time.replace(':', '')}"
            new_events.append({
                "id": eid,
                "title": t["title"],
                "eventType": "concert",
                "date": date,
                "startTime": start_time,
                "endTime": None,
                "status": status,
                "ensembleIds": [ENSEMBLE_ID],
                "venueId": VENUE_ID,
                "cityId": CITY_ID,
                "conductorPersonIds": conductor_ids,
                "soloistPersonIds": soloist_ids,
                "program": program,
                "seriesId": None,
                "description": description,
                "source": {
                    "url": DETAIL_BASE + slug,
                    "name": SOURCE_NAME,
                    "retrievedAt": RETRIEVED_AT,
                },
                "ticketUrl": href,
                "lastVerified": RETRIEVED_AT,
            })
        if i % 10 == 0:
            print(f"   [{i}/{len(included)}] ...")
        time.sleep(0.15)

    # Doppelte IDs (mehrere Termine gleichen Tags ohne Zeit) absichern
    seen_ids: Dict[str, int] = {}
    for e in new_events:
        if e["id"] in seen_ids:
            seen_ids[e["id"]] += 1
            e["id"] = f"{e['id']}-{seen_ids[e['id']]}"
        else:
            seen_ids[e["id"]] = 1

    print(f"\n   Neue Events: {len(new_events)}")
    if skipped_no_date:
        print(f"   Ohne Termin/Ticket übersprungen ({len(skipped_no_date)}): {skipped_no_date}")

    # 3. Idempotent entfernen + einfügen
    def is_ours(e: Dict[str, Any]) -> bool:
        src = (e.get("source") or {}).get("url", "") or ""
        return SOURCE_HOST in src and ENSEMBLE_ID in e.get("ensembleIds", [])

    before = len(events_doc["events"])
    events_doc["events"] = [e for e in events_doc["events"] if not is_ours(e)]
    print(f"   Alte Bochum-Events entfernt: {before - len(events_doc['events'])}")
    events_doc["events"].extend(new_events)
    events_doc.setdefault("metadata", {})["lastUpdated"] = RETRIEVED_AT

    save(data / "events.json", events_doc)
    save(data / "people.json", people_doc)
    save(data / "composers.json", composers_doc)
    save(data / "works.json", works_doc)
    prog_events = sum(1 for e in new_events if e["program"])
    print(f"\n✓ Ingest abgeschlossen: {len(new_events)} Events ({prog_events} mit Programm), "
          f"{len(people_doc['people'])} Personen, {len(composers_doc['composers'])} Komponist:innen, "
          f"{len(works_doc['works'])} Werke gesamt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
