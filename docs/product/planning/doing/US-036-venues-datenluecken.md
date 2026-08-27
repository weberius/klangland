# User Story 036 - Fehlende Adressen, Koordinaten und Websites bei Spielstätten

## User Story

**Als** Datenpfleger:in von Klangland,
**möchte ich** eine vollständige Übersicht aller Spielstätten mit fehlender Adresse, fehlenden Koordinaten oder fehlender Website haben,
**damit** ich die fehlenden Angaben gezielt manuell recherchieren und in [venues.json](../../../../data/venues.json) nachtragen kann.

## Kontext / Problem

Mit dem Ingest der **Philharmonie Südwestfalen** ([ingest_philsw.py](../../../../docs/data-tooling/ingest_philsw.py), siehe [philharmonie-suedwestfalen.md](../../../../docs/data-tooling/philharmonie-suedwestfalen.md)) sind **33 neue Spielstätten** in [venues.json](../../../../data/venues.json) hinzugekommen. Sie wurden absichtlich mit `address: null` und `coordinates: null` angelegt (Konvention aus US-022); ein anschließender Lauf von [fetch_venue_addresses.py](../../../../docs/data-tooling/fetch_venue_addresses.py) konnte wegen wiederholter Drosselung/Nichterreichbarkeit der Overpass-API sowie mangels eindeutiger OSM-Treffer nur **3 der 33** neuen Venues auflösen (Schützenhalle Grevenbrück, Kulturhaus Lüdenscheid, Festhalle Wilnsdorf – jeweils nur Adresse/Koordinaten, nicht Website).

Ein vollständiger Abgleich des gesamten Datenbestands (160 Venues) zeigt:

