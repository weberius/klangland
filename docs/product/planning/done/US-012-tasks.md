# US-012 – Umsetzungs-Tasks

Umsetzung von [US-012](./US-012-kalender-eintrag.md): Auf der Event-Detailseite eine Aktion
„In den Kalender eintragen", die clientseitig eine standardkonforme iCalendar-Datei (`.ics`,
RFC 5545) für genau dieses Event erzeugt und zum Öffnen/Download anbietet.

## Architektur-Entscheidung (verbindlich)

- Reine **`.ics`-Lösung ohne Backend**: Erzeugung clientseitig als Blob, Download/Öffnen über
  einen temporären Anchor. Keine Plattform-/Browsererkennung, keine anbieterspezifischen Links.
- Die iCalendar-Erzeugung liegt als **reine, testbare Funktion** in einem neuen Modul
  `web/src/app/core/ics.ts` (Eingabe: aufgelöste Event-Daten + absolute Event-URL; Ausgabe:
  `.ics`-Text). Die Detailseite ruft sie nur auf und stößt den Download an.
- Zeitzone **Europe/Berlin** wird über `DTSTART;TZID=Europe/Berlin` **mit eingebettetem
  `VTIMEZONE`-Block** ausgegeben, damit Sommer-/Winterzeit in allen Zielkalendern korrekt
  interpretiert wird.
- Text- und Formatregeln nach RFC 5545: Escaping von `\ , ; \n` in Textwerten und Zeilenfaltung
  (Line-Folding) bei 75 Oktett.
- Wiederverwendung bestehender Lookups aus [DataService](../../../../web/src/app/core/data.service.ts)
  (Venue, City, Ensembles, Personen) und Datumshilfen aus
  [date-util](../../../../web/src/app/core/date-util.ts).

Betroffene Dateien:
- [web/src/app/core/ics.ts](../../../../web/src/app/core/) (neu)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) / [.html](../../../../web/src/app/pages/event-detail/event-detail.html) / [.css](../../../../web/src/app/pages/event-detail/event-detail.css)
- [web/src/app/core/app-config.ts](../../../../web/src/app/core/app-config.ts) (Basis-URL für den `URL`-Rückverweis, falls nötig)
- [docs/product/contracts/kalender-eintrag.feature](../../contracts/) / [ears/kalender-eintrag.md](../../ears/) (neu)
- [docs/product/contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md)

---

## Task 1 – iCalendar-Builder (`ics.ts`)

- Reine Funktion `buildEventIcs(params)` erstellen, die aus Event + aufgelösten Feldern
  (Spielstätte, Stadt, Ensemble-/Dirigent:innen-Namen, absolute Event-URL) einen gültigen
  `VCALENDAR`/`VEVENT`-Text erzeugt.
- Kopf: `BEGIN:VCALENDAR`, `VERSION:2.0`, `PRODID`, `CALSCALE:GREGORIAN`, eingebetteter
  `VTIMEZONE` für Europe/Berlin.
- `VEVENT`-Felder:
  - `UID`: stabil und eindeutig je Event (z. B. `<event.id>@klangland`).
  - `DTSTAMP`: Erzeugungszeitpunkt (UTC).
  - `SUMMARY`: Event-Titel (bei `status = cancelled` mit Kennzeichnung, s. Task 3).
  - `DTSTART`/`DTEND`: Zeit-Logik s. Task 2.
  - `LOCATION`: Spielstätte + Adresse + Stadt (kommagerecht escaped).
  - `DESCRIPTION`: Ensemble(s), Dirigent:in, optional Kurzprogramm, plus Link zur Event-Seite.
  - `URL`: absolute Event-Detail-URL.
  - `STATUS`: `CANCELLED` bei abgesagten Events (sonst `CONFIRMED`).
- Text-Escaping und Zeilenfaltung (75 Oktett) als Helfer implementieren.
- **Deckt ab:** AK 3, AK 7, AK 8, AK 9.

## Task 2 – Zeit- und Dauer-Logik

- Bei vorhandener `startTime`: `DTSTART;TZID=Europe/Berlin:YYYYMMDDTHHMMSS`.
  - `endTime` vorhanden → `DTEND` analog.
  - `endTime` fehlt → sinnvolle Standarddauer setzen (z. B. 2 Stunden) und dokumentieren.
