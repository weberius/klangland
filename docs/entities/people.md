# Personen (`people.json`)

## Zweck

`people` beschreibt natürliche Personen, die in Klangland auftreten – Dirigent:innen und
Solist:innen. Eine Person ist ein reiner **Identitätsdatensatz** und enthält bewusst
**keine** Funktions- oder Rollenangabe: Welche Funktion eine Person hat, ergibt sich
ausschließlich aus der referenzierenden Entität (siehe [Beziehungen](#beziehungen)).
Dadurch lassen sich Gast-Dirigent:innen und Solist:innen ohne Änderung des Personenmodells
ergänzen.

## Datei

`data/people.json` – Metadaten-Umschlag mit Array `people` (siehe
[data-model.md](../data-model.md#metadaten-umschlag)).

## Beispiel

```json
{
  "id": "marie-jacquot",
  "name": "Marie Jacquot"
}
```

## Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `name` | ja | string | Anzeigename inkl. korrekter Diakritika (z. B. `Andrés Orozco-Estrada`). |

## Funktion statt Rolle

Das frühere Feld `role` wurde entfernt. Die Funktion einer Person ist **kontextabhängig**
und wird nicht dupliziert, sondern über Beziehungen bestimmt:

- **Chefdirigent:in:** eine Person ist Chefdirigent:in eines Ensembles genau dann, wenn ein
  [`ensembles.chiefConductorPersonId`](ensembles.md) auf sie zeigt.
- **Dirigent:in / Solist:in eines Konzerts:** ergibt sich aus
  [`events.conductorPersonIds` bzw. `events.soloistPersonIds`](../events-and-relations.md).

Dieselbe Person kann so in einem Event dirigieren und in einem anderen als Solist:in
auftreten, ohne dass das Personenmodell dies vorwegnehmen muss.

## Beziehungen

- **Ensemble → Person:** [`ensembles.chiefConductorPersonId`](ensembles.md).
- **Event → Person:** [`events.conductorPersonIds[]` und `events.soloistPersonIds[]`](../events-and-relations.md).

Eine Person kann von mehreren Ensembles und Events referenziert werden.

## Pflege und Validierung

- `id` eindeutig; `name` gesetzt.
- Kein `role`-Feld (bewusst entfernt).
- Referenzielle Integrität: Jede von Ensembles/Events referenzierte `personId` existiert
  hier. Personen ohne Referenz sind zulässig (Warnung statt Fehler).
