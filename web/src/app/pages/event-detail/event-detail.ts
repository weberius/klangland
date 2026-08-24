import {
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { DataService } from '../../core/data.service';
import { FavoritesService } from '../../core/favorites.service';
import { APP_CONFIG } from '../../core/app-config';
import { VenueLocation } from '../../shared/venue-location/venue-location';
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
  imports: [RouterLink, VenueLocation],
  templateUrl: './event-detail.html',
  styleUrl: './event-detail.css',
})
export class EventDetailPage {
  protected readonly data = inject(DataService);
  protected readonly favorites = inject(FavoritesService);
  private route = inject(ActivatedRoute);
  private params = toSignal(this.route.paramMap);

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
}
