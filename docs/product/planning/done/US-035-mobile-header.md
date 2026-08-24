# User Story 035 - Mobile Kopfzeile: quadratischer Burger-Button, platzsparende Suche, zentriertes Filter-Popover und Klangland-Icon

## User Story

**Als** Nutzer:in der Klangland-Webanwendung auf einem Smartphone,
**möchte ich** eine Kopfzeile, in der Suche, Filter-Anzeige und Navigations-Button auch bei
aktiven Filterchips genügend Platz haben und klar erkennbar sind,
**damit** ich die Navigation und die Suche auch mit schmalem Bildschirm zuverlässig und
komfortabel bedienen kann.

## Kontext / Problem

Die Kopfzeile ([app.html](../../../../web/src/app/app.html),
[app.css](../../../../web/src/app/app.css)) enthält von links nach rechts: das Marken-Symbol
(aktuell ein ♪-Notenzeichen, `.brand-mark`), das globale Suchfeld (`.global-search`), den
Filter-Button ([app-filter-button](../../../../web/src/app/shared/filter-button/)) und den
Burger-Button für die Hauptnavigation (`.nav-toggle`). In der mobilen Ansicht treten vier
zusammenhängende Probleme auf:

1. **Burger-Button verzerrt sich:** `.nav-toggle` ist zwar mit fester Breite/Höhe (`2.5rem` ×
   `2.5rem`) als Quadrat definiert
   ([app.css:191-203](../../../../web/src/app/app.css#L191-L203)), hat aber kein
   `flex-shrink: 0` innerhalb des Flex-Containers `.header-inner`. Ist ein Filter aktiv, zeigt
   der Filter-Button zusätzlich einen Zähler-Chip (`.filter-count`,
   [filter-button.html:14](../../../../web/src/app/shared/filter-button/filter-button.html#L14)),
   der zusätzlichen Platz beansprucht. Auf schmalen Viewports wird dadurch der Burger-Button
   in der Breite zusammengedrückt und erscheint hochkant-rechteckig statt quadratisch, was ihn
   schwerer bedienbar macht.
2. **Suchfeld beansprucht dauerhaft Platz:** Das Suchfeld
   ([app.html:9-25](../../../../web/src/app/app.html#L9-L25)) und der Marken-Schriftzug
   „Klangland" (`.brand-text`) sind gleichzeitig sichtbar und konkurrieren mit Filter-Button
   und Burger-Button um den knappen Platz in der Kopfzeile.
3. **Filter-Popover ist an den Button gebunden:** Das Popover
   ([filter-button.css:58-69](../../../../web/src/app/shared/filter-button/filter-button.css#L58-L69))
   ist `position: absolute; right: 0` relativ zum Filter-Button positioniert und orientiert
   sich an dessen Breite/Position statt an der Bildschirmmitte, was es auf kleinen
   Bildschirmen ungünstig platziert.
4. **Marken-Symbol ist ein Platzhalter:** Das ♪-Zeichen (`.brand-mark`,
   [app.html:6](../../../../web/src/app/app.html#L6)) ist nur eine Unicode-Notiz und
   entspricht nicht dem eigentlichen Klangland-Icon, das bereits im Projekt hinterlegt ist
   (z. B. [web/public/favicon-96x96.png](../../../../web/public/favicon-96x96.png), außerdem
   `apple-touch-icon.png` und `web-app-manifest-192x192.png`/`-512x512.png` im selben
   Verzeichnis).

Betroffen sind ausschließlich die globale Kopfzeile (`app.html`/`app.css`) und der
Filter-Button (`filter-button.html`/`.css`). Die Seiteninhalte, `page-header`-Komponente
(Seitentitel/Beschreibung/Filter-Chips je Einzelseite) und die Hauptnavigation selbst sind
nicht betroffen.

## Gewählte Lösung

- Der Burger-Button erhält `flex-shrink: 0` (bzw. `flex: none`), damit er unter allen
  Platzverhältnissen quadratisch bleibt.
- Das Suchfeld erhält einen erweiterten Fokuszustand: Sobald es fokussiert ist, wird es
  breiter dargestellt und überdeckt dabei den Marken-Schriftzug „Klangland" (das Marken-Symbol
  bleibt sichtbar); dadurch steht rechts mehr Platz für Filter-Anzeige und Burger-Button zur
  Verfügung. Beim Verlassen des Fokus kehrt das Suchfeld in seine ursprüngliche Breite zurück
  und der Schriftzug wird wieder sichtbar.
- Das Filter-Popover wird von der button-relativen Positionierung gelöst und stattdessen
  horizontal auf dem Bildschirm zentriert dargestellt (z. B. über `position: fixed` mit
  zentrierter Ausrichtung statt `position: absolute; right: 0`).
- Das ♪-Platzhaltersymbol wird durch das bestehende Klangland-Icon aus `web/public` ersetzt,
  in derselben Größe wie der Burger-Button dargestellt.

## Akzeptanzkriterien

1. **Burger-Button bleibt quadratisch:** Der Navigations-Button (Burger-Menü) wird in der
   mobilen Ansicht unabhängig davon, ob ein oder mehrere Filter aktiv sind (Zähler-Chip
   sichtbar oder nicht), stets quadratisch dargestellt und bleibt bequem antippbar.
2. **Suchfeld erweitert sich bei Fokus:** Wird das Suchfeld fokussiert (Tap/Klick), vergrößert
   es sich sichtbar und überdeckt dabei den Schriftzug „Klangland"; das Marken-Symbol bleibt
   erkennbar.
3. **Suchfeld kehrt zur Ausgangsgröße zurück:** Verliert das Suchfeld den Fokus (z. B. durch
   Tippen außerhalb) und enthält keinen Suchtext, kehrt es zur ursprünglichen, schmaleren
   Breite zurück und der Schriftzug „Klangland" ist wieder sichtbar.
4. **Ausreichend Platz für Filter und Burger-Menü:** Bei fokussiertem, erweitertem Suchfeld
   bleibt rechts genug Platz, damit Filter-Anzeige (inkl. Zähler) und Burger-Button nicht an
   den äußersten Rand gedrängt werden und gut bedienbar bleiben.
5. **Filter-Popover zentriert:** Ein Klick auf den Filter-Button öffnet das Popover
   horizontal zentriert auf dem Bildschirm (nicht mehr am rechten Rand des Buttons
   ausgerichtet), sowohl in der mobilen als auch in der Desktop-Ansicht.
6. **Klangland-Icon statt Notensymbol:** Das ♪-Platzhaltersymbol links in der Kopfzeile wird
   durch das bestehende Klangland-Icon aus `web/public` ersetzt.
7. **Icon-Größe wie Burger-Button:** Das neue Marken-Icon wird in derselben Größe wie der
   Burger-Button (Breite und Höhe) dargestellt.
8. **Barrierefreiheit unverändert:** Der Link zur Startseite (`aria-label="Klangland
   Startseite"`) bleibt erhalten und funktionsfähig; das neue Icon erhält ein passendes
   `alt`-Attribut bzw. bleibt (wie zuvor das Notensymbol) dekorativ mit vorhandenem
   `aria-label` am umschließenden Link.
9. **Desktop-Ansicht unverändert:** Auf breiten Viewports (Desktop) verändert sich das
   Erscheinungsbild von Suchfeld, Filter-Button und Burger-Button nicht spürbar negativ; die
   Änderungen zielen primär auf die mobile Darstellung, dürfen die Desktop-Darstellung aber
   nicht verschlechtern.

## Out of Scope

- Änderungen an der Hauptnavigation selbst (Menüpunkte, Reihenfolge, Verhalten beim Öffnen).
- Änderungen an der Filterlogik (`FilterService`/`FavoritesService`) oder den im Popover
  angebotenen Filterkriterien.
- Änderungen an der Such-Logik/den Suchergebnissen selbst (nur Breite/Sichtbarkeit des
  Eingabefelds).
- Einführung eines neuen App-Icons/Favicons (es wird ausschließlich ein bereits vorhandenes
  Icon aus `web/public` wiederverwendet).
