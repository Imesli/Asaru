/**
 * Asaru Sim Engine
 *
 * Core simulation for automated interceptor assignment against drone swarms.
 * Takes real attack data (routes + events) and defense site placements,
 * then runs a time-stepped simulation deciding which interceptor from which
 * site engages which incoming drone.
 */

// ─── Geometry helpers ───────────────────────────────────────────

function toRad(deg) { return deg * Math.PI / 180; }
function toDeg(rad) { return rad * 180 / Math.PI; }

/** Haversine distance in km between two [lat, lon] points */
export function distanceKm(a, b) {
  const R = 6371;
  const dLat = toRad(b[0] - a[0]);
  const dLon = toRad(b[1] - a[1]);
  const sin2 = Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(a[0])) * Math.cos(toRad(b[0])) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(sin2), Math.sqrt(1 - sin2));
}

/** Bearing in degrees from point a to point b */
export function bearing(a, b) {
  const dLon = toRad(b[1] - a[1]);
  const y = Math.sin(dLon) * Math.cos(toRad(b[0]));
  const x = Math.cos(toRad(a[0])) * Math.sin(toRad(b[0])) -
    Math.sin(toRad(a[0])) * Math.cos(toRad(b[0])) * Math.cos(dLon);
  return (toDeg(Math.atan2(y, x)) + 360) % 360;
}

/** Interpolate position along a waypoint path at a given fraction (0–1) */
export function interpolateRoute(waypoints, fraction) {
  if (waypoints.length < 2) return waypoints[0] ? [waypoints[0].lat, waypoints[0].lon] : [0, 0];
  const f = Math.max(0, Math.min(1, fraction));

  // Build cumulative distances
  const dists = [0];
  for (let i = 1; i < waypoints.length; i++) {
    dists.push(dists[i - 1] + distanceKm(
      [waypoints[i - 1].lat, waypoints[i - 1].lon],
      [waypoints[i].lat, waypoints[i].lon]
    ));
  }
  const totalDist = dists[dists.length - 1];
  const targetDist = f * totalDist;

  // Find segment
  for (let i = 1; i < dists.length; i++) {
    if (dists[i] >= targetDist) {
      const segFrac = (targetDist - dists[i - 1]) / (dists[i] - dists[i - 1] || 1);
      const lat = waypoints[i - 1].lat + segFrac * (waypoints[i].lat - waypoints[i - 1].lat);
      const lon = waypoints[i - 1].lon + segFrac * (waypoints[i].lon - waypoints[i - 1].lon);
      return [lat, lon];
    }
  }
  const last = waypoints[waypoints.length - 1];
  return [last.lat, last.lon];
}

/** Total route distance in km */
export function routeDistance(waypoints) {
  let d = 0;
  for (let i = 1; i < waypoints.length; i++) {
    d += distanceKm(
      [waypoints[i - 1].lat, waypoints[i - 1].lon],
      [waypoints[i].lat, waypoints[i].lon]
    );
  }
  return d;
}


// ─── Drone state ────────────────────────────────────────────────

const DECOY_TYPES = new Set(['gerbera_decoy', 'parody_decoy', 'unknown_decoy']);

/**
 * Build a Drone object from a route trace record.
 * speed_kmh comes from the parent event's drone_types or falls back to defaults.
 */
export function createDrone(route, speedKmh = 185) {
  const wps = route.waypoints || [];
  const dist = routeDistance(wps);
  const flightTimeSec = (dist / speedKmh) * 3600;
  const droneType = route.drone_type || 'shahed_136';

  return {
    id: route.id,
    routeId: route.id,
    eventId: route.event_id,
    droneType,
    isDecoy: DECOY_TYPES.has(droneType),
    droneCount: route.drone_count || 1,
    waypoints: wps,
    totalDistKm: dist,
    speedKmh,
    flightTimeSec,
    // Sim state
    status: 'inbound',  // inbound | intercepted | hit_target | evading
    progress: 0,         // 0–1 along route
    position: wps.length ? [wps[0].lat, wps[0].lon] : [0, 0],
    assignedInterceptor: null,
    interceptTime: null,
    engagementAttempts: 0,  // how many times we've tried to intercept this drone
    maxEngagements: 3,      // max re-engagement attempts
  };
}


