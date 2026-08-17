// Deutsche Anzeigetexte für kontrollierte Werte.

import { EnsembleType, EventStatus, EventType, Genre, InstitutionType, VenueType } from '../models/models';

export const ENSEMBLE_TYPE_LABELS: Record<EnsembleType, string> = {
  symphony_orchestra: 'Sinfonieorchester',
  philharmonic_orchestra: 'Philharmonisches Orchester',
  radio_orchestra: 'Rundfunkorchester',
  opera_orchestra: 'Opernorchester',
};

export const VENUE_TYPE_LABELS: Record<VenueType, string> = {
  concert_hall: 'Konzerthaus',
  philharmonic_hall: 'Philharmonie',
  theatre: 'Theater',
  opera_house: 'Opernhaus',
  other: 'Wechselnde Spielstätten',
};

export const INSTITUTION_TYPE_LABELS: Record<InstitutionType, string> = {
  theatre: 'Theater',
  opera_house: 'Opernhaus',
  broadcaster: 'Rundfunkanstalt',
  orchestra_institution: 'Orchestergesellschaft',
  cultural_institution: 'Kulturinstitution',
};

export const GENRE_LABELS: Record<Genre, string> = {
  symphony: 'Sinfonie',
  concerto: 'Konzert',
  overture: 'Ouvertüre',
  opera: 'Oper',
  oratorio: 'Oratorium',
  requiem: 'Requiem',
  chamber_music: 'Kammermusik',
  other: 'Sonstiges',
};

export const EVENT_STATUS_LABELS: Record<EventStatus, string> = {
  scheduled: 'Geplant',
  cancelled: 'Abgesagt',
  postponed: 'Verschoben',
  rescheduled: 'Neu angesetzt',
};

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  concert: 'Konzert',
  opera: 'Oper',
  festival: 'Festival',
};

export function label<T extends string>(map: Record<T, string>, key: T | null | undefined): string {
  if (!key) return '';
  return map[key] ?? key;
}
