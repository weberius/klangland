// TypeScript-Modelle für die Klangland-Datenobjekte.
// Entspricht den Dokumenten unter /docs (data-model.md, entities/*, events-and-relations.md).

export interface Metadata {
  version: string;
  lastUpdated: string;
  language?: string;
  season?: string;
  scope?: string;
  notes?: string;
}

export interface City {
  id: string;
  name: string;
  country: string;
  /**
   * Kfz-Kennzeichen der Stadt (z. B. Köln → „K"). Nur für Städte mit ansässigem
   * Ensemble gepflegt; steuert die Ort-Filter-Bubbles (US-011). Städte ohne
   * Kennzeichen erzeugen keine Bubble.
   */
  plate?: string;
  /**
   * Geokoordinaten der Stadt selbst (nicht einer Spielstätte). Nur für Städte mit
   * ansässigem Ensemble gepflegt; Grundlage der Kartenmarker (US-013). Per Overpass-
   * API recherchiert (siehe docs/data-tooling/geocode_cities.py).
   */
  coordinates?: Coordinates;
}

export interface Person {
  id: string;
  name: string;
}

export type InstitutionType =
  | 'theatre'
  | 'opera_house'
  | 'broadcaster'
  | 'orchestra_institution'
  | 'cultural_institution';

export interface Institution {
  id: string;
  name: string;
  cityIds: string[];
  region: string | null;
  type: InstitutionType;
  ensembleIds: string[];
}

// Grundtyp – was für ein Ensemble es ist (genau ein Wert).
export type EnsembleType =
  | 'orchestra'
  | 'chamber_orchestra'
  | 'ensemble'
  | 'big_band'
  | 'chorus'
  | 'vocal_ensemble';

// Institutionelle bzw. funktionale Rolle(n) eines Ensembles (0..n).
export type EnsembleRole =
  | 'symphony_orchestra'
  | 'philharmonic_orchestra'
  | 'radio_orchestra'
  | 'opera_orchestra'
  | 'theater_orchestra'
  | 'state_orchestra';

// Musikalische Schwerpunkte eines Ensembles (0..n).
export type MusicalProfile =
  | 'classical'
  | 'romantic'
  | 'baroque'
  | 'early_music'
  | 'historically_informed_performance'
  | 'contemporary'
  | 'new_music'
  | 'opera'
  | 'musical'
  | 'film_music'
  | 'game_music'
  | 'jazz'
  | 'crossover'
  | 'entertainment'
  | 'choral'
  | 'vocal';

export interface Ensemble {
  id: string;
  name: string;
  type: EnsembleType;
  professional: boolean;
  roles: EnsembleRole[];
  musicalProfiles: MusicalProfile[];
  cityIds: string[];
  region: string | null;
  country: string;
  chiefConductorPersonId: string | null;
  description: string | null;
  website: string | null;
  venueId: string | null;
  source: string | null;
  wikipedia: { summary: string; url: string } | null;
}

export type VenueType =
  | 'concert_hall'
  | 'philharmonic_hall'
  | 'theatre'
  | 'opera_house'
  | 'other';

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface Venue {
  id: string;
  name: string;
  cityIds: string[];
  region: string | null;
  address: string | null;
  coordinates: Coordinates | null;
  website: string | null;
  type: VenueType;
  institutionId: string | null;
}

export interface Composer {
  id: string;
  name: string;
  life: { from: number; to: number | null } | null;
  /** Externe Open-Opus-Referenz (US-017); erlaubt Re-Sync/Herkunftsnachweis. */
  openOpusId?: string | null;
  /** Deutschsprachige Epoche, aus Open Opus gemappt (US-017). */
  epoch?: string | null;
  /** Kuratierte Kurzfassung (~60 Wörter) + Artikel-URL, analog Ensemble (US-017). */
  wikipedia?: { summary: string; url: string } | null;
  /** Lokal persistiertes Portrait (US-024); Quelle Wikipedia/Wikimedia Commons. */
  portrait?: {
    file: string; // Dateiname relativ zum Portrait-Verzeichnis (z. B. "ludwig-van-beethoven.jpg")
    source: string; // Quell-URL (Wikipedia/Wikimedia Commons), Ziel der Attribution
    credit?: string | null; // optionale Urheber-/Bildbeschreibung für die Attribution
  } | null;
}

export type Genre =
  | 'symphony'
  | 'concerto'
  | 'overture'
  | 'opera'
  | 'oratorio'
  | 'requiem'
  | 'chamber_music'
  | 'other';

export interface CatalogueEntry {
  system: string;
  number: string;
}

export interface Work {
  id: string;
  composerId: string;
  title: string;
  catalogue: CatalogueEntry[];
  yearComposed: { from: number; to: number } | null;
  genre: Genre;
  durationMinutes: number | null;
  version: string | null;
  scoring: string | null;
  description: string | null;
  /** Externe Open-Opus-Referenz (US-017); erlaubt Re-Sync/Herkunftsnachweis. */
  openOpusId?: string | null;
  /** Open-Opus-Kennzeichen als Grundlage für spätere Werkvorschläge (US-017). */
  popular?: boolean;
  recommended?: boolean;
  /** Kuratierte Kurzfassung (~60 Wörter) + Artikel-URL, analog Ensemble (US-017). */
  wikipedia?: { summary: string; url: string } | null;
}

export interface ProgramItem {
  workId: string;
  movement?: string | null;
  movements?: string[] | null;
  version?: string | null;
}

export type EventStatus = 'scheduled' | 'cancelled' | 'postponed' | 'rescheduled';
export type EventType = 'concert' | 'opera' | 'festival';

export interface EventSource {
  url: string;
  calendarUrl: string | null;
  name: string;
  retrievedAt: string;
}

export interface ConcertEvent {
  id: string;
  title: string;
  eventType: EventType;
  date: string; // YYYY-MM-DD
  startTime: string | null; // HH:MM
  endTime: string | null;
  status: EventStatus;
  ensembleIds: string[];
  venueId: string;
  cityId: string;
  conductorPersonIds: string[];
  soloistPersonIds: string[];
  program: ProgramItem[];
  seriesId: string | null;
  description: string | null;
  source: EventSource | null;
  ticketUrl: string | null;
  lastVerified: string | null;
}

// Umschlag-Typen der einzelnen JSON-Dateien
export interface Wrapped<T> {
  metadata: Metadata;
  [key: string]: unknown | T[];
}
