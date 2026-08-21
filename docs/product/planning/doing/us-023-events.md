# User Story 023 - Umgestaltung Veranstaltungsseite

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** auf der Veranstaltungsseite Beschreibung, Programm, Mitwirkende und den Veranstaltungsort inkl. Adresse, Routing-Möglichkeit und einer Karte übersichtlich aufbereitet sehen,
**damit** ich mich schnell über das Konzert informieren und den Weg zur Spielstätte finden kann.

## Kontext / Problem

Die Veranstaltungsdetailseite [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html) stellt die Inhalte heute so dar:

- Ein zweispaltiges Raster ([detail-grid](../../../../web/src/app/pages/event-detail/event-detail.html#L38-L81)) mit den Boxen **Mitwirkende** (links) und **Veranstaltungsort** (rechts).
- Darunter ein volle Breite einnehmender Abschnitt **Programm** ([event-detail.html:83-109](../../../../web/src/app/pages/event-detail/event-detail.html#L83-L109)).
- Anschließend der Abschnitt **Quelle**.

Daraus ergeben sich mehrere Schwächen:

1. Das **Programm** ist inhaltlich der Kern einer Konzertseite, steht aktuell aber unter den Boxen und damit nicht an prominentester Stelle.
2. Die **Beschreibung** des Events ([`ConcertEvent.description`](../../../../web/src/app/models/models.ts#L186)) wird derzeit **gar nicht** angezeigt, obwohl sie in [events.json](../../../../data/events.json) gepflegt wird.
3. Der **Veranstaltungsort** zeigt Name, Stadt, Website und (seit US-022) die Adresse. Es fehlt jedoch eine Möglichkeit, sich zur Spielstätte navigieren zu lassen, sowie eine **Karte**, die den Ort verortet.

Mit US-022 stehen für Spielstätten strukturierte Adressen (`address`) und Geokoordinaten (`coordinates`) zur Verfügung ([`Venue`](../../../../web/src/app/models/models.ts#L131-L139)). Für Kartenanzeige existiert bereits eine Leaflet-/OpenStreetMap-Integration auf der [city-map](../../../../web/src/app/pages/city-map/city-map.ts)-Seite, die als Vorbild dient.

Betroffen ist die Veranstaltungsdetailseite ([event-detail](../../../../web/src/app/pages/event-detail/)). Der Seitenkopf (Titel, Datum, Status, Aktions-Buttons Tickets/Kalender/Merken) und der Abschnitt **Quelle** bleiben inhaltlich unverändert; verändert wird die Anordnung und der Inhalt der darunterliegenden Boxen.

## Gewählte Lösung

### 1. Neues Boxen-Layout

Die vier Inhaltsblöcke werden neu angeordnet.

**Desktop (2×2-Raster):**

```
┌─────────────────────┬─────────────────────┐
│ Programm            │ Mitwirkende         │  (oben links / oben rechts)
│ (Beschreibung +     │                     │
│  Werkliste)         │                     │
├─────────────────────┼─────────────────────┤
│ Veranstaltungsort   │ Karte               │  (unten links / unten rechts)
│ (Adresse + Routing) │                     │
└─────────────────────┴─────────────────────┘
```

**Mobil (gestapelt, in dieser Reihenfolge):**

1. Programm (Beschreibung + Werkliste)
2. Mitwirkende
3. Veranstaltungsort (Adresse + Routing)
4. Karte

Das Programm steht damit in beiden Ansichten an oberster/erster Stelle.

### 2. Beschreibung in der Programm-Box

Die Event-Beschreibung ([`ConcertEvent.description`](../../../../web/src/app/models/models.ts#L186)) wird **innerhalb** der Programm-Box **oberhalb** der Werkliste angezeigt. Ist keine Beschreibung vorhanden (`null`/leer), entfällt sie ersatzlos; die Werkliste bzw. der bestehende Fallback-Text bleibt unverändert.

### 3. Veranstaltungsort mit Adresse

Die Box **Veranstaltungsort** zeigt weiterhin Name (verlinkt auf die Venue-Detailseite), Stadt und – sofern vorhanden – die Website. Zusätzlich wird die **strukturierte Adresse** (US-022) angezeigt. Die bestehende Adressanzeige über `venueAddress()` wird beibehalten bzw. entsprechend eingebunden. Fehlt die Adresse (`null`), entfällt sie.

### 4. Routing-Button mit Anbieterauswahl

In der Veranstaltungsort-Box gibt es einen **Button**, der einen **Dialog** öffnet. Der Dialog bietet Links zu mehreren Kartenanbietern an (z. B. **Google Maps**, **Apple Maps**, **OpenStreetMap**), über die sich Benutzer:innen z. B. eine Route berechnen lassen können. Umgesetzt wird das plattformübergreifend über reguläre Karten-Links (URLs), die in einem neuen Tab geöffnet werden – bevorzugt anhand der Koordinaten, hilfsweise anhand der Adresse.

Der Dialog enthält – analog zum bestehenden Ticket-Dialog ([event-detail.html:130-148](../../../../web/src/app/pages/event-detail/event-detail.html#L130-L148)) – den **Hinweis, dass Benutzer:innen damit das Angebot verlassen**. Das bestehende Dialog-Muster (Backdrop, `role="dialog"`, `aria-modal`, Abbrechen-Aktion) wird wiederverwendet.

Sind weder Koordinaten noch Adresse vorhanden, wird der Routing-Button nicht angeboten.

### 5. Karte des Veranstaltungsortes

Unterhalb bzw. rechts unten wird eine **kleine Karte** angezeigt, die auf die Koordinaten der Spielstätte einzoomt und einen Marker setzt. Umgesetzt wird sie mit **Leaflet und OpenStreetMap-Kacheln**, analog zur [city-map](../../../../web/src/app/pages/city-map/city-map.ts)-Seite (inkl. OSM-Attribution). Hat die Spielstätte keine Koordinaten (`coordinates === null`), wird keine Karte (und keine leere Box) angezeigt.

## Akzeptanzkriterien

1. **Programm zuerst:** In der mobilen Ansicht ist die Programm-Box der erste Inhaltsblock unter dem Seitenkopf; in der Desktop-Ansicht steht sie oben links im 2×2-Raster.
2. **Reihenfolge Desktop:** Im Desktop-Raster gilt: oben links Programm, oben rechts Mitwirkende, unten links Veranstaltungsort, unten rechts Karte.
3. **Reihenfolge Mobil:** In der mobilen (gestapelten) Ansicht erscheinen die Blöcke in der Reihenfolge Programm → Mitwirkende → Veranstaltungsort → Karte.
4. **Beschreibung angezeigt:** Ist `event.description` gesetzt, wird sie innerhalb der Programm-Box oberhalb der Werkliste dargestellt; ist sie `null`/leer, wird nichts angezeigt und der bisherige Programm-/Fallback-Inhalt bleibt unverändert.
5. **Adresse im Veranstaltungsort:** Die Veranstaltungsort-Box zeigt Name (verlinkt), Stadt, ggf. Website sowie – falls vorhanden – die strukturierte Adresse der Spielstätte. Fehlende Bestandteile werden ohne leere Zeilen weggelassen.
6. **Routing-Button:** Sind Koordinaten oder Adresse der Spielstätte vorhanden, gibt es in der Veranstaltungsort-Box einen Button, der einen Dialog öffnet.
7. **Anbieterauswahl im Dialog:** Der Dialog bietet Links zu mindestens zwei gängigen Kartenanbietern (z. B. Google Maps, Apple Maps, OpenStreetMap), die in einem neuen Tab geöffnet werden und – wenn möglich – die Spielstätte anhand der Koordinaten, sonst der Adresse ansteuern.
8. **Hinweis auf Verlassen:** Der Routing-Dialog weist deutlich darauf hin, dass Benutzer:innen mit dem Öffnen eines Kartenanbieters das Angebot verlassen. Der Dialog ist per Abbrechen/Backdrop schließbar und barrierefrei ausgezeichnet (`role="dialog"`, `aria-modal`, beschriftende `aria-labelledby`).
9. **Karte:** Bei vorhandenen Koordinaten wird unten rechts (Desktop) bzw. als letzter Block (Mobil) eine Leaflet-Karte mit OpenStreetMap-Kacheln angezeigt, die auf die Spielstätte einzoomt und diese mit einem Marker markiert; die OSM-Attribution ist sichtbar.
10. **Fehlende Geodaten:** Hat die Spielstätte keine Koordinaten, wird keine (leere) Kartenbox angezeigt. Sind weder Koordinaten noch Adresse vorhanden, wird auch kein Routing-Button angeboten.
11. **Unverändert:** Seitenkopf (Titel, Datum, Status, Buttons Tickets/Kalender/Merken), der Ticket-Dialog und der Abschnitt Quelle bleiben in Inhalt und Verhalten unverändert.

## Out of Scope

- Änderungen an den Datenmodellen oder an [events.json](../../../../data/events.json)/[venues.json](../../../../data/venues.json) (Adresse/Koordinaten stammen aus US-022).
- Recherche/Nachpflege fehlender Adressen oder Koordinaten von Spielstätten.
- Anzeige oder Umgestaltung der Karte/Adresse auf der Venue-Detailseite ([venue-detail](../../../../web/src/app/pages/venue-detail/)).
- Berechnung von Routen/Entfernungen innerhalb von Klangland (es wird nur zu externen Kartenanbietern verlinkt).
- Änderungen am Seitenkopf, am Ticket-Dialog oder am Quelle-Abschnitt.

<!--
Umsetzungs-Tasks:
In separater Datei US-023-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
