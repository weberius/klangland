# US-020 – Umsetzungs-Tasks

Umsetzung von [US-020](./us-020-filter.md): kombinierter Filter (Ort + Musikprofil) über einen
Filter-Button mit Popover in der Kopfleiste, schmalere Suche und aktive Filter als entfernbare
Chips unterhalb der Seitenüberschrift. Aufbauend auf dem bestehenden US-011-Ort-Filter.

## Architektur-Entscheidung (verbindlich)

- Der bestehende root-bereitgestellte [FilterService](../../../../web/src/app/core/filter.service.ts)
  wird um einen **zweiten Zustand** `selectedProfiles` erweitert; er bleibt die einzige Quelle
  der Filterauswahl (In-App-Persistenz, kein `localStorage`/`sessionStorage`).
- **Ableitungslogik** (verfügbare Profile, kombinierte Filterung) liegt weiterhin als reine
  Methoden im [DataService](../../../../web/src/app/core/data.service.ts). Die drei
  `*ForCities`-Methoden werden auf ein **gemeinsames Ensemble-Prädikat**
  `ensembleMatches(ensemble, cityIds, profiles)` umgestellt (ODER innerhalb, UND zwischen den
  Kategorien; Ort und Profil müssen von demselben Ensemble erfüllt werden).
- Der **Filter-Auslöser wandert in die Kopfleiste** ([app.html](../../../../web/src/app/app.html)),
  da der Filter global wirkt. Die bisherige Dauer-Bubblezeile in
  [city-filter](../../../../web/src/app/shared/city-filter/) wird zur reinen
  **Aktiv-Chip-Leiste** unter der Überschrift umgebaut (Info-Button bleibt).
- Popover-Interaktionen (Außenklick, ESC, Schließen bei Navigation) folgen dem bestehenden
  Muster der globalen Suche in [app.ts](../../../../web/src/app/app.ts#L141-L159).
- Kein zusätzliches State-Management- oder UI-Framework; nur Angular Signals wie im Bestand.

Betroffene Dateien:
- [web/src/app/core/filter.service.ts](../../../../web/src/app/core/filter.service.ts)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts)
- [web/src/app/shared/filter-menu/](../../../../web/src/app/shared/) (neu: Kopfleisten-Button + Popover)
- [web/src/app/shared/city-filter/](../../../../web/src/app/shared/city-filter/) (Umbau zu Aktiv-Chips)
- [web/src/app/app.html](../../../../web/src/app/app.html) / [app.css](../../../../web/src/app/app.css)
- [web/src/app/pages/calendar/calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts)
- [web/src/app/pages/ensemble-list/ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts)
- [web/src/app/pages/venue-list/venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts)
- [docs/product/contracts/filter.feature](../../contracts/filter.feature) / [ears/filter.md](../../ears/filter.md)
- [docs/product/contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md)

---

## Task 1 – FilterService um Musikprofil-Auswahl erweitern

- In [filter.service.ts](../../../../web/src/app/core/filter.service.ts) zweiten Zustand
  `selectedProfiles = signal<ReadonlySet<MusicalProfile>>(new Set())` mit `selectedProfiles`
  (readonly), `isProfileSelected(profile)` und `toggleProfile(profile)` ergänzen.
- `hasSelection` auf „Städte **oder** Profile aktiv" erweitern.
- Neu: `reset()` (leert beide Sets) und `activeCount` (computed: `cities.size + profiles.size`)
  für den Aktiv-Zähler des Buttons.
- **Deckt ab:** AK 2, AK 6, AK 7, AK 12, AK 14, AK 15.

## Task 2 – DataService: Profil-Quelle und kombinierte Filterung

