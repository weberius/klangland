# Ensembles (`ensembles.json`)

## Zweck

Ein `ensemble` ist ein klingender Klangkörper – Sinfonie-, Philharmonie-, Rundfunk- oder
Opernorchester, perspektivisch auch Kammerorchester, Chöre und andere Ensembles.
`ensembles` ist der Oberbegriff und ersetzt den früheren Begriff `orchestras`. Ensembles
sind Stammdaten und enthalten keine Konzerttermine; Termine stehen ausschließlich in
[`events.json`](../events-and-relations.md).

## Datei

`data/ensembles.json` – Metadaten-Umschlag mit Array `ensembles` (siehe
[data-model.md](../data-model.md#metadaten-umschlag)). Das `metadata`-Feld führt zusätzlich
`scope` zur Eingrenzung des Datenbestands.

## Beispiel

```json
{
  "id": "wdr-sinfonieorchester",
  "name": "WDR Sinfonieorchester",
  "type": "orchestra",
  "professional": true,
  "roles": ["radio_orchestra", "symphony_orchestra"],
  "musicalProfiles": ["contemporary", "new_music"],
  "cityIds": ["koeln"],
  "region": null,
  "country": "Deutschland",
  "chiefConductorPersonId": "marie-jacquot",
  "description": "Internationales Spitzenniveau mit Schwerpunkt auf Musik des 20. und 21. Jahrhunderts …",
  "website": "https://www1.wdr.de/orchester-und-chor/sinfonieorchester/",
  "venueId": "koelner-philharmonie",
  "source": "https://www1.wdr.de/…/jacquot-chefdirigentin-100.html"
}
```

## Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `name` | ja | string | Offizieller Name des Ensembles. |
| `type` | ja | enum | Grundtyp des Ensembles (was für ein Ensemble es ist). Kontrolliert, s. u. |
| `professional` | ja | boolean | Ob es sich um ein professionelles Ensemble handelt. |
| `roles` | ja | string[] | Institutionelle/funktionale Rolle(n); kontrolliert, s. u. Mehrfachwerte erlaubt; darf `[]` sein. |
| `musicalProfiles` | ja | string[] | Musikalische Schwerpunkte; kontrolliert, s. u. Mehrfachwerte erlaubt; darf `[]` sein. |
| `cityIds` | ja | string[] | Sitzort(e); Referenz(en) auf [`cities.id`](cities.md). Doppelsitze als zwei Einträge. |
| `region` | ja | string \| null | Übergeordnete Region als Freitext (z. B. `Ruhrgebiet`, `Südwestfalen`), falls zutreffend; sonst `null`. Keine City. |
| `country` | ja | string | Land, derzeit stets `Deutschland`. |
| `chiefConductorPersonId` | ja | string \| null | Chefdirigent:in; Referenz auf [`people.id`](people.md). |
| `description` | ja | string \| null | Kurzbeschreibung für das Ensembleprofil. |
| `website` | ja | string \| null | Offizielle Website. |
| `venueId` | ja | string \| null | Stammsaal/wichtigste Spielstätte; Referenz auf [`venues.id`](venues.md). |
| `source` | ja | string \| null | Quelle der Stammdaten (URL). |

`null` ist bei `chiefConductorPersonId`, `description`, `website`, `venueId` und `source`
zulässig, wenn die Angabe noch nicht recherchiert ist.

## Trennung von `type`, `roles` und `musicalProfiles`

`type`, `roles` und `musicalProfiles` werden bewusst getrennt modelliert, da sie
unterschiedliche Sachverhalte beschreiben:

- `type` beschreibt, **was für ein Ensemble** es ist (genau ein Wert).
- `roles` beschreibt, **welche institutionelle bzw. funktionale Aufgabe** es erfüllt.
- `musicalProfiles` beschreibt, **welche musikalischen Schwerpunkte** es besitzt.

Ein Ensemble kann mehrere Rollen und Profile gleichzeitig besitzen. Die Werte sind
kontrollierte Wertelisten, damit sie konsistent für Filter, Suche und Auswertungen
verwendet werden können.

## Kontrollierte Werte: `type`

| Wert | Bedeutung |
| --- | --- |
| `orchestra` | Orchester |
| `chamber_orchestra` | Kammerorchester |
| `ensemble` | Ensemble |
| `big_band` | Big Band |
| `chorus` | Chor |
| `vocal_ensemble` | Vokalensemble |

## Kontrollierte Werte: `roles`

| Wert | Bedeutung |
| --- | --- |
| `symphony_orchestra` | Sinfonieorchester |
| `philharmonic_orchestra` | Philharmonisches Orchester |
| `radio_orchestra` | Rundfunkorchester |
| `opera_orchestra` | Opernorchester |
| `theater_orchestra` | Theaterorchester |
| `state_orchestra` | Landesorchester |

## Kontrollierte Werte: `musicalProfiles`

| Wert | Bedeutung |
| --- | --- |
| `classical` | Klassik |
| `romantic` | Romantik |
| `baroque` | Barock |
| `early_music` | Alte Musik |
| `historically_informed_performance` | Historische Aufführungspraxis |
| `contemporary` | Zeitgenössische Musik |
| `new_music` | Neue Musik |
| `opera` | Oper |
| `musical` | Musical |
| `film_music` | Filmmusik |
| `game_music` | Spielemusik |
| `jazz` | Jazz |
| `crossover` | Crossover |
| `entertainment` | Unterhaltung |
| `choral` | Chormusik |
| `vocal` | Vokalmusik |

Weitere Werte werden bei Bedarf ergänzt und müssen zugleich in `models.ts`, `labels.ts`
und dieser Doku gepflegt werden.

## Beziehungen

- **Ensemble → Person:** `chiefConductorPersonId` → [`people`](people.md).
- **Ensemble → Venue:** `venueId` → [`venues`](venues.md) (Stammsaal). Ein Ensemble tritt
  darüber hinaus laut Events auch an anderen Venues auf.
- **Institution → Ensemble:** die tragende Institution referenziert das Ensemble über
  [`institutions.ensembleIds`](institutions.md). Es gibt bewusst **keinen**
  `institutionId`-Rückverweis im Ensemble; die Zugehörigkeit wird über die Institution
  ermittelt.
- **Event → Ensemble:** [`events.ensembleIds[]`](../events-and-relations.md) verweist auf
  Ensembles. Für das Ensembleprofil werden alle Events mit passender ID gesammelt.

## Pflege und Validierung

- `id` eindeutig; `name`, `type`, `professional`, `country` gesetzt; `roles` und
  `musicalProfiles` vorhanden (dürfen `[]` sein); `cityIds` und `region` vorhanden
  (`region` darf `null` sein).
- `type` liegt im kontrollierten Wertebereich; jeder Wert in `roles` und in
  `musicalProfiles` liegt im jeweils kontrollierten Wertebereich.
- Referenzielle Integrität: jede ID in `cityIds` existiert in `cities.json`;
  `chiefConductorPersonId` (falls gesetzt) existiert in `people.json`; `venueId` (falls
  gesetzt) existiert in `venues.json`.
- Empfehlung: Jedes Ensemble wird von genau einer Institution getragen.
