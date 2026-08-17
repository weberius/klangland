#!/usr/bin/env python3
"""Ingest the Bergische Symphoniker 2026/27 schedule into klangland ``data/*.json``.

Source: https://bergischesymphoniker.de/api/concerts (Payload CMS JSON API).
Public concert pages: https://bergischesymphoniker.de/konzerte/<slug>.

Curated (Option B): works/composers are enriched with life dates, composition years,
genre and approximate duration. Program/cast noise from the CMS is filtered out and,
where useful, preserved in the event ``description``.

Idempotent: re-running removes previously ingested Bergische events (matched by the
source host) and merges master data (people, works, composers, venues, cities)
without creating duplicates.

Usage:
    python docs/data-tooling/ingest_bergische.py            # fetch live API
    python docs/data-tooling/ingest_bergische.py --raw f.json   # use saved API dump
    python docs/data-tooling/ingest_bergische.py --date 2026-08-17
"""
import argparse, datetime, json, os, re, sys, unicodedata, urllib.request

API_URL = "https://bergischesymphoniker.de/api/concerts?limit=200&depth=2"
SEASON = "2026/27"
ENSEMBLE_ID = "bergische-symphoniker"
SRC_HOST = "bergischesymphoniker.de"
SRC_NAME = "Bergische Symphoniker"

# Repo paths, resolved relative to this file (docs/data-tooling/ -> repo root).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")

_args = argparse.ArgumentParser(description="Ingest Bergische Symphoniker schedule")
_args.add_argument("--raw", help="path to a saved /api/concerts JSON dump")
_args.add_argument("--date", default=datetime.date.today().isoformat(),
                   help="retrievedAt/lastVerified date (YYYY-MM-DD)")
ARGS = _args.parse_args()
TODAY = ARGS.date

