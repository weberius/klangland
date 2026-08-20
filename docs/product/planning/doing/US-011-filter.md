# User Story 011 - Ort-Filter für Kalender, Ensembles und Spielstätten

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** die Anzeige über Ort-Bubbles unterhalb der Seitenüberschrift auf eine oder mehrere Städte einschränken können,
**damit** ich Konzerte, Ensembles und Spielstätten gezielt nach den Ensemble-Standorten filtern kann, die mich interessieren.

## Kontext / Problem

Aktuell werden im Konzertkalender ([calendar.html:1-3](../../../../web/src/app/pages/calendar/calendar.html#L1-L3)), in der Ensemble-Liste ([ensemble-list.html:1-4](../../../../web/src/app/pages/ensemble-list/ensemble-list.html#L1-L4)) und in der Spielstätten-Liste ([venue-list.html:1-4](../../../../web/src/app/pages/venue-list/venue-list.html#L1-L4)) immer alle erfassten Inhalte angezeigt. Es gibt keine Möglichkeit, die Anzeige auf einen bestimmten Ort einzugrenzen. Bei wachsendem Datenbestand wird es dadurch schwerer, die Angebote einer bestimmten Stadt zu überblicken.

Im Datenmodell hat jedes Ensemble einen **Sitzort** ([ensembles.json](../../../../data/ensembles.json) → `cityIds`). Events verweisen über `ensembleIds` auf die auftretenden Ensembles ([events.json](../../../../data/events.json)) und Spielstätten sind über `venueId`/`cityId` mit Events verknüpft. Diese Sitzort-Zuordnung soll die einheitliche Grundlage des Filters bilden.

Zusätzlich wird die Kopfleiste überarbeitet: Die Navigation ([app.html:53-73](../../../../web/src/app/app.html#L53-L73)) wird aktuell nur in schmalen Viewports als Burger-Menü (`nav-toggle`) und im Desktop inline dargestellt.

**Betroffen** sind der Konzertkalender, die Ensemble-Liste, die Spielstätten-Liste sowie die globale Kopfleiste/Navigation. **Nicht betroffen** sind die Detailseiten (Event-, Ensemble-, Spielstätten-Detail) und die globale Suche ([app.html:9-52](../../../../web/src/app/app.html#L9-L52)).

## Gewählte Lösung

**Ort-Filter als Bubbles, gesteuert über den Ensemble-Sitzort.** Unterhalb der Seitenüberschrift wird eine Reihe von Bubbles angezeigt – eine je Stadt, in der mindestens ein Ensemble seinen Sitz hat. Städte, die nur als Veranstaltungsort auftreten, aber kein ansässiges Ensemble haben, erzeugen **keine** Bubble.

Der Filter wirkt auf allen drei Listen konsistent über den Sitzort der Ensembles:

- **Kalender:** Es werden Events angezeigt, bei denen mindestens ein auftretendes Ensemble seinen Sitz in einer ausgewählten Stadt hat (ein Gastspiel eines Kölner Ensembles außerhalb Kölns erscheint also unter „Köln").
- **Ensembles:** Es werden Ensembles mit Sitz in einer ausgewählten Stadt angezeigt.
- **Spielstätten:** Es werden Spielstätten angezeigt, in denen Ensembles der ausgewählten Stadt auftreten (unabhängig vom Standort der Spielstätte).

Die Auswahl ist **additiv** (Mehrfachauswahl per ODER) und **persistiert** über Seitenwechsel hinweg, bis sie manuell aufgehoben wird; einen expliziten „Reset"-Button gibt es nicht. Zum Platzsparen tragen die Bubbles nicht den vollen Ortsnamen, sondern das **Kfz-Kennzeichen** der Stadt (Köln → „K", Düsseldorf → „D", Dortmund → „DO"). Diese Zuordnung wird als Datum an den Städten gepflegt ([cities.json](../../../../data/cities.json)).

Die bisher unter der Überschrift stehende Beschreibung wird hinter einem Info-Button („i") verborgen, um Platz für die Filter-Bubbles zu schaffen. Die Navigation wird in **allen** Viewports (mobil wie Desktop) einheitlich als quadratisches Burger-Menü dargestellt.

## Akzeptanzkriterien

1. **Bubble-Quelle:** Es wird genau eine Bubble je Stadt angezeigt, in der mindestens ein Ensemble seinen Sitz hat; Städte ohne ansässiges Ensemble erzeugen keine Bubble.
2. **Bubble-Beschriftung:** Jede Bubble zeigt das Kfz-Kennzeichen der Stadt (z. B. Köln → „K", Düsseldorf → „D", Dortmund → „DO"), nicht den ausgeschriebenen Ortsnamen.
3. **Kennzeichen-Daten:** Zu jeder betroffenen Stadt ist das Kfz-Kennzeichen als Datum hinterlegt ([cities.json](../../../../data/cities.json)); die Zuordnung ist recherchiert und korrekt.
4. **Standardzustand:** Beim ersten Seitenaufruf ist keine Bubble ausgewählt und es werden alle Inhalte (Events/Ensembles/Spielstätten) angezeigt.
5. **Auswahl (Kalender):** Ist mindestens eine Bubble ausgewählt, zeigt der Kalender nur Events, bei denen mindestens ein auftretendes Ensemble seinen Sitz in einer der ausgewählten Städte hat.
6. **Auswahl (Ensembles):** Ist mindestens eine Bubble ausgewählt, zeigt die Ensemble-Liste nur Ensembles mit Sitz in einer der ausgewählten Städte.
7. **Auswahl (Spielstätten):** Ist mindestens eine Bubble ausgewählt, zeigt die Spielstätten-Liste nur Spielstätten, in denen Ensembles einer der ausgewählten Städte auftreten.
8. **Additive Mehrfachauswahl:** Das Auswählen weiterer Bubbles erweitert die Anzeige (ODER-Verknüpfung); Köln + Düsseldorf zeigt Inhalte beider Städte.
9. **Abwählen:** Eine ausgewählte Bubble kann durch erneutes Anklicken wieder abgewählt werden; sind danach keine Bubbles mehr ausgewählt, werden wieder alle Inhalte angezeigt.
10. **Markierung:** Ausgewählte Bubbles sind sichtbar markiert dargestellt, nicht ausgewählte sind nicht markiert.
11. **Persistenz:** Die getroffene Auswahl bleibt beim Wechsel zwischen Kalender-, Ensemble- und Spielstätten-Seite erhalten und wirkt dort jeweils gemäß Kriterium 5–7. Es gibt keinen „Reset"-Button; der Filter wird ausschließlich durch Abwählen verändert.
12. **Position:** Die Filter-Bubbles stehen unterhalb der jeweiligen Seitenüberschrift (Konzertkalender, Ensembles, Spielstätten).
13. **Info-Button:** Die zuvor unter der Überschrift stehende Beschreibung ist hinter einem Info-Button („i") verborgen und lässt sich darüber ein-/ausblenden.
14. **Burger-Navigation:** Die Hauptnavigation wird in allen Viewports (mobil und Desktop) als Burger-Menü angezeigt; der Umschalt-Button ist stets quadratisch dargestellt.
15. **Barrierefreiheit:** Bubbles und Info-Button sind echte, per Tastatur bedienbare Bedienelemente (Fokus, Enter/Space) und kommunizieren ihren Zustand (ausgewählt/nicht ausgewählt bzw. auf-/zugeklappt) an assistive Technologien.

## Out of Scope

- Filtern nach dem **Veranstaltungsort** eines Events (`event.cityId`) statt nach dem Sitzort des auftretenden Ensembles – bewusst nicht gewählt.
- Filtern nach anderen Kriterien als dem Ort (z. B. Ensemble-Typ, Genre, Zeitraum).
- Persistieren der Filterauswahl über Seiten-Reloads oder Browser-Sitzungen hinaus (nur In-App-Persistenz während der Navigation).
- Bubbles für Städte, die ausschließlich als Veranstaltungsort, aber ohne ansässiges Ensemble vorkommen.
- Änderungen an den Detailseiten und an der globalen Suche.
