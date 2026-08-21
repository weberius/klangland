# US-017 – Umsetzungs-Tasks

Umsetzung von [US-017](./US-017-open-opus.md): Anreicherung der Komponist:innen- und Werkdaten aus Open Opus (strukturierte Metadaten + externe IDs) und aus der Wikipedia (kuratierte Kurzfassungen), inkl. sichtbarer Attributierung von Open Opus. Reine **Datenschicht** – die UI-Darstellung ist Teil von [US-024](../backlog/us-024-composers-and-works.md).

Betroffene Dateien:
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts) (Modelle `Composer`, `Work`)
- [data/composers.json](../../../../data/composers.json) (Datenquelle; wird per `tools/sync-data.mjs` nach `web/public/data` synchronisiert)
- [data/works.json](../../../../data/works.json) (dito)
- neu: `docs/data-tooling/import_openopus.py` (Python-Importer, analog zu den vorhandenen `ingest_*.py`)
- neu/aktualisiert: [docs/data-tooling/README.md](../../../../docs/data-tooling/README.md) und/oder [README.md](../../../../README.md) (Attributierung & Herkunftsdoku)

Grundsatz zum Datenfluss: Änderungen immer in `data/*.json` vornehmen (nicht in `web/public/data/...`); der Sync läuft automatisch bei `prebuild`/`prestart` ([tools/sync-data.mjs](../../../../tools/sync-data.mjs)). Da die JSON direkt als `Composer[]`/`Work[]` geladen wird ([data.service.ts:220-221](../../../../web/src/app/core/data.service.ts#L220-L221)), wirkt eine reine Interface-Änderung ohne zusätzlichen Mapper.

---

## Task 1 – Datenmodell erweitern (models.ts)

Bezug: AK 1, AK 2, AK 3, AK 4.

- Im [`Composer`-Interface](../../../../web/src/app/models/models.ts#L131-L135) optionale Felder ergänzen:
  ```ts
  openOpusId?: string | null;   // externe Open-Opus-Referenz (AK 1)
  epoch?: string | null;        // deutschsprachige Epoche aus Open Opus (AK 2)
  wikipedia?: { summary: string; url: string } | null;  // kuratierte Kurzfassung (AK 4)
  ```
- Im [`Work`-Interface](../../../../web/src/app/models/models.ts#L152-L163) optionale Felder ergänzen:
  ```ts
  openOpusId?: string | null;   // externe Open-Opus-Referenz (AK 1)
  popular?: boolean;            // Open-Opus-Kennzeichen (AK 3)
  recommended?: boolean;        // Open-Opus-Kennzeichen (AK 3)
  wikipedia?: { summary: string; url: string } | null;  // kuratierte Kurzfassung (AK 4)
  ```
  - `wikipedia` bewusst als eigenes Objekt (analog `Ensemble.wikipedia`, [models.ts:104](../../../../web/src/app/models/models.ts#L104)); das bestehende `Work.description` bleibt für sachliche Notizen (Fassung, Besetzung) reserviert.
- Alle neuen Felder optional/`| null`, damit bestehende Datensätze ohne Anreicherung valide bleiben. Bestehende Felder unverändert lassen.
- Prüfen, ob der bestehende `Genre`-Union ([models.ts:137-145](../../../../web/src/app/models/models.ts#L137-L145)) mit den Open-Opus-Gattungen (`Chamber`, `Keyboard`, `Orchestral`, `Stage`, `Vocal`) kollidiert. **Klangland-Gattungen bleiben führend**; die Open-Opus-Gattung wird beim Import gemäß Task 3 gemappt, nicht das interne Enum ersetzt.

## Task 2 – Python-Importer anlegen (docs/data-tooling/import_openopus.py)

Bezug: AK 1, AK 2, AK 3, AK 5, AK 6, AK 8, AK 11.

- Neues Skript analog zu den bestehenden `ingest_*.py` (gleicher Kopf-Docstring mit Quelle, Aufruf, Idempotenz-Hinweis; `json`/`pathlib`; schreibt nach `data/composers.json` bzw. `data/works.json`).
- Datenbezug: Open-Opus-Dump `https://api.openopus.org/work/dump.json` bzw. gezielte Endpunkte (Komponist-Suche/`/composer/list/ids`, `/work/list/composer/.../genre/all`, `/work/detail`). **Kein Laufzeitzugriff** der Webanwendung (AK 5) – der Abruf passiert nur beim manuellen Skriptlauf.
- Matching: Für die **bereits in Klangland vorhandenen** Komponist:innen/Werke (Fokus: die in [events.json](../../../../data/events.json) referenzierten, AK 10 / Story „kein Massenimport") den passenden Open-Opus-Eintrag über Name/Titel ermitteln und dessen `id` als `openOpusId` speichern.
- Anreicherung Komponist:in (AK 2): `epoch` (auf Deutsch gemappt, siehe Task 3), Abgleich der Lebensdaten `life.from`/`life.to` gegen `birth`/`death`; **Abweichungen protokollieren** (stdout-Report), nicht still überschreiben.
- Anreicherung Werk (AK 3): Werkverzeichnis-/`catalogue`-Angaben ergänzen, `popular`/`recommended` übernehmen.
- **Kein unkontrolliertes Überschreiben (AK 6):** Bereits gepflegte redaktionelle Felder – insbesondere `wikipedia`, `description`, kuratierte `title` – werden **nicht** durch den Import ersetzt. Der Importer ergänzt nur fehlende bzw. explizit als „aus Open Opus" markierte Felder. Erneuter Lauf ist idempotent.
- **Rate-Limiting (AK 11):** Zentrale Fetch-Hilfsfunktion, die vor jedem HTTP-Request eine Pause einlegt, sodass **höchstens ein Request pro Sekunde** an denselben Dienst geht (z. B. Zeitstempel des letzten Requests merken und per `time.sleep()` auf ein Mindestintervall von 1,0 s auffüllen – robuster als ein festes `sleep(1)`, da lokale Verarbeitungszeit angerechnet wird). Zusätzlich einen sprechenden `User-Agent` setzen und HTTP-Fehler/Timeouts sauber behandeln (mit moderatem Backoff, ohne das 1-req/s-Limit zu unterlaufen).
- **Caching:** Roh-Antworten (Dump, `/work/detail`-Aufrufe) lokal zwischenspeichern (z. B. unter einem gitignorierten Cache-Verzeichnis), damit erneute Läufe die Server nicht unnötig belasten.
- Skript gibt am Ende einen kurzen Report aus (ergänzte IDs, Konflikte/Abweichungen, nicht gematchte Einträge).

## Task 3 – Epochen-Mapping (Open Opus → Deutsch)

Bezug: AK 2.

- Mapping-Tabelle im Importer hinterlegen (Open-Opus-Epochen → deutschsprachige Werte), z. B.:
  `Medieval→Mittelalter`, `Renaissance→Renaissance`, `Baroque→Barock`, `Classical→Klassik`, `Early Romantic→Frühromantik`, `Romantic→Romantik`, `Late Romantic→Spätromantik`, `20th Century→20. Jahrhundert`, `Post-War→Nachkriegszeit`, `21st Century→21. Jahrhundert`.
- Nicht abbildbare/unbekannte Epochen: Rohwert übernehmen und im Report kennzeichnen.

## Task 4 – Wikipedia-Recherche & Datenpflege (composers.json, works.json)

Bezug: AK 4, AK 10, AK 11.

> Rate-Limit: Auch bei der Wikipedia-Recherche gilt das 1-Request-pro-Sekunde-Limit (AK 11). Sofern Abrufe skriptgestützt erfolgen, dieselbe gedrosselte Fetch-Hilfe wie in Task 2 verwenden; bei rein manueller Recherche ist das Limit ohnehin eingehalten.

- Für die in [events.json](../../../../data/events.json) referenzierten Komponist:innen und (relevanten) Werke den passenden **deutschsprachigen** Wikipedia-Artikel recherchieren.
- Wo ein geeigneter Artikel existiert, `wikipedia` pflegen:
  - `summary`: eigenständig formulierte Zusammenfassung von **ca. 60 Wörtern** (kein wörtlicher Auszug), analog zum Vorgehen in [US-014](../done/US-014-ensemble-wikipedia.md).
  - `url`: Voll-URL des Artikels (z. B. `https://de.wikipedia.org/wiki/...`).
- Existiert kein geeigneter Artikel: Feld auf `null` setzen bzw. weglassen (konsistent handhaben).
- Einheitliche Feld-Reihenfolge/Position der neuen Felder in den Objekten beibehalten.

## Task 5 – Attributierung von Open Opus & Herkunftsdoku

Bezug: AK 7, AK 8.

- Open Opus als Datenquelle **sichtbar attribuieren** – namentliche Nennung „Open Opus" plus Link auf `https://openopus.org` – mindestens in der Projektdokumentation:
  - [docs/data-tooling/README.md](../../../../docs/data-tooling/README.md): neuen Abschnitt „Datenquellen / Attributierung" mit Open Opus (Daten: CC0/Public Domain) und dem Hinweis, dass die Attributierung freiwillig aus Transparenzgründen erfolgt.
  - Ggf. Verweis in der Haupt-[README.md](../../../../README.md).
- Herkunft je Datensatz nachvollziehbar machen: `openOpusId` als maschinenlesbaren Herkunftsnachweis nutzen; Wikipedia-Quelle steckt in `wikipedia.url` (AK 8).
- Hinweis für [US-024](../backlog/us-024-composers-and-works.md) notieren: Sobald die Daten in der UI erscheinen, muss der Open-Opus-Credit an einer für Nutzer:innen erreichbaren Stelle (z. B. Datenquellen-/Impressum-Hinweis) sichtbar sein. (Sichtbare UI-Attributierung ist **nicht** Teil von US-017.)

## Task 6 – Metadaten & Versionierung

Bezug: AK 9.

- In [data/composers.json](../../../../data/composers.json) und [data/works.json](../../../../data/works.json) `metadata.version` / `metadata.lastUpdated` hochziehen und `notes` um den Hinweis auf Open Opus / Wikipedia als Quellen ergänzen.
- Import- und Pflegeänderungen in nachvollziehbaren Git-Commits erfassen (Skriptlauf und redaktionelle Pflege getrennt committen, damit maschinelle vs. manuelle Änderungen unterscheidbar bleiben).

## Task 7 – Manuelle Verifikation

- `python3 docs/data-tooling/import_openopus.py` läuft fehlerfrei, ist bei erneutem Lauf idempotent (kein Diff bei unveränderter Quelle) und überschreibt keine kuratierten `wikipedia`/`description`-Felder (AK 5, AK 6).
- Rate-Limit geprüft (AK 11): Über eine kurze Log-/Zeitmessung nachweisen, dass zwischen zwei Netzwerk-Requests mindestens ~1 Sekunde liegt (z. B. Debug-Ausgabe der Request-Zeitstempel bei einem Lauf mit mehreren Abrufen).
- `data/composers.json` und `data/works.json` sind valides JSON; Stichprobe:
  - mehrere Komponist:innen haben `openOpusId` und plausible `epoch` (deutschsprachig) (AK 1, AK 2);
  - mehrere Werke haben `openOpusId`, ggf. `popular`/`recommended` und ergänztes Werkverzeichnis (AK 1, AK 3);
  - gepflegte `wikipedia`-Einträge: ~60 Wörter, gültige `de.wikipedia.org`-URLs (AK 4).
- `cd web && npm run build` – kompiliert fehlerfrei (Typänderungen wirksam, keine bestehenden Nutzungen gebrochen).
- Attributierung geprüft: Open-Opus-Credit inkl. Link in der Doku vorhanden (AK 7).
- Report des Importers gesichtet: Lebensdaten-Abweichungen und nicht gematchte Einträge sind dokumentiert bzw. bereinigt.

## Definition of Done

- Alle Akzeptanzkriterien 1–11 aus [US-017](./US-017-open-opus.md) erfüllt.
- `npm run build` ohne Fehler/Warnungen; `data/composers.json` und `data/works.json` valides JSON.
- Importer idempotent und dokumentiert; Open Opus in der Doku sichtbar attribuiert.
- Keine Änderungen an der UI (bleibt US-024 vorbehalten) und keine Laufzeitabhängigkeit zu Open Opus/Wikipedia.
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben (zusammen mit dieser Tasks-Datei).
