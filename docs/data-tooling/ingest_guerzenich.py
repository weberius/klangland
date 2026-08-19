#!/usr/bin/env python3
"""Ingest the Gürzenich-Orchester Köln 2026/27 schedule into klangland ``data/*.json``.

Source: https://www.guerzenich-orchester.de/de/event-detail/<slug> (TYPO3 site).
The canonical event list comes from the events sub-sitemap; only bookable events of
season 2026/27 (those exposing concrete dates) are ingested.

Curated (Option B): works/composers are enriched with life dates, composition years,
genre and approximate duration. Program blobs from the CMS are hand-mapped per event
to accurate work records; generic/announcement text is preserved in ``description``.

Idempotent: re-running removes previously ingested Gürzenich events (matched by the
source host) and merges master data without duplicates.

Usage:
    python docs/data-tooling/ingest_guerzenich.py            # use saved season JSON
    python docs/data-tooling/ingest_guerzenich.py --raw guerzenich_season_raw.json
    python docs/data-tooling/ingest_guerzenich.py --date 2026-08-17
"""
import argparse, datetime, html, json, os, re, sys, unicodedata, urllib.request

SRC_HOST = "guerzenich-orchester.de"
SRC_NAME = "Gürzenich-Orchester Köln"
CALENDAR_URL = f"https://www.{SRC_HOST}/de/programm"
ENSEMBLE_ID = "guerzenich-orchester-koeln"

SITEMAP = "https://www.guerzenich-orchester.de/de/sitemap.xml"
EVENT_BASE = "https://www.guerzenich-orchester.de/de/event-detail/"
SEASON_START, SEASON_END = "2026-08-01", "2027-08-01"  # season 2026/27 window

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")

_ap = argparse.ArgumentParser(description="Ingest Gürzenich-Orchester Köln schedule")
_ap.add_argument("--raw", default=None,
                 help="path to a saved parsed-season JSON; if omitted, scrape the live site")
_ap.add_argument("--date", default=datetime.date.today().isoformat(),
                 help="retrievedAt/lastVerified date (YYYY-MM-DD)")
ARGS = _ap.parse_args()
TODAY = ARGS.date

# ---------- helpers ----------
_UML = {"ä":"ae","ö":"oe","ü":"ue","Ä":"ae","Ö":"oe","Ü":"ue","ß":"ss",
        "ł":"l","ø":"o","đ":"d","ħ":"h","ı":"i","æ":"ae","œ":"oe",
        "ț":"t","ș":"s","ğ":"g","ç":"c","ñ":"n","å":"a","š":"s","ž":"z","č":"c"}
def fold(s):
    s = s.strip().lower()
    for k,v in _UML.items():
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

# ---------- live scraper / HTML parser ----------
def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "klangland-ingest"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def _clean(s):
    if s is None: return ""
    s = re.sub(r"<[^>]+>", " ", s); s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def _grab(pat, t):
    m = re.search(pat, t, re.S); return m.group(1) if m else None

def _event_slugs():
    """Canonical event slugs from the events sub-sitemap."""
    idx = _get(SITEMAP)
    ev_sm = re.search(r"<loc>([^<]*sitemap=events[^<]*)</loc>", idx)
    if not ev_sm: return []
    sm = _get(html.unescape(ev_sm.group(1)))
    slugs = re.findall(r"/de/event-detail/([a-z0-9-]+)", sm)
    return sorted(set(slugs))

def _parse_event(t_html, slug):
    title = _clean(_grab(r'<h1 class="m-event__title">(.*?)</h1>', t_html))
    category = _clean(_grab(r'm-event__categories">(.*?)</div>', t_html))
    date_day = _clean(_grab(r'm-event__date-day">(.*?)</div>', t_html))
    years = [int(y) for y in re.findall(r"(20\d{2})", date_day or "")]
    # cast
    cast = []
    cm = re.search(r'Besetzung\s*</h2>\s*<ul class="m-event__occupation">(.*?)</ul>', t_html, re.S)
    if cm:
        for el in re.findall(r'<li class="m-event__occupation-element">(.*?)</li>', cm.group(1), re.S):
            cast.append({"name": _clean(_grab(r'occupation-element-title">(.*?)</h3>', el)),
                         "role": _clean(_grab(r'occupation-element-position">(.*?)</p>', el))})
    # performances
    perfs = []
    dc = re.search(r'data-component="eventDates">(.*?)(?:<h2|<footer|m-event__text|</main>)', t_html, re.S)
    container = dc.group(1) if dc else ""
    for item in re.split(r"m-event-dates__wrapper", container)[1:]:
        day = _clean(_grab(r'm-event-dates__day">(.*?)</div>', item))
        time = _clean(_grab(r'm-event-dates__time">(.*?)</div>', item))
        ven = _clean(_grab(r'm-event-dates__venue">(.*?)</div>', item))
        tk = _grab(r'm-event-dates__button[^"]*"\s+href="([^"]+)"', item) or \
             _grab(r'href="([^"]+)"[^>]*class="[^"]*m-event-dates__button', item)
        if day:
            perfs.append({"day": day, "time": time, "venue": ven,
                          "ticket": html.unescape(tk) if tk else None})
    return {"slug": slug, "title": title, "category": category,
            "dateHeader": date_day, "years": years, "cast": cast, "performances": perfs}

