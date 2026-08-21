# US-015 – Umsetzungs-Tasks

Umsetzung von [US-015](./US-015-ticket-links.md): Ticket-Link nur bei zeitlicher/statusbezogener Sinnhaftigkeit anzeigen und beim Klick per Bestätigungsdialog auf das Verlassen der Seite hinweisen.

Betroffene Dateien:
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts)
- [web/src/app/pages/event-detail/event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)
- [web/src/app/pages/event-detail/event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css)
- [web/src/app/core/date-util.ts](../../../../web/src/app/core/date-util.ts) (gemeinsamer „heute"-Helfer)
- ggf. [web/src/app/pages/calendar/calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts) (optionale Refaktorierung auf den Helfer)

Referenz für den Dialog: der bestehende, barrierefreie Dialog in [city-map.html:14-29](../../../../web/src/app/pages/city-map/city-map.html#L14-L29) / [city-map.ts:49-59](../../../../web/src/app/pages/city-map/city-map.ts#L49-L59) (`role="dialog"`, `aria-modal="true"`, Signal-gesteuert).

---

## Task 1 – Gemeinsamen „heute"-Helfer bereitstellen (date-util.ts)

Bezug: AK 1, AK 2, AK 3.

- Aktuell wird das heutige Datum nur inline in der Kalenderseite bestimmt und respektiert dabei `APP_CONFIG.referenceDate` ([calendar.ts:106-111](../../../../web/src/app/pages/calendar/calendar.ts#L106-L111)). Damit die Ticket-Logik dieselbe Referenz nutzt (und Zeitzonenprobleme vermeidet, da mit ISO-Strings verglichen wird), diese Berechnung als wiederverwendbaren Helfer nach [date-util.ts](../../../../web/src/app/core/date-util.ts) ziehen:
  ```ts
  // referenceDate erlaubt ein festes „Heute" (Tests/Demo), sonst Systemdatum.
  export function todayIso(referenceDate?: string | null): string {
    if (referenceDate) return referenceDate;
    const now = new Date();
    return isoDate(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }
  ```
- Vergleich funktioniert per lexikographischem String-Vergleich auf `YYYY-MM-DD` (`event.date >= todayIso(...)` = heute oder Zukunft), konsistent mit der übrigen ISO-Datumslogik.
- Optional (kein Muss, um Scope klein zu halten): [calendar.ts](../../../../web/src/app/pages/calendar/calendar.ts) auf `todayIso(APP_CONFIG.referenceDate)` umstellen, damit es nur eine Quelle gibt. Verhalten muss identisch bleiben.

## Task 2 – Sichtbarkeits-Logik im Component (event-detail.ts)

Bezug: AK 1, AK 2, AK 3, AK 4, AK 5.

- `APP_CONFIG` und `todayIso` importieren.
- Ein abgeleitetes Signal ergänzen, das genau dann `true` ist, wenn ein Ticketkauf sinnvoll ist:
  ```ts
  /** Ticket-Link nur zeigen, wenn ein URL da ist, das Event nicht abgesagt ist
   *  und das Datum heute oder in der Zukunft liegt (US-015). */
  readonly canBuyTickets = computed(() => {
    const e = this.event();
    if (!e || !e.ticketUrl) return false;
    if (e.status === 'cancelled') return false;
    return e.date >= todayIso(APP_CONFIG.referenceDate);
  });
  ```
  - `!e.ticketUrl` deckt AK 5 ab (kein URL → kein Button).
  - `status === 'cancelled'` deckt AK 4 ab. `postponed`/`rescheduled` behalten den Link bewusst, solange das Datum nicht vergangen ist (siehe US „Gewählte Lösung").
  - `e.date >= todayIso(...)` deckt AK 1–3 ab (Veranstaltungstag zählt noch).

## Task 3 – Bestätigungsdialog im Component (event-detail.ts)

Bezug: AK 6, AK 7, AK 8.

- Signal für die Sichtbarkeit des Dialogs ergänzen: `protected readonly ticketDialogOpen = signal(false);` (`signal` aus `@angular/core` importieren).
- Handler ergänzen:
  ```ts
  /** Öffnet den Verlassen-Hinweis; der externe Link wird erst nach Bestätigung geöffnet. */
  openTicketDialog(): void {
    if (this.canBuyTickets()) this.ticketDialogOpen.set(true);
  }

  /** Bricht den Hinweis ab – es wird nichts geöffnet (AK 8). */
  cancelTicketDialog(): void {
    this.ticketDialogOpen.set(false);
  }

  /** Bestätigt den Hinweis und öffnet die externe Ticketseite im neuen Tab (AK 7). */
  confirmTickets(): void {
    const url = this.event()?.ticketUrl;
    this.ticketDialogOpen.set(false);
    if (url) window.open(url, '_blank', 'noopener');
  }
  ```
- Hinweis (Popup-Blocker): `window.open` wird hier direkt im Klick-Handler des Bestätigen-Buttons aufgerufen (also innerhalb einer echten Nutzergeste) – dadurch greift kein Popup-Blocker. Deshalb bewusst **kein** `<a href>` mit vorheriger `preventDefault`-Kaskade.

## Task 4 – Template anpassen (event-detail.html)

Bezug: AK 1–8, AK 9 (unveränderte Bereiche), AK 10.

- Den bestehenden Ticket-Link ([event-detail.html:20-22](../../../../web/src/app/pages/event-detail/event-detail.html#L20-L22)) ersetzen: statt eines immer sichtbaren `<a>` einen Button, der über `@if (canBuyTickets())` ein-/ausgeblendet wird und den Dialog öffnet:
  ```html
  @if (canBuyTickets()) {
    <button type="button" class="btn btn-primary" (click)="openTicketDialog()">Tickets</button>
  }
  ```
  - Ein `<button>` (statt `<a>`) ist korrekt, weil der Klick zuerst den Dialog auslöst und nicht direkt navigiert.
- Dialog-Markup ergänzen (analog [city-map.html:14-29](../../../../web/src/app/pages/city-map/city-map.html#L14-L29)), am Ende des `@else`-Blocks:
  ```html
  @if (ticketDialogOpen()) {
    <div class="dialog-backdrop" (click)="cancelTicketDialog()"></div>
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="ticket-dialog-title">
      <h2 id="ticket-dialog-title">Externe Seite öffnen</h2>
      <p>
        Sie verlassen Klangland und öffnen die Ticketseite des Anbieters in einem neuen
        Tab/Fenster. Von dort führt keine Zurück-Navigation in diese Anwendung.
      </p>
      <div class="dialog-actions">
        <button type="button" class="btn" (click)="cancelTicketDialog()">Abbrechen</button>
        <button type="button" class="btn btn-primary" (click)="confirmTickets()">Tickets öffnen</button>
      </div>
    </div>
  }
  ```
- Alle übrigen Aktionen (Kalender-Eintrag, Favorit) und Seitenbereiche unverändert lassen (AK 9).
- Barrierefreiheit (AK 10): `role="dialog"`, `aria-modal="true"`, `aria-labelledby`; Buttons sind per Tastatur erreichbar. Optional: `Escape` schließt den Dialog (per `(keydown.escape)` / Host-Listener) und Fokus auf den ersten Dialog-Button setzen – konsistent zum bestehenden Dialog-Verhalten.

## Task 5 – Styling (event-detail.css)

Bezug: AK 10, optische Integration.

- Falls die Klassen `.dialog`, `.dialog-backdrop`, `.dialog-actions` nicht global verfügbar sind, an das bestehende City-Map-Dialog-Styling angleichen (Backdrop-Overlay, zentriertes Panel, sichtbarer Fokuszustand der Buttons). Vorhandene globale Styles bevorzugt wiederverwenden statt duplizieren.
- Button-Reihe `.dialog-actions` mit klarem Abstand; `.btn-primary` (Bestätigen) und neutraler `.btn` (Abbrechen) konsistent zu den übrigen Buttons.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` und im Browser prüfen (ggf. `APP_CONFIG.referenceDate` in [app-config.ts](../../../../web/src/app/core/app-config.ts) nutzen, um „heute" für Tests zu setzen):
  - Zukünftiges Event mit `ticketUrl`, `status = scheduled`: Button sichtbar (AK 1).
  - Event am heutigen Tag (`referenceDate` = Event-Datum): Button sichtbar (AK 3).
  - Vergangenes Event mit `ticketUrl`: kein Button (AK 2).
  - Zukünftiges Event mit `status = cancelled`: kein Button (AK 4).
  - Event ohne `ticketUrl` (`null`): kein Button (AK 5).
  - Klick auf Button → Dialog mit Verlassen-Hinweis (AK 6); „Tickets öffnen" öffnet neuen Tab auf `ticketUrl` (AK 7); „Abbrechen"/Backdrop schließt Dialog ohne Öffnen, Nutzer:in bleibt auf der Seite (AK 8).
  - Tastatur: Button und Dialog-Buttons per Tab erreichbar, Fokus sichtbar; (optional) Escape schließt (AK 10).
  - Übrige Aktionen (Kalender, Favorit) und Inhalte unverändert (AK 9).

## Definition of Done

- Alle Akzeptanzkriterien 1–10 aus [US-015](./US-015-ticket-links.md) erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen an anderen Seiten (außer optionaler, verhaltensgleicher Refaktorierung der Kalender-„heute"-Berechnung).
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben.
