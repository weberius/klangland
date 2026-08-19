# Events und Beziehungen

> Teil des Datenmodells. Die übergreifenden Konventionen und alle anderen Datenobjekte
> sind in [`data-model.md`](data-model.md) dokumentiert. Dieses Dokument beschreibt die
> Event-Entität sowie die Werk-/Programm-Trennung; die Werkstammdaten selbst stehen in
> [`entities/composers-and-works.md`](entities/composers-and-works.md).

## Zweck

Ein Event beschreibt eine konkrete Aufführung zu einem konkreten Zeitpunkt an einem konkreten Ort. Es ist kein Stammdatensatz für ein Ensemble, eine Spielstätte oder ein Werk.

Die erste Event-Datei enthält bewusst Beispieldaten. Die Quellen verwenden `example.org` und dürfen nicht als recherchierte Konzerttermine verstanden werden.

## Entitäten

```text
Person ── wird eingesetzt als ── Dirigent:in / Solist:in
Ensemble ── spielt ── Event ── findet statt in ── Venue
City ── beschreibt den Ort ── Event
Event ── enthält ── Programmpunkte ── referenzieren ── Work
Institution ── betreibt/verantwortet ── Venue oder Ensemble
Work ── wurde geschrieben von ── Composer
```

Die Stammdaten liegen in getrennten Dateien:

- `data/people.json`
- `data/institutions.json`
- `data/ensembles.json`
- `data/venues.json`
- `data/cities.json`
- `data/composers.json`
- `data/works.json`
- `data/events.json`

Events referenzieren diese Objekte ausschließlich über IDs. Namen werden nicht zusätzlich im Event gespeichert. Dadurch kann beispielsweise der Name einer Spielstätte zentral korrigiert werden, ohne historische Events zu ändern.

## Ein Event ist eine Aufführung

Mehrere Aufführungstermine mit gleichem Programm werden als mehrere Events angelegt:

```text
02.10.2026, 19:30, Tonhalle Düsseldorf -> eigenes Event
03.10.2026, 19:30, Tonhalle Düsseldorf -> eigenes Event
```

Das erlaubt unterschiedliche Uhrzeiten, Spielstätten, Besetzungen und Statuswerte. Ein Sammelfeld wie `dates` wird deshalb nicht verwendet.

## Felder

| Feld | Bedeutung |
| --- | --- |
| `id` | stabile, interne Klangland-ID |
| `title` | sichtbarer Veranstaltungs- oder Programmtitel |
| `eventType` | zunächst `concert`, später z. B. `opera` oder `festival` |
| `date` | Aufführungstag im Format `YYYY-MM-DD` |
| `startTime` / `endTime` | lokale Uhrzeit im Format `HH:MM` |
| `status` | z. B. `scheduled`, `cancelled`, `postponed` oder `rescheduled` |
| `ensembleIds` | ein oder mehrere auftretende Ensembles |
| `venueId` | konkrete Spielstätte |
| `cityId` | eigenständige Ortsreferenz, auch für Open-Air-Orte ohne klassisches Venue |
| `conductorPersonIds` | dirigierende Personen |
| `soloistPersonIds` | solistische Personen |
| `program` | geordnete Programmpunkte; Reihenfolge entspricht dem Konzertprogramm |
| `program[].workId` | Referenz auf ein Werk in `works.json` |
| `program[].movement` / `movements` | optional aufgeführter Satz oder Sätze |
| `program[].version` | optional aufgeführte Fassung |
| `seriesId` | vorbereitete Referenz auf eine spätere Reihen-Entität |
| `source` | Herkunftsobjekt mit `url`, `calendarUrl`, `name` und `retrievedAt` |
| `source.url` | konkrete Veranstaltungsseite des Events (Pflicht) |
| `source.calendarUrl` | Kalender-/Übersichtsseite, über die das Event recherchiert wurde; darf `null` sein |
| `source.name` | Organisation bzw. Anbieter der primären Quelle |
| `source.retrievedAt` | Datum des letzten Abrufs bzw. der Recherche |
| `lastVerified` | letzte fachliche Prüfung des Events |
| `ticketUrl` | optionaler direkter Ticketlink, sofern vorhanden |

Ein `source`-Objekt sieht damit z. B. so aus:

```json
{
  "url": "https://www.koelner-philharmonie.de/de/konzerte/aufbruch-marie-jacquot-yulianna-avdeeva/9250",
  "calendarUrl": "https://www1.wdr.de/orchester-und-chor/sinfonieorchester/konzerte/termine",
  "name": "Kölner Philharmonie",
  "retrievedAt": "2026-08-17"
}
```

## Werke und Programm

Werkdaten und Aufführungsdaten werden strikt getrennt. `works.json` beantwortet die Frage „Was ist das Werk?“, `events.json` die Frage „Wann und wie wird es aufgeführt?“. Ein Werk kann deshalb in beliebig vielen Events vorkommen.

```json
{
  "workId": "mahler-sinfonie-3",
  "movement": null,
  "version": null
}
```

Die Reihenfolge im `program`-Array ist verbindlich. Einzelne Sätze werden im Event angegeben, weil die konkrete Aufführung nur einen Teil eines Werkes enthalten kann. Katalognummern und Komponist:innen bleiben im Werk beziehungsweise in `composers.json`.

## Werkstammdaten

Ein Werk enthält keine Termine, Spielstätten oder Ensembles:

```json
{
  "id": "mahler-sinfonie-3",
  "composerId": "gustav-mahler",
  "title": "Sinfonie Nr. 3 d-Moll",
  "catalogue": [],
  "yearComposed": { "from": 1893, "to": 1896 },
  "genre": "symphony",
  "durationMinutes": 95,
  "version": null,
  "scoring": null,
  "description": null
}
```

`genre` ist ein kontrollierter Wert, zum Beispiel `symphony`, `concerto`, `overture`, `opera`, `oratorio`, `requiem`, `chamber_music` oder `other`. Katalogangaben werden als Liste modelliert, weil ein Werk mehrere Systeme haben kann.

## Pflege und Validierung

Das Datenpflegewerkzeug soll mindestens prüfen:

- eindeutige Event-IDs;
- gültige ISO-Daten und `HH:MM`-Uhrzeiten;
- vorhandene Referenzen auf Ensembles, Venues, Cities und Personen;
- erlaubte Status- und Eventtypwerte;
- vorhandene Quelle und `lastVerified`; `source.url` ist Pflicht, `source.calendarUrl` ist optional (`null` zulässig);
- keine versehentliche Zusammenfassung mehrerer Aufführungen in einem Event.

Abgesagte oder verschobene Veranstaltungen werden nicht gelöscht. Ihr Status wird aktualisiert, damit die Änderungshistorie über Git nachvollziehbar bleibt.
