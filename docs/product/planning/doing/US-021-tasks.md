# US-021 – Umsetzungs-Tasks

Umsetzung von [US-021](./US-021-favoriten.md): Events als Favoriten markieren (Stern in der
Detailansicht), in der Übersicht kennzeichnen, im US-020-Popover „Nur Favoriten" filtern
(UND-kombiniert mit Ort/Profil) und die Auswahl per Link auf Abruf teilen. Favoriten sind
flüchtig (nur im Speicher, Wiederherstellung ausschließlich über den geteilten Link).

## Architektur-Entscheidung (verbindlich)

- Neuer root-bereitgestellter `FavoritesService` hält (a) das Set favorisierter Event-IDs und
  (b) das Flag „Nur Favoriten". Analog zum [FilterService](../../../../web/src/app/core/filter.service.ts)
  ohne `localStorage`/`sessionStorage`.
- **Wiederherstellung nur über die URL:** Beim App-Start werden Favoriten aus einem
  Query-Parameter gelesen; die App schreibt die Auswahl **nicht** laufend in die URL. Ein
  „Teilen"-Aktion erzeugt den Link auf Abruf.
- Der Favoriten-Filter wird in die bestehende Event-Ermittlung eingehängt: die gefilterten
  Events in [calendar.ts:48](../../../../web/src/app/pages/calendar/calendar.ts#L48) werden nach
  `eventsForFilter(...)` zusätzlich auf Favoriten reduziert (Favoriten sind eventspezifisch;
  [ensemble-list](../../../../web/src/app/pages/ensemble-list/) und
  [venue-list](../../../../web/src/app/pages/venue-list/) bleiben unberührt).
- „Alle zurücksetzen" im Popover ruft neben `FilterService.clear()` auch die Rücksetzung des
  `FavoritesService` (Markierungen + Filter-Flag) auf.
- Kein zusätzliches State-Management- oder UI-Framework; nur Angular Signals wie im Bestand.

Betroffene Dateien:
- [web/src/app/core/favorites.service.ts](../../../../web/src/app/core/) (neu)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) / [.html](../../../../web/src/app/pages/event-detail/event-detail.html) / [.css](../../../../web/src/app/pages/event-detail/event-detail.css)
- [web/src/app/pages/calendar/calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts) / [.html](../../../../web/src/app/pages/calendar/calendar.html) / [.css](../../../../web/src/app/pages/calendar/calendar.css)
- [web/src/app/shared/filter-button/](../../../../web/src/app/shared/filter-button/) (Popover erweitern)
- [web/src/app/app.ts](../../../../web/src/app/app.ts) (Favoriten aus Query-Parametern initialisieren)
- [docs/product/contracts/favoriten.feature](../../contracts/) / [ears/favoriten.md](../../ears/) (neu)
- [docs/product/contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md)

---

## Task 1 – FavoritesService

- Neue Datei `web/src/app/core/favorites.service.ts` mit `@Injectable({ providedIn: 'root' })`.
- Zustand:
  - `_ids = signal<ReadonlySet<string>>(new Set())` (favorisierte Event-IDs) mit
    `isFavorite(id)`, `toggle(id)`, readonly `ids` und `hasFavorites` (computed).
  - `_onlyFavorites = signal(false)` (Filter-Flag) mit `onlyFavorites` (readonly),
    `setOnlyFavorites(value)` bzw. `toggleOnlyFavorites()`.
- `setFromIds(ids: string[])` für die Initialisierung aus der URL; `reset()` leert IDs **und**
  Flag.
- **Deckt ab:** AK 1, AK 4, AK 5, AK 12.

## Task 2 – Favoriten in der Event-Detailansicht markieren

- In [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) den
  `FavoritesService` injizieren; `isFavorite`/`toggle` für den aktuellen Event anbinden.
- In [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html) im
  `event-head` einen Stern-Toggle-Button ergänzen (`aria-pressed`, sprechendes `aria-label`,
  z. B. „Zu Favoriten hinzufügen" / „Aus Favoriten entfernen").
- Stern-Styling (aktiv/inaktiv) in [event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css)
  ohne zusätzliche Icon-Bibliothek (vorhandenes Projektmuster / Unicode-Stern).
- **Deckt ab:** AK 1, AK 2, AK 13.

## Task 3 – Favoriten-Markierung in der Kalender-Übersicht

