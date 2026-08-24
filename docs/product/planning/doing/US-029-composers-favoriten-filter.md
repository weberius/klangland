# User Story 029 - Komponistinnen-Liste nach Favoriten filtern

## User Story

**Als** Nutzer:in, die Events als Favoriten markiert hat,
**möchte ich** auf der Komponist:innen-Seite (`composers`) den Filter „Nur Favoriten" anwenden können,
**damit** mir ausschließlich die Komponist:innen angezeigt werden, deren Werke in einem meiner Favoriten-Events gespielt werden.

## Kontext / Problem

Die Seite `composers` filtert ihre Listenansicht aktuell nach Ort und Musikprofil. Ein Filterkriterium „Nur Favoriten" fehlt. Nutzer:innen, die bestimmte Events als Favoriten markiert haben, können auf der Komponist:innen-Seite aktuell nicht direkt erkennen, welche Komponist:innen in ihren Favoriten-Events vertreten sind.

## Gewählte Lösung

Das bestehende Filterset auf `composers` wird um das Kriterium „Nur Favoriten" erweitert. Bei aktivem Favoriten-Filter werden nur Komponist:innen angezeigt, deren Werke in mindestens einem als Favorit markierten Event aufgeführt werden.

## Akzeptanzkriterien

1. **Filter vorhanden:** Auf der Seite `composers` steht das Filterkriterium „Nur Favoriten" zur Verfügung.
2. **Korrekte Filterung:** Bei aktivem Favoriten-Filter werden ausschließlich Komponist:innen angezeigt, die mit mindestens einem Favoriten-Event verknüpft sind.
3. **Kombination mit anderen Filtern:** Der Favoriten-Filter lässt sich mit den bestehenden Filtern (Ort, Musikprofil) kombinieren.
4. **Keine Favoriten aktiv:** Ist kein Event als Favorit markiert und der Favoriten-Filter ist aktiviert, wird eine leere Liste oder ein entsprechender Hinweistext angezeigt.

## Out of Scope

- Favoritenmarkierung einzelner Komponist:innen (im Unterschied zu Events).
- Filterung auf der Detailseite `composers/:id` (eigene Story).
