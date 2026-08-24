# US-035 – Umsetzungs-Tasks

Umsetzung von [US-035](./US-035-mobile-header.md): Vier zusammenhängende Korrekturen an der
globalen Kopfzeile ([app.html](../../../../web/src/app/app.html) /
[app.css](../../../../web/src/app/app.css)) und am Filter-Popover
([filter-button](../../../../web/src/app/shared/filter-button/)), damit die mobile Ansicht
bei aktiven Filtern genug Platz für Burger-Button und Filter-Anzeige lässt.

## Architektur-Entscheidung (verbindlich)

- **Burger-Button (AK 1):** `.nav-toggle` erhält `flex-shrink: 0` (bzw. `flex: none`), damit
  die bereits vorhandene feste Größe (`2.5rem` × `2.5rem`,
  [app.css:191-203](../../../../web/src/app/app.css#L191-L203)) innerhalb von
  `.header-inner` nicht durch den Zähler-Chip des Filter-Buttons zusammengedrückt wird.
- **Suchfeld-Erweiterung (AK 2–4):** Neues Signal `searchFocused` in
  [app.ts](../../../../web/src/app/app.ts), gesetzt über `(focus)`/`(blur)` am Sucheingabefeld.
  Abgeleitetes Computed `searchExpanded = computed(() => searchFocused() ||
  searchQuery().trim().length > 0)` (nutzt das bereits vorhandene `searchQuery`-Signal) –
  das Suchfeld bleibt also auch bei vorhandenem Text ohne Fokus erweitert (AK 3 verlangt
  „kehrt zurück … und enthält keinen Suchtext"), und schrumpft erst, wenn **weder** Fokus
  **noch** Text vorhanden sind.
  `[class.search-expanded]="searchExpanded()"` auf `.global-search` binden.
  **Konkretisierung von „überdeckt":** Statt echter Überlappung per Absolut-Positionierung
  (fehleranfällig bei unterschiedlichen Viewport-Breiten) wird `.brand-text` bei
  `.search-expanded` per CSS ausgeblendet (`display: none` bzw. `visibility: hidden` +
  Breite 0) und `.global-search` wächst über Flexbox (`flex-grow`) in den freiwerdenden
  Platz. Das Marken-Symbol (Icon, siehe AK 6/7) bleibt in jedem Zustand sichtbar. Ergebnis
  für Nutzer:innen ist optisch identisch zur geforderten Überdeckung: Der Schriftzug
  verschwindet, das Suchfeld nimmt sichtbar mehr Platz ein.
- **Filter-Popover zentrieren (AK 5):** `.filter-popover`
  ([filter-button.css:58-69](../../../../web/src/app/shared/filter-button/filter-button.css#L58-L69))
  wechselt von `position: absolute; right: 0` (relativ zum Button) zu `position: fixed; left:
  50%; transform: translateX(-50%)` (horizontal zentriert auf dem Viewport, funktioniert
  unabhängig von der Position des Buttons in Mobile- und Desktop-Ansicht). Die vertikale
  Position (`top`) wird weiterhin knapp unterhalb der Kopfzeile benötigt; da `position: fixed`
  nicht mehr relativ zu `:host` berechnet werden kann, wird sie in
  [filter-button.ts](../../../../web/src/app/shared/filter-button/filter-button.ts) beim
  Öffnen dynamisch aus `toggleButton().nativeElement.getBoundingClientRect().bottom` ermittelt
  und per `[style.top.px]` gebunden – robust gegenüber Änderungen der Kopfzeilenhöhe (z. B.
  durch Task 1/2 dieser Story).
- **Marken-Icon (AK 6–8):** `.brand-mark`
  ([app.html:6](../../../../web/src/app/app.html#L6)) wird von einem `<span>♪</span>` zu
  einem `<img>` mit `src="favicon-96x96.png"` (vorhandene Datei in
  [web/public](../../../../web/public/favicon-96x96.png)) geändert. Größe per CSS auf die
  Maße des Burger-Buttons (`2.5rem` × `2.5rem`) festgelegt. `alt=""` und `aria-hidden="true"`
  (das Icon bleibt dekorativ, da der umschließende Link bereits `aria-label="Klangland
  Startseite"` trägt – identisch zum bisherigen Verhalten des ♪-Zeichens).

Betroffene Dateien:

- [web/src/app/app.html](../../../../web/src/app/app.html)
- [web/src/app/app.ts](../../../../web/src/app/app.ts)
- [web/src/app/app.css](../../../../web/src/app/app.css)
- [web/src/app/shared/filter-button/filter-button.ts](../../../../web/src/app/shared/filter-button/filter-button.ts)
- [web/src/app/shared/filter-button/filter-button.html](../../../../web/src/app/shared/filter-button/filter-button.html)
- [web/src/app/shared/filter-button/filter-button.css](../../../../web/src/app/shared/filter-button/filter-button.css)

---

## Task 1 – Burger-Button quadratisch fixieren

- In [app.css](../../../../web/src/app/app.css) bei `.nav-toggle`
  ([Zeile 191](../../../../web/src/app/app.css#L191)) `flex-shrink: 0;` ergänzen.
- **Deckt ab:** AK 1.

## Task 2 – Suchfeld-Erweiterung bei Fokus

- In [app.ts](../../../../web/src/app/app.ts) Signal `searchFocused = signal(false)`
  ergänzen; `(focus)`-Handler setzt es auf `true`, `(blur)`-Handler auf `false`.
- Computed `searchExpanded = computed(() => this.searchFocused() ||
  this.searchQuery().trim().length > 0)` ergänzen.
- In [app.html](../../../../web/src/app/app.html) am `#searchInput`
  ([Zeile 11-25](../../../../web/src/app/app.html#L11-L25)) `(focus)`/`(blur)`-Bindings
  ergänzen (bestehendes `(focus)="onSearchFocus()"` bleibt für die Ergebnis-Anzeige
  erhalten, zusätzlich das neue Fokus-Tracking); `[class.search-expanded]="searchExpanded()"`
  auf `.global-search` ([Zeile 9](../../../../web/src/app/app.html#L9)) binden.
- In [app.css](../../../../web/src/app/app.css) `.global-search.search-expanded` ergänzen
  (z. B. `flex-grow: 1; max-width: none;`) und `.brand-text` bei aktivem
  `.search-expanded`-Zustand des Geschwister-Elements ausblenden (CSS-Selektor über den
  gemeinsamen `.header-inner`-Elternknoten, z. B. `.header-inner:has(.search-expanded)
  .brand-text`, mit einfachem Fallback über eine zusätzliche Klasse am `.header-inner`, falls
  `:has()`-Unterstützung im Zielbrowser-Set fraglich ist).
- **Deckt ab:** AK 2, AK 3, AK 4.

## Task 3 – Filter-Popover horizontal zentrieren

- In [filter-button.ts](../../../../web/src/app/shared/filter-button/filter-button.ts)
  `popoverTop = signal<number>(0)` ergänzen; in `toggle()`
  ([Zeile 62](../../../../web/src/app/shared/filter-button/filter-button.ts#L62)) beim
  Öffnen `popoverTop.set(toggleButton()!.nativeElement.getBoundingClientRect().bottom + 8)`
  setzen.
- In [filter-button.html](../../../../web/src/app/shared/filter-button/filter-button.html)
  `[style.top.px]="popoverTop()"` am Popover-Container ergänzen.
- In [filter-button.css](../../../../web/src/app/shared/filter-button/filter-button.css)
  `.filter-popover` ([Zeile 58-69](../../../../web/src/app/shared/filter-button/filter-button.css#L58-L69))
  von `position: absolute; top: calc(100% + 0.4rem); right: 0;` auf `position: fixed; left:
  50%; transform: translateX(-50%);` umstellen; `width: min(22rem, calc(100vw - 2rem))`
  beibehalten.
- **Deckt ab:** AK 5.

## Task 4 – Marken-Icon ersetzen

- In [app.html](../../../../web/src/app/app.html) `<span class="brand-mark"
  aria-hidden="true">♪</span>` ([Zeile 6](../../../../web/src/app/app.html#L6)) durch
  `<img class="brand-mark" src="favicon-96x96.png" alt="" aria-hidden="true">` ersetzen.
- In [app.css](../../../../web/src/app/app.css) `.brand-mark`
  ([Zeile 44-47](../../../../web/src/app/app.css#L44-L47)) auf `width: 2.5rem; height:
  2.5rem; object-fit: contain;` umstellen (bisherige Font-Size-Regel entfernen).
- **Deckt ab:** AK 6, AK 7, AK 8.

## Task 5 – Desktop-Regression prüfen

- Auf breiten Viewports (> 720 px) sichten, dass Suchfeld-Erweiterung, zentriertes Popover
  und neues Icon keine negativen Auswirkungen auf die bisherige Desktop-Darstellung haben
  (insbesondere: Popover war vorher rechtsbündig unter dem Button, jetzt bildschirmzentriert
  – das ist laut AK 5 explizit gewollt, nicht nur mobil).
- **Deckt ab:** AK 9.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser (Mobile-Emulation, z. B. 360–400 px Breite) prüfen:
  - Mit aktivem Filter (Zähler-Chip sichtbar) bleibt der Burger-Button quadratisch (AK 1).
  - Klick/Tap ins Suchfeld: Feld wird breiter, „Klangland"-Schriftzug verschwindet, Icon
    bleibt sichtbar (AK 2).
  - Fokus verlassen ohne eingegebenen Text: Suchfeld schrumpft zurück, Schriftzug erscheint
    wieder (AK 3). Fokus verlassen **mit** Text: Suchfeld bleibt erweitert.
  - Bei erweitertem Suchfeld bleiben Filter-Anzeige und Burger-Button gut antippbar, nicht am
    Rand gequetscht (AK 4).
  - Filter-Button antippen: Popover erscheint horizontal zentriert auf dem Bildschirm, auch
    bei aktivem Filter-Zähler (AK 5).
  - Kopfzeile zeigt links das Klangland-Icon (kein ♪-Zeichen mehr) in Burger-Button-Größe
    (AK 6, AK 7); Link zur Startseite funktioniert weiterhin per Tastatur/Screenreader
    (AK 8).
  - Test auf Desktop-Breite (> 720 px): keine Regression (AK 9).

## Definition of Done

- Akzeptanzkriterien 1–9 aus [US-035](./US-035-mobile-header.md) erfüllt.
- Keine Änderung an Filterlogik, Suchlogik oder Hauptnavigation (nur Layout/Darstellung).
- Build erfolgreich; Verhalten manuell in Mobile- und Desktop-Breite geprüft.
