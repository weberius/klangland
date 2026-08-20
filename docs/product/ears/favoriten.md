# EARS – Favoriten

**System:** die Favoriten-Funktion (Stern auf der Event-Detailseite, Markierung in der
Kalender-Übersicht, „Nur Favoriten"-Filter und Teilen-Aktion im Filter-Popover)

Favoriten für Events: markieren, in der Übersicht kennzeichnen, im Popover filtern
(UND-kombiniert mit Ort/Profil) und per Link teilen. Favoriten sind flüchtig (nur im
Speicher); Wiederherstellung ausschließlich über den geteilten Link. Siehe auch
[Contract](../contracts/favoriten.feature) und
[US-021](../planning/done/US-021-favoriten.md).

## Markieren

- **FAV-1** (ereignisgesteuert): WENN der Favoriten-Stern auf einer Event-Detailseite
  ausgelöst wird, MUSS die Favoriten-Funktion den Favoriten-Zustand des Events umschalten
  und den neuen Zustand sichtbar darstellen.

- **FAV-2** (ubiquitär): Die Favoriten-Funktion MUSS Favoriten ausschließlich für Events
  bereitstellen, nicht für Ensembles oder Spielstätten.

## Kennzeichnung in der Übersicht

- **FAV-3** (zustandsgesteuert): SOLANGE ein Event als Favorit markiert ist, MUSS die
  Kalender-Übersicht das Event (Kachel und Agenda) mit einem Stern in der rechten oberen
  Ecke kennzeichnen.

## Flüchtiger Zustand

- **FAV-4** (ubiquitär): Die Favoriten-Funktion MUSS den Favoriten-Zustand nur im Speicher
  halten und darf ihn nicht in `localStorage` oder `sessionStorage` persistieren.

- **FAV-5** (ubiquitär): Ohne Zutun MUSS die Favoriten-Funktion im Standardzustand keine
  Favoriten gesetzt und den Favoriten-Filter ausgeschaltet haben.

## Filtern

- **FAV-6** (ereignisgesteuert): WENN „Nur Favoriten" im Filter-Popover umgeschaltet wird,
  MUSS die Favoriten-Funktion den Favoriten-Filter ein- bzw. ausschalten.

- **FAV-7** (zustandsgesteuert): SOLANGE der Favoriten-Filter aktiv ist, MUSS der Kalender
  nur favorisierte Events anzeigen.

- **FAV-8** (zustandsgesteuert): SOLANGE der Favoriten-Filter zusammen mit Ort und/oder
  Musikprofil aktiv ist, MUSS der Kalender die Kriterien UND-kombinieren (innerhalb Ort bzw.
  Profil jeweils ODER).

- **FAV-9** (ubiquitär): Die Favoriten-Funktion MUSS die Ensemble- und Spielstätten-Liste
  vom Favoriten-Filter unberührt lassen.

## Zurücksetzen

- **FAV-10** (ereignisgesteuert): WENN „Alle zurücksetzen" im Popover ausgelöst wird, MUSS
  die Favoriten-Funktion neben den Ort-/Profil-Filtern auch den Favoriten-Filter und alle
  Favoriten-Markierungen entfernen.

## Teilen und Wiederherstellen

- **FAV-11** (ereignisgesteuert): WENN die Teilen-Aktion ausgelöst wird, MUSS die
  Favoriten-Funktion auf Abruf einen Link erzeugen, dessen Query-Parameter die favorisierten
  Events kodiert.

- **FAV-12** (ereignisgesteuert): WENN die App über einen Link mit Favoriten-Parameter
  geladen wird, MUSS die Favoriten-Funktion die enthaltenen, existierenden Events als
  Favoriten wiederherstellen.

- **FAV-13** (ubiquitär): Die Favoriten-Funktion MUSS beim Aufruf/Reload ohne
  Favoriten-Parameter keine Favoriten setzen.

- **FAV-14** (ereignisgesteuert): FALLS der Favoriten-Parameter unbekannte oder ungültige
  IDs enthält, DANN MUSS die Favoriten-Funktion diese ignorieren und nur existierende Events
  übernehmen.

## Barrierefreiheit

- **FAV-15** (ubiquitär): Die Favoriten-Funktion MUSS Stern-Toggle und „Nur
  Favoriten"-Umschaltung als per Tastatur bedienbare Bedienelemente bereitstellen und ihren
  Zustand (z. B. `aria-pressed`) an assistive Technologien kommunizieren.
