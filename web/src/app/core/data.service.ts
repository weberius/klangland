import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom, forkJoin } from 'rxjs';

import {
  City, Composer, ConcertEvent, Ensemble, Institution, Metadata, MusicalProfile, Person, Venue, Work,
} from '../models/models';
import { MUSICAL_PROFILE_LABELS } from './labels';
import { APP_CONFIG } from './app-config';
import { formatAddress } from './address';

export type SearchDocumentKind = 'event' | 'ensemble' | 'venue';

export interface SearchDocument {
  id: string;
  kind: SearchDocumentKind;
  title: string;
  subtitle: string;
  route: readonly [string, string];
  searchText: string;
}

interface Store {
  metadata: Metadata | null;
  cities: Map<string, City>;
  people: Map<string, Person>;
  institutions: Map<string, Institution>;
  ensembles: Map<string, Ensemble>;
  venues: Map<string, Venue>;
  composers: Map<string, Composer>;
  works: Map<string, Work>;
  events: ConcertEvent[];
  searchDocuments: SearchDocument[];
}

function index<T extends { id: string }>(items: T[]): Map<string, T> {
  return new Map(items.map((i) => [i.id, i]));
}

function normalizeSource(event: ConcertEvent): ConcertEvent['source'] {
  if (!event.source) return null;
  return {
    url: event.source.url,
    calendarUrl: event.source.calendarUrl ?? null,
    name: event.source.name || 'Unbekannte Quelle',
    retrievedAt: event.source.retrievedAt || event.lastVerified || '',
  };
}

function normalizeEvent(event: ConcertEvent): ConcertEvent {
  return {
    ...event,
    conductorPersonIds: event.conductorPersonIds ?? [],
    soloistPersonIds: event.soloistPersonIds ?? [],
    program: event.program ?? [],
    seriesId: event.seriesId ?? null,
    description: event.description ?? null,
    source: normalizeSource(event),
    ticketUrl: event.ticketUrl ?? null,
    lastVerified: event.lastVerified ?? event.source?.retrievedAt ?? null,
  };
}

function joinDefined(values: Array<string | null | undefined>, separator: string): string {
  return values
    .map((value) => value?.trim())
    .filter((value): value is string => Boolean(value))
    .join(separator);
}

function buildSearchDocuments(params: {
  events: ConcertEvent[];
  cities: Map<string, City>;
  people: Map<string, Person>;
  ensembles: Map<string, Ensemble>;
  venues: Map<string, Venue>;
  composers: Map<string, Composer>;
  works: Map<string, Work>;
}): SearchDocument[] {
  const {
    events, cities, people, ensembles, venues, composers, works,
  } = params;
  const documents: SearchDocument[] = [];

  for (const event of events) {
    const venueName = venues.get(event.venueId)?.name ?? '';
    const cityName = cities.get(event.cityId)?.name ?? '';
    const ensembleNames = event.ensembleIds
      .map((id) => ensembles.get(id)?.name ?? '')
      .filter((name) => name.length > 0);
    const conductorNames = event.conductorPersonIds
      .map((id) => people.get(id)?.name ?? '')
      .filter((name) => name.length > 0);
    const soloistNames = event.soloistPersonIds
      .map((id) => people.get(id)?.name ?? '')
      .filter((name) => name.length > 0);
    const workSearchParts = event.program.flatMap((item) => {
      const work = works.get(item.workId);
      if (!work) return [];
      const composerName = composers.get(work.composerId)?.name ?? '';
      return [work.title, composerName];
    });

    documents.push({
      id: event.id,
      kind: 'event',
      title: event.title,
      subtitle: joinDefined(
        [
          event.date,
          event.startTime ? `${event.startTime} Uhr` : null,
          ensembleNames.join(', '),
          joinDefined([venueName, cityName], ', '),
        ],
        ' · ',
      ),
      route: ['/events', event.id],
      searchText: joinDefined(
        [
          event.title,
          event.description,
          event.status,
          event.source?.name,
          venueName,
          cityName,
          ensembleNames.join(' '),
          conductorNames.join(' '),
          soloistNames.join(' '),
          workSearchParts.join(' '),
        ],
        ' ',
      ),
    });
  }

  for (const ensemble of ensembles.values()) {
    const cityNames = ensemble.cityIds
      .map((id) => cities.get(id)?.name ?? '')
      .filter((name) => name.length > 0);
    const chiefConductorName = ensemble.chiefConductorPersonId
      ? (people.get(ensemble.chiefConductorPersonId)?.name ?? '')
      : '';

    documents.push({
      id: ensemble.id,
      kind: 'ensemble',
      title: ensemble.name,
      subtitle: joinDefined([cityNames.join(' / '), ensemble.country], ', '),
      route: ['/ensembles', ensemble.id],
      searchText: joinDefined(
        [
          ensemble.name,
          ensemble.description,
          ensemble.type,
          ensemble.roles.join(' '),
          ensemble.musicalProfiles.join(' '),
          chiefConductorName,
          cityNames.join(' '),
          ensemble.region,
          ensemble.country,
        ],
        ' ',
      ),
    });
  }

  for (const venue of venues.values()) {
    const cityNames = venue.cityIds
      .map((id) => cities.get(id)?.name ?? '')
      .filter((name) => name.length > 0);
    const addressLine = formatAddress(venue.address);

    documents.push({
      id: venue.id,
      kind: 'venue',
      title: venue.name,
      subtitle: joinDefined([cityNames.join(' / '), addressLine], ' · '),
      route: ['/venues', venue.id],
      searchText: joinDefined(
        [
          venue.name,
          addressLine,
          venue.region,
          venue.type,
          cityNames.join(' '),
        ],
        ' ',
      ),
    });
  }

  return documents;
}

