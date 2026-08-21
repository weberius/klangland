# ADR-008: Leaflet und OpenStreetMap für die Kartenansicht

**Status:** accepted (2026-08-21)

## Evaluation criteria

**Summary:** Für die Kartenseite ([US-013](../product/planning/done/US-013-map-country.md), Route
`/cities`) wird eine Bibliothek zur Kartendarstellung sowie eine Quelle für die Stadt-Koordinaten
benötigt. Die Karte zeigt alle Orte mit ansässigem Ensemble als Marker und muss sich in die
statische Webapp ([ADR-001](ADR-001-statische-webapp-ohne-backend.md)) und das JSON-Datenmodell
([ADR-002](ADR-002-json-dateien-als-single-source-of-truth.md)) einfügen.

**Specifics:**

- **Statisch deploybar:** kein Laufzeitserver, Einbettung als reine Client-Bibliothek.
- **Kein API-Schlüssel/keine Registrierung:** vermeidet Secrets im statischen Bundle und
  Abrechnungskonten (passend zu „unabhängig von externen APIs", PRD §29).
- **Kosten/Lizenz:** freie Nutzung, offene Lizenz.
- **Bundle-/Integrationsaufwand:** überschaubare Größe, Angular-Einbindung ohne Wrapper-Zwang.
- **Barrierefreiheit & Attribution:** tastaturbedienbare Marker, korrekte Kartenrechte-Attribution.
- **Koordinaten:** reproduzierbare, offen lizenzierte Quelle für die Stadt-Koordinaten, die in
  `cities.json` als Stammdaten abgelegt werden (nicht zur Laufzeit geladen).

## Candidates to consider

**Summary:** Betrachtet werden verbreitete Client-Kartenbibliotheken sowie die Geocoding-Quelle.

Kartendarstellung:

1. **Leaflet + OpenStreetMap-Rasterkacheln.**
2. **MapLibre GL JS + freie Vektor-Tiles.**
3. **Google Maps / Mapbox GL JS** (kommerzielle Tile-Anbieter).
4. **Selbstgezeichnete SVG-Karte von NRW** (kein externer Tile-Dienst).

Koordinatenquelle:

- **Overpass-API (OpenStreetMap)** vs. kommerzieller Geocoder.

## Research and analysis of each candidate

**Leaflet + OpenStreetMap**

- Erfüllt alle Kriterien: schlanke, etablierte Bibliothek ohne API-Schlüssel; OSM-Rasterkacheln
  sind frei nutzbar (mit Pflicht-Attribution). Marker werden als `divIcon` gerendert und sind
  tastaturbedienbar. Einbindung als npm-Paket (`leaflet` + `@types/leaflet`) direkt in eine
  Standalone-Seite; das DOM wird von Leaflet außerhalb der Angular-Templates verwaltet
  (`ViewEncapsulation.None`, `afterNextRender`).
- Cost: Neue Laufzeit-Abhängigkeit; die Kartenkacheln werden **zur Laufzeit** von externen
  OSM-Servern geladen. Damit hat die App an dieser einen Stelle eine externe Laufzeitabhängigkeit
  – anders als der übrige, rein aus JSON gespeiste Teil. Bewusst akzeptiert, da nur die
  Kartenkacheln betroffen sind; die fachlichen Daten (Orte, Ensembles, Koordinaten) stammen
  weiterhin ausschließlich aus den versionierten JSON-Dateien.
- SWOT: **S** kostenlos, kein Key, kleines Bundle, große Verbreitung. **W** externer Tile-Dienst
  zur Laufzeit. **O** Kacheln später auf einen anderen/eigenen Tile-Server umstellbar. **T**
  Nutzungsrichtlinien/Verfügbarkeit des öffentlichen OSM-Tile-Servers.

**MapLibre GL JS**

- Technisch geeignet und ebenfalls offen, aber schwergewichtiger (WebGL, größeres Bundle) und
  benötigt in der Praxis eine Vektor-Tile-Quelle/Style – mehr Aufwand als für eine reine
  Marker-Übersicht nötig.

**Google Maps / Mapbox GL JS**

- Erfordern API-Schlüssel, Konten und ggf. Kosten; ein Schlüssel im statischen Bundle
  widerspricht dem schlüsselfreien Kriterium. Abgelehnt.

**Selbstgezeichnete SVG-Karte**

- Käme ohne externen Tile-Dienst aus, bietet aber kein Zoom/Pan und keinen geografischen Kontext;
  Pflege der Geometrie wäre aufwändig. Für den angestrebten Überblick zu unflexibel.

**Koordinatenquelle – Overpass-API**

- Die Stadt-Koordinaten werden **einmalig vorab** per Skript
  ([`geocode_cities.py`](../data-tooling/geocode_cities.py)) über die Overpass-API ermittelt
  (administrative Grenze innerhalb NRW, Mittelpunkt) und als `coordinates` in `cities.json`
  abgelegt – passend zu den idempotenten Ingest-Skripten
  ([ADR-005](ADR-005-idempotente-python-ingest-skripte.md)). Selbstbeschränkung: höchstens eine
  Abfrage pro Sekunde. Zur Laufzeit findet **kein** Geocoding statt.

## Recommendation

**Summary:** Leaflet mit OpenStreetMap-Rasterkacheln für die Kartenseite; Stadt-Koordinaten vorab
per Overpass-API in `cities.json` erfasst.

**Specifics:** `leaflet` (+ `@types/leaflet`) als Laufzeit-Abhängigkeit, eingebunden in eine
lazy geladene Standalone-Seite `CityMapPage` unter `/cities`. OSM-Kacheln mit vorgeschriebener
Attribution; Ensemble-Orte als rote `divIcon`-Marker, der aktive Ort-Filter wird über Marker-Klassen
hervorgehoben. Der Ort-Filter läuft über den bestehenden `FilterService` (Konsistenz mit US-020),
nicht über einen kartenlokalen Zustand. Koordinaten sind Stammdaten in `cities.json` und werden
offline per Overpass recherchiert. Die externe Laufzeitabhängigkeit beschränkt sich auf die
Kartenkacheln und ist bei Bedarf auf einen anderen Tile-Server umstellbar.
