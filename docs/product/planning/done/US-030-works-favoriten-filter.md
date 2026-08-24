# User Story 030 - Werke-Liste nach Favoriten filtern

## User Story

**Als** Nutzer:in, die Events als Favoriten markiert hat,
**möchte ich** auf der Werke-Seite (`works`) den Filter „Nur Favoriten" anwenden können,
**damit** mir ausschließlich die Werke angezeigt werden, die in einem meiner Favoriten-Events gespielt werden.

## Kontext / Problem

Die Seite `works` filtert ihre Listenansicht aktuell nach Ort und Musikprofil. Ein Filterkriterium „Nur Favoriten" fehlt. Nutzer:innen, die bestimmte Events als Favoriten markiert haben, können auf der Werke-Seite aktuell nicht direkt erkennen, welche Werke in ihren Favoriten-Events aufgeführt werden.

## Gewählte Lösung

Das bestehende Filterset auf `works` wird um das Kriterium „Nur Favoriten" erweitert. Bei aktivem Favoriten-Filter werden nur Werke angezeigt, die in mindestens einem als Favorit markierten Event aufgeführt werden.

## Akzeptanzkriterien

1. **Filter vorhanden:** Auf der Seite `works` steht das Filterkriterium „Nur Favoriten" zur Verfügung.
2. **Korrekte Filterung:** Bei aktivem Favoriten-Filter werden ausschließlich Werke angezeigt, die mit mindestens einem Favoriten-Event verknüpft sind.
3. **Kombination mit anderen Filtern:** Der Favoriten-Filter lässt sich mit den bestehenden Filtern (Ort, Musikprofil) kombinieren.
4. **Keine Favoriten aktiv:** Ist kein Event als Favorit markiert und der Favoriten-Filter ist aktiviert, wird eine leere Liste oder ein entsprechender Hinweistext angezeigt.

## Out of Scope

- Favoriten-Filterung auf der Werk-Detailseite `works/:id` (eigene Story).
- Favoritenmarkierung einzelner Werke (im Unterschied zu Events).
