# Daten-Ingest: Philharmonie Südwestfalen (Spielzeit 2026/27)

Dieses Dokument beschreibt, wie der Spielplan der **Philharmonie Südwestfalen** für die
Spielzeit 2026/27 recherchiert und in die versionierten JSON-Dateien unter
[`data/`](../../data) übernommen wurde. Skript daneben:
[`ingest_philsw.py`](ingest_philsw.py).

Siehe auch das übergreifende Datenmodell in [`data-model.md`](../data-model.md) und die
Event-Regeln in [`events-and-relations.md`](../events-and-relations.md).

## Quelle

- **Website:** `https://www.philsw.de/` — die dortige Kalender-/Terminseite ist zum
  Erfassungszeitpunkt **nicht durchgängig gepflegt** und wurde deshalb nicht als
  Datenquelle verwendet.
- **Primärquelle:** das **Spielzeitbuch 2026/27** als PDF —
  `https://www.philsw.de/wp-content/uploads/2026/07/PhilSW-Spielzeitbuch-2026-27.pdf`
  (100 Seiten, Adobe-InDesign-Satz). Es ist vollständiger und aktueller als die
  Website und wurde als **primäre, autoritative Quelle** direkt ausgewertet.
- Da es keine Einzel-Veranstaltungsseiten gibt, verweist `source.url` bei **jedem**
  Event auf das PDF selbst (nicht auf eine Detailseite); `source.calendarUrl` verweist
  auf `https://www.philsw.de/`.

Anders als bei den bisherigen Quellen ([`docs/data-tooling/README.md`](README.md))
handelt es sich hier nicht um eine HTML-/API-Quelle, sondern um ein **PDF-Dokument**.
Die Extraktion erfolgte mit `pdftotext -layout` (Poppler) und anschließender manueller
Kuratierung der Konzert-, Programm- und Besetzungsangaben (Option B, angereichert) —
ein automatisiertes Parsing des zweispaltigen, grafisch verschachtelten Layouts wäre
fehleranfällig gewesen.

## Datenfluss

```text
PhilSW-Spielzeitbuch 2026/27 (PDF)
          ↓  pdftotext -layout (Poppler)
Rohtext je Doppelseite
          ↓  manuelle Kuratierung: Konzerte, Termine, Programm, Besetzung
Zwischenrepräsentation (PRODUCTIONS in ingest_philsw.py)
          ↓  NRW-Filter + Ausschluss geschlossener Veranstaltungen
data/events.json (+ people/works/composers/venues/cities)
          ↓
Validierung (referenzielle Integrität, IDs, Formate)
          ↓
fetch_venue_addresses.py (OpenStreetMap-Recherche neuer Spielstätten)
```

## Umfang: Nordrhein-Westfalen-Filter

Das Spielzeitbuch enthält auch Gastspiele außerhalb NRWs. Konsistent mit dem
Projekt-Scope („Konzertveranstaltungen in Nordrhein-Westfalen", siehe
[`README.md`](../../README.md)) und dem Präzedenzfall in
[`philharmonisches-orchester-hagen.md`](philharmonisches-orchester-hagen.md)
(Gastspiele außerhalb der Stadt/Region werden ausgeschlossen statt fälschlich
zugeordnet) wurden **nur Aufführungen in Nordrhein-Westfalen** übernommen. Folgende
Orte wurden per Nominatim-Abgleich als **nicht NRW** identifiziert und ausgeschlossen:

| Ort | Bundesland/Land |
| --- | --- |
| Betzdorf | Rheinland-Pfalz |
| Wirges | Rheinland-Pfalz |
| Höhn | Rheinland-Pfalz |
| Wolfsburg | Niedersachsen |
| München | Bayern |
| Dillenburg | Hessen |
| Amsterdam | Niederlande |

