# User Story 028 - Spielstätten-Liste nach Favoriten filtern

## User Story

**Als** Nutzer:in, die Events als Favoriten markiert hat,
**möchte ich** auf der Spielstätten-Seite (`venues`) den Filter „Nur Favoriten" anwenden können,
**damit** mir ausschließlich die Spielstätten angezeigt werden, an denen eines meiner Favoriten-Events stattfindet.

## Kontext / Problem

Die Seite `venues` filtert ihre Listenansicht aktuell nach Ort und Musikprofil. Ein Filterkriterium „Nur Favoriten" fehlt. Wenn Nutzer:innen ihre Favoriten-Events überblicken möchten, können sie über die Spielstätten-Seite aktuell nicht direkt sehen, welche Spielstätten für ihre Favoriten relevant sind. Außerdem wird in der gefilterten Liste das Favoritensymbol der zugehörigen Events nicht angezeigt.

## Gewählte Lösung

Das bestehende Filterset auf `venues` wird um das Kriterium „Nur Favoriten" erweitert. Bei aktivem Favoriten-Filter werden nur Spielstätten angezeigt, denen mindestens ein als Favorit markiertes Event zugeordnet ist. Zusätzlich werden in der Listenansicht der Spielstätten die zugehörigen Events mit ihrem Favoritenstatus (Sternchen) gekennzeichnet.

## Akzeptanzkriterien

1. **Filter vorhanden:** Auf der Seite `venues` steht das Filterkriterium „Nur Favoriten" zur Verfügung.
2. **Korrekte Filterung:** Bei aktivem Favoriten-Filter werden ausschließlich Spielstätten angezeigt, denen mindestens ein Favoriten-Event zugeordnet ist.
3. **Favoritenmarkierung sichtbar:** Die zugehörigen Events in der Spielstätten-Liste zeigen das Sternchen-Symbol, wenn sie als Favorit markiert sind.
4. **Kombination mit anderen Filtern:** Der Favoriten-Filter lässt sich mit den bestehenden Filtern (Ort, Musikprofil) kombinieren.
5. **Keine Favoriten aktiv:** Ist kein Event als Favorit markiert und der Favoriten-Filter ist aktiviert, wird eine leere Liste oder ein entsprechender Hinweistext angezeigt.

## Out of Scope

- Änderungen an der Detailseite einzelner Spielstätten (`venues/:id`).
- Favoriten-Filterung auf anderen Seiten (eigene Stories).
