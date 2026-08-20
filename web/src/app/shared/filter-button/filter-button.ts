import {
  Component, ElementRef, HostListener, computed, inject, signal, viewChild,
} from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';

/**
 * Filter-Auslöser in der Kopfleiste (US-020): ein Button mit Aktiv-Zähler, der ein
 * Popover mit zwei Chip-Abschnitten (Ort, Musikprofil) öffnet. Das Popover schließt
 * bei Klick außerhalb, mit ESC und bei Seitennavigation.
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

  protected readonly open = signal(false);
  protected readonly cities = computed(() => this.data.filterCities());
  protected readonly profiles = computed(() => this.data.filterProfiles());

  private readonly toggleButton = viewChild<ElementRef<HTMLButtonElement>>('toggleButton');

  constructor() {
    // AK 18: Popover bei Seitennavigation schließen.
    this.router.events
      .pipe(
        filter((e) => e instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.open.set(false));
  }

  toggle(): void {
    this.open.update((o) => !o);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.open()) return;
    const target = event.target;
    if (target instanceof Node && !this.host.nativeElement.contains(target)) {
      this.open.set(false);
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (!this.open()) return;
    this.open.set(false);
    this.toggleButton()?.nativeElement.focus();
  }
}
