import { Component, computed, inject, input, signal } from '@angular/core';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';

/**
 * Filterleiste unterhalb der Seitenüberschrift (US-011): eine Bubble je Stadt mit
 * ansässigem Ensemble, beschriftet mit dem Kfz-Kennzeichen. Zusätzlich blendet ein
 * Info-Button die als `description` übergebene Seitenbeschreibung ein/aus.
 */
@Component({
  selector: 'app-city-filter',
  templateUrl: './city-filter.html',
  styleUrl: './city-filter.css',
})
export class CityFilter {
  private readonly data = inject(DataService);
  protected readonly filter = inject(FilterService);

  /** Unter der Überschrift verborgene Seitenbeschreibung. */
  readonly description = input<string>('');

  protected readonly cities = computed(() => this.data.filterCities());
  protected readonly descriptionOpen = signal(false);

  toggleCity(cityId: string): void {
    this.filter.toggle(cityId);
  }

  toggleDescription(): void {
    this.descriptionOpen.update((open) => !open);
  }
}
