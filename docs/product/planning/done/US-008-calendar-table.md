# User Story 008 - Darstellung, wenn mehr als zwei Konzerte an einem Tag

## User Story

**Als** Besucher:in, der:die den Konzertkalender am Desktop-Monitor als Monatsübersicht nutzt,
**möchte ich** an einem Tag mit mehr als zwei Konzerten die zunächst verborgenen Termine mit einem Klick einblenden (und wieder ausblenden) können,
**damit** ich alle Termine eines Tages im Überblick behalte, ohne die Monatsansicht zu verlassen.

## Kontext / Problem

Der Konzertkalender wird in der Desktop-Ansicht als Tabelle angezeigt. Es können pro Tabellenfeld 2 Konzerttermine angezeigt werden. Gibt es weitere Konzerttermine, wird unterhalb der angezeigten Konzerttermine z.B. '+ 1 weitere' oder '+ 4 weitere' angezeigt ([calendar.html:55-57](../../../../web/src/app/pages/calendar/calendar.html#L55-L57)). Dieser Hinweis ist aktuell **nicht interaktiv** – es ist nicht möglich, diese weiteren Konzerttermine zu erkennen.

Betroffen ist ausschließlich die **Desktop-Tabelle**. Die mobile Agenda ([calendar.html:78-90](../../../../web/src/app/pages/calendar/calendar.html#L78-L90)) zeigt bereits alle Termine eines Tages und bleibt unverändert.

## Gewählte Lösung

**Inline-Aufklappen (Toggle).** Der Hinweis `+ N weitere` wird zu einem klickbaren Element. Bei Klick klappt die betreffende Tageszelle in-place auf und zeigt **alle** Termine dieses Tages; darunter erscheint `weniger anzeigen`, mit dem die Zelle wieder eingeklappt wird. Die Tabellenzeile wird dadurch höher – das ist der bewusst akzeptierte Kompromiss zugunsten der vollständigen Übersicht.

## Akzeptanzkriterien

1. **Standardzustand:** Ein Tag mit mehr als 2 Terminen zeigt die ersten 2 Termine und darunter `+ N weitere` (N = Anzahl der verborgenen Termine).
2. **Aufklappen:** Ein Klick auf `+ N weitere` blendet **alle** Termine dieses Tages ein.
3. **Einklappen:** Im aufgeklappten Zustand wird statt `+ N weitere` der Text `weniger anzeigen` angezeigt; ein Klick darauf stellt den Standardzustand (2 Termine + `+ N weitere`) wieder her.
4. **Unabhängigkeit je Tag:** Jede Tageszelle wird separat auf- und zugeklappt. Mehrere Zellen können gleichzeitig aufgeklappt sein; das Auf-/Zuklappen einer Zelle beeinflusst keine andere.
5. **Tage mit ≤ 2 Terminen** bleiben unverändert (kein Toggle, kein Hinweis).
6. **Monatswechsel:** Beim Wechsel des Monats (Vor/Zurück/Heute) startet die Ansicht wieder im eingeklappten Standardzustand.
7. **Barrierefreiheit:** Der Toggle ist ein echtes, per Tastatur bedienbares Bedienelement (Fokus, Enter/Space) und kommuniziert seinen Zustand (auf-/zugeklappt) an assistive Technologien.
8. **Mobile Agenda** bleibt funktional und optisch unverändert.

## Out of Scope

- Popover-/Modal-Darstellung (alternative Lösungsansätze) – bewusst nicht gewählt.
- Persistieren des Aufklapp-Zustands über Seiten-Reloads oder Navigation hinweg.
- Änderungen an der Termin-Detailseite oder an den Event-Chips selbst.
