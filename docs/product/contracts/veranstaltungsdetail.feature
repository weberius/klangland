# language: de

Funktionalität: Veranstaltungsdetail
  Die Detailseite einer Veranstaltung zeigt alle gespeicherten Informationen zu
  einem Konzert: Termin, Mitwirkende, Programm, Spielstätte und die Quelle. Sie
  ist über eine eigene, teilbare URL erreichbar.

  Grundlage:
    Angenommen der Datenbestand ist geladen
    Und es gibt die Veranstaltung "Mahler 3" am 2. Oktober 2026 um 19:30 Uhr

  Szenario: Termin und Titel werden angezeigt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich den Titel "Mahler 3"
    Und ich sehe das ausgeschriebene Datum "Freitag, 2. Oktober 2026"
    Und ich sehe die Uhrzeit "19:30 Uhr"

  Szenario: Mitwirkende werden mit Rollen dargestellt
    Angenommen "Mahler 3" wird von den Düsseldorfer Symphonikern gespielt
    Und "Vitali Alekseenok" dirigiert
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich das Ensemble "Düsseldorfer Symphoniker" als Verweis auf sein Profil
    Und ich sehe "Vitali Alekseenok" als Dirigent:in

  Szenario: Solist:innen werden nur angezeigt, wenn vorhanden
    Angenommen für "Mahler 3" sind keine Solist:innen erfasst
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann wird kein Abschnitt für Solist:innen angezeigt

  Szenario: Das vollständige Programm wird angezeigt
    Angenommen das Programm von "Mahler 3" enthält das Werk "Sinfonie Nr. 3 d-Moll" von "Gustav Mahler"
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich im Programm den Komponisten "Gustav Mahler"
    Und den Werktitel "Sinfonie Nr. 3 d-Moll"
    Und, sofern vorhanden, Katalognummer, Entstehungsjahr, Fassung und Satz

  Szenario: Veranstaltung ohne erfasstes Programm
    Angenommen für "Mahler 3" ist kein Programm und kein Programmhinweis erfasst
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich den Hinweis "Kein Programm erfasst."

  Szenario: Spielstätte mit Adresse und Website
    Angenommen "Mahler 3" findet in der "Tonhalle Düsseldorf" statt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich die Spielstätte "Tonhalle Düsseldorf" als Verweis auf ihr Profil
    Und ich sehe die Stadt
    Und, sofern hinterlegt, die Adresse und einen Link zur Website der Spielstätte

  Szenario: Die Quelle der Veranstaltung ist nachvollziehbar
    Angenommen "Mahler 3" hat die Quelle "Tonhalle Düsseldorf", abgerufen am 2026-08-17
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich einen Quellenlink "Tonhalle Düsseldorf"
    Und den Hinweis "(abgerufen am 2026-08-17)"

  Szenario: Kalenderseite der Quelle wird angezeigt, wenn hinterlegt
    Angenommen "Mahler 3" hat zur Quelle eine Kalender- bzw. Übersichtsseite hinterlegt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich zusätzlich einen Verweis auf die Kalender-/Übersichtsseite der Quelle

  Szenario: Ohne Kalenderseite kein Kalender-Link
    Angenommen für "Mahler 3" ist zur Quelle keine Kalender- bzw. Übersichtsseite hinterlegt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann wird kein Verweis auf eine Kalender-/Übersichtsseite angezeigt

  Szenario: Ticket-Verweis nur bei hinterlegter Ticket-URL
    Angenommen für "Mahler 3" ist keine Ticket-URL hinterlegt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann wird kein Ticket-Verweis angezeigt

  Szenario: Ein abgesagtes Konzert wird gekennzeichnet
    Angenommen "Mahler 3" ist abgesagt
    Wenn ich die Detailseite von "Mahler 3" öffne
    Dann sehe ich einen Hinweis, dass die Veranstaltung abgesagt ist

  Szenario: Aufruf einer nicht existierenden Veranstaltung
    Wenn ich die Detailseite mit einer unbekannten Veranstaltungs-ID öffne
    Dann sehe ich den Hinweis "Diese Veranstaltung wurde nicht gefunden."
    Und ich sehe einen Verweis zurück zum Kalender

  Szenario: Direkter Deep-Link auf eine Veranstaltung
    Wenn ich die Adresse "/events/event-2026-10-02-duesseldorf-mahler3" aufrufe
    Dann sehe ich die Detailseite von "Mahler 3"