def _compute_dates(ev):
    """Attach ISO date + HH:MM to each performance using header year(s)."""
    ys = sorted(set(ev["years"]))
    def year_for(month):
        if len(ys) == 1: return ys[0]
        if not ys: return None
        return ys[0] if month >= 8 else ys[-1]   # Aug-Dec -> earlier year
    dates = []
    for p in ev["performances"]:
        m = re.match(r"(\d{2})\.(\d{2})\.", p["day"])
        if not m: continue
        dd, mm = int(m.group(1)), int(m.group(2))
        yy = year_for(mm)
        p["date"] = f"{yy:04d}-{mm:02d}-{dd:02d}" if yy else None
        tm = re.search(r"(\d{1,2}):(\d{2})", p["time"] or "")
        p["startTime"] = f"{int(tm.group(1)):02d}:{tm.group(2)}" if tm else None
        if p["date"]: dates.append(p["date"])
    ev["firstDate"] = min(dates) if dates else None
    return ev

def scrape_season():
    """Scrape the live site and return season-2026/27 events with computed dates.

    Only events that expose concrete (bookable) dates within the season window are
    returned — past-season pages no longer list dates and are skipped.
    """
    out = []
    for slug in _event_slugs():
        try:
            ev = _compute_dates(_parse_event(_get(EVENT_BASE + slug), slug))
        except Exception as exc:  # network / parse hiccup on a single page
            print(f"!! failed {slug}: {exc}", file=sys.stderr); continue
        if not ev["firstDate"]:
            continue
        if SEASON_START <= ev["firstDate"] < SEASON_END:
            out.append(ev)
    out.sort(key=lambda e: e["firstDate"])
    return out

# ---------- curation: new composers (id -> (name, from, to)) ----------
NEW_COMPOSERS = {
    "george-gershwin": ("George Gershwin", 1898, 1937),
    "joerg-widmann": ("Jörg Widmann", 1973, None),
    "oskar-jockel": ("Oskar Jockel", 1995, None),
    "niels-wilhelm-gade": ("Niels Wilhelm Gade", 1817, 1890),
    "ernst-von-dohnanyi": ("Ernst von Dohnányi", 1877, 1960),
    "anton-arensky": ("Anton Arensky", 1861, 1906),
    "hector-berlioz": ("Hector Berlioz", 1803, 1869),
    "ralph-vaughan-williams": ("Ralph Vaughan Williams", 1872, 1958),
    "thomas-dunhill": ("Thomas Dunhill", 1877, 1946),
    "roger-quilter": ("Roger Quilter", 1877, 1953),
    "carl-nielsen": ("Carl Nielsen", 1865, 1931),
    "alban-berg": ("Alban Berg", 1885, 1935),
    "jacques-ibert": ("Jacques Ibert", 1890, 1962),
    "ian-clarke": ("Ian Clarke", 1964, None),
    "claude-debussy": ("Claude Debussy", 1862, 1918),
    "luigi-boccherini": ("Luigi Boccherini", 1743, 1805),
    "niccolo-paganini": ("Niccolò Paganini", 1782, 1840),
    "mario-castelnuovo-tedesco": ("Mario Castelnuovo-Tedesco", 1895, 1968),
    "hans-werner-henze": ("Hans Werner Henze", 1926, 2012),
    "eivind-groven": ("Eivind Groven", 1901, 1977),
    "edvard-grieg": ("Edvard Grieg", 1843, 1907),
    "matthias-pintscher": ("Matthias Pintscher", 1971, None),
    "henry-purcell": ("Henry Purcell", 1659, 1695),
    "gideon-klein": ("Gideon Klein", 1919, 1945),
    "vassos-nicolaou": ("Vassos Nicolaou", 1971, None),
    "nikolai-kapustin": ("Nikolai Kapustin", 1937, 2020),
}
# source composer string (as parsed) -> composer id (existing or new)
COMPOSER_ID = {
    "George Gershwin":"george-gershwin",
    "Felix Mendelssohn Bartholdy":"felix-mendelssohn-bartholdy",
    "Jörg Widmann":"joerg-widmann",
    "Johannes Brahms":"johannes-brahms",
    "Richard Strauss":"richard-strauss",
    "Oskar Jockel":"oskar-jockel",
    "Igor Strawinsky":"igor-strawinsky",
    "Leonard Bernstein":"leonard-bernstein",
    "Niels Wilhelm Gade":"niels-wilhelm-gade",
    "Ernst von Dohnányi":"ernst-von-dohnanyi",
    "Joseph Haydn":"joseph-haydn",
    "Sergej Rachmaninow":"sergej-rachmaninow",
    "Sergej Prokofjew":"sergej-prokofjew",
    "Robert Schumann":"robert-schumann",
    "Anton Arensky":"anton-arensky",
    "Franz Schubert":"franz-schubert",
    "Béla Bartók":"bela-bartok",
    "Camille Saint-Saëns":"camille-saint-saens",
    "Camille Saint-Säens":"camille-saint-saens",
    "Gustav Mahler":"gustav-mahler",
    "Johann Sebastian Bach":"johann-sebastian-bach",
    "Wolfgang Amadeus Mozart":"wolfgang-amadeus-mozart",
    "Hector Berlioz":"hector-berlioz",
    "Richard Wagner":"richard-wagner",
    "Ralph Vaughan Williams":"ralph-vaughan-williams",
    "Thomas Dunhill":"thomas-dunhill",
    "Roger Quilter":"roger-quilter",
    "Jean Sibelius":"jean-sibelius",
    "Antonín Dvořák":"antonin-dvorak",
    "Carl Nielsen":"carl-nielsen",
    "Alban Berg":"alban-berg",
    "Jacques Ibert":"jacques-ibert",
    "Ian Clarke":"ian-clarke",
    "Claude Debussy":"claude-debussy",
    "Peter Tschaikowsky":"peter-iljitsch-tschaikowsky",
    "Luigi Boccherini":"luigi-boccherini",
    "Niccolò Paganini":"niccolo-paganini",
    "Mario Castelnuovo-Tedesco":"mario-castelnuovo-tedesco",
    "Hans Werner Henze":"hans-werner-henze",
    "Eivind Groven":"eivind-groven",
    "Edvard Grieg":"edvard-grieg",
    "Matthias Pintscher":"matthias-pintscher",
    "Paul Hindemith":"paul-hindemith",
    "Henry Purcell":"henry-purcell",
    "Gideon Klein":"gideon-klein",
    "Vassos Nicolaou":"vassos-nicolaou",
    "Carl Maria von Weber":"carl-maria-von-weber",
    "Nikolai Kapustin":"nikolai-kapustin",
    "Ludwig van Beethoven":"ludwig-van-beethoven",
    "Anton Bruckner":"anton-bruckner",
}

