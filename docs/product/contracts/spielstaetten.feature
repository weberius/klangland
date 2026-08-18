# language: de

Funktionalität: Spielstätten
  Klangland bietet eine Übersicht aller erfassten Spielstätten sowie ein Profil
  je Spielstätte mit Stammdaten und den dort stattfindenden Veranstaltungen.

  Grundlage:
    Angenommen der Datenbestand ist geladen

  Rule: Die Spielstättenübersicht listet alle Spielstätten

    Szenario: Alle Spielstätten werden alphabetisch angezeigt
      Wenn ich die Seite "Spielstätten" öffne
      Dann sehe ich alle erfassten Spielstätten
      Und sie sind alphabetisch nach Namen sortiert

    Szenario: Eine Spielstättenkarte zeigt die wichtigsten Angaben
      Angenommen es gibt die Spielstätte "Tonhalle Düsseldorf"
      Wenn ich die Seite "Spielstätten" öffne
      Dann zeigt die Karte den Namen "Tonhalle Düsseldorf"
      Und den Ort
      Und die Anzahl der dort erfassten Veranstaltungen

  Rule: Das Spielstättenprofil zeigt Stammdaten und Veranstaltungen

    Szenario: Stammdaten einer Spielstätte
      Angenommen es gibt die Spielstätte "Tonhalle Düsseldorf" in "Düsseldorf"
      Wenn ich das Profil von "Tonhalle Düsseldorf" öffne
      Dann sehe ich den Namen und den Ort der Spielstätte
      Und, sofern hinterlegt, die Trägerinstitution

    Szenario: Veranstaltungen an der Spielstätte
      Angenommen in der "Tonhalle Düsseldorf" finden erfasste Konzerte statt
      Wenn ich das Profil von "Tonhalle Düsseldorf" öffne
      Dann sehe ich die dort stattfindenden Veranstaltungen chronologisch geordnet

    Szenario: Direkter Deep-Link auf ein Spielstättenprofil
      Wenn ich die Adresse "/venues/tonhalle-duesseldorf" aufrufe
      Dann sehe ich das Profil von "Tonhalle Düsseldorf"
