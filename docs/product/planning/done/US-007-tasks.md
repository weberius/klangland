# US-007 – Umsetzungs-Tasks

Umsetzung von [US-007](./US-007-ensemble-complete.md): Ensemble-Name in den Kalender-Kacheln immer vollständig anzeigen; Uhrzeit, Titel und Ensemble jeweils in eigener Zeile.

Betroffene Dateien:
- [web/src/app/pages/calendar/calendar.css](../../../../web/src/app/pages/calendar/calendar.css)
- [web/src/app/pages/calendar/calendar.html](../../../../web/src/app/pages/calendar/calendar.html) (voraussichtlich nur Prüfung)

---

## Task 1 – Kürzung des Ensemble-Namens entfernen (calendar.css)

- In `.chip-sub` ([calendar.css:117-123](../../../../web/src/app/pages/calendar/calendar.css#L117-L123)) die Kürzungs-Regeln entfernen: `white-space: nowrap;`, `overflow: hidden;`, `text-overflow: ellipsis;`.
- `display: block` und die gedämpfte Farbe (`color: var(--color-text-muted)`) beibehalten.
- Sicherstellen, dass lange Namen umbrechen (Standard `white-space: normal`); bei Bedarf `overflow-wrap: anywhere` ergänzen, damit auch sehr lange Wörter/Namen nicht seitlich überlaufen.
- **Deckt ab:** AK 3 (Ensemble vollständig, kein `…`).

## Task 2 – Zeilenumbruch nach der Uhrzeit sicherstellen (calendar.css)

- `.chip-time` ([calendar.css:108-112](../../../../web/src/app/pages/calendar/calendar.css#L108-L112)) von inline auf `display: block` umstellen und `margin-right` entfernen (durch den Block-Umbruch nicht mehr nötig).
- Hervorhebung (`font-weight`, `color`) unverändert lassen.
- `.chip-title` ist bereits `display: block` ([calendar.css:113-116](../../../../web/src/app/pages/calendar/calendar.css#L113-L116)) → Titel steht damit in eigener Zeile.
- **Deckt ab:** AK 1 (Uhrzeit eigene Zeile) und AK 2 (Titel eigene Zeile).

## Task 3 – Zellenhöhe als Mindesthöhe bestätigen (calendar.css)

- Prüfen, dass `.day-cell` weiterhin nach unten wächst: `height: 7.5rem` ([calendar.css:53-59](../../../../web/src/app/pages/calendar/calendar.css#L53-L59)) wirkt in der Tabelle als Mindesthöhe. Zur besseren Lesbarkeit optional zu `min-height: 7.5rem` ändern (funktional gleichwertig).
- Sicherstellen, dass keine Regel den Inhalt der Kachel abschneidet (kein `overflow: hidden` / keine feste `height` auf `.event-chip` oder `.day-events`).
- **Deckt ab:** AK 4 (Kachel wächst, nichts wird abgeschnitten) und AK 6 (Spaltenbreite unverändert, nur Höhe passt sich an – `table-layout: fixed` bleibt).

## Task 4 – Template prüfen (calendar.html)

- Markup der Kachel ([calendar.html:46-54](../../../../web/src/app/pages/calendar/calendar.html#L46-L54)) sichten: Reihenfolge `chip-time` → `chip-title` → `chip-sub` ist korrekt; voraussichtlich **keine Änderung** nötig.
- Bestätigen, dass `@if (time(e))` ([calendar.html:49](../../../../web/src/app/pages/calendar/calendar.html#L49)) erhalten bleibt, damit Events ohne Uhrzeit keine leere Zeile erzeugen.
- **Deckt ab:** AK 5 (ohne Uhrzeit kein führender Umbruch).

## Task 5 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` (bzw. `ng serve`) und im Browser prüfen:
  - Termin mit langem Ensemble-Namen (z. B. „Neue Philharmonie Westfalen", „Niederrheinische Sinfoniker"): Name vollständig, ggf. mehrzeilig, kein `…` (AK 3).
  - Uhrzeit, Titel, Ensemble stehen jeweils in eigener Zeile (AK 1, AK 2).
  - Kachel/Zelle wächst nach unten, nichts abgeschnitten (AK 4).
  - Event ohne Uhrzeit: keine leere erste Zeile (AK 5).
  - Spaltenbreiten des Rasters unverändert (AK 6).
  - Schmales Fenster: mobile Agenda unverändert (AK 7).
- Zusammen mit [US-008](./US-008-calendar-table.md) prüfen, falls beide umgesetzt sind: aufgeklappte Zellen + höhere Kacheln sehen gemeinsam sauber aus.

## Definition of Done

- Akzeptanzkriterien 1–7 der User Story erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen an der mobilen Agenda oder der Event-Detailseite.
- Story-Datei nach Abschluss von `inprogress/` nach `done/` verschieben (sofern dieses Verzeichnis genutzt wird).
