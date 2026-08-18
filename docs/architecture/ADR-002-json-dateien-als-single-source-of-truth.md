# ADR-002: Versionierte JSON-Dateien als Single Source of Truth

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist das Speicher- und Ablageformat für den gesamten Datenbestand
(Ensembles, Venues, Personen, Werke, Events …). Die Datenqualität und -aktualität ist laut
PRD §34 der wichtigste Teil des Produkts; das Format muss dies unterstützen.

**Specifics:**

- **Versionierbarkeit:** Änderungen müssen als lesbare Git-Diffs review- und
  rückrollbar sein.
- **Nachvollziehbarkeit:** jede Aussage muss eine Quelle tragen (PRD §9.1, §16).
- **Werkzeugunabhängigkeit:** ohne Server/DB les- und schreibbar (Editor, Skripte, CI).
- **Direkte Auslieferbarkeit:** ohne Transformationsschritt vom Browser konsumierbar.
- **Prüfbarkeit:** maschinell validierbar (Schema, referenzielle Integrität).

## Candidates to consider

**Summary:** Kandidaten sind textbasierte, versionierbare Formate sowie Datenbanken. Da die
App statisch ist ([ADR-001](ADR-001-statische-webapp-ohne-backend.md)), sind serverseitige
Speicher nachrangig.

1. **JSON-Dateien im Git-Repo** (`data/*.json`).
2. **SQLite-Datei im Repo.**
3. **CSV/Spreadsheet.**
4. **YAML/TOML-Dateien im Repo.**

## Research and analysis of each candidate

**JSON-Dateien im Git**

- Erfüllt alle Kriterien: nativ vom Browser ladbar, per `git diff` reviewbar, per JSON
  Schema validierbar, von Python- und Node-Werkzeugen trivial verarbeitbar.
- Cost: keine Lizenz-/Betriebskosten; Pflegeaufwand liegt im Kuratieren, nicht im Format.
- SWOT: **S** universell, diff-freundlich, direkt auslieferbar. **W** Redundanz-/
  Konsistenzrisiko ohne Validierung, große Arrays werden unübersichtlich. **O** JSON Schema
  + Validator (PRD §16–17). **T** Merge-Konflikte bei paralleler Pflege großer Dateien.

**SQLite**

- Binärformat: kein sinnvoller Git-Diff, nicht direkt vom Browser als statisches Asset
  konsumierbar ohne WASM-Schicht. Verletzt Versionierbarkeit/Direktauslieferung.

**CSV/Spreadsheet**

- Ungeeignet für verschachtelte Strukturen (Programm mit mehreren Werken, Quellenobjekt).
  Schwache Typisierung, keine Referenzsemantik.

**YAML/TOML**

- Gut lesbar und diff-freundlich, aber zusätzlicher Parse-Schritt im Browser nötig und
  fehleranfälligere Syntax (Einrückung). JSON ist ohne Umweg auslieferbar.

**Opinions/feedback:** README und `docs/data-model.md` benennen die versionierte JSON-Datei
ausdrücklich als „Single Source of Truth". Der `DataService` konsumiert ausschließlich diese
geprüften Daten.

## Recommendation

**Summary:** Versionierte JSON-Dateien unter `data/` sind die maßgebliche Datenquelle.

**Specifics:** Alle Inhalte werden als JSON im Git gepflegt und reviewt. Ein
`metadata`-Umschlag (`version`, `lastUpdated`, `language`, optional `season`) begleitet jede
Datei. Die konkrete Aufteilung auf mehrere Dateien und die Referenzsemantik regelt
[ADR-003](ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md); die Auslieferung an die
App regelt [ADR-006](ADR-006-datensync-als-build-artefakt.md). Ein JSON-Schema und ein
Python-Validator (PRD §16–17) sind vorgesehen, um die maschinelle Prüfbarkeit einzulösen.
