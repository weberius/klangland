#!/usr/bin/env python3
"""
Trägt kuratierte Wikipedia-Kurzfassungen in data/composers.json ein (User Story 017).

Liest eine Kuratierungs-Datei (JSON: { composerId: { "summary": ..., "url": ... } }) und setzt
das Feld ``wikipedia`` der jeweiligen Komponist:innen. Die Kurzfassungen stammen aus der
redaktionellen Kuratierung (eigenständig formuliert, ~60 Wörter; kein wörtlicher Auszug, AK 4);
dieses Skript schreibt sie lediglich strukturiert und ordnungserhaltend in die Datei.

Grundsätze:
  * Kein Überschreiben bereits kuratierter ``wikipedia``-Einträge, außer mit --force.
  * Feldreihenfolge stabil: ``wikipedia`` wird ans Ende des Komponist:innen-Objekts gesetzt.
  * Validierung: url muss auf de.wikipedia.org zeigen; summary nicht leer.

Aufruf:  python3 docs/data-tooling/apply_wikipedia_composers.py <kuratierung.json> [--force]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def main() -> int:
    parser = argparse.ArgumentParser(description="Trägt kuratierte Wikipedia-Kurzfassungen ein (US-017).")
    parser.add_argument("curation", help="JSON-Datei { composerId: { summary, url } }")
    parser.add_argument("--force", action="store_true", help="Vorhandene wikipedia-Einträge überschreiben.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    composers_path = repo / "data" / "composers.json"
    doc = json.loads(composers_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["composers"]}

    curation: Dict[str, Any] = json.loads(Path(args.curation).read_text(encoding="utf-8"))

    applied, skipped, invalid, unknown = 0, 0, 0, 0
    for cid, entry in curation.items():
        composer = by_id.get(cid)
        if composer is None:
            print(f"  ? unbekannte composerId: {cid}", file=sys.stderr)
            unknown += 1
            continue
        summary = (entry or {}).get("summary", "").strip()
        url = (entry or {}).get("url", "").strip()
        if not summary or "de.wikipedia.org" not in url:
            print(f"  ! ungültig (summary/url) für {cid}", file=sys.stderr)
            invalid += 1
            continue
        if composer.get("wikipedia") and not args.force:
            skipped += 1
            continue
        composer["wikipedia"] = {"summary": summary, "url": url}
        applied += 1

    composers_path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    total = sum(1 for c in doc["composers"] if c.get("wikipedia"))
    print(f"\n=== Wikipedia-Kuratierung angewandt ===")
    print(f"Neu gesetzt   : {applied}")
    print(f"Übersprungen  : {skipped} (bereits vorhanden)")
    print(f"Ungültig      : {invalid}")
    print(f"Unbekannte ID : {unknown}")
    print(f"Gesamt mit wikipedia: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
