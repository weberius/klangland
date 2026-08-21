# US-023 – Umsetzungs-Tasks

Umsetzung von [US-023](./us-023-events.md): Die Veranstaltungsdetailseite
([event-detail](../../../../web/src/app/pages/event-detail/)) wird neu strukturiert (2×2-Raster mit
Programm, Mitwirkende, Veranstaltungsort, Karte), die Event-Beschreibung wird angezeigt, ein
Routing-Dialog und eine Karte des Veranstaltungsortes kommen hinzu.

## Architektur-Entscheidungen (verbindlich)

- **Nur Frontend, keine Datenänderung:** Adresse (`Venue.address`) und Koordinaten
  (`Venue.coordinates`) stammen aus US-022 und liegen bereits vor. `events.json`/`venues.json` sowie
  die Datenmodelle in [models.ts](../../../../web/src/app/models/models.ts) werden **nicht** geändert.
- **Karte:** wiederverwendetes Muster der [city-map](../../../../web/src/app/pages/city-map/city-map.ts)-Seite:
  **Leaflet** (`import * as L from 'leaflet'`) mit **OpenStreetMap**-Kacheln inkl. Attribution. Die
  Leaflet-Basis-CSS ist bereits global eingebunden ([styles.css:3](../../../../web/src/styles.css#L3)),
  daher **keine** zusätzliche CSS-Einbindung nötig. Marker als `L.divIcon` (vermeidet das bekannte
  Problem fehlender Default-Marker-Bilder im Angular-Build).
- **Routing:** plattformübergreifend über **reguläre Karten-Links** (URLs) zu mehreren Anbietern
  (Google Maps, Apple Maps, OpenStreetMap), geöffnet in neuem Tab (`target="_blank" rel="noopener"`).
  Kein Deep-Link-/URL-Scheme-Bastelwerk, keine Geräteerkennung – der Ziel-Link nutzt bevorzugt die
  Koordinaten, hilfsweise die formatierte Adresse.
- **Dialog:** Wiederverwendung des bestehenden Verlassen-Hinweis-Dialog-Musters (Backdrop,
  `role="dialog"`, `aria-modal`, `aria-labelledby`, Abbrechen) aus dem Ticket-Dialog
  ([event-detail.html:130-148](../../../../web/src/app/pages/event-detail/event-detail.html#L130-L148),
  [event-detail.css:91-125](../../../../web/src/app/pages/event-detail/event-detail.css#L91-L125)).
- **Unverändert:** Seitenkopf (Titel/Datum/Status/Buttons), Ticket-Dialog und Quelle-Abschnitt
  bleiben in Inhalt und Verhalten wie bisher.

Betroffene Dateien:
- [web/src/app/pages/event-detail/event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts)
- [web/src/app/pages/event-detail/event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css)
- ggf. [web/src/styles.css](../../../../web/src/styles.css) (globaler Marker-Style, falls nicht wiederverwendet)

---

## Task 1 – Boxen-Layout auf 2×2-Raster umstellen (HTML/CSS)

- In [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html) die vier
  Inhaltsblöcke in **eine** gemeinsame `.detail-grid`-Container in dieser DOM-Reihenfolge legen:
  1. **Programm** (bisher [event-detail.html:83-109](../../../../web/src/app/pages/event-detail/event-detail.html#L83-L109), aktuell außerhalb des Rasters) → jetzt als erste Box
  2. **Mitwirkende** (bisher [event-detail.html:39-64](../../../../web/src/app/pages/event-detail/event-detail.html#L39-L64))
  3. **Veranstaltungsort** (bisher [event-detail.html:66-80](../../../../web/src/app/pages/event-detail/event-detail.html#L66-L80))
  4. **Karte** (neu, siehe Task 4)
- Die DOM-Reihenfolge erfüllt beides gleichzeitig: Desktop-Grid füllt zeilenweise
  (oben links Programm, oben rechts Mitwirkende, unten links Veranstaltungsort, unten rechts Karte)
  und die mobile Einspaltigkeit stapelt in exakt dieser Reihenfolge.
- CSS in [event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css): `.detail-grid`
  bleibt `grid-template-columns: 1fr 1fr` mit `@media (max-width: 720px)` → 1 Spalte
  ([event-detail.css:38-42](../../../../web/src/app/pages/event-detail/event-detail.css#L38-L42),
  [event-detail.css:127-131](../../../../web/src/app/pages/event-detail/event-detail.css#L127-L131)).
  Die Programm-Box erhält die Klassen `card detail-block` wie die übrigen Boxen; die bisherige
  Voll-Breiten-Darstellung des Programms entfällt.
- **Deckt ab:** AK 1, AK 2, AK 3.

## Task 2 – Event-Beschreibung in der Programm-Box anzeigen

- In der Programm-Box **oberhalb** der Werkliste die Beschreibung rendern, wenn gesetzt:
  `@if (event()!.description) { <p class="event-description">{{ event()!.description }}</p> }`
  (Klartext; kein Markdown).
- Reconcile mit der bestehenden `programFallbackText()`-Heuristik
  ([event-detail.ts:109-114](../../../../web/src/app/pages/event-detail/event-detail.ts#L109-L114)):
  Da die Beschreibung nun **immer** oben in der Box steht, wird die Sonderbehandlung, die
  „Werke von …"-Beschreibungen als Programmkörper ausgab, **entfernt**. Neue Logik der Werkliste:
  - Programm vorhanden → Werkliste (`<ol class="program">`) wie bisher.
  - Programm leer und **keine** Beschreibung → „Kein Programm erfasst." (unverändert).
  - Programm leer und Beschreibung vorhanden → kein zusätzlicher Hinweis (die Beschreibung deckt es ab);
    verhindert doppelte Anzeige desselben Textes.
- `programFallbackText`-Computed samt Nutzung aus [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts)
  und Template entfernen bzw. auf die obige, einfachere Bedingung reduzieren.
- **Deckt ab:** AK 4.

## Task 3 – Veranstaltungsort-Box mit Adresse (bestätigen/anpassen)

- Die Box zeigt weiterhin Name (verlinkt), Stadt, Adresse (`venueAddress()`,
  [event-detail.ts:101](../../../../web/src/app/pages/event-detail/event-detail.ts#L101)) und ggf.
  Website ([event-detail.html:66-80](../../../../web/src/app/pages/event-detail/event-detail.html#L66-L80)).
  Fehlende Bestandteile werden per `@if` ohne Leerzeilen weggelassen (bereits so umgesetzt).
- Innerhalb dieser Box den Routing-Button (Task 4) ergänzen.
- **Deckt ab:** AK 5.

## Task 4 – Routing-Button mit Anbieter-Dialog

- **event-detail.ts:**
  - Signal `mapsDialogOpen = signal(false)` sowie `openMapsDialog()`/`closeMapsDialog()` analog zum
    Ticket-Dialog ([event-detail.ts:67-78](../../../../web/src/app/pages/event-detail/event-detail.ts#L67-L78)).
  - Computed `canRoute` = `true`, wenn `venue()?.coordinates` **oder** `venueAddress()` vorhanden.
  - Computed `mapsLinks` liefert die Ziel-URLs (bevorzugt Koordinaten `lat,lng`, sonst
    `encodeURIComponent(venueAddress())`):
    - Google Maps: `https://www.google.com/maps/dir/?api=1&destination=<lat,lng|addr>`
    - Apple Maps: `https://maps.apple.com/?daddr=<lat,lng|addr>`
    - OpenStreetMap: `https://www.openstreetmap.org/directions?to=<lat,lng>` bzw.
      `https://www.openstreetmap.org/search?query=<addr>`
- **event-detail.html:**
  - In der Veranstaltungsort-Box `@if (canRoute()) { <button class="btn" (click)="openMapsDialog()">Route/Karten-App öffnen</button> }`.
  - Dialog analog zum Ticket-Dialog (Backdrop + `.dialog`, `role="dialog"`, `aria-modal="true"`,
    `aria-labelledby`): Überschrift, **Hinweis auf Verlassen des Angebots**, Liste der Anbieter-Links
    (`<a [href]="…" target="_blank" rel="noopener">`), Abbrechen-Button. Backdrop-Klick schließt.
- **Deckt ab:** AK 6, AK 7, AK 8; AK 10 (kein Button ohne Koordinaten und Adresse).

## Task 5 – Karte des Veranstaltungsortes (Leaflet)

- **event-detail.ts:**
  - Imports/Signaturen analog [city-map.ts](../../../../web/src/app/pages/city-map/city-map.ts):
    `import * as L from 'leaflet'`, `afterNextRender`, `viewChild`, `ElementRef`, `implements OnDestroy`.
  - `mapContainer = viewChild<ElementRef<HTMLElement>>('map')` (optional, da nur bei Koordinaten
    gerendert). Im Konstruktor `afterNextRender(() => this.initMap())`.
  - `initMap()`: nur ausführen, wenn Container **und** `venue()?.coordinates` vorhanden. Karte auf die
    Koordinaten zentrieren (`L.map(el, { center: [lat, lng], zoom: 15 })`), OSM-`tileLayer` mit
    derselben Attribution wie city-map, einen `L.marker` mit `L.divIcon` setzen.
  - `ngOnDestroy()`: `this.map?.remove()` (Leaflet-Instanz freigeben).
- **event-detail.html:** vierte Box als `section.card.detail-block` mit
  `@if (venue()?.coordinates) { <h2>Karte</h2><div #map class="event-map"></div> }`. Ohne Koordinaten
  wird **keine** (leere) Box gerendert.
- **Deckt ab:** AK 9, AK 10 (keine Karte ohne Koordinaten).

## Task 6 – Karten-Styling

- In [event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css) `.event-map`
  formatieren (Höhe/Rahmen/Radius, eigener Stacking-Context), angelehnt an
  [city-map.css:4-16](../../../../web/src/app/pages/city-map/city-map.css#L4-L16):
  ```css
  .event-map {
    height: min(40vh, 320px);
    width: 100%;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    overflow: hidden;
    position: relative;
    z-index: 0; /* sperrt Leaflet-z-indices in die Karte ein */
  }
  ```
- Marker-Style für den `L.divIcon`: entweder die bereits **global** vorhandenen Klassen
  `.city-marker-wrap`/`.city-marker` (city-map nutzt `ViewEncapsulation.None`) wiederverwenden **oder**
  einen kleinen dedizierten Marker-Style global in [styles.css](../../../../web/src/styles.css)
  ergänzen. Component-CSS von event-detail bleibt gekapselt – die Marker-Klasse **muss** global sein.
- **Deckt ab:** AK 9 (sichtbare, korrekt eingezoomte Karte mit Marker).

## Task 7 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` und im Browser prüfen:
  - **Desktop (> 720px):** 2×2-Raster – Programm oben links, Mitwirkende oben rechts,
    Veranstaltungsort unten links, Karte unten rechts (AK 1, AK 2).
  - **Mobil (≤ 720px, DevTools):** Reihenfolge Programm → Mitwirkende → Veranstaltungsort → Karte (AK 3).
  - Event **mit** Beschreibung: Beschreibung steht oben in der Programm-Box über der Werkliste;
    Event **ohne** Beschreibung: keine Beschreibung, Werkliste/„Kein Programm erfasst." wie erwartet (AK 4).
  - Veranstaltungsort zeigt Adresse; ein Venue ohne Adresse zeigt keine Adresszeile (AK 5).
  - Routing-Button öffnet Dialog mit Anbieter-Links (Google/Apple/OSM), Hinweis auf Verlassen des
    Angebots vorhanden; Links öffnen im neuen Tab und zeigen den Ort; Abbrechen/Backdrop schließt (AK 6–8).
  - Venue **mit** Koordinaten: Karte zoomt auf den Ort mit Marker + OSM-Attribution; Venue **ohne**
    Koordinaten: keine Kartenbox, kein Routing-Button falls auch keine Adresse (AK 9, AK 10).
  - Seitenkopf, Ticket-Dialog und Quelle unverändert (AK 11).
- Beim Verlassen der Seite keine Konsolenfehler (Leaflet-Instanz wird via `ngOnDestroy` entfernt).

## Definition of Done

- Akzeptanzkriterien 1–11 aus [US-023](./us-023-events.md) erfüllt.
- Layout auf 2×2-Raster (Desktop) / gestapelt (Mobil) umgestellt; Programm zuerst; Beschreibung in der
  Programm-Box; `programFallbackText`-Sonderfall bereinigt (keine Doppelanzeige).
- Routing-Dialog mit mehreren Kartenanbietern und Verlassen-Hinweis; Karte (Leaflet/OSM) des
  Veranstaltungsortes inkl. sauberem `ngOnDestroy`.
- Keine Änderungen an Datenmodellen oder `events.json`/`venues.json`; `npm run build` ohne Fehler.
- Story- und Tasks-Datei nach Abschluss von `doing/` nach `done/` verschieben.
