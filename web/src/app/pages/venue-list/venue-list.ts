import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Venue } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';
import { VENUE_TYPE_LABELS, label } from '../../core/labels';

@Component({
  selector: 'app-venue-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './venue-list.html',
  styleUrl: './venue-list.css',
})
export class VenueListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly venues = computed(() =>
    this.data.venuesForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
  );

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
