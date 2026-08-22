import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { Composer, Work } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';

interface ComposerCardView {
  composer: Composer;
  life: string;
  portraitUrl: string | null;
  works: Work[];
  moreWorksCount: number;
}

@Component({
  selector: 'app-composer-list',
  imports: [RouterLink, PageHeader],
  templateUrl: './composer-list.html',
  styleUrl: './composer-list.css',
})
export class ComposerListPage {
  private data = inject(DataService);
  private filter = inject(FilterService);

  readonly loading = computed(() => this.data.loading());
  readonly composers = computed(() =>
    this.data.composersForFilter(this.filter.selectedCityIds(), this.filter.selectedProfileIds()),
  );
  readonly cards = computed<ComposerCardView[]>(() =>
    this.composers().map((composer) => {
      const works = this.works(composer);
      const preview = works.slice(0, 3);
      return {
        composer,
        life: this.life(composer),
        portraitUrl: this.portraitUrl(composer),
        works: preview,
        moreWorksCount: Math.max(0, works.length - preview.length),
      };
    }),
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
