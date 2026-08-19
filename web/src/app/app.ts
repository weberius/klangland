import { Component, ElementRef, HostListener, inject, signal, viewChild } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DataService } from './core/data.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly data = inject(DataService);
  private readonly router = inject(Router);

  /** Zustand der mobilen Burger-Navigation. */
  protected readonly menuOpen = signal(false);

  private readonly burgerButton = viewChild<ElementRef<HTMLButtonElement>>('burgerButton');

  constructor() {
    // AK 4: Menü nach erfolgter Navigation zuverlässig schließen.
    this.router.events
      .pipe(
        filter((e) => e instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.menuOpen.set(false));
  }

  toggleMenu(): void {
    this.menuOpen.update((open) => !open);
  }

  closeMenu(): void {
    if (!this.menuOpen()) return;
    this.menuOpen.set(false);
    // Fokus-Rückgabe auf den Burger-Button (offener Punkt der Story).
    this.burgerButton()?.nativeElement.focus();
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.closeMenu();
  }
}
