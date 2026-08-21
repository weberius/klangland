# US-018 – Umsetzungs-Tasks

Umsetzung von [US-018](./US-018-works.md): Werke-Übersicht (`/works`) und Werk-Detailseite (`/works/:id`) analog zu den Spielstätten-Seiten, inkl. Navigationspunkt.

Betroffene / neue Dateien:
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (Zugriffe: programmierte Werke, Events je Werk)
- [web/src/app/app.routes.ts](../../../../web/src/app/app.routes.ts) (neue Routen)
- [web/src/app/app.html](../../../../web/src/app/app.html#L71-L74) (Navigationspunkt)
- **neu** `web/src/app/pages/work-list/work-list.{ts,html,css}` (Vorbild: [venue-list](../../../../web/src/app/pages/venue-list/))
- **neu** `web/src/app/pages/work-detail/work-detail.{ts,html,css}` (Vorbild: [venue-detail](../../../../web/src/app/pages/venue-detail/))

Wiederverwendung: [`app-page-header`](../../../../web/src/app/shared/page-header/page-header.ts), [`app-event-list`](../../../../web/src/app/shared/event-list.ts) (`showVenue`/`showEnsemble` default `true`), `GENRE_LABELS`/`label` aus [labels.ts](../../../../web/src/app/core/labels.ts).

---

## Task 1 – Datenzugriffe im DataService (data.service.ts)

Bezug: AK 5, AK 6, AK 7, AK 9.

- Methode für die Events eines Werks ergänzen (analog zu [`eventsForVenue`](../../../../web/src/app/core/data.service.ts#L350-L352), chronologisch via `byDateTime`):
  ```ts
  /** Chronologische Events, in deren Programm das Werk vorkommt (US-018). */
  eventsForWork(workId: string): ConcertEvent[] {
    return this.events
      .filter((e) => e.program.some((p) => p.workId === workId))
      .sort(this.byDateTime);
  }
  ```
- Getter/Methode für die in der Übersicht anzuzeigenden Werke ergänzen: **nur Werke mit mindestens einem Event**, jedes genau einmal, sortiert nach Komponist, dann Titel:
  ```ts
  /** Programmierte Werke (in >=1 Event), sortiert nach Komponist, dann Titel (US-018). */
  get programmedWorks(): Work[] {
    const ids = new Set<string>();
    for (const e of this.events) for (const p of e.program) ids.add(p.workId);
    return [...ids]
      .map((id) => this.work(id))
      .filter((w): w is Work => !!w)
      .sort((a, b) => {
        const ca = this.composer(a.composerId)?.name ?? '';
        const cb = this.composer(b.composerId)?.name ?? '';
        return ca.localeCompare(cb, 'de') || a.title.localeCompare(b.title, 'de');
      });
  }
  ```
  - `Set` deckt „jedes Werk genau einmal" ab (AK 5); der `filter` entfernt evtl. unbekannte `workId`s.
  - Sortierschlüssel ist `composer.name` (Modell hat keinen Nachnamen – bewusster Kompromiss, siehe US).
- `Work` ist bereits importiert/verfügbar; keine Modelländerung nötig.

## Task 2 – Routen ergänzen (app.routes.ts)

Bezug: AK 1, AK 2.

- Zwei lazy-geladene Routen analog zu `venues`/`venues/:id` ergänzen ([app.routes.ts:26-39](../../../../web/src/app/app.routes.ts#L26-L39)):
  ```ts
  {
    path: 'works',
    loadComponent: () => import('./pages/work-list/work-list').then((m) => m.WorkListPage),
    title: 'Werke · Klangland',
  },
  {
    path: 'works/:id',
    loadComponent: () => import('./pages/work-detail/work-detail').then((m) => m.WorkDetailPage),
    title: 'Werk · Klangland',
  },
  ```
- Reihenfolge: Liste vor Detail; beide vor der `**`-Catch-all-Route.

## Task 3 – Navigationspunkt „Werke" (app.html)

Bezug: AK 3.

- In der Hauptnavigation ([app.html:71-74](../../../../web/src/app/app.html#L71-L74)) einen Link ergänzen, konsistent zu den übrigen (mit `routerLinkActive="active"` und `(click)="closeMenu()"`):
  ```html
  <a routerLink="/works" routerLinkActive="active" (click)="closeMenu()">Werke</a>
  ```
- Sinnvolle Position wählen (z. B. nach „Spielstätten"). `routerLinkActive` markiert `/works` und `/works/:id` automatisch (kein `exact` nötig, wie bei den anderen Detail-Routen).

## Task 4 – Übersichtsseite (work-list.{ts,html,css})

Bezug: AK 4, AK 5, AK 6, AK 7, AK 10.

- Komponente `WorkListPage` analog zu [venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts):
  ```ts
  @Component({
    selector: 'app-work-list',
    imports: [RouterLink, PageHeader],
    templateUrl: './work-list.html',
    styleUrl: './work-list.css',
  })
  export class WorkListPage {
    private data = inject(DataService);
    readonly works = computed(() => this.data.programmedWorks);
    composerName(w: Work): string { return this.data.composer(w.composerId)?.name ?? ''; }
    eventCount(w: Work): number { return this.data.eventsForWork(w.id).length; }
  }
  ```
  - Hinweis: Da `programmedWorks` ein Getter über das (nach Laden konstante) Store ist, ist ein `computed` ausreichend; alternativ direkter Getter-Zugriff im Template.
- Template analog zu [venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html): `app-page-header` (heading „Werke", passende `description`), `.card-grid`, je Werk eine anklickbare Kachel:
  ```html
  <a class="card work-card" [routerLink]="['/works', w.id]">
    <p class="muted composer">{{ composerName(w) }}</p>
    <h2 class="work-title">{{ w.title }}</h2>
    <p class="muted count">
      {{ eventCount(w) }} {{ eventCount(w) === 1 ? 'Veranstaltung' : 'Veranstaltungen' }}
    </p>
  </a>
  ```
  - Komponist hervorgehoben/oben (AK 7), Titel als Kachel-Überschrift, Event-Anzahl mit Singular/Plural (vgl. Venue-Kachel).
  - Leerzustand („Keine Werke erfasst.") analog Venue-Liste.
- CSS: `.card-grid`/`.card` wiederverwenden; nur werk-spezifische Feinheiten (`.composer`, `.work-title`) ergänzen, am Venue-Stil orientiert (AK 10).

## Task 5 – Detailseite (work-detail.{ts,html,css})

Bezug: AK 2, AK 8, AK 9, AK 10.

- Komponente `WorkDetailPage` analog zu [venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts):
  ```ts
  export class WorkDetailPage {
    protected readonly data = inject(DataService);
    private route = inject(ActivatedRoute);
    private params = toSignal(this.route.paramMap);
    readonly work = computed<Work | undefined>(() => {
      const id = this.params()?.get('id');
      return id ? this.data.work(id) : undefined;
    });
    readonly composer = computed(() => this.data.composer(this.work()?.composerId));
    readonly genreLabel = computed(() => { const w = this.work(); return w ? label(GENRE_LABELS, w.genre) : ''; });
    readonly events = computed(() => { const w = this.work(); return w ? this.data.eventsForWork(w.id) : []; });
    // Formatierungen für Werkverzeichnis/Jahre wie in event-detail.ts (formatCatalogue/formatYears)
  }
  ```
- Werkverzeichnis-Nummer(n) und Entstehungszeit werden wie im Programm der Event-Detailseite formatiert ([event-detail.ts:137-147](../../../../web/src/app/pages/event-detail/event-detail.ts#L137-L147)). Zwei Optionen:
  - **A (pragmatisch):** die kleinen Helfer `formatCatalogue`/`formatYears` in `work-detail.ts` spiegeln.
  - **B (sauberer):** diese Helfer in eine geteilte Util auslösen und in event-detail + work-detail nutzen. Nur wählen, wenn ohne größeren Umbau möglich; sonst A.
- Template analog zu [venue-detail.html](../../../../web/src/app/pages/venue-detail/venue-detail.html):
  - „nicht gefunden"-Zweig + Zurück-Link `‹ Alle Werke` (`routerLink="/works"`) bei `!work()` (AK 2).
  - `header` mit Titel und Komponist.
  - `aside.card.profile-facts` mit `<dl>`; jede Zeile in `@if` gehüllt, damit nicht gepflegte Felder entfallen (AK 8): Werkverzeichnis (`catalogue.length`), Entstehungszeit (`yearComposed`), Genre (`genreLabel()`), Dauer (`durationMinutes`, z. B. „X Min."), Fassung (`version`), Besetzung (`scoring`).
  - Beschreibung (`description`) als eigener Absatz, wenn vorhanden.
  - `events-section` mit `<h2>Veranstaltungen ({{ events().length }})</h2>` und `<app-event-list [events]="events()" />` (Venue-Spalte hier sinnvoll sichtbar, daher Default `showVenue=true`) (AK 9).
- CSS: bestehende Klassen (`profile-head`, `profile-facts`, `events-section`, `back-link`) wiederverwenden (AK 10).

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` und im Browser prüfen:
  - Navigationspunkt „Werke" sichtbar, führt zu `/works`, Aktiv-Zustand korrekt (AK 3).
  - Übersicht zeigt Kacheln nur für Werke mit Events, jedes einmal (AK 5), sortiert nach Komponist dann Titel (AK 6); Kachel zeigt Komponist, Titel, Event-Anzahl mit korrektem Plural (AK 7).
  - Klick auf Kachel öffnet `/works/:id` (AK 4).
  - Detailseite zeigt gepflegte Werk-Infos ohne leere Zeilen (AK 8) und die Veranstaltungsliste mit Links zu den Events (AK 9).
  - Unbekannte ID (`/works/xyz`) zeigt „nicht gefunden" + Zurück-Link (AK 2).
  - Tastaturbedienung: Kacheln/Links per Tab erreichbar, Fokus sichtbar (AK 10).
  - Bestehende Seiten (Kalender, Ensembles, Spielstätten, Karte, Event-Detail) unverändert (AK 11).
  - Schmales Fenster: Kachel-Grid und Detail-Layout intakt.

## Definition of Done

- Alle Akzeptanzkriterien 1–11 aus [US-018](./US-018-works.md) erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen am `Work`-Datenmodell oder an bestehenden Seiten (außer dem neuen Navigationspunkt und den neuen Routen).
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben.
