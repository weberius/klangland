# US-011 – Umsetzungs-Tasks

Umsetzung von [US-011](./US-011-filter.md): Ort-Filter als Bubbles unterhalb der
Seitenüberschrift für Kalender, Ensembles und Spielstätten, gesteuert über den
**Sitzort der Ensembles** (`ensemble.cityIds`). Zusätzlich: Beschreibung hinter Info-Button
und einheitliche Burger-Navigation in allen Viewports.

## Architektur-Entscheidung (verbindlich)

- Die Filterauswahl lebt in einem **eigenen, root-bereitgestellten `FilterService`**
  (`@Injectable({ providedIn: 'root' })`) als Signal `selectedCityIds` (`Set<string>`).
  Root-Bereitstellung sorgt für die geforderte **In-App-Persistenz** über Seitenwechsel
  hinweg, ohne `localStorage`/`sessionStorage` (Reload-Persistenz ist Out of Scope).
- **Ableitungslogik** (Bubble-Städte, gefilterte Listen) wird als reine Hilfsmethoden im
  [DataService](../../../../web/src/app/core/data.service.ts) ergänzt, damit Seiten- und
  Filterlogik nicht auf Rohdaten arbeiten. Der `FilterService` hält nur den Zustand.
- Kein zusätzliches State-Management-Framework; ausschließlich Angular Signals wie im
  Bestand (vgl. Such-Umsetzung in [app.ts](../../../../web/src/app/app.ts)).

Betroffene Dateien:
- [data/cities.json](../../../../data/cities.json) (Kfz-Kennzeichen ergänzen)
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts) (`City.plate`)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (Ableitungen)
- [web/src/app/core/filter.service.ts](../../../../web/src/app/core/filter.service.ts) (neu)
- [web/src/app/pages/calendar/calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts) / [.html](../../../../web/src/app/pages/calendar/calendar.html)
- [web/src/app/pages/ensemble-list/ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts) / [.html](../../../../web/src/app/pages/ensemble-list/ensemble-list.html)
- [web/src/app/pages/venue-list/venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts) / [.html](../../../../web/src/app/pages/venue-list/venue-list.html)
- Gemeinsame Filterleiste-Komponente (neu, z. B. `web/src/app/shared/city-filter/`)
- [web/src/app/app.html](../../../../web/src/app/app.html) / [app.css](../../../../web/src/app/app.css) (Burger-Nav)
- [docs/product/contracts/filter.feature](../../contracts/filter.feature) (neu)
- [docs/product/ears/filter.md](../../ears/filter.md) (neu)
- [docs/product/contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md)

---

## Task 1 – Kfz-Kennzeichen im Datenmodell verankern

- In [models.ts](../../../../web/src/app/models/models.ts) das Interface `City` um ein
  Feld `plate: string` (Kfz-Kennzeichen) erweitern.
- In [cities.json](../../../../data/cities.json) **ausschließlich zu den Städten mit
  ansässigem Ensemble** (d. h. den bubble-relevanten Städten) das korrekte Kfz-Kennzeichen
  recherchieren und als `plate` ergänzen (z. B. Köln → `K`, Düsseldorf → `D`,
  Dortmund → `DO`, Essen → `E`, Wuppertal → `W`, Bonn → `BN`, Aachen → `AC`). Kennzeichen
  ausschließlich anhand offizieller Zuordnung setzen; kreisangehörige Orte tragen das
  Kreis-Kennzeichen. Städte ohne ansässiges Ensemble erhalten kein `plate` und erzeugen
  keine Bubble.
- Da `plate` damit optional ist, im Modell als `plate?: string` (bzw. `string | null`)
  führen und die Bubble-Quelle so umsetzen, dass Städte ohne Kennzeichen übersprungen
  werden.
- **Deckt ab:** AK 2, AK 3.

## Task 2 – FilterService mit persistenter Ort-Auswahl

- Neue Datei [filter.service.ts](../../../../web/src/app/core/filter.service.ts) mit
  `@Injectable({ providedIn: 'root' })`.
