# User Story 017 - Open Opus & Wikipedia als Quellen für Komponist:innen- und Werkdaten

## User Story

**Als** Betreiber:in von Klangland
**möchte ich** Komponist:innen- und Werkdaten aus Open Opus (strukturierte Metadaten) und aus der Wikipedia (verständliche Einordnung) anreichern,
**damit** die Werkdatenbank nicht vollständig manuell gepflegt werden muss, Veranstaltungen eindeutig mit Werken verknüpft werden können und Besucher:innen fundierte, lesbare Informationen zu Komponist:innen und Werken erhalten.

## Kontext / Problem

Klangland pflegt Stammdaten zu Komponist:innen in [composers.json](../../../../data/composers.json) und zu Werken in [works.json](../../../../data/works.json). Die Datenmodelle [`Composer`](../../../../web/src/app/models/models.ts#L131-L135) und [`Work`](../../../../web/src/app/models/models.ts#L152-L163) sind heute knapp gehalten (Komponist: Name, Lebensdaten; Werk: Titel, Werkverzeichnis, Entstehungsjahr, Gattung, Dauer u. a.). Es fehlen:

* eine **stabile externe Referenz**, um Datensätze eindeutig zuzuordnen und später aktualisieren zu können,
* eine **redaktionell verständliche Einordnung** (Kurzbiografie, Werkkontext), die über reine Fakten hinausgeht.

Zwei Quellen ergänzen sich hier überschneidungsfrei:

* **Open Opus** ([API](https://github.com/openopus-org/openopus_api/tree/master), [USAGE](https://github.com/openopus-org/openopus_api/blob/master/USAGE.md), [Dump](https://api.openopus.org/work/dump.json)) liefert **ausschließlich strukturierte Metadaten** – zu Komponist:innen (`complete_name`, `birth`, `death`, `epoch`, `portrait`, externe ID) und zu Werken (`title`, `subtitle`, `genre`, Werkverzeichnis, `popular`/`recommended`, externe ID). Open Opus enthält **keine** Biografien, Werkbeschreibungen oder Programmtexte.
* **Wikipedia** liefert genau diese fehlende Prosa. Analog zu [US-014](../done/US-014-ensemble-wikipedia.md) wird pro Komponist:in und (relevantem) Werk eine **eigenständig formulierte Kurzfassung** samt Quellenverweis recherchiert und kuratiert gepflegt.

Damit gilt: **Open Opus = Gerüst (Fakten, Struktur, IDs), Wikipedia = Einordnung (verständliche Prosa).**

## Gewählte Lösung

### 1. Open Opus als Basisquelle für strukturierte Daten

* Ein **Python-Importer** ruft die Open-Opus-Daten ab (Dump bzw. API), normalisiert sie und übernimmt sie in die lokalen `composers.json`- und `works.json`-Dateien. Open Opus ist **keine Laufzeitabhängigkeit** der Webanwendung.
* **Schonender Abruf:** Recherche und Download erfolgen bewusst gedrosselt, um die fremden Server (Open Opus, Wikipedia) nicht zu belasten – **höchstens ein Netzwerk-Request pro Sekunde**. Ergebnisse werden möglichst lokal zwischengespeichert, damit wiederholte Läufe nicht dieselben Ressourcen erneut abrufen.
* Jeder importierte Datensatz speichert neben der eigenen Klangland-ID die **externe Open-Opus-ID** (`openOpusId`), damit Datensätze eindeutig zugeordnet und später re-synchronisiert werden können.
* Übernommen bzw. ergänzt werden strukturierte Felder, insbesondere:
  * Komponist:in: **Epoche** (`epoch`, Open-Opus-Werte auf Deutsch abgebildet), Lebensdaten (Abgleich/Validierung), Portrait-URL (optional, siehe Out of Scope zu Lizenz).
  * Werk: kanonischer Titel/Untertitel, normalisierte **Gattung**, **Werkverzeichnis-Nummern**, sowie die Open-Opus-Kennzeichen `popular`/`recommended` als Grundlage für spätere Werkvorschläge.
* Der Import überschreibt **keine** manuell kuratierten Felder unkontrolliert; bei Konflikten hat die redaktionelle Pflege Vorrang (Import ergänzt, ersetzt nicht blind).

### 2. Wikipedia als Quelle für verständliche Einordnung

* Komponist:innen und (im Programm relevante) Werke erhalten optionale **Wikipedia-Angaben** nach dem Muster aus [US-014](../done/US-014-ensemble-wikipedia.md): eine **eigenständig formulierte Kurzfassung von ca. 60 Wörtern** (kein wörtlicher Auszug) plus **URL zum Artikel**, gebündelt als `wikipedia: { summary, url }`.
* Diese Kurzfassungen werden im Rahmen dieses Tickets **recherchiert und formuliert** (Internet-/Wikipedia-Recherche ist Teil des Tickets) und kuratiert in den Projektdaten gepflegt – **nicht** zur Laufzeit geladen.

### 3. Datenqualität, Herkunft, Versionierung

* Open-Opus-Daten gelten als **gute Basis, nicht als autoritative Referenz**; kritische oder fehlende Angaben werden durch weitere Quellen ergänzt bzw. validiert.
* **Attributierung von Open Opus:** Auch wenn die Open-Opus-Daten unter CC0 (Public Domain) stehen und eine Namensnennung rechtlich nicht zwingend ist, wird Open Opus als Quelle **sichtbar attribuiert** – als Zeichen der Transparenz und Fairness gegenüber dem Projekt. Der Credit nennt Open Opus namentlich und verlinkt auf das Projekt (`https://openopus.org`).
* Die **Herkunft der Daten** (Open Opus als CC0-/Public-Domain-Quelle mit sichtbarem Credit, Wikipedia mit Quellenhinweis pro Kurzfassung) wird in den Datensätzen bzw. der Projektdokumentation transparent dokumentiert.
* Alle Importe und redaktionellen Änderungen werden über **Git versioniert**.

Bewusst akzeptierter Kompromiss: Die kuratierten Kurzfassungen sind redaktionelle Momentaufnahmen und aktualisieren sich nicht automatisch, wenn sich Open Opus oder der Wikipedia-Artikel ändern.

## Akzeptanzkriterien

1. **Externe Referenz:** Die Modelle `Composer` und `Work` sowie die Daten in [composers.json](../../../../data/composers.json)/[works.json](../../../../data/works.json) unterstützen eine optionale externe Open-Opus-ID (`openOpusId`). Datensätze ohne externe ID bleiben valide.
2. **Strukturierte Anreicherung Komponist:in:** Das `Composer`-Modell unterstützt mindestens ein Feld **Epoche** (aus Open Opus, deutschsprachig abgebildet). Bestehende Lebensdaten werden gegen Open Opus abgeglichen; Abweichungen werden dokumentiert.
3. **Strukturierte Anreicherung Werk:** Gattung und Werkverzeichnis-Angaben werden – wo vorhanden – aus Open Opus ergänzt/validiert; die Open-Opus-Kennzeichen `popular`/`recommended` können übernommen werden.
4. **Wikipedia-Kurzfassung:** `Composer` und `Work` unterstützen optionale Wikipedia-Angaben `wikipedia: { summary, url } | null` (eigenständig formulierte Kurzfassung ~60 Wörter + Artikel-URL) analog zum `Ensemble`-Modell. Datensätze ohne diese Angaben bleiben valide.
5. **Import ohne Laufzeitabhängigkeit:** Ein **Python-Importer** ruft Open-Opus-Daten ab, normalisiert sie und schreibt sie in die lokalen JSON-Dateien. Die Webanwendung greift zur Laufzeit **nicht** auf Open Opus oder Wikipedia zu.
6. **Kein unkontrolliertes Überschreiben:** Der Importer ergänzt Datensätze und respektiert bereits kuratierte redaktionelle Felder (insb. Wikipedia-Kurzfassungen); ein Re-Import zerstört keine manuelle Pflege.
7. **Attributierung Open Opus:** Open Opus wird als Datenquelle sichtbar attribuiert (namentliche Nennung „Open Opus" plus Link auf `https://openopus.org`). Der Credit ist mindestens in der Projektdokumentation und – sobald die Daten in der UI dargestellt werden (US-024) – an einer für Nutzer:innen erreichbaren Stelle (z. B. Datenquellen-/Impressum-Hinweis) sichtbar. Dies erfolgt bewusst, obwohl CC0 keine Namensnennung verlangt.
8. **Herkunft/Attributierung gesamt:** Die Datenherkunft wird transparent dokumentiert (Open Opus als CC0-Basisquelle mit Credit; Wikipedia mit Quellenhinweis pro Kurzfassung).
9. **Versionierung:** Import- und Pflege-Änderungen sind über Git nachvollziehbar versioniert.
10. **Recherche/Datenpflege:** Für die aktuell in [events.json](../../../../data/events.json) referenzierten Komponist:innen und Werke werden – wo ein geeigneter Artikel existiert – Wikipedia-URL und Kurzfassung gepflegt.
11. **Schonender Abruf / Rate-Limiting:** Der Importer und alle Recherche-Skripte begrenzen ihre Netzwerkzugriffe auf Open Opus und Wikipedia auf **maximal einen Request pro Sekunde** (mindestens 1 Sekunde Pause zwischen zwei Requests). Wo möglich werden Antworten lokal gecacht, um unnötige Wiederholungsanfragen zu vermeiden.

## Out of Scope

* Anzeige/Integration der Daten in der UI (eigene `/composers`- und `/works`-Seiten) – siehe [US-024](../backlog/us-024-composers-and-works.md).
* Live-Abruf von Open Opus oder Wikipedia zur Laufzeit der Webanwendung.
* Automatische Generierung oder Aktualisierung der Wikipedia-Kurzfassungen.
* Einbindung von Portrait-/Bildmedien in die Anwendung, solange deren Lizenz nicht geklärt ist (die Portrait-URL kann als Metadatum gespeichert, aber vorerst nicht angezeigt werden).
* Vollständiger Import des gesamten Open-Opus-Katalogs; Fokus liegt auf den in Klangland tatsächlich referenzierten Komponist:innen und Werken (Open Opus dient als Nachschlage-/Ergänzungsquelle, nicht als Massenimport).
* Mehrsprachigkeit der Kurzfassungen (nur Deutsch).

<!--
Umsetzungs-Tasks:
In separater Datei US-017-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