/**
 * Lädt alle JSON-Stammdaten einmalig und stellt Lookups sowie
 * beziehungsauflösende Hilfsmethoden bereit. Die App ist statisch;
 * es gibt keine Schreiblogik.
 */
@Injectable({ providedIn: 'root' })
export class DataService {
  private http = inject(HttpClient);

  private readonly _store = signal<Store | null>(null);
  private readonly _error = signal(false);

  readonly loaded = computed(() => this._store() !== null);
  readonly hasError = this._error.asReadonly();

  async load(): Promise<void> {
    if (this._store()) return;
    const base = APP_CONFIG.dataBasePath;
    const get = <T>(file: string) => this.http.get<T>(`${base}/${file}`);
    try {
      const r = await firstValueFrom(
        forkJoin({
          cities: get<{ metadata: Metadata; cities: City[] }>('cities.json'),
          people: get<{ people: Person[] }>('people.json'),
          institutions: get<{ institutions: Institution[] }>('institutions.json'),
          ensembles: get<{ ensembles: Ensemble[] }>('ensembles.json'),
          venues: get<{ venues: Venue[] }>('venues.json'),
          composers: get<{ composers: Composer[] }>('composers.json'),
          works: get<{ works: Work[] }>('works.json'),
          events: get<{ metadata: Metadata; events: ConcertEvent[] }>('events.json'),
        }),
      );
      const cities = index(r.cities.cities);
      const people = index(r.people.people);
      const institutions = index(r.institutions.institutions);
      const ensembles = index(r.ensembles.ensembles);
      const venues = index(r.venues.venues);
      const composers = index(r.composers.composers);
      const works = index(r.works.works);
      const events = r.events.events.map(normalizeEvent);

      this._store.set({
        metadata: r.events.metadata ?? null,
        cities,
        people,
        institutions,
        ensembles,
        venues,
        composers,
        works,
        events,
        searchDocuments: buildSearchDocuments({
          events,
          cities,
          people,
          ensembles,
          venues,
          composers,
          works,
        }),
      });
    } catch (e) {
      console.error('Daten konnten nicht geladen werden', e);
      this._error.set(true);
    }
  }

  private get store(): Store | null {
    return this._store();
  }

  // ---- Basis-Lookups -------------------------------------------------------

