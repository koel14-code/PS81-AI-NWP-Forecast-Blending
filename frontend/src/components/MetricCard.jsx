import React from 'react';

export function MetricCard({ value, label, subtext, color = 'var(--text-main)', icon: Icon }) {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
        <div className="kpi-val" style={{ color }}>{value}</div>
        {Icon && (
          <div style={{ background: 'rgba(37, 99, 235, 0.08)', padding: '6px', borderRadius: '8px' }}>
            <Icon size={16} color="var(--accent-blue)" />
          </div>
        )}
      </div>
      <div className="kpi-label">{label}</div>
      {subtext && (
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
          {subtext}
        </div>
      )}
    </div>
  );
}
