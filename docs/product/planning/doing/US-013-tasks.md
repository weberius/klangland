# US-013 – Umsetzungs-Tasks

Umsetzung von [US-013](./US-013-map-country.md): Kartenseite unter `/cities`, die alle Orte mit
ansässigem Ensemble als rote Leaflet-Marker auf OpenStreetMap zeigt; Klick öffnet einen Dialog
mit den Ensembles des Ortes und einem Button zum Aktivieren/Deaktivieren des Ort-Filters.

## Architektur-Entscheidung (verbindlich)

- **Datenquelle:** `data/*.json` (Repo-Wurzel) ist die Quelle der Wahrheit, `web/public/data/*.json`
  ist die ausgelieferte Kopie (aktuell inhaltsgleich, [angular.json:21-26](../../../../web/angular.json#L21-L26)
  serviert `public/**/*`). Neue Koordinaten müssen in **beide** cities.json geschrieben werden.
- **Koordinaten am City-Objekt:** Die bestehende Schnittstelle
  [`Coordinates`](../../../../web/src/app/models/models.ts#L107-L110) (`{ lat, lng }`, bereits von
  `Venue` genutzt) wird für `City.coordinates` wiederverwendet – kein neues Format.
- **Filter über den Bestand:** Der Ort-Filter wird ausschließlich über den root-bereitgestellten
  [`FilterService`](../../../../web/src/app/core/filter.service.ts) gesetzt
  (`toggleCity(cityId)` / `isCitySelected(cityId)`), damit die geforderte In-App-Persistenz und
  Konsistenz mit US-020 gilt. Kein eigener Filter-Zustand auf der Kartenseite.
- **Kartenbibliothek:** Leaflet als neue Laufzeit-Abhängigkeit (+ `@types/leaflet`), OSM-Rasterkacheln
  mit Pflicht-Attribution. Kein zusätzliches Karten-/UI-Framework.
- **Seitenmuster:** Neue Standalone-Seite analog zu den bestehenden Pages
  ([venue-list](../../../../web/src/app/pages/venue-list/) als Vorlage: `.ts`/`.html`/`.css`),
  lazy geladen über [app.routes.ts](../../../../web/src/app/app.routes.ts). Angular Signals wie im Bestand.

Betroffene Dateien:
- `tools/fetch-city-coordinates.py` (neu) – Overpass-Recherche
- [data/cities.json](../../../../data/cities.json) + [web/public/data/cities.json](../../../../web/public/data/cities.json)
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts)
- [web/package.json](../../../../web/package.json) / [web/angular.json](../../../../web/angular.json)
- `web/src/app/pages/cities-map/` (neu: `.ts`/`.html`/`.css`)
- [web/src/app/app.routes.ts](../../../../web/src/app/app.routes.ts)
- [web/src/app/app.html](../../../../web/src/app/app.html)

---

## Task 1 – Koordinaten recherchieren (Python/Overpass)

- `tools/fetch-city-coordinates.py` anlegen: liest cities.json, ermittelt aus
  [ensembles.json](../../../../data/ensembles.json) alle Orte mit mindestens einem zugeordneten
  Ensemble (Vereinigung aller `ensemble.cityIds`) und fragt für jeden fehlenden Ort die
  **Overpass-API** von OpenStreetMap nach den Koordinaten des Stadtzentrums ab.
- **Ratenbegrenzung:** höchstens **eine Abfrage pro Sekunde** (fester `sleep(1)` zwischen Requests),
  aussagekräftiger `User-Agent`; Fehler/nicht gefundene Orte protokollieren statt abbrechen.
- Ausgabe: schreibt `coordinates: { lat, lng }` je Ort zurück in `data/cities.json` (idempotent –
  vorhandene Koordinaten nicht überschreiben) und aktualisiert `metadata.version`/`lastUpdated`.
- **Deckt ab:** AK 6, AK 7.

## Task 2 – Koordinaten in beide cities.json übernehmen

- Skript gegen `data/cities.json` laufen lassen und das Ergebnis nach
  `web/public/data/cities.json` spiegeln (beide Dateien inhaltsgleich halten).
- Ergebnis stichprobenartig prüfen (z. B. Köln/Aachen/Dortmund liegen plausibel im Stadtgebiet).
- **Deckt ab:** AK 5, AK 6.

## Task 3 – Datenmodell und DataService

