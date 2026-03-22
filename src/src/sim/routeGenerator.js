/**
 * Synthetic route generator for war game scenarios.
 *
 * When a scenario has no pre-existing route traces in the dataset,
 * this generates plausible flight paths from launch regions to defense site
 * areas, with randomized waypoints for realistic-looking approach vectors.
 */

/** Random float in [min, max) */
function rand(min, max) { return min + Math.random() * (max - min); }

/** Add random offset to a lat/lon (degrees) */
function jitter(lat, lon, kmRadius = 50) {
  const degPerKm = 1 / 111;
  const r = kmRadius * degPerKm;
  return { lat: lat + rand(-r, r), lon: lon + rand(-r, r) };
}

/**
 * Generate synthetic routes for a scenario.
 *
 * @param {Object} scenario - Full scenario JSON (attack config + defense_sites)
 * @returns {Array} Array of route-trace-like objects usable by the sim engine
 */
export function generateScenarioRoutes(scenario) {
  const { attack, defense_sites } = scenario;
  if (!attack || !defense_sites?.length) return [];

  // Build launch points from launch_regions or fallback to hardcoded coords
  const launchCoords = getLaunchCoords(scenario);
  if (launchCoords.length === 0) return [];

  // Build target points from defense sites (drones aim at defended areas)
  const targets = defense_sites.map(ds => ({
    lat: ds.lat,
    lon: ds.lon,
    name: ds.name,
    id: ds.id,
  }));

  const routes = [];
  const droneTypes = attack.drone_types || [];

  for (const dt of droneTypes) {
    const count = dt.count || 0;
    const type = dt.type;
    const speed = dt.speed_kmh || 180;

    for (let i = 0; i < count; i++) {
      // Pick a random launch point and target
      const launch = launchCoords[Math.floor(Math.random() * launchCoords.length)];
      const target = targets[Math.floor(Math.random() * targets.length)];

      // Generate 3-5 intermediate waypoints for realistic approach
      const numMidpoints = 2 + Math.floor(Math.random() * 3);
      const waypoints = [];

      // Launch point
      const launchJitter = jitter(launch.lat, launch.lon, 30);
      waypoints.push({
        name: launch.name || 'Launch',
        lat: launchJitter.lat,
        lon: launchJitter.lon,
        type: 'origin',
      });

      // Intermediate waypoints (interpolated with random deviation)
      for (let m = 1; m <= numMidpoints; m++) {
        const frac = m / (numMidpoints + 1);
        const midLat = launch.lat + (target.lat - launch.lat) * frac;
        const midLon = launch.lon + (target.lon - launch.lon) * frac;
        const deviation = jitter(midLat, midLon, 80);
        waypoints.push({
          name: `WP${m}`,
          lat: deviation.lat,
          lon: deviation.lon,
          type: 'transit',
        });
      }

      // Target point
      const targetJitter = jitter(target.lat, target.lon, 15);
      waypoints.push({
        name: target.name || 'Target',
        lat: targetJitter.lat,
        lon: targetJitter.lon,
        type: 'target',
      });

      routes.push({
        id: `${scenario.id}_route_${type}_${String(i).padStart(4, '0')}`,
        event_id: scenario.event_id || scenario.id,
        drone_type: type,
        drone_count: 1,
        route_type: Math.random() > 0.7 ? 'circuitous' : 'direct',
        approach_direction: getApproachDirection(launch, target),
        waypoints,
        outcome: 'unknown', // sim will determine this
        sources: [{ name: 'Scenario generation', confidence: 'sim_placement' }],
      });
    }
  }

  return routes;
}

/** Get compass direction from launch to target */
function getApproachDirection(from, to) {
  const dLat = to.lat - from.lat;
  const dLon = to.lon - from.lon;
  const angle = Math.atan2(dLon, dLat) * 180 / Math.PI;
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const idx = Math.round(((angle + 360) % 360) / 45) % 8;
  return dirs[idx];
}

/** Extract launch coordinates from scenario */
function getLaunchCoords(scenario) {
  const regions = scenario.attack?.launch_regions || [];

  // If launch_regions are strings (names only), use theater-specific fallbacks
  if (regions.length > 0 && typeof regions[0] === 'string') {
    return getTheaterLaunchPoints(scenario.theater, regions);
  }

  // If they have coordinates, use them directly
  if (regions.length > 0 && regions[0].lat != null) {
    return regions;
  }

  return getTheaterLaunchPoints(scenario.theater, regions);
}

/** Hardcoded launch coordinates by theater for scenarios without explicit coords */
function getTheaterLaunchPoints(theater, regionNames) {
  const THEATER_LAUNCHES = {
    ukraine: [
      { name: 'Kursk Oblast', lat: 51.7, lon: 36.2 },
      { name: 'Krasnodar Krai', lat: 45.0, lon: 38.9 },
      { name: 'Crimea', lat: 45.3, lon: 34.0 },
      { name: 'Sea of Azov', lat: 46.0, lon: 36.5 },
      { name: 'Bryansk Oblast', lat: 53.2, lon: 34.4 },
    ],
    gulf: [
      { name: 'Kerman Province', lat: 30.3, lon: 57.1 },
      { name: 'Fars Province', lat: 29.6, lon: 52.5 },
      { name: 'Khuzestan Province', lat: 31.3, lon: 48.7 },
      { name: 'Hormozgan Province', lat: 27.2, lon: 56.3 },
      { name: 'Sistan-Baluchestan Province', lat: 27.5, lon: 60.8 },
    ],
  };

  const points = THEATER_LAUNCHES[theater] || THEATER_LAUNCHES.ukraine;

  // If region names were specified, try to match them
  if (regionNames.length > 0 && typeof regionNames[0] === 'string') {
    const matched = regionNames.map(name =>
      points.find(p => p.name.toLowerCase().includes(name.toLowerCase().split(' ')[0]))
    ).filter(Boolean);
    if (matched.length > 0) return matched;
  }

  return points;
}
