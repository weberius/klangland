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

## Projektaufbau

```text
.
├── data/                     # Single Source of Truth (versionierte JSON-Dateien)
│   ├── people.json
│   ├── institutions.json
│   ├── ensembles.json
│   ├── venues.json
│   ├── cities.json
│   ├── composers.json
│   ├── works.json
│   └── events.json
├── web/                      # Angular-/TypeScript-Webapp
├── docs/
│   ├── product/prd.md        # Produktanforderungen
│   ├── product/contracts/    # Gherkin-Szenarien (umgesetztes Verhalten)
│   ├── product/ears/         # Anforderungen in EARS-Notation
│   ├── product/planning/     # Backlog / User Stories
│   ├── architecture/         # Architecture Decision Records (ADR)
│   ├── data-model.md         # Datenmodell (Klammer über alle Entitäten)
│   ├── events-and-relations.md
│   ├── entities/             # Detaildoku je Entität
│   ├── data-tooling/         # Ingest-Skripte + Doku je Quelle
│   └── templates/            # Vorlagen (ADR, Gherkin, EARS)
└── README.md
```

Geplant, aber noch nicht angelegt: `schema/` (JSON-Schema) sowie ein gebündeltes
Python-Datenpflegewerkzeug (`data-tool/` mit Validator/Updater/Reports). Die Datenpflege
erfolgt derzeit über quellenspezifische Ingest-Skripte unter
[`docs/data-tooling/`](docs/data-tooling/).

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

Aktuell werden Spielpläne über **quellenspezifische, idempotente Python-Ingest-Skripte** in
die JSON-Dateien übernommen. Jede Quelle hat ein Skript und eine kurze Doku (Quelle, Mapping,
Kuratierung) unter [`docs/data-tooling/`](docs/data-tooling/). Die Skripte entfernen zuvor
eingespielte Events derselben Quelle und legen Stammdaten anhand ihrer IDs dublettenfrei an.

