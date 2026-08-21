#!/usr/bin/env python3
"""
Portrait-Beschaffung für die programmierten Komponist:innen (User Story 024).

Zweck:  Ermittelt zu den Komponist:innen in data/composers.json ein führendes Portrait aus
        Wikipedia/Wikimedia Commons, lädt es herunter und legt es als committetes Projekt-Asset
        unter data/portraits/<composerId>.<ext> ab. Anschließend wird das Feld
        ``portrait`` = { file, source, credit } in data/composers.json gesetzt. Die Webanwendung
        bindet ausschließlich diese lokalen Dateien ein und ruft zur Laufzeit KEINE Fremd-URLs ab.

Quelle:  Wikipedia (de)  REST-Summary  https://de.wikipedia.org/api/rest_v1/page/summary/{titel}
                          → führendes Bild (originalimage/thumbnail) → Commons-Dateiname
         Wikimedia Commons imageinfo   https://commons.wikimedia.org/w/api.php
                          → auf THUMB_WIDTH_PX begrenzte Bildvariante (bounded Dateigröße; kein
                            Re-Encoding), Dateibeschreibungsseite (Attribution-Ziel) und
                            Urheber/Lizenz (credit). Die Lizenzfrage ist bei dieser Quelle in der
                            Regel geklärt (AK 14).

Schonender Abruf (AK 15):  höchstens EIN Request pro Sekunde an denselben Dienst; lokale
        Verarbeitungszeit wird angerechnet. Gilt für Metadaten-Abfrage UND Bild-Download.
        Metadaten-Antworten werden gitignoriert unter docs/data-tooling/.cache/ gecacht.

Idempotenz:  Bereits gepflegte ``portrait``-Einträge werden nicht ersetzt (außer --force);
        bereits vorhandene Bilddateien werden nicht erneut heruntergeladen.

Aufruf:  python3 docs/data-tooling/fetch_composer_portraits.py [--no-network] [--force] [--verbose]
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Platzhalter-/Sammeleinträge überspringen (aus dem Open-Opus-Importer wiederverwenden).
from import_openopus import SKIP_IDS  # type: ignore
from fetch_wikipedia_composers import TITLE_OVERRIDES, NO_ARTICLE_IDS  # type: ignore

WIKI_BASE = "https://de.wikipedia.org"
COMMONS_BASE = "https://commons.wikimedia.org"
USER_AGENT = "klangland-portrait-collector/1.0 (US-024; https://openopus.org contact: klangland)"
MIN_INTERVAL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 30
RETRY_WAITS_SECONDS = [5, 15, 30]
# Auf diese Breite begrenzte Variante laden (bounded Dateigröße; ausreichend für Kachel/Detail).
THUMB_WIDTH_PX = 400
CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


class Fetcher:
    """Rate-limitierter Zugriff mit JSON-Cache (Metadaten) und Binär-Download (Bilder)."""

    def __init__(self, cache_dir: Path, *, offline: bool, verbose: bool) -> None:
        self.cache_dir = cache_dir
        self.offline = offline
        self.verbose = verbose
        self._last = 0.0
        self.network_calls = 0
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _wait(self) -> None:
        # 1-req/s-Grenze (AK 15): lokale Verarbeitungszeit wird angerechnet.
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
        payload = self._request(url, expect_json=True)
        if payload is not None:
            cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return payload

    def get_bytes(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Lädt eine Binärdatei; gibt (Daten, Content-Type) zurück. Kein JSON-Cache."""
        if self.offline:
            return None
        return self._request(url, expect_json=False)

    def _request(self, url: str, *, expect_json: bool):
        for attempt, extra in enumerate([0, *RETRY_WAITS_SECONDS]):
            if extra:
                time.sleep(extra)
            self._wait()
            self.network_calls += 1
            if self.verbose:
                print(f"    → GET {url}  (t={time.monotonic():.1f}s)")
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                    raw = resp.read()
                    if expect_json:
                        return json.loads(raw.decode("utf-8"))
                    content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
                    return raw, content_type
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


