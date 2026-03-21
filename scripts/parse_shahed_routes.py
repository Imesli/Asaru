#!/usr/bin/env python3
"""Parse ShahedTracker tweet text into Asaru route_trace schema.

Usage:
  1. Copy tweet text from @ShahedTracker into a text file (one tweet per block, separated by blank lines)
  2. Run: python3 parse_shahed_routes.py tweets.txt output_routes.json

The parser looks for route patterns like:
  "Mykolaiv > Kirovohrad > Cherkasy > Kyiv"
  "Odesa → Vinnytsia → Khmelnytskyi"

It also extracts:
  - Launch sites from "launched from X, Y, Z"
  - Totals from "A total of N Shahed type UAVs were launched"
  - Interception data from "N UAVs were claimed destroyed"
  - Regional breakdowns from "20 in Sumy, 19 in Odesa"

You can also paste tweet text directly to stdin:
  echo "Mykolaiv > Kirovohrad > Kyiv" | python3 parse_shahed_routes.py
"""

import json
import re
import sys
from datetime import datetime

# Geocoding for Ukrainian cities/oblasts
CITY_COORDS = {
    "Mykolaiv": (46.97, 32.00),
    "Kirovohrad": (48.51, 32.26),
    "Kropyvnytskyi": (48.51, 32.26),
    "Cherkasy": (49.44, 32.06),
    "Kyiv": (50.45, 30.52),
    "Vinnytsia": (49.23, 28.47),
    "Khmelnytskyi": (49.42, 26.99),
    "Zhytomyr": (50.25, 28.66),
    "Odesa": (46.48, 30.73),
    "Kherson": (46.64, 32.62),
    "Kharkiv": (49.99, 36.23),
    "Dnipro": (48.46, 35.05),
    "Zaporizhzhia": (47.84, 35.14),
    "Poltava": (49.59, 34.55),
    "Sumy": (50.91, 34.80),
    "Chernihiv": (51.50, 31.30),
    "Lviv": (49.84, 24.03),
    "Rivne": (50.62, 26.25),
    "Ternopil": (49.55, 25.59),
    "Ivano-Frankivsk": (48.92, 24.71),
    "Uman": (48.75, 30.22),
    "Bila Tserkva": (49.80, 30.11),
    "Starokostyantyniv": (49.76, 27.22),
    "Chernivtsi": (48.29, 25.94),
    "Lutsk": (50.75, 25.34),
    # Launch sites
    "Primorsko-Akhtarsk": (46.05, 38.17),
    "Millerovo": (48.92, 40.39),
    "Kursk": (51.73, 36.19),
    "Bryansk": (53.25, 34.37),
    "Oryol": (52.97, 36.06),
    "Shatalovo": (54.02, 32.44),
    "Navlya": (52.84, 34.51),
    "Yeysk": (46.71, 38.27),
    "Crimea": (45.35, 34.50),
    "Hvardiiske": (45.11, 34.05),
    "Chauda": (45.01, 35.83),
}

# Also match oblast names to city coords
OBLAST_TO_CITY = {
    "Mykolaiv oblast": "Mykolaiv",
    "Kirovohrad oblast": "Kirovohrad",
    "Cherkasy oblast": "Cherkasy",
    "Kyiv oblast": "Kyiv",
    "Vinnytsia oblast": "Vinnytsia",
    "Khmelnytskyi oblast": "Khmelnytskyi",
    "Zhytomyr oblast": "Zhytomyr",
    "Odesa oblast": "Odesa",
    "Kherson oblast": "Kherson",
    "Kharkiv oblast": "Kharkiv",
    "Dnipropetrovsk oblast": "Dnipro",
    "Zaporizhzhia oblast": "Zaporizhzhia",
    "Poltava oblast": "Poltava",
    "Sumy oblast": "Sumy",
    "Chernihiv oblast": "Chernihiv",
    "Lviv oblast": "Lviv",
    "Rivne oblast": "Rivne",
    "Ternopil oblast": "Ternopil",
    "Ivano-Frankivsk oblast": "Ivano-Frankivsk",
}


def parse_route_string(route_str):
    """Parse 'Mykolaiv > Kirovohrad > Kyiv' into waypoints."""
    # Split on > or → or >>
    parts = re.split(r'\s*(?:>+|→|➜|➡)\s*', route_str.strip())
    parts = [p.strip() for p in parts if p.strip()]

    waypoints = []
    for i, name in enumerate(parts):
        # Normalize name
        clean = name.strip().rstrip('.,;:')
        # Check direct match
        coords = CITY_COORDS.get(clean)
        if not coords:
            # Check oblast mapping
            mapped = OBLAST_TO_CITY.get(clean)
            if mapped:
                coords = CITY_COORDS.get(mapped)
                clean = mapped

        wp_type = "launch" if i == 0 else ("target" if i == len(parts) - 1 else "transit")
        waypoints.append({
            "name": clean,
            "lat": coords[0] if coords else None,
            "lon": coords[1] if coords else None,
            "type": wp_type,
            "altitude_m": None,
            "time_approx": None,
        })

    return waypoints