  city(id: string | null | undefined): City | undefined {
    return id ? this.store?.cities.get(id) : undefined;
  }
  person(id: string | null | undefined): Person | undefined {
    return id ? this.store?.people.get(id) : undefined;
  }
  institution(id: string | null | undefined): Institution | undefined {
    return id ? this.store?.institutions.get(id) : undefined;
  }
  ensemble(id: string | null | undefined): Ensemble | undefined {
    return id ? this.store?.ensembles.get(id) : undefined;
  }
  venue(id: string | null | undefined): Venue | undefined {
    return id ? this.store?.venues.get(id) : undefined;
  }
  composer(id: string | null | undefined): Composer | undefined {
    return id ? this.store?.composers.get(id) : undefined;
  }
  work(id: string | null | undefined): Work | undefined {
    return id ? this.store?.works.get(id) : undefined;
  }
  event(id: string): ConcertEvent | undefined {
    return this.store?.events.find((e) => e.id === id);
  }

  // ---- Listen --------------------------------------------------------------

  get ensembles(): Ensemble[] {
    return [...(this.store?.ensembles.values() ?? [])].sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }
  get venues(): Venue[] {
    return [...(this.store?.venues.values() ?? [])].sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }
  get institutionsList(): Institution[] {
    return [...(this.store?.institutions.values() ?? [])].sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }

  /** Trägerinstitution eines Ensembles (Rückbezug über institution.ensembleIds). */
  institutionForEnsemble(ensembleId: string): Institution | undefined {
    for (const inst of this.store?.institutions.values() ?? []) {
      if (inst.ensembleIds.includes(ensembleId)) return inst;
    }
    return undefined;
  }
  get events(): ConcertEvent[] {
    return this.store?.events ?? [];
  }
  get seasonLabel(): string | null {
    return this.store?.metadata?.season ?? null;
  }
  get searchDocuments(): SearchDocument[] {
    return this.store?.searchDocuments ?? [];
  }

  // ---- Beziehungen / abgeleitete Werte ------------------------------------

  /** Anzeigename für einen oder mehrere Orte (kommagetrennt). */
  cityNames(ids: string[] | null | undefined): string {
    if (!ids || ids.length === 0) return '';
    return ids.map((id) => this.city(id)?.name ?? id).join(' / ');
  }

  personNames(ids: string[] | null | undefined): string[] {
    if (!ids || ids.length === 0) return [];
    return ids.map((id) => this.person(id)?.name ?? id);
  }

  ensembleNames(ids: string[] | null | undefined): string[] {
    if (!ids || ids.length === 0) return [];
    return ids.map((id) => this.ensemble(id)?.name ?? id);
  }

  /** Chronologisch sortierte Events eines Monats (year, month 1-12). */
  eventsInMonth(year: number, month: number): ConcertEvent[] {
    const prefix = `${year}-${String(month).padStart(2, '0')}`;
    return this.events
      .filter((e) => e.date.startsWith(prefix))
      .sort(this.byDateTime);
  }

  eventsForEnsemble(ensembleId: string): ConcertEvent[] {
    return this.events.filter((e) => e.ensembleIds.includes(ensembleId)).sort(this.byDateTime);
  }

  eventsForVenue(venueId: string): ConcertEvent[] {
    return this.events.filter((e) => e.venueId === venueId).sort(this.byDateTime);
  }

  /** Chronologische Events, in deren Programm das Werk vorkommt (US-018). */
  eventsForWork(workId: string): ConcertEvent[] {
    return this.events
      .filter((e) => e.program.some((p) => p.workId === workId))
      .sort(this.byDateTime);
  }

