# User Story 032 - Filter und Favoritenmarkierung auf Komponist:in-Detailseite

## User Story

**Als** Nutzer:in, die Events als Favoriten markiert hat und globale Filter gesetzt hat,
**möchte ich**, dass auf der Komponist:in-Detailseite (`composers/:id`) sowohl die Veranstaltungsliste als auch die Liste der gespielten Werke gefiltert werden und Favoriten-Events mit einem Sternchen gekennzeichnet sind,
**damit** ich schnell meine relevanten Veranstaltungen und Werke im Kontext einer Komponist:in überblicken kann.

## Kontext / Problem

Auf der Seite `composers/:id` werden Veranstaltungen und gespielte Werke einer Komponist:in aufgelistet. Aktuell werden weder die globalen Filter (Ort, Musikprofil, Nur Favoriten) auf diese Listen angewendet, noch wird bei Favoriten-Events das Sternchen-Symbol angezeigt. Das ist inkonsistent mit dem Verhalten anderer Listenansichten in der Anwendung.

## Gewählte Lösung

Die Seite `composers/:id` wird um zwei Aspekte erweitert:
1. Die Veranstaltungsliste und die Liste der gespielten Werke werden entsprechend der aktiv gesetzten globalen Filter (Ort, Musikprofil, Nur Favoriten) eingeschränkt.
2. Favoriten-Events in der Veranstaltungsliste werden mit dem Sternchen-Symbol markiert.

## Akzeptanzkriterien

1. **Favoritenmarkierung:** Als Favorit markierte Events in der Veranstaltungsliste auf `composers/:id` zeigen das Sternchen-Symbol.
2. **Favoriten-Filter auf Veranstaltungen:** Bei aktivem „Nur Favoriten"-Filter werden in der Veranstaltungsliste ausschließlich Favoriten-Events angezeigt.
3. **Favoriten-Filter auf Werke:** Bei aktivem „Nur Favoriten"-Filter werden in der Liste der gespielten Werke nur Werke angezeigt, die in mindestens einem Favoriten-Event aufgeführt werden.
4. **Ort- und Musikprofilfilter:** Die bestehenden Filter (Ort, Musikprofil) wirken ebenfalls auf beide Listen.
5. **Kein Ergebnis:** Liefert ein aktiver Filter keine Treffer, wird eine leere Liste oder ein entsprechender Hinweistext angezeigt.
6. **Stammdaten unberührt:** Die Kerninformationen der Komponist:in (Name, Biografie etc.) werden durch Filter nicht ausgeblendet.

## Out of Scope

- Favoritenmarkierung von Komponist:innen selbst.
- Filterung der allgemeinen Komponist:innen-Liste `composers` (eigene Story US-029).
