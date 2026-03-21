#!/usr/bin/env python3
"""Parse scraped Shahed Tracker data into route traces.

Handles two formats:
1. Explicit routes: "Mykolaiv > Kirovohrad > Cherkasy > Kyiv"
2. Oblast movement: "UAVs reached Poltava from the North. Groups traveled from Sumy and Kharkiv"
   → inferred route: Sumy > Kharkiv > Poltava

Also extracts geocoded strike locations with precise coordinates.
"""

import json
import re
from datetime import datetime

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
    "Starokostyantyniv": (49.76, 27.22),
    "Chernivtsi": (48.29, 25.94),
    "Lutsk": (50.75, 25.34),
    "Stryi": (49.26, 23.85),
    "Chervonohrad": (50.39, 24.23),
    "Myrhorod": (49.97, 33.61),
    "Kremenchuk": (49.07, 33.42),
    "Pavlohrad": (48.54, 35.87),
    "Kryvyi Rih": (47.91, 33.39),
    "Kamianske": (48.68, 34.59),
    "Voznesensk": (47.57, 31.33),
    "Pervomais'k": (48.04, 30.85),
    "Pervomaysk": (48.04, 30.85),
    "Sarny": (51.34, 26.60),
    "Moshchne": (51.52, 31.83),
    "Malodolyns'ke": (46.34, 30.63),
    "Chornomorsk": (46.30, 30.65),
    # Launch sites
    "Primorsko-Akhtarsk": (46.05, 38.17),
    "Millerovo": (48.92, 40.39),
    "Kursk": (51.73, 36.19),
    "Bryansk": (53.25, 34.37),
    "Oryol": (52.97, 36.06),
    "Orel": (52.97, 36.06),
    "Navlya": (52.84, 34.51),
    "Yeysk": (46.71, 38.27),
    "Crimea": (45.35, 34.50),
    "Black Sea": (44.50, 33.50),
}

OBLAST_TO_CITY = {
    "Mykolaiv Oblast": "Mykolaiv",
    "Kirovohrad Oblast": "Kirovohrad",
    "Cherkasy Oblast": "Cherkasy",
    "Kyiv Oblast": "Kyiv",
    "Vinnytsia Oblast": "Vinnytsia",
    "Khmelnytskyi Oblast": "Khmelnytskyi",
    "Zhytomyr Oblast": "Zhytomyr",
    "Odesa Oblast": "Odesa",
    "Kherson Oblast": "Kherson",
    "Kharkiv Oblast": "Kharkiv",
    "Dnipropetrovsk Oblast": "Dnipro",
    "Zaporizhzhia Oblast": "Zaporizhzhia",
    "Poltava Oblast": "Poltava",
    "Sumy Oblast": "Sumy",
    "Chernihiv Oblast": "Chernihiv",
    "Lviv Oblast": "Lviv",
    "Rivne Oblast": "Rivne",
    "Ternopil Oblast": "Ternopil",
}


def make_waypoint(name, wp_type="transit"):
    coords = CITY_COORDS.get(name)
    return {
        "seq": 0,  # filled later
        "name": name,
        "lat": coords[0] if coords else None,
        "lon": coords[1] if coords else None,
        "type": wp_type,
        "altitude_m": None,
        "time_approx": None,
    }


def parse_date(text):
    """Extract date from attack header."""
    patterns = [
        (r'(\d{1,2})-(\d{1,2})([A-Z]{3})(\d{4})', 'range'),
        (r'(\d{1,2})([A-Z]{3})(\d{4})', 'single'),
        (r'(\d{1,2})([A-Z][a-z]{2})(\d{2,4})', 'single'),
    ]
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
    }
    for pat, typ in patterns:
        m = re.search(pat, text)
        if m:
            g = m.groups()
            if typ == 'range':
                day, month, year = int(g[0]), month_map.get(g[2], 1), int(g[3])
            else:
                day, month = int(g[0]), month_map.get(g[1], 1)
                year = int(g[2])
                if year < 100:
                    year += 2000
            return f"{year}-{month:02d}-{day:02d}"
    return None


def parse_launch_sites(text):
    """Extract launch site names."""
    m = re.search(r'launched from\s+(.+?)(?:\.|$)', text, re.IGNORECASE)
    if not m:
        return []
    sites_str = m.group(1)
    # Split on "and" and commas
    parts = re.split(r'\s*(?:,\s*and\s+|,\s*|\s+and\s+)', sites_str)
    sites = []
    for p in parts:
        p = p.strip().rstrip('.')
        # Handle "the X district" -> X
        p = re.sub(r'^the\s+', '', p, flags=re.IGNORECASE)
        p = re.sub(r'\s+(?:district|Oblast|region)$', '', p, flags=re.IGNORECASE)
        if p and p in CITY_COORDS:
            sites.append(p)
        elif p:
            # Try partial match
            for city in CITY_COORDS:
                if p.lower() in city.lower() or city.lower() in p.lower():
                    sites.append(city)
                    break
    return sites


def extract_explicit_routes(text):
    """Extract 'City > City > City' routes."""
    routes = []
    route_pattern = r'([A-Z][a-z]+(?:[-/\s]+[A-Za-z]+)*(?:\s*(?:>+|→|➜|➡)\s*[A-Z][a-z]+(?:[-/\s]+[A-Za-z]+)*){2,})'
    for match in re.finditer(route_pattern, text):
        route_str = match.group(1)
        parts = re.split(r'\s*(?:>+|→|➜|➡)\s*', route_str.strip())
        parts = [p.strip().rstrip('.,;:') for p in parts if p.strip()]
        if len(parts) >= 3:
            routes.append(parts)
    return routes


