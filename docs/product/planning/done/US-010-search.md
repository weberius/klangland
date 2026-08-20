# User Story 010 - Globale Suche

## User Story

**Als** Besucher:in von Klangland,  
**möchte ich** auf jeder Seite in der oberen Leiste ein Suchfeld zwischen „Klangland“ und der Navigation nutzen können, das ab mindestens drei eingegebenen Zeichen eine Fuzzy-Suche über alle Daten im [data](/Users/wolfram/workspaces/klangland/data)-Verzeichnis ausführt,  
**damit** ich Inhalte wie Komponist:innen, Werke und Veranstaltungen schnell finde, auch wenn ich Suchbegriffe nicht exakt schreibe.

## Kontext / Problem

Aktuell gibt es keine zentrale Suche, um Inhalte in Klangland schnell auffindbar zu machen. Nutzer:innen müssen Informationen manuell über Navigation und Seitenstruktur suchen. Dadurch steigt der Aufwand insbesondere dann, wenn nur ein Teilbegriff bekannt ist oder ein Name falsch geschrieben wird.  
Die Suche soll global in der Kopfzeile verfügbar sein, damit sie auf allen Seiten konsistent nutzbar ist.

## Gewählte Lösung

In der oberen Leiste wird ein globales Suchfeld zwischen Titel („Klangland“) und Navigation integriert.  
Die Suche läuft gegen alle relevanten Daten aus dem [data](/Users/wolfram/workspaces/klangland/data)-Bestand und verwendet Fuzzy-Matching, um auch nahe Treffer (z. B. Tippfehler) zu liefern.  
Die Suche wird bei Eingabe automatisch ausgelöst, jedoch erst ab mindestens drei Zeichen, um zu kurze und wenig hilfreiche Anfragen zu vermeiden.

## Akzeptanzkriterien

1. **Globale Verfügbarkeit:** Das Suchfeld ist auf jeder Seite in der oberen Leiste sichtbar und nutzbar.
2. **Position und Darstellung:** Das Suchfeld steht zwischen „Klangland“ und der Navigation, nutzt den verfügbaren Platz und ist mit einem Suchsymbol als Suche erkennbar.
3. **Mindesteingabe:** Eine Suche wird erst ausgeführt, wenn mindestens drei Zeichen eingegeben wurden.
4. **Automatische Auslösung:** Ab der Mindesteingabe wird die Suche bei Eingabe automatisch gestartet, ohne separaten Such-Button.
5. **Suchraum:** Die Suche berücksichtigt alle relevanten Daten aus dem [data](/Users/wolfram/workspaces/klangland/data)-Verzeichnis.
6. **Fuzzy-Verhalten:** Nahe Treffer werden gefunden, z. B. führt „bethoven“ zu Treffern für „Beethoven“.

## Out of Scope

- Einführung einer erweiterten Suchsyntax (z. B. Operatoren wie AND/OR, Feldfilter).
- Ranking-Optimierung über eine grundlegende Fuzzy-Suche hinaus.
- Externe Suchdienste oder Indexierung außerhalb der lokalen Projektdaten.