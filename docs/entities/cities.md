# Städte/Orte (`cities.json`)

## Zweck

Eine `city` ist eine eigenständige, normalisierte Ortsreferenz. Sie ist die **einzige
maßgebliche Quelle für Orte** im Datenmodell: Events, Institutionen, Ensembles und
Spielstätten referenzieren Orte ausschließlich über `cityId`/`cityIds`, nicht als Freitext.
Das erlaubt konsistente Ortsnamen in App und Filtern und deckt auch Open-Air-Orte ohne
klassische Venue ab.

## Datei

`data/cities.json` – Metadaten-Umschlag mit Array `cities` (siehe
[data-model.md](../data-model.md#metadaten-umschlag)). Der Bestand enthält alle Sitzorte der
erfassten Institutionen, Ensembles und Spielstätten sowie die von Events referenzierten Orte.

## Beispiel

Ein reiner Veranstaltungsort (ohne ansässiges Ensemble):

```json
{
  "id": "duesseldorf",
  "name": "Düsseldorf",
  "country": "Deutschland"
}
```

Eine Stadt mit ansässigem Ensemble trägt zusätzlich Kennzeichen und Koordinaten:

```json
{
  "id": "koeln",
  "name": "Köln",
  "country": "Deutschland",
  "plate": "K",
  "coordinates": { "lat": 50.93866, "lng": 6.95995 }
}
```

## Felder

| Feld | Pflicht | Typ | Bedeutung |
| --- | --- | --- | --- |
| `id` | ja | string | Stabile Klangland-ID (`kebab-case`, ASCII-transliteriert). |
| `name` | ja | string | Anzeigename des Ortes inkl. Diakritika. |
| `country` | ja | string | Land, derzeit stets `Deutschland`. |
| `plate` | optional | string | Kfz-Kennzeichen der Stadt (z. B. Köln → `K`). Nur für Städte mit ansässigem Ensemble gepflegt; beschriftet die Ort-Filter-Bubbles (US-011). Städte ohne Kennzeichen erzeugen keine Bubble. |
| `coordinates` | optional | object | Geokoordinaten der **Stadt selbst** (nicht einer Spielstätte), Form `{ "lat": number, "lng": number }`. Nur für Städte mit ansässigem Ensemble gepflegt; Grundlage der roten Kartenmarker (US-013). Per Overpass-API recherchiert (siehe [`geocode_cities.py`](../data-tooling/geocode_cities.py)). |

`plate` und `coordinates` sind bewusst nur für **Ensemble-Orte** gepflegt: Die Ort-Filter-Bubbles
und die Karte zeigen ausschließlich Städte mit mindestens einem ansässigen Ensemble. Reine
Veranstaltungsorte (nur über Events referenziert) bleiben ohne beide Felder.

## Städte sind Orte, keine Regionen

`cities` enthält ausschließlich echte Städte/Gemeinden. Übergeordnete Regionen wie
`Ruhrgebiet`, `Südwestfalen` oder `Bergisches Land` sind **keine** Cities; sie werden bei
den Stammdaten im separaten Feld `region` geführt (siehe
[institutions.md](institutions.md), [ensembles.md](ensembles.md), [venues.md](venues.md)).

## Beziehungen

- **Event → City:** [`events.cityId`](../events-and-relations.md) verweist auf genau eine City.
- **Institution/Ensemble/Venue → City:** `cityIds[]` verweist auf eine oder mehrere Cities
  (Doppelsitze wie Krefeld/Mönchengladbach werden als zwei Einträge abgebildet). Eine leere
  Liste ist zulässig für Entitäten ohne festen Ort (z. B. wechselnde Spielstätten).

## Pflege und Validierung

- `id` eindeutig; `name`, `country` gesetzt.
- Jede `cityId`/jeder Eintrag in `cityIds` aus anderen Dateien existiert hier.
- `cities` enthält keine Regionen (diese gehören in `region`).
- `plate`, sofern gesetzt, ist das korrekte Kfz-Kennzeichen; `coordinates`, sofern gesetzt,
  enthält gültige `lat`/`lng`-Werte. Beide sind für jede Stadt mit ansässigem Ensemble erwartet.
