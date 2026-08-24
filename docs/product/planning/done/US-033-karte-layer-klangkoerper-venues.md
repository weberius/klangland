# User Story 033 - Zwei Karten-Layer für Klangkörper und Spielstätten

## User Story

**Als** Nutzer:in der Klangland-Karte (`cities`),
**möchte ich** zwischen zwei Karten-Layern wählen können – Standorte der Klangkörper und Adressen der Spielstätten –,
**damit** ich sowohl einen Überblick über die Orchesterlandschaft als auch über die konkreten Veranstaltungsorte erhalte.

## Kontext / Problem

Die Karte auf der `cities`-Seite zeigt aktuell ausschließlich die Standorte der Klangkörper als rote Punkte. Adressen von Spielstätten (Venues) sind nicht sichtbar. Nutzer:innen, die wissen möchten, wo konkrete Veranstaltungen stattfinden, erhalten auf der Karte keine entsprechende Information. Zudem fehlt eine Legende, die die Bedeutung der Kartenpunkte erklärt.

## Gewählte Lösung

Die Karte wird um einen zweiten Layer für die Adressen der Spielstätten ergänzt. Über eine Layer-Auswahl (Checkbox-Gruppe) kann zwischen den beiden Layern gewechselt werden. Der Standort-der-Klangkörper-Layer ist standardmäßig aktiv; der Spielstätten-Layer muss explizit aktiviert werden. Spielstätten werden mit blauen Punkten dargestellt (Klangkörper weiterhin rot). Eine Kartenlegende erklärt die Farbzuordnung.

## Akzeptanzkriterien

1. **Standard-Layer:** Beim Öffnen der Karte ist der Layer „Standorte der Klangkörper" (rote Punkte) aktiv.
2. **Spielstätten-Layer:** Der Layer „Adressen der Spielstätten" (blaue Punkte) kann explizit aktiviert werden.
3. **Layer-Auswahl:** Es gibt ein UI-Element (z. B. Toggle, Checkboxen), das das Umschalten zwischen den Layern erlaubt.
4. **Farbcodierung:** Klangkörper-Standorte sind rot, Spielstätten-Adressen sind blau dargestellt.
5. **Legende:** Die Karte enthält eine Legende, die die Bedeutung der Farben erklärt.
6. **Gleichzeitige Anzeige:** Beide Layer können gleichzeitig aktiv sein, sodass rote und blaue Punkte nebeneinander erscheinen.
7. **Korrekte Daten:** Die blauen Punkte entsprechen den tatsächlichen Adressen der in der Datenbank hinterlegten Spielstätten.

## Out of Scope

- Filterung der Kartenpunkte nach Ort, Musikprofil oder Favoriten.
- Interaktive Pop-ups oder Detail-Panels für Kartenpunkte (sofern nicht bereits vorhanden).
- Weitere Layer jenseits der zwei beschriebenen.
