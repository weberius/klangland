# language: de

Funktionalität: Datenladen und Navigation
  Die App ist statisch und lädt ihren Datenbestand einmalig beim Start aus
  versionierten JSON-Dateien. Fehlerhafte oder fehlende Daten dürfen die App
  nicht zum Absturz bringen. Grundlegende Navigation und Erreichbarkeit sind
  auf jeder Seite gegeben.

  Szenario: Erfolgreiches Laden des Datenbestands
    Angenommen die JSON-Daten sind verfügbar
    Wenn ich die App öffne
    Dann werden Ensembles, Spielstätten und Veranstaltungen angezeigt

  Szenario: Fehler beim Laden des Datenbestands
    Angenommen die JSON-Daten können nicht geladen werden
    Wenn ich die App öffne
    Dann sehe ich den Hinweis "Die Veranstaltungsdaten konnten nicht geladen werden."
    Und die Anwendung stürzt nicht ab

  Szenario: Hauptnavigation ist auf jeder Seite verfügbar
    Angenommen der Datenbestand ist geladen
    Wenn ich eine beliebige Seite öffne
    Dann sehe ich die Navigation zu "Kalender", "Ensembles" und "Spielstätten"

  Szenario: Aufruf einer unbekannten Adresse
    Angenommen der Datenbestand ist geladen
    Wenn ich eine nicht existierende Adresse aufrufe
    Dann sehe ich den Hinweis "Seite nicht gefunden"
    Und ich sehe einen Verweis zurück zum Kalender

  Szenario: Konfigurierbares Referenzdatum für "heute"
    Angenommen als Referenzdatum ist der 1. Oktober 2026 konfiguriert
    Wenn ich die Startseite öffne
    Dann wird der Kalender für "Oktober 2026" als aktueller Monat angezeigt
