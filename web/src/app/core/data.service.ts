import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom, forkJoin } from 'rxjs';

import {
  City, Composer, ConcertEvent, Ensemble, Institution, Metadata, Person, Venue, Work,
} from '../models/models';
import { APP_CONFIG } from './app-config';

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
}

function index<T extends { id: string }>(items: T[]): Map<string, T> {
  return new Map(items.map((i) => [i.id, i]));
}

function normalizeSource(event: ConcertEvent): ConcertEvent['source'] {
  if (!event.source) return null;
  return {
    url: event.source.url,
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
      this._store.set({
        metadata: r.events.metadata ?? null,
        cities: index(r.cities.cities),
        people: index(r.people.people),
        institutions: index(r.institutions.institutions),
        ensembles: index(r.ensembles.ensembles),
        venues: index(r.venues.venues),
        composers: index(r.composers.composers),
        works: index(r.works.works),
        events: r.events.events.map(normalizeEvent),
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
}
