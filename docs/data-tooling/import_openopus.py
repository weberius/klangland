#!/usr/bin/env python3
"""
Importer für strukturierte Komponist:innen- und Werkdaten aus Open Opus (User Story 017).

Quelle:  Open Opus  https://openopus.org  (Daten unter CC0 / Public Domain)
         API-Doku    https://github.com/openopus-org/openopus_api/blob/master/USAGE.md
         Endpunkte:  /composer/list/search/{name}.json           (Komponist:innen-Suche)
                     /work/list/composer/{id}/genre/all.json     (Werke einer:s Komponist:in)

Open Opus liefert AUSSCHLIESSLICH strukturierte Metadaten (keine Prosa/Biografien).
Angereichert werden – nur wo noch nicht kuratiert vorhanden –:
  * Komponist:in: openOpusId, epoch (deutschsprachig gemappt); Lebensdaten werden gegen
    Open Opus abgeglichen, Abweichungen NUR protokolliert (nicht still überschrieben).
  * Werk:        openOpusId, popular/recommended, ggf. Werkverzeichnis (op.-Nummer),
    sofern das interne `catalogue` leer ist.

Grundsätze:
  * Open Opus ist KEINE Laufzeitabhängigkeit – der Abruf passiert nur bei diesem Skriptlauf.
  * Kein unkontrolliertes Überschreiben: kuratierte Felder (wikipedia, description,
    title, bestehende catalogue/genre/life) bleiben unangetastet. Erneuter Lauf ist idempotent.
  * Schonender Abruf (AK 11): höchstens EIN Request pro Sekunde an denselben Dienst; lokale
    Verarbeitungszeit wird auf das Mindestintervall angerechnet. Roh-Antworten werden unter
    einem gitignorierten Cache-Verzeichnis zwischengespeichert (keine Wiederholungsanfragen).

Deutsche Transliteration mancher Namen (Tschaikowsky, Schostakowitsch …) weicht von der
englischen Open-Opus-Schreibung ab; dafür gibt es eine Alias-Tabelle (SEARCH_ALIASES).
Nicht gematchte oder mehrdeutige Einträge werden am Ende reportet, nicht geraten.

Aufruf:  python3 docs/data-tooling/import_openopus.py [--force] [--no-network]
         --force       vorhandene openOpusId/epoch neu ermitteln (überschreibt sie)
         --no-network  nur aus dem lokalen Cache arbeiten (kein Netzwerkzugriff)
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Konstanten -------------------------------------------------------------

API_BASE = "https://api.openopus.org"
USER_AGENT = "klangland-openopus-importer/1.0 (US-017; https://openopus.org)"
MIN_INTERVAL_SECONDS = 1.0  # AK 11: höchstens ein Request pro Sekunde
REQUEST_TIMEOUT_SECONDS = 30
RETRY_WAITS_SECONDS = [5, 15, 30]  # Backoff bei Drosselung/Timeout (ohne 1-req/s zu unterlaufen)

# Ähnlichkeitsschwellen fürs Matching (0..1).
COMPOSER_MATCH_THRESHOLD = 0.86
# Kuratierte Alias-Suchbegriffe zielen bereits auf eine bestimmte Person; dort genügt eine
# niedrigere Schwelle (deutsche vs. englische Transliteration weicht oft ab).
COMPOSER_MATCH_THRESHOLD_ALIAS = 0.55
WORK_MATCH_THRESHOLD = 0.72

# Open-Opus-Epochen → deutschsprachige Werte (AK 2 / Task 3).
EPOCH_MAP = {
    "Medieval": "Mittelalter",
    "Renaissance": "Renaissance",
    "Baroque": "Barock",
    "Classical": "Klassik",
    "Early Romantic": "Frühromantik",
    "Romantic": "Romantik",
    "Late Romantic": "Spätromantik",
    "20th Century": "20. Jahrhundert",
    "Post-War": "Nachkriegszeit",
    "21st Century": "21. Jahrhundert",
}

# Deutsche Schreibung → Open-Opus-Suchbegriff (englische/originale Schreibung).
# Nur nötig, wo die einfache ASCII-Transliteration nicht trifft.
SEARCH_ALIASES = {
    "sergej-prokofjew": "Prokofiev",
    "peter-iljitsch-tschaikowsky": "Tchaikovsky",
    "pjotr-i-tschaikowski": "Tchaikovsky",
    "pjotr-i-tschaikowsky": "Tchaikovsky",
    "pjotr-tschaikowski": "Tchaikovsky",
    "peter-tschaikowsky": "Tchaikovsky",
    "sergej-rachmaninow": "Rachmaninoff",
    "sergej-w-rachmaninow": "Rachmaninoff",
    "alexander-skrjabin": "Scriabin",
    "igor-strawinsky": "Stravinsky",
    "dmitri-schostakowitsch": "Shostakovich",
    "dmitrij-schostakowitsch": "Shostakovich",
    "dmitri-d-schostakowitsch": "Shostakovich",
    "camille-saint-saens": "Saens",
    "nikolai-rimski-korsakow": "Rimsky",
    "modest-mussorgski": "Mussorgsky",
    "modest-mussorgsky": "Mussorgsky",
    "aram-chatschaturjan": "Khachaturian",
    "dmitri-kabalewski": "Kabalevsky",
    "reinhold-gliere": "Gliere",
    "alexander-borodin": "Borodin",
    "anatoli-ljadow": "Lyadov",
    "nikolai-kapustin": "Kapustin",
    "rodion-schtschedrin": "Shchedrin",
    "alfred-schnittke": "Schnittke",
    "sofia-gubaidulina": "Gubaidulina",
    "michail-iwanowitsch-glinka": "Glinka",
    "anton-arensky": "Arensky",
    "sergei-eduardowitsch-bortkiewicz": "Bortkiewicz",
    "bedrich-smetana": "Smetana",
    "leos-janacek": "Janacek",
    "antonin-dvorak": "Dvorak",
    "bohuslav-martinu": "Martinu",
    "georg-friedrich-haendel": "Handel",
    "felix-mendelssohn-bartholdy": "Mendelssohn",
    "carl-philipp-emanuel-bach": "Carl Philipp Emanuel Bach",
    "carl-philipp-emmanuel-bach": "Carl Philipp Emanuel Bach",
    "johann-christian-bach": "Johann Christian Bach",
    "gyoergy-ligeti": "Ligeti",
    "zoltan-kodaly": "Kodaly",
    "bela-bartok": "Bartok",
    "ernst-von-dohnanyi": "Dohnanyi",
    "george-enescu": "Enescu",
    "isaac-albeniz": "Albeniz",
    "manuel-de-falla": "Falla",
    "heitor-villa-lobos": "Villa",
    "arvo-paert": "Part",
    "erkki-sven-tueuer": "Tuur",
    "peteris-vasks": "Vasks",
    "carl-maria-von-weber": "Weber",
    "jean-sibelius": "Sibelius",
    "edvard-grieg": "Grieg",
    "gabriel-faure": "Faure",
    "cesar-franck": "Franck",
    "maurice-ravel": "Ravel",
    "ottorino-respighi": "Respighi",
    "niccolo-paganini": "Paganini",
    "arcangelo-corelli": "Corelli",
    "jean-baptiste-lully": "Lully",
    "domenico-scarlatti": "Domenico Scarlatti",
    "giuseppe-tartini": "Tartini",
    "tommaso-vitali": "Vitali",
    "arnold-bax": "Bax",
}

# Komponist:innen-IDs, die KEINE echten Personen sind (Sammel-/Platzhaltereinträge in
# composers.json). Diese werden übersprungen und nicht gegen Open Opus gesucht.
SKIP_IDS = {
    "nach-dem-kinderbuch",
    "werke-von-magnus",
    "tzu-ning-erhu-roehrenspiesslaute",
    "daniele-di-renzo",
    "werke-von-viktor-ewald",
    "musikalisches",
    "werke-von-franz-schubert",
    "keita-yamamoto",
    "werke-von-leopold-mozart",
    "n-n-solist-in",
    "das-tagesprogramm-zum-download",
    "projektklassen-b",
    "ein-mix-aus-klassik",
    "werke-von-johann",
    "werke-von-georg-friedrich",
    "reinhold-friedrich",
    "dorothea-stepp",
    "duette-terzette-und",
    "caroline-steiner",
    "charlie-chaplin",
    "kamalini-mukherji-bickram-ghosh",
    "wolfgang-amadeus",
    "eduard-resatsch",
    "erik-satie-claude-debussy",
    "claude-debussy-andre-caplet",
    "eric-idle-john-du-prez",
}


# --- HTTP mit Drosselung & Cache -------------------------------------------

class RateLimiter:
    """Sorgt für mindestens MIN_INTERVAL_SECONDS zwischen zwei Netzwerk-Requests (AK 11)."""

    def __init__(self, min_interval: float) -> None:
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self) -> None:
        gap = self.min_interval - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()


class Fetcher:
    """Rate-limitierter, gecachter GET auf die Open-Opus-API."""

    def __init__(self, cache_dir: Path, *, offline: bool, verbose: bool) -> None:
        self.cache_dir = cache_dir
        self.offline = offline
        self.verbose = verbose
        self.limiter = RateLimiter(MIN_INTERVAL_SECONDS)
        self.network_calls = 0
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, url: str) -> Path:
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", url.replace(API_BASE + "/", ""))
        return self.cache_dir / f"{slug}.json"

    def get_json(self, url: str) -> Optional[Dict[str, Any]]:
        cache_path = self._cache_path(url)
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                cache_path.unlink(missing_ok=True)  # kaputten Cache verwerfen

        if self.offline:
            return None

        payload = self._request_with_backoff(url)
        if payload is not None:
            cache_path.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
        return payload

    def _request_with_backoff(self, url: str) -> Optional[Dict[str, Any]]:
        for attempt, extra_wait in enumerate([0, *RETRY_WAITS_SECONDS]):
            if extra_wait:
                time.sleep(extra_wait)
            self.limiter.wait()  # 1-req/s-Grenze gilt für JEDEN Versuch
            self.network_calls += 1
            if self.verbose:
                print(f"    → GET {url}  (t={time.monotonic():.1f}s)")
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                if error.code in (429, 500, 502, 503, 504) and attempt < len(RETRY_WAITS_SECONDS):
                    print(f"    … {error.code} für {url}, erneuter Versuch")
                    continue
                if error.code == 404:
                    return None
                print(f"    ! HTTP {error.code} für {url}", file=sys.stderr)
                return None
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
                if attempt < len(RETRY_WAITS_SECONDS):
                    print(f"    … Fehler ({error}) für {url}, erneuter Versuch")
                    continue
                print(f"    ! Abbruch für {url}: {error}", file=sys.stderr)
                return None
        return None


# --- Normalisierung & Matching ---------------------------------------------

def strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    """Kleinschreibung, ohne Diakritika, nur alphanumerisch + Leerzeichen."""
    text = strip_diacritics(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def surname(name: str) -> str:
    """Letztes Namenswort als Suchbegriff (Open-Opus-Suche ist Substring-basiert)."""
    tokens = [t for t in re.split(r"[\s.]+", name.strip()) if t]
    return tokens[-1] if tokens else name


def year_from_date(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    match = re.match(r"(\d{3,4})", date_str)
    return int(match.group(1)) if match else None


# --- Komponist:innen-Import -------------------------------------------------

def match_composer(
    fetcher: Fetcher, composer: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Sucht den passenden Open-Opus-Komponisten; None wenn kein sicherer Treffer."""
    name = composer["name"]
    alias = SEARCH_ALIASES.get(composer["id"])
    query = alias if alias else surname(name)
    url = f"{API_BASE}/composer/list/search/{urllib.parse.quote(query)}.json"
    payload = fetcher.get_json(url)
    if not payload:
        return None
    candidates = payload.get("composers") or []
    if not candidates:
        return None

    latin_name = strip_diacritics(name)
    best, best_score = None, 0.0
    for cand in candidates:
        complete = cand.get("complete_name", "")
        score = max(
            similarity(name, complete),
            similarity(latin_name, complete),
            similarity(surname(name), surname(complete)),
        )
        # Lebensdaten als Tie-Breaker/Bestätigung.
        life = composer.get("life") or {}
        birth = year_from_date(cand.get("birth"))
        if life.get("from") and birth and abs(life["from"] - birth) <= 1:
            score += 0.05
        if score > best_score:
            best, best_score = cand, score
    threshold = COMPOSER_MATCH_THRESHOLD_ALIAS if alias else COMPOSER_MATCH_THRESHOLD
    if best is not None and best_score >= threshold:
        return best
    return None