// ─── Defense site state ─────────────────────────────────────────

/** Clone defense sites for a sim run so originals aren't mutated */
export function initDefenseSites(sites) {
  return sites.map(site => ({
    ...site,
    assets: site.assets.map(a => ({
      ...a,
      currentStock: a.stock,
      cooldownUntil: 0,  // sim-time seconds
      engagements: [],   // track what this asset shot at
    })),
  }));
}


// ─── Assignment algorithm ───────────────────────────────────────

/**
 * The core assignment function with enhanced logic:
 * - Decoy discrimination: assets with can_discriminate_decoys skip decoys
 * - Geran-3 priority: fast movers get priority + SAMs preferred for them
 * - Ammo conservation: keeps a reserve when stock is low
 * - Re-engagement: drones that survived a miss can be re-engaged
 */
export function assignInterceptors(activeDrones, defenseSites, simTime) {
  const assignments = [];

  // Cost weights — higher = less preferred
  const WEAPON_COST = {
    interceptor_drone: 1,
    aaa: 2,
    ew: 0.5,
    manpads: 3,
    sam_missile: 10,
  };

  // Minimum reserve: don't use last 10% of stock (except EW which is unlimited-feel)
  const RESERVE_RATIO = 0.1;

  // Sort drones by threat priority
  const sorted = [...activeDrones]
    .filter(d => d.status === 'inbound' && !d.assignedInterceptor && d.engagementAttempts < d.maxEngagements)
    .sort((a, b) => {
      // Strike drones before decoys
      if (a.isDecoy !== b.isDecoy) return a.isDecoy ? 1 : -1;
      // Geran-3 (fast, ~600 km/h) gets highest priority
      const aFast = a.speedKmh >= 500;
      const bFast = b.speedKmh >= 500;
      if (aFast !== bFast) return aFast ? -1 : 1;
      // Faster drones next
      if (a.speedKmh !== b.speedKmh) return b.speedKmh - a.speedKmh;
      // Further along route = more urgent
      return b.progress - a.progress;
    });

  for (const drone of sorted) {
    let bestScore = Infinity;
    let bestAssignment = null;

    for (const site of defenseSites) {
      const siteLoc = [site.lat, site.lon];
      const dist = distanceKm(drone.position, siteLoc);

      for (let ai = 0; ai < site.assets.length; ai++) {
        const asset = site.assets[ai];

        // Skip if out of stock or on cooldown
        if (asset.currentStock <= 0) continue;
        if (asset.cooldownUntil > simTime) continue;

        // Ammo conservation: keep reserve unless drone is very close (urgent)
        const reserveThreshold = Math.ceil((asset.stock || 1) * RESERVE_RATIO);
        if (asset.currentStock <= reserveThreshold && drone.progress < 0.7 && asset.type !== 'ew') continue;

        // Range check
        if (dist > asset.range_km) continue;

        // Decoy discrimination: if asset can discriminate and drone is a decoy, skip it
        if (asset.can_discriminate_decoys && drone.isDecoy) continue;

        // Get kill probability for this drone type
        const kp = asset.kill_probability?.[drone.droneType] ??
                   asset.kill_probability?.unknown ?? 0.5;

        // Score: lower is better
        const costMult = WEAPON_COST[asset.type] || 5;
        const stockRatio = asset.currentStock / (asset.stock || 1);

        // For fast movers (Geran-3), prefer SAMs/high-kp weapons despite cost
        const fastMoverBonus = (drone.speedKmh >= 500 && kp > 0.6) ? 0.3 : 1;

        // Penalty for re-engaging same drone with same weapon type (try different weapons)
        const reEngagePenalty = drone.engagementAttempts > 0 ? 1.5 : 1;

        const score = (dist / asset.range_km) * costMult * (1 / (kp + 0.01)) *
                      (1 / (stockRatio + 0.1)) * fastMoverBonus * reEngagePenalty;

        if (score < bestScore) {
          bestScore = score;
          bestAssignment = {
            droneId: drone.id,
            siteId: site.id,
            siteName: site.name,
            assetIndex: ai,
            assetType: asset.type,
            weapon: asset.weapon,
            distance: dist,
            killProb: kp,
            engageTime: simTime,
          };
        }
      }
    }

    if (bestAssignment) {
      assignments.push(bestAssignment);

      // Update asset state
      const site = defenseSites.find(s => s.id === bestAssignment.siteId);
      const asset = site.assets[bestAssignment.assetIndex];
      asset.currentStock--;
      asset.cooldownUntil = simTime + (asset.reload_time_s || 0);
      asset.engagements.push(bestAssignment);

      // Mark drone as engaged
      drone.assignedInterceptor = bestAssignment;
    }
  }

  return assignments;
}


