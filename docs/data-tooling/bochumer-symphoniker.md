# Bochumer Symphoniker – Ingest 2026/27

Quelle: [Programm/Kalender der Bochumer Symphoniker](https://www.bochumer-symphoniker.de/programm/search////0//1)
(JS-gerendert, paginiert). Datenzugriff über den internen Endpunkt und die Detailseiten.

Skript: [`ingest_bochum.py`](ingest_bochum.py)

## Quelle / Technik

Die Kalenderseite lädt Events dynamisch per `POST /programm?type=1691066967`
(Formularfelder u. a. `page`, `viewType`) und liefert JSON mit einem HTML-Fragment je
Seite (`pages` = Liste der Seitenzahlen). Das Skript paginiert über alle Seiten, sammelt die
Detail-Slugs und lädt je Veranstaltung `…/programm/detail/<slug>`.

Auf der Detailseite werden ausgelesen:

- **Termine + Uhrzeit + Ticket** aus dem Block `#ceventTickets`
  (`<a href="…reservix…" class="date">` mit Datum/Uhrzeit) bzw. – bei Konzerten mit nur
  einem Termin – aus dem Hero-Ticket-Button (`title="… | … Uhr"`).
- **Programm / Mit / Beschreibung** aus `#ceventTextColumns`
  (`<strong>Komponist</strong><br>Werk`).
- **Ticket-Links:** Reservix-URL je Aufführung (`ticketUrl`).

## Umfang

Aufgenommen werden **alle Eigenkonzerte** der Bochumer Symphoniker im
**Anneliese Brost Musikforum Ruhr** (`zeughauskultur-bochum`): orchestrale Reihen
(Meisterstücke, Matinée, Pur, Geschichten, Concerto, Chor), Kammermusik (Camera, Quartett),
Familien-/Kinderkonzerte (Krabbelkäfer, Lauschbild, Märchenzelt, Familie) sowie die
BOSY-Extra-Sonderkonzerte.

Ergebnis: **67 Produktionen → 99 Aufführungen** (je Aufführungstermin ein Event),
Spielzeit 05.09.2026–04.07.2027. **94 Events** haben einen Reservix-Ticketlink; 5 (noch)
nicht (vier reine Schulkonzert-Termine ohne öffentlichen Verkauf sowie ein Kammerkonzert,
dessen Vorverkauf zum Erfassungszeitpunkt noch nicht freigeschaltet war).

### Bewusst ausgeschlossen

| Sparte | Grund |
| --- | --- |
| Musikschule | Veranstaltungen der Musikschule Bochum, nicht des Orchesters |
| Musikvermittlung | Nachwuchs-/Vermittlungsformate (z. B. Orchesterkurs-Abschluss) |
| Zu Gast | Gastspiele fremder Künstler:innen (z. B. Klavier-Festival Ruhr, Igor Levit) |
| BOSY on Tour | auswärtige Gastspiele (Dortmund, Amsterdam, Erwitte …); Venues nicht im Bestand |
| Hörprobe | offene Proben/Preview-Formate, keine eigenständigen Konzerte |

Ebenfalls ausgelassen: **Die BOSY am KAP** (Open-Air-Saisonabschluss am Bermuda3Eck) – kein
Musikforum-Venue im Bestand und kein Ticket-Verkauf über Reservix.

## Modellierungsentscheidungen

- **Ensemble:** alle Events referenzieren `bochumer-symphoniker`; bei Kammer-/Familienformaten
  treten Musiker:innen des Orchesters auf. Die Namen der Kammerensembles (z. B. „Viktoria
  Quartett", „artTone Trio") stehen im `description`-Freitext.
- **Programm** wird in `program[].workId` normalisiert; `works.json` und `composers.json`
  werden dabei ergänzt. Neue Komponist:innen werden dublettenfrei angelegt (mit
  Schreibvarianten-Aliassen, z. B. „Sergei Rachmaninow" → `sergej-rachmaninow`;
  Lebensdaten `life: null`, da nicht aus der Quelle belegt). Werke werden über
  (Komponist + normalisierter Titel) dedupliziert und wo möglich mit bestehenden Werken
  wiederverwendet. **Genre** wird heuristisch aus dem Titel abgeleitet (kontrollierte Werte;
  Suiten/Sinfonische Dichtungen/Lieder → `other`), **Katalognummern** nur bei eindeutigen
  Systemen (op./KV/BWV) geparst, `yearComposed`/`durationMinutes` bleiben `null` (nicht
  erfunden). Titel, die die Quelle per `<br>` umbricht (Tonart/Beiname wie „…Es-Dur"+„Eroica"),
  werden zu einem Werk zusammengeführt. 59 der 99 Events haben ein Werkprogramm; die übrigen
  40 sind Pop-/Familien-/Kinderkonzerte ohne klassische Werkliste.
- **Verschobene Konzerte:** Ein als „in die Saison 2027/28 verschoben" gekennzeichnetes
  Konzert (SchlagAbtausch, 14.03.27) erhält `status: "postponed"` und einen Hinweis in
  `description`.
- **Dirigent:innen/Solist:innen** werden als Personen angelegt (dublettenfrei über IDs);
  Rollen werden aus der Besetzung („Name, Instrument/Stimme/Leitung") erkannt. Personen mit
  Doppelrolle (z. B. Sergey Malov: Violine **und** Leitung) stehen in beiden Listen.
- **Chöre/Moderation/Sprecher** haben kein eigenes Feld → `description` bzw. ausgelassen
  (siehe Event-Modellierungs-Konventionen).

## Idempotenz

Vor dem Schreiben werden alle Events mit Quell-Host `bochumer-symphoniker.de` und Ensemble
`bochumer-symphoniker` entfernt und neu angelegt; Personen werden nur ergänzt, wenn ihre ID
noch fehlt. Ein erneuter Lauf ist damit gefahrlos wiederholbar.

## Offene Punkte / Grenzen

- `genre` ist heuristisch, `yearComposed`/`life`/`durationMinutes` sind `null` – eine spätere
  Anreicherung der Werk-/Komponist:innen-Stammdaten ist möglich.
- Ticket-Links, die vom Veranstalter erst später veröffentlicht werden (5 Events), sollten
  bei einer Aktualisierung nachgezogen werden (erneuter Lauf genügt).
- Die automatische Rollen-/Namens- und Programmerkennung ist heuristisch; bei ungewöhnlich
  formatierten Detailseiten empfiehlt sich ein Stichproben-Abgleich.
