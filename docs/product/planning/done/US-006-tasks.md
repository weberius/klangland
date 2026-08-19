# US-006 – Umsetzungs-Tasks

Umsetzung von [US-006](./US-006-navigation.md): Burger-Navigation auf mobil (≤ 720px) und kompakte Monatsauswahl (`<`/`>`) ohne Zeilenumbruch.

Betroffene Dateien:
- [web/src/app/app.ts](../../../../web/src/app/app.ts)
- [web/src/app/app.html](../../../../web/src/app/app.html)
- [web/src/app/app.css](../../../../web/src/app/app.css)
- [web/src/app/pages/calendar/calendar.html](../../../../web/src/app/pages/calendar/calendar.html)
- [web/src/app/pages/calendar/calendar.css](../../../../web/src/app/pages/calendar/calendar.css)

---

## Task 1 – Menüzustand in der App-Komponente (app.ts)

- In [app.ts](../../../../web/src/app/app.ts) ein `signal<boolean>` (z. B. `menuOpen`) einführen.
- Methoden ergänzen: `toggleMenu()`, `closeMenu()`.
- **Auto-Schließen bei Navigation (AK 4):** Auf `Router`-Events reagieren (z. B. `NavigationEnd` abonnieren oder in einem `effect` auf die aktuelle URL) und `menuOpen` auf `false` setzen. Alternativ `closeMenu()` an den Klick der Nav-Links binden.
- **ESC (AK 4):** Über einen `@HostListener('document:keydown.escape')` oder `(keydown.escape)` das Menü schließen.
- **Fokus-Rückgabe (offener Punkt):** Beim Schließen den Fokus auf den Burger-Button zurücksetzen (ViewChild/Signal-Referenz auf den Button).

## Task 2 – Burger-Markup und Menü (app.html)

- In [app.html:9-13](../../../../web/src/app/app.html#L9-L13) einen Burger-`<button>` vor/neben der `<nav>` ergänzen:
  - `type="button"`, `(click)="toggleMenu()"`,
  - `[attr.aria-expanded]="menuOpen()"`, `aria-controls="main-nav"`,
  - `[attr.aria-label]="menuOpen() ? 'Menü schließen' : 'Menü öffnen'"`,
  - Icon ohne Icon-Bibliothek (drei CSS-Balken oder Unicode `☰`, dekorativ `aria-hidden`).
- Der `<nav class="main-nav">` eine `id="main-nav"` geben und den Offen-Zustand anbinden (z. B. `[class.open]="menuOpen()"`).
- An den drei Links `(click)="closeMenu()"` ergänzen (unterstützt AK 4), `routerLinkActive="active"` bleibt erhalten (AK 5).
- **Deckt ab:** AK 1, AK 3, AK 5, AK 6.

## Task 3 – Responsives Styling der Navigation (app.css)

- **Desktop (> 720px):** Burger-Button ausblenden (`display: none`), `.main-nav` unverändert horizontal ([app.css:48-67](../../../../web/src/app/app.css#L48-L67)). → AK 2
- **Mobil (≤ 720px)** via `@media (max-width: 720px)` (gleicher Breakpoint wie Grid/Agenda):
  - Burger-Button sichtbar.
  - `.main-nav` standardmäßig ausgeblendet und nur bei `.open` als aufgeklapptes Menü anzeigen (z. B. vertikale Liste unter dem Header).
  - Menü über dem Inhalt darstellen: passende `z-index`-Ebene relativ zum sticky `.site-header` ([app.css:21-27](../../../../web/src/app/app.css#L21-L27)), damit nichts abgeschnitten wird. → AK 7
- Sichtbarer Fokus-Stil (`:focus-visible`) für Burger-Button und Menülinks. → AK 6
- **Deckt ab:** AK 1, AK 2, AK 7.

## Task 4 – Monatsauswahl auf `<`/`>` reduzieren (calendar.html)

- In [calendar.html:10-12](../../../../web/src/app/pages/calendar/calendar.html#L10-L12) die sichtbaren Beschriftungen auf `<` bzw. `>` kürzen (Texte „Vorheriger"/„Nächster" entfernen).
- Die `aria-label` „Vorheriger Monat" / „Nächster Monat" **beibehalten** (AK 10); das sichtbare Zeichen dekorativ halten (`aria-hidden` am Zeichen, falls als eigenes Span).
- `prevLink()`/`nextLink()` und der „Heute"-Button bleiben unverändert (AK 11).
- **Deckt ab:** AK 8, AK 10, AK 11.

## Task 5 – Monatszeile ohne Umbruch (calendar.css)

- `.month-nav` ([calendar.css:1-17](../../../../web/src/app/pages/calendar/calendar.css#L1-L17)) so anpassen, dass die Zeile nicht mehr umbricht (`flex-wrap: nowrap` bzw. schmalere Buttons), und die `min-width: 12rem` des `.month-title` prüfen/reduzieren, damit es auch auf schmalen Geräten in eine Zeile passt.
- Sicherstellen, dass die `<`/`>`-Buttons kompakt sind (gleiche Höhe/Ausrichtung wie bisher).
- Position des „Heute"-Buttons prüfen (aktuell `margin-left: auto` bzw. auf Mobil `margin-left: 0`, [calendar.css:15-17](../../../../web/src/app/pages/calendar/calendar.css#L15-L17) / [calendar.css:215-217](../../../../web/src/app/pages/calendar/calendar.css#L215-L217)).
- **Deckt ab:** AK 9, AK 11.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` (bzw. `ng serve`) und im Browser prüfen:
  - **Desktop (> 720px):** Navigation horizontal, kein Burger (AK 2); Monatszeile einzeilig mit `<`/`>` und „Heute" (AK 8, AK 9, AK 11).
  - **Mobil (≤ 720px, Fenster verschmälern):** Burger sichtbar; Öffnen/Schließen per Klick (AK 1, AK 3); Menü liegt über dem Inhalt (AK 7).
  - Auswahl eines Punkts schließt das Menü; `ESC` schließt das Menü (AK 4).
  - Aktiver Menüpunkt bleibt markiert (AK 5).
  - Tastatur: Burger per Tab erreichbar, mit Enter/Space bedienbar, Fokus sichtbar, Fokus-Rückgabe beim Schließen (AK 6).
  - Monatszeile bricht auf sehr schmalen Geräten nicht um (AK 9).
- Kurzer Screenreader-/A11y-Check des Burger-Buttons (`aria-expanded` wechselt, Label „Menü öffnen/schließen").

## Definition of Done

- Akzeptanzkriterien 1–11 der User Story erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen an Seiteninhalten oder an der Monatsberechnungslogik.
- Story-Datei nach Abschluss von `inprogress/` nach `done/` verschieben (sofern dieses Verzeichnis genutzt wird).
