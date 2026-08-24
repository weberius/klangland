# User Story 034 - Karte und Navigation zur Karten-App auf der Spielstätten-Detailseite

## User Story

**Als** Nutzer:in, die eine Spielstätte besuchen möchte,
**möchte ich** auf der Detailseite einer Spielstätte (`venues/:id`) eine eingebettete Karte sowie einen Button zum Öffnen der nativen Karten-App meines Geräts sehen,
**damit** ich den Weg zur Spielstätte schnell und unkompliziert finden kann.

## Kontext / Problem

Auf der Detailseite eines Events (`events/:id`) werden neben dem Veranstaltungsort bereits eine eingebettete Karte und ein Button zum Öffnen der Karten-App des Geräts angeboten. Auf der Spielstätten-Detailseite (`venues/:id`) fehlen diese Elemente bislang komplett. Nutzer:innen, die direkt zur Spielstätten-Seite navigieren, erhalten dort keine Navigationshilfe. Darüber hinaus sollte die Darstellung des Veranstaltungsorts auf beiden Seiten vereinheitlicht werden – idealerweise durch eine gemeinsame Komponente.

## Gewählte Lösung

Die Detailseite `venues/:id` wird in der Desktop-Ansicht um eine zusätzliche Box für die eingebettete Karte erweitert. Der Kartenpunkt der Spielstätte wird blau dargestellt (konsistent mit dem Spielstätten-Layer der `cities`-Karte). Außerdem wird ein Button „In Karten-App öffnen" ergänzt. Die Darstellung des Veranstaltungsorts auf `events/:id` und `venues/:id` wird in einer gemeinsamen Komponente zusammengeführt.

## Akzeptanzkriterien

1. **Karten-Box auf `venues/:id`:** In der Desktop-Ansicht gibt es neben Ort und Adresse eine Box mit einer eingebetteten Karte, die den Standort der Spielstätte zeigt.
2. **Blauer Kartenpunkt:** Der Marker für die Spielstätte auf der eingebetteten Karte ist blau.
3. **Button „In Karten-App öffnen":** Auf `venues/:id` gibt es einen Button, der die native Karten-App des Geräts (z. B. Apple Maps, Google Maps) mit der Adresse der Spielstätte öffnet.
4. **Konsistente Darstellung:** Die Darstellung des Veranstaltungsorts (Karte + Navigations-Button) auf `events/:id` und `venues/:id` ist visuell und funktional identisch.
5. **Gemeinsame Komponente:** Die Karten- und Navigationsdarstellung ist in einer wiederverwendbaren Komponente implementiert, die auf beiden Seiten eingesetzt wird.
6. **Mobile Ansicht:** Auf mobilen Geräten verhält sich die Darstellung sinnvoll (z. B. nur Button, keine vollständige Karten-Box, falls das Layout es erfordert).

## Out of Scope

- Änderungen an der eingebetteten Karte auf `events/:id` über die Vereinheitlichung hinaus.
- Integration weiterer Karten-Provider.
- Routenplanung innerhalb der Anwendung.
