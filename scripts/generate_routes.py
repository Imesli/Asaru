#!/usr/bin/env python3
"""Generate plausible interpolated route traces from event launch→target data.

Shahed-136 flight characteristics:
- Speed: ~180 km/h (prop), Geran-3: ~600 km/h (jet)
- Altitude: 100-500m AGL (low to avoid radar)
- Range: ~2,500 km (Shahed-136), ~1,800 km (Geran-2)
- Navigation: GPS + INS, follows waypoint corridors
- Behavior: Avoids major air defense zones, follows geographic features,
  often routes through "corridor oblasts" to reach deep targets

Known Ukrainian corridor patterns (from Shahed Tracker observations):
- Southern corridor: Crimea/Black Sea → Mykolaiv → Kirovohrad → central targets
- Eastern corridor: Kursk/Bryansk → Sumy/Chernihiv → Kyiv
- Western loop: South → Vinnytsia → Khmelnytskyi → western targets
- Direct east: Donetsk front → Zaporizhzhia/Dnipro

This script generates route waypoints by:
1. Taking launch and target coordinates from events
2. Adding intermediate waypoints along known corridor patterns
3. Adding slight randomization to avoid unrealistic straight lines
"""

import json
import math
import os
import random
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Known corridor waypoints (transit cities drones fly through)
CORRIDOR_WAYPOINTS = {
    "Mykolaiv": {"lat": 46.97, "lon": 32.00},
    "Kirovohrad": {"lat": 48.51, "lon": 32.26},
    "Cherkasy": {"lat": 49.44, "lon": 32.06},
    "Vinnytsia": {"lat": 49.23, "lon": 28.47},
    "Khmelnytskyi": {"lat": 49.42, "lon": 26.99},
    "Zhytomyr": {"lat": 50.25, "lon": 28.66},
    "Uman": {"lat": 48.75, "lon": 30.22},
    "Bila Tserkva": {"lat": 49.80, "lon": 30.11},
    "Sumy": {"lat": 50.91, "lon": 34.80},
    "Chernihiv": {"lat": 51.50, "lon": 31.30},
    "Poltava": {"lat": 49.59, "lon": 34.55},
    "Kropyvnytskyi": {"lat": 48.51, "lon": 32.26},
    "Odesa": {"lat": 46.48, "lon": 30.73},
    "Kherson": {"lat": 46.64, "lon": 32.62},
    "Zaporizhzhia": {"lat": 47.84, "lon": 35.14},
    "Dnipro": {"lat": 48.46, "lon": 35.05},
    "Rivne": {"lat": 50.62, "lon": 26.25},
    "Ternopil": {"lat": 49.55, "lon": 25.59},
    "Lviv": {"lat": 49.84, "lon": 24.03},
    "Ivano-Frankivsk": {"lat": 48.92, "lon": 24.71},
}

