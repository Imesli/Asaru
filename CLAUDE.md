# Asaru — by Imesli

## What this is
Asaru is an open-source visual intelligence platform for mass drone attack data from active conflicts. It combines a structured, machine-readable dataset of drone attack patterns with interactive visualisation. The name "Asaru" means "watch/observe" — it's the product name under Imesli (meaning "voice" in Amazigh/Berber).

## The bigger picture
Asaru is the first building block toward an **automated interceptor assignment engine** — software that takes radar tracks of incoming drone swarms and automatically decides which interceptor drones to launch from which distributed sites, with no human in the loop.

The path:
1. **Asaru dataset + visualisation** (NOW) — structured data of real attack patterns, visualised on a map
2. **Asaru sim** (NEXT) — 2D simulation where you can replay real attacks and test assignment algorithms
3. **Asaru engine** (FUTURE) — the automated assignment system that connects radar to interceptor launch

## Why this matters right now
- Iran is launching thousands of Shahed drones against Gulf states RIGHT NOW (Feb-Mar 2026)
- The US Pentagon admitted this week they're ill-prepared for mass drone attacks
- Ukraine has 3+ years of Shahed attack data — 54,000+ drones launched in 2025 alone
- Ukrainian interceptor drones (Sting, Bullet, Octopus) now account for 70% of Shahed kills over Kyiv
- Nobody has structured this attack data in a machine-readable format with flight path traces
- Nobody has built the automated assignment layer that connects radar to interceptor launch

## Current state
Schema is designed and validated. Example records exist. Validation script works. Now need to:
1. Build the visual frontend (interactive map showing attacks)
2. Populate with real data from sources below
3. The visualisation IS the product — people share maps, not JSON files

## Data schema
Two levels of data, both defined as JSON Schema in `schema/`:

### Attack Events (`schema/attack_event.schema.json`)
One record per attack event (typically one night). Fields include:
- Date, time, duration
- Total drones launched, strike vs decoy split
- Drone types and speeds (Shahed-136, Geran-2, Geran-3, Gerbera decoy, etc.)
- Launch regions with coordinates
- Target regions with coordinates and target type
- Interception rates and methods
- Wave data (multi-wave attacks)
- Source citations with confidence levels (official/verified_osint/osint/news_report/estimate)

### Route Traces (`schema/route_trace.schema.json`)
Individual drone flight paths reconstructed from ground observer reports:
- Ordered waypoint sequences with geocoded coordinates
- Approach direction and route type (direct/circuitous/looping)
- Outcome (intercepted/hit_target/crashed/etc.)
- These are approximate routes through named cities, not GPS tracks — good enough for simulation

## Primary data sources (in order of reliability)

### Tier 1 — Already structured, CSIS-verified
- **PetroIvaniuk Kaggle dataset**: https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine
  - CSV files: missile_attacks_daily.csv and missile_and_UAV.csv
  - Columns: time_start, time_end, model, launch_place, target, launched, destroyed, destroyed_details, carrier, source
  - Covers Sep 2022 - Nov 2024
  - Verified by CSIS against Ukrainian Air Force official numbers

### Tier 2 — Structured in reports, needs extraction
- **ISIS (Institute for Science & International Security)**: https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine
  - Monthly analysis with daily counts, strike/decoy ratios, hit rates, geographic data
  - Covers Jan 2025 - Jan 2026
  - Tables in PDF — clean enough to extract

- **Konrad Adenauer Foundation Air War Monitor**: Published monthly
  - Interception rates by weapon type (drone/cruise/ballistic)
  - Month-over-month trends

### Tier 3 — Semi-structured, high value
- **Shahed Tracker (@ShahedTracker on X/Twitter)**: https://x.com/ShahedTracker
  - Nightly summaries with totals, interception rates, decoy rates
  - FLIGHT PATH DATA — approximate routes like "Mykolaiv > Kirovohrad > Cherkasy > Kyiv > Vinnytsia > Khmelnytskyi"
  - This route data is the most unique and valuable part — nobody else has structured it
  - Monthly aggregates also posted

### Tier 4 — Iran conflict, emerging in real time
- Gulf state defence ministry statements (via news): UAE, Bahrain, Qatar, Kuwait intercept numbers
- CENTCOM statements
- News reporting from Defense News, CNBC, Al Jazeera, etc.
- Data is being generated daily — collecting it NOW means building the only structured record

## Key data points from research

### Ukraine (2025-2026)
- Russia launched 54,538 Shahed-type drones in 2025
- ~60% strike drones, ~40% decoys (since Sep 2025 official split published)
- Peak: 6,297 launched in July 2025 (~203/day)
- Steady state: ~176/day from autumn 2025
- Previously 5 launch sites, expanding to 12-15
- Attacks come in waves from different directions
- Interception rate: peaked at 94-97%, dropped to ~80-84% by late 2025
- Interceptor drones now account for 70%+ of Shahed kills over Kyiv
- 1,500+ interceptor drones deployed per day
- Russia adding countermeasures: rear IR spotlights to blind pilots, evasive manoeuvres, air-to-air missiles on Shaheds
- Geran-3 jet variant: 600 km/h, much harder to intercept

### Iran (Feb-Mar 2026)
- 2,000+ drones and 500+ missiles launched since Feb 28
- UAE: 1,072 drones detected, 1,001 intercepted
- Bahrain: 123 destroyed
- Kuwait: 384 intercepted
- Qatar: 39 detected, 24 intercepted
- US using reverse-engineered Shahed (Lucas drone) in combat for first time
- Pentagon admitted gaps in counter-drone capability

## Tech stack
- No decisions made yet on frontend framework
- Data is JSON with JSON Schema validation
- Python validation script exists at `scripts/validate.py`
- For the visual map: consider a React app with deck.gl or Mapbox GL for rendering attack paths and patterns
- Should be deployable as a static site (GitHub Pages or similar)

## Project structure
```
asaru/
├── CLAUDE.md              # This file
├── README.md              # Public-facing README
├── schema/                # JSON Schema definitions
│   ├── attack_event.schema.json
│   └── route_trace.schema.json
├── data/
│   ├── ukraine/           # Ukraine/Russia conflict data
│   └── iran/              # Iran 2026 conflict data
├── examples/              # Example records for reference
│   ├── example_events.json
│   └── example_routes.json
├── scripts/
│   └── validate.py        # Schema validation + completeness reporting
├── docs/                  # Data dictionary and methodology
└── src/                   # Frontend visualisation (to build)
```

## Immediate tasks
1. Build the visual frontend — interactive map showing attack patterns
2. Pull the Kaggle dataset and transform into our schema
3. Extract 2025 data from ISIS reports
4. Structure Shahed Tracker flight path data (the unique value)
5. Add Iran 2026 conflict data as it emerges
6. Write README and first blog post

## Company context
- **Imesli** = "voice" in Amazigh (Berber). UK-based defence tech startup.
- Founder is an experienced software developer, comfortable with hardware and software
- Open-source first approach — dataset and visualisation are free, future enterprise products are paid
- Target markets: Ukraine (via BRAVE1), UK MOD (via DASA), NATO allies, Gulf states, commercial
- Long-term product: automated interceptor assignment engine (the "brain" between radar and interceptor launch)
