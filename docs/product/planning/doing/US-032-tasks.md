# US-032 – Umsetzungs-Tasks

Umsetzung von [US-032](./US-032-composers-detail-filter-favoriten.md): Die
Komponist:in-Detailseite (`composers/:id`) wendet bereits den Ort-/Profil-Filter an
([composer-detail.ts:40-52](../../../../web/src/app/pages/composer-detail/composer-detail.ts#L40-L52)),
aber weder den Favoriten-Filter noch eine Favoriten-Markierung auf den Veranstaltungen.

## Architektur-Entscheidung (verbindlich)

- **Voraussetzung 1:** [US-028, Task 1](./US-028-tasks.md) – `favoriteEventIds`-Parameter
  auf `eventsForFilter`/`worksForFilter`.
- **Voraussetzung 2:** [US-027](./US-027-tasks.md) – Favoriten-Stern in
  [EventList](../../../../web/src/app/shared/event-list.ts). Damit ist AK 1 dieser Story
  bereits automatisch erfüllt, sobald `composer-detail` weiterhin `<app-event-list>`
  verwendet – keine zusätzliche Änderung an der Event-Darstellung nötig.
- [DataService.worksForComposer](../../../../web/src/app/core/data.service.ts#L408) und
  [eventsForComposer](../../../../web/src/app/core/data.service.ts#L419) erhalten je einen
  zusätzlichen optionalen Parameter `favoriteEventIds?: ReadonlySet<string> | null`, den sie
  an ihre internen `worksForFilter`-/`eventsForFilter`-Aufrufe durchreichen. Dadurch
  enthält die „Gespielte Werke"-Liste bei aktivem Favoriten-Filter nur noch Werke, die in
  mindestens einem favorisierten Event vorkommen (AK 3), und die Event-Liste nur noch
  favorisierte Events (AK 2) – beides konsistent zur bestehenden UND-Verknüpfung mit
  Ort/Profil.
- `ComposerDetailPage` injiziert zusätzlich `FavoritesService` und reicht
  `favorites.onlyFavorites() ? favorites.ids() : null` an beide Aufrufe durch.
- Die „Gespielte Werke"-Liste ist reines `<ul>`-Markup
  ([composer-detail.html:75-84](../../../../web/src/app/pages/composer-detail/composer-detail.html#L75-L84)),
  keine Werk-Favoriten existieren – nur die Filterung der Werk-**Menge** ändert sich, nicht
  ihre Darstellung.

Betroffene Dateien:

- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts)
- [web/src/app/pages/composer-detail/composer-detail.ts](../../../../web/src/app/pages/composer-detail/composer-detail.ts)
- [web/src/app/pages/composer-detail/composer-detail.html](../../../../web/src/app/pages/composer-detail/composer-detail.html)

---

## Task 1 – DataService: worksForComposer/eventsForComposer um Favoriten erweitern

- `worksForComposer(composerId, cityIds, profileIds, favoriteEventIds?)`: Parameter an
  `worksForFilter` durchreichen.
- `eventsForComposer(composerId, cityIds, profileIds, favoriteEventIds?)`: Parameter sowohl
  an den internen `worksForComposer`-Aufruf (zur Ermittlung der `workIds`) als auch an den
  `eventsForFilter`-Aufruf durchreichen.
- **Deckt ab:** Grundlage für AK 2, AK 3.

## Task 2 – ComposerDetailPage: Favoriten-Filter anwenden

- In [composer-detail.ts](../../../../web/src/app/pages/composer-detail/composer-detail.ts)
  `FavoritesService` injizieren.
- `works`- und `events`-Computeds (Zeilen 40-52) um den vierten Parameter
  `favorites.onlyFavorites() ? favorites.ids() : null` erweitern.
- **Deckt ab:** AK 2, AK 3, AK 4.

## Task 3 – Leerer Zustand bei Filter ohne Treffer

- In [composer-detail.html](../../../../web/src/app/pages/composer-detail/composer-detail.html)
  wird der Abschnitt „Gespielte Werke" bei leerem `works()`-Array aktuell komplett
  ausgeblendet (`@if (works().length)`,
  [Zeile 75](../../../../web/src/app/pages/composer-detail/composer-detail.html#L75)). Für
  einen aktiven, aber ergebnislosen Filter einen Hinweistext ergänzen (z. B. „Keine Werke
  im aktuellen Filter."), statt den Abschnitt ersatzlos verschwinden zu lassen.
- Sicherstellen, dass Name, Lebensdaten, Epoche, Portrait und Wikipedia-Abschnitt der
  Komponist:in unabhängig vom Filter weiterhin angezeigt werden (AK 6).
- **Deckt ab:** AK 5, AK 6.

## Task 4 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Ein Event favorisieren, zur zugehörigen Komponist:in navigieren: Das Event ist in der
    Veranstaltungsliste mit Stern markiert (AK 1, geerbt aus US-027).
  - „Nur Favoriten" aktivieren: Veranstaltungsliste zeigt nur favorisierte Events (AK 2);
    „Gespielte Werke" zeigt nur Werke aus favorisierten Events (AK 3).
  - Ort-/Profil-Filter wirken weiterhin auf beide Listen (AK 4).
  - Kein Treffer bei restriktivem Filter zeigt Hinweistext statt leerem Verschwinden
    (AK 5).
  - Komponist:innen-Stammdaten bleiben bei jedem Filterzustand sichtbar (AK 6).

## Definition of Done

- Akzeptanzkriterien 1–6 aus [US-032](./US-032-composers-detail-filter-favoriten.md)
  erfüllt.
- `worksForComposer`/`eventsForComposer` bleiben für bestehende Aufrufer ohne neuen
  Parameter abwärtskompatibel.
- Build erfolgreich; Verhalten manuell geprüft.
