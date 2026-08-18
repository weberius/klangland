# Bielefelder Philharmoniker – Ingest 2026/27

Quelle: [Kalender der Bielefelder Philharmoniker](https://www.buo-bielefeld.de/philharmoniker/kalender)
(TYPO3, `tx_uibuoproductions_calendar`, „Mehr laden"-Paging) + Detailseiten
`https://www.buo-bielefeld.de/<venue>/veranstaltung/<slug>`.

Skript: [`ingest_bielefeld.py`](ingest_bielefeld.py)

## Quelle / Technik

- Der **Kalender** ist server-gerendert; jeder Eintrag (`data-calender-result-item`) enthält
  Datum, Uhrzeit, **Ort**, Sparte (Badge), Detail-Link und **Ticket-URL** (Eventim-Inhouse,
  `theater-bielefeld.eventim-inhouse.de/webshop/…?event=<id>`). Paginiert wird durch Folgen
  des „Mehr laden"-Links (trägt den jeweils gültigen TYPO3-`cHash`).
- **Detailseiten** liefern die **Besetzung** über die `/person/`-Links im Abschnitt
  „Auf der Bühne" (Format „Name rolle"). Das **Programm** steht – uneinheitlich – im
  `<meta itemprop="description">` (Format „Komponist (Lebensdaten)Werk", zeilenweise). Wo das
  fehlt, wird das Programm aus „Komponist – Werk"-Titeln abgeleitet (nur wenn der Nachname auf
  eine:n bekannte:n Komponist:in im Bestand auflösbar ist).

## Umfang

Nur **Orchesterkonzerte** in Bielefeld (Detailpfad `/philharmoniker/` oder
`/rudolf-oetker-halle/`), Saison 12.09.2026–05.07.2027: Symphonie-, Kammer-, Sonder-,
Kinder- und Familienkonzerte („Klassik um 3", „Klassik-Lounge", „BiPhil After Work" u. a.).

Ergebnis: **71 Aufführungen**. **39** haben einen Ticketlink (die übrigen sind quellseitig
ticketlos, u. a. Schul-/Matineetermine). **32** haben ein strukturiertes Werkprogramm
(Meta-Description bzw. Titel-Ableitung).

### Ausgeschlossen: szenische Produktionen

Oper/Ballett/Musiktheater (Detailpfad `/theater/`, z. B. Tosca, Die Zauberflöte,
Der Troubadour, The Birds of Alfred Hitchcock, Ein Sommernachtstraum, Milk Teeth) werden
ausgelassen – wie bei den anderen Orchestern beschränkt sich der Bestand auf Konzerte.

## Spielstätten

Neu angelegt: `rudolf-oetker-halle-bielefeld` (Haupt-Konzerthaus, Großer/Kleiner Saal/Foyer),
`stadttheater-buehne-bielefeld`, `assapheum-bethel-bielefeld`, `universitaet-bielefeld`,
`zionskirche-bethel-bielefeld` sowie `bielefeld-umgebung` (Fallback für 1 Termin ohne
ausgewiesenen Ort). Das bestehende `stadthalle-bielefeld` erscheint in dieser Saison nicht.

## Programm-Normalisierung

Das Programm wird in `program[].workId` überführt (`works.json`/`composers.json` ergänzt),
damit es auf der Event-Seite dargestellt wird. Genre heuristisch aus dem Titel; Katalog­nummern
(op./KV/BWV/WoO/Hob/D) werden geparst; `yearComposed`/`life`/`durationMinutes` bleiben `null`.
Werke werden über (Komponist + normalisierter Titel) dedupliziert und mit dem Bestand
wiederverwendet.

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `buo-bielefeld.de` und Ensemble
`bielefelder-philharmoniker` entfernt und neu angelegt; Stammdaten werden nur ergänzt, wenn
ID/Schlüssel fehlen.

## Offene Punkte / Grenzen

- **Programm-Abdeckung (32/71):** Bei vielen Konzerten (Kammer-, Kinder-, „Klassik um 3"-,
  After-Work-Formate) wird die Werkliste erst per JavaScript nachgeladen und ist im statischen
  HTML nicht enthalten; dort bleibt `program` leer. Symphoniekonzerte und „Komponist – Werk"-
  Programme sind erfasst. Eine vollständige Erfassung erforderte einen Headless-Browser.
- `genre` ist heuristisch; `yearComposed`/`life` sind `null` – spätere Anreicherung möglich.
- Programm-/Besetzungserkennung ist heuristisch; Stichproben-Abgleich empfohlen.
