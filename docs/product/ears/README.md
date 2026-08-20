# Anforderungen in EARS-Notation

Dieses Verzeichnis beschreibt das **aktuell umgesetzte** Verhalten von Klangland als
Anforderungen in EARS-Notation (Easy Approach to Requirements Syntax). Grundlage ist das
Template [`../../templates/ears.md`](../../templates/ears.md).

EARS beschränkt natürliche Sprache auf eine feste Klauselreihenfolge und ein kleines
Schlüsselwort-Vokabular. Jede Anforderung hat: null bis mehrere Vorbedingungen, null oder
einen Auslöser, genau ein System und eine oder mehrere Systemreaktionen.

## Muster und deutsche Schlüsselwörter

Klangland-Dokumente sind deutschsprachig; wir verwenden daher deutsche EARS-Schlüsselwörter
in fester Zuordnung zu den fünf EARS-Mustern:

| EARS-Muster | Englisch | Verwendetes deutsches Schlüsselwort | Form |
| --- | --- | --- | --- |
| Ubiquitär (immer aktiv) | (kein Keyword) | – | Das `<System>` MUSS `<Reaktion>`. |
| Ereignisgesteuert | WHEN | **WENN** | WENN `<Auslöser>`, MUSS das `<System>` `<Reaktion>`. |
| Zustandsgesteuert | WHILE | **SOLANGE** | SOLANGE `<Vorbedingung>`, MUSS das `<System>` `<Reaktion>`. |
| Optionales Merkmal | WHERE | **SOFERN** | SOFERN `<Merkmal vorhanden>`, MUSS das `<System>` `<Reaktion>`. |
| Unerwünschtes Verhalten | IF / THEN | **FALLS / DANN** | FALLS `<Auslöser>`, DANN MUSS das `<System>` `<Reaktion>`. |
| Komplex | Kombination | – | SOLANGE …, WENN …, MUSS das `<System>` `<Reaktion>`. |

„MUSS" entspricht dem EARS-`SHALL`.

## Dateien

| Datei | System / Bereich |
| --- | --- |
| [`kalender.md`](kalender.md) | Konzertkalender (Startansicht, Navigation, Kacheln) |
| [`veranstaltungsdetail.md`](veranstaltungsdetail.md) | Veranstaltungsdetailseite |
| [`ensembles.md`](ensembles.md) | Ensembleübersicht und -profil |
| [`spielstaetten.md`](spielstaetten.md) | Spielstättenübersicht und -profil |
| [`plattform-und-daten.md`](plattform-und-daten.md) | Statische Webapp, Datenladen, Fehler, Deep-Links, Barrierefreiheit |
| [`suche.md`](suche.md) | Globale Suche im Header über den Datenbestand |
| [`filter.md`](filter.md) | Ort-Filter über Bubbles (Sitzort) für Kalender, Ensembles und Spielstätten |
| [`datenpflege.md`](datenpflege.md) | Ingest-Skripte und Datenintegrität (Daten-Tooling) |

## Konventionen

- Jede Anforderung hat eine stabile ID (`<PRÄFIX>-<Nr.>`) für Referenzierung und Tests.
- Genau **ein** System pro Anforderung; das System steht im jeweiligen Dokumentkopf.
- Anforderungen beschreiben **beobachtbares** Verhalten, keine Implementierungsdetails.
- Umfang = umgesetzter Stand, inkl. Ort-Filter
  ([US-011 Filter](../planning/doing/US-011-filter.md) → [`filter.md`](filter.md)).

## Bezug zu anderen Dokumenten

- Fachliche Grundlage: [PRD](../prd.md) (Akzeptanzkriterien §32).
- Beobachtbare Szenarien: [Contracts (Gherkin)](../contracts/).
- Architekturentscheidungen: [ADRs](../../architecture/).
- Datenmodell: [`../../data-model.md`](../../data-model.md).
