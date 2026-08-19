# User Story: Open Opus als Quelle für Werkdaten

**Als Betreiber von Klangland möchte ich Open Opus als externe Datenquelle für Komponist:innen und klassische Werke nutzen, damit die Werkdatenbank nicht vollständig manuell gepflegt werden muss und Veranstaltungen eindeutig mit Werken verknüpft werden können.**

**Begründung / Akzeptanzkriterien:**

* Open Opus stellt **strukturierte Metadaten zu klassischen Komponist:innen und Werken** bereit.
* Die Daten umfassen insbesondere **Komponist, Werktitel, Gattung und Epoche** und eignen sich damit als Basis für `works.json`.
* Open Opus verfügt über eine **öffentliche API und einen vollständigen JSON-Datenexport**, sodass die Daten automatisiert importiert werden können.
* Die **Open-Opus-Daten sind laut Projektangabe Public Domain** und können daher in Klangland übernommen, verändert und lokal gespeichert werden.
* Jedes importierte Werk soll neben der eigenen Klangland-ID die **externe Open-Opus-ID** speichern, damit Datensätze später eindeutig zugeordnet und aktualisiert werden können.
* Open Opus soll **nicht als Laufzeitabhängigkeit** der Webanwendung verwendet werden. Die Daten werden durch einen Python-Importer regelmäßig abgerufen, normalisiert und in die lokalen `works.json`- bzw. `composers.json`-Dateien übernommen.
* Die Datenqualität von Open Opus wird als **gute Basis, aber nicht als wissenschaftlich vollständige oder autoritative Referenz** betrachtet. Kritische oder fehlende Angaben können durch weitere Quellen ergänzt bzw. validiert werden.
* Die Herkunft der Daten wird in den Datensätzen bzw. in der Projektdokumentation transparent dokumentiert.
* Änderungen und Aktualisierungen der importierten Daten sollen über **Git versioniert** werden.

**Kurzfassung für das PRD:**

> **Open Opus dient Klangland als offene, strukturierte Basisquelle für Komponist:innen und Werke der klassischen Musik. Die Daten werden automatisiert importiert, lokal normalisiert und als eigene Stammdaten gespeichert. Open Opus ist damit eine Datenquelle, nicht die Laufzeitabhängigkeit der Anwendung.**
