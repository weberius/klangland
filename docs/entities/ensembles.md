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
  "type": "radio_orchestra",
  "cityIds": ["koeln"],
  "region": null,
  "country": "Deutschland",
  "chiefConductorPersonId": "marie-jacquot",
  "artisticProfile": ["Sinfonik", "20. Jahrhundert", "Neue Musik", "Uraufführungen"],
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
| `type` | ja | enum | Art des Ensembles. |
| `cityIds` | ja | string[] | Sitzort(e); Referenz(en) auf [`cities.id`](cities.md). Doppelsitze als zwei Einträge. |
| `region` | ja | string \| null | Übergeordnete Region als Freitext (z. B. `Ruhrgebiet`, `Südwestfalen`), falls zutreffend; sonst `null`. Keine City. |
| `country` | ja | string | Land, derzeit stets `Deutschland`. |
| `chiefConductorPersonId` | ja | string \| null | Chefdirigent:in; Referenz auf [`people.id`](people.md). |
| `artisticProfile` | ja | string[] | Schlagworte zum künstlerischen Profil (für Filter/Anzeige). |
| `description` | ja | string \| null | Kurzbeschreibung für das Ensembleprofil. |
| `website` | ja | string \| null | Offizielle Website. |
| `venueId` | ja | string \| null | Stammsaal/wichtigste Spielstätte; Referenz auf [`venues.id`](venues.md). |
| `source` | ja | string \| null | Quelle der Stammdaten (URL). |

`null` ist bei `chiefConductorPersonId`, `description`, `website`, `venueId` und `source`
zulässig, wenn die Angabe noch nicht recherchiert ist.

## Kontrollierte Werte: `type`

| Wert | Bedeutung |
| --- | --- |
| `symphony_orchestra` | Sinfonieorchester |
| `philharmonic_orchestra` | Philharmonisches Orchester |
| `radio_orchestra` | Rundfunkorchester |
| `opera_orchestra` | Opernorchester |

Weitere Werte (z. B. `chamber_orchestra`, `choir`) werden bei Bedarf ergänzt.

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

- `id` eindeutig; `name`, `type`, `country` gesetzt; `cityIds` und `region` vorhanden
  (`region` darf `null` sein).
- `type` liegt im kontrollierten Wertebereich.
- Referenzielle Integrität: jede ID in `cityIds` existiert in `cities.json`;
  `chiefConductorPersonId` (falls gesetzt) existiert in `people.json`; `venueId` (falls
  gesetzt) existiert in `venues.json`.
- Empfehlung: Jedes Ensemble wird von genau einer Institution getragen.
