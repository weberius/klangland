import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Ensemble } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';
import {
  ENSEMBLE_ROLE_LABELS, ENSEMBLE_TYPE_LABELS, MUSICAL_PROFILE_LABELS, label,
} from '../../core/labels';

@Component({
  selector: 'app-ensemble-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './ensemble-list.html',
  styleUrl: './ensemble-list.css',
})
export class EnsembleListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly ensembles = computed(() =>
    this.data.ensemblesForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
  );

  cityName(e: Ensemble): string {
    return this.data.cityNames(e.cityIds) || e.region || '';
  }
  conductorName(e: Ensemble): string {
    return this.data.person(e.chiefConductorPersonId)?.name ?? '';
  }
  typeLabel(e: Ensemble): string {
    return label(ENSEMBLE_TYPE_LABELS, e.type);
  }
  roleLabels(e: Ensemble): string[] {
    return e.roles.map((r) => label(ENSEMBLE_ROLE_LABELS, r));
  }
  profileLabels(e: Ensemble): string[] {
    return e.musicalProfiles.map((p) => label(MUSICAL_PROFILE_LABELS, p));
  }
  eventCount(e: Ensemble): number {
    return this.data.eventsForEnsemble(e.id).length;
  }
}
