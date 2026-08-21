# US-022 – Umsetzungs-Tasks

Umsetzung von [US-022](./us-022-venues-addresses.md): Postadresse und Geokoordinaten der
Spielstätten aus OpenStreetMap recherchieren und in den Stammdaten pflegen. Dazu wird `address`
von einem String auf ein strukturiertes Objekt umgestellt und ein Python-Skript
(Overpass + Nominatim, ≤ 1 Abfrage/Sekunde) erstellt, das die Daten befüllt.

## Architektur-Entscheidung (verbindlich)

- **Datenquelle (Source of Truth):** `data/*.json` (Repo-Wurzel) ist die Quelle der Wahrheit,
  `web/public/data/*.json` ist die ausgelieferte Kopie und muss inhaltsgleich gehalten werden.
  Neue Adressen/Koordinaten müssen in **beide** `venues.json` geschrieben werden.
- **Adress-Format:** `Venue.address` wird von `string | null` auf ein strukturiertes
  `Address | null` umgestellt (`street`, `houseNumber`, `postalCode`, `city` – je `string | null`).
  Das ist ein **Breaking Change**: alle bestehenden Lesestellen (Anzeige, Suche, ICS-Export)
  müssen auf eine Formatierungs-Hilfsfunktion umgestellt werden.
- **Koordinaten:** Das bestehende Interface [`Coordinates`](../../../../web/src/app/models/models.ts#L107-L110)
  (`{ lat, lng }`, bereits von `Venue`/`City` genutzt) wird unverändert wiederverwendet.
- **Kein Laufzeit-Zugriff auf OSM:** Overpass/Nominatim werden ausschließlich im Recherche-Skript
  aufgerufen. Die Webanwendung liest nur die statischen `venues.json`.
- **Skript-Muster:** Analog zu [geocode_cities.py](../../../../docs/data-tooling/geocode_cities.py)
  (US-013): reine Standardbibliothek (`urllib`, `json`, `argparse`, `time`), idempotent, `--force`,
  Selbstbeschränkung ≥ 1 s zwischen Requests, Backoff bei HTTP 429/504.

Betroffene Dateien:
- `docs/data-tooling/fetch_venue_addresses.py` (neu) – OSM-Recherche
- [data/venues.json](../../../../data/venues.json) + [web/public/data/venues.json](../../../../web/public/data/venues.json)
- [web/src/app/models/models.ts](../../../../web/src/app/models/models.ts) (`Venue`, neues `Address`)
- [web/src/app/core/data.service.ts](../../../../web/src/app/core/data.service.ts) (Suche + Formatter)
- [web/src/app/pages/venue-detail/venue-detail.html](../../../../web/src/app/pages/venue-detail/venue-detail.html)
- [web/src/app/pages/venue-detail/venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts)
- [web/src/app/pages/event-detail/event-detail.html](../../../../web/src/app/pages/event-detail/event-detail.html)
- [web/src/app/pages/event-detail/event-detail.ts](../../../../web/src/app/pages/event-detail/event-detail.ts)
- [docs/entities/venues.md](../../../../docs/entities/venues.md)

---

## Task 1 – Datenmodell `Address` einführen

- In [models.ts](../../../../web/src/app/models/models.ts) ein neues Interface `Address` ergänzen:
  ```ts
  export interface Address {
    street: string | null;
    houseNumber: string | null;
    postalCode: string | null;
    city: string | null;
  }
  ```
- Im [`Venue`](../../../../web/src/app/models/models.ts#L119-L128)-Interface `address: string | null`
  auf `address: Address | null` umstellen. `coordinates: Coordinates | null` bleibt unverändert.
- **Deckt ab:** AK 1.

## Task 2 – Adress-Formatierer (Anzeige) bereitstellen

- Eine wiederverwendbare Hilfsfunktion `formatAddress(address: Address | null): string | null`
  bereitstellen (z. B. in [data.service.ts](../../../../web/src/app/core/data.service.ts) oder einem
  kleinen Util-Modul): setzt `"Straße Hausnummer, PLZ Ort"` zusammen und lässt fehlende (`null`)
  Bestandteile sauber weg; gibt `null` zurück, wenn kein Feld gesetzt ist.
- Diese Funktion ist die **einzige** Stelle, an der aus dem strukturierten Objekt ein Anzeige-String
  wird (DRY), und wird in Task 3–4 genutzt.
- **Deckt ab:** AK 1 (technische Grundlage), unterstützt AK 2.

## Task 3 – Suche/Index auf strukturierte Adresse umstellen

- In [data.service.ts:175](../../../../web/src/app/core/data.service.ts#L175) (Venue-`subtitle`) und
  [data.service.ts:180](../../../../web/src/app/core/data.service.ts#L180) (`searchText`) das direkte
  `venue.address` (bisher String) durch `formatAddress(venue.address)` ersetzen, damit Suchtext und
  Untertitel weiterhin die Adresse enthalten.
- **Deckt ab:** AK 2.

## Task 4 – Anzeige auf Detailseiten umstellen

- [venue-detail.html:17-19](../../../../web/src/app/pages/venue-detail/venue-detail.html#L17-L19):
  `venue()!.address` (String) durch den formatierten Wert ersetzen (z. B. Signal/Getter
  `addressLine()` in [venue-detail.ts](../../../../web/src/app/pages/venue-detail/venue-detail.ts),
  der `formatAddress` nutzt); die `@if`-Bedingung auf den formatierten Wert prüfen.
- [event-detail.html:72](../../../../web/src/app/pages/event-detail/event-detail.html#L72):
  analog auf den formatierten Adress-String umstellen.
- [event-detail.ts:146](../../../../web/src/app/pages/event-detail/event-detail.ts#L146):
  `venueAddress: venue?.address ?? null` auf `venueAddress: formatAddress(venue?.address ?? null)`
  umstellen (String bleibt für den ICS-/Kalender-Export erhalten).
- **Deckt ab:** AK 2.

## Task 5 – Recherche-Skript (Python/Overpass + Nominatim)

- `docs/data-tooling/fetch_venue_addresses.py` neu anlegen (nur Standardbibliothek, Muster wie
  [geocode_cities.py](../../../../docs/data-tooling/geocode_cities.py)):
  - Liest [venues.json](../../../../data/venues.json) und [cities.json](../../../../data/cities.json)
    (für Stadtname/-eingrenzung über `venue.cityIds`).
  - Ermittelt je Spielstätte über die **Overpass-API** den passenden OSM-Treffer (Suche nach `name`,
    eingegrenzt auf NRW/die zugeordnete Stadt, um gleichnamige Orte auszuschließen) samt
    `center`-Koordinaten (`{ lat, lng }`).
  - Ergänzt über **Nominatim** (reverse-geocoding auf den Koordinaten bzw. strukturierte Suche) die
    vollständige Postadresse und mappt sie auf `Address` (`street`, `houseNumber`, `postalCode`,
    `city`).
  - **Ratenbegrenzung:** höchstens **eine Abfrage pro Sekunde** (Selbstbeschränkung ≥ 1 s zwischen
    Requests, über beide APIs hinweg gezählt), aussagekräftiger `User-Agent`; Backoff bei HTTP
    429/504 mit wachsender Wartezeit und Wiederholung.
- **Deckt ab:** AK 3, AK 4, AK 5, AK 7.

## Task 6 – Idempotenz, Fehlerbehandlung & Bericht im Skript

- Skript ist **idempotent**: Venues mit bereits gefüllter `address`/`coordinates` werden
  übersprungen; `--force` erzwingt die Neuermittlung.
- Vorhandene Werte werden **nie mit `null` überschrieben**. Nicht auflösbare Venues (kein
  eindeutiger Treffer, `cityIds: []`, generische Namen) bleiben unverändert (`null`).
- Am Ende gibt das Skript einen **Bericht** aus: Anzahl aktualisiert / übersprungen / fehlgeschlagen
  sowie eine Liste der nicht aufgelösten Venue-IDs. Netzwerk-/Parsefehler pro Venue werden
  protokolliert, führen aber nicht zum Abbruch.
- Nach dem Lauf `metadata.version`/`lastUpdated` und den `notes`-Hinweis in
  [venues.json](../../../../data/venues.json) aktualisieren.
- **Deckt ab:** AK 6, AK 8, AK 9 (Metadaten).

## Task 7 – Erstbefüllung ausführen & spiegeln

- Skript gegen `data/venues.json` ausführen; Ergebnis stichprobenartig prüfen (z. B. Tonhalle
  Düsseldorf, Kölner Philharmonie liegen plausibel und haben eine vollständige Adresse).
- Ergebnis nach `web/public/data/venues.json` spiegeln (beide Dateien inhaltsgleich).
- Nicht aufgelöste Venues aus dem Bericht notieren (bleiben `null`; keine manuelle Nachpflege in
  dieser Story).
- **Deckt ab:** AK 9.

## Task 8 – Dokumentation aktualisieren

- [venues.md](../../../../docs/entities/venues.md) anpassen: `address`-Feld als strukturiertes Objekt
  (`Address`) beschreiben, das Beispiel-JSON aktualisieren, den Hinweis „noch nicht recherchiert"
  entfernen/relativieren und die OSM-Herkunft (Overpass + Nominatim) sowie das neue Skript nennen.
- **Deckt ab:** AK 2, AK 10.

## Task 9 – Manuelle Verifikation

- `cd web && npm run build` – kompiliert fehlerfrei (Breaking Change vollständig nachgezogen).
- `cd web && npm start` und im Browser prüfen:
  - Venue-Detailseite einer befüllten Spielstätte zeigt die zusammengesetzte Adresse korrekt; eine
    Spielstätte ohne Adresse zeigt keine Adresszeile (AK 2).
  - Event-Detailseite zeigt die Venue-Adresse; ICS-Export enthält weiterhin die Adresse als Text
    (AK 2).
  - Suche findet eine Spielstätte über Straße/PLZ/Ort (AK 2).
- Skript-Verhalten prüfen: zweiter Lauf ohne `--force` fragt nichts erneut ab; Bericht listet nicht
  aufgelöste Venues; ≤ 1 Abfrage/Sekunde erkennbar (AK 5, AK 6, AK 8).
- `data/venues.json` und `web/public/data/venues.json` sind inhaltsgleich (AK 9).

## Definition of Done

- Akzeptanzkriterien 1–10 aus [US-022](./us-022-venues-addresses.md) erfüllt.
- `Venue.address` ist strukturiert (`Address`); alle Lesestellen (Anzeige, Suche, ICS-Export) über
  `formatAddress` umgestellt; `npm run build` ohne Fehler.
- Recherche-Skript `fetch_venue_addresses.py` vorhanden: OSM via Overpass + Nominatim, ≤ 1
  Abfrage/Sekunde, idempotent, `--force`, überschreibt keine Werte mit `null`, gibt Bericht aus.
- Adressen/Koordinaten – soweit automatisch ermittelbar – in `data/` und `web/public/data/` gepflegt
  und inhaltsgleich; Metadaten-Hinweis aktualisiert; [venues.md](../../../../docs/entities/venues.md)
  auf das neue Format gebracht.
- Keine Laufzeit-Anbindung an OSM in der Webanwendung.
- Story- und Tasks-Datei nach Abschluss von `doing/` nach `done/` verschieben.