def W(wid, cid, title, catalogue, yf, yt, genre, dur, version=None, scoring=None, desc=None):
    year = None if yf is None else {"from": yf, "to": yt if yt is not None else yf}
    return {"id":wid,"composerId":cid,"title":title,"catalogue":catalogue,
            "yearComposed":year,"genre":genre,"durationMinutes":dur,
            "version":version,"scoring":scoring,"description":desc}

# ---------- curation: new works (id -> record) ----------
NEW_WORKS = {
 "gershwin-amerikaner-in-paris": W("gershwin-amerikaner-in-paris","george-gershwin","Ein Amerikaner in Paris",[],1928,1928,"other",18),
 "gershwin-porgy-and-bess-concert-of-songs": W("gershwin-porgy-and-bess-concert-of-songs","george-gershwin","A Concert of Songs (Auszüge aus »Porgy and Bess«)",[],1935,1935,"other",30,version="Arrangement 2024"),
 "mendelssohn-sinfonie-5-reformation": W("mendelssohn-sinfonie-5-reformation","felix-mendelssohn-bartholdy","Sinfonie Nr. 5 d-Moll »Reformationssinfonie«",[cat("Opus","107")],1830,1830,"symphony",30),
 "widmann-ad-absurdum": W("widmann-ad-absurdum","joerg-widmann","ad absurdum – Konzertstück für Trompete und kleines Orchester",[],2002,2002,"concerto",12),
 "brahms-gesang-aus-fingal": W("brahms-gesang-aus-fingal","johannes-brahms","Gesang aus Fingal",[cat("Opus","17b")],1860,1860,"other",5),
 "jockel-auftragswerk-2026": W("jockel-auftragswerk-2026","oskar-jockel","Auftragswerk für die Orchesterakademie",[],2026,2026,"other",None),
 "strawinsky-pulcinella-suite": W("strawinsky-pulcinella-suite","igor-strawinsky","Pulcinella-Suite",[],1920,1920,"other",22,version="rev. 1949"),
 "brahms-schicksalslied": W("brahms-schicksalslied","johannes-brahms","Schicksalslied",[cat("Opus","54")],1871,1871,"other",16),
 "bernstein-chichester-psalms": W("bernstein-chichester-psalms","leonard-bernstein","Chichester Psalms",[],1965,1965,"other",19),
 "gade-streichsextett": W("gade-streichsextett","niels-wilhelm-gade","Streichsextett Es-Dur",[cat("Opus","44")],1863,1864,"chamber_music",30),
 "dohnanyi-streichsextett": W("dohnanyi-streichsextett","ernst-von-dohnanyi","Streichsextett B-Dur",[],1893,1896,"chamber_music",28),
 "haydn-le-matin": W("haydn-le-matin","joseph-haydn","Sinfonie Nr. 6 D-Dur »Le Matin«",[cat("Hob","I:6")],1761,1761,"symphony",22),
 "rachmaninow-sinfonie-6": None,  # placeholder guard (unused)
 "prokofjew-sinfonie-6": W("prokofjew-sinfonie-6","sergej-prokofjew","Sinfonie Nr. 6 es-Moll",[cat("Opus","111")],1945,1947,"symphony",40),
 "arensky-streichquartett-2": W("arensky-streichquartett-2","anton-arensky","Streichquartett Nr. 2 a-Moll",[cat("Opus","35")],1894,1894,"chamber_music",23),
 "schubert-streichquintett-d956": W("schubert-streichquintett-d956","franz-schubert","Streichquintett C-Dur",[cat("D","956"),cat("Opus","163")],1828,1828,"chamber_music",55),
 "bartok-violakonzert": W("bartok-violakonzert","bela-bartok","Konzert für Viola und Orchester",[cat("Sz","120")],1945,1945,"concerto",21),
 "haydn-cellokonzert-2": W("haydn-cellokonzert-2","joseph-haydn","Konzert für Violoncello und Orchester Nr. 2 D-Dur",[cat("Hob","VIIb:2")],1783,1783,"concerto",26),
 "saint-saens-violinkonzert-3": W("saint-saens-violinkonzert-3","camille-saint-saens","Konzert für Violine und Orchester Nr. 3 h-Moll",[cat("Opus","61")],1880,1880,"concerto",30),
 "mahler-sinfonie-6": W("mahler-sinfonie-6","gustav-mahler","Sinfonie Nr. 6 a-Moll »Tragische«",[],1903,1904,"symphony",80),
 "bach-orchestersuite-1": W("bach-orchestersuite-1","johann-sebastian-bach","Orchestersuite Nr. 1 C-Dur",[cat("BWV","1066")],1718,1723,"other",25),
 "mozart-oboenkonzert-c-dur": W("mozart-oboenkonzert-c-dur","wolfgang-amadeus-mozart","Konzert für Oboe und Orchester C-Dur",[cat("KV","314")],1777,1777,"concerto",21),
 "schubert-sinfonie-7-unvollendete": W("schubert-sinfonie-7-unvollendete","franz-schubert","Sinfonie h-Moll »Unvollendete«",[cat("D","759")],1822,1822,"symphony",25),
 "berlioz-carnaval-romain": W("berlioz-carnaval-romain","hector-berlioz","Le carnaval romain – Ouvertüre",[cat("Opus","9")],1844,1844,"overture",9),
 "mozart-sinfonie-40": W("mozart-sinfonie-40","wolfgang-amadeus-mozart","Sinfonie Nr. 40 g-Moll",[cat("KV","550")],1788,1788,"symphony",30),
 "mozart-requiem": W("mozart-requiem","wolfgang-amadeus-mozart","Requiem d-Moll",[cat("KV","626")],1791,1791,"requiem",50),
 "bartok-wunderbarer-mandarin": W("bartok-wunderbarer-mandarin","bela-bartok","Der wunderbare Mandarin – Tanzpantomime",[cat("Opus","19"),cat("Sz","73")],1918,1926,"other",30),
 "wagner-parsifal-3-aufzug": W("wagner-parsifal-3-aufzug","richard-wagner","Parsifal – 3. Aufzug",[cat("WWV","111")],1877,1882,"opera",70),
 "vaughan-williams-on-wenlock-edge": W("vaughan-williams-on-wenlock-edge","ralph-vaughan-williams","On Wenlock Edge – Sechs Lieder für Tenor, Klavier und Streichquartett",[],1909,1909,"chamber_music",22),
 "dunhill-klavierquartett": W("dunhill-klavierquartett","thomas-dunhill","Klavierquartett h-Moll",[cat("Opus","16")],1903,1903,"chamber_music",24),
 "quilter-to-julia": W("quilter-to-julia","roger-quilter","To Julia – Sechs Gedichte von Robert Herrick",[cat("Opus","8")],1906,1906,"chamber_music",15),
 "sibelius-finlandia": W("sibelius-finlandia","jean-sibelius","Finlandia – Sinfonische Dichtung",[cat("Opus","26")],1899,1900,"other",9),
 "dvorak-cellokonzert": W("dvorak-cellokonzert","antonin-dvorak","Konzert für Violoncello und Orchester h-Moll",[cat("Opus","104")],1894,1895,"concerto",40),
 "nielsen-sinfonie-5": W("nielsen-sinfonie-5","carl-nielsen","Sinfonie Nr. 5",[cat("Opus","50")],1920,1922,"symphony",35),
 "berg-lulu": W("berg-lulu","alban-berg","Lulu – Oper in drei Akten (unvollendete Fassung)",[],1928,1935,"opera",180),
 "berlioz-trio-jeunes-ismaelites": W("berlioz-trio-jeunes-ismaelites","hector-berlioz","Trio des jeunes Ismaélites aus »L’enfance du Christ«",[cat("Opus","25")],1850,1854,"chamber_music",7),
 "ibert-deux-interludes": W("ibert-deux-interludes","jacques-ibert","Deux Interludes für Flöte, Violine und Harfe",[],1946,1946,"chamber_music",7),
 "saint-saens-fantaisie-violine-harfe": W("saint-saens-fantaisie-violine-harfe","camille-saint-saens","Fantaisie für Violine und Harfe",[cat("Opus","124")],1907,1907,"chamber_music",15),
 "clarke-maya": W("clarke-maya","ian-clarke","Maya für zwei Flöten und Harfe",[],1986,2000,"chamber_music",8),
 "debussy-chansons-de-bilitis": W("debussy-chansons-de-bilitis","claude-debussy","Chansons de Bilitis für zwei Flöten, zwei Harfen, Celesta und Sprecher",[],1900,1900,"chamber_music",13),
 "bach-matthaeus-passion": W("bach-matthaeus-passion","johann-sebastian-bach","Matthäus-Passion",[cat("BWV","244")],1727,1727,"oratorio",165),
 "wagner-wesendonck-ring-ohne-worte": W("wagner-wesendonck-ring-ohne-worte","richard-wagner","Der Ring ohne Worte (zusammengestellt von Lorin Maazel)",[],1987,1987,"other",70,version="nach Werken von 1848–1874"),
 "tschaikowsky-streichquartett-2": W("tschaikowsky-streichquartett-2","peter-iljitsch-tschaikowsky","Streichquartett Nr. 2 F-Dur",[cat("Opus","22")],1873,1874,"chamber_music",35),
 "brahms-streichquartett-op51-2": W("brahms-streichquartett-op51-2","johannes-brahms","Streichquartett a-Moll",[cat("Opus","51/2")],1873,1873,"chamber_music",34),
 "boccherini-fandango": W("boccherini-fandango","luigi-boccherini","Fandango aus dem Gitarrenquintett Nr. 4 D-Dur",[cat("G","448")],1788,1788,"chamber_music",8),
 "paganini-gitarrenquintett-2": W("paganini-gitarrenquintett-2","niccolo-paganini","Quintett für Gitarre und Streichtrio Nr. 2 C-Dur",[cat("MS","29")],1820,1820,"chamber_music",20),
 "castelnuovo-tedesco-gitarrenquintett": W("castelnuovo-tedesco-gitarrenquintett","mario-castelnuovo-tedesco","Quintett für Gitarre und Streichquartett",[cat("Opus","143")],1950,1950,"chamber_music",26),
 "henze-neue-volkslieder-hirtengesaenge": W("henze-neue-volkslieder-hirtengesaenge","hans-werner-henze","Neue Volkslieder und Hirtengesänge für Fagott, Gitarre und Streichtrio",[],1983,1996,"chamber_music",25),
 "groven-hjalar-ljod": W("groven-hjalar-ljod","eivind-groven","Hjalar-Ljod – Ouvertüre",[cat("Opus","38")],1950,1950,"overture",10),
 "grieg-klavierkonzert": W("grieg-klavierkonzert","edvard-grieg","Klavierkonzert a-Moll",[cat("Opus","16")],1868,1868,"concerto",30),
 "tschaikowsky-sinfonie-5": W("tschaikowsky-sinfonie-5","peter-iljitsch-tschaikowsky","Sinfonie Nr. 5 e-Moll",[cat("Opus","64")],1888,1888,"symphony",47),
 "pintscher-neues-werk-2027": W("pintscher-neues-werk-2027","matthias-pintscher","Neues Werk für Orchester",[],2027,2027,"other",None),
 "hindemith-violinkonzert": W("hindemith-violinkonzert","paul-hindemith","Konzert für Violine und Orchester",[],1939,1939,"concerto",27),
 "bartok-konzert-fuer-orchester": W("bartok-konzert-fuer-orchester","bela-bartok","Konzert für Orchester",[cat("Sz","116")],1943,1943,"other",38),
 "purcell-drei-fantasien": W("purcell-drei-fantasien","henry-purcell","Drei Fantasien für Violine, Viola und Violoncello",[],1680,1680,"chamber_music",10),
 "klein-streichtrio": W("klein-streichtrio","gideon-klein","Trio für Violine, Viola und Violoncello",[],1944,1944,"chamber_music",15),
 "nicolaou-ueberblendungen": W("nicolaou-ueberblendungen","vassos-nicolaou","Überblendungen für Streichtrio und zwei Schlagzeuger",[],2020,2020,"chamber_music",15),
 "beethoven-coriolan-ouvertuere": W("beethoven-coriolan-ouvertuere","ludwig-van-beethoven","Ouvertüre zu Coriolan",[cat("Opus","62")],1807,1807,"overture",8),
 "beethoven-klavierkonzert-3": W("beethoven-klavierkonzert-3","ludwig-van-beethoven","Konzert für Klavier und Orchester Nr. 3 c-Moll",[cat("Opus","37")],1800,1803,"concerto",35),
 "schumann-sinfonie-1-fruehling": W("schumann-sinfonie-1-fruehling","robert-schumann","Sinfonie Nr. 1 B-Dur »Frühlingssinfonie«",[cat("Opus","38")],1841,1841,"symphony",31),
 "weber-trio-floete-cello-klavier": W("weber-trio-floete-cello-klavier","carl-maria-von-weber","Trio für Flöte, Violoncello und Klavier g-Moll",[cat("Opus","63")],1818,1819,"chamber_music",23),
 "brahms-cellosonate-1": W("brahms-cellosonate-1","johannes-brahms","Sonate für Violoncello und Klavier e-Moll",[cat("Opus","38")],1862,1865,"chamber_music",27),
 "prokofjew-floetensonate": W("prokofjew-floetensonate","sergej-prokofjew","Sonate für Flöte und Klavier D-Dur",[cat("Opus","94")],1942,1943,"chamber_music",24),
 "kapustin-trio-op86": W("kapustin-trio-op86","nikolai-kapustin","Trio für Flöte, Violoncello und Klavier",[cat("Opus","86")],1998,1998,"chamber_music",16),
 "schumann-manfred-ouvertuere": W("schumann-manfred-ouvertuere","robert-schumann","Ouvertüre zu Manfred",[cat("Opus","115")],1848,1852,"overture",12),
 "schumann-cellokonzert": W("schumann-cellokonzert","robert-schumann","Konzert für Violoncello und Orchester a-Moll",[cat("Opus","129")],1850,1850,"concerto",25),
 "schumann-sinfonie-2": W("schumann-sinfonie-2","robert-schumann","Sinfonie Nr. 2 C-Dur",[cat("Opus","61")],1845,1846,"symphony",38),
 "rachmaninow-paganini-rhapsodie-orgel": W("rachmaninow-paganini-rhapsodie-orgel","sergej-rachmaninow","Rhapsodie über ein Thema von Paganini",[cat("Opus","43")],1934,1934,"concerto",24,version="Bearbeitung für Orgel und Orchester"),
 "mozart-klavierkonzert-15": W("mozart-klavierkonzert-15","wolfgang-amadeus-mozart","Konzert für Klavier und Orchester Nr. 15 B-Dur",[cat("KV","450")],1784,1784,"concerto",25),
}
NEW_WORKS = {k:v for k,v in NEW_WORKS.items() if v is not None}

