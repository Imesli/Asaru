#!/usr/bin/env python3
"""Enrich Iran events with additional intelligence from research agent."""

import json

with open("data/iran/events.json") as f:
    events = json.load(f)

# Build lookup
by_id = {e["id"]: e for e in events}

# Enrich March 21 with Diego Garcia IRBM + Natanz + cumulative numbers
e = by_id["IR_20260321_MULTI"]
e["notes"] = (
    "Day 22. War enters 4th week. IRAN FIRED 2 INTERMEDIATE-RANGE BALLISTIC MISSILES AT DIEGO GARCIA "
    "(~4,000km range) — both missed (1 failed mid-flight, 1 possibly intercepted by SM-3). First IRBM use, "
    "revealing greater range than admitted. US-Israel attacked Natanz nuclear enrichment facility (2nd time) — "
    "IAEA confirmed no radiation leak. Cumulative: Hengaw 6th report — 5,900 killed in Iran (5,305 military + "
    "595 civilian), 18,000+ injured. 17 Israeli civilians killed, 3,834 injured. 13 US service members KIA + "
    "6 in KC-135 crash. 886+ killed in Lebanon (111 children), 1M displaced. Oil $112-115/bbl. Iranian attacks "
    "down 90% from early war (Pentagon). 70%+ of Iran's missile launchers neutralized. Ukrainian drone tech "
    "deployed to Gulf for air defense."
)
e["target_regions"].append({
    "name": "Diego Garcia (US-UK base, Indian Ocean)",
    "lat": -7.32,
    "lon": 72.42,
    "target_type": "military"
})

# Enrich March 10 UAE with Strait of Hormuz mining
e = by_id["IR_20260310_UAE"]
e["notes"] += " Same day: Iran began laying mines in Strait of Hormuz. US destroyed 16 Iranian minelayers. Strait effectively closed since Mar 4 — tanker traffic down ~70%."

# Enrich March 12 Iraq with more detail
e = by_id["IR_20260312_IRQ"]
e["notes"] += " Oil tanker Safesea Vishnu (Marshall Islands flag) attacked by Iranian explosive boats near Basra — 1 Indian crew member killed. 21 confirmed attacks on merchant ships by this date. 3 cargo ships struck off Iran's coast including one in Strait of Hormuz."

# Enrich March 12 Israel with Hezbollah joint attack details
e = by_id["IR_20260312_ISR"]
e["notes"] += " 5 hours of sustained fire, 50+ targets across Israel. Iran targeted Palmachim Airbase, Ovda Airbase, Shin Bet HQ. CENTCOM: ~6,000 targets struck in Iran total by this date."

# Enrich March 16 UAE with naval warfare
e = by_id["IR_20260316_UAE"]
e["notes"] += " CENTCOM: 100+ Iranian naval vessels destroyed including all 4 Soleimani-class corvettes. 3rd Iranian ballistic missile intercepted by NATO near Incirlik Air Base, Turkey."

# Enrich March 17 Israel with assassination details
e = by_id["IR_20260317_ISR"]
e["notes"] += " Israel also killed intelligence minister Esmaeil Khatib in overnight airstrike."

# Enrich March 18 Israel with Hengaw numbers
e = by_id["IR_20260318_ISR"]
e["notes"] += " Israel struck South Pars gas field (world's largest) with US coordination — triggering Iran's energy-for-energy retaliation cycle. Hengaw 5th report: 5,300 killed in Iran in 18 days (511 civilians, 4,789 military)."

# Enrich March 19 Israel
e = by_id["IR_20260319_ISR"]
e["notes"] += " 19 Iranian attack waves identified (exceptional day). US F-35 damaged by Iranian fire — emergency landing at US base. Brent crude briefly hit $119/bbl."

# Enrich March 20 Kuwait
e = by_id["IR_20260320_KWT"]
e["notes"] += " Pentagon: Iran drone/missile attacks down 90% from early war days. Trump considering asking Congress for $200B to fund the war."

# Add a new route for the Diego Garcia IRBM
with open("data/iran/routes.json") as f:
    routes = json.load(f)

diego_route = {
    "id": "IR_20260321_MULTI_R01",
    "event_id": "IR_20260321_MULTI",
    "drone_count": None,
    "drone_type": "irbm_shahab_variant",
    "outcome": "missed",
    "waypoints": [
        {"seq": 0, "name": "Central Iran (unknown IRBM site)", "lat": 33.50, "lon": 52.00, "type": "launch", "time_approx": None},
        {"seq": 1, "name": "Southern Iran", "lat": 27.00, "lon": 56.00, "type": "transit", "time_approx": None},
        {"seq": 2, "name": "Arabian Sea", "lat": 15.00, "lon": 65.00, "type": "transit", "time_approx": None},
        {"seq": 3, "name": "Indian Ocean", "lat": 0.00, "lon": 70.00, "type": "transit", "time_approx": None},
        {"seq": 4, "name": "Diego Garcia (US-UK base)", "lat": -7.32, "lon": 72.42, "type": "target", "time_approx": None}
    ],
    "approach_direction": "N",
    "route_type": "ballistic_trajectory",
    "estimated_distance_km": 4000,
    "notes": "IRBM trajectory to Diego Garcia — ~4,000km range. Both missiles missed (1 failed mid-flight, 1 possibly intercepted by SM-3). First use of IRBMs in the war, revealing Iran has greater range than publicly admitted. Unprecedented targeting of Indian Ocean base.",
    "conflict": "iran_2026",
    "sources": [
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/03/21/iran-targeted-but-did-not-hit-diego-garcia-base-with-missiles-wsj.html", "confidence": "news_report"},
        {"name": "Estimated trajectory", "url": None, "confidence": "estimate"}
    ]
}

existing_ids = {r["id"] for r in routes}
if diego_route["id"] not in existing_ids:
    routes.append(diego_route)

routes.sort(key=lambda x: x["event_id"])

with open("data/iran/events.json", "w") as f:
    json.dump(events, f, indent=2)

with open("data/iran/routes.json", "w") as f:
    json.dump(routes, f, indent=2)

print(f"Enriched events. Total: {len(events)}")
print(f"Routes total: {len(routes)}")