def title_for(composer: Dict[str, Any]) -> str:
    """Ermittelt den kanonischen Wikipedia-Artikeltitel als Ausgangspunkt für die Bildsuche."""
    # Vorhandene wikipedia.url ist am zuverlässigsten (bereits in US-017 kuratiert).
    wiki = composer.get("wikipedia") or {}
    url = wiki.get("url") or ""
    marker = "/wiki/"
    if marker in url:
        slug = url.split(marker, 1)[1]
        return urllib.parse.unquote(slug).replace("_", " ")
    if composer["id"] in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[composer["id"]]
    return composer["name"]


def image_url_from_summary(fetcher: Fetcher, title: str) -> Optional[str]:
    quoted = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"{WIKI_BASE}/api/rest_v1/page/summary/{quoted}"
    data = fetcher.get_json(url, f"summary_{title}")
    if not data:
        return None
    original = (data.get("originalimage") or {}).get("source")
    thumb = (data.get("thumbnail") or {}).get("source")
    return original or thumb


# Nicht-Portrait-Bilder in der Artikel-Bildliste (Unterschriften, Karten, Wappen …) überspringen.
NON_PORTRAIT_RE = re.compile(
    r"signature|unterschrift|\bmap\b|karte|logo|wappen|coat|noten|score|grave|grab|denkmal|"
    r"haus|building|gedenk|plaque|tafel|autograph",
    re.IGNORECASE,
)
PORTRAIT_EXTS = (".jpg", ".jpeg", ".png", ".gif")


def image_url_from_media_list(fetcher: Fetcher, title: str) -> Optional[str]:
    """
    Fallback, wenn die REST-Summary kein führendes Bild liefert: erste geeignete Bilddatei aus der
    Artikel-Bildliste (media-list). Unterschriften, Karten, Notenbeispiele u. Ä. werden übersprungen.
    """
    quoted = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"{WIKI_BASE}/api/rest_v1/page/media-list/{quoted}"
    data = fetcher.get_json(url, f"medialist_{title}")
    for item in (data or {}).get("items", []):
        if item.get("type") != "image":
            continue
        item_title = item.get("title") or ""
        if not item_title.lower().endswith(PORTRAIT_EXTS) or NON_PORTRAIT_RE.search(item_title):
            continue
        src = (item.get("srcset") or [{}])[0].get("src")
        if src:
            return f"https:{src}" if src.startswith("//") else src
    return None


def commons_filename(image_url: str) -> Optional[str]:
    """Dateiname aus einer upload.wikimedia.org-URL (Thumbnails werden auf das Original reduziert)."""
    path = urllib.parse.urlparse(image_url).path
    name = urllib.parse.unquote(path.rsplit("/", 1)[-1])
    # Thumbnail-URLs enden auf .../<Original>/<breite>px-<Original>.<ext>
    thumb = re.match(r"^\d+px-(.+)$", name)
    if thumb and "/thumb/" in image_url:
        name = thumb.group(1)
    return name or None


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_image(
    fetcher: Fetcher, image_url: str, article_url: str
) -> Tuple[str, str, Optional[str]]:
    """
    Liefert (download_url, source, credit) über die Commons-imageinfo-API: eine auf THUMB_WIDTH_PX
    begrenzte Bildvariante als Download-Ziel, die Dateibeschreibungsseite als Attribution-Ziel und
    Urheber/Lizenz als credit. Fällt auf das führende Summary-Bild zurück, wenn kein Commons-
    Datensatz gefunden wird.
    """
    filename = commons_filename(image_url)
    if not filename:
        return image_url, article_url, None
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "prop": "imageinfo",
        "titles": f"File:{filename}", "iiprop": "extmetadata|url",
        "iiurlwidth": str(THUMB_WIDTH_PX),
    })
    url = f"{COMMONS_BASE}/w/api.php?{params}"
    payload = fetcher.get_json(url, f"imageinfo_{filename}")
    pages = ((payload or {}).get("query") or {}).get("pages") or {}
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        download_url = info.get("thumburl") or info.get("url") or image_url
        source = info.get("descriptionurl") or article_url
        meta = info.get("extmetadata") or {}
        artist = strip_html((meta.get("Artist") or {}).get("value", ""))
        license_name = strip_html((meta.get("LicenseShortName") or {}).get("value", ""))
        parts = [p for p in (artist, license_name) if p]
        credit = " – ".join(parts) if parts else None
        return download_url, source, credit
    return image_url, article_url, None


