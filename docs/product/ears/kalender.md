# EARS – Konzertkalender

**System:** der Kalender

Der Kalender ist die Startansicht und zeigt einen Monat als Montag–Sonntag-Raster mit
kompakten Veranstaltungskacheln. Siehe auch [Contract](../contracts/kalender.feature).

## Anforderungen

- **KAL-1** (ubiquitär): Der Kalender MUSS einen Monat als Raster mit sieben Spalten von
  Montag bis Sonntag darstellen.

- **KAL-2** (ubiquitär): Der Kalender MUSS Monats- und Wochentagsnamen in deutscher Sprache
  anzeigen.

- **KAL-3** (ereignisgesteuert): WENN die Startseite ohne Monatsangabe geöffnet wird, MUSS
  der Kalender den aktuellen Monat anzeigen.

- **KAL-4** (ereignisgesteuert): WENN eine Adresse der Form `/calendar/<jahr>/<monat>` mit
  gültigem Monat aufgerufen wird, MUSS der Kalender diesen Monat anzeigen.

- **KAL-5** (unerwünschtes Verhalten): FALLS die Monatsangabe in der Adresse ungültig ist,
  DANN MUSS der Kalender den aktuellen Monat anzeigen.

- **KAL-6** (ubiquitär): Der Kalender MUSS die Anzahl der Veranstaltungen des angezeigten
  Monats zusammenfassend ausweisen.

- **KAL-7** (zustandsgesteuert): SOLANGE ein Tag Veranstaltungen enthält, MUSS der Kalender
  für diesen Tag je Veranstaltung eine Kachel mit Titel und ausführendem Ensemble anzeigen.

- **KAL-8** (optionales Merkmal): SOFERN für eine Veranstaltung eine Uhrzeit hinterlegt ist,
  MUSS der Kalender die Uhrzeit in der Kachel anzeigen.

- **KAL-9** (zustandsgesteuert): SOLANGE ein Tag mehr als zwei Veranstaltungen enthält, MUSS
  der Kalender die ersten zwei anzeigen und die weiteren als Hinweis „+ N weitere"
  zusammenfassen.

- **KAL-10** (zustandsgesteuert): SOLANGE ein Tag der heutige Tag ist, MUSS der Kalender
  diesen Tag hervorheben.

- **KAL-11** (zustandsgesteuert): SOLANGE eine Veranstaltung den Status „abgesagt" hat, MUSS
  der Kalender die zugehörige Kachel als abgesagt kennzeichnen.

- **KAL-12** (ereignisgesteuert): WENN die Aktion „Nächster" ausgelöst wird, MUSS der
  Kalender den folgenden Monat anzeigen, ohne die Seite vollständig neu zu laden.

- **KAL-13** (ereignisgesteuert): WENN die Aktion „Vorheriger" ausgelöst wird, MUSS der
  Kalender den vorangehenden Monat anzeigen, ohne die Seite vollständig neu zu laden.

- **KAL-14** (ereignisgesteuert): WENN die Aktion „Heute" ausgelöst wird, MUSS der Kalender
  den aktuellen Monat anzeigen.

- **KAL-15** (unerwünschtes Verhalten): FALLS der angezeigte Monat keine Veranstaltungen
  enthält, DANN MUSS der Kalender den Hinweis „Keine Veranstaltungen in diesem Monat."
  anzeigen.

- **KAL-16** (ereignisgesteuert): WENN eine Veranstaltungskachel ausgewählt wird, MUSS der
  Kalender zur Detailseite dieser Veranstaltung wechseln.
