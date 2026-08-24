# User Story 027 - Favoritenmarkierung von Events in der Orchester-Detailseite

## User Story

**Als** Nutzer:in, die ein Event als Favorit markiert hat,
**möchte ich** dieses Event auch in der Veranstaltungsliste auf der Orchester-Detailseite (`orchestras/:id`) mit dem Favoriten-Symbol gekennzeichnet sehen,
**damit** ich meine Favoriten konsistent über alle Listen in der Anwendung erkenne.

## Kontext / Problem

Auf der Detailseite eines Orchesters werden am unteren Seitenbereich die zugehörigen Veranstaltungen aufgelistet. Wenn eine Veranstaltung von der Nutzer:in als Favorit markiert wurde, ist diese Markierung in der dortigen Liste aktuell nicht sichtbar. Das Favoritensymbol (Sternchen) wird in dieser Liste nicht angezeigt, obwohl es in anderen Kontexten (z. B. der Event-Listenansicht) korrekt erscheint.

## Gewählte Lösung

Die Event-Listenkomponente auf der Orchester-Detailseite (`orchestras/:id`) wird so angepasst, dass für jedes aufgelistete Event geprüft wird, ob es als Favorit markiert ist, und das entsprechende Favoritensymbol (Sternchen) eingeblendet wird. Die Logik soll konsistent mit der Favoritenmarkierung in anderen Listenansichten sein.

## Akzeptanzkriterien

1. **Anzeige des Favoriten-Symbols:** Ein als Favorit markiertes Event zeigt in der Veranstaltungsliste auf `orchestras/:id` das Sternchen-Symbol.
2. **Konsistenz:** Das Symbol wird identisch zu anderen Listenansichten (z. B. der allgemeinen Events-Liste) dargestellt.
3. **Interaktivität:** Das Favoriten-Symbol ist klickbar und ermöglicht das direkte Entfernen/Hinzufügen des Favoriten, wie in anderen Listen.
4. **Nicht-Favoriten unverändert:** Events ohne Favoritenmarkierung zeigen kein Symbol – die bestehende Darstellung bleibt erhalten.

## Out of Scope

- Änderungen an der Favoritenlogik selbst (Speicherung, Synchronisation).
- Filterung der Liste nach Favoriten (eigene Story).