def enrich_composer(
    composer: Dict[str, Any],
    match: Dict[str, Any],
    *,
    force: bool,
    report: Dict[str, list],
) -> bool:
    """Trägt openOpusId/epoch nach und prüft Lebensdaten. True bei Änderung."""
    changed = False

    if force or not composer.get("openOpusId"):
        if composer.get("openOpusId") != match["id"]:
            composer["openOpusId"] = match["id"]
            changed = True

    if force or not composer.get("epoch"):
        raw_epoch = match.get("epoch")
        if raw_epoch:
            mapped = EPOCH_MAP.get(raw_epoch)
            if mapped is None:
                mapped = raw_epoch
                report["unknown_epochs"].append(f"{composer['name']}: {raw_epoch}")
            if composer.get("epoch") != mapped:
                composer["epoch"] = mapped
                changed = True

    # Lebensdaten abgleichen – NUR protokollieren, nicht überschreiben (AK 2/6).
    life = composer.get("life") or {}
    oo_birth = year_from_date(match.get("birth"))
    oo_death = year_from_date(match.get("death"))
    if life.get("from") and oo_birth and abs(life["from"] - oo_birth) > 1:
        report["life_diffs"].append(
            f"{composer['name']}: birth lokal {life['from']} ↔ Open Opus {oo_birth}"
        )
    if life.get("to") and oo_death and abs(life["to"] - oo_death) > 1:
        report["life_diffs"].append(
            f"{composer['name']}: death lokal {life['to']} ↔ Open Opus {oo_death}"
        )

    return changed


