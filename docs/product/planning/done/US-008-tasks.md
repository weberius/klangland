# US-008 – Umsetzungs-Tasks

Umsetzung von [US-008](./US-008-calendar-table.md): Inline-Aufklappen der weiteren Konzerttermine in der Desktop-Tabelle.

Betroffene Dateien:
- [web/src/app/pages/calendar/calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts)
- [web/src/app/pages/calendar/calendar.html](../../../../web/src/app/pages/calendar/calendar.html)
- [web/src/app/pages/calendar/calendar.css](../../../../web/src/app/pages/calendar/calendar.css)

---

## Task 1 – Aufklapp-Zustand als Signal (calendar.ts)

- Ein `signal<Set<string>>` (z. B. `expandedDays`) einführen, das die ISO-Daten der aufgeklappten Tage hält.
- Methoden ergänzen:
  - `toggleDay(iso: string)` – ISO im Set an-/abwählen (neues `Set` setzen, damit die Signal-Änderung erkannt wird).
  - `isExpanded(iso: string): boolean` – Prüfung für das Template.
- **AK 6 (Monatswechsel):** Beim Wechsel von `current()` (Monat) das Set zurücksetzen. Da der Monat aus der Route (`params`) abgeleitet ist, den Reset an die Monatsänderung koppeln (z. B. via `effect`, der auf `current()` reagiert und `expandedDays.set(new Set())` aufruft).
- Sichtbare Terminanzahl im eingeklappten Zustand als Konstante (`VISIBLE = 2`) definieren, statt der Magic Number `2`.

## Task 2 – Template-Logik (calendar.html)

- In der Tageszelle ([calendar.html:45-58](../../../../web/src/app/pages/calendar/calendar.html#L45-L58)) die Terminliste abhängig vom Zustand rendern:
  - eingeklappt: `cell.events.slice(0, VISIBLE)`
  - aufgeklappt: `cell.events` (vollständig)
- Den bisherigen statischen `<li class="more">` durch einen **`<button>`** ersetzen:
  - eingeklappt und `cell.events.length > VISIBLE` → `+ {{ cell.events.length - VISIBLE }} weitere`, `(click)="toggleDay(cell.iso)"`.
  - aufgeklappt → `weniger anzeigen`, `(click)="toggleDay(cell.iso)"`.
- Barrierefreiheit (AK 7): am Button `type="button"`, `[attr.aria-expanded]="isExpanded(cell.iso)"` und ein sprechendes `[attr.aria-label]` (z. B. „3 weitere Termine am 15. anzeigen").
- Sicherstellen, dass Tage mit ≤ 2 Terminen keinen Button rendern (AK 5).

## Task 3 – Styling (calendar.css)

- `.more` von `<li>`-Text auf Button umstellen: Button-Reset (kein Rahmen/Hintergrund, `cursor: pointer`, linksbündig, Schriftgröße/Farbe wie bisher aus [calendar.css:124-127](../../../../web/src/app/pages/calendar/calendar.css#L124-L127)).
- Hover-/Focus-visible-Zustand ergänzen (Unterstreichung oder Farbe), damit die Klickbarkeit erkennbar und der Tastaturfokus sichtbar ist.
- Prüfen, dass die Zelle bei vielen Terminen sauber in die Höhe wächst (`.day-cell` / `.day-events`) und das umliegende Raster nicht zerreißt; ggf. `vertical-align: top` der Zellen bestätigen.

## Task 4 – Manuelle Verifikation

- `cd web && npm run build` – Kompiliert fehlerfrei.
- `cd web && npm start` (bzw. `ng serve`) und im Browser prüfen:
  - Tag mit > 2 Terminen: `+ N weitere` klicken → alle Termine sichtbar, Text wird zu `weniger anzeigen`; erneut klicken → wieder 2 Termine.
  - Zwei verschiedene Tage unabhängig auf-/zuklappen (AK 4).
  - Monat wechseln → alle Zellen wieder eingeklappt (AK 6).
  - Tastaturbedienung: Button per Tab erreichbar, mit Enter/Space bedienbar, Fokus sichtbar (AK 7).
  - Mobile Ansicht (schmales Fenster): Agenda unverändert (AK 8).
- Als Testmonat eignet sich ein Monat mit ≥ 3 Konzerten an einem Tag (z. B. über den Datenbestand einen solchen Tag ermitteln).

## Definition of Done

- Alle Akzeptanzkriterien 1–8 aus der User Story erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen an der mobilen Agenda oder an anderen Seiten.
- Story-Datei nach Abschluss von `inprogress/` nach `done/` verschieben (sofern dieses Verzeichnis genutzt wird).
