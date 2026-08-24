# US-034 – Umsetzungs-Tasks

Umsetzung von [US-034](./US-034-venues-detail-karte-navigation.md): Die
Spielstätten-Detailseite (`venues/:id`) erhält dieselbe Karten- und
Karten-App-Navigationsdarstellung wie die Event-Detailseite (`events/:id`) – umgesetzt als
gemeinsame, wiederverwendbare Komponente.

## Architektur-Entscheidung (verbindlich)

- **Extraktion statt Duplikation:** Die bestehende Karten-/Navigationslogik aus
  [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts)
  (Leaflet-Karte via `initMap()`, `mapsLinks`-Computed, `mapsDialogOpen`-Signal,
  `openMapsDialog()`/`closeMapsDialog()`) wird in eine neue, eigenständige Komponente
  `web/src/app/shared/venue-location/venue-location.ts` extrahiert. Die Komponente erhält
  Name, Adresse und Koordinaten als `input()` (z. B. über den `Venue`-Typ direkt, oder
  einzelne Felder – Entscheidung in Task 1 konkretisieren) und kapselt: eingebettete Karte,
  „Route / Karten-App öffnen"-Button, Auswahldialog (Google Maps/Apple Maps/OpenStreetMap).
- `event-detail.ts`/`.html` werden auf die neue Komponente umgestellt (kein
  Verhaltensunterschied für Endnutzer:innen, aber DRY).
- `venue-detail.ts`/`.html` bindet dieselbe Komponente zusätzlich zu Ort/Adresse ein
  (Desktop: eigene Box in `profile-facts`/`profile-grid`).
- **Marker-Farbe:** blau, über den Token `--color-info`/die Klasse `.venue-marker`, die in
  [US-033, Task 2](./US-033-tasks.md) eingeführt wird. Falls US-033 noch nicht umgesetzt
  ist, wird der Token hier in [styles.css](../../../../web/src/styles.css) ergänzt (nicht
  doppelt anlegen, falls bereits vorhanden).
- Mobile Darstellung: Karten-Box kann auf schmalen Viewports reduziert dargestellt werden
  (z. B. nur Button sichtbar, Karte ausgeblendet oder kollabiert) – konkretes Verhalten wird
  an das bestehende responsive Muster von `event-detail.css`/`venue-detail.css` angelehnt.

Betroffene Dateien:

- [web/src/app/shared/venue-location/](../../../../web/src/app/shared/) (neu:
  `venue-location.ts`/`.html`/`.css`)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) / [.html](../../../../web/src/app/pages/event-detail/event-detail.html) / [.css](../../../../web/src/app/pages/event-detail/event-detail.css)
- [web/src/app/pages/venue-detail/venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts) / [.html](../../../../web/src/app/pages/venue-detail/venue-detail.html) / [.css](../../../../web/src/app/pages/venue-detail/venue-detail.css)
- [web/src/styles.css](../../../../web/src/styles.css) (nur falls `--color-info` noch nicht
  aus US-033 vorhanden)

---

## Task 1 – Gemeinsame Komponente `venue-location` erstellen

- Neue Standalone-Komponente `web/src/app/shared/venue-location/venue-location.ts` mit
  `input()` für Name, Adresse (formatiert, z. B. via
  [formatAddress](../../../../web/src/app/core/address.ts)) und `coordinates: Coordinates |
  null`.
- Leaflet-Kartenaufbau (`afterNextRender`/`viewChild`/`L.Map`), Marker als `divIcon` mit der
  Klasse `.venue-marker` (blau, siehe Architektur-Entscheidung), `ngOnDestroy` für
  `map.remove()` – Logik 1:1 aus
  [event-detail.ts:244-269](../../../../web/src/app/pages/event-detail/event-detail.ts#L244-L269)
  übernehmen.
- `mapsLinks`-Computed (Google Maps/Apple Maps/OpenStreetMap-Links) und
  Auswahldialog-Markup/-Logik aus
  [event-detail.ts:108-143](../../../../web/src/app/pages/event-detail/event-detail.ts#L108-L143)
  und [event-detail.html:111-116,165-185](../../../../web/src/app/pages/event-detail/event-detail.html#L111-L116)
  übernehmen.
- **Deckt ab:** Grundlage für AK 1, AK 2, AK 3, AK 5.

## Task 2 – event-detail auf die neue Komponente umstellen

- In [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) die
  extrahierte Karten-/Dialoglogik entfernen, `VenueLocation` importieren und mit den
  Venue-Daten des aktuellen Events instanziieren.
- In [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html) den
  Abschnitt „Veranstaltungsort"/„Karte" (Zeilen 97-123) entsprechend anpassen.
- Regressionscheck: Bestehendes Verhalten und Erscheinungsbild bleiben für `events/:id`
  unverändert.
- **Deckt ab:** AK 4 (Konsistenz-Grundlage, Ausgangsseite).

## Task 3 – venue-detail: Komponente einbinden

- In [venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts)
  `VenueLocation` importieren und mit `venue()` instanziieren.
- In [venue-detail.html](../../../../web/src/app/pages/venue-detail/venue-detail.html) eine
  zusätzliche Box neben `profile-facts` (Ort/Adresse) für die Karte ergänzen (Desktop-Layout,
  analog zum `detail-grid`-Muster aus `event-detail.html`).
- **Deckt ab:** AK 1, AK 3, AK 4.

## Task 4 – Marker-Farbe sicherstellen

- Prüfen, ob `--color-info`/`.venue-marker` (blau) bereits aus US-033 vorhanden ist; falls
  nicht, hier in [styles.css](../../../../web/src/styles.css) ergänzen (keine doppelte
  Token-Definition).
- **Deckt ab:** AK 2.

## Task 5 – Responsives Verhalten prüfen

- Mobile Darstellung von `venues/:id` mit der neuen Karten-Box sichten und ggf. CSS
  anpassen (z. B. volle Breite, Kartenhöhe), konsistent zum bestehenden Verhalten auf
  `events/:id`.
- **Deckt ab:** AK 6.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - `venues/:id` zeigt in der Desktop-Ansicht eine Karten-Box mit blauem Marker (AK 1, AK 2).
  - Button „In Karten-App öffnen" öffnet den bekannten Auswahldialog (AK 3).
  - `events/:id` und `venues/:id` zeigen die Karten-/Navigationsdarstellung optisch und
    funktional identisch (AK 4).
  - Beide Seiten nutzen dieselbe Komponente (Code-Review: kein duplizierter Karten-Code)
    (AK 5).
  - Mobile Ansicht verhält sich sinnvoll (AK 6).

## Definition of Done

- Akzeptanzkriterien 1–6 aus [US-034](./US-034-venues-detail-karte-navigation.md) erfüllt.
- Karten-/Navigationslogik existiert nur noch einmal (in `venue-location`), `event-detail`
  und `venue-detail` sind reine Konsumenten.
- Build erfolgreich; Verhalten manuell auf beiden Seiten geprüft.
