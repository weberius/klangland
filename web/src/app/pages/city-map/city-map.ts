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
import { RouterLink } from '@angular/router';
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

  private readonly mapContainer = viewChild.required<ElementRef<HTMLElement>>('map');

  /** Orte mit ansässigem Ensemble und hinterlegten Koordinaten (rote Marker). */
  protected readonly cities = this.data.mapCities();

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

  constructor() {
    // Karte erst nach dem ersten Rendern aufbauen (Container hat dann eine Größe).
    afterNextRender(() => this.initMap());
    // Marker-Hervorhebung an den aktiven Ort-Filter koppeln (AK 11/12).
    effect(() => this.updateHighlights());
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
      marker.addTo(map);
      this.markers.set(city.id, marker);
      points.push([coords.lat, coords.lng]);
    }

    if (points.length > 0) {
      map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 11 });
    }
    this.updateHighlights();
  }

  /** Spiegelt den aktiven Ort-Filter in die Marker-Darstellung (Klasse `active`). */
  private updateHighlights(): void {
    const active = this.filter.selectedCityIds();
    for (const [id, marker] of this.markers) {
      marker.getElement()?.classList.toggle('active', active.has(id));
    }
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
  }
}