  /**
   * Programmierte Werke, eingegrenzt über den Ort-/Profil-Filter (US-018/US-020) – Quelle
   * des Werke-Kachel-Grids. Berücksichtigt werden Werke, die in mindestens einem gefilterten
   * Event-Programm vorkommen; leere Auswahl = alle programmierten Werke (analog zu
   * venuesForFilter). Jedes Werk erscheint genau einmal (Set); sortiert nach Komponist und –
   * bei gleichem Komponisten – nach Werktitel (deutsch). Der filter entfernt unbekannte workIds.
   */
  worksForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Work[] {
    const ids = new Set<string>();
    for (const e of this.eventsForFilter(cityIds, profileIds)) {
      for (const p of e.program) ids.add(p.workId);
    }
    return [...ids]
      .map((id) => this.work(id))
      .filter((w): w is Work => Boolean(w))
      .sort((a, b) => {
        const byComposer = (this.composer(a.composerId)?.name ?? '').localeCompare(
          this.composer(b.composerId)?.name ?? '',
          'de',
        );
        return byComposer !== 0 ? byComposer : a.title.localeCompare(b.title, 'de');
      });
  }

  /**
   * Komponist:innen mit >=1 programmierten Werk (unter Ort-/Profil-Filter) – Quelle des
   * Komponist:innen-Kachel-Grids (US-024). Baut auf worksForFilter auf und erbt damit die
   * Filter-/Saison-Semantik (leere Auswahl = alle programmierten Komponist:innen). Das Set
   * sichert „jede:r genau einmal"; sortiert nach Name (deutsch).
   */
  composersForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Composer[] {
    const ids = new Set<string>();
    for (const w of this.worksForFilter(cityIds, profileIds)) ids.add(w.composerId);
    return [...ids]
      .map((id) => this.composer(id))
      .filter((c): c is Composer => Boolean(c))
      .sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }

  /** Programmierte Werke einer Komponist:in (unter Filter), sortiert nach Titel (US-024). */
  worksForComposer(
    composerId: string,
    cityIds: ReadonlySet<string>,
    profileIds: ReadonlySet<string>,
  ): Work[] {
    return this.worksForFilter(cityIds, profileIds)
      .filter((w) => w.composerId === composerId)
      .sort((a, b) => a.title.localeCompare(b.title, 'de'));
  }

  /** Chronologische Events (unter Filter), in deren Programm ein Werk der Komponist:in vorkommt (US-024). */
  eventsForComposer(
    composerId: string,
    cityIds: ReadonlySet<string>,
    profileIds: ReadonlySet<string>,
  ): ConcertEvent[] {
    const workIds = new Set(this.worksForComposer(composerId, cityIds, profileIds).map((w) => w.id));
    return this.eventsForFilter(cityIds, profileIds)
      .filter((e) => e.program.some((p) => workIds.has(p.workId)))
      .sort(this.byDateTime);
  }

  /** Alle Events eines Tages (ISO). */
  eventsOnDate(iso: string): ConcertEvent[] {
    return this.events.filter((e) => e.date === iso).sort(this.byDateTime);
  }

  private byDateTime = (a: ConcertEvent, b: ConcertEvent): number => {
    if (a.date !== b.date) return a.date < b.date ? -1 : 1;
    return (a.startTime ?? '').localeCompare(b.startTime ?? '');
  };

  /** Stammsaal-Venue eines Ensembles. */
  homeVenue(ensemble: Ensemble): Venue | undefined {
    return this.venue(ensemble.venueId);
  }

  // ---- Kombinierter Filter (US-020) ----------------------------------------
  // Der Filter wirkt über die auftretenden Ensembles: Ort = Sitzort der Ensembles
  // (ensemble.cityIds), Profil = ensemble.musicalProfiles. Verknüpfung: ODER
  // innerhalb einer Kategorie, UND zwischen den Kategorien – wobei Ort und Profil
  // von demselben Ensemble erfüllt sein müssen. Eine leere Kategorie schränkt nicht
  // ein; sind beide leer, gilt in allen *ForFilter-Methoden „alles anzeigen".

  /**
   * Städte, in denen mindestens ein Ensemble seinen Sitz hat UND die ein
   * Kfz-Kennzeichen tragen – Quelle der Ort-Chips im Popover. Städte, die nur als
   * Veranstaltungsort auftreten oder kein Kennzeichen haben, sind ausgeschlossen.
   * Sortiert nach Anzeigename.
   */
  filterCities(): City[] {
    const ids = new Set<string>();
    for (const ensemble of this.store?.ensembles.values() ?? []) {
      for (const cityId of ensemble.cityIds) ids.add(cityId);
    }
    return [...ids]
      .map((id) => this.city(id))
      .filter((c): c is City => Boolean(c && c.plate))
      .sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }

