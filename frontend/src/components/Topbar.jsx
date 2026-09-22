import React, { useState, useEffect } from 'react';
import { StatusBadge } from './StatusBadge';
import { CloudSun, Clock } from 'lucide-react';

const PAGE_NAMES = {
  overview: 'Overview',
  forecast: 'Forecast Intelligence',
  weights: 'Adaptive AI',
  spatial: 'Spatial Intelligence',
  verification: 'Verification',
  extreme: 'Extreme Weather',
  methodology: 'Methodology',
};

export function Topbar({ activeTab = 'overview', isBackendOnline = true }) {
  const [utcTime, setUtcTime] = useState('');

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const timeStr = now.toISOString().substring(11, 19) + ' UTC';
      setUtcTime(timeStr);
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <CloudSun size={18} color="var(--text-muted)" />
        <span style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
          {PAGE_NAMES[activeTab] || 'Overview'}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          LIVE FORECAST INTELLIGENCE
        </div>
        <StatusBadge online={isBackendOnline} />
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.04em' }}>
          3 NWP SOURCES • 6 CITIES
        </div>
        {utcTime && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-subtle)', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid rgba(255, 255, 255, 0.08)', padding: '3px 8px', borderRadius: '6px' }}>
            <Clock size={12} color="var(--text-subtle)" />
            <span>{utcTime}</span>
          </div>
        )}
      </div>
    </header>
  );
}

