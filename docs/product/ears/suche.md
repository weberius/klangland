# EARS – Suche

**System:** die Kopfzeile der Webapp

Globale Suche in der Kopfzeile über den geladenen Datenbestand. Siehe auch
[Contract](../contracts/suche.feature).

## Suchfeld und Verfügbarkeit

- **SUC-1** (ubiquitär): Die Kopfzeile der Webapp MUSS auf jeder Seite ein Suchfeld anzeigen.

- **SUC-2** (ubiquitär): Die Kopfzeile der Webapp MUSS das Suchfeld zwischen
  „Klangland" und der Hauptnavigation platzieren.

## Suchauslösung

- **SUC-3** (zustandsgesteuert): SOLANGE weniger als drei Zeichen eingegeben sind, MUSS die
  Kopfzeile der Webapp keine Suche ausführen.

- **SUC-4** (ereignisgesteuert): WENN mindestens drei Zeichen in das Suchfeld eingegeben
  werden, MUSS die Kopfzeile der Webapp die Suche automatisch ausführen.

## Trefferqualität und Suchraum

- **SUC-5** (ubiquitär): Die Kopfzeile der Webapp MUSS die Suche über den geladenen
  Datenbestand ausführen.

- **SUC-6** (ubiquitär): Die Kopfzeile der Webapp MUSS Fuzzy-Suche unterstützen, damit auch
  nahe Schreibweisen Treffer liefern.
