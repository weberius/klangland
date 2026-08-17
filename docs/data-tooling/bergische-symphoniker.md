# Daten-Ingest: Bergische Symphoniker (Spielzeit 2026/27)

Dieses Dokument beschreibt, wie der Spielplan der **Bergischen Symphoniker** für die
Spielzeit 2026/27 recherchiert und in die versionierten JSON-Dateien unter
[`data/`](../../data) übernommen wurde. Das zugehörige Skript liegt daneben:
[`ingest_bergische.py`](ingest_bergische.py).

Es ergänzt die in [`data-model.md`](../data-model.md) und
[`events-and-relations.md`](../events-and-relations.md) beschriebene Datenbasis um
konkrete Aufführungen und die dafür nötigen Stammdaten (Werke, Komponist:innen,
Personen, Spielstätten, Städte).

## Quelle

- **API:** `https://bergischesymphoniker.de/api/concerts?limit=200&depth=2`
  (Payload-CMS-JSON-Endpunkt der offiziellen Website).
- **Öffentliche Konzertseiten:** `https://bergischesymphoniker.de/konzerte/<slug>` —
  wird als `source.url` je Event gespeichert.
- **Saisonfilter:** nur Dokumente mit `season.title == "2026/27"`.

Ein Konzert-Dokument der API liefert u. a. `title`, `subtitle`, `slug`, `categories`,
`performances` (Termine mit `dateTime`, `venue`, `ticketUrl`), `program`
(`composer`, `workTitle`, `opus`) und `cast` (`name`, `role`).

## Datenfluss

```text
bergischesymphoniker.de/api/concerts
          ↓  (Saison 2026/27 filtern, flach machen)
Zwischenrepräsentation (title, performances, program, cast)
          ↓  (Kuratierung + Mapping, siehe unten)
data/events.json (+ works/composers/people/venues/cities)
          ↓
Validierung (referenzielle Integrität, IDs, Formate)
```

## Umfang und Tiefe

- **Umfang:** maximal — alle Kategorien werden übernommen (Philharmonische, Sonder-,
  Familien-, Kammer- und Meisterkonzerte, Musiktheater, „Orchester unterwegs", ON FIRE!,
  Schulkonzerte). Es entsteht **je Aufführungstermin ein eigenes Event** (kein
  Sammelfeld), konform zu [`events-and-relations.md`](../events-and-relations.md).
- **Stammdaten-Tiefe (Option B, angereichert):** Die API liefert nur Komponistenname,
  Werktitel und teils Opus/Katalognummer. Lebensdaten, Kompositionsjahr, Genre und
  ungefähre Werkdauer werden im Skript **kuratiert ergänzt** (Dictionaries
  `NEW_COMPOSERS` und `WORKS`). Wo etwas unbekannt ist, bleibt das Feld `null`.

## Mapping-Regeln

### Spielstätten (`VENUE_MAP`, `NEW_VENUES`)

Quell-Bezeichnungen werden auf stabile Venue-IDs abgebildet. Die beiden Stammsäle in
Solingen werden als eigene Spielstätten geführt (`konzerthaus-solingen`,
`theater-solingen`), Remscheid als `teo-otto-theater`. Gastspielorte (Kirchen, Parks,
Schloss Burg, Museum, auswärtige Häuser) werden als neue Venues vom Typ `other`
angelegt; auswärtige Städte (`leverkusen`, `muelheim-an-der-ruhr`, `coesfeld`) kommen
als neue Einträge nach [`cities.json`](../../data/cities.json).

Für Gast-/Fremdspielstätten ist `institutionId` `null` (kein bekannter Träger). Der
zugehörige Typ in [`models.ts`](../../web/src/app/models/models.ts) und
[`venues.md`](../entities/venues.md) ist entsprechend `string | null`.

### Besetzung (`cast` → Personen)

| Quell-Rolle | Zielfeld |
| --- | --- |
| `Leitung…`, `Dirigent…` | `conductorPersonIds` |
| Instrument/Stimme (`Violine`, `Klavier`, `Sopran`, `Sprecher`, `Gesang`, `Texte und Rap`, …) | `soloistPersonIds` |
| `Inszenierung`, `Choreographie`, `Moderation`, `Einstudierung`, Chor/Ensemble, `N.N.` | verworfen |

