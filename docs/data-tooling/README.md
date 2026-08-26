# Daten-Tooling

Skripte und Dokumentation zur Recherche und Übernahme von Spielplänen in die
versionierten JSON-Dateien unter [`data/`](../../data). Jedes Ensemble mit eigener,
maschinenlesbarer Quelle bekommt hier ein Ingest-Skript und eine kurze Doku, die die
Quelle, die Mapping-Regeln und die Kuratierungsentscheidungen festhält.

Die Skripte sind **idempotent**: Sie entfernen zuvor eingespielte Events der jeweiligen
Quelle (erkannt am Quell-Host) und legen Stammdaten anhand ihrer IDs dublettenfrei an.

Ein laufender Diskussionsstand zur Weiterentwicklung (Coverage-Audit bestehender Quellen,
Ausbau um WDR-Ensembles/Oper NRW-weit, geplante Registry + gemeinsames Tooling) steht in
[`strategie-datenaktualisierung.md`](strategie-datenaktualisierung.md).

## Übersicht

| Ensemble | Quelle | Skript | Doku |
| --- | --- | --- | --- |
| Bergische Symphoniker | `bergischesymphoniker.de/api/concerts` | [`ingest_bergische.py`](ingest_bergische.py) | [bergische-symphoniker.md](bergische-symphoniker.md) |
| Sinfonieorchester Aachen | `theateraachen.de` (Konzertseite + Detailseiten) | [`ingest_aachen.py`](ingest_aachen.py) | [sinfonieorchester-aachen.md](sinfonieorchester-aachen.md) |
| Bochumer Symphoniker | `bochumer-symphoniker.de` (Suche/Paging + Detailseiten) | [`ingest_bochum.py`](ingest_bochum.py) | [bochumer-symphoniker.md](bochumer-symphoniker.md) |
| Dortmunder Philharmoniker | `theaterdo.de` (Kalender-Paging + Detailseiten) | [`ingest_dortmund.py`](ingest_dortmund.py) | [dortmunder-philharmoniker.md](dortmunder-philharmoniker.md) |
| Beethoven Orchester Bonn | `beethoven-orchester.de` (Archiv 26-27 + Detailseiten) | [`ingest_bonn.py`](ingest_bonn.py) | [beethoven-orchester-bonn.md](beethoven-orchester-bonn.md) |
| Bielefelder Philharmoniker | `buo-bielefeld.de` (Kalender-Paging + Detailseiten) | [`ingest_bielefeld.py`](ingest_bielefeld.py) | [bielefelder-philharmoniker.md](bielefelder-philharmoniker.md) |
| Duisburger Philharmoniker | `duisburger-philharmoniker.de` (Kalender + Detailseiten) | [`ingest_duisburg.py`](ingest_duisburg.py) | [duisburger-philharmoniker.md](duisburger-philharmoniker.md) |
| Philharmonisches Orchester Hagen | `theaterhagen.de` (Kalender monatsweise + Detailseiten) | [`ingest_hagen.py`](ingest_hagen.py) | [philharmonisches-orchester-hagen.md](philharmonisches-orchester-hagen.md) |
| Essener Philharmoniker | `theater-essen.de/programm/spielzeit-26-27` (HTML) | [`ingest_essener.py`](ingest_essener.py) | [essener-philharmoniker.md](essener-philharmoniker.md) |
| Gürzenich-Orchester Köln | `guerzenich-orchester.de` (Sitemap + Detailseiten) | [`ingest_guerzenich.py`](ingest_guerzenich.py) | [guerzenich-orchester-koeln.md](guerzenich-orchester-koeln.md) |

## Stammdaten-Anreicherung

| Datenbereich | Quelle | Skript | Doku |
| --- | --- | --- | --- |
| Ensemble-Orte (Geokoordinaten) | OpenStreetMap Overpass | [`geocode_cities.py`](geocode_cities.py) | US-013 |
| Komponist:innen & Werke (Metadaten) | Open Opus | [`import_openopus.py`](import_openopus.py) | US-017 |
| Komponist:innen (Wikipedia-Quellen sammeln) | Wikipedia (de) | [`fetch_wikipedia_composers.py`](fetch_wikipedia_composers.py) | US-017 |
| Komponist:innen (volle Wikipedia-Intros) | Wikipedia (de) | [`fetch_wikipedia_intros.py`](fetch_wikipedia_intros.py) | US-017 |
| Komponist:innen (kuratierte Kurzfassungen eintragen) | – | [`apply_wikipedia_composers.py`](apply_wikipedia_composers.py) | US-017 |
| Komponist:innen-Portraits (Download) | Wikipedia / Wikimedia Commons | [`fetch_composer_portraits.py`](fetch_composer_portraits.py) | US-024 |

`import_openopus.py` ergänzt `data/composers.json` und `data/works.json` um die externe
`openOpusId`, die deutschsprachige `epoch` sowie die Werk-Kennzeichen `popular`/`recommended`
und – wo lokal leer – Werkverzeichnis-Nummern. Kuratierte Felder (`wikipedia`, `description`,
`title`, bestehende `catalogue`/`life`) werden **nicht** überschrieben; ein erneuter Lauf ist
idempotent. Lebensdaten werden gegen Open Opus abgeglichen und Abweichungen nur reportet.
Open Opus ist **keine Laufzeitabhängigkeit** – der Abruf passiert ausschließlich beim
manuellen Skriptlauf und wird lokal (gitignoriert) gecacht.

