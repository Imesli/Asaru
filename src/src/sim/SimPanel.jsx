import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { runSimulation } from './engine.js';

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

export default function SimPanel({
  events, routes, defenseSites, onSimTick, onSimResults, visible,
  onUpdateDefenseSites, onPlaceSiteMode,
}) {
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [simState, setSimState] = useState('idle');
  const [simResults, setSimResults] = useState(null);
  const [playbackIdx, setPlaybackIdx] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSection, setActiveSection] = useState('attack'); // attack | defense | results
  const [editingSiteId, setEditingSiteId] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const ticksRef = useRef([]);
  const animRef = useRef(null);
  const lastFrameRef = useRef(0);

  const simableEvents = useMemo(() => {
    const routeEventIds = new Set(routes.map(r => r.event_id));
    return events.filter(e => routeEventIds.has(e.id)).sort((a, b) => b.date.localeCompare(a.date));
  }, [events, routes]);

  const eventRoutes = useMemo(() => {
    if (!selectedEventId) return [];
    return routes.filter(r => r.event_id === selectedEventId);
  }, [routes, selectedEventId]);

  const selectedEvent = useMemo(() => events.find(e => e.id === selectedEventId), [events, selectedEventId]);

  // Run sim
  const handleRun = useCallback(() => {
    if (!selectedEventId || eventRoutes.length === 0) return;
    setSimState('running');
    setPlaybackIdx(0);
    setIsPlaying(false);

    setTimeout(() => {
      const results = runSimulation({
        routes: eventRoutes, defenseSites, event: selectedEvent, timeStepSec: 10,
      });
      ticksRef.current = results.ticks;
      setSimResults(results);
      setSimState('done');
      setActiveSection('results');
      if (onSimResults) onSimResults(results);
      if (results.ticks.length > 0 && onSimTick) onSimTick(results.ticks[0]);
    }, 50);
  }, [selectedEventId, eventRoutes, defenseSites, selectedEvent, onSimTick, onSimResults]);

  // Compare: run same attack with current vs saved config
  const handleCompare = useCallback(() => {
    if (!selectedEventId || eventRoutes.length === 0 || !simResults) return;
    setComparisonResult(simResults);
    // Re-run with current (possibly modified) defense sites
    setTimeout(() => {
      const newResults = runSimulation({
        routes: eventRoutes, defenseSites, event: selectedEvent, timeStepSec: 10,
      });
      ticksRef.current = newResults.ticks;
      setSimResults(newResults);
      setSimState('done');
      if (onSimResults) onSimResults(newResults);
      if (newResults.ticks.length > 0 && onSimTick) onSimTick(newResults.ticks[0]);
    }, 50);
  }, [selectedEventId, eventRoutes, defenseSites, selectedEvent, simResults, onSimTick, onSimResults]);

  // Playback
  useEffect(() => {
    if (!isPlaying || simState !== 'done') return;
    const ticks = ticksRef.current;
    const msPerTick = 100 / playbackSpeed;
    const step = (timestamp) => {
      if (timestamp - lastFrameRef.current >= msPerTick) {
        lastFrameRef.current = timestamp;
        setPlaybackIdx(prev => {
          const next = prev + 1;
          if (next >= ticks.length) { setIsPlaying(false); return prev; }
          if (onSimTick) onSimTick(ticks[next]);
          return next;
        });
      }
      animRef.current = requestAnimationFrame(step);
    };
    animRef.current = requestAnimationFrame(step);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [isPlaying, playbackSpeed, simState, onSimTick]);

  const handleScrub = useCallback((e) => {
    const idx = parseInt(e.target.value, 10);
    setPlaybackIdx(idx);
    if (ticksRef.current[idx] && onSimTick) onSimTick(ticksRef.current[idx]);
  }, [onSimTick]);

  // Defense site management
  const removeSite = (id) => {
    if (onUpdateDefenseSites) onUpdateDefenseSites(defenseSites.filter(s => s.id !== id));
  };

  const addPreset = (presetKey, name, lat, lon) => {
    const preset = WEAPON_PRESETS[presetKey];
    const newId = `DS_UA_${String(defenseSites.length + 1).padStart(3, '0')}`;
    const newSite = {
      id: newId, conflict: 'ukraine_russia', name, lat, lon,
      status: 'active', assets: preset.assets, radar_range_km: preset.radar_range_km,
      notes: `User-placed ${preset.label}`,
      sources: [{ name: 'Sim placement', confidence: 'sim_placement' }],
    };
    if (onUpdateDefenseSites) onUpdateDefenseSites([...defenseSites, newSite]);
  };

  const updateSiteStock = (siteId, assetIdx, newStock) => {
    const updated = defenseSites.map(s => {
      if (s.id !== siteId) return s;
      const assets = s.assets.map((a, i) => i === assetIdx ? { ...a, stock: newStock } : a);
      return { ...s, assets };
    });
    if (onUpdateDefenseSites) onUpdateDefenseSites(updated);
  };

  // Save/load configs
  const saveConfig = () => {
    const config = JSON.stringify(defenseSites);
    localStorage.setItem('asaru_defense_config', config);
  };

  const loadConfig = () => {
    const saved = localStorage.getItem('asaru_defense_config');
    if (saved && onUpdateDefenseSites) {
      onUpdateDefenseSites(JSON.parse(saved));
    }
  };

  const hasSavedConfig = !!localStorage.getItem('asaru_defense_config');

  if (!visible) return null;

  return (
    <div className="sim-panel">
      <div className="sim-header">SIM ENGINE</div>

      {/* Section tabs */}
      <div className="sim-tabs">
        <button className={`sim-tab ${activeSection === 'attack' ? 'active' : ''}`}
          onClick={() => setActiveSection('attack')}>Attack</button>
        <button className={`sim-tab ${activeSection === 'defense' ? 'active' : ''}`}
          onClick={() => setActiveSection('defense')}>Defense</button>
        <button className={`sim-tab ${activeSection === 'results' ? 'active' : ''}`}
          onClick={() => setActiveSection('results')}>Results</button>
      </div>

      {/* ─── ATTACK section ─── */}
      {activeSection === 'attack' && (
        <>
          <div className="sim-section">
            <label className="sim-label">Attack event</label>
            <select className="sim-select" value={selectedEventId || ''}
              onChange={e => { setSelectedEventId(e.target.value || null); setSimState('idle'); setSimResults(null); setComparisonResult(null); }}>
              <option value="">Select an event…</option>
              {simableEvents.map(ev => (
                <option key={ev.id} value={ev.id}>
                  {ev.date} — {ev.totals?.launched_total || '?'} drones
                  {ev.conflict === 'iran_2026' ? ' [Iran]' : ' [UA]'}
                </option>
              ))}
            </select>
          </div>

          {selectedEvent && (
            <div className="sim-section sim-event-info">
              <div className="sim-stat-row">
                <span className="sim-stat-label">Routes available</span>
                <span className="sim-stat-value">{eventRoutes.length}</span>
              </div>
              <div className="sim-stat-row">
                <span className="sim-stat-label">Drones launched</span>
                <span className="sim-stat-value">{selectedEvent.totals?.launched_total || '—'}</span>
              </div>
              <div className="sim-stat-row">
                <span className="sim-stat-label">Actual intercept rate</span>
                <span className="sim-stat-value">
                  {selectedEvent.totals?.intercepted_total && selectedEvent.totals?.launched_total
                    ? `${Math.round(selectedEvent.totals.intercepted_total / selectedEvent.totals.launched_total * 100)}%`
                    : '—'}
                </span>
              </div>
              <div className="sim-stat-row">
                <span className="sim-stat-label">Defense sites</span>
                <span className="sim-stat-value">{defenseSites.length}</span>
              </div>
            </div>
          )}

          {selectedEventId && (
            <button className="sim-run-btn" onClick={handleRun}>
              {simState === 'done' ? 'Re-run Simulation' : 'Run Simulation'}
            </button>
          )}

          {simState === 'running' && <div className="sim-running">Running…</div>}
        </>
      )}

      {/* ─── DEFENSE section ─── */}
      {activeSection === 'defense' && (
        <>
          <div className="sim-section">
            <div className="sim-label">Add Defense Site</div>
            <div className="sim-presets">
              {Object.entries(WEAPON_PRESETS).map(([key, preset]) => (
                <button key={key} className="sim-preset-btn"
                  onClick={() => {
                    if (onPlaceSiteMode) onPlaceSiteMode(key);
                  }}>
                  {preset.label}
                </button>
              ))}
            </div>
            <div className="sim-hint">Click a preset, then click the map to place it</div>
          </div>

          <div className="sim-section">
            <div className="sim-label">Config</div>
            <div className="sim-config-btns">
              <button className="sim-config-btn" onClick={saveConfig}>Save layout</button>
              <button className="sim-config-btn" onClick={loadConfig} disabled={!hasSavedConfig}>
                Load saved
              </button>
            </div>
          </div>

          <div className="sim-section sim-sites-list">
            <div className="sim-label">Active Sites ({defenseSites.length})</div>
            {defenseSites.map(site => (
              <div key={site.id} className={`sim-site-card ${editingSiteId === site.id ? 'editing' : ''}`}>
                <div className="sim-site-header" onClick={() => setEditingSiteId(editingSiteId === site.id ? null : site.id)}>
                  <span className="sim-site-name-sm">{site.name}</span>
                  <button className="sim-site-remove" onClick={(e) => { e.stopPropagation(); removeSite(site.id); }}>×</button>
                </div>
                {editingSiteId === site.id && (
                  <div className="sim-site-edit">
                    {site.assets.map((asset, ai) => (
                      <div key={ai} className="sim-asset-edit">
                        <span className="sim-asset-name">{asset.weapon}</span>
                        <div className="sim-stock-control">
                          <button onClick={() => updateSiteStock(site.id, ai, Math.max(0, asset.stock - 5))}>-</button>
                          <span className="sim-stock-val">{asset.stock}</span>
                          <button onClick={() => updateSiteStock(site.id, ai, asset.stock + 5)}>+</button>
                        </div>
                        <span className="sim-asset-range">{asset.range_km}km</span>
                      </div>
                    ))}
                    <div className="sim-site-coords">
                      {site.lat.toFixed(2)}, {site.lon.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {/* ─── RESULTS section ─── */}
      {activeSection === 'results' && (
        <>
          {/* Playback controls */}
          {simState === 'done' && simResults && (
            <>
              <div className="sim-section sim-playback">
                <div className="sim-playback-controls">
                  <button className="sim-step-btn" onClick={() => {
                    const prev = Math.max(0, playbackIdx - 1);
                    setPlaybackIdx(prev); setIsPlaying(false);
                    if (ticksRef.current[prev] && onSimTick) onSimTick(ticksRef.current[prev]);
                  }}>⏮</button>
                  <button className="sim-play-btn" onClick={() => {
                    if (playbackIdx >= ticksRef.current.length - 1) setPlaybackIdx(0);
                    setIsPlaying(p => !p);
                  }}>{isPlaying ? '⏸' : '▶'}</button>
                  <button className="sim-step-btn" onClick={() => {
                    const next = Math.min(ticksRef.current.length - 1, playbackIdx + 1);
                    setPlaybackIdx(next); setIsPlaying(false);
                    if (ticksRef.current[next] && onSimTick) onSimTick(ticksRef.current[next]);
                  }}>⏭</button>
                  <input type="range" className="sim-scrubber" min={0}
                    max={ticksRef.current.length - 1} value={playbackIdx} onChange={handleScrub} />
                  <select className="sim-speed" value={playbackSpeed}
                    onChange={e => setPlaybackSpeed(Number(e.target.value))}>
                    <option value={0.5}>0.5x</option>
                    <option value={1}>1x</option>
                    <option value={2}>2x</option>
                    <option value={5}>5x</option>
                    <option value={10}>10x</option>
                  </select>
                </div>
                <div className="sim-time-label">
                  T+{Math.round((ticksRef.current[playbackIdx]?.time || 0) / 60)}min
                  {' / '}{Math.round(simResults.simDurationSec / 60)}min
                </div>
              </div>

              {/* Comparison */}
              {comparisonResult && (
                <div className="sim-section sim-comparison">
                  <div className="sim-results-header">Comparison</div>
                  <div className="sim-compare-grid">
                    <div /><div className="sim-compare-label">Previous</div><div className="sim-compare-label">Current</div>
                    <div className="sim-compare-label">Intercept</div>
                    <div className="sim-compare-val">{Math.round(comparisonResult.interceptionRate * 100)}%</div>
                    <div className={`sim-compare-val ${simResults.interceptionRate > comparisonResult.interceptionRate ? 'better' : 'worse'}`}>
                      {Math.round(simResults.interceptionRate * 100)}%
                    </div>
                    <div className="sim-compare-label">Leakers</div>
                    <div className="sim-compare-val">{comparisonResult.leakers}</div>
                    <div className={`sim-compare-val ${simResults.leakers < comparisonResult.leakers ? 'better' : 'worse'}`}>
                      {simResults.leakers}
                    </div>
                  </div>
                </div>
              )}

              {/* Results */}
              <div className="sim-section sim-results">
                <div className="sim-results-header">Results</div>
                <div className="sim-stat-row">
                  <span className="sim-stat-label">Overall intercept</span>
                  <span className="sim-stat-value sim-stat-good">
                    {Math.round(simResults.interceptionRate * 100)}%
                  </span>
                </div>
                <div className="sim-stat-row">
                  <span className="sim-stat-label">Intercepted</span>
                  <span className="sim-stat-value">{simResults.intercepted}/{simResults.totalDrones}</span>
                </div>
                <div className="sim-stat-row">
                  <span className="sim-stat-label">Leakers (hit target)</span>
                  <span className="sim-stat-value sim-stat-bad">{simResults.leakers}</span>
                </div>
                {simResults.strikeTotal > 0 && simResults.decoyTotal > 0 && (
                  <>
                    <div className="sim-stat-row" style={{ marginTop: 6, paddingTop: 6, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                      <span className="sim-stat-label">Strike intercept</span>
                      <span className="sim-stat-value sim-stat-good">
                        {Math.round(simResults.strikeInterceptionRate * 100)}%
                      </span>
                    </div>
                    <div className="sim-stat-row">
                      <span className="sim-stat-label">Strike drones</span>
                      <span className="sim-stat-value">{simResults.strikeIntercepted}/{simResults.strikeTotal}</span>
                    </div>
                    <div className="sim-stat-row">
                      <span className="sim-stat-label">Decoys in swarm</span>
                      <span className="sim-stat-value">{simResults.decoyTotal}</span>
                    </div>
                    <div className="sim-stat-row">
                      <span className="sim-stat-label">Interceptors wasted on decoys</span>
                      <span className="sim-stat-value" style={{ color: simResults.decoysWasted > 0 ? '#f59e0b' : 'inherit' }}>
                        {simResults.decoysWasted}
                      </span>
                    </div>
                  </>
                )}
                <div className="sim-stat-row">
                  <span className="sim-stat-label">Total engagements</span>
                  <span className="sim-stat-value">{simResults.totalEngagements}</span>
                </div>
              </div>

              {/* Per-site breakdown */}
              <div className="sim-section sim-sites">
                <div className="sim-results-header">Site Performance</div>
                {simResults.siteResults.map(site => (
                  <div key={site.id} className="sim-site-row">
                    <div className="sim-site-name">{site.name}</div>
                    {site.assets.map((a, i) => (
                      <div key={i} className="sim-asset-row">
                        <span className="sim-asset-weapon">{a.weapon}</span>
                        <span className="sim-asset-stat">{a.fired} fired / {a.remaining} left</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              <div className="sim-btn-group">
                <button className="sim-run-btn sim-rerun" onClick={handleRun}>Re-run (new RNG)</button>
                <button className="sim-run-btn sim-rerun" onClick={handleCompare}>Compare</button>
              </div>
            </>
          )}

          {simState !== 'done' && (
            <div className="sim-empty-state">
              Select an attack and run the simulation to see results here.
            </div>
          )}
        </>
      )}
    </div>
  );
}
