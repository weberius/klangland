# EARS – Spielstätten

**System:** die Spielstättenübersicht bzw. das Spielstättenprofil

Übersicht aller Spielstätten sowie Profil je Spielstätte mit Stammdaten und den dort
stattfindenden Veranstaltungen. Siehe auch [Contract](../contracts/spielstaetten.feature).

## Spielstättenübersicht

- **SPI-1** (ubiquitär): Die Spielstättenübersicht MUSS alle erfassten Spielstätten anzeigen.

- **SPI-2** (ubiquitär): Die Spielstättenübersicht MUSS die Spielstätten alphabetisch nach
  Namen sortieren.

- **SPI-3** (ubiquitär): Die Spielstättenübersicht MUSS je Spielstätte Name, Ort sowie die
  Anzahl der dort erfassten Veranstaltungen anzeigen.

- **SPI-4** (ereignisgesteuert): WENN eine Spielstättenkarte ausgewählt wird, MUSS die
  Spielstättenübersicht zum Profil dieser Spielstätte wechseln.

## Spielstättenprofil

- **SPI-5** (ereignisgesteuert): WENN eine Adresse der Form `/venues/<id>` mit bekannter
  Spielstätten-ID aufgerufen wird, MUSS das Spielstättenprofil diese Spielstätte anzeigen.

- **SPI-6** (ubiquitär): Das Spielstättenprofil MUSS Name und Ort der Spielstätte anzeigen.

- **SPI-7** (optionales Merkmal): SOFERN eine Trägerinstitution hinterlegt ist, MUSS das
  Spielstättenprofil diese anzeigen.

- **SPI-8** (zustandsgesteuert): SOLANGE an der Spielstätte Veranstaltungen erfasst sind,
  MUSS das Spielstättenprofil diese chronologisch geordnet anzeigen.
