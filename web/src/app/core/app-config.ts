// Laufzeitkonfiguration der App.

export interface AppConfig {
  // Basis-Pfad der JSON-Daten (relativ zum <base href>).
  dataBasePath: string;
  // Referenzdatum für "heute" (YYYY-MM-DD). null = tatsächliches Systemdatum.
  // Für Demo/Tests kann hier z. B. '2026-10-01' gesetzt werden, damit
  // Beispiel-Events im Kalender sichtbar sind.
  referenceDate: string | null;
}

export const APP_CONFIG: AppConfig = {
  dataBasePath: 'data',
  // DEMO: Auf '2026-10-01' gesetzt, damit die aktuellen Beispiel-Events (Okt/Nov 2026)
  // beim Öffnen sichtbar sind. Für den Produktivbetrieb auf null setzen
  // (dann wird der tatsächliche aktuelle Monat angezeigt).
  referenceDate: '2026-09-01',
};
