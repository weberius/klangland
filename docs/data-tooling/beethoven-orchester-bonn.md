# Beethoven Orchester Bonn – Ingest 2026/27

Quelle: [Spielplan/Archiv 26-27](https://www.beethoven-orchester.de/archiv/26-27/)
(server-gerendert) + Detailseiten `https://www.beethoven-orchester.de/konzerte/<slug>/`.

Skript: [`ingest_bonn.py`](ingest_bonn.py)

## Quelle / Technik

- Die **Archivseite** enthält alle Konzert-Elemente (`_segment__cpatterns__element`) mit
  Slug (`data-uri_details`), Titel, Datum (`_sdate__YYYYMMDD`), Uhrzeit, **Ort** (Info-Block)
  und **Ticket-URL** (Ticket-Button-Link; Host variiert: `derticketservice`,
  `beethovenfest.de`, Tour-Veranstalter).
- Die **Detailseiten** liefern **Programm** und **Besetzung** im Block
  `_segment__cdetails__infos`. Dieser ist in Absätze gegliedert (durch Leerzeilen getrennt):
  Titel/Reihe · Datum/Ort · Besetzung · Programm · Preise/Hinweise. Die Programm-Gruppe wird
  daran erkannt, dass ihre erste Zeile ein Komponist (Personenname ohne Rolle/Ensemble) ist;
  Werke folgen darunter, mehrere Werke pro Komponist sind möglich, „+" trennt Komponisten.
  Besetzung: `Name → Rolle`, `Name <em>Rolle</em>` oder `Name Rolle`.

## Umfang

Alle **Heimkonzerte in Bonn** der Saison 26/27 (17.06.2026–12.07.2027): Freitags-/Abo-,
Kammer- (Beethoven-Haus, Alter Bundesrat), Familien-/Kinder-, Karnevals-, Chor- und
Sonderkonzerte.

Ergebnis: **58 Aufführungen**. **54** haben einen Ticketlink; **55** ein strukturiertes
Werkprogramm (die 3 ohne: Klavier-Medley „Klavier Pur", Open-Air „Klassik!Picknick" und der
Kinder-Auszug „Ma mère l'oye" – quellseitig ohne Werkliste).

### Ausgeschlossen: auswärtige Tourneen

Konzerte an Spielstätten außerhalb Bonns (Venue/City nicht im Bestand) werden ausgelassen –
u. a. Kurhaus Bad Honnef, Rhein-Mosel-Halle Koblenz, Kulturzentrum Toblach (Italien),
Warschau, Oslo, Kopenhagen, Helsingborg, Elbphilharmonie Hamburg, Concertgebouw Amsterdam.

## Spielstätten

Neu angelegt (Adressen `null`): `beethovenhalle-bonn` (Großer Saal), `beethovenhalle-studio-bonn`
(Studio), `beethoven-haus-bonn`, `alter-bundesrat-bonn`, `kreuzkirche-bonn`, `opernhaus-bonn`,
`kunstrasen-bonn`, `basecamp-bonn`. Das bestehende `world-conference-center-bonn`
(Ausweichspielstätte während der Beethovenhallen-Sanierung) erscheint in dieser Saison nicht.

## Programm-Normalisierung

Das Programm wird in `program[].workId` überführt (`works.json`/`composers.json` ergänzt),
damit es auf der Event-Seite dargestellt wird. Genre heuristisch aus dem Titel (kontrollierte
Werte); Katalognummern (op./KV/BWV/WoO/Hob/D) werden geparst; Jahreszahlen und Scoring-/Notiz-
zeilen (Besetzungsangaben, „Auszüge aus", Uraufführung …) werden übersprungen. `yearComposed`,
Komponisten-`life` und `durationMinutes` bleiben `null`. Werke werden über (Komponist +
normalisierter Titel) dedupliziert und mit dem Bestand wiederverwendet.

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `beethoven-orchester.de` und Ensemble
`beethoven-orchester-bonn` entfernt und neu angelegt; Stammdaten werden nur ergänzt, wenn
ID/Schlüssel fehlen.

## Offene Punkte / Grenzen

- Kinder-/Medley-/Open-Air-Formate ohne Werkliste bleiben ohne `program`.
- `genre` ist heuristisch (z. B. „Missa Solemnis"/„Carmina Burana" → `other`); `yearComposed`/
  `life` sind `null` – spätere Anreicherung möglich.
- Programm-/Besetzungs-Erkennung ist heuristisch (variierende Detailseiten); Stichproben-
  Abgleich empfohlen. Klavierduos o. Ä. (z. B. „Katia und Marielle Labèque") stehen als
  ein Solisten-Eintrag.
