# Product Requirements Document (PRD)

## 1. Produktübersicht

### 1.1 Arbeitstitel

**NRW Orchester-Kalender**

> **Hinweis:** Das Projekt wird inzwischen unter dem Namen **Klangland** geführt; der
> Konzertkalender ist dessen erste Anwendung. „NRW Orchester-Kalender" bleibt als
> beschreibender Arbeitstitel dieses Dokuments erhalten.

Eine schlanke, statische Webapplikation zur Übersicht der professionellen Sinfonie- und Philharmonieorchester in Nordrhein-Westfalen und deren Konzertveranstaltungen in der Spielzeit 2026/27 und darüber hinaus.

Die Anwendung bezieht sämtliche Inhalte aus einer versionierten **JSON-Datei**. Die Webapplikation selbst benötigt kein Backend und keine Datenbank.

Die Aktualisierung der Veranstaltungsdaten erfolgt durch:

1. Recherche bzw. Ermittlung neuer oder geänderter Veranstaltungen
2. Aktualisierung der JSON-Datendatei
3. Commit/Deploy der Anwendung
4. Die neue JSON-Datei wird beim nächsten Deployment ausgeliefert.

Zusätzlich soll ein **Python-Skript bzw. ein wiederverwendbarer Skill** entwickelt werden, der die Pflege und Aktualisierung der JSON-Datei unterstützt.

---

# 2. Ziele

## 2.1 Primäres Ziel

Der Nutzer soll auf einen Blick erkennen können:

* welche professionellen Orchester in NRW existieren,
* wo sie beheimatet sind,
* wer ihr:e Chefdirigent:in bzw. Generalmusikdirektor:in ist,
* welches musikalische Profil sie haben,
* **wann welches Orchester ein Konzert spielt**,
* wo dieses Konzert stattfindet,
* was gespielt wird,
* wer dirigiert und
* welche weiteren relevanten Informationen zum Konzert verfügbar sind.

## 2.2 Nutzungsszenario

Die Anwendung soll insbesondere folgende Frage beantworten:

> „Welche interessanten Orchesterkonzerte gibt es in NRW in diesem Monat?“

Der Kalender ist deshalb die **Startansicht** der Anwendung.

Die Orchesterübersicht ist als zweiter zentraler Bereich verfügbar.

---

# 3. Nicht-Ziele

Für die erste Version sind folgende Funktionen ausdrücklich nicht erforderlich:

* Benutzerkonten
* Anmeldung
* persönliche Favoriten
* Ticketkauf
* Sitzplatzreservierung
* Backend-Datenbank
* Live-Synchronisation mit Veranstaltern
* automatische Aktualisierung während des Seitenbetriebs
* Kommentarfunktionen
* Bewertungen
* Social Features
* komplexe Routenplanung
* automatische Erkennung von Konzertterminen aus Webseiten

Diese Funktionen können später ergänzt werden, sind aber nicht Bestandteil des MVP.

---

# 4. Zielgruppe

Primäre Zielgruppe:

**Interessierte an klassischer Musik in Nordrhein-Westfalen**, insbesondere Personen, die regelmäßig Konzerte verschiedener Orchester besuchen und dafür einen zentralen Überblick benötigen.

Sekundäre Zielgruppe:

* Klassik-Einsteiger:innen
* Konzertreisende innerhalb NRWs
* Musikstudent:innen
* Musikjournalist:innen
* Konzertveranstalter:innen
* Nutzer:innen, die gezielt nach Komponisten oder Orchestern suchen

---

# 5. Informationsarchitektur

Die Anwendung besteht zunächst aus zwei Hauptbereichen:

```text
NRW Orchester-Kalender
│
├── Kalender
│   ├── August 2026
│   ├── September 2026
│   ├── Oktober 2026
│   └── ...
│
├── Orchester
│   ├── Aachen
│   ├── Bielefeld
│   ├── Bochum
│   ├── Bonn
│   └── ...
│
└── Veranstaltung
    └── Detailansicht
```

Der **Kalender ist die Default-Ansicht**.

---