# ---------- curation: program per event (slug -> ordered list of work ids) ----------
# Reused existing ids: saint-saens-sinfonie-3-orgel, rachmaninow-klavierkonzert-2,
# tschaikowsky-romeo-et-juliette, strauss-also-sprach-zarathustra,
# strauss-rosenkavalier-suite, brahms-sinfonie-1, bruckner-sinfonie-7, schubert-streichtrio-d581
PROGRAM = {
 "philharmonieprobe": [],
 "summertime": ["gershwin-amerikaner-in-paris","gershwin-porgy-and-bess-concert-of-songs"],
 "jubilaeumskonzert-koelner-philharmonie": ["mendelssohn-sinfonie-5-reformation","widmann-ad-absurdum","brahms-gesang-aus-fingal","strauss-also-sprach-zarathustra"],
 "female-voices-of-resilience": [],
 "happy-birthday": ["jockel-auftragswerk-2026","strawinsky-pulcinella-suite"],
 "zum-licht": ["brahms-schicksalslied","bernstein-chichester-psalms","brahms-sinfonie-1"],
 "entfernte-verwandte": ["gade-streichsextett","dohnanyi-streichsextett"],
 "ein-haydn-spass": ["haydn-le-matin"],
 "bock-auf-klassik-oktober": ["rachmaninow-klavierkonzert-2","prokofjew-sinfonie-6"],
 "auf-neuen-wegen": ["rachmaninow-klavierkonzert-2","prokofjew-sinfonie-6"],
 "delirium": ["schumann-manfred-ouvertuere","schumann-cellokonzert","schumann-sinfonie-2"],
 "rueckblenden": ["arensky-streichquartett-2","schubert-streichquintett-d956"],
 "kronberg-academy-26-27": ["bartok-violakonzert","haydn-cellokonzert-2","saint-saens-violinkonzert-3","strauss-rosenkavalier-suite"],
 "musikalischer-fruehschoppen-26-27": [],
 "schicksalsschlaege": ["mahler-sinfonie-6"],
 "das-geheimnis-der-weihnachtswichtel": [],
 "das-geheimnis-der-weihnachtswichtel-schulkonzerte": [],
 "lichterglanz": ["bach-orchestersuite-1","mozart-oboenkonzert-c-dur","schubert-sinfonie-7-unvollendete","berlioz-carnaval-romain"],
 "bock-auf-klassik-januar": ["mozart-sinfonie-40","mozart-requiem"],
 "mysterium": ["mozart-sinfonie-40","mozart-requiem"],
 "erloesung": ["bartok-wunderbarer-mandarin","wagner-parsifal-3-aufzug"],
 "love-and-loss": ["vaughan-williams-on-wenlock-edge","dunhill-klavierquartett","quilter-to-julia"],
 "feuer-und-eis": ["sibelius-finlandia","dvorak-cellokonzert","nielsen-sinfonie-5"],
 "heldinnen": [],
 "heldinnen-schulkonzerte": [],
 "schwippschwapp-wasser-marsch": [],
 "verfuehrerisch": ["berlioz-trio-jeunes-ismaelites","ibert-deux-interludes","saint-saens-fantaisie-violine-harfe","clarke-maya","debussy-chansons-de-bilitis"],
 "femme-fatale": ["berg-lulu"],
 "passion": ["bach-matthaeus-passion"],
 "suchtgefahr": ["wagner-wesendonck-ring-ohne-worte"],
 "pocket-symphonies": ["tschaikowsky-streichquartett-2","brahms-streichquartett-op51-2"],
 "saite-an-saite": ["boccherini-fandango","paganini-gitarrenquintett-2","castelnuovo-tedesco-gitarrenquintett","henze-neue-volkslieder-hirtengesaenge"],
 "aus-tiefster-seele": ["groven-hjalar-ljod","grieg-klavierkonzert","tschaikowsky-sinfonie-5"],
 "ab-ins-all": [],
 "buergerschreck": ["pintscher-neues-werk-2027","hindemith-violinkonzert","bartok-konzert-fuer-orchester"],
 "koelner-buergerorchester-2": [],
 "zeitspruenge": ["purcell-drei-fantasien","klein-streichtrio","nicolaou-ueberblendungen","schubert-streichtrio-d581"],
 "bock-auf-klassik-juni": ["tschaikowsky-romeo-et-juliette","rachmaninow-paganini-rhapsodie-orgel","saint-saens-sinfonie-3-orgel"],
 "alle-register": ["tschaikowsky-romeo-et-juliette","rachmaninow-paganini-rhapsodie-orgel","saint-saens-sinfonie-3-orgel"],
 "leuchtfeuer": ["beethoven-coriolan-ouvertuere","beethoven-klavierkonzert-3","schumann-sinfonie-1-fruehling"],
 "spielversprechend": ["weber-trio-floete-cello-klavier","brahms-cellosonate-1","prokofjew-floetensonate","kapustin-trio-op86"],
 "ellen-oder-es-wird-gut": [],
 "jso-meets-go": [],
 "bahnbrechend": ["mozart-klavierkonzert-15","bruckner-sinfonie-7"],
}

