# US-030 – Umsetzungs-Tasks

Umsetzung von [US-030](./US-030-works-favoriten-filter.md): Die global im Header
vorhandene „Nur Favoriten"-Umschaltung (`FavoritesService.onlyFavorites`) muss zusätzlich
auf die Werke-Liste (`works`) wirken.

## Architektur-Entscheidung (verbindlich)

- **Voraussetzung:** Diese Story baut auf der in [US-028, Task 1](./US-028-tasks.md)
  beschriebenen Erweiterung von
  [DataService.worksForFilter](../../../../web/src/app/core/data.service.ts#L375) um einen
  optionalen `favoriteEventIds`-Parameter auf. Ist diese Erweiterung noch nicht umgesetzt,
  zuerst dort nachziehen (nicht duplizieren).
- **Keine neue Filter-UI**, keine Änderung an `FavoritesService`.
- [WorkListPage](../../../../web/src/app/pages/work-list/work-list.ts) ruft
  `worksForFilter` direkt auf ([work-list.ts:20](../../../../web/src/app/pages/work-list/work-list.ts#L20));
  der Favoriten-Parameter wird dort durchgereicht.

Betroffene Dateien:

- [web/src/app/pages/work-list/work-list.ts](../../../../web/src/app/pages/work-list/work-list.ts)
- [web/src/app/pages/work-list/work-list.html](../../../../web/src/app/pages/work-list/work-list.html)

---

## Task 1 – WorkListPage: Favoriten-Filter anwenden

- In [work-list.ts](../../../../web/src/app/pages/work-list/work-list.ts) den
  `FavoritesService` injizieren.
- Aufruf in Zeile 20 erweitern:
  `this.data.worksForFilter(cityIds, profileIds, favorites.onlyFavorites() ? favorites.ids() : null)`.
- **Deckt ab:** AK 1, AK 2, AK 3.

## Task 2 – Leerer Zustand bei aktivem Favoriten-Filter ohne Treffer

- In [work-list.html](../../../../web/src/app/pages/work-list/work-list.html) prüfen, ob
  der bestehende Hinweis „Keine Werke erfasst." ausreicht oder ein spezifischerer Text
  sinnvoll ist, wenn der Favoriten-Filter aktiv ist (z. B. „Keine Werke aus favorisierten
  Veranstaltungen.").
- **Deckt ab:** AK 4.

## Task 3 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Ein Event favorisieren, „Nur Favoriten" aktivieren: `works` zeigt nur die Werke, die im
    favorisierten Event gespielt werden (AK 1, AK 2).
  - Kombination mit Ort-/Profil-Filter liefert die erwartete Schnittmenge (AK 3).
  - Ohne Favoriten und aktivem Filter erscheint eine leere Liste mit Hinweistext (AK 4).
  - Kalender-, Spielstätten- und Komponist:innen-Verhalten (US-021, US-028, US-029) bleiben
    unverändert (Regressionstest).

## Definition of Done

- Akzeptanzkriterien 1–4 aus [US-030](./US-030-works-favoriten-filter.md) erfüllt.
- Build erfolgreich; Verhalten manuell geprüft.
