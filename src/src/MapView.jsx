import { useMemo, useState, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { Map as MapGL } from 'react-map-gl';
import { ScatterplotLayer, PathLayer, ArcLayer, TextLayer, LineLayer } from '@deck.gl/layers';
import 'maplibre-gl/dist/maplibre-gl.css';

const INITIAL_VIEW_STATE = {
  longitude: 35,
  latitude: 42,
  zoom: 4.2,
  pitch: 25,
  bearing: 5,
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const ROUTE_COLORS = {
  direct: [96, 165, 250],
  circuitous: [245, 158, 11],
  looping: [239, 68, 68],
  ballistic_trajectory: [192, 132, 252],
  unknown: [148, 163, 184],
};

// Launch sites are ALWAYS green — "this is where it came from"
const LAUNCH_COLOR = [52, 211, 153]; // emerald green

// Targets are ALWAYS in the red/warm spectrum — "this got hit"
const TARGET_COLORS = {
  energy: [251, 146, 60],     // orange
  military: [239, 68, 68],    // red
  residential: [244, 114, 182], // pink
  civilian: [244, 114, 182],  // pink
  urban: [248, 113, 113],     // light red
  industrial: [251, 191, 36], // amber
  infrastructure: [251, 146, 60], // orange
  transport: [251, 146, 60],  // orange
  diplomatic: [192, 132, 252], // purple
  religious: [192, 132, 252], // purple
  mixed: [251, 146, 60],     // orange
  unknown: [248, 113, 113],  // light red
};

// Conflict accent colors (used for arc tinting, not point colors)
const CONFLICT_ACCENT = {
  ukraine_russia: [245, 197, 66],
  iran_2026: [224, 82, 82],
};

const LAYER_DEFS = [
  { key: 'arcs', label: 'Strike arcs', color: '#94a3b8' },
  { key: 'routes', label: 'Routes', color: '#60a5fa' },
  { key: 'launches', label: 'Launch sites', color: '#34d399' },
  { key: 'targets', label: 'Targets', color: '#ef4444' },
  { key: 'labels', label: 'Labels', color: '#ffffff' },
  { key: 'iranReach', label: 'Iran strike range', color: '#ef4444' },
];

const WEAPON_PRESETS = {
  interceptor_base: {
    label: 'Interceptor Drone Base',
    assets: [
      { type: 'interceptor_drone', weapon: 'sting', stock: 30, range_km: 15, speed_kmh: 250, reload_time_s: 8,
        kill_probability: { shahed_136: 0.82, geran_2: 0.78, geran_3: 0.45, gerbera_decoy: 0.85, unknown: 0.70 },
        can_discriminate_decoys: false },
      { type: 'interceptor_drone', weapon: 'bullet', stock: 20, range_km: 12, speed_kmh: 300, reload_time_s: 5,
        kill_probability: { shahed_136: 0.88, geran_2: 0.84, geran_3: 0.55, gerbera_decoy: 0.90, unknown: 0.75 },
        can_discriminate_decoys: false },
    ],
    radar_range_km: 80,
  },
  sam_battery: {
    label: 'SAM Battery',
    assets: [
      { type: 'sam_missile', weapon: 'nasams', stock: 16, range_km: 25, speed_kmh: null, reload_time_s: 15,
        kill_probability: { shahed_136: 0.95, geran_2: 0.93, geran_3: 0.80, gerbera_decoy: 0.95, unknown: 0.85 },
        can_discriminate_decoys: false },
    ],
    radar_range_km: 120,
  },
  mixed_defense: {
    label: 'Mixed Defense',
    assets: [
      { type: 'interceptor_drone', weapon: 'octopus', stock: 25, range_km: 20, speed_kmh: 220, reload_time_s: 12,
        kill_probability: { shahed_136: 0.78, geran_2: 0.74, geran_3: 0.40, gerbera_decoy: 0.80, unknown: 0.65 },
        can_discriminate_decoys: true },
      { type: 'aaa', weapon: 'gepard', stock: 150, range_km: 4, speed_kmh: null, reload_time_s: 0.1,
        kill_probability: { shahed_136: 0.65, geran_2: 0.62, geran_3: 0.35, gerbera_decoy: 0.60, unknown: 0.50 },
        can_discriminate_decoys: false },
    ],
    radar_range_km: 60,
  },
  ew_station: {
    label: 'EW Station',
    assets: [
      { type: 'ew', weapon: 'ew_jammer', stock: 1, range_km: 30, speed_kmh: null, reload_time_s: null,
        kill_probability: { shahed_136: 0.25, geran_2: 0.20, geran_3: 0.10, gerbera_decoy: 0.30, unknown: 0.15 },
        can_discriminate_decoys: true },
    ],
    radar_range_km: 40,
  },
  anvil_base: {
    label: 'Anvil Kinetic Kill',
    assets: [
      { type: 'interceptor_drone', weapon: 'anvil', stock: 20, range_km: 18, speed_kmh: 350, reload_time_s: 10,
        kill_probability: { shahed_136: 0.92, geran_2: 0.90, geran_3: 0.65, gerbera_decoy: 0.92, unknown: 0.80 },
        can_discriminate_decoys: false },
    ],
    radar_range_km: 90,
  },
};

export default function MapView({ events, routes, selectedEvent, onSelectEvent, mapHighlight, visibleLayers = {}, onToggleLayer, simTick, defenseSites = [], simMode = false, placeSiteMode = null, onPlaceSite, iranStrikeRegions = null }) {
  const [tooltip, setTooltip] = useState(null);
  const [showLayerPanel, setShowLayerPanel] = useState(false);

  const viewState = useMemo(() => {
    if (selectedEvent) {
      const points = [
        ...selectedEvent.launch_regions.filter(r => r.lat && r.lon).map(r => [r.lon, r.lat]),
        ...selectedEvent.target_regions.filter(r => r.lat && r.lon).map(r => [r.lon, r.lat]),
      ];
      if (points.length > 0) {
        const lons = points.map(p => p[0]);
        const lats = points.map(p => p[1]);
        const centerLon = (Math.min(...lons) + Math.max(...lons)) / 2;
        const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
        const span = Math.max(Math.max(...lons) - Math.min(...lons), Math.max(...lats) - Math.min(...lats), 2);
        const zoom = Math.max(3, Math.min(8, Math.log2(360 / span) - 0.5));
        return { ...INITIAL_VIEW_STATE, longitude: centerLon, latitude: centerLat, zoom };
      }
    }
    return INITIAL_VIEW_STATE;
  }, [selectedEvent]);

  // ── Data derivations ──

  const arcData = useMemo(() => {
    const arcs = [];
    for (const event of events) {
      for (const launch of event.launch_regions) {
        if (!launch.lat || !launch.lon) continue;
        for (const target of event.target_regions) {
          if (!target.lat || !target.lon) continue;
          arcs.push({
            source: [launch.lon, launch.lat],
            target: [target.lon, target.lat],
            event,
            launchName: launch.name,
            targetName: target.name,
            targetType: target.target_type,
            count: event.totals.launched_total,
          });
        }
      }
    }
    return arcs;
  }, [events]);

  const launchPoints = useMemo(() => {
    const map = new Map();
    for (const event of events) {
      for (const r of event.launch_regions) {
        if (!r.lat || !r.lon) continue;
        const key = r.name;
        const existing = map.get(key);
        if (existing) {
          existing.totalLaunched += event.totals.launched_total || 0;
          existing.eventCount++;
        } else {
          map.set(key, {
            position: [r.lon, r.lat], name: r.name, conflict: event.conflict,
            totalLaunched: event.totals.launched_total || 0, eventCount: 1,
            confidence: r.confidence,
          });
        }
      }
    }
    return [...map.values()];
  }, [events]);

  const targetPoints = useMemo(() => {
    const map = new Map();
    for (const event of events) {
      for (const r of event.target_regions) {
        if (!r.lat || !r.lon) continue;
        const key = r.name;
        const existing = map.get(key);
        if (existing) {
          existing.eventCount++;
        } else {
          map.set(key, {
            position: [r.lon, r.lat], name: r.name, conflict: event.conflict,
            targetType: r.target_type || 'unknown', eventCount: 1,
          });
        }
      }
    }
    return [...map.values()];
  }, [events]);

  const pathData = useMemo(() => {
    return routes.map(route => ({
      path: route.waypoints.filter(w => w.lat != null && w.lon != null).map(w => [w.lon, w.lat]),
      route,
      routeType: route.route_type || 'unknown',
      isHighlighted: mapHighlight?.type === 'route' && mapHighlight?.id === route.id,
    }));
  }, [routes, mapHighlight]);

  const waypointData = useMemo(() => {
    const points = [];
    for (const route of routes) {
      for (const wp of route.waypoints) {
        if (wp.lat == null || wp.lon == null) continue;
        points.push({
          position: [wp.lon, wp.lat],
          name: wp.name,
          type: wp.type,
          route,
          isHighlighted: mapHighlight?.type === 'route' && mapHighlight?.id === route.id,
        });
      }
    }
    return points;
  }, [routes, mapHighlight]);

  const handleHover = useCallback(({ object, x, y, layer }) => {
    if (object) {
      setTooltip({ object, x, y, layerId: layer.id });
    } else {
      setTooltip(null);
    }
  }, []);

  const handleMapClick = useCallback((info) => {
    if (!placeSiteMode || !onPlaceSite || !info.coordinate) return;
    const preset = WEAPON_PRESETS[placeSiteMode];
    if (!preset) return;
    const [lon, lat] = info.coordinate;
    const newSite = {
      id: `DS_USER_${Date.now()}`,
      conflict: 'ukraine_russia',
      name: `${preset.label} (${lat.toFixed(1)}, ${lon.toFixed(1)})`,
      lat, lon,
      status: 'active',
      assets: JSON.parse(JSON.stringify(preset.assets)),
      radar_range_km: preset.radar_range_km,
      notes: `User-placed ${preset.label}`,
      sources: [{ name: 'Sim placement', confidence: 'sim_placement' }],
    };
    onPlaceSite(newSite);
  }, [placeSiteMode, onPlaceSite]);

  // ── Layers ──

  const layers = [
    // Strike corridors (arcs from launch to target)
    !simMode && visibleLayers.arcs !== false && new ArcLayer({
      id: 'strike-corridors',
      data: arcData,
      getSourcePosition: d => d.source,
      getTargetPosition: d => d.target,
      getSourceColor: [...LAUNCH_COLOR, 100],
      getTargetColor: d => {
        const tc = TARGET_COLORS[d.targetType] || TARGET_COLORS.unknown;
        return [...tc, 160];
      },
      getWidth: d => {
        if (!d.count) return 1;
        return Math.min(Math.max(Math.log10(d.count) * 1.5, 1), 5);
      },
      greatCircle: true,
      pickable: true,
      onHover: handleHover,
    }),

    // Flight route paths
    !simMode && visibleLayers.routes !== false && new PathLayer({
      id: 'routes',
      data: pathData,
      getPath: d => d.path,
      getColor: d => {
        const c = ROUTE_COLORS[d.routeType] || ROUTE_COLORS.unknown;
        return [...c, d.isHighlighted ? 255 : 180];
      },
      getWidth: d => d.isHighlighted ? 4 : 2.5,
      widthMinPixels: 2,
      rounded: true,
      pickable: true,
      onHover: handleHover,
      updateTriggers: {
        getColor: [mapHighlight],
        getWidth: [mapHighlight],
      },
    }),

    // Route waypoints
    !simMode && visibleLayers.routes !== false && new ScatterplotLayer({
      id: 'waypoints',
      data: waypointData,
      getPosition: d => d.position,
      getRadius: d => {
        if (d.isHighlighted) return 7000;
        if (d.type === 'last_known' || d.type === 'intercept') return 5000;
        return 3500;
      },
      getFillColor: d => {
        const alpha = d.isHighlighted ? 240 : 160;
        if (d.type === 'launch') return [...LAUNCH_COLOR, alpha];
        if (d.type === 'intercept') return [239, 68, 68, alpha];
        if (d.type === 'target') return [239, 68, 68, alpha];
        if (d.type === 'last_known') return [245, 158, 11, alpha];
        return [148, 163, 184, alpha]; // transit
      },
      radiusMinPixels: 2,
      radiusMaxPixels: 8,
      pickable: true,
      onHover: handleHover,
      updateTriggers: {
        getRadius: [mapHighlight],
        getFillColor: [mapHighlight],
      },
    }),

    // Launch sites (sized by total drones launched) — ALWAYS GREEN
    !simMode && visibleLayers.launches !== false && new ScatterplotLayer({
      id: 'launch-sites',
      data: launchPoints,
      getPosition: d => d.position,
      getFillColor: d => {
        const isHL = mapHighlight?.type === 'launch' && mapHighlight?.id === d.name;
        return [...LAUNCH_COLOR, isHL ? 240 : 180];
      },
      getRadius: d => Math.max(8000, Math.sqrt(d.totalLaunched) * 400),
      radiusMinPixels: 6,
      radiusMaxPixels: 20,
      stroked: true,
      getLineColor: d => {
        const isHL = mapHighlight?.type === 'launch' && mapHighlight?.id === d.name;
        return [255, 255, 255, isHL ? 120 : 40];
      },
      lineWidthMinPixels: 1,
      pickable: true,
      onHover: handleHover,
      onClick: ({ object }) => {
        if (!object) return;
        const evt = events.find(e => e.launch_regions.some(l => l.name === object.name));
        if (evt) onSelectEvent(evt);
      },
      updateTriggers: {
        getFillColor: [mapHighlight],
        getLineColor: [mapHighlight],
      },
    }),

    // Launch site pulse ring — green glow
    !simMode && visibleLayers.launches !== false && new ScatterplotLayer({
      id: 'launch-pulse',
      data: launchPoints,
      getPosition: d => d.position,
      getFillColor: [0, 0, 0, 0],
      getRadius: d => Math.max(12000, Math.sqrt(d.totalLaunched) * 600),
      radiusMinPixels: 8,
      radiusMaxPixels: 30,
      stroked: true,
      getLineColor: [...LAUNCH_COLOR, 40],
      lineWidthMinPixels: 1,
    }),

    // Target / strike zones — ALWAYS warm/red spectrum
    !simMode && visibleLayers.targets !== false && new ScatterplotLayer({
      id: 'strike-zones',
      data: targetPoints,
      getPosition: d => d.position,
      getFillColor: d => {
        const c = TARGET_COLORS[d.targetType] || TARGET_COLORS.unknown;
        const isHL = mapHighlight?.type === 'target' && mapHighlight?.id === d.name;
        return [...c, isHL ? 220 : 150];
      },
      getRadius: d => 8000 + d.eventCount * 3000,
      radiusMinPixels: 5,
      radiusMaxPixels: 16,
      stroked: true,
      getLineColor: d => {
        const isHL = mapHighlight?.type === 'target' && mapHighlight?.id === d.name;
        return [255, 255, 255, isHL ? 100 : 30];
      },
      lineWidthMinPixels: 1,
      pickable: true,
      onHover: handleHover,
      onClick: ({ object }) => {
        if (!object) return;
        const evt = events.find(e => e.target_regions.some(t => t.name === object.name));
        if (evt) onSelectEvent(evt);
      },
      updateTriggers: {
        getFillColor: [mapHighlight],
        getLineColor: [mapHighlight],
      },
    }),

    // Strike zone outer ring
    !simMode && visibleLayers.targets !== false && new ScatterplotLayer({
      id: 'strike-zone-ring',
      data: targetPoints,
      getPosition: d => d.position,
      getFillColor: [0, 0, 0, 0],
      getRadius: d => 12000 + d.eventCount * 4000,
      radiusMinPixels: 7,
      radiusMaxPixels: 24,
      stroked: true,
      getLineColor: d => {
        const c = TARGET_COLORS[d.targetType] || TARGET_COLORS.unknown;
        return [...c, 30];
      },
      lineWidthMinPixels: 1,
    }),

    // Labels
    !simMode && visibleLayers.labels !== false && new TextLayer({
      id: 'launch-labels',
      data: launchPoints,
      getPosition: d => d.position,
      getText: d => d.name,
      getSize: 11,
      getColor: [...LAUNCH_COLOR, 180],
      getTextAnchor: 'start',
      getAlignmentBaseline: 'center',
      getPixelOffset: [14, 0],
      fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif',
      fontWeight: 500,
      outlineWidth: 2,
      outlineColor: [8, 9, 14, 220],
      collisionEnabled: true,
      getCollisionPriority: d => d.totalLaunched,
    }),

    !simMode && visibleLayers.labels !== false && new TextLayer({
      id: 'target-labels',
      data: targetPoints,
      getPosition: d => d.position,
      getText: d => d.name,
      getSize: 11,
      getColor: d => {
        const c = TARGET_COLORS[d.targetType] || TARGET_COLORS.unknown;
        return [...c, 180];
      },
      getTextAnchor: 'start',
      getAlignmentBaseline: 'center',
      getPixelOffset: [14, 0],
      fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif',
      fontWeight: 500,
      outlineWidth: 2,
      outlineColor: [8, 9, 14, 220],
      collisionEnabled: true,
      getCollisionPriority: d => d.eventCount,
    }),

    // ── Iran strike range overlay ──

    // Range rings from Iranian launch sites
    !simMode && visibleLayers.iranReach !== false && iranStrikeRegions && iranStrikeRegions.launch_sites.flatMap(site =>
      iranStrikeRegions.range_rings.map(ring => new ScatterplotLayer({
        id: `iran-range-${site.name}-${ring.label}`.replace(/\s/g, '_'),
        data: [{ position: [site.lon, site.lat], range_km: ring.range_km, color: ring.color, label: ring.label }],
        getPosition: d => d.position,
        getFillColor: [0, 0, 0, 0],
        getRadius: d => d.range_km * 1000,
        stroked: true,
        getLineColor: d => [...d.color, 20],
        lineWidthMinPixels: 1,
      }))
    ),

    // Iranian launch site markers
    !simMode && visibleLayers.iranReach !== false && iranStrikeRegions && new ScatterplotLayer({
      id: 'iran-launch-sites',
      data: iranStrikeRegions.launch_sites,
      getPosition: d => [d.lon, d.lat],
      getFillColor: [239, 68, 68, 200],
      getRadius: 12000,
      radiusMinPixels: 5,
      radiusMaxPixels: 12,
      stroked: true,
      getLineColor: [239, 68, 68, 60],
      lineWidthMinPixels: 2,
      pickable: true,
      onHover: handleHover,
    }),

    // Confirmed target markers (diamond-shaped via larger radius + label)
    !simMode && visibleLayers.iranReach !== false && iranStrikeRegions && new ScatterplotLayer({
      id: 'iran-targets',
      data: iranStrikeRegions.confirmed_targets,
      getPosition: d => [d.lon, d.lat],
      getFillColor: d => d.status === 'within_expanded_range' ? [245, 158, 11, 160] : [239, 68, 68, 160],
      getRadius: d => d.status === 'within_expanded_range' ? 14000 : 10000,
      radiusMinPixels: 4,
      radiusMaxPixels: 10,
      stroked: true,
      getLineColor: d => d.status === 'within_expanded_range' ? [245, 158, 11, 60] : [239, 68, 68, 60],
      lineWidthMinPixels: 1,
      pickable: true,
      onHover: handleHover,
    }),

    // Iran target labels
    !simMode && visibleLayers.iranReach !== false && iranStrikeRegions && new TextLayer({
      id: 'iran-target-labels',
      data: iranStrikeRegions.confirmed_targets,
      getPosition: d => [d.lon, d.lat],
      getText: d => {
        const intercepted = d.drones_intercepted != null ? ` (${d.drones_intercepted} int.)` : '';
        return `${d.name}${intercepted}`;
      },
      getSize: 10,
      getColor: d => d.status === 'within_expanded_range' ? [245, 158, 11, 180] : [239, 68, 68, 180],
      getTextAnchor: 'start',
      getPixelOffset: [14, 0],
      fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif',
      fontWeight: 500,
      outlineWidth: 2,
      outlineColor: [8, 9, 14, 220],
    }),

    // Iran launch site labels
    !simMode && visibleLayers.iranReach !== false && iranStrikeRegions && new TextLayer({
      id: 'iran-launch-labels',
      data: iranStrikeRegions.launch_sites,
      getPosition: d => [d.lon, d.lat],
      getText: d => d.name,
      getSize: 9,
      getColor: [239, 68, 68, 140],
      getTextAnchor: 'start',
      getPixelOffset: [14, 0],
      fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif',
      fontWeight: 500,
      outlineWidth: 2,
      outlineColor: [8, 9, 14, 220],
    }),

    // ── Sim layers ──

    // Defense site markers (blue diamonds)
    defenseSites.length > 0 && new ScatterplotLayer({
      id: 'defense-sites',
      data: defenseSites,
      getPosition: d => [d.lon, d.lat],
      getFillColor: [59, 130, 246, 180],
      getRadius: 10000,
      radiusMinPixels: 6,
      radiusMaxPixels: 14,
      stroked: true,
      getLineColor: [59, 130, 246, 80],
      lineWidthMinPixels: 2,
      pickable: true,
      onHover: handleHover,
    }),

    // Defense site range rings
    defenseSites.length > 0 && new ScatterplotLayer({
      id: 'defense-ranges',
      data: defenseSites.flatMap(s =>
        s.assets.map(a => ({ ...s, range_km: a.range_km, assetType: a.type }))
      ),
      getPosition: d => [d.lon, d.lat],
      getFillColor: [0, 0, 0, 0],
      getRadius: d => d.range_km * 1000,
      stroked: true,
      getLineColor: [59, 130, 246, 25],
      lineWidthMinPixels: 1,
    }),

    // Defense site active glow (pulsing ring when sim is running)
    simTick && defenseSites.length > 0 && new ScatterplotLayer({
      id: 'defense-active-glow',
      data: defenseSites,
      getPosition: d => [d.lon, d.lat],
      getFillColor: [59, 130, 246, 15 + (simTick.time % 15) * 2],
      getRadius: 18000 + (simTick.time % 15) * 600,
      radiusMinPixels: 12,
      radiusMaxPixels: 28,
      stroked: true,
      getLineColor: [59, 130, 246, 40 + (simTick.time % 15) * 3],
      lineWidthMinPixels: 1,
      updateTriggers: { getFillColor: [simTick.time], getRadius: [simTick.time], getLineColor: [simTick.time] },
    }),

    // Defense site labels
    defenseSites.length > 0 && new TextLayer({
      id: 'defense-labels',
      data: defenseSites,
      getPosition: d => [d.lon, d.lat],
      getText: d => d.name,
      getSize: 10,
      getColor: [59, 130, 246, 160],
      getTextAnchor: 'start',
      getPixelOffset: [14, 0],
      fontFamily: '-apple-system, BlinkMacSystemFont, system-ui, sans-serif',
      fontWeight: 500,
      outlineWidth: 2,
      outlineColor: [8, 9, 14, 220],
    }),

    // Sim drone trail lines (fading path behind each drone)
    simTick && new PathLayer({
      id: 'sim-trails',
      data: simTick.drones.filter(d => d.trail && d.trail.length >= 2),
      getPath: d => d.trail.map(p => [p[1], p[0]]),
      getColor: d => {
        if (d.status === 'intercepted') return [52, 211, 153, 80];
        if (d.status === 'hit_target') return [239, 68, 68, 80];
        return [255, 200, 50, 60];
      },
      getWidth: 2,
      widthMinPixels: 1,
      rounded: true,
      updateTriggers: { getPath: [simTick.time], getColor: [simTick.time] },
    }),

    // Engagement arcs (defense site → drone) — green kills, red misses
    simTick && simTick.engagementLines && simTick.engagementLines.length > 0 && new ArcLayer({
      id: 'sim-engagements',
      data: simTick.engagementLines,
      getSourcePosition: d => [d.from[1], d.from[0]],
      getTargetPosition: d => [d.to[1], d.to[0]],
      getSourceColor: d => d.outcome === 'intercepted' ? [52, 211, 153, 200] : [239, 68, 68, 150],
      getTargetColor: d => d.outcome === 'intercepted' ? [52, 211, 153, 120] : [239, 68, 68, 80],
      getWidth: 3,
      greatCircle: false,
      updateTriggers: { getSourcePosition: [simTick.time], getTargetPosition: [simTick.time] },
    }),

    // Sim drone positions (animated dots during playback) — colored by type
    simTick && new ScatterplotLayer({
      id: 'sim-drones',
      data: simTick.drones.filter(d => d.status === 'inbound'),
      getPosition: d => [d.position[1], d.position[0]],
      getFillColor: d => {
        if (d.isDecoy) return [148, 163, 184, 180];       // grey-ish decoys
        if (d.droneType === 'geran_3') return [249, 115, 22, 240]; // bright orange fast movers
        return [255, 200, 50, 220];                        // yellow regular strike
      },
      getRadius: 6000,
      radiusMinPixels: 4,
      radiusMaxPixels: 10,
      updateTriggers: { getPosition: [simTick.time], getFillColor: [simTick.time] },
    }),

    // Sim intercepted markers (green dot)
    simTick && new ScatterplotLayer({
      id: 'sim-intercepted',
      data: simTick.drones.filter(d => d.status === 'intercepted'),
      getPosition: d => [d.position[1], d.position[0]],
      getFillColor: [52, 211, 153, 200],
      getRadius: 8000,
      radiusMinPixels: 5,
      radiusMaxPixels: 12,
      stroked: true,
      getLineColor: [52, 211, 153, 100],
      lineWidthMinPixels: 2,
      updateTriggers: { getPosition: [simTick.time] },
    }),

    // Sim leakers (hit target — red pulse)
    simTick && new ScatterplotLayer({
      id: 'sim-leakers',
      data: simTick.drones.filter(d => d.status === 'hit_target'),
      getPosition: d => [d.position[1], d.position[0]],
      getFillColor: [239, 68, 68, 220],
      getRadius: 10000,
      radiusMinPixels: 6,
      radiusMaxPixels: 14,
      stroked: true,
      getLineColor: [239, 68, 68, 100],
      lineWidthMinPixels: 2,
      updateTriggers: { getPosition: [simTick.time] },
    }),

    // Sim leaker threat rings — pulsing danger zone around leakers
    simTick && new ScatterplotLayer({
      id: 'sim-leaker-threat',
      data: simTick.drones.filter(d => d.status === 'hit_target'),
      getPosition: d => [d.position[1], d.position[0]],
      getFillColor: [239, 68, 68, 30],
      getRadius: 25000 + (simTick.time % 20) * 1500,
      radiusMinPixels: 14,
      radiusMaxPixels: 40,
      stroked: true,
      getLineColor: [239, 68, 68, 50],
      lineWidthMinPixels: 1,
      updateTriggers: { getPosition: [simTick.time], getRadius: [simTick.time] },
    }),
  ].flat().filter(Boolean);

  // ── Tooltip ──

  const renderTooltip = () => {
    if (!tooltip) return null;
    const { object, x, y, layerId } = tooltip;

    let title = '';
    let sub = '';
    let detail = '';

    if (layerId === 'strike-corridors') {
      title = `${object.launchName} \u2192 ${object.targetName}`;
      sub = object.targetType ? `Target type: ${object.targetType}` : '';
      detail = `${object.event.date} \u2014 ${object.count?.toLocaleString() || '?'} launched`;
    } else if (layerId === 'routes') {
      const r = object.route;
      title = `${(r.route_type || 'unknown').toUpperCase()} route \u2014 ${r.approach_direction || '?'} approach`;
      sub = r.waypoints.map(w => w.name).join(' \u2192 ');
      detail = `${r.drone_count || '?'} drone${(r.drone_count || 0) > 1 ? 's' : ''} \u2014 outcome: ${r.outcome || 'unknown'}`;
    } else if (layerId === 'launch-sites') {
      title = `LAUNCH: ${object.name}`;
      sub = `${object.totalLaunched.toLocaleString()} drones launched across ${object.eventCount} event${object.eventCount > 1 ? 's' : ''}`;
      detail = `Confidence: ${object.confidence}`;
    } else if (layerId === 'strike-zones') {
      title = `TARGET: ${object.name}`;
      sub = `Type: ${object.targetType} \u2014 ${object.eventCount} event${object.eventCount > 1 ? 's' : ''}`;
    } else if (layerId === 'waypoints') {
      title = object.name;
      sub = `${object.type.replace(/_/g, ' ')} waypoint`;
    } else if (layerId === 'defense-sites') {
      title = `DEFENSE: ${object.name}`;
      const totalStock = object.assets.reduce((s, a) => s + a.stock, 0);
      const weapons = object.assets.map(a => a.weapon).join(', ');
      sub = `${weapons} \u2014 ${totalStock} total stock`;
      detail = `Radar: ${object.radar_range_km || '?'}km`;
    } else if (layerId === 'iran-launch-sites') {
      title = `IRAN LAUNCH: ${object.name}`;
      sub = `Type: ${object.type.replace(/_/g, ' ')}`;
    } else if (layerId === 'iran-targets') {
      title = object.name;
      sub = object.drones_intercepted != null ? `${object.drones_intercepted} intercepted` : object.status.replace(/_/g, ' ');
      detail = `${object.distance_from_iran_km}km from Iran${object.notes ? ' \u2014 ' + object.notes : ''}`;
    }

    return (
      <div className="map-tooltip" style={{ left: x + 14, top: y - 14 }}>
        <div className="tooltip-title">{title}</div>
        {sub && <div className="tooltip-sub">{sub}</div>}
        {detail && <div className="tooltip-detail">{detail}</div>}
      </div>
    );
  };

  return (
    <>
      <DeckGL
        initialViewState={viewState}
        controller={true}
        layers={layers}
        onClick={placeSiteMode ? handleMapClick : undefined}
        getCursor={() => placeSiteMode ? 'crosshair' : 'grab'}
        style={{ width: '100%', height: '100%' }}
      >
        <MapGL mapStyle={MAP_STYLE} />
      </DeckGL>
      {renderTooltip()}
      {simMode && simTick?.counts && (
        <div className="sim-hud">
          <div className="sim-hud-row">
            <span className="sim-hud-dot sim-hud-inbound" />
            <span className="sim-hud-label">Inbound</span>
            <span className="sim-hud-val">{simTick.counts.inbound}</span>
          </div>
          <div className="sim-hud-row">
            <span className="sim-hud-dot sim-hud-intercepted" />
            <span className="sim-hud-label">Intercepted</span>
            <span className="sim-hud-val">{simTick.counts.intercepted}</span>
          </div>
          <div className="sim-hud-row">
            <span className="sim-hud-dot sim-hud-leaker" />
            <span className="sim-hud-label">Leakers</span>
            <span className="sim-hud-val">{simTick.counts.hit}</span>
          </div>
          <div className="sim-hud-divider" />
          <div className="sim-hud-row">
            <span className="sim-hud-label">Rate</span>
            <span className="sim-hud-val sim-hud-rate">
              {simTick.counts.intercepted + simTick.counts.hit > 0
                ? Math.round(simTick.counts.intercepted / (simTick.counts.intercepted + simTick.counts.hit) * 100) + '%'
                : '—'}
            </span>
          </div>
        </div>
      )}
      {placeSiteMode && (
        <div className="place-mode-banner">
          Click map to place {WEAPON_PRESETS[placeSiteMode]?.label || 'defense site'}
        </div>
      )}
      {!simMode && <div className="map-controls-br">
        {showLayerPanel && onToggleLayer && (
          <div className="ml-panel">
            <div className="ml-section-label">Layers</div>
            {LAYER_DEFS.map(({ key, label, color }) => (
              <button
                key={key}
                className={`ml-toggle ${visibleLayers[key] !== false ? 'on' : 'off'}`}
                onClick={() => onToggleLayer(key)}
              >
                <span className="ml-indicator" style={{
                  background: visibleLayers[key] !== false ? color : 'transparent',
                  borderColor: color,
                }} />
                {label}
              </button>
            ))}
          </div>
        )}
        <button className="settings-cog" onClick={() => setShowLayerPanel(p => !p)} title="Map settings">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>}
    </>
  );
}
