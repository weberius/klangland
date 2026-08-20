import { Injectable, computed, signal } from '@angular/core';

function toggleInSet(set: ReadonlySet<string>, id: string): Set<string> {
  const next = new Set(set);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  return next;
}

/**
 * Hält die aktive Filter-Auswahl (US-020) als root-bereitgestellten Zustand:
 * Orte (Sitzort der Ensembles) und Musikprofile. Die Root-Instanz sorgt für die
 * geforderte In-App-Persistenz über Seitenwechsel hinweg (Kalender ↔ Ensembles ↔
 * Spielstätten), ohne localStorage/sessionStorage – Persistenz über Reload/Session
 * hinaus ist bewusst Out of Scope.
 *
 * Die Auswahl ist additiv: ODER innerhalb einer Kategorie, UND zwischen den
 * Kategorien (siehe DataService.*ForFilter).
 */
@Injectable({ providedIn: 'root' })
export class FilterService {
  private readonly _cityIds = signal<ReadonlySet<string>>(new Set());
  private readonly _profileIds = signal<ReadonlySet<string>>(new Set());

  /** Aktuell ausgewählte Stadt-IDs (leer = keine Ort-Einschränkung). */
  readonly selectedCityIds = this._cityIds.asReadonly();
  /** Aktuell ausgewählte Musikprofile (leer = keine Profil-Einschränkung). */
  readonly selectedProfileIds = this._profileIds.asReadonly();

  /** Anzahl aktiver Filter über beide Kategorien (für den Zähler am Button). */
  readonly activeCount = computed(() => this._cityIds().size + this._profileIds().size);

  /** Ob überhaupt eine Auswahl aktiv ist. */
  readonly hasSelection = computed(() => this.activeCount() > 0);

  isCitySelected(cityId: string): boolean {
    return this._cityIds().has(cityId);
  }
  isProfileSelected(profileId: string): boolean {
    return this._profileIds().has(profileId);
  }

  /** Wählt eine Stadt an bzw. ab (additive Mehrfachauswahl). */
  toggleCity(cityId: string): void {
    this._cityIds.set(toggleInSet(this._cityIds(), cityId));
  }

  /** Wählt ein Musikprofil an bzw. ab (additive Mehrfachauswahl). */
  toggleProfile(profileId: string): void {
    this._profileIds.set(toggleInSet(this._profileIds(), profileId));
  }

  /** Entfernt alle Filter beider Kategorien. */
  clear(): void {
    this._cityIds.set(new Set());
    this._profileIds.set(new Set());
  }
}
