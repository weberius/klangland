# Klangland

Eine schlanke, statische Datenplattform für Musikensembles, Spielstätten und Konzertveranstaltungen in Nordrhein-Westfalen. Der Konzertkalender ist die erste Anwendung von Klangland.

Der Kalender beantwortet die zentrale Frage:

> Welche interessanten Orchesterkonzerte gibt es in NRW in diesem Monat?

## Produktidee

Die Anwendung zeigt den aktuellen Monat als Startansicht. Veranstaltungen werden nach Datum in einer deutschen Monatsansicht dargestellt und können in einer Detailansicht geöffnet werden. Eine zweite zentrale Ansicht stellt die erfassten Orchester mit ihren Stammdaten und Veranstaltungen vor.

Geplante Bereiche:

- Kalender mit Monatsnavigation und mehreren Veranstaltungen pro Tag
- Veranstaltungsdetailseiten mit Programm, Künstler:innen, Spielstätte und Quelle
- Ensemble- und Orchesterübersicht mit Profilen
- Spielstättenübersicht mit eigenen Profilen
- Direkte URLs für Monate, Ensembles, Spielstätten und Veranstaltungen
- Responsive Darstellung für Desktop und Smartphone
- Tastaturbedienung, sichtbare Fokuszustände und semantische HTML-Struktur

## Architektur

Die Anwendung ist als statische Webapp konzipiert und benötigt kein Backend und keine Datenbank.

```text
Recherche offizieller Quellen
          ↓
Datenaufbereitung und Validierung
          ↓
/data/*.json
          ↓
Git und statisches Deployment
          ↓
Webapp im Browser
```

Die versionierte JSON-Datei ist die Single Source of Truth. Die Webapp konsumiert ausschließlich geprüfte Daten und enthält keine Logik zur Datenbeschaffung.

## Geplanter Projektaufbau

```text
.
├── data/
│   ├── people.json
│   ├── institutions.json
│   ├── ensembles.json
│   ├── venues.json
│   ├── cities.json
│   ├── composers.json
│   ├── works.json
│   ├── events.json
│   └── README.md
├── data-tool/
│   ├── validator/
│   ├── updater/
│   └── reports/
├── schema/
│   └── klangland.schema.json
├── web/
│   └── Angular-/TypeScript-Webapp
├── docs/
│   ├── product/prd.md
│   └── events-and-relations.md
└── README.md
```

## Datenmodell

Die Daten liegen in versionierten JSON-Dateien. Jede Entität besitzt eine eigene Datei und eine eigene Quelle. Das Domänenmodell ist über den Kalender hinaus für eine Klangland-Datenplattform ausgelegt. Stammdaten werden nicht in Veranstaltungen dupliziert; Beziehungen werden ausschließlich über IDs hergestellt:

```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-08-22",
    "season": "2026/27"
  },
  "people": [],
  "institutions": [],
  "ensembles": [],
  "venues": [],
  "composers": [],
  "works": [],
  "events": []
}
```

Die zentralen Beziehungen sind:

```text
Institution ── betreibt/veranstaltet ── Venue
Institution ── trägt ── Ensemble
Person ── leitet ── Ensemble
Ensemble ── spielt ── Event ── findet statt in ── Venue
City ── beschreibt den Ort ── Event
Event ── enthält ── Work
Work ── geschrieben von ── Composer
```

Ein `Event` referenziert daher `ensembleIds`, `venueId`, `cityId`, `workId`-Werte und `conductorPersonIds`. Das Werk selbst enthält keine Aufführungsdaten. Programmpunkte können zusätzlich einen aufgeführten Satz oder eine Fassung angeben. Wiederkehrende Konzerte werden als einzelne Veranstaltungen gespeichert. Jede Veranstaltung soll eine eindeutige ID, ein gültiges Datum und eine ursprüngliche Quelle besitzen.

`works.json` enthält Werkstammdaten. `composers.json` enthält die Komponist:innen. Katalognummern werden als Liste mit `system` und `number` gespeichert, damit beispielsweise Opus-, KV-, D- und WAB-Angaben abgebildet werden können. `durationMinutes` ist eine ungefähre Werksdauer und nicht die Konzertdauer.

`ensembles` ersetzt `orchestras` als Oberbegriff. So können später neben Sinfonie- und Philharmonieorchestern auch Rundfunk-, Kammer- und Opernorchester, Chöre oder andere Ensembles erfasst werden. `venues` sind eigenständige Stammdaten mit Adresse, Koordinaten, Typ und Institutionenbezug. Dadurch kann die Anwendung später neben Ensembleprofilen auch Spielstättenprofile und deren Veranstaltungsprogramm anzeigen.

## Tech-Stack

- Frontend: Angular und TypeScript
- Build: Angular CLI
- Styling: CSS oder schlanke Utility-CSS-Lösung
- Daten: versionierte JSON-Datei
- Datenpflege: Python-CLI
- Deployment: statischer Host, zum Beispiel GitHub Pages, Netlify, Vercel oder Cloudflare Pages

## Datenpflege

Das geplante Python-Werkzeug `nrw_orchester_data` prüft die JSON-Datei und unterstützt ihre Aktualisierung.

```bash
python -m nrw_orchester_data validate
python -m nrw_orchester_data add-event
python -m nrw_orchester_data update
python -m nrw_orchester_data report
```

Die Validierung soll unter anderem doppelte IDs, ungültige Datums- und Uhrzeitwerte, fehlende Pflichtfelder sowie ungültige Ensemble-, Institution- und Venue-Referenzen erkennen. Fehler führen zu einem Exit Code ungleich null. Vergangene Veranstaltungen bleiben erhalten, werden aber als Warnung gemeldet.

Offizielle Websites der Orchester und Veranstalter sind bevorzugte Quellen. Änderungen an Datum, Dirigent:in, Programm, Veranstaltungsort oder Absage werden zunächst als Vorschlag beziehungsweise Änderungsbericht ausgegeben und nicht ohne Prüfung überschrieben.

## Entwicklungsstatus

Das Repository enthält das Produktanforderungsdokument, die dokumentierte und normalisierte JSON-Datenbasis sowie die erste Version der **Angular-Webapp** unter [`web/`](web/). Die App zeigt Kalender, Ensemble- und Spielstättenprofile sowie Veranstaltungsdetails aus den JSON-Daten an (siehe [`web/README.md`](web/README.md)).

```bash
cd web && npm install && npm start   # Dev-Server auf http://localhost:4200
```

Das JSON-Schema und das Python-Datenpflegewerkzeug sind als nächste Umsetzungsschritte vorgesehen.

## Anforderungen aus dem MVP

Das MVP soll:

- beim Öffnen den tatsächlichen aktuellen Monat anzeigen, optional mit konfigurierbarem Referenzdatum für Tests;
- Monatsnavigation ohne vollständigen Seiten-Reload ermöglichen;
- Konzerte kompakt und vollständig verlinkbar darstellen;
- Ensemble-, Spielstätten- und Veranstaltungsdetailseiten anbieten;
- ohne Backend funktionieren;
- mit geprüften JSON-Daten reproduzierbar gebaut und statisch deployt werden können.

Der vollständige Anforderungskatalog steht in [`docs/product/prd.md`](docs/product/prd.md).

Das vollständige Datenmodell mit allen Datenobjekten, gemeinsamen Konventionen und Beziehungen ist in [`docs/data-model.md`](docs/data-model.md) dokumentiert. Je Entität gibt es eine Detaildoku unter [`docs/entities/`](docs/entities/); die Event-spezifischen Regeln stehen in [`docs/events-and-relations.md`](docs/events-and-relations.md).