# extra description notes for events with generic/announced programmes
DESC_NOTES = {
 "philharmonieprobe": "Öffentliche Probe zum jeweiligen Konzertprogramm.",
 "female-voices-of-resilience": "Programm wird noch bekannt gegeben.",
 "musikalischer-fruehschoppen-26-27": "Matinee mit Musiker:innen des Gürzenich-Orchesters; Programm wird kurzfristig bekannt gegeben.",
 "das-geheimnis-der-weihnachtswichtel": "Mit Musik von Peter I. Tschaikowsky, Nikolaj Rimskij-Korsakow, Edvard Grieg, Camille Saint-Saëns und Armas Järnefelt.",
 "das-geheimnis-der-weihnachtswichtel-schulkonzerte": "Mit Musik von Peter I. Tschaikowsky, Nikolaj Rimskij-Korsakow, Edvard Grieg, Camille Saint-Saëns und Armas Järnefelt.",
 "heldinnen": "Programm wird zu einem späteren Zeitpunkt bekannt gegeben.",
 "heldinnen-schulkonzerte": "Programm sowie weitere Mitwirkende werden zu einem späteren Zeitpunkt bekannt gegeben.",
 "schwippschwapp-wasser-marsch": "Programm und Besetzung werden zu einem späteren Zeitpunkt bekannt gegeben.",
 "ab-ins-all": "Ein musikalisches Weltraum-Abenteuer mit Werken von Jules Massenet, Jean Françaix, Béla Bartók, Johannes Brahms, Philip Glass, Franz Schubert und Maddalena Lombardini Sirmen.",
 "koelner-buergerorchester-2": "Programm wird zu einem späteren Zeitpunkt bekannt gegeben.",
 "ellen-oder-es-wird-gut": "Chorprojekt »Singen mit Klasse!« mit Kölner Grundschulklassen.",
 "jso-meets-go": "Programm und Mitwirkende werden zu einem späteren Zeitpunkt bekannt gegeben.",
}

