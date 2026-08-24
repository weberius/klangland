# US-028 – Umsetzungs-Tasks

Umsetzung von [US-028](./US-028-venues-favoriten-filter.md): Die bereits global im
Header vorhandene „Nur Favoriten"-Umschaltung
([filter-button.html:53-69](../../../../web/src/app/shared/filter-button/filter-button.html#L53-L69),
`FavoritesService.onlyFavorites`) wirkt bislang nur auf den Kalender
([calendar.ts:51](../../../../web/src/app/pages/calendar/calendar.ts#L51)). Sie muss
zusätzlich auf die Spielstätten-Liste (`venues`) wirken, inkl. Favoriten-Markierung der
zugehörigen Events.

## Architektur-Entscheidung (verbindlich)

- **Keine neue Filter-UI.** Der Favoriten-Filter existiert bereits global im
  `FilterButton`-Popover (Header); diese Story verdrahtet lediglich seinen Zustand
  (`FavoritesService.onlyFavorites()` / `.ids()`) in die Spielstätten-Ableitung.
- **Zentrale DataService-Erweiterung (Grundlage für US-028 bis US-032):**
  [DataService.eventsForFilter](../../../../web/src/app/core/data.service.ts#L509) erhält
  einen optionalen dritten Parameter `favoriteEventIds?: ReadonlySet<string> | null`. Ist er
  gesetzt, werden die City-/Profil-gefilterten Events zusätzlich auf diese ID-Menge
  eingeschränkt (UND-Kombination, analog zur bestehenden Kombinationslogik aus
  [US-021](../done/US-021-favoriten.md)).
  [venuesForFilter](../../../../web/src/app/core/data.service.ts#L530) und
  [worksForFilter](../../../../web/src/app/core/data.service.ts#L375) erhalten denselben
  optionalen dritten Parameter und reichen ihn an ihren internen `eventsForFilter`-Aufruf
  durch. `composersForFilter` erhält ihn ebenfalls (Konsistenz, auch wenn aktuell ungenutzt).
  Ohne Angabe (bzw. `null`/`undefined`) ist das Verhalten identisch zum Bestand – bestehende
  Aufrufer (Kalender, Werke-/Komponist:innen-Seiten vor ihrer jeweiligen Story) bleiben
  unverändert lauffähig.
- **Diese zentrale Erweiterung wird als Task 1 dieser Story umgesetzt.**
  [US-029](./US-029-tasks.md), [US-030](./US-030-tasks.md), [US-031](./US-031-tasks.md) und
  [US-032](./US-032-tasks.md) setzen sie voraus und verweisen hierher, statt sie zu
  duplizieren.
- **Favoriten-Markierung je Spielstätte (AK 3):** `VenueListPage` ermittelt zusätzlich zur
  Event-Anzahl je Venue die Liste der favorisierten Events
  (`data.eventsForVenue(v.id).filter(e => favorites.isFavorite(e.id))`) und zeigt sie – nur
  wenn nicht leer – als kompakte Zusatzzeile auf der Karte an (Stern + Titel), unabhängig
  vom aktiven Favoriten-Filter (analog zur bestehenden Vorschau-Logik in
  [composer-list.ts](../../../../web/src/app/pages/composer-list/composer-list.ts)).

Betroffene Dateien:

- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (Task 1, zentral)
- [web/src/app/pages/venue-list/venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts)
- [web/src/app/pages/venue-list/venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html)
- [web/src/app/pages/venue-list/venue-list.css](../../../../web/src/app/pages/venue-list/venue-list.css)

---

## Task 1 – DataService um favoriten-bewusste Filterung erweitern

- `eventsForFilter(cityIds, profileIds, favoriteEventIds?: ReadonlySet<string> | null)`:
  bestehende City-/Profil-Filterung beibehalten, Ergebnis zusätzlich mit
  `favoriteEventIds.has(e.id)` einschränken, falls übergeben.
- `venuesForFilter(cityIds, profileIds, favoriteEventIds?)`: dritten Parameter an den
  internen `eventsForFilter`-Aufruf durchreichen; Kurzschluss-Rückgabe `return this.venues`
  bei leerer Auswahl nur noch verwenden, wenn zusätzlich `favoriteEventIds` nicht gesetzt ist.
- `worksForFilter(cityIds, profileIds, favoriteEventIds?)` und `composersForFilter(cityIds,
  profileIds, favoriteEventIds?)` analog anpassen (Durchreichen an `eventsForFilter` bzw.
  `worksForFilter`).
- JSDoc-Kommentare der betroffenen Methoden um den Favoriten-Parameter ergänzen.
- **Deckt ab:** Grundlage für AK 1–2, keine direkte AK dieser Story, aber Voraussetzung für
  US-029 bis US-032.

## Task 2 – VenueListPage: Favoriten-Filter anwenden

- In [venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts) den
  `FavoritesService` injizieren.
- `venues`-Computed um dritten Parameter erweitern:
  `favorites.onlyFavorites() ? favorites.ids() : null`.
- **Deckt ab:** AK 1, AK 2, AK 4.

## Task 3 – Favoriten-Events je Spielstätte anzeigen

- In [venue-list.ts](../../../../web/src/app/pages/venue-list/venue-list.ts) je Venue die
  favorisierten Events ermitteln (siehe Architektur-Entscheidung) und der Karte als
  zusätzliches Feld bereitstellen (z. B. `favoriteEvents(v): ConcertEvent[]`).
- In [venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html) diese
  Liste unterhalb der bestehenden Meta-Zeile rendern (★ + Event-Titel je Zeile), nur wenn
  nicht leer.
- Styling in [venue-list.css](../../../../web/src/app/pages/venue-list/venue-list.css)
  ergänzen (kompakt, konsistent mit `.favorite-marker`/`★`-Mustern).
- **Deckt ab:** AK 3.

## Task 4 – Leerer Zustand bei aktivem Favoriten-Filter ohne Treffer

- In [venue-list.html](../../../../web/src/app/pages/venue-list/venue-list.html) die
  bestehende Meldung „Keine Spielstätten erfasst." greift bereits bei leerem Array – prüfen,
  ob ein spezifischerer Hinweistext sinnvoll ist, wenn der Favoriten-Filter aktiv ist (z. B.
  „Keine Spielstätten mit favorisierten Veranstaltungen.").
- **Deckt ab:** AK 5.

## Task 5 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Ein Event favorisieren, im Header „Nur Favoriten" aktivieren: `venues` zeigt nur die
    zugehörige Spielstätte (AK 1, AK 2).
  - Die Spielstätten-Karte zeigt das favorisierte Event mit Stern (AK 3).
  - Kombination mit Ort-/Profil-Filter liefert die erwartete Schnittmenge (AK 4).
  - Ohne Favoriten und aktivem Filter erscheint eine leere Liste mit Hinweistext (AK 5).
  - Kalender-Verhalten (US-021) bleibt unverändert (Regressionstest).

## Definition of Done

- Akzeptanzkriterien 1–5 aus [US-028](./US-028-venues-favoriten-filter.md) erfüllt.
- `DataService`-Erweiterung ist abwärtskompatibel (bestehende Aufrufer ohne dritten
  Parameter unverändert lauffähig).
- Build erfolgreich; Verhalten manuell geprüft.
