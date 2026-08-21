import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Composer, Work } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';

@Component({
  selector: 'app-composer-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './composer-list.html',
  styleUrl: './composer-list.css',
})
export class ComposerListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly composers = computed(() =>
    this.data.composersForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
  );

  works(c: Composer): Work[] {
    return this.data.worksForComposer(
      c.id,
      this.filter.selectedCityIds(),
      this.filter.selectedProfileIds(),
    );
  }

  life(c: Composer): string {
    const l = c.life;
    if (!l || l.from === null) return '';
    return l.to ? `${l.from}–${l.to}` : `* ${l.from}`;
  }

  portraitUrl(c: Composer): string | null {
    return c.portrait ? `portraits/${c.portrait.file}` : null;
  }
}
