import { useState, useEffect, useMemo } from 'react';
import MapView from './MapView';
import './App.css';

const CONFLICT_META = {
  ukraine_russia: { label: 'Ukraine / Russia', color: '#f5c542', short: 'UKR' },
  iran_2026: { label: 'Iran 2026', color: '#e05252', short: 'IRN' },
};

const TARGET_TYPE_COLORS = {
  energy: '#f59e0b',
  military: '#ef4444',
  residential: '#a78bfa',
  industrial: '#64748b',
  transport: '#22d3ee',
  mixed: '#f97316',
  unknown: '#475569',
};

const ROUTE_TYPE_META = {
  direct: { color: '#60a5fa', label: 'Direct' },
  circuitous: { color: '#f59e0b', label: 'Circuitous' },
  looping: { color: '#ef4444', label: 'Looping' },
  unknown: { color: '#64748b', label: 'Unknown' },
};

const DRONE_MODEL_LABELS = {
  shahed_136: 'Shahed-136',
  shahed_131: 'Shahed-131',
  shahed_238: 'Shahed-238',
  geran_2: 'Geran-2',
  geran_3: 'Geran-3 (jet)',
  geran_5: 'Geran-5',
  gerbera_decoy: 'Gerbera (decoy)',
  parody_decoy: 'Parody (decoy)',
  supercam: 'SuperCam',
  zala: 'ZALA',
  orlan: 'Orlan',
  unknown_strike: 'Unknown (strike)',
  unknown_decoy: 'Unknown (decoy)',
  unknown: 'Unknown',
};

function fmt(n) { return n == null ? '--' : n.toLocaleString(); }
function pct(n) { return n == null ? '--' : Math.round(n * 100) + '%'; }

