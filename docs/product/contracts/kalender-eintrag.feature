# language: de

Funktionalität: Termin in den Kalender eintragen
  Auf der Veranstaltungsdetailseite kann ich einen Termin mit einem Klick in meinen
  Gerätekalender übernehmen. Klangland erzeugt dafür clientseitig eine standardkonforme
  iCalendar-Datei (.ics, RFC 5545) für genau dieses Event – ohne Backend.

  Grundlage:
    Angenommen der Datenbestand ist geladen
    Und es gibt die Veranstaltung "Mahler 3" am 2. Oktober 2026 um 19:30 Uhr

  Szenario: Aktion ist vorhanden und bedienbar
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich ein Bedienelement "In den Kalender eintragen"
    Und das Bedienelement ist ein per Tastatur bedienbarer Button

  Szenario: Ein Klick erzeugt clientseitig eine .ics-Datei
    Wenn ich die Detailseite von "Mahler 3" öffne
    Und ich "In den Kalender eintragen" auslöse
    Dann wird eine iCalendar-Datei (.ics) für "Mahler 3" erzeugt und zum Download angeboten
    Und es wird kein Backend-Aufruf benötigt

  Szenario: Die Datei enthält die Pflichtfelder
    Wenn ich für "Mahler 3" die Kalenderdatei erzeuge
    Dann enthält die Datei den Titel "Mahler 3"
    Und den Startzeitpunkt aus Datum und Uhrzeit
    Und den Ort aus Spielstätte und Stadt
    Und eine Beschreibung mit Ensemble(s) und Dirigent:in
    Und einen Link zurück zur Detailseite von "Mahler 3"

  Szenario: Start und Ende verwenden die Zeitzone Europe/Berlin
    Angenommen "Mahler 3" hat eine Endzeit von 21:30 Uhr
    Wenn ich für "Mahler 3" die Kalenderdatei erzeuge
    Dann sind Beginn und Ende in der Zeitzone Europe/Berlin hinterlegt
    Und der Zielkalender zeigt Beginn 19:30 Uhr und Ende 21:30 Uhr

  Szenario: Fehlende Uhrzeit erzeugt einen ganztägigen Eintrag
    Angenommen für "Mahler 3" ist keine Beginnzeit erfasst
    Wenn ich für "Mahler 3" die Kalenderdatei erzeuge
    Dann enthält die Datei einen ganztägigen Eintrag am Veranstaltungsdatum

  Szenario: Ein abgesagtes Konzert wird im Kalendereintrag kenntlich gemacht
    Angenommen "Mahler 3" ist abgesagt
    Wenn ich für "Mahler 3" die Kalenderdatei erzeuge
    Dann ist der Eintrag als abgesagt gekennzeichnet
    Und der Titel weist die Absage aus

  Szenario: Erneuter Import aktualisiert statt zu duplizieren
    Angenommen ich habe "Mahler 3" bereits in meinen Kalender importiert
    Wenn ich die Kalenderdatei erneut importiere
    Dann trägt der Eintrag dieselbe eindeutige Kennung
    Und der bestehende Termin wird aktualisiert statt dupliziert