# ---------- curation: venues ----------
def V(vid,name,vtype,inst=None):
    return {"id":vid,"name":name,"cityIds":["koeln"],"region":None,"address":None,
            "coordinates":None,"website":None,"type":vtype,"institutionId":inst}
NEW_VENUES = [
 V("kammermusiksaal-kartaeuserwall-koeln","Kammermusiksaal am Kartäuserwall","concert_hall"),
 V("rheinische-musikschule-koeln","Rheinische Musikschule Köln","other"),
 V("buergerzentrum-engelshof-koeln","Bürgerzentrum Engelshof","other"),
 V("belgisches-haus-koeln","Belgisches Haus","other"),
]
def venue_id(raw):
    r=raw.lower()
    if "philharmonie" in r: return "koelner-philharmonie"
    if "kammermusiksaal" in r or "kartäuserwall" in r: return "kammermusiksaal-kartaeuserwall-koeln"
    if "musikschule" in r: return "rheinische-musikschule-koeln"
    if "engelshof" in r: return "buergerzentrum-engelshof-koeln"
    if "belgisches haus" in r: return "belgisches-haus-koeln"
    return None

# ---------- curation: cast roles ----------
CONDUCTOR_ROLE = re.compile(r"dirigent|leitung", re.I)
SKIP_ROLE = re.compile(r"moderation|künstlerische leitung|ko-moderation", re.I)
SKIP_NAME = re.compile(r"^(n\.n\.?|gürzenich-orchester|wdr sinfonieorchester|kölner bürgerchor|"
                       r"kölner bürgerorchester|a song for you|amsterdam baroque choir|"
                       r"chor der oper köln|wiener singverein|chorwerk ruhr|inner unity ensemble|"
                       r"projektchor|knaben des kölner|solist des tölzer|orchesterakademie|"
                       r"das gürzenich-orchester|kölner schüler|12 kölner|"
                       r"weltraumforscherin)", re.I)
