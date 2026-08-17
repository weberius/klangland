# Daten-Ingest: Gürzenich-Orchester Köln (Spielzeit 2026/27)

Dieses Dokument beschreibt, wie der Spielplan des **Gürzenich-Orchesters Köln** für die
Spielzeit 2026/27 recherchiert und in die versionierten JSON-Dateien unter
[`data/`](../../data) übernommen wurde. Skript daneben:
[`ingest_guerzenich.py`](ingest_guerzenich.py).

Siehe auch das übergreifende Datenmodell in [`data-model.md`](../data-model.md) und die
Event-Regeln in [`events-and-relations.md`](../events-and-relations.md).

## Quelle

- **Website:** `https://www.guerzenich-orchester.de/de/programm` (TYPO3-CMS, serverseitig
  gerendert, keine offene JSON-API).
- **Kanonische Eventliste:** die Events-Sub-Sitemap
  `https://www.guerzenich-orchester.de/de/sitemap.xml?sitemap=events`.
- **Detailseiten:** `https://www.guerzenich-orchester.de/de/event-detail/<slug>` — wird je
  Event als `source.url` gespeichert.

Anders als bei den [Bergischen Symphonikern](bergische-symphoniker.md) gibt es keine
JSON-API. Das Skript liest daher die HTML-Detailseiten und extrahiert die strukturierten
Blöcke `m-event__title`, `m-event__categories`, `m-event__date-day`, die Programmliste
`m-program`, die Besetzung `m-event__occupation` und die Termine `m-event-dates`.

## Datenfluss

```text
sitemap.xml?sitemap=events           (kanonische Slugs)
          ↓
/de/event-detail/<slug>  (HTML je Event parsen)
          ↓
Termine + Besetzung + Kategorie + Datumskopf → Zwischenrepräsentation
          ↓  (Kuratierung + Mapping, siehe unten)
data/events.json (+ works/composers/people/venues)
          ↓
Validierung (referenzielle Integrität, IDs, Formate)
```

## Saison-Erkennung

Vergangene Veranstaltungen (Spielzeiten bis einschließlich 2025/26) blenden auf ihren
Detailseiten **keine buchbaren Termine** mehr ein. Das Skript berechnet für jede
Aufführung aus `Tag.Monat` plus der Jahresangabe im Datumskopf ein ISO-Datum und behält
nur Events, deren erster Termin im Fenster **2026-08-01 … 2027-08-01** liegt. So ergeben
sich genau die 44 Produktionen (83 Termine) der Spielzeit 2026/27.

## Umfang und Tiefe

- **Umfang:** maximal — alle 44 Veranstaltungen inkl. Sinfonie-, Kammer-, Familien- und
  Schulkonzerten, „Bock auf Klassik", Passions-/Benefiz-/Sonderkonzerten sowie
  Formaten ohne veröffentlichtes Programm (PhilharmonieProbe, Musikalischer Frühschoppen).
  Je Termin ein eigenes Event.
- **Stammdaten-Tiefe (Option B, angereichert):** Werke/Komponist:innen mit Lebensdaten,
  Kompositionsjahr, Genre und ungefährer Dauer. Da die Programm-HTML mehrere Werke pro
  Komponist:in verschachtelt und teils verrauscht ist, ist die **Programmzuordnung je
  Event kuratiert** hinterlegt (`PROGRAM`: Slug → geordnete Werk-IDs), statt sie
  vollautomatisch zu parsen. Werke werden mit `works.json` wiederverwendet, wo sie schon
  existieren (z. B. Saint-Saëns' Orgelsinfonie, Rachmaninows 2. Klavierkonzert,
  Tschaikowskys „Roméo et Juliette", Strauss' „Zarathustra", Brahms' 1. Sinfonie,
  Bruckners 7. Sinfonie, Schuberts Streichtrio D 581).

## Mapping-Regeln

### Spielstätten (`venue_id`, `NEW_VENUES`)

Alle Termine liegen in Köln. `Kölner Philharmonie` referenziert die bestehende Venue
`koelner-philharmonie`. Neu angelegt werden `kammermusiksaal-kartaeuserwall-koeln`
(`concert_hall`) sowie `rheinische-musikschule-koeln`, `buergerzentrum-engelshof-koeln`
und `belgisches-haus-koeln` (jeweils `type: other`, `institutionId: null`).