# --- Werk-Import ------------------------------------------------------------

OPUS_RE = re.compile(r"\bop\.?\s*(\d+[a-z]?)(?:\s*,?\s*no\.?\s*(\d+))?", re.IGNORECASE)


def parse_catalogue(oo_title: str) -> List[Dict[str, str]]:
    """Extrahiert eine op.-Nummer aus einem Open-Opus-Titel (konservativ)."""
    match = OPUS_RE.search(oo_title)
    if not match:
        return []
    number = match.group(1)
    if match.group(2):
        number = f"{number} Nr. {match.group(2)}"
    return [{"system": "Opus", "number": number}]


def enrich_works(
    works_for_composer: List[Dict[str, Any]],
    oo_works: List[Dict[str, Any]],
    *,
    force: bool,
    report: Dict[str, list],
) -> int:
    """Matcht lokale Werke gegen Open-Opus-Werke; gibt Anzahl geänderter Werke zurück."""
    changed_count = 0
    for work in works_for_composer:
        if work.get("openOpusId") and not force:
            continue
        title = work["title"]
        best, best_score = None, 0.0
        for oo in oo_works:
            oo_title = oo.get("title", "")
            oo_full = f"{oo_title} {oo.get('subtitle', '')}".strip()
            score = max(similarity(title, oo_title), similarity(title, oo_full))
            if score > best_score:
                best, best_score = oo, score
        if best is None or best_score < WORK_MATCH_THRESHOLD:
            report["unmatched_works"].append(f"{work['id']} – {title}")
            continue

        work_changed = False
        if work.get("openOpusId") != best["id"]:
            work["openOpusId"] = best["id"]
            work_changed = True
        popular = best.get("popular") in ("1", 1, True)
        recommended = best.get("recommended") in ("1", 1, True)
        if work.get("popular") != popular:
            work["popular"] = popular
            work_changed = True
        if work.get("recommended") != recommended:
            work["recommended"] = recommended
            work_changed = True
        # Werkverzeichnis nur ergänzen, wenn lokal leer (kein Überschreiben, AK 6).
        if not work.get("catalogue"):
            cat = parse_catalogue(best.get("title", ""))
            if cat:
                work["catalogue"] = cat
                work_changed = True

        if work_changed:
            changed_count += 1
    return changed_count


