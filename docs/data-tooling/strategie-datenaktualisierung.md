# Strategie: Datenaktualisierung & Ausbau auf weitere Ensembles (Arbeitsstand)

**Status:** Diskussionsstand, keine Entscheidung final. Dient als Einstiegspunkt, um die
Arbeit an anderer Stelle fortzusetzen. Kein ADR (dafür fehlen noch getroffene
Entscheidungen), aber Kandidat für spätere ADRs, sobald einzelne Punkte final sind.

## Ausgangslage

- [`docs/data-tooling/`](.) enthält aktuell **10 quellenspezifische Ingest-Skripte** (siehe
  Tabelle in [`README.md`](README.md)), die jeweils idempotent Events + Stammdaten in
  `data/*.json` schreiben ([ADR-005](../architecture/ADR-005-idempotente-python-ingest-skripte.md)).
- Nicht alle erfassten Ensembles haben ein Skript. Beispiel **Köln**: Das
  Gürzenich-Orchester hat ein Skript ([`ingest_guerzenich.py`](ingest_guerzenich.py) +
  [`guerzenich-orchester-koeln.md`](guerzenich-orchester-koeln.md)); das **WDR
  Sinfonieorchester** ist zwar in [`data/ensembles.json`](../../data/ensembles.json) als
  Ensemble angelegt und hat Events in `events.json`, aber **kein** eigenes Ingest-Skript
  (Events wirken händisch/beispielhaft recherchiert, vgl. Hinweistext in
  `events["metadata"]["notes"]` in [`ingest_guerzenich.py`](ingest_guerzenich.py#L563)).
- Gewünschter Ausbau (Auslöser dieser Diskussion):
  - Vollständigkeitsprüfung/Nacherfassung bestehender Quellen, **beginnend mit Köln**,
    perspektivisch für alle Ensembles.
  - Neue Ensembles: **WDR Funkhausorchester**, **WDR Big Band**, **WDR Chor**.
  - **Opernaufführungen** — nicht nur Köln, sondern **NRW-weit**.

## Grundproblem, das die Strategie lösen soll

Mit wachsender Zahl an Quellen wird unsichtbar, **welche Ensembles/Institutionen bereits
erfasst sind, welche ein Skript haben, welche nur Stammdaten ohne Events, und welche noch
gar nicht modelliert sind.** Der Wunsch: eine Konfigurationsdatei mit dem Soll-Zustand
(analog zu `ensembles.json`, aber inkl. URL/Ort/Status je Quelle), gegen die ein Skript den
Ist-Zustand abgleicht.

## Vereinbarte Grundrichtung

### 1. Zwei Ebenen, nicht eine
1. **Bestehende Erfassung stabilisieren/prüfen** (Coverage-Audit, beginnend Köln).
2. **Skalierbares Modell für neue Ensembles/Institutionen** (Registry + vereinheitlichtes
   Tooling), bevor NRW-weit viele neue Scraper entstehen.

### 2. Quelltypen unterscheiden (wichtig für Oper)
Nicht jede Quelle ist ein Ensemble. Vorschlag für `kind`:
- `ensemble` — z. B. Gürzenich-Orchester, WDR Sinfonieorchester.
- `institution` — z. B. Oper Köln (`data/institutions.json`, `type: opera_house`,
  referenziert per `ensembleIds` das spielende Ensemble). Opernaufführungen hängen fachlich
  eher an der Institution/dem Haus als am Ensemble.

Damit lässt sich Oper NRW-weit modellieren, ohne Opernhäuser als Pseudo-Ensembles zu
verbiegen.

### 3. Zielarchitektur: Registry + gemeinsames Tooling statt N isolierter Skripte

```text
docs/data-tooling/
├── registry/
│   └── sources.json        # Soll-Zustand: eine Zeile pro Quelle (Ensemble ODER Institution)
├── lib/                     # aus ingest_*.py extrahierte gemeinsame Bausteine
│   ├── io.py                # load()/save() für data/*.json
│   ├── text.py               # fold(), Umlaut-Transliteration
│   ├── pipeline.py            # idempotente Remove-Merge-Save-Logik, resolve_description()
│   ├── validate.py            # referenzielle Integrität, Formate
│   └── diff.py                # Vorher/Nachher-Vergleich für Reports
├── adapters/                # heutige ingest_*.py, vereinheitlicht (Migration, kein Rewrite)
├── cli.py                    # `status | run | report | validate`
└── <bestehende .md-Dokus je Quelle bleiben>
```

Migration ist **inkrementell**: bestehende Skripte bleiben lauffähig, `lib/` wird aus
identischem Boilerplate extrahiert (z. B. `fold()`/`load()`/`save()`, die in
[`ingest_bergische.py`](ingest_bergische.py) und [`ingest_guerzenich.py`](ingest_guerzenich.py)
fast identisch vorkommen), CLI ruft Adapter zunächst nur zusätzlich auf.

### 4. Registry-Schema (Kernidee der Nutzeranfrage, erweitert)

Pro Quelle mindestens:

```json
{
  "sourceId": "wdr-sinfonieorchester",
  "kind": "ensemble",
  "entityRef": { "file": "ensembles.json", "id": "wdr-sinfonieorchester" },
  "displayName": "WDR Sinfonieorchester",
  "status": "planned",

  "location": {
    "cityId": "koeln",
    "venueId": "koelner-philharmonie",
    "venueConfidence": "primary_only",
    "note": "Auswärtstermine je Event aus der Quelle bestimmen, nicht pauschal zuordnen (vgl. Hagen-Muster)."
  },

  "calendar": {
    "url": "https://www1.wdr.de/orchester-und-chor/sinfonieorchester/konzerte/termine",
    "kind": "html_paged",
    "requiresJs": false
  },

  "descriptionPolicy": {
    "mode": "facts_only",
    "curationQueue": ".cache/descriptions/wdr-sinfonieorchester/pending.json",
    "fallbackWhenNoProgram": "source_announcement_note"
  },

  "adapter": null,
  "docUrl": "docs/data-tooling/wdr-sinfonieorchester.md"
}
```

**Statuswerte:** `active` (Adapter läuft) · `planned` (Stammdaten vorhanden, kein Adapter) ·
`not_modeled` (noch nicht mal in `ensembles.json`/`institutions.json`) · `blocked`
(technisch/inhaltlich noch nicht scrapebar) · `manual_only`.

**Wichtige Validierungsregel:** `status: "active"` ist nur zulässig, wenn `location.cityId`
und `calendar.url` gesetzt sind — sonst automatisch `blocked` mit Grund (`missing_location`
/ `missing_calendar_url`). Verhindert, dass ein Adapter startet, bevor Ortszuordnung geklärt
ist.

**Ort ist zweistufig zu denken:**
- `ensembles.json`/`institutions.json` → Sitzort (Stammdaten, bereits vorhanden).
- `registry.location` → Default/Fallback für Events, **wenn** die Quelle selbst keine
  Ortsangabe liefert. Auswärtstermine sollen weiterhin pro Event aus der Quelle erkannt
  werden (Vorbild: [`philharmonisches-orchester-hagen.md`](philharmonisches-orchester-hagen.md),
  das Gastspiele außerhalb Hagens korrekt ausschließt statt pauschal zuzuordnen).

### 5. `status`-Kommando (Kern des gewünschten Abgleichs)

Vergleicht `registry/sources.json` gegen `ensembles.json`/`institutions.json` und meldet:
- Quellen mit Adapter vs. ohne.
- Ensembles/Institutionen, die **gar nicht** in der Registry stehen (`MISSING_FROM_REGISTRY`).
- Blockierte Quellen mit Begründung.

Exit Code ≠ 0, wenn nicht alle Quellen `active` sind (CI-/Übersichtstauglich). Beispielhafte
Ausgabe und Pseudocode wurden im Chat skizziert, aber **noch nicht implementiert**.

### 6. Event-Beschreibungen: Rechtsklarheit + Fallback für leeres Programm

Ausgangspunkt: In [`ingest_guerzenich.py`](ingest_guerzenich.py#L369) gibt es bereits ein
Ad-hoc-Muster (`DESC_NOTES`), das Events ohne erkennbares Programm einen Hinweistext in
`description` gibt (z. B. „Programm wird noch bekannt gegeben"). Das soll verallgemeinert
werden.

**Dreistufiger Workflow (analog zum bestehenden Wikipedia-Kurationsprozess für
Komponist:innen, siehe [`README.md`](README.md#wikipedia-kurzfassungen-ablauf)):**

1. **Rohtext-Erfassung** — Adapter zieht Ankündigungs-/Teasertext, landet zunächst in
   `.cache/descriptions/<source>/raw.json` (gitignored), **nicht** direkt in `events.json`.
2. **Redaktion** — eigenständig formulierte Kurzfassung, kein wörtlicher Auszug (gleicher
   Grundsatz wie bei Wikipedia-Kurzfassungen, wegen Urheberrecht an Ankündigungstexten der
   Orchester-Websites).
3. **Anwendung** — Skript schreibt nur in leere `description`-Felder, überschreibt nichts
   Kuratiertes.

**Praktikabler Mittelweg für Skalierung** (ohne Redaktionsschritt für jede Quelle):
`descriptionPolicy.mode`
- `facts_only` — Adapter darf automatisiert **Fakten-Sätze** bauen (Werk-/Solistenliste,
  Anlasstyp, Moderation, Kooperationspartner) — siehe bereits vorhandene Beispiele in
  `events.json` (z. B. „Antrittskonzert der neuen Chefdirigentin Marie Jacquot.",
  „Mit dem WDR Rundfunkchor."). **Keine** Übernahme von Fließtext/Marketing-Prosa.
- `curated_required` — Rohtext muss zwingend durch die Redaktionsschleife (Quelle liefert
  nur werbliche Fließtexte, kein strukturiertes Programm).
- `none` — keine Beschreibung übernehmen.

**Fallback-Priorität, wenn kein Programm erkannt wurde** (füllt die sonst leere
UI-Programmbox):

```python
def resolve_description(event, curated_text=None):
    if curated_text:
        return curated_text
    if event.get("program"):
        return None  # Programmliste füllt die Box selbst, keine Redundanz
    if event.get("_source_announcement_note"):
        return event["_source_announcement_note"]
    return None
```

Nur wenn `program` leer ist, wird `description` zur Pflichtfüllung der UI-Box; ist ein
Programm vorhanden, bleibt `description` optional.

## Vorgeschlagene Roadmap (Reihenfolge, noch nicht final committed)

**Phase A — sofort**
1. Coverage-Matrix/Registry mit den 10 bestehenden aktiven Quellen befüllen (`status: active`).
2. Köln-Audit: Gürzenich-Orchester-Ergebnis gegen Website nachprüfen (Anzahl
   Produktionen/Termine, Programmabdeckung, fehlklassifizierte Formate).
3. WDR-Ensembles strukturieren: Sinfonieorchester (Registry-Eintrag ergänzen, Adapter
   fehlt noch), Funkhausorchester/Big Band/Chor (`not_modeled` → zunächst Stammdaten in
   `ensembles.json` anlegen).
4. Oper-Scope festlegen: Nur Köln zuerst oder direkt NRW-weit? Nur Aufführungen mit
   Orchesterbeteiligung oder vollständiger Spielplan?

**Phase B — kurzfristig**
5. `lib/` aus bestehenden Skripten extrahieren (kein Verhaltensunterschied).
6. `status`-Kommando lauffähig bauen (reine Read-Only-Auswertung, kein Risiko für
   bestehende Daten).
7. `resolve_description()` in eine gemeinsame Pipeline heben.

**Phase C — Ausbau**
8. Neue Kölner Quellen (WDR Funkhausorchester, Big Band, Chor, Oper Köln) im neuen
   Adapter-Format bauen.
9. Danach NRW-weit nach Quelltyp skalieren (weitere Opernhäuser, Rundfunkensembles,
   städtische Orchester).

## Offene Entscheidungen (nächste Schritte bei Wiederaufnahme)

- [ ] Scope endgültig festlegen: nur Konzerte (Scope 1) vs. + Oper (Scope 2) vs. + Chor/Big
      Band/Sonderformate (Scope 3).
- [ ] Oper-Modellierung im Datenmodell verbindlich klären: `eventType: "opera"` + `ensembleIds`
      + `institutionId` — braucht es zusätzlich eine `productionId` für Opernserien?
- [ ] Erste Umsetzung wählen: Registry+`status`-Kommando **oder** Köln-Audit zuerst?
- [ ] `registry/sources.json` mit echten Daten für alle 10 bestehenden Quellen + neue
      WDR-Einträge + Oper Köln befüllen.
- [ ] `descriptionPolicy` pro bestehender Quelle nachträglich festlegen (aktuell nur für
      Gürzenich implizit über `DESC_NOTES` gelöst).

## Referenzen

- [`README.md`](README.md) — Quellenübersicht, Stammdaten-Anreicherung, Wikipedia-Workflow.
- [`ingest_guerzenich.py`](ingest_guerzenich.py) / [`guerzenich-orchester-koeln.md`](guerzenich-orchester-koeln.md) — Vorbild für Köln-Audit.
- [`philharmonisches-orchester-hagen.md`](philharmonisches-orchester-hagen.md) — Vorbild für
  korrekte Auswärtstermin-Behandlung.
- [ADR-005](../architecture/ADR-005-idempotente-python-ingest-skripte.md) — Grundsatzentscheidung
  für idempotente Ingest-Skripte, auf der diese Strategie aufbaut.
- [`data/institutions.json`](../../data/institutions.json) — `oper-koeln` als bestehendes
  Beispiel für `type: opera_house` mit `ensembleIds`.
