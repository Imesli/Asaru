# Asaru

**Open, machine-readable dataset of mass drone attack patterns from active conflicts.**

Structured data covering Russian Shahed drone campaigns against Ukraine (2022–present) and Iranian drone strikes against Gulf states and US assets (2026–present). Designed for simulation, analysis, and building automated air defence systems.

## Why This Exists

Every night, hundreds of drones attack Ukrainian cities. Iran has launched thousands of drones against Gulf states since February 2026. The data about these attacks exists — in Ukrainian Air Force reports, OSINT trackers, think tank analyses, and news articles. But it's scattered across PDFs, tweets, Telegram channels, and dashboards that aren't machine-readable.

If you're building a drone defence simulation, training an interceptor assignment algorithm, or analysing attack patterns, you need this data in a format you can actually use. That's what this is.

## What's In The Dataset

### Attack Events
Each record is a single attack event (typically one night's campaign) or a monthly aggregate.

Fields include: total drones launched, strike vs decoy breakdown, interception rates, drone types and speeds, launch regions, target regions, wave timing, interception method breakdown, and data provenance with confidence levels.

### Route Traces
Where available, individual drone flight paths reconstructed from ground observer reports and OSINT tracking. Encoded as ordered waypoint sequences with geocoded coordinates.

These are approximate transit routes through named locations — not precise GPS tracks. They're accurate enough for simulation use: realistic attack geometry, approach directions, and the circuitous routing patterns drones use to evade air defences.

## Data Quality

Every record includes source citations and confidence tags:

- **official** — Government or military source (Ukrainian Air Force, Gulf state defence ministries)
- **verified_osint** — Cross-checked by multiple independent OSINT sources (CSIS-verified Kaggle dataset, ISIS reports)
- **osint** — Single OSINT source (Shahed Tracker, monitoring Telegram channels)
- **news_report** — Journalist citing named or unnamed sources
- **estimate** — Calculated or derived from other data

The completeness report (`python scripts/validate.py`) shows exactly which fields are filled and which are sparse. We'd rather have honest gaps than fabricated data.

## Primary Sources

| Source | Type | Coverage | Confidence |
|--------|------|----------|------------|
| Ukrainian Air Force (via PetroIvaniuk/Kaggle) | Daily attack totals | Sep 2022 – Nov 2024 | Official, CSIS-verified |
| ISIS (Institute for Science & International Security) | Monthly analysis with strike/decoy splits | Jan 2025 – Jan 2026 | Verified OSINT |
| Shahed Tracker (@ShahedTracker) | Nightly summaries, route traces | 2024 – present | OSINT |
| Konrad Adenauer Foundation Air War Monitor | Monthly interception rates by weapon type | 2024 – present | Verified OSINT |
| Gulf state defence ministries (via news) | Iran conflict intercept data | Feb 2026 – present | Official (via news reports) |
| CENTCOM statements | Iran conflict totals | Feb 2026 – present | Official |

## Schema

JSON Schema definitions in `schema/`:
- `attack_event.schema.json` — Attack event records
- `route_trace.schema.json` — Flight path records

Run `python scripts/validate.py` to validate all data files and see completeness reports.

## Repo Structure

```
asaru/
├── schema/                    # JSON Schema definitions
│   ├── attack_event.schema.json
│   └── route_trace.schema.json
├── data/
│   ├── ukraine/              # Ukraine/Russia conflict data
│   └── iran/                 # Iran 2026 conflict data
├── examples/                  # Example records for reference
├── scripts/
│   └── validate.py           # Schema validation + completeness reporting
└── docs/                      # Data dictionary and methodology
```

## Usage

```python
import json

# Load attack events
with open('data/ukraine/events_2025.json') as f:
    events = json.load(f)

# Filter to large-scale attacks
large_attacks = [e for e in events if (e['totals']['launched_total'] or 0) > 200]

# Load route traces
with open('data/ukraine/routes_2025.json') as f:
    routes = json.load(f)

# Get routes for a specific event
event_routes = [r for r in routes if r['event_id'] == 'UA_20250907_001']
```

## For Simulation

This dataset is designed to be ingested by air defence simulations. A typical workflow:

1. Load attack events to define threat scenarios
2. Use route traces to generate realistic approach geometries
3. Use strike/decoy ratios to populate simulated threat mixes
4. Use interception rates as validation targets — does your simulated defence achieve similar rates?

## Contributing

This dataset grows through manual extraction from public sources. Contributions welcome:

1. New attack events from Ukrainian Air Force reports or news
2. Route trace data from Shahed Tracker or monitoring channels
3. Iran conflict data as it emerges
4. Corrections to existing records

All contributions must include source citations and confidence levels.

## Licence

Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, share, and adapt with attribution.
Code: MIT

## Related Projects

- [CSIS Russian Firepower Strike Tracker](https://www.csis.org/programs/futures-lab/projects/russian-firepower-strike-tracker-analyzing-missile-attacks-ukraine) — Interactive dashboard of missile attacks
- [PetroIvaniuk/2022-Ukraine-Russia-War-Dataset](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset) — Foundation dataset (CSIS-verified)
- [ISIS Monthly Shahed Analysis](https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine) — Detailed monthly reports

## Context

This project is part of a broader effort to build open tools for automated drone defence. The dataset feeds directly into simulation and assignment algorithm development. If you're working on counter-drone systems, reach out.
