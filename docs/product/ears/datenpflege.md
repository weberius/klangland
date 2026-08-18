# EARS – Datenpflege (Daten-Tooling)

**System:** das Ingest-Skript

Je Quelle gibt es ein idempotentes Python-Ingest-Skript, das Spielpläne in die
versionierten JSON-Dateien übernimmt. Siehe [Daten-Tooling](../../data-tooling/README.md)
und [ADR-005](../../architecture/ADR-005-idempotente-python-ingest-skripte.md).

## Anforderungen

- **DAT-1** (ubiquitär): Das Ingest-Skript MUSS je Aufführungstermin genau ein Event
  erzeugen.

- **DAT-2** (ubiquitär): Das Ingest-Skript MUSS Beziehungen ausschließlich über IDs
  herstellen und Stammdaten nicht in referenzierenden Objekten duplizieren.

- **DAT-3** (ubiquitär): Das Ingest-Skript MUSS IDs im `kebab-case` mit Transliteration
  deutscher Umlaute (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`) bilden.

- **DAT-4** (ereignisgesteuert): WENN das Ingest-Skript erneut ausgeführt wird, MUSS es die
  zuvor aus derselben Quelle eingespielten Events entfernen, bevor es neue schreibt
  (Idempotenz).

- **DAT-5** (unerwünschtes Verhalten): FALLS ein Stammdatum anhand seiner ID bereits
  existiert, DANN DARF das Ingest-Skript es NICHT ein zweites Mal anlegen.

- **DAT-6** (ubiquitär): Das Ingest-Skript MUSS zu jedem Event die ursprüngliche Quelle
  erfassen.

- **DAT-7** (ereignisgesteuert): WENN ein Ingest-Lauf abgeschlossen ist, MUSS die
  referenzielle Integrität, die Eindeutigkeit der IDs sowie die Gültigkeit der Datums- und
  Zeitformate geprüft werden.

- **DAT-8** (unerwünschtes Verhalten): FALLS eine referenzierte ID nicht in ihrer Zieldatei
  existiert, DANN MUSS die Prüfung den betroffenen Datensatz als Fehler melden.
