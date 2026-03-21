#!/usr/bin/env python3
"""Validate OpenSkyData JSON files against schemas and report data completeness."""

import json
import sys
import os
from pathlib import Path
from jsonschema import validate, ValidationError

def load_json(path):
    with open(path) as f:
        return json.load(f)

def validate_file(data_path, schema_path):
    schema = load_json(schema_path)
    data = load_json(data_path)
    
    if not isinstance(data, list):
        data = [data]
    
    errors = []
    for i, record in enumerate(data):
        try:
            validate(instance=record, schema=schema)
        except ValidationError as e:
            errors.append(f"  Record {i} ({record.get('id', 'NO ID')}): {e.message}")
    
    return data, errors

def completeness_report(records, schema_type):
    """Report how complete the data is across all records."""
    if schema_type == "event":
        fields = [
            ("date", lambda r: r.get("date")),
            ("totals.launched_total", lambda r: r.get("totals", {}).get("launched_total")),
            ("totals.launched_drones", lambda r: r.get("totals", {}).get("launched_drones")),
            ("totals.launched_drones_strike", lambda r: r.get("totals", {}).get("launched_drones_strike")),
            ("totals.launched_drones_decoy", lambda r: r.get("totals", {}).get("launched_drones_decoy")),
            ("totals.intercepted_total", lambda r: r.get("totals", {}).get("intercepted_total")),
            ("totals.hits", lambda r: r.get("totals", {}).get("hits")),
            ("totals.interception_rate", lambda r: r.get("totals", {}).get("interception_rate")),
            ("drone_types (any)", lambda r: len(r.get("drone_types", [])) > 0),
            ("launch_regions (any)", lambda r: len(r.get("launch_regions", [])) > 0),
            ("target_regions (any)", lambda r: len(r.get("target_regions", [])) > 0),
            ("waves (any)", lambda r: len(r.get("waves", [])) > 0),
            ("interception_methods (any filled)", lambda r: any(
                v is not None for v in r.get("interception_methods", {}).values()
            )),
        ]
    elif schema_type == "route":
        fields = [
            ("waypoints (2+)", lambda r: len(r.get("waypoints", [])) >= 2),
            ("waypoints with coords", lambda r: all(
                w.get("lat") is not None for w in r.get("waypoints", [])
            )),
            ("drone_type", lambda r: r.get("drone_type")),
            ("outcome", lambda r: r.get("outcome")),
            ("approach_direction", lambda r: r.get("approach_direction")),
            ("route_type", lambda r: r.get("route_type")),
        ]
    else:
        return
    
    total = len(records)
    if total == 0:
        print("  No records to analyse.")
        return
    
    print(f"\n  Completeness across {total} records:")
    print(f"  {'Field':<40} {'Filled':>8} {'Rate':>8}")
    print(f"  {'-'*40} {'-'*8} {'-'*8}")
    for name, accessor in fields:
        filled = sum(1 for r in records if accessor(r))
        rate = filled / total * 100
        print(f"  {name:<40} {filled:>8} {rate:>7.1f}%")

def conflict_summary(records):
    """Show breakdown by conflict."""
    conflicts = {}
    for r in records:
        c = r.get("conflict", "unknown")
        conflicts[c] = conflicts.get(c, 0) + 1
    
    print(f"\n  By conflict:")
    for c, count in sorted(conflicts.items()):
        print(f"    {c}: {count} events")

def main():
    base = Path(__file__).parent.parent
    schema_dir = base / "schema"
    
    # Find all JSON data files
    data_dirs = [base / "data" / "ukraine", base / "data" / "iran", base / "examples"]
    
    event_schema = schema_dir / "attack_event.schema.json"
    route_schema = schema_dir / "route_trace.schema.json"
    
    all_events = []
    all_routes = []
    total_errors = 0
    
    for data_dir in data_dirs:
        if not data_dir.exists():
            continue
        for f in sorted(data_dir.glob("*.json")):
            fname = f.name.lower()
            if "route" in fname:
                schema_path = route_schema
                schema_type = "route"
            elif "event" in fname:
                schema_path = event_schema
                schema_type = "event"
            else:
                continue
            
            print(f"\n{'='*60}")
            print(f"Validating: {f.relative_to(base)}")
            print(f"Schema: {schema_type}")
            
            data, errors = validate_file(f, schema_path)
            
            if errors:
                print(f"  ERRORS ({len(errors)}):")
                for e in errors:
                    print(e)
                total_errors += len(errors)
            else:
                print(f"  VALID ({len(data)} records)")
            
            if schema_type == "event":
                all_events.extend(data)
                completeness_report(data, "event")
            else:
                all_routes.extend(data)
                completeness_report(data, "route")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Total events: {len(all_events)}")
    print(f"  Total routes: {len(all_routes)}")
    print(f"  Validation errors: {total_errors}")
    
    if all_events:
        conflict_summary(all_events)
        completeness_report(all_events, "event")
    
    if all_routes:
        completeness_report(all_routes, "route")
    
    return 0 if total_errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