# 6. Kalender

## 6.1 Default-Zustand

Beim Öffnen der Anwendung wird automatisch der aktuelle Monat angezeigt.

Für den definierten Startzeitpunkt:

**August 2026**

Die Anwendung darf das Datum nicht fest auf August 2026 programmieren. Stattdessen soll der aktuelle Monat anhand des Systemdatums bestimmt werden.

Für Entwicklungs-/Demo-Zwecke soll optional ein Referenzdatum konfigurierbar sein.

Beispiel:

```text
referenceDate = null
```

→ tatsächliches heutiges Datum verwenden.

Oder:

```text
referenceDate = "2026-08-22"
```

→ für Tests den 22. August 2026 verwenden.

---

## 6.2 Monatsansicht

Der Kalender wird als klassische Monatsansicht dargestellt.

Beispiel:

```text
                 August 2026

       ‹                         ›

Mo     Di     Mi     Do     Fr     Sa     So
27     28     29     30     31      1      2
 3      4      5      6      7      8      9
10     11     12     13     14     15     16
17     18     19     20     21     22     23
24     25     26     27     28     29     30
31
```

Dabei entspricht die Kalenderwoche der in Deutschland üblichen Darstellung:

**Montag → Sonntag**

---

## 6.3 Navigation

Es gibt mindestens zwei Navigationsmöglichkeiten:

* vorheriger Monat
* nächster Monat

Optional:

* Button **„Heute“**

Beispiel:

```text
‹       August 2026       ›
             Heute
```

Die Navigation darf nicht die Seite vollständig neu laden.

---

# 7. Veranstaltungskacheln

Jeder Kalendertag wird durch eine Kachel dargestellt.

Ein Tag ohne Konzert enthält lediglich das Datum.

Ein Tag mit Konzert enthält eine kompakte Veranstaltungsdarstellung.

### Beispiel

```text
┌─────────────────────────┐
│ 22                      │
│                         │
│ Bruckner 7              │
│                         │
│ Duisburger Philharmon.  │
│ Stefan Blunier          │
│ Duisburg                │
└─────────────────────────┘
```

Bei mehreren Veranstaltungen am selben Tag:

```text
┌─────────────────────────┐
│ 22                      │
│                         │
│ Bruckner 7              │
│ Duisburger Philharm.    │
│                         │
│ Beethoven 5             │
│ WDR Sinfonieorchester   │
│                         │
│ + 1 weiteres Konzert    │
└─────────────────────────┘
```

---

# 8. Inhalte einer Veranstaltungskachel

Eine Kachel soll mindestens folgende Informationen zeigen:

### Pflichtinformationen

* Datum
* Veranstaltungstitel
* Orchester
* Dirigent:in
* Veranstaltungsort / Stadt

### Optional

* Uhrzeit
* Solist:in
* Hauptwerk / Komponist
* Veranstaltungsreihe

Die Darstellung muss so kompakt sein, dass auch mehrere Veranstaltungen an einem Tag sinnvoll dargestellt werden können.

---

# 9. Veranstaltungsdetails

Ein Klick auf eine Veranstaltung öffnet eine Detailansicht.

Diese kann als:

* Modal/Dialog
* Drawer
* eigene URL/Route

implementiert werden.

**Empfehlung:** eigene URL/Route, damit Veranstaltungen direkt verlinkbar sind.

Beispiel:

```text
/events/2026-10-02-duesseldorfer-symphoniker-mahler-3
```

## 9.1 Detailinformationen

Die Detailansicht enthält:

### Veranstaltung

* Titel
* Datum
* Beginn
* ggf. Ende
* Veranstaltungsreihe

### Orchester

* Name
* Ort
* Chefdirigent:in
* Kurzbeschreibung
* Link zur Orchesterseite

### Künstler:innen

* Dirigent:in
* Solist:innen
* ggf. Chor

### Programm

Für jedes Werk:

* Komponist
* Werk
* optional Opus-/Werknummer
* optional Entstehungsjahr

Beispiel:

