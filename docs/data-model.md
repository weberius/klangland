# Datenmodell – Übersicht

Dieses Dokument ist die Klammer über alle Datenobjekte von Klangland. Es beschreibt
die gemeinsamen Konventionen, die vollständige Entitätenlandschaft und die
Beziehungen der Datenobjekte untereinander. Für jedes Objekt gibt es ein eigenes,
detailliertes Dokument (siehe [Entitäten](#entitäten)).

Zusammen mit [`events-and-relations.md`](events-and-relations.md) und dem
[PRD](product/prd.md) bildet diese Doku die Grundlage für die Erstellung von
App und Daten.

## Grundprinzipien

- **Getrennte Dateien:** Jede zentrale Entität besitzt eine eigene JSON-Datei unter `data/`.
- **Beziehungen nur über IDs:** Entitäten referenzieren einander ausschließlich über
  IDs. Namen oder andere Stammdaten werden nicht in referenzierenden Objekten dupliziert.
  Dadurch kann z. B. der Name einer Spielstätte zentral korrigiert werden, ohne
  historische Events zu ändern.
- **Single Source of Truth:** Die versionierten JSON-Dateien sind die maßgebliche
  Datenquelle. Die Webapp konsumiert ausschließlich geprüfte Daten und enthält keine
  Logik zur Datenbeschaffung.
- **Stammdaten vs. Ereignisdaten:** Stammdaten (Personen, Ensembles, Venues, Werke …)
  beschreiben zeitlose Eigenschaften. Ereignisdaten (`events.json`) beschreiben eine
  konkrete Aufführung zu einem konkreten Zeitpunkt.

## Metadaten-Umschlag

Jede Datei ist ein Objekt mit einem `metadata`-Feld und einem Array, das nach der
Entität benannt ist (`institutions`, `ensembles`, `venues`, …).

```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-08-17",
    "language": "de"
  },
  "ensembles": []
}
```

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `version` | ja | Schemaversion der Datei (`major.minor`). |
| `lastUpdated` | ja | Datum der letzten Änderung im Format `YYYY-MM-DD`. |
| `language` | ja | Sprachcode der textuellen Inhalte, aktuell `de`. |
| `season` | optional | Spielzeit, nur bei `events.json` relevant (z. B. `2026/27`). |
| `scope` / `notes` | optional | Freitext zur Einordnung des Datenbestands. |

## ID-Konventionen

- IDs sind stabil, intern und werden **nie** wiederverwendet oder inhaltlich verändert.
- Format: `kebab-case`, ASCII-transliteriert (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`).
  Beispiel: `Gürzenich-Orchester Köln` → `guerzenich-orchester-koeln`.
- Event-IDs folgen dem Muster `event-YYYY-MM-DD-<ort>-<kurztitel>` und sind ebenfalls stabil.
- IDs müssen innerhalb ihrer Datei eindeutig sein.

## Entitäten

| Datei | Array-Schlüssel | Objekt | Detaildoku |
| --- | --- | --- | --- |
| `data/people.json` | `people` | Personen (Dirigent:innen, Solist:innen) | [entities/people.md](entities/people.md) |
| `data/institutions.json` | `institutions` | Träger/Veranstalter | [entities/institutions.md](entities/institutions.md) |
| `data/ensembles.json` | `ensembles` | Orchester und andere Ensembles | [entities/ensembles.md](entities/ensembles.md) |
| `data/venues.json` | `venues` | Spielstätten | [entities/venues.md](entities/venues.md) |
| `data/cities.json` | `cities` | Orte/Städte | [entities/cities.md](entities/cities.md) |
| `data/composers.json` | `composers` | Komponist:innen | [entities/composers-and-works.md](entities/composers-and-works.md) |
| `data/works.json` | `works` | Werkstammdaten | [entities/composers-and-works.md](entities/composers-and-works.md) |
| `data/events.json` | `events` | Aufführungen/Veranstaltungen | [events-and-relations.md](events-and-relations.md) |

Wie Spielpläne recherchiert und in diese Dateien übernommen werden, ist im
[Daten-Tooling](data-tooling/README.md) dokumentiert (Ingest-Skripte je Quelle).

## Beziehungen

```text
Institution ──< betreibt/verantwortet >── Venue
Institution ──< trägt >── Ensemble
Institution ── sitzt in ── City(s)
Person ──< leitet (Chefdirigent:in) >── Ensemble
Ensemble ── hat Stammsaal ── Venue
Ensemble ── sitzt in ── City(s)
Venue ── liegt in ── City(s)
Composer ──< schrieb >── Work

Event ──> Ensemble(s)        (ensembleIds)
Event ──> Venue              (venueId)
Event ──> City               (cityId)
Event ──> Person(en)         (conductorPersonIds, soloistPersonIds)
Event ──> Work(e)            (program[].workId)
```

Alle Ortsbezüge laufen über `cities.json`: Events über `cityId`, Institutionen, Ensembles
und Venues über `cityIds`. Übergeordnete Regionen (z. B. `Ruhrgebiet`) sind keine Cities,
sondern stehen im Freitextfeld `region`. Siehe [Ortsbezug](#ortsbezug).

## Referenz-Matrix

Welches Feld in welcher Datei zeigt auf welche Entität:

| Quelle (Datei · Feld) | Ziel-Entität | Kardinalität |
| --- | --- | --- |
| `institutions` · `ensembleIds[]` | `ensembles.id` | 1 Institution → n Ensembles |
| `institutions` · `cityIds[]` | `cities.id` | 1 Institution → n Cities |
| `ensembles` · `chiefConductorPersonId` | `people.id` | 1 Ensemble → 1 Person |
| `ensembles` · `venueId` | `venues.id` | 1 Ensemble → 1 Stammsaal |
| `ensembles` · `cityIds[]` | `cities.id` | 1 Ensemble → n Cities |
| `venues` · `institutionId` | `institutions.id` | 1 Venue → 1 Institution |
| `venues` · `cityIds[]` | `cities.id` | 1 Venue → 0..n Cities |
| `works` · `composerId` | `composers.id` | 1 Werk → 1 Komponist:in |
| `events` · `ensembleIds[]` | `ensembles.id` | 1 Event → n Ensembles |
| `events` · `venueId` | `venues.id` | 1 Event → 1 Venue |
| `events` · `cityId` | `cities.id` | 1 Event → 1 City |
| `events` · `conductorPersonIds[]` | `people.id` | 1 Event → n Personen |
| `events` · `soloistPersonIds[]` | `people.id` | 1 Event → n Personen |
| `events` · `program[].workId` | `works.id` | 1 Programmpunkt → 1 Werk |
| `events` · `seriesId` | *(Reihen-Entität, noch nicht angelegt)* | vorbereitet |

Es gibt bewusst eine **Doppelbeziehung Institution ↔ Ensemble** (`ensembleIds` im
einen, kein Rückverweis im anderen) und **Venue ↔ Institution** (`institutionId`).
Die Validierung muss beide Richtungen konsistent halten (siehe unten).

## Ortsbezug

Ortsangaben sind vollständig normalisiert: `cities.json` ist die einzige Quelle für Orte.

- **Events** referenzieren genau einen Ort über `cityId`.
- **Institutionen, Ensembles und Venues** referenzieren ihre Sitzorte über `cityIds`
  (Array). Doppelsitze (z. B. Krefeld/Mönchengladbach, Duisburg/Düsseldorf) werden als
  mehrere Einträge abgebildet; Entitäten ohne festen Ort (z. B. wechselnde Spielstätten)
  können eine leere Liste `[]` führen.
- **Regionen** wie `Ruhrgebiet`, `Südwestfalen` oder `Bergisches Land` sind **keine**
  Cities. Sie stehen im optionalen Freitextfeld `region` der Stammdaten und werden nicht in
  `cities.json` aufgenommen.

Ein früher vorhandenes Freitextfeld `city` in den Stammdaten wurde durch `cityIds`
(+ `region`) ersetzt. Details: [entities/cities.md](entities/cities.md).

## Validierung (übergreifend)

Das geplante Python-Werkzeug (`nrw-orchester-data`, siehe PRD Abschnitt 16–17) soll
mindestens prüfen:

- eindeutige IDs pro Datei;
- gültige `metadata` (Version, `lastUpdated` als ISO-Datum);
- referenzielle Integrität aller Felder aus der [Referenz-Matrix](#referenz-matrix):
  jede referenzierte ID existiert in der Zieldatei;
- Konsistenz der Doppelbeziehungen (jede `institutions.ensembleIds`-Referenz existiert,
  jede `venues.institutionId`-Referenz existiert);
- kontrollierte Werte (`type`, `roles`, `musicalProfiles`, `genre`, `status`, `eventType`)
  liegen im erlaubten Wertebereich; die maßgeblichen Ensemble-Wertelisten (`type`, `roles`,
  `musicalProfiles`) stehen in [entities/ensembles.md](entities/ensembles.md);
- keine verwaisten Stammdaten werden hart gelöscht (nur als Warnung gemeldet).

Details zu den entitätsspezifischen Regeln stehen in der jeweiligen Detaildoku.
