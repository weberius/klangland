# US-025 – Umsetzungs-Tasks

Umsetzung von [US-025](./us-025-impressum.md): Footer umbauen und vier eigenständige Rechts-/Lizenzseiten (Impressum, Haftungsausschluss, Datenschutz, Quellen/Lizenzen) mit eigenen Routen anlegen.

Betroffene Dateien:
- neu: `web/src/app/pages/impressum/impressum.ts` (+ `.html`)
- neu: `web/src/app/pages/haftungsausschluss/haftungsausschluss.ts` (+ `.html`)
- neu: `web/src/app/pages/datenschutz/datenschutz.ts` (+ `.html`)
- neu: `web/src/app/pages/quellen/quellen.ts` (+ `.html`)
- [web/src/app/app.routes.ts](../../../../web/src/app/app.routes.ts)
- [web/src/app/app.html](../../../../web/src/app/app.html) (Footer)
- [web/src/app/app.css](../../../../web/src/app/app.css) (Footer-Styling)
- ggf. [web/src/styles.css](../../../../web/src/styles.css) (gemeinsame Prosa-Klasse für die Inhaltsseiten)

Inhaltsquellen (redaktionell übernehmen, Markdown → HTML von Hand umsetzen):
- Impressum: [impressumModalLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/impressumModalLi.md)
- Haftungsausschluss: [disclaimerModalLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/disclaimerModalLi.md)
- Datenschutz: [datenschutzLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/datenschutzLi.md)

---

## Task 1 – Vier Inhaltsseiten-Komponenten anlegen

Für jede Seite eine eigenständige (standalone) Komponente nach dem Muster der [not-found-Seite](../../../../web/src/app/pages/not-found/not-found.ts) erstellen: einfache Inhaltsseite mit `.page-header`-Überschrift (`<h1>`) und Fließtext. **Keine** `DataService`-/`PageHeader`-Abhängigkeit nötig (die Seiten sind rein statisch). Inhalt als `templateUrl` (`.html`) pflegen.

Gemeinsame Punkte für alle vier Seiten:
- Überschrift als `<h1>`, Text in gut lesbaren Absätzen/Listen.
- Zurück-Link „‹ Zum Kalender" (`routerLink="/"`) analog zu bestehenden Detailseiten.
- Externe Links mit `target="_blank" rel="noopener"` (AK 9).
- Gemeinsame Prosa-Klasse (z. B. `legal-content`) für Lesebreite/Abstände nutzen (siehe Task 4).

**Task 1a – Impressum (`/impressum`)** (AK 4)
- Inhalt aus `impressumModalLi.md` übernehmen.
- Unterhalb der E-Mail-Zeile zusätzlich einfügen: `Internet: https://wolfram.eberius.photography` (als Link).

**Task 1b – Haftungsausschluss (`/haftungsausschluss`)** (AK 5)
- Inhalt aus `disclaimerModalLi.md` übernehmen.

