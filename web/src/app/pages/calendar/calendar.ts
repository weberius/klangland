import { Component, computed, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { FavoritesService } from '../../core/favorites.service';
import { APP_CONFIG } from '../../core/app-config';
import { ConcertEvent } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';
import {
  WEEKDAYS_SHORT_DE, addMonths, formatMonthYear, isoDate, pad2, parseIso, todayIso, weekdayMondayFirst,
} from '../../core/date-util';

interface DayCell {
  day: number;
  iso: string;
  inMonth: boolean;
  isToday: boolean;
  events: ConcertEvent[];
}

interface AgendaDay {
  iso: string;
  day: number;
  weekdayShort: string;
  events: ConcertEvent[];
}

@Component({
  selector: 'app-calendar',
  imports: [RouterLink, PageHeader],
  templateUrl: './calendar.html',
  styleUrl: './calendar.css',
})
export class CalendarPage {
  protected readonly data = inject(DataService);
  private readonly filter = inject(FilterService);
  private readonly favorites = inject(FavoritesService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  /**
   * Nach der aktiven Ort-/Profil-Auswahl (Sitzort der Ensembles) gefilterte
   * Events, gruppiert nach Datum und je Tag chronologisch sortiert. Leere
   * Auswahl = alle Events. Ist zusätzlich der Favoriten-Filter aktiv (US-021),
   * bleiben nur favorisierte Events übrig (UND-Kombination mit Ort/Profil).
   */
  private readonly eventsByDate = computed(() => {
    const map = new Map<string, ConcertEvent[]>();
    const onlyFavorites = this.favorites.onlyFavorites();
    for (const e of this.data.eventsForFilter(
      this.filter.selectedCityIds(),
      this.filter.selectedProfileIds(),
    )) {
      if (onlyFavorites && !this.favorites.isFavorite(e.id)) continue;
      const list = map.get(e.date);
      if (list) list.push(e);
      else map.set(e.date, [e]);
    }
    for (const list of map.values()) {
      list.sort((a, b) => (a.startTime ?? '').localeCompare(b.startTime ?? ''));
    }
    return map;
  });

  private eventsOnDate(iso: string): ConcertEvent[] {
    return this.eventsByDate().get(iso) ?? [];
  }

  readonly weekdays = WEEKDAYS_SHORT_DE;

  /** Anzahl der im eingeklappten Zustand sichtbaren Termine pro Tageszelle. */
  protected readonly VISIBLE = 2;

  /** ISO-Daten der aktuell aufgeklappten Tageszellen (Desktop-Tabelle). */
  private readonly expandedDays = signal<ReadonlySet<string>>(new Set());

  constructor() {
    // AK 6: Beim Monatswechsel den Aufklapp-Zustand zurücksetzen.
    let firstRun = true;
    effect(() => {
      this.current();
      if (firstRun) {
        firstRun = false;
        return;
      }
      this.expandedDays.set(new Set());
    });
  }

  isExpanded(iso: string): boolean {
    return this.expandedDays().has(iso);
  }

  toggleDay(iso: string): void {
    const next = new Set(this.expandedDays());
    if (next.has(iso)) {
      next.delete(iso);
    } else {
      next.add(iso);
    }
    this.expandedDays.set(next);
  }

  /** Heutiges Datum (ISO) – konfigurierbares Referenzdatum oder Systemdatum. */
  readonly todayIso = todayIso(APP_CONFIG.referenceDate);

  /** Angezeigter Monat aus der Route oder – falls nicht gesetzt – der aktuelle Monat. */
  readonly current = computed<{ year: number; month: number }>(() => {
    const p = this.params();
    const y = Number(p?.get('year'));
    const m = Number(p?.get('month'));
    if (Number.isInteger(y) && Number.isInteger(m) && m >= 1 && m <= 12) {
      return { year: y, month: m };
    }
    const t = parseIso(this.todayIso);
    return { year: t.year, month: t.month };
  });

  readonly monthLabel = computed(() => formatMonthYear(this.current().year, this.current().month));

  /** Hinter dem Info-Button verborgene Seitenbeschreibung. */
  readonly pageDescription = computed(() => {
    const base = 'Professionelle Orchester in Nordrhein-Westfalen';
    const season = this.data.seasonLabel;
    return season ? `${base} · Spielzeit ${season}` : base;
  });

  readonly prevLink = computed(() => {
    const { year, month } = addMonths(this.current().year, this.current().month, -1);
    return ['/calendar', year, month];
  });
  readonly nextLink = computed(() => {
    const { year, month } = addMonths(this.current().year, this.current().month, 1);
    return ['/calendar', year, month];
  });

  /** Wochenraster Montag–Sonntag, inkl. angrenzender Tage der Nachbarmonate. */
  readonly weeks = computed<DayCell[][]>(() => {
    const { year, month } = this.current();
    const firstWeekday = weekdayMondayFirst(year, month, 1);
    const start = new Date(year, month - 1, 1 - firstWeekday);

    const dim = new Date(year, month, 0).getDate();
    const totalCells = Math.ceil((firstWeekday + dim) / 7) * 7;

    const cells: DayCell[] = [];
    for (let i = 0; i < totalCells; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      const iso = isoDate(d.getFullYear(), d.getMonth() + 1, d.getDate());
      cells.push({
        day: d.getDate(),
        iso,
        inMonth: d.getMonth() === month - 1,
        isToday: iso === this.todayIso,
        events: this.eventsOnDate(iso),
      });
    }

    const weeks: DayCell[][] = [];
    for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
    return weeks;
  });

  /** Agenda-Ansicht (mobil): nur Tage des Monats mit Veranstaltungen. */
  readonly agenda = computed<AgendaDay[]>(() => {
    const { year, month } = this.current();
    const days: AgendaDay[] = [];
    const dim = new Date(year, month, 0).getDate();
    for (let day = 1; day <= dim; day++) {
      const iso = isoDate(year, month, day);
      const events = this.eventsOnDate(iso);
      if (events.length) {
        days.push({
          iso,
          day,
          weekdayShort: WEEKDAYS_SHORT_DE[weekdayMondayFirst(year, month, day)],
          events,
        });
      }
    }
    return days;
  });

  readonly monthEventCount = computed(() => {
    const { year, month } = this.current();
    const prefix = `${year}-${pad2(month)}`;
    let count = 0;
    for (const [iso, events] of this.eventsByDate()) {
      if (iso.startsWith(prefix)) count += events.length;
    }
    return count;
  });

  // Anzeigehilfen ------------------------------------------------------------

  ensembleName(e: ConcertEvent): string {
    return this.data.ensembleNames(e.ensembleIds)[0] ?? '';
  }
  conductorName(e: ConcertEvent): string {
    return this.data.personNames(e.conductorPersonIds)[0] ?? '';
  }
  cityName(e: ConcertEvent): string {
    return this.data.city(e.cityId)?.name ?? '';
  }
  time(e: ConcertEvent): string {
    return e.startTime ?? '';
  }
  eventLink(e: ConcertEvent): unknown[] {
    return ['/events', e.id];
  }
  /** Ob ein Event in der Übersicht als Favorit gekennzeichnet wird (US-021). */
  isFavorite(e: ConcertEvent): boolean {
    return this.favorites.isFavorite(e.id);
  }

  protected readonly pad2 = pad2;
}