  /**
   * Städte mit mindestens einem ansässigen Ensemble UND hinterlegten Koordinaten –
   * Quelle der roten Kartenmarker (US-013). Spielstätten-Orte ohne eigenes Ensemble
   * sowie Ensemble-Orte ohne Koordinaten bleiben unberücksichtigt. Sortiert nach Name.
   */
  mapCities(): City[] {
    const ids = new Set<string>();
    for (const ensemble of this.store?.ensembles.values() ?? []) {
      for (const cityId of ensemble.cityIds) ids.add(cityId);
    }
    return [...ids]
      .map((id) => this.city(id))
      .filter((c): c is City => Boolean(c?.coordinates))
      .sort((a, b) => a.name.localeCompare(b.name, 'de'));
  }

  /** Ensembles mit Sitz in der angegebenen Stadt, sortiert nach Name. */
  ensemblesInCity(cityId: string): Ensemble[] {
    return this.ensembles.filter((e) => e.cityIds.includes(cityId));
  }

  /**
   * Musikprofile, die bei mindestens einem Ensemble tatsächlich vorkommen –
   * Quelle der Profil-Chips im Popover. Nicht vorkommende Profile fehlen.
   * Sortiert nach deutschem Label.
   */
  filterProfiles(): { id: MusicalProfile; label: string }[] {
    const ids = new Set<MusicalProfile>();
    for (const ensemble of this.store?.ensembles.values() ?? []) {
      for (const profile of ensemble.musicalProfiles) ids.add(profile);
    }
    return [...ids]
      .map((id) => ({ id, label: MUSICAL_PROFILE_LABELS[id] }))
      .sort((a, b) => a.label.localeCompare(b.label, 'de'));
  }

  /**
   * Events, bei denen mindestens ein auftretendes Ensemble die Filterkombination
   * erfüllt (Gastspiele erscheinen also unter dem Sitzort). Leere Auswahl = alle.
   */
  eventsForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): ConcertEvent[] {
    if (cityIds.size === 0 && profileIds.size === 0) return this.events;
    return this.events.filter((e) =>
      e.ensembleIds.some((id) => {
        const ensemble = this.ensemble(id);
        return ensemble ? this.ensembleMatches(ensemble, cityIds, profileIds) : false;
      }),
    );
  }

  /** Ensembles, die die Filterkombination erfüllen. Leere Auswahl = alle. */
  ensemblesForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Ensemble[] {
    if (cityIds.size === 0 && profileIds.size === 0) return this.ensembles;
    return this.ensembles.filter((e) => this.ensembleMatches(e, cityIds, profileIds));
  }

  /**
   * Spielstätten, in denen Ensembles auftreten, die die Filterkombination erfüllen
   * (über eventsForFilter → venueId), unabhängig vom Standort der Spielstätte.
   * Leere Auswahl = alle Spielstätten.
   */
  venuesForFilter(cityIds: ReadonlySet<string>, profileIds: ReadonlySet<string>): Venue[] {
    if (cityIds.size === 0 && profileIds.size === 0) return this.venues;
    const venueIds = new Set(this.eventsForFilter(cityIds, profileIds).map((e) => e.venueId));
    return this.venues.filter((v) => venueIds.has(v.id));
  }

  /**
   * Erfüllt ein einzelnes Ensemble die Filterkombination? Ort UND Profil müssen von
   * demselben Ensemble erfüllt sein; eine leere Kategorie schränkt nicht ein.
   */
  private ensembleMatches(
    ensemble: Ensemble,
    cityIds: ReadonlySet<string>,
    profileIds: ReadonlySet<string>,
  ): boolean {
    const cityOk = cityIds.size === 0 || ensemble.cityIds.some((id) => cityIds.has(id));
    const profileOk =
      profileIds.size === 0 || ensemble.musicalProfiles.some((p) => profileIds.has(p));
    return cityOk && profileOk;
  }
}