- In [models.ts](../../../../web/src/app/models/models.ts#L13-L23) `City` um
  `coordinates?: Coordinates` erweitern (bestehendes `Coordinates`-Interface wiederverwenden).
- In [data.service.ts](../../../../web/src/app/core/data.service.ts) zwei Methoden ergänzen:
  - `mapCities(): City[]` – alle Orte mit **mindestens einem Ensemble** *und* vorhandenen
    `coordinates` (analog zu `filterCities()` bei [data.service.ts:382](../../../../web/src/app/core/data.service.ts#L382),
    aber Kriterium `coordinates` statt `plate`), sortiert nach Name.
  - `ensemblesInCity(cityId: string): Ensemble[]` – alle Ensembles, deren `cityIds` den Ort
    enthalten, sortiert nach Name (Quelle für die Dialog-Liste).
- **Deckt ab:** AK 4, AK 8.

## Task 4 – Leaflet einbinden

- `leaflet` und `@types/leaflet` als Abhängigkeiten in [web/package.json](../../../../web/package.json)
  ergänzen (`npm install`).
- Leaflet-CSS global verfügbar machen (Eintrag in [angular.json](../../../../web/angular.json#L27-L29)
  `styles` oder Import in `styles.css`), damit Karte und Marker korrekt gerendert werden.
- **Deckt ab:** AK 3.

## Task 5 – Kartenseite `cities-map` (Route + Karte)

- Neue Standalone-Komponente `web/src/app/pages/cities-map/` (`.ts`/`.html`/`.css`).
- Route in [app.routes.ts](../../../../web/src/app/app.routes.ts) ergänzen: `path: 'cities'`,
  lazy `loadComponent`, `title: 'Karte · Klangland'`.
- In der Komponente Leaflet nach dem View-Init initialisieren (Kartencontainer-Element),
  OSM-`tileLayer` mit Pflicht-**Attribution** setzen, Kartenausschnitt so wählen, dass alle Marker
  sichtbar sind (z. B. `fitBounds` über die Marker-Koordinaten).
- Für jeden Ort aus `DataService.mapCities()` einen **roten** Marker auf `city.coordinates` setzen
  (roter Punkt via `L.circleMarker` oder `divIcon`; keine Venue-Marker).
- Leaflet-Instanz bei `ngOnDestroy` entfernen (`map.remove()`), um Speicherlecks/HMR-Probleme zu
  vermeiden.
- **Deckt ab:** AK 1, AK 3, AK 4, AK 5.

## Task 6 – Klick-Dialog mit Ensembles und Filter-Button

- Klick auf einen Marker öffnet einen **Dialog/Popover** (Angular-Overlay/Signal-gesteuert oder
  Leaflet-Popup), der den Ortsnamen und die **Ensembles des Ortes**
  (`DataService.ensemblesInCity(city.id)`) auflistet.
- Button im Dialog:
  - Zustand aus `FilterService.isCitySelected(city.id)` ableiten; Beschriftung wechselt zwischen
    „Nach diesem Ort filtern" und „Filter für diesen Ort entfernen".
  - Klick ruft `FilterService.toggleCity(city.id)` – aktiviert bzw. deaktiviert den Ort-Filter.
- Der Filter bleibt danach über den `FilterService` app-weit aktiv (Persistenz beim Seitenwechsel),
  bis er hier oder an den bestehenden Stellen (Popover/Chips, US-020) wieder entfernt wird.
- **Deckt ab:** AK 8, AK 9, AK 10.

## Task 7 – Aktiven Ort auf der Karte hervorheben

- Marker-Darstellung reaktiv an `FilterService.selectedCityIds()` koppeln: Orte, für die der Filter
  aktiv ist, deutlich unterscheidbar hervorheben (z. B. größerer/andersfarbiger Marker oder Rahmen).
- Beim Zurücksetzen des Filters (an den vorhandenen Stellen) verschwindet die Hervorhebung wieder.
- **Deckt ab:** AK 11, AK 12.

## Task 8 – Navigationseintrag „Karte"

- In [app.html:71-73](../../../../web/src/app/app.html#L71-L73) einen vierten Nav-Link ergänzen:
  `<a routerLink="/cities" routerLinkActive="active" (click)="closeMenu()">Karte</a>`
  neben Kalender, Ensembles, Spielstätten.
- **Deckt ab:** AK 2.

## Task 9 – Barrierefreiheit

- Dialog-Button: `type="button"`, aussagekräftiges Label bzw. `aria-pressed`/`aria-label`, das den
  Zustand (aktiv/inaktiv) kommuniziert; per Tastatur erreichbar und bedienbar (Enter/Space),
  sichtbarer Fokus.
- Marker als klickbare Elemente per Tastatur erreichbar bzw. – falls Leaflet dies nicht hergibt –
  eine zugängliche Alternative anbieten (dokumentieren, was umgesetzt wurde).
- **Deckt ab:** AK 13.

## Task 10 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` und im Browser prüfen:
  - `/cities` erreichbar; Nav-Eintrag „Karte" vorhanden und im aktiven Zustand markiert (AK 1, AK 2).
  - Karte lädt OSM-Kacheln inkl. Attribution; nur Ensemble-Orte als rote Marker, keine Venues
    (AK 3, AK 4).
  - Marker sitzen auf dem Stadtzentrum (Stichprobe Köln – nicht auf der Philharmonie) (AK 5).
  - Klick auf Köln öffnet Dialog mit den Kölner Ensembles + Filter-Button (AK 8).
  - Filter aktivieren → zum Kalender wechseln: nur Konzerte mit `cityId` „koeln"; Filter bleibt beim
    Navigieren aktiv (AK 9, AK 10).
  - Aktiver Ort auf der Karte hervorgehoben; Zurücksetzen (Popover/Chips) entfernt Filter und
    Hervorhebung (AK 11, AK 12).
  - Tastaturbedienung des Filter-Buttons inkl. Zustands-ARIA (AK 13).

## Definition of Done

- Akzeptanzkriterien 1–13 aus [US-013](./US-013-map-country.md) erfüllt.
- Koordinaten für alle Ensemble-Orte in `data/` und `web/public/data/` gepflegt; Recherche-Skript
  mit ≤ 1 Abfrage/Sekunde vorhanden.
- Kartenseite zeigt ausschließlich rote Ensemble-Orte auf Stadt-Koordinaten; Filter läuft über den
  bestehenden `FilterService` (In-App-Persistenz, konsistent mit US-020).
- `npm run build` ohne Fehler; keine Änderungen an Detailseiten oder der bestehenden Filterlogik
  über die Nutzung des `FilterService` hinaus.
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben.
