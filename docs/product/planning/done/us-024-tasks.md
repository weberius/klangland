# US-024 – Umsetzungs-Tasks

Umsetzung von [US-024](./us-024-composers-and-works.md): Komponist:innen-Seiten (`/composers`, `/composers/:id`) analog zu den Werke-/Venue-Seiten, Erweiterung der Werk-Detailseite (Komponisten-Verlinkung + Open-Opus-/Wikipedia-Anreicherung) sowie Beschaffung, Persistierung und attribuierte Anzeige von Komponisten-Portraits aus Wikipedia/Wikimedia Commons.

Betroffene / neue Dateien:
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts) (`Composer` um Portrait-Feld ergänzen)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (Zugriffe: Komponist:innen/Werke/Events je Filter bzw. Komponist:in)
- [web/src/app/app.routes.ts](../../../../web/src/app/app.routes.ts) (neue Routen)
- [web/src/app/app.html](../../../../web/src/app/app.html#L71-L75) (Navigationspunkt)
- **neu** `web/src/app/pages/composer-list/composer-list.{ts,html,css}` (Vorbild: [work-list](../../../../web/src/app/pages/work-list/), [venue-list](../../../../web/src/app/pages/venue-list/))
- **neu** `web/src/app/pages/composer-detail/composer-detail.{ts,html,css}` (Vorbild: [ensemble-detail](../../../../web/src/app/pages/ensemble-detail/), [work-detail](../../../../web/src/app/pages/work-detail/))
- [web/src/app/pages/work-detail/work-detail.{ts,html}](../../../../web/src/app/pages/work-detail/) (erweitern)
- [data/composers.json](../../../../data/composers.json) (Portrait-Feld pflegen)
- **neu** `data/portraits/` (heruntergeladene Bilddateien, committet)
- **neu** `docs/data-tooling/fetch_composer_portraits.py` (Download-Tool, Vorbild: [fetch_wikipedia_composers.py](../../../../docs/data-tooling/fetch_wikipedia_composers.py))
- [web/tools/sync-data.mjs](../../../../web/tools/sync-data.mjs) (Portraits mitkopieren)
- [web/.gitignore](../../../../web/.gitignore#L46) (synchronisiertes Portrait-Zielverzeichnis ignorieren)
- [docs/data-tooling/README.md](../../../../docs/data-tooling/README.md) (Bildquelle/Attribution dokumentieren)

Wiederverwendung: [`FilterService`](../../../../web/src/app/core/filter.service.ts) (`selectedCityIds()`/`selectedProfileIds()`), [`app-page-header`](../../../../web/src/app/shared/page-header/page-header.ts), [`app-event-list`](../../../../web/src/app/shared/event-list.ts), Wiki-Attributions-Markup aus [ensemble-detail.html:53-66](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L53-L66).

Grundsatz zum Datenfluss (wie US-017): Änderungen immer in `data/*` vornehmen; der Sync ([web/tools/sync-data.mjs](../../../../web/tools/sync-data.mjs)) läuft automatisch bei `prebuild`/`prestart` und kopiert nach `web/public/` (Build-Artefakt, gitignored).

> **Netzwerk-Grundregel für alle Skript-Tasks (AK 15):** Jeder HTTP-Abruf gegen Wikipedia/Wikimedia Commons hält **mindestens 1 Sekunde Abstand** zum vorherigen Request an denselben Dienst. Umsetzung wie in [fetch_wikipedia_composers.py](../../../../docs/data-tooling/fetch_wikipedia_composers.py) (`MIN_INTERVAL_SECONDS = 1.0`, Zeitstempel des letzten Requests merken und per `time.sleep()` auf das Mindestintervall auffüllen – lokale Verarbeitungszeit wird angerechnet, robuster als ein festes `sleep(1)`). Roh-Antworten werden gitignoriert unter `docs/data-tooling/.cache/` zwischengespeichert.

---

## Task 1 – Datenmodell: Portrait-Feld (models.ts)

Bezug: AK 12.

- Im [`Composer`-Interface](../../../../web/src/app/models/models.ts#L131-L141) ein optionales Portrait-Feld ergänzen:
  ```ts
  /** Lokal persistiertes Portrait (US-024); Quelle Wikipedia/Wikimedia Commons. */
  portrait?: {
    file: string;    // Dateiname relativ zum Portrait-Verzeichnis (z. B. "ludwig-van-beethoven.jpg")
    source: string;  // Quell-URL (Wikipedia/Wikimedia Commons), Ziel der Attribution
    credit?: string | null; // optionale Urheber-/Bildbeschreibung für die Attribution
  } | null;
  ```
- Feld optional/`| null`, damit Komponist:innen ohne Bild valide bleiben (AK 12). Keine weiteren Modelländerungen; `Work` bleibt unverändert (Anreicherungsfelder aus US-017 sind bereits vorhanden).

## Task 2 – Portrait-Download-Tool (docs/data-tooling/fetch_composer_portraits.py)

Bezug: AK 12, AK 13, AK 14, AK 15, AK 17.

- Neues Python-Skript analog zu [fetch_wikipedia_composers.py](../../../../docs/data-tooling/fetch_wikipedia_composers.py) (gleicher Kopf-Docstring: Zweck, Quelle, „Schonender Abruf", Cache, Aufruf). `SKIP_IDS`/`TITLE_OVERRIDES` aus [import_openopus.py](../../../../docs/data-tooling/import_openopus.py) wiederverwenden, damit Platzhalter-/Sammeleinträge übersprungen werden.
- Für die in [composers.json](../../../../data/composers.json) vorhandenen Komponist:innen das **führende Bild** ermitteln:
  - bevorzugt über die Wikipedia-REST-Summary (`https://de.wikipedia.org/api/rest_v1/page/summary/{titel}` → `originalimage`/`thumbnail`), alternativ über die Wikimedia-Commons-/`pageimages`-API; vorhandene `wikipedia.url` je Komponist:in als Ausgangspunkt nutzen.
  - Es werden Bilder aus Wikipedia/Wikimedia Commons bezogen (Lizenzfrage dort i. d. R. geklärt, AK 14) – **keine** Fremdquellen.
- **Download & Persistierung (AK 13):** Bild herunterladen und unter `data/portraits/<composerId>.<ext>` speichern (committet). Datei-Endung aus Content-Type/URL ableiten; sinnvolle Maximalgröße/Format beibehalten (Re-Encoding ist Out of Scope).
- **Rückschreiben (AK 12):** `portrait: { file, source, credit? }` in `data/composers.json` setzen – `source` = Quell-URL (Wikipedia-Artikel bzw. Commons-Dateiseite), `credit` sofern leicht ermittelbar (sonst `null`).
- **Kein unkontrolliertes Überschreiben (Analogie US-017 AK 6):** Bereits gepflegte `portrait`-Einträge nicht ersetzen; erneuter Lauf ist idempotent (kein Diff bei unveränderter Quelle, kein Re-Download bei vorhandener Datei). Optional analog zu US-017 in `fetch_` (recherchiert/lädt) und `apply_` (schreibt Feld) trennen, falls redaktionelle Kuratierung gewünscht ist.
- **Rate-Limiting (AK 15):** Zentrale gedrosselte Fetch-Hilfe verwenden (siehe Netzwerk-Grundregel oben) – **max. ein Request pro Sekunde**; gilt für Metadaten-Abfrage **und** Bild-Download. Sprechenden `User-Agent` setzen, HTTP-Fehler/Timeouts mit moderatem Backoff behandeln, ohne das 1-req/s-Limit zu unterlaufen.
- **Caching:** Metadaten-Antworten unter `docs/data-tooling/.cache/` (bereits gitignored) ablegen; heruntergeladene Bilder liegen als Endprodukt in `data/portraits/`.
- Abschluss-Report auf stdout: gefunden/geladen, übersprungen, nicht gefunden, Konflikte.

## Task 3 – Portraits ausliefern (sync-data.mjs, gitignore, Assets)

Bezug: AK 13, AK 16.

- [web/tools/sync-data.mjs](../../../../web/tools/sync-data.mjs) erweitern, sodass zusätzlich zu den `*.json` das Verzeichnis `data/portraits/` nach `web/public/portraits/` kopiert wird (rekursiv, `mkdirSync(..., { recursive: true })`). Single Source of Truth bleibt `data/portraits/`; `web/public/portraits/` ist ein Build-Artefakt.
- In [web/.gitignore](../../../../web/.gitignore#L46) analog zu `public/data/` auch `public/portraits/` ignorieren (synchronisiertes Zielverzeichnis nicht committen).
- Assets werden aus `web/public` ausgeliefert ([angular.json](../../../../web/angular.json), `assets`-Glob `public/**/*`); es ist **keine** angular.json-Änderung nötig. **Achtung Namenskollision:** Das öffentliche Bildverzeichnis heißt bewusst `portraits/` (nicht `composers/`), um nicht mit der Route `/composers` zu kollidieren. Bild-URL zur Laufzeit: `portraits/<file>` (kein Fremd-URL-Zugriff, AK 13).

## Task 4 – Datenzugriffe im DataService (data.service.ts)

Bezug: AK 4, AK 5, AK 8, AK 9.

- **Programmierte Komponist:innen unter Filter** (Quelle des Kachel-Grids, analog zu [`worksForFilter`](../../../../web/src/app/core/data.service.ts#L368-L383)):
  ```ts
  /** Komponist:innen mit >=1 programmierten Werk (unter Ort-/Profil-Filter), sortiert nach Name (US-024). */
  composersForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Composer[] {
    const ids = new Set<string>();
    for (const w of this.worksForFilter(cityIds, profileIds)) ids.add(w.composerId);
    return [...ids]
      .map((id) => this.composer(id))
      .filter((c): c is Composer => Boolean(c))
      .sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }
  ```
  - Baut auf `worksForFilter` auf und erbt damit die Filter-/Saison-Semantik (AK 4); `Set` sichert „jede:r genau einmal" (AK 4); Sortierung nach `name` (AK 5).
- **Werke einer Komponist:in unter Filter** (AK 6, AK 8):
  ```ts
  /** Programmierte Werke einer Komponist:in (unter Filter), sortiert nach Titel (US-024). */
  worksForComposer(composerId: string, cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Work[] {
    return this.worksForFilter(cityIds, profileIds)
      .filter((w) => w.composerId === composerId)
      .sort((a, b) => a.title.localeCompare(b.title, 'de'));
  }
  ```
- **Events einer Komponist:in unter Filter** (AK 9):
  ```ts
  /** Chronologische Events (unter Filter), in deren Programm ein Werk der Komponist:in vorkommt (US-024). */
  eventsForComposer(composerId: string, cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): ConcertEvent[] {
    const workIds = new Set(this.worksForComposer(composerId, cityIds, profileIds).map((w) => w.id));
    return this.eventsForFilter(cityIds, profileIds)
      .filter((e) => e.program.some((p) => workIds.has(p.workId)))
      .sort(this.byDateTime);
  }
  ```
- Kein neuer Store/Cache (abgeleitete Berechnungen genügen, analog `venuesForFilter`). `Composer` ist bereits importiert.

## Task 5 – Routen ergänzen (app.routes.ts)

Bezug: AK 1, AK 2.

- Zwei lazy-geladene Routen analog zu `works`/`works/:id` ([app.routes.ts:40-49](../../../../web/src/app/app.routes.ts#L40-L49)) ergänzen:
  ```ts
  {
    path: 'composers',
    loadComponent: () => import('./pages/composer-list/composer-list').then((m) => m.ComposerListPage),
    title: 'Komponist:innen · Klangland',
  },
  {
    path: 'composers/:id',
    loadComponent: () => import('./pages/composer-detail/composer-detail').then((m) => m.ComposerDetailPage),
    title: 'Komponist:in · Klangland',
  },
  ```
- Reihenfolge: Liste vor Detail; beide vor der `**`-Catch-all-Route.

## Task 6 – Navigationspunkt „Komponist:innen" (app.html)

Bezug: AK 3.

- In der Hauptnavigation ([app.html:71-75](../../../../web/src/app/app.html#L71-L75)) einen Link ergänzen, konsistent zu den übrigen (mit `routerLinkActive="active"` und `(click)="closeMenu()"`), sinnvolle Position (z. B. nach „Werke"):
  ```html
  <a routerLink="/composers" routerLinkActive="active" (click)="closeMenu()">Komponist:innen</a>
  ```
- `routerLinkActive` markiert `/composers` und `/composers/:id` automatisch (kein `exact` nötig).

## Task 7 – Übersichtsseite (composer-list.{ts,html,css})

Bezug: AK 1, AK 4, AK 5, AK 6, AK 16.

- Komponente `ComposerListPage` analog zu [work-list.ts](../../../../web/src/app/pages/work-list/work-list.ts) (Filter über `FilterService`):
  ```ts
  export class ComposerListPage {
    private data = inject(DataService);
    private filter = inject(FilterService);

    readonly composers = computed(() =>
      this.data.composersForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
    );
    works(c: Composer): Work[] {
      return this.data.worksForComposer(c.id, this.filter.selectedCityIds(), this.filter.selectedProfileIds());
    }
    life(c: Composer): string {
      const l = c.life; if (!l) return '';
      return l.to ? `${l.from}–${l.to}` : `* ${l.from}`;
    }
    portraitUrl(c: Composer): string | null {
      return c.portrait ? `portraits/${c.portrait.file}` : null;
    }
  }
  ```
- Template analog zu [work-list.html](../../../../web/src/app/pages/work-list/work-list.html): `app-page-header` (heading „Komponist:innen", passende `description`), `.card-grid`, je Komponist:in eine anklickbare Kachel `[routerLink]="['/composers', c.id]"`:
  - Portrait `@if (portraitUrl(c); as src)` mit `<img [src]="src" [alt]="c.name + ' – Portrait'" loading="lazy">` (AK 6, AK 16); sonst sauberes Weglassen/Platzhalter.
  - Name (hervorgehoben) + Lebensdaten (`life(c)`).
  - Liste der gespielten Werke (`works(c)`), Werktitel als `<ul>` (AK 6).
  - Leerzustand („Keine Komponist:innen erfasst.") analog Work-/Venue-Liste.
- CSS: `.card-grid`/`.card` wiederverwenden; nur komponisten-spezifische Feinheiten (`.portrait`, `.composer-name`, `.work-list`) am bestehenden Stil orientiert (AK 16).

## Task 8 – Detailseite (composer-detail.{ts,html,css})

Bezug: AK 2, AK 6, AK 7, AK 8, AK 9, AK 14, AK 16.

- Komponente `ComposerDetailPage` analog zu [work-detail.ts](../../../../web/src/app/pages/work-detail/work-detail.ts)/[ensemble-detail](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.ts):
  ```ts
  export class ComposerDetailPage {
    protected readonly data = inject(DataService);
    private route = inject(ActivatedRoute);
    private filter = inject(FilterService);
    private params = toSignal(this.route.paramMap);

    readonly composer = computed<Composer | undefined>(() => {
      const id = this.params()?.get('id');
      return id ? this.data.composer(id) : undefined;
    });
    readonly life = computed(() => { /* wie in Task 7 */ });
    readonly portraitUrl = computed(() => {
      const p = this.composer()?.portrait; return p ? `portraits/${p.file}` : null;
    });
    readonly works = computed(() => {
      const c = this.composer(); return c
        ? this.data.worksForComposer(c.id, this.filter.selectedCityIds(), this.filter.selectedProfileIds()) : [];
    });
    readonly events = computed(() => {
      const c = this.composer(); return c
        ? this.data.eventsForComposer(c.id, this.filter.selectedCityIds(), this.filter.selectedProfileIds()) : [];
    });
  }
  ```
- Template:
  - „nicht gefunden"-Zweig + Zurück-Link `‹ Alle Komponist:innen` (`routerLink="/composers"`) bei `!composer()` (AK 2).
  - `header` mit Name; Portrait `@if (portraitUrl(); as src)` mit `<img>` und darunter **sichtbarer Attribution**, die auf die Quelle verweist (Muster [ensemble-detail.html:57-61](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L57-L61)):
    ```html
    <p class="image-attribution">
      Bild: <a [href]="composer()!.portrait!.source" target="_blank" rel="noopener">Wikimedia Commons / Wikipedia</a>@if (composer()!.portrait!.credit) { – {{ composer()!.portrait!.credit }} }
    </p>
    ```
    (AK 14)
  - `aside.card.profile-facts` mit `<dl>`: Lebensdaten und – je in `@if` gehüllt (AK 7) – Epoche (`composer()!.epoch`). Nicht gepflegte Felder entfallen.
  - Wikipedia-Abschnitt `@if (composer()!.wikipedia; as wiki)` exakt nach dem Ensemble-Muster (Kurzfassung + Quellenverweis + „Zum vollständigen Artikel") (AK 7).
  - **Gespielte Werke** (AK 8): `<section>` mit `<h2>` und `<ul>`, je Werk `<a [routerLink]="['/works', w.id]">{{ w.title }}</a>` (per Tastatur erreichbar).
  - **Veranstaltungen** (AK 9): `events-section` mit `<h2>Veranstaltungen ({{ events().length }})</h2>` und `<app-event-list [events]="events()" />` (Default `showVenue`/`showEnsemble` = true sinnvoll).
- CSS: bestehende Klassen (`profile-head`, `profile-facts`, `wiki-section`, `wiki-attribution`, `events-section`, `back-link`) wiederverwenden; `.portrait`/`.image-attribution` ergänzen (AK 16).

## Task 9 – Werk-Detailseite erweitern (work-detail.{ts,html})

Bezug: AK 10, AK 11, AK 18.

- **Komponisten-Verlinkung (AK 10):** In [work-detail.html](../../../../web/src/app/pages/work-detail/work-detail.html) den Komponistennamen (Header `L9` und `<dd>` `L16`) auf die Detailseite verlinken, sofern die Komponist:in bekannt ist:
  ```html
  @if (composer(); as c) {
    <a [routerLink]="['/composers', c.id]">{{ c.name }}</a>
  } @else {
    {{ composerName() }}
  }
  ```
  (`composer()` ist in [work-detail.ts:26](../../../../web/src/app/pages/work-detail/work-detail.ts#L26) bereits vorhanden.)
- **Anreicherung sichtbar machen (AK 11):**
  - Epoche der Komponist:in als zusätzliche `<dl>`-Zeile, `@if (composer()?.epoch)`.
  - Kennzeichen `popular`/`recommended` (falls gesetzt) als dezente Badges/Zeilen, jeweils in `@if`.
  - Werk-Wikipedia-Kurzfassung: neuen Abschnitt nach dem Ensemble-Muster `@if (work()!.wikipedia; as wiki)` (Kurzfassung + Quellenverweis) ergänzen; die bestehende `description-section` bleibt erhalten.
  - Alle Ergänzungen nur bei gepflegten Feldern; keine leeren Zeilen (AK 11).
- Werke-Übersicht (`/works`) und übrige Seiten bleiben unverändert (AK 18).

## Task 10 – Metadaten, Attribution & Doku

Bezug: AK 14, AK 17.

- [data/composers.json](../../../../data/composers.json): `metadata.version`/`metadata.lastUpdated` hochziehen und `notes` um die Bildquelle (Wikipedia/Wikimedia Commons, lokal persistiert, Attribution über `portrait.source`) ergänzen.
- [docs/data-tooling/README.md](../../../../docs/data-tooling/README.md): im Abschnitt „Datenquellen / Attributierung" die **Komponisten-Portraits** (Quelle Wikipedia/Wikimedia Commons, lokal persistiert, sichtbare Attribution in der UI) sowie das neue Tool `fetch_composer_portraits.py` (inkl. 1-req/s-Limit) aufnehmen. Den in [US-017 Task 5](../done/US-017-tasks.md#L80) notierten Hinweis auflösen: Der Open-Opus-Credit ist mit dieser Story an einer für Nutzer:innen erreichbaren Stelle sichtbar (siehe unten).
- **Sichtbarer Open-Opus-/Quellen-Credit in der UI:** Da die Open-Opus-/Wikipedia-Daten nun dargestellt werden ([US-017 AK 7](../done/US-017-open-opus.md#L57)), einen dezenten Datenquellen-Hinweis („Open Opus", Link `https://openopus.org`; Wikipedia/Wikimedia Commons) an erreichbarer Stelle ergänzen (z. B. Footer oder auf `/composers`). Umfang bewusst klein halten; Bild-Attribution je Bild erfolgt bereits in Task 8 (AK 14).
- Git: Bild-Assets (`data/portraits/`), Skript und redaktionelle Pflege in nachvollziehbaren Commits erfassen (maschineller Lauf und manuelle Pflege getrennt) (AK 17).

## Task 11 – Manuelle Verifikation

- **Download-Tool (AK 13, AK 15):** `python3 docs/data-tooling/fetch_composer_portraits.py` läuft fehlerfrei; erneuter Lauf ist idempotent (kein Re-Download, kein Diff bei unveränderter Quelle). Über Log-/Zeitstempel nachweisen, dass zwischen zwei Netzwerk-Requests **≥ ~1 Sekunde** liegt (Metadaten **und** Bild-Download). Bilder liegen in `data/portraits/`.
- `data/composers.json` ist valides JSON; Stichprobe: mehrere Komponist:innen haben ein `portrait` mit `file` + `source` (AK 12).
- `cd web && npm run build` – kompiliert fehlerfrei; Sync kopiert Portraits nach `web/public/portraits/` (Task 3).
- `cd web && npm start` und im Browser prüfen:
  - Navigationspunkt „Komponist:innen" sichtbar, führt zu `/composers`, Aktiv-Zustand korrekt (AK 3).
  - Übersicht zeigt nur programmierte Komponist:innen, jede einmal (AK 4), alphabetisch nach Name (AK 5); Kachel zeigt Name, Lebensdaten, Portrait (bzw. sauberes Weglassen) und gespielte Werke (AK 6).
  - Ort-/Profil-Filter (US-020) wirkt auf `/composers` und die Werk-/Event-Listen der Detailseite (AK 4).
  - Klick auf Kachel öffnet `/composers/:id` (AK 1, AK 2); unbekannte ID zeigt „nicht gefunden" + Zurück-Link (AK 2).
  - Detailseite: Lebensdaten, ggf. Epoche und Wikipedia-Kurzfassung mit Quellenverweis, ohne leere Zeilen (AK 7); Portrait mit sichtbarer, auf die Quelle verweisender Attribution (AK 14); gespielte Werke verlinken auf `/works/:id` (AK 8); Veranstaltungsliste chronologisch mit Event-Links (AK 9).
  - Werk-Detail (`/works/:id`): Komponistenname verlinkt auf `/composers/:id` (AK 10); Epoche/`popular`/`recommended`/Werk-Wikipedia werden sichtbar, wenn gepflegt (AK 11).
  - Datenquellen-Credit (Open Opus + Bildquelle) an erreichbarer Stelle sichtbar (AK 14, US-017 AK 7).
  - Tastaturbedienung: Kacheln, Werk- und Event-Links per Tab erreichbar, Fokus sichtbar; `<img>` mit `alt` (AK 16).
  - Werke-Übersicht (`/works`) und übrige Seiten unverändert (AK 18).
  - Schmales Fenster: Kachel-Grid, Portraits und Detail-Layout intakt.

## Definition of Done

- Alle Akzeptanzkriterien 1–18 aus [US-024](./us-024-composers-and-works.md) erfüllt.
- `npm run build` ohne Fehler/Warnungen; `data/composers.json` valides JSON.
- Portrait-Download-Tool idempotent, hält das 1-Request-pro-Sekunde-Limit ein und ruft zur Laufzeit keine Fremd-URLs ab (Bilder lokal committet).
- Bilder mit sichtbarer, auf die Quelle verweisender Attribution; Open-Opus-Credit in der UI erreichbar.
- Werke-Übersicht und bestehende Seiten (außer Navigationspunkt, neuen Routen und erweitertem Werk-Detail) unverändert.
- Story-Datei und diese Tasks-Datei nach Abschluss von `doing/` nach `done/` verschieben.
