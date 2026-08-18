# Dortmunder Philharmoniker – Ingest 2026/27

Quelle: [Kalender Theater Dortmund](https://www.theaterdo.de/kalender/) (Solr-Paging,
server-gerendert) + Detailseiten `https://www.theaterdo.de/produktionen/detail/<slug>/`.

Skript: [`ingest_dortmund.py`](ingest_dortmund.py)

## Quelle / Technik

- **Termine, Uhrzeit, Ort, Ticket** stammen aus dem **Kalender** (`?tx_solr[page]=N`,
  15 Events/Seite). Je Event-Block: `event__date` (Monat/Tag), Uhrzeit aus `event__details`,
  Ort aus dem Ort-`<span>`, Sparte aus `event__division`, Ticket aus dem
  Eventim-Webshop-Link (`ticket.theaterdo.de/…/shop?event=<id>`). Gefiltert wird auf die
  Sparte **Philharmoniker**.
- **Programm und Besetzung** stammen aus den **Detailseiten** (die Termine/Tickets stehen
  dort nicht – sie werden per Eventim-Widget nachgeladen). Programm: Block hinter
  `orange-line--right` (`<strong>Komponist</strong> Werk<br>…`); Besetzung: Abschnitt
  „Besetzung" hinter `orange-line--left` (`<strong>Rolle</strong> <a>Name</a>`).

## Umfang

Alle Konzerte der Sparte **Philharmoniker** der Spielzeit 2026/27:
Philharmonische Konzerte, Kammerkonzerte, Familien-, Baby-, Sitzkissen-, „Junge Leute"-,
Deep-Dive-, Late-Night- (Kokerei Hansa), Neujahrs-, Stummfilm-, Kaffeehaus-,
Mitsing-, Benefiz- und Sonderkonzerte (z. B. „medizin meets musik", Beethoven-NOW-Festival).

Ergebnis: **62 Aufführungen** (Zeitraum 09.09.2026–14.07.2027). **40** haben einen
Eventim-Ticketlink; die übrigen sind ticketlos in der Quelle (Matineen, Gratis-Formate,
Baby-/Familienkonzerte mit anderem Verkaufsweg). **Öffentliche Proben** werden
ausgeschlossen (keine eigenständigen Konzerte).

## Spielstätten

Die Philharmoniker spielen an vielen Orten. `konzerthaus-dortmund` existierte bereits; neu
angelegt wurden u. a. `opernhaus-dortmund` (Opernfoyer), `kokerei-hansa-dortmund`,
`baukunstarchiv-nrw-dortmund`, `akademie-theater-digitalitaet-dortmund`,
`deutsches-fussballmuseum-dortmund`, `phoenix-des-lumieres-dortmund`,
`thier-galerie-dortmund`, `domicil-dortmund` (Adressen `null`, sofern nicht belegt).

## Programm-Normalisierung

Das Programm wird in `program[].workId` überführt (`works.json`/`composers.json` werden
ergänzt), damit es auf der Event-Seite dargestellt wird. Genre wird heuristisch aus dem Titel
abgeleitet (kontrollierte Werte), Katalognummern (op./KV/BWV/Hob) werden geparst,
`yearComposed`/`life`/`durationMinutes` bleiben `null` (nicht aus der Quelle belegt). Werke
werden über (Komponist + normalisierter Titel) dedupliziert und mit dem Bestand
wiederverwendet. 26 der 62 Events haben ein strukturiertes Werkprogramm; Formate ohne
klassische Werkliste (Baby-/Familien-/Sitzkissen-/Deep-Dive-/Late-Night-/Film-/Café-Konzerte)
bleiben ohne `program`.

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `theaterdo.de` und Ensemble
`dortmunder-philharmoniker` entfernt und neu angelegt; Stammdaten (Venues, Personen,
Komponist:innen, Werke) werden nur ergänzt, wenn ihre ID/ihr Schlüssel fehlt.

## Offene Punkte / Grenzen

- Beim **Beethoven-NOW-Festival** listet die Quelle die Werke fett **ohne Komponistenzeile**
  (Ein-Komponisten-Abende); um keine Pseudo-Komponist:innen anzulegen, bleiben diese zwei
  Konzerte vorerst ohne `program`.
- `genre` ist heuristisch; `yearComposed`/`life` sind `null` – spätere Anreicherung möglich.
- Programm-/Besetzungs-Erkennung ist heuristisch (variierende Detailseiten-Formate);
  Stichproben-Abgleich empfohlen.
