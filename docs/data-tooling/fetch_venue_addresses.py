#!/usr/bin/env python3
"""
Adress- und Koordinaten-Recherche für die Spielstätten (User Story 022).

Ermittelt für jede Spielstätte in venues.json aus dem OpenStreetMap-Ökosystem
die Geokoordinaten und eine strukturierte Postadresse und legt sie als

    "coordinates": { "lat": …, "lng": … }
    "address": { "street": …, "houseNumber": …, "postalCode": …, "city": … }

in venues.json ab (Grundlage der späteren Kartenansicht).

Quellen:
  * Overpass-API   – ordnet die Spielstätte einem OSM-Objekt zu und liefert dessen
                     Mittelpunkt (``out center``). Die Suche wird über den Namen und
                     die zugeordnete Stadt (venue.cityIds → cities.json) präzisiert
                     und auf Nordrhein-Westfalen eingegrenzt (Projekt-Scope), damit
                     gleichnamige Orte anderswo nicht fälschlich getroffen werden.
  * Nominatim      – liefert per Reverse-Geocoding auf diesen Koordinaten eine
                     vollständige, saubere Postadresse (Straße, Hausnummer, PLZ, Ort).

OSM ist KEINE Laufzeitabhängigkeit der Webanwendung – die Daten werden einmalig
recherchiert und in venues.json gespeichert.

Schonender Abruf (AK 5): Es wird über beide APIs hinweg höchstens EINE Abfrage pro
Sekunde ausgeführt (Selbstbeschränkung). Bei Drosselung (HTTP 429/504) wartet das
Skript zusätzlich (Backoff) und wiederholt.

Idempotenz / kein Datenverlust (AK 6): Bereits gefüllte Felder werden standardmäßig
nicht erneut abgefragt; vorhandene Werte werden NIE mit ``null`` überschrieben. Mit
``--force`` werden alle Felder neu ermittelt.

Aufruf:  python3 docs/data-tooling/fetch_venue_addresses.py [--force] [--limit N]
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
from typing import Any, Dict, List, Optional

# --- Konstanten -------------------------------------------------------------

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
# Aussagekräftiger User-Agent inkl. Kontakt-Hinweis (Nominatim-/Overpass-Nutzungsregeln).
USER_AGENT = "klangland-venue-geocoder/1.0 (US-022; OpenStreetMap Overpass+Nominatim)"
# Selbstbeschränkung: mindestens diese Zeitspanne (Sekunden) zwischen zwei Abfragen,
# über BEIDE APIs hinweg gezählt (AK 5).
MIN_INTERVAL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 60
# Bundesland, auf das die Overpass-Suche eingegrenzt wird (Projekt-Scope: NRW).
STATE_NAME = "Nordrhein-Westfalen"
# Wiederholungen bei Drosselung/Timeout (HTTP 429/504) und die jeweiligen Wartezeiten.
RETRY_WAITS_SECONDS = [5, 15, 30]


class ThrottledError(Exception):
    """OSM hat gedrosselt (429) oder ist ausgelastet (504) – wiederholbar."""


# --- HTTP-Grundfunktionen mit Rate-Limit & Backoff --------------------------


class RateLimiter:
    """Erzwingt mind. MIN_INTERVAL_SECONDS zwischen zwei Abrufen (über alle APIs)."""

    def __init__(self) -> None:
        self._last = 0.0

    def wait(self) -> None:
        remaining = MIN_INTERVAL_SECONDS - (time.monotonic() - self._last)
        if remaining > 0:
            time.sleep(remaining)
        self._last = time.monotonic()


def _http_get_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (429, 504):
            raise ThrottledError(f"HTTP {error.code}") from error
        raise


def _http_post_json(url: str, data: Dict[str, str]) -> Any:
    payload = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (429, 504):
            raise ThrottledError(f"HTTP {error.code}") from error
        raise


def with_retry(call, limiter: RateLimiter):
    """
    Führt ``call()`` mit Rate-Limit aus und wiederholt bei Drosselung (429/504) mit
    wachsender Wartezeit. Jeder Versuch respektiert die 1-Abfrage-pro-Sekunde-Grenze.
    """
    for attempt, wait in enumerate([0, *RETRY_WAITS_SECONDS]):
        if wait:
            time.sleep(wait)
        limiter.wait()
        try:
            return call()
        except ThrottledError as error:
            if attempt == len(RETRY_WAITS_SECONDS):
                raise
            print(f"    … gedrosselt ({error}), erneuter Versuch in {RETRY_WAITS_SECONDS[attempt]} s")
    return None


# --- Overpass: Zuordnung + Koordinaten --------------------------------------


def _escape(value: str) -> str:
    """Escapt Anführungszeichen/Backslashes für die Overpass-QL-String-Literale."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_overpass_query(name: str, city_name: Optional[str]) -> str:
    """
    Overpass-QL: sucht ein benanntes Objekt (node/way/relation) per case-insensitivem
    Namensvergleich. Ist eine Stadt bekannt, wird die Suche auf deren administrative
    Fläche eingegrenzt, sonst auf das Bundesland NRW. ``out center 1`` liefert den
    Mittelpunkt des ersten Treffers.
    """
    name_re = _escape(re.escape(name))
    if city_name:
        area = (
            f'area["boundary"="administrative"]["admin_level"~"6|8"]'
            f'["name"="{_escape(city_name)}"]->.searchArea;'
        )
    else:
        area = (
            f'area["boundary"="administrative"]["admin_level"="4"]'
            f'["name"="{_escape(STATE_NAME)}"]->.searchArea;'
        )
    return (
        "[out:json][timeout:50];"
        f"{area}"
        "("
        f'nwr["name"~"^{name_re}$",i](area.searchArea);'
        ");"
        "out center 1;"
    )


