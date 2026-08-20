# language: de

Funktionalität: Globale Suche
  Die Webapp bietet auf jeder Seite eine globale Suche in der Kopfzeile, damit
  Inhalte aus dem Datenbestand schnell auffindbar sind.

  Grundlage:
    Angenommen der Datenbestand ist geladen

  Szenario: Suchfeld ist auf jeder Seite verfügbar
    Wenn ich eine beliebige Seite öffne
    Dann sehe ich in der Kopfzeile ein Suchfeld

  Szenario: Suche startet erst ab drei Zeichen
    Wenn ich in das Suchfeld "be" eingebe
    Dann wird keine Suche ausgeführt
    Und ich sehe den Hinweis "Mindestens 3 Zeichen eingeben."

  Szenario: Suche startet automatisch bei Eingabe
    Wenn ich in das Suchfeld "beeth" eingebe
    Dann sehe ich automatisch passende Treffer

  Szenario: Fuzzy-Treffer bei Tippfehlern
    Wenn ich in das Suchfeld "bethoven" eingebe
    Dann sehe ich Treffer zu "Beethoven"

  Szenario: Treffer führen auf bestehende Detail- oder Listenansichten
    Angenommen ich sehe einen Treffer in der Ergebnisliste
    Wenn ich den Treffer auswähle
    Dann gelange ich zur passenden Seite des Treffers
