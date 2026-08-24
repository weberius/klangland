import {
  Component,
  ElementRef,
  HostListener,
  OnDestroy,
  ViewEncapsulation,
  afterNextRender,
  computed,
  effect,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import * as L from 'leaflet';

import { DataService } from '../../core/data.service';
import { FilterService } from '../../core/filter.service';
import { City } from '../../models/models';
import { PageHeader } from '../../shared/page-header/page-header';

/**
 * Kartenseite (US-013): zeigt alle Orte mit ansässigem Ensemble als rote Marker auf
 * einer OpenStreetMap-Karte (Leaflet). Ein Klick auf einen Marker öffnet einen Dialog
 * mit den Ensembles des Ortes und einem Button, der den Ort-Filter (FilterService,
 * US-020) setzt bzw. entfernt. Der aktuell gefilterte Ort wird auf der Karte
 * hervorgehoben.
 *
 * Leaflet manipuliert das DOM außerhalb der Angular-Templates; daher ist die
 * View-Kapselung für diese Seite deaktiviert und alle Regeln sind unter
 * `.city-map-page` gescoped.
 */
@Component({
  selector: 'app-city-map',
  imports: [PageHeader, RouterLink],
  templateUrl: './city-map.html',
  styleUrl: './city-map.css',
  encapsulation: ViewEncapsulation.None,
})
export class CityMapPage implements OnDestroy {
  private readonly data = inject(DataService);
  protected readonly filter = inject(FilterService);
  private readonly router = inject(Router);

  private readonly mapContainer = viewChild.required<ElementRef<HTMLElement>>('map');

  /** Orte mit ansässigem Ensemble und hinterlegten Koordinaten (rote Marker). */
  protected readonly cities = this.data.mapCities();
  /** Spielstätten mit hinterlegten Koordinaten (blaue Marker, US-033). */
  protected readonly mapVenues = this.data.mapVenues();

  /** Layer „Standorte der Klangkörper" – standardmäßig aktiv (US-033, AK 1). */
  protected readonly showEnsembleLayer = signal(true);
  /** Layer „Adressen der Spielstätten" – standardmäßig aus (US-033, AK 2). */
  protected readonly showVenueLayer = signal(false);

  /** Im Dialog angezeigter Ort (null = Dialog geschlossen). */
  protected readonly selectedCity = signal<City | null>(null);
  /** Ensembles des aktuell im Dialog geöffneten Ortes. */
  protected readonly selectedEnsembles = computed(() => {
    const city = this.selectedCity();
    return city ? this.data.ensemblesInCity(city.id) : [];
  });
  /** Ob für den geöffneten Ort der Ort-Filter aktiv ist. */
  protected readonly selectedIsFiltered = computed(() => {
    const city = this.selectedCity();
    return city ? this.filter.selectedCityIds().has(city.id) : false;
  });

  private map: L.Map | null = null;
  private readonly markers = new Map<string, L.Marker>();
  /** Blaue Spielstätten-Marker (US-033), analog zu `markers`. */
  private readonly venueMarkers = new Map<string, L.Marker>();

  constructor() {
    // Karte erst nach dem ersten Rendern aufbauen (Container hat dann eine Größe).
    afterNextRender(() => this.initMap());
    // Marker-Hervorhebung an den aktiven Ort-Filter koppeln (AK 11/12).
    effect(() => this.updateHighlights());
    // Layer-Sichtbarkeit an die beiden Signals koppeln (US-033, AK 1/2/6).
    effect(() => this.updateLayers());
  }

  private initMap(): void {
    const container = this.mapContainer().nativeElement;
    // Zentrum grob auf NRW; die Ansicht wird anschließend auf die Marker eingepasst.
    const map = L.map(container, { center: [51.45, 7.5], zoom: 8 });
    this.map = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende',
    }).addTo(map);

    const points: L.LatLngExpression[] = [];
    for (const city of this.cities) {
      const coords = city.coordinates;
      if (!coords) continue;
      const marker = L.marker([coords.lat, coords.lng], {
        icon: L.divIcon({
          className: 'city-marker-wrap',
          html: '<span class="city-marker"></span>',
          iconSize: [18, 18],
          iconAnchor: [9, 9],
        }),
        keyboard: true,
        title: city.name,
        alt: `Ort ${city.name} – Ensembles anzeigen`,
        riseOnHover: true,
      });
      marker.on('click', () => this.openCity(city));
      this.markers.set(city.id, marker);
      points.push([coords.lat, coords.lng]);
    }

    // Blaue Spielstätten-Marker mit schlankem Popup (Name + Link zur Detailseite, US-033).
    for (const venue of this.mapVenues) {
      const coords = venue.coordinates;
      if (!coords) continue;
      const marker = L.marker([coords.lat, coords.lng], {
        icon: L.divIcon({
          className: 'city-venue-marker-wrap',
          html: '<span class="city-venue-marker"></span>',
          iconSize: [18, 18],
          iconAnchor: [9, 9],
        }),
        keyboard: true,
        title: venue.name,
        alt: `Spielstätte ${venue.name}`,
        riseOnHover: true,
      });
      marker.bindPopup(this.buildVenuePopup(venue.id, venue.name));
      this.venueMarkers.set(venue.id, marker);
    }

    if (points.length > 0) {
      map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 11 });
    }
    this.updateLayers();
    this.updateHighlights();
  }

  /** Popup-Inhalt eines Spielstätten-Markers: Name + Link, der per Angular-Router navigiert. */
  private buildVenuePopup(venueId: string, name: string): HTMLElement {
    const container = document.createElement('div');
    container.className = 'venue-popup';
    const title = document.createElement('strong');
    title.textContent = name;
    const link = document.createElement('a');
    link.href = `/venues/${venueId}`;
    link.textContent = 'Zur Spielstätte ›';
    link.addEventListener('click', (event) => {
      event.preventDefault();
      this.router.navigate(['/venues', venueId]);
    });
    container.append(title, document.createElement('br'), link);
    return container;
  }

  /**
   * Blendet beide Marker-Layer entsprechend der Signals ein/aus (US-033, AK 1/2/6).
   * Wichtig: Beide Layer-Signals werden **vor** dem `map`-Guard gelesen, damit der aufrufende
   * `effect` sie auch beim ersten Lauf (Karte noch nicht initialisiert) als Abhängigkeit erfasst
   * und beim Umschalten der Checkboxen erneut ausgeführt wird.
   */
  private updateLayers(): void {
    const showEnsembles = this.showEnsembleLayer();
    const showVenues = this.showVenueLayer();
    const map = this.map;
    if (!map) return;
    for (const marker of this.markers.values()) {
      if (showEnsembles) marker.addTo(map);
      else map.removeLayer(marker);
    }
    for (const marker of this.venueMarkers.values()) {
      if (showVenues) marker.addTo(map);
      else map.removeLayer(marker);
    }
    // Nach dem (Wieder-)Einblenden die Filter-Hervorhebung erneut anwenden.
    this.updateHighlights();
  }

  /** Spiegelt den aktiven Ort-Filter in die Marker-Darstellung (Klasse `active`). */
  private updateHighlights(): void {
    const active = this.filter.selectedCityIds();
    for (const [id, marker] of this.markers) {
      marker.getElement()?.classList.toggle('active', active.has(id));
    }
  }

  /** Schaltet den Klangkörper-Layer um (US-033, AK 3). */
  protected toggleEnsembleLayer(): void {
    this.showEnsembleLayer.update((v) => !v);
  }

  /** Schaltet den Spielstätten-Layer um (US-033, AK 3). */
  protected toggleVenueLayer(): void {
    this.showVenueLayer.update((v) => !v);
  }

  protected openCity(city: City): void {
    this.selectedCity.set(city);
  }

  protected closeDialog(): void {
    this.selectedCity.set(null);
  }

  @HostListener('document:keydown.escape')
  protected onEscape(): void {
    if (this.selectedCity()) this.closeDialog();
  }

  /** Setzt bzw. entfernt den Ort-Filter für den geöffneten Ort (AK 9). */
  protected toggleFilter(): void {
    const city = this.selectedCity();
    if (city) this.filter.toggleCity(city.id);
  }

  ngOnDestroy(): void {
    this.map?.remove();
    this.map = null;
    this.markers.clear();
    this.venueMarkers.clear();
  }
}
