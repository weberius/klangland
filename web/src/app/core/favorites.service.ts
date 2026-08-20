import { Injectable, computed, signal } from '@angular/core';

function toggleInSet(set: ReadonlySet<string>, id: string): Set<string> {
  const next = new Set(set);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  return next;
}

/**
 * Hält die Favoriten-Auswahl (US-021) als root-bereitgestellten Zustand:
 * (a) das Set favorisierter Event-IDs und (b) das Flag „Nur Favoriten".
 *
 * Favoriten sind eventspezifisch und bewusst **flüchtig**: Der Zustand lebt nur
 * im Speicher (kein localStorage/sessionStorage). Wiederhergestellt wird die
 * Auswahl ausschließlich über einen geteilten Link (Query-Parameter, siehe
 * FilterButton.shareLink / App-Initialisierung).
 */
@Injectable({ providedIn: 'root' })
export class FavoritesService {
  private readonly _ids = signal<ReadonlySet<string>>(new Set());
  private readonly _onlyFavorites = signal(false);

  /** Aktuell favorisierte Event-IDs (leer = keine Favoriten). */
  readonly ids = this._ids.asReadonly();
  /** Ob der Filter „Nur Favoriten" aktiv ist. */
  readonly onlyFavorites = this._onlyFavorites.asReadonly();

  /** Anzahl markierter Favoriten. */
  readonly favoriteCount = computed(() => this._ids().size);
  /** Ob überhaupt Favoriten markiert sind. */
  readonly hasFavorites = computed(() => this._ids().size > 0);

  isFavorite(id: string): boolean {
    return this._ids().has(id);
  }

  /** Markiert einen Event als Favorit bzw. hebt die Markierung wieder auf. */
  toggle(id: string): void {
    this._ids.set(toggleInSet(this._ids(), id));
  }

  setOnlyFavorites(value: boolean): void {
    this._onlyFavorites.set(value);
  }

  toggleOnlyFavorites(): void {
    this._onlyFavorites.update((v) => !v);
  }

  /**
   * Initialisiert die Favoriten aus einer Liste von IDs (z. B. aus dem
   * Query-Parameter eines geteilten Links). Der Aufrufer stellt sicher, dass nur
   * existierende Event-IDs übergeben werden.
   */
  setFromIds(ids: string[]): void {
    this._ids.set(new Set(ids));
  }

  /** Leert die Favoriten-Markierungen **und** setzt das Filter-Flag zurück. */
  reset(): void {
    this._ids.set(new Set());
    this._onlyFavorites.set(false);
  }
}
