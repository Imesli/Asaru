#!/usr/bin/env python3
"""Transform PetroIvaniuk Kaggle CSV into Asaru attack_event schema."""

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

# Geocoding lookup for Russian launch sites
LAUNCH_COORDS = {
    "Primorsko-Akhtarsk": {"lat": 46.05, "lon": 38.17, "confidence": "confirmed"},
    "Kursk oblast": {"lat": 51.73, "lon": 36.19, "confidence": "confirmed"},
    "Bryansk oblast": {"lat": 53.25, "lon": 34.37, "confidence": "confirmed"},
    "Oryol oblast": {"lat": 52.97, "lon": 36.06, "confidence": "confirmed"},
    "Millerovo": {"lat": 48.92, "lon": 40.39, "confidence": "confirmed"},
    "Hvardiiske, Crimea": {"lat": 45.11, "lon": 34.05, "confidence": "confirmed"},
    "Hvardiiske": {"lat": 45.11, "lon": 34.05, "confidence": "confirmed"},
    "Shatalovo": {"lat": 54.02, "lon": 32.44, "confidence": "confirmed"},
    "Chauda, Crimea": {"lat": 45.01, "lon": 35.83, "confidence": "confirmed"},
    "Chauda": {"lat": 45.01, "lon": 35.83, "confidence": "confirmed"},
    "Crimea": {"lat": 45.35, "lon": 34.50, "confidence": "likely"},
    "Black Sea": {"lat": 44.00, "lon": 34.00, "confidence": "estimated"},
    "Caspian Sea": {"lat": 42.00, "lon": 50.00, "confidence": "estimated"},
    "Rostov oblast": {"lat": 47.24, "lon": 39.72, "confidence": "likely"},
    "Voronezh oblast": {"lat": 51.67, "lon": 39.21, "confidence": "likely"},
    "Belgorod oblast": {"lat": 50.60, "lon": 36.60, "confidence": "likely"},
    "Donetsk oblast": {"lat": 48.00, "lon": 37.80, "confidence": "likely"},
    "Tambov oblast": {"lat": 52.73, "lon": 41.44, "confidence": "likely"},
    "Mozdok": {"lat": 43.74, "lon": 44.65, "confidence": "confirmed"},
    "Tikhoretsk": {"lat": 45.85, "lon": 40.13, "confidence": "confirmed"},
    "Yeysk": {"lat": 46.71, "lon": 38.27, "confidence": "confirmed"},
    "Engels": {"lat": 51.49, "lon": 46.11, "confidence": "confirmed"},
    "Saratov": {"lat": 51.53, "lon": 46.03, "confidence": "confirmed"},
    "Astrakhan": {"lat": 46.35, "lon": 48.04, "confidence": "likely"},
    "Lipetsk": {"lat": 52.62, "lon": 39.57, "confidence": "likely"},
    "Savasleyka": {"lat": 55.28, "lon": 42.36, "confidence": "confirmed"},
    "Olenegorsk": {"lat": 68.14, "lon": 33.28, "confidence": "confirmed"},
    "Murmansk": {"lat": 68.97, "lon": 33.07, "confidence": "likely"},
}

