# US-018 – Umsetzungs-Tasks

Umsetzung von [US-018](./US-018-profile.md): Ensembles anhand von **`type`**,
**`professional`**, **`roles`** und **`musicalProfiles`** klassifizieren. Das heutige
`type` (`symphony_orchestra`, `philharmonic_orchestra`, `radio_orchestra`,
`opera_orchestra`) beschreibt eine **institutionelle Rolle** und wandert nach `roles`; das
neue `type` wird ein **grober Grundtyp** (`orchestra`, …). Das bisherige Freitextfeld
`artisticProfile` wird durch die kontrollierte Liste `musicalProfiles` **ersetzt** (Werte
werden migriert, siehe [Task 5](#task-5--datenmigration-dataensemblesjson)).

## Modell-Entscheidung (verbindlich für alle Tasks)

- `type` – **was** für ein Ensemble es ist (genau ein Wert):
  `orchestra`, `chamber_orchestra`, `ensemble`, `big_band`, `chorus`, `vocal_ensemble`.
- `professional` – `boolean`, ob professionelles Ensemble.
- `roles` – **welche institutionelle/funktionale Aufgabe** (0..n):
  `symphony_orchestra`, `philharmonic_orchestra`, `radio_orchestra`, `opera_orchestra`,
  `theater_orchestra`, `state_orchestra`.
- `musicalProfiles` – **musikalische Schwerpunkte** (0..n):
  `classical`, `romantic`, `baroque`, `early_music`,
  `historically_informed_performance`, `contemporary`, `new_music`, `opera`, `musical`,
  `film_music`, `game_music`, `jazz`, `crossover`, `entertainment`, `choral`, `vocal`.
- `artisticProfile` (Freitext) **entfällt**; nicht auf eine Profil-Wert abbildbare
  Nuancen (z. B. „Familienkonzerte", „Landesorchester", „Nachwuchsarbeit") gehen bei der
  Migration bewusst nicht in `musicalProfiles`, sondern dürfen bei Bedarf in `description`
  formuliert werden.

Diese Werte sind die **kontrollierten Wertelisten** (AK 6) und müssen in models.ts,
labels.ts, der Entity-Doku und der Validierung identisch sein.

Betroffene Dateien:
- [docs/architecture/README.md](../../../architecture/README.md) + neues ADR-007
- [docs/entities/ensembles.md](../../../entities/ensembles.md)
- [docs/data-model.md](../../../data-model.md)
- [docs/product/contracts/ensembles.feature](../../contracts/ensembles.feature)
- [docs/product/ears/ensembles.md](../../ears/ensembles.md)
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts)
- [web/src/app/core/labels.ts](../../../../web/src/app/core/labels.ts)
- [web/src/app/pages/ensemble-list/ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts)
- [web/src/app/pages/ensemble-list/ensemble-list.html](../../../../web/src/app/pages/ensemble-list/ensemble-list.html)
- [web/src/app/pages/ensemble-detail/ensemble-detail.ts](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.ts)
- [web/src/app/pages/ensemble-detail/ensemble-detail.html](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html)
- [data/ensembles.json](../../../../data/ensembles.json)

---

## Task 1 – ADR für das Ensemble-Klassifikationsmodell

- Neues **ADR-007** anlegen: `docs/architecture/ADR-007-ensemble-klassifikationsmodell.md`
  (nächste freie Nummer, Format wie
  [ADR-003](../../../architecture/ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md):
  Titel, Status `accepted (2026-08-19)`, Evaluation criteria, Candidates, Analyse/SWOT,
  Recommendation).
- Kern der Entscheidung dokumentieren: **Trennung** von `type` (was), `roles` (Funktion)
  und `musicalProfiles` (Schwerpunkte) statt eines einzelnen `type`; `professional` als
  eigenes Flag; kontrollierte Wertelisten für Filter/Suche/Auswertung; **Ablösung** von
  `artisticProfile` durch `musicalProfiles`.
- Kandidaten mind.: (a) einzelnes flaches `type` (Status quo, verworfen), (b) getrennte
  Facetten `type`/`roles`/`musicalProfiles` (gewählt), (c) frei kombinierbare Tag-Liste
  ohne Facettentrennung (verworfen, keine Auswertbarkeit).
- Hinweis aufnehmen, dass dieses ADR die Ensemble-Typ-Festlegung aus
  [ADR-003](../../../architecture/ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md)
  (Erweiterbarkeit „neue Ensemble-Typen") **konkretisiert**, sie nicht supersedet.
- Übersichtstabelle in [architecture/README.md](../../../architecture/README.md) um die
  ADR-007-Zeile ergänzen.
- **Deckt ab:** AK 5 (getrennte Modellierung), AK 6 (kontrollierte Werte).

## Task 2 – Entity-Definition aktualisieren (docs/entities/ensembles.md)

- Feldtabelle anpassen:
  - `type` → Bedeutung „Grundtyp des Ensembles" (kontrolliert, s. u.).
  - **Neu** `professional` (Pflicht, `boolean`).
  - **Neu** `roles` (Pflicht, `string[]`, kontrolliert; darf `[]` sein).
  - **Neu** `musicalProfiles` (Pflicht, `string[]`, kontrolliert; darf `[]` sein).
  - `artisticProfile`-Zeile **entfernen**.
- Drei „Kontrollierte Werte"-Tabellen ergänzen/ersetzen: `type`, `roles`,
  `musicalProfiles` – exakt die Werte aus der Modell-Entscheidung oben, jeweils mit
  deutscher Bedeutung.
- Distinktion `type` vs. `roles` vs. `musicalProfiles` als Fließtext beschreiben (aus der
  User Story übernehmen). Beispiel-JSON auf das neue Schema umstellen (inkl.
  `professional`, `roles`, `musicalProfiles`; ohne `artisticProfile`).
- Abschnitt „Pflege und Validierung": `type`, jeder Wert in `roles` und in
  `musicalProfiles` liegen im kontrollierten Wertebereich.
- **Deckt ab:** AK 1–7. **Sync-Anker:** Werte hier müssen 1:1 zu Task 3/4 passen.

## Task 3 – TypeScript-Modell aktualisieren (models.ts)

- In [models.ts](../../../../web/src/app/models/models.ts):
  - `EnsembleType` neu definieren:
    `'orchestra' | 'chamber_orchestra' | 'ensemble' | 'big_band' | 'chorus' | 'vocal_ensemble'`.
  - **Neu** `EnsembleRole =
    'symphony_orchestra' | 'philharmonic_orchestra' | 'radio_orchestra' | 'opera_orchestra' | 'theater_orchestra' | 'state_orchestra'`.
  - **Neu** `MusicalProfile` = Union der 16 Profil-Werte aus der Modell-Entscheidung.
  - Interface `Ensemble`: `type: EnsembleType` beibehalten; **`professional: boolean`**,
    **`roles: EnsembleRole[]`**, **`musicalProfiles: MusicalProfile[]`** ergänzen;
    **`artisticProfile` entfernen**.
- **Deckt ab:** AK 1–7 (Datenmodell). **Sync-Anker:** Union-Typen müssen zu Task 2 passen.

## Task 4 – Anzeige-Labels aktualisieren (labels.ts)

- In [labels.ts](../../../../web/src/app/core/labels.ts):
  - `ENSEMBLE_TYPE_LABELS: Record<EnsembleType, string>` auf die neuen `type`-Werte
    umstellen (z. B. `orchestra: 'Orchester'`, `chamber_orchestra: 'Kammerorchester'`,
    `ensemble: 'Ensemble'`, `big_band: 'Big Band'`, `chorus: 'Chor'`,
    `vocal_ensemble: 'Vokalensemble'`).
  - **Neu** `ENSEMBLE_ROLE_LABELS: Record<EnsembleRole, string>` (z. B.
    `symphony_orchestra: 'Sinfonieorchester'`, `philharmonic_orchestra: 'Philharmonisches Orchester'`,
    `radio_orchestra: 'Rundfunkorchester'`, `opera_orchestra: 'Opernorchester'`,
    `theater_orchestra: 'Theaterorchester'`, `state_orchestra: 'Landesorchester'`).
  - **Neu** `MUSICAL_PROFILE_LABELS: Record<MusicalProfile, string>` (deutsche Labels für
    alle 16 Werte, z. B. `classical: 'Klassik'`, `romantic: 'Romantik'`,
    `historically_informed_performance: 'Historische Aufführungspraxis'`,
    `new_music: 'Neue Musik'`, `choral: 'Chormusik'`, …).
- Vorhandene `label(...)`-Helper-Signatur unverändert lassen.
- **Deckt ab:** AK 6 (konsistente Anzeige der kontrollierten Werte).

## Task 5 – Datenmigration (data/ensembles.json)

- Alle 17 Ensembles auf das neue Schema umstellen: `professional: true` (Scope =
  professionelle Ensembles), `type: "orchestra"`, altes `type` → passender `roles`-Eintrag,
  `artisticProfile` → `musicalProfiles` gemäß Tabelle. `artisticProfile`-Schlüssel
  entfernen. `metadata.version` auf `1.2`, `metadata.lastUpdated` auf `2026-08-19` setzen.
- **Migrationstabelle** (`type` für alle = `orchestra`, `professional` = `true`):

  | id | roles | musicalProfiles |
  | --- | --- | --- |
  | sinfonieorchester-aachen | symphony_orchestra, opera_orchestra | classical, romantic, opera |
  | bielefelder-philharmoniker | philharmonic_orchestra, opera_orchestra | contemporary, new_music, opera |
  | bochumer-symphoniker | symphony_orchestra | classical, romantic, new_music |
  | beethoven-orchester-bonn | symphony_orchestra, opera_orchestra | classical, historically_informed_performance |
  | dortmunder-philharmoniker | philharmonic_orchestra, opera_orchestra | contemporary |
  | duisburger-philharmoniker | philharmonic_orchestra, opera_orchestra | romantic, opera, new_music |
  | duesseldorfer-symphoniker | symphony_orchestra, opera_orchestra | classical, romantic, contemporary, opera |
  | essener-philharmoniker | philharmonic_orchestra, opera_orchestra | classical, romantic, opera, choral, contemporary |
  | philharmonisches-orchester-hagen | philharmonic_orchestra, opera_orchestra | romantic, opera |
  | guerzenich-orchester-koeln | symphony_orchestra, opera_orchestra | romantic, contemporary, new_music, opera |
  | wdr-sinfonieorchester | radio_orchestra, symphony_orchestra | contemporary, new_music |
  | niederrheinische-sinfoniker | symphony_orchestra, opera_orchestra | classical, romantic, opera |
  | sinfonieorchester-muenster | symphony_orchestra, opera_orchestra | classical, romantic, opera, choral |
  | neue-philharmonie-westfalen | philharmonic_orchestra, opera_orchestra | classical, romantic |
  | philharmonie-suedwestfalen | symphony_orchestra, state_orchestra | classical, romantic |
  | bergische-symphoniker | symphony_orchestra | classical, romantic, contemporary |
  | sinfonieorchester-wuppertal | symphony_orchestra, opera_orchestra | romantic, contemporary, opera |

- **Mapping-Regeln** (dokumentiert, falls neue Ensembles hinzukommen):
  Name „Philharmoniker/Philharmonie/Philharmonisches" → `philharmonic_orchestra`, sonst
  „Sinfonieorchester/Symphoniker/Sinfoniker" → `symphony_orchestra`; Rundfunk →
  zusätzlich `radio_orchestra`; Landesorchester → zusätzlich `state_orchestra`; spielt für
  ein Opern-/Musiktheaterhaus → zusätzlich `opera_orchestra`.
  Freitext→Profil: Klassik/Wiener Klassik/Beethoven→`classical`,
  Romantik/Spätromantik/Bruckner/Mahler→`romantic`, Barock→`baroque`, Alte
  Musik→`early_music`, Historische Aufführungspraxis→`historically_informed_performance`,
  Moderne/Zeitgenössische Musik/20./21. Jahrhundert→`contemporary`, Neue
  Musik/Uraufführungen→`new_music`, Oper/Musiktheater→`opera`, Chormusik/Chor→`choral`,
  Vokalmusik→`vocal`, Jazz→`jazz`, Musical→`musical`, Filmmusik→`film_music`,
  Spielemusik→`game_music`, Crossover→`crossover`, Unterhaltung→`entertainment`.
  Nicht-musikalische Freitextwerte (Formate, Vermittlung, Region) werden **verworfen**.
- **Deckt ab:** AK 1–4, AK 7 (mehrere Rollen/Profile je Ensemble). **Sync-Anker:** alle
  Werte müssen im Wertebereich von Task 3 liegen.

## Task 6 – Ensembleliste (ensemble-list.ts / .html)

- [ensemble-list.ts](../../../../web/src/app/pages/ensemble-list/ensemble-list.ts):
  `artisticProfile` nicht mehr verwenden. `typeLabel(e)` bleibt (jetzt Grundtyp). Optional
  Helfer `roleLabels(e)` / `profileLabels(e)` ergänzen (Arrays → deutsche Labels via
  `ENSEMBLE_ROLE_LABELS` / `MUSICAL_PROFILE_LABELS`).
- [ensemble-list.html](../../../../web/src/app/pages/ensemble-list/ensemble-list.html):
  Meta-Zeile `{{ cityName(e) }} · {{ typeLabel(e) }}` beibehalten; Tag-Liste von
  `e.artisticProfile` auf **`musicalProfiles`-Labels** umstellen (erste 3). Ggf. die
  Rolle(n) als zusätzliche Info anzeigen. `e.artisticProfile.length` durch
  `musicalProfiles.length` ersetzen.
- **Deckt ab:** AK 1, 3, 4, 6 (Anzeige der neuen Klassifikation).

## Task 7 – Ensembleprofil (ensemble-detail.ts / .html)

- [ensemble-detail.ts](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.ts):
  `ENSEMBLE_TYPE_LABELS` weiter für `typeLabel`; Helfer für `roles` und `musicalProfiles`
  ergänzen. Keine Referenz mehr auf `artisticProfile`.
- [ensemble-detail.html](../../../../web/src/app/pages/ensemble-detail/ensemble-detail.html):
  Tag-Block von `artisticProfile` auf `musicalProfiles`-Labels umstellen. Rollen z. B. in
  der Fakten-`<dl>` (`profile-facts`) als eigener Punkt „Rolle(n)" darstellen; Grundtyp in
  der Kopfzeile beibehalten.
- **Deckt ab:** AK 1, 3, 4, 6.

## Task 8 – Gherkin-Contract erweitern (ensembles.feature)

- In [ensembles.feature](../../contracts/ensembles.feature) eine neue `Rule` für die
  Klassifikation ergänzen (Format wie bestehende Szenarien, `# language: de`), z. B.:
  - Szenario: Grundtyp und Rolle(n) auf der Ensemblekarte/-profil sichtbar
    (z. B. „Beethoven Orchester Bonn" → Typ „Orchester", Rollen „Sinfonieorchester" und
    „Opernorchester").
  - Szenario: Musikalische Schwerpunkte werden als Profile angezeigt.
  - Szenario (AK 7): Ein Ensemble mit **mehreren** Rollen zeigt alle Rollen an.
- Nur beobachtbares Verhalten formulieren (keine Feldnamen/Implementierung).
- **Deckt ab:** AK 3, 4, 7.

## Task 9 – EARS-Anforderungen ergänzen (ears/ensembles.md)

- In [ears/ensembles.md](../../ears/ensembles.md) neue Anforderungen fortlaufend ergänzen
  (ENS-10 ff.), z. B.:
  - **ENS-10** (ubiquitär): Das Ensembleprofil MUSS den Grundtyp des Ensembles anzeigen.
  - **ENS-11** (zustandsgesteuert): SOLANGE einem Ensemble Rollen zugeordnet sind, MUSS
    das Ensembleprofil alle zugeordneten Rollen anzeigen.
  - **ENS-12** (zustandsgesteuert): SOLANGE einem Ensemble musikalische Profile zugeordnet
    sind, MUSS das Ensembleprofil diese anzeigen.
  - Formulierung im Stil der bestehenden EARS-Sätze; Verweis auf den Contract beibehalten.
- **Deckt ab:** AK 1, 3, 4, 5.

## Task 10 – Datenmodell-Doku/Validierung (data-model.md)

- In [data-model.md](../../../data-model.md) den Validierungsabschnitt „kontrollierte Werte"
  so ergänzen, dass neben `type` auch `roles` und `musicalProfiles` gegen ihre
  Wertebereiche geprüft werden (bestehende Aufzählung `type, role, genre, status,
  eventType` konsistent halten).
- Kurzverweis, dass die maßgeblichen Wertelisten in
  [entities/ensembles.md](../../../entities/ensembles.md) stehen.
- **Deckt ab:** AK 6.

## Task 11 – Verifikation & Abschluss

- `cd web && npm run build` – kompiliert fehlerfrei; TypeScript erzwingt über die neuen
  Union-Typen, dass models.ts, labels.ts und die Daten (via sync) zueinander passen.
- Prüfen, dass `data/ensembles.json` valides JSON ist und **kein** Ensemble mehr
  `artisticProfile` enthält; jedes Ensemble hat `type`, `professional`, `roles`,
  `musicalProfiles`.
- `cd web && npm start` und im Browser prüfen: Ensembleliste und -profil zeigen Grundtyp,
  Rollen und musikalische Profile korrekt; keine leeren/kaputten Tag-Listen.
- Kein Feld `artisticProfile` mehr im Code (grep im `web/src`-Verzeichnis).
- Story-Datei nach Abschluss von `inprogress/` nach `done/` verschieben und diese
  Tasks-Datei mitverschieben (Muster wie US-006/007/008).

## Definition of Done

- Akzeptanzkriterien 1–7 der User Story erfüllt.
- Entity-Definition ([entities/ensembles.md](../../../entities/ensembles.md)), Modell
  ([models.ts](../../../../web/src/app/models/models.ts)), Labels
  ([labels.ts](../../../../web/src/app/core/labels.ts)) und Daten
  ([ensembles.json](../../../../data/ensembles.json)) verwenden **identische** kontrollierte
  Wertelisten.
- ADR-007 angelegt und in der ADR-Übersicht verlinkt; Gherkin- und EARS-Artefakte
  ergänzt.
- `npm run build` ohne Fehler; JSON valide; kein `artisticProfile` mehr im Bestand/Code.
