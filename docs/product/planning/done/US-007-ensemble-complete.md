# User Story 007 - Orchesternamen komplett anzeigen

## User Story

**Als** Besucher:in, der:die den Konzertkalender als Monatsübersicht nutzt,
**möchte ich** in jeder Konzert-Kachel den vollständigen Ensemble-Namen sehen,
**damit** ich erkennen kann, welches Orchester spielt, ohne die Detailseite öffnen zu müssen.

## Kontext / Problem

In der Kalenderansicht werden die Konzerttermine als Kacheln (Event-Chips) angezeigt ([calendar.html:46-54](../../../../web/src/app/pages/calendar/calendar.html#L46-L54)): zuerst die Uhrzeit, dann der Titel der Veranstaltung, zuletzt der Name des Ensembles.

Der Ensemble-Name wird aktuell einzeilig abgeschnitten und mit `…` dargestellt. Ursache ist die Regel `.chip-sub` mit `white-space: nowrap; overflow: hidden; text-overflow: ellipsis` ([calendar.css:117-123](../../../../web/src/app/pages/calendar/calendar.css#L117-L123)). Dadurch sind längere Orchesternamen (z. B. „Niederrheinische Sinfoniker" oder „Neue Philharmonie Westfalen") nicht vollständig lesbar.

Die Kachel darf sich nach unten vergrößern: `.day-cell` besitzt `height: 7.5rem`, was in einer Tabelle als **Mindesthöhe** wirkt – die Zelle wächst also bereits mit dem Inhalt ([calendar.css:53-59](../../../../web/src/app/pages/calendar/calendar.css#L53-L59)).

Betroffen ist die **Desktop-Tabelle**. Die mobile Agenda nutzt eine eigene Darstellung und ist nicht Teil dieser Story.

## Gewählte Lösung

Die Kachel-Darstellung wird auf konsequentes Umbrechen umgestellt:

- Uhrzeit, Titel und Ensemble-Name stehen jeweils in einer eigenen Zeile (`display: block`).
- Beim Ensemble-Namen wird die Kürzung entfernt (`white-space`, `overflow`, `text-overflow`), sodass er bei Bedarf über mehrere Zeilen vollständig umbricht.
- Die Kachel bzw. Tabellenzelle wächst dabei nach unten mit dem Inhalt (Mindesthöhe bleibt erhalten).

## Akzeptanzkriterien

1. **Uhrzeit in eigener Zeile:** Ist eine Uhrzeit vorhanden, steht sie in einer eigenen Zeile; der Titel beginnt in der nächsten Zeile.
2. **Titel in eigener Zeile:** Nach dem Titel folgt ein Zeilenumbruch; der Ensemble-Name beginnt in einer neuen Zeile.
3. **Ensemble vollständig:** Der Ensemble-Name wird immer vollständig angezeigt und bricht bei Bedarf über mehrere Zeilen um. Es erscheint kein `…` und keine Kürzung.
4. **Kachel wächst:** Die Kachel/Zelle vergrößert sich nach unten entsprechend dem Inhalt; nichts wird abgeschnitten.
5. **Ohne Uhrzeit:** Bei Events ohne Uhrzeit entsteht keine leere Zeile (kein führender Umbruch); die Kachel beginnt mit dem Titel.
6. **Rasterbreite unverändert:** Die sieben Spalten des Monatsrasters bleiben gleich breit; nur die Zeilenhöhe passt sich an.
7. **Mobile Agenda unverändert:** Darstellung und Verhalten der Agenda-Ansicht bleiben unangetastet.

## Zu berücksichtigen (offene Punkte)

- **Mehrere Ensembles pro Event:** Die Kachel zeigt derzeit nur das erste Ensemble (`ensembleNames(...)[0]`, [calendar.ts:124-126](../../../../web/src/app/pages/calendar/calendar.ts#L124-L126)). Diese Story stellt sicher, dass **dieser eine** Name vollständig erscheint; das Anzeigen mehrerer Ensembles ist bewusst nicht Teil der Story (siehe Out of Scope).
- **Wechselwirkung mit US-008:** Höhere Kacheln vergrößern die Zeilenhöhe zusätzlich zum Aufklappen weiterer Termine ([US-008](./US-008-calendar-table.md)). Beide Änderungen müssen zusammen sauber aussehen – bei der Umsetzung/Abnahme gemeinsam prüfen.
- **Lange Titel:** Der Titel bricht (wie bisher) mehrzeilig um; es darf keine neue Kürzung/Clamp am Titel eingeführt werden.
- **Konsistenz Farben/Größen:** Schriftgrößen und Farben der Zeilen (Zeit hervorgehoben, Ensemble gedämpft) bleiben unverändert.

## Out of Scope

- Anzeige mehrerer Ensembles pro Event (weiterhin nur das erste).
- Änderungen an der mobilen Agenda.
- Änderungen an der Event-Detailseite.
