# EARS – Plattform, Datenladen und Navigation

**System:** die Webapp

Übergreifende Anforderungen an die statische Webapp: Datenladen, Fehlerbehandlung,
Navigation, Deep-Links, Konfiguration, Sprache und Barrierefreiheit. Siehe auch
[Contract](../contracts/datenladen-und-navigation.feature) sowie die
[ADRs](../../architecture/).

## Statik und Datenladen

- **PLT-1** (ubiquitär): Die Webapp MUSS ohne Backend und ohne Datenbank funktionieren.

- **PLT-2** (ubiquitär): Die Webapp MUSS ihren Datenbestand ausschließlich aus den
  versionierten JSON-Dateien beziehen und darf keine Logik zur Datenbeschaffung enthalten.

- **PLT-3** (ereignisgesteuert): WENN die Webapp gestartet wird, MUSS sie den Datenbestand
  einmalig laden und für die Dauer der Sitzung im Speicher vorhalten.

- **PLT-4** (unerwünschtes Verhalten): FALLS der Datenbestand nicht geladen werden kann,
  DANN MUSS die Webapp den Hinweis „Die Veranstaltungsdaten konnten nicht geladen werden."
  anzeigen und darf nicht abstürzen.

- **PLT-5** (unerwünschtes Verhalten): FALLS einzelne Veranstaltungen fehlerhafte oder
  unvollständige Felder enthalten, DANN MUSS die Webapp die übrige Anwendung weiter
  darstellen.

## Navigation und Deep-Links

- **PLT-6** (ubiquitär): Die Webapp MUSS auf jeder Seite eine Hauptnavigation zu „Kalender",
  „Ensembles" und „Spielstätten" bereitstellen.

- **PLT-7** (ubiquitär): Die Webapp MUSS Monate, Ensembles, Spielstätten und Veranstaltungen
  über direkte, teilbare URLs erreichbar machen.

- **PLT-8** (unerwünschtes Verhalten): FALLS eine unbekannte Adresse aufgerufen wird, DANN
  MUSS die Webapp den Hinweis „Seite nicht gefunden" sowie einen Verweis zurück zum Kalender
  anzeigen.

## Konfiguration

- **PLT-9** (zustandsgesteuert): SOLANGE ein Referenzdatum konfiguriert ist, MUSS die Webapp
  dieses Datum als „heute" verwenden.

- **PLT-10** (unerwünschtes Verhalten): FALLS kein Referenzdatum konfiguriert ist, DANN MUSS
  die Webapp das tatsächliche Systemdatum als „heute" verwenden.

## Sprache und Barrierefreiheit

- **PLT-11** (ubiquitär): Die Webapp MUSS ihre Oberfläche und Datumsangaben in deutscher
  Sprache darstellen.

- **PLT-12** (ubiquitär): Die Webapp MUSS eine semantische HTML-Struktur, per Tastatur
  erreichbare interaktive Elemente sowie sichtbare Fokuszustände bereitstellen.

- **PLT-13** (ubiquitär): Die Webapp MUSS einen Sprunglink „Zum Inhalt springen" sowie
  beschriftete Navigations- und Steuerelemente bereitstellen.

- **PLT-14** (zustandsgesteuert): SOLANGE die Webapp auf einem schmalen Bildschirm angezeigt
  wird, MUSS sie eine für kleine Geräte geeignete Darstellung des Kalenders anbieten.