- Bei fehlender `startTime` (`null`): ganztägiger Eintrag
  `DTSTART;VALUE=DATE:YYYYMMDD` und `DTEND;VALUE=DATE:<Folgetag>`.
- Datums-/Zeitformatierung ohne Zeitzonen-Verschiebungsfehler umsetzen (Werte stammen aus den
  lokalen Feldern `date`/`startTime`/`endTime`, [models.ts:169](../../../../web/src/app/models/models.ts#L169)).
- **Deckt ab:** AK 4, AK 5.

## Task 3 – Aktion in der Event-Detailseite

- In [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) eine Methode
  ergänzen, die die aufgelösten Felder sammelt (`venue()`, `cityName()`, `ensembles()`,
  `conductors()`), `buildEventIcs(...)` aufruft und die Datei als Download anbietet
  (Blob `text/calendar`, Dateiname z. B. `<event.id>.ics`, temporärer Anchor + `revokeObjectURL`).
- Absolute Event-URL bestimmen (aus `window.location`/Router bzw.
  [app-config](../../../../web/src/app/core/app-config.ts)).
- In [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html) im
  `event-head` (nahe Tickets/Status) einen Button „In den Kalender eintragen" ergänzen.
- Bei abgesagten Events die Kennzeichnung im `SUMMARY`/`STATUS` sicherstellen (Zusammenspiel mit
  Task 1).
- Button-Styling in [event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css)
  nach bestehendem Muster (`btn`).
- **Deckt ab:** AK 1, AK 2, AK 6, AK 10.

## Task 4 – Barrierefreiheit und unveränderte Bereiche

- Aktion als echtes `<button>` (Tastaturbedienung, sichtbarer Fokus) mit klarem Label.
- Sicherstellen, dass Übersichts-/Listenseiten und die übrige Detailseite unverändert bleiben.
- **Deckt ab:** AK 10, AK 11.

## Task 5 – Produktspezifikation ergänzen (Contract + EARS)

- Neue Gherkin-Datei `kalender-eintrag.feature` mit Szenarien zu: Aktion vorhanden,
  clientseitige `.ics`-Erzeugung, Pflichtfelder, Uhrzeit/ganztägig-Fallback, abgesagtes Event,
  Rückverweis-URL.
- Neue EARS-Datei `kalender-eintrag.md` mit stabilen IDs.
- [contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md) um
  US-012 ergänzen.
- **Deckt ab:** AK 1–11.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Aktion „In den Kalender eintragen" auf der Event-Detailseite sichtbar und per Tastatur
    bedienbar (AK 1, AK 10).
  - Klick lädt eine `.ics`-Datei ohne Netzwerk-/Backend-Aufruf (AK 2).
  - Import der Datei in Apple Kalender/Google Kalender/Outlook: Titel, Start/Ende, Ort und
    Beschreibung inkl. Link korrekt; Zeit in Europe/Berlin richtig (AK 3, AK 4, AK 8, AK 9).
  - Event ohne `startTime` erzeugt einen ganztägigen Eintrag (AK 5).
  - Abgesagtes Event ist im Kalendereintrag als abgesagt erkennbar (AK 6).
  - Erneuter Import aktualisiert den bestehenden Termin (gleiche `UID`) statt zu duplizieren
    (AK 7).
  - Übersichts-/Listenseiten unverändert (AK 11).

## Definition of Done

- Akzeptanzkriterien 1–11 aus [US-012](./US-012-kalender-eintrag.md) erfüllt.
- `.ics`-Erzeugung ist clientseitig, ohne Backend, und als reine Funktion in `ics.ts` gekapselt.
- Erzeugte Dateien sind gültiges iCalendar (RFC 5545) und importieren korrekt auf iOS/macOS,
  Android, Windows/Outlook und Google Kalender.
- Übersichts-/Listenseiten und übrige Detailinhalte bleiben regressionsfrei.
- Build erfolgreich; Import manuell mit Positiv-/Sonderfällen (ohne Uhrzeit, abgesagt) geprüft.
