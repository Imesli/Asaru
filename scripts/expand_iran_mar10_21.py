#!/usr/bin/env python3
"""Add Iran war events and routes for March 10-21, 2026."""

import json

# New events: March 10-21, 2026
NEW_EVENTS = [
    # === MARCH 10 ===
    {
        "id": "IR_20260310_UAE",
        "conflict": "iran_2026",
        "date": "2026-03-10",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 45,
            "launched_drones": 30,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 15,
            "intercepted_total": 38,
            "intercepted_drones": None,
            "hits": 7,
            "lost_location": None,
            "interception_rate": 0.84
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "likely"}
        ],
        "target_regions": [
            {"name": "Ruwais Industrial Complex (ADNOC)", "lat": 24.11, "lon": 52.73, "target_type": "energy"},
            {"name": "Al Dhafra Air Base", "lat": 24.25, "lon": 54.55, "target_type": "military"}
        ],
        "waves": [],
        "interception_methods": {"THAAD": None, "Patriot": None, "Cheongung_II": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "ADNOC forced to shut Ruwais refinery (922,000 bpd capacity) after drone strike set fire to industrial complex. Largest single energy infrastructure hit of the war so far."},
        "notes": "Day 11. Iranian drone strike hit Ruwais Industrial Complex in Abu Dhabi, housing UAE's largest oil refinery. ADNOC halted operations. Fire visible on satellite imagery. Major escalation in energy infrastructure targeting.",
        "sources": [
            {"name": "The National", "url": "https://www.thenationalnews.com/business/energy/2026/03/10/fire-breaks-out-at-al-ruwais-refinery-in-uae-after-drone-strike/", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "Ukrainska Pravda", "url": "https://www.pravda.com.ua/eng/news/2026/03/10/8024859/", "confidence": "news_report", "fields_sourced": ["totals"]}
        ]
    },
    {
        "id": "IR_20260310_BHR",
        "conflict": "iran_2026",
        "date": "2026-03-10",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "drone",
        "totals": {
            "launched_total": 8,
            "launched_drones": 8,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": None,
            "intercepted_total": 5,
            "intercepted_drones": 5,
            "hits": 3,
            "lost_location": None,
            "interception_rate": 0.63
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Manama Al Seef residential area", "lat": 26.23, "lon": 50.56, "target_type": "civilian"},
            {"name": "Sitra petroleum refinery", "lat": 26.15, "lon": 50.63, "target_type": "energy"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Drone strike on Al Seef residential building killed 29-year-old woman, injured 8. Separate strike near Sitra refinery injured 32 Bahrainis (4 serious)."},
        "notes": "Day 11. Drone strike on residential building in Al Seef, Manama killed a 29-year-old woman and injured 8 others. Separate attack near petroleum refinery in Sitra injured 32 Bahraini citizens.",
        "sources": [
            {"name": "Wikipedia - 2026 Iranian strikes on Bahrain", "url": "https://en.wikipedia.org/wiki/2026_Iranian_strikes_on_Bahrain", "confidence": "news_report", "fields_sourced": ["totals", "notes"]}
        ]
    },
    {
        "id": "IR_20260310_ISR",
        "conflict": "iran_2026",
        "date": "2026-03-10",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "ballistic_missile",
        "totals": {
            "launched_total": 10,
            "launched_drones": None,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 10,
            "intercepted_total": 7,
            "intercepted_drones": None,
            "hits": 3,
            "lost_location": None,
            "interception_rate": 0.70
        },
        "drone_types": [],
        "launch_regions": [
            {"name": "Western Iran (Kermanshah)", "lat": 34.31, "lon": 47.06, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Tel Aviv metropolitan area", "lat": 32.07, "lon": 34.78, "target_type": "urban"}
        ],
        "waves": [{"wave_number": 1, "time_start": None, "drone_count": None, "direction": "E", "notes": "10 ballistic missiles with multiple warheads targeting Tel Aviv. 124 people injured."}],
        "interception_methods": {"Arrow_3": None, "Iron_Dome": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "10 ballistic missiles with multiple warheads fired at Tel Aviv. 124 people injured. Multiple warhead technology complicates interception."},
        "notes": "Day 11. Iran fired 10 ballistic missiles with multiple warheads at Tel Aviv. Israel reported 124 people injured. Multiple warhead missiles represent escalation in lethality.",
        "sources": [
            {"name": "Alma Research Center", "url": "https://israel-alma.org/daily-report-the-second-iran-war-march-10-2026-1800/", "confidence": "verified_osint", "fields_sourced": ["totals", "waves", "notes"]}
        ]
    },

    # === MARCH 11-12 ===
    {
        "id": "IR_20260312_BHR",
        "conflict": "iran_2026",
        "date": "2026-03-12",
        "time_start": "2026-03-11T22:00:00Z",
        "time_end": "2026-03-12T06:00:00Z",
        "duration_hours": 8,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 15,
            "launched_drones": 12,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 3,
            "intercepted_total": 10,
            "intercepted_drones": None,
            "hits": 5,
            "lost_location": None,
            "interception_rate": 0.67
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Bahrain International Airport (Muharraq)", "lat": 26.27, "lon": 50.63, "target_type": "infrastructure"},
            {"name": "Muharraq fuel depot", "lat": 26.26, "lon": 50.62, "target_type": "energy"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Iranian drones hit Bahrain International Airport on Muharraq Island, setting fuel tanks on fire. Interior ministry confirmed airport targeted — material damage but no loss of life at airport."},
        "notes": "Night of Mar 11-12. Iranian drones struck Bahrain International Airport on Muharraq Island, setting fuel tanks on fire. Also struck fuel depot in Muharraq Governorate causing large fire. BDF has intercepted 112 ballistic missiles and 186 drones total since war began.",
        "sources": [
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/bahrain-international-airport-under-direct-attack-as-iranian-drone-strike-sets-fire-to-crucial-fuel-storage-facility-amplifying-regional-tensions/", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "Middle East Eye", "url": "https://www.middleeasteye.net/live-blog/live-blog-update/bahrain-says-drone-strike-damaged-airport", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
    {
        "id": "IR_20260312_IRQ",
        "conflict": "iran_2026",
        "date": "2026-03-12",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 20,
            "launched_drones": 12,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 8,
            "intercepted_total": 14,
            "intercepted_drones": None,
            "hits": 6,
            "lost_location": None,
            "interception_rate": 0.70
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Coalition base near Erbil", "lat": 36.19, "lon": 44.01, "target_type": "military"},
            {"name": "Coalition base near Baghdad", "lat": 33.31, "lon": 44.37, "target_type": "military"}
        ],
        "waves": [],
        "interception_methods": {"Patriot": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Iranian drones and missiles hit coalition military camps near Erbil and Baghdad, wounding US soldiers. Oil tanker Safesea Vishnu attacked by Iranian explosive boats near Basra — 1 Indian crew member killed."},
        "notes": "Day 13. Iranian strikes hit coalition bases near Erbil and Baghdad, wounding US soldiers. Oil tanker Safesea Vishnu attacked near Basra by Iranian explosive boats — 1 crew member killed. 6 US airmen killed when KC-135 tanker crashed in western Iraq during operations.",
        "sources": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/12/iran-targets-gulf-nations-with-missiles-drones-as-oil-prices-soar", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "Wikipedia - Timeline of 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_2026_Iran_war", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
    {
        "id": "IR_20260312_ISR",
        "conflict": "iran_2026",
        "date": "2026-03-12",
        "time_start": "2026-03-12T11:55:00Z",
        "time_end": "2026-03-12T12:35:00Z",
        "duration_hours": 0.67,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 30,
            "launched_drones": 15,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 15,
            "intercepted_total": 24,
            "intercepted_drones": None,
            "hits": 6,
            "lost_location": None,
            "interception_rate": 0.80
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Western Iran (Kermanshah)", "lat": 34.31, "lon": 47.06, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Lebanon (Hezbollah)", "lat": 33.87, "lon": 35.51, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Northern Israel", "lat": 32.80, "lon": 35.50, "target_type": "military"},
            {"name": "Central Israel", "lat": 32.07, "lon": 34.78, "target_type": "urban"}
        ],
        "waves": [{"wave_number": 1, "time_start": "2026-03-12T11:55:00Z", "drone_count": None, "direction": "E", "notes": "Combined rockets, missiles, drones from Lebanon (N) and Iran (E). At 12:35 UTC Israel struck Hezbollah targets in southern Lebanon."}],
        "interception_methods": {"Arrow_3": None, "Iron_Dome": None, "Davids_Sling": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Combined attack from Lebanon and Iran simultaneously — coordinated multi-axis strike. Israel responded with strikes on Hezbollah targets in southern Lebanon."},
        "notes": "Day 13. Coordinated multi-axis attack: rockets/missiles/drones from Lebanon (north) and Iran (east) simultaneously between 11:55-12:35 UTC. Israel struck Hezbollah targets in southern Lebanon in response.",
        "sources": [
            {"name": "Wikipedia - Timeline of 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_2026_Iran_war", "confidence": "news_report", "fields_sourced": ["totals", "waves", "notes"]}
        ]
    },

    # === MARCH 13 ===
    {
        "id": "IR_20260313_SAU",
        "conflict": "iran_2026",
        "date": "2026-03-13",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "drone",
        "totals": {
            "launched_total": 50,
            "launched_drones": 50,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": None,
            "intercepted_total": 43,
            "intercepted_drones": 43,
            "hits": 7,
            "lost_location": None,
            "interception_rate": 0.86
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Prince Sultan Air Base (Al-Kharj)", "lat": 24.06, "lon": 47.58, "target_type": "military"},
            {"name": "Dhahran military installations", "lat": 26.27, "lon": 50.14, "target_type": "military"},
            {"name": "Riyadh area", "lat": 24.71, "lon": 46.68, "target_type": "urban"}
        ],
        "waves": [{"wave_number": 1, "time_start": None, "drone_count": 50, "direction": "NE", "notes": "50 drones targeting Saudi Arabia within hours — largest single drone wave against the kingdom."}],
        "interception_methods": {"Patriot": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Saudi intercepted 2 ballistic missiles targeting Prince Sultan Air Base. 50 drones launched within hours — largest wave against Saudi Arabia in the war."},
        "notes": "Day 14. Saudi Arabia targeted with 50 drones within hours — largest single wave against the kingdom. Saudi MoD intercepted 2 ballistic missiles toward Prince Sultan Air Base at Al-Kharj. Shelter-in-place for Jeddah, Riyadh, Dhahran.",
        "sources": [
            {"name": "The National", "url": "https://www.thenationalnews.com/news/gulf/2026/03/13/saudi-arabia-targeted-with-50-drones-in-hours-as-iran-launches-new-wave-of-attacks-on-gulf/", "confidence": "news_report", "fields_sourced": ["totals", "target_regions", "notes"]}
        ]
    },

    # === MARCH 14 ===
    {
        "id": "IR_20260314_IRQ",
        "conflict": "iran_2026",
        "date": "2026-03-14",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "drone",
        "totals": {
            "launched_total": 5,
            "launched_drones": 5,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": None,
            "intercepted_total": 3,
            "intercepted_drones": 3,
            "hits": 2,
            "lost_location": None,
            "interception_rate": 0.60
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Baghdad Green Zone (Royal Tulip Hotel)", "lat": 33.31, "lon": 44.38, "target_type": "diplomatic"},
            {"name": "Baghdad (Kata'ib Hezbollah target)", "lat": 33.30, "lon": 44.40, "target_type": "military"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Drone struck Royal Tulip Al Rasheed Hotel hosting EU and Saudi Arabian delegation. Kata'ib Hezbollah commander Abu Ali al-Askari killed in separate airstrike."},
        "notes": "Day 15. Drone struck first two floors of Royal Tulip Al Rasheed Hotel in Baghdad Green Zone, hosting EU and Saudi delegation. Kata'ib Hezbollah security commander Abu Ali al-Askari killed in separate airstrike on Baghdad.",
        "sources": [
            {"name": "Wikipedia - Timeline of 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_2026_Iran_war", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "FDD Long War Journal", "url": "https://www.longwarjournal.org/archives/2026/03/iranian-drones-and-missiles-hit-regional-oil-fields-airports-military-bases-and-ports-march-13-16-updates.php", "confidence": "verified_osint", "fields_sourced": ["notes"]}
        ]
    },

    # === MARCH 16 ===
    {
        "id": "IR_20260316_UAE",
        "conflict": "iran_2026",
        "date": "2026-03-16",
        "time_start": "2026-03-16T02:00:00Z",
        "time_end": "2026-03-16T10:00:00Z",
        "duration_hours": 8,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 35,
            "launched_drones": 25,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 10,
            "intercepted_total": 30,
            "intercepted_drones": None,
            "hits": 5,
            "lost_location": None,
            "interception_rate": 0.86
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "likely"}
        ],
        "target_regions": [
            {"name": "Dubai International Airport", "lat": 25.25, "lon": 55.36, "target_type": "infrastructure"},
            {"name": "Shah Gas Field (ADNOC/Occidental)", "lat": 23.55, "lon": 53.77, "target_type": "energy"},
            {"name": "Abu Dhabi", "lat": 24.45, "lon": 54.65, "target_type": "urban"}
        ],
        "waves": [],
        "interception_methods": {"THAAD": None, "Patriot": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Shahed-type drone struck fuel storage tank at Dubai International Airport, sparking large fire. Flights suspended 7+ hours. At least 1 killed in Abu Dhabi. Shah gas field also struck. As of Mar 17: 314 ballistic missiles, 15 cruise missiles, 1,672 UAVs fired at UAE total."},
        "notes": "Day 17. Shahed drone hit fuel tank outside Dubai International Airport — world's busiest airport suspended flights 7+ hours. Drone strike also sparked fire at Shah gas field. 1 killed in Abu Dhabi. Cumulative total as of Mar 17: 314 ballistic missiles, 15 cruise missiles, 1,672 UAVs fired at UAE. 8 killed, 157 injured total.",
        "sources": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/16/drone-strike-disrupts-dubai-flights-as-iran-continues-gulf-attacks", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "CNBC", "url": "https://www.cnbc.com/2026/03/16/dubai-airport-suspends-flights-drone-attack.html", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Wikipedia - 2026 Iranian strikes on UAE", "url": "https://en.wikipedia.org/wiki/2026_Iranian_strikes_on_the_United_Arab_Emirates", "confidence": "news_report", "fields_sourced": ["totals"]}
        ]
    },

    # === MARCH 17 ===
    {
        "id": "IR_20260317_ISR",
        "conflict": "iran_2026",
        "date": "2026-03-17",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "ballistic_missile",
        "totals": {
            "launched_total": 20,
            "launched_drones": None,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 20,
            "intercepted_total": 16,
            "intercepted_drones": None,
            "hits": 4,
            "lost_location": None,
            "interception_rate": 0.80
        },
        "drone_types": [],
        "launch_regions": [
            {"name": "Western Iran (Kermanshah)", "lat": 34.31, "lon": 47.06, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Tabriz North", "lat": 38.25, "lon": 46.13, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Ramat Gan (Tel Aviv metro)", "lat": 32.08, "lon": 34.81, "target_type": "urban"},
            {"name": "Northern Israel", "lat": 32.80, "lon": 35.50, "target_type": "urban"}
        ],
        "waves": [],
        "interception_methods": {"Arrow_3": None, "Iron_Dome": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Retaliatory barrage after Israeli airstrikes killed senior officials Ali Larijani and Basij chief Gholamreza Soleimani. 2 Israeli civilians killed in Ramat Gan. Israel launched ground invasion of southern Lebanon same day."},
        "notes": "Day 18. Iran launched retaliatory missile barrage after Israel killed senior officials Ali Larijani and Basij commander Gholamreza Soleimani. 2 Israeli civilians killed in Ramat Gan. Israel launched ground invasion of southern Lebanon the same day.",
        "sources": [
            {"name": "Alma Research Center", "url": "https://israel-alma.org/daily-report-second-iran-war-march-17-2026-1600/", "confidence": "verified_osint", "fields_sourced": ["totals", "notes"]},
            {"name": "Wikipedia - Timeline of 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_2026_Iran_war", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
    {
        "id": "IR_20260317_LBN",
        "conflict": "iran_2026",
        "date": "2026-03-17",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "ground_invasion",
        "totals": {
            "launched_total": None,
            "launched_drones": None,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": None,
            "intercepted_total": None,
            "intercepted_drones": None,
            "hits": None,
            "lost_location": None,
            "interception_rate": None
        },
        "drone_types": [],
        "launch_regions": [
            {"name": "Northern Israel border", "lat": 33.10, "lon": 35.20, "bearing_deg": None, "confidence": "official"}
        ],
        "target_regions": [
            {"name": "Southern Lebanon (Hezbollah infrastructure)", "lat": 33.27, "lon": 35.20, "target_type": "military"},
            {"name": "Beirut (Hezbollah HQ)", "lat": 33.89, "lon": 35.50, "target_type": "military"},
            {"name": "Beqaa Valley", "lat": 33.85, "lon": 36.00, "target_type": "military"},
            {"name": "Sidon", "lat": 33.56, "lon": 35.37, "target_type": "military"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "IDF struck ~400 Hezbollah targets: missile launchers, observation systems, weapons storage, HQs across Beirut, Beqaa, Sidon, and southern Lebanon. Ground invasion of southern Lebanon launched same day."},
        "notes": "Day 18. Israel launched ground invasion of southern Lebanon. IDF completed dozens of waves of strikes against Hezbollah infrastructure — about 400 targets struck including missile launchers, observation systems, weapons storage, and headquarters across Beirut, Beqaa, Sidon, and southern Lebanon.",
        "sources": [
            {"name": "Wikipedia - Timeline of 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_2026_Iran_war", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]}
        ]
    },

    # === MARCH 18 ===
    {
        "id": "IR_20260318_QAT",
        "conflict": "iran_2026",
        "date": "2026-03-18",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 30,
            "launched_drones": 20,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 10,
            "intercepted_total": 18,
            "intercepted_drones": None,
            "hits": 12,
            "lost_location": None,
            "interception_rate": 0.60
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "likely"}
        ],
        "target_regions": [
            {"name": "Ras Laffan Industrial City (LNG)", "lat": 25.91, "lon": 51.56, "target_type": "energy"},
            {"name": "Mesaieed Industrial City", "lat": 24.98, "lon": 51.55, "target_type": "energy"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Major strike on Ras Laffan gas facility caused extensive damage and sizeable fires at multiple LNG facilities. QatarEnergy CEO said attack cut ~17% of output potentially for 5 years. Qatar expelled Iranian military/security attaches within 24 hours."},
        "notes": "Day 19. MAJOR ESCALATION. Iran struck Qatar's Ras Laffan LNG facility causing 'extensive damage' and fires at multiple facilities. QatarEnergy CEO: ~17% of output cut, potentially for 5 years. Qatar declared Iranian embassy military attaches persona non grata — expelled within 24 hours. Retaliation for Israel's strike on Iran's South Pars gas field.",
        "sources": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/18/qatar-says-iran-missile-attack-sparks-fire-causes-damage-at-gas-facility", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "CNBC", "url": "https://www.cnbc.com/2026/03/18/iran-war-qatar-ras-laffan-natural-gas-lng.html", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
    {
        "id": "IR_20260318_ISR",
        "conflict": "iran_2026",
        "date": "2026-03-18",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "ballistic_missile",
        "totals": {
            "launched_total": 35,
            "launched_drones": 10,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 25,
            "intercepted_total": 25,
            "intercepted_drones": None,
            "hits": 10,
            "lost_location": None,
            "interception_rate": 0.71
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Western Iran (Kermanshah)", "lat": 34.31, "lon": 47.06, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Tabriz North", "lat": 38.25, "lon": 46.13, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Tel Aviv", "lat": 32.07, "lon": 34.78, "target_type": "urban"},
            {"name": "Jerusalem Old City", "lat": 31.78, "lon": 35.23, "target_type": "religious"},
            {"name": "Beit Shemesh", "lat": 31.75, "lon": 34.99, "target_type": "urban"},
            {"name": "Central Israel (Hod Hasharon)", "lat": 32.15, "lon": 34.89, "target_type": "urban"}
        ],
        "waves": [
            {"wave_number": 1, "time_start": None, "drone_count": None, "direction": "E", "notes": "13 waves total: 6 toward Tel Aviv (46.2%), 4 toward south (30.8%), 2 toward Jerusalem (15.4%), 1 toward north (7.7%)."},
        ],
        "interception_methods": {"Arrow_3": None, "Iron_Dome": None, "Davids_Sling": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "13 attack waves. Missile debris fell on Temple Mount (Al-Aqsa Mosque damage), Church of Holy Sepulchre, and Jewish Quarter. Synagogue shelter in Beit Shemesh struck — 9 civilians killed, dozens injured. 1 foreign worker killed near Hod Hasharon. 1 killed in Tel Aviv building strike."},
        "notes": "Day 19. Iran 'revenge' missile attack: 13 waves. Missile debris hit Temple Mount/Al-Aqsa, Church of Holy Sepulchre, Jewish Quarter in Jerusalem Old City. Synagogue shelter in Beit Shemesh struck — 9 civilians killed. Foreign worker killed in Moshav Adanim. Building struck in Tel Aviv killing 1. IRGC said attacks avenged Larijani assassination.",
        "sources": [
            {"name": "Times of Israel", "url": "https://www.timesofisrael.com/liveblog-march-18-2026/", "confidence": "news_report", "fields_sourced": ["target_regions", "waves", "notes"]},
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/18/iran-launches-revenge-missile-attack-on-israel-after-assassinations", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Alma Research Center", "url": "https://israel-alma.org/daily-report-the-second-iran-war-march-19-2026-1800/", "confidence": "verified_osint", "fields_sourced": ["waves"]}
        ]
    },
    {
        "id": "IR_20260318_UAE",
        "conflict": "iran_2026",
        "date": "2026-03-18",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 40,
            "launched_drones": 30,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 10,
            "intercepted_total": 34,
            "intercepted_drones": None,
            "hits": 6,
            "lost_location": None,
            "interception_rate": 0.85
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "likely"}
        ],
        "target_regions": [
            {"name": "Abu Dhabi", "lat": 24.45, "lon": 54.65, "target_type": "urban"},
            {"name": "Dubai", "lat": 25.20, "lon": 55.27, "target_type": "urban"},
            {"name": "Al Dhafra Air Base", "lat": 24.25, "lon": 54.55, "target_type": "military"}
        ],
        "waves": [],
        "interception_methods": {"THAAD": None, "Patriot": None, "Cheongung_II": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Continued attacks on UAE. Iran declared 'not a single liter of oil' would ship from the Gulf. UAE Foreign Ministry called attacks 'Terrorist Attacks' on Mar 19."},
        "notes": "Day 19. Continued drone and missile attacks on UAE. Iran threatened that 'not a single liter of oil' would ship from the Gulf. Part of broader energy infrastructure escalation after Israel struck South Pars gas field.",
        "sources": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/18/iran-fires-missiles-drones-across-gulf-region-remains-in-war-crosshairs", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Times of Israel", "url": "https://www.timesofisrael.com/iran-keeps-up-attacks-on-gulf-states-says-not-a-single-liter-of-oil-will-ship-out/", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },

    # === MARCH 19 ===
    {
        "id": "IR_20260319_ISR",
        "conflict": "iran_2026",
        "date": "2026-03-19",
        "time_start": None,
        "time_end": None,
        "duration_hours": 1,
        "attack_type": "ballistic_missile",
        "totals": {
            "launched_total": 25,
            "launched_drones": None,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 25,
            "intercepted_total": 19,
            "intercepted_drones": None,
            "hits": 6,
            "lost_location": None,
            "interception_rate": 0.76
        },
        "drone_types": [],
        "launch_regions": [
            {"name": "Western Iran (Kermanshah)", "lat": 34.31, "lon": 47.06, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Tabriz North", "lat": 38.25, "lon": 46.13, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Jerusalem", "lat": 31.78, "lon": 35.23, "target_type": "urban"},
            {"name": "Northern Israel", "lat": 32.80, "lon": 35.50, "target_type": "urban"},
            {"name": "Haifa (Bazan Oil Refinery)", "lat": 32.82, "lon": 35.00, "target_type": "energy"}
        ],
        "waves": [
            {"wave_number": 1, "time_start": None, "drone_count": None, "direction": "E", "notes": "5 missile salvos at Jerusalem and northern Israel within 1 hour."},
        ],
        "interception_methods": {"Arrow_3": None, "Iron_Dome": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "5 missile salvos at Jerusalem and northern Israel within 1 hour. Bazan oil refinery in Haifa damaged."},
        "notes": "Day 20. Iran launched 5 missile salvos at Jerusalem and northern Israel within one hour. Bazan oil refinery in Haifa damaged. Continued energy infrastructure targeting on both sides — Brent crude hit $115/barrel.",
        "sources": [
            {"name": "Times of Israel", "url": "https://www.timesofisrael.com/liveblog-march-19-2026/", "confidence": "news_report", "fields_sourced": ["target_regions", "waves", "notes"]},
            {"name": "Jerusalem Post", "url": "https://www.jpost.com/israel-news/defense-news/article-890480", "confidence": "news_report", "fields_sourced": ["target_regions"]}
        ]
    },

    # === MARCH 20 ===
    {
        "id": "IR_20260320_KWT",
        "conflict": "iran_2026",
        "date": "2026-03-20",
        "time_start": "2026-03-20T01:00:00Z",
        "time_end": None,
        "duration_hours": None,
        "attack_type": "drone",
        "totals": {
            "launched_total": 15,
            "launched_drones": 15,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": None,
            "intercepted_total": 10,
            "intercepted_drones": 10,
            "hits": 5,
            "lost_location": None,
            "interception_rate": 0.67
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Mina Al-Ahmadi Refinery", "lat": 29.06, "lon": 48.15, "target_type": "energy"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Iranian drones struck Mina Al-Ahmadi refinery (730,000 bpd capacity) — Kuwait's largest. Fires at several operational units. Hit during Eid al-Fitr celebrations. No injuries reported. Refinery had been hit day before as well."},
        "notes": "Day 21. Iranian drones struck Kuwait's Mina Al-Ahmadi refinery (730,000 bpd), the country's largest, sparking fires at several units. Attack came during Eid al-Fitr. Part of Iran's broadening campaign against Gulf energy infrastructure after Israel struck South Pars gas field.",
        "sources": [
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/20/kuwait-oil-refinery-hit-again-as-iran-targets-gulf-energy-infrastructure", "confidence": "news_report", "fields_sourced": ["target_regions", "notes"]},
            {"name": "US News", "url": "https://www.usnews.com/news/us/articles/2026-03-20/kuwait-says-its-mina-al-ahmadi-refinery-again-hit-in-iranian-drone-attacks-starting-fire", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "NPR", "url": "https://www.npr.org/2026/03/20/nx-s1-5754550/israel-strikes-tehran-iran-attacks-gulf", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
    {
        "id": "IR_20260320_SAU",
        "conflict": "iran_2026",
        "date": "2026-03-20",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 25,
            "launched_drones": 18,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 7,
            "intercepted_total": 21,
            "intercepted_drones": None,
            "hits": 4,
            "lost_location": None,
            "interception_rate": 0.84
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "Prince Sultan Air Base (Al-Kharj)", "lat": 24.06, "lon": 47.58, "target_type": "military"},
            {"name": "Ras Tanura oil terminal", "lat": 26.64, "lon": 50.17, "target_type": "energy"}
        ],
        "waves": [],
        "interception_methods": {"Patriot": None},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "Continued attacks on Saudi military and energy infrastructure. Iran launched retaliatory strikes after Larijani killing. Part of broader energy escalation."},
        "notes": "Day 21. Continued Iranian strikes on Saudi Arabia targeting Prince Sultan Air Base and energy infrastructure. Part of energy-for-energy escalation cycle after Israel struck South Pars. Trump said considering 'winding down' military ops same day.",
        "sources": [
            {"name": "NPR", "url": "https://www.npr.org/2026/03/20/nx-s1-5754550/israel-strikes-tehran-iran-attacks-gulf", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "CNBC", "url": "https://www.cnbc.com/2026/03/20/trump-iran-war-ceasefire.html", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },

    # === MARCH 21 ===
    {
        "id": "IR_20260321_MULTI",
        "conflict": "iran_2026",
        "date": "2026-03-21",
        "time_start": None,
        "time_end": None,
        "duration_hours": None,
        "attack_type": "combined_drone_missile",
        "totals": {
            "launched_total": 60,
            "launched_drones": 40,
            "launched_drones_strike": None,
            "launched_drones_decoy": None,
            "launched_missiles_cruise": None,
            "launched_missiles_ballistic": 20,
            "intercepted_total": 48,
            "intercepted_drones": None,
            "hits": 12,
            "lost_location": None,
            "interception_rate": 0.80
        },
        "drone_types": [{"model": "shahed_136", "count": None, "speed_kmh": 185}],
        "launch_regions": [
            {"name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Isfahan (Badr Air Base)", "lat": 32.62, "lon": 51.70, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Hajiabad Missile Base", "lat": 28.30, "lon": 55.90, "bearing_deg": None, "confidence": "estimated"},
            {"name": "Tabriz North", "lat": 38.25, "lon": 46.13, "bearing_deg": None, "confidence": "estimated"}
        ],
        "target_regions": [
            {"name": "UAE (multiple targets)", "lat": 24.45, "lon": 54.65, "target_type": "military"},
            {"name": "Saudi Arabia (multiple targets)", "lat": 24.71, "lon": 46.68, "target_type": "military"},
            {"name": "Kuwait (multiple targets)", "lat": 29.38, "lon": 47.99, "target_type": "military"},
            {"name": "Israel (multiple targets)", "lat": 32.07, "lon": 34.78, "target_type": "urban"}
        ],
        "waves": [],
        "interception_methods": {},
        "defence_context": {"interceptor_drones_deployed": None, "sorties_flown": None,
            "notes": "War enters 4th week. No ceasefire — Iran FM: 'We don't ask for ceasefire but war must end.' Trump considering 'winding down' but more Marines deploying. Cumulative: 1,444+ dead in Iran, 18+ in Israel, 21+ in Gulf states. Brent crude at $112-115/barrel."},
        "notes": "Day 22. War enters 4th week with continued multi-country strikes. No ceasefire in sight — both sides reject negotiations. Cumulative toll: 1,444+ killed in Iran (204 children), 18+ in Israel, 21 in Gulf states. 18,000+ injured in Iran. US struck 7,000+ targets in Iran. Oil prices at $112-115/barrel. Ukrainian drone tech reportedly deployed to Gulf states for air defense.",
        "sources": [
            {"name": "NPR", "url": "https://www.npr.org/2026/03/21/nx-s1-5755539/iran-war-fourth-week", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Salon", "url": "https://www.salon.com/2026/03/21/how-iran-war-became-a-worst-case-scenario-for-gulf-states/", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/3/20/iran-war-what-is-happening-on-day-21-of-us-israel-attacks", "confidence": "news_report", "fields_sourced": ["notes"]},
            {"name": "Mining Awareness", "url": "https://miningawareness.wordpress.com/2026/03/21/iran-still-attacking-arab-neighbors-ukraines-tech-deployed-in-middle-east-to-protect-civilians-key-infrastructure-against-iranian-air-attacks/", "confidence": "news_report", "fields_sourced": ["notes"]}
        ]
    },
]

# New routes for the new events
NEW_ROUTES = [
    # Mar 10 — Ruwais ADNOC strike
    {
        "id": "IR_20260310_UAE_R01",
        "event_id": "IR_20260310_UAE",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Isfahan", "lat": 32.65, "lon": 51.68, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Shiraz", "lat": 29.59, "lon": 52.58, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Bushehr coast", "lat": 28.97, "lon": 50.84, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Persian Gulf crossing", "lat": 26.50, "lon": 52.00, "type": "transit", "time_approx": None},
            {"seq": 4, "name": "Ruwais Industrial Complex", "lat": 24.11, "lon": 52.73, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "direct",
        "estimated_distance_km": 1200,
        "notes": "Strike route to Ruwais/ADNOC refinery. Drone hit industrial complex causing fire, forcing shutdown of 922,000 bpd refinery.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 10 — Bahrain residential
    {
        "id": "IR_20260310_BHR_R01",
        "event_id": "IR_20260310_BHR",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Hajiabad", "lat": 28.30, "lon": 55.90, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Persian Gulf", "lat": 27.00, "lon": 53.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Qatar coast", "lat": 26.00, "lon": 51.50, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Manama (Al Seef)", "lat": 26.23, "lon": 50.56, "type": "target", "time_approx": None}
        ],
        "approach_direction": "E",
        "route_type": "direct",
        "estimated_distance_km": 700,
        "notes": "Drone struck residential building in Al Seef, Manama. 1 woman killed, 8 injured.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 12 — Bahrain airport
    {
        "id": "IR_20260312_BHR_R01",
        "event_id": "IR_20260312_BHR",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Hajiabad", "lat": 28.30, "lon": 55.90, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Persian Gulf", "lat": 27.00, "lon": 53.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Bahrain approach", "lat": 26.50, "lon": 50.80, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Bahrain International Airport (Muharraq)", "lat": 26.27, "lon": 50.63, "type": "target", "time_approx": None}
        ],
        "approach_direction": "E",
        "route_type": "direct",
        "estimated_distance_km": 700,
        "notes": "Drone struck Bahrain airport on Muharraq Island, setting fuel tanks on fire.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 12 — Iraq coalition bases
    {
        "id": "IR_20260312_IRQ_R01",
        "event_id": "IR_20260312_IRQ",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Iraq border", "lat": 34.50, "lon": 45.50, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Erbil (coalition base)", "lat": 36.19, "lon": 44.01, "type": "target", "time_approx": None}
        ],
        "approach_direction": "E",
        "route_type": "direct",
        "estimated_distance_km": 350,
        "notes": "Strike on coalition military camp near Erbil. US soldiers wounded.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 13 — Saudi Arabia 50-drone wave
    {
        "id": "IR_20260313_SAU_R01",
        "event_id": "IR_20260313_SAU",
        "drone_count": 50,
        "drone_type": "shahed_136",
        "outcome": "intercepted",
        "waypoints": [
            {"seq": 0, "name": "Isfahan", "lat": 32.65, "lon": 51.68, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Persian Gulf crossing", "lat": 28.00, "lon": 50.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Bahrain strait", "lat": 26.50, "lon": 50.50, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Saudi eastern coast", "lat": 26.27, "lon": 50.14, "type": "transit", "time_approx": None},
            {"seq": 4, "name": "Prince Sultan Air Base (Al-Kharj)", "lat": 24.06, "lon": 47.58, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "circuitous",
        "estimated_distance_km": 1400,
        "notes": "Largest single drone wave against Saudi Arabia — 50 drones within hours. Most intercepted by Patriot systems.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 16 — Dubai airport
    {
        "id": "IR_20260316_UAE_R01",
        "event_id": "IR_20260316_UAE",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Hajiabad", "lat": 28.30, "lon": 55.90, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Strait of Hormuz", "lat": 26.56, "lon": 56.25, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Sharjah coast", "lat": 25.40, "lon": 55.50, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Dubai International Airport", "lat": 25.25, "lon": 55.36, "type": "target", "time_approx": None}
        ],
        "approach_direction": "E",
        "route_type": "direct",
        "estimated_distance_km": 350,
        "notes": "Shahed drone hit fuel storage tank at Dubai Int'l Airport. Flights suspended 7+ hours. World's busiest airport by international passengers.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 16 — Shah gas field
    {
        "id": "IR_20260316_UAE_R02",
        "event_id": "IR_20260316_UAE",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Isfahan", "lat": 32.65, "lon": 51.68, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Shiraz", "lat": 29.59, "lon": 52.58, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Persian Gulf coast", "lat": 27.00, "lon": 52.50, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "UAE interior", "lat": 24.50, "lon": 54.00, "type": "transit", "time_approx": None},
            {"seq": 4, "name": "Shah Gas Field", "lat": 23.55, "lon": 53.77, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "direct",
        "estimated_distance_km": 1250,
        "notes": "Drone struck Shah gas field operated by ADNOC/Occidental, sparking fire.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 18 — Qatar Ras Laffan LNG
    {
        "id": "IR_20260318_QAT_R01",
        "event_id": "IR_20260318_QAT",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Isfahan", "lat": 32.65, "lon": 51.68, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Bushehr coast", "lat": 28.97, "lon": 50.84, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Persian Gulf", "lat": 27.00, "lon": 51.50, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Ras Laffan Industrial City", "lat": 25.91, "lon": 51.56, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "direct",
        "estimated_distance_km": 800,
        "notes": "Strike on Qatar's Ras Laffan LNG facility — world's largest LNG complex. 'Extensive damage' cutting ~17% of output potentially for 5 years.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 18 — Jerusalem/Beit Shemesh
    {
        "id": "IR_20260318_ISR_R01",
        "event_id": "IR_20260318_ISR",
        "drone_count": None,
        "drone_type": "emad_ballistic",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Kermanshah", "lat": 34.31, "lon": 47.06, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Iraq airspace", "lat": 33.50, "lon": 44.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Jordan airspace", "lat": 32.00, "lon": 37.00, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Jerusalem Old City", "lat": 31.78, "lon": 35.23, "type": "target", "time_approx": None}
        ],
        "approach_direction": "E",
        "route_type": "ballistic_trajectory",
        "estimated_distance_km": 1200,
        "notes": "Ballistic missile trajectory. Debris fell on Temple Mount (Al-Aqsa damage), Church of Holy Sepulchre, Jewish Quarter. Beit Shemesh synagogue shelter struck — 9 killed.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 19 — Jerusalem/Haifa salvos
    {
        "id": "IR_20260319_ISR_R01",
        "event_id": "IR_20260319_ISR",
        "drone_count": None,
        "drone_type": "emad_ballistic",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Tabriz", "lat": 38.25, "lon": 46.13, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Turkey/Iraq border region", "lat": 37.00, "lon": 43.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Northern Iraq", "lat": 36.00, "lon": 40.00, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Haifa (Bazan Refinery)", "lat": 32.82, "lon": 35.00, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "ballistic_trajectory",
        "estimated_distance_km": 1400,
        "notes": "Ballistic missile from Tabriz to Haifa. Bazan oil refinery damaged. 5 salvos at Jerusalem/northern Israel within 1 hour.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 20 — Kuwait Mina Al-Ahmadi
    {
        "id": "IR_20260320_KWT_R01",
        "event_id": "IR_20260320_KWT",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "hit_target",
        "waypoints": [
            {"seq": 0, "name": "Mahidasht (Kermanshah)", "lat": 34.32, "lon": 46.76, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Iraq airspace (Basra)", "lat": 30.50, "lon": 47.80, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Northern Kuwait", "lat": 29.80, "lon": 47.90, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Mina Al-Ahmadi Refinery", "lat": 29.06, "lon": 48.15, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "direct",
        "estimated_distance_km": 600,
        "notes": "Drone struck Kuwait's largest oil refinery (730,000 bpd). Fires at multiple units. Attack during Eid al-Fitr.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
    # Mar 20 — Saudi Ras Tanura
    {
        "id": "IR_20260320_SAU_R01",
        "event_id": "IR_20260320_SAU",
        "drone_count": None,
        "drone_type": "shahed_136",
        "outcome": "intercepted",
        "waypoints": [
            {"seq": 0, "name": "Isfahan", "lat": 32.65, "lon": 51.68, "type": "launch", "time_approx": None},
            {"seq": 1, "name": "Persian Gulf", "lat": 28.00, "lon": 50.00, "type": "transit", "time_approx": None},
            {"seq": 2, "name": "Saudi eastern coast", "lat": 26.70, "lon": 50.10, "type": "transit", "time_approx": None},
            {"seq": 3, "name": "Ras Tanura oil terminal", "lat": 26.64, "lon": 50.17, "type": "target", "time_approx": None}
        ],
        "approach_direction": "NE",
        "route_type": "direct",
        "estimated_distance_km": 900,
        "notes": "Drones targeted Ras Tanura oil terminal. Most intercepted by Saudi Patriot systems.",
        "conflict": "iran_2026",
        "sources": [{"name": "Estimated from launch region and target", "url": None, "confidence": "estimate"}]
    },
]


def main():
    # Load existing data
    with open("data/iran/events.json") as f:
        events = json.load(f)
    with open("data/iran/routes.json") as f:
        routes = json.load(f)

    existing_ids = {e["id"] for e in events}
    existing_route_ids = {r["id"] for r in routes}

    added_events = 0
    for e in NEW_EVENTS:
        if e["id"] not in existing_ids:
            events.append(e)
            added_events += 1

    added_routes = 0
    for r in NEW_ROUTES:
        if r["id"] not in existing_route_ids:
            routes.append(r)
            added_routes += 1

    # Sort events by date
    events.sort(key=lambda x: x["date"], reverse=True)
    # Sort routes by event_id
    routes.sort(key=lambda x: x["event_id"])

    with open("data/iran/events.json", "w") as f:
        json.dump(events, f, indent=2)

    with open("data/iran/routes.json", "w") as f:
        json.dump(routes, f, indent=2)

    print(f"Added {added_events} new events (total: {len(events)})")
    print(f"Added {added_routes} new routes (total: {len(routes)})")

    # Summary
    dates = sorted(set(e["date"] for e in events))
    print(f"\nDate coverage: {dates[0]} to {dates[-1]}")
    countries = {}
    for e in events:
        for t in e.get("target_regions", []):
            name = t["name"].split("(")[0].strip().split(",")[0].strip()
            countries[name] = countries.get(name, 0) + 1
    print(f"Unique targets: {len(countries)}")

    # Count by country code
    by_country = {}
    for e in events:
        code = e["id"].split("_")[2]
        by_country[code] = by_country.get(code, 0) + 1
    print(f"\nEvents by target country:")
    for c, n in sorted(by_country.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
