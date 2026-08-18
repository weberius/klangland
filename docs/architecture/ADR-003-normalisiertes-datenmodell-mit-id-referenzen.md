# ADR-003: Normalisiertes Datenmodell mit getrennten Dateien und ID-Referenzen

**Status:** accepted (2026-08-18)

## Evaluation criteria

**Summary:** Gesucht ist die Struktur des Datenmodells: wie Entitäten (Personen,
Institutionen, Ensembles, Venues, Cities, Composers, Works, Events) abgelegt und miteinander
verknüpft werden. Das Modell soll über den Kalender hinaus als Klangland-Datenplattform
tragfähig sein.

**Specifics:**

- **Konsistenz:** ein Stammdatum (z. B. Venue-Name) darf nur an **einer** Stelle
  gepflegt werden.
- **Historische Stabilität:** Korrekturen an Stammdaten dürfen vergangene Events nicht
  verfälschen.
- **Erweiterbarkeit:** neue Ensemble-Typen (Chöre, Kammer-, Opernorchester) und spätere
  Ansichten (Venue-Profile) ohne Modellbruch.
- **Prüfbarkeit:** referenzielle Integrität maschinell validierbar.
- **Verarbeitbarkeit im Browser:** effiziente Auflösung von Beziehungen zur Laufzeit.

## Candidates to consider

**Summary:** Kandidaten unterscheiden sich im Grad der Normalisierung und in der
Datei-Aufteilung.

1. **Normalisiert, getrennte Dateien je Entität, Beziehungen nur über IDs.**
2. **Denormalisiert / eingebettet:** Events enthalten Ensemble-, Venue- und Werkdaten
   inline.
3. **Eine große Datei mit allen Arrays**, aber weiterhin ID-Referenzen.

## Research and analysis of each candidate

**Normalisiert + getrennte Dateien + ID-Referenzen**

- Erfüllt alle Kriterien: jede Entität hat eine Datei und eine Quelle; Referenzen laufen
  ausschließlich über stabile `kebab-case`-IDs; Stammdaten werden nie in referenzierenden
  Objekten dupliziert. Namenkorrekturen wirken zentral, ohne Events zu berühren.
- Cost: höherer Aufwand beim Erfassen (IDs anlegen, Referenzen setzen) und beim Auflösen im
  Client; dafür deutlich geringere Wartungskosten.
- SWOT: **S** konsistent, erweiterbar, diff-arme Änderungen, klare Zuständigkeit je Datei.
  **W** referenzielle Integrität muss aktiv geprüft werden (Doppelbeziehungen
  Institution↔Ensemble, Venue↔Institution). **O** trägt spätere Filter/Profile ohne
  Umbau. **T** verwaiste Referenzen bei unsauberer Pflege.

**Denormalisiert / eingebettet**

- Verfehlt Konsistenz und historische Stabilität: dieselben Stammdaten liegen in vielen
  Events; eine Korrektur müsste überall nachgezogen werden und verändert Historie.
- SWOT: **S** einfache Einzelabfrage. **W** massive Redundanz, Update-Anomalien.

**Eine große Datei mit ID-Referenzen**

- Referenzsemantik ok, aber schlechtere Trennung von Zuständigkeit/Quelle je Entität und
  größere Merge-Konflikte. Getrennte Dateien sind reviewfreundlicher.

**Opinions/feedback:** `docs/data-model.md` (Grundprinzipien, Referenz-Matrix, Ortsbezug)
und die Entitäts-Detaildokus legen dieses Modell fest. Der `DataService` indexiert jede
Entität nach ID in eine `Map` und bietet beziehungsauflösende Helfer – exakt der
normalisierte Ansatz. Ortsangaben sind vollständig über `cities.json` normalisiert;
Regionen sind bewusst Freitext.

## Recommendation

**Summary:** Normalisiertes Modell mit einer JSON-Datei je Entität und Beziehungen
ausschließlich über stabile IDs.

**Specifics:** Es gelten die in `docs/data-model.md` dokumentierten Konventionen: stabile,
nie wiederverwendete `kebab-case`-IDs (Umlaut-Transliteration), Event-IDs nach Muster
`event-YYYY-MM-DD-<ort>-<kurztitel>`, Trennung Stammdaten vs. Ereignisdaten. Die
referenzielle Integrität (inkl. der beiden Doppelbeziehungen) wird durch den geplanten
Validator abgesichert (PRD §16). Wiederkehrende Konzerte werden bewusst als einzelne Events
gespeichert statt über eine Recurrence-Engine (PRD §15).
