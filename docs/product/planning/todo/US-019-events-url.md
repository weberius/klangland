# User Story 019 - Herkunft und Nachvollziehbarkeit von Veranstaltungsdaten

**Als Betreiber von Klangland möchte ich neben der konkreten Veranstaltungsseite auch die zugrunde liegende Kalender- bzw. Übersichtsseite eines Events speichern, damit die Herkunft der recherchierten Veranstaltungsdaten nachvollziehbar und überprüfbar bleibt.**

#### Akzeptanzkriterien

* Das Feld `source` eines Events wird um `calendarUrl` erweitert.
* `source.url` enthält weiterhin die **konkrete Veranstaltungsseite** des Events.
* `source.calendarUrl` enthält die **Kalender- oder Übersichtsseite**, über die das Event recherchiert bzw. gefunden wurde.
* `source.name` bezeichnet die Organisation bzw. den Anbieter der primären Quelle.
* `source.retrievedAt` dokumentiert, wann die Quelle zuletzt abgerufen bzw. recherchiert wurde.
* `ticketUrl` enthält – sofern verfügbar – einen direkten Link zum Ticketverkauf.
* `lastVerified` dokumentiert weiterhin, wann die inhaltlichen Angaben des Events zuletzt überprüft wurden.
* `calendarUrl` darf `null` sein, wenn keine übergeordnete Kalenderseite existiert oder ermittelt werden konnte.
* Die Webapp soll in der Event-Detailansicht mindestens die **konkrete Veranstaltungsseite** als Quelle und – sofern vorhanden – die **Ticketseite** verlinken. Die Kalender-URL kann optional ebenfalls angezeigt werden.

#### Beispiel

```json
{
  "source": {
    "url": "https://www.koelner-philharmonie.de/de/konzerte/aufbruch-marie-jacquot-yulianna-avdeeva/9250",
    "calendarUrl": "https://www1.wdr.de/orchester-und-chor/sinfonieorchester/konzerte/termine",
    "name": "Kölner Philharmonie",
    "retrievedAt": "2026-08-17"
  },
  "ticketUrl": null,
  "lastVerified": "2026-08-17"
}
```

**Ziel:** Jede Veranstaltung soll in `Klangland` auf ihre ursprüngliche Quelle zurückgeführt werden können. Dadurch wird transparent, **woher ein Termin stammt, wo seine Details überprüft werden können und – sofern vorhanden – wo Tickets erhältlich sind.**