Personen werden über [`people.json`](../../data/people.json) dedupliziert (Abgleich per
Name); neue IDs entstehen durch Transliteration (`fold()`: `ä→ae`, `ö→oe`, `ü→ue`,
`ß→ss`, Diakritika werden entfernt) — konsistent zu bestehenden IDs.

### Programm (`program` → Werke)

- Reale Werke werden in [`works.json`](../../data/works.json) angelegt bzw. wiederverwendet
  (Schlüssel: Quell-Komponist + Werktitel). Häufig gespielte Auszüge werden – wie im
  Bestand (`wagner-lohengrin-vorspiel-1-akt`) – als eigenes Werk modelliert.
- **Verrauschte Programm-Einträge** (Solistenname statt Werk, generische Angaben wie
  „Musik von Debussy, Ravel, Fauré") werden **nicht** als Werk angelegt, sondern in die
  Event-`description` übernommen (`NOISE`).
- Neue Komponist:innen werden mit Lebensdaten in
  [`composers.json`](../../data/composers.json) ergänzt.

### Event-Felder

- `eventType`: `concert`, für Opern (`La bohème`, `Der Vogelhändler`) `opera`.
- `date`/`startTime`: aus `performance.dateTime` (die CMS-Zeit wird als Ortszeit
  interpretiert).
- `id`-Konvention: `event-<YYYY-MM-DD>-<stadt>-<titel-slug>`, bei Kollision um Uhrzeit
  bzw. Zähler ergänzt.
- `source`: `{ url: konzertseite, name: "Bergische Symphoniker", retrievedAt: <datum> }`.
- `ticketUrl`, `lastVerified` werden gesetzt; `status` ist `scheduled`.

## Ausführen

```bash
# Live-Abruf der API
python docs/data-tooling/ingest_bergische.py

# Reproduzierbar aus gespeichertem API-Dump und mit festem Datum
python docs/data-tooling/ingest_bergische.py --raw dump.json --date 2026-08-17
```

Pfade werden relativ zum Skript aufgelöst; es schreibt direkt nach `data/*.json` und
aktualisiert `metadata.lastUpdated`.

### Idempotenz

Der Lauf entfernt zunächst alle zuvor eingespielten Bergische-Events (erkannt am
Quell-Host `bergischesymphoniker.de` in `source.url`) und legt sie neu an. Stammdaten
(Personen, Werke, Komponist:innen, Spielstätten, Städte) werden anhand ihrer IDs
zusammengeführt und nicht dupliziert. Mehrfaches Ausführen ist daher unkritisch.

## Validierung

Nach dem Ingest wurde geprüft:

- eindeutige IDs je Datei;
- gültige `YYYY-MM-DD`-Daten und `HH:MM`-Uhrzeiten;
- auflösbare Referenzen (Ensemble, Venue, City, Personen, Werke, Komponist:innen,
  Institution);
- kontrollierte Werte für `eventType`, `status`, `genre`, `venue.type`;
- `yearComposed` ist entweder `null` oder `{ from, to }` mit Ganzzahlen.

Ergebnis des Erstlaufs: **85 Events** (aus 46 Produktionen), 57 Werke, 29 neue
Komponist:innen, 49 Personen, 19 Spielstätten (17 neu) – 0 Validierungsfehler.

## Bekannte Einschränkungen

- Einzelne Werke ohne gesicherte Daten (z. B. zeitgenössische Auftragswerke) haben
  `yearComposed`/`durationMinutes` = `null`.
- Adressen und Koordinaten neuer Spielstätten sind noch nicht recherchiert (`null`),
  konsistent zum übrigen Bestand.
- Nicht-künstlerische Mitwirkende (Inszenierung, Moderation, Chor-Einstudierung) werden
  bewusst nicht als Personen erfasst, da das Modell nur Dirigat und Solistik kennt.
