import { useState, useEffect, useRef } from 'react';

const BOOT_LINES = [
  { text: '', delay: 300 },
  { text: 'IMESLI DEFENCE SYSTEMS', delay: 100, cls: 'boot-brand' },
  { text: 'ASARU v1.0.0 — Visual Intelligence Platform', delay: 100, cls: 'boot-title' },
  { text: '════════════════════════════════════════════', delay: 200, cls: 'boot-rule' },
  { text: '', delay: 150 },
  { text: '> Initializing radar subsystem...', delay: 400 },
  { text: '  [OK] Radar array online', delay: 100, cls: 'boot-ok' },
  { text: '> Loading attack event database...', delay: 500 },
  { text: null, delay: 100, id: 'events' }, // filled dynamically
  { text: '> Loading flight route traces...', delay: 400 },
  { text: null, delay: 100, id: 'routes' },
  { text: '> Loading defense site configurations...', delay: 300 },
  { text: null, delay: 100, id: 'sites' },
  { text: '> Connecting map renderer...', delay: 600 },
  { text: '  [OK] deck.gl WebGL context acquired', delay: 100, cls: 'boot-ok' },
  { text: '> Running schema validation...', delay: 400 },
  { text: '  [OK] All records validated', delay: 100, cls: 'boot-ok' },
  { text: '', delay: 200 },
  { text: '════════════════════════════════════════════', delay: 100, cls: 'boot-rule' },
  { text: '  SYSTEM READY — LAUNCHING INTERFACE', delay: 300, cls: 'boot-ready' },
  { text: '', delay: 800 },
];

export default function BootScreen({ counts, onComplete }) {
  const [visibleLines, setVisibleLines] = useState([]);
  const [done, setDone] = useState(false);
  const [fadeOut, setFadeOut] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    let idx = 0;
    let timeout;

    const showNext = () => {
      if (idx >= BOOT_LINES.length) {
        setDone(true);
        setTimeout(() => {
          setFadeOut(true);
          setTimeout(() => onComplete(), 500);
        }, 200);
        return;
      }

      const line = BOOT_LINES[idx];
      let text = line.text;

      // Fill dynamic lines
      if (line.id === 'events') {
        text = `  [OK] ${counts.events.toLocaleString()} attack events loaded`;
      } else if (line.id === 'routes') {
        text = `  [OK] ${counts.routes.toLocaleString()} flight routes loaded`;
      } else if (line.id === 'sites') {
        text = `  [OK] ${counts.sites} defense sites loaded`;
      }

      setVisibleLines(prev => [...prev, { text, cls: line.cls || (line.id ? 'boot-ok' : ''), id: line.id }]);
      idx++;
      timeout = setTimeout(showNext, line.delay);
    };

    timeout = setTimeout(showNext, 400);
    return () => clearTimeout(timeout);
  }, [counts, onComplete]);

  // Auto-scroll
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [visibleLines]);

  return (
    <div className={`boot-screen ${fadeOut ? 'boot-fade-out' : ''}`}>
      <div className="boot-terminal" ref={containerRef}>
        {visibleLines.map((line, i) => (
          <div key={i} className={`boot-line ${line.cls || ''}`}>
            {line.text}
            {i === visibleLines.length - 1 && !done && <span className="boot-cursor">█</span>}
          </div>
        ))}
      </div>
      <div className="boot-footer">
        <img src={`${import.meta.env.BASE_URL}imesli-logo.svg`} alt="" className="boot-footer-logo" />
        <span className="boot-footer-text">IMESLI</span>
      </div>
    </div>
  );
}
