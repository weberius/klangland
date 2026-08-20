import {
  Component, ElementRef, HostListener, computed, inject, signal, viewChild,
} from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { FavoritesService } from '../../core/favorites.service';

/**
 * Filter-Auslöser in der Kopfleiste (US-020): ein Button mit Aktiv-Zähler, der ein
 * Popover mit Chip-Abschnitten (Ort, Musikprofil) öffnet. Das Popover schließt
 * bei Klick außerhalb, mit ESC und bei Seitennavigation.
 *
 * US-021 ergänzt eine „Nur Favoriten"-Umschaltung sowie eine „Teilen"-Aktion, die
 * auf Abruf einen Link mit den favorisierten Events erzeugt.
 */
@Component({
  selector: 'app-filter-button',
  templateUrl: './filter-button.html',
  styleUrl: './filter-button.css',
})
export class FilterButton {
  private readonly data = inject(DataService);
  private readonly router = inject(Router);
  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  protected readonly filter = inject(FilterService);
  protected readonly favorites = inject(FavoritesService);

  protected readonly open = signal(false);
  protected readonly cities = computed(() => this.data.filterCities());
  protected readonly profiles = computed(() => this.data.filterProfiles());

  /** Auf Abruf erzeugter Teilen-Link (null = noch nicht erzeugt). */
  protected readonly shareUrl = signal<string | null>(null);
  /** Ob der Teilen-Link erfolgreich in die Zwischenablage kopiert wurde. */
  protected readonly copied = signal(false);

  /** Aktiv-Zähler am Button inkl. „Nur Favoriten" (Ort + Profil + Favoriten-Filter). */
  protected readonly activeCount = computed(
    () => this.filter.activeCount() + (this.favorites.onlyFavorites() ? 1 : 0),
  );
  /** Ob es überhaupt etwas zurückzusetzen gibt (Filter, Favoriten-Filter oder Markierungen). */
  protected readonly canReset = computed(
    () => this.filter.hasSelection() || this.favorites.onlyFavorites() || this.favorites.hasFavorites(),
  );

  private readonly toggleButton = viewChild<ElementRef<HTMLButtonElement>>('toggleButton');

  constructor() {
    // AK 18: Popover bei Seitennavigation schließen.
    this.router.events
      .pipe(
        filter((e) => e instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.close());
  }

  toggle(): void {
    if (this.open()) this.close();
    else this.open.set(true);
  }

  private close(): void {
    this.open.set(false);
    // Teilen-Status beim Schließen verwerfen, damit ein veralteter Link nicht wieder auftaucht.
    this.shareUrl.set(null);
    this.copied.set(false);
  }

  /** Setzt Ort-/Profil-Filter, Favoriten-Filter und Favoriten-Markierungen zurück (AK 8). */
  resetAll(): void {
    this.filter.clear();
    this.favorites.reset();
    this.shareUrl.set(null);
    this.copied.set(false);
  }

  /**
   * Erzeugt auf Abruf einen absoluten Link zur App mit den favorisierten Events als
   * Query-Parameter und legt ihn – wenn möglich – in die Zwischenablage (AK 9). Der
   * Link wird zusätzlich im Popover angezeigt, damit er auch ohne Zwischenablage-
   * Zugriff kopierbar bleibt.
   */
  share(): void {
    const ids = [...this.favorites.ids()];
    if (ids.length === 0) return;
    const url = new URL(window.location.href);
    url.search = '';
    url.searchParams.set('favorites', ids.join(','));
    const link = url.toString();
    this.shareUrl.set(link);
    this.copied.set(false);
    navigator.clipboard?.writeText(link).then(
      () => this.copied.set(true),
      () => this.copied.set(false),
    );
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.open()) return;
    const target = event.target;
    if (target instanceof Node && !this.host.nativeElement.contains(target)) {
      this.close();
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.open()) return;
    this.close();
    this.toggleButton()?.nativeElement.focus();
  }
}
