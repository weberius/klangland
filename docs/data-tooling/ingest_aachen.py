#!/usr/bin/env python3
"""
Ingest-Skript für das Sinfonieorchester Aachen, Spielzeit 2026/27.

Quelle: https://www.theateraachen.de/de/seiten/konzerte-2627.html
        + Detailseiten der einzelnen Sinfoniekonzerte.

Erfasst werden die acht Sinfoniekonzerte (je zwei Aufführungen) im Eurogress Aachen.
Kammerkonzerte (Kammerensembles der Orchestermusiker:innen) sowie Sonderkonzerte mit
Fremdensembles (»Wunschkonzert« des Western Balkans Youth Orchestra, Wildes Holz
»Block-Party«) gehören nicht zum Kernspielplan des Orchesters und werden ausgelassen.

Die Programm-, Besetzungs- und Termindaten wurden aus den Detailseiten kuratiert und sind
hier als Konstanten hinterlegt. Das Skript ist idempotent: bei erneutem Lauf werden die
zuvor eingespielten Aachen-Events (erkannt an Quell-Host + Ensemble) entfernt und neu
angelegt; Stammdaten (Venue, Komponist:innen, Werke, Personen) werden anhand ihrer IDs
dublettenfrei ergänzt.

Aufruf:  python3 docs/data-tooling/ingest_aachen.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# --- Konstanten -------------------------------------------------------------

SOURCE_HOST = "theateraachen.de"
SOURCE_NAME = "Theater Aachen"
ENSEMBLE_ID = "sinfonieorchester-aachen"
CITY_ID = "aachen"
VENUE_ID = "eurogress-aachen"
RETRIEVED_AT = "2026-08-18"

# Neue Spielstätte (Konzertsaal der Aachener Sinfoniekonzerte).
NEW_VENUE = {
    "id": VENUE_ID,
    "name": "Eurogress Aachen",
    "cityIds": [CITY_ID],
    "region": None,
    "address": "Monheimsallee 48, 52062 Aachen",
    "coordinates": None,
    "website": "https://www.eurogress-aachen.de",
    "type": "concert_hall",
    "institutionId": None,
}

# Neue Komponist:innen (nur die im Bestand noch fehlenden).
NEW_COMPOSERS = {
    "john-rutter": {"id": "john-rutter", "name": "John Rutter", "life": {"from": 1945, "to": None}},
    "lili-boulanger": {"id": "lili-boulanger", "name": "Lili Boulanger", "life": {"from": 1893, "to": 1918}},
    "alberto-ginastera": {"id": "alberto-ginastera", "name": "Alberto Ginastera", "life": {"from": 1916, "to": 1983}},
    "xavier-montsalvatge": {"id": "xavier-montsalvatge", "name": "Xavier Montsalvatge", "life": {"from": 1912, "to": 2002}},
    "manuel-de-falla": {"id": "manuel-de-falla", "name": "Manuel de Falla", "life": {"from": 1876, "to": 1946}},
    "alexander-borodin": {"id": "alexander-borodin", "name": "Alexander Borodin", "life": {"from": 1833, "to": 1887}},
    "jennifer-higdon": {"id": "jennifer-higdon", "name": "Jennifer Higdon", "life": {"from": 1962, "to": None}},
    "giuseppe-verdi": {"id": "giuseppe-verdi", "name": "Giuseppe Verdi", "life": {"from": 1813, "to": 1901}},
    "andrea-tarrodi": {"id": "andrea-tarrodi", "name": "Andrea Tarrodi", "life": {"from": 1981, "to": None}},
}


def work(work_id, composer_id, title, genre, catalogue=None, year=None):
    """Hilfsfunktion für einen Werk-Datensatz im Zielschema."""
    return {
        "id": work_id,
        "composerId": composer_id,
        "title": title,
        "catalogue": catalogue or [],
        "yearComposed": ({"from": year[0], "to": year[1]} if year else None),
        "genre": genre,
        "durationMinutes": None,
        "version": None,
        "scoring": None,
        "description": None,
    }


def opus(n):
    return [{"system": "Opus", "number": n}]


# Neue Werke (nur die im Bestand noch fehlenden). Vorhandene Werke werden über ihre
# IDs wiederverwendet (kodaly-galantai-tancok, gershwin-amerikaner-in-paris).
NEW_WORKS = {
    # 1. Sinfoniekonzert
    "elgar-wand-of-youth-suite-1": work(
        "elgar-wand-of-youth-suite-1", "edward-elgar",
        "»The Wand of Youth« – Suite Nr. 1", "other", opus("1a"), (1907, 1907)),
    "rutter-partita": work(
        "rutter-partita", "john-rutter", "Partita", "other"),
    "boulanger-dun-matin-de-printemps": work(
        "boulanger-dun-matin-de-printemps", "lili-boulanger",
        "»D'un matin de printemps«", "other", None, (1917, 1918)),
    "ravel-daphnis-et-chloe-auszuege": work(
        "ravel-daphnis-et-chloe-auszuege", "maurice-ravel",
        "»Daphnis et Chloé« – Symphonie chorégraphique (Auszüge)", "other", None, (1909, 1912)),
    # 2. Sinfoniekonzert
    "ginastera-estancia-tanze": work(
        "ginastera-estancia-tanze", "alberto-ginastera",
        "Tänze aus dem Ballett »Estancia«", "other", opus("8a"), (1941, 1941)),
    "montsalvatge-sinfonietta-concerto": work(
        "montsalvatge-sinfonietta-concerto", "xavier-montsalvatge",
        "»Sinfonietta-concerto« für Flöte und Orchester", "concerto"),
    "falla-el-amor-brujo-suite": work(
        "falla-el-amor-brujo-suite", "manuel-de-falla",
        "Suite aus »El amor brujo«", "other", None, (1915, 1915)),
    # 3. Sinfoniekonzert (kodaly-galantai-tancok wird wiederverwendet)
    "dohnanyi-variationen-kinderlied": work(
        "dohnanyi-variationen-kinderlied", "ernst-von-dohnanyi",
        "»Variationen über ein Kinderlied« für Orchester mit konzertantem Klavier",
        "other", opus("25"), (1914, 1914)),
    "brahms-sinfonie-4": work(
        "brahms-sinfonie-4", "johannes-brahms",
        "Sinfonie Nr. 4 e-Moll", "symphony", opus("98"), (1884, 1885)),
    # 4. Sinfoniekonzert
    "tschaikowsky-violinkonzert": work(
        "tschaikowsky-violinkonzert", "peter-iljitsch-tschaikowsky",
        "Konzert für Violine und Orchester D-Dur", "concerto", opus("35"), (1878, 1878)),
    "borodin-fuerst-igor-ouvertuere": work(
        "borodin-fuerst-igor-ouvertuere", "alexander-borodin",
        "Ouvertüre zu »Fürst Igor«", "overture", None, (1869, 1887)),
    "schostakowitsch-sinfonie-9": work(
        "schostakowitsch-sinfonie-9", "dmitri-schostakowitsch",
        "Sinfonie Nr. 9 Es-Dur", "symphony", opus("70"), (1945, 1945)),
    # 5. Sinfoniekonzert (gershwin-amerikaner-in-paris wird wiederverwendet)
    "higdon-percussion-concerto": work(
        "higdon-percussion-concerto", "jennifer-higdon",
        "Concerto for Percussion", "concerto", None, (2005, 2005)),
    "dvorak-sinfonie-9-neue-welt": work(
        "dvorak-sinfonie-9-neue-welt", "antonin-dvorak",
        "Sinfonie Nr. 9 e-Moll »Aus der Neuen Welt«", "symphony", opus("95"), (1893, 1893)),
    # 6. Sinfoniekonzert
    "beethoven-leonore-ouvertuere-3": work(
        "beethoven-leonore-ouvertuere-3", "ludwig-van-beethoven",
        "Ouvertüre Nr. 3 zu »Leonore«", "overture", opus("72b"), (1806, 1806)),
    "beethoven-klavierkonzert-5": work(
        "beethoven-klavierkonzert-5", "ludwig-van-beethoven",
        "Konzert für Klavier und Orchester Nr. 5 Es-Dur", "concerto", opus("73"), (1809, 1809)),
    "berlioz-symphonie-fantastique": work(
        "berlioz-symphonie-fantastique", "hector-berlioz",
        "»Symphonie fantastique«", "symphony", opus("14"), (1830, 1830)),
    # 7. Sinfoniekonzert
    "verdi-messa-da-requiem": work(
        "verdi-messa-da-requiem", "giuseppe-verdi",
        "Messa da Requiem", "requiem", None, (1874, 1874)),
    # 8. Sinfoniekonzert
    "brahms-violinkonzert": work(
        "brahms-violinkonzert", "johannes-brahms",
        "Konzert für Violine und Orchester D-Dur", "concerto", opus("77"), (1878, 1878)),
    "tarrodi-fragments-of-enlightenment": work(
        "tarrodi-fragments-of-enlightenment", "andrea-tarrodi",
        "»Fragments of Enlightenment«", "other"),
    "mozart-sinfonie-39": work(
        "mozart-sinfonie-39", "wolfgang-amadeus-mozart",
        "Sinfonie Nr. 39 Es-Dur", "symphony", [{"system": "KV", "number": "543"}], (1788, 1788)),
}

# Neue Personen (Dirigent:innen/Solist:innen); levente-toeroek existiert bereits.
NEW_PEOPLE = [
    {"id": "tomas-grau", "name": "Tomàs Grau"},
    {"id": "felix-mildenberger", "name": "Felix Mildenberger"},
    {"id": "riccardo-frizza", "name": "Riccardo Frizza"},
    {"id": "clara-andrada", "name": "Clara Andrada"},
    {"id": "alexandra-urquiola", "name": "Alexandra Urquiola"},
    {"id": "jozsef-balog", "name": "József Balog"},
    {"id": "francesco-de-angelis", "name": "Francesco de Angelis"},
    {"id": "alexej-gerassimez", "name": "Alexej Gerassimez"},
    {"id": "eloise-bella-kohn", "name": "Eloïse Bella Kohn"},
    {"id": "larisa-akbari", "name": "Larisa Akbari"},
    {"id": "mario-rojas", "name": "Mario Rojas"},
    {"id": "max-bell", "name": "Max Bell"},
    {"id": "giulia-rimonda", "name": "Giulia Rimonda"},
]

# Die acht Sinfoniekonzerte. Je Konzert zwei Aufführungen (Sa 19:00 / So 18:00).
# Termine: (Datum, Uhrzeit, Reservix-Ticket-URL).
CONCERTS = [
    {
        "num": 1,
        "title": "1. Sinfoniekonzert",
        "slug": "1-sinfoniekonzert-3",
        "dates": [
            ("2026-09-19", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545031"),
            ("2026-09-20", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549457"),
        ],
        "conductorIds": ["levente-toeroek"],
        "soloistIds": [],
        "programWorkIds": [
            "elgar-wand-of-youth-suite-1",
            "rutter-partita",
            "boulanger-dun-matin-de-printemps",
            "ravel-daphnis-et-chloe-auszuege",
        ],
        "description": (
            "Antrittskonzert des neuen Generalmusikdirektors Levente Török. Mit Opernchor "
            "Aachen und Sinfonischem Chor Aachen (Choreinstudierung: Alexander Einarsson)."
        ),
    },
    {
        "num": 2,
        "title": "2. Sinfoniekonzert",
        "slug": "2-sinfoniekonzert-3",
        "dates": [
            ("2026-10-17", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545694"),
            ("2026-10-18", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549458"),
        ],
        "conductorIds": ["tomas-grau"],
        "soloistIds": ["clara-andrada", "alexandra-urquiola"],
        "programWorkIds": [
            "ginastera-estancia-tanze",
            "montsalvatge-sinfonietta-concerto",
            "falla-el-amor-brujo-suite",
        ],
        "description": None,
    },
    {
        "num": 3,
        "title": "3. Sinfoniekonzert",
        "slug": "3-sinfoniekonzert-3",
        "dates": [
            ("2026-11-14", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545702"),
            ("2026-11-15", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549476"),
        ],
        "conductorIds": ["levente-toeroek"],
        "soloistIds": ["jozsef-balog"],
        "programWorkIds": [
            "kodaly-galantai-tancok",
            "dohnanyi-variationen-kinderlied",
            "brahms-sinfonie-4",
        ],
        "description": None,
    },
    {
        "num": 4,
        "title": "4. Sinfoniekonzert",
        "slug": "4-sinfoniekonzert-3",
        "dates": [
            ("2027-02-13", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545711"),
            ("2027-02-14", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549477"),
        ],
        "conductorIds": ["levente-toeroek"],
        "soloistIds": ["francesco-de-angelis"],
        "programWorkIds": [
            "tschaikowsky-violinkonzert",
            "borodin-fuerst-igor-ouvertuere",
            "schostakowitsch-sinfonie-9",
        ],
        "description": None,
    },
    {
        "num": 5,
        "title": "5. Sinfoniekonzert",
        "slug": "5-sinfoniekonzert-3",
        "dates": [
            ("2027-03-20", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545932"),
            ("2027-03-21", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549478"),
        ],
        "conductorIds": ["felix-mildenberger"],
        "soloistIds": ["alexej-gerassimez"],
        "programWorkIds": [
            "gershwin-amerikaner-in-paris",
            "higdon-percussion-concerto",
            "dvorak-sinfonie-9-neue-welt",
        ],
        "description": None,
    },
    {
        "num": 6,
        "title": "6. Sinfoniekonzert",
        "slug": "6-sinfoniekonzert-3",
        "dates": [
            ("2027-04-24", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545938"),
            ("2027-04-25", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549480"),
        ],
        "conductorIds": ["riccardo-frizza"],
        "soloistIds": ["eloise-bella-kohn"],
        "programWorkIds": [
            "beethoven-leonore-ouvertuere-3",
            "beethoven-klavierkonzert-5",
            "berlioz-symphonie-fantastique",
        ],
        "description": None,
    },
    {
        "num": 7,
        "title": "7. Sinfoniekonzert",
        "slug": "7-sinfoniekonzert-3",
        "dates": [
            ("2027-05-22", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2545982"),
            ("2027-05-23", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549488"),
        ],
        "conductorIds": ["levente-toeroek"],
        "soloistIds": ["larisa-akbari", "mario-rojas", "max-bell"],
        "programWorkIds": ["verdi-messa-da-requiem"],
        "description": (
            "Verdis »Messa da Requiem« mit Sinfonieorchester Aachen, Opernchor Aachen und "
            "Sinfonischem Chor Aachen. In Kooperation mit der Chorbiennale."
        ),
    },
    {
        "num": 8,
        "title": "8. Sinfoniekonzert",
        "slug": "8-sinfoniekonzert-3",
        "dates": [
            ("2027-06-19", "19:00", "https://theateraachen.reservix.de/p/reservix/event/2546149"),
            ("2027-06-20", "18:00", "https://theateraachen.reservix.de/p/reservix/event/2549517"),
        ],
        "conductorIds": ["levente-toeroek"],
        "soloistIds": ["giulia-rimonda"],
        "programWorkIds": [
            "brahms-violinkonzert",
            "tarrodi-fragments-of-enlightenment",
            "mozart-sinfonie-39",
        ],
        "description": None,
    },
]


# --- Ein-/Ausgabe -----------------------------------------------------------

def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def detail_url(slug: str) -> str:
    return f"https://www.theateraachen.de/de/produktionen/{slug}.html"


def event_id(date: str, num: int) -> str:
    return f"event-{date}-aachen-{num}-sinfoniekonzert"


def main() -> int:
    repo = Path(__file__).resolve().parent.parent.parent
    data = repo / "data"

    events_doc = load(data / "events.json")
    venues_doc = load(data / "venues.json")
    composers_doc = load(data / "composers.json")
    works_doc = load(data / "works.json")
    people_doc = load(data / "people.json")

    print("=== Sinfonieorchester Aachen – Ingest 2026/27 ===\n")

    # 1) Venue ergänzen
    venue_ids = {v["id"] for v in venues_doc["venues"]}
    if NEW_VENUE["id"] not in venue_ids:
        venues_doc["venues"].append(NEW_VENUE)
        print(f"+ Venue: {NEW_VENUE['id']}")
    else:
        print(f"= Venue vorhanden: {NEW_VENUE['id']}")

    # 2) Komponist:innen ergänzen
    composer_ids = {c["id"] for c in composers_doc["composers"]}
    added_c = 0
    for cid, rec in NEW_COMPOSERS.items():
        if cid not in composer_ids:
            composers_doc["composers"].append(rec)
            composer_ids.add(cid)
            added_c += 1
    print(f"+ Komponist:innen neu: {added_c} (Bestand: {len(composer_ids)})")

    # 3) Werke ergänzen (referenzierte Komponist:innen müssen existieren)
    work_ids = {w["id"] for w in works_doc["works"]}
    added_w = 0
    for wid, rec in NEW_WORKS.items():
        if rec["composerId"] not in composer_ids:
            print(f"! Werk {wid}: Komponist {rec['composerId']} fehlt – übersprungen")
            continue
        if wid not in work_ids:
            works_doc["works"].append(rec)
            work_ids.add(wid)
            added_w += 1
    print(f"+ Werke neu: {added_w} (Bestand: {len(work_ids)})")

    # 4) Personen ergänzen
    person_ids = {p["id"] for p in people_doc["people"]}
    added_p = 0
    for rec in NEW_PEOPLE:
        if rec["id"] not in person_ids:
            people_doc["people"].append(rec)
            person_ids.add(rec["id"])
            added_p += 1
    print(f"+ Personen neu: {added_p} (Bestand: {len(person_ids)})")

    # 5) Alte Aachen-Events entfernen (idempotent): Quelle theateraachen.de + Ensemble
    def is_ours(e: Dict[str, Any]) -> bool:
        src = (e.get("source") or {}).get("url", "") or ""
        return SOURCE_HOST in src and ENSEMBLE_ID in e.get("ensembleIds", [])

    before = len(events_doc["events"])
    events_doc["events"] = [e for e in events_doc["events"] if not is_ours(e)]
    removed = before - len(events_doc["events"])
    print(f"- Alte Aachen-Events entfernt: {removed}")

    # 6) Neue Events anlegen
    new_events: List[Dict[str, Any]] = []
    for c in CONCERTS:
        program = [{"workId": wid} for wid in c["programWorkIds"]]
        for date, start_time, ticket_url in c["dates"]:
            new_events.append({
                "id": event_id(date, c["num"]),
                "title": c["title"],
                "eventType": "concert",
                "date": date,
                "startTime": start_time,
                "endTime": None,
                "status": "scheduled",
                "ensembleIds": [ENSEMBLE_ID],
                "venueId": VENUE_ID,
                "cityId": CITY_ID,
                "conductorPersonIds": list(c["conductorIds"]),
                "soloistPersonIds": list(c["soloistIds"]),
                "program": program,
                "seriesId": None,
                "description": c["description"],
                "source": {
                    "url": detail_url(c["slug"]),
                    "name": SOURCE_NAME,
                    "retrievedAt": RETRIEVED_AT,
                },
                "ticketUrl": ticket_url,
                "lastVerified": RETRIEVED_AT,
            })

    events_doc["events"].extend(new_events)
    print(f"+ Neue Aachen-Events: {len(new_events)}")

    # 7) Metadaten aktualisieren
    events_doc.setdefault("metadata", {})
    events_doc["metadata"]["lastUpdated"] = RETRIEVED_AT

    # 8) Speichern
    save(data / "events.json", events_doc)
    save(data / "venues.json", venues_doc)
    save(data / "composers.json", composers_doc)
    save(data / "works.json", works_doc)
    save(data / "people.json", people_doc)

    print("\n✓ Ingest abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
