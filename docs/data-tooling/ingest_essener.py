#!/usr/bin/env python3
"""
Ingest script for Essener Philharmoniker 2026/27 season.

Source: https://www.theater-essen.de/programm/spielzeit-26-27/

This script:
1. Fetches all events from the Essener Philharmoniker season 2026/27
2. Parses HTML to extract dates, times, venues, cast, program
3. Filters for Essener Philharmoniker performances
4. Enriches with composer/work metadata
5. Merges with existing data/events.json, data/people.json, etc.
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from collections import defaultdict
from html import unescape

# Constants
BASE_URL = "https://www.theater-essen.de"
SEASON_URL = f"{BASE_URL}/programm/spielzeit-26-27/"
ENSEMBLE_ID = "essener-philharmoniker"

# Season window: 2026/27 season = Sept 2026 to August 2027
SEASON_START = datetime(2026, 8, 1)
SEASON_END = datetime(2027, 8, 31)

# Known venues
VENUES_MAP = {
    "Philharmonie Essen": "philharmonie-essen",
    "Philharmonie-Essen": "philharmonie-essen",
    "Gruga-Saal": "gruga-saal-essen",
    "Licht-Hof": "licht-hof-essen",
    "Bethanien": "bethanien-essen",
    "Aalto Musiktheater": "aalto-musiktheater-essen",
}

# Roles: conductor/soloist mapping
CONDUCTOR_ROLES = {"Dirigent", "Leitung", "Künstlerische Leitung", "conductor"}
SOLOIST_KEYWORDS = {"Sopran", "Alt", "Tenor", "Bass", "Violine", "Viola", "Violoncello", "Cello", 
                    "Klavier", "Orgel", "Flöte", "Oboe", "Klarinette", "Fagott", "Horn", "Trompete",
                    "Posaune", "Tuba", "Harfe", "Gitarre", "Vokal", "vocal", "solo"}
SKIP_PERSON_KEYWORDS = {
    "philharmoniker", "orchester", "ballett", "chor", "ensemble", "compagnie", "company", "musiktheater",
}

# Program mapping: slug -> structured program items.
PROGRAM = {
    "bruckner-3-153256": [
        {"workId": "wagner-siegfried-idyll"},
        {"workId": "bruckner-sinfonie-3", "version": "3. Fassung"},
    ],
    "eroica-153285": [
        {"workId": "brahms-tragische-ouvertuere"},
        {"workId": "britten-violinkonzert-d-moll"},
        {"workId": "beethoven-sinfonie-3-eroica"},
    ],
}

# New composers to add
NEW_COMPOSERS = {
    "benjamin-britten": {
        "id": "benjamin-britten",
        "name": "Benjamin Britten",
        "life": {"from": 1913, "to": 1976},
    },
}

# New works to add
NEW_WORKS = {
    "bruckner-sinfonie-3": {
        "id": "bruckner-sinfonie-3",
        "composerId": "anton-bruckner",
        "title": "Sinfonie Nr. 3 d-Moll",
        "catalogue": [],
        "yearComposed": {"from": 1873, "to": 1889},
        "genre": "symphony",
        "durationMinutes": None,
        "version": None,
        "scoring": None,
        "description": None,
    },
    "brahms-tragische-ouvertuere": {
        "id": "brahms-tragische-ouvertuere",
        "composerId": "johannes-brahms",
        "title": "Tragische Ouvertüre d-Moll",
        "catalogue": [{"system": "Opus", "number": "81"}],
        "yearComposed": {"from": 1880, "to": 1880},
        "genre": "overture",
        "durationMinutes": 14,
        "version": None,
        "scoring": None,
        "description": None,
    },
    "britten-violinkonzert-d-moll": {
        "id": "britten-violinkonzert-d-moll",
        "composerId": "benjamin-britten",
        "title": "Violinkonzert d-Moll",
        "catalogue": [{"system": "Opus", "number": "15"}],
        "yearComposed": {"from": 1938, "to": 1939},
        "genre": "concerto",
        "durationMinutes": 32,
        "version": None,
        "scoring": None,
        "description": None,
    },
    "beethoven-sinfonie-3-eroica": {
        "id": "beethoven-sinfonie-3-eroica",
        "composerId": "ludwig-van-beethoven",
        "title": "Sinfonie Nr. 3 Es-Dur »Eroica«",
        "catalogue": [{"system": "Opus", "number": "55"}],
        "yearComposed": {"from": 1802, "to": 1804},
        "genre": "symphony",
        "durationMinutes": 48,
        "version": None,
        "scoring": None,
        "description": None,
    },
}

def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch URL and return HTML content."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {url}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_events(html: str) -> Dict[str, Dict[str, Any]]:
    """Extract event slugs and titles from season listing page."""
    events = {}
    
    # Pattern: href="/programm/spielzeit-26-27/{slug}/" ... title text
    event_links = re.findall(
        r'href="(/programm/spielzeit-26-27/([^/]+)/)"[^>]*>([^<]*)</a>',
        html
    )
    
    for href, slug, title in event_links:
        title = unescape(title).strip()
        if not title:
            continue
        
        if slug not in events:
            events[slug] = {
                'slug': slug,
                'url': f"{BASE_URL}{href}",
                'title': title,
            }
    
    return events


def parse_date_string(date_str: str, year: int = 2026) -> Optional[str]:
    """Parse German date string to ISO format (YYYY-MM-DD)."""
    if not date_str:
        return None
    
    months = {
        'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6,
        'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Dezember': 12
    }
    
    # Try pattern: "1. September 2026" or "1. September"
    # Use explicit character class for German umlauts
    match = re.search(r'(\d{1,2})\.\s+([A-Za-zäöüßÄÖÜ]+)\s+(\d{4})?', date_str)
    if match:
        day, month_str, year_str = match.groups()
        month = months.get(month_str)
        if month:
            year = int(year_str) if year_str else year
            try:
                dt = datetime(year, month, int(day))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None
    
    return None


def parse_time_string(time_str: str) -> Optional[str]:
    """Parse German time string to HH:MM format."""
    if not time_str:
        return None
    
    # Pattern: "20:00 Uhr" or "20:00" or "20.00"
    match = re.search(r'(\d{1,2})[:\.](\d{2})', time_str)
    if match:
        hour, minute = match.groups()
        return f"{hour:>02}.{minute}"
    
    return None


def extract_meta_description(event_html: str) -> str:
    """Extract the HTML meta description content."""
    match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', event_html, re.IGNORECASE)
    return unescape(match.group(1)).strip() if match else ""


def extract_richtext_description(event_html: str) -> str:
    """Extract the long-form richtext body for an event detail page."""
    match = re.search(
        r'<div class="page-outer page-outer--richtext --margintop-none --marginbottom-xxlarge">(.*?)</div>\s*</div>',
        event_html,
        re.DOTALL,
    )
    if not match:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', match.group(1))
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', unescape(text)).strip()


def extract_performances(event_html: str, slug: str) -> List[Dict[str, Any]]:
    """Extract performance data from event detail page."""
    performances = []

    # Extract venue
    venue_id = "philharmonie-essen"  # Default
    for venue_pattern, venue_id_mapped in VENUES_MAP.items():
        if venue_pattern.lower() in event_html.lower():
            venue_id = venue_id_mapped
            break
    
    # Extract program/works and cast from meta description first.
    program_text = ""
    cast_text = ""
    meta_description = extract_meta_description(event_html)
    richtext_description = extract_richtext_description(event_html)
    if meta_description:
        head, sep, tail = meta_description.partition("Besetzung:")
        head = head.strip(" ,")
        if ", Werke von " in head:
            program_text = f"Werke von {head.split(', Werke von ', 1)[1].strip(' ,')}"
        elif ", Musik von " in head:
            program_text = f"Musik von {head.split(', Musik von ', 1)[1].strip(' ,')}"
        elif head.startswith("Werke von ") or head.startswith("Musik von "):
            program_text = head

        if sep:
            cast_text = tail.strip(" ,")

    if not program_text:
        program_match = re.search(
            r'(?:Werke von|Musik von|Komposition)[:—\s]+([^<]{20,500})',
            event_html, re.IGNORECASE
        )
        if program_match:
            program_text = unescape(program_match.group(1).strip())

    if not cast_text:
        cast_match = re.search(r'Besetzung[:—\s]+([^<]{20,500})', event_html)
        if cast_match:
            cast_text = unescape(cast_match.group(1).strip())

    # Prefer the explicit next-performance blocks; they contain accurate start/end times.
    block_pattern = re.compile(
        r'<div class="nextperformance__date">([^<]+)</div>.*?'
        r'<div class="nextperformance__time[^"]*[^>]*>.*?'
        r'<meta itemprop="startDate" content="([^"]+)">([^<]*)</div>',
        re.DOTALL,
    )
    blocks = block_pattern.findall(event_html)
    if blocks:
        for date_text, start_iso, time_text in blocks:
            start = start_iso.strip()
            date = start[:10]
            start_time = start[11:16] if len(start) >= 16 else None
            end_time = None
            time_match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', unescape(time_text))
            if time_match:
                start_time = time_match.group(1)
                end_time = time_match.group(2)

            try:
                dt = datetime.fromisoformat(date)
                if SEASON_START <= dt <= SEASON_END:
                    performances.append({
                        'date': date,
                        'time': start_time or '20:00',
                        'end_time': end_time,
                        'venue': venue_id,
                        'program': program_text,
                        'description': richtext_description or program_text,
                        'cast': cast_text,
                    })
            except ValueError:
                continue
        return performances

    # Fallback: extract dates from German format patterns like "Donnerstag 17. September 2026"
    date_pattern = r'(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)?\s*(\d{1,2})\.\s+(September|Oktober|November|Dezember|Januar|Februar|März|April|Mai|Juni|Juli|August)\s+(202[67])'
    dates = []
    for match in re.finditer(date_pattern, event_html):
        day, month, year = match.groups()
        iso_date = parse_date_string(f"{day}. {month} {year}")
        if iso_date:
            dates.append(iso_date)
    dates = list(dict.fromkeys(dates))
    time_matches = re.findall(r'(\d{2}):(\d{2})', event_html)
    times = [f"{h}:{m}" for h, m in time_matches] if time_matches else ["20:00"]
    for i, date in enumerate(dates):
        try:
            dt = datetime.fromisoformat(date)
            if SEASON_START <= dt <= SEASON_END:
                performances.append({
                    'date': date,
                    'time': times[i % len(times)],
                    'end_time': None,
                    'venue': venue_id,
                    'program': program_text,
                    'description': richtext_description or program_text,
                    'cast': cast_text,
                })
        except ValueError:
            continue
    
    return performances


def fold_name(name: str) -> str:
    """Fold German diacritics to ASCII for ID generation."""
    mapping = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE',
    }
    for char, replacement in mapping.items():
        name = name.replace(char, replacement)
    # Remove remaining non-ASCII
    return ''.join(c for c in name if ord(c) < 128)


def extract_persons_from_cast(cast_text: str) -> Tuple[List[str], List[str]]:
    """Extract conductor and soloist names from cast text."""
    conductors = []
    soloists = []
    
    if not cast_text:
        return conductors, soloists
    
    # Split by comma or newline
    parts = re.split(r'[,\n]', cast_text)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check if it's a conductor role
        is_conductor = any(role in part for role in CONDUCTOR_ROLES)
        
        # Try to extract person name (usually before the role)
        # Pattern: "Name, Rolle" or "Rolle: Name"
        name_match = re.search(r'^([A-ZÄÖÜa-zäöß\s\-\.]+?)(?:\s*(?:,|—|–)|\s+(?:Dirigent|Leitung))', part)
        if not name_match:
            name_match = re.search(r':\s*([A-ZÄÖÜa-zäöß\s\-\.]+)', part)
        
        if name_match:
            name = name_match.group(1).strip()
            if name and len(name) > 2:
                if is_conductor:
                    conductors.append(name)
                else:
                    soloists.append(name)
    
    return conductors, soloists


def ensure_person(name: str, people: Dict[str, Any], people_by_id: Dict[str, Dict[str, str]],
                  people_id_by_name: Dict[str, str]) -> Optional[str]:
    """Create or reuse a person record and return its ID."""
    clean_name = re.sub(r"\s+", " ", name).strip(" ,;:")
    if not clean_name:
        return None
    lower_name = clean_name.lower()
    if any(keyword in lower_name for keyword in SKIP_PERSON_KEYWORDS):
        return None

    key = lower_name
    if key in people_id_by_name:
        return people_id_by_name[key]

    person_id = fold_name(clean_name).lower().replace(' ', '-')
    base = person_id
    suffix = 2
    while person_id in people_by_id and people_by_id[person_id]['name'].strip().lower() != key:
        person_id = f"{base}-{suffix}"
        suffix += 1

    if person_id not in people_by_id:
        record = {'id': person_id, 'name': clean_name}
        people['people'].append(record)
        people_by_id[person_id] = record
        people_id_by_name[key] = person_id

    return person_id


def ensure_composer(composer_id: str, composers: Dict[str, Any], composer_ids: set[str]) -> Optional[str]:
    """Create or reuse a composer record and return its ID."""
    if composer_id in composer_ids:
        return composer_id
    record = NEW_COMPOSERS.get(composer_id)
    if not record:
        return None
    composers['composers'].append(record)
    composer_ids.add(composer_id)
    return composer_id


def ensure_work(work_id: str, works: Dict[str, Any], work_ids: set[str], composers: Dict[str, Any],
                composer_ids: set[str]) -> Optional[str]:
    """Create or reuse a work record and return its ID."""
    if work_id in work_ids:
        return work_id
    record = NEW_WORKS.get(work_id)
    if not record:
        return None
    if not ensure_composer(record['composerId'], composers, composer_ids):
        return None
    works['works'].append(record)
    work_ids.add(work_id)
    return work_id


def generate_event_id(date: str, city: str, title: str) -> str:
    """Generate consistent event ID."""
    # Format: event-YYYY-MM-DD-city-short
    date_part = date.replace('-', '')  # YYYYMMDD
    title_part = title.lower().replace(' ', '-')[:20]
    return f"event-{date}-{city.lower()}-{title_part}"


def load_existing_data(repo_root: Path) -> Tuple[List, List, List, List, List]:
    """Load existing data files."""
    events_file = repo_root / 'data' / 'events.json'
    people_file = repo_root / 'data' / 'people.json'
    works_file = repo_root / 'data' / 'works.json'
    composers_file = repo_root / 'data' / 'composers.json'
    venues_file = repo_root / 'data' / 'venues.json'
    
    # Load events with metadata wrapper
    events_data = json.loads(events_file.read_text()) if events_file.exists() else {}
    events = events_data.get('events', []) if isinstance(events_data, dict) else []
    
    people = json.loads(people_file.read_text()) if people_file.exists() else {}
    works = json.loads(works_file.read_text()) if works_file.exists() else {}
    composers = json.loads(composers_file.read_text()) if composers_file.exists() else {}
    venues = json.loads(venues_file.read_text()) if venues_file.exists() else {}
    
    return events, people, works, composers, venues


def save_data(repo_root: Path, events: List, people: Dict, works: Dict, composers: Dict, venues: Dict):
    """Save updated data files."""
    # Wrap events with metadata
    events_wrapper = {
        'metadata': {
            'version': '1.1',
            'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
            'season': '2026/27',
            'language': 'de'
        },
        'events': events
    }
    
    (repo_root / 'data' / 'events.json').write_text(json.dumps(events_wrapper, indent=2, ensure_ascii=False))
    (repo_root / 'data' / 'people.json').write_text(json.dumps(people, indent=2, ensure_ascii=False))
    (repo_root / 'data' / 'works.json').write_text(json.dumps(works, indent=2, ensure_ascii=False))
    (repo_root / 'data' / 'composers.json').write_text(json.dumps(composers, indent=2, ensure_ascii=False))
    (repo_root / 'data' / 'venues.json').write_text(json.dumps(venues, indent=2, ensure_ascii=False))


def main():
    """Main ingest routine."""
    repo_root = Path(__file__).parent.parent.parent
    
    print("=== Essener Philharmoniker Ingest ===\n")
    
    # Fetch season page
    print("1. Fetching season listing...")
    season_html = fetch_url(SEASON_URL)
    if not season_html:
        print("Failed to fetch season page")
        return 1
    
    # Extract event links
    events_dict = extract_events(season_html)
    print(f"   Found {len(events_dict)} unique events")
    
    # Filter for Essener Philharmoniker events
    # The TUP site has many different ensembles. We need to filter for "Essener Philharmoniker" events
    print(f"\n2. Fetching and parsing event detail pages...")
    
    essener_events = {}
    all_performances = []
    
    # Batch fetch to find Essener Philharmoniker events
    for i, (slug, event_info) in enumerate(events_dict.items()):
        if (i + 1) % 20 == 0:
            print(f"   [{i+1}/{len(events_dict)}] Scanned {i+1} events, found {len(essener_events)} Essener Philharmoniker events...")
        
        event_html = fetch_url(event_info['url'])
        if not event_html:
            continue
        
        # Check if this is an Essener Philharmoniker event
        # Look for "Essener Philharmoniker" text or related keywords
        if 'Essener Philharmoniker' not in event_html:
            continue
        
        essener_events[slug] = event_info
        
        # Extract performances
        performances = extract_performances(event_html, slug)
        
        for perf in performances:
            perf['slug'] = slug
            perf['title'] = event_info['title']
            perf['url'] = event_info['url']
            all_performances.append(perf)
    
    print(f"\n   Found {len(essener_events)} Essener Philharmoniker events")
    print(f"   Extracted {len(all_performances)} performances total")
    
    # Load existing data
    print(f"\n3. Loading existing data...")
    events, people, works, composers, venues = load_existing_data(repo_root)
    print(f"   Existing events: {len(events)}")
    existing_work_ids = {work['id'] for work in works.get('works', [])}
    composer_ids = {composer['id'] for composer in composers.get('composers', [])}
    people_by_id = {person['id']: person for person in people.get('people', [])}
    people_id_by_name = {person['name'].strip().lower(): person['id'] for person in people.get('people', [])}
    
    # Remove old Essener events (idempotent)
    old_count = len(events)
    events = [
        e for e in events
        if e.get('source', {}).get('url', '').startswith(BASE_URL) is False
        or ENSEMBLE_ID not in e.get('ensembleIds', [])
    ]
    print(f"   Removed {old_count - len(events)} old Essener events")
    
    # Merge new performances
    print(f"\n4. Adding new performances...")
    new_event_count = 0
    for perf in all_performances:
        event_id = generate_event_id(perf['date'], 'essen', perf['title'])
        
        # Check if event already exists
        if any(e['id'] == event_id for e in events):
            continue
        
        # Build event
        event = {
            'id': event_id,
            'title': perf['title'],
            'eventType': 'concert',
            'date': perf['date'],
            'startTime': perf.get('time', '20:00'),
            'endTime': perf.get('end_time'),
            'status': 'scheduled',
            'ensembleIds': [ENSEMBLE_ID],
            'venueId': perf.get('venue', 'philharmonie-essen'),
            'cityId': 'essen',
            'conductorPersonIds': [],
            'soloistPersonIds': [],
            'program': [],
            'seriesId': None,
            'description': perf.get('description') or perf.get('program') or None,
            'source': {
                'url': perf['url'],
                'name': 'Theater und Philharmonie Essen',
                'retrievedAt': datetime.now().strftime('%Y-%m-%d'),
            },
            'ticketUrl': None,
            'lastVerified': datetime.now().strftime('%Y-%m-%d'),
        }
        
        # Add program works if mapped
        if perf['slug'] in PROGRAM:
            program_items = []
            for item in PROGRAM[perf['slug']]:
                work_id = ensure_work(item['workId'], works, existing_work_ids, composers, composer_ids)
                if not work_id:
                    continue
                program_item = {'workId': work_id}
                if item.get('version'):
                    program_item['version'] = item['version']
                program_items.append(program_item)
            event['program'] = program_items
        
        # Add cast
        conductor_names, soloist_names = extract_persons_from_cast(perf.get('cast', ''))
        event['conductorPersonIds'] = [
            pid for pid in (ensure_person(name, people, people_by_id, people_id_by_name) for name in conductor_names) if pid
        ]
        event['soloistPersonIds'] = [
            pid for pid in (ensure_person(name, people, people_by_id, people_id_by_name) for name in soloist_names) if pid
        ]
        
        events.append(event)
        new_event_count += 1
    
    print(f"   Added {new_event_count} new events")
    
    # Save updated data
    print(f"\n5. Saving updated data...")
    save_data(repo_root, events, people, works, composers, venues)
    print(f"   Saved to data/events.json")
    
    print(f"\n✓ Ingest complete: {new_event_count} new Essener Philharmoniker events")
    return 0


if __name__ == '__main__':
    sys.exit(main())
