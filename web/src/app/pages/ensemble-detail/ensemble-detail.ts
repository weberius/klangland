import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { EventList } from '../../shared/event-list';
import { Ensemble, Institution, Venue } from '../../models/models';
import { ENSEMBLE_TYPE_LABELS, INSTITUTION_TYPE_LABELS, label } from '../../core/labels';

@Component({
  selector: 'app-ensemble-detail',
  imports: [RouterLink, EventList],
  templateUrl: './ensemble-detail.html',
  styleUrl: './ensemble-detail.css',
})
export class EnsembleDetailPage {
  protected readonly data = inject(DataService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  readonly ensemble = computed<Ensemble | undefined>(() => {
    const id = this.params()?.get('id');
    return id ? this.data.ensemble(id) : undefined;
  });

  readonly typeLabel = computed(() => {
    const e = this.ensemble();
    return e ? label(ENSEMBLE_TYPE_LABELS, e.type) : '';
  });
  readonly cityName = computed(() => {
    const e = this.ensemble();
    return e ? this.data.cityNames(e.cityIds) || e.region || '' : '';
  });
  readonly conductorName = computed(() => this.data.person(this.ensemble()?.chiefConductorPersonId)?.name ?? '');
  readonly homeVenue = computed<Venue | undefined>(() => this.data.venue(this.ensemble()?.venueId));

  readonly institution = computed<Institution | undefined>(() => {
    const e = this.ensemble();
    return e ? this.data.institutionForEnsemble(e.id) : undefined;
  });
  readonly institutionType = computed(() => {
    const inst = this.institution();
    return inst ? label(INSTITUTION_TYPE_LABELS, inst.type) : '';
  });

  readonly events = computed(() => {
    const e = this.ensemble();
    return e ? this.data.eventsForEnsemble(e.id) : [];
  });
}