- Zustand `selectedCityIds = signal<ReadonlySet<string>>(new Set())` plus API:
  `isSelected(cityId)`, `toggle(cityId)` (An-/Abwählen), `hasSelection` (computed),
  `selectedIds` (readonly).
- Kein Persistieren über Reload/Session hinaus; Root-Instanz genügt für Persistenz
  während der Navigation.
- **Deckt ab:** AK 4, AK 8, AK 9, AK 11.

## Task 3 – Ableitungslogik im DataService

- In [data.service.ts](../../../../web/src/app/core/data.service.ts) reine Hilfsmethoden
  ergänzen, die den Sitzort der Ensembles auswerten:
  - `filterCities()`: alle Städte, in denen **mindestens ein Ensemble** seinen Sitz hat
    (aus `ensemble.cityIds`), alphabetisch/sinnvoll sortiert – Quelle der Bubbles.
    Städte, die nur als Veranstaltungsort auftreten, sind ausgeschlossen.
  - `eventsForCities(cityIds)`: Events, bei denen **mindestens ein** auftretendes
    Ensemble (`event.ensembleIds`) seinen Sitz in einer der `cityIds` hat.
  - `ensemblesForCities(cityIds)`: Ensembles mit `cityIds`-Schnitt zur Auswahl.
  - `venuesForCities(cityIds)`: Spielstätten, in denen Ensembles der ausgewählten Städte
    auftreten (über `eventsForCities → venueId → venue`), unabhängig vom Venue-Standort.
- Leere Auswahl bedeutet in allen drei Fällen „alles anzeigen" (Aufrufer-Konvention
  dokumentieren).
- **Deckt ab:** AK 1, AK 5, AK 6, AK 7 (technische Grundlage).

## Task 4 – Wiederverwendbare Filterleiste (Bubbles)

- Neue Standalone-Komponente `city-filter` (z. B. `web/src/app/shared/city-filter/`),
  die die Bubble-Reihe rendert und `DataService.filterCities()` + `FilterService` nutzt.
- Je Stadt eine Bubble mit dem **Kfz-Kennzeichen** als Beschriftung; Klick ruft
  `FilterService.toggle(cityId)`.
- Bubbles als echte `<button>`-Elemente (Tastaturbedienung, Enter/Space) mit
  `aria-pressed` für den Auswahlzustand; ausgewählte Bubbles sichtbar markiert.