def fetch_concerts():
    """Return the raw list of concert docs from the API or a saved dump."""
    if ARGS.raw:
        with open(ARGS.raw, encoding="utf-8") as f:
            return json.load(f)["docs"]
    req = urllib.request.Request(API_URL, headers={"User-Agent": "klangland-ingest"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["docs"]

def extract_season(docs):
    """Flatten API docs of the target season into the intermediate shape."""
    def stitle(doc):
        s = doc.get("season")
        return s.get("title") if isinstance(s, dict) else None
    out = []
    for doc in docs:
        if stitle(doc) != SEASON:
            continue
        out.append({
            "title": (doc.get("title") or "").strip(),
            "subtitle": (doc.get("subtitle") or "").strip(),
            "slug": doc.get("slug"),
            "categories": [c.get("title") for c in doc.get("categories", [])],
            "performances": [{"dateTime": p.get("dateTime"),
                              "venue": (p.get("venue") or "").strip(),
                              "ticketUrl": p.get("ticketUrl")}
                             for p in doc.get("performances", [])],
            "program": [{"composer": (p.get("composer") or "").strip(),
                         "workTitle": (p.get("workTitle") or "").strip(),
                         "opus": p.get("opus")}
                        for p in doc.get("program", [])],
            "cast": [{"name": (c.get("name") or "").strip(),
                      "role": (c.get("role") or "").strip()}
                     for c in doc.get("cast", [])],
        })
    def firstdate(c):
        ds = sorted(p["dateTime"] for p in c["performances"] if p.get("dateTime"))
        return ds[0] if ds else "zzzz"
    out.sort(key=firstdate)
    return out

# ---------- helpers ----------
_UML = {"ä":"ae","ö":"oe","ü":"ue","Ä":"ae","Ö":"oe","Ü":"ue","ß":"ss",
        "ł":"l","ø":"o","đ":"d","ħ":"h","ı":"i","æ":"ae","œ":"oe",
        "ț":"t","ș":"s","ğ":"g","ç":"c","ñ":"n"}
def fold(s):
    s = s.strip().lower()
    for k,v in _UML.items():
        s = s.replace(k.lower(), v)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s

def load(name):
    with open(f"{DATA}/{name}.json", encoding="utf-8") as f:
        return json.load(f)
def save(name, obj):
    with open(f"{DATA}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

# ---------- curation: composers ----------
# id -> (name, from, to)
_UML = {"ä":"ae","ö":"oe","ü":"ue","Ä":"ae","Ö":"oe","Ü":"ue","ß":"ss",
        "ł":"l","ø":"o","đ":"d","ħ":"h","ı":"i","æ":"ae","œ":"oe",
        "ț":"t","ș":"s","ğ":"g","ç":"c","ñ":"n"}
def fold(s):
    s = s.strip().lower()
    for k,v in _UML.items():
        s = s.replace(k.lower(), v)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s

def load(name):
    with open(f"{DATA}/{name}.json", encoding="utf-8") as f:
        return json.load(f)
def save(name, obj):
    with open(f"{DATA}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

# ---------- curation: composers ----------
# id -> (name, from, to)
NEW_COMPOSERS = {
    "gabriel-faure": ("Gabriel Fauré", 1845, 1924),
    "ethel-mary-smyth": ("Ethel Mary Smyth", 1858, 1944),
    "malek-jandali": ("Malek Jandali", 1972, None),
    "bilal-irshed": ("Bilal Irshed", None, None),
    "alan-menken": ("Alan Menken", 1949, None),
    "nikolai-rimski-korsakow": ("Nikolai Rimski-Korsakow", 1844, 1908),
    "aram-chatschaturjan": ("Aram Chatschaturjan", 1903, 1978),
    "david-magrane": ("David Magrané", None, None),
    "william-walton": ("William Walton", 1902, 1983),
    "johannes-brahms": ("Johannes Brahms", 1833, 1897),
    "wolfgang-amadeus-mozart": ("Wolfgang Amadeus Mozart", 1756, 1791),
    "jean-sibelius": ("Jean Sibelius", 1865, 1957),
    "samy-moussa": ("Samy Moussa", 1984, None),
    "felix-mendelssohn-bartholdy": ("Felix Mendelssohn Bartholdy", 1809, 1847),
    "robert-schumann": ("Robert Schumann", 1810, 1856),
    "alexander-zemlinsky": ("Alexander Zemlinsky", 1871, 1942),
    "johann-sebastian-bach": ("Johann Sebastian Bach", 1685, 1750),
    "arvo-paert": ("Arvo Pärt", 1935, None),
    "anna-clyne": ("Anna Clyne", 1980, None),
    "john-adams": ("John Adams", 1947, None),
    "nino-rota": ("Nino Rota", 1911, 1979),
    "michael-haydn": ("Michael Haydn", 1737, 1806),
    "cesar-franck": ("César Franck", 1822, 1890),
    "paul-hindemith": ("Paul Hindemith", 1895, 1963),
    "lidia-de-migno": ("Lidia De Migno", None, None),
    "dmitri-schostakowitsch": ("Dmitri Schostakowitsch", 1906, 1975),
    "dmitri-kabalewski": ("Dmitri Kabalewski", 1904, 1987),
    "igor-strawinsky": ("Igor Strawinsky", 1882, 1971),
    "manuel-ponce": ("Manuel Ponce", 1882, 1948),
}
# source composer string -> composer id (existing reused + new)
COMPOSER_ID = {
    "Ludwig van Beethoven": "ludwig-van-beethoven",
    "Franz Schubert": "franz-schubert",
    "Anton Webern": "anton-webern",
    "Sergei Prokofjew": "sergej-prokofjew",
    "Camille Saint-Saëns": "camille-saint-saens",
    "Pijotr Iljitsch Tschaikowski": "peter-iljitsch-tschaikowsky",
    "Sergej Rachmaninoff": "sergej-rachmaninow",
    "Sergei Rachmaninow": "sergej-rachmaninow",
    "Sergei Rachmaninov": "sergej-rachmaninow",
    "Béla Bartók": "bela-bartok",
    "Carl Maria von Weber": "carl-maria-von-weber",
    "Ernest Bloch": "ernest-bloch",
    "Charles Ives": "charles-ives",
    "Caroline Shaw": "caroline-shaw",
    "Francis Poulenc": "francis-poulenc",
    "Richard Strauss": "richard-strauss",
    "Anton Bruckner": "anton-bruckner",
    "Gabriel Fauré": "gabriel-faure",
    "Ethel Mary Smyth": "ethel-mary-smyth",
    "Malek Jandali": "malek-jandali",
    "Bilal Irshed": "bilal-irshed",
    "Alan Menken": "alan-menken",
    "Nikolai Rimski-Korsakow": "nikolai-rimski-korsakow",
    "Aram Chatschaturjan": "aram-chatschaturjan",
    "David Magrané": "david-magrane",
    "William Walton": "william-walton",
    "Johannes Brahms": "johannes-brahms",
    "W. A. Mozart": "wolfgang-amadeus-mozart",
    "Jean Sibelius": "jean-sibelius",
    "Samy Moussa": "samy-moussa",
    "Felix Mendelssohn": "felix-mendelssohn-bartholdy",
    "Robert Schumann": "robert-schumann",
    "Alexander Zemlinsky": "alexander-zemlinsky",
    "Johann Sebastian Bach": "johann-sebastian-bach",
    "Arvo Pärt": "arvo-paert",
    "Anna Clyne": "anna-clyne",
    "John Adams": "john-adams",
    "Nino Rota": "nino-rota",
    "Michael Haydn": "michael-haydn",
    "César Franck": "cesar-franck",
    "Richard Strauss ": "richard-strauss",
    "Paul Hindemith": "paul-hindemith",
    "Lidia De Migno": "lidia-de-migno",
    "Dmitri Schostakowitsch": "dmitri-schostakowitsch",
    "Dmitri Kabalewski": "dmitri-kabalewski",
    "Igor Strawinsky": "igor-strawinsky",
    "Manuel Ponce": "manuel-ponce",
}

def cat(system, number):
    return {"system": system, "number": number}

# ---------- curation: works ----------
# key (source_composer, source_workTitle) -> work record
def W(wid, cid, title, catalogue, yf, yt, genre, dur, version=None, scoring=None, desc=None):
    year = None if yf is None else {"from": yf, "to": yt}
    return {"id": wid, "composerId": cid, "title": title, "catalogue": catalogue,
            "yearComposed": year, "genre": genre,
            "durationMinutes": dur, "version": version, "scoring": scoring, "description": desc}

WORKS = {
 ("Gabriel Fauré","Ouvertüre aus »Masques et Bergamasques« Suite für Orchester"):
    W("faure-masques-et-bergamasques-ouvertuere","gabriel-faure","Ouvertüre aus »Masques et Bergamasques«",[cat("Opus","112")],1919,1919,"overture",7),
 ("Ethel Mary Smyth","Scherzo aus: Serenade D-Dur"):
    W("smyth-serenade-d-dur-scherzo","ethel-mary-smyth","Scherzo aus der Serenade D-Dur",[],1889,1890,"other",6),
 ("Béla Bartók","Rumänische Volkstänze Sz.68 BB 76"):
    W("bartok-rumaenische-volkstaenze","bela-bartok","Rumänische Volkstänze",[cat("Sz","68"),cat("BB","76")],1915,1917,"other",6),
 ("Camille Saint-Saëns","»Danse Bacchanale« aus: Samson et Dalila"):
    W("saint-saens-danse-bacchanale","camille-saint-saens","Danse Bacchanale aus »Samson et Dalila«",[cat("Opus","47")],1877,1877,"other",7),
 ("Malek Jandali","Symphonic Dances"):
    W("jandali-symphonic-dances","malek-jandali","Symphonic Dances",[],None,None,"other",None),
 ("Bilal Irshed","Al Mutanabbi"):
    W("irshed-al-mutanabbi","bilal-irshed","Al Mutanabbi",[],None,None,"other",None),
 ("Bilal Irshed","On the Way from Granada"):
    W("irshed-on-the-way-from-granada","bilal-irshed","On the Way from Granada",[],None,None,"other",None),
 ("Alan Menken","Aladdin"):
    W("menken-aladdin","alan-menken","Aladdin (Auszüge)",[],1992,1992,"other",None),
 ("Nikolai Rimski-Korsakow","Der Hummelflug aus: »Das Märchen vom Zaren Saltan«"):
    W("rimski-korsakow-hummelflug","nikolai-rimski-korsakow","Der Hummelflug aus »Das Märchen vom Zaren Saltan«",[],1899,1900,"other",3),
 ("Aram Chatschaturjan","»Sabre Dance« aus: Gayaneh"):
    W("chatschaturjan-saebeltanz","aram-chatschaturjan","Säbeltanz aus »Gayaneh«",[],1942,1942,"other",3),
 ("David Magrané","Partita on Henry VIII’s »Pastime with Good Company«"):
    W("magrane-partita-pastime","david-magrane","Partita on Henry VIII’s »Pastime with Good Company«",[],None,None,"other",None),
 ("William Walton","Konzert für Violine und Orchester"):
    W("walton-violinkonzert","william-walton","Konzert für Violine und Orchester h-Moll",[],1938,1939,"concerto",30),
 ("Johannes Brahms","Sinfonie Nr. 1 c-Moll"):
    W("brahms-sinfonie-1","johannes-brahms","Sinfonie Nr. 1 c-Moll",[cat("Opus","68")],1855,1876,"symphony",47),
 ("Sergei Prokofjew","Peter und der Wolf"):
    W("prokofjew-peter-und-der-wolf","sergej-prokofjew","Peter und der Wolf",[cat("Opus","67")],1936,1936,"other",25),
 ("Sergej Rachmaninoff","Prélude, Gavotte und Gigue nach Bachs Partita E-Dur"):
    W("rachmaninow-bach-partita-transkription","sergej-rachmaninow","Prélude, Gavotte und Gigue (nach J. S. Bachs Partita E-Dur)",[],1933,1933,"other",12),
 ("Franz Schubert","4 Impromptus für Klavier"):
    W("schubert-impromptus-d899","franz-schubert","4 Impromptus für Klavier",[cat("Opus","90"),cat("D","899")],1827,1827,"other",28),
 ("Sergei Rachmaninow","Etudes tableaux"):
    W("rachmaninow-etudes-tableaux-op33","sergej-rachmaninow","Études-tableaux",[cat("Opus","33")],1911,1911,"other",20),
 ("Sergei Rachmaninow","Variationen d-Moll op. 42 über ein Thema von Corelli"):
    W("rachmaninow-corelli-variationen","sergej-rachmaninow","Variationen über ein Thema von Corelli d-Moll",[cat("Opus","42")],1931,1931,"other",20),
 ("W. A. Mozart","Symphonie Nr. 32 G-Dur"):
    W("mozart-sinfonie-32","wolfgang-amadeus-mozart","Sinfonie Nr. 32 G-Dur",[cat("KV","318")],1779,1779,"symphony",8),
 ("Carl Maria von Weber","Konzert für Klarinette und Orchester Nr. 2 Es-Dur"):
    W("weber-klarinettenkonzert-2","carl-maria-von-weber","Konzert für Klarinette und Orchester Nr. 2 Es-Dur",[cat("Opus","74")],1811,1811,"concerto",23),
 ("Jean Sibelius","Symphonie Nr. 2 D-Dur"):
    W("sibelius-sinfonie-2","jean-sibelius","Sinfonie Nr. 2 D-Dur",[cat("Opus","43")],1901,1902,"symphony",43),
 ("Samy Moussa","»Elysium«"):
    W("moussa-elysium","samy-moussa","Elysium",[],2022,2022,"other",12),
 ("Anton Bruckner","Symphonie Nr. 6 A-Dur"):
    W("bruckner-sinfonie-6","anton-bruckner","Sinfonie Nr. 6 A-Dur",[cat("WAB","106")],1879,1881,"symphony",55),
 ("Felix Mendelssohn","Quartett Nr. 2 e-Moll"):
    W("mendelssohn-streichquartett-op44-2","felix-mendelssohn-bartholdy","Streichquartett Nr. 4 e-Moll",[cat("Opus","44/2")],1837,1837,"chamber_music",28),
 ("Johannes Brahms","Klarinetten-Quartett h-Moll"):
    W("brahms-klarinettenquintett","johannes-brahms","Klarinettenquintett h-Moll",[cat("Opus","115")],1891,1891,"chamber_music",38),
 ("Caroline Shaw","»Entr’acte«"):
    W("shaw-entracte","caroline-shaw","Entr’acte",[],2011,2011,"other",12),
 ("Robert Schumann","Klavierkonzert a-Moll"):
    W("schumann-klavierkonzert","robert-schumann","Klavierkonzert a-Moll",[cat("Opus","54")],1841,1845,"concerto",31),
 ("Alexander Zemlinsky","Symphonie Nr. 1 d-Moll"):
    W("zemlinsky-sinfonie-1","alexander-zemlinsky","Sinfonie Nr. 1 d-Moll",[],1892,1892,"symphony",40),
 ("Johann Sebastian Bach","Weihnachtsoratorium"):
    W("bach-weihnachtsoratorium","johann-sebastian-bach","Weihnachtsoratorium",[cat("BWV","248")],1734,1734,"oratorio",150),
 ("Arvo Pärt","»Fratres« für Streichorchester und Schlagzeug"):
    W("paert-fratres","arvo-paert","Fratres",[],1977,1977,"other",11,version="Fassung für Streichorchester und Schlagzeug"),
 ("Anna Clyne","»Dance«"):
    W("clyne-dance","anna-clyne","Dance (für Violoncello und Orchester)",[],2019,2019,"concerto",25),
 ("Pijotr Iljitsch Tschaikowski","Symphonie Nr. 6 h-Moll op. 74 »Pathétique«"):
    W("tschaikowsky-sinfonie-6","peter-iljitsch-tschaikowsky","Sinfonie Nr. 6 h-Moll »Pathétique«",[cat("Opus","74")],1893,1893,"symphony",47),
 ("Ludwig van Beethoven","Streichtrio Nr. 3 c-Moll"):
    W("beethoven-streichtrio-op9-3","ludwig-van-beethoven","Streichtrio Nr. 3 c-Moll",[cat("Opus","9/3")],1797,1798,"chamber_music",26),
 ("Anton Webern","Streichtrio"):
    W("webern-streichtrio","anton-webern","Streichtrio",[cat("Opus","20")],1927,1927,"chamber_music",9),
 ("Franz Schubert","Streichtrio"):
    W("schubert-streichtrio-d581","franz-schubert","Streichtrio B-Dur",[cat("D","581")],1817,1817,"chamber_music",22),
 ("John Adams","»The Chairman Dances« Foxtrott für Orchester"):
    W("adams-the-chairman-dances","john-adams","The Chairman Dances (Foxtrott für Orchester)",[],1985,1985,"other",13),
 ("Nino Rota","»Divertimento Concertante«"):
    W("rota-divertimento-concertante","nino-rota","Divertimento Concertante für Kontrabass und Orchester",[],1968,1973,"concerto",25),
 ("Francis Poulenc","Sinfonietta"):
    W("poulenc-sinfonietta","francis-poulenc","Sinfonietta",[cat("FP","141")],1947,1948,"other",28),
 ("Michael Haydn","Sinfonia Nr. 25 G-Dur"):
    W("michael-haydn-sinfonia-25","michael-haydn","Sinfonia Nr. 25 G-Dur",[cat("MH","334")],1783,1783,"symphony",18),
 ("César Franck","Grande Pièce Symphonique"):
    W("franck-grande-piece-symphonique","cesar-franck","Grande Pièce Symphonique",[cat("Opus","17")],1863,1863,"other",27,version="Bearbeitung für Orgel und Orchester von Zsigmond Szathmáry"),
 ("Richard Strauss","»Also sprach Zarathustra«"):
    W("strauss-also-sprach-zarathustra","richard-strauss","Also sprach Zarathustra",[cat("Opus","30")],1896,1896,"other",33),
 ("Charles Ives","»The unanswered question«"):
    W("ives-the-unanswered-question","charles-ives","The Unanswered Question",[],1908,1908,"other",6),
 ("Paul Hindemith","Symphonie »Mathis der Maler«"):
    W("hindemith-mathis-der-maler-sinfonie","paul-hindemith","Sinfonie »Mathis der Maler«",[],1933,1934,"symphony",27),
 ("Anton Bruckner","»Te deum« C-Dur"):
    W("bruckner-te-deum","anton-bruckner","Te Deum C-Dur",[cat("WAB","45")],1881,1884,"other",24),
 ("Franz Schubert","Ouvertüre in c-Moll"):
    W("schubert-ouvertuere-c-moll-d8a","franz-schubert","Ouvertüre c-Moll",[cat("D","8a")],1811,1811,"overture",8),
 ("Lidia De Migno","»Mein Traum« für Streichquartett"):
    W("de-migno-mein-traum","lidia-de-migno","Mein Traum (für Streichquartett)",[],None,None,"chamber_music",None),
 ("Franz Schubert","Streichquartett Nr. 5 in B-Dur"):
    W("schubert-streichquartett-5-d68","franz-schubert","Streichquartett Nr. 5 B-Dur",[cat("D","68")],1813,1813,"chamber_music",20),
 ("Franz Schubert","Streichquartett Nr. 15 G-Dur"):
    W("schubert-streichquartett-15-d887","franz-schubert","Streichquartett Nr. 15 G-Dur",[cat("D","887")],1826,1826,"chamber_music",45),
 ("Robert Schumann","Ouvertüre, Scherzo und Finale"):
    W("schumann-ouvertuere-scherzo-finale","robert-schumann","Ouvertüre, Scherzo und Finale",[cat("Opus","52")],1841,1841,"other",18),
 ("Manuel Ponce","Concierto del sur"):
    W("ponce-concierto-del-sur","manuel-ponce","Concierto del Sur (für Gitarre und Orchester)",[],1941,1941,"concerto",25),
 ("Ludwig van Beethoven","Symphonie Nr. 4 B-Dur"):
    W("beethoven-sinfonie-4","ludwig-van-beethoven","Sinfonie Nr. 4 B-Dur",[cat("Opus","60")],1806,1806,"symphony",34),
 ("Ernest Bloch","Three Nocturnes C-Dur"):
    W("bloch-three-nocturnes","ernest-bloch","Three Nocturnes (für Klaviertrio)",[],1924,1924,"chamber_music",12),
 ("Dmitri Schostakowitsch","Trio Nr. 1 c-Moll"):
    W("schostakowitsch-klaviertrio-1","dmitri-schostakowitsch","Klaviertrio Nr. 1 c-Moll",[cat("Opus","8")],1923,1923,"chamber_music",13),
 ("Johannes Brahms","Trio Nr. 1 H-Dur"):
    W("brahms-klaviertrio-1","johannes-brahms","Klaviertrio Nr. 1 H-Dur",[cat("Opus","8")],1854,1854,"chamber_music",35),
 ("Dmitri Kabalewski","»Die Komödianten« Suite"):
    W("kabalewski-die-komoedianten","dmitri-kabalewski","»Die Komödianten«, Suite",[cat("Opus","26")],1940,1940,"other",16),
 ("Igor Strawinsky","»Der Feuervogel« Suite für Orchester"):
    W("strawinsky-feuervogel-suite","igor-strawinsky","»Der Feuervogel«, Suite für Orchester",[],1919,1919,"other",22,version="Suite 1919"),
 ("Sergei Rachmaninov","Klavierkonzert Nr. 2 c-Moll"):
    W("rachmaninow-klavierkonzert-2","sergej-rachmaninow","Klavierkonzert Nr. 2 c-Moll",[cat("Opus","18")],1900,1901,"concerto",33),
}

# program entries that are NOT real works (noise) -> optional description note
NOISE = {
 ("Musik von","Debussy, Ravel, Fauré"): "Werke von Debussy, Ravel und Fauré.",
 ("Weihnachtskonzert","des Polizeichors Essen"): "Weihnachtskonzert des Polizeichors Essen.",
 ("Neujahrskonzert","Mariam Batsashvili Klavier"): "Neujahrskonzert mit Mariam Batsashvili (Klavier).",
 ("»Nur der RWE«","Sounds of Hafenstraße"): "Mit »Nur der RWE« – Sounds of Hafenstraße.",
}

# ---------- curation: venues & cities ----------
NEW_CITIES = [
 {"id":"leverkusen","name":"Leverkusen","country":"Deutschland"},
 {"id":"muelheim-an-der-ruhr","name":"Mülheim an der Ruhr","country":"Deutschland"},
 {"id":"coesfeld","name":"Coesfeld","country":"Deutschland"},
]
def V(vid,name,city,vtype,inst,region=None):
    return {"id":vid,"name":name,"cityIds":[city],"region":region,"address":None,
            "coordinates":None,"website":None,"type":vtype,"institutionId":inst}
BS_INST = "bergische-symphoniker-institution"
NEW_VENUES = [
 V("konzerthaus-solingen","Konzerthaus Solingen","solingen","concert_hall",BS_INST),
 V("theater-solingen","Theater Solingen","solingen","theatre",BS_INST),
 V("teo-otto-theater","Teo Otto Theater","remscheid","theatre",BS_INST),
 V("zentrum-fuer-verfolgte-kuenste","Zentrum für verfolgte Künste","solingen","other",None),
 V("schloss-burg","Schloss Burg","solingen","other",None),
 V("forum-leverkusen","Forum Leverkusen","leverkusen","concert_hall",None),
 V("stadthalle-muelheim","Stadthalle Mülheim an der Ruhr","muelheim-an-der-ruhr","concert_hall",None),
 V("konzert-theater-coesfeld","Konzert Theater Coesfeld","coesfeld","theatre",None),
 V("lutherkirche-remscheid","Lutherkirche Remscheid","remscheid","other",None),
 V("dorper-kirche-solingen","Dorper Kirche","solingen","other",None),
 V("stadtkirche-solingen","Stadtkirche Solingen","solingen","other",None),
 V("suedpark-solingen","Südpark Solingen","solingen","other",None),
 V("stadtpark-konzertmuschel-remscheid","Stadtpark Konzertmuschel Remscheid","remscheid","other",None),
 V("brueckenpark-solingen","Brückenpark Müngsten","solingen","other",None),
 V("marktplatz-graefrath-solingen","Marktplatz Gräfrath","solingen","other",None),
 V("munsterplatz-lennep-remscheid","Munsterplatz Lennep","remscheid","other",None),
 V("heimatbuehne-luettringhausen-remscheid","Heimatbühne Lüttringhausen","remscheid","other",None),
]
VENUE_MAP = {
 "Konzerthaus Solingen":"konzerthaus-solingen",
 "Theater Solingen":"theater-solingen",
 "Theater und Konzerthaus Solingen":"theater-und-konzerthaus-solingen",
 "Teo Otto Theater Remscheid":"teo-otto-theater",
 "Teo Otto Theater":"teo-otto-theater",
 "Essen Philharmonie":"philharmonie-essen",
 "Zentrum für verfolgte Künste Solingen":"zentrum-fuer-verfolgte-kuenste",
 "Schloss Burg Rittersaal":"schloss-burg",
 "Leverkusen Forum":"forum-leverkusen",
 "Mülheim / Ruhr Stadthalle":"stadthalle-muelheim",
 "Coesfeld Konzert Theater":"konzert-theater-coesfeld",
 "Remscheid Lutherkirche":"lutherkirche-remscheid",
 "Lutherkirche Remscheid":"lutherkirche-remscheid",
 "Solingen Dorper Kirche":"dorper-kirche-solingen",
 "Stadtkirche Solingen":"stadtkirche-solingen",
 "Solingen Südpark":"suedpark-solingen",
 "Remscheid Stadtpark Konzertmuschel":"stadtpark-konzertmuschel-remscheid",
 "Solingen Brückenpark":"brueckenpark-solingen",
 "Solingen-Gräfrath Marktplatz":"marktplatz-graefrath-solingen",
 "Remscheid-Lennep Munsterplatz":"munsterplatz-lennep-remscheid",
 "Remscheid-Lüttringhausen Heimatbühne":"heimatbuehne-luettringhausen-remscheid",
}
VENUE_CITY = {v["id"]: v["cityIds"][0] for v in NEW_VENUES}
VENUE_CITY.update({"theater-und-konzerthaus-solingen":"solingen","philharmonie-essen":"essen"})

# ---------- curation: roles ----------
SOLO_ROLES = {"Violine","Viola","Violoncello","Kontrabass","Klavier","Klarinette","Oboe",
              "Fagott","Blockflöte","Orgel","Gitarre","Sopran","Alt","Tenor","Bariton",
              "Bass","Gesang","Sprecher","Texte und Rap"}
SKIP_NAMES = {"N.N.","Chor der","Atlantic Ballet Atlantique Canada"}

def clean_name(n):
    return re.sub(r"[\s,]+$","",n.strip())

OPERA_TITLES = {"La bohème","Der Vogelhändler"}

# ---------- run ----------
concerts = extract_season(fetch_concerts())

people = load("people"); composers = load("composers"); works = load("works")
venues = load("venues"); cities = load("cities"); events = load("events")

people_by_id = {p["id"]: p for p in people["people"]}
people_id_by_name = {p["name"].strip().lower(): p["id"] for p in people["people"]}
comp_ids = {c["id"] for c in composers["composers"]}
work_ids = {w["id"] for w in works["works"]}
venue_ids = {v["id"] for v in venues["venues"]}
city_ids = {c["id"] for c in cities["cities"]}

used_people=set(); used_composers=set(); used_works=set(); used_venues=set()

def ensure_person(name):
    name = clean_name(name)
    if not name or name in SKIP_NAMES: return None
    key = name.lower()
    if key in people_id_by_name:
        pid = people_id_by_name[key]
    else:
        pid = fold(name)
        base = pid; i=2
        while pid in people_by_id and people_by_id[pid]["name"].strip().lower()!=key:
            pid = f"{base}-{i}"; i+=1
        if pid not in people_by_id:
            rec={"id":pid,"name":name}
            people["people"].append(rec); people_by_id[pid]=rec
            people_id_by_name[key]=pid
    used_people.add(pid)
    return pid

# add cities & venues (master data) up-front for referential completeness
for c in NEW_CITIES:
    if c["id"] not in city_ids:
        cities["cities"].append(c); city_ids.add(c["id"])
for v in NEW_VENUES:
    if v["id"] not in venue_ids:
        venues["venues"].append(v); venue_ids.add(v["id"])

def add_work(src_comp, title):
    rec = WORKS.get((src_comp, title))
    if not rec: return None
    if rec["id"] not in work_ids:
        works["works"].append(rec); work_ids.add(rec["id"])
    used_works.add(rec["id"]); used_composers.add(rec["composerId"])
    return rec["id"]

# remove previously ingested Bergische events (idempotency)
before = len(events["events"])
events["events"] = [e for e in events["events"]
                    if SRC_HOST not in ((e.get("source") or {}).get("url","") or "")]
removed = before - len(events["events"])

existing_event_ids = {e["id"] for e in events["events"]}
new_events=[]

for c in concerts:
    title = c["title"]; subtitle = c["subtitle"]
    full_title = f"{title} – {subtitle}" if subtitle else title
    is_opera = title in OPERA_TITLES
    # cast -> conductor / soloist person ids
    conductors=[]; soloists=[]
    for ca in c["cast"]:
        role = ca["role"].strip(); name = ca["name"].strip()
        if role.startswith("Leitung") or role.startswith("Dirigent"):
            pid=ensure_person(name)
            if pid and pid not in conductors: conductors.append(pid)
        elif role.endswith("Violine") and name=="Alinde Quartett":
            pid=ensure_person(role[:-len("Violine")])  # "Eugenia Ottaviano"
            if pid and pid not in soloists: soloists.append(pid)
        elif role in SOLO_ROLES:
            pid=ensure_person(name)
            if pid and pid not in soloists: soloists.append(pid)
        # else: staging/moderation/choir/ensemble -> skip
    # program -> work ids  + noise notes
    prog=[]; notes=[]
    for p in c["program"]:
        comp=p["composer"]; wt=p["workTitle"]
        if (comp,wt) in NOISE:
            notes.append(NOISE[(comp,wt)]); continue
        wid=add_work(comp,wt)
        if wid: prog.append({"workId":wid})
        else: notes.append(f"Programm: {comp} – {wt}." if comp else f"Programm: {wt}.")
    desc_parts=[]
    if subtitle: desc_parts.append(subtitle if subtitle.endswith(('.','!','?')) else subtitle+".")
    desc_parts += notes
    description = " ".join(desc_parts) if desc_parts else None
    # one event per performance
    for perf in c["performances"]:
        dt=perf["dateTime"]; date=dt[:10]; start=dt[11:16]
        vid=VENUE_MAP.get(perf["venue"])
        if not vid:
            print("!! UNMAPPED VENUE:", perf["venue"], file=sys.stderr); continue
        used_venues.add(vid)
        cid=VENUE_CITY.get(vid,"solingen")
        base=f"event-{date}-{cid}-{fold(title)}"
        eid=base; 
        if eid in existing_event_ids:
            eid=f"{base}-{start.replace(':','')}"
        i=2
        while eid in existing_event_ids:
            eid=f"{base}-{i}"; i+=1
        existing_event_ids.add(eid)
        ev={
            "id":eid,"title":full_title,
            "eventType":"opera" if is_opera else "concert",
            "date":date,"startTime":start,"endTime":None,"status":"scheduled",
            "ensembleIds":[ENSEMBLE_ID],"venueId":vid,"cityId":cid,
            "conductorPersonIds":list(conductors),"soloistPersonIds":list(soloists),
            "program":list(prog),"seriesId":None,"description":description,
            "source":{"url":f"https://{SRC_HOST}/konzerte/{c['slug']}","name":SRC_NAME,"retrievedAt":TODAY},
            "ticketUrl":perf.get("ticketUrl"),"lastVerified":TODAY,
        }
        new_events.append(ev)

new_events.sort(key=lambda e:(e["date"],e["startTime"],e["id"]))
events["events"].extend(new_events)

# append new composer master records referenced by works
for cid in sorted(used_composers):
    if cid not in comp_ids:
        if cid in NEW_COMPOSERS:
            nm,fr,to=NEW_COMPOSERS[cid]
            composers["composers"].append({"id":cid,"name":nm,"life":{"from":fr,"to":to}})
            comp_ids.add(cid)
        else:
            print("!! MISSING COMPOSER RECORD:", cid, file=sys.stderr)

# update metadata timestamps
for obj in (people,composers,works,venues,cities,events):
    obj.setdefault("metadata",{})["lastUpdated"]=TODAY
events["metadata"]["notes"]=("Enthält recherchierte Konzerte des WDR Sinfonieorchesters "
  "(Kölner Philharmonie) und der Bergischen Symphoniker (Spielzeit 2026/27, Quelle: "
  "bergischesymphoniker.de) sowie einige frühere Beispieldatensätze (Quellen mit example.org).")

save("people",people); save("composers",composers); save("works",works)
save("venues",venues); save("cities",cities); save("events",events)

print(f"Removed prior Bergische events: {removed}")
print(f"New events: {len(new_events)}  (total now {len(events['events'])})")
print(f"New people: {len(used_people)} used; people total {len(people['people'])}")
print(f"Works used: {len(used_works)}; works total {len(works['works'])}")
print(f"Composers used: {len(used_composers)}; composers total {len(composers['composers'])}")
print(f"Venues used: {len(used_venues)}; venues total {len(venues['venues'])}")
