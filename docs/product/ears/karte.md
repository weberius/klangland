# EARS – Karte der Ensemble-Orte

**System:** die Kartenseite (`/cities`)

Geografische Übersicht aller Orte mit ansässigem Ensemble auf einer OpenStreetMap-Karte.
Ein Klick auf einen Ort öffnet einen Dialog mit den dort ansässigen Ensembles und erlaubt es,
von dort aus den Ort-Filter zu setzen. Siehe auch [Contract](../contracts/karte.feature),
[Ort-Filter](filter.md) und [US-013](../planning/done/US-013-map-country.md).

## Route und Navigation

- **KAR-1** (ubiquitär): Die Webapp MUSS die Kartenseite unter der Route `/cities` mit dem
  Seitentitel „Karte · Klangland" bereitstellen.

- **KAR-2** (ubiquitär): Die Hauptnavigation MUSS zusätzlich zu „Kalender", „Ensembles" und
  „Spielstätten" den Eintrag „Karte" (Ziel `/cities`) anzeigen und ihn im aktiven Zustand markieren.

## Kartengrundlage

- **KAR-3** (ubiquitär): Die Kartenseite MUSS die Karte mit OpenStreetMap-Kacheln rendern und
  die vorgeschriebene OSM-Attribution anzeigen.

## Marker

- **KAR-4** (ubiquitär): Die Kartenseite MUSS ausschließlich Orte mit mindestens einem
  ansässigen Ensemble und hinterlegten Koordinaten als roten Marker darstellen.

- **KAR-5** (ubiquitär): Die Kartenseite MUSS keine Spielstätten/Venues als Marker darstellen.

- **KAR-6** (ubiquitär): Die Kartenseite MUSS jeden Marker auf der Koordinate der Stadt selbst
  positionieren, nicht auf der Adresse einer Spielstätte.

## Dialog und Filter

- **KAR-7** (ereignisgesteuert): WENN ein Marker ausgelöst wird, MUSS die Kartenseite einen
  Dialog öffnen, der die Ensembles dieses Ortes auflistet.

- **KAR-8** (ereignisgesteuert): WENN im geöffneten Dialog der Filter-Button ausgelöst wird und
  der Ort noch nicht gefiltert ist, MUSS die Kartenseite den Ort-Filter für diesen Ort setzen.

- **KAR-9** (ereignisgesteuert): WENN im geöffneten Dialog der Filter-Button ausgelöst wird und
  der Ort bereits gefiltert ist, MUSS die Kartenseite den Ort-Filter für diesen Ort entfernen.

- **KAR-10** (ubiquitär): Die Kartenseite MUSS den Ort-Filter über den gemeinsamen Filterdienst
  setzen, sodass die Auswahl mit dem Bubble-Filter (US-011/US-020) konsistent und über
  Seitenwechsel hinweg wirksam ist.

## Hervorhebung

- **KAR-11** (zustandsgesteuert): SOLANGE der Ort-Filter für einen Ort aktiv ist, MUSS die
  Kartenseite dessen Marker sichtbar vom Standard-Marker unterscheidbar hervorheben.

- **KAR-12** (ereignisgesteuert): WENN der Ort-Filter zurückgesetzt oder deaktiviert wird, MUSS
  die Kartenseite die zugehörige Marker-Hervorhebung entfernen.

## Barrierefreiheit

- **KAR-13** (ubiquitär): Die Kartenseite MUSS den Filter-Button im Dialog per Tastatur bedienbar
  bereitstellen und seinen Zustand (aktiv/inaktiv) an assistive Technologien kommunizieren.

- **KAR-14** (ereignisgesteuert): WENN im geöffneten Dialog die Escape-Taste ausgelöst wird, MUSS
  die Kartenseite den Dialog schließen.
