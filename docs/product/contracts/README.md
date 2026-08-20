# Contracts (Gherkin)

Ausführbare Spezifikationen des **aktuell umgesetzten** Verhaltens von Klangland als
Gherkin-`.feature`-Dateien. Sie beschreiben das beobachtbare Verhalten aus Nutzersicht und
folgen dem Referenz-Template unter [`../../templates/gherkin.md`](../../templates/gherkin.md).

Die Szenarien sind in deutscher Gherkin-Lokalisierung geschrieben (`# language: de`),
passend zur Domänensprache des Projekts (Schlüsselwörter: `Funktionalität`, `Grundlage`,
`Regel`, `Szenario`, `Szenariogrundriss`, `Beispiele`, `Angenommen`, `Wenn`, `Dann`, `Und`,
`Aber`).

## Übersicht

| Datei | Deckt ab |
| --- | --- |
| [`kalender.feature`](kalender.feature) | Startansicht, Monatsraster, Kacheln, Monatsnavigation, Deep-Links, „Heute", leerer Monat, Absagen |
| [`veranstaltungsdetail.feature`](veranstaltungsdetail.feature) | Termin, Mitwirkende, Programm, Spielstätte, Quelle, Tickets, „nicht gefunden" |
| [`ensembles.feature`](ensembles.feature) | Ensembleübersicht und -profil inkl. zugehöriger Veranstaltungen |
| [`spielstaetten.feature`](spielstaetten.feature) | Spielstättenübersicht und -profil inkl. Veranstaltungen |
| [`datenladen-und-navigation.feature`](datenladen-und-navigation.feature) | Einmaliges Laden, Fehlerbehandlung, Hauptnavigation, 404, Referenzdatum |
| [`suche.feature`](suche.feature) | Globale Suche im Header mit Mindestlänge und Fuzzy-Treffern |
| [`filter.feature`](filter.feature) | Ort-Filter über Bubbles (Sitzort), Kennzeichen, Auswahl je Liste, Persistenz, Info-Toggle, Burger-Nav |
| [`kalender-eintrag.feature`](kalender-eintrag.feature) | „In den Kalender eintragen": clientseitige `.ics`-Erzeugung, Pflichtfelder, Zeitzone, ganztägig-Fallback, Absage, stabile UID |

## Bezug zu anderen Dokumenten

- Fachliche Grundlage: [PRD](../prd.md) (Akzeptanzkriterien §32) und
  [Datenmodell](../../data-model.md).
- Architekturentscheidungen: [`../../architecture/`](../../architecture/) — u. a. statische
  App ohne Backend und JSON als Single Source of Truth prägen die Szenarien zu Datenladen
  und Fehlerbehandlung.

## Umfang und Abgrenzung

Diese Contracts spiegeln den **implementierten** Stand (Kalender, Detailseiten, Profile,
Datenladen, Suche, Ort-Filter). Noch nicht entwickelte Backlog-Stories erhalten eigene
Contracts, sobald sie umgesetzt werden bzw. als Vorab-Spezifikation gewünscht sind.

Zuletzt spezifiziert: [US-012 Kalender-Eintrag](../planning/doing/US-012-kalender-eintrag.md)
→ [`kalender-eintrag.feature`](kalender-eintrag.feature).

## Konventionen

- Eine `Funktionalität` pro Datei; verwandte Szenarien ggf. über `Regel` gruppiert.
- Schritte beschreiben **beobachtbares** Verhalten, keine Implementierungsdetails.
- 3–5 Schritte pro Szenario; wiederkehrende Vorbedingungen in `Grundlage`.
- Konkrete Beispieldaten (z. B. „Mahler 3", „Tonhalle Düsseldorf") dienen der
  Anschaulichkeit und entsprechen dem Muster des vorhandenen Datenbestands.
