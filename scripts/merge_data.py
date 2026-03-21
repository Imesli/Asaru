#!/usr/bin/env python3
"""Merge all data sources into single frontend-ready JSON files.

Priority (highest first):
1. Hand-curated events (data/ukraine/events.json, data/iran/events.json) — richer detail
2. Kaggle-transformed events (data/ukraine/kaggle_events.json) — fill gaps

Deduplication: For Ukraine events on dates that exist in both hand-curated and Kaggle,
keep the hand-curated version (it has ISIS/OSINT enrichments).
"""

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "src", "public", "data")


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def merge_events():
    # Hand-curated events (highest priority)
    ua_curated = load_json(os.path.join(DATA, "ukraine", "events.json"))
    ir_curated = load_json(os.path.join(DATA, "iran", "events.json"))

    # ISIS 2025 events
    ua_isis = load_json(os.path.join(DATA, "ukraine", "isis_2025_events.json"))

    # Kaggle events
    ua_kaggle = load_json(os.path.join(DATA, "ukraine", "kaggle_events.json"))

    # Build set of dates covered by hand-curated Ukraine events
    curated_dates = set()
    for e in ua_curated:
        curated_dates.add(e["date"])

    # Merge: keep all curated + ISIS, add Kaggle where date not already covered
    merged = list(ua_curated) + list(ir_curated) + list(ua_isis)
    for e in ua_isis:
        curated_dates.add(e["date"])
    kaggle_added = 0
    for e in ua_kaggle:
        if e["date"] not in curated_dates:
            merged.append(e)
            kaggle_added += 1

    # Sort by date
    merged.sort(key=lambda e: e["date"], reverse=True)

    # Deduplicate IDs
    seen_ids = set()
    for e in merged:
        while e["id"] in seen_ids:
            # Increment suffix
            parts = e["id"].rsplit("_", 1)
            num = int(parts[1]) + 1
            e["id"] = f"{parts[0]}_{num:03d}"
        seen_ids.add(e["id"])

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "events.json"), "w") as f:
        json.dump(merged, f, indent=2)

    print(f"Events merged:")
    print(f"  Ukraine curated: {len(ua_curated)}")
    print(f"  Iran curated:    {len(ir_curated)}")
    print(f"  ISIS 2025:       {len(ua_isis)}")
    print(f"  Kaggle total:    {len(ua_kaggle)}")
    print(f"  Kaggle added:    {kaggle_added} (skipped {len(ua_kaggle) - kaggle_added} overlapping dates)")
    print(f"  Final total:     {len(merged)}")


def merge_routes():
    # Hand-curated routes (highest priority)
    routes = []
    curated_count = 0
    for conflict_dir in ["ukraine", "iran"]:
        path = os.path.join(DATA, conflict_dir, "routes.json")
        loaded = load_json(path)
        routes.extend(loaded)
        curated_count += len(loaded)

    # Example routes
    example_path = os.path.join(BASE, "examples", "example_routes.json")
    example_routes = load_json(example_path)
    route_ids = {r["id"] for r in routes}
    for r in example_routes:
        if r["id"] not in route_ids:
            routes.append(r)

    example_added = len(routes) - curated_count

    # Shahed Tracker routes (verified OSINT)
    st_path = os.path.join(DATA, "ukraine", "shahed_tracker_routes.json")
    st_routes = load_json(st_path)
    st_added = 0
    for r in st_routes:
        if r["id"] not in route_ids:
            routes.append(r)
            route_ids.add(r["id"])
            st_added += 1

    # Generated/interpolated routes
    generated_path = os.path.join(DATA, "ukraine", "generated_routes.json")
    generated = load_json(generated_path)
    gen_added = 0
    for r in generated:
        if r["id"] not in route_ids:
            routes.append(r)
            route_ids.add(r["id"])
            gen_added += 1

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "routes.json"), "w") as f:
        json.dump(routes, f, indent=2)

    print(f"Routes merged:")
    print(f"  Hand-curated:  {curated_count}")
    print(f"  Shahed Tracker: {st_added}")
    print(f"  Examples:      {example_added}")
    print(f"  Generated:     {gen_added}")
    print(f"  Total:         {len(routes)}")


if __name__ == "__main__":
    merge_events()
    merge_routes()