```text
Gustav Mahler
Sinfonie Nr. 3 d-Moll

Johannes Brahms
Alt-Rhapsodie op. 53
```

### Veranstaltungsort

* Name des Saals
* Stadt
* Adresse
* optional Website

### Quellen

Zu jeder Veranstaltung soll die ursprüngliche Informationsquelle gespeichert werden.

Beispiel:

```text
Quelle:
https://...
```

Die Quelle ist für die Datenpflege wichtig und sollte auch in der Detailansicht als Link angezeigt werden.

---

# 10. Orchesterübersicht

Die Anwendung enthält eine Übersicht aller erfassten Orchester.

Darstellung beispielsweise als Karten:

```text
┌─────────────────────────────────────┐
│ WDR Sinfonieorchester               │
│ Köln                                │
│                                     │
│ Chefdirigentin: Marie Jacquot       │
│                                     │
│ Neue Musik · Moderne · Sinfonik     │
│                                     │
│ 24 Veranstaltungen                  │
└─────────────────────────────────────┘
```

---

# 11. Ensemble-Stammdaten

Für jedes Ensemble werden mindestens folgende Daten benötigt. Beziehungen werden
ausschließlich über IDs hergestellt; Ort, Leitung und Stammsaal werden **nicht** eingebettet,
sondern über `cityIds`, `chiefConductorPersonId` und `venueId` referenziert:

```json
{
  "id": "sinfonieorchester-aachen",
  "name": "Sinfonieorchester Aachen",
  "type": "symphony_orchestra",
  "country": "Deutschland",
  "cityIds": ["aachen"],
  "region": null,
  "chiefConductorPersonId": "levente-toeroek",
  "venueId": "theater-aachen",
  "artisticProfile": ["Klassik", "Romantik", "Oper", "Sinfonik"],
  "description": "...",
  "website": null,
  "source": null
}
```

> **Hinweis:** Das ursprünglich hier skizzierte flache Modell (eingebettete Felder `city`,
> `chiefConductor`, `venue`) wurde zugunsten des normalisierten Modells aufgegeben. Maßgeblich
> ist die Detaildoku [`docs/entities/ensembles.md`](../entities/ensembles.md) bzw. das
> Datenmodell [`docs/data-model.md`](../data-model.md); die Entscheidung ist in
> [ADR-003](../architecture/ADR-003-normalisiertes-datenmodell-mit-id-referenzen.md)
> festgehalten.

---

# 12. Orchesterprofil

Beim Klick auf ein Orchester sollen folgende Informationen sichtbar sein:

* Name
* Sitz
* Chefdirigent:in / Generalmusikdirektor:in
* musikalischer Schwerpunkt
* Kurzbeschreibung
* Stammsaal bzw. wichtigste Spielstätte
* Website
* Anzahl der erfassten Veranstaltungen
* Liste bzw. Kalender der Veranstaltungen dieses Orchesters

Optional kann später eine kleine Karte ergänzt werden.

---

# 13. Datenmodell

Die Daten werden in getrennten, versionierten JSON-Dateien gespeichert. Jede zentrale Entität besitzt eine eigene Datei; Beziehungen zwischen Entitäten werden ausschließlich über IDs hergestellt:

```text
/data/people.json
/data/institutions.json
/data/ensembles.json
/data/venues.json
/data/cities.json
/data/composers.json
/data/works.json
/data/events.json
```

Empfohlen wird folgende Struktur:

```json
{
  "metadata": {
    "version": "1.0",
    "lastUpdated": "2026-08-22",
    "season": "2026/27"
  },

  "people": [],
  "institutions": [],
  "ensembles": [],
  "venues": [],
  "cities": [],
        "composers": [],
  "works": [],
  "events": []
}
```

Die Entitäten sind bewusst getrennt: Eine Institution kann mehrere Spielstätten betreiben und Ensembles tragen. Ein Ensemble kann an verschiedenen Spielstätten auftreten. Ein Event verbindet Ensemble, Venue, Personen und Werke. `ensembles` ist der Oberbegriff; `orchestras` wird nicht mehr als zentrale Entität verwendet.

