# EARS – Termin in den Kalender eintragen

**System:** die Veranstaltungsdetailseite

Die Detailseite bietet an, einen Termin clientseitig als standardkonforme iCalendar-Datei
(.ics, RFC 5545) in den Gerätekalender zu übernehmen – ohne Backend. Siehe auch
[Contract](../contracts/kalender-eintrag.feature).

## Anforderungen

- **CAL-1** (ubiquitär): Die Veranstaltungsdetailseite MUSS ein klar beschriftetes, per
  Tastatur bedienbares Bedienelement „In den Kalender eintragen" anzeigen.

- **CAL-2** (ereignisgesteuert): WENN das Bedienelement „In den Kalender eintragen"
  ausgelöst wird, MUSS die Veranstaltungsdetailseite clientseitig – ohne Backend-Aufruf –
  eine iCalendar-Datei (.ics) für genau diese Veranstaltung erzeugen und zum
  Öffnen/Download anbieten.

- **CAL-3** (ubiquitär): Die erzeugte iCalendar-Datei MUSS Titel, Startzeitpunkt (Datum und
  Uhrzeit), Ort (Spielstätte und Stadt) sowie eine Beschreibung mit Ensemble(s)/Dirigent:in
  und einem Link zur Veranstaltungsdetailseite enthalten.

- **CAL-4** (optionales Merkmal): SOFERN eine Endzeit hinterlegt ist, MUSS die iCalendar-Datei
  das Ende setzen; Beginn und Ende MÜSSEN die Zeitzone Europe/Berlin verwenden, sodass sie im
  Zielkalender korrekt erscheinen.

- **CAL-5** (unerwünschtes Verhalten): FALLS keine Beginnzeit erfasst ist, DANN MUSS die
  iCalendar-Datei einen ganztägigen Eintrag am Veranstaltungsdatum enthalten.

- **CAL-6** (zustandsgesteuert): SOLANGE eine Veranstaltung den Status „abgesagt" hat, MUSS
  die iCalendar-Datei die Absage kenntlich machen (Status abgesagt und Kennzeichnung im Titel).

- **CAL-7** (ubiquitär): Die iCalendar-Datei MUSS je Veranstaltung eine stabile, eindeutige
  Kennung (UID) tragen, sodass ein erneuter Import den bestehenden Termin aktualisiert statt
  ihn zu duplizieren.

- **CAL-8** (ubiquitär): Die iCalendar-Datei MUSS gültiges iCalendar (RFC 5545) sein und einen
  Rückverweis auf die Veranstaltungsdetailseite (URL-Feld) enthalten.