# Target region coords (Ukrainian oblasts/cities)
TARGET_COORDS = {
    "Kyiv": {"lat": 50.45, "lon": 30.52, "type": "mixed"},
    "Kyiv oblast": {"lat": 50.45, "lon": 30.52, "type": "mixed"},
    "Kharkiv": {"lat": 49.99, "lon": 36.23, "type": "mixed"},
    "Kharkiv oblast": {"lat": 49.99, "lon": 36.23, "type": "mixed"},
    "Odesa": {"lat": 46.48, "lon": 30.73, "type": "energy"},
    "Odesa oblast": {"lat": 46.48, "lon": 30.73, "type": "energy"},
    "Dnipro": {"lat": 48.46, "lon": 35.05, "type": "industrial"},
    "Dnipropetrovsk oblast": {"lat": 48.46, "lon": 35.05, "type": "industrial"},
    "Zaporizhzhia": {"lat": 47.84, "lon": 35.14, "type": "energy"},
    "Zaporizhzhia oblast": {"lat": 47.84, "lon": 35.14, "type": "energy"},
    "Lviv": {"lat": 49.84, "lon": 24.03, "type": "mixed"},
    "Lviv oblast": {"lat": 49.84, "lon": 24.03, "type": "mixed"},
    "Vinnytsia": {"lat": 49.23, "lon": 28.47, "type": "military"},
    "Vinnytsia oblast": {"lat": 49.23, "lon": 28.47, "type": "military"},
    "Zhytomyr": {"lat": 50.25, "lon": 28.66, "type": "military"},
    "Zhytomyr oblast": {"lat": 50.25, "lon": 28.66, "type": "military"},
    "Poltava": {"lat": 49.59, "lon": 34.55, "type": "military"},
    "Poltava oblast": {"lat": 49.59, "lon": 34.55, "type": "military"},
    "Chernihiv": {"lat": 51.50, "lon": 31.30, "type": "mixed"},
    "Chernihiv oblast": {"lat": 51.50, "lon": 31.30, "type": "mixed"},
    "Sumy": {"lat": 50.91, "lon": 34.80, "type": "mixed"},
    "Sumy oblast": {"lat": 50.91, "lon": 34.80, "type": "mixed"},
    "Mykolaiv": {"lat": 46.97, "lon": 32.00, "type": "industrial"},
    "Mykolaiv oblast": {"lat": 46.97, "lon": 32.00, "type": "industrial"},
    "Kherson": {"lat": 46.64, "lon": 32.62, "type": "mixed"},
    "Kherson oblast": {"lat": 46.64, "lon": 32.62, "type": "mixed"},
    "Khmelnytskyi": {"lat": 49.42, "lon": 26.99, "type": "military"},
    "Khmelnytskyi oblast": {"lat": 49.42, "lon": 26.99, "type": "military"},
    "Cherkasy": {"lat": 49.44, "lon": 32.06, "type": "industrial"},
    "Cherkasy oblast": {"lat": 49.44, "lon": 32.06, "type": "industrial"},
    "Rivne": {"lat": 50.62, "lon": 26.25, "type": "energy"},
    "Rivne oblast": {"lat": 50.62, "lon": 26.25, "type": "energy"},
    "Ivano-Frankivsk": {"lat": 48.92, "lon": 24.71, "type": "energy"},
    "Ivano-Frankivsk oblast": {"lat": 48.92, "lon": 24.71, "type": "energy"},
    "Ternopil": {"lat": 49.55, "lon": 25.59, "type": "mixed"},
    "Ternopil oblast": {"lat": 49.55, "lon": 25.59, "type": "mixed"},
    "Volyn oblast": {"lat": 50.75, "lon": 25.34, "type": "mixed"},
    "Chernivtsi": {"lat": 48.29, "lon": 25.94, "type": "mixed"},
    "Chernivtsi oblast": {"lat": 48.29, "lon": 25.94, "type": "mixed"},
    "Kirovohrad oblast": {"lat": 48.51, "lon": 32.26, "type": "mixed"},
    "Kropyvnytskyi": {"lat": 48.51, "lon": 32.26, "type": "mixed"},
    "Donetsk": {"lat": 48.00, "lon": 37.80, "type": "military"},
    "Luhansk": {"lat": 48.57, "lon": 39.31, "type": "military"},
    "Zakarpattia oblast": {"lat": 48.62, "lon": 22.29, "type": "mixed"},
}

# Map Kaggle model names to Asaru drone_type enum
MODEL_MAP = {
    "Shahed-136/131": "shahed_136",
    "Unknown UAV": "unknown",
    "Orlan-10": "orlan",
    "Supercam": "supercam",
    "ZALA": "zala",
    "Lancet": "unknown_strike",
    "Reconnaissance UAV": "unknown",
}

# Missile models (not drones)
MISSILE_MODELS = {
    "X-101/X-555", "X-59", "X-59/X-69", "X-22", "X-47M2 Kinzhal",
    "X-31P", "X-35", "Iskander-M", "Iskander-M/KN-23", "Iskander-K",
    "Kalibr", "C-300", "KAB", "Tochka-U", "Kh-101", "P-800 Onyx",
    "Молнія", "3M22 Tsyrkon", "Р-500",
}


def safe_int(val):
    if not val or val == 'nan' or val == '':
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def parse_launch_places(raw):
    """Split 'Primorsko-Akhtarsk and Kursk oblast and ...' into list."""
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(" and ")]
    return [p for p in parts if p]


def parse_target_regions(raw):
    """Parse 'affected region' or 'target_main' field."""
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(" and ")]
    return [p for p in parts if p]


def determine_attack_type(rows):
    has_drones = any(r['model'] not in MISSILE_MODELS for r in rows if r.get('model'))
    has_missiles = any(r['model'] in MISSILE_MODELS for r in rows if r.get('model'))
    if has_drones and has_missiles:
        return "combined_drone_missile"
    elif has_missiles:
        return "missile_only"
    elif has_drones:
        return "drone_only"
    return "unknown"