---

# 14. Veranstaltungs-Datensatz

Beispiel:

```json
{
        "id": "event-2026-10-02-duesseldorf-mahler3",
        "title": "Mahler 3",
        "eventType": "concert",

  "date": "2026-10-02",
  "startTime": "19:30",
  "endTime": null,

  "status": "scheduled",
  "ensembleIds": ["duesseldorfer-symphoniker"],
  "venueId": "tonhalle-duesseldorf",
  "cityId": "duesseldorf",
  "conductorPersonIds": ["vitali-alekseenok"],
  "soloistPersonIds": [],

        "program": [
                {
                        "workId": "mahler-sinfonie-3",
                        "movement": null,
                        "version": null
                }
        ],

        "seriesId": null,
        "description": null,

  "source": {
        "url": "https://example.org/konzerte/mahler-3",
        "name": "Beispielquelle",
        "retrievedAt": "2026-08-17"
  },

        "ticketUrl": null,
        "lastVerified": "2026-08-17"
}
```

---

# 15. Wiederkehrende Veranstaltungen

Einzelne Konzerte werden als **separate Veranstaltungen** gespeichert.

Beispiel:

```text
18.09.2026 – 19:30
19.09.2026 – 19:30
20.09.2026 – 11:00
```

werden als drei Events gespeichert.

Es soll keine komplizierte Regel-Engine für wiederkehrende Termine geben.

Das macht die Daten robuster und erlaubt unterschiedliche Uhrzeiten, Säle und Programme.

---

# 16. Datenqualität

Da die JSON-Datei die zentrale Datenquelle ist, ist Datenqualität besonders wichtig.

Das Python-Werkzeug soll deshalb mindestens folgende Prüfungen durchführen:

### Pflichtfelder

* eindeutige Ensemble-ID
* eindeutige Veranstaltungs-ID
* gültiges Datum
* Ensemble existiert
* Veranstaltungsort existiert
* referenzierte Werke und Komponist:innen existieren
* Titel vorhanden

### Konsistenz

* keine doppelten IDs in Ensembles, Werken, Komponist:innen und Veranstaltungen
* gültige ISO-Datumswerte
* Uhrzeiten im Format `HH:MM`
* jede Veranstaltung verweist auf existierende Ensembles
* jede Veranstaltung verweist auf einen existierenden Veranstaltungsort
* jeder Programmpunkt verweist auf ein existierendes Werk
* jedes Werk verweist auf einen existierenden Komponisten
* `genre` und Katalogsysteme verwenden kontrollierte Werte

### Quellen

Jede Veranstaltung sollte eine Quelle besitzen.

### Zeitliche Prüfung

Das Werkzeug soll Veranstaltungen erkennen, deren Datum bereits in der Vergangenheit liegt.

Diese werden nicht automatisch gelöscht.

Stattdessen kann das Tool melden:

```text
12 Veranstaltungen liegen in der Vergangenheit.
```

So bleibt die historische Datenbasis erhalten.

---

# 17. Python-Datenpflegewerkzeug

Es soll ein Python-Tool zur Pflege der JSON-Daten entwickelt werden.

Arbeitstitel:

```text
nrw-orchester-data
```

Mögliche CLI:

```bash
python -m nrw_orchester_data validate
python -m nrw_orchester_data add-event
python -m nrw_orchester_data update
python -m nrw_orchester_data report
```

## 17.1 validate

Prüft die komplette JSON-Datei.

Beispiel:

```text
Checking data...

✓ 17 ensembles
✓ 23 venues
✓ 184 events
✓ no duplicate IDs
✓ all ensemble references valid
✓ all institution references valid
✓ all venue references valid
✓ all dates valid

Warnings:
! 7 events are in the past
! 3 events have no ticket URL
```

Der Prozess soll bei echten Datenfehlern mit einem **Exit Code != 0** beendet werden.

Damit kann die Validierung später in CI/CD integriert werden.

---

# 18. Aktualisierung der Daten

Die langfristige Zielsetzung ist ein halbautomatischer Datenpflegeprozess.

