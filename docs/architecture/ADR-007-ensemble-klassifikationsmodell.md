# ADR-007: Facettiertes Klassifikationsmodell für Ensembles

**Status:** accepted (2026-08-19)

## Evaluation criteria

**Summary:** Gesucht ist, wie Ensembles klassifiziert werden, damit unterschiedliche
professionelle Klangkörper – von Sinfonie- über Opernorchester bis zu Ensembles für Alte
Musik – einheitlich und flexibel dargestellt, gefiltert und ausgewertet werden können. Bisher
trug ein einzelnes `type`-Feld (`symphony_orchestra`, `philharmonic_orchestra`,
`radio_orchestra`, `opera_orchestra`) und ein Freitextfeld `artisticProfile` diese
Information vermischt.

**Specifics:**

- **Ausdruckskraft:** ein Ensemble kann gleichzeitig ein bestimmter Grundtyp sein, mehrere
  institutionelle Rollen erfüllen (z. B. Sinfonie- **und** Opernorchester) und mehrere
  musikalische Schwerpunkte haben.
- **Trennschärfe:** „was für ein Ensemble" (Typ), „welche Aufgabe" (Rolle) und „welche
  Schwerpunkte" (Profil) sind unterschiedliche Sachverhalte und sollen nicht in ein Feld
  gepresst werden.
- **Auswertbarkeit:** Werte müssen kontrolliert (Wertelisten) sein, damit Filter, Suche und
  Auswertungen konsistent funktionieren.
- **Erweiterbarkeit:** neue Ensemble-Typen (Kammerorchester, Chöre, Big Bands …) ohne
  Modellbruch.
- **Prüfbarkeit:** kontrollierte Werte maschinell (TypeScript-Union-Typen, Validierung)
  gegen den Wertebereich prüfbar.

## Candidates to consider

**Summary:** Kandidaten unterscheiden sich darin, ob Klassifikation in einem flachen Feld,
in getrennten Facetten oder in einer ungegliederten Tag-Liste abgebildet wird.

1. **Einzelnes flaches `type`** (Status quo): ein Wert je Ensemble, zusätzlich Freitext
   `artisticProfile`.
2. **Getrennte Facetten** `type` (Grundtyp, 1 Wert), `professional` (Flag), `roles`
   (0..n) und `musicalProfiles` (0..n), jeweils kontrollierte Wertelisten.
3. **Frei kombinierbare Tag-Liste** ohne Facettentrennung: eine Menge Tags je Ensemble.

## Research and analysis of each candidate

**Einzelnes flaches `type` (verworfen)**

- Kann Doppelrollen (Sinfonie- und Opernorchester) nicht abbilden; vermischt Grundtyp und
  Rolle. Musikalische Schwerpunkte lagen nur als deutscher Freitext (`artisticProfile`) vor
  und waren daher nicht konsistent auswertbar.
- SWOT: **S** einfach. **W** keine Mehrfachrollen, keine kontrollierten Profile, geringe
  Auswertbarkeit. **T** heterogene Freitextwerte verhindern Filter/Suche.

**Getrennte Facetten (gewählt)**

- Bildet alle Kriterien ab: `type` als grober Grundtyp, `roles` und `musicalProfiles` als
  Mehrfachwerte, `professional` als eigenes Flag. Alle Facetten sind kontrollierte
  Wertelisten, in `models.ts`, `labels.ts`, `entities/ensembles.md` und den Daten identisch
  gehalten und über TypeScript-Union-Typen erzwungen.
- Cost: mehr Felder und eine Migration der Bestandsdaten (`type` → `roles`,
  `artisticProfile` → `musicalProfiles`).
- SWOT: **S** trennscharf, mehrfachwertig, auswertbar, erweiterbar. **W** höhere
  Pflegekomplexität (mehrere Wertelisten synchron halten). **O** Grundlage für spätere
  Filter/Suche (US-011). **T** Wertelisten müssen konsistent gepflegt werden.

**Frei kombinierbare Tag-Liste (verworfen)**

- Flexibel, aber ohne Facettentrennung ist nicht maschinell unterscheidbar, ob ein Tag den
  Typ, eine Rolle oder ein Profil meint. Auswertungen und gezielte Filter werden dadurch
  unzuverlässig.
- SWOT: **S** maximal flexibel. **W** keine Semantik je Facette, schlechte Auswertbarkeit.

## Recommendation

**Summary:** Facettiertes Modell mit getrennten, kontrollierten Feldern `type` (Grundtyp),
`professional` (Flag), `roles` (0..n) und `musicalProfiles` (0..n); Ablösung des bisherigen
Freitextfelds `artisticProfile` durch `musicalProfiles`.

**Specifics:** Das heutige `type` beschreibt eine institutionelle Rolle und wandert nach
`roles`; das neue `type` ist ein grober Grundtyp (`orchestra`, `chamber_orchestra`,
`ensemble`, `big_band`, `chorus`, `vocal_ensemble`). Die maßgeblichen Wertelisten stehen in
[entities/ensembles.md](../entities/ensembles.md) und werden in `models.ts` und `labels.ts`
gespiegelt. Nicht auf ein Profil abbildbare Freitext-Nuancen (z. B. „Familienkonzerte",
„Landesorchester", „Nachwuchsarbeit") gehen bei der Migration bewusst nicht in
`musicalProfiles`, sondern dürfen bei Bedarf in `description` formuliert werden.

Dieses ADR **konkretisiert** die in
[ADR-003](ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md) genannte Erweiterbarkeit
(„neue Ensemble-Typen") für die Ensemble-Klassifikation; es supersedet ADR-003 nicht.
