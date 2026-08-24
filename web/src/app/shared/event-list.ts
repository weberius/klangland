import { Component, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../core/data.service';
import { FavoritesService } from '../core/favorites.service';
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
  private favorites = inject(FavoritesService);

  readonly events = input.required<ConcertEvent[]>();
  readonly showEnsemble = input(true);
  readonly showVenue = input(true);

  formatLongDate = formatLongDate;

  /** Ob das Event als Favorit markiert ist (US-027, konsistent mit anderen Listen). */
  isFavorite(e: ConcertEvent): boolean {
    return this.favorites.isFavorite(e.id);
  }

  /**
   * Togglet den Favoritenstatus direkt in der Liste (US-027, AK 3). Verhindert, dass der
   * Klick zusätzlich den umschließenden Zeilen-Link zur Event-Detailseite auslöst.
   */
  toggleFavorite(e: ConcertEvent, event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    this.favorites.toggle(e.id);
  }

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
