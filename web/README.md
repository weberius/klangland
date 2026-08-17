# Klangland Web

Statische Angular-Webapp, die den Klangland-Datenbestand (`/data/*.json`) im Browser
anzeigt: Konzertkalender, Ensemble- und Spielstättenprofile sowie Veranstaltungsdetails.
Es gibt kein Backend; die App liest ausschließlich die geprüften JSON-Dateien.

## Voraussetzungen

- Node.js 20.19+ / 22.12+ / 24+ (getestet mit Node 24)
- npm

## Entwicklung

```bash
cd web
npm install          # einmalig
npm start            # Dev-Server auf http://localhost:4200
```

`npm start` und `npm run build` synchronisieren vorher automatisch die Daten
(`npm run sync:data`) aus dem Repo-Verzeichnis `../data` nach `public/data`.

## Build

```bash
npm run build        # Produktionsbuild nach web/dist/klangland-web/
```

Das Ergebnis ist eine rein statische Anwendung und kann auf jedem statischen Host
(GitHub Pages, Netlify, Vercel, Cloudflare Pages) deployt werden.

## Daten

- Single Source of Truth bleibt `/data/*.json` im Repo-Wurzelverzeichnis.
- `web/public/data/` ist ein **Build-Artefakt** (in `.gitignore`), das per
  `tools/sync-data.mjs` aus `/data` erzeugt wird.
- Die Datenmodelle in `src/app/models/models.ts` entsprechen den Dokumenten unter
  `/docs` (`data-model.md`, `entities/*`, `events-and-relations.md`).

## Routen (Deep-Links)

| Route | Ansicht |
| --- | --- |
| `/` | Kalender, aktueller Monat |
| `/calendar/:year/:month` | Kalender eines bestimmten Monats |
| `/ensembles` | Ensemble-Übersicht |
| `/ensembles/:id` | Ensemble-Profil |
| `/venues` | Spielstätten-Übersicht |
| `/venues/:id` | Spielstätten-Profil |
| `/events/:id` | Veranstaltungsdetail |

## Konfiguration

`src/app/core/app-config.ts`:

- `referenceDate`: Referenzdatum für „heute". `null` = tatsächliches Systemdatum.
  Aktuell steht hier als **Demo** `'2026-10-01'`, damit die Beispiel-Events (Okt/Nov 2026)
  beim Öffnen sichtbar sind. Für den Produktivbetrieb auf `null` setzen.
- `dataBasePath`: Basis-Pfad der JSON-Daten (Standard `data`).

## Architektur (Kurzüberblick)

- **Standalone-Komponenten**, Angular Signals, lazy geladene Seiten-Komponenten.
- `DataService` (`src/app/core/data.service.ts`) lädt alle JSON-Dateien einmalig beim
  App-Start (`provideAppInitializer`), indexiert sie nach ID und löst die Beziehungen
  zwischen den Entitäten auf.
- Bei Ladefehlern zeigt die App eine Fehlermeldung statt abzustürzen.