- **31 Venues** haben `address: null` **und** `coordinates: null` (30 davon neu aus dem PhilSW-Ingest, 1 bereits zuvor bestehend).
- **81 Venues** haben `website: null` (33 davon neu aus dem PhilSW-Ingest, 48 bereits zuvor bestehend – `website` wurde im Projekt bislang nie als Pflichtfeld recherchiert, siehe Out-of-Scope-Abgrenzung in US-022, Punkt „Pflege weiterer Venue-Felder (z. B. `website`, ...)").

Diese Story schafft **nur die Übersicht** als Grundlage für die anschließende **manuelle** Recherche; es wird an dieser Stelle **kein** Code geändert und **kein** weiterer automatisierter Recherche-Lauf ausgeführt.

## Gewählte Lösung

Diese Story ist rein dokumentarisch: Sie listet alle betroffenen Venues in vier nach Priorität geordneten Tabellen auf. Die eigentliche Recherche und das Nachtragen der Werte in [venues.json](../../../../data/venues.json) erfolgt **manuell in einer Folgearbeit**, nicht im Rahmen dieser Story.

### Tabelle 1 – Priorität hoch: Neue Venues (PhilSW) ohne Adresse und Koordinaten

Diese 30 Venues haben zusätzlich auch keine Website. Der automatisierte Lauf von `fetch_venue_addresses.py` konnte sie nicht eindeutig auflösen (kein OSM-Treffer bzw. Overpass-Timeout).

| Venue-ID | Name | Ort | Typ |
| --- | --- | --- | --- |
| `apollo-theater-siegen` | Apollo-Theater Siegen | Siegen | theatre |
| `aula-gymnasium-bad-laasphe` | Aula des Gymnasiums Bad Laasphe | Bad Laasphe | other |
| `aula-gymnasium-wilnsdorf` | Aula des Gymnasiums Wilnsdorf | Wilnsdorf | other |
| `buergerhaus-bad-berleburg` | Bürgerhaus Bad Berleburg | Bad Berleburg | other |
| `dreslers-park-kreuztal` | Dreslers Park Kreuztal | Kreuztal | other |
| `erloeserkirche-neunkirchen-siegerland` | Erlöserkirche Neunkirchen | Neunkirchen (Siegerland) | other |
| `ev-kirche-bad-lippspringe` | Ev. Kirche Bad Lippspringe | Bad Lippspringe | other |
| `ev-kirche-hilchenbach` | Ev. Kirche Hilchenbach | Hilchenbach | other |
| `ginsburg-turmzimmer-hilchenbach` | Ginsburg Turmzimmer Hilchenbach-Lützel | Hilchenbach | other |
| `haus-der-musik-siegen` | Haus der Musik Siegen | Siegen | concert_hall |
| `kath-kirche-st-alexander-schmallenberg` | Kath. Kirche St. Alexander Schmallenberg | Schmallenberg | other |
| `kath-kirche-st-martin-olsberg-bigge` | Kath. Kirche St. Martin Olsberg-Bigge | Olsberg | other |
| `kirche-am-roemer-burbach` | Kirche am Römer Burbach | Burbach | other |
| `kultureller-marktplatz-hilchenbach` | Kultureller Marktplatz Hilchenbach-Dahlbruch | Hilchenbach | other |
| `kurhaus-hamm` | Kurhaus Hamm | Hamm | other |
| `marktplatz-hilchenbach` | Marktplatz Hilchenbach | Hilchenbach | other |
| `metronom-theater-oberhausen` | Metronom-Theater Oberhausen | Oberhausen | theatre |
| `museum-oberes-schloss-siegen` | Museum Oberes Schloss Siegen | Siegen | other |
| `neue-aula-warstein` | Neue Aula Warstein | Warstein | other |
| `otto-flick-halle-kreuztal` | Otto-Flick-Halle Kreuztal | Kreuztal | other |
| `paedagogisches-zentrum-gesamtschule-kierspe` | Pädagogisches Zentrum der Gesamtschule Kierspe | Kierspe | other |
| `paedagogisches-zentrum-lennestadt` | Pädagogisches Zentrum Lennestadt | Lennestadt | other |
| `parktheater-iserlohn` | Parktheater Iserlohn | Iserlohn | theatre |
| `pfarrkirche-st-johannes-baptist-attendorn` | Pfarrkirche St. Johannes Baptist Attendorn | Attendorn | other |
| `sauerlandhalle-lennestadt` | Sauerlandhalle Lennestadt | Lennestadt | other |
| `schlossplatz-muenster` | Schlossplatz Münster | Münster | other |
| `st-johannes-kirche-arnsberg-neheim` | St. Johannes Kirche Arnsberg-Neheim | Arnsberg | other |
| `stadthalle-schmallenberg` | Stadthalle Schmallenberg | Schmallenberg | other |
| `stift-keppel-konventssaal-hilchenbach` | Stift Keppel Konventssaal | Hilchenbach | other |
| `theater-lippstadt` | Theater Lippstadt | Lippstadt | theatre |

### Tabelle 2 – Priorität mittel: Neue Venues (PhilSW) mit Adresse/Koordinaten, aber ohne Website

| Venue-ID | Name | Ort |
| --- | --- | --- |
| `festhalle-wilnsdorf` | Festhalle Wilnsdorf | Wilnsdorf |
| `kulturhaus-luedenscheid` | Kulturhaus Lüdenscheid | Lüdenscheid |
| `schuetzenhalle-grevenbrueck` | Schützenhalle Grevenbrück | Lennestadt |

### Tabelle 3 – Sonderfall (Altbestand): Venue ohne Adresse und Koordinaten

| Venue-ID | Name | Ort | Hinweis |
| --- | --- | --- | --- |
| `bielefeld-umgebung` | Bielefeld und Umgebung | Bielefeld | Bewusst generischer Fallback-Eintrag für 1 Termin ohne konkrete Spielstätte (siehe [bielefelder-philharmoniker.md](../../../../docs/data-tooling/bielefelder-philharmoniker.md)). Vermutlich **nicht** sinnvoll recherchierbar – vor Bearbeitung prüfen, ob überhaupt eine konkrete Adresse existieren kann. |

### Tabelle 4 – Priorität niedrig: Bestehender Altbestand ohne Website

Diese 47 Venues existierten bereits vor dem PhilSW-Ingest und haben Adresse/Koordinaten, aber keine Website. `website` war im Projekt bislang kein recherchiertes Pflichtfeld (vgl. US-022, Out-of-Scope-Abgrenzung); die Aufnahme hier dient der Vollständigkeit der Bestandsaufnahme.

| Venue-ID | Name | Ort |
| --- | --- | --- |
| `theater-aachen` | Theater Aachen | Aachen |
| `stadthalle-bielefeld` | Stadthalle Bielefeld | Bielefeld |
| `zeughauskultur-bochum` | Anneliese Brost Musikforum Ruhr | Bochum |
| `kreuzkirche-bonn` | Kreuzkirche Bonn | Bonn |
| `world-conference-center-bonn` | World Conference Center Bonn | Bonn |
| `konzert-theater-coesfeld` | Konzert Theater Coesfeld | Coesfeld |
| `akademie-theater-digitalitaet-dortmund` | Akademie für Theater und Digitalität | Dortmund |
| `deutsches-fussballmuseum-dortmund` | Deutsches Fußballmuseum Dortmund | Dortmund |
| `opernhaus-dortmund` | Opernhaus Dortmund | Dortmund |
| `thier-galerie-dortmund` | Thier-Galerie Dortmund | Dortmund |
| `landschaftspark-duisburg-nord` | Landschaftspark Duisburg-Nord | Duisburg |
| `kunstmuseum-gelsenkirchen` | Kunstmuseum Gelsenkirchen | Gelsenkirchen |
| `matthaeuskirche-gelsenkirchen` | Matthäuskirche | Gelsenkirchen |
| `musiktheater-im-revier` | Musiktheater im Revier | Gelsenkirchen |
| `johanniskirche-hagen` | Johanniskirche | Hagen |
| `kulturzentrum-herne` | Kulturzentrum | Herne |
| `haus-opherdicke` | Haus Opherdicke | Holzwickede |
| `konzertaula-kamen` | Konzertaula | Kamen |
| `belgisches-haus-koeln` | Belgisches Haus | Köln |
| `buergerzentrum-engelshof-koeln` | Bürgerzentrum Engelshof | Köln |
| `seidenweberhaus-krefeld` | Seidenweberhaus | Krefeld |
| `forum-leverkusen` | Forum Leverkusen | Leverkusen |
| `heinz-hilpert-theater` | Heinz-Hilpert-Theater | Lünen |
| `theater-marl` | Theater Marl | Marl |
| `kaiser-friedrich-halle-moenchengladbach` | Kaiser-Friedrich-Halle | Mönchengladbach |
| `theater-moenchengladbach` | Theater Mönchengladbach | Mönchengladbach |
| `stadthalle-muelheim` | Stadthalle Mülheim an der Ruhr | Mülheim an der Ruhr |
| `buergerhaus-sued-recklinghausen` | Bürgerhaus Süd | Recklinghausen |
| `christuskirche-recklinghausen` | Christuskirche | Recklinghausen |
| `depot-npw-probenzentrum-recklinghausen` | Depot (NPW-Probenzentrum) | Recklinghausen |
| `rathausplatz-recklinghausen` | Rathausplatz | Recklinghausen |
| `ruhrfestspielhaus` | Ruhrfestspielhaus | Recklinghausen |
| `sparkasse-vest-recklinghausen` | Sparkasse Vest | Recklinghausen |
| `lutherkirche-remscheid` | Lutherkirche Remscheid | Remscheid |
| `munsterplatz-lennep-remscheid` | Munsterplatz Lennep | Remscheid |
| `stadtpark-konzertmuschel-remscheid` | Stadtpark Konzertmuschel Remscheid | Remscheid |
| `teo-otto-theater` | Teo Otto Theater | Remscheid |
| `freischuetz-schwerte` | Freischütz | Schwerte |
| `rohrmeisterei-schwerte` | Rohrmeisterei | Schwerte |
| `siegener-stadthalle` | Siegerlandhalle | Siegen |
| `brueckenpark-solingen` | Brückenpark Müngsten | Solingen |
| `dorper-kirche-solingen` | Dorper Kirche | Solingen |
| `marktplatz-graefrath-solingen` | Marktplatz Gräfrath | Solingen |
| `schloss-burg` | Schloss Burg | Solingen |
| `theater-und-konzerthaus-solingen` | Theater und Konzerthaus Solingen | Solingen |
| `erich-goepfert-stadthalle-unna` | Erich-Göpfert-Stadthalle | Unna |
| `marktplatz-unna` | Marktplatz Unna | Unna |

## Akzeptanzkriterien

1. **Vollständige Bestandsaufnahme:** Alle Venues aus [venues.json](../../../../data/venues.json) mit `address: null` oder `coordinates: null` sind in Tabelle 1 oder Tabelle 3 erfasst; alle Venues mit `website: null` sind in Tabelle 2 oder Tabelle 4 erfasst. Kein betroffener Venue-Datensatz fehlt.
2. **Priorisierung erkennbar:** Die Tabellen unterscheiden zwischen neu hinzugekommenen Venues (PhilSW-Ingest, Tabellen 1–2) und Altbestand (Tabellen 3–4), damit die Recherche nach Dringlichkeit sortiert angegangen werden kann.
3. **Ausreichend Kontext je Zeile:** Jede Zeile nennt mindestens Venue-ID, Namen und zugeordneten Ort, damit eine gezielte manuelle Suche möglich ist, ohne zusätzlich in `venues.json` nachschlagen zu müssen.
4. **Sonderfall dokumentiert:** Der generische Fallback-Eintrag `bielefeld-umgebung` ist als vermutlich nicht recherchierbar gekennzeichnet, damit dafür keine unnötige Suche gestartet wird.
5. **Keine Datenänderung:** Diese Story ändert [venues.json](../../../../data/venues.json) oder andere Daten-/Codedateien **nicht**. Sie ist rein die Recherchegrundlage für eine spätere, manuelle Nachpflege.

## Out of Scope

- Die eigentliche Recherche und das Eintragen von Adresse, Koordinaten oder Website in [venues.json](../../../../data/venues.json) – erfolgt manuell in einer separaten Folgearbeit.
- Ein erneuter oder erweiterter automatisierter Lauf von [fetch_venue_addresses.py](../../../../docs/data-tooling/fetch_venue_addresses.py) (z. B. mit anderen Suchstrategien für die nicht aufgelösten Venues).
- Ergänzung von `website` als recherchiertes Pflichtfeld im Datenmodell/Tooling (bleibt weiterhin optional, vgl. US-022).
- Darstellung der Adress-/Karten-Vollständigkeit in der Webanwendung.