- In [calendar.html](../../../../web/src/app/pages/calendar/calendar.html) favorisierte Events
  kennzeichnen: Stern-Marker oben rechts auf dem `event-chip` (Monatsraster, ab
  [Zeile 42](../../../../web/src/app/pages/calendar/calendar.html#L42)) und im `agenda-event`
  ([Zeile 92](../../../../web/src/app/pages/calendar/calendar.html#L92)).
- In [calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts) `FavoritesService`
  injizieren und `isFavorite(e.id)` bereitstellen.
- Positionierung/Styling des Markers in [calendar.css](../../../../web/src/app/pages/calendar/calendar.css).
- **Deckt ab:** AK 3.

## Task 4 – Favoriten-Filter im Popover und kombinierte Filterung

- Im [filter-button](../../../../web/src/app/shared/filter-button/)-Popover eine Umschaltung
  „Nur Favoriten" ergänzen (`aria-pressed`), gebunden an
  `FavoritesService.onlyFavorites`/`toggleOnlyFavorites()`.
- „Alle zurücksetzen" so erweitern, dass es zusätzlich `FavoritesService.reset()` aufruft
  (Markierungen + Filter-Flag); Aktiv-Zustand/Zähler des Buttons entsprechend berücksichtigen.
- In [calendar.ts:48](../../../../web/src/app/pages/calendar/calendar.ts#L48) das Ergebnis von
  `eventsForFilter(selectedCityIds(), selectedProfileIds())` bei aktivem `onlyFavorites`
  zusätzlich auf `isFavorite(e.id)` einschränken (UND-Kombination; Ort/Profil bleiben ODER
  innerhalb ihrer Kategorie).
- Ensemble-/Spielstätten-Liste bleiben vom Favoriten-Filter unberührt.
- **Deckt ab:** AK 5, AK 6, AK 7, AK 8.

## Task 5 – Teilen per Link (Query-Parameter)

- Query-Parameter-Schema festlegen (z. B. `?favorites=<id1>,<id2>`), robust gegen unbekannte/
  ungültige IDs (nur existierende Events übernehmen).
- „Teilen"-Aktion (im Popover nahe „Nur Favoriten") erzeugt auf Abruf den absoluten Link zur
  aktuellen App inkl. Favoriten-Parameter und legt ihn in die Zwischenablage bzw. bietet ihn an.
- In [app.ts](../../../../web/src/app/app.ts) beim Start die Query-Parameter einmalig auslesen
  (`ActivatedRoute`/`Router`) und `FavoritesService.setFromIds(...)` aufrufen; die App schreibt
  die Auswahl anschließend **nicht** laufend zurück in die URL.
- **Deckt ab:** AK 9, AK 10, AK 11.

## Task 6 – Barrierefreiheit absichern

- Stern-Toggle (Detail + Marker in Übersicht rein informativ), „Nur Favoriten"-Umschaltung und
  „Teilen"-Aktion per Tastatur bedienbar, sichtbarer Fokus, Zustands-ARIA (`aria-pressed`).
- Marker in der Übersicht mit sinnvollem Textäquivalent (z. B. `aria-label`/`visually-hidden`
  „Favorit"), ohne die anklickbare Chip-Fläche zu stören.
- **Deckt ab:** AK 13.

## Task 7 – Produktspezifikation ergänzen (Contract + EARS)

- Neue Gherkin-Datei `favoriten.feature` mit Szenarien zu: Markieren/Abwählen, Markierung in der
  Übersicht, „Nur Favoriten"-Filter inkl. UND-Kombination, Zurücksetzen, Teilen-Link und
  Wiederherstellung, kein Rest ohne Parameter.
- Neue EARS-Datei `favoriten.md` mit stabilen IDs.
- [contracts/README.md](../../contracts/README.md) / [ears/README.md](../../ears/README.md) um
  US-021 ergänzen.
- **Deckt ab:** AK 1–14.

## Task 8 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Stern in der Event-Detailansicht markiert/entfernt den Event; Zustand sichtbar (AK 1, AK 2).
  - Favorisierte Events tragen in Kalender-Kachel und Agenda den Stern oben rechts (AK 3).
  - „Nur Favoriten" im Popover schränkt den Kalender ein; Kombination mit Köln/Düsseldorf +
    Klassik/Oper liefert die erwartete Schnittmenge (AK 5, AK 6); Ensemble-/Spielstätten-Liste
    unbeeinflusst (AK 7).
  - „Alle zurücksetzen" entfernt Filter, Favoriten-Filter und Markierungen (AK 8).
  - „Teilen" erzeugt einen Link mit Favoriten-Parametern; Öffnen des Links stellt die Favoriten
    her (AK 9, AK 10); Aufruf ohne Parameter zeigt keine Favoriten (AK 11).
  - Kein `localStorage`/`sessionStorage`-Eintrag (AK 4); Tastaturbedienung/ARIA (AK 13).

## Definition of Done

- Akzeptanzkriterien 1–14 aus [US-021](./US-021-favoriten.md) erfüllt.
- Favoriten sind flüchtig (nur im Speicher); Wiederherstellung ausschließlich über den geteilten
  Link.
- Favoriten-Filter wirkt nur auf Events (Kalender), UND-kombiniert mit Ort/Profil; „Alle
  zurücksetzen" räumt Filter, Favoriten-Filter und Markierungen ab.
- Bestehende Ort-/Profil-Filterung (US-020) und Detailseiteninhalte bleiben regressionsfrei.
- Build erfolgreich; Verhalten manuell mit Positiv-/Negativfällen geprüft.