DIRECTION_FROM_REGION = {
    "south": "south",
    "west": "west",
    "east": "east",
    "north": "north",
    "Odesa oblast": "south",
    "Mykolaiv oblast": "south",
    "Kherson oblast": "south",
    "Zaporizhzhia oblast": "southeast",
    "Dnipropetrovsk oblast": "east",
    "Kharkiv oblast": "east",
    "Poltava oblast": "east",
    "Kirovohrad oblast": "south",
    "Cherkasy oblast": "east",
    "Khmelnytskyi oblast": "west",
    "Lviv oblast": "west",
    "Ivano-Frankivsk oblast": "west",
    "Rivne oblast": "northwest",
    "Vinnytsia oblast": "southwest",
    "Zhytomyr oblast": "west",
    "Sumy oblast": "northeast",
    "Chernihiv oblast": "north",
    "Kyiv oblast": "north",
    "Donetsk oblast": "east",
}


def build_waves_from_directions(interception_by_region):
    """Build wave data from directional interception counts."""
    if not interception_by_region:
        return []
    # Group by direction
    by_direction = defaultdict(int)
    for region, count in interception_by_region.items():
        direction = DIRECTION_FROM_REGION.get(region, None)
        if direction:
            by_direction[direction] += count
    if not by_direction:
        return []
    waves = []
    for i, (direction, count) in enumerate(sorted(by_direction.items(), key=lambda x: -x[1]), 1):
        waves.append({
            "wave_number": i,
            "time_approx": None,
            "drone_count": count,
            "direction": direction,
            "notes": f"Interceptions in {direction} sector"
        })
    return waves


def build_notes(border_crossings, turbojet_total):
    """Build notes string from extra data."""
    parts = []
    if border_crossings:
        bc_str = ", ".join(f"{c}: {n}" for c, n in border_crossings.items())
        parts.append(f"Border crossings: {bc_str}")
    if turbojet_total:
        parts.append(f"Included {turbojet_total} Geran-3 turbojet drones")
    return ". ".join(parts) if parts else None


def build_source_url(source_field):
    """Convert 'kpszsu/posts/...' to Facebook URL."""
    if not source_field:
        return None
    if source_field.startswith("kpszsu/"):
        return f"https://www.facebook.com/{source_field}"
    if source_field.startswith("http"):
        return source_field
    return None