Das Werkzeug soll perspektivisch in der Lage sein:

1. Ensemble- und Institutionen-Websites zu kennen
2. Veranstaltungsquellen zu kennen
3. vorhandene Veranstaltungen zu laden
4. neue Veranstaltungen zu erkennen
5. Änderungen gegenüber dem bestehenden Datensatz zu erkennen
6. Vorschläge für neue/geänderte Datensätze zu erzeugen
7. die JSON-Datei nach Bestätigung zu aktualisieren

Wichtig:

**Automatisches Überschreiben von Konzertdaten ohne Prüfung soll zunächst nicht erfolgen.**

Bei Änderungen wie:

```text
Datum geändert
Dirigent geändert
Programm geändert
Veranstaltungsort geändert
Konzert abgesagt
```

soll das Tool die Änderung zunächst anzeigen.

---

# 19. Skill zur Datenaktualisierung

Zusätzlich zum Python-Skript soll ein Skill definiert werden, der eine Recherche- und Aktualisierungsroutine beschreibt.

Beispielhafter Ablauf:

```text
"Update NRW orchestra data"

        ↓

Ensembleliste und Institutionen laden

        ↓

Offizielle Websites recherchieren

        ↓

Spielpläne abrufen

        ↓

Termine extrahieren

        ↓

Mit bestehender JSON vergleichen

        ↓

Neue / geänderte / entfernte Termine anzeigen

        ↓

Änderungen bestätigen

        ↓

JSON aktualisieren

        ↓

Schema validieren

        ↓

Änderungsbericht erzeugen
```

Die **offiziellen Seiten der Orchester bzw. Veranstalter sollen die bevorzugten Quellen** sein.

---

# 20. Änderungsbericht

Nach einem Update soll ein maschinen- und menschenlesbarer Report erzeugt werden:

```text
NRW Orchester Update
22.08.2026

Neue Veranstaltungen:       12
Geänderte Veranstaltungen:   4
Entfernte Veranstaltungen:   1

Orchester:
Düsseldorfer Symphoniker     +2
Essener Philharmoniker       +3
Dortmunder Philharmoniker    +4
WDR Sinfonieorchester        +3

Änderungen:
- 02.10.2026: Dirigent geändert
- 15.10.2026: Beginn von 19:00 auf 19:30 geändert
...
```

---

# 21. Technische Architektur

Für das MVP wird eine **statische Webanwendung** empfohlen.

```text
                ┌───────────────────┐
                │   JSON-Daten      │
                │ getrennte JSON-   │
                │ Stammdatendateien │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Static Web App     │
                │                   │
                │ Kalender           │
                │ Ensembles          │
                │ Spielstätten       │
                │ Details            │
                └─────────┬─────────┘
                          │
                          ▼
                    Browser
```

Kein Backend erforderlich.

---

# 22. Empfohlener Tech-Stack

Für das MVP:

### Frontend

**Angular + TypeScript**

Begründung:

* gute Unterstützung für Kalenderoberflächen
* klare Struktur für Komponenten und Routing
* gute Erweiterbarkeit
* statisch deploybar

Die Anwendung soll mit Angular umgesetzt werden.

### Build

**Angular CLI**

### Styling

CSS bzw. eine schlanke Utility-CSS-Lösung.

Das Design soll zunächst bewusst schlicht sein.

### Daten

JSON als statische Ressource.

### Deployment

Geeignet sind beispielsweise:

* GitHub Pages
* Netlify
* Vercel
* Cloudflare Pages

Das Deployment soll automatisch nach einem Push auf den entsprechenden Branch erfolgen können.

---

# 23. URL-Struktur

Die Anwendung soll Deep Links unterstützen.

Beispiel:

```text
/
```

→ Kalender, aktueller Monat

```text
/calendar/2026/10
```

→ Oktober 2026

```text
/ensembles
```

→ Ensembleübersicht

```text
/ensembles/wdr-sinfonieorchester
```

→ Ensembleprofil

```text
/venues/tonhalle-duesseldorf
```

→ Spielstättenprofil

