import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { FavoritesService } from '../../core/favorites.service';
import { EventList } from '../../shared/event-list';
import { Composer } from '../../models/models';

@Component({
  selector: 'app-composer-detail',
  imports: [RouterLink, EventList],
  templateUrl: './composer-detail.html',
  styleUrl: './composer-detail.css',
})
export class ComposerDetailPage {
  protected readonly data = inject(DataService);
  private route = inject(ActivatedRoute);
  private filter = inject(FilterService);
  private favorites = inject(FavoritesService);
  private params = toSignal(this.route.paramMap);

  readonly loading = computed(() => this.data.loading());

  readonly composer = computed<Composer | undefined>(() => {
    const id = this.params()?.get('id');
    return id ? this.data.composer(id) : undefined;
  });

  readonly life = computed(() => {
    const l = this.composer()?.life;
    if (!l || l.from === null) return '';
    return l.to ? `${l.from}–${l.to}` : `* ${l.from}`;
  });

  readonly portraitUrl = computed(() => {
    const p = this.composer()?.portrait;
    return p ? `portraits/${p.file}` : null;
  });

  readonly works = computed(() => {
    const c = this.composer();
    return c
      ? this.data.worksForComposer(
          c.id,
          this.filter.selectedCityIds(),
          this.filter.selectedProfileIds(),
          this.favorites.onlyFavorites() ? this.favorites.ids() : null,
        )
      : [];
  });

  readonly events = computed(() => {
    const c = this.composer();
    return c
      ? this.data.eventsForComposer(
          c.id,
          this.filter.selectedCityIds(),
          this.filter.selectedProfileIds(),
          this.favorites.onlyFavorites() ? this.favorites.ids() : null,
        )
      : [];
  });

  /** Ob ein globaler Filter aktiv ist (spezifischerer Leer-Hinweis, US-032 AK 5). */
  readonly filterActive = computed(
    () =>
      this.filter.selectedCityIds().size > 0 ||
      this.filter.selectedProfileIds().size > 0 ||
      this.favorites.onlyFavorites(),
  );
}
