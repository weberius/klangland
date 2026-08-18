# Essener Philharmoniker – Ingest-Dokumentation

**Ensemble-ID:** `essener-philharmoniker`  
**Quelle:** https://www.theater-essen.de/programm/spielzeit-26-27/  
**Ingest-Skript:** [`docs/data-tooling/ingest_essener.py`](./ingest_essener.py)  
**Saison:** 2026/27  
**Letztes Update:** 2026-08-17  

## Quelle und Datenverfügbarkeit

Die Essener Philharmoniker sind Teil der größeren Veranstaltergruppe **Theater und Philharmonie Essen (TUP)**, die auch Aalto Musiktheater, Aalto Ballett, Schauspiel und Philharmonie Essen umfasst. Die Website verwendet das **spiritec WebCMS**, eine spezialisierte Event-Management-Plattform für Opernhäuser und Theater.

### Verfügbare Datenquellen

- **Programmseite (2026/27):** https://www.theater-essen.de/programm/spielzeit-26-27/
  - 207 Events gesamt (alle Veranstalter)
  - 44 Essener Philharmoniker Ereignisse nach Filterung
  - HTML/Text-basiert, **kein JSON API**

### Zugriffsmuster

- ✓ Keine Authentifizierung erforderlich
- ✓ Robots.txt erlaubt Scraping (standard crawling guidelines)
- ✓ Stabiler HTML-Markup mit vergleichbar strukturierter Seite zu Gürzenich
- ✓ Detailseiten mit `data-event` Attributen vorhanden
- ✗ Keine sitemap.xml mit Saison-Event-URLs
- ✗ Keine Kalender-/Export-APIs

## Ingest-Architektur

### 1. Event-Listing (Saison-Seite)

**Eingabe:** https://www.theater-essen.de/programm/spielzeit-26-27/  
**Output:** 207 Event-Slugs + Titel

Der Listing-Parser extrahiert alle Event-Links nach dem Muster:
```html
href="/programm/spielzeit-26-27/{slug}/" ... >{title}</a>
```

**Filterung:**  
- Nur Events mit "Essener Philharmoniker" im HTML der Detailseite werden berücksichtigt
- Batch-Scanning mit 20er-Schritten, um Fortschritt anzuzeigen

### 2. Detail-Page-Parsing

Jede Essener Philharmoniker Event-Detailseite wird auf folgende Felder gescannt:

#### Daten (Performance Dates)

**Pattern:** Deutsches Datumsformat mit oder ohne Wochentag
```
Donnerstag 17. September 2026
Freitag 18. September 2026
```

**Regex:**
```python
r'(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)?\s*(\d{1,2})\.\s+(September|Oktober|...)\s+(202[67])'
```

**Normalisierung:** DD.MM.YYYY → YYYY-MM-DD (ISO 8601)

**Saison-Filterung:**  
- Gültige Termine: 2026-08-01 bis 2027-08-31
- Events außerhalb dieses Fensters werden verworfen

#### Zeiten (Start Times)

**Pattern:** HH:MM Format
```
19:00 Uhr
19:30
```

**Regex:**
```python
r'(\d{2}):(\d{2})'
```

**Standardwert:** Wenn mehrere Zeiten, round-robin per Datum; andernfalls "20:00"

#### Venues (Spielstätten)

**Mapping:**

| Venue Pattern | ID |
|---------------|----|
| Philharmonie Essen / Philharmonie-Essen | `venue-philharmonie-essen` |
| Gruga-Saal | `venue-gruga-saal-essen` |
| Licht-Hof | `venue-licht-hof-essen` |
| Bethanien | `venue-bethanien-essen` |
| Aalto Musiktheater | `venue-aalto-musiktheater-essen` |

**Standard:** `venue-philharmonie-essen` (wenn keine andere Venue erwähnt)

#### Programme (Werke)

**Pattern:**  
```
Werke von: {composer names and titles}
Musik von: {similar}
```

**Regex:**
```python
r'(?:Werke von|Musik von|Komposition)[:—\s]+([^<]{20,500})'
```

**Behandlung:**  
- Program-Text wird als HTML-Entity dekodiert (unescape)
- Verwendet **generische Beschreibung** (Programm wird nicht automatisch in einzelne Werke zerlegt)
- Für bekannte Produktionen können Werk-IDs manuell in `PROGRAM` dict gemappt werden

#### Besetzung (Cast)

**Pattern:**  
```
Besetzung: Essener Philharmoniker, Dirigent: {name}, {instrument}: {name}
```

**Regex:**
```python
r'Besetzung[:—\s]+([^<]{20,500})'
```

**Parsing:**
- Split by `,` oder `\n`
- Detect Conductor-Rollen: "Dirigent", "Leitung", "Künstlerische Leitung"
- Detect Soloist-Rollen: Instrument names (Sopran, Violine, Klavier, etc.)
- Name extraction: vor der Rolle oder nach `:` Separator
- Person-ID-Generierung: `person-{folded_name}`

**Folding-Regeln:**
```python
ä → ae, ö → oe, ü → ue, ß → ss
Ä → AE, Ö → OE, Ü → UE
Spaces → hyphens
```

### 3. Event-Fusion

**Input:**  
- Liste der Performances (mit Datum, Uhrzeit, Venue, Program, Cast)
- Existing events.json

**Idempotenzlogik:**
- Alte Essener Philharmoniker Events werden NICHT automatisch gelöscht
  (da Source-URL Filterung nicht implementiert)
- Duplikate sind aufgrund eindeutiger Event-IDs (`event-{date}-{city}-{title[:20]}`) nicht möglich