def download_portrait(
    fetcher: Fetcher, image_url: str, dest_dir: Path, composer_id: str
) -> Optional[str]:
    """Lädt das Bild herunter und gibt den Dateinamen zurück (None bei Fehler)."""
    existing = list(dest_dir.glob(f"{composer_id}.*"))
    if existing:
        return existing[0].name  # bereits vorhanden – kein Re-Download (Idempotenz)
    result = fetcher.get_bytes(image_url)
    if not result:
        return None
    data, content_type = result
    ext = CONTENT_TYPE_EXT.get(content_type)
    if not ext:
        url_ext = Path(urllib.parse.urlparse(image_url).path).suffix.lower().lstrip(".")
        ext = url_ext if url_ext in CONTENT_TYPE_EXT.values() else "jpg"
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{composer_id}.{ext}"
    (dest_dir / filename).write_bytes(data)
    return filename


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lädt Komponist:innen-Portraits (US-024).")
    parser.add_argument("--no-network", action="store_true", help="Nur aus dem Cache arbeiten.")
    parser.add_argument("--force", action="store_true", help="Vorhandene portrait-Einträge neu ermitteln.")
    parser.add_argument("--verbose", action="store_true", help="Request-Zeitstempel loggen.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    composers_path = repo / "data" / "composers.json"
    portraits_dir = repo / "data" / "portraits"
    cache_dir = Path(__file__).resolve().parent / ".cache" / "portraits"

    doc = json.loads(composers_path.read_text(encoding="utf-8"))
    composers = doc["composers"]
    fetcher = Fetcher(cache_dir, offline=args.no_network, verbose=args.verbose)

    found, downloaded, skipped, missing, not_found = 0, 0, 0, 0, []
    changed = False

    for composer in composers:
        cid = composer["id"]
        if cid in SKIP_IDS or cid in NO_ARTICLE_IDS:
            skipped += 1
            continue
        if composer.get("portrait") and not args.force:
            skipped += 1
            continue

        title = title_for(composer)
        article_url = (composer.get("wikipedia") or {}).get("url") or f"{WIKI_BASE}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
        image_url = image_url_from_summary(fetcher, title)
        if not image_url:
            # Fallback: erste geeignete Bilddatei aus der Artikel-Bildliste.
            image_url = image_url_from_media_list(fetcher, title)
        if not image_url:
            not_found.append(f"{cid} – {composer['name']}")
            missing += 1
            continue
        found += 1

        download_url, source, credit = resolve_image(fetcher, image_url, article_url)
        filename = download_portrait(fetcher, download_url, portraits_dir, cid)
        if not filename:
            not_found.append(f"{cid} – {composer['name']} (Download fehlgeschlagen)")
            missing += 1
            continue
        if not (portraits_dir / filename).stat().st_size:
            not_found.append(f"{cid} – {composer['name']} (leere Datei)")
            missing += 1
            continue
        downloaded += 1

        portrait = {"file": filename, "source": source, "credit": credit}
        if composer.get("portrait") != portrait:
            composer["portrait"] = portrait
            changed = True

    if changed:
        doc["metadata"]["lastUpdated"] = "2026-08-21"
        save(composers_path, doc)

    print("\n=== Komponist:innen-Portraits: Report ===")
    print(f"Portraits gefunden   : {found}")
    print(f"Neu heruntergeladen  : {downloaded}")
    print(f"Übersprungen         : {skipped} (Platzhalter oder bereits gepflegt)")
    print(f"Ohne Bild            : {missing}")
    print(f"Netzwerk-Requests    : {fetcher.network_calls}")
    if not_found:
        print("\n-- Ohne verwendbares Portrait --")
        for line in not_found:
            print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
