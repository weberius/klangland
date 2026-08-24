import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { EventList } from '../../shared/event-list';
import { VenueLocation } from '../../shared/venue-location/venue-location';
import { Institution, Venue } from '../../models/models';
import { INSTITUTION_TYPE_LABELS, VENUE_TYPE_LABELS, label } from '../../core/labels';
import { formatAddress } from '../../core/address';

@Component({
  selector: 'app-venue-detail',
  imports: [RouterLink, EventList, VenueLocation],
  templateUrl: './venue-detail.html',
  styleUrl: './venue-detail.css',
})
export class VenueDetailPage {
  protected readonly data = inject(DataService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  readonly venue = computed<Venue | undefined>(() => {
    const id = this.params()?.get('id');
    return id ? this.data.venue(id) : undefined;
  });

  readonly typeLabel = computed(() => {
    const v = this.venue();
    return v ? label(VENUE_TYPE_LABELS, v.type) : '';
  });
  readonly cityName = computed(() => {
    const v = this.venue();
    return v ? this.data.cityNames(v.cityIds) || v.region || '' : '';
  });
  readonly addressLine = computed(() => formatAddress(this.venue()?.address));
  readonly institution = computed<Institution | undefined>(() => this.data.institution(this.venue()?.institutionId));
  readonly institutionType = computed(() => {
    const inst = this.institution();
    return inst ? label(INSTITUTION_TYPE_LABELS, inst.type) : '';
  });

  readonly events = computed(() => {
    const v = this.venue();
    return v ? this.data.eventsForVenue(v.id) : [];
  });
}