def extract_movement_routes(text, launch_sites):
    """Extract routes from 'UAVs reached X from Y' descriptions."""
    routes = []

    # Pattern: "UAVs reached [cities] from [direction/city]. traveled from [cities]"
    blocks = re.split(r'(?=\w+ Oblast)', text)

    for block in blocks:
        # Get oblast target
        oblast_m = re.match(r'(\w+ Oblast)', block)
        if not oblast_m:
            continue
        oblast = oblast_m.group(1)
        target_city = OBLAST_TO_CITY.get(oblast)
        if not target_city:
            continue

        # Get specific cities reached
        reached = []
        rm = re.search(r'reached\s+(?:the\s+)?(.+?)(?:\s+from|\s*\.|\s*$)', block)
        if rm:
            cities_str = rm.group(1)
            for city in CITY_COORDS:
                if city.lower() in cities_str.lower():
                    reached.append(city)
            if not reached:
                reached = [target_city]

        # Get origin/transit cities
        origins = []
        tm = re.search(r'traveled from\s+(.+?)(?:\.|$)', block, re.IGNORECASE)
        if tm:
            origin_str = tm.group(1)
            for city in CITY_COORDS:
                if city.lower() in origin_str.lower():
                    origins.append(city)

        fm = re.search(r'from the\s+(\w+)', block)
        if fm and not origins:
            direction = fm.group(1)
            # Direction to likely launch site
            if direction in ('North', 'Northeast'):
                origins = [ls for ls in launch_sites if ls in ('Kursk', 'Bryansk', 'Navlya', 'Oryol')]
            elif direction in ('South', 'Southeast'):
                origins = [ls for ls in launch_sites if ls in ('Crimea', 'Yeysk')]
            elif direction in ('East',):
                origins = [ls for ls in launch_sites if ls in ('Millerovo', 'Kursk')]

        if not origins and launch_sites:
            origins = [launch_sites[0]]

        for dest in reached:
            if origins:
                route = origins + [dest]
            else:
                route = [dest]
            if len(route) >= 2:
                routes.append(route)

    return routes


def parse_attack_block(text):
    """Parse one attack block into route traces."""
    date = parse_date(text)
    launch_sites = parse_launch_sites(text)
    explicit = extract_explicit_routes(text)
    movement = extract_movement_routes(text, launch_sites)

    # Also extract precise strike coordinates
    coord_matches = re.findall(r'(\d{2}\.\d{4,5}),?\s*(\d{2}\.\d{4,5})', text)

    all_routes = []

    # Process explicit routes
    for i, city_list in enumerate(explicit):
        waypoints = []
        for j, city in enumerate(city_list):
            # Handle "Mykolaiv/Odesa" split
            cities = city.split('/')
            for c in cities:
                c = c.strip()
                wp_type = "launch" if j == 0 else ("target" if j == len(city_list) - 1 else "transit")
                wp = make_waypoint(c, wp_type)
                wp["seq"] = len(waypoints) + 1
                waypoints.append(wp)

        if len(waypoints) >= 3:
            all_routes.append({
                "waypoints": waypoints,
                "route_type": "circuitous" if len(waypoints) > 4 else "direct",
                "approach_direction": None,
            })

    # Process movement-inferred routes
    for i, city_list in enumerate(movement):
        waypoints = []
        for j, city in enumerate(city_list):
            wp_type = "launch" if j == 0 else ("target" if j == len(city_list) - 1 else "transit")
            wp = make_waypoint(city, wp_type)
            wp["seq"] = j + 1
            waypoints.append(wp)

        if len(waypoints) >= 2:
            all_routes.append({
                "waypoints": waypoints,
                "route_type": "direct" if len(waypoints) <= 3 else "circuitous",
                "approach_direction": None,
            })

    return date, launch_sites, all_routes, coord_matches


def main():
    with open("data/shahed_tracker_scraped.txt") as f:
        text = f.read()

    blocks = re.split(r'\n\n+', text)

    all_traces = []
    route_seq = 1

    for block in blocks:
        if not block.strip():
            continue

        date, launches, routes, coords = parse_attack_block(block)
        if not date:
            continue

        date_compact = date.replace("-", "")
        event_id = f"UA_{date_compact}_001"

        for route_data in routes:
            trace = {
                "id": f"UA_{date_compact}_001_R{route_seq:02d}",
                "event_id": event_id,
                "conflict": "ukraine_russia",
                "drone_type": "shahed_136",
                "drone_count": None,
                "route_type": route_data["route_type"],
                "approach_direction": route_data.get("approach_direction"),
                "outcome": "intercepted",
                "waypoints": route_data["waypoints"],
                "estimated_distance_km": None,
                "notes": f"Extracted from @ShahedTracker thread for {date}",
                "source": {
                    "name": "Shahed Tracker (@ShahedTracker)",
                    "url": "https://x.com/ShahedTracker",
                    "confidence": "verified_osint"
                }
            }
            all_traces.append(trace)
            route_seq += 1
            print(f"  Route {trace['id']}: {' > '.join(wp['name'] for wp in route_data['waypoints'])}")

        if routes:
            print(f"Date {date}: {len(routes)} routes extracted from {len(launches)} launch sites")

    # Save
    output = "data/ukraine/shahed_tracker_routes.json"
    with open(output, "w") as f:
        json.dump(all_traces, f, indent=2)
    print(f"\nWrote {len(all_traces)} routes to {output}")


if __name__ == "__main__":
    main()