### Besetzung (`cast` → Personen)

| Quell-Rolle | Zielfeld |
| --- | --- |
| enthält `Dirigent…` oder `Leitung` | `conductorPersonIds` |
| Instrument/Stimme (`Sopran`, `Tenor`, `Klavier`, `Violine`, `Orgel`, `Oud`, `Sprecher`, …) | `soloistPersonIds` |
| `… und Leitung` (z. B. „Oboe und Leitung") | beides (Dirigat **und** Solist) |
| `Moderation`, `Künstlerische Leitung`, `Ko-Moderation` | verworfen |
| Chöre, Orchester, Ensembles, `N.N.` | verworfen |

Die Rollenerkennung ist bewusst case-insensitiv, damit auch großgeschriebene
Rollenanfänge (`Sopran`, `Klavier`, …) korrekt als Solistik erkannt werden. Personen
werden über [`people.json`](../../data/people.json) per Name dedupliziert; neue IDs
entstehen durch Transliteration (`fold()`).

### Programm (`PROGRAM` → Werke)

- Pro Event eine geordnete Liste kuratierter Werk-IDs. Neue Werke stehen mit
  angereicherten Metadaten in `NEW_WORKS`, neue Komponist:innen mit Lebensdaten in
  `NEW_COMPOSERS`.
- Events mit generischer Ansage („Programm wird noch bekannt gegeben", „Mit Musik von …")
  oder reine Proben/Matineen bekommen **kein** Programm; der Hinweistext landet in der
  Event-`description` (`DESC_NOTES`).

### Event-Felder

- `eventType`: durchgehend `concert` (die konzertante „Lulu" in der Sinfoniekonzert-Reihe
  wird als `concert` geführt, nicht als `opera`).
- `id`-Konvention: `event-<YYYY-MM-DD>-koeln-<titel-slug>`, bei Kollision um Uhrzeit bzw.
  Zähler ergänzt.
- `source.url` = Detailseite; `ticketUrl` aus dem Termin-Block; `status` = `scheduled`.

## Ausführen

```bash
# Live-Scrape der Website (self-contained)
python docs/data-tooling/ingest_guerzenich.py

# Reproduzierbar aus gespeicherter, geparster Saison-JSON und mit festem Datum
python docs/data-tooling/ingest_guerzenich.py --raw season.json --date 2026-08-17
```

Ohne `--raw` liest das Skript Sitemap und Detailseiten direkt; mit `--raw` eine zuvor
geparste Liste (Events mit `performances` inkl. `date`/`startTime`). Pfade werden relativ
zum Skript aufgelöst; geschrieben wird nach `data/*.json` inkl. `metadata.lastUpdated`.

### Idempotenz

Der Lauf entfernt zunächst alle zuvor eingespielten Gürzenich-Events (erkannt am
Quell-Host `guerzenich-orchester.de` in `source.url`) und legt sie neu an. Stammdaten
werden anhand ihrer IDs zusammengeführt und nicht dupliziert.

## Validierung

Ergebnis: **83 Events** (44 Produktionen), 76 Werke (davon 68 neu), 26 neue
Komponist:innen, ~90 Personen, 4 neue Spielstätten – 0 Validierungsfehler, keine
verwaisten Personen/Komponist:innen. Geprüft wurden eindeutige IDs, gültige
`YYYY-MM-DD`/`HH:MM`-Werte, auflösbare Referenzen sowie kontrollierte Werte für
`eventType`, `status`, `genre` und `venue.type`.

## Bekannte Einschränkungen

- Werke ohne gesicherte Daten (Auftrags-/Uraufführungen wie das „Neue Werk" von Matthias
  Pintscher oder Oskar Jockels Akademie-Auftragswerk) haben `durationMinutes` und teils
  `yearComposed` als Näherung bzw. `null`.
- Bei Konzerten mit generischer Programmansage bleibt `program` leer; die Angaben stehen
  in der `description`.
- Adressen/Koordinaten neuer Spielstätten sind noch nicht recherchiert (`null`).
