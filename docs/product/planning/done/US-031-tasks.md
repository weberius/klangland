# US-031 – Umsetzungs-Tasks

Umsetzung von [US-031](./US-031-works-detail-filter.md): Die Werk-Detailseite
(`works/:id`) ignoriert aktuell sowohl die Ort-/Profil-Filter (`FilterService`) als auch
den Favoriten-Filter (`FavoritesService`) vollständig –
[work-detail.ts:57-59](../../../../web/src/app/pages/work-detail/work-detail.ts#L57-L59)
ruft `data.eventsForWork(w.id)` ohne jede Einschränkung auf.

## Architektur-Entscheidung (verbindlich)

- **Voraussetzung:** Diese Story baut auf der in [US-028, Task 1](./US-028-tasks.md)
  beschriebenen Erweiterung von
  [DataService.eventsForFilter](../../../../web/src/app/core/data.service.ts#L509) um einen
  optionalen `favoriteEventIds`-Parameter auf. Ist diese Erweiterung noch nicht umgesetzt,
  zuerst dort nachziehen.
- [DataService.eventsForWork](../../../../web/src/app/core/data.service.ts#L362) erhält
  zwei zusätzliche **optionale** Parameter `cityIds`, `profileIds` (jeweils Default
  `new Set()`) sowie `favoriteEventIds?: ReadonlySet<string> | null`, analog zum Muster von
  [eventsForComposer](../../../../web/src/app/core/data.service.ts#L419): die unveränderte
  Werk-Ereignisliste wird zusätzlich mit der Ergebnismenge von
  `eventsForFilter(cityIds, profileIds, favoriteEventIds)` geschnitten. Ohne Angabe der
  neuen Parameter bleibt das Verhalten identisch zum Bestand – der bestehende Aufruf in
  [work-list.ts](../../../../web/src/app/pages/work-list/work-list.ts) (nur `eventCount`)
  bleibt unverändert lauffähig.
- `WorkDetailPage` injiziert zusätzlich `FilterService` und `FavoritesService` und reicht
  deren aktuellen Zustand an `eventsForWork` durch.
- Die Favoriten-Markierung (★) der einzelnen Events erscheint automatisch über die aus
  [US-027](./US-027-tasks.md) erweiterte [EventList](../../../../web/src/app/shared/event-list.ts)
  – hierfür ist auf dieser Seite keine zusätzliche Änderung nötig.

Betroffene Dateien:

- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts)
- [web/src/app/pages/work-detail/work-detail.ts](../../../../web/src/app/pages/work-detail/work-detail.ts)
- [web/src/app/pages/work-detail/work-detail.html](../../../../web/src/app/pages/work-detail/work-detail.html)

---

## Task 1 – DataService: eventsForWork um Filter-/Favoriten-Parameter erweitern

- `eventsForWork(workId: string, cityIds: ReadonlySet<string> = new Set(), profileIds:
  ReadonlySet<string> = new Set(), favoriteEventIds?: ReadonlySet<string> | null)`: bei
  leerer `cityIds`/`profileIds`-Auswahl und ohne `favoriteEventIds` unverändertes Verhalten
  zurückgeben; andernfalls Ergebnis mit `eventsForFilter(cityIds, profileIds,
  favoriteEventIds)` schneiden (IDs-Set-Abgleich, sortiert nach Datum/Zeit wie bisher).
- **Deckt ab:** Grundlage für AK 1–4.

## Task 2 – WorkDetailPage: Filter- und Favoriten-Service einbinden

- In [work-detail.ts](../../../../web/src/app/pages/work-detail/work-detail.ts)
  `FilterService` und `FavoritesService` injizieren.
- `events`-Computed
  ([Zeile 56-59](../../../../web/src/app/pages/work-detail/work-detail.ts#L56-L59))
  erweitern:
  `data.eventsForWork(w.id, filter.selectedCityIds(), filter.selectedProfileIds(),
  favorites.onlyFavorites() ? favorites.ids() : null)`.
- **Deckt ab:** AK 1, AK 2, AK 3, AK 4.

## Task 3 – Leerer Zustand bei Filter ohne Treffer

- Prüfen, dass [EventList](../../../../web/src/app/shared/event-list.ts) bei leerem Array
  bereits „Keine Veranstaltungen erfasst." zeigt; ggf. spezifischeren Hinweistext auf
  `work-detail.html` ergänzen, wenn ein Filter aktiv ist.
- Sicherstellen, dass Titel, Komponist:in, Werkverzeichnis, Entstehungszeit und Dauer des
  Werks unabhängig vom Filter weiterhin angezeigt werden (AK 6).
- **Deckt ab:** AK 5, AK 6.

## Task 4 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Ort-Filter aktivieren: `works/:id` zeigt nur Veranstaltungen aus dem gewählten Ort
    (AK 1).
  - Musikprofil-Filter aktivieren: nur passende Veranstaltungen (AK 2).
  - „Nur Favoriten" aktivieren: nur favorisierte Veranstaltungen, mit Stern markiert
    (AK 3, geerbt aus US-027).
  - Mehrere Filter gleichzeitig liefern die erwartete Schnittmenge (AK 4).
  - Kein Treffer bei restriktivem Filter zeigt eine leere Liste/Hinweistext (AK 5).
  - Werk-Stammdaten bleiben bei jedem Filterzustand sichtbar (AK 6).

## Definition of Done

- Akzeptanzkriterien 1–6 aus [US-031](./US-031-works-detail-filter.md) erfüllt.
- `eventsForWork` bleibt für bestehende Aufrufer ohne neue Parameter abwärtskompatibel.
- Build erfolgreich; Verhalten manuell geprüft.
