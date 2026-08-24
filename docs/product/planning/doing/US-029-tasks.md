# US-029 – Umsetzungs-Tasks

Umsetzung von [US-029](./US-029-composers-favoriten-filter.md): Die global im Header
vorhandene „Nur Favoriten"-Umschaltung (`FavoritesService.onlyFavorites`) muss zusätzlich
auf die Komponist:innen-Liste (`composers`) wirken.

## Architektur-Entscheidung (verbindlich)

- **Voraussetzung:** Diese Story baut auf der in [US-028, Task 1](./US-028-tasks.md)
  beschriebenen Erweiterung von
  [DataService.worksForFilter](../../../../web/src/app/core/data.service.ts#L375) um einen
  optionalen `favoriteEventIds`-Parameter auf. Ist diese Erweiterung noch nicht umgesetzt,
  zuerst dort nachziehen (nicht duplizieren).
- **Keine neue Filter-UI**, keine Änderung an `FavoritesService`.
- [ComposerListPage](../../../../web/src/app/pages/composer-list/composer-list.ts)
  gruppiert Werke bereits lokal aus einem einzigen `worksForFilter`-Aufruf
  ([composer-list.ts:43](../../../../web/src/app/pages/composer-list/composer-list.ts#L43)).
  Der Favoriten-Parameter wird an genau dieser Stelle durchgereicht; die bestehende
  Gruppierungs-/Sortierlogik bleibt unverändert (Performance-Optimierung aus US-024 bleibt
  erhalten).

Betroffene Dateien:

- [web/src/app/pages/composer-list/composer-list.ts](../../../../web/src/app/pages/composer-list/composer-list.ts)
- [web/src/app/pages/composer-list/composer-list.html](../../../../web/src/app/pages/composer-list/composer-list.html)

---

## Task 1 – ComposerListPage: Favoriten-Filter anwenden

- In [composer-list.ts](../../../../web/src/app/pages/composer-list/composer-list.ts) den
  `FavoritesService` injizieren.
- Aufruf in Zeile 43 erweitern:
  `this.data.worksForFilter(cityIds, profileIds, favorites.onlyFavorites() ? favorites.ids() : null)`.
- **Deckt ab:** AK 1, AK 2, AK 3.

## Task 2 – Leerer Zustand bei aktivem Favoriten-Filter ohne Treffer

- In [composer-list.html](../../../../web/src/app/pages/composer-list/composer-list.html)
  prüfen, ob der bestehende Hinweis „Keine Komponist:innen erfasst." ausreicht oder ein
  spezifischerer Text sinnvoll ist, wenn der Favoriten-Filter aktiv ist (z. B. „Keine
  Komponist:innen mit favorisierten Veranstaltungen.").
- **Deckt ab:** AK 4.

## Task 3 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Ein Event favorisieren, „Nur Favoriten" aktivieren: `composers` zeigt nur die
    Komponist:in(nen), deren Werk im favorisierten Event gespielt wird (AK 1, AK 2).
  - Kombination mit Ort-/Profil-Filter liefert die erwartete Schnittmenge (AK 3).
  - Ohne Favoriten und aktivem Filter erscheint eine leere Liste mit Hinweistext (AK 4).
  - Kalender- und Spielstätten-Verhalten (US-021, US-028) bleiben unverändert
    (Regressionstest).

## Definition of Done

- Akzeptanzkriterien 1–4 aus [US-029](./US-029-composers-favoriten-filter.md) erfüllt.
- Bestehende Performance-Optimierung (ein `worksForFilter`-Aufruf statt n) bleibt erhalten.
- Build erfolgreich; Verhalten manuell geprüft.