- `filterProfiles(): MusicalProfile[]` ergänzen: alle bei mindestens einem Ensemble
  vorkommenden `musicalProfiles`, sortiert nach deutschem Label
  ([labels.ts](../../../../web/src/app/core/labels.ts#L25)); keine leeren Profile.
- Gemeinsames Prädikat `ensembleMatches(ensemble, cityIds, profiles)` einführen:
  `(cityIds leer ODER Sitzort-Schnitt) UND (profiles leer ODER Profil-Schnitt)`.
- Die drei bestehenden Methoden darauf umstellen bzw. um den Profil-Parameter erweitern:
  - `eventsForCities` → `eventsForFilter(cityIds, profiles)`: Events mit mindestens einem
    auftretenden Ensemble, das `ensembleMatches` erfüllt (ersetzt `ensemblesSitInCities`).
  - `ensemblesForCities` → `ensemblesForFilter(cityIds, profiles)`.
  - `venuesForCities` → `venuesForFilter(cityIds, profiles)` (über die gefilterten Events).
- Leere Gesamtauswahl = alle Inhalte (Aufrufer-Konvention beibehalten).
- **Deckt ab:** AK 5, AK 7, AK 8, AK 9, AK 10, AK 11 (technische Grundlage).

## Task 3 – Kopfleisten-Komponente `filter-menu` (Button + Popover)

- Neue Standalone-Komponente (z. B. `web/src/app/shared/filter-menu/`), gerendert in
  [app.html](../../../../web/src/app/app.html) zwischen Suchcontainer und `nav-toggle`.
- Button: Pill mit Label „Filter" und Aktiv-Zähler-Badge (`FilterService.activeCount`),
  `aria-haspopup="true"`, `aria-expanded`, `aria-controls` auf das Popover.
- Popover mit zwei Abschnitten:
  - **Ort:** Chips aus `DataService.filterCities()` (Kfz-Kennzeichen), `toggle(city.id)`.
  - **Musikprofil:** Chips aus `DataService.filterProfiles()` (deutsches Label),
    `toggleProfile(profile)`.
  - Chips als `<button aria-pressed>` mit sichtbarer Markierung des Auswahlzustands.
  - „Zurücksetzen"-Aktion (nur bei `hasSelection`), ruft `reset()`.
- Schließen bei Außenklick, ESC und Navigation (Muster aus
  [app.ts](../../../../web/src/app/app.ts#L141-L159); eigener `ElementRef` + `HostListener`
  oder Orchestrierung im App-Root).
- **Deckt ab:** AK 1, AK 2, AK 4, AK 5, AK 14, AK 15, AK 16, AK 18, AK 19.

## Task 4 – `city-filter` zu Aktiv-Chip-Leiste umbauen

- In [city-filter](../../../../web/src/app/shared/city-filter/) die Dauer-Bubblezeile
  entfernen. Stattdessen die **aktiven Filter als entfernbare Chips** rendern (Kennzeichen für
  Orte, deutsches Label für Profile), jeder Chip mit „✕"-Button, der den jeweiligen Filter
  über `toggle`/`toggleProfile` entfernt.
- Ohne aktive Auswahl wird außer dem Info-Button nichts angezeigt (footprint = 0).
- Info-Button („i") + Beschreibung unverändert erhalten (`description`-Input bleibt); der
  Info-Button wird **hinter der Überschrift** platziert, sein Verhalten ändert sich nicht.
- Komponente bleibt in Kalender-, Ensemble- und Spielstätten-Template eingebunden.
- **Deckt ab:** AK 13, AK 15, AK 17.

## Task 5 – Suche schmaler und Kopfleisten-Layout

- In [app.css](../../../../web/src/app/app.css#L49) `.global-search` schmaler dimensionieren
  (z. B. `flex: 1 1 12rem`, `max-width: 34rem`), sodass der Filter-Button daneben Platz hat.
- Filter-Button-Styling nach Designsystem (Pill/Icon, Badge, Fokus-/Hover-/Active-Zustände);
  Popover-Stil analog zu `.search-results` (Fläche, Rahmen, Schatten, Radius, `z-index`).
- Responsives Verhalten (`@media (max-width: 720px)`): Filter-Button ggf. auf Symbol + Badge
  reduzieren; Kopfleiste bleibt aufgeräumt.
- **Deckt ab:** AK 3, AK 20.

## Task 6 – Seiten auf kombinierte Filterung umstellen

- [calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts#L48): gefilterte Events über
  `eventsForFilter(selectedIds(), selectedProfiles())` beziehen (Monatsraster, Agenda, Zähler).
- [ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts#L22):
  `ensemblesForFilter(...)`.
- [venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts#L20):
  `venuesForFilter(...)`.
- Reaktiv an beide FilterService-Signale koppeln (computed).
- **Deckt ab:** AK 9, AK 10, AK 11, AK 12.

## Task 7 – Barrierefreiheit absichern

- Filter-Button: `aria-haspopup`, `aria-expanded`, `aria-controls`, Tastaturbedienung,
  sichtbarer Fokus.
- Popover-Chips: `aria-pressed`; Aktiv-Chips unter der Überschrift: „✕"-Buttons mit
  aussagekräftigem `aria-label` (z. B. „Filter Köln entfernen").
- Fokusreihenfolge/-rückgabe beim Öffnen/Schließen des Popovers sinnvoll.
- **Deckt ab:** AK 16, AK 19.

## Task 8 – Produktspezifikation aktualisieren (Contract + EARS)

- [filter.feature](../../contracts/filter.feature) um Szenarien zu Musikprofil-Filter,
  Popover-Interaktion, kombinierter UND/ODER-Semantik, Aktiv-Chips und Zurücksetzen ergänzen.
- [filter.md](../../ears/filter.md) um stabile IDs für die neuen Anforderungen erweitern.
- [contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md)
  auf US-020 aktualisieren.
- **Deckt ab:** AK 1–20.

## Task 9 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Kopfleiste: schmalere Suche + Filter-Button mit Zähler zwischen Suche und Navigation
    (AK 1–3).
  - Popover zeigt Ort-Chips (Kennzeichen) und Musikprofil-Chips (nur vorkommende Profile)
    (AK 4, AK 5).
  - Standardzustand ohne Auswahl zeigt alle Inhalte (AK 6).
  - ODER innerhalb Kategorie, UND zwischen Kategorien; dasselbe Ensemble muss beide erfüllen
    (AK 7, AK 8) – Gegenprobe mit Kölner Jazz- vs. Klassik-Ensemble.
  - Wirkung auf Kalender, Ensembles, Spielstätten; Persistenz beim Seitenwechsel (AK 9–12).
  - Aktive Chips unter der Überschrift entfernbar; „Zurücksetzen" leert alles; Abwählen im
    Popover; Markierung sichtbar (AK 13–16).
  - Info-Button funktioniert weiter (AK 17).
  - Popover schließt bei Außenklick/ESC/Navigation (AK 18).
  - Tastaturbedienung und Zustands-ARIA (AK 19); Verhalten in schmalem Viewport (AK 20).

## Definition of Done

- Akzeptanzkriterien 1–20 aus [US-020](./us-020-filter.md) erfüllt.
- Filter wirkt global über Ort + Musikprofil (ODER innerhalb, UND zwischen; gleiche-Ensemble-
  Semantik) auf allen drei Listen; keine Änderungen an Detailseiten oder Suchlogik.
- Auswahl persistiert während der Navigation, nicht über Reload/Session hinaus.
- Dauer-Bubblezeile entfernt; Filter beansprucht ohne Auswahl keinen Platz unter der
  Überschrift.
- Build erfolgreich; Filter- und Popover-Verhalten manuell mit Positiv-/Negativfällen geprüft.
