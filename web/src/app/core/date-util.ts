// Deutsche Datums-/Kalenderhilfen. Arbeitet mit ISO-Strings (YYYY-MM-DD),
// um Zeitzonenprobleme zu vermeiden.

export const MONTHS_DE = [
  'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember',
];

export const WEEKDAYS_SHORT_DE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
export const WEEKDAYS_LONG_DE = [
  'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag',
];

export function pad2(n: number): string {
  return n < 10 ? '0' + n : String(n);
}

export function isoDate(year: number, month: number, day: number): string {
  return `${year}-${pad2(month)}-${pad2(day)}`;
}

export interface Ymd {
  year: number;
  month: number; // 1-12
  day: number;
}

export function parseIso(iso: string): Ymd {
  const [year, month, day] = iso.split('-').map(Number);
  return { year, month, day };
}

// Montag=0 … Sonntag=6
export function weekdayMondayFirst(year: number, month: number, day: number): number {
  const jsDay = new Date(year, month - 1, day).getDay(); // 0=So … 6=Sa
  return (jsDay + 6) % 7;
}

export function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

export function formatMonthYear(year: number, month: number): string {
  return `${MONTHS_DE[month - 1]} ${year}`;
}

// "2. Oktober 2026"
export function formatLongDate(iso: string): string {
  const { year, month, day } = parseIso(iso);
  return `${day}. ${MONTHS_DE[month - 1]} ${year}`;
}

// "Freitag, 2. Oktober 2026"
export function formatFullDate(iso: string): string {
  const { year, month, day } = parseIso(iso);
  const wd = WEEKDAYS_LONG_DE[weekdayMondayFirst(year, month, day)];
  return `${wd}, ${day}. ${MONTHS_DE[month - 1]} ${year}`;
}

// Heutiges Datum als ISO-String (YYYY-MM-DD). referenceDate erlaubt ein festes
// „Heute" (Demo/Tests), sonst das Systemdatum. Vergleiche laufen lexikografisch
// auf YYYY-MM-DD, konsistent zur übrigen ISO-Datumslogik.
export function todayIso(referenceDate?: string | null): string {
  if (referenceDate) return referenceDate;
  const now = new Date();
  return isoDate(now.getFullYear(), now.getMonth() + 1, now.getDate());
}

export function addMonths(year: number, month: number, delta: number): { year: number; month: number } {
  const zeroBased = month - 1 + delta;
  const newYear = year + Math.floor(zeroBased / 12);
  const newMonth = ((zeroBased % 12) + 12) % 12;
  return { year: newYear, month: newMonth + 1 };
}
