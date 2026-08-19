// Deutsche Anzeigetexte für kontrollierte Werte.

import {
  EnsembleRole, EnsembleType, EventStatus, EventType, Genre, InstitutionType, MusicalProfile, VenueType,
} from '../models/models';

export const ENSEMBLE_TYPE_LABELS: Record<EnsembleType, string> = {
  orchestra: 'Orchester',
  chamber_orchestra: 'Kammerorchester',
  ensemble: 'Ensemble',
  big_band: 'Big Band',
  chorus: 'Chor',
  vocal_ensemble: 'Vokalensemble',
};

export const ENSEMBLE_ROLE_LABELS: Record<EnsembleRole, string> = {
  symphony_orchestra: 'Sinfonieorchester',
  philharmonic_orchestra: 'Philharmonisches Orchester',
  radio_orchestra: 'Rundfunkorchester',
  opera_orchestra: 'Opernorchester',
  theater_orchestra: 'Theaterorchester',
  state_orchestra: 'Landesorchester',
};

export const MUSICAL_PROFILE_LABELS: Record<MusicalProfile, string> = {
  classical: 'Klassik',
  romantic: 'Romantik',
  baroque: 'Barock',
  early_music: 'Alte Musik',
  historically_informed_performance: 'Historische Aufführungspraxis',
  contemporary: 'Zeitgenössische Musik',
  new_music: 'Neue Musik',
  opera: 'Oper',
  musical: 'Musical',
  film_music: 'Filmmusik',
  game_music: 'Spielemusik',
  jazz: 'Jazz',
  crossover: 'Crossover',
  entertainment: 'Unterhaltung',
  choral: 'Chormusik',
  vocal: 'Vokalmusik',
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
