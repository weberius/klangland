# ADR-006: Datenbereitstellung an die App als Build-Artefakt

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist der Mechanismus, wie die im Repo-Wurzelverzeichnis `data/`
gepflegten JSON-Dateien ([ADR-002](ADR-002-json-dateien-als-single-source-of-truth.md)) der
statischen Angular-App als Assets bereitgestellt werden – ohne die Single Source of Truth zu
duplizieren.

**Specifics:**

- **Eine Wahrheit:** `data/` bleibt die einzige gepflegte Quelle; keine parallele
  Pflege einer Kopie.
- **Kein doppelter Diff:** eine Kopie im App-Verzeichnis darf nicht versioniert werden.
- **Zuverlässigkeit:** der aktuelle Stand liegt bei jedem `start`/`build` automatisch vor.
- **Einfachheit:** minimale Toolchain, keine zusätzliche Laufzeitabhängigkeit.
- **Statik:** Ergebnis passt zur rein statischen Auslieferung
  ([ADR-001](ADR-001-statische-webapp-ohne-backend.md)).

## Candidates to consider

**Summary:** Die Kandidaten unterscheiden sich darin, ob und wie die Daten in den
App-Build gelangen.

1. **Sync-Skript kopiert `data/` → `web/public/data/`** (gitignoriertes Build-Artefakt),
   automatisch via npm-`pre`-Hooks.
2. **JSON-Dateien direkt im App-Verzeichnis pflegen** (`web/public/data` als Quelle).
3. **Kopie committen** (versionierte Duplikate in `web/public/data`).
4. **Symlink** von `web/public/data` auf `../data`.
5. **Laufzeit-Fetch aus `data/` über konfigurierten Pfad** ohne Kopie.

## Research and analysis of each candidate

**Sync-Skript + gitignoriertes Artefakt**

- Erfüllt alle Kriterien: `tools/sync-data.mjs` kopiert alle `*.json` nach `public/data`;
  `prestart`/`prebuild` triggern es automatisch. `public/data` ist gitignoriert ⇒ keine
  Duplikat-Diffs. Reine Node-Standardbibliothek, keine Zusatzabhängigkeit.
- Cost: ein kleines Skript + zwei npm-Hooks; vernachlässigbar.
- SWOT: **S** eine Wahrheit, automatisch, plattformunabhängig, einfach. **W** Kopie ist
  bei direktem `ng`-Aufruf ohne Hook nicht garantiert aktuell. **O** Sync-Schritt kann
  später Schema-Validierung mitausführen. **T** —

**Direkt im App-Verzeichnis pflegen**

- Verletzt die Trennung: die App-interne Kopie würde zur faktischen Quelle; Skripte und
  Doku ([ADR-005](ADR-005-idempotente-python-ingest-skripte.md)) zeigen aber auf `data/`.

**Kopie committen**

- Erzeugt doppelte, driftende Diffs desselben Inhalts; genau das soll vermieden werden.

**Symlink**

- Nicht zuverlässig plattformübergreifend (Windows/CI) und für manche Bundler intransparent.

**Laufzeit-Fetch aus `data/`**

- `data/` liegt außerhalb des App-Assets-Roots; im statischen Deployment nicht adressierbar
  ohne Kopie ins Bundle. Löst das Problem nicht.

**Opinions/feedback:** `web/README.md` und der Skript-Kopf dokumentieren `public/data`
ausdrücklich als Build-Artefakt und `data/` als Single Source of Truth. Der `DataService`
lädt über den konfigurierbaren `dataBasePath` (Standard `data`).

## Recommendation

**Summary:** `data/` bleibt Quelle; `tools/sync-data.mjs` erzeugt `web/public/data/` als
gitignoriertes Build-Artefakt, automatisch vor `start` und `build`.

**Specifics:** Der Sync läuft über die npm-Hooks `prestart`/`prebuild` (auch manuell via
`npm run sync:data`). Die App liest die Daten einmalig beim Start über den `DataService`
(`provideAppInitializer`, `forkJoin` über alle Dateien) und indexiert sie in-memory nach ID;
bei Ladefehlern zeigt sie eine Fehlermeldung statt abzustürzen (PRD §30). Der Datenpfad ist
über `APP_CONFIG.dataBasePath` konfigurierbar. Perspektivisch kann der Sync-Schritt die
Schema-/Integritätsprüfung (PRD §16–17) mit ausführen.