// ─── Engagement resolution ──────────────────────────────────────

/** Roll the dice on each engagement and determine outcome */
export function resolveEngagements(drones) {
  const results = [];

  for (const drone of drones) {
    if (drone.status !== 'inbound' || !drone.assignedInterceptor) continue;

    const kp = drone.assignedInterceptor.killProb;
    const roll = Math.random();

    if (roll < kp) {
      drone.status = 'intercepted';
      drone.interceptTime = drone.assignedInterceptor.engageTime;
      results.push({
        droneId: drone.id,
        outcome: 'intercepted',
        by: drone.assignedInterceptor.weapon,
        site: drone.assignedInterceptor.siteName,
        killProb: kp,
        roll,
      });
    } else {
      // Missed — drone continues, can be re-engaged
      const missedWeapon = drone.assignedInterceptor.weapon;
      drone.assignedInterceptor = null;
      drone.engagementAttempts++;
      results.push({
        droneId: drone.id,
        outcome: 'missed',
        by: missedWeapon,
        killProb: kp,
        roll,
      });
    }
  }

  return results;
}


// ─── Sim runner ─────────────────────────────────────────────────

/**
 * Run a complete simulation of one attack event.
 *
 * @param {Object} params
 * @param {Array} params.routes - Route trace records for this event
 * @param {Array} params.defenseSites - Defense site records
 * @param {Object} params.event - The attack event record (for drone speeds etc)
 * @param {number} params.timeStepSec - Simulation time step (default 10s)
 * @param {Function} params.onTick - Called each tick with full sim state (for animation)
 *
 * @returns {Object} Final sim results
 */