def extract_routes_from_text(text):
    """Extract route strings from tweet text."""
    routes = []

    # Normalize: replace newlines within route patterns
    text_clean = text.replace('\n', ' ')

    # Pattern 1: "CityA > CityB > CityC" (with > or → or >>)
    # Allow hyphens in names (Primorsko-Akhtarsk)
    route_pattern = r'([A-Z][a-z]+(?:[-\s]+[A-Za-z]+)*(?:\s*(?:>+|→|➜|➡)\s*[A-Z][a-z]+(?:[-\s]+[A-Za-z]+)*){2,})'
    for match in re.finditer(route_pattern, text_clean):
        route_str = match.group(1)
        waypoints = parse_route_string(route_str)
        if len(waypoints) >= 3:  # At least launch + transit + target
            routes.append(waypoints)

    return routes


def extract_date(text):
    """Try to extract attack date from tweet text."""
    # Pattern: "DD-DDMMMYYYY" or "DD MMMM YYYY"
    patterns = [
        r'(\d{1,2})-(\d{1,2})([A-Z]{3})(\d{4})',  # 24-25JUL2024
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})',
        r'(\d{4})-(\d{2})-(\d{2})',  # ISO date
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                groups = m.groups()
                if len(groups) == 4:  # DD-DDMMMYYYY
                    month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                                 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
                    return f"{groups[3]}-{month_map[groups[2].upper()]:02d}-{int(groups[0]):02d}"
                elif len(groups) == 3 and len(groups[0]) == 4:  # ISO
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
            except:
                pass
    return None


def extract_totals(text):
    """Extract launch/interception numbers from tweet text."""
    totals = {}
    # "A total of N Shahed type UAVs were launched"
    m = re.search(r'total of (\d+)\s+(?:Shahed|UAV)', text, re.IGNORECASE)
    if m:
        totals['launched'] = int(m.group(1))

    # "N UAVs were claimed destroyed" or "N were destroyed"
    m = re.search(r'(\d+)\s+(?:UAVs?\s+)?(?:were\s+)?(?:claimed\s+)?destroyed', text, re.IGNORECASE)
    if m:
        totals['destroyed'] = int(m.group(1))

    # "N lost from EW"
    m = re.search(r'(\d+)\s+lost\s+(?:from|to)\s+EW', text, re.IGNORECASE)
    if m:
        totals['ew_lost'] = int(m.group(1))

    return totals


def parse_tweets(text):
    """Parse a block of tweet text into route traces."""
    date = extract_date(text)
    totals = extract_totals(text)
    routes_data = extract_routes_from_text(text)

    results = []
    for i, waypoints in enumerate(routes_data):
        date_compact = (date or "unknown").replace("-", "")
        route = {
            "id": f"RT_UA_{date_compact}_{i+1:03d}",
            "event_id": f"UA_{date_compact}_001",
            "conflict": "ukraine_russia",
            "date": date,
            "drone_type": "shahed_136",
            "drone_count": None,
            "route_type": "unknown",
            "approach_direction": None,
            "outcome": "unknown",
            "waypoints": waypoints,
            "notes": f"Parsed from @ShahedTracker tweet",
            "sources": [{
                "name": "Shahed Tracker (@ShahedTracker)",
                "url": "https://x.com/ShahedTracker",
                "confidence": "verified_osint",
            }],
        }
        results.append(route)

    return results, date, totals


def main():
    if len(sys.argv) > 1 and sys.argv[1] != '-':
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Split into tweet blocks (separated by blank lines)
    blocks = re.split(r'\n\s*\n', text)

    all_routes = []
    for block in blocks:
        if not block.strip():
            continue
        routes, date, totals = parse_tweets(block)
        if routes:
            print(f"Date {date}: found {len(routes)} routes")
            all_routes.extend(routes)
        if totals:
            print(f"  Totals: {totals}")

    if not all_routes:
        # Try parsing the whole text as one block
        routes, date, totals = parse_tweets(text)
        all_routes = routes
        if totals:
            print(f"Totals: {totals}")

    output_path = sys.argv[2] if len(sys.argv) > 2 else '/dev/stdout'
    if output_path == '/dev/stdout':
        print(json.dumps(all_routes, indent=2))
    else:
        with open(output_path, 'w') as f:
            json.dump(all_routes, f, indent=2)
        print(f"\nWrote {len(all_routes)} routes to {output_path}")


if __name__ == '__main__':
    main()
