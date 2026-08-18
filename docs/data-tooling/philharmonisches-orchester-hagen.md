# Philharmonisches Orchester Hagen – Ingest 2026/27

Quelle: [Kalender / Alle Termine](https://www.theaterhagen.de/kalender/alle-termine/) (TYPO3)
+ Detailseiten `https://www.theaterhagen.de/veranstaltung/<slug>/<uid>/show/Play/`.

Skript: [`ingest_hagen.py`](ingest_hagen.py)

## Quelle / Technik

- Der Kalender wird **monatsweise** geladen (Monats-Links `tx_theatre_kalender[month]=<ts>`
  mit cHash; die Saison 2026/27 = Aug 2026 – Jul 2027).
- Jeder `event-item` liefert Datum/Uhrzeit, Titel/Untertitel, **Ort** (`event-time`:
  `<b>Name</b><small>, Adresse, PLZ Ort</small>`) und ggf. Ticket-Link.
- Die **Detailseiten** liefern das **Programm** (`div.play-intro`:
  `<strong>Komponist</strong><br>Werk`), die **Besetzung** (`ul.actors`: role/actor) und die
  **Termin-Ticketliste** (`Vorstellungen / Termine` → je Termin ein Eventim-Link
  `theaterhagen.eventim-inhouse.de/webshop/…?event=<id>`, gemappt nach Datum).

## Umfang / Ortsprüfung

Der Theater-Hagen-Kalender enthält Oper, Schauspiel, Tanz, Kinder (LUTZ) **und** Konzerte.
Aufgenommen werden nur **Konzertformate des Orchesters** (Titel enthält „…konzert":
Sinfonie-, Kammer-, Familien-, Krabbel-, Advents-, Neujahrs-, Mitsingkonzert usw.).

**Orte werden je Termin aus der Adresse gelesen.** Nur Konzerte in **Hagen** werden
aufgenommen; Gastspiele außerhalb (z. B. das 7. Sinfoniekonzert am 13.05.2027 in der
**Kölner Philharmonie**, „Orchester unterwegs" im Parktheater Iserlohn) werden ausgelassen und
**nicht** fälschlich Hagen zugeordnet. Unbekannte Orte werden nur angelegt, wenn die Stadt
eindeutig Hagen ist – leere/andere Städte führen zum Ausschluss.

Ergebnis: **36 Aufführungen** (06.09.2026–11.07.2027). **27** haben einen Ticketlink; **9**
ein strukturiertes Werkprogramm (die Sinfoniekonzerte; Kammer-/Familien-/Krabbelkonzerte
listen quellseitig kein Werkprogramm auf ihren Detailseiten).

## Spielstätten (alle in Hagen)

`theater-hagen` (Großes Haus, bestehend) wird wiederverwendet; neu: `stadthalle-hagen`,
`kunstquartier-hagen`, `lutz-hagen` (Lutz Theater), `theatercafe-hagen`, `johanniskirche-hagen`.

## Programm-Normalisierung

Programm → `program[].workId` (`works.json`/`composers.json` ergänzt; Genre heuristisch;
Katalognummern op./KV/BWV/WoO/Hob/D geparst; `yearComposed`/`life`/`durationMinutes` `null`).
Werke werden über (Komponist + normalisierter Titel) dedupliziert. Ein Markup-Glitch der
Quelle (Zeichen hinter `</strong>`, z. B. „Detlev Glaner</strong>t") wird korrekt dem
Komponistennamen zugeschlagen („Detlev Glanert"). Besetzung (Dirigent:in/Solist:innen) wird
aus `ul.actors` gelesen, sofern vorhanden.

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `theaterhagen.de` und Ensemble
`philharmonisches-orchester-hagen` entfernt und neu angelegt; Stammdaten werden nur ergänzt.

## Offene Punkte / Grenzen

- Programm-Abdeckung 9/36: nur die Sinfoniekonzerte führen eine Werkliste; Kammer-/Familien-/
  Krabbelkonzerte haben quellseitig kein `play-intro`-Programm.
- Auswärts-/Gastspiele (Orte außerhalb Hagens) sind nicht enthalten.
- `genre` ist heuristisch; `yearComposed`/`life` sind `null`.