# Known corridor patterns: launch_region → list of transit waypoints to reach target area
CORRIDORS = {
    # Southern routes (Crimea/Primorsko-Akhtarsk)
    ("south", "Kyiv"): ["Mykolaiv", "Kirovohrad", "Cherkasy"],
    ("south", "Kyiv oblast"): ["Mykolaiv", "Kirovohrad", "Cherkasy"],
    ("south", "Khmelnytskyi"): ["Mykolaiv", "Kirovohrad", "Vinnytsia"],
    ("south", "Khmelnytskyi oblast"): ["Mykolaiv", "Kirovohrad", "Vinnytsia"],
    ("south", "Vinnytsia"): ["Mykolaiv", "Kirovohrad", "Uman"],
    ("south", "Vinnytsia oblast"): ["Mykolaiv", "Kirovohrad", "Uman"],
    ("south", "Zhytomyr"): ["Mykolaiv", "Kirovohrad", "Vinnytsia"],
    ("south", "Zhytomyr oblast"): ["Mykolaiv", "Kirovohrad", "Vinnytsia"],
    ("south", "Lviv"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi", "Ternopil"],
    ("south", "Lviv oblast"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi", "Ternopil"],
    ("south", "Rivne"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi"],
    ("south", "Rivne oblast"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi"],
    ("south", "Ivano-Frankivsk"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi"],
    ("south", "Ivano-Frankivsk oblast"): ["Mykolaiv", "Kirovohrad", "Vinnytsia", "Khmelnytskyi"],
    ("south", "Dnipro"): ["Mykolaiv", "Kirovohrad"],
    ("south", "Dnipropetrovsk oblast"): ["Mykolaiv", "Kirovohrad"],
    ("south", "Poltava"): ["Mykolaiv", "Kirovohrad", "Cherkasy"],
    ("south", "Poltava oblast"): ["Mykolaiv", "Kirovohrad", "Cherkasy"],
    ("south", "Cherkasy"): ["Mykolaiv", "Kirovohrad"],
    ("south", "Cherkasy oblast"): ["Mykolaiv", "Kirovohrad"],

    # Northern routes (Kursk/Bryansk)
    ("north", "Kyiv"): ["Sumy", "Chernihiv"],
    ("north", "Kyiv oblast"): ["Sumy", "Chernihiv"],
    ("north", "Zhytomyr"): ["Sumy", "Chernihiv"],
    ("north", "Zhytomyr oblast"): ["Sumy", "Chernihiv"],
    ("north", "Poltava"): ["Sumy"],
    ("north", "Poltava oblast"): ["Sumy"],
    ("north", "Cherkasy"): ["Sumy", "Poltava"],
    ("north", "Cherkasy oblast"): ["Sumy", "Poltava"],
    ("north", "Khmelnytskyi"): ["Sumy", "Chernihiv", "Zhytomyr"],
    ("north", "Khmelnytskyi oblast"): ["Sumy", "Chernihiv", "Zhytomyr"],

    # Eastern routes (Millerovo/Rostov/Donetsk)
    ("east", "Dnipro"): ["Zaporizhzhia"],
    ("east", "Dnipropetrovsk oblast"): ["Zaporizhzhia"],
    ("east", "Kyiv"): ["Poltava", "Cherkasy"],
    ("east", "Kyiv oblast"): ["Poltava", "Cherkasy"],
    ("east", "Kharkiv"): [],
    ("east", "Kharkiv oblast"): [],
}

# Classify launch sites by direction
LAUNCH_DIRECTION = {
    "Primorsko-Akhtarsk": "south",
    "Hvardiiske, Crimea": "south",
    "Hvardiiske": "south",
    "Chauda, Crimea": "south",
    "Chauda": "south",
    "Crimea": "south",
    "Kursk oblast": "north",
    "Bryansk oblast": "north",
    "Oryol oblast": "north",
    "Shatalovo": "north",
    "Millerovo": "east",
    "Rostov oblast": "east",
    "Voronezh oblast": "north",
    "Belgorod oblast": "north",
    "Donetsk oblast": "east",
    "Tambov oblast": "north",
    "Black Sea": "south",
}

# Geocoding for launch sites (reuse from kaggle_to_asaru.py)
LAUNCH_COORDS = {
    "Primorsko-Akhtarsk": (46.05, 38.17),
    "Kursk oblast": (51.73, 36.19),
    "Bryansk oblast": (53.25, 34.37),
    "Oryol oblast": (52.97, 36.06),
    "Millerovo": (48.92, 40.39),
    "Hvardiiske, Crimea": (45.11, 34.05),
    "Hvardiiske": (45.11, 34.05),
    "Shatalovo": (54.02, 32.44),
    "Chauda, Crimea": (45.01, 35.83),
    "Chauda": (45.01, 35.83),
    "Crimea": (45.35, 34.50),
    "Black Sea": (44.00, 34.00),
}

TARGET_COORDS = {
    "Kyiv": (50.45, 30.52),
    "Kyiv oblast": (50.45, 30.52),
    "Kharkiv": (49.99, 36.23),
    "Kharkiv oblast": (49.99, 36.23),
    "Odesa": (46.48, 30.73),
    "Odesa oblast": (46.48, 30.73),
    "Dnipro": (48.46, 35.05),
    "Dnipropetrovsk oblast": (48.46, 35.05),
    "Zaporizhzhia": (47.84, 35.14),
    "Zaporizhzhia oblast": (47.84, 35.14),
    "Vinnytsia": (49.23, 28.47),
    "Vinnytsia oblast": (49.23, 28.47),
    "Khmelnytskyi": (49.42, 26.99),
    "Khmelnytskyi oblast": (49.42, 26.99),
    "Zhytomyr": (50.25, 28.66),
    "Zhytomyr oblast": (50.25, 28.66),
    "Lviv": (49.84, 24.03),
    "Lviv oblast": (49.84, 24.03),
    "Rivne": (50.62, 26.25),
    "Rivne oblast": (50.62, 26.25),
    "Cherkasy": (49.44, 32.06),
    "Cherkasy oblast": (49.44, 32.06),
    "Poltava": (49.59, 34.55),
    "Poltava oblast": (49.59, 34.55),
    "Mykolaiv": (46.97, 32.00),
    "Mykolaiv oblast": (46.97, 32.00),
    "Kherson": (46.64, 32.62),
    "Kherson oblast": (46.64, 32.62),
    "Sumy": (50.91, 34.80),
    "Sumy oblast": (50.91, 34.80),
    "Chernihiv": (51.50, 31.30),
    "Chernihiv oblast": (51.50, 31.30),
    "Ivano-Frankivsk": (48.92, 24.71),
    "Ivano-Frankivsk oblast": (48.92, 24.71),
    "Ternopil": (49.55, 25.59),
    "Ternopil oblast": (49.55, 25.59),
    "Kirovohrad oblast": (48.51, 32.26),
    "Chernivtsi": (48.29, 25.94),
    "Chernivtsi oblast": (48.29, 25.94),
}


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def jitter(lat, lon, km=5):
    """Add small random offset to avoid overlapping routes."""
    dlat = (random.random() - 0.5) * (km / 111)
    dlon = (random.random() - 0.5) * (km / (111 * math.cos(math.radians(lat))))
    return round(lat + dlat, 4), round(lon + dlon, 4)


def classify_route_type(waypoints):
    """Classify as direct/circuitous/looping based on path efficiency."""
    if len(waypoints) < 2:
        return "direct"
    start = waypoints[0]
    end = waypoints[-1]
    straight = haversine_km(start["lat"], start["lon"], end["lat"], end["lon"])
    actual = sum(
        haversine_km(waypoints[i]["lat"], waypoints[i]["lon"],
                     waypoints[i+1]["lat"], waypoints[i+1]["lon"])
        for i in range(len(waypoints)-1)
    )
    ratio = actual / straight if straight > 0 else 1
    if ratio < 1.3:
        return "direct"
    elif ratio < 2.0:
        return "circuitous"
    else:
        return "looping"


def approach_direction(launch_lat, launch_lon, target_lat, target_lon):
    """Determine cardinal approach direction."""
    dlat = target_lat - launch_lat
    dlon = target_lon - launch_lon
    angle = math.degrees(math.atan2(dlon, dlat))
    if -22.5 <= angle < 22.5: return "north"
    if 22.5 <= angle < 67.5: return "northeast"
    if 67.5 <= angle < 112.5: return "east"
    if 112.5 <= angle < 157.5: return "southeast"
    if angle >= 157.5 or angle < -157.5: return "south"
    if -157.5 <= angle < -112.5: return "southwest"
    if -112.5 <= angle < -67.5: return "west"
    return "northwest"


def generate_route(event, launch_name, launch_lat, launch_lon, target_name, target_lat, target_lon, drone_count, route_idx):
    """Generate a single route trace with interpolated waypoints."""
    direction = LAUNCH_DIRECTION.get(launch_name, "south")
    corridor_key = (direction, target_name)

    waypoints = []

    # Start: launch point
    jlat, jlon = jitter(launch_lat, launch_lon, km=3)
    waypoints.append({
        "name": launch_name,
        "lat": jlat, "lon": jlon,
        "type": "launch",
        "altitude_m": None,
        "time_approx": None,
    })

    # Middle: corridor waypoints
    corridor = CORRIDORS.get(corridor_key, [])
    for wp_name in corridor:
        wp = CORRIDOR_WAYPOINTS.get(wp_name)
        if wp:
            wlat, wlon = jitter(wp["lat"], wp["lon"], km=8)
            waypoints.append({
                "name": wp_name,
                "lat": wlat, "lon": wlon,
                "type": "transit",
                "altitude_m": None,
                "time_approx": None,
            })

    # If no corridor found, add a midpoint to avoid straight lines
    if not corridor:
        mid_lat = (launch_lat + target_lat) / 2 + (random.random() - 0.5) * 0.5
        mid_lon = (launch_lon + target_lon) / 2 + (random.random() - 0.5) * 0.5
        waypoints.append({
            "name": "transit",
            "lat": round(mid_lat, 4), "lon": round(mid_lon, 4),
            "type": "transit",
            "altitude_m": None,
            "time_approx": None,
        })

    # End: target
    outcome = "intercepted" if random.random() < (event["totals"].get("interception_rate") or 0.85) else "hit_target"
    end_type = "intercept" if outcome == "intercepted" else "target"

    # If intercepted, end slightly before target
    if outcome == "intercepted" and len(waypoints) >= 2:
        last_wp = waypoints[-1]
        ilat = last_wp["lat"] + (target_lat - last_wp["lat"]) * random.uniform(0.3, 0.8)
        ilon = last_wp["lon"] + (target_lon - last_wp["lon"]) * random.uniform(0.3, 0.8)
        waypoints.append({
            "name": f"near {target_name}",
            "lat": round(ilat, 4), "lon": round(ilon, 4),
            "type": end_type,
            "altitude_m": None,
            "time_approx": None,
        })
    else:
        jlat, jlon = jitter(target_lat, target_lon, km=2)
        waypoints.append({
            "name": target_name,
            "lat": jlat, "lon": jlon,
            "type": end_type,
            "altitude_m": None,
            "time_approx": None,
        })

    route_type = classify_route_type(waypoints)
    date_compact = event["date"].replace("-", "")

    return {
        "id": f"RT_UA_{date_compact}_{route_idx:03d}",
        "event_id": event["id"],
        "conflict": "ukraine_russia",
        "date": event["date"],
        "drone_type": "shahed_136",
        "drone_count": drone_count,
        "route_type": route_type,
        "approach_direction": approach_direction(launch_lat, launch_lon, target_lat, target_lon),
        "outcome": outcome,
        "waypoints": waypoints,
        "notes": f"Interpolated route: {launch_name} → {' → '.join(corridor)} → {target_name}" if corridor else f"Interpolated route: {launch_name} → {target_name}",
        "sources": [{
            "name": "Asaru interpolation from Kaggle/UAF data",
            "url": None,
            "confidence": "estimate",
        }],
    }


def generate_all_routes(events_path, output_path, max_routes_per_event=3):
    with open(events_path) as f:
        events = json.load(f)

    # Only generate for Ukraine events with Shahed data
    shahed_events = [e for e in events if e["conflict"] == "ukraine_russia"
                     and any(dt.get("model") in ("shahed_136", "shahed_131", "geran_2")
                             for dt in e.get("drone_types", []))]

    random.seed(42)  # Reproducible routes

    all_routes = []
    for event in shahed_events:
        launches = [l for l in event.get("launch_regions", []) if l.get("lat") and l.get("lon")]
        targets = [t for t in event.get("target_regions", [])
                   if t.get("lat") and t.get("lon") and t["name"] != "Ukraine"]

        if not launches or not targets:
            continue

        # Generate routes for significant launch→target pairs
        route_idx = 1
        drone_total = sum(dt.get("count", 0) for dt in event.get("drone_types", [])
                         if dt.get("model") in ("shahed_136", "shahed_131", "geran_2", "unknown"))

        for launch in launches[:2]:  # Top 2 launch sites
            for target in targets[:max_routes_per_event]:
                # Distribute drones roughly across routes
                per_route = max(1, drone_total // (len(launches) * min(len(targets), max_routes_per_event)))

                route = generate_route(
                    event, launch["name"], launch["lat"], launch["lon"],
                    target["name"], target["lat"], target["lon"],
                    per_route, route_idx
                )
                all_routes.append(route)
                route_idx += 1

    with open(output_path, "w") as f:
        json.dump(all_routes, f, indent=2)

    print(f"Generated {len(all_routes)} interpolated routes from {len(shahed_events)} Shahed events")
    outcomes = {}
    for r in all_routes:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    print(f"Outcomes: {outcomes}")
    types = {}
    for r in all_routes:
        types[r["route_type"]] = types.get(r["route_type"], 0) + 1
    print(f"Route types: {types}")


if __name__ == "__main__":
    events_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data", "ukraine", "kaggle_events.json")
    output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "data", "ukraine", "generated_routes.json")
    generate_all_routes(events_path, output_path)
