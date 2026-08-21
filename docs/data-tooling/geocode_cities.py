#!/usr/bin/env python3
"""
Geokodierungs-Skript für die Ensemble-Orte (User Story 013).

Ermittelt für jede Stadt in cities.json, die mindestens ein ansässiges Ensemble
(ensembles.json → cityIds) hat, die Geokoordinaten der Stadt selbst und legt sie
als ``coordinates: { "lat": …, "lng": … }`` in cities.json ab. Grundlage der
Kartenmarker in US-013.

Quelle: Overpass-API von OpenStreetMap. Abgefragt wird die administrative Grenze
der Stadt (boundary=administrative) innerhalb des Bundeslandes Nordrhein-Westfalen
(Projekt-Scope) und deren Mittelpunkt (``out center``). Die Eingrenzung auf NRW
verhindert Treffer auf gleichnamige Orte anderswo (z. B. Hagen in Schleswig-Holstein).
Es gilt eine Selbstbeschränkung von höchstens EINER Abfrage pro Sekunde (AK 7); bei
Drosselung (HTTP 429/504) wartet das Skript zusätzlich (Backoff) und wiederholt.

Das Skript ist idempotent: bereits vorhandene Koordinaten werden standardmäßig nicht
erneut abgefragt. Mit ``--force`` werden alle Ensemble-Orte neu geokodiert.

Aufruf:  python3 docs/data-tooling/geocode_cities.py [--force]
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Konstanten -------------------------------------------------------------

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "klangland-geocoder/1.0 (US-013; OpenStreetMap Overpass)"
# Selbstbeschränkung: mindestens diese Zeitspanne (Sekunden) zwischen zwei Abfragen.
MIN_INTERVAL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 60
# Bundesland, auf das die Suche eingegrenzt wird (Projekt-Scope: NRW).
STATE_NAME = "Nordrhein-Westfalen"
# Wiederholungen bei Drosselung/Timeout (HTTP 429/504) und die jeweiligen Wartezeiten.
RETRY_WAITS_SECONDS = [5, 15, 30]


def ensemble_city_ids(ensembles: List[Dict[str, Any]]) -> set:
    """Menge aller Städte-IDs, denen mindestens ein Ensemble zugeordnet ist."""
    ids = set()
    for ensemble in ensembles:
        for city_id in ensemble.get("cityIds", []):
            ids.add(city_id)
    return ids


def build_query(name: str) -> str:
    """
    Overpass-QL: administrative Stadtgrenze anhand des Namens, eingegrenzt auf das
    Bundesland NRW (über eine benannte Area). ``admin_level`` 6 (kreisfreie Städte)
    bzw. 8 (kreisangehörige Städte) deckt beide Fälle ab. Liefert den Mittelpunkt
    (``out center``) des ersten Treffers.
    """
    return (
        "[out:json][timeout:50];"
        f'area["boundary"="administrative"]["admin_level"="4"]["name"="{STATE_NAME}"]->.state;'
        "("
        f'relation["boundary"="administrative"]["admin_level"~"6|8"]["name"="{name}"](area.state);'
        ");"
        "out center 1;"
    )


class ThrottledError(Exception):
    """Overpass hat gedrosselt (429) oder ist ausgelastet (504) – wiederholbar."""


def _request_overpass(query: str) -> Optional[Dict[str, float]]:
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    request = urllib.request.Request(
        OVERPASS_URL, data=data, headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (429, 504):
            raise ThrottledError(f"HTTP {error.code}") from error
        raise

    for element in payload.get("elements", []):
        center = element.get("center")
        if center and "lat" in center and "lon" in center:
            return {"lat": round(center["lat"], 5), "lng": round(center["lon"], 5)}
        if "lat" in element and "lon" in element:
            return {"lat": round(element["lat"], 5), "lng": round(element["lon"], 5)}
    return None


def query_overpass(query: str) -> Optional[Dict[str, float]]:
    """
    Führt eine Overpass-Abfrage aus und gibt {lat, lng} des ersten Treffers zurück.
    Bei Drosselung (429/504) wird mit wachsender Wartezeit erneut versucht. Jeder
    Versuch respektiert die 1-Abfrage-pro-Sekunde-Grenze über den zusätzlichen
    Backoff (>= 5 s).
    """
    for attempt, wait in enumerate([0, *RETRY_WAITS_SECONDS]):
        if wait:
            time.sleep(wait)
        try:
            return _request_overpass(query)
        except ThrottledError as error:
            if attempt == len(RETRY_WAITS_SECONDS):
                raise
            print(f"    … gedrosselt ({error}), erneuter Versuch in {RETRY_WAITS_SECONDS[attempt]} s")
    return None


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Geokodiert die Ensemble-Orte via Overpass.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Alle Ensemble-Orte neu geokodieren, auch bereits vorhandene Koordinaten.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    data_dir = repo / "data"
    cities_path = data_dir / "cities.json"
    ensembles_path = data_dir / "ensembles.json"

    cities_doc = load(cities_path)
    ensembles_doc = load(ensembles_path)

    target_ids = ensemble_city_ids(ensembles_doc["ensembles"])
    cities = cities_doc["cities"]

    todo = [
        city
        for city in cities
        if city["id"] in target_ids and (args.force or not city.get("coordinates"))
    ]
    if not todo:
        print("Alle Ensemble-Orte sind bereits geokodiert. (--force zum Erzwingen)")
        return 0

    print(f"Geokodiere {len(todo)} Ort(e) (max. 1 Abfrage/Sekunde) …")
    last_request = 0.0
    failures = 0
    for city in todo:
        # Selbstbeschränkung: mind. MIN_INTERVAL_SECONDS zwischen zwei Abfragen (AK 7).
        wait = MIN_INTERVAL_SECONDS - (time.monotonic() - last_request)
        if wait > 0:
            time.sleep(wait)
        last_request = time.monotonic()

        name = city["name"]
        try:
            coords = query_overpass(build_query(name))
        except Exception as error:  # noqa: BLE001 - Netzwerk-/Parsefehler pro Ort tolerieren
            print(f"  ! {name}: Abfrage fehlgeschlagen ({error})", file=sys.stderr)
            failures += 1
            continue

        if coords is None:
            print(f"  ! {name}: kein Treffer bei Overpass", file=sys.stderr)
            failures += 1
            continue

        city["coordinates"] = coords
        print(f"  ✓ {name}: {coords['lat']}, {coords['lng']}")

    save(cities_path, cities_doc)
    print(f"cities.json aktualisiert. {len(todo) - failures} erfolgreich, {failures} Fehler.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
