# US-033 – Umsetzungs-Tasks

Umsetzung von [US-033](./US-033-karte-layer-klangkoerper-venues.md): Die Karte
([city-map](../../../../web/src/app/pages/city-map/)) zeigt aktuell ausschließlich rote
Klangkörper-Marker. Sie erhält einen zweiten, umschaltbaren Layer für Spielstätten-Adressen
(blau) sowie eine Legende.

## Architektur-Entscheidung (verbindlich)

- **Neue Datenquelle:** `DataService.mapVenues(): Venue[]` – Spielstätten mit hinterlegten
  Koordinaten (`venue.coordinates`), analog zu
  [mapCities()](../../../../web/src/app/core/data.service.ts#L474). Keine Filterung nach
  Ort/Profil/Favoriten (explizit Out of Scope).
- **Layer-Zustand:** Zwei Signals in `CityMapPage`: `showEnsembleLayer = signal(true)`
  (Standard an) und `showVenueLayer = signal(false)` (Standard aus), unabhängig
  voneinander umschaltbar; beide können gleichzeitig aktiv sein.
- **Marker-Rendering:** Zweite `Map<string, L.Marker>` (`venueMarkers`) analog zur
  bestehenden `markers`-Map für Klangkörper-Orte
  ([city-map.ts:63](../../../../web/src/app/pages/city-map/city-map.ts#L63)). Marker werden
  beim Umschalten des jeweiligen Layers über `addTo(map)`/`removeFrom(map)` (bzw.
  `map.removeLayer`) ein-/ausgeblendet, nicht bei jedem Toggle neu aufgebaut.
- **Klick-Verhalten Spielstätten-Marker:** Einfacher, an den Marker gebundener Leaflet-Popup
  (`marker.bindPopup(...)`) mit Venue-Name und Link zu `/venues/:id` – bewusst schlanker als
  der bestehende Ensemble-Dialog (kein Filter-Toggle für Venues, siehe Out of Scope).
- **Farbsystem (verbindliche, projektweite Entscheidung):** Der Marker der Spielstätte
  `.venue-marker` ([styles.css:147](../../../../web/src/styles.css#L147))
  ist aktuell **rot** (`background: var(--color-danger)`), obwohl er inhaltlich eine
  Spielstätte darstellt. Diese Story führt einen neuen Design-Token `--color-info` (Blau)
  in [styles.css](../../../../web/src/styles.css) ein und stellt `.venue-marker` auf diesen
  Token um. Das wirkt sich als **beabsichtigter Seiteneffekt** auch auf die
  Einzel-Veranstaltungsort-Karte auf `events/:id`
  ([event-detail.ts:259-268](../../../../web/src/app/pages/event-detail/event-detail.ts#L259-L268))
  aus – dort wird der Marker dadurch ebenfalls blau, was die von
  [US-034](./US-034-tasks.md) geforderte Konsistenz zwischen `events/:id` und `venues/:id`
  vorwegnimmt. Falls US-034 bereits vor dieser Story umgesetzt wurde und den Token schon
  eingeführt hat, wird er hier wiederverwendet statt doppelt angelegt.
- Die Klangkörper-Marker (`.city-marker`, rot/`--color-danger`) bleiben unverändert.
- **Legende:** Statisches Overlay-Element auf der Karte mit zwei Einträgen („● Standorte der
  Klangkörper" rot, „● Adressen der Spielstätten" blau).

Betroffene Dateien:

- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (`mapVenues()`)
- [web/src/styles.css](../../../../web/src/styles.css) (`--color-info`, `.venue-marker`)
- [web/src/app/pages/city-map/city-map.ts](../../../../web/src/app/pages/city-map/city-map.ts)
- [web/src/app/pages/city-map/city-map.html](../../../../web/src/app/pages/city-map/city-map.html)
- [web/src/app/pages/city-map/city-map.css](../../../../web/src/app/pages/city-map/city-map.css)

---

## Task 1 – DataService: mapVenues() ergänzen

- Neue Methode `mapVenues(): Venue[]`, gefiltert auf `v.coordinates`, sortiert nach Name
  (analog `mapCities()`).
- **Deckt ab:** Grundlage für AK 2.

## Task 2 – Farb-Token einführen und Marker umstellen

- In [styles.css](../../../../web/src/styles.css) neuen Token `--color-info` (Blauton,
  passend zum bestehenden Farbschema) im `:root`-Block ergänzen.
- `.venue-marker` von `var(--color-danger)` auf `var(--color-info)` umstellen.
- **Deckt ab:** AK 4.

## Task 3 – Layer-Umschalter-UI

- In [city-map.ts](../../../../web/src/app/pages/city-map/city-map.ts) die beiden Signals
  `showEnsembleLayer`/`showVenueLayer` ergänzen; Toggle-Methoden.
- In [city-map.html](../../../../web/src/app/pages/city-map/city-map.html) zwei
  Checkbox-/Toggle-Steuerelemente oberhalb der Karte ergänzen (Label „Standorte der
  Klangkörper" / „Adressen der Spielstätten"), gebunden an die Signals.
- **Deckt ab:** AK 1, AK 2, AK 3.

## Task 4 – Spielstätten-Marker rendern

- In [city-map.ts](../../../../web/src/app/pages/city-map/city-map.ts) `mapVenues()`
  laden, `venueMarkers`-Map aufbauen (blauer `divIcon`, eigene CSS-Klasse, z. B.
  `.city-venue-marker` mit `background: var(--color-info)`), Popup mit Name + Link zu
  `/venues/:id`.
- Marker abhängig von `showVenueLayer()` per `effect()` ein-/ausblenden (analog zu
  [updateHighlights()](../../../../web/src/app/pages/city-map/city-map.ts#L113)).
- Klangkörper-Marker analog abhängig von `showEnsembleLayer()` ein-/ausblendbar machen.
- **Deckt ab:** AK 1, AK 2, AK 3, AK 6, AK 7.

## Task 5 – Legende ergänzen

- In [city-map.html](../../../../web/src/app/pages/city-map/city-map.html) ein
  Legenden-Overlay (z. B. unten links auf der Karte) mit den zwei Farb-Erklärungen
  ergänzen; Styling in [city-map.css](../../../../web/src/app/pages/city-map/city-map.css).
- **Deckt ab:** AK 5.

## Task 6 – Barrierefreiheit

- Layer-Umschalter per Tastatur bedienbar, `aria-pressed`/`aria-checked`, sichtbarer Fokus.
- Popup-Inhalt der Spielstätten-Marker mit sinnvollem Fokus-Handling (Leaflet-Standard prüfen,
  ggf. `keyboard: true` wie bei den bestehenden Ensemble-Markern).
- **Deckt ab:** AK 1–7 (Querschnitt).

## Task 7 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Beim Öffnen der Karte ist nur der Klangkörper-Layer (rot) aktiv (AK 1).
  - Spielstätten-Layer lässt sich explizit aktivieren (blau, AK 2, AK 3).
  - Beide Layer gleichzeitig aktivierbar, Farben korrekt (AK 4, AK 6).
  - Legende erklärt die Farbzuordnung (AK 5).
  - Anzahl/Position der blauen Punkte entspricht den Spielstätten-Datensätzen (AK 7).
  - Einzel-Veranstaltungsort-Karte auf `events/:id` zeigt nun ebenfalls einen blauen
    Marker (Regressionscheck des Seiteneffekts aus Task 2).

## Definition of Done

- Akzeptanzkriterien 1–7 aus [US-033](./US-033-karte-layer-klangkoerper-venues.md) erfüllt.
- Bestehendes Klangkörper-Marker-Verhalten (Dialog, Ort-Filter-Highlighting) unverändert.
- Build erfolgreich; Verhalten manuell geprüft.
