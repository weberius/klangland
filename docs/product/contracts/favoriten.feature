# language: de

Funktionalität: Favoriten für Events (markieren, filtern, teilen)
  Besucher:innen können einzelne Konzerte als Favoriten markieren, die Kalender-Anzeige
  auf ihre Favoriten einschränken und die Auswahl per Link teilen. Favoriten leben nur im
  Speicher; wiederhergestellt wird die Auswahl ausschließlich über einen geteilten Link.

  Grundlage:
    Angenommen der Datenbestand ist geladen

  Regel: Favoriten lassen sich nur für Events markieren

    Szenario: Event auf der Detailseite als Favorit markieren
      Angenommen ich betrachte die Detailseite eines Konzerts
      Wenn ich den Favoriten-Stern auswähle
      Dann ist das Konzert als Favorit markiert
      Und der Stern zeigt den aktiven Zustand an

    Szenario: Favoriten-Markierung wieder aufheben
      Angenommen ich habe ein Konzert als Favorit markiert
      Wenn ich den Favoriten-Stern erneut auswähle
      Dann ist das Konzert nicht mehr als Favorit markiert

    Szenario: Ensembles und Spielstätten kennen keine Favoriten
      Wenn ich ein Ensemble- oder Spielstättenprofil betrachte
      Dann gibt es dort kein Favoriten-Symbol

  Regel: Favorisierte Events sind in der Übersicht gekennzeichnet

    Szenario: Stern in der Kalender-Kachel
      Angenommen ich habe ein Konzert als Favorit markiert
      Wenn ich den Konzertkalender betrachte
      Dann trägt die Kachel des Konzerts einen Stern in der rechten oberen Ecke

  Regel: Der Favoriten-Filter wirkt nur auf den Kalender

    Szenario: „Nur Favoriten" schränkt den Kalender ein
      Angenommen ich habe zwei Konzerte als Favoriten markiert
      Wenn ich im Filter-Popover "Nur Favoriten" einschalte
      Dann zeigt der Kalender ausschließlich meine favorisierten Konzerte

    Szenario: Kombination mit Ort und Musikprofil
      Angenommen ich habe mehrere Konzerte als Favoriten markiert
      Und "Nur Favoriten" ist eingeschaltet
      Wenn ich zusätzlich Köln und Düsseldorf sowie Klassik und Oper auswähle
      Dann sehe ich nur favorisierte Konzerte mit Klassik oder Oper in Köln oder Düsseldorf

    Szenario: Ensemble- und Spielstätten-Liste bleiben unberührt
      Angenommen "Nur Favoriten" ist eingeschaltet
      Wenn ich die Ensemble- oder Spielstätten-Liste betrachte
      Dann ist deren Inhalt vom Favoriten-Filter unbeeinflusst

  Regel: Zurücksetzen räumt Filter und Markierungen ab

    Szenario: „Alle zurücksetzen" entfernt auch die Favoriten
      Angenommen ich habe Ort-/Profil-Filter gesetzt und Konzerte favorisiert
      Und "Nur Favoriten" ist eingeschaltet
      Wenn ich im Popover "Alle zurücksetzen" auswähle
      Dann sind Ort-/Profil-Filter, der Favoriten-Filter und alle Markierungen entfernt

  Regel: Teilen und Wiederherstellen erfolgen ausschließlich über den Link

    Szenario: Teilen erzeugt einen Link mit den Favoriten
      Angenommen ich habe Konzerte als Favoriten markiert
      Wenn ich im Popover "Teilen" auswähle
      Dann erhalte ich einen Link, dessen Query-Parameter die favorisierten Konzerte kodiert

    Szenario: Öffnen eines geteilten Links stellt die Favoriten wieder her
      Angenommen ich öffne die App über einen geteilten Favoriten-Link
      Wenn die App geladen ist
      Dann sind die im Link enthaltenen Konzerte als Favoriten markiert
      Aber unbekannte oder ungültige IDs im Link werden ignoriert

    Szenario: Ohne Favoriten-Parameter gibt es keine Favoriten
      Wenn ich die App ohne Favoriten-Parameter öffne oder neu lade
      Dann sind keine Favoriten markiert
      Und der Favoriten-Filter ist ausgeschaltet