```text
/events/2026-10-02-duesseldorfer-symphoniker-mahler-3
```

→ Veranstaltungsdetail

Damit können einzelne Veranstaltungen direkt geteilt bzw. als Bookmark gespeichert werden.

---

# 24. Filter und Suche

Für das MVP sind Filter nicht zwingend erforderlich, sollten aber bei der Architektur berücksichtigt werden.

Sinnvolle spätere Filter:

### Orchester

```text
☐ Aachen
☐ Bonn
☐ Bochum
☐ Dortmund
...
```

### Komponist

```text
Beethoven
Brahms
Bruckner
Mahler
Mozart
Schumann
...
```

### Region

```text
Rheinland
Ruhrgebiet
Westfalen
Bergisches Land
...
```

### musikalisches Profil

```text
Klassik
Romantik
Spätromantik
Neue Musik
Oper
Chormusik
...
```

---

# 25. Mobile Darstellung

Die Anwendung muss auf mobilen Geräten gut funktionieren.

Desktop:

```text
┌────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│ Mo     │ Di     │ Mi     │ Do     │ Fr     │ Sa     │ So     │
├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│        │        │        │        │        │ Konzert│        │
│        │        │        │        │        │        │        │
└────────┴────────┴────────┴────────┴────────┴────────┴────────┘
```

Mobil:

Die Monatsansicht kann auf eine kompakte 7-Spalten-Darstellung reagieren.

Die wichtigsten Informationen einer Veranstaltung müssen auch auf kleinen Bildschirmen erkennbar bleiben.

---

# 26. Accessibility

Die Anwendung soll grundlegende WCAG-Anforderungen berücksichtigen.

Insbesondere:

* ausreichender Kontrast
* Tastaturnavigation
* sichtbarer Fokus
* semantische HTML-Struktur
* Buttons statt klickbarer `div`s
* verständliche Beschriftungen
* Screenreader-freundliche Kalendernavigation

Beispiel:

```text
← Vorheriger Monat
August 2026
Nächster Monat →
```

statt ausschließlich grafischer Icons ohne Beschriftung.

---

# 27. Internationalisierung

Die erste Version ist **deutschsprachig**.

Datum:

```text
22. August 2026
```

Wochentage:

```text
Mo Di Mi Do Fr Sa So
```

Das Datenmodell sollte trotzdem so gestaltet werden, dass später eine englische Oberfläche ergänzt werden kann.

---

# 28. Design

Das Design soll sich an einer modernen klassischen Konzertplattform orientieren.

Anforderungen:

* ruhig
* hochwertig
* übersichtlich
* keine übermäßigen Animationen
* gute Lesbarkeit
* Kalender im Mittelpunkt
* Orchester und Musik im Vordergrund

Farbwelt kann zunächst neutral gehalten werden.

Ein einzelnes visuelles Highlight kann beispielsweise für den aktuellen Tag oder wichtige Veranstaltungen verwendet werden.

---

# 29. Performance

Da die Daten als JSON ausgeliefert werden und die Anwendung statisch ist, soll die Performance sehr gut sein.

Ziele:

* keine Server-Requests pro Kalenderzelle
* JSON nur einmal laden
* Veranstaltungen im Browser filtern
* keine großen Bilder im MVP
* keine externe Datenbank

---

# 30. Fehlerbehandlung

Wenn die JSON-Datei nicht geladen werden kann:

```text
Die Veranstaltungsdaten konnten nicht geladen werden.

Bitte versuche es später erneut.
```

Wenn einzelne Veranstaltungen fehlerhafte Daten enthalten, darf dies nicht zum Absturz der gesamten Anwendung führen.

---

# 31. MVP-Funktionsumfang

Die erste veröffentlichungsfähige Version muss enthalten:

### Kalender

* [ ] aktueller Monat als Startansicht
* [ ] Monatsnavigation
* [ ] deutsche Monats- und Wochentagsnamen
* [ ] Anzeige von Veranstaltungen
* [ ] mehrere Veranstaltungen pro Tag
* [ ] klickbare Veranstaltungen
* [ ] Veranstaltungsdetails

