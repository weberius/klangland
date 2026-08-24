# language: de

Funktionalität: Datenpflege und Datenintegrität
  Die Ingest-Skripte laden Spielpläne aus offiziellen Quellen idempotent in die
  versionierten JSON-Dateien. Jeder Lauf validiert die Datenintegrität, Eindeutigkeit
  der IDs und die Konsistenz aller Verweise.

  Hintergrund:
    Angenommen das Ingest-Skript ist konfiguriert
    Und die Quelldaten sind verfügbar

  Szenario: Ingest-Skript erstellt genau ein Event pro Aufführungstermin
    Wenn das Ingest-Skript eine Quelle mit 5 verschiedenen Aufführungsterminen lädt
    Dann werden genau 5 Events erzeugt
    Und jedes Event hat eine eindeutige ID

  Szenario: Beziehungen werden über IDs hergestellt
    Wenn das Ingest-Skript ein Konzert mit Ensemble, Ort und Komponist einspielt
    Dann enthält das Event nur die IDs dieser Entitäten
    Und keine Stammdaten sind in das Event dupliziert

  Szenario: IDs folgen dem kebab-case-Format mit Transliteration
    Wenn das Ingest-Skript ein Ensemble "Düsseldorf Philea" einspielt
    Dann wird die ID "duesseldorf-philea" erzeugt
    Und Umlaute sind korrekt transliteriert

  Szenario: Ingest-Lauf ist idempotent
    Angenommen die Quelle hatte beim letzten Lauf 3 Events
    Wenn das Ingest-Skript dieselbe Quelle erneut lädt
    Dann werden die alten 3 Events dieser Quelle zuerst gelöscht
    Und dann die neuen Events eingespielt
    Und die Gesamtzahl der Events ist konsistent

  Szenario: Duplikate von Stammdaten werden nicht erzeugt
    Angenommen eine Institution mit ID "kok-koeln" existiert bereits
    Wenn das Ingest-Skript dieselbe Institution erneut einspielt
    Dann wird keine neue Institution angelegt
    Und die bestehende wird nicht dupliziert

  Szenario: Quelle wird bei jedem Event erfasst
    Wenn das Ingest-Skript ein Event einspielt
    Dann hat das Event eine Quelle (z.B. "orchestras-nrw", "wdr-sinfonieorchester")
    Und die Quelle ist nachverfolgbar

  Szenario: Referenzielle Integrität wird nach dem Ingest überprüft
    Wenn das Ingest-Skript einen Lauf abgeschlossen hat
    Dann werden alle Referenzen in den Veranstaltungen überprüft
    Und alle referenzierten Ensemble-, Ort- und Personen-IDs existieren
    Und keine verwaisten Verweise bleiben zurück

  Szenario: Ungültige Datumsformate werden erkannt
    Wenn das Ingest-Skript ein Event mit fehlertemporalen Daten einspielt
    Dann wird dies bei der Validierung erkannt
    Und der Datensatz wird als Fehler protokolliert

  Szenario: Fehlende referenzierte Entitäten werden als Fehler gemeldet
    Wenn ein Event eine Ensemble-ID "unbekannt-ensemble" enthält
    Und diese ID existiert nicht in ensembles.json
    Dann wird ein Validierungsfehler gemeldet
    Und das Event wird als problematisch markiert
