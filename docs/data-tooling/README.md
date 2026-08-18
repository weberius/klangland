# Daten-Tooling

Skripte und Dokumentation zur Recherche und Übernahme von Spielplänen in die
versionierten JSON-Dateien unter [`data/`](../../data). Jedes Ensemble mit eigener,
maschinenlesbarer Quelle bekommt hier ein Ingest-Skript und eine kurze Doku, die die
Quelle, die Mapping-Regeln und die Kuratierungsentscheidungen festhält.

Die Skripte sind **idempotent**: Sie entfernen zuvor eingespielte Events der jeweiligen
Quelle (erkannt am Quell-Host) und legen Stammdaten anhand ihrer IDs dublettenfrei an.

## Übersicht

| Ensemble | Quelle | Skript | Doku |
| --- | --- | --- | --- |
| Bergische Symphoniker | `bergischesymphoniker.de/api/concerts` | [`ingest_bergische.py`](ingest_bergische.py) | [bergische-symphoniker.md](bergische-symphoniker.md) |
| Sinfonieorchester Aachen | `theateraachen.de` (Konzertseite + Detailseiten) | [`ingest_aachen.py`](ingest_aachen.py) | [sinfonieorchester-aachen.md](sinfonieorchester-aachen.md) |
| Bochumer Symphoniker | `bochumer-symphoniker.de` (Suche/Paging + Detailseiten) | [`ingest_bochum.py`](ingest_bochum.py) | [bochumer-symphoniker.md](bochumer-symphoniker.md) |
| Dortmunder Philharmoniker | `theaterdo.de` (Kalender-Paging + Detailseiten) | [`ingest_dortmund.py`](ingest_dortmund.py) | [dortmunder-philharmoniker.md](dortmunder-philharmoniker.md) |
| Beethoven Orchester Bonn | `beethoven-orchester.de` (Archiv 26-27 + Detailseiten) | [`ingest_bonn.py`](ingest_bonn.py) | [beethoven-orchester-bonn.md](beethoven-orchester-bonn.md) |
| Bielefelder Philharmoniker | `buo-bielefeld.de` (Kalender-Paging + Detailseiten) | [`ingest_bielefeld.py`](ingest_bielefeld.py) | [bielefelder-philharmoniker.md](bielefelder-philharmoniker.md) |
| Essener Philharmoniker | `theater-essen.de/programm/spielzeit-26-27` (HTML) | [`ingest_essener.py`](ingest_essener.py) | [essener-philharmoniker.md](essener-philharmoniker.md) |
| Gürzenich-Orchester Köln | `guerzenich-orchester.de` (Sitemap + Detailseiten) | [`ingest_guerzenich.py`](ingest_guerzenich.py) | [guerzenich-orchester-koeln.md](guerzenich-orchester-koeln.md) |

## Konventionen

- Zielschema und Beziehungen: [`../data-model.md`](../data-model.md),
  [`../events-and-relations.md`](../events-and-relations.md).
- Je Aufführungstermin ein Event; Referenzen ausschließlich über IDs.
- IDs in `kebab-case`; Transliteration deutscher Umlaute (`ä→ae`, `ö→oe`, `ü→ue`,
  `ß→ss`), sonstige Diakritika werden entfernt.
- Nach jedem Ingest: referenzielle Integrität, ID-Eindeutigkeit sowie Datums-/
  Zeitformate prüfen.
