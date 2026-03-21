#!/usr/bin/env python3
"""Fix generated_routes.json: convert 'sources' array to 'source' object as required by schema."""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "ukraine" / "generated_routes.json"

DEFAULT_SOURCE = {
    "name": "Algorithmically interpolated from attack event data",
    "url": None,
    "confidence": "estimate"
}


def main():
    with open(DATA_FILE, "r") as f:
        routes = json.load(f)

    print(f"Loaded {len(routes)} routes")

    fixed = 0
    for route in routes:
        if "source" not in route:
            # Use first entry from 'sources' array if present, otherwise use default
            if "sources" in route and route["sources"]:
                src = route["sources"][0]
                route["source"] = {
                    "name": src.get("name", DEFAULT_SOURCE["name"]),
                    "url": src.get("url"),
                    "confidence": src.get("confidence", "estimate")
                }
            else:
                route["source"] = dict(DEFAULT_SOURCE)
            fixed += 1

        # Remove the non-schema 'sources' field
        route.pop("sources", None)

    with open(DATA_FILE, "w") as f:
        json.dump(routes, f, indent=2, ensure_ascii=False)

    print(f"Fixed {fixed} routes (added 'source', removed 'sources')")
    print(f"Saved to {DATA_FILE}")


if __name__ == "__main__":
    main()
