import { useMemo, useState, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { Map as MapGL } from 'react-map-gl';
import { ScatterplotLayer, PathLayer, ArcLayer, TextLayer } from '@deck.gl/layers';
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
  unknown: [148, 163, 184],
};

const CONFLICT_COLORS = {
  ukraine_russia: [245, 197, 66],
  iran_2026: [224, 82, 82],
};

const TARGET_TYPE_COLORS = {
  energy: [245, 158, 11],
  military: [239, 68, 68],
  residential: [167, 139, 250],
  industrial: [100, 116, 139],
  transport: [34, 211, 238],
  mixed: [249, 115, 22],
  unknown: [71, 85, 105],
};

export default function MapView({ events, routes, selectedEvent, onSelectEvent, mapHighlight }) {
  const [tooltip, setTooltip] = useState(null);

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

  // ── Layers ──

  const layers = [
    // Strike corridors (arcs from launch to target)
    new ArcLayer({
      id: 'strike-corridors',
      data: arcData,
      getSourcePosition: d => d.source,
      getTargetPosition: d => d.target,
      getSourceColor: d => [...(CONFLICT_COLORS[d.event.conflict] || [150, 150, 150]), 80],
      getTargetColor: d => {
        const tc = TARGET_TYPE_COLORS[d.targetType] || TARGET_TYPE_COLORS.unknown;
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
    new PathLayer({
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
    new ScatterplotLayer({
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
        if (d.type === 'launch') return [100, 200, 100, alpha];
        if (d.type === 'intercept') return [239, 68, 68, alpha];
        if (d.type === 'target') return [239, 68, 68, alpha];
        if (d.type === 'last_known') return [245, 158, 11, alpha];
        return [148, 163, 184, alpha];
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

    // Launch sites (sized by total drones launched)
    new ScatterplotLayer({
      id: 'launch-sites',
      data: launchPoints,
      getPosition: d => d.position,
      getFillColor: d => {
        const c = CONFLICT_COLORS[d.conflict] || [150, 150, 150];
        const isHL = mapHighlight?.type === 'launch' && mapHighlight?.id === d.name;
        return [...c, isHL ? 240 : 160];
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

    // Launch site pulse ring
    new ScatterplotLayer({
      id: 'launch-pulse',
      data: launchPoints,
      getPosition: d => d.position,
      getFillColor: [0, 0, 0, 0],
      getRadius: d => Math.max(12000, Math.sqrt(d.totalLaunched) * 600),
      radiusMinPixels: 8,
      radiusMaxPixels: 30,
      stroked: true,
      getLineColor: d => {
        const c = CONFLICT_COLORS[d.conflict] || [150, 150, 150];
        return [...c, 40];
      },
      lineWidthMinPixels: 1,
    }),

    // Target / strike zones (colored by target type)
    new ScatterplotLayer({
      id: 'strike-zones',
      data: targetPoints,
      getPosition: d => d.position,
      getFillColor: d => {
        const c = TARGET_TYPE_COLORS[d.targetType] || TARGET_TYPE_COLORS.unknown;
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
    new ScatterplotLayer({
      id: 'strike-zone-ring',
      data: targetPoints,
      getPosition: d => d.position,
      getFillColor: [0, 0, 0, 0],
      getRadius: d => 12000 + d.eventCount * 4000,
      radiusMinPixels: 7,
      radiusMaxPixels: 24,
      stroked: true,
      getLineColor: d => {
        const c = TARGET_TYPE_COLORS[d.targetType] || TARGET_TYPE_COLORS.unknown;
        return [...c, 30];
      },
      lineWidthMinPixels: 1,
    }),

    // Labels
    new TextLayer({
      id: 'launch-labels',
      data: launchPoints,
      getPosition: d => d.position,
      getText: d => d.name,
      getSize: 11,
      getColor: [255, 255, 255, 140],
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

    new TextLayer({
      id: 'target-labels',
      data: targetPoints,
      getPosition: d => d.position,
      getText: d => d.name,
      getSize: 11,
      getColor: d => {
        const c = TARGET_TYPE_COLORS[d.targetType] || TARGET_TYPE_COLORS.unknown;
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
  ];

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
        style={{ width: '100%', height: '100%' }}
      >
        <MapGL mapStyle={MAP_STYLE} />
      </DeckGL>
      {renderTooltip()}
    </>
  );
}
