# ADR-005: Datenerfassung über idempotente Ingest-Skripte je Quelle

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist der Weg, wie Spielpläne der Orchester/Veranstalter in die
versionierten JSON-Dateien ([ADR-002](ADR-002-json-dateien-als-single-source-of-truth.md))
gelangen. Datenqualität und Nachvollziehbarkeit sind laut PRD §34 die wichtigste
Produktfunktion.

**Specifics:**

- **Reproduzierbarkeit:** ein erneuter Lauf darf keinen Datenmüll erzeugen (Idempotenz).
- **Nachvollziehbarkeit:** Quelle, Mapping-Regeln und Kuratierungsentscheidungen je
  Ensemble dokumentiert; jedes Event trägt seine Quelle.
- **Quellenvielfalt:** verschiedene Quellformate (JSON-API, HTML, Sitemap+Detailseiten).
- **Kontrolle vor Übernahme:** kein automatisches, ungeprüftes Überschreiben von
  Konzertdaten (PRD §18).
- **Trennung von der App:** die Webapp enthält **keine** Beschaffungslogik (PRD §34).

## Candidates to consider

**Summary:** Kandidaten unterscheiden sich in Automatisierungsgrad und Kopplung an die App.

1. **Idempotente Python-Ingest-Skripte je Quelle** (+ Kurzdoku je Ensemble).
2. **Manuelle JSON-Pflege von Hand.**
3. **Generischer Live-Scraper/Crawler**, der zur Laufzeit oder im Deploy Daten zieht.
4. **Zentrales Ein-Tool** (`nrw-orchester-data`) von Beginn an mit Voll-Automatik.

## Research and analysis of each candidate

**Idempotente Ingest-Skripte je Quelle**

- Erfüllt die Kriterien: jedes Skript entfernt zuvor eingespielte Events seiner Quelle
  (erkannt am Quell-Host) und legt Stammdaten dublettenfrei über IDs an ⇒ wiederholbar
  ohne Duplikate. Je Quelle gibt es eine Doku mit Quelle, Mapping und Kuratierung. Passt zur
  Heterogenität der Quellen (API/HTML/Sitemap).
- Cost: pro neuer Quelle ein neues Skript + Doku; dafür robuste, überprüfbare Läufe.
- SWOT: **S** reproduzierbar, quellenspezifisch anpassbar, klar dokumentiert, von der App
  entkoppelt. **W** Wartung bei Quelländerungen, kein einheitliches CLI (noch). **O** Basis
  für den späteren gemeinsamen Validator/Updater. **T** brechende Änderungen der
  Quellseiten.

**Manuelle Pflege**

- Nicht reproduzierbar und fehleranfällig bei Dutzenden Events pro Orchester; skaliert
  nicht.

**Generischer Live-Scraper**

- Verletzt Nicht-Ziele (keine automatische Erkennung aus Webseiten zur Laufzeit, PRD §3)
  und die Trennung App/Beschaffung. Fragil gegenüber uneinheitlichen Quellen.

**Voll-Automatik-Ein-Tool sofort**

- Höchster Vorabaufwand, widerspricht dem Prinzip „kein ungeprüftes Überschreiben".
  Sinnvoll erst später als Klammer über die bewährten Skripte (PRD §17–18).

**Opinions/feedback:** `docs/data-tooling/README.md` beschreibt die Skripte als idempotent
und quellenspezifisch; bereits umgesetzt für Bergische Symphoniker (JSON-API), Essener
Philharmoniker (HTML) und Gürzenich-Orchester (Sitemap+Detailseiten). Die Git-Historie
zeigt den inkrementellen, quellenweisen Aufbau.

## Recommendation

**Summary:** Pro Quelle ein idempotentes Python-Ingest-Skript mit begleitender Doku; die
Webapp bleibt reine Konsumentin.

**Specifics:** Neue Ensembles/Quellen erhalten je ein Skript unter `docs/data-tooling/` plus
eine Kurzdoku (Quelle, Mapping, Kuratierung). Skripte sind idempotent (Events der Quelle vor
dem Schreiben entfernen, Stammdaten über IDs dublettenfrei anlegen). Nach jedem Ingest werden
referenzielle Integrität, ID-Eindeutigkeit sowie Datums-/Zeitformate geprüft. Der geplante
gemeinsame Validator/Updater `nrw-orchester-data` (PRD §16–18) baut später auf diesem
Fundament auf und bleibt beim Grundsatz „Änderungen erst anzeigen, dann übernehmen".
