# US-019 – Umsetzungs-Tasks

Umsetzung von [US-019](./US-019-events-url.md): Das `source`-Objekt eines Events wird um
**`calendarUrl`** (Kalender-/Übersichtsseite, über die das Event recherchiert wurde)
erweitert. `source.url` bleibt die **konkrete Veranstaltungsseite**, `calendarUrl` **darf
`null`** sein. Bestehende Events erhalten `calendarUrl: null` (echte Kalender-URLs werden
später nachgetragen).

## Modell-Entscheidung (verbindlich)

- `EventSource` bekommt ein neues Feld `calendarUrl: string | null` (Pflichtfeld im Typ,
  Wert darf `null` sein). Keine weiteren Feldänderungen (`url`, `name`, `retrievedAt`
  unverändert). `ticketUrl` und `lastVerified` bleiben auf Event-Ebene wie bisher.
- Für alle 1291 Bestands-Events wird `calendarUrl: null` gesetzt, damit die Struktur
  einheitlich ist (kein `undefined`/fehlendes Feld).

Betroffene Dateien:
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts)
- [docs/events-and-relations.md](../../../events-and-relations.md)
- [data/events.json](../../../../data/events.json)
- [web/src/app/pages/event-detail/event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts) (voraussichtlich nur Prüfung)
- [docs/product/contracts/veranstaltungsdetail.feature](../../contracts/veranstaltungsdetail.feature)
- [docs/product/ears/veranstaltungsdetail.md](../../ears/veranstaltungsdetail.md)
- [docs/data-tooling/](../../../data-tooling/) (`ingest_*.py`)
- [docs/architecture/](../../../architecture/) (nur ADR-Bewertung)

---

## Task 1 – ADR-Bewertung (kein neues ADR)

- Prüfen und **kurz dokumentieren**, dass US-019 **keine** neue Architekturentscheidung
  auslöst: Es handelt sich um eine feldweite Erweiterung innerhalb des bestehenden
  normalisierten Modells und ändert weder Datei-Aufteilung noch Referenzsemantik.
- Einschlägige bestehende ADRs bleiben maßgeblich und werden **nicht** umgeschrieben:
  [ADR-002](../../../architecture/ADR-002-json-dateien-als-single-source-of-truth.md)
  (JSON als Single Source of Truth, Herkunft/Provenienz) und
  [ADR-005](../../../architecture/ADR-005-idempotente-python-ingest-skripte.md)
  (idempotente Ingest-Skripte je Quelle) – letzteres ist für Task 6 relevant.
- Ergebnis: **kein** Eintrag in [architecture/README.md](../../../architecture/README.md)
  nötig. (Diese Bewertung ist die „Berücksichtigung ADR"; sie muss nicht als Datei
  abgelegt werden.)
- **Deckt ab:** organisatorisch, keine AK direkt.

## Task 2 – TypeScript-Modell erweitern (models.ts)