### Wikipedia-Kurzfassungen (Ablauf)

Die kuratierten `wikipedia`-Kurzfassungen der Komponist:innen entstehen in vier Schritten
(alle Netzzugriffe rate-limitiert auf max. 1 Request/Sekunde und lokal gecacht):

1. `fetch_wikipedia_composers.py` – ermittelt je Komponist:in den passenden de-Wikipedia-Artikel
   (Titel/URL) und legt Kandidaten unter `.cache/wikipedia/candidates.json` ab. Fehltreffer
   (Listen-/Chronikseiten, gleichnamige andere Personen) sind über `NO_ARTICLE_IDS`/`TITLE_OVERRIDES`
   ausgeschlossen bzw. korrigiert.
2. `fetch_wikipedia_intros.py` – ergänzt je Kandidat:in den vollständigen Einleitungsabschnitt als
   Recherchegrundlage.
3. Redaktion – aus den Quellen werden **eigenständig formulierte** Kurzfassungen (~60 Wörter, kein
   wörtlicher Auszug) erstellt und als `{ composerId: { summary, url } }` gesammelt.
4. `apply_wikipedia_composers.py <kuratierung.json>` – schreibt die Kurzfassungen ordnungserhaltend
   und ohne Überschreiben bestehender Einträge in `data/composers.json`.

## Datenquellen / Attributierung

- **Open Opus** ([openopus.org](https://openopus.org)) – strukturierte Komponist:innen- und
  Werk-Metadaten. Die Daten stehen unter **CC0 / Public Domain**; eine Namensnennung ist
  rechtlich nicht erforderlich. Klangland nennt Open Opus dennoch **freiwillig aus
  Transparenz- und Fairnessgründen** als Quelle. Herkunft je Datensatz maschinenlesbar über
  das Feld `openOpusId`.
- **Wikipedia** – Grundlage der kuratierten Kurzfassungen (`wikipedia.summary`, ~60 Wörter,
  eigenständig formuliert, kein wörtlicher Auszug). Der Quellennachweis je Kurzfassung steckt
  in `wikipedia.url` (verlinkter Artikel).
- **Komponist:innen-Portraits** (Wikipedia / Wikimedia Commons) – mit
  [`fetch_composer_portraits.py`](fetch_composer_portraits.py) recherchiert das führende
  Artikelbild, lädt eine auf 400 px Breite begrenzte Variante herunter und legt sie als
  committetes Projekt-Asset unter [`data/portraits/`](../../data/portraits) ab (Single Source of
  Truth; via [`sync-data.mjs`](../../web/tools/sync-data.mjs) nach `web/public/portraits/`
  gespiegelt, dort gitignored). Zu jedem Bild werden `portrait.source` (Commons-Dateiseite als
  Attribution-Ziel) und – sofern leicht ermittelbar – `portrait.credit` (Urheber/Lizenz aus den
  Commons-Metadaten) gepflegt. Die Lizenzfrage ist bei dieser Quelle in der Regel geklärt. Die
  Webanwendung bindet **ausschließlich** lokale Dateien ein und ruft zur Laufzeit **keine**
  Fremd-URLs für Bilder ab; die Attribution ist in der UI bei jeder Bildanzeige sichtbar
  (Komponist:innen-Detailseite). Netzzugriffe sind auf **max. 1 Request/Sekunde** gedrosselt
  (Metadaten und Download) und lokal unter `.cache/portraits/` gecacht.

Der Open-Opus-Credit inkl. Link sowie der Wikipedia-/Wikimedia-Commons-Hinweis sind seit US-024
an einer für Nutzer:innen erreichbaren Stelle (Footer der Webanwendung) sichtbar. Die
Bild-Attribution je Portrait erfolgt zusätzlich direkt an der Bildanzeige.

### Bekannte Lebensdaten-Abweichungen Open Opus ↔ Klangland

Der Importer gleicht Lebensdaten gegen Open Opus ab und überschreibt sie **nicht**, sondern
protokolliert Abweichungen (AK 2). Bei den folgenden Datensätzen sind die Open-Opus-Werte
fehlerhaft; Klangland behält die geprüften lokalen Werte:

| Komponist:in | Klangland | Open Opus | Bewertung |
| --- | --- | --- | --- |
| Clara Schumann | 1819–1896 | 1810–1856 | Open Opus falsch (verwechselt mit Robert Schumann) |
| Michael Haydn | 1737–1806 | 1732–1809 | Open Opus falsch (verwechselt mit Joseph Haydn) |
| Frank Martin | 1890–1974 | 1890–1959 | Open Opus falsches Sterbejahr |

## Konventionen

- Zielschema und Beziehungen: [`../data-model.md`](../data-model.md),
  [`../events-and-relations.md`](../events-and-relations.md).
- Je Aufführungstermin ein Event; Referenzen ausschließlich über IDs.
- IDs in `kebab-case`; Transliteration deutscher Umlaute (`ä→ae`, `ö→oe`, `ü→ue`,
  `ß→ss`), sonstige Diakritika werden entfernt.
- Nach jedem Ingest: referenzielle Integrität, ID-Eindeutigkeit sowie Datums-/
  Zeitformate prüfen.
