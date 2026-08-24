import { Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { FavoritesService } from '../../core/favorites.service';
import { EventList } from '../../shared/event-list';
import { Composer, Work } from '../../models/models';
import { GENRE_LABELS, label } from '../../core/labels';

@Component({
  selector: 'app-work-detail',
  imports: [RouterLink, EventList],
  templateUrl: './work-detail.html',
  styleUrl: './work-detail.css',
})
export class WorkDetailPage {
  protected readonly data = inject(DataService);
  private filter = inject(FilterService);
  private favorites = inject(FavoritesService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  readonly work = computed<Work | undefined>(() => {
    const id = this.params()?.get('id');
    return id ? this.data.work(id) : undefined;
  });

  readonly composer = computed<Composer | undefined>(() => this.data.composer(this.work()?.composerId));

  readonly composerName = computed(() => this.composer()?.name ?? 'Unbekannte:r Komponist:in');

  readonly genreLabel = computed(() => {
    const w = this.work();
    return w ? label(GENRE_LABELS, w.genre) : '';
  });

  /** Werkverzeichnis-Nummern (z. B. „op. 67, WoO 59"). Leer, wenn keine gepflegt. */
  readonly catalogue = computed(() => {
    const w = this.work();
    if (!w || w.catalogue.length === 0) return '';
    return w.catalogue
      .map((c) => (c.system.toLowerCase() === 'opus' ? `op. ${c.number}` : `${c.system} ${c.number}`))
      .join(', ');
  });

  /** Entstehungszeit als Jahr oder Zeitraum (z. B. „1808" oder „1804–1808"). */
  readonly years = computed(() => {
    const y = this.work()?.yearComposed;
    if (!y) return '';
    return y.from === y.to ? `${y.from}` : `${y.from}–${y.to}`;
  });

  readonly duration = computed(() => {
    const minutes = this.work()?.durationMinutes;
    return minutes ? `${minutes} Minuten` : '';
  });

  readonly events = computed(() => {
    const w = this.work();
    return w
      ? this.data.eventsForWork(
          w.id,
          this.filter.selectedCityIds(),
          this.filter.selectedProfileIds(),
          this.favorites.onlyFavorites() ? this.favorites.ids() : null,
        )
      : [];
  });

  /** Ob ein globaler Filter aktiv ist (spezifischerer Leer-Hinweis, US-031 AK 5). */
  readonly filterActive = computed(
    () =>
      this.filter.selectedCityIds().size > 0 ||
      this.filter.selectedProfileIds().size > 0 ||
      this.favorites.onlyFavorites(),
  );
}
