# User Story 018 - Werke-Seite (Übersicht und Detail)

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** die gespielten Werke auf einer eigenen Seite als alphabetische Übersicht durchstöbern und je Werk eine Detailseite mit weiteren Informationen und den zugehörigen Veranstaltungen öffnen können,
**damit** ich das Repertoire der Saison vom Werk her erschließen und passende Konzerte finden kann.

## Kontext / Problem

Klangland stellt bereits Ensembles, Spielstätten und den Kalender auf eigenen Seiten dar; die Hauptnavigation verweist auf Kalender, Ensembles, Spielstätten und Karte ([app.html:71-74](../../../../web/src/app/app.html#L71-L74)). Für **Werke** existiert bisher keine eigene Seite – sie tauchen nur im Programm einzelner Events auf ([event-detail.html:83-108](../../../../web/src/app/pages/event-detail/event-detail.html#L83-L108)). Ein Einstieg „vom Werk her" fehlt.

Die Daten sind vorhanden: Das [`Work`-Modell](../../../../web/src/app/models/models.ts#L152-L163) enthält Titel, Komponist (`composerId`), Werkverzeichnis-Nummern (`catalogue`), Entstehungszeit (`yearComposed`), Genre, Dauer, Fassung, Besetzung und Beschreibung. Werke werden über `ProgramItem.workId` mit Events verknüpft ([models.ts:165-170](../../../../web/src/app/models/models.ts#L165-L170)); der [`DataService`](../../../../web/src/app/core/data.service.ts) bietet bereits `work(id)`, `composer(id)` sowie Event-Zugriffe.

Als fachliches Vorbild dient die **Spielstätten-Seite**: Übersicht als Kachel-Grid ([venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html)) und Detailseite mit Event-Liste ([venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts)).

Nicht betroffen: bestehende Seiten (Kalender, Ensembles, Spielstätten, Karte, Event-Detail) und das Datenmodell bleiben unverändert.

## Gewählte Lösung

Es werden zwei neue Seiten unter der Route `/works` (Übersicht) und `/works/:id` (Detail) analog zu den Venue-Seiten angelegt und ein Navigationspunkt **„Werke"** in die Hauptnavigation aufgenommen.

**Übersicht** (`/works`): Kachel-Grid im vorhandenen `.card-grid`-Stil. Es werden **nur Werke angezeigt, die in mindestens einem Event-Programm vorkommen** (Werke ohne Veranstaltung erscheinen nicht). Die Kacheln sind **nach Komponist und anschließend nach Werktitel** sortiert; eine Kachel stellt den Komponisten in den Vordergrund und zeigt den Werktitel sowie die Anzahl der Veranstaltungen. Ein Klick öffnet die Detailseite.

**Detail** (`/works/:id`): zeigt die verfügbaren Werk-Informationen (Titel, Komponist, Werkverzeichnis-Nummer(n), Entstehungszeit, Genre, Dauer, Fassung, Besetzung, Beschreibung – jeweils nur, wenn gepflegt) sowie eine chronologische **Liste der Veranstaltungen, in deren Programm das Werk vorkommt** (wiederverwendbare [`EventList`](../../../../web/src/app/shared/event-list.ts)).

Bewusst akzeptierte Kompromisse:
- Sortierung „nach Komponist" nutzt das vorhandene `Composer.name` als Sortierschlüssel (das Modell kennt keinen separaten Nachnamen); eine echte Nachnamen-Sortierung ist nicht Teil dieser Story.
- Der Komponist wird als Text angezeigt (es existiert noch keine Komponisten-Detailseite; vgl. Backlog US-024).
- Es wird kein neuer `DataService`-Zustand/Cache eingeführt, wenn eine einfache abgeleitete Berechnung genügt (analog zu `eventsForVenue`).

## Akzeptanzkriterien

1. **Route Übersicht:** Unter `/works` ist eine Werke-Übersicht erreichbar.
2. **Route Detail:** Unter `/works/:id` ist die Detailseite des jeweiligen Werks erreichbar; eine unbekannte ID führt zu einer sinnvollen „nicht gefunden"-Behandlung (analog zu bestehenden Detailseiten).
3. **Navigation:** Die Hauptnavigation enthält einen Punkt „Werke", der auf `/works` verweist und den Aktiv-Zustand korrekt anzeigt (`routerLinkActive`), konsistent zu den übrigen Navigationspunkten.
4. **Kachel-Übersicht:** Werke werden als Kacheln im bestehenden `.card-grid`-Stil dargestellt; jede Kachel ist als Ganzes anklickbar und verlinkt auf `/works/:id`.
5. **Umfang:** In der Übersicht erscheinen ausschließlich Werke, die in mindestens einem Event-Programm referenziert werden; jedes solche Werk erscheint genau einmal.
6. **Sortierung:** Die Kacheln sind alphabetisch nach Komponist und – bei gleichem Komponisten – nach Werktitel sortiert (deutsche Sortierung, `localeCompare('de')`).
7. **Kachel-Inhalt:** Eine Kachel zeigt den Komponisten (hervorgehoben), den Werktitel und die Anzahl zugehöriger Veranstaltungen (mit korrektem Singular/Plural, vgl. Venue-Kachel).
8. **Detail-Informationen:** Die Detailseite zeigt den Werktitel und den Komponisten sowie die weiteren gepflegten Angaben (Werkverzeichnis-Nummer(n), Entstehungszeit, Genre, Dauer, Fassung, Besetzung, Beschreibung). Nicht gepflegte Felder werden ausgelassen und erzeugen keine leeren Zeilen.
9. **Veranstaltungsliste:** Die Detailseite enthält eine chronologisch sortierte Liste der Veranstaltungen, in deren Programm das Werk vorkommt; jeder Eintrag verlinkt auf die zugehörige Event-Detailseite (wiederverwendete `EventList`).
10. **Konsistenz/Barrierefreiheit:** Layout, Kartenstil, Zurück-Link und Überschriftenstruktur orientieren sich an den Venue-Seiten; die Übersicht hat eine Seitenüberschrift (`app-page-header`), Kacheln und Links sind per Tastatur erreichbar.
11. **Unveränderte Bereiche:** Bestehende Seiten und das Datenmodell bleiben in Darstellung und Verhalten unverändert.

## Out of Scope

- Filter- oder Suchfunktion speziell für Werke (z. B. nach Genre/Komponist); die bestehende globale Suche/Filter wird nicht erweitert.
- Eine eigene Komponisten-Detailseite oder Verlinkung des Komponisten (separates Backlog-Thema, US-024).
- Anzeige von Werken, die in keinem Event vorkommen.
- Änderungen am `Work`-Datenmodell oder an den Werkdaten (`works.json`).
- Gruppierung/Register (z. B. Alphabet-Anker) in der Übersicht.

<!--
Umsetzungs-Tasks:
In separater Datei US-018-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
