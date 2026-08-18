# ADR-001: Statische Webapp ohne Backend

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist die Auslieferungsarchitektur für den NRW-Orchester-Kalender.
Der Kern des Produkts ist eine kuratierte, sich langsam ändernde Konzertübersicht – nicht
ein transaktionales System. Bewertet wird, welche Architektur diesen Charakter am besten
trägt.

**Specifics:**

- **Betriebsaufwand:** möglichst kein Server, keine Datenbank, keine Laufzeit-Infrastruktur.
- **Kosten:** Hosting soll dauerhaft günstig bis kostenlos sein.
- **Performance:** schnelle Erstanzeige, kein Server-Request pro Kalenderzelle
  (PRD §29).
- **Reproduzierbarkeit:** ein Commit ⇒ ein deterministisch baubarer, deploybarer Stand.
- **Datenhoheit:** die App enthält **keine** Logik zur Datenbeschaffung (PRD §34).
- **Sicherheit:** minimale Angriffsfläche (keine Nutzerkonten, keine Schreibpfade, PRD §3).

## Candidates to consider

**Summary:** Die Kandidaten ergeben sich aus dem Spektrum „vollständig serverlos" bis
„klassisches Backend". Ausschlaggebend ist, dass alle Inhalte aus einer versionierten
Datei stammen und sich selten ändern.

1. **Statische Webapp** (SPA), Daten als statische JSON-Assets, kein Backend.
2. **Backend + Datenbank** (z. B. Node/Python-API mit PostgreSQL).
3. **Headless CMS / BaaS** (z. B. Contentful, Firebase) als Datenquelle.
4. **Server-Side Rendering mit Live-Datenquelle** (z. B. Next.js gegen Veranstalter-APIs).

## Research and analysis of each candidate

**Statische Webapp**

- Erfüllt Kriterien: kein Betrieb, kostenloses Hosting, sehr gute Performance (JSON einmal
  laden, dann im Browser filtern), voll reproduzierbar über Git, minimale Angriffsfläche.
- Cost: nur Buildzeit; Hosting auf GitHub Pages / Netlify / Vercel / Cloudflare Pages
  kostenlos.
- SWOT: **S** einfach, schnell, versionierbar, offline sicherbar. **W** keine
  Live-Daten, jede Änderung erfordert Deploy. **O** trivial cachebar/CDN-fähig. **T** bei
  sehr großen Datenmengen wachsende Initial-Payload.

**Backend + Datenbank**

- Verfehlt „kein Betrieb" und „günstig": Server + DB müssen betrieben, aktualisiert und
  gesichert werden. Für seltene Datenänderungen unverhältnismäßig.
- SWOT: **S** flexible Queries. **W** Betriebslast, Kosten, Angriffsfläche. **T**
  Vendor-/Infra-Ausfälle betreffen die reine Leseanwendung.

**Headless CMS / BaaS**

- Verlagert Betrieb zum Anbieter, verletzt aber Datenhoheit/Reproduzierbarkeit: Daten
  leben außerhalb von Git, Diffs und Review entfallen.
- SWOT: **W** Vendor-Lock-in, laufende Kosten, kein Git-Diff der Inhalte.

**SSR mit Live-Datenquelle**

- Widerspricht Nicht-Zielen (keine Live-Synchronisation, keine automatische Extraktion aus
  Webseiten, PRD §3). Fragile Abhängigkeit von uneinheitlichen Veranstalterquellen zur
  Laufzeit.

**Opinions/feedback:** PRD (§21, §34, §35) und README empfehlen explizit die statische
Variante; Datenpflege ist eine bewusst **getrennte** Offline-Aufgabe (siehe
[ADR-005](ADR-005-idempotente-python-ingest-skripte.md)).

## Recommendation

**Summary:** Statische Webapp ohne Backend.

**Specifics:** Die Angular-App wird als rein statisches Bundle gebaut und ausgeliefert; die
Daten liegen als statische JSON-Assets bei
([ADR-002](ADR-002-json-dateien-als-single-source-of-truth.md)). Die App lädt die Daten
einmalig clientseitig und enthält keinerlei Schreib- oder Beschaffungslogik. Datenänderungen
werden über Git und ein neues Deployment wirksam. Deployment-Ziel bleibt ein beliebiger
statischer Host mit CDN.
