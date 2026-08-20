// iCalendar-Erzeugung (RFC 5545) für ein einzelnes Event – reine, testbare Funktion
// ohne Angular-/Browser-Abhängigkeiten. Die Detailseite ruft `buildEventIcs` auf und
// stößt den Download an (US-012). Zeitzone Europe/Berlin wird mit eingebettetem
// VTIMEZONE-Block ausgegeben, damit Sommer-/Winterzeit überall korrekt gilt.

import { EventStatus } from '../models/models';
import { pad2, parseIso } from './date-util';

export interface IcsEventInput {
  /** Stabile Event-ID – Basis der eindeutigen UID. */
  id: string;
  title: string;
  /** Veranstaltungsdatum als ISO-String (YYYY-MM-DD). */
  date: string;
  /** Beginn als HH:MM (lokale Wandzeit) oder null für ganztägig. */
  startTime: string | null;
  /** Ende als HH:MM oder null (dann Standarddauer bzw. ganztägig). */
  endTime: string | null;
  status: EventStatus;
  venueName: string | null;
  venueAddress: string | null;
  cityName: string | null;
  ensembleNames: string[];
  conductorNames: string[];
  /** Absolute URL der Event-Detailseite (Rückverweis). */
  eventUrl: string;
  /** Erzeugungszeitpunkt für DTSTAMP; injizierbar für Tests. */
  now?: Date;
}

/** Fehlt eine Endzeit bei gesetztem Beginn, wird diese Standarddauer angenommen. */
const DEFAULT_DURATION_MINUTES = 120;

const PRODID = '-//Klangland//Konzertkalender//DE';

// Statischer VTIMEZONE-Block für Europe/Berlin (CET/CEST inkl. EU-DST-Regeln).
const VTIMEZONE = [
  'BEGIN:VTIMEZONE',
  'TZID:Europe/Berlin',
  'BEGIN:DAYLIGHT',
  'TZOFFSETFROM:+0100',
  'TZOFFSETTO:+0200',
  'TZNAME:CEST',
  'DTSTART:19700329T020000',
  'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU',
  'END:DAYLIGHT',
  'BEGIN:STANDARD',
  'TZOFFSETFROM:+0200',
  'TZOFFSETTO:+0100',
  'TZNAME:CET',
  'DTSTART:19701025T030000',
  'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU',
  'END:STANDARD',
  'END:VTIMEZONE',
];

/** Escaping von Textwerten gemäß RFC 5545 (Reihenfolge beachten: Backslash zuerst). */
function escapeText(value: string): string {
  return value
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\r?\n/g, '\\n');
}

/** Byte-Länge eines Strings in UTF-8 (für oktett-korrekte Zeilenfaltung). */
function byteLength(value: string): number {
  if (typeof TextEncoder !== 'undefined') return new TextEncoder().encode(value).length;
  return unescape(encodeURIComponent(value)).length;
}

/**
 * Zeilenfaltung nach RFC 5545: Zeilen dürfen 75 Oktett nicht überschreiten;
 * Fortsetzungszeilen beginnen mit einem Leerzeichen. Mehrbyte-Zeichen werden nie
 * mitten in einer UTF-8-Sequenz getrennt (Faltung erfolgt zeichenweise).
 */
function foldLine(line: string): string {
  if (byteLength(line) <= 75) return line;
  const out: string[] = [];
  let current = '';
  let currentBytes = 0;
  let first = true;
  for (const char of line) {
    const charBytes = byteLength(char);
    // Fortsetzungszeilen tragen bereits ein führendes Leerzeichen (1 Oktett).
    const limit = first ? 75 : 74;
    if (currentBytes + charBytes > limit) {
      out.push(current);
      current = char;
      currentBytes = charBytes;
      first = false;
    } else {
      current += char;
      currentBytes += charBytes;
    }
  }
  out.push(current);
  return out.map((part, i) => (i === 0 ? part : ' ' + part)).join('\r\n');
}

/** UTC-Zeitstempel im Format YYYYMMDDTHHMMSSZ (für DTSTAMP). */
function formatUtcStamp(date: Date): string {
  return (
    `${date.getUTCFullYear()}${pad2(date.getUTCMonth() + 1)}${pad2(date.getUTCDate())}` +
    `T${pad2(date.getUTCHours())}${pad2(date.getUTCMinutes())}${pad2(date.getUTCSeconds())}Z`
  );
}

/** Lokale Wandzeit im Format YYYYMMDDTHHMMSS (ohne Zeitzonen-Umrechnung). */
function formatLocalDateTime(iso: string, time: string): string {
  const { year, month, day } = parseIso(iso);
  const [hour, minute] = time.split(':').map(Number);
  return `${year}${pad2(month)}${pad2(day)}T${pad2(hour)}${pad2(minute)}00`;
}

