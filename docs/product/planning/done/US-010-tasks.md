# US-010 – Umsetzungs-Tasks

Umsetzung von [US-010](./US-010-search.md): globale Suche in der Kopfzeile mit Fuzzy-Matching,
Mindestlänge von 3 Zeichen und Suchraum über alle relevanten Daten unter
[data/](../../../../data/).

## Bibliotheks-Entscheidung (verbindlich)

- Für die Fuzzy-Suche wird **Fuse.js** eingesetzt (`fuse.js` als Runtime-Dependency im
  Angular-Frontend).
- Begründung: gute Qualität bei Tippfehler-Toleranz, konfigurierbare Gewichtung, keine
  Backend-Abhängigkeit, passt zur statischen App-Architektur.

Betroffene Dateien:
- [web/package.json](../../../../web/package.json)
- [web/package-lock.json](../../../../web/package-lock.json)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts)
- [web/src/app/app.ts](../../../../web/src/app/app.ts)
- [web/src/app/app.html](../../../../web/src/app/app.html)
- [web/src/app/app.css](../../../../web/src/app/app.css)
- [docs/product/contracts/README.md](../../contracts/README.md)
- [docs/product/ears/README.md](../../ears/README.md)
- [docs/product/contracts/suche.feature](../../contracts/suche.feature) (neu)
- [docs/product/ears/suche.md](../../ears/suche.md) (neu)

---

## Task 1 – Such-UX und Ergebnisdarstellung festziehen (ohne Scope-Erweiterung)

- Suchfeld als globales Element in der Header-Leiste zwischen Brand und Navigation planen.
- Ergebnisdarstellung als kompakte Trefferliste direkt unter dem Suchfeld (keine eigene
  Suchergebnisseite, keine Facetten), damit die Story im vorhandenen Scope bleibt.
- Treffer als Links auf bestehende Detail-/Listenrouten modellieren
  (`/events/:id`, `/ensembles/:id`, `/venues/:id`).
- **Deckt ab:** AK 1, AK 2, AK 4.

## Task 2 – Fuse.js integrieren

- In [web/package.json](../../../../web/package.json) `fuse.js` zu `dependencies` ergänzen.
- Lockfile [web/package-lock.json](../../../../web/package-lock.json) aktualisieren.
- Keine weitere Suchbibliothek parallel einführen.
- **Deckt ab:** technische Grundlage für AK 5, AK 6.

## Task 3 – Suchdaten im DataService bereitstellen

- In [data.service.ts](../../../../web/src/app/core/data.service.ts) einen konsistenten
  Suchraum aus den geladenen Daten aufbauen (mindestens Events, Ensembles, Spielstätten;
  optional zusätzlich Werke/Komponist:innen, sofern mit bestehenden Routen sinnvoll verlinkbar).
- Einheitliches internes Suchdokument je Treffer definieren (z. B. `id`, `kind`, `title`,
  `subtitle`, `route`, `keywords`), damit UI und Suche nicht auf Rohobjekten arbeiten.
- Sicherstellen, dass bei nicht geladenen Daten kein fehlerhafter Suchlauf ausgelöst wird.
- **Deckt ab:** AK 5.

## Task 4 – Fuzzy-Suche mit Mindestlänge implementieren

- In [app.ts](../../../../web/src/app/app.ts) Suchzustand ergänzen (`query`, `results`,
  ggf. `isOpen`), inkl. Logik:
  - unter 3 Zeichen: keine Suche ausführen, keine Trefferliste anzeigen;
  - ab 3 Zeichen: Suche über Fuse.js ausführen und Trefferliste aktualisieren.
- Fuse.js-Konfiguration so wählen, dass Tippfehler wie `bethoven` → `Beethoven` gefunden
  werden (Schwelle/Felder dokumentieren).
- Ergebnisanzahl sinnvoll begrenzen (z. B. Top-N), um Header-UI performant und lesbar zu
  halten.
- **Deckt ab:** AK 3, AK 4, AK 6.

## Task 5 – Header-Markup für Suche ergänzen

- In [app.html](../../../../web/src/app/app.html) Suchfeld zwischen Brand und Navigation
  einbauen.
- Sichtbares Suchsymbol ergänzen (ohne zusätzliche Icon-Bibliothek; vorhandenes Projektmuster
  verwenden).
- Trefferliste semantisch und zugänglich ausgeben (Liste mit anklickbaren Treffern, sinnvolle
  Labels/ARIA-Attribute).
- Sicherstellen, dass die bestehende Navigation (inkl. Burger-Menü) funktional bleibt.
- **Deckt ab:** AK 1, AK 2, AK 4.

## Task 6 – Responsives Styling und Platznutzung

- In [app.css](../../../../web/src/app/app.css) Header-Layout so erweitern, dass das Suchfeld
  den verfügbaren Zwischenraum zwischen Brand und Navigation nutzt.
- Desktop- und Mobilverhalten definieren (inkl. Zusammenspiel mit Burger-Navigation bei
  `max-width: 720px`).
- Fokus-, Hover- und Active-Zustände für Suchfeld und Trefferliste nach bestehendem
  Designsystem umsetzen.
- **Deckt ab:** AK 2.

## Task 7 – Suchinteraktionen und Routing absichern

- Bei Klick auf einen Treffer zur Zielroute navigieren und Trefferliste schließen.
- Bei Route-Wechsel, ESC und Fokusverlust konsistentes Öffnen/Schließen der Trefferliste
  sicherstellen (analog zu bestehenden Header-Interaktionen).
- Sicherstellen, dass die Suche auf jeder Seite verfügbar bleibt (App-Root statt Page-Komponenten).
- **Deckt ab:** AK 1, AK 4.

## Task 8 – Produktspezifikation ergänzen (Contract + EARS)

- Neue Gherkin-Datei [suche.feature](../../contracts/suche.feature) mit Szenarien zu:
  - globale Verfügbarkeit,
  - Position im Header,
  - Mindestlänge 3 Zeichen,
  - Fuzzy-Treffer bei Tippfehlern.
- Neue EARS-Datei [suche.md](../../ears/suche.md) mit stabilen IDs für die Suchanforderungen.
- [contracts/README.md](../../contracts/README.md) und
  [ears/README.md](../../ears/README.md) um US-010 nicht mehr als „Backlog-only“, sondern als
  spezifizierten Umfang ergänzen.
- **Deckt ab:** AK 1–6.

## Task 9 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Suche auf Kalender-, Ensemble-, Spielstätten- und Detailseiten sichtbar (AK 1).
  - Suchfeld zwischen Brand und Navigation, mit Suchsymbol und adaptiver Breite (AK 2).
  - Bei 1–2 Zeichen keine Suche; ab 3 Zeichen automatische Suche (AK 3, AK 4).
  - Suchraum enthält relevante Datenobjekte aus [data/](../../../../data/) (AK 5).
  - Tippfehler-Beispiel (`bethoven`) liefert erwarteten Treffer (`Beethoven`) (AK 6).

## Definition of Done

- Akzeptanzkriterien 1–6 aus [US-010](./US-010-search.md) erfüllt.
- `fuse.js` ist die einzige eingesetzte Fuzzy-Suchbibliothek.
- Header-Navigation (inkl. Burger-Menü) bleibt funktional und regressionsfrei.
- Build erfolgreich; Suchverhalten manuell mit Positiv-/Negativfällen geprüft.
