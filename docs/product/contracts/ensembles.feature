# language: de

Funktionalität: Ensembles
  Klangland bietet eine Übersicht aller erfassten Ensembles sowie ein Profil je
  Ensemble mit Stammdaten und den zugehörigen Veranstaltungen.

  Grundlage:
    Angenommen der Datenbestand ist geladen

  Rule: Die Ensembleübersicht listet alle Ensembles

    Szenario: Alle Ensembles werden alphabetisch angezeigt
      Wenn ich die Seite "Ensembles" öffne
      Dann sehe ich alle erfassten Ensembles
      Und sie sind alphabetisch nach Namen sortiert

    Szenario: Eine Ensemblekarte zeigt die wichtigsten Stammdaten
      Angenommen es gibt das Ensemble "Düsseldorfer Symphoniker"
      Wenn ich die Seite "Ensembles" öffne
      Dann zeigt die Karte den Namen "Düsseldorfer Symphoniker"
      Und den Sitzort
      Und die Chefdirigentin oder den Chefdirigenten
      Und die Anzahl der erfassten Veranstaltungen

    Szenario: Zu einem Ensembleprofil wechseln
      Angenommen es gibt das Ensemble "Düsseldorfer Symphoniker"
      Wenn ich auf der Seite "Ensembles" die Karte "Düsseldorfer Symphoniker" wähle
      Dann gelange ich zum Profil dieses Ensembles

  Rule: Das Ensembleprofil zeigt Stammdaten und Veranstaltungen

    Szenario: Stammdaten eines Ensembles
      Angenommen es gibt das Ensemble "Düsseldorfer Symphoniker" in "Düsseldorf"
      Und die Chefdirigentin bzw. der Chefdirigent ist hinterlegt
      Wenn ich das Profil von "Düsseldorfer Symphoniker" öffne
      Dann sehe ich den Namen, den Sitzort und die Leitung des Ensembles
      Und, sofern hinterlegt, den Stammsaal und die Trägerinstitution

    Szenario: Veranstaltungen des Ensembles
      Angenommen die "Düsseldorfer Symphoniker" haben erfasste Konzerte
      Wenn ich das Profil von "Düsseldorfer Symphoniker" öffne
      Dann sehe ich die zugehörigen Veranstaltungen chronologisch geordnet

    Szenario: Von einem Ensembleprofil zu einer Veranstaltung
      Angenommen die "Düsseldorfer Symphoniker" haben das Konzert "Mahler 3"
      Wenn ich im Profil das Konzert "Mahler 3" wähle
      Dann gelange ich zur Detailseite dieser Veranstaltung

    Szenario: Direkter Deep-Link auf ein Ensembleprofil
      Wenn ich die Adresse "/ensembles/duesseldorfer-symphoniker" aufrufe
      Dann sehe ich das Profil von "Düsseldorfer Symphoniker"

  Rule: Das Ensembleprofil zeigt Grundtyp, Rollen und musikalische Schwerpunkte

    Szenario: Grundtyp und Rollen eines Ensembles
      Angenommen es gibt das Ensemble "Beethoven Orchester Bonn"
      Wenn ich das Profil von "Beethoven Orchester Bonn" öffne
      Dann sehe ich den Grundtyp "Orchester"
      Und die Rollen "Sinfonieorchester" und "Opernorchester"

    Szenario: Musikalische Schwerpunkte werden angezeigt
      Angenommen es gibt das Ensemble "Beethoven Orchester Bonn"
      Wenn ich das Profil von "Beethoven Orchester Bonn" öffne
      Dann sehe ich seine musikalischen Schwerpunkte

    Szenario: Ein Ensemble mit mehreren Rollen zeigt alle Rollen
      Angenommen es gibt ein Ensemble mit mehreren Rollen
      Wenn ich sein Profil öffne
      Dann sehe ich alle zugeordneten Rollen