Produktionen, die **ausschließlich** außerhalb NRWs stattfinden (z. B. das
Sinfoniekonzert am 17.10.2026 in Wolfsburg oder das Neujahrskonzert in München),
entfallen dadurch vollständig; bei Produktionen mit gemischten Terminen (z. B.
„Last Night of the Proms" oder „Christmas Classics at the Movies") wurde nur der
jeweilige Auswärtstermin ausgelassen, die NRW-Termine blieben erhalten.

### Ausgeschlossen: geschlossene Veranstaltungen

Analog zum Präzedenzfall in [`bochumer-symphoniker.md`](bochumer-symphoniker.md)
(reine Schulkonzert-Termine ohne öffentlichen Verkauf) wurden folgende, im
Spielzeitbuch explizit als geschlossen ausgewiesene Formate **nicht** aufgenommen:

- „Konzerte für Entdecker – Kitakonzerte" (29./30.09.2026, „Anmeldung nur für Kitas")
- alle „Musikpädagogisches Projekt – Schulkonzerte" (März/Mai 2027, jeweils
  „geschlossene Veranstaltung")

„Baby-Konzerte", „Teddybär-Konzerte" und „PhilVibes" sind dagegen öffentlich buchbare
Familienformate (eigene Legenden-Kategorie im Spielzeitbuch, nicht als „KIDS:
geschlossen" markiert) und wurden aufgenommen.

### Bekannte Einschränkung: KulturPur35 ohne festes Datum

„KulturPur35" (Konzert auf dem Giller, Hilchenbach-Lützel) ist im Spielzeitbuch nur mit
„13.–17. Mai 2027 (genaues Datum N.N.)" angegeben. Da kein gültiges Einzeldatum vorliegt
(Pflichtfeld `date`), wurde dieser Termin **nicht** aufgenommen.

## Umfang und Tiefe

- **Umfang:** 45 Produktionen mit 90 Aufführungsterminen in NRW (Sinfonie-, Kammer-,
  Familien- und Chorkonzerte, „Last Night of the Proms", Filmmusik-Galas,
  Neujahrskonzerte u. a.), Spielzeit 2026/27 (29.08.2026–10.07.2027).
- **Stammdaten-Tiefe (Option B, angereichert):** Werke/Komponist:innen mit Lebensdaten,
  Kompositionsjahr, Genre, Katalognummern (op./KV/BWV/WWV/D/Hob./TWV/VB/SC), soweit im
  Spielzeitbuch angegeben. Bestehende Werke wurden wiederverwendet, wo sie schon in
  `works.json` existieren (u. a. Beethovens 8. Sinfonie, Mendelssohns
  „Reformationssinfonie", Schuberts Forellenquintett und Streichtrio D 581, Prokofjews
  „Peter und der Wolf").
- **Bewusst nicht strukturiert:** Konzerte mit nur vager Programmansage („Werke von
  E. Kálmán, J. Brahms, V. Monti, P. de Sarasate u. a.", „Last Night of the Proms" ohne
  gedruckte Werkliste, Filmmusik-Galas) erhalten **kein** `program`, stattdessen einen
  Hinweistext in `description` (füllt die sonst leere Programm-Box in der UI, siehe
  auch das gleiche Muster bei [`ingest_guerzenich.py`](ingest_guerzenich.py) /
  `DESC_NOTES`). Ein mehrsätziges Opern-Arien-Medley (Dirigierkurs-Konzert am
  06.09.2026) wurde nur in seinen klar abgrenzbaren Orchesterwerken strukturiert
  erfasst; die zahlreichen Arien/Duette mit noch unbenannten Solist:innen (N.N.)
  wurden **nicht** einzeln als Werke angelegt, sondern in der Beschreibung
  zusammengefasst, um keine Datensätze für unbesetzte Kurzausschnitte zu erzeugen.

## Mapping-Regeln

### Spielstätten (`venueId`)

33 neue Spielstätten wurden angelegt (`type` überwiegend `other` für Kirchen/Mehrzweck-
hallen/Freiluftorte, `theatre` für Theater, `concert_hall` für das „Haus der Musik"
Siegen). Vier Spielstätten wurden aus dem Bestand wiederverwendet: `koelner-philharmonie`,
`beethovenhalle-bonn`, `stadthalle-bielefeld`, `eurogress-aachen`, `konzert-theater-coesfeld`.
Adressen/Koordinaten wurden zunächst auf `null` gesetzt und anschließend mit dem
bestehenden Projektwerkzeug [`fetch_venue_addresses.py`](fetch_venue_addresses.py)
(OpenStreetMap Overpass + Nominatim, US-022) recherchiert.

Auffällig: Die Hauptspielstätte der meisten Konzerte ist laut Spielzeitbuch das
**Apollo-Theater Siegen** (`apollo-theater-siegen`, neu angelegt), nicht die als
`venueId` in [`ensembles.json`](../../data/ensembles.json) hinterlegte
`siegener-stadthalle` („Siegerlandhalle"). Diese Diskrepanz wurde nicht automatisch
aufgelöst (siehe „Bekannte Einschränkungen" unten).

### Orte (`cityId`, `NEW_CITIES`)

18 neue Städte wurden angelegt (u. a. Hilchenbach, Kreuztal, Lüdenscheid, Iserlohn,
Oberhausen, Hamm — jeweils als Minimaldatensatz `id`/`name`/`country`, da keines der
neuen Ensembles dort ansässig ist und daher kein Kfz-Kennzeichen/keine Koordinaten
benötigt werden, siehe Konvention in `cities.json.metadata.notes`). Münster, Coesfeld,
Herne, Lippstadt, Bonn, Bielefeld, Aachen und Köln waren bereits vorhanden und wurden
wiederverwendet.

### Besetzung (Dirigent:innen/Solist:innen → Personen)

Dirigent:innen und Solist:innen werden über [`people.json`](../../data/people.json)
per Name dedupliziert (u. a. `daniel-huppert`, `sandro-hirsch` aus dem Bestand
wiederverwendet). Rollen (Instrument/Stimme) stehen nicht als eigenes Schema-Feld zur
Verfügung und wurden daher in die Event-`description` integriert, wo sie über die
reine Namensnennung hinausgehende Information tragen (z. B. „Sandro Hirsch (Trompete,
Brüder-Busch-Preisträger 2025)"). Chöre (z. B. Oratorienchor Köln, Ev. Kantorei Bad
Lippspringe) werden mangels eigenem Schema-Feld ebenfalls als Text in `description`
geführt — konsistent mit dem bestehenden Muster einzelner WDR-Rundfunkchor-Nennungen
in `events.json`.

### Komponist:innen und Werke

14 neue Komponist:innen wurden angelegt. Acht im Programm vorkommende Komponist:innen
(Anna Clyne, Augusta Holmès, César Franck, Engelbert Humperdinck, Jennifer Higdon,
Johan Halvorsen, Louis Spohr, Ottorino Respighi) waren bereits im Bestand vorhanden
(aus anderen Ensemble-Ingests) und wurden **unverändert wiederverwendet**, ohne ihre
bestehenden Lebensdaten/Wikipedia-Kurzfassungen zu überschreiben.

53 neue Werke wurden angelegt; 16 Werke aus dem Bestand wiederverwendet (siehe
`REUSE_WORKS` in [`ingest_philsw.py`](ingest_philsw.py)).

### Event-Felder

- `eventType`: durchgehend `concert`.
- `id`-Konvention: `event-<YYYY-MM-DD>-<ort>-<titel-slug>`, bei mehreren Terminen am
  selben Tag/Ort um die Uhrzeit ergänzt (z. B. zwei Baby-Konzert-Slots, mehrere
  Vorstellungen von „Drei Haselnüsse für Aschenbrödel" am selben Tag).
- `source.url` = PDF-URL des Spielzeitbuchs (identisch für alle Events, da keine
  Einzel-Veranstaltungsseiten existieren); `ticketUrl` = `null` (im Spielzeitbuch nicht
  ausgewiesen); `status` = `scheduled`.
- `startTime` ist bei einem Event (`Sommerfest im Haus der Musik`, 03.07.2027) `null`,
  weil im Spielzeitbuch nur „N.N. Uhr" angegeben ist — laut Datenmodell zulässig.

## Ausführen

```bash
python docs/data-tooling/ingest_philsw.py
python docs/data-tooling/ingest_philsw.py --date 2026-08-26
```

Es gibt keinen `--raw`-Modus wie bei den HTML-/API-Quellen, da die gesamte
Zwischenrepräsentation (`PRODUCTIONS`, `NEW_WORKS`, `NEW_COMPOSERS`, `NEW_VENUES`,
`NEW_CITIES`) bereits kuratiert im Skript selbst steht (keine Live-Netzabfrage beim
Lauf). Nach dem Ingest empfiehlt sich ein Lauf von
[`fetch_venue_addresses.py`](fetch_venue_addresses.py), um die neu angelegten
Spielstätten zu geokodieren.

### Idempotenz

Der Lauf entfernt zunächst alle zuvor eingespielten PhilSW-Events (erkannt am
Quell-Host `philsw.de` in `source.url`) und legt sie neu an. Stammdaten werden anhand
ihrer IDs zusammengeführt und nicht dupliziert; ein zweiter Lauf ohne Datenänderung
erzeugt exakt dieselben 90 Events und keine neuen Stammdatensätze.

## Validierung

Ergebnis: **90 Events** (45 Produktionen), davon 29 mit strukturiertem Programm; 53
neue Werke, 14 neue Komponist:innen, 47 neue Personen, 33 neue Spielstätten, 18 neue
Städte (19 inkl. Hamm, siehe unten) — 0 Validierungsfehler (eindeutige IDs, gültige
`YYYY-MM-DD`/`HH:MM`-Werte, auflösbare Referenzen auf Ensemble/Venue/City/Person/Werk,
kontrollierte Werte für `eventType`, `status` und `genre`).

## Bekannte Einschränkungen

- **Adressen/Koordinaten** der neuen Spielstätten wurden nach dem Ingest mit
  [`fetch_venue_addresses.py`](fetch_venue_addresses.py) recherchiert; einzelne, in
  OpenStreetMap nicht eindeutig auffindbare Orte (z. B. offene Marktplätze,
  schulische Aulen) bleiben ggf. mit `address`/`coordinates: null` zurück und können
  bei Bedarf manuell nachgepflegt werden.
- **`siegener-stadthalle` vs. `apollo-theater-siegen`:** Das in `ensembles.json` als
  `venueId` hinterlegte Haus wird im Spielzeitbuch 2026/27 nicht bespielt; tatsächliche
  Hauptspielstätte ist das neu angelegte `apollo-theater-siegen`. Eine Korrektur des
  Ensemble-Stammdatensatzes war nicht Teil dieses Ingests.
- **Vage Programmangaben** („Werke von … u. a.", Last-Night-of-the-Proms-Konzerte ohne
  gedruckte Werkliste, Filmmusik-Galas) bleiben ohne `program`; die Ansage steht in
  `description`.
- **Dirigierkurs-Konzert (06.09.2026):** Nur die klar abgrenzbaren Orchesterwerke
  wurden strukturiert erfasst; die begleitenden Opern-Arien/Duette mit noch nicht
  benannten Solist:innen sind nur in der `description` zusammengefasst.
- **Boulangers „D'un matin de printemps":** Das Spielzeitbuch nennt „(1913)"; der
  bestehende Klangland-Datensatz (aus einem früheren Ingest) führt die musikwissen-
  schaftlich gesicherten Kompositionsjahre 1917/1918. Der bestehende, geprüfte Wert
  wurde beibehalten (vgl. das Verfahren bei Open-Opus-Abweichungen in
  [`README.md`](README.md#bekannte-lebensdaten-abweichungen-open-opus--klangland)).
- **KulturPur35** (13.–17.05.2027) ist mangels festen Datums nicht enthalten.
