# US-014 – Umsetzungs-Tasks

Umsetzung von [US-014](./US-014-ensemble-wikipedia.md): Kuratierte Wikipedia-Kurzfassung, Attributierung und Link zum Artikel auf der Ensemble-Detailseite.

Betroffene Dateien:
- [data/ensembles.json](../../../../data/ensembles.json) (Datenquelle; wird per `tools/sync-data.mjs` nach `web/public/data` synchronisiert)
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts)
- [web/src/app/pages/ensemble-detail/ensemble-detail.html](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html)
- [web/src/app/pages/ensemble-detail/ensemble-detail.css](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.css)
- ggf. [web/src/app/pages/ensemble-detail/ensemble-detail.ts](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.ts)

---

## Task 1 – Datenmodell erweitern (models.ts)

Bezug: AK 1.

- Im [`Ensemble`-Interface](../../../../web/src/app/models/models.ts#L89-L104) ein optionales, gruppiertes Feld für die Wikipedia-Angaben ergänzen – analog zum bestehenden `source`-Muster bei Events (zusammengehörige Felder als Objekt):
  ```ts
  wikipedia: { summary: string; url: string } | null;
  ```
  - Objekt-Variante gewählt, damit „Abschnitt nur zeigen, wenn Daten da" per einfacher `ensemble.wikipedia`-Prüfung geht (AK 5).
- Das Feld als `| null` deklarieren, damit Ensembles ohne Artikel valide bleiben. Bestehende Felder unverändert lassen.
- Da die JSON direkt als `Ensemble[]` geladen wird ([data.service.ts:218](../../../../web/src/app/core/data.service.ts#L218)), ist kein Mapper/Parser anzupassen – die Typänderung wirkt allein über das Interface.

## Task 2 – Recherche & Datenpflege (data/ensembles.json)

Bezug: AK 6, AK 2, AK 3, AK 4.

- Für jedes Ensemble in [ensembles.json](../../../../data/ensembles.json) den passenden deutschsprachigen Wikipedia-Artikel recherchieren.
- Wo ein geeigneter Artikel existiert, das Feld pflegen:
  - `summary`: eigenständig formulierte Zusammenfassung von **ca. 60 Wörtern** (kein wörtlicher Auszug, siehe US „Eigene Zusammenfassung").
  - `url`: Voll-URL des Artikels (z. B. `https://de.wikipedia.org/wiki/...`).
- Existiert kein geeigneter Artikel: Feld auf `null` setzen (oder weglassen – konsistent handhaben).
- Feld-Konvention beachten (vgl. [event-modeling-conventions](../../../../home/wolfram/.claude/projects/-home-wolfram-workspaces-klangland/memory/event-modeling-conventions.md), sofern für Ensembles einschlägig): einheitliche Reihenfolge/Position des neuen Feldes im Objekt.
- `metadata.version` / `metadata.lastUpdated` in [ensembles.json](../../../../data/ensembles.json) hochziehen.
- Hinweis: Änderungen in `data/ensembles.json` vornehmen (nicht in `web/public/data/...`); der Sync läuft automatisch bei `prebuild`/`prestart`.

## Task 3 – Wikipedia-Abschnitt darstellen (ensemble-detail.html)

Bezug: AK 2, AK 3, AK 4, AK 5, AK 7 (bestehende Inhalte), AK 8.

- Neuen `<section>`-Abschnitt in der Detailseite ergänzen (z. B. innerhalb `.profile-main` unter der Beschreibung/Tags oder als eigener Abschnitt über den Veranstaltungen – konsistent zur bestehenden Struktur [ensemble-detail.html:13-56](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L13-L56)).
- Den gesamten Abschnitt mit `@if (ensemble()!.wikipedia; as wiki) { ... }` umschließen → **Ausblenden bei fehlenden Daten (AK 5)**.
- Inhalt:
  - Überschrift, z. B. `<h2>Über das Ensemble</h2>` bzw. „Aus der Wikipedia" (semantische Auszeichnung, AK 8).
  - Kurzfassung: `<p>{{ wiki.summary }}</p>` (AK 2).
  - Attributierung (AK 3): kleiner Hinweistext, der die Wikipedia als Grundlage nennt und auf den Artikel verlinkt, z. B.
    „Zusammenfassung auf Basis des <a>Wikipedia-Artikels</a> (CC BY-SA)".
  - Link zum vollständigen Artikel (AK 4): `<a [href]="wiki.url" target="_blank" rel="noopener">Zum vollständigen Artikel</a>` – analog zum bestehenden Website-Link [ensemble-detail.html:47](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html#L47).
- Bestehende Bereiche (Beschreibung, Tags, Fakten, Website, Veranstaltungen) unverändert lassen (AK 7).

## Task 4 – Styling (ensemble-detail.css)

Bezug: AK 8, optische Integration.

- Für den neuen Abschnitt Klassen ergänzen und am bestehenden Stil ausrichten (Abstände wie `.events-section`/`.lead`).
- Attributierungs-/Quellen-Zeile dezent gestalten (`color: var(--color-text-muted)`, kleinere Schrift – vgl. `.profile-facts dt`/`.muted`).
- Sicherstellen, dass Links einen sichtbaren Fokus-/Hover-Zustand haben (Konsistenz mit übrigen Links).

## Task 5 – Optional: Aufbereitung in ensemble-detail.ts

Nur falls im Template Logik nötig wird (z. B. abgeleitetes Signal). In der Regel reicht der direkte Zugriff über `ensemble()!.wikipedia` im Template; dann entfällt dieser Task. Kein zusätzliches `computed` einführen, wenn es keinen Mehrwert bietet.

## Task 6 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei (Typänderung + Template).
- `cd web && npm start` und im Browser prüfen:
  - Ensemble **mit** gepflegten Wikipedia-Daten: Abschnitt erscheint mit Kurzfassung (~60 Wörter), Attributierung und funktionierendem Artikel-Link (öffnet neuen Tab) (AK 2–4).
  - Ensemble **ohne** Wikipedia-Daten: Abschnitt fehlt vollständig, restliche Seite unverändert (AK 5, AK 7).
  - Tastaturbedienung: Artikel-Link per Tab erreichbar, Fokus sichtbar, Linktext aussagekräftig (AK 8).
  - Mobile Ansicht (schmales Fenster): Layout des neuen Abschnitts bleibt intakt.
- Stichprobe der Datenpflege: mehrere Einträge in [ensembles.json](../../../../data/ensembles.json) auf ~60 Wörter und gültige URLs prüfen (AK 6).

## Definition of Done

- Alle Akzeptanzkriterien 1–8 aus [US-014](./US-014-ensemble-wikipedia.md) erfüllt.
- `npm run build` ohne Fehler/Warnungen; `data/ensembles.json` valides JSON.
- Keine Änderungen an anderen Seiten oder bestehenden Feldern des Ensemble-Modells.
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben.
