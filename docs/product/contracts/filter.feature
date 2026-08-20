# language: de

Funktionalität: Ort-Filter für Kalender, Ensembles und Spielstätten
  Unterhalb der Seitenüberschrift von Konzertkalender, Ensembles und Spielstätten
  stehen Ort-Bubbles, mit denen die Anzeige über den Sitzort der Ensembles auf eine
  oder mehrere Städte eingeschränkt werden kann. Die Auswahl bleibt beim Wechsel
  zwischen den drei Listen erhalten.

  Grundlage:
    Angenommen der Datenbestand ist geladen

  Regel: Bubbles stammen aus den Sitzorten der Ensembles

    Szenario: Nur Städte mit ansässigem Ensemble erzeugen eine Bubble
      Wenn ich den Konzertkalender öffne
      Dann sehe ich genau eine Ort-Bubble je Stadt, in der mindestens ein Ensemble seinen Sitz hat
      Aber ich sehe keine Bubble für Städte, die nur als Veranstaltungsort vorkommen

    Szenario: Bubbles tragen das Kfz-Kennzeichen
      Wenn ich den Konzertkalender öffne
      Dann zeigt jede Ort-Bubble das Kfz-Kennzeichen der Stadt
      Und die Bubble für Köln zeigt "K"
      Und die Bubble für Düsseldorf zeigt "D"

  Regel: Ohne Auswahl werden alle Inhalte angezeigt

    Szenario: Standardzustand ist ohne Auswahl
      Wenn ich den Konzertkalender zum ersten Mal öffne
      Dann ist keine Bubble ausgewählt
      Und es werden alle Veranstaltungen angezeigt

  Regel: Eine Auswahl filtert konsistent über den Sitzort der Ensembles

    Szenario: Kalender zeigt nur Veranstaltungen der gewählten Städte
      Angenommen ich habe die Bubble "K" ausgewählt
      Wenn ich den Konzertkalender betrachte
      Dann sehe ich nur Veranstaltungen, bei denen mindestens ein auftretendes Ensemble seinen Sitz in Köln hat
      Und ein Gastspiel eines Kölner Ensembles außerhalb Kölns erscheint weiterhin

    Szenario: Ensemble-Liste zeigt nur Ensembles der gewählten Städte
      Angenommen ich habe die Bubble "K" ausgewählt
      Wenn ich die Ensemble-Liste betrachte
      Dann sehe ich nur Ensembles mit Sitz in Köln

    Szenario: Spielstätten-Liste zeigt nur bespielte Spielstätten der gewählten Städte
      Angenommen ich habe die Bubble "K" ausgewählt
      Wenn ich die Spielstätten-Liste betrachte
      Dann sehe ich nur Spielstätten, in denen Ensembles aus Köln auftreten

  Regel: Mehrfachauswahl wirkt additiv und lässt sich aufheben

    Szenario: Additive Mehrfachauswahl
      Angenommen ich habe die Bubble "K" ausgewählt
      Wenn ich zusätzlich die Bubble "D" auswähle
      Dann sehe ich Inhalte aus Köln und Düsseldorf

    Szenario: Abwählen einer Bubble
      Angenommen ich habe die Bubbles "K" und "D" ausgewählt
      Wenn ich die Bubble "K" erneut anklicke
      Dann ist "K" nicht mehr ausgewählt
      Und ich sehe nur noch Inhalte aus Düsseldorf

    Szenario: Alle Bubbles abgewählt zeigt wieder alle Inhalte
      Angenommen ich habe die Bubble "K" ausgewählt
      Wenn ich die Bubble "K" erneut anklicke
      Dann ist keine Bubble ausgewählt
      Und es werden wieder alle Inhalte angezeigt

  Regel: Die Auswahl bleibt beim Seitenwechsel erhalten

    Szenario: Persistenz über die Navigation
      Angenommen ich habe im Konzertkalender die Bubble "K" ausgewählt
      Wenn ich zur Ensemble-Liste wechsle
      Dann ist die Bubble "K" weiterhin ausgewählt
      Und die Ensemble-Liste ist auf Köln eingeschränkt

  Regel: Beschreibung und Navigation

    Szenario: Info-Button blendet die Seitenbeschreibung ein und aus
      Angenommen die Seitenbeschreibung ist nicht sichtbar
      Wenn ich den Info-Button "i" auswähle
      Dann sehe ich die Seitenbeschreibung
      Und wenn ich den Info-Button erneut auswähle, wird die Beschreibung wieder ausgeblendet

    Szenario: Hauptnavigation als Burger-Menü in allen Viewports
      Wenn ich eine beliebige Seite in beliebiger Fensterbreite öffne
      Dann sehe ich die Hauptnavigation als quadratisches Burger-Menü
