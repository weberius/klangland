# EARS – Ensembles

**System:** die Ensembleübersicht bzw. das Ensembleprofil

Übersicht aller Ensembles sowie Profil je Ensemble mit Stammdaten und zugehörigen
Veranstaltungen. Siehe auch [Contract](../contracts/ensembles.feature).

## Ensembleübersicht

- **ENS-1** (ubiquitär): Die Ensembleübersicht MUSS alle erfassten Ensembles anzeigen.

- **ENS-2** (ubiquitär): Die Ensembleübersicht MUSS die Ensembles alphabetisch nach Namen
  sortieren.

- **ENS-3** (ubiquitär): Die Ensembleübersicht MUSS je Ensemble Name, Sitzort, Leitung sowie
  die Anzahl der erfassten Veranstaltungen anzeigen.

- **ENS-4** (ereignisgesteuert): WENN eine Ensemblekarte ausgewählt wird, MUSS die
  Ensembleübersicht zum Profil dieses Ensembles wechseln.

## Ensembleprofil

- **ENS-5** (ereignisgesteuert): WENN eine Adresse der Form `/ensembles/<id>` mit bekannter
  Ensemble-ID aufgerufen wird, MUSS das Ensembleprofil dieses Ensemble anzeigen.

- **ENS-6** (ubiquitär): Das Ensembleprofil MUSS Name, Sitzort und Leitung des Ensembles
  anzeigen.

- **ENS-7** (optionales Merkmal): SOFERN ein Stammsaal oder eine Trägerinstitution
  hinterlegt ist, MUSS das Ensembleprofil diese anzeigen.

- **ENS-8** (zustandsgesteuert): SOLANGE dem Ensemble Veranstaltungen zugeordnet sind, MUSS
  das Ensembleprofil diese chronologisch geordnet anzeigen.

- **ENS-9** (ereignisgesteuert): WENN im Profil eine Veranstaltung ausgewählt wird, MUSS das
  Ensembleprofil zur Detailseite dieser Veranstaltung wechseln.
