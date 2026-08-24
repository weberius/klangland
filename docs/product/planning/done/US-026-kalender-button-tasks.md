# US-026 – Umsetzungs-Tasks

Umsetzung von [US-026](./US-026-kalender-button-klarheit.md): Der Button auf der
Event-Detailseite muss unmissverständlich klarstellen, dass er einen Termin in den
**nativen Gerätekalender** exportiert (nicht den Klangland-eigenen Kalender). Rein
inhaltliche/textliche Änderung – die bestehende `.ics`-Export-Funktion
([ics.ts](../../../../web/src/app/core/ics.ts)) bleibt unverändert.

## Architektur-Entscheidung (verbindlich)

- Keine funktionale Änderung, nur Label/Hinweistext auf der Event-Detailseite.
- Neue Beschriftung: **„Termin in Geräte-Kalender speichern"** (ersetzt „In den Kalender
  eintragen").
- Ergänzendes `title`-Attribut (Tooltip) sowie `aria-label` am Button erläutern die
  Wirkung genauer, z. B.: „Lädt eine Kalenderdatei (.ics) herunter, um diesen Termin in
  den Kalender Ihres Smartphones oder Rechners zu übernehmen."
- Der Klangland-eigene Kalender (Route `/calendar`) und dessen Navigation/Wortlaut bleiben
  unangetastet.

Betroffene Dateien:

- [web/src/app/pages/event-detail/event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html#L23) (Button-Text, Zeile 23)
- [web/src/app/pages/event-detail/event-detail.css](../../../../web/src/app/pages/event-detail/event-detail.css) (nur falls Zeilenumbruch/Breite angepasst werden muss)

---

## Task 1 – Button-Beschriftung und Hinweistext anpassen

- In [event-detail.html:23](../../../../web/src/app/pages/event-detail/event-detail.html#L23)
  den Button-Text von „In den Kalender eintragen" auf „Termin in Geräte-Kalender
  speichern" ändern.
- `title`- und `aria-label`-Attribut mit dem oben festgelegten Erläuterungstext ergänzen.
- Prüfen, ob der längere Text im `event-actions`-Zeilenlayout (Desktop und Mobile) noch
  sauber umbricht; bei Bedarf `event-detail.css` anpassen (z. B. `white-space`/`flex-wrap`).
- **Deckt ab:** AK 1, AK 2, AK 3.

## Task 2 – Manuelle Verifikation

- `cd web && npm run build` – Build ohne Fehler.
- `cd web && npm start` und im Browser prüfen:
  - Auf einer beliebigen `events/:id`-Seite ist der neue Button-Text lesbar und
    verständlich, ohne den Klangland-Kalender zu erwähnen (AK 1).
  - Tooltip (Hover) bzw. Screenreader-Ansage (`aria-label`) erläutert den Export in den
    Gerätekalender (AK 2).
  - Der `.ics`-Download funktioniert unverändert wie vor der Änderung (AK 3).
  - Die Kalenderseite (`/calendar`) und ihre Beschriftungen sind unverändert (AK 4).

## Definition of Done

- Akzeptanzkriterien 1–4 aus [US-026](./US-026-kalender-button-klarheit.md) erfüllt.
- Keine Änderung an der `.ics`-Exportlogik oder am Klangland-eigenen Kalender.
- Build erfolgreich; Wortlaut manuell im Browser geprüft.