def query_overpass_coords(name: str, city_name: Optional[str], limiter: RateLimiter):
    """{lat, lng} des ersten Treffers oder None."""
    query = build_overpass_query(name, city_name)
    payload = with_retry(lambda: _http_post_json(OVERPASS_URL, {"data": query}), limiter)
    if not payload:
        return None
    for element in payload.get("elements", []):
        center = element.get("center")
        if center and "lat" in center and "lon" in center:
            return {"lat": round(center["lat"], 5), "lng": round(center["lon"], 5)}
        if "lat" in element and "lon" in element:
            return {"lat": round(element["lat"], 5), "lng": round(element["lon"], 5)}
    return None


# --- Nominatim: Postadresse per Reverse-Geocoding ---------------------------


def query_nominatim_address(coords: Dict[str, float], limiter: RateLimiter):
    """
    Reverse-Geocoding auf den Overpass-Koordinaten. Mappt die OSM-Adressbestandteile
    auf das Address-Format (street, houseNumber, postalCode, city). Fehlende
    Bestandteile bleiben None.
    """
    params = urllib.parse.urlencode(
        {
            "format": "jsonv2",
            "lat": coords["lat"],
            "lon": coords["lng"],
            "addressdetails": 1,
            "zoom": 18,
            "accept-language": "de",
        }
    )
    url = f"{NOMINATIM_REVERSE_URL}?{params}"
    payload = with_retry(lambda: _http_get_json(url), limiter)
    if not payload:
        return None
    addr = payload.get("address") or {}
    street = addr.get("road") or addr.get("pedestrian") or addr.get("footway")
    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or addr.get("city_district")
    )
    result = {
        "street": street,
        "houseNumber": addr.get("house_number"),
        "postalCode": addr.get("postcode"),
        "city": city,
    }
    # Nur zurückgeben, wenn wenigstens ein Bestandteil ermittelt wurde.
    return result if any(result.values()) else None


