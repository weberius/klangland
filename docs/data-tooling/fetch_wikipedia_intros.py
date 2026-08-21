#!/usr/bin/env python3
"""
Ergänzt die Wikipedia-Kandidaten um den vollständigen Einleitungsabschnitt (US-017).

Die REST-Summary (fetch_wikipedia_composers.py) liefert nur einen sehr kurzen Auszug (oft ein
Satz). Für faktentreue ~60-Wort-Kurzfassungen wird hier zusätzlich der vollständige
Intro-Abschnitt über die MediaWiki-Extracts-API geholt und als ``extract_full`` in
candidates.json ergänzt. Rate-Limit (AK 11): max. 1 Request/Sekunde; Antworten werden gecacht.

Aufruf:  python3 docs/data-tooling/fetch_wikipedia_intros.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

WIKI_API = "https://de.wikipedia.org/w/api.php"
USER_AGENT = "klangland-wikipedia-collector/1.0 (US-017; https://openopus.org)"
MIN_INTERVAL = 1.0


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    cache_dir = Path(__file__).resolve().parent / ".cache" / "wikipedia" / "intros"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cand_path = repo / "docs/data-tooling/.cache/wikipedia/candidates.json"
    cand = json.loads(cand_path.read_text(encoding="utf-8"))

    last = 0.0
    calls = 0
    for cid, entry in cand.items():
        title = entry.get("title")
        if not title:
            continue
        slug = re.sub(r"[^A-Za-z0-9._-]+", "_", title)[:150]
        cache_file = cache_dir / f"{slug}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
        else:
            gap = MIN_INTERVAL - (time.monotonic() - last)
            if gap > 0:
                time.sleep(gap)
            last = time.monotonic()
            calls += 1
            params = urllib.parse.urlencode({
                "action": "query", "format": "json", "prop": "extracts",
                "exintro": "1", "explaintext": "1", "redirects": "1", "titles": title,
            })
            req = urllib.request.Request(f"{WIKI_API}?{params}", headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            except Exception as error:  # noqa: BLE001
                print(f"  ! {cid}: {error}")
                continue
        pages = (data.get("query") or {}).get("pages") or {}
        for page in pages.values():
            full = (page.get("extract") or "").strip()
            if full:
                entry["extract_full"] = full
            break

    cand_path.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    have = sum(1 for e in cand.values() if e.get("extract_full"))
    print(f"Intro-Abschnitte ergänzt: {have}/{len(cand)}; Netzwerk-Requests: {calls}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