- In [models.ts](../../../../web/src/app/models/models.ts) das Interface `EventSource`
  ([models.ts:129-133](../../../../web/src/app/models/models.ts#L129-L133)) um
  `calendarUrl: string | null;` ergänzen (Reihenfolge z. B. nach `url`).
- Keine Änderung an `ConcertEvent.ticketUrl` / `lastVerified`.
- **Deckt ab:** AK 1, 8. **Sync-Anker:** muss zu Entity-Doku (Task 3) und Daten (Task 5)
  passen.

## Task 3 – Entity-/Datenmodell-Doku aktualisieren (events-and-relations.md)

- In [events-and-relations.md](../../../events-and-relations.md) die Feldtabelle
  ([events-and-relations.md:69](../../../events-and-relations.md#L69)) so präzisieren, dass
  `source` als Objekt mit `url`, `calendarUrl`, `name`, `retrievedAt` beschrieben wird –
  jeweils mit Bedeutung gemäß US-019:
  - `source.url` – konkrete Veranstaltungsseite (AK 2).
  - `source.calendarUrl` – Kalender-/Übersichtsseite, über die recherchiert wurde; darf
    `null` sein (AK 3, 8).
  - `source.name` – Organisation/Anbieter der primären Quelle (AK 4).
  - `source.retrievedAt` – Datum des letzten Abrufs (AK 5).
  - `ticketUrl` (Event-Ebene) – direkter Ticketlink, sofern vorhanden (AK 6).
  - `lastVerified` (Event-Ebene) – letzte inhaltliche Prüfung (AK 7).
- Ein Beispiel-`source`-Objekt mit `calendarUrl` ergänzen (analog zum Beispiel in der User
  Story).
- Im Abschnitt „Pflege und Validierung" ergänzen, dass `calendarUrl` optional (`null`
  zulässig) ist und `source.url` weiterhin Pflicht bleibt.
- **Deckt ab:** AK 1–8. **Sync-Anker:** Feldbedeutungen müssen zu Task 2 identisch sein.

## Task 4 – Event-Detailseite: Quellenanzeige (event-detail.html / .ts)

- [event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)
  Quellen-Abschnitt
  ([event-detail.html:97-108](../../../../web/src/app/pages/event-detail/event-detail.html#L97-L108)):
  - Bestätigen, dass weiterhin die **konkrete Veranstaltungsseite** verlinkt ist
    (`source.url` als `href`, `source.name` als Text) – erfüllt AK 9 (Pflichtteil).
  - Ticket-Verweis bleibt im Header
    ([event-detail.html:19-21](../../../../web/src/app/pages/event-detail/event-detail.html#L19-L21))
    – erfüllt AK 9 (Ticketseite, sofern vorhanden).
  - **Optional** die Kalender-/Übersichtsseite anzeigen: nur rendern, wenn
    `source.calendarUrl` gesetzt ist, z. B. ein zusätzlicher Link „Kalender/Übersicht der
    Quelle" mit `target="_blank" rel="noopener"`.
- [event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts): bei Bedarf
  ein `computed` für `calendarUrl` ergänzen; sonst keine Logikänderung.
- **Deckt ab:** AK 9 (und optionale Kalender-URL-Anzeige).

## Task 5 – Bestandsdaten migrieren (data/events.json)

- In allen **1291** `source`-Objekten das Feld `calendarUrl: null` einfügen (bevorzugt
  direkt nach `url`), ohne bestehende Werte zu verändern.
- Umsetzung mechanisch/skriptgestützt (z. B. Python-Einzeiler, der jedes `event.source`
  um `calendarUrl` ergänzt, falls nicht vorhanden) und **idempotent** halten (erneutes
  Ausführen ändert nichts).
- `metadata.lastUpdated` in [events.json](../../../../data/events.json) auf `2026-08-19`
  setzen; `metadata.version` minor erhöhen.
- Danach prüfen: valides JSON; jedes `source` hat die Schlüssel
  `url, calendarUrl, name, retrievedAt`; kein `source` ist `null`.
- **Deckt ab:** AK 1, 8. **Sync-Anker:** Feld muss zum Typ aus Task 2 passen.

## Task 6 – Ingest-Skripte für Neudaten (docs/data-tooling/ingest_*.py)

- Alle `ingest_*.py` so anpassen, dass beim Erzeugen des `source`-Objekts `calendarUrl`
  gesetzt wird – mit der bekannten Kalender-/Übersichts-URL der jeweiligen Quelle, sonst
  `None`. Damit erhalten künftige Läufe echte Kalender-URLs (ADR-005: idempotent).
- Kein erneuter Massenlauf im Rahmen dieser Story erforderlich (Bestand wird über Task 5
  auf `null` gesetzt); echte URLs werden bei der nächsten regulären Aktualisierung je
  Quelle nachgezogen.
- **Deckt ab:** AK 3 (Pflege künftiger `calendarUrl`-Werte).

## Task 7 – Gherkin-Contract ergänzen (veranstaltungsdetail.feature)

- In [veranstaltungsdetail.feature](../../contracts/veranstaltungsdetail.feature) das
  bestehende Quellen-Szenario
  ([veranstaltungsdetail.feature:49-53](../../contracts/veranstaltungsdetail.feature#L49-L53))
  beibehalten und ein Szenario für die optionale Kalender-URL ergänzen, z. B.:
  - Szenario: „Kalenderseite der Quelle wird angezeigt, wenn hinterlegt" – bei gesetzter
    `calendarUrl` erscheint zusätzlich ein Link zur Übersichts-/Kalenderseite.
  - Szenario: „Ohne Kalenderseite kein Kalender-Link" – bei `calendarUrl = null` wird kein
    zusätzlicher Link angezeigt.
- Nur beobachtbares Verhalten formulieren, keine Feldnamen/Implementierung.
- **Deckt ab:** AK 3, 8, 9.

## Task 8 – EARS-Anforderung ergänzen (ears/veranstaltungsdetail.md)

- In [ears/veranstaltungsdetail.md](../../ears/veranstaltungsdetail.md) DET-14
  ([veranstaltungsdetail.md:55-56](../../ears/veranstaltungsdetail.md#L55-L56)) beibehalten
  (Quellenlink mit Name und Abrufdatum) und eine neue Anforderung ergänzen:
  - **DET-17** (optionales Merkmal): SOFERN zur Quelle eine Kalender-/Übersichts-URL
    hinterlegt ist, MUSS die Veranstaltungsdetailseite einen zusätzlichen Verweis auf diese
    Seite anzeigen.
  - Formulierung im Stil der bestehenden DET-Sätze; Verweis auf den Contract beibehalten.
- **Deckt ab:** AK 3, 9.

## Task 9 – Verifikation & Abschluss

- `cd web && npm run build` – kompiliert fehlerfrei (der erweiterte `EventSource`-Typ wird
  über den Daten-Sync gegen die JSON-Daten wirksam).
- JSON-Validierung von [events.json](../../../../data/events.json); Stichprobe: ein Event
  mit und (nach Task 6/Folge-Läufen) ggf. eines mit gesetzter `calendarUrl`.
- `cd web && npm start` und im Browser: Quellenlink (konkrete Veranstaltungsseite) und –
  falls vorhanden – Ticketlink sichtbar; bei `calendarUrl = null` **kein** Kalender-Link.
- Story-Datei nach Abschluss von `inprogress/` nach `done/` verschieben und diese
  Tasks-Datei mitverschieben (Muster wie US-006/007/008).

## Definition of Done

- Akzeptanzkriterien 1–9 der User Story erfüllt.
- Modell ([models.ts](../../../../web/src/app/models/models.ts)), Doku
  ([events-and-relations.md](../../../events-and-relations.md)) und Daten
  ([events.json](../../../../data/events.json)) verwenden `calendarUrl` konsistent
  (`string | null`, in allen `source`-Objekten vorhanden).
- Gherkin- und EARS-Artefakte um die optionale Kalender-URL ergänzt; ADR-Bewertung
  dokumentiert (kein neues ADR).
- `npm run build` ohne Fehler; `events.json` valide; kein `source` ohne `calendarUrl`.