/** Reines Datum im Format YYYYMMDD (für ganztägige Einträge). */
function formatDate(iso: string): string {
  const { year, month, day } = parseIso(iso);
  return `${year}${pad2(month)}${pad2(day)}`;
}

/**
 * Addiert Minuten zu einer lokalen Wandzeit und gibt das Ergebnis als
 * YYYYMMDDTHHMMSS zurück. Die Rechnung läuft über UTC, um DST-abhängige
 * Verschiebungen der Laufzeitzone zu vermeiden – es zählt reine Wandzeit-Arithmetik.
 */
function addMinutesLocal(iso: string, time: string, minutes: number): string {
  const { year, month, day } = parseIso(iso);
  const [hour, minute] = time.split(':').map(Number);
  const t = Date.UTC(year, month - 1, day, hour, minute) + minutes * 60_000;
  const d = new Date(t);
  return (
    `${d.getUTCFullYear()}${pad2(d.getUTCMonth() + 1)}${pad2(d.getUTCDate())}` +
    `T${pad2(d.getUTCHours())}${pad2(d.getUTCMinutes())}00`
  );
}

/** Nächster Tag als YYYYMMDD (für DTEND ganztägiger Einträge). */
function nextDay(iso: string): string {
  const { year, month, day } = parseIso(iso);
  const d = new Date(Date.UTC(year, month - 1, day) + 86_400_000);
  return `${d.getUTCFullYear()}${pad2(d.getUTCMonth() + 1)}${pad2(d.getUTCDate())}`;
}

function buildDescription(input: IcsEventInput): string {
  const lines: string[] = [];
  if (input.ensembleNames.length) {
    const label = input.ensembleNames.length === 1 ? 'Ensemble' : 'Ensembles';
    lines.push(`${label}: ${input.ensembleNames.join(', ')}`);
  }
  if (input.conductorNames.length) {
    const label = input.conductorNames.length === 1 ? 'Dirigent:in' : 'Dirigent:innen';
    lines.push(`${label}: ${input.conductorNames.join(', ')}`);
  }
  if (lines.length) lines.push('');
  lines.push(`Mehr Infos: ${input.eventUrl}`);
  return lines.join('\n');
}

function buildLocation(input: IcsEventInput): string {
  return [input.venueName, input.venueAddress, input.cityName]
    .map((part) => part?.trim())
    .filter((part): part is string => Boolean(part))
    .join(', ');
}

/**
 * Erzeugt den vollständigen iCalendar-Text (VCALENDAR mit einem VEVENT) für ein Event.
 * Gibt gültiges RFC-5545-iCalendar mit CRLF-Zeilenenden zurück.
 */
export function buildEventIcs(input: IcsEventInput): string {
  const now = input.now ?? new Date();
  const cancelled = input.status === 'cancelled';
  const summary = cancelled ? `Abgesagt: ${input.title}` : input.title;

  const lines: string[] = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    `PRODID:${PRODID}`,
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    ...VTIMEZONE,
    'BEGIN:VEVENT',
    `UID:${input.id}@klangland`,
    `DTSTAMP:${formatUtcStamp(now)}`,
    `SUMMARY:${escapeText(summary)}`,
  ];

  if (input.startTime) {
    lines.push(`DTSTART;TZID=Europe/Berlin:${formatLocalDateTime(input.date, input.startTime)}`);
    const end = input.endTime
      ? formatLocalDateTime(input.date, input.endTime)
      : addMinutesLocal(input.date, input.startTime, DEFAULT_DURATION_MINUTES);
    lines.push(`DTEND;TZID=Europe/Berlin:${end}`);
  } else {
    // Kein Beginn hinterlegt → ganztägiger Eintrag am Veranstaltungsdatum.
    lines.push(`DTSTART;VALUE=DATE:${formatDate(input.date)}`);
    lines.push(`DTEND;VALUE=DATE:${nextDay(input.date)}`);
  }

  const location = buildLocation(input);
  if (location) lines.push(`LOCATION:${escapeText(location)}`);
  lines.push(`DESCRIPTION:${escapeText(buildDescription(input))}`);
  lines.push(`URL:${escapeText(input.eventUrl)}`);
  lines.push(`STATUS:${cancelled ? 'CANCELLED' : 'CONFIRMED'}`);
  lines.push('END:VEVENT');
  lines.push('END:VCALENDAR');

  return lines.map(foldLine).join('\r\n') + '\r\n';
}

/** Vorschlag für den Dateinamen eines Event-Downloads. */
export function icsFileName(eventId: string): string {
  return `${eventId}.ics`;
}