export function runSimulation({
  routes,
  defenseSites: rawSites,
  event,
  timeStepSec = 10,
  onTick = null,
}) {
  // Build drone speed lookup from event
  const speedByType = {};
  if (event?.drone_types) {
    for (const dt of event.drone_types) {
      if (dt.speed_kmh) speedByType[dt.type || dt.model] = dt.speed_kmh;
    }
  }
  const defaultSpeed = speedByType.shahed_136 || 185;

  // Initialize
  const drones = routes.map(r => {
    const speed = speedByType[r.drone_type] || defaultSpeed;
    const d = createDrone(r, speed);
    d.trail = []; // position history for trail rendering
    return d;
  });

  const sites = initDefenseSites(rawSites);
  const allEngagements = [];
  const tickHistory = [];

  // Find max flight time to know when sim ends
  const maxFlightTime = Math.max(...drones.map(d => d.flightTimeSec), 0);
  const simDuration = maxFlightTime * 1.1; // 10% buffer

  let simTime = 0;
  let decoysWasted = 0; // track interceptors wasted on decoys

  while (simTime < simDuration) {
    // 1. Advance drone positions
    for (const drone of drones) {
      if (drone.status !== 'inbound') continue;

      drone.progress = Math.min(1, simTime / drone.flightTimeSec);
      drone.position = interpolateRoute(drone.waypoints, drone.progress);
      drone.trail.push([...drone.position]);

      // Reached target?
      if (drone.progress >= 1) {
        drone.status = drone.isDecoy ? 'intercepted' : 'hit_target'; // decoys reaching target = harmless
      }
    }

    // 2. Run assignment algorithm for drones in range (includes re-engagement for missed drones)
    const inbound = drones.filter(d => d.status === 'inbound');
    const newAssignments = assignInterceptors(inbound, sites, simTime);
    allEngagements.push(...newAssignments);

    // 3. Resolve engagements for drones that have been assigned
    const results = resolveEngagements(drones);

    // Track decoy waste
    for (const r of results) {
      if (r.outcome === 'intercepted') {
        const drone = drones.find(d => d.id === r.droneId);
        if (drone?.isDecoy) decoysWasted++;
      }
    }

    // 4. Record tick
    // Build engagement lines for this tick
    const engagementLines = results.map(r => {
      const drone = drones.find(d => d.id === r.droneId);
      const assignment = drone?.assignedInterceptor || newAssignments.find(a => a.droneId === r.droneId);
      if (!assignment || !drone) return null;
      const site = sites.find(s => s.id === assignment.siteId);
      if (!site) return null;
      return {
        from: [site.lat, site.lon],
        to: [...drone.position],
        outcome: r.outcome,
        weapon: r.by || assignment.weapon,
      };
    }).filter(Boolean);

    // Count running totals
    const totalInbound = drones.filter(d => d.status === 'inbound').length;
    const totalIntercepted = drones.filter(d => d.status === 'intercepted').length;
    const totalHit = drones.filter(d => d.status === 'hit_target').length;

    const tick = {
      time: simTime,
      drones: drones.map(d => ({
        id: d.id,
        position: [...d.position],
        status: d.status,
        progress: d.progress,
        droneType: d.droneType,
        isDecoy: d.isDecoy,
        trail: d.trail.map(p => [...p]),
      })),
      counts: { inbound: totalInbound, intercepted: totalIntercepted, hit: totalHit, total: drones.length },
      engagementLines,
      newAssignments,
      engagementResults: results,
      sites: sites.map(s => ({
        id: s.id,
        name: s.name,
        lat: s.lat,
        lon: s.lon,
        assets: s.assets.map(a => ({
          type: a.type,
          weapon: a.weapon,
          currentStock: a.currentStock,
          stock: a.stock,
        })),
      })),
    };

    tickHistory.push(tick);
    if (onTick) onTick(tick);

    simTime += timeStepSec;
  }

  // Compile results
  const strikeDrones = drones.filter(d => !d.isDecoy);
  const decoyDrones = drones.filter(d => d.isDecoy);
  const intercepted = drones.filter(d => d.status === 'intercepted').length;
  const hitTarget = drones.filter(d => d.status === 'hit_target').length;
  const strikeIntercepted = strikeDrones.filter(d => d.status === 'intercepted').length;
  const strikeHit = strikeDrones.filter(d => d.status === 'hit_target').length;
  const totalDrones = drones.length;

  return {
    totalDrones,
    intercepted,
    hitTarget,
    interceptionRate: totalDrones > 0 ? intercepted / totalDrones : 0,
    // Strike-only metrics (excluding decoys)
    strikeTotal: strikeDrones.length,
    strikeIntercepted,
    strikeHit,
    strikeInterceptionRate: strikeDrones.length > 0 ? strikeIntercepted / strikeDrones.length : 0,
    decoyTotal: decoyDrones.length,
    decoysWasted, // interceptors spent on decoys
    leakers: hitTarget,
    totalEngagements: allEngagements.length,
    tickCount: tickHistory.length,
    simDurationSec: simTime,
    ticks: tickHistory,
    // Per-site summary
    siteResults: sites.map(s => ({
      id: s.id,
      name: s.name,
      assets: s.assets.map(a => ({
        weapon: a.weapon,
        fired: a.stock - a.currentStock,
        remaining: a.currentStock,
        engagements: a.engagements.length,
      })),
    })),
    // Per-drone summary
    droneResults: drones.map(d => ({
      id: d.id,
      type: d.droneType,
      isDecoy: d.isDecoy,
      status: d.status,
      engagementAttempts: d.engagementAttempts,
      interceptedBy: d.assignedInterceptor?.weapon || null,
      interceptedAt: d.assignedInterceptor?.siteName || null,
    })),
  };
}
