# NRW Orchester-Kalender

Eine schlanke, statische Webanwendung für professionelle Sinfonie- und Philharmonieorchester in Nordrhein-Westfalen und ihre Konzertveranstaltungen.

Der Kalender beantwortet die zentrale Frage:

> Welche interessanten Orchesterkonzerte gibt es in NRW in diesem Monat?

## Produktidee

Die Anwendung zeigt den aktuellen Monat als Startansicht. Veranstaltungen werden nach Datum in einer deutschen Monatsansicht dargestellt und können in einer Detailansicht geöffnet werden. Eine zweite zentrale Ansicht stellt die erfassten Orchester mit ihren Stammdaten und Veranstaltungen vor.

Geplante Bereiche:

- Kalender mit Monatsnavigation und mehreren Veranstaltungen pro Tag
- Veranstaltungsdetailseiten mit Programm, Künstler:innen, Spielstätte und Quelle
- Orchesterübersicht und Orchesterprofile
- Direkte URLs für Monate, Orchester und Veranstaltungen
- Responsive Darstellung für Desktop und Smartphone
- Tastaturbedienung, sichtbare Fokuszustände und semantische HTML-Struktur

## Architektur

Die Anwendung ist als statische Webapp konzipiert und benötigt kein Backend und keine Datenbank.

```text
Recherche offizieller Quellen
          ↓
Datenaufbereitung und Validierung
          ↓
/data/orchestras.json
          ↓
Git und statisches Deployment
          ↓
Webapp im Browser
```

Die versionierte JSON-Datei ist die Single Source of Truth. Die Webapp konsumiert ausschließlich geprüfte Daten und enthält keine Logik zur Datenbeschaffung.

## Geplanter Projektaufbau

```text
.
├── data/
│   └── orchestras.json
├── data-tool/
│   ├── validator/
│   ├── updater/
│   └── reports/
├── schema/
│   └── orchestras.schema.json
├── web/
│   └── Angular-/TypeScript-Webapp
├── docs/
│   └── product/prd.md
└── README.md
```

## Datenmodell

Die zentrale Datei enthält Metadaten zur Spielzeit sowie Orchester, Veranstaltungsorte und einzelne Veranstaltungen:

```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-08-22",
    "season": "2026/27"
  },
  "orchestras": [],
  "venues": [],
  "events": []
}
```

Wiederkehrende Konzerte werden als einzelne Veranstaltungen gespeichert. Jede Veranstaltung soll eine eindeutige ID, ein gültiges Datum, Referenzen auf Orchester und Veranstaltungsort sowie eine ursprüngliche Quelle besitzen.

## Tech-Stack

- Frontend: Angular und TypeScript
- Build: Angular CLI
- Styling: CSS oder schlanke Utility-CSS-Lösung
- Daten: versionierte JSON-Datei
- Datenpflege: Python-CLI
- Deployment: statischer Host, zum Beispiel GitHub Pages, Netlify, Vercel oder Cloudflare Pages

## Datenpflege

Das geplante Python-Werkzeug `nrw_orchester_data` prüft die JSON-Datei und unterstützt ihre Aktualisierung.

```bash
python -m nrw_orchester_data validate
python -m nrw_orchester_data add-event
python -m nrw_orchester_data update
python -m nrw_orchester_data report
```

Die Validierung soll unter anderem doppelte IDs, ungültige Datums- und Uhrzeitwerte, fehlende Pflichtfelder sowie ungültige Orchester- und Venue-Referenzen erkennen. Fehler führen zu einem Exit Code ungleich null. Vergangene Veranstaltungen bleiben erhalten, werden aber als Warnung gemeldet.

Offizielle Websites der Orchester und Veranstalter sind bevorzugte Quellen. Änderungen an Datum, Dirigent:in, Programm, Veranstaltungsort oder Absage werden zunächst als Vorschlag beziehungsweise Änderungsbericht ausgegeben und nicht ohne Prüfung überschrieben.

## Entwicklungsstatus

Das Repository enthält derzeit das Produktanforderungsdokument. Die Webapp, die JSON-Datenbasis, das Schema und das Python-Datenpflegewerkzeug sind als nächste Umsetzungsschritte vorgesehen.

## Anforderungen aus dem MVP

Das MVP soll:

- beim Öffnen den tatsächlichen aktuellen Monat anzeigen, optional mit konfigurierbarem Referenzdatum für Tests;
- Monatsnavigation ohne vollständigen Seiten-Reload ermöglichen;
- Konzerte kompakt und vollständig verlinkbar darstellen;
- Orchester- und Veranstaltungsdetailseiten anbieten;
- ohne Backend funktionieren;
- mit geprüften JSON-Daten reproduzierbar gebaut und statisch deployt werden können.

Der vollständige Anforderungskatalog steht in [`docs/product/prd.md`](docs/product/prd.md).
