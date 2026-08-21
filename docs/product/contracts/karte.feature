# language: de

Funktionalität: Karte der Ensemble-Orte
  Unter "/cities" zeigt eine OpenStreetMap-Karte alle Orte mit ansässigem Ensemble
  als rote Marker. Ein Klick auf einen Marker öffnet einen Dialog mit den Ensembles
  des Ortes und einem Button, der den Ort-Filter setzt oder entfernt. Der Filter wirkt
  über den gemeinsamen Filterdienst und bleibt beim Seitenwechsel erhalten.

  Grundlage:
    Angenommen der Datenbestand ist geladen
    Und ich öffne die Kartenseite unter "/cities"

  Regel: Die Karte zeigt nur Ensemble-Orte als rote Marker

    Szenario: Nur Städte mit ansässigem Ensemble erhalten einen Marker
      Wenn die Karte geladen ist
      Dann sehe ich einen roten Marker für jede Stadt mit mindestens einem ansässigen Ensemble
      Aber ich sehe keinen Marker für Städte, die nur als Veranstaltungsort vorkommen
      Und ich sehe keine Marker für Spielstätten

    Szenario: Marker sitzen auf der Stadtkoordinate
      Wenn die Karte geladen ist
      Dann liegt der Marker für Köln auf den Koordinaten der Stadt Köln
      Und nicht auf der Koordinate einer einzelnen Spielstätte

    Szenario: Die Karte nennt OpenStreetMap als Quelle
      Wenn die Karte geladen ist
      Dann sehe ich die OpenStreetMap-Attribution auf der Karte

  Regel: Ein Klick auf einen Marker öffnet den Ensemble-Dialog

    Szenario: Dialog listet die Ensembles des Ortes
      Wenn ich den Marker für Köln anklicke
      Dann öffnet sich ein Dialog
      Und der Dialog listet die in Köln ansässigen Ensembles

    Szenario: Dialog lässt sich mit Escape schließen
      Angenommen ich habe den Marker für Köln angeklickt
      Wenn ich die Escape-Taste drücke
      Dann ist der Dialog geschlossen

  Regel: Aus dem Dialog wird der Ort-Filter gesetzt und entfernt

    Szenario: Ort-Filter über den Dialog aktivieren
      Angenommen ich habe den Marker für Köln angeklickt
      Wenn ich im Dialog den Filter-Button auslöse
      Dann ist der Ort-Filter für Köln aktiv
      Und der Marker für Köln ist auf der Karte hervorgehoben

    Szenario: Ort-Filter über den Dialog wieder entfernen
      Angenommen der Ort-Filter für Köln ist aktiv
      Und ich habe den Marker für Köln angeklickt
      Wenn ich im Dialog den Filter-Button erneut auslöse
      Dann ist der Ort-Filter für Köln nicht mehr aktiv
      Und die Hervorhebung des Markers ist entfernt

  Regel: Der von der Karte gesetzte Filter wirkt seitenübergreifend

    Szenario: Filter aus der Karte bleibt im Kalender aktiv
      Angenommen ich habe über die Karte den Ort-Filter für Köln aktiviert
      Wenn ich zum Konzertkalender wechsle
      Dann ist die Ort-Bubble "K" ausgewählt
      Und der Kalender zeigt nur Veranstaltungen mit Bezug zu Köln
