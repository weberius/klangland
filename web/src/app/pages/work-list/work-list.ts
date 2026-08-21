import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Work } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';

@Component({
  selector: 'app-work-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './work-list.html',
  styleUrl: './work-list.css',
})
export class WorkListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly works = computed(() =>
    this.data.worksForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
  );

  composerName(w: Work): string {
    return this.data.composer(w.composerId)?.name ?? 'Unbekannte:r Komponist:in';
  }
  eventCount(w: Work): number {
    return this.data.eventsForWork(w.id).length;
  }
}
