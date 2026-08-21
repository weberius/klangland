# User Story 015 - Ticket-Link nur bei Sinnhaftigkeit und mit Verlassen-Hinweis

## User Story

**Als** Besucher:in einer Event-Detailseite,
**möchte ich** einen Ticket-Link nur dann sehen, wenn ein Ticketkauf zeitlich noch sinnvoll ist, und beim Klick darauf klar darüber informiert werden, dass ich die Seite verlasse,
**damit** ich nicht auf nutzlose Ticket-Links für vergangene oder abgesagte Veranstaltungen stoße und beim Wechsel auf eine externe Seite nicht unerwartet den Kontext verliere.

## Kontext / Problem

Die Event-Detailseite zeigt aktuell einen "Tickets"-Button, sobald für das Event ein `ticketUrl` gepflegt ist ([event-detail.html:19-22](../../../../web/src/app/pages/event-detail/event-detail.html#L19-L22)). Der Button wird dabei **unabhängig vom Datum** dargestellt: Auch bei Veranstaltungen, die bereits stattgefunden haben, erscheint der Link, obwohl ein Ticketkauf dann keinen Sinn mehr ergibt. Ebenso wird der Link bei abgesagten Events (`status = 'cancelled'`) weiterhin angezeigt.

Der Link öffnet bereits in einem neuen Tab (`target="_blank"`, `rel="noopener"`). Es fehlt jedoch ein Hinweis darauf, dass Nutzer:innen damit die Klangland-Seite verlassen, ein neuer Tab/ein neues Fenster geöffnet wird und es innerhalb dieses externen Ziels keine Zurück-Navigation zur Anwendung gibt.

Das Event-Modell kennt `ticketUrl`, `date` und `status` ([models.ts:182-201](../../../../web/src/app/models/models.ts#L182-L201)); die möglichen Status-Werte sind `scheduled | cancelled | postponed | rescheduled` ([models.ts:172](../../../../web/src/app/models/models.ts#L172)).

Betroffen ist ausschließlich die **Event-Detailseite**. Andere Seiten (Kalender, Ensemble-, Venue-, Personen-Detailseiten) und andere Aktionen (Kalender-Eintrag, Favorit) bleiben unverändert.

## Gewählte Lösung

**Sichtbarkeit (Datum + Status):** Der Ticket-Link wird nur angezeigt, wenn ein `ticketUrl` gepflegt ist **und** ein Kauf noch sinnvoll ist. Das ist der Fall, wenn das Event-Datum nicht in der Vergangenheit liegt (der Veranstaltungstag selbst zählt noch als sinnvoll) und das Event nicht abgesagt ist (`status ≠ 'cancelled'`). Verlegte/neu terminierte Events (`postponed`, `rescheduled`) behalten den Link, sofern ihr Datum nicht in der Vergangenheit liegt, da die Veranstaltung grundsätzlich weiterhin geplant ist.

**Verlassen-Hinweis (Bestätigungsdialog):** Beim Klick auf den Ticket-Button erscheint zunächst ein Bestätigungsdialog, der darauf hinweist, dass Klangland verlassen und die externe Ticketseite in einem neuen Tab/Fenster geöffnet wird und dass es von dort keine Zurück-Navigation in die Anwendung gibt. Erst nach Bestätigung wird der externe Link im neuen Tab geöffnet; bei Abbruch geschieht nichts und Nutzer:innen bleiben auf der Detailseite.

Bewusst akzeptierter Kompromiss: Die Sinnhaftigkeit wird allein aus dem gepflegten Event-Datum abgeleitet (Tagesgenauigkeit, keine Berücksichtigung von Uhrzeit oder tatsächlichen Verkaufsfristen der externen Ticketanbieter).

## Akzeptanzkriterien

1. **Anzeige bei sinnvollem Kauf:** Für ein Event mit gepflegtem `ticketUrl`, dessen Datum heute oder in der Zukunft liegt und das nicht abgesagt ist, wird der "Tickets"-Button auf der Event-Detailseite angezeigt.
2. **Ausblenden bei Vergangenheit:** Liegt das Event-Datum vor dem heutigen Tag, wird der Ticket-Button nicht angezeigt, auch wenn ein `ticketUrl` gepflegt ist.
3. **Veranstaltungstag zählt:** Findet das Event am heutigen Tag statt, wird der Ticket-Button weiterhin angezeigt.
4. **Ausblenden bei Absage:** Ist das Event abgesagt (`status = 'cancelled'`), wird der Ticket-Button nicht angezeigt, unabhängig vom Datum.
5. **Kein Ticket-Link gepflegt:** Ist kein `ticketUrl` vorhanden (`null`), wird kein Ticket-Button angezeigt (unverändertes Verhalten).
6. **Verlassen-Hinweis beim Klick:** Beim Klick auf den Ticket-Button erscheint ein Bestätigungsdialog mit dem Hinweis, dass die Klangland-Seite verlassen wird, ein neuer Tab/ein neues Fenster geöffnet wird und es dort keine Zurück-Navigation in die Anwendung gibt.
7. **Bestätigung öffnet Ziel:** Nach Bestätigung des Dialogs wird die externe Ticketseite in einem neuen Tab geöffnet (`target="_blank"`, `rel="noopener"`).
8. **Abbruch bleibt auf Seite:** Bei Abbruch des Dialogs wird kein externer Link geöffnet und die Nutzer:in verbleibt unverändert auf der Event-Detailseite.
9. **Unveränderte Bereiche:** Die übrigen Aktionen und Inhalte der Detailseite (Kalender-Eintrag, Favorit, Quelle, Programm etc.) bleiben in Darstellung und Verhalten unverändert.
10. **Barrierefreiheit:** Der Ticket-Button bzw. -Link ist per Tastatur erreichbar und aussagekräftig benannt; der Bestätigungsdialog ist per Tastatur bedienbar (Bestätigen/Abbrechen) und für Screenreader zugänglich.

## Out of Scope

- Berücksichtigung von Uhrzeit oder tatsächlichen Verkaufsschlusszeiten der externen Ticketanbieter (nur tagesgenaue Datumsprüfung).
- Prüfung, ob ein Event tatsächlich ausverkauft ist (es existiert kein entsprechender Status).
- Änderungen am Ticket-Handling auf anderen Seiten (z. B. Kalenderliste, Übersichten).
- Live-Validierung, ob der externe `ticketUrl` erreichbar bzw. noch gültig ist.
- Einführung eines dauerhaften "externer Link"-Hinweises für andere externe Links (Quelle, Website der Spielstätte).

<!--
Umsetzungs-Tasks:
In separater Datei US-015-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