function App() {
  const [events, setEvents] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [selectedConflict, setSelectedConflict] = useState('all');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [activeTab, setActiveTab] = useState('sit');
  const [mapHighlight, setMapHighlight] = useState(null); // { type: 'launch'|'target'|'route', id }

  useEffect(() => {
    Promise.all([
      fetch('/data/events.json').then(r => r.json()),
      fetch('/data/routes.json').then(r => r.json()),
    ]).then(([evts, rts]) => {
      setEvents(evts);
      setRoutes(rts);
    });
  }, []);

  const filteredEvents = useMemo(() => {
    if (selectedConflict === 'all') return events;
    return events.filter(e => e.conflict === selectedConflict);
  }, [events, selectedConflict]);

  const filteredRoutes = useMemo(() => {
    const ids = new Set(filteredEvents.map(e => e.id));
    return routes.filter(r => ids.has(r.event_id));
  }, [routes, filteredEvents]);

  // ── Analytical aggregates ──

  const intel = useMemo(() => {
    const fe = filteredEvents;
    const fr = filteredRoutes;

    // Launch sites
    const launchMap = new Map();
    for (const e of fe) {
      for (const l of e.launch_regions) {
        const key = l.name;
        const existing = launchMap.get(key);
        if (existing) {
          existing.eventCount++;
          existing.totalLaunched += e.totals.launched_total || 0;
          existing.confidence = l.confidence;
        } else {
          launchMap.set(key, {
            name: l.name, lat: l.lat, lon: l.lon,
            eventCount: 1,
            totalLaunched: e.totals.launched_total || 0,
            confidence: l.confidence,
            conflict: e.conflict,
          });
        }
      }
    }
    const launchSites = [...launchMap.values()].sort((a, b) => b.totalLaunched - a.totalLaunched);

    // Target zones
    const targetMap = new Map();
    for (const e of fe) {
      for (const t of e.target_regions) {
        const key = t.name;
        const existing = targetMap.get(key);
        if (existing) {
          existing.eventCount++;
          if (t.target_type && t.target_type !== 'unknown') existing.types.add(t.target_type);
        } else {
          targetMap.set(key, {
            name: t.name, lat: t.lat, lon: t.lon,
            eventCount: 1,
            types: new Set(t.target_type && t.target_type !== 'unknown' ? [t.target_type] : []),
            conflict: e.conflict,
          });
        }
      }
    }
    const targetZones = [...targetMap.values()]
      .map(t => ({ ...t, types: [...t.types] }))
      .sort((a, b) => b.eventCount - a.eventCount);

    // Drone types aggregated
    const droneMap = new Map();
    for (const e of fe) {
      for (const d of (e.drone_types || [])) {
        const key = d.model;
        const existing = droneMap.get(key);
        if (existing) {
          existing.count += d.count || 0;
          if (d.speed_kmh) existing.speed = d.speed_kmh;
          existing.events++;
        } else {
          droneMap.set(key, {
            model: d.model,
            label: DRONE_MODEL_LABELS[d.model] || d.model,
            count: d.count || 0,
            speed: d.speed_kmh,
            events: 1,
          });
        }
      }
    }
    const droneTypes = [...droneMap.values()].sort((a, b) => b.count - a.count);

    // Route pattern breakdown
    const routePatterns = { direct: 0, circuitous: 0, looping: 0, unknown: 0 };
    const outcomeBreakdown = {};
    let totalWaypoints = 0;
    for (const r of fr) {
      routePatterns[r.route_type || 'unknown']++;
      const outcome = r.outcome || 'unknown';
      outcomeBreakdown[outcome] = (outcomeBreakdown[outcome] || 0) + (r.drone_count || 1);
      totalWaypoints += r.waypoints.length;
    }

    // Aggregate totals
    let launched = 0, intercepted = 0, hits = 0, drones = 0, missiles = 0, decoys = 0, strikes = 0;
    for (const e of fe) {
      launched += e.totals.launched_total || 0;
      intercepted += e.totals.intercepted_total || 0;
      hits += e.totals.hits || 0;
      drones += e.totals.launched_drones || 0;
      missiles += (e.totals.launched_missiles_ballistic || 0) + (e.totals.launched_missiles_cruise || 0);
      decoys += e.totals.launched_drones_decoy || 0;
      strikes += e.totals.launched_drones_strike || 0;
    }

    // Per-conflict breakdown
    const conflictStats = {};
    for (const e of fe) {
      if (!conflictStats[e.conflict]) {
        conflictStats[e.conflict] = { launched: 0, intercepted: 0, events: 0 };
      }
      conflictStats[e.conflict].launched += e.totals.launched_total || 0;
      conflictStats[e.conflict].intercepted += e.totals.intercepted_total || 0;
      conflictStats[e.conflict].events++;
    }

    return {
      launched, intercepted, hits, drones, missiles, decoys, strikes,
      launchSites, targetZones, droneTypes,
      routePatterns, outcomeBreakdown, totalWaypoints,
      totalRoutes: fr.length, totalEvents: fe.length,
      conflictStats,
    };
  }, [filteredEvents, filteredRoutes]);

  // ── Render helpers ──

  const renderSitTab = () => (
    <div className="panel-content">
      {/* Aggregate stats grid */}
      <div className="intel-section">
        <div className="section-label">Aggregate Totals</div>
        <div className="stats-grid">
          <div className="sg-item"><span className="sg-val">{fmt(intel.launched)}</span><span className="sg-label">Launched</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.intercepted)}</span><span className="sg-label">Intercepted</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.hits)}</span><span className="sg-label">Hits</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.drones)}</span><span className="sg-label">Drones</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.missiles)}</span><span className="sg-label">Missiles</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.strikes)}</span><span className="sg-label">Strike</span></div>
          <div className="sg-item"><span className="sg-val">{fmt(intel.decoys)}</span><span className="sg-label">Decoy</span></div>
          <div className="sg-item"><span className="sg-val">{intel.intercepted && intel.launched ? pct(intel.intercepted / intel.launched) : '--'}</span><span className="sg-label">Int. Rate</span></div>
        </div>
      </div>

      {/* Per-conflict comparison */}
      {Object.keys(intel.conflictStats).length > 1 && (
        <div className="intel-section">
          <div className="section-label">By Conflict</div>
          {Object.entries(intel.conflictStats).map(([conflict, s]) => (
            <div key={conflict} className="conflict-row">
              <span className="cr-dot" style={{ background: CONFLICT_META[conflict]?.color }} />
              <span className="cr-name">{CONFLICT_META[conflict]?.short || conflict}</span>
              <span className="cr-stat">{fmt(s.launched)} launched</span>
              <span className="cr-stat">{fmt(s.intercepted)} int.</span>
              <span className="cr-stat">{s.events} events</span>
            </div>
          ))}
        </div>
      )}

      {/* Launch sites */}
      <div className="intel-section">
        <div className="section-label">Launch Sites ({intel.launchSites.length})</div>
        <table className="intel-table">
          <thead><tr><th>Site</th><th>Events</th><th>Conf.</th></tr></thead>
          <tbody>
            {intel.launchSites.map((s, i) => (
              <tr key={i}
                className={mapHighlight?.type === 'launch' && mapHighlight?.id === s.name ? 'highlighted' : ''}
                onMouseEnter={() => setMapHighlight({ type: 'launch', id: s.name })}
                onMouseLeave={() => setMapHighlight(null)}
              >
                <td>
                  <span className="site-dot" style={{ background: CONFLICT_META[s.conflict]?.color || '#888' }} />
                  {s.name}
                </td>
                <td className="num">{s.eventCount}</td>
                <td><span className={`conf-badge conf-${s.confidence}`}>{s.confidence}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Target zones */}
      <div className="intel-section">
        <div className="section-label">Strike Zones ({intel.targetZones.length})</div>
        <table className="intel-table">
          <thead><tr><th>Target</th><th>Type</th><th>Events</th></tr></thead>
          <tbody>
            {intel.targetZones.map((t, i) => (
              <tr key={i}
                className={mapHighlight?.type === 'target' && mapHighlight?.id === t.name ? 'highlighted' : ''}
                onMouseEnter={() => setMapHighlight({ type: 'target', id: t.name })}
                onMouseLeave={() => setMapHighlight(null)}
              >
                <td>{t.name}</td>
                <td>
                  {t.types.length > 0 ? t.types.map(tp => (
                    <span key={tp} className="type-tag" style={{ borderColor: TARGET_TYPE_COLORS[tp] || '#555', color: TARGET_TYPE_COLORS[tp] || '#999' }}>
                      {tp}
                    </span>
                  )) : <span className="type-tag dim">--</span>}
                </td>
                <td className="num">{t.eventCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Drone models */}
      <div className="intel-section">
        <div className="section-label">Drone Types Observed ({intel.droneTypes.length})</div>
        <table className="intel-table">
          <thead><tr><th>Model</th><th>Count</th><th>Speed</th></tr></thead>
          <tbody>
            {intel.droneTypes.map((d, i) => (
              <tr key={i}>
                <td>{d.label}</td>
                <td className="num">{d.count > 0 ? fmt(d.count) : '--'}</td>
                <td className="num">{d.speed ? `${d.speed} km/h` : '--'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderRoutesTab = () => (
    <div className="panel-content">
      {/* Route pattern breakdown */}
      <div className="intel-section">
        <div className="section-label">Route Pattern Analysis</div>
        <div className="pattern-bars">
          {Object.entries(intel.routePatterns).filter(([, v]) => v > 0).map(([type, count]) => {
            const total = intel.totalRoutes || 1;
            const pctVal = Math.round((count / total) * 100);
            return (
              <div key={type} className="pattern-row">
                <span className="pr-label">
                  <span className="pr-dot" style={{ background: ROUTE_TYPE_META[type]?.color }} />
                  {ROUTE_TYPE_META[type]?.label || type}
                </span>
                <div className="pr-bar-track">
                  <div className="pr-bar-fill" style={{ width: `${pctVal}%`, background: ROUTE_TYPE_META[type]?.color }} />
                </div>
                <span className="pr-count">{count} ({pctVal}%)</span>
              </div>
            );
          })}
        </div>
        <div className="micro-stat">
          {intel.totalRoutes} routes tracked across {intel.totalWaypoints} waypoints
        </div>
      </div>

      {/* Individual routes */}
      <div className="intel-section">
        <div className="section-label">Tracked Routes</div>
        {filteredRoutes.map(route => (
          <div
            key={route.id}
            className={`route-card ${mapHighlight?.type === 'route' && mapHighlight?.id === route.id ? 'highlighted' : ''}`}
            onMouseEnter={() => setMapHighlight({ type: 'route', id: route.id })}
            onMouseLeave={() => setMapHighlight(null)}
          >
            <div className="rc-header">
              <span className="rc-dot" style={{ background: ROUTE_TYPE_META[route.route_type || 'unknown']?.color }} />
              <span className="rc-type">{route.route_type || 'unknown'}</span>
              <span className="rc-dir">{route.approach_direction || '--'}</span>
              {route.drone_count && <span className="rc-drones">{route.drone_count} UAV{route.drone_count > 1 ? 's' : ''}</span>}
            </div>
            <div className="rc-path">
              {route.waypoints.map((wp, i) => (
                <span key={i}>
                  {i > 0 && <span className="rc-arrow">&rarr;</span>}
                  <span className={`rc-wp ${wp.type === 'last_known' ? 'rc-wp-last' : ''} ${wp.type === 'intercept' ? 'rc-wp-intercept' : ''}`}>
                    {wp.name}
                  </span>
                </span>
              ))}
            </div>
            {route.notes && <div className="rc-notes">{route.notes}</div>}
            <div className="rc-meta">
              <span className={`conf-badge conf-${route.source.confidence}`}>{route.source.confidence}</span>
              <span className="rc-src">{route.source.name}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Outcome breakdown */}
      {Object.keys(intel.outcomeBreakdown).length > 0 && (
        <div className="intel-section">
          <div className="section-label">Drone Outcomes</div>
          <div className="outcome-grid">
            {Object.entries(intel.outcomeBreakdown).map(([outcome, count]) => (
              <div key={outcome} className="outcome-item">
                <span className="oi-count">{count}</span>
                <span className="oi-label">{outcome.replace(/_/g, ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderEventsTab = () => (
    <div className="panel-content">
      {filteredEvents.map(event => (
        <div
          key={event.id}
          className={`event-row ${selectedEvent?.id === event.id ? 'selected' : ''}`}
          onClick={() => setSelectedEvent(selectedEvent?.id === event.id ? null : event)}
        >
          <div className="er-top">
            <span className="er-conflict-dot" style={{ background: CONFLICT_META[event.conflict]?.color }} />
            <span className="er-date">{event.date}</span>
            <span className="er-type">{event.attack_type.replace(/_/g, ' ')}</span>
          </div>
          <div className="er-stats">
            {event.totals.launched_total != null && <span>{fmt(event.totals.launched_total)} launched</span>}
            {event.totals.intercepted_total != null && <span>{fmt(event.totals.intercepted_total)} int.</span>}
            {event.totals.interception_rate != null && <span>{pct(event.totals.interception_rate)} rate</span>}
            {event.totals.hits != null && <span>{fmt(event.totals.hits)} hits</span>}
          </div>

          {selectedEvent?.id === event.id && (
            <div className="er-detail">
              {/* Drone breakdown */}
              {event.drone_types?.length > 0 && (
                <div className="erd-section">
                  <div className="erd-label">Drone Types</div>
                  {event.drone_types.map((d, i) => (
                    <div key={i} className="erd-row">
                      <span>{DRONE_MODEL_LABELS[d.model] || d.model}</span>
                      <span>{d.count != null ? fmt(d.count) : '--'}{d.speed_kmh ? ` @ ${d.speed_kmh} km/h` : ''}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Launch regions */}
              {event.launch_regions?.length > 0 && (
                <div className="erd-section">
                  <div className="erd-label">Launch Origins</div>
                  {event.launch_regions.map((l, i) => (
                    <div key={i} className="erd-row">
                      <span>{l.name}</span>
                      <span>{l.lat && l.lon ? `${l.lat.toFixed(2)}, ${l.lon.toFixed(2)}` : '--'} <span className={`conf-badge conf-${l.confidence}`}>{l.confidence}</span></span>
                    </div>
                  ))}
                </div>
              )}

              {/* Target regions */}
              {event.target_regions?.length > 0 && (
                <div className="erd-section">
                  <div className="erd-label">Strike Zones</div>
                  {event.target_regions.map((t, i) => (
                    <div key={i} className="erd-row">
                      <span>{t.name}</span>
                      <span>
                        {t.target_type && <span className="type-tag" style={{ borderColor: TARGET_TYPE_COLORS[t.target_type] || '#555', color: TARGET_TYPE_COLORS[t.target_type] || '#999' }}>{t.target_type}</span>}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Defence context */}
              {event.defence_context?.notes && (
                <div className="erd-section">
                  <div className="erd-label">Defence Context</div>
                  <div className="erd-notes">{event.defence_context.notes}</div>
                </div>
              )}

              {event.notes && (
                <div className="erd-section">
                  <div className="erd-label">Notes</div>
                  <div className="erd-notes">{event.notes}</div>
                </div>
              )}

              {/* Sources */}
              <div className="erd-section">
                <div className="erd-label">Sources</div>
                {event.sources.map((s, i) => (
                  <div key={i} className="erd-source">
                    <span className={`conf-badge conf-${s.confidence}`}>{s.confidence}</span>
                    <span>{s.name}</span>
                    {s.fields_sourced && <span className="erd-fields">({s.fields_sourced.join(', ')})</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="sh-top">
            <div>
              <h1>ASARU</h1>
              <div className="tagline">Visual Intelligence Platform</div>
            </div>
            <div className="sh-brand">IMESLI</div>
          </div>
        </div>

        <div className="conflict-tabs">
          <button className={`conflict-tab ${selectedConflict === 'all' ? 'active' : ''}`}
            onClick={() => { setSelectedConflict('all'); setSelectedEvent(null); }}>All</button>
          {Object.entries(CONFLICT_META).map(([key, { label, color }]) => (
            <button key={key}
              className={`conflict-tab ${selectedConflict === key ? 'active' : ''}`}
              onClick={() => { setSelectedConflict(key); setSelectedEvent(null); }}>
              <span className="tab-dot" style={{ backgroundColor: color }} />
              {label}
            </button>
          ))}
        </div>

        <div className="panel-tabs">
          <button className={`ptab ${activeTab === 'sit' ? 'active' : ''}`} onClick={() => setActiveTab('sit')}>SITUATIONAL</button>
          <button className={`ptab ${activeTab === 'events' ? 'active' : ''}`} onClick={() => setActiveTab('events')}>EVENTS</button>
          <button className={`ptab ${activeTab === 'routes' ? 'active' : ''}`} onClick={() => setActiveTab('routes')}>ROUTES</button>
        </div>

        {activeTab === 'sit' && renderSitTab()}
        {activeTab === 'events' && renderEventsTab()}
        {activeTab === 'routes' && renderRoutesTab()}
      </div>

      <div className="map-container">
        <MapView
          events={filteredEvents}
          routes={filteredRoutes}
          selectedEvent={selectedEvent}
          onSelectEvent={setSelectedEvent}
          mapHighlight={mapHighlight}
        />
      </div>
    </div>
  );
}

export default App;
