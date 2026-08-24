# US-027 – Umsetzungs-Tasks

Umsetzung von [US-027](./US-027-orchester-event-favorit.md): Favorisierte Events müssen
auch in der Veranstaltungsliste der Ensemble-Detailseite (Route `/ensembles/:id`,
Komponente [ensemble-detail](../../../../web/src/app/pages/ensemble-detail/)) – im
Anwenderjargon „Orchester-Detailseite" – als Favorit erkennbar sein.

## Architektur-Entscheidung (verbindlich)

- Die Ensemble-Detailseite zeigt ihre Veranstaltungen über die **gemeinsam genutzte**
  Komponente [EventList](../../../../web/src/app/shared/event-list.ts) an
  (`<app-event-list [events]="events()" [showEnsemble]="false" />`,
  siehe [ensemble-detail.html:70](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L70)).
  Die Favoriten-Markierung wird deshalb **einmalig in `EventList`** ergänzt und nicht in
  `ensemble-detail` dupliziert.
- `EventList` erhält direkten Zugriff auf den root-bereitgestellten
  [FavoritesService](../../../../web/src/app/core/favorites.service.ts) (analog zum
  bestehenden `DataService`-Zugriff) und rendert je Zeile einen Stern
  (★ favorisiert / ☆ nicht favorisiert), visuell angelehnt an den Stern-Toggle aus
  [event-detail.html:24-34](../../../../web/src/app/pages/event-detail/event-detail.html#L24-L34).
- Anders als der rein informative Stern in der Kalenderübersicht
  ([calendar.html:42-46](../../../../web/src/app/pages/calendar/calendar.html#L42-L46))
  fordert AK 3 dieser Story ein **klickbares** Symbol: Der Stern ist ein eigener
  `<button>` innerhalb der Listenzeile, der `FavoritesService.toggle(e.id)` aufruft und
  per `event.stopPropagation()`/`event.preventDefault()` verhindert, dass der Klick
  zusätzlich den Zeilen-Link (`routerLink` zur Event-Detailseite) auslöst.
- **Seiteneffekt (beabsichtigt):** Da `EventList` außerdem von
  [venue-detail](../../../../web/src/app/pages/venue-detail/venue-detail.ts),
  [composer-detail](../../../../web/src/app/pages/composer-detail/composer-detail.ts) und
  [work-detail](../../../../web/src/app/pages/work-detail/work-detail.ts) verwendet wird,
  erhalten auch diese Seiten automatisch die Favoriten-Markierung. Das ist gewollt und wird
  von [US-032](./US-032-composers-detail-filter-favoriten.md) vorausgesetzt.

Betroffene Dateien:

- [web/src/app/shared/event-list.ts](../../../../web/src/app/shared/event-list.ts)
- [web/src/app/shared/event-list.html](../../../../web/src/app/shared/event-list.html)
- [web/src/app/shared/event-list.css](../../../../web/src/app/shared/event-list.css)

---

## Task 1 – FavoritesService in EventList einbinden

- In [event-list.ts](../../../../web/src/app/shared/event-list.ts) den
  `FavoritesService` injizieren; Methoden `isFavorite(e: ConcertEvent): boolean` und
  `toggleFavorite(e: ConcertEvent, event: Event): void` (mit `stopPropagation()`/
  `preventDefault()`) ergänzen.
- **Deckt ab:** AK 1, AK 3.

## Task 2 – Sternchen-Button in der Listenzeile ergänzen

- In [event-list.html](../../../../web/src/app/shared/event-list.html) je Zeile
  (`event-row`) einen Stern-Button vor bzw. neben `event-row-title` ergänzen:
  `[class.is-favorite]`, `[attr.aria-pressed]="isFavorite(e)"`, sprechendes
  `aria-label` („Zu Favoriten hinzufügen" / „Aus Favoriten entfernen"),
  `(click)="toggleFavorite(e, $event)"`.
- **Deckt ab:** AK 1, AK 3.

## Task 3 – Styling des Sternchen-Buttons

- In [event-list.css](../../../../web/src/app/shared/event-list.css) Stil für
  gefüllten/leeren Stern ergänzen, angelehnt an `.favorite-star`
  ([event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css)) bzw.
  `.favorite-marker` ([calendar.css](../../../../web/src/app/pages/calendar/calendar.css)).
  Sichtbarer Fokuszustand für den neuen Button nicht vergessen.
- **Deckt ab:** AK 2.

## Task 4 – Verifikation auf weiteren EventList-Konsumenten

- Sichten, dass `venue-detail`, `composer-detail` und `work-detail` durch die Änderung an
  `EventList` keine Layout-Regressionen zeigen (Sternchen fügt sich in bestehende
  Zeilenbreite ein).
- **Deckt ab:** AK 2 (Konsistenz).

## Task 5 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Auf `ensembles/:id` ein Event über die Event-Detailseite favorisieren, zurück zur
    Ensemble-Detailseite navigieren: Das Event zeigt den gefüllten Stern (AK 1).
  - Stern-Darstellung entspricht optisch dem übrigen Projektmuster (AK 2).
  - Klick auf den Stern in der Liste togglet den Favoritenstatus, ohne auf die
    Event-Detailseite zu navigieren (AK 3).
  - Nicht favorisierte Events zeigen weiterhin keinen gefüllten Stern (AK 4).

## Definition of Done

- Akzeptanzkriterien 1–4 aus [US-027](./US-027-orchester-event-favorit.md) erfüllt.
- Favoriten-Logik in `FavoritesService` unverändert (nur Konsum in `EventList`).
- Build erfolgreich; Verhalten manuell auf der Ensemble-Detailseite geprüft.
