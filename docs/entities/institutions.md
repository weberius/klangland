# Institutionen (`institutions.json`)

## Zweck

Eine `institution` ist der **Träger bzw. Veranstalter**, der ein oder mehrere Ensembles
trägt und/oder Spielstätten betreibt – etwa ein Theater, ein Opernhaus, eine
Rundfunkanstalt oder eine eigenständige Orchestergesellschaft. Die Institution bündelt die
organisatorische Verantwortung; sie ist kein Ort und kein klingendes Ensemble.

## Datei

`data/institutions.json` – Metadaten-Umschlag mit Array `institutions` (siehe
[data-model.md](../data-model.md#metadaten-umschlag)).

## Beispiel

```json
{
  "id": "deutsche-oper-am-rhein",
  "name": "Deutsche Oper am Rhein",
  "cityIds": ["duisburg", "duesseldorf"],
  "region": null,
  "type": "opera_house",
  "ensembleIds": ["duisburger-philharmoniker", "duesseldorfer-symphoniker"]
}
```

## Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `name` | ja | string | Offizieller Name des Trägers/Veranstalters. |
| `cityIds` | ja | string[] | Sitzort(e); Referenz(en) auf [`cities.id`](cities.md). Doppelsitze als zwei Einträge (z. B. `["krefeld", "moenchengladbach"]`). |
| `region` | ja | string \| null | Übergeordnete Region als Freitext (z. B. `Ruhrgebiet`, `Südwestfalen`, `Bergisches Land`), falls zutreffend; sonst `null`. Keine City. |
| `type` | ja | enum | Art der Institution. |
| `ensembleIds` | ja | string[] | Getragene Ensembles; Referenz auf [`ensembles.id`](ensembles.md). |

## Kontrollierte Werte: `type`

| Wert | Bedeutung |
| --- | --- |
| `theatre` | Stadt-/Stadttheater mit Musiktheater- und Konzertbetrieb |
| `opera_house` | Opernhaus |
| `broadcaster` | Rundfunkanstalt (z. B. WDR) |
| `orchestra_institution` | Eigenständige Orchestergesellschaft/-institution |
| `cultural_institution` | Sonstige kulturelle Trägerorganisation |

## Beziehungen

- **Institution → Ensemble:** über `ensembleIds[]`. Eine Institution kann mehrere
  Ensembles tragen (z. B. Deutsche Oper am Rhein → Duisburger + Düsseldorfer).
- **Venue → Institution:** [`venues.institutionId`](venues.md) verweist zurück auf die
  Institution, die die Spielstätte betreibt/verantwortet. Diese Beziehung ist die
  Gegenrichtung und wird **nicht** zusätzlich als Feld in der Institution gespeichert; die
  App/Validierung ermittelt die Venues einer Institution über `venues`.

Achtung Konsistenz: `ensembleIds` und die `institutionId` der Venues bilden zwei getrennte
Kanten. Die Validierung muss beide gegen die Zieldateien prüfen.

## Pflege und Validierung

- `id` eindeutig; `name`, `type` gesetzt; `cityIds` und `region` vorhanden (`region` darf `null` sein).
- `type` liegt im kontrollierten Wertebereich.
- Jede ID in `cityIds` existiert in `cities.json`.
- Jede ID in `ensembleIds` existiert in `ensembles.json`.
- Empfehlung: Jedes in `ensembles.json` vorhandene Ensemble wird von genau einer
  Institution getragen (kein verwaistes Ensemble).
