import {
  Component, ElementRef, HostListener, computed, inject, signal, viewChild,
} from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import Fuse from 'fuse.js';
import { DataService, SearchDocument } from './core/data.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly data = inject(DataService);
  private readonly router = inject(Router);
  private readonly MIN_SEARCH_CHARS = 3;
  private readonly SEARCH_LIMIT = 12;

  /** Zustand der mobilen Burger-Navigation. */
  protected readonly menuOpen = signal(false);
  /** Globaler Suchbegriff im Header. */
  protected readonly searchQuery = signal('');
  /** Sichtbarkeit der Trefferliste. */
  protected readonly searchOpen = signal(false);
  /** Aktuelle Suchtreffer. */
  protected readonly searchResults = signal<SearchDocument[]>([]);

  private readonly burgerButton = viewChild<ElementRef<HTMLButtonElement>>('burgerButton');
  private readonly searchContainer = viewChild<ElementRef<HTMLElement>>('searchContainer');
  private searchFuse: Fuse<SearchDocument> | null = null;
  private searchFuseSize = 0;

  protected readonly searchNeedsMoreChars = computed(() => {
    const length = this.searchQuery().trim().length;
    return length > 0 && length < this.MIN_SEARCH_CHARS;
  });
  protected readonly searchShowsResults = computed(() =>
    this.searchQuery().trim().length >= this.MIN_SEARCH_CHARS && this.searchResults().length > 0);
  protected readonly searchShowsNoResults = computed(() =>
    this.searchQuery().trim().length >= this.MIN_SEARCH_CHARS && this.searchResults().length === 0);

  constructor() {
    // Nach Navigation mobile Navigation und Trefferliste zuverlässig schließen.
    this.router.events
      .pipe(
        filter((e) => e instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => {
        this.menuOpen.set(false);
        this.searchOpen.set(false);
      });
  }

  toggleMenu(): void {
    this.menuOpen.update((open) => !open);
  }

  closeMenu(): void {
    if (!this.menuOpen()) return;
    this.menuOpen.set(false);
    this.burgerButton()?.nativeElement.focus();
  }

  onSearchInput(value: string): void {
    this.searchQuery.set(value);
    const query = value.trim();

    if (!query) {
      this.searchResults.set([]);
      this.searchOpen.set(false);
      return;
    }

    this.searchOpen.set(true);
    if (query.length < this.MIN_SEARCH_CHARS) {
      this.searchResults.set([]);
      return;
    }

    const fuse = this.getSearchFuse();
    if (!fuse) {
      this.searchResults.set([]);
      return;
    }

    this.searchResults.set(
      fuse.search(query, { limit: this.SEARCH_LIMIT }).map((match) => match.item),
    );
  }

  onSearchFocus(): void {
    if (this.searchQuery().trim().length > 0) this.searchOpen.set(true);
  }

  selectSearchResult(): void {
    this.searchOpen.set(false);
    this.searchQuery.set('');
    this.searchResults.set([]);
    this.menuOpen.set(false);
  }

  searchKindLabel(result: SearchDocument): string {
    switch (result.kind) {
      case 'event':
        return 'Veranstaltung';
      case 'ensemble':
        return 'Ensemble';
      case 'venue':
        return 'Spielstätte';
      default:
        return 'Treffer';
    }
  }

  private getSearchFuse(): Fuse<SearchDocument> | null {
    const documents = this.data.searchDocuments;
    if (documents.length === 0) return null;

    if (!this.searchFuse || this.searchFuseSize !== documents.length) {
      this.searchFuse = new Fuse(documents, {
        includeScore: true,
        threshold: 0.38,
        ignoreLocation: true,
        minMatchCharLength: 2,
        keys: [
          { name: 'title', weight: 0.45 },
          { name: 'subtitle', weight: 0.25 },
          { name: 'searchText', weight: 0.3 },
        ],
      });
      this.searchFuseSize = documents.length;
    }

    return this.searchFuse;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.searchOpen()) return;
    const container = this.searchContainer()?.nativeElement;
    if (!container) return;
    const target = event.target;
    if (target instanceof Node && !container.contains(target)) {
      this.searchOpen.set(false);
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.searchOpen()) {
      this.searchOpen.set(false);
      return;
    }
    this.closeMenu();
  }
}