INSTRUMENT_HINT = re.compile(r"sopran|mezzo|alt\b|tenor|bariton|bass|gesang|klavier|violine|viola|"
    r"violoncello|cello|kontrabass|flöte|oboe|klarinette|fagott|horn|trompete|posaune|orgel|"
    r"harfe|gitarre|schlagzeug|celesta|oud|santur|kamancheh|drehorgel|blockflöte|sprecher|speaker", re.I)

def role_kind(role, name):
    """Return 'conductor', 'soloist', 'both', or None."""
    if SKIP_NAME.match(name.strip()):
        return None
    r = role.strip()
    if not r:
        return None
    if SKIP_ROLE.search(r):          # moderation / künstlerische Leitung / ko-moderation
        return None
    is_cond = bool(CONDUCTOR_ROLE.search(r))
    is_solo = bool(INSTRUMENT_HINT.search(r))
    if is_cond and is_solo:
        return "both"          # e.g. "Oboe und Leitung"
    if is_cond:
        return "conductor"
    if is_solo:
        return "soloist"
    return None

# ---------- run ----------
if ARGS.raw:
    season = json.load(open(ARGS.raw, encoding="utf-8"))
else:
    season = scrape_season()

people = load("people"); composers = load("composers"); works = load("works")
venues = load("venues"); cities = load("cities"); events = load("events")

people_by_id = {p["id"]: p for p in people["people"]}
people_id_by_name = {p["name"].strip().lower(): p["id"] for p in people["people"]}
comp_ids = {c["id"] for c in composers["composers"]}
work_ids = {w["id"] for w in works["works"]}
venue_ids = {v["id"] for v in venues["venues"]}

used_people=set(); used_works=set(); used_composers=set(); used_venues=set()

