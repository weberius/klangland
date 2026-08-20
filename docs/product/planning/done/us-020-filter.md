# User Story 020 - Kombinierter Filter (Ort + Musikprofil) im Kopfleisten-Popover

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** die Anzeige von Kalender, Ensembles und Spielstätten platzsparend über einen
Filter-Button in der Kopfleiste nach **Ort** und zusätzlich nach **Musikprofil** der
Ensembles einschränken können,
**damit** ich gezielt die Angebote finde, die mich interessieren, ohne dass der Filter
dauerhaft viel Platz unter der Überschrift beansprucht.

## Kontext / Problem

Mit [US-011](../done/US-011-filter.md) wurde ein Ort-Filter eingeführt: eine Reihe von
Kennzeichen-Bubbles unterhalb der Seitenüberschrift, gesteuert über den Sitzort der
Ensembles ([city-filter.html](../../../../web/src/app/shared/city-filter/city-filter.html),
[filter.service.ts](../../../../web/src/app/core/filter.service.ts)). Diese Lösung hat zwei
Schwächen:

1. **Platzbedarf:** Die Bubble-Zeile steht dauerhaft unter jeder Überschrift und bricht bei
   wachsender Städtezahl über mehrere Zeilen um – auch wenn gar nicht gefiltert wird.