- Info-Button („i") als Toggle für die Seitenbeschreibung: eigener Button mit
  `aria-expanded`, der einen per Content-Projection/Input übergebenen Beschreibungstext
  ein-/ausblendet.
- **Deckt ab:** AK 2, AK 10, AK 13, AK 15.

## Task 5 – Filterleiste in die drei Listenseiten einbinden

- In [calendar.html](../../../../web/src/app/pages/calendar/calendar.html),
  [ensemble-list.html](../../../../web/src/app/pages/ensemble-list/ensemble-list.html) und
  [venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html) die
  `city-filter`-Leiste **unterhalb der `<h1>`** in `.page-header` platzieren und die
  bisherige `<p class="muted">`-Beschreibung hinter den Info-Button verlagern.
- In den jeweiligen `*.ts`:
  - [calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts): Tageszellen/Agenda
    auf `eventsForCities(selection)` umstellen, wenn eine Auswahl existiert (statt
    `eventsOnDate` ungefiltert); Monats-Zähler entsprechend anpassen.
  - [ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts):
    `ensembles`-Computed auf `ensemblesForCities(selection)` umstellen.
  - [venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts):
    `venues`-Computed auf `venuesForCities(selection)` umstellen.
- Filter reaktiv an `FilterService.selectedIds` koppeln (computed); leere Auswahl =
  alle Inhalte.
- **Deckt ab:** AK 4, AK 5, AK 6, AK 7, AK 8, AK 9, AK 11, AK 12, AK 13.

## Task 6 – Styling der Bubbles und Info-Beschreibung

- Bubble-Stil (kompakt, kennzeichentauglich), Markierung des aktiven Zustands sowie
  Fokus-/Hover-/Active-Zustände nach bestehendem Designsystem umsetzen.
- Ein-/Ausblenden der Beschreibung visuell sauber (kein Layout-Sprung), Position
  konsistent auf allen drei Seiten.
- Responsives Verhalten der Bubble-Reihe (Umbruch bei vielen Städten).
- **Deckt ab:** AK 10, AK 12, AK 13.

## Task 7 – Burger-Navigation in allen Viewports vereinheitlichen

- In [app.css](../../../../web/src/app/app.css) die Navigation so anpassen, dass der
  `nav-toggle`-Button **in allen Breakpoints** sichtbar ist (auch Desktop, bisher nur
  `max-width: 720px`) und `nav.main-nav` per `menuOpen()` ein-/ausklappt.
- Umschalt-Button **quadratisch** gestalten.
- Bestehende Signal-Logik in [app.ts](../../../../web/src/app/app.ts) (`toggleMenu`,
  `closeMenu`, ESC, Fokus-Rückgabe) bleibt erhalten und regressionsfrei; Suche im Header
  unverändert nutzbar.
- **Deckt ab:** AK 14.

## Task 8 – Barrierefreiheit absichern

- Bubbles und Info-Button per Tastatur fokussier- und auslösbar (Enter/Space), sichtbarer
  Fokusindikator.
- Zustandskommunikation an assistive Technologien: Bubbles `aria-pressed`, Info-Button
  `aria-expanded` (+ `aria-controls` auf die Beschreibung).
- Burger-Button behält `aria-expanded`/`aria-controls`/`aria-label` wie im Bestand.
- **Deckt ab:** AK 14, AK 15.

## Task 9 – Produktspezifikation ergänzen (Contract + EARS)

- Neue Gherkin-Datei [filter.feature](../../contracts/filter.feature) mit Szenarien zu:
  Bubble-Quelle (Sitzort), Kennzeichen-Beschriftung, Standardzustand, Auswahl je Liste,
  additive Mehrfachauswahl, Abwählen, Persistenz über Seitenwechsel, Info-Toggle,
  Burger-Nav in allen Viewports.
- Neue EARS-Datei [filter.md](../../ears/filter.md) mit stabilen IDs für die
  Filteranforderungen.
- [contracts/README.md](../../contracts/README.md) und [ears/README.md](../../ears/README.md)
  um US-011 als spezifizierten Umfang ergänzen.
- **Deckt ab:** AK 1–15.

## Task 10 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Genau eine Bubble je Stadt mit ansässigem Ensemble; keine Bubble für reine
    Veranstaltungsorte (AK 1).
  - Bubbles zeigen Kfz-Kennzeichen, nicht den Ortsnamen (AK 2, AK 3).
  - Erstaufruf ohne Auswahl zeigt alle Inhalte (AK 4).
  - Auswahl filtert Kalender/Ensembles/Spielstätten korrekt nach Sitzort inkl.
    Gastspiel-Fall (Kölner Ensemble außerhalb Kölns unter „K") (AK 5–7).
  - Mehrfachauswahl (K + D) verknüpft additiv; Abwählen setzt zurück (AK 8, AK 9).
  - Ausgewählte Bubbles markiert (AK 10); Auswahl bleibt beim Seitenwechsel erhalten
    (AK 11); Position unter der Überschrift (AK 12).
  - Info-Button blendet Beschreibung ein/aus (AK 13).
  - Burger-Menü in Desktop- und Mobilbreite, Button quadratisch (AK 14).
  - Tastaturbedienung und Zustands-ARIA für Bubbles, Info- und Burger-Button (AK 15).

## Definition of Done

- Akzeptanzkriterien 1–15 aus [US-011](./US-011-filter.md) erfüllt.
- Filter wirkt konsistent über den Sitzort der Ensembles auf allen drei Listen; keine
  Änderungen an Detailseiten oder globaler Suche.
- Filterauswahl persistiert während der Navigation, nicht über Reload/Session hinaus.
- Kfz-Kennzeichen recherchiert und korrekt in [cities.json](../../../../data/cities.json).
- Burger-Navigation in allen Viewports funktional und regressionsfrei.
- Build erfolgreich; Filter- und Navigationsverhalten manuell mit Positiv-/Negativfällen
  geprüft.
