# User Story 006 - Navigation

## User Story

**Als** Besucher:in, der:die die App auf einem mobilen Gerät nutzt,
**möchte ich** eine kompakte, aufgeräumte Navigation und eine platzsparende Monatsauswahl,
**damit** ich auch auf schmalen Bildschirmen ohne umbrechende oder überladene Bedienleisten zwischen den Seiten und Monaten wechseln kann.

## Kontext / Problem

Die Hauptnavigation ([app.html:9-13](../../../../web/src/app/app.html#L9-L13)) zeigt die drei Ziele „Kalender", „Ensembles" und „Spielstätten" als horizontale Linkleiste – auf schmalen Bildschirmen umbricht bzw. verbraucht sie viel Platz. Eine kompakte Darstellung (Burger) fehlt.

Die Monatsnavigation im Kalender ([calendar.html:9-14](../../../../web/src/app/pages/calendar/calendar.html#L9-L14)) verwendet für das Blättern die langen Beschriftungen „‹ Vorheriger" und „Nächster ›". Zusammen mit dem Monatstitel und dem „Heute"-Button führt das dazu, dass die Zeile mit dem Monatstitel umbricht.

Zur Einordnung: Die App schaltet bei **max-width 720px** von der Tabellen- auf die Agenda-Ansicht um ([calendar.css:208](../../../../web/src/app/pages/calendar/calendar.css#L208)). Dieser Breakpoint definiert „mobil" und sollte auch für die Burger-Navigation gelten. Die App-Komponente ist aktuell zustandslos ([app.ts](../../../../web/src/app/app.ts)); für das Öffnen/Schließen des Menüs wird ein Zustand (Signal) benötigt.

## Gewählte Lösung

- **Burger-Navigation auf mobil:** Unterhalb des Breakpoints (≤ 720px) werden die drei Navigationspunkte hinter einem Burger-Icon zusammengefasst und per Klick auf-/zugeklappt. Oberhalb (> 720px) bleibt die horizontale Navigation unverändert.
- **Kompakte Monatsauswahl:** Das Blättern wird auf die Zeichen `<` und `>` reduziert (die langen Texte „Vorheriger"/„Nächster" entfallen). Dadurch passt die Monatszeile in eine Zeile und bricht nicht mehr um. Die beschreibenden `aria-label` bleiben erhalten.

## Akzeptanzkriterien

### Burger-Navigation

1. **Mobil (≤ 720px):** Die drei Navigationspunkte „Kalender", „Ensembles", „Spielstätten" sind hinter einem Burger-Icon zusammengefasst.
2. **Desktop (> 720px):** Die Navigation bleibt horizontal sichtbar; es wird kein Burger-Icon angezeigt.
3. **Öffnen/Schließen:** Ein Klick/Tap auf das Burger-Icon öffnet das Menü, ein weiterer schließt es.
4. **Auto-Schließen:** Das Menü schließt sich beim Auswählen eines Navigationspunkts (Navigation) sowie bei Drücken von `ESC`.
5. **Aktiver Zustand:** Der aktuell aktive Menüpunkt bleibt hervorgehoben (`routerLinkActive`).
6. **Barrierefreiheit:** Das Burger-Element ist ein `<button>` mit `aria-expanded`, `aria-controls` und sprechendem Label (z. B. „Menü öffnen"/„Menü schließen"), ist per Tastatur bedienbar (Enter/Space) und hat einen sichtbaren Fokus.
7. **Überlagerung:** Das aufgeklappte Menü wird im sticky Header korrekt über dem Seiteninhalt dargestellt (kein Abschneiden, korrekte `z-index`-Ebene).

### Monatsnavigation

8. **Kompakte Zeichen:** Vor-/Zurück-Blättern wird auf `<` und `>` reduziert; die Texte „Vorheriger"/„Nächster" entfallen.
9. **Kein Umbruch:** Die Zeile mit dem Monatstitel bricht nicht mehr um – weder auf Desktop noch auf Mobil.
10. **Beschriftung erhalten:** Die Blätter-Buttons behalten ihre beschreibenden `aria-label` („Vorheriger Monat"/„Nächster Monat"), obwohl sichtbar nur `<`/`>` erscheint.
11. **„Heute" bleibt:** Der „Heute"-Button bleibt vorhanden und erreichbar.

## Zu berücksichtigen (offene Punkte)

- **Einheitlicher Breakpoint:** Für den Burger denselben Breakpoint (720px) wie für die Grid-/Agenda-Umschaltung verwenden, damit „mobil" konsistent definiert ist.
- **Zustand & Auto-Schließen:** [app.ts](../../../../web/src/app/app.ts) benötigt ein Signal für den Menüzustand. Nach der Navigation muss das Menü zuverlässig schließen (z. B. Klick-Handler auf die Links oder Reaktion auf Router-Events); zusätzlich `ESC`.
- **Fokus-Rückgabe:** Beim Schließen des Menüs (per ESC/Auswahl) sollte der Fokus sinnvoll gesetzt werden (z. B. zurück auf den Burger-Button).
- **Icon-Umsetzung:** Burger-Icon ohne zusätzliche Icon-Bibliothek (CSS-Balken oder Unicode-Symbol) – im Projekt sind keine Icon-Pakete vorhanden.
- **Glyphen `<`/`>`:** Als visuelles Zeichen genügt ein klares Chevron/Kleiner-/Größer-Zeichen; entscheidend ist das erhaltene `aria-label`. Aktuell werden `‹`/`›` genutzt – Konsistenz mit dem gewünschten `<`/`>` festlegen.
- **Kein-Umbruch erzwingen:** Ggf. `flex-wrap` der Monatszeile ([calendar.css:1-17](../../../../web/src/app/pages/calendar/calendar.css#L1-L17)) und die `min-width` des Monatstitels prüfen/anpassen, damit AK 9 auf sehr schmalen Geräten hält.
- **Erweiterbarkeit:** Künftige Navigationsziele (z. B. Suche/Filter aus dem Backlog) sollen sich in dieselbe Navigationsstruktur einfügen lassen – deren Umsetzung ist aber nicht Teil dieser Story.

## Out of Scope

- Integration von Suche/Filter oder weiteren Navigationszielen.
- Änderungen an den Seiteninhalten selbst (nur Navigation/Monatsauswahl).
- Änderungen an der Logik der Monatsberechnung (`prevLink`/`nextLink` bleiben unverändert; nur die Darstellung ändert sich).
