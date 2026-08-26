#!/usr/bin/env python3
"""Ingest the Philharmonie Südwestfalen 2026/27 schedule into klangland ``data/*.json``.

Source: PhilSW-Spielzeitbuch 2026/27 (PDF season programme book), published at
https://www.philsw.de/wp-content/uploads/2026/07/PhilSW-Spielzeitbuch-2026-27.pdf
The orchestra's own event calendar on philsw.de is not consistently maintained; the
season book is the more complete and current primary source and is therefore used
directly. There is no per-event web page, so ``source.url`` points at the PDF for
every event (see ``docs/data-tooling/philharmonie-suedwestfalen.md`` for details).

Scope (curated, Option B — enriched work/composer metadata):
  * Only performances taking place in Nordrhein-Westfalen are ingested, consistent
    with the project scope ("Konzertveranstaltungen in Nordrhein-Westfalen", see
    README.md) and the precedent set by ingest_hagen.py (out-of-city/out-of-region
    guest performances are excluded, not mis-attributed). Guest performances in
    Rheinland-Pfalz (Betzdorf, Wirges, Höhn), Hessen (Dillenburg), Bayern (München),
    Niedersachsen (Wolfsburg) and the Netherlands (Amsterdam) are therefore omitted;
    productions with *no* remaining NRW performance are dropped entirely.
  * Closed/non-public events (Kita-only "Konzerte für Entdecker", "Schulkonzerte"
    marked "geschlossene Veranstaltung") are excluded, consistent with the precedent
    in ingest_bochum.py (reine Schulkonzert-Termine ohne öffentlichen Verkauf).
  * KulturPur35 (13.–17. Mai 2027) has no fixed date in the season book ("genaues
    Datum N.N.") and is therefore not ingested (no valid single date available).

Idempotent: re-running removes previously ingested PhilSW events (matched by the
source host philsw.de) and merges master data (people, works, composers, venues,
cities) without creating duplicates. New venues are written with
``coordinates``/``address`` set to ``null``; run ``fetch_venue_addresses.py``
afterwards to research them via OpenStreetMap (existing project tool, US-022).

Usage:
    python docs/data-tooling/ingest_philsw.py
    python docs/data-tooling/ingest_philsw.py --date 2026-08-26
"""
import argparse
import datetime
import json
import os
import re
import sys
import unicodedata

SRC_HOST = "philsw.de"
SRC_NAME = "Philharmonie Südwestfalen"
SRC_URL = "https://www.philsw.de/wp-content/uploads/2026/07/PhilSW-Spielzeitbuch-2026-27.pdf"
CALENDAR_URL = "https://www.philsw.de/"
ENSEMBLE_ID = "philharmonie-suedwestfalen"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")

_ap = argparse.ArgumentParser(description="Ingest Philharmonie Südwestfalen schedule (Spielzeitbuch 2026/27)")
_ap.add_argument("--date", default=datetime.date.today().isoformat(),
                  help="retrievedAt/lastVerified date (YYYY-MM-DD)")
ARGS = _ap.parse_args()
TODAY = ARGS.date

# ---------- generic helpers (shared idiom with the other ingest_*.py scripts) ----------
_UML = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "ae", "Ö": "oe", "Ü": "ue", "ß": "ss"}


def fold(s):
    s = s.strip().lower()
    for k, v in _UML.items():
        s = s.replace(k.lower(), v)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def load(name):
    with open(f"{DATA}/{name}.json", encoding="utf-8") as f:
        return json.load(f)


