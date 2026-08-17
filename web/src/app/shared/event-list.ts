import { Component, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../core/data.service';
import { ConcertEvent } from '../models/models';
import { formatLongDate } from '../core/date-util';
import { EVENT_STATUS_LABELS, label } from '../core/labels';

/** Kompakte, chronologische Liste von Veranstaltungen (für Profile). */
@Component({
  selector: 'app-event-list',
  imports: [RouterLink],
  templateUrl: './event-list.html',
  styleUrl: './event-list.css',
})
export class EventList {
  private data = inject(DataService);

  readonly events = input.required<ConcertEvent[]>();
  readonly showEnsemble = input(true);
  readonly showVenue = input(true);

  formatLongDate = formatLongDate;

  ensembleName(e: ConcertEvent): string {
    return this.data.ensembleNames(e.ensembleIds).join(', ');
  }
  venueName(e: ConcertEvent): string {
    return this.data.venue(e.venueId)?.name ?? '';
  }
  cityName(e: ConcertEvent): string {
    return this.data.city(e.cityId)?.name ?? '';
  }
  conductorName(e: ConcertEvent): string {
    return this.data.personNames(e.conductorPersonIds).join(', ');
  }
  statusLabel(e: ConcertEvent): string {
    return e.status === 'scheduled' ? '' : label(EVENT_STATUS_LABELS, e.status);
  }
}
