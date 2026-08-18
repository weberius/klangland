# language: de

Funktionalität: Konzertkalender
  Der Kalender ist die Startansicht von Klangland und beantwortet die Frage
  "Welche interessanten Orchesterkonzerte gibt es in NRW in diesem Monat?".
  Er zeigt einen Monat als Montag–Sonntag-Raster mit kompakten
  Veranstaltungskacheln und erlaubt die Navigation zwischen Monaten.

  Grundlage:
    Angenommen der Datenbestand ist geladen
    Und als heutiges Datum gilt der 1. Oktober 2026

  Szenario: Beim Öffnen wird der aktuelle Monat angezeigt
    Wenn ich die Startseite öffne
    Dann sehe ich den Kalender für "Oktober 2026"
    Und die Wochentage sind von Montag bis Sonntag angeordnet

  Szenario: Anzahl der Veranstaltungen des Monats wird zusammengefasst
    Wenn ich den Kalender für "Oktober 2026" öffne
    Dann sehe ich eine Zusammenfassung mit der Anzahl der Veranstaltungen in diesem Monat

  Szenario: Ein Konzert erscheint am richtigen Kalendertag
    Angenommen am 2. Oktober 2026 findet das Konzert "Mahler 3" statt
    Wenn ich den Kalender für "Oktober 2026" öffne
    Dann sehe ich am 2. Oktober eine Kachel mit dem Titel "Mahler 3"
    Und die Kachel zeigt das ausführende Ensemble
    Und die Kachel zeigt die Uhrzeit, sofern eine hinterlegt ist

  Szenario: Der heutige Tag ist hervorgehoben
    Wenn ich den Kalender für "Oktober 2026" öffne
    Dann ist der 1. Oktober als heutiger Tag markiert

  Szenario: Mehrere Konzerte an einem Tag werden gekürzt dargestellt
    Angenommen am 3. Oktober 2026 finden vier Konzerte statt
    Wenn ich den Kalender für "Oktober 2026" öffne
    Dann zeigt die Kachel des 3. Oktober die ersten zwei Konzerte
    Und darunter den Hinweis "+ 2 weitere"

  Szenario: Zum nächsten Monat navigieren
    Angenommen ich betrachte den Kalender für "Oktober 2026"
    Wenn ich "Nächster" wähle
    Dann sehe ich den Kalender für "November 2026"
    Und die Seite wird dabei nicht vollständig neu geladen

  Szenario: Zum vorherigen Monat navigieren
    Angenommen ich betrachte den Kalender für "Oktober 2026"
    Wenn ich "Vorheriger" wähle
    Dann sehe ich den Kalender für "September 2026"

  Szenariogrundriss: Monatswechsel über das Jahresende hinweg
    Angenommen ich betrachte den Kalender für "<start>"
    Wenn ich "<richtung>" wähle
    Dann sehe ich den Kalender für "<ziel>"

    Beispiele:
      | start         | richtung   | ziel          |
      | Dezember 2026 | Nächster   | Januar 2027   |
      | Januar 2027   | Vorheriger | Dezember 2026 |

  Szenario: Über einen Deep-Link direkt einen Monat aufrufen
    Wenn ich die Adresse "/calendar/2026/11" aufrufe
    Dann sehe ich den Kalender für "November 2026"

  Szenario: Mit "Heute" zum aktuellen Monat zurückkehren
    Angenommen ich betrachte den Kalender für "Januar 2027"
    Wenn ich "Heute" wähle
    Dann sehe ich den Kalender für "Oktober 2026"

  Szenario: Ein Monat ohne Veranstaltungen
    Angenommen im August 2026 finden keine Veranstaltungen statt
    Wenn ich den Kalender für "August 2026" öffne
    Dann sehe ich den Hinweis "Keine Veranstaltungen in diesem Monat."

  Szenario: Ein abgesagtes Konzert ist als solches erkennbar
    Angenommen das Konzert "Bruckner 7" am 5. Oktober 2026 ist abgesagt
    Wenn ich den Kalender für "Oktober 2026" öffne
    Dann ist die Kachel von "Bruckner 7" als abgesagt gekennzeichnet

  Szenario: Ein Konzert öffnen
    Angenommen am 2. Oktober 2026 findet das Konzert "Mahler 3" statt
    Wenn ich im Kalender die Kachel "Mahler 3" wähle
    Dann gelange ich zur Detailseite dieser Veranstaltung