# --- Datei-I/O --------------------------------------------------------------


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- Hauptlogik -------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recherchiert Adresse & Koordinaten der Spielstätten via OpenStreetMap."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Alle Felder neu ermitteln, auch bereits vorhandene Adressen/Koordinaten.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nur die ersten N zu bearbeitenden Spielstätten verarbeiten (Testlauf).",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    data_dir = repo / "data"
    venues_path = data_dir / "venues.json"
    cities_path = data_dir / "cities.json"

    venues_doc = load(venues_path)
    cities_doc = load(cities_path)
    city_names = {city["id"]: city["name"] for city in cities_doc["cities"]}

    venues = venues_doc["venues"]
    todo = [
        venue
        for venue in venues
        if args.force or not venue.get("address") or not venue.get("coordinates")
    ]
    if args.limit is not None:
        todo = todo[: args.limit]

    if not todo:
        print("Alle Spielstätten sind bereits vollständig recherchiert. (--force zum Erzwingen)")
        return 0

    print(f"Recherchiere {len(todo)} Spielstätte(n) (max. 1 Abfrage/Sekunde) …")
    limiter = RateLimiter()
    updated = 0
    skipped_unresolved: List[str] = []
    failures = 0

    for venue in todo:
        name = venue["name"]
        city_ids = venue.get("cityIds") or []
        city_name = city_names.get(city_ids[0]) if city_ids else None

        need_coords = args.force or not venue.get("coordinates")
        need_address = args.force or not venue.get("address")

        # Ortsungebundene/„wechselnde" Spielstätten ohne Stadt lassen sich nicht
        # eindeutig auflösen – unverändert lassen und im Bericht vermerken (AK 8).
        if not city_ids:
            print(f"  – {name}: ohne cityIds, nicht auflösbar (übersprungen)")
            skipped_unresolved.append(venue["id"])
            continue

        try:
            coords = query_overpass_coords(name, city_name, limiter)
        except Exception as error:  # noqa: BLE001 - Netzwerk-/Parsefehler pro Venue tolerieren
            print(f"  ! {name}: Overpass-Abfrage fehlgeschlagen ({error})", file=sys.stderr)
            failures += 1
            continue

        if coords is None:
            print(f"  – {name}: kein eindeutiger OSM-Treffer (übersprungen)")
            skipped_unresolved.append(venue["id"])
            continue

        # Adresse über Reverse-Geocoding – auf den ermittelten bzw. vorhandenen Koordinaten.
        address = None
        address_source = coords if need_coords else venue.get("coordinates")
        if need_address:
            try:
                address = query_nominatim_address(address_source, limiter)
            except Exception as error:  # noqa: BLE001
                print(f"  ! {name}: Nominatim-Abfrage fehlgeschlagen ({error})", file=sys.stderr)

        # Vorhandene Werte NIE mit null überschreiben (AK 6).
        changed = False
        if need_coords and coords:
            venue["coordinates"] = coords
            changed = True
        if need_address and address:
            venue["address"] = address
            changed = True

        if changed:
            updated += 1
            coord_str = f"{coords['lat']}, {coords['lng']}"
            addr_str = ""
            if address:
                addr_str = " | " + ", ".join(
                    str(v) for v in [address.get("street"), address.get("houseNumber"),
                                     address.get("postalCode"), address.get("city")] if v
                )
            print(f"  ✓ {name}: {coord_str}{addr_str}")
        else:
            print(f"  – {name}: nichts Neues ermittelt (übersprungen)")
            skipped_unresolved.append(venue["id"])

    save(venues_path, venues_doc)

    # --- Bericht (AK 8) -----------------------------------------------------
    print("\n=== Bericht ===")
    print(f"  aktualisiert:  {updated}")
    print(f"  fehlgeschlagen: {failures}")
    print(f"  nicht aufgelöst: {len(skipped_unresolved)}")
    if skipped_unresolved:
        print("  nicht aufgelöste Venue-IDs:")
        for vid in skipped_unresolved:
            print(f"    - {vid}")
    print("\nHinweis: venues.json aktualisiert. Kopie nach web/public/data/ spiegeln!")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
