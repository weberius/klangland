import {
  Component,
  ElementRef,
  OnDestroy,
  afterNextRender,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import * as L from 'leaflet';

import { DataService } from '../../core/data.service';
import { FavoritesService } from '../../core/favorites.service';
import { APP_CONFIG } from '../../core/app-config';
import { Composer, ConcertEvent, Ensemble, Venue, Work } from '../../models/models';
import { formatFullDate, todayIso } from '../../core/date-util';
import { formatAddress } from '../../core/address';
import { buildEventIcs, icsFileName } from '../../core/ics';
import {
  ENSEMBLE_TYPE_LABELS, EVENT_STATUS_LABELS, EVENT_TYPE_LABELS, GENRE_LABELS, label,
} from '../../core/labels';

interface ProgramLine {
  work: Work | undefined;
  composer: Composer | undefined;
  catalogue: string;
  years: string;
  movement: string | null;
  movements: string[] | null;
  version: string | null;
}

@Component({
  selector: 'app-event-detail',
  imports: [RouterLink],
  templateUrl: './event-detail.html',
  styleUrl: './event-detail.css',
})
export class EventDetailPage implements OnDestroy {
  protected readonly data = inject(DataService);
  protected readonly favorites = inject(FavoritesService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

  /** Container der Veranstaltungsort-Karte; optional, da nur bei Koordinaten gerendert (US-023). */
  private readonly mapContainer = viewChild<ElementRef<HTMLElement>>('map');
  private map: L.Map | null = null;

  constructor() {
    // Karte erst nach dem ersten Rendern aufbauen (Container existiert dann, hat eine Größe).
    afterNextRender(() => this.initMap());
  }

  readonly event = computed<ConcertEvent | undefined>(() => {
    const id = this.params()?.get('id');
    return id ? this.data.event(id) : undefined;
  });

  /** Ob der aktuelle Event als Favorit markiert ist (US-021). */
  readonly isFavorite = computed(() => {
    const e = this.event();
    return e ? this.favorites.isFavorite(e.id) : false;
  });

  /** Schaltet die Favoriten-Markierung des aktuellen Events um. */
  toggleFavorite(): void {
    const e = this.event();
    if (e) this.favorites.toggle(e.id);
  }

  /**
   * Ticket-Link nur zeigen, wenn ein URL gepflegt ist, das Event nicht abgesagt ist
   * und das Datum heute oder in der Zukunft liegt (US-015). `postponed`/`rescheduled`
   * behalten den Link bewusst, solange das Datum nicht vergangen ist.
   */
  readonly canBuyTickets = computed(() => {
    const e = this.event();
    if (!e || !e.ticketUrl) return false;
    if (e.status === 'cancelled') return false;
    return e.date >= todayIso(APP_CONFIG.referenceDate);
  });

  /** Sichtbarkeit des Verlassen-Hinweis-Dialogs (US-015). */
  protected readonly ticketDialogOpen = signal(false);

  /** Öffnet den Verlassen-Hinweis; der externe Link wird erst nach Bestätigung geöffnet. */
  openTicketDialog(): void {
    if (this.canBuyTickets()) this.ticketDialogOpen.set(true);
  }

  /** Bricht den Hinweis ab – es wird nichts geöffnet (AK 8). */
  cancelTicketDialog(): void {
    this.ticketDialogOpen.set(false);
  }

  /** Bestätigt den Hinweis und öffnet die externe Ticketseite im neuen Tab (AK 7). */
  confirmTickets(): void {
    const url = this.event()?.ticketUrl;
    this.ticketDialogOpen.set(false);
    // window.open direkt im Klick-Handler → echte Nutzergeste, kein Popup-Blocker.
    if (url) window.open(url, '_blank', 'noopener');
  }

  /** Sichtbarkeit des Routing-/Karten-Anbieter-Dialogs (US-023). */
  protected readonly mapsDialogOpen = signal(false);

  /** Ob ein Routing-Button angeboten wird: nur bei Koordinaten oder Adresse (AK 6/10). */
  readonly canRoute = computed(() => !!(this.venue()?.coordinates || this.venueAddress()));

  /**
   * Ziel-Links zu externen Kartenanbietern (AK 7). Bevorzugt die Koordinaten
   * (`lat,lng`), hilfsweise die formatierte Adresse. Reguläre Karten-URLs statt
   * Geräte-Deeplinks – plattformübergreifend und ohne Erkennung.
   */
  readonly mapsLinks = computed<{ label: string; url: string }[]>(() => {
    const coords = this.venue()?.coordinates ?? null;
    const address = this.venueAddress();
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

  /** Öffnet den Verlassen-Hinweis-Dialog mit der Anbieterauswahl (AK 6). */
  openMapsDialog(): void {
    if (this.canRoute()) this.mapsDialogOpen.set(true);
  }

  /** Schließt den Routing-Dialog ohne einen Anbieter zu öffnen (AK 8). */
  closeMapsDialog(): void {
    this.mapsDialogOpen.set(false);
  }

  readonly fullDate = computed(() => {
    const e = this.event();
    return e ? formatFullDate(e.date) : '';
  });

  readonly ensembles = computed<Ensemble[]>(() =>
    (this.event()?.ensembleIds ?? []).map((id) => this.data.ensemble(id)).filter((x): x is Ensemble => !!x),
  );

  readonly conductors = computed(() => this.data.personNames(this.event()?.conductorPersonIds ?? []));
  readonly soloists = computed(() => this.data.personNames(this.event()?.soloistPersonIds ?? []));

  readonly venue = computed<Venue | undefined>(() => this.data.venue(this.event()?.venueId));
  readonly venueAddress = computed(() => formatAddress(this.venue()?.address));
  readonly cityName = computed(() => this.data.city(this.event()?.cityId)?.name ?? '');

  readonly statusLabel = computed(() => {
    const e = this.event();
    return e && e.status !== 'scheduled' ? label(EVENT_STATUS_LABELS, e.status) : '';
  });
  readonly typeLabel = computed(() => label(EVENT_TYPE_LABELS, this.event()?.eventType));
  /** Bereinigte Event-Beschreibung; leer, wenn nicht gepflegt (US-023, AK 4). */
  readonly eventDescription = computed(() => this.event()?.description?.trim() ?? '');
  readonly program = computed<ProgramLine[]>(() =>
    (this.event()?.program ?? []).map((p) => {
      const work = this.data.work(p.workId);
      const composer = work ? this.data.composer(work.composerId) : undefined;
      return {
        work,
        composer,
        catalogue: this.formatCatalogue(work),
        years: this.formatYears(work),
        movement: p.movement ?? null,
        movements: p.movements ?? null,
        version: p.version ?? work?.version ?? null,
      };
    }),
  );

  /**
   * Erzeugt clientseitig eine iCalendar-Datei (.ics) für dieses Event und bietet sie
   * als Download an – ohne Backend-Aufruf (US-012). Zielsysteme (Apple/Google/Outlook)
   * verstehen das Format nativ.
   */
  addToCalendar(): void {
    const e = this.event();
    if (!e) return;
    const venue = this.venue();
    const ics = buildEventIcs({
      id: e.id,
      title: e.title,
      date: e.date,
      startTime: e.startTime,
      endTime: e.endTime,
      status: e.status,
      venueName: venue?.name ?? null,
      venueAddress: formatAddress(venue?.address),
      cityName: this.cityName() || null,
      ensembleNames: this.ensembles().map((ens) => ens.name),
      conductorNames: this.conductors(),
      eventUrl: window.location.href,
    });

    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = icsFileName(e.id);
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  ensembleTypeLabel(e: Ensemble): string {
    return label(ENSEMBLE_TYPE_LABELS, e.type);
  }
  genreLabel(w: Work | undefined): string {
    return w ? label(GENRE_LABELS, w.genre) : '';
  }

  private formatCatalogue(work: Work | undefined): string {
    if (!work || work.catalogue.length === 0) return '';
    return work.catalogue
      .map((c) => (c.system.toLowerCase() === 'opus' ? `op. ${c.number}` : `${c.system} ${c.number}`))
      .join(', ');
  }
  private formatYears(work: Work | undefined): string {
    if (!work?.yearComposed) return '';
    const { from, to } = work.yearComposed;
    return from === to ? `${from}` : `${from}–${to}`;
  }

  /**
   * Baut die kleine Leaflet-/OSM-Karte des Veranstaltungsortes auf (US-023, AK 9).
   * Läuft nur, wenn Container und Koordinaten vorhanden sind; Marker als `L.divIcon`,
   * um das bekannte Problem fehlender Default-Marker-Bilder im Angular-Build zu umgehen.
   */
  private initMap(): void {
    const el = this.mapContainer()?.nativeElement;
    const coords = this.venue()?.coordinates;
    if (!el || !coords) return;

    const map = L.map(el, { center: [coords.lat, coords.lng], zoom: 15 });
    this.map = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende',
    }).addTo(map);

    const name = this.venue()?.name ?? 'Veranstaltungsort';
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