def transform(csv_path, output_path):
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))

    # Group rows by date
    by_date = defaultdict(list)
    for r in rows:
        date = r['time_start'][:10]
        by_date[date].append(r)

    events = []
    for date in sorted(by_date.keys()):
        date_rows = by_date[date]

        # Totals
        total_launched = 0
        total_destroyed = 0
        drone_launched = 0
        drone_strike = 0
        drone_decoy = 0
        missile_cruise = 0
        missile_ballistic = 0
        drone_types = defaultdict(int)
        launch_names = set()
        target_names = set()
        source_urls = set()
        interception_by_region = defaultdict(int)
        border_crossings = defaultdict(int)
        turbojet_total = 0
        turbojet_destroyed = 0

        for r in date_rows:
            launched = safe_int(r.get('launched'))
            destroyed = safe_int(r.get('destroyed'))
            model = r.get('model', '')

            if launched:
                total_launched += launched
            if destroyed:
                total_destroyed += destroyed

            if model in MISSILE_MODELS:
                if model in ("Iskander-M", "Iskander-M/KN-23", "C-300", "KAB", "Tochka-U", "X-47M2 Kinzhal"):
                    if launched:
                        missile_ballistic += launched
                else:
                    if launched:
                        missile_cruise += launched
            else:
                if launched:
                    drone_launched += launched
                asaru_model = MODEL_MAP.get(model, "unknown")
                if launched:
                    drone_types[asaru_model] += launched

            # Strike vs decoy split from is_shahed field
            is_shahed = safe_int(r.get('is_shahed'))
            if is_shahed and launched and 'Shahed' in model:
                drone_strike += is_shahed
                drone_decoy += (launched - is_shahed)

            # Turbojet (Geran-3) data
            tj = safe_int(r.get('turbojet'))
            tjd = safe_int(r.get('turbojet_destroyed'))
            if tj:
                turbojet_total += tj
            if tjd:
                turbojet_destroyed += tjd

            # Parse launch places
            for lp in parse_launch_places(r.get('launch_place', '')):
                launch_names.add(lp)

            # Parse target regions from affected region (interception locations)
            for tr in parse_target_regions(r.get('affected region', '')):
                target_names.add(tr)
            for tr in parse_target_regions(r.get('target_main', '')):
                target_names.add(tr)

            # Parse destroyed_details for directional/regional interception data
            dd = r.get('destroyed_details', '')
            if dd and dd != '{}':
                try:
                    d = eval(dd)
                    for region, count in d.items():
                        if str(count) != 'nan' and count:
                            interception_by_region[region] += int(count)
                except:
                    pass

            # Parse border_crossing data
            bc = r.get('border_crossing', '')
            if bc and bc != '{}':
                try:
                    d = eval(bc)
                    for country, count in d.items():
                        if str(count) != 'nan' and count:
                            border_crossings[country] += int(float(count))
                except:
                    pass

            # Source
            url = build_source_url(r.get('source', ''))
            if url:
                source_urls.add(url)

        # Use destroyed_details regions as target regions if we have them
        # These are more specific than the generic target fields
        for region in interception_by_region:
            target_names.add(region)

        if total_launched == 0:
            continue

        # Build launch_regions
        launch_regions = []
        for name in sorted(launch_names):
            coords = LAUNCH_COORDS.get(name)
            launch_regions.append({
                "name": name,
                "lat": coords["lat"] if coords else None,
                "lon": coords["lon"] if coords else None,
                "confidence": coords["confidence"] if coords else "estimated",
            })

        # Build target_regions
        target_regions = []
        for name in sorted(target_names):
            coords = TARGET_COORDS.get(name)
            target_regions.append({
                "name": name,
                "lat": coords["lat"] if coords else None,
                "lon": coords["lon"] if coords else None,
                "target_type": coords["type"] if coords else "unknown",
            })

        # If no target regions parsed, add generic Ukraine
        if not target_regions:
            target_regions = [{"name": "Ukraine", "lat": 48.38, "lon": 31.17, "target_type": "mixed"}]

        # Build drone_types array
        drone_type_arr = []
        for model, count in sorted(drone_types.items(), key=lambda x: -x[1]):
            drone_type_arr.append({"model": model, "count": count, "speed_kmh": None})

        # Time
        time_start = date_rows[0].get('time_start', '')
        time_end = date_rows[0].get('time_end', '')
        ts = time_start[11:16] if len(time_start) > 11 else None
        te = time_end[11:16] if len(time_end) > 11 else None

        # Interception rate
        rate = round(total_destroyed / total_launched, 3) if total_launched > 0 else None

        # Hits
        hits_val = None
        not_reached = sum(safe_int(r.get('not_reach_goal')) or 0 for r in date_rows)
        still_attacking = sum(safe_int(r.get('still_attacking')) or 0 for r in date_rows)
        if total_launched and total_destroyed:
            hits_val = total_launched - total_destroyed - not_reached

        # ID
        date_compact = date.replace('-', '')
        event_id = f"UA_{date_compact}_001"

        event = {
            "id": event_id,
            "conflict": "ukraine_russia",
            "date": date,
            "time_start": ts,
            "time_end": te,
            "duration_hours": None,
            "attack_type": determine_attack_type(date_rows),
            "totals": {
                "launched_total": total_launched,
                "launched_drones": drone_launched if drone_launched > 0 else None,
                "launched_drones_strike": drone_strike if drone_strike > 0 else None,
                "launched_drones_decoy": drone_decoy if drone_decoy > 0 else None,
                "launched_missiles_cruise": missile_cruise if missile_cruise > 0 else None,
                "launched_missiles_ballistic": missile_ballistic if missile_ballistic > 0 else None,
                "intercepted_total": total_destroyed,
                "intercepted_drones": None,
                "hits": hits_val if hits_val and hits_val > 0 else None,
                "lost_location": None,
                "interception_rate": rate,
            },
            "drone_types": drone_type_arr if drone_type_arr else [],
            "launch_regions": launch_regions,
            "target_regions": target_regions,
            "waves": build_waves_from_directions(interception_by_region),
            "interception_methods": {},
            "defence_context": {},
            "notes": build_notes(border_crossings, turbojet_total),
            "sources": [
                {
                    "name": "PetroIvaniuk Kaggle / Ukrainian Air Force",
                    "url": list(source_urls)[0] if source_urls else "https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine",
                    "confidence": "official",
                    "fields_sourced": ["totals", "launch_regions", "drone_types"],
                }
            ],
        }

        events.append(event)

    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"Transformed {len(events)} events from {len(rows)} CSV rows")
    print(f"Date range: {events[0]['date']} to {events[-1]['date']}")

    # Stats
    total = sum(e['totals']['launched_total'] for e in events)
    print(f"Total projectiles: {total:,}")


if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/kaggle_ukraine/missile_attacks_daily.csv'
    output_path = sys.argv[2] if len(sys.argv) > 2 else '/Users/oliverbouzad/fwegrht/Asaru/data/ukraine/kaggle_events.json'
    transform(csv_path, output_path)