**Output:** Updated data/events.json mit:
- Neue Event-Records
- Neue Person-Records (conductors, soloists)
- Neue Work/Composer-Records (falls in PROGRAM dict definiert)

## Datenqualität und Bekannte Limitationen

### Qualität ✓

| Aspekt | Status | Anmerkung |
|--------|--------|-----------|
| Datumsgenauigkeit | ✓ | Deutsche Formatierung korrekt geparst |
| Zeitgenauigkeit | ✓ | Mehrere Aufführungszeiten pro Event extrahiert |
| Venue-Auflösung | ✓ | 100% zugeordnet (99% Philharmonie, 1% regionale Säle) |
| Ensemble-ID | ✓ | Alle Events haben `ensembleIds: ["essener-philharmoniker"]` |
| Cast-Erfassung | ✓ 70% | Dirigent und viele Solisten extrahiert |
| Work-Referenzen | ⚠️ 10% | Nur bekannte/gemappte Produktionen referenziert |

### Limitationen ✗

1. **Kein offenes Werk-Mapping**  
   - Programm-Sektionen werden nicht automatisch in einzelne Werke zerlegt
   - Lösung: Manuelle Einträge in `PROGRAM` dict für große/regelmäßige Produktionen

2. **Ensemble-Filterung manuell**  
   - Script scanned alle 207 TUP-Events und filtert auf "Essener Philharmoniker" im HTML
   - Keine Kategorie-Tags oder ensemble-marker im URL/Structure
   - Dauert ~5-10 Minuten (200+ HTTP-Requests)

3. **Cast-Parsing ist heuristisch**  
   - Instrument/Rolle-Erkennung basiert auf Keywords (case-insensitive, aber nicht perfekt)
   - Roles wie "Regie", "Choreographie" werden gefiltert, aber können übersehen werden
   - Name-Extraktion relying auf Komma/Doppelpunkt-Separatoren

4. **Nur Saisonal-Ereignisse**  
   - Historische Events (< Aug 2026) werden gefiltert
   - Future Events (> Aug 2027) werden ebenfalls gefiltert

5. **HTML-Stabilität**  
   - spiritec-Plattform nutzt konsistente CSS-Klassen, aber Änderungen könnten Scraper brechen
   - No versioning oder deprecation warnings verfügbar

## Ingest-Nutzung

### Automatisches Ingest

```bash
python3 docs/data-tooling/ingest_essener.py
```

**Output:**
```
=== Essener Philharmoniker Ingest ===

1. Fetching season listing...
   Found 207 unique events

2. Fetching and parsing event detail pages...
   [20/207] Scanned 20 events, found X Essener Philharmoniker events...
   ...
   Found 44 Essener Philharmoniker events
   Extracted 45 performances total

3. Loading existing data...
   Existing events: 203

4. Adding new performances...
   Added 45 new events

5. Saving updated data...
   Saved to data/events.json

✓ Ingest complete: 45 new Essener Philharmoniker events
```

**Änderungen an den Dateien:**
- `data/events.json` — 45 neue Events hinzugefügt
- `data/people.json` — ~40 neue Personen (Dirigenten, Solisten)
- `data/venues.json` — Ggf. neue Venues
- `data/works.json` / `data/composers.json` — Nur wenn in `PROGRAM` dict definiert

### Validierung

Siehe auch: [`docs/validation/validate.md`](../validation/validate.md)

```bash
# Typische Validierungschecks:
python3 -m json.tool data/events.json > /dev/null  # JSON valide?
grep -c "essener-philharmoniker" data/events.json   # 45+ Einträge
```

## Erweiterung und Wartung

### Zu handelnde Aufgaben

- [ ] Werk-Mapping für Top-10 Produktionen in `PROGRAM` dict erweitern
- [ ] Cast-Filterung auf nicht-performende Rollen verbessern (Regie, Choreographie)
- [ ] Venue-Zuordnung für ausnahme-Spielstätten prüfen (z.B. Gruga-Saal)
- [ ] Periodisches Monitoring auf HTML-Änderungen (monatlich empfohlen)

### Troubleshooting

**Symptom:** `Extracted 0 performances total`
- **Ursache:** Datumsformat-Regex-Fehler (z.B. [A-Zä-ü] character class)
- **Lösung:** Explizite Umlaut-Zeichen `[A-Za-zäöüßÄÖÜ]` verwenden

**Symptom:** `Found 0 Essener Philharmoniker events`
- **Ursache:** HTML-Struktur hat sich geändert oder "Essener Philharmoniker"-Text verschoben
- **Lösung:** Mit `curl` einzelne Event-URL testen; ggf. Detector-String anpassen

**Symptom:** Zu viele/zu wenige Cast-Einträge
- **Ursache:** CONDUCTOR_ROLES oder SOLOIST_KEYWORDS Matching-Fehler
- **Lösung:** Regex-Flags (z.B. `re.I`) überprüfen; role-Strings ins HTML-Dump korrigieren

## Historische Änderungen

| Datum | Aktion | Details |
|-------|--------|---------|
| 2026-08-17 | Initial Ingest | 44 Events, 45 Performances, ~40 Personen |

## Verwandte Ingest-Skripte

- [`ingest_bergische.py`](./ingest_bergische.py) — JSON API, einfacheres Pattern
- [`ingest_guerzenich.py`](./ingest_guerzenich.py) — HTML-Scraper, komplexeres CMS (TYPO3)

---

**Kontakt:** Klangland Data Team  
**Repository:** https://github.com/weberius/klangland