2. **Nur ein Kriterium:** Es kann ausschließlich nach Ort gefiltert werden. Ein Filter nach
   dem **musikalischen Profil** der Ensembles (`ensemble.musicalProfiles`, 16 mögliche Werte,
   deutsche Labels in [labels.ts](../../../../web/src/app/core/labels.ts#L25)) fehlt. Eine
   zweite Dauer-Bubblezeile wäre noch raumgreifender.

Zusätzlich beansprucht die globale Suche in der Kopfleiste viel Breite
([app.css](../../../../web/src/app/app.css#L49): `flex: 1 1 20rem`, bis `44rem`), sodass in
der Kopfleiste kein Platz für einen Filter-Auslöser eingeplant ist.

**Betroffen** sind die Kopfleiste ([app.html](../../../../web/src/app/app.html)), der
Konzertkalender, die Ensemble-Liste und die Spielstätten-Liste sowie der geteilte
Filterzustand. **Nicht betroffen** sind die Detailseiten und die Funktionsweise der globalen
Suche (nur ihre Breite ändert sich).

## Gewählte Lösung

**Ein zentraler Filter-Auslöser in der Kopfleiste, der ein Popover mit beiden Filtergruppen
öffnet.** Die Suche wird schmaler; rechts daneben (vor der Navigation) steht ein
**Filter-Button** mit einem **Aktiv-Zähler** (z. B. „Filter · 2"). Der Button öffnet ein
Popover mit zwei Abschnitten:

- **Ort:** je eine Chip-Schaltfläche mit Kfz-Kennzeichen für jede Stadt mit ansässigem
  Ensemble (wie in US-011).
- **Musikprofil:** je eine Chip-Schaltfläche mit deutschem Label für jedes musikalische
  Profil, das bei mindestens einem Ensemble tatsächlich vorkommt (keine leeren Profile).

Die bisher dauerhaft sichtbare Bubble-Zeile entfällt. Stattdessen werden **aktive Filter als
entfernbare Chips** unterhalb der Seitenüberschrift angezeigt – solange nichts ausgewählt
ist, beansprucht der Filter dort **keinen** Platz.

Der Filter wirkt weiterhin **global** (Kalender, Ensembles, Spielstätten) und **persistiert**
über Seitenwechsel hinweg (In-App, nicht über Reload/Session hinaus). Die Auswahl ist
**additiv**: **ODER** innerhalb einer Kategorie, **UND** zwischen den Kategorien. Ort und
Profil müssen von **demselben** auftretenden Ensemble erfüllt werden (ein Kölner
Klassik-Ensemble erscheint unter „K" + „Klassik", ein Kölner Jazz-Ensemble nicht).

Der Info-Button („i") mit der Seitenbeschreibung bleibt unabhängig vom Filter erhalten. Er
wird hinter der Überschrift platziert; sein Verhalten ändert sich nicht.

## Akzeptanzkriterien

1. **Filter-Button:** In der Kopfleiste steht auf jeder Seite zwischen Suche und Navigation
   ein Filter-Button, der ein Popover öffnet und schließt.
2. **Aktiv-Zähler:** Der Filter-Button zeigt die Anzahl der aktiven Filter (Summe aus Orten
   und Profilen); ohne Auswahl wird kein Zähler bzw. „0" angezeigt.
3. **Schmalere Suche:** Das Suchfeld ist schmaler als zuvor und lässt in der Kopfleiste Platz
   für den Filter-Button; die Suchfunktion selbst bleibt unverändert.
4. **Popover – Ort:** Das Popover enthält einen Abschnitt „Ort" mit genau einer
   Chip-Schaltfläche (Kfz-Kennzeichen) je Stadt mit ansässigem Ensemble.
5. **Popover – Musikprofil:** Das Popover enthält einen Abschnitt „Musikprofil" mit genau
   einer Chip-Schaltfläche (deutsches Label) je Profil, das bei mindestens einem Ensemble
   vorkommt; nicht vorkommende Profile erscheinen nicht.
6. **Standardzustand:** Beim ersten Aufruf ist nichts ausgewählt und es werden alle Inhalte
   angezeigt.
7. **ODER innerhalb Kategorie:** Mehrere ausgewählte Orte bzw. mehrere ausgewählte Profile
   werden je Kategorie additiv (ODER) verknüpft.
8. **UND zwischen Kategorien:** Sind Ort **und** Profil ausgewählt, werden nur Inhalte
   angezeigt, bei denen dasselbe auftretende Ensemble Sitzort **und** Profil erfüllt.
9. **Wirkung Kalender:** Der Kalender zeigt nur Events, bei denen mindestens ein auftretendes
   Ensemble die aktive Filterkombination erfüllt.
10. **Wirkung Ensembles:** Die Ensemble-Liste zeigt nur Ensembles, die die aktive
    Filterkombination erfüllen.
11. **Wirkung Spielstätten:** Die Spielstätten-Liste zeigt nur Spielstätten, in denen
    Ensembles auftreten, die die aktive Filterkombination erfüllen.
12. **Persistenz:** Die Auswahl bleibt beim Wechsel zwischen Kalender-, Ensemble- und
    Spielstätten-Seite erhalten.
13. **Aktive Filter als Chips:** Unterhalb der Seitenüberschrift werden die aktiven Filter
    als Chips angezeigt; jeder Chip lässt sich einzeln über ein „✕" entfernen. Ohne Auswahl
    wird dort kein Filter-Element angezeigt.
14. **Zurücksetzen:** Im Popover gibt es eine Möglichkeit, alle Filter auf einmal zu
    entfernen; sie ist nur bei aktiver Auswahl verfügbar.
15. **Abwählen:** Eine ausgewählte Chip-Schaltfläche im Popover kann durch erneutes Anklicken
    wieder abgewählt werden.
16. **Markierung:** Ausgewählte Chip-Schaltflächen im Popover sind sichtbar markiert.
17. **Info-Button:** Der Info-Button („i") mit der Seitenbeschreibung bleibt unabhängig vom
    Filter erhalten, wird hinter der Überschrift platziert und behält sein bisheriges
    Verhalten.
18. **Popover-Verhalten:** Das Popover schließt bei Klick außerhalb, mit ESC und bei
    Seitennavigation.
19. **Barrierefreiheit:** Filter-Button (`aria-haspopup`, `aria-expanded`, `aria-controls`),
    Chip-Schaltflächen (`aria-pressed`) und die entfernbaren aktiven Chips sind per Tastatur
    bedienbar und kommunizieren ihren Zustand an assistive Technologien.
20. **Responsiv:** In schmalen Viewports bleibt der Filter-Button bedienbar (ggf. auf
    Symbol + Zähler reduziert), ohne die Kopfleiste zu überladen.

## Out of Scope

- Filtern nach weiteren Kriterien (Ensemble-Typ, Genre, Zeitraum, Veranstaltungsort eines
  Events).
- Persistieren der Auswahl über Reload/Browser-Sitzung hinaus (nur In-App-Persistenz).
- Änderungen an der Suchlogik über die Feldbreite hinaus.
- Änderungen an den Detailseiten (Event, Ensemble, Spielstätte).
- Filtern von Ensembles/Events über das Profil einer *anderen* als der auftretenden Formation.
