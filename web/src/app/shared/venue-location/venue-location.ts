import {
  Component,
  ElementRef,
  OnDestroy,
  afterNextRender,
  computed,
  input,
  signal,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';

import { Coordinates } from '../../models/models';

/**
 * Gemeinsame Karten-/Navigationsdarstellung eines Veranstaltungsortes (US-034): eine
 * eingebettete Leaflet-/OSM-Karte mit blauem Marker sowie ein Button, der einen
 * Auswahldialog externer Kartenanbieter (Google Maps / Apple Maps / OpenStreetMap)
 * öffnet. Wird sowohl auf der Event-Detailseite als auch auf der Spielstätten-Detailseite
 * eingesetzt (DRY). Kapselt die zuvor in `event-detail` dupliziert vorliegende Logik.
 */
@Component({
  selector: 'app-venue-location',
  templateUrl: './venue-location.html',
  styleUrl: './venue-location.css',
})
export class VenueLocation implements OnDestroy {
  /** Name des Ortes (Marker-Titel). */
  readonly name = input<string>('Veranstaltungsort');
  /** Formatierte Adresszeile (Fallback-Routingziel, wenn keine Koordinaten vorliegen). */
  readonly address = input<string | null>(null);
  /** Geokoordinaten des Ortes; ohne sie wird keine Karte gerendert. */
  readonly coordinates = input<Coordinates | null>(null);

  private readonly mapContainer = viewChild<ElementRef<HTMLElement>>('map');
  private map: L.Map | null = null;

  constructor() {
    afterNextRender(() => this.initMap());
  }

  /** Ob ein Routing-Button angeboten wird: nur bei Koordinaten oder Adresse. */
  readonly canRoute = computed(() => !!(this.coordinates() || this.address()));

  /** Sichtbarkeit des Routing-/Karten-Anbieter-Dialogs. */
  protected readonly mapsDialogOpen = signal(false);

  /**
   * Ziel-Links zu externen Kartenanbietern. Bevorzugt die Koordinaten (`lat,lng`),
   * hilfsweise die formatierte Adresse. Reguläre Karten-URLs statt Geräte-Deeplinks –
   * plattformübergreifend und ohne Erkennung.
   */
  readonly mapsLinks = computed<{ label: string; url: string }[]>(() => {
    const coords = this.coordinates();
    const address = this.address();
    const dest = coords ? `${coords.lat},${coords.lng}` : (address ?? '');
    if (!dest) return [];
    const enc = encodeURIComponent(dest);
    return [
      { label: 'Google Maps', url: `https://www.google.com/maps/dir/?api=1&destination=${enc}` },
      { label: 'Apple Maps', url: `https://maps.apple.com/?daddr=${enc}` },
      {
        label: 'OpenStreetMap',
        url: coords
          ? `https://www.openstreetmap.org/directions?to=${enc}`
          : `https://www.openstreetmap.org/search?query=${enc}`,
      },
    ];
  });

  openMapsDialog(): void {
    if (this.canRoute()) this.mapsDialogOpen.set(true);
  }

  closeMapsDialog(): void {
    this.mapsDialogOpen.set(false);
  }

  /**
   * Baut die kleine Leaflet-/OSM-Karte auf. Läuft nur, wenn Container und Koordinaten
   * vorhanden sind; Marker als `L.divIcon` (blaue `.venue-marker`-Klasse), um das bekannte
   * Problem fehlender Default-Marker-Bilder im Angular-Build zu umgehen.
   */
  private initMap(): void {
    const el = this.mapContainer()?.nativeElement;
    const coords = this.coordinates();
    if (!el || !coords) return;

    const map = L.map(el, { center: [coords.lat, coords.lng], zoom: 15 });
    this.map = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende',
    }).addTo(map);

    const name = this.name();
    L.marker([coords.lat, coords.lng], {
      icon: L.divIcon({
        className: 'venue-marker-wrap',
        html: '<span class="venue-marker"></span>',
        iconSize: [18, 18],
        iconAnchor: [9, 9],
      }),
      title: name,
      alt: name,
    }).addTo(map);
  }

  ngOnDestroy(): void {
    this.map?.remove();
    this.map = null;
  }
}