### Ensembles und Orchester

* [ ] vollständige Ensembleliste
* [ ] Ort
* [ ] Chefdirigent:in
* [ ] musikalisches Profil
* [ ] Website
* [ ] Stammsaal / wichtigste Spielstätte
* [ ] Ensembledetailseite

### Spielstätten

* [ ] vollständige Spielstättenliste
* [ ] Spielstättenprofil
* [ ] Liste der dort stattfindenden Veranstaltungen

### Daten

* [ ] JSON-Schema
* [ ] Ensemble-Stammdaten
* [ ] Personen-Stammdaten
* [ ] Institutionen-Stammdaten
* [ ] Veranstaltungsdaten
* [ ] Veranstaltungsorte
* [ ] Quellen
* [ ] Versionierung

### Datenpflege

* [ ] Python-Validator
* [ ] Prüfung auf doppelte IDs
* [ ] Prüfung auf fehlende Referenzen
* [ ] Prüfung von Datum/Uhrzeit
* [ ] Änderungsreport

### Deployment

* [ ] statischer Build
* [ ] JSON wird mit ausgeliefert
* [ ] Deployment über Git
* [ ] reproduzierbarer Build

---

# 32. Akzeptanzkriterien

Das MVP gilt als erfolgreich umgesetzt, wenn:

### Kalender

1. Beim Öffnen wird der aktuelle Monat angezeigt.
2. Der Nutzer kann einen Monat vor/zurück navigieren.
3. Ein Konzert wird am korrekten Kalendertag angezeigt.
4. Die Kachel zeigt mindestens Titel, Orchester, Dirigent:in und Ort.
5. Mehrere Veranstaltungen am gleichen Tag werden unterstützt.
6. Eine Veranstaltung kann geöffnet werden.
7. Die Detailseite zeigt das vollständige gespeicherte Programm.
8. Quelle und Veranstaltungsort werden angezeigt.

### Orchester

9. Alle definierten NRW-Orchester sind vorhanden.
10. Jedes Orchester besitzt die erforderlichen Stammdaten.
11. Eine Orchesterseite listet die zugehörigen Veranstaltungen.

### Daten

12. Die Anwendung funktioniert vollständig ohne Backend.
13. Ein Austausch der JSON-Datei aktualisiert die Veranstaltungen nach einem neuen Deployment.
14. Das Python-Tool erkennt fehlerhafte Daten.
15. Das Python-Tool erkennt doppelte IDs.
16. Das Python-Tool erkennt ungültige Orchester-/Venue-Referenzen.

### Usability

17. Die Kalenderansicht funktioniert auf Desktop und Smartphone.
18. Veranstaltungen sind mit Tastatur erreichbar.
19. Direkte URLs zu Monat, Orchester und Veranstaltung funktionieren.

---

# 33. Erweiterungen nach dem MVP

Nach einer ersten stabilen Version bieten sich folgende Erweiterungen an:

## Phase 2 – Suche & Filter

* Suche nach Orchester
* Suche nach Komponist
* Filter nach Ort
* Filter nach musikalischem Schwerpunkt
* Filter nach Dirigent

## Phase 3 – Persönlicher Konzertplan

* Favoriten
* „Meine Konzerte“
* Export als iCal/ICS
* Kalenderintegration
* Erinnerungen

## Phase 4 – Kartenansicht ✓ umgesetzt

