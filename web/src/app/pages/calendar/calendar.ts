import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { APP_CONFIG } from '../../core/app-config';
import { ConcertEvent } from '../../models/models';
import {
  WEEKDAYS_SHORT_DE, addMonths, formatMonthYear, isoDate, pad2, parseIso, weekdayMondayFirst,
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
  imports: [RouterLink],
  templateUrl: './calendar.html',
  styleUrl: './calendar.css',
})
export class CalendarPage {
  protected readonly data = inject(DataService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  readonly weekdays = WEEKDAYS_SHORT_DE;

  /** Heutiges Datum (ISO) – konfigurierbares Referenzdatum oder Systemdatum. */
  readonly todayIso = ((): string => {
    if (APP_CONFIG.referenceDate) return APP_CONFIG.referenceDate;
    const now = new Date();
    return isoDate(now.getFullYear(), now.getMonth() + 1, now.getDate());
  })();

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
        events: this.data.eventsOnDate(iso),
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
      const events = this.data.eventsOnDate(iso);
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

  readonly monthEventCount = computed(() =>
    this.data.eventsInMonth(this.current().year, this.current().month).length,
  );

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

  protected readonly pad2 = pad2;
}
