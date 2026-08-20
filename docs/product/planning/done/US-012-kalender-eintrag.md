# User Story 012 - Termin in den Kalender eintragen

## User Story

**Als** Besucher:in von Klangland,
**möchte ich** ein Konzert direkt von seiner Detailseite aus mit einem Klick in meinen
Gerätekalender übernehmen,
**damit** ich den Termin ohne manuelles Abtippen speichere und rechtzeitig daran erinnert werde.

## Kontext / Problem

Die Event-Detailseite ([event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html),
Route `events/:id` in [app.routes.ts:36](../../../../web/src/app/app.routes.ts#L36)) zeigt alle
relevanten Termindaten – Titel, Datum, Uhrzeit, Spielstätte, Ensemble, Quelle. Es gibt jedoch
keine Möglichkeit, diesen Termin in den persönlichen Kalender zu übernehmen; Nutzer:innen müssen
die Angaben von Hand abtippen. Das ist umständlich und fehleranfällig.

Klangland ist eine **statische App ohne Backend** ([DataService](../../../../web/src/app/core/data.service.ts)
lädt nur versionierte JSON-Dateien). Eine Lösung muss daher clientseitig funktionieren. Das
Datenmodell liefert die nötigen Felder ([models.ts](../../../../web/src/app/models/models.ts#L169):
`title`, `date`, `startTime`, `endTime`, `status`, `venueId`, `cityId`, `ensembleIds` sowie
`source`).

**Betroffen** ist ausschließlich die Event-Detailseite. **Nicht betroffen** sind die
Übersichts-/Listenseiten (Kalender, Ensembles, Spielstätten) und die übrige Detailansicht.

## Gewählte Lösung

Auf der Event-Detailseite wird eine Aktion „In den Kalender eintragen" ergänzt, die
**clientseitig eine standardkonforme iCalendar-Datei (`.ics`, RFC 5545)** für genau dieses Event
erzeugt und zum Öffnen/Download anbietet.

Der Vorteil: `.ics` wird von allen relevanten Zielsystemen nativ verstanden – Apple Kalender
(iOS/macOS), Android, Windows/Outlook sowie Google Kalender. Damit genügt **eine** Umsetzung
für alle Plattformen, ohne Backend und ohne Plattform-/Browsererkennung.

Bewusst verworfene Alternativen: eine plattform-/browserabhängige Auswahl bzw. anbieterspezifische
„Zu Google/Outlook hinzufügen"-Links – zugunsten der einfacheren, wartungsarmen und offline
funktionierenden `.ics`-Lösung.

Der `.ics`-Eintrag (`VEVENT`) enthält mindestens: Titel (`SUMMARY`), Start/Ende (`DTSTART`/`DTEND`
mit Zeitzone Europe/Berlin), Ort (`LOCATION` aus Spielstätte + Stadt), eine Beschreibung
(`DESCRIPTION` mit Ensemble(s)/Dirigent:in und Link zur Event-Seite), einen Rückverweis (`URL`)
sowie eine stabile, eindeutige Kennung (`UID`).

## Akzeptanzkriterien

1. **Aktion vorhanden:** Auf jeder Event-Detailseite gibt es eine klar beschriftete Aktion
   „In den Kalender eintragen".
2. **Clientseitige Erzeugung:** Ein Klick erzeugt clientseitig eine `.ics`-Datei für genau dieses
   Event; es wird kein Backend-Aufruf benötigt.
3. **Pflichtfelder:** Die Datei enthält Titel, Startzeitpunkt (Datum + Uhrzeit), Ort (Spielstätte
   und Stadt) sowie eine Beschreibung mit Ensemble(s)/Dirigent:in und einem Link zur
   Event-Detailseite.
4. **Zeit und Dauer:** Bei vorhandener `endTime` wird das Ende korrekt gesetzt; die Zeitangaben
   verwenden die Zeitzone Europe/Berlin, sodass Start/Ende im Zielkalender richtig erscheinen.
5. **Fehlende Uhrzeit:** Ist `startTime` nicht gesetzt, wird ein sinnvoller Fallback erzeugt
   (ganztägiger Eintrag am Veranstaltungsdatum).
6. **Abgesagte Events:** Bei `status = cancelled` wird die Absage im Kalendereintrag kenntlich
   gemacht (`STATUS:CANCELLED` und/oder Kennzeichnung im Titel).
7. **Stabile UID:** Jeder Eintrag trägt eine stabile, eindeutige `UID` je Event, sodass ein
   erneuter Import den bestehenden Termin aktualisiert statt zu duplizieren.
8. **Standardkonformität:** Die Datei ist gültiges iCalendar (RFC 5545) und lässt sich auf
   iOS/macOS, Android, Windows/Outlook und Google Kalender importieren.
9. **Rückverweis:** Der Eintrag verlinkt über das `URL`-Feld auf die Event-Detailseite.
10. **Barrierefreiheit:** Die Aktion ist ein echtes, per Tastatur bedienbares Bedienelement mit
    aussagekräftigem Label.
11. **Unveränderte Bereiche:** Übersichts-/Listenseiten und die übrige Event-Detailseite bleiben
    unverändert.

## Out of Scope

- Favoriten, Favoriten-Filter und das Teilen von Auswahlen per URL – eigene Story (US-021).
- Plattform-/Browsererkennung und anbieterspezifische „Zu Google/Outlook hinzufügen"-Links.
- Serverseitige Kalender-Feeds/Abonnements (laufend aktualisierte `.ics`-Subscriptions).
- Automatisches Setzen von Erinnerungen/Alarmen (`VALARM`).
- Sammel-Export mehrerer Events auf einmal.

<!--
Umsetzungs-Tasks in separater Datei US-012-tasks.md im selben Verzeichnis pflegen.
-->
