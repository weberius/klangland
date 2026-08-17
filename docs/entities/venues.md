# Spielstätten (`venues.json`)

## Zweck

Ein `venue` ist eine konkrete Spielstätte (Saal, Theater, Opernhaus). Venues sind
eigenständige Stammdaten mit Adresse, Koordinaten, Typ und Institutionenbezug. Dadurch
kann die App neben Ensembleprofilen auch Spielstättenprofile mit eigenem
Veranstaltungsprogramm anzeigen.

## Datei

`data/venues.json` – Metadaten-Umschlag mit Array `venues` (siehe
[data-model.md](../data-model.md#metadaten-umschlag)). Hinweis: Adressen und Koordinaten
sind derzeit noch nicht recherchiert und daher `null`.

## Beispiel

```json
{
  "id": "tonhalle-duesseldorf",
  "name": "Tonhalle Düsseldorf",
  "cityIds": ["duesseldorf"],
  "region": null,
  "address": null,
  "coordinates": null,
  "website": "https://www.tonhalle.de/",
  "type": "philharmonic_hall",
  "institutionId": "deutsche-oper-am-rhein"
}
```

## Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`). |
| `name` | ja | string | Name des Saals/der Spielstätte. |
| `cityIds` | ja | string[] | Ort(e); Referenz(en) auf [`cities.id`](cities.md). Physische Säle haben genau einen Eintrag; wechselnde Spielorte können `[]` haben. |
| `region` | ja | string \| null | Übergeordnete Region als Freitext (z. B. `Ruhrgebiet`), v. a. für ortsungebundene Spielstätten; sonst `null`. Keine City. |
| `address` | ja | string \| null | Postanschrift; noch nicht recherchiert (`null`). |
| `coordinates` | ja | object \| null | Geokoordinaten für die spätere Kartenansicht, erwartet `{ "lat": number, "lng": number }`; noch `null`. |
| `website` | ja | string \| null | Offizielle Website der Spielstätte. |
| `type` | ja | enum | Art der Spielstätte. |
| `institutionId` | ja | string \| null | Betreibende/verantwortliche Institution; Referenz auf [`institutions.id`](institutions.md). `null` bei Gast-/Fremdspielstätten ohne bekannten Träger (z. B. Kirchen, Parks, auswärtige Häuser). |

## Kontrollierte Werte: `type`

| Wert | Bedeutung |
| --- | --- |
| `concert_hall` | Konzerthaus/-saal |
| `philharmonic_hall` | Philharmonie |
| `theatre` | Theater |
| `opera_house` | Opernhaus |
| `other` | Sonstiges, inkl. wechselnder Spielorte (z. B. `wechselnde-spielstaetten-ruhrgebiet`) |

## Beziehungen

- **Venue → Institution:** `institutionId` → [`institutions`](institutions.md). Mehrere
  Venues können zur selben Institution gehören.
- **Ensemble → Venue:** [`ensembles.venueId`](ensembles.md) verweist auf den Stammsaal.
- **Event → Venue:** [`events.venueId`](../events-and-relations.md) verweist auf die
  konkrete Spielstätte einer Aufführung. Das Spielstättenprofil sammelt alle Events mit
  passender `venueId`.
- **Venue → City:** über `cityIds` → [`cities`](cities.md).

## Pflege und Validierung

- `id` eindeutig; `name`, `type`, `institutionId` gesetzt; `cityIds` und `region`
  vorhanden (`region` darf `null` sein).
- `type` liegt im kontrollierten Wertebereich.
- Jede ID in `cityIds` existiert in `cities.json`; `institutionId` existiert in `institutions.json`.
- `coordinates`, sofern gesetzt, enthält gültige `lat`/`lng`-Werte.