**Task 1c – Datenschutz (`/datenschutz`)** (AK 6) — an Klangland angepasst
- Basis aus `datenschutzLi.md`, aber inhaltlich auf Klangland zuschneiden. Es müssen mindestens folgende Punkte korrekt beschrieben sein:
  - **Hosting GitHub Pages:** technisch bedingte Verarbeitung von IP-Adressen in Server-Logs durch GitHub (Auftragsverarbeitung, Drittlandbezug USA).
  - **OpenStreetMap-Kartenkacheln:** Auf Karten-/Detailseiten werden Kacheln von `tile.openstreetmap.org` zur Laufzeit geladen; dabei wird die IP an die OpenStreetMap Foundation übertragen. Auf deren Datenschutzhinweise verweisen ([city-map.ts:78](../../../../web/src/app/pages/city-map/city-map.ts#L78), [event-detail.ts:252](../../../../web/src/app/pages/event-detail/event-detail.ts#L252)).
  - **Keine Cookies, kein Tracking/Analytics.**
  - **Keine persistente Speicherung im Browser:** Favoriten liegen nur flüchtig im Arbeitsspeicher und werden ausschließlich über Share-Link-Query-Parameter wiederhergestellt ([favorites.service.ts:10-18](../../../../web/src/app/core/favorites.service.ts#L10-L18)); kein `localStorage`/`sessionStorage`.
- Passagen der Vorlage, die auf Klangland nicht zutreffen (z. B. foto-/projektspezifische Dienste), entfernen.

**Task 1d – Quellen/Lizenzen (`/quellen`)** (AK 7)
- Die bisher im Footer stehende Namensnennung hierher übernehmen: **Open Opus** (Metadaten), **Wikipedia / Wikimedia Commons** (Kurzfassungen und Portraits) inkl. Hinweis auf die **CC-BY-SA**-Lizenz.
- Ergänzen: **OpenStreetMap-Mitwirkende** (Kartendaten/Kacheln) und **Leaflet** (Kartenbibliothek).

## Task 2 – Routen ergänzen (app.routes.ts) (AK 3, AK 8)

- Vier lazy geladene `loadComponent`-Routen ergänzen, jeweils mit `title` im bestehenden Muster:
  - `impressum` → „Impressum · Klangland"
  - `haftungsausschluss` → „Haftungsausschluss · Klangland"
  - `datenschutz` → „Datenschutz · Klangland"
  - `quellen` → „Quellen & Lizenzen · Klangland"
- Die Routen **vor** der Catch-all-Route `{ path: '**' }` einordnen.
- Deep-Link + Reload funktionieren über den bestehenden SPA-404-Fallback (siehe Deploy-Workflow) – keine zusätzliche Konfiguration nötig.

## Task 3 – Footer umbauen (app.html) (AK 1, AK 2)

- Den bisherigen beschreibenden `<p>`-Text und den `.footer-credits`-Block entfernen ([app.html:96-107](../../../../web/src/app/app.html#L96-L107)).
- Stattdessen eine Linkzeile einfügen (z. B. `<nav class="footer-links" aria-label="Rechtliches">`) mit vier `routerLink`-Links:
  - `/impressum` „Impressum"
  - `/haftungsausschluss` „Haftungsausschluss"
  - `/datenschutz` „Datenschutz"
  - `/quellen` „Quellen & Lizenzen"
- Der Footer liegt im App-Shell und erscheint dadurch automatisch auf **jeder** Seite (AK 2).
- Optional (Copyright/Kurzbezeichnung) darf eine schlichte Zeile „Klangland" bleiben; die alte Quellen-/Beschreibungszeile jedoch nicht.

## Task 4 – Styling (app.css / styles.css) (AK 9)

- `.site-footer` anpassen ([app.css:237-247](../../../../web/src/app/app.css#L237-L247)): Linkzeile als horizontale Liste mit Abständen/Trennern, umbruchfähig (mobil), gute Kontraste.
- `:focus-visible` für die Footer-Links sicherstellen (sichtbarer Tastaturfokus).
- Gemeinsame Prosa-Klasse `legal-content` (bevorzugt in [styles.css](../../../../web/src/styles.css)) für die vier Inhaltsseiten: begrenzte Lesebreite, Absatz-/Listenabstände, Link-Styling.

## Task 5 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei.
- `cd web && npm start` und im Browser prüfen:
  - Footer zeigt auf jeder Seite die vier Links; die alte Beschreibungs-/Quellenzeile ist verschwunden (AK 1, AK 2).
  - Jeder Link öffnet die passende Seite unter der erwarteten Route (AK 3).
  - Direktaufruf/Neuladen z. B. von `/klangland/datenschutz` funktioniert (SPA-404-Fallback) (AK 3).
  - Browser-Tab-Titel je Seite korrekt (AK 8).
  - Impressum enthält die Internet-Zeile (AK 4); Datenschutz benennt GitHub Pages, OpenStreetMap-Kacheln und „keine Cookies/keine Speicherung" (AK 6); Quellen-Seite nennt Open Opus, Wikipedia/Wikimedia (CC BY-SA), OpenStreetMap, Leaflet (AK 7).
  - Tastaturbedienung: Footer-Links per Tab erreichbar, Fokus sichtbar; externe Links mit `rel="noopener"` (AK 9).
  - Kalender-, Listen- und Detailseiten unverändert (AK 10).

## Definition of Done

- Alle Akzeptanzkriterien 1–10 der User Story erfüllt.
- `npm run build` ohne Fehler/Warnungen.
- Keine Änderungen an der Datenerhebung/-verarbeitung selbst (reine Footer-/Dokumentationsänderung).
- Story-Datei nach Abschluss von `doing/` nach `done/` verschieben.
