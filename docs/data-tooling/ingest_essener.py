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

# Program mapping: slug -> [(work_id, notes)]
PROGRAM = {
    # Hören Sie die Neugierde: Größe Sinfonische Konzerte
    "hoehner-classic-160438": [("work-schumann-symphony-3", "")],
    
    # Don Giovanni (Oper)
    "don-giovanni": [("work-mozart-don-giovanni", "")],
    
    # Bruckner 3
    "bruckner-3-153256": [("work-bruckner-symphony-3", ""), ("work-wagner-rienzi-overture", "")],
    
    # Weitere Produktionen - wird mit generischer Beschreibung markiert
}

# New composers to add
NEW_COMPOSERS = {}

# New works to add
NEW_WORKS = {}

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


def extract_performances(event_html: str, slug: str) -> List[Dict[str, Any]]:
    """Extract performance data from event detail page."""
    performances = []
    
    # Extract dates from German format patterns like "Donnerstag 17. September 2026"
    date_pattern = r'(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)?\s*(\d{1,2})\.\s+(September|Oktober|November|Dezember|Januar|Februar|März|April|Mai|Juni|Juli|August)\s+(202[67])'
    date_matches = re.finditer(date_pattern, event_html)
    
    dates = []
    for match in date_matches:
        day, month, year = match.groups()
        iso_date = parse_date_string(f"{day}. {month} {year}")
        if iso_date:
            dates.append(iso_date)
    
    # Remove duplicates while preserving order
    dates = list(dict.fromkeys(dates))
    
    # Extract times from "HH:MM" pattern
    time_matches = re.findall(r'(\d{2}):(\d{2})', event_html)
    times = [f"{h}:{m}" for h, m in time_matches] if time_matches else ["20:00"]
    
    # Extract venue
    venue_id = "philharmonie-essen"  # Default
    for venue_pattern, venue_id_mapped in VENUES_MAP.items():
        if venue_pattern.lower() in event_html.lower():
            venue_id = venue_id_mapped
            break
    
    # Extract program/works
    program_text = ""
    program_match = re.search(
        r'(?:Werke von|Musik von|Komposition)[:—\s]+([^<]{20,500})',
        event_html, re.IGNORECASE
    )
    if program_match:
        program_text = unescape(program_match.group(1).strip())
    
    # Extract cast
    cast_text = ""
    cast_match = re.search(r'Besetzung[:—\s]+([^<]{20,500})', event_html)
    if cast_match:
        cast_text = unescape(cast_match.group(1).strip())
    
    # Create performances from dates
    # Each date gets paired with a time (round-robin if there are multiple times)
    if dates:
        for i, date in enumerate(dates):
            time = times[i % len(times)]  # Cycle through available times
            try:
                dt = datetime.fromisoformat(date)
                if SEASON_START <= dt <= SEASON_END:
                    performance = {
                        'date': date,
                        'time': time,
                        'venue': venue_id,
                        'program': program_text,
                        'cast': cast_text,
                    }
                    performances.append(performance)
            except:
                pass
    
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
    """Extract conductor and soloist person IDs from cast text."""
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
                person_id = f"person-{fold_name(name).lower().replace(' ', '-')}"
                
                if is_conductor:
                    conductors.append(person_id)
                else:
                    soloists.append(person_id)
    
    return conductors, soloists


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
            'endTime': None,
            'status': 'scheduled',
            'ensembleIds': [ENSEMBLE_ID],
            'venueId': perf.get('venue', 'venue-philharmonie-essen'),
            'cityId': 'city-essen',
            'program': [],
            'source': {
                'url': perf['url'],
                'fetched': datetime.now().isoformat()
            }
        }
        
        # Add program works if mapped
        if perf['slug'] in PROGRAM:
            event['program'] = [
                {'workId': wid, 'notes': notes}
                for wid, notes in PROGRAM[perf['slug']]
            ]
        
        # Add cast
        conductors, soloists = extract_persons_from_cast(perf.get('cast', ''))
        if conductors:
            event['conductorPersonIds'] = conductors
        if soloists:
            event['soloistPersonIds'] = soloists
        
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
