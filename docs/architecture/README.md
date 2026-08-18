# Architecture Decision Records

Dieses Verzeichnis dokumentiert die zentralen Architekturentscheidungen von Klangland als
Architecture Decision Records (ADR). Jede Datei folgt dem Template unter
[`../templates/adr.md`](../templates/adr.md): Titel, Status, Bewertungskriterien, betrachtete
Kandidaten, Analyse (inkl. SWOT) und Empfehlung.

Die ADRs halten Entscheidungen fest, die in der bisherigen Entwicklung bereits getroffen und
umgesetzt wurden. Ergänzender Kontext steht im [PRD](../product/prd.md), im
[Datenmodell](../data-model.md) und im [Daten-Tooling](../data-tooling/README.md).

## Übersicht

| ADR | Thema | Status |
| --- | --- | --- |
| [ADR-001](ADR-001-statische-webapp-ohne-backend.md) | Statische Webapp ohne Backend | accepted |
| [ADR-002](ADR-002-json-dateien-als-single-source-of-truth.md) | Versionierte JSON-Dateien als Single Source of Truth | accepted |
| [ADR-003](ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md) | Normalisiertes Datenmodell mit getrennten Dateien und ID-Referenzen | accepted |
| [ADR-004](ADR-004-angular-als-frontend-framework.md) | Angular und TypeScript als Frontend-Framework | accepted |
| [ADR-005](ADR-005-idempotente-python-ingest-skripte.md) | Datenerfassung über idempotente Ingest-Skripte je Quelle | accepted |
| [ADR-006](ADR-006-datensync-als-build-artefakt.md) | Datenbereitstellung an die App als Build-Artefakt | accepted |

## Konventionen

- Dateiname: `ADR-<NNN>-<thema-in-kebab-case>.md`, fortlaufend nummeriert.
- Ein ADR pro Entscheidung; einmal akzeptierte ADRs werden nicht umgeschrieben, sondern bei
  Bedarf durch ein neues ADR ersetzt (Status `superseded`).
- Status: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded`.