# --- I/O --------------------------------------------------------------------

def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Importiert Open-Opus-Metadaten (US-017).")
    parser.add_argument("--force", action="store_true",
                        help="Vorhandene openOpusId/epoch/Werk-IDs neu ermitteln.")
    parser.add_argument("--no-network", action="store_true",
                        help="Nur aus lokalem Cache arbeiten (kein Netzwerkzugriff).")
    parser.add_argument("--verbose", action="store_true", help="Request-Zeitstempel loggen.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    data_dir = repo / "data"
    composers_path = data_dir / "composers.json"
    works_path = data_dir / "works.json"
    cache_dir = Path(__file__).resolve().parent / ".cache" / "openopus"

    composers_doc = load(composers_path)
    works_doc = load(works_path)
    composers = composers_doc["composers"]
    works = works_doc["works"]

    works_by_composer: Dict[str, List[Dict[str, Any]]] = {}
    for work in works:
        works_by_composer.setdefault(work["composerId"], []).append(work)

    fetcher = Fetcher(cache_dir, offline=args.no_network, verbose=args.verbose)
    report: Dict[str, list] = {
        "matched": [], "unmatched_composers": [], "skipped": [],
        "unknown_epochs": [], "life_diffs": [], "unmatched_works": [],
    }

    composers_changed = 0
    works_changed = 0

    for composer in composers:
        if composer["id"] in SKIP_IDS:
            report["skipped"].append(composer["name"])
            continue

        match = match_composer(fetcher, composer)
        if match is None:
            report["unmatched_composers"].append(f"{composer['id']} – {composer['name']}")
            continue

        report["matched"].append(f"{composer['name']} → OO {match['id']} ({match.get('complete_name')})")
        if enrich_composer(composer, match, force=args.force, report=report):
            composers_changed += 1

        # Werke dieser:s Komponist:in nur laden, wenn es lokale Werke gibt.
        local_works = works_by_composer.get(composer["id"], [])
        if not local_works:
            continue
        url = f"{API_BASE}/work/list/composer/{match['id']}/genre/all.json"
        oo_payload = fetcher.get_json(url)
        oo_works = (oo_payload or {}).get("works") or []
        if oo_works:
            works_changed += enrich_works(
                local_works, oo_works, force=args.force, report=report
            )

    if composers_changed:
        composers_doc["metadata"]["lastUpdated"] = "2026-08-21"
        save(composers_path, composers_doc)
    if works_changed:
        works_doc["metadata"]["lastUpdated"] = "2026-08-21"
        save(works_path, works_doc)

    # --- Report ------------------------------------------------------------
    print("\n=== Open-Opus-Import: Report ===")
    print(f"Komponist:innen gematcht : {len(report['matched'])}")
    print(f"  davon geändert         : {composers_changed}")
    print(f"Komponist:innen ohne Match: {len(report['unmatched_composers'])}")
    print(f"Übersprungen (Platzhalter): {len(report['skipped'])}")
    print(f"Werke geändert           : {works_changed}")
    print(f"Werke ohne Match         : {len(report['unmatched_works'])}")
    print(f"Netzwerk-Requests        : {fetcher.network_calls}")

    if report["life_diffs"]:
        print("\n-- Lebensdaten-Abweichungen (nur protokolliert) --")
        for line in report["life_diffs"]:
            print(f"  ! {line}")
    if report["unknown_epochs"]:
        print("\n-- Unbekannte Epochen (Rohwert übernommen) --")
        for line in report["unknown_epochs"]:
            print(f"  ? {line}")
    if report["unmatched_composers"]:
        print("\n-- Komponist:innen ohne Open-Opus-Match --")
        for line in report["unmatched_composers"]:
            print(f"  - {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