Komponist:innen- und Werk-Stammdaten werden zusätzlich aus **[Open Opus](https://openopus.org)**
angereichert (strukturierte Metadaten, `openOpusId`, Epoche, `popular`/`recommended`) sowie um
kuratierte, eigenständig formulierte **Wikipedia**-Kurzfassungen ergänzt. Open Opus steht unter
CC0; Klangland nennt die Quelle dennoch freiwillig aus Transparenzgründen (Details und
Attributierung: [`docs/data-tooling/README.md`](docs/data-tooling/README.md)).

Perspektivisch ist zusätzlich ein **gebündeltes Werkzeug** (`nrw-orchester-data`) geplant, das
die JSON-Dateien validiert und die Aktualisierung unterstützt:

```bash
python -m nrw_orchester_data validate
python -m nrw_orchester_data add-event
python -m nrw_orchester_data update
python -m nrw_orchester_data report
```

Die Validierung soll unter anderem doppelte IDs, ungültige Datums- und Uhrzeitwerte, fehlende Pflichtfelder sowie ungültige Ensemble-, Institution- und Venue-Referenzen erkennen. Fehler führen zu einem Exit Code ungleich null. Vergangene Veranstaltungen bleiben erhalten, werden aber als Warnung gemeldet.

Offizielle Websites der Orchester und Veranstalter sind bevorzugte Quellen. Änderungen an Datum, Dirigent:in, Programm, Veranstaltungsort oder Absage werden zunächst als Vorschlag beziehungsweise Änderungsbericht ausgegeben und nicht ohne Prüfung überschrieben.

## Entwicklungsstatus

Das Repository enthält das Produktanforderungsdokument, die dokumentierte und normalisierte JSON-Datenbasis (u. a. 17 Ensembles, 37 Spielstätten und rund 290 Veranstaltungen der Spielzeit 2026/27) sowie die erste Version der **Angular-Webapp** unter [`web/`](web/). Die App zeigt Kalender, Ensemble- und Spielstättenprofile sowie Veranstaltungsdetails aus den JSON-Daten an (siehe [`web/README.md`](web/README.md)). Die Datenerfassung erfolgt über die Ingest-Skripte unter [`docs/data-tooling/`](docs/data-tooling/). Ergänzend liegen Architekturentscheidungen ([`docs/architecture/`](docs/architecture/)), Gherkin-Contracts ([`docs/product/contracts/`](docs/product/contracts/)) und EARS-Anforderungen ([`docs/product/ears/`](docs/product/ears/)) vor.

```bash
cd web && npm install && npm start   # Dev-Server auf http://localhost:4200
```

Das JSON-Schema und ein gebündeltes Python-Datenpflegewerkzeug sind als nächste Umsetzungsschritte vorgesehen.

## Deployment (GitHub Pages)

Die Webapp wird über **GitHub Actions** automatisch auf **GitHub Pages** veröffentlicht.
Der Workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml) baut
und deployt bei jedem Push auf `main` (oder manuell über „Run workflow"). Zielseite:

```text
https://weberius.github.io/klangland/
```

### Einmalige Einrichtung

In den Repo-Einstellungen unter **Settings → Pages → Build and deployment** als
**Source „GitHub Actions"** auswählen. Ohne diese Einstellung schlägt der Deploy-Schritt fehl.

### Ablauf des Workflows

1. **Checkout** und Node.js 22 mit npm-Cache (`web/package-lock.json`).
2. `npm ci` im Verzeichnis `web/`.
3. **Build:** `npm run build -- --configuration production --base-href /klangland/`.
   - `npm run build` löst den `prebuild`-Hook (`tools/sync-data.mjs`) aus, der die JSON-Daten
     aus [`data/`](data/) nach `web/public/data` kopiert. Ein direktes `ng build` würde diesen
     Schritt überspringen und die App ohne Daten ausliefern.
   - `--base-href /klangland/` passt die Pfade an das Pages-Unterverzeichnis an (Repo-Name).
4. **SPA-Fallback:** `index.html` wird als `404.html` kopiert, damit Deep-Links (z. B.
   `…/klangland/events/<id>`) auch beim direkten Aufruf/Neuladen funktionieren.
5. **Upload & Deploy** des Verzeichnisses `web/dist/klangland/browser` über
   `actions/upload-pages-artifact` und `actions/deploy-pages`.

### Manuelles Bauen (lokal, optional)

```bash
cd web
npm ci
npm run build -- --base-href /klangland/     # Ausgabe: web/dist/klangland/browser
```

Das Ergebnis ist rein statisch und lässt sich alternativ auf jedem statischen Host
(Netlify, Vercel, Cloudflare Pages) veröffentlichen. Bei Deployment im Web-Root oder unter
einer eigenen Domain den `--base-href` entsprechend anpassen (z. B. `/`).

> Hinweis: Für den Produktivbetrieb sollte in [`web/src/app/core/app-config.ts`](web/src/app/core/app-config.ts)
> das Demo-`referenceDate` auf `null` gesetzt werden, damit der tatsächliche aktuelle Monat
> als Startansicht erscheint.

## Anforderungen aus dem MVP

Das MVP soll:

- beim Öffnen den tatsächlichen aktuellen Monat anzeigen, optional mit konfigurierbarem Referenzdatum für Tests;
- Monatsnavigation ohne vollständigen Seiten-Reload ermöglichen;
- Konzerte kompakt und vollständig verlinkbar darstellen;
- Ensemble-, Spielstätten- und Veranstaltungsdetailseiten anbieten;
- ohne Backend funktionieren;
- mit geprüften JSON-Daten reproduzierbar gebaut und statisch deployt werden können.

Der vollständige Anforderungskatalog steht in [`docs/product/prd.md`](docs/product/prd.md).
Das umgesetzte Verhalten ist zusätzlich als Gherkin-Contracts ([`docs/product/contracts/`](docs/product/contracts/)) und als EARS-Anforderungen ([`docs/product/ears/`](docs/product/ears/)) spezifiziert; die zentralen Architekturentscheidungen stehen als ADRs unter [`docs/architecture/`](docs/architecture/).

Das vollständige Datenmodell mit allen Datenobjekten, gemeinsamen Konventionen und Beziehungen ist in [`docs/data-model.md`](docs/data-model.md) dokumentiert. Je Entität gibt es eine Detaildoku unter [`docs/entities/`](docs/entities/); die Event-spezifischen Regeln stehen in [`docs/events-and-relations.md`](docs/events-and-relations.md).

---

**Dokumentationsstatus (Stand 2026-08-24)**

- **Version:** 1.0 (Spielzeit 2026/27)
- **ADRs:** 8 akzeptiert (ADR-001 bis ADR-008)
- **Gherkin-Contracts:** 11 Szenarien-Dateien
- **EARS-Anforderungen:** 11 Spezifikations-Dateien mit 171+ Anforderungen
- **PRD:** Vollständig für MVP-Spielzeit 2026/27
- **Letztes Update:** 2026-08-24 (Dateinamensharmonisierung, fehlende Gherkin-Szenarien ergänzt)
