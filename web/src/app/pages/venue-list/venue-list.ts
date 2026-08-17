import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { Venue } from '../../models/models';
import { VENUE_TYPE_LABELS, label } from '../../core/labels';

@Component({
  selector: 'app-venue-list',
  imports: [RouterLink],
  templateUrl: './venue-list.html',
  styleUrl: './venue-list.css',
})
export class VenueListPage {
  private data = inject(DataService);

  readonly venues = computed(() => this.data.venues);

  cityName(v: Venue): string {
    return this.data.cityNames(v.cityIds) || v.region || '';
  }
  typeLabel(v: Venue): string {
    return label(VENUE_TYPE_LABELS, v.type);
  }
  eventCount(v: Venue): number {
    return this.data.eventsForVenue(v.id).length;
  }
}
