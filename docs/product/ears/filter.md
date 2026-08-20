# EARS – Ort-Filter

**System:** die Filterleiste der Listenseiten (Kalender, Ensembles, Spielstätten)

Ort-Filter über Bubbles unterhalb der Seitenüberschrift, gesteuert über den Sitzort der
Ensembles. Siehe auch [Contract](../contracts/filter.feature) und
[US-011](../planning/doing/US-011-filter.md).

## Bubble-Quelle und Beschriftung

- **FIL-1** (ubiquitär): Die Filterleiste MUSS genau eine Bubble je Stadt anzeigen, in der
  mindestens ein Ensemble seinen Sitz hat.

- **FIL-2** (ubiquitär): Die Filterleiste MUSS für Städte, die ausschließlich als
  Veranstaltungsort ohne ansässiges Ensemble vorkommen, keine Bubble anzeigen.

- **FIL-3** (ubiquitär): Die Filterleiste MUSS jede Bubble mit dem Kfz-Kennzeichen der
  Stadt beschriften, nicht mit dem ausgeschriebenen Ortsnamen.

## Standardzustand

- **FIL-4** (zustandsgesteuert): SOLANGE keine Bubble ausgewählt ist, MUSS die Filterleiste
  alle Inhalte (Veranstaltungen, Ensembles, Spielstätten) anzeigen.

## Auswahl und Wirkung

- **FIL-5** (zustandsgesteuert): SOLANGE mindestens eine Bubble ausgewählt ist, MUSS der
  Kalender nur Veranstaltungen anzeigen, bei denen mindestens ein auftretendes Ensemble
  seinen Sitz in einer der ausgewählten Städte hat.

- **FIL-6** (zustandsgesteuert): SOLANGE mindestens eine Bubble ausgewählt ist, MUSS die
  Ensemble-Liste nur Ensembles mit Sitz in einer der ausgewählten Städte anzeigen.

- **FIL-7** (zustandsgesteuert): SOLANGE mindestens eine Bubble ausgewählt ist, MUSS die
  Spielstätten-Liste nur Spielstätten anzeigen, in denen Ensembles einer der ausgewählten
  Städte auftreten.

- **FIL-8** (zustandsgesteuert): SOLANGE mehrere Bubbles ausgewählt sind, MUSS die
  Filterleiste die Auswahl additiv (ODER-Verknüpfung) auswerten.

## Auswahl ändern

- **FIL-9** (ereignisgesteuert): WENN eine nicht ausgewählte Bubble angeklickt wird, MUSS
  die Filterleiste die zugehörige Stadt zur Auswahl hinzufügen.

- **FIL-10** (ereignisgesteuert): WENN eine ausgewählte Bubble erneut angeklickt wird, MUSS
  die Filterleiste die zugehörige Stadt aus der Auswahl entfernen.

- **FIL-11** (ubiquitär): Die Filterleiste MUSS ausgewählte Bubbles sichtbar markiert und
  nicht ausgewählte Bubbles unmarkiert darstellen.

## Persistenz

- **FIL-12** (ubiquitär): Die Filterleiste MUSS die getroffene Auswahl beim Wechsel zwischen
  Kalender-, Ensemble- und Spielstätten-Seite erhalten.

## Position und Beschreibung

- **FIL-13** (ubiquitär): Die Filterleiste MUSS unterhalb der jeweiligen Seitenüberschrift
  stehen.

- **FIL-14** (ereignisgesteuert): WENN der Info-Button „i" ausgelöst wird, MUSS die
  Filterleiste die Sichtbarkeit der Seitenbeschreibung umschalten.

## Navigation

- **FIL-15** (ubiquitär): Die Kopfzeile der Webapp MUSS die Hauptnavigation in allen
  Viewports als quadratisches Burger-Menü anzeigen.

## Barrierefreiheit

- **FIL-16** (ubiquitär): Die Filterleiste MUSS Bubbles und Info-Button als per Tastatur
  bedienbare Bedienelemente bereitstellen und ihren Zustand (ausgewählt bzw. auf-/zugeklappt)
  an assistive Technologien kommunizieren.
