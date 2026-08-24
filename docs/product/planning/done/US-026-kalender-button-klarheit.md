# User Story 026 - Klarere Beschriftung des „In den Kalender eintragen"-Buttons

## User Story

**Als** Nutzer:in der Klangland-Webanwendung,
**möchte ich** auf der Detailseite eines Events einen klar verständlichen Hinweis erhalten, was der Button „In den Kalender eintragen" bewirkt,
**damit** ich nicht verwirrt bin, ob das Event in den Klangland-Kalender oder in den Gerätkalender (Smartphone/Desktop) eingetragen wird.

## Kontext / Problem

Auf der Detailseite eines Events (`events/:id`) existiert ein Button „In den Kalender eintragen". Die Webanwendung bietet selbst einen eigenen Kalender an, weshalb unklar ist, ob der Button das Event in den App-internen Klangland-Kalender oder in den nativen Gerätkalender (z. B. via `.ics`-Download oder CalDAV) einträgt. Diese Mehrdeutigkeit führt bei Nutzer:innen zu Verwirrung.

## Gewählte Lösung

Die Beschriftung und/oder der Tooltip des Buttons wird so angepasst, dass eindeutig hervorgeht, dass das Event in den **nativen Gerätkalender** (Smartphone / Desktop-Kalenderapp) übertragen wird – nicht in den Klangland-internen Kalender. Die präzisere Formulierung lautet: „Termin exportieren". Zusätzlich wird ein erklärender Hinweistext in Form eines (i) ergänzt.

## Akzeptanzkriterien

1. **Eindeutige Beschriftung:** Der Button auf `events/:id` trägt eine Bezeichnung, die unmissverständlich auf den nativen Gerätkalender verweist (kein Bezug zum Klangland-eigenen Kalender).
2. **Konsistenz:** Die neue Beschriftung ist auf allen Stellen im Interface einheitlich verwendet, wo diese Funktion angeboten wird.
3. **Kein funktionaler Bruch:** Die eigentliche Funktionalität (Export des Termins) bleibt unverändert erhalten.
4. **Klangland-Kalender unberührt:** Die Navigation und Funktion des Klangland-internen Kalenders wird durch diese Änderung nicht beeinflusst.

## Out of Scope

- Änderungen an der technischen Implementierung des Kalender-Exports (z. B. Format, Felder).
- Überarbeitung des Klangland-eigenen Kalenders.
