# EARS – Veranstaltungsdetail

**System:** die Veranstaltungsdetailseite

Die Detailseite zeigt alle gespeicherten Informationen einer Veranstaltung und ist über
eine eigene, teilbare URL erreichbar. Siehe auch
[Contract](../contracts/veranstaltungsdetail.feature).

## Anforderungen

- **DET-1** (ereignisgesteuert): WENN eine Adresse der Form `/events/<id>` mit bekannter
  Veranstaltungs-ID aufgerufen wird, MUSS die Veranstaltungsdetailseite die zugehörige
  Veranstaltung anzeigen.

- **DET-2** (unerwünschtes Verhalten): FALLS die Veranstaltungs-ID unbekannt ist, DANN MUSS
  die Veranstaltungsdetailseite den Hinweis „Diese Veranstaltung wurde nicht gefunden."
  sowie einen Verweis zurück zum Kalender anzeigen.

- **DET-3** (ubiquitär): Die Veranstaltungsdetailseite MUSS Titel und ausgeschriebenes Datum
  der Veranstaltung anzeigen.

- **DET-4** (optionales Merkmal): SOFERN eine Beginnzeit hinterlegt ist, MUSS die
  Veranstaltungsdetailseite die Uhrzeit anzeigen.

- **DET-5** (optionales Merkmal): SOFERN eine Endzeit hinterlegt ist, MUSS die
  Veranstaltungsdetailseite auch die Endzeit anzeigen.

- **DET-6** (zustandsgesteuert): SOLANGE der Veranstaltung mindestens ein Ensemble
  zugeordnet ist, MUSS die Veranstaltungsdetailseite die Ensembles als Verweise auf ihre
  Profile anzeigen.

- **DET-7** (optionales Merkmal): SOFERN Dirigent:innen erfasst sind, MUSS die
  Veranstaltungsdetailseite diese anzeigen.

- **DET-8** (optionales Merkmal): SOFERN Solist:innen erfasst sind, MUSS die
  Veranstaltungsdetailseite diese anzeigen.

- **DET-9** (zustandsgesteuert): SOLANGE ein Programm erfasst ist, MUSS die
  Veranstaltungsdetailseite je Programmpunkt Komponist:in und Werktitel anzeigen.

- **DET-10** (optionales Merkmal): SOFERN zu einem Programmpunkt Katalognummer,
  Entstehungsjahr, Fassung oder Satz vorliegen, MUSS die Veranstaltungsdetailseite diese
  ergänzenden Angaben anzeigen.

- **DET-11** (unerwünschtes Verhalten): FALLS weder ein Programm noch ein Programmhinweis
  erfasst ist, DANN MUSS die Veranstaltungsdetailseite den Hinweis „Kein Programm erfasst."
  anzeigen.

- **DET-12** (ubiquitär): Die Veranstaltungsdetailseite MUSS die Spielstätte mit Ort
  anzeigen und, sofern vorhanden, als Verweis auf ihr Profil verlinken.

- **DET-13** (optionales Merkmal): SOFERN zur Spielstätte eine Adresse oder eine Website
  hinterlegt ist, MUSS die Veranstaltungsdetailseite diese anzeigen.

- **DET-14** (optionales Merkmal): SOFERN zur Veranstaltung eine Quelle hinterlegt ist, MUSS
  die Veranstaltungsdetailseite einen Quellenlink mit Namen und Abrufdatum anzeigen.

- **DET-15** (optionales Merkmal): SOFERN eine Ticket-Adresse hinterlegt ist, MUSS die
  Veranstaltungsdetailseite einen Ticket-Verweis anzeigen.

- **DET-16** (zustandsgesteuert): SOLANGE eine Veranstaltung nicht den Status „geplant" hat,
  MUSS die Veranstaltungsdetailseite den abweichenden Status (z. B. „abgesagt") ausweisen.
