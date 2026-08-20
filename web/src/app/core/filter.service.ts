import { Injectable, computed, signal } from '@angular/core';

/**
 * Hält die aktive Ort-Filter-Auswahl (US-011) als root-bereitgestellten Zustand.
 * Die Root-Instanz sorgt für die geforderte In-App-Persistenz über Seitenwechsel
 * hinweg (Kalender ↔ Ensembles ↔ Spielstätten), ohne localStorage/sessionStorage –
 * Persistenz über Reload/Session hinaus ist bewusst Out of Scope.
 */
@Injectable({ providedIn: 'root' })
export class FilterService {
  private readonly _selectedCityIds = signal<ReadonlySet<string>>(new Set());

  /** Aktuell ausgewählte Stadt-IDs (leer = alle Inhalte anzeigen). */
  readonly selectedIds = this._selectedCityIds.asReadonly();

  /** Ob überhaupt eine Auswahl aktiv ist. */
  readonly hasSelection = computed(() => this._selectedCityIds().size > 0);

  isSelected(cityId: string): boolean {
    return this._selectedCityIds().has(cityId);
  }

  /** Wählt eine Stadt an bzw. ab (additive Mehrfachauswahl). */
  toggle(cityId: string): void {
    const next = new Set(this._selectedCityIds());
    if (next.has(cityId)) {
      next.delete(cityId);
    } else {
      next.add(cityId);
    }
    this._selectedCityIds.set(next);
  }
}