> **Status:** Umgesetzt in [US-013](planning/done/US-013-map-country.md). Unter der Route
> `/cities` (Navigationseintrag „Karte") zeigt eine Leaflet-/OpenStreetMap-Karte alle Orte mit
> ansässigem Ensemble als rote Marker; ein Klick öffnet einen Dialog mit den Ensembles des Ortes
> und setzt bzw. entfernt von dort den Ort-Filter. Spezifikation: [`ears/karte.md`](ears/karte.md)
> und [`contracts/karte.feature`](contracts/karte.feature).

Eine geografische NRW-Karte zeigt:

```text
              Bielefeld
                   ●

       Münster ●

              ● Herford

     Essen ●   ● Dortmund

Duisburg ● ● Bochum ●

       Düsseldorf ●
             ● Wuppertal
       Solingen ●

 Köln ●
        ● Bonn

Aachen ●
```

Beim Klick auf einen Ort werden die dort ansässigen Orchester und kommenden Veranstaltungen angezeigt.

## Phase 5 – Automatisierte Datenpflege

Das Python-/Skill-System kann regelmäßig:

* offizielle Spielpläne prüfen,
* neue Termine erkennen,
* Änderungen melden,
* abgesagte Konzerte erkennen,
* Quellen aktualisieren.

---

# 34. Datenpflege als zentrale Produktfunktion

Obwohl die Webanwendung selbst relativ einfach ist, ist die **Qualität und Aktualität der JSON-Daten der wichtigste Teil des Produkts**.

Daher soll das Projekt von Anfang an zwei klar getrennte Komponenten besitzen:

```text
nrw-orchester/
│
├── web/
│   └── Webapplikation
│
├── data/
│   ├── people.json
│   ├── institutions.json
│   ├── ensembles.json
│   ├── venues.json
│   ├── works.json
│   └── events.json
│
├── data-tool/
│   ├── validator
│   ├── updater
│   └── reports
│
├── schema/
│   └── klangland.schema.json
│
└── README.md
```

Die Webanwendung darf **keine Logik zur Datenbeschaffung** enthalten.

Sie konsumiert ausschließlich die geprüfte JSON-Datei.

---

# 35. Grundprinzip der Datenhoheit

Die JSON-Datei ist die **Single Source of Truth** für die Webanwendung.

```text
Recherche
    ↓
Rohinformationen
    ↓
Datenaufbereitung
    ↓
Validierung
    ↓
getrennte JSON-Dateien
    ↓
Git
    ↓
Deploy
    ↓
Webapp
```

Dadurch bleibt die Anwendung:

* einfach,
* schnell,
* unabhängig von externen APIs,
* leicht zu sichern,
* versionierbar,
* reproduzierbar.

---

# 36. Erfolgskriterium des Gesamtprojekts

Das Projekt ist erfolgreich, wenn ein Klassikinteressierter die Seite öffnet und innerhalb weniger Sekunden beantworten kann:

> **Was kann ich diesen Monat in NRW hören?**

und anschließend mit maximal zwei Klicks weiß:

> **Was wird gespielt, von wem, wann und wo?**

Die Anwendung soll dabei nicht versuchen, einen vollständigen Konzertführer für Deutschland zu ersetzen. Ihr Kern ist eine **hochwertige, gepflegte und übersichtliche Konzertübersicht der professionellen Orchester in Nordrhein-Westfalen**.

---

# 37. Empfohlene nächste Umsetzungsschritte

Die Entwicklung sollte in dieser Reihenfolge erfolgen:

1. **Ensemble-, Institutionen- und Venue-Modell endgültig festlegen**
2. JSON Schema definieren
3. vollständige Ensemble-, Personen- und Institutionen-Stammdaten erfassen
4. Veranstaltungsorte erfassen
5. Spielpläne 2026/27 recherchieren und JSON aufbauen
6. Python-Validator entwickeln
7. Kalender-UI entwickeln
8. Veranstaltungsdetailseite entwickeln
9. Ensemble- und Spielstättenprofile entwickeln
10. responsive/mobile Darstellung
11. Deployment einrichten
12. Datenaktualisierungs-Skill/Python-Updater entwickeln
13. erste vollständige Datenaktualisierung durchführen
14. anschließend Kartenansicht und Filter als nächste Ausbaustufe

**Wichtig:** Die Entwicklung sollte zunächst mit einer kleinen, aber realen Datenmenge (z. B. 3 Orchester und jeweils 5–10 Veranstaltungen) erfolgen. Erst wenn Datenmodell, Kalender und Detailansicht funktionieren, sollte der komplette NRW-Datensatz eingepflegt werden. Dadurch werden Änderungen am Datenmodell erheblich einfacher.
