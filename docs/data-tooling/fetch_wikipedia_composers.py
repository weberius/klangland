#!/usr/bin/env python3
"""
Wikipedia-Quellensammler für die kuratierten Komponist:innen-Kurzfassungen (User Story 017).

Zweck:  Sammelt für die real existierenden Komponist:innen in data/composers.json den passenden
        deutschsprachigen Wikipedia-Artikel (kanonischer Titel, URL) samt Intro-Auszug als
        *Recherchegrundlage*. Das Skript SCHREIBT NICHTS in composers.json – die eigentlichen
        `wikipedia.summary`-Kurzfassungen (~60 Wörter) werden daraus eigenständig formuliert und
        kuratiert eingetragen (kein wörtlicher Auszug; AK 4).

Quelle:  Wikipedia (de)  REST-Summary  https://de.wikipedia.org/api/rest_v1/page/summary/{titel}
                         Such-API      https://de.wikipedia.org/w/api.php (list=search)

Schonender Abruf (AK 11):  höchstens EIN Request pro Sekunde an de.wikipedia.org; lokale
        Verarbeitungszeit wird angerechnet. Roh-Antworten werden gitignoriert gecacht, damit
        erneute Läufe die Server nicht belasten.

Ergebnis:  docs/data-tooling/.cache/wikipedia/candidates.json
           { composerId: { name, title, url, extract, type } }
        sowie ein Report (gefunden / nicht gefunden / mehrdeutig) auf stdout.

Aufruf:  python3 docs/data-tooling/fetch_wikipedia_composers.py [--no-network]
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

# Alias-Tabelle aus dem Open-Opus-Importer (Platzhalter-/Sammeleinträge überspringen).
from import_openopus import SKIP_IDS  # type: ignore

WIKI_BASE = "https://de.wikipedia.org"
USER_AGENT = "klangland-wikipedia-collector/1.0 (US-017; https://openopus.org contact: klangland)"
MIN_INTERVAL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 30
RETRY_WAITS_SECONDS = [5, 15, 30]

# Direkte Titel-Overrides, wo der Personenname allein nicht auf den Artikel führt
# (Mehrdeutigkeit) oder abweichend geschrieben ist.
TITLE_OVERRIDES = {
    "peter-iljitsch-tschaikowsky": "Pjotr Iljitsch Tschaikowski",
    "pjotr-i-tschaikowski": "Pjotr Iljitsch Tschaikowski",
    "pjotr-i-tschaikowsky": "Pjotr Iljitsch Tschaikowski",
    "pjotr-tschaikowski": "Pjotr Iljitsch Tschaikowski",
    "peter-tschaikowsky": "Pjotr Iljitsch Tschaikowski",
    "sergej-prokofjew": "Sergei Sergejewitsch Prokofjew",
    "alexander-skrjabin": "Alexander Nikolajewitsch Skrjabin",
    "sergej-rachmaninow": "Sergei Wassiljewitsch Rachmaninow",
    "dmitri-schostakowitsch": "Dmitri Dmitrijewitsch Schostakowitsch",
    "nikolai-rimski-korsakow": "Nikolai Andrejewitsch Rimski-Korsakow",
    "modest-mussorgski": "Modest Petrowitsch Mussorgski",
    "aram-chatschaturjan": "Aram Iljitsch Chatschaturjan",
    "johann-strauss": "Johann Strauss (Sohn)",
    "michael-haydn": "Michael Haydn",
    "carl-philipp-emanuel-bach": "Carl Philipp Emanuel Bach",
    "johann-christian-bach": "Johann Christian Bach",
    "franz-schmidt": "Franz Schmidt (Komponist)",
    "john-adams": "John Adams (Komponist)",
    "george-onslow": "George Onslow (Komponist)",
    "john-williams": "John Williams (Komponist)",
    "leroy-anderson": "Leroy Anderson",
    "manuel-ponce": "Manuel María Ponce",
    "alexander-borodin": "Alexander Porfirjewitsch Borodin",
    "toro-takemitsu": "Tōru Takemitsu",
    "j-bodin-de-boismortier": "Joseph Bodin de Boismortier",
    "tommaso-vitali": "Tomaso Antonio Vitali",
    "louise-aldolpha-le-beau": "Luise Adolpha Le Beau",
}

# Komponist:innen-IDs, deren automatische Suche NUR Fehltreffer lieferte (Listen-/Chronikseiten
# oder gleichnamige andere Personen) und für die es keinen geeigneten de-Wikipedia-Personenartikel
# gibt. Werden nicht als Kandidaten ausgegeben (manuell verifiziert, US-017).
NO_ARTICLE_IDS = {
    "ian-clarke", "oskar-jockel", "vassos-nicolaou", "jona-kuemper", "wang-jue",
    "john-cheetham", "ladislas-de-rohozinski", "gabriel-kahane", "courtney-bryan",
    "jp-jofre", "mark-kaminski", "allan-stephenson", "geoffrey-keating",
    "evelyn-klaunzer", "sergiu-natra", "enea-cavallo", "thorsten-schmid-kapfenburg",
    "andrew-lippa", "sally-beamish", "libby-larsen", "carl-philipp-emmanuel-bach",
    "jim-parker",
}


class Fetcher:
    def __init__(self, cache_dir: Path, *, offline: bool) -> None:
        self.cache_dir = cache_dir
        self.offline = offline
        self._last = 0.0
        self.network_calls = 0
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _wait(self) -> None:
        gap = MIN_INTERVAL_SECONDS - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()

    def _cache_path(self, key: str) -> Path:
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", key)[:180]
        return self.cache_dir / f"{slug}.json"

    def get_json(self, url: str, cache_key: str) -> Optional[Dict[str, Any]]:
        cache_path = self._cache_path(cache_key)
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                cache_path.unlink(missing_ok=True)
        if self.offline:
            return None
        payload = self._request(url)
        if payload is not None:
            cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return payload

    def _request(self, url: str) -> Optional[Dict[str, Any]]:
        for attempt, extra in enumerate([0, *RETRY_WAITS_SECONDS]):
            if extra:
                time.sleep(extra)
            self._wait()
            self.network_calls += 1
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    return None
                if error.code in (429, 500, 502, 503, 504) and attempt < len(RETRY_WAITS_SECONDS):
                    continue
                print(f"    ! HTTP {error.code} für {url}", file=sys.stderr)
                return None
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
                if attempt < len(RETRY_WAITS_SECONDS):
                    continue
                print(f"    ! Abbruch {url}: {error}", file=sys.stderr)
                return None
        return None


def summary_for_title(fetcher: Fetcher, title: str) -> Optional[Dict[str, Any]]:
    quoted = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"{WIKI_BASE}/api/rest_v1/page/summary/{quoted}"
    return fetcher.get_json(url, f"summary_{title}")


def search_title(fetcher: Fetcher, name: str) -> Optional[str]:
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "list": "search",
        "srsearch": f"{name} Komponist", "srlimit": "1", "srnamespace": "0",
    })
    url = f"{WIKI_BASE}/w/api.php?{params}"
    payload = fetcher.get_json(url, f"search_{name}")
    hits = ((payload or {}).get("query") or {}).get("search") or []
    return hits[0]["title"] if hits else None


def resolve(fetcher: Fetcher, composer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Ermittelt Artikel (Titel/URL/Auszug) für eine:n Komponist:in; None wenn nichts Sinnvolles."""
    candidates = []
    if composer["id"] in TITLE_OVERRIDES:
        candidates.append(TITLE_OVERRIDES[composer["id"]])
    candidates.append(composer["name"])

    for title in candidates:
        data = summary_for_title(fetcher, title)
        if data and data.get("type") == "standard" and data.get("extract"):
            return data

    # Fallback: Volltextsuche → Titel → Summary.
    found = search_title(fetcher, composer["name"])
    if found:
        data = summary_for_title(fetcher, found)
        if data and data.get("type") == "standard" and data.get("extract"):
            return data
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Sammelt Wikipedia-Quellen für Komponist:innen (US-017).")
    parser.add_argument("--no-network", action="store_true", help="Nur aus dem Cache arbeiten.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    composers = json.loads((repo / "data" / "composers.json").read_text(encoding="utf-8"))["composers"]
    cache_dir = Path(__file__).resolve().parent / ".cache" / "wikipedia"
    fetcher = Fetcher(cache_dir, offline=args.no_network)

    candidates: Dict[str, Any] = {}
    not_found = []
    for composer in composers:
        if composer["id"] in SKIP_IDS or composer["id"] in NO_ARTICLE_IDS:
            continue
        data = resolve(fetcher, composer)
        title = (data or {}).get("title", "") or ""
        # Sicherheitsnetz: Listen-/Chronikseiten sind keine Personenartikel.
        if data and (title.startswith("Liste ") or title == "Chronik der Komponisten"):
            data = None
        if not data:
            not_found.append(f"{composer['id']} – {composer['name']}")
            continue
        candidates[composer["id"]] = {
            "name": composer["name"],
            "title": data.get("title"),
            "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
            "extract": data.get("extract"),
            "description": data.get("description"),
        }

    out_path = cache_dir / "candidates.json"
    out_path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\n=== Wikipedia-Quellen: Report ===")
    print(f"Kandidaten gefunden : {len(candidates)}")
    print(f"Ohne Artikel        : {len(not_found)}")
    print(f"Netzwerk-Requests   : {fetcher.network_calls}")
    print(f"Ausgabe             : {out_path.relative_to(repo)}")
    if not_found:
        print("\n-- Ohne geeigneten Artikel --")
        for line in not_found:
            print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