def save(name, obj):
    with open(f"{DATA}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def cat(system, number):
    return {"system": system, "number": number}


# ---------- new master data: cities ----------
# Minimal records (no resident ensemble ⇒ no plate/coordinates, per existing convention).
NEW_CITIES = [
    {"id": "lennestadt", "name": "Lennestadt", "country": "Deutschland"},
    {"id": "hilchenbach", "name": "Hilchenbach", "country": "Deutschland"},
    {"id": "burbach", "name": "Burbach", "country": "Deutschland"},
    {"id": "arnsberg", "name": "Arnsberg", "country": "Deutschland"},
    {"id": "bad-laasphe", "name": "Bad Laasphe", "country": "Deutschland"},
    {"id": "kreuztal", "name": "Kreuztal", "country": "Deutschland"},
    {"id": "luedenscheid", "name": "Lüdenscheid", "country": "Deutschland"},
    {"id": "schmallenberg", "name": "Schmallenberg", "country": "Deutschland"},
    {"id": "olsberg", "name": "Olsberg", "country": "Deutschland"},
    {"id": "attendorn", "name": "Attendorn", "country": "Deutschland"},
    {"id": "iserlohn", "name": "Iserlohn", "country": "Deutschland"},
    {"id": "oberhausen", "name": "Oberhausen", "country": "Deutschland"},
    {"id": "bad-berleburg", "name": "Bad Berleburg", "country": "Deutschland"},
    {"id": "wilnsdorf", "name": "Wilnsdorf", "country": "Deutschland"},
    {"id": "kierspe", "name": "Kierspe", "country": "Deutschland"},
    {"id": "neunkirchen-siegerland", "name": "Neunkirchen (Siegerland)", "country": "Deutschland"},
    {"id": "warstein", "name": "Warstein", "country": "Deutschland"},
    {"id": "bad-lippspringe", "name": "Bad Lippspringe", "country": "Deutschland"},
    {"id": "hamm", "name": "Hamm", "country": "Deutschland"},
]

# ---------- new master data: venues ----------
# coordinates/address left null; fetch_venue_addresses.py fills them in later (US-022).
NEW_VENUES = [
    ("schlossplatz-muenster", "Schlossplatz Münster", ["muenster"], "other"),
    ("schuetzenhalle-grevenbrueck", "Schützenhalle Grevenbrück", ["lennestadt"], "other"),
    ("kultureller-marktplatz-hilchenbach", "Kultureller Marktplatz Hilchenbach-Dahlbruch", ["hilchenbach"], "other"),
    ("kirche-am-roemer-burbach", "Kirche am Römer Burbach", ["burbach"], "other"),
    ("apollo-theater-siegen", "Apollo-Theater Siegen", ["siegen"], "theatre"),
    ("theater-lippstadt", "Theater Lippstadt", ["lippstadt"], "theatre"),
    ("st-johannes-kirche-arnsberg-neheim", "St. Johannes Kirche Arnsberg-Neheim", ["arnsberg"], "other"),
    ("haus-der-musik-siegen", "Haus der Musik Siegen", ["siegen"], "concert_hall"),
    ("aula-gymnasium-bad-laasphe", "Aula des Gymnasiums Bad Laasphe", ["bad-laasphe"], "other"),
    ("stift-keppel-konventssaal-hilchenbach", "Stift Keppel Konventssaal", ["hilchenbach"], "other"),
    ("otto-flick-halle-kreuztal", "Otto-Flick-Halle Kreuztal", ["kreuztal"], "other"),
    ("kulturhaus-luedenscheid", "Kulturhaus Lüdenscheid", ["luedenscheid"], "other"),
    ("stadthalle-schmallenberg", "Stadthalle Schmallenberg", ["schmallenberg"], "other"),
    ("kath-kirche-st-alexander-schmallenberg", "Kath. Kirche St. Alexander Schmallenberg", ["schmallenberg"], "other"),
    ("kath-kirche-st-martin-olsberg-bigge", "Kath. Kirche St. Martin Olsberg-Bigge", ["olsberg"], "other"),
    ("pfarrkirche-st-johannes-baptist-attendorn", "Pfarrkirche St. Johannes Baptist Attendorn", ["attendorn"], "other"),
    ("parktheater-iserlohn", "Parktheater Iserlohn", ["iserlohn"], "theatre"),
    ("metronom-theater-oberhausen", "Metronom-Theater Oberhausen", ["oberhausen"], "theatre"),
    ("ev-kirche-hilchenbach", "Ev. Kirche Hilchenbach", ["hilchenbach"], "other"),
    ("paedagogisches-zentrum-lennestadt", "Pädagogisches Zentrum Lennestadt", ["lennestadt"], "other"),
    ("festhalle-wilnsdorf", "Festhalle Wilnsdorf", ["wilnsdorf"], "other"),
    ("paedagogisches-zentrum-gesamtschule-kierspe", "Pädagogisches Zentrum der Gesamtschule Kierspe", ["kierspe"], "other"),
    ("erloeserkirche-neunkirchen-siegerland", "Erlöserkirche Neunkirchen", ["neunkirchen-siegerland"], "other"),
    ("neue-aula-warstein", "Neue Aula Warstein", ["warstein"], "other"),
    ("museum-oberes-schloss-siegen", "Museum Oberes Schloss Siegen", ["siegen"], "other"),
    ("sauerlandhalle-lennestadt", "Sauerlandhalle Lennestadt", ["lennestadt"], "other"),
    ("buergerhaus-bad-berleburg", "Bürgerhaus Bad Berleburg", ["bad-berleburg"], "other"),
    ("ev-kirche-bad-lippspringe", "Ev. Kirche Bad Lippspringe", ["bad-lippspringe"], "other"),
    ("kurhaus-hamm", "Kurhaus Hamm", ["hamm"], "other"),
    ("ginsburg-turmzimmer-hilchenbach", "Ginsburg Turmzimmer Hilchenbach-Lützel", ["hilchenbach"], "other"),
    ("aula-gymnasium-wilnsdorf", "Aula des Gymnasiums Wilnsdorf", ["wilnsdorf"], "other"),
    ("marktplatz-hilchenbach", "Marktplatz Hilchenbach", ["hilchenbach"], "other"),
    ("dreslers-park-kreuztal", "Dreslers Park Kreuztal", ["kreuztal"], "other"),
]
# Existing venues reused as-is (no new record): koelner-philharmonie, beethovenhalle-bonn,
# stadthalle-bielefeld, eurogress-aachen.

# ---------- new master data: composers ----------
# (id, name, birth, death-or-None) — life dates as printed in the season book.
NEW_COMPOSERS = [
    ("joseph-martin-kraus", "Joseph Martin Kraus", 1756, 1792),
    ("kevin-puts", "Kevin Puts", 1972, None),
    ("igor-stravinsky", "Igor Stravinsky", 1882, 1971),
    ("georg-philipp-telemann", "Georg Philipp Telemann", 1681, 1767),
    ("antonio-salieri", "Antonio Salieri", 1750, 1825),
    ("johann-strauss-vater", "Johann Strauß (Vater)", 1804, 1848),
    ("carl-ditters-von-dittersdorf", "Carl Ditters von Dittersdorf", 1739, 1799),
    ("fritz-kreisler", "Fritz Kreisler", 1875, 1962),
    ("jules-massenet", "Jules Massenet", 1842, 1912),
    ("reynaldo-hahn", "Reynaldo Hahn", 1874, 1947),
    ("hans-gal", "Hans Gál", 1890, 1987),
    ("adolf-busch", "Adolf Busch", 1891, 1952),
    ("ferruccio-busoni", "Ferruccio Busoni", 1866, 1924),
    ("franz-ignaz-danzi", "Franz Ignaz Danzi", 1763, 1826),
]
# Already present in composers.json (reused as-is, not re-added; existing life dates kept):
# augusta-holmes, anna-clyne, louis-spohr, ottorino-respighi, cesar-franck, johan-halvorsen,
# engelbert-humperdinck, jennifer-higdon.

# ---------- new master data: works ----------
# W(id, composerId, title, catalogue-list, yearFrom, yearTo, genre, duration=None)
def W(wid, cid, title, catalogue, yf, yt, genre):
    return {"id": wid, "composerId": cid, "title": title, "catalogue": catalogue,
            "yearComposed": ({"from": yf, "to": yt} if yf else None), "genre": genre,
            "durationMinutes": None, "version": None, "scoring": None, "description": None}


NEW_WORKS = [
    W("wagner-vorspiel-tristan-und-isolde", "richard-wagner",
      "Vorspiel zu »Tristan und Isolde«", [cat("WWV", "90")], 1857, 1857, "overture"),
    W("wagner-meistersinger-vorspiel-3-akt", "richard-wagner",
      "Vorspiel zum dritten Akt aus »Die Meistersinger von Nürnberg«", [cat("WWV", "96")], 1862, 1862, "overture"),
    W("mozart-ouvertuere-don-giovanni", "wolfgang-amadeus-mozart",
      "Ouvertüre zu »Don Giovanni«", [cat("KV", "527")], 1787, 1787, "overture"),
    W("mozart-violinkonzert-d-dur-kv218", "wolfgang-amadeus-mozart",
      "Violinkonzert D-Dur", [cat("KV", "218")], 1775, 1775, "concerto"),
    W("kraus-ouvertuere-olympie", "joseph-martin-kraus",
      "Ouvertüre zur Oper »Olympie«", [cat("VB", "33")], None, None, "overture"),
    W("mendelssohn-sinfonie-3-schottische", "felix-mendelssohn-bartholdy",
      "Sinfonie Nr. 3 a-Moll »Schottische Sinfonie«", [cat("Opus", "56")], 1829, 1831, "symphony"),
    W("mayer-ouvertuere-nr-2-d-dur", "emilie-mayer", "Ouvertüre Nr. 2 D-Dur", [], 1850, 1850, "overture"),
    W("mayer-sinfonie-nr-7-f-moll", "emilie-mayer", "Sinfonie Nr. 7 f-Moll", [], 1856, 1856, "symphony"),
    W("puts-virelai", "kevin-puts", "Virelai after Guillaume de Machaut", [], 2019, 2019, "other"),
    W("bruch-kol-nidrei", "max-bruch",
      "»Kol Nidrei« für Violoncello und Orchester", [cat("Opus", "47")], 1880, 1880, "other"),
    W("stravinsky-monumentum-pro-gesualdo", "igor-stravinsky",
      "»Monumentum pro Gesualdo«", [], 1960, 1960, "other"),
    W("bach-brandenburgisches-konzert-3", "johann-sebastian-bach",
      "Brandenburgisches Konzert Nr. 3 G-Dur", [cat("BWV", "1048")], 1718, 1718, "concerto"),
    W("bach-schafe-koennen-sicher-weiden", "johann-sebastian-bach",
      "»Schafe können sicher weiden« aus der Kantate", [cat("BWV", "208")], None, None, "other"),
    W("telemann-sinfonia-spirituosa", "georg-philipp-telemann",
      "»Sinfonia spirituosa« D-Dur", [cat("TWV", "44:1")], None, None, "symphony"),
    W("corelli-concerto-8-notte-di-natale", "arcangelo-corelli",
      "Concerto Nr. 8 g-Moll »Fatto per la notte di natale«", [cat("Opus", "6/8")], None, None, "concerto"),
    W("bach-wir-eilen-bwv78", "johann-sebastian-bach",
      "»Wir eilen« aus Kantate »Jesu, der du meine Seele«", [cat("BWV", "78")], 1724, 1724, "other"),
    W("mozart-sinfonie-29-a-dur", "wolfgang-amadeus-mozart",
      "Sinfonie Nr. 29 A-Dur", [cat("KV", "201")], 1774, 1774, "symphony"),
    W("bizet-sinfonie-1-c-dur", "georges-bizet", "Sinfonie Nr. 1 C-Dur", [], 1855, 1855, "symphony"),
    W("mozart-ouvertuere-cosi-fan-tutte", "wolfgang-amadeus-mozart",
      "Ouvertüre zu »Così fan tutte«", [cat("KV", "588")], 1790, 1790, "overture"),
    W("mozart-klavierkonzert-c-dur-kv503", "wolfgang-amadeus-mozart",
      "Klavierkonzert C-Dur", [cat("KV", "503")], 1786, 1786, "concerto"),
    W("mozart-sinfonie-38-prager", "wolfgang-amadeus-mozart",
      "Sinfonie Nr. 38 D-Dur »Prager«", [cat("KV", "504")], 1786, 1786, "symphony"),
    W("haydn-londoner-trio-3-spiritoso", "joseph-haydn",
      "Spiritoso aus Londoner Trio Nr. 3", [], None, None, "chamber_music"),
    W("mozart-sechs-laendlerische-taenze", "wolfgang-amadeus-mozart",
      "Sechs Ländlerische Tänze", [], None, None, "chamber_music"),
    W("salieri-trio-in-g", "antonio-salieri", "Trio in G", [], None, None, "chamber_music"),
    W("strauss-vater-trompeten-walzer", "johann-strauss-vater",
      "Trompeten-Walzer", [], None, None, "chamber_music"),
    W("dittersdorf-divertimento-in-e", "carl-ditters-von-dittersdorf",
      "Divertimento in E", [], None, None, "chamber_music"),
    W("brahms-hymne-grosser-joachim", "johannes-brahms",
      "Hymne zur Verherrlichung des großen Joachim", [], None, None, "chamber_music"),
    W("kreisler-schoen-rosmarin", "fritz-kreisler", "»Schön Rosmarin«", [], None, None, "other"),
    W("massenet-meditation-thais", "jules-massenet",
      "»Méditation« aus »Thaïs«", [], None, None, "other"),
    W("haydn-divertimento-d-allegro", "joseph-haydn",
      "Allegro aus Divertimento in D", [], None, None, "chamber_music"),
    W("beethoven-sechs-gesellschafts-menuette", "ludwig-van-beethoven",
      "Sechs Gesellschafts-Menuette", [], None, None, "chamber_music"),
    W("debussy-childrens-corner-orch-caplet", "claude-debussy",
      "»Children's Corner« (orch. Caplet)", [], 1908, 1908, "other"),
    W("hahn-suite-le-bal-de-beatrice-deste", "reynaldo-hahn",
      "Suite »Le Bal de Béatrice d'Este«", [], 1905, 1905, "other"),
    W("holmes-ludus-pro-patria-interlude", "augusta-holmes",
      "»Ludus pro Patria«: Interlude", [], 1888, 1888, "other"),
    W("franck-le-chasseur-maudit", "cesar-franck", "»Le Chasseur maudit«", [], 1882, 1882, "other"),
    W("respighi-ancient-airs-and-dances-3", "ottorino-respighi",
      "Ancient Airs and Dances, Suite No. 3", [], None, None, "other"),
    W("humperdinck-quintett-g-dur", "engelbert-humperdinck",
      "Quintett G-Dur", [], None, None, "chamber_music"),
    W("sibelius-en-saga", "jean-sibelius", "»En Saga«", [cat("Opus", "9")], 1892, 1892, "other"),
    W("sibelius-valse-triste", "jean-sibelius", "»Valse triste«", [cat("Opus", "44")], 1903, 1903, "other"),
    W("halvorsen-norwegische-rhapsodie-1", "johan-halvorsen",
      "»Norwegische Rhapsodie« Nr. 1 A-Dur", [], 1919, 1920, "other"),
    W("grieg-sinfonische-taenze", "edvard-grieg",
      "Sinfonische Tänze", [cat("Opus", "64")], 1898, 1898, "other"),
    W("bernstein-candide-auswahl", "leonard-bernstein",
      "»Candide« (Auswahl)", [], 1956, 1974, "other"),
    W("clyne-restless-oceans", "anna-clyne", "»Restless Oceans«", [], 2018, 2018, "other"),
    W("gal-quintett-op107", "hans-gal",
      "Quintett für Klarinette und Streichquartett", [cat("Opus", "107")], None, None, "chamber_music"),
    W("busch-serenade-a-dur-op53b", "adolf-busch",
      "Serenade A-Dur für Klarinette, Violine und Viola", [cat("Opus", "53b")], None, None, "chamber_music"),
    W("busoni-suite-g-moll-klarinette", "ferruccio-busoni",
      "Suite g-Moll für Klarinette und Streichquartett", [], None, None, "chamber_music"),
    W("danzi-fagottquartett-3-op40", "franz-ignaz-danzi",
      "Fagottquartett Nr. 3", [cat("Opus", "40")], None, None, "chamber_music"),
    W("mozart-divertimento-es-dur-kv573", "wolfgang-amadeus-mozart",
      "Divertimento Es-Dur", [cat("KV", "573")], None, None, "chamber_music"),
    W("britten-welcome-ode", "benjamin-britten",
      "»Welcome Ode« für Chor und Orchester", [cat("Opus", "95")], 1976, 1976, "other"),
    W("beethoven-chorfantasie", "ludwig-van-beethoven",
      "Fantasie c-Moll für Klavier, Chor und Orchester (»Chorfantasie«)", [cat("Opus", "80")], None, None, "other"),
    W("puccini-messa-di-gloria", "giacomo-puccini",
      "Messa (»Messa di Gloria«)", [cat("SC", "6")], 1878, 1880, "oratorio"),
    W("schubert-streichquartett-14-der-tod-und-das-maedchen", "franz-schubert",
      "Streichquartett Nr. 14 d-Moll »Der Tod und das Mädchen«", [cat("D", "810")], None, None, "chamber_music"),
    W("spohr-die-letzten-dinge", "louis-spohr",
      "»Die letzten Dinge«", [], 1825, 1826, "oratorio"),
]

# Existing works reused as-is (composerId, workId) — not re-created:
REUSE_WORKS = [
    "tschaikowski-fantasie-ouvertuere-romeo-und-julia", "strauss-rosenkavalier-suite",
    "haydn-sinfonie-103", "beethoven-sinfonie-nr-8-f-dur", "mendelssohn-sinfonie-5-reformation",
    "bach-orchestersuite-nr-3-d-dur", "ravel-pavane-pour-une-infante-defunte",
    "ravel-le-tombeau-de-couperin", "boulanger-dun-matin-de-printemps",
    "brahms-variationen-ueber-ein-thema-von-haydn", "schubert-klavierquintett-a-dur-forellenquintett",
    "schumann-sinfonie-1-fruehling", "brahms-klavierkonzert-nr-2-b-dur",
    "brahms-klarinettenquintett", "schubert-streichtrio-d581", "prokofjew-peter-und-der-wolf",
    "higdon-blue-cathedral",
]

# ---------- productions ----------
# Each production is one printed programme (title + cast + program) that may recur at
# several NRW venues/dates. Non-NRW legs are already excluded from `performances`, per
# the module docstring; productions with zero remaining NRW legs are not listed at all.
#
# performances: list of (date, startTime-or-None, venueId, cityId)
# conductors / soloists: list of (personId, displayName[, role])
# program: list of work ids (NEW_WORKS ids or REUSE_WORKS ids)
# extra: free-text sentences appended to the generated description

PRODUCTIONS = [
    dict(
        id="sommerkonzert-landesregierung-2026", title="Sommerkonzert der Landesregierung NRW",
        performances=[("2026-08-29", "20:15", "schlossplatz-muenster", "muenster")],
        conductors=[("ingmar-beck", "Ingmar Beck")], soloists=[], program=[],
        extra=["Live-TV-Übertragung; Antrittskonzert von Chefdirigent Ingmar Beck.",
               "Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="sinfoniekonzert-dirigierkurs-detmold-2026",
        title="Sinfoniekonzert zum Abschluss des Dirigierkurses der Musikhochschule Detmold",
        performances=[("2026-09-06", "17:00", "schuetzenhalle-grevenbrueck", "lennestadt")],
        conductors=[("johannes-klumpp", "Johannes Klumpp")], soloists=[],
        program=["wagner-vorspiel-tristan-und-isolde", "wagner-meistersinger-vorspiel-3-akt",
                 "tschaikowski-fantasie-ouvertuere-romeo-und-julia"],
        extra=["Abschlusskonzert des Dirigierkurses der Musikhochschule Detmold; Solist:innen laut "
               "Spielzeitbuch noch nicht benannt (N.N.).",
               "Zusätzlich zu den gelisteten Orchesterwerken erklingen Opernszenen aus Nicolais "
               "»Die lustigen Weiber von Windsor«, Tschaikowskis »Eugen Onegin« und »Iolanta«, "
               "Moniuszkos »Halka« sowie Wagners »Meistersinger« und Richard Strauss’ »Rosenkavalier« "
               "mit noch nicht benannten Solist:innen."],
    ),
    dict(
        id="last-night-of-the-proms-sep2026", title="Last Night of the Proms",
        performances=[
            ("2026-09-10", "20:00", "kultureller-marktplatz-hilchenbach", "hilchenbach"),
            ("2026-09-12", "18:00", "kirche-am-roemer-burbach", "burbach"),
            ("2026-09-13", "18:00", "theater-lippstadt", "lippstadt"),
        ],
        conductors=[("russell-harris", "Russell Harris")],
        soloists=[("mirjam-theil", "Mirjam Theil", "Sopran"),
                  ("sandro-hirsch", "Sandro Hirsch", "Trompete, Brüder-Busch-Preisträger 2025")],
        program=[],
        extra=["Konzert im Stil der Londoner »Last Night of the Proms« mit britischen "
               "Konzertklassikern; Einzeltitel im Spielzeitbuch nicht ausgewiesen.",
               "In Hilchenbach-Dahlbruch Verleihung des Brüder-Busch-Preis 2025 an Sandro Hirsch; "
               "die Aufführung in Burbach firmiert zusätzlich als »Römerkonzert«."],
    ),
    dict(
        id="re-sonanz-2026", title="Re:Sonanz", subtitle="Sinfoniekonzert S-Klassik",
        performances=[("2026-09-18", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2026-09-19", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("thomas-reif", "Thomas Reif", "Violine")],
        program=["mozart-ouvertuere-don-giovanni", "mozart-violinkonzert-d-dur-kv218",
                  "higdon-blue-cathedral", "strauss-rosenkavalier-suite"],
        extra=["Antrittskonzert von Chefdirigent Ingmar Beck.",
               "Einführungsvortrag am 15. September 2026 mit Veronika Jefremowa."],
    ),
    dict(
        id="sinfoniekonzert-arnsberg-neheim-2026", title="Sinfoniekonzert",
        performances=[("2026-09-25", "19:00", "st-johannes-kirche-arnsberg-neheim", "arnsberg")],
        conductors=[("josephine-korda", "Josephine Korda")], soloists=[],
        program=["kraus-ouvertuere-olympie", "haydn-sinfonie-103", "mendelssohn-sinfonie-3-schottische"],
        extra=[],
    ),
    dict(
        id="baby-konzerte-2026-10-02", title="Baby-Konzerte",
        performances=[("2026-10-02", "09:15", "haus-der-musik-siegen", "siegen"),
                      ("2026-10-02", "10:45", "haus-der-musik-siegen", "siegen")],
        conductors=[("russell-harris", "Russell Harris")], soloists=[], program=[],
        extra=["Konzertformat für die Allerkleinsten und ihre Familien."],
    ),
    dict(
        id="last-night-of-the-proms-okt2026", title="Last Night of the Proms",
        performances=[("2026-10-03", "17:00", "aula-gymnasium-bad-laasphe", "bad-laasphe")],
        conductors=[("russell-harris", "Russell Harris")],
        soloists=[("richard-morrison", "Richard Morrison", "Bariton")], program=[],
        extra=["Konzert im Stil der Londoner »Last Night of the Proms«; Einzeltitel im "
               "Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="der-tod-und-das-maedchen-2026", title="Der Tod und das Mädchen",
        subtitle="Kammermusik und Lesung im Stift Keppel",
        performances=[("2026-10-04", "17:00", "stift-keppel-konventssaal-hilchenbach", "hilchenbach")],
        conductors=[],
        soloists=[("sueda-seifert", "Sueda Seifert", "Violine"),
                  ("johanna-lorbach", "Johanna Lorbach", "Violine"),
                  ("daniel-rivas-lopez", "Daniel Rivas Lopez", "Viola"),
                  ("german-prentki", "Germán Prentki", "Cello")],
        program=["schubert-streichquartett-14-der-tod-und-das-maedchen"],
        extra=["Mit der Erzählung »Der Tod und das Mädchen« von Mika Seifert, gelesen von N.N."],
    ),
    dict(
        id="philvibes-1-2026", title="PhilVibes #1",
        performances=[("2026-10-09", "19:30", "haus-der-musik-siegen", "siegen")],
        conductors=[], soloists=[], program=[],
        extra=["Experimentelle Konzertreihe der Philharmonie Südwestfalen im Haus der Musik; "
               "Besetzung und Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="berta-brixen-beethoven-tanzende-maus-2026",
        title="Berta Brixen: Beethoven und die tanzende Maus", subtitle="Teddybär-Konzert",
        performances=[("2026-10-11", "15:00", "otto-flick-halle-kreuztal", "kreuztal")],
        conductors=[("alexandra-lubchansky", "Alexandra Lubchansky")], soloists=[], program=[],
        extra=["Konzept und Moderation: Andrea Hoever.",
               "Beethoven-Programm für Kinder; Einzeltitel im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="re-form-2026", title="Re:Form", subtitle="Sinfoniekonzert",
        performances=[("2026-10-16", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("erik-asgeirsson", "Erik Ásgeirsson", "Cello")],
        program=["puts-virelai", "bruch-kol-nidrei", "stravinsky-monumentum-pro-gesualdo",
                  "brahms-variationen-ueber-ein-thema-von-haydn", "mendelssohn-sinfonie-5-reformation"],
        extra=["Einführungsvortrag am 13. Oktober 2026 mit Bettina Landgraf."],
    ),
    dict(
        id="re-discover-2026", title="Re:Discover", subtitle="Sinfoniekonzert",
        performances=[("2026-11-06", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2026-11-08", "18:00", "kulturhaus-luedenscheid", "luedenscheid")],
        conductors=[("sigiswald-kuijken", "Sigiswald Kuijken")], soloists=[],
        program=["mayer-ouvertuere-nr-2-d-dur", "beethoven-sinfonie-nr-8-f-dur", "mayer-sinfonie-nr-7-f-moll"],
        extra=["Einführungsvortrag am 4. November 2026 mit Katrin Mainz."],
    ),
    dict(
        id="crossover-konzertgala-volksbank-2026", title="Crossover-Konzertgala der Volksbank",
        performances=[("2026-11-14", "19:00", "stadthalle-schmallenberg", "schmallenberg")],
        conductors=[("juheon-han", "Juheon Han")], soloists=[], program=[],
        extra=["Chor: Fleckenberger Sound Projekt.",
               "Crossover-Programm; Einzeltitel im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="baby-konzerte-2026-12-03", title="Baby-Konzerte",
        performances=[("2026-12-03", "09:15", "haus-der-musik-siegen", "siegen"),
                      ("2026-12-03", "10:45", "haus-der-musik-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")], soloists=[], program=[], extra=[],
    ),
    dict(
        id="festliche-barockmusik-adventszeit-2026", title="Festliche Barockmusik zur Adventszeit",
        performances=[
            ("2026-12-03", "19:30", "kath-kirche-st-alexander-schmallenberg", "schmallenberg"),
            ("2026-12-04", "19:30", "kath-kirche-st-martin-olsberg-bigge", "olsberg"),
            ("2026-12-06", "16:00", "pfarrkirche-st-johannes-baptist-attendorn", "attendorn"),
        ],
        conductors=[("ingmar-beck", "Ingmar Beck")], soloists=[],
        program=["bach-brandenburgisches-konzert-3", "bach-schafe-koennen-sicher-weiden",
                  "telemann-sinfonia-spirituosa", "corelli-concerto-8-notte-di-natale",
                  "bach-wir-eilen-bwv78", "bach-orchestersuite-nr-3-d-dur"],
        extra=[],
    ),
    dict(
        id="christmas-classics-at-the-movies-2026", title="Christmas Classics at the Movies",
        performances=[("2026-12-12", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2026-12-13", "18:30", "apollo-theater-siegen", "siegen"),
                      ("2026-12-17", "20:00", "parktheater-iserlohn", "iserlohn")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("marie-sophie-pollak", "Marie-Sophie Pollak", "Sopran, Artist in Residence")],
        program=[],
        extra=["Filmmusik-Gala; Einzeltitel im Spielzeitbuch nicht ausgewiesen.",
               "Einführungsvortrag am 8. Dezember 2026 mit Bruce Whitson."],
    ),
    dict(
        id="drei-haselnuesse-fuer-aschenbroedel-2026",
        title="Drei Haselnüsse für Aschenbrödel", subtitle="Live-Begleitung zum Filmklassiker",
        performances=[
            ("2026-12-20", "15:00", "beethovenhalle-bonn", "bonn"),
            ("2026-12-20", "18:30", "beethovenhalle-bonn", "bonn"),
            ("2026-12-22", "19:30", "stadthalle-bielefeld", "bielefeld"),
            ("2026-12-23", "16:00", "eurogress-aachen", "aachen"),
            ("2026-12-23", "19:30", "eurogress-aachen", "aachen"),
            ("2026-12-27", "15:00", "koelner-philharmonie", "koeln"),
            ("2026-12-27", "19:00", "koelner-philharmonie", "koeln"),
            ("2026-12-28", "16:00", "metronom-theater-oberhausen", "oberhausen"),
            ("2026-12-28", "19:30", "metronom-theater-oberhausen", "oberhausen"),
        ],
        conductors=[("markus-huber", "Markus Huber")], soloists=[], program=[],
        extra=["Live-Orchesterbegleitung zum tschechischen Filmklassiker »Tři oříšky pro Popelku« "
               "(»Drei Haselnüsse für Aschenbrödel«, 1973)."],
    ),
    dict(
        id="philsw-barock-2026", title="PhilSW Barock", subtitle="Kammerkonzert",
        performances=[("2026-12-31", "19:30", "ev-kirche-hilchenbach", "hilchenbach")],
        conductors=[], soloists=[], program=[],
        extra=["Silvester-Kammerkonzert; Besetzung und Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="neujahrskonzerte-2027", title="Neujahrskonzerte",
        performances=[
            ("2027-01-01", "17:00", "apollo-theater-siegen", "siegen"),
            ("2027-01-03", "17:00", "otto-flick-halle-kreuztal", "kreuztal"),
            ("2027-01-04", "19:30", "buergerhaus-bad-berleburg", "bad-berleburg"),
            ("2027-01-06", "19:00", "kulturhaus-luedenscheid", "luedenscheid"),
            ("2027-01-07", "20:00", "paedagogisches-zentrum-lennestadt", "lennestadt"),
            ("2027-01-08", "19:30", "festhalle-wilnsdorf", "wilnsdorf"),
            ("2027-01-09", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-01-10", "15:00", "apollo-theater-siegen", "siegen"),
            ("2027-01-11", "20:00", "aula-gymnasium-bad-laasphe", "bad-laasphe"),
            ("2027-01-12", "19:30", "paedagogisches-zentrum-gesamtschule-kierspe", "kierspe"),
            ("2027-01-13", "19:00", "erloeserkirche-neunkirchen-siegerland", "neunkirchen-siegerland"),
        ],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("anna-morgoulets", "Anna Morgoulets", "Violine")], program=[],
        extra=["Programm: Werke von E. Kálmán, J. Brahms, V. Monti, P. de Sarasate u. a. – "
               "keine Einzeltitel im Spielzeitbuch ausgewiesen."],
    ),
    dict(
        id="sinfoniekonzert-luedenscheid-2027", title="Sinfoniekonzert",
        performances=[("2027-01-17", "18:00", "kulturhaus-luedenscheid", "luedenscheid")],
        conductors=[("daniel-huppert", "Daniel Huppert")], soloists=[],
        program=["ravel-pavane-pour-une-infante-defunte", "mozart-sinfonie-29-a-dur", "bizet-sinfonie-1-c-dur"],
        extra=[],
    ),
    dict(
        id="neujahrskonzert-warstein-2027", title="Neujahrskonzert",
        performances=[("2027-01-24", "11:00", "neue-aula-warstein", "warstein")],
        conductors=[("maria-benyumova", "Maria Benyumova")],
        soloists=[("christoph-soldan", "Christoph Soldan", "Klavier")], program=[],
        extra=["Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="kammerkonzert-oberes-schloss-2027-01", title="Kammerkonzert im Oberen Schloss",
        performances=[("2027-01-24", "17:30", "museum-oberes-schloss-siegen", "siegen")],
        conductors=[],
        soloists=[("marie-sophie-pollak", "Marie-Sophie Pollak", "Sopran, Artist in Residence 2026/27"),
                  ("yoshie-saito", "Yoshie Saito", "Violine"),
                  ("ksenia-ivakina", "Ksenia Ivakina", "Violine"),
                  ("daniel-ibanez-garcia", "Daniel Ibáñez-García", "Viola"),
                  ("werner-stephan", "Werner Stephan", "Cello")],
        program=[],
        extra=["Mit dem Quarteto Neux; Programm laut Spielzeitbuch noch offen (N.N.)."],
    ),
    dict(
        id="re-vienna-2027", title="Re:Vienna", subtitle="Gala der Wiener Klassik",
        performances=[("2027-01-28", "19:30", "kulturzentrum-herne", "herne"),
                      ("2027-01-29", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2027-01-30", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("avery-gagliano", "Avery Gagliano", "Klavier")],
        program=["mozart-ouvertuere-cosi-fan-tutte", "mozart-klavierkonzert-c-dur-kv503", "mozart-sinfonie-38-prager"],
        extra=["Einführungsvortrag am 26. Januar 2027 mit Hans André Stamm."],
    ),
    dict(
        id="gala-der-filmmusik-2027", title="Gala der Filmmusik",
        performances=[
            ("2027-02-04", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-05", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-06", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-08", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-09", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-12", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-13", "19:30", "apollo-theater-siegen", "siegen"),
            ("2027-02-19", "19:30", "sauerlandhalle-lennestadt", "lennestadt"),
        ],
        conductors=[("markus-huber", "Markus Huber")], soloists=[], program=[],
        extra=["Filmmusik-Gala; Einzeltitel im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="aus-dem-wienerwald-2027", title="Aus dem Wienerwald",
        subtitle="Kammerkonzert im Oberen Schloss",
        performances=[("2027-02-14", "17:30", "museum-oberes-schloss-siegen", "siegen")],
        conductors=[],
        soloists=[("sangmin-park", "Sangmin Park", "Violine"),
                  ("liliane-hazin-dorus", "Liliane Hazin-Dorus", "Violine"),
                  ("eric-steffens", "Eric Steffens", "Kontrabass")],
        program=["haydn-londoner-trio-3-spiritoso", "mozart-sechs-laendlerische-taenze",
                  "salieri-trio-in-g", "strauss-vater-trompeten-walzer", "dittersdorf-divertimento-in-e",
                  "brahms-hymne-grosser-joachim", "kreisler-schoen-rosmarin", "massenet-meditation-thais",
                  "haydn-divertimento-d-allegro", "beethoven-sechs-gesellschafts-menuette"],
        extra=["Trio SaLiEri."],
    ),
    dict(
        id="peter-und-der-wolf-2027", title="Peter und der Wolf", subtitle="Teddybär-Konzert",
        performances=[("2027-02-21", "15:00", "otto-flick-halle-kreuztal", "kreuztal")],
        conductors=[], soloists=[], program=["prokofjew-peter-und-der-wolf"],
        extra=["Moderation: N.N."],
    ),
    dict(
        id="re-impression-2027", title="Re:Impression", subtitle="Sinfoniekonzert",
        performances=[("2027-02-26", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("claire-gibault", "Claire Gibault")], soloists=[],
        program=["ravel-le-tombeau-de-couperin", "debussy-childrens-corner-orch-caplet",
                  "boulanger-dun-matin-de-printemps", "hahn-suite-le-bal-de-beatrice-deste",
                  "holmes-ludus-pro-patria-interlude", "franck-le-chasseur-maudit"],
        extra=["Einführungsvortrag am 22. Februar 2027 mit Bettina Landgraf."],
    ),
    dict(
        id="musikpaedagogisches-projekt-oberes-schloss-2027-03",
        title="Kammerkonzert im Oberen Schloss",
        performances=[("2027-03-07", "17:30", "museum-oberes-schloss-siegen", "siegen")],
        conductors=[],
        soloists=[("anar-ibrahimov", "Anar Ibrahimov", "Violine"),
                  ("liliane-hazin-dorus", "Liliane Hazin-Dorus", "Violine"),
                  ("daniel-ibanez-garcia", "Daniel Ibáñez-García", "Viola"),
                  ("erik-asgeirsson", "Erik Ásgeirsson", "Cello"),
                  ("eric-steffens", "Eric Steffens", "Kontrabass"),
                  ("anastasia-avdejeva", "Anastasia Avdejeva", "Klavier")],
        program=["respighi-ancient-airs-and-dances-3", "humperdinck-quintett-g-dur",
                  "schubert-klavierquintett-a-dur-forellenquintett"],
        extra=["Sieg Ensemble."],
    ),
    dict(
        id="chorkonzert-bad-lippspringe-2027", title="Chorkonzert",
        performances=[("2027-03-14", "17:00", "ev-kirche-bad-lippspringe", "bad-lippspringe")],
        conductors=[("kolja-berning", "Kolja Berning")],
        soloists=[("anna-maria-kossbau", "Anna-Maria Koßbau", "Alt"),
                  ("andreas-elias-post", "Andreas Elias Post", "Bass")],
        program=["mendelssohn-sinfonie-5-reformation", "spohr-die-letzten-dinge"],
        extra=["Sopran und Tenor laut Spielzeitbuch noch nicht benannt (N.N.).",
               "Chor: Ev. Kantorei Bad Lippspringe."],
    ),
    dict(
        id="baby-konzerte-2027-03-17", title="Baby-Konzerte",
        performances=[("2027-03-17", "09:15", "haus-der-musik-siegen", "siegen"),
                      ("2027-03-17", "10:45", "haus-der-musik-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")], soloists=[], program=[], extra=[],
    ),
    dict(
        id="re-barock-2027", title="Re:Barock", subtitle="Sinfoniekonzert",
        performances=[("2027-03-19", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("marie-sophie-pollak", "Marie-Sophie Pollak", "Sopran, Artist in Residence")],
        program=[],
        extra=["Programm: Werke von A. Vivaldi, J. Haydn, G. B. Sammartini u. a. – keine Einzeltitel "
               "im Spielzeitbuch ausgewiesen.",
               "Einführungsvortrag am 16. März 2027 mit Veronika Jefremowa."],
    ),
    dict(
        id="kammerkonzert-oberes-schloss-2027-04", title="Kammerkonzert im Oberen Schloss",
        performances=[("2027-04-04", "17:30", "museum-oberes-schloss-siegen", "siegen")],
        conductors=[],
        soloists=[("julia-brodbeck", "Julia Brodbeck", "Klarinette"),
                  ("yoshie-saito", "Yoshie Saito", "Violine"),
                  ("ksenia-ivakina", "Ksenia Ivakina", "Violine"),
                  ("elena-santana-de-la-rosa", "Elena Santana de la Rosa", "Viola"),
                  ("renate-aperloo", "Renate Aperloo", "Cello")],
        program=["gal-quintett-op107", "busch-serenade-a-dur-op53b", "busoni-suite-g-moll-klarinette",
                  "brahms-klarinettenquintett"],
        extra=[],
    ),
    dict(
        id="si-wi-von-oben-2027", title="SI-WI von oben. Philharmonisch.",
        subtitle="Live-Musik von Alexander Reuber zum Film von Alexander Fischbach",
        performances=[("2027-04-10", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2027-04-11", "11:00", "apollo-theater-siegen", "siegen")],
        conductors=[("leonard-evers", "Leonard Evers")], soloists=[], program=[],
        extra=["Live-Musik von Alexander Reuber zu einem Luftbildfilm von Alexander Fischbach über "
               "Siegen-Wittgenstein; Einzeltitel im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="re-landscape-2027", title="Re:Landscape", subtitle="Sinfoniekonzert",
        performances=[("2027-04-16", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2027-04-18", "18:00", "kulturhaus-luedenscheid", "luedenscheid")],
        conductors=[("simon-gaudenz", "Simon Gaudenz")], soloists=[],
        program=["sibelius-en-saga", "sibelius-valse-triste", "halvorsen-norwegische-rhapsodie-1",
                  "grieg-sinfonische-taenze"],
        extra=["Einführungsvortrag am 13. April 2027 mit Katrin Mainz."],
    ),
    dict(
        id="chorkonzert-hamm-lippstadt-2027", title="Chorkonzert",
        performances=[("2027-04-25", "18:00", "kurhaus-hamm", "hamm"),
                      ("2027-05-02", "18:00", "theater-lippstadt", "lippstadt")],
        conductors=[("lothar-r-mayer", "Lothar R. Mayer"), ("burkhard-schmitt", "Burkhard Schmitt")],
        soloists=[], program=["bernstein-candide-auswahl"],
        extra=["Dirigent: Lothar R. Mayer (25. April, Hamm), Burkhard Schmitt (2. Mai, Lippstadt).",
               "Solist:innen laut Spielzeitbuch noch nicht benannt (N.N.).",
               "Chöre: Städtischer Musikverein Hamm, Konzertchor Musikverein Lippstadt."],
    ),
    dict(
        id="last-night-of-the-proms-mai2027", title="Last Night of the Proms",
        performances=[("2027-05-05", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[("russell-harris", "Russell Harris")],
        soloists=[("cordelia-katharina-weil", "Cordelia Katharina Weil", "Mezzo-Sopran")], program=[],
        extra=["Konzert im Stil der Londoner »Last Night of the Proms«; Einzeltitel im "
               "Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="philvibes-2-2027", title="PhilVibes #2",
        performances=[("2027-05-08", "19:30", "haus-der-musik-siegen", "siegen")],
        conductors=[], soloists=[], program=[],
        extra=["Experimentelle Konzertreihe der Philharmonie Südwestfalen im Haus der Musik; "
               "Besetzung und Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="re-currents-2027", title="Re:Currents", subtitle="Sinfoniekonzert",
        performances=[("2027-05-22", "19:30", "apollo-theater-siegen", "siegen"),
                      ("2027-05-23", "18:00", "konzert-theater-coesfeld", "coesfeld")],
        conductors=[("ingmar-beck", "Ingmar Beck")],
        soloists=[("fabian-mueller", "Fabian Müller", "Klavier")],
        program=["clyne-restless-oceans", "schumann-sinfonie-1-fruehling", "brahms-klavierkonzert-nr-2-b-dur"],
        extra=["Einführungsvortrag am 18. Mai 2027 mit Hans André Stamm."],
    ),
    dict(
        id="wunderschoen-2027", title="Wunderschön!",
        subtitle="Live-Musik zum Film »Süditalien: Amalfiküste, Capri, Neapel« mit Musik von Andy Miles",
        performances=[("2027-05-29", "19:30", "apollo-theater-siegen", "siegen")],
        conductors=[], soloists=[], program=[],
        extra=["Moderation: Tamina Kallert.",
               "Live-Musik von Andy Miles zum Reisefilm; Einzeltitel im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="kammermusik-turmzimmer-ginsburg-2027", title="Kammermusik im Turmzimmer der Ginsburg",
        performances=[("2027-06-06", "17:00", "ginsburg-turmzimmer-hilchenbach", "hilchenbach")],
        conductors=[],
        soloists=[("susumu-takahashi", "Susumu Takahashi", "Fagott"),
                  ("yoshie-saito", "Yoshie Saito", "Violine"),
                  ("elena-santana-de-la-rosa", "Elena Santana de la Rosa", "Viola"),
                  ("paulina-gude", "Paulina Gude", "Cello")],
        program=["schubert-streichtrio-d581", "danzi-fagottquartett-3-op40", "mozart-divertimento-es-dur-kv573"],
        extra=[],
    ),
    dict(
        id="baby-konzerte-2027-06-17", title="Baby-Konzerte",
        performances=[("2027-06-17", "09:15", "haus-der-musik-siegen", "siegen"),
                      ("2027-06-17", "10:45", "haus-der-musik-siegen", "siegen")],
        conductors=[("bernhard-steiner", "Bernhard Steiner")], soloists=[], program=[], extra=[],
    ),
    dict(
        id="sommerkonzerte-2027", title="Sommerkonzerte",
        performances=[("2027-06-18", "19:30", "aula-gymnasium-wilnsdorf", "wilnsdorf"),
                      ("2027-06-19", "19:30", "marktplatz-hilchenbach", "hilchenbach"),
                      ("2027-06-20", "17:00", "buergerhaus-bad-berleburg", "bad-berleburg")],
        conductors=[("bernhard-steiner", "Bernhard Steiner")], soloists=[], program=[],
        extra=["Open-Air-Konzert in Hilchenbach (Marktplatz).",
               "Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
    dict(
        id="chorkonzert-koeln-2027", title="Chorkonzert",
        performances=[("2027-06-27", "11:00", "koelner-philharmonie", "koeln")],
        conductors=[("joachim-geibel", "Joachim Geibel")],
        soloists=[("lukas-schmidt", "Lukas Schmidt", "Tenor"),
                  ("thomas-laske", "Thomas Laske", "Bass"),
                  ("christoph-schnackertz", "Christoph Schnackertz", "Klavier")],
        program=["britten-welcome-ode", "beethoven-chorfantasie", "puccini-messa-di-gloria"],
        extra=["Chor: Oratorienchor Köln."],
    ),
    dict(
        id="sommerfest-haus-der-musik-2027", title="Sommerfest im Haus der Musik",
        performances=[("2027-07-03", None, "haus-der-musik-siegen", "siegen")],
        conductors=[], soloists=[], program=[],
        extra=["Uhrzeit laut Spielzeitbuch noch nicht bekannt (N.N.)."],
    ),
    dict(
        id="kreuztal-open-air-2027", title="Kreuztal Open-Air",
        performances=[("2027-07-10", "20:00", "dreslers-park-kreuztal", "kreuztal")],
        conductors=[("ingmar-beck", "Ingmar Beck")], soloists=[], program=[],
        extra=["Open-Air-Konzert; Programm im Spielzeitbuch nicht ausgewiesen."],
    ),
]

# ---------- load, merge, write ----------
people = load("people")
composers = load("composers")
works = load("works")
venues = load("venues")
cities = load("cities")
events = load("events")

people_ids = {p["id"] for p in people["people"]}
composer_ids = {c["id"] for c in composers["composers"]}
work_ids = {w["id"] for w in works["works"]}
venue_ids = {v["id"] for v in venues["venues"]}
city_ids = {c["id"] for c in cities["cities"]}

# idempotency: drop any previously ingested PhilSW events (matched by source host)
removed = 0
kept_events = []
for e in events["events"]:
    src = (e.get("source") or {}).get("url") or ""
    if SRC_HOST in src:
        removed += 1
    else:
        kept_events.append(e)
events["events"] = kept_events
existing_ids = {e["id"] for e in events["events"]}

# master data: cities
added_cities = 0
for c in NEW_CITIES:
    if c["id"] not in city_ids:
        cities["cities"].append(c)
        city_ids.add(c["id"])
        added_cities += 1

# master data: venues
added_venues = 0
for vid, name, city_list, vtype in NEW_VENUES:
    if vid not in venue_ids:
        venues["venues"].append({
            "id": vid, "name": name, "cityIds": city_list, "region": None,
            "address": None, "coordinates": None, "website": None,
            "type": vtype, "institutionId": None,
        })
        venue_ids.add(vid)
        added_venues += 1

# master data: composers
added_composers = 0
for cid, name, birth, death in NEW_COMPOSERS:
    if cid not in composer_ids:
        composers["composers"].append({"id": cid, "name": name, "life": {"from": birth, "to": death}})
        composer_ids.add(cid)
        added_composers += 1

# master data: works
added_works = 0
for w in NEW_WORKS:
    if w["id"] not in work_ids:
        works["works"].append(w)
        work_ids.add(w["id"])
        added_works += 1
    if w["composerId"] not in composer_ids:
        print("!! MISSING COMPOSER RECORD:", w["composerId"], file=sys.stderr)

for wid in REUSE_WORKS:
    if wid not in work_ids:
        print("!! REUSE_WORKS references unknown work id:", wid, file=sys.stderr)

# master data: people (conductors/soloists collected inline from productions)
new_people = 0
for prod in PRODUCTIONS:
    for pid, name, *_ in [(*c, None) for c in prod["conductors"]] + list(prod["soloists"]):
        if pid not in people_ids:
            people["people"].append({"id": pid, "name": name})
            people_ids.add(pid)
            new_people += 1

# events
new_events = []
prog_events = 0
for prod in PRODUCTIONS:
    conductor_ids = [pid for pid, _ in prod["conductors"]]
    soloist_ids = [pid for pid, _name, *_role in prod["soloists"]]
    program = []
    for wid in prod["program"]:
        if wid not in work_ids:
            print("!! UNKNOWN WORK IN PROGRAM:", wid, "(", prod["id"], ")", file=sys.stderr)
            continue
        program.append({"workId": wid, "movement": None, "version": None})
    description = " ".join(prod.get("extra", [])) or None

    for date, start, vid, cid in prod["performances"]:
        if vid not in venue_ids:
            print("!! UNMAPPED VENUE:", vid, "(", prod["id"], ")", file=sys.stderr)
            continue
        if cid not in city_ids:
            print("!! UNMAPPED CITY:", cid, "(", prod["id"], ")", file=sys.stderr)
            continue
        title = prod["title"]
        base = f"event-{date}-{cid}-{fold(title)}"
        eid = base
        if eid in existing_ids and start:
            eid = f"{base}-{start.replace(':', '')}"
        i = 2
        while eid in existing_ids:
            eid = f"{base}-{i}"
            i += 1
        existing_ids.add(eid)
        if program:
            prog_events += 1
        new_events.append({
            "id": eid, "title": title, "eventType": "concert", "date": date,
            "startTime": start, "endTime": None, "status": "scheduled",
            "ensembleIds": [ENSEMBLE_ID], "venueId": vid, "cityId": cid,
            "conductorPersonIds": conductor_ids, "soloistPersonIds": soloist_ids,
            "program": program, "seriesId": None, "description": description,
            "source": {"url": SRC_URL, "calendarUrl": CALENDAR_URL, "name": SRC_NAME, "retrievedAt": TODAY},
            "ticketUrl": None, "lastVerified": TODAY,
        })

new_events.sort(key=lambda e: (e["date"], e["startTime"] or "", e["id"]))
events["events"].extend(new_events)

for obj in (people, composers, works, venues, cities, events):
    obj.setdefault("metadata", {})["lastUpdated"] = TODAY
events["metadata"]["notes"] = events["metadata"].get("notes", "") + (
    " Enthält recherchierte Konzerte der Philharmonie Südwestfalen (Spielzeitbuch 2026/27, Quelle: "
    "philsw.de/wp-content/uploads); nur Aufführungen in Nordrhein-Westfalen wurden übernommen."
)

save("people", people)
save("composers", composers)
save("works", works)
save("venues", venues)
save("cities", cities)
save("events", events)

print(f"Removed prior PhilSW events: {removed}")
print(f"New events: {len(new_events)} (total now {len(events['events'])}); {prog_events} mit Programm")
print(f"New people: {new_people}; people total {len(people['people'])}")
print(f"New composers: {added_composers}; composers total {len(composers['composers'])}")
print(f"New works: {added_works}; works total {len(works['works'])}")
print(f"New venues: {added_venues}; venues total {len(venues['venues'])}")
print(f"New cities: {added_cities}; cities total {len(cities['cities'])}")
