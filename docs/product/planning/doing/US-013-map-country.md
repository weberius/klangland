# User Story 013 - Ensemble-Orte auf einer Karte

## User Story

**Als** Besucher:in, der:die einen räumlichen Überblick über die Musiklandschaft sucht,
**möchte ich** alle Orte mit ansässigem Ensemble auf einer Karte sehen und von dort aus den Ort-Filter setzen können,
**damit** ich schnell erkenne, wo Ensembles beheimatet sind, und die Konzertauswahl auf einen Ort einschränken kann.

## Kontext / Problem

Die App zeigt Ensembles ([ensembles.json](../../../../data/ensembles.json)) und ihre Sitzorte ([cities.json](../../../../data/cities.json)) bisher ausschließlich als Listen. Eine **geografische Übersicht**, wo die Ensembles beheimatet sind, fehlt vollständig.

Ein Ort-Filter existiert bereits: Der `FilterService` hält die aktive Ort-Auswahl additiv und persistent über Seitenwechsel hinweg ([filter.service.ts:20-58](../../../../web/src/app/core/filter.service.ts#L20-L58), eingeführt in US-020). Es fehlt eine Möglichkeit, diesen Filter **direkt von einer Karte aus** zu setzen.

Für die Kartendarstellung fehlen zudem die **Geokoordinaten**: cities.json enthält je Ort nur `id`, `name`, `country` und ggf. `plate`, aber keine Länge/Breite.

Betroffen sind eine **neue Seite/Route** sowie die Hauptnavigation ([app.html:65-74](../../../../web/src/app/app.html#L65-L74)) und die Datendatei cities.json. **Nicht** betroffen sind Spielstätten (Venues) – diese werden auf dieser Karte bewusst nicht dargestellt.

## Gewählte Lösung

**Eigene Kartenseite unter der Route `/cities`** mit einer OpenStreetMap-Karte, gerendert über **Leaflet**. Jeder Ort, dem ein Ensemble zugeordnet ist, wird als **roter Punkt** auf den Koordinaten der **Stadt selbst** (nicht der Spielstätte) angezeigt. Die Ansicht dient dem Überblick.

Ein **Klick auf einen Marker** öffnet einen Dialog/Popover, der die **Ensembles dieses Ortes** auflistet und einen **Button** anbietet, mit dem der Ort-Filter für diesen Ort **aktiviert bzw. deaktiviert** werden kann. Wird der Filter aktiviert, nutzt die Seite den bestehenden `FilterService` (additiv, konsistent mit US-020); der Filter bleibt bei der weiteren Nutzung der App aktiv, bis er wieder deaktiviert bzw. an den bereits vorhandenen Stellen zurückgesetzt wird. Der aktuell gefilterte Ort wird auf der Karte **visuell hervorgehoben**.

Die fehlenden Koordinaten werden vorab per **Overpass-API von OpenStreetMap** recherchiert (eigenes Python-Skript, **max. 1 Abfrage pro Sekunde**) und je Ort in cities.json abgelegt.

Ein neuer Navigationseintrag **„Karte“** wird neben „Kalender“, „Ensembles“ und „Spielstätten“ angezeigt.

## Akzeptanzkriterien

1. **Route:** Unter `http://localhost:4200/cities` ist die Kartenseite erreichbar (lazy geladen, Seitentitel im Stil der übrigen Routen, z. B. „Karte · Klangland“).
2. **Navigation:** In der Hauptnavigation erscheint zusätzlich zu „Kalender“, „Ensembles“ und „Spielstätten“ der Eintrag **„Karte“**, der auf `/cities` verweist und im aktiven Zustand markiert ist.
3. **Kartengrundlage:** Die Karte nutzt OpenStreetMap-Kacheln und wird mit Leaflet gerendert (inkl. korrekter OSM-Attribution).
4. **Nur Ensemble-Orte:** Es werden ausschließlich Orte mit mindestens einem zugeordneten Ensemble als **rote Marker** dargestellt. Spielstätten/Venues werden **nicht** angezeigt.
5. **Marker-Position:** Jeder Marker sitzt auf der Koordinate der **Stadt** (z. B. Köln), nicht auf der Adresse/Koordinate einer Spielstätte.
6. **Koordinatendaten:** Für jeden Ort mit zugeordnetem Ensemble sind in cities.json Geokoordinaten (Länge/Breite) hinterlegt.
7. **Recherche-Skript:** Es existiert ein Python-Skript, das die Koordinaten über die Overpass-API bezieht und dabei **höchstens eine Abfrage pro Sekunde** stellt.
8. **Klick öffnet Dialog:** Ein Klick auf einen Marker öffnet einen Dialog/Popover, der die **Ensembles dieses Ortes** auflistet.
9. **Filter setzen/entfernen:** Der Dialog enthält einen Button, mit dem der Ort-Filter für diesen Ort **aktiviert bzw. deaktiviert** wird. Bei Aktivierung werden fortan nur noch Konzerte mit der entsprechenden `cityId` (z. B. `koeln`) berücksichtigt.
10. **Persistenz:** Ein aktivierter Ort-Filter bleibt über Seitenwechsel hinweg aktiv (über den bestehenden `FilterService`, konsistent mit US-020), bis er deaktiviert bzw. an den bereits vorhandenen Stellen zurückgesetzt wird.
11. **Hervorhebung:** Ein Ort, für den der Filter aktiv ist, wird auf der Karte visuell hervorgehoben (unterscheidbar vom Standard-Marker).
12. **Filter zurücksetzen:** Das Zurücksetzen des Filters funktioniert an den bereits vorhandenen Stellen und entfernt auch die Karten-Hervorhebung.
13. **Barrierefreiheit:** Der Button zum Setzen/Entfernen des Filters ist per Tastatur bedienbar und kommuniziert seinen Zustand (aktiv/inaktiv) an assistive Technologien.

## Out of Scope

- Darstellung von Spielstätten/Venues auf der Karte.
- Clustering, Suche, Umkreissuche oder abweichende Marker-Farben je Genre/Ensemble-Typ (nur einheitlich rote Punkte).
- Persistieren des Filters über Reload/Session hinaus (localStorage/sessionStorage) – bewusst wie in US-020 ausgeschlossen.
- Anzeige der gefilterten Konzerte auf der Kartenseite selbst (die Filterwirkung greift auf den bestehenden Seiten wie dem Kalender).
- Änderungen am bestehenden Popover-Filter (US-020) über die Nutzung des `FilterService` hinaus.
