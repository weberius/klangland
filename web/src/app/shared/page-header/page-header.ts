import { Component, computed, inject, input, signal } from '@angular/core';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { MusicalProfile } from '../../models/models';
import { MUSICAL_PROFILE_LABELS, label } from '../../core/labels';

interface ActiveChip {
  key: string;
  label: string;
  kind: 'city' | 'profile';
  id: string;
}

/**
 * Seitenüberschrift (US-020) mit Info-Button für die Seitenbeschreibung sowie den
 * aktiven Filtern als einzeln entfernbare Chips. Ohne Auswahl wird dort kein
 * Filter-Element angezeigt und es entsteht kein Platzbedarf.
 */
@Component({
  selector: 'app-page-header',
  templateUrl: './page-header.html',
  styleUrl: './page-header.css',
})
export class PageHeader {
  private readonly data = inject(DataService);
  protected readonly filter = inject(FilterService);

  /** Seitenüberschrift (h1). */
  readonly heading = input.required<string>();
  /** Hinter dem Info-Button verborgene Seitenbeschreibung. */
  readonly description = input<string>('');

  protected readonly descriptionOpen = signal(false);

  protected readonly activeChips = computed<ActiveChip[]>(() => {
    const chips: ActiveChip[] = [];
    for (const id of this.filter.selectedCityIds()) {
      chips.push({ key: `city:${id}`, kind: 'city', id, label: this.data.city(id)?.name ?? id });
    }
    for (const id of this.filter.selectedProfileIds()) {
      chips.push({
        key: `profile:${id}`,
        kind: 'profile',
        id,
        label: label(MUSICAL_PROFILE_LABELS, id as MusicalProfile),
      });
    }
    return chips;
  });

  toggleDescription(): void {
    this.descriptionOpen.update((open) => !open);
  }

  removeChip(chip: ActiveChip): void {
    if (chip.kind === 'city') this.filter.toggleCity(chip.id);
    else this.filter.toggleProfile(chip.id);
  }
}