def ensure_person(name):
    name = re.sub(r"\s+"," ",name).strip()
    if not name: return None
    key = name.lower()
    if key in people_id_by_name:
        pid = people_id_by_name[key]
    else:
        pid = fold(name); base=pid; i=2
        while pid in people_by_id and people_by_id[pid]["name"].strip().lower()!=key:
            pid=f"{base}-{i}"; i+=1
        if pid not in people_by_id:
            rec={"id":pid,"name":name}
            people["people"].append(rec); people_by_id[pid]=rec; people_id_by_name[key]=pid
    used_people.add(pid); return pid

# add master venues
for v in NEW_VENUES:
    if v["id"] not in venue_ids:
        venues["venues"].append(v); venue_ids.add(v["id"])

def add_work(wid):
    if wid in work_ids:
        used_works.add(wid)
        # track composer of existing work
        for w in works["works"]:
            if w["id"]==wid: used_composers.add(w["composerId"]); break
        return wid
    rec = NEW_WORKS.get(wid)
    if not rec:
        print("!! UNKNOWN WORK ID:", wid, file=sys.stderr); return None
    works["works"].append(rec); work_ids.add(wid)
    used_works.add(wid); used_composers.add(rec["composerId"])
    return wid

MONTHS_GUARD=True

# remove previously ingested Gürzenich events
before=len(events["events"])
events["events"]=[e for e in events["events"]
                  if SRC_HOST not in ((e.get("source") or {}).get("url","") or "")]
removed=before-len(events["events"])

existing_ids={e["id"] for e in events["events"]}
new_events=[]

OPERA_SLUGS=set()  # Femme fatale is a concertante performance in the Sinfoniekonzert series

for e in season:
    slug=e["slug"]; title=e["title"]; category=e["category"]
    # conductors / soloists from cast
    conductors=[]; soloists=[]
    for c in e["cast"]:
        kind=role_kind(c.get("role",""), c.get("name",""))
        if not kind: continue
        pid=ensure_person(c["name"])
        if not pid: continue
        if kind in ("conductor","both") and pid not in conductors: conductors.append(pid)
        if kind in ("soloist","both") and pid not in soloists: soloists.append(pid)
    # program
    prog=[]
    for wid in PROGRAM.get(slug, []):
        rid=add_work(wid)
        if rid: prog.append({"workId":rid})
    # description
    parts=[]
    if category: parts.append(category+".")
    if slug in DESC_NOTES: parts.append(DESC_NOTES[slug])
    description=" ".join(parts) if parts else None
    etype="opera" if slug in OPERA_SLUGS else "concert"
    # one event per performance
    for perf in e["performances"]:
        date=perf.get("date"); start=perf.get("startTime")
        if not date: continue
        vid=venue_id(perf.get("venue",""))
        if not vid:
            print("!! UNMAPPED VENUE:", perf.get("venue"), file=sys.stderr); continue
        used_venues.add(vid)
        base=f"event-{date}-koeln-{fold(title)}"
        eid=base
        if eid in existing_ids and start:
            eid=f"{base}-{start.replace(':','')}"
        i=2
        while eid in existing_ids:
            eid=f"{base}-{i}"; i+=1
        existing_ids.add(eid)
        new_events.append({
            "id":eid,"title":title,"eventType":etype,"date":date,"startTime":start,
            "endTime":None,"status":"scheduled","ensembleIds":[ENSEMBLE_ID],
            "venueId":vid,"cityId":"koeln","conductorPersonIds":list(conductors),
            "soloistPersonIds":list(soloists),"program":list(prog),"seriesId":None,
            "description":description,
            "source":{"url":f"https://www.{SRC_HOST}/de/event-detail/{slug}","calendarUrl":CALENDAR_URL,"name":SRC_NAME,"retrievedAt":TODAY},
            "ticketUrl":perf.get("ticket"),"lastVerified":TODAY,
        })

new_events.sort(key=lambda e:(e["date"], e["startTime"] or "", e["id"]))
events["events"].extend(new_events)

# append new composers referenced
for cid in sorted(used_composers):
    if cid not in comp_ids:
        if cid in NEW_COMPOSERS:
            nm,fr,to=NEW_COMPOSERS[cid]
            composers["composers"].append({"id":cid,"name":nm,"life":{"from":fr,"to":to}})
            comp_ids.add(cid)
        else:
            print("!! MISSING COMPOSER RECORD:", cid, file=sys.stderr)

for obj in (people,composers,works,venues,cities,events):
    obj.setdefault("metadata",{})["lastUpdated"]=TODAY
events["metadata"]["notes"]=("Enthält recherchierte Konzerte des WDR Sinfonieorchesters "
  "(Kölner Philharmonie), der Bergischen Symphoniker (bergischesymphoniker.de) und des "
  "Gürzenich-Orchesters Köln (guerzenich-orchester.de), Spielzeit 2026/27, sowie einige "
  "frühere Beispieldatensätze (Quellen mit example.org).")

save("people",people); save("composers",composers); save("works",works)
save("venues",venues); save("cities",cities); save("events",events)

print(f"Removed prior Gürzenich events: {removed}")
print(f"New events: {len(new_events)} (total now {len(events['events'])})")
print(f"People used: {len(used_people)}; total {len(people['people'])}")
print(f"Works used: {len(used_works)}; total {len(works['works'])}")
print(f"Composers used: {len(used_composers)}; total {len(composers['composers'])}")
print(f"Venues used: {len(used_venues)}; total {len(venues['venues'])}")
