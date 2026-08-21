# User Story 022 - Adressen und Koordinaten für Spielstätten

## User Story

**Als** Betreiber:in von Klangland,
**möchte ich** für die Spielstätten (Venues) Postadresse und Geokoordinaten aus OpenStreetMap automatisch recherchieren und in den Stammdaten pflegen,
**damit** Spielstätten mit vollständiger Adresse dargestellt und später auf einer Karte verortet werden können, ohne jede Adresse von Hand suchen zu müssen.

## Kontext / Problem

Spielstätten sind eigenständige Stammdaten in [venues.json](../../../../data/venues.json) (siehe [venues.md](../../../../docs/entities/venues.md)). Das Modell [`Venue`](../../../../web/src/app/models/models.ts#L119-L128) kennt bereits die Felder `address` und `coordinates`, diese sind aber für alle Venues noch `null` – der Metadaten-Hinweis in [venues.json](../../../../data/venues.json) vermerkt ausdrücklich: „Adressen und Koordinaten sind noch nicht recherchiert und daher null." Damit fehlt sowohl die menschenlesbare Postanschrift als auch die Grundlage für eine spätere Kartenansicht der Spielstätten.

`address` ist heute als schlichter String (`string | null`) modelliert. Für eine strukturierte Darstellung (z. B. Straße/PLZ/Ort getrennt, spätere Filter- oder Kartenlogik) reicht das nicht aus; das Feld soll auf ein strukturiertes Objekt umgestellt werden.

Für Städte existiert bereits ein vergleichbares Geokodierungs-Skript ([geocode_cities.py](../../../../docs/data-tooling/geocode_cities.py) aus US-013), das über die Overpass-API von OpenStreetMap arbeitet, idempotent ist und eine Selbstbeschränkung von höchstens einer Abfrage pro Sekunde einhält. Diese Vorgehensweise dient als Vorbild.

Betroffen sind das `Venue`-Datenmodell, die Daten in [venues.json](../../../../data/venues.json), die Entity-Dokumentation [venues.md](../../../../docs/entities/venues.md) sowie ein neues Daten-Tooling-Skript unter [docs/data-tooling/](../../../../docs/data-tooling/). Die konkrete Darstellung der Adresse/Karte auf der Venue-Detailseite ([venue-detail](../../../../web/src/app/pages/venue-detail/)) ist **nicht** Teil dieser Story (nur die Datengrundlage wird geschaffen).

## Gewählte Lösung

### 1. Strukturiertes Adress-Modell

Das Feld `address` wird von `string | null` auf ein **strukturiertes Objekt** `Address | null` umgestellt, mit mindestens den Feldern Straße, Hausnummer, Postleitzahl und Ort:

```ts
interface Address {
  street: string | null;
  houseNumber: string | null;
  postalCode: string | null;
  city: string | null;
}
```

`coordinates` bleibt wie bisher `{ lat: number; lng: number } | null`. Das Modell [`Venue`](../../../../web/src/app/models/models.ts#L119-L128), die Daten in [venues.json](../../../../data/venues.json) und die Dokumentation [venues.md](../../../../docs/entities/venues.md) werden entsprechend angepasst. Venues ohne recherchierte Adresse/Koordinaten bleiben mit `null` valide.

### 2. Python-Recherche-Skript auf Basis von OpenStreetMap

Ein neues Python-Skript unter [docs/data-tooling/](../../../../docs/data-tooling/) (analog zu [geocode_cities.py](../../../../docs/data-tooling/geocode_cities.py)) ermittelt für jede Spielstätte Adresse und Koordinaten aus OpenStreetMap:

* Als Quelle dient das **OSM-Ökosystem**: die **Overpass-API** für die Zuordnung/Koordinaten der Spielstätte sowie **Nominatim** (ebenfalls OSM) für eine vollständige, saubere Postadresse. OSM ist **keine Laufzeitabhängigkeit** der Webanwendung – die Daten werden einmalig recherchiert und in [venues.json](../../../../data/venues.json) gespeichert.
* **Schonender Abruf:** Es wird höchstens **eine Abfrage pro Sekunde** ausgeführt (Selbstbeschränkung), um die OSM-Infrastruktur nicht zu belasten. Bei Drosselung (z. B. HTTP 429/504) wartet das Skript zusätzlich (Backoff) und wiederholt.
* Die Suche wird über Name und zugeordnete Stadt (`cityIds` → [cities.json](../../../../data/cities.json)) präzisiert und – dem Projekt-Scope folgend – auf Nordrhein-Westfalen bzw. die jeweilige Stadt eingegrenzt, um Fehltreffer auf gleichnamige Orte zu vermeiden.
* Das Skript ist **idempotent**: bereits gefüllte Felder werden standardmäßig nicht erneut abgefragt; ein `--force`-Schalter erzwingt die Neuermittlung.

### 3. Umgang mit nicht auflösbaren Spielstätten

Lässt sich eine Spielstätte nicht eindeutig auflösen (generische Namen, ortsungebundene/„wechselnde" Spielstätten mit `cityIds: []`, fehlende OSM-Daten), bleiben `address` und/oder `coordinates` auf `null`. Das Skript **überschreibt keine** bereits vorhandenen Werte mit `null` und listet die nicht aufgelösten Venues am Ende in einem **Bericht** auf. Eine manuelle Nachpflege dieser Fälle ist nicht Teil dieser Story.

### 4. Erstbefüllung der Daten

Im Rahmen dieser Story wird das Skript für alle aktuell in [venues.json](../../../../data/venues.json) erfassten Spielstätten ausgeführt und die Ergebnisse als Daten committet. Der Metadaten-Hinweis in [venues.json](../../../../data/venues.json) wird entsprechend aktualisiert.

## Akzeptanzkriterien

1. **Strukturiertes Adress-Modell:** Das `Venue`-Modell modelliert `address` als strukturiertes Objekt `Address | null` mit mindestens Straße, Hausnummer, Postleitzahl und Ort. `coordinates` bleibt `{ lat, lng } | null`. Venues ohne Adresse/Koordinaten (`null`) bleiben valide.
2. **Modell, Daten und Doku konsistent:** [venues.json](../../../../data/venues.json) und die Dokumentation [venues.md](../../../../docs/entities/venues.md) entsprechen dem neuen `address`-Format; bestehende Referenzen/Beispiele sind angepasst.
3. **Recherche-Skript vorhanden:** Ein ausführbares Python-Skript unter [docs/data-tooling/](../../../../docs/data-tooling/) ermittelt für Spielstätten Adresse und Koordinaten aus OpenStreetMap (Overpass für Zuordnung/Koordinaten, Nominatim für die Postadresse) und schreibt sie nach [venues.json](../../../../data/venues.json).
4. **Keine Laufzeitabhängigkeit:** Die Webanwendung greift zur Laufzeit **nicht** auf Overpass/Nominatim/OSM zu; die Recherche erfolgt ausschließlich über das Skript.
5. **Rate-Limit:** Das Skript führt höchstens **eine Abfrage pro Sekunde** aus. Bei Drosselung (HTTP 429/504) wird mit wachsender Wartezeit erneut versucht.
6. **Idempotenz / kein Datenverlust:** Ein erneuter Lauf fragt bereits gefüllte Felder standardmäßig nicht erneut ab und überschreibt vorhandene Werte nicht mit `null`. Ein `--force`-Schalter erzwingt die Neuermittlung.
7. **Präzise Zuordnung:** Die Suche nutzt Name und `cityIds` und ist auf den Projekt-Scope (NRW/Stadt) eingegrenzt, sodass gleichnamige Orte nicht fälschlich getroffen werden.
8. **Nicht auflösbare Venues:** Kann eine Spielstätte nicht eindeutig aufgelöst werden, bleiben die betroffenen Felder `null`; das Skript gibt am Ende einen Bericht der nicht aufgelösten Venues aus und beendet ohne Datenverlust.
9. **Erstbefüllung:** Für die aktuell in [venues.json](../../../../data/venues.json) erfassten Spielstätten sind Adresse und Koordinaten – soweit automatisch ermittelbar – gepflegt und committet; der Metadaten-Hinweis in [venues.json](../../../../data/venues.json) ist aktualisiert.
10. **Nachvollziehbarkeit:** Skript und Datenänderungen sind über Git versioniert; die OSM-Herkunft der Daten ist dokumentiert.

## Out of Scope

- Darstellung von Adresse und Karte auf der Venue-Detailseite ([venue-detail](../../../../web/src/app/pages/venue-detail/)) oder in der Übersicht – hier wird nur die Datengrundlage geschaffen.
- Manuelle Nachrecherche von Spielstätten, die sich nicht automatisch auflösen lassen (nur Bericht, keine Pflicht-Nachpflege).
- Pflege weiterer Venue-Felder (z. B. `website`, `region`, `institutionId`).
- Recherche von Adressen außerhalb des Projekt-Scopes (NRW).
- Laufzeit-Anbindung an OSM/Overpass/Nominatim in der Webanwendung.

<!--
Umsetzungs-Tasks:
In separater Datei US-022-tasks.md im selben Verzeichnis pflegen.
Struktur dort: nummerierte Tasks (je betroffene Datei/Verantwortlichkeit), pro Task konkrete Schritte
mit Bezug auf die Akzeptanzkriterien, ein Abschnitt "Manuelle Verifikation" und eine "Definition of Done".
-->
