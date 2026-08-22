# User Story 025 - Impressum, Haftungsausschluss und Datenschutz

## User Story

**Als** Betreiber von Klangland,
**möchte ich** die rechtlich erforderlichen Angaben (Impressum, Haftungsausschluss, Datenschutz) sowie die Quellen-/Lizenznachweise auf eigenen, dauerhaft erreichbaren Seiten bereitstellen,
**damit** die gesetzlichen Pflichten (Impressumspflicht, DSGVO, Lizenzbedingungen der genutzten Inhalte) erfüllt sind und Besucher:innen diese Angaben von jeder Seite aus leicht finden.

## Kontext / Problem

Der Footer zeigt aktuell einen beschreibenden Fließtext samt Quellen-/Namensnennung ([app.html:96-107](../../../../web/src/app/app.html#L96-L107)):

> „Klangland – Konzertkalender für Nordrhein-Westfalen. Statische App, Daten aus versionierten JSON-Dateien. Komponist:innen- und Werk-Metadaten von Open Opus; Kurzfassungen und Portraits aus Wikipedia / Wikimedia Commons."

Damit fehlen der Anwendung die **rechtlich verpflichtenden Seiten** Impressum und Datenschutz vollständig; ein Haftungsausschluss existiert ebenfalls nicht. Gleichzeitig ist die vorhandene Namensnennung lizenzrechtlich relevant (u. a. CC BY-SA für Wikipedia-/Wikimedia-Inhalte) und darf nicht ersatzlos entfallen.

Datenschutzrechtlich sind für die – ansonsten statische – App insbesondere zu berücksichtigen:

- **Hosting auf GitHub Pages:** Server-Logs verarbeiten technisch bedingt IP-Adressen (Auftrag/Drittland USA).
- **Kartenkacheln von OpenStreetMap:** Auf der Karten- und der Veranstaltungs-Detailseite werden Kacheln von `tile.openstreetmap.org` **zur Laufzeit** nachgeladen; dabei wird die IP-Adresse an einen Dritten übertragen ([city-map.ts:78](../../../../web/src/app/pages/city-map/city-map.ts#L78), [event-detail.ts:252](../../../../web/src/app/pages/event-detail/event-detail.ts#L252)).
- **Keine Cookies, kein Tracking, keine persistente Client-Speicherung:** Favoriten liegen ausschließlich flüchtig im Arbeitsspeicher und werden nur über Share-Link-Query-Parameter wiederhergestellt ([favorites.service.ts:10-18](../../../../web/src/app/core/favorites.service.ts#L10-L18)); es werden weder `localStorage`/`sessionStorage` noch Analyse-Dienste genutzt.

Betroffen sind der Footer sowie das Routing ([app.routes.ts](../../../../web/src/app/app.routes.ts)). Die inhaltlichen Ansichten (Kalender, Ensembles, Werke usw.) bleiben unverändert.

## Gewählte Lösung

Der beschreibende Footertext wird entfernt und durch eine kompakte **Linkzeile** ersetzt. Verlinkt werden vier eigenständige Seiten mit je eigener Route:

1. **Impressum** (`/impressum`)
2. **Haftungsausschluss** (`/haftungsausschluss`)
3. **Datenschutz** (`/datenschutz`)
4. **Quellen/Lizenzen** (`/quellen`)

Inhalte:

- **Impressum** wird aus der bestehenden Vorlage übernommen (`fotopfade`: [impressumModalLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/impressumModalLi.md)) und um eine Zeile **„Internet: https://wolfram.eberius.photography"** unterhalb der E-Mail-Adresse ergänzt.
- **Haftungsausschluss** wird aus der Vorlage übernommen (`fotopfade`: [disclaimerModalLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/disclaimerModalLi.md)).
- **Datenschutz** basiert auf der Vorlage (`fotopfade`: [datenschutzLi.md](https://github.com/weberius/fotopfade/blob/main/locales/koeln-muelheim/de/datenschutzLi.md)), wird aber an Klangland **angepasst**: GitHub Pages als Hoster (IP in Server-Logs), OpenStreetMap-Kacheln als Drittanbieter, ausdrücklicher Hinweis, dass keine Cookies, kein Tracking und keine persistente Speicherung im Browser stattfinden (Favoriten nur flüchtig/über Share-Link).
- **Quellen/Lizenzen** nimmt die bisher im Footer stehende Namensnennung auf (Open Opus; Wikipedia / Wikimedia Commons inkl. CC-BY-SA-Hinweis für Kurzfassungen und Portraits) und ergänzt die weiteren Fremdbestandteile (OpenStreetMap-Mitwirkende, Kartenbibliothek Leaflet).

Die Seiten sind statische Inhaltsseiten im bestehenden Seiten-/Routing-Muster (lazy geladene Standalone-Komponenten). Die vier Links erscheinen im Footer auf **jeder** Seite.

## Akzeptanzkriterien

1. **Alter Footertext entfernt:** Der bisherige beschreibende Fließtext und die Quellen-Nennung stehen nicht mehr im Footer.
2. **Footer-Links:** Der Footer zeigt auf jeder Seite die vier Links „Impressum", „Haftungsausschluss", „Datenschutz" und „Quellen/Lizenzen".
3. **Eigene Routen:** Jeder Link führt auf eine eigene Seite mit eigener Route (`/impressum`, `/haftungsausschluss`, `/datenschutz`, `/quellen`). Direktaufruf per Deep-Link und Neuladen der Seite funktionieren (SPA-404-Fallback vorhanden).
4. **Impressum-Inhalt:** Die Impressumsseite enthält die aus der Vorlage übernommenen Angaben sowie zusätzlich die Zeile „Internet: https://wolfram.eberius.photography" unterhalb der E-Mail-Adresse.
5. **Haftungsausschluss-Inhalt:** Die Seite gibt den Text der Vorlage wieder.
6. **Datenschutz-Inhalt (angepasst):** Die Datenschutzseite benennt korrekt (a) GitHub Pages als Hoster und die Verarbeitung von IP-Adressen in Server-Logs, (b) das Nachladen von OpenStreetMap-Kartenkacheln als Drittanbieter mit IP-Übertragung und (c) dass keine Cookies, kein Tracking/Analytics und keine persistente Speicherung im Browser erfolgen (Favoriten nur flüchtig bzw. über Share-Link).
7. **Quellen/Lizenzen-Inhalt:** Die Seite nennt Open Opus sowie Wikipedia/Wikimedia Commons (mit CC-BY-SA-Hinweis) und zusätzlich OpenStreetMap-Mitwirkende und Leaflet.
8. **Seitentitel:** Jede der vier Seiten setzt einen passenden Browser-Titel im bestehenden Muster (z. B. „Impressum · Klangland").
9. **Barrierefreiheit:** Die Footer-Links sind echte, per Tastatur erreichbare Links mit sichtbarem Fokus; externe Links öffnen mit `rel="noopener"`.
10. **Unveränderte Bereiche:** Kalender-, Listen- und Detailseiten sowie die Datenerhebung/-verarbeitung selbst bleiben funktional und technisch unverändert (reine Dokumentations-/Footer-Änderung).

## Out of Scope

- Cookie-Banner bzw. Consent-Management (nicht erforderlich, da keine Cookies/kein Tracking).
- Mehrsprachigkeit der Rechtstexte (nur Deutsch).
- Aufnahme der vier Seiten in die Hauptnavigation/das Menü (bewusst nur im Footer).
- Änderung der tatsächlichen Datenverarbeitung (z. B. Self-Hosting der Kartenkacheln zur Vermeidung der IP-Übertragung) – hier wird der Ist-Zustand dokumentiert, nicht verändert.
- Juristische Endabnahme der Texte (redaktionelle Übernahme der Vorlagen, keine Rechtsberatung).
