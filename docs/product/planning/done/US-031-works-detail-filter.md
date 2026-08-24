# User Story 031 - Filter auf Werk-Detailseite anwenden

## User Story

**Als** Nutzer:in der Klangland-Webanwendung,
**möchte ich**, dass die globalen Filter (Ort, Musikprofil, Nur Favoriten) auch auf der Werk-Detailseite (`works/:id`) wirken,
**damit** die auf der Detailseite angezeigten Veranstaltungen und Informationen konsistent mit meinen aktiven Filtereinstellungen sind.

## Kontext / Problem

Auf der Seite `works/:id` werden Details zu einem einzelnen Werk sowie zugehörige Veranstaltungen angezeigt. Im Gegensatz zu den Listenansichten (`works`, `composers`, `venues`) bleibt die Detailseite aktuell von den globalen Filtern (Ort, Musikprofil, Favoriten) unberührt. Das führt dazu, dass Veranstaltungen erscheinen, die nicht den Filterkriterien der Nutzer:in entsprechen, was die Konsistenz des Nutzungserlebnisses beeinträchtigt.

## Gewählte Lösung

Die Detailseite `works/:id` wird so angepasst, dass die aktiv gesetzten globalen Filter (Ort, Musikprofil, Nur Favoriten) auf die dort angezeigten Veranstaltungslisten angewendet werden. Die Filterlogik soll dabei dieselbe sein wie in den Listenansichten.

## Akzeptanzkriterien

1. **Ortsfilter wirkt:** Ist ein Ortsfilter aktiv, werden auf `works/:id` nur Veranstaltungen aus dem gewählten Ort angezeigt.
2. **Musikprofilfilter wirkt:** Ist ein Musikprofilfilter aktiv, werden nur passende Veranstaltungen angezeigt.
3. **Favoritenfilter wirkt:** Ist „Nur Favoriten" aktiv, werden nur als Favorit markierte Veranstaltungen auf `works/:id` angezeigt.
4. **Kombination:** Mehrere gleichzeitig aktive Filter werden kumulativ angewendet.
5. **Kein Ergebnis:** Liefert ein aktiver Filter keine Treffer, wird eine leere Liste oder ein entsprechender Hinweistext angezeigt.
6. **Stammdaten unberührt:** Die Kerninformationen des Werks (Titel, Komponist:in, Beschreibung) werden durch Filter nicht ausgeblendet.

## Out of Scope

- Anpassung der Filterbedienelemente selbst.
- Filterung auf anderen Detailseiten (eigene Stories).
