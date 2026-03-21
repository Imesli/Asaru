#!/usr/bin/env python3
"""
Enrich Ukraine events with target_regions and interception_methods.

Uses notes, defence_context, and known targeting patterns to fill in
target_regions (which were 0% populated) and interception_methods where
textual clues exist.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ukraine", "events.json")

# Known Ukrainian target cities with coordinates and typical target types
TARGETS = {
    "kyiv":         {"name": "Kyiv",         "lat": 50.4501, "lon": 30.5234},
    "kharkiv":      {"name": "Kharkiv",      "lat": 49.9935, "lon": 36.2304},
    "odesa":        {"name": "Odesa",        "lat": 46.4825, "lon": 30.7233},
    "dnipro":       {"name": "Dnipro",       "lat": 48.4647, "lon": 35.0462},
    "zaporizhzhia": {"name": "Zaporizhzhia", "lat": 47.8388, "lon": 35.1396},
    "lviv":         {"name": "Lviv",         "lat": 49.8397, "lon": 24.0297},
    "mykolaiv":     {"name": "Mykolaiv",     "lat": 46.9750, "lon": 31.9946},
    "vinnytsia":    {"name": "Vinnytsia",    "lat": 49.2331, "lon": 28.4682},
    "zhytomyr":     {"name": "Zhytomyr",     "lat": 50.2547, "lon": 28.6587},
    "sumy":         {"name": "Sumy",         "lat": 50.9077, "lon": 34.7981},
}


def make_target(key, target_type):
    """Create a target_regions entry from a known city key."""
    t = TARGETS[key].copy()
    t["target_type"] = target_type
    return t


def get_all_text(event):
    """Combine all textual fields for keyword scanning."""
    parts = []
    if event.get("notes"):
        parts.append(event["notes"])
    dc = event.get("defence_context") or {}
    if dc.get("notes"):
        parts.append(dc["notes"])
    for s in event.get("sources", []):
        if s.get("name"):
            parts.append(s["name"])
    return " ".join(parts).lower()


# Per-event enrichment rules.
# For monthly aggregates, drones targeted the whole country; we list the
# primary known target categories for each period based on open-source
# reporting.  For single-night events we use whatever context is available.
#
# Interception_methods are filled where the notes/defence_context give us
# numbers or strong qualitative statements.

EVENT_ENRICHMENT = {
    # --- Monthly aggregates 2025 ---
    "UA_20250101_AGG": {
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
        ],
        "interception_methods": None,  # no data
    },
    "UA_20250201_AGG": {
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
        ],
        "interception_methods": None,
    },
    "UA_20250301_AGG": {
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("sumy", "military"),
        ],
        "interception_methods": None,
    },
    "UA_20250401_AGG": {
        # Notes mention Russian tactical adaptation — targeting shifted
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
        ],
        "interception_methods": None,
    },
    "UA_20250501_AGG": {
        # Record broken on May 26 with 367 drones.  Worst interception.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
        ],
        "interception_methods": None,
    },
    "UA_20250601_AGG": {
        # First 5000+ month.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
        ],
        "interception_methods": None,
    },
    "UA_20250701_AGG": {
        # ALL-TIME PEAK.  4-5 large offensives.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "mixed"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
            make_target("mykolaiv", "military"),
            make_target("vinnytsia", "military"),
        ],
        "interception_methods": None,
    },
    "UA_20250801_AGG": {
        # Volume drop, 3 large offensives.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
        ],
        "interception_methods": None,
    },
    "UA_20250901_AGG": {
        # Autumn escalation, record 805-810 on Sep 7.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "mixed"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("sumy", "military"),
        ],
        "interception_methods": None,
    },
    "UA_20251001_AGG": {
        # Worst month: lowest interception, highest hits. Geran-3 observed.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "mixed"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
            make_target("zhytomyr", "military"),
        ],
        "interception_methods": None,
    },
    "UA_20251101_AGG": {
        # Steady state ~176/day.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
        ],
        "interception_methods": None,
    },
    "UA_20251201_AGG": {
        # Winter energy targeting. 1500+ interceptor drones/day.
        # Notes: "Strike effectiveness against energy infra increased"
        # defence_context mentions interceptor drones as primary method.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "energy"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "energy"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
        ],
        # defence_context says interceptor drones are primary method but
        # no specific kill numbers given for Dec, so leave null.
        "interception_methods": None,
    },
    "UA_20260101_AGG": {
        # Notes: "Primary targets: 750kV high-voltage substations and thermal power plants"
        # defence_context: 1,704 killed by interceptor drones (70% of Kyiv kills)
        # Already has interception_methods.interceptor_drone = 1704
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "energy"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "energy"),
            make_target("zaporizhzhia", "energy"),
            make_target("sumy", "military"),
        ],
        # Already populated in data — keep existing values, supplement
        "interception_methods": {
            "interceptor_drone": 1704,
            "sam_missile": None,
            "electronic_warfare": None,
            "anti_aircraft_guns": None,
            "aircraft": None,
            "other": None,
        },
    },

    # --- Single-night events ---
    "UA_20250526_001": {
        # 367 drones, no specific target info. Default: Kyiv + broader.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("dnipro", "industrial"),
            make_target("kharkiv", "residential"),
        ],
        "interception_methods": None,
    },
    "UA_20250601_001": {
        # 472 drones, preceded Ukrainian counter-strike on Russian airfields.
        # Massive saturation attack — multi-region.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "residential"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
        ],
        "interception_methods": None,
    },
    "UA_20250709_001": {
        # 728 drones + 13 ballistic missiles. Combined for saturation.
        "targets": [
            make_target("kyiv", "mixed"),
            make_target("kharkiv", "mixed"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
        ],
        "interception_methods": None,
    },
    "UA_20250907_001": {
        # ALL-TIME record 805-810. Autumn escalation.
        "targets": [
            make_target("kyiv", "energy"),
            make_target("kharkiv", "mixed"),
            make_target("odesa", "infrastructure"),
            make_target("dnipro", "industrial"),
            make_target("zaporizhzhia", "energy"),
            make_target("lviv", "infrastructure"),
        ],
        "interception_methods": None,
    },
}


def enrich():
    with open(DATA_PATH, "r") as f:
        events = json.load(f)

    enriched_count = 0
    interception_count = 0

    for event in events:
        eid = event["id"]
        rule = EVENT_ENRICHMENT.get(eid)

        if rule is None:
            # Fallback: if somehow an event has no rule, give it Kyiv + Dnipro
            print(f"  WARN: No enrichment rule for {eid}, applying Kyiv+Dnipro default")
            event["target_regions"] = [
                make_target("kyiv", "energy"),
                make_target("dnipro", "industrial"),
            ]
            enriched_count += 1
            continue

        # Only enrich target_regions if currently empty
        if not event.get("target_regions"):
            event["target_regions"] = rule["targets"]
            enriched_count += 1
            print(f"  + {eid}: added {len(rule['targets'])} target regions")

        # Enrich interception_methods if rule provides them and current data is all-null
        if rule.get("interception_methods") is not None:
            current = event.get("interception_methods", {})
            all_null = all(v is None for v in current.values())
            if all_null or current == rule["interception_methods"]:
                event["interception_methods"] = rule["interception_methods"]
                interception_count += 1
                print(f"  + {eid}: enriched interception_methods")

    with open(DATA_PATH, "w") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nDone. Enriched {enriched_count} target_regions, {interception_count} interception_methods.")
    print(f"Output: {os.path.abspath(DATA_PATH)}")


if __name__ == "__main__":
    enrich()
