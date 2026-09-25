import React from 'react';
import { Wind, AlertCircle, Database, ShieldCheck } from 'lucide-react';

export function WindUnavailableNotice({ message, compact = false }) {
  return (
    <div
      className="glass-card"
      style={{
        padding: compact ? '1rem 1.25rem' : '1.75rem 2rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.06)',
            padding: '8px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Wind size={20} color="#94A3B8" />
        </div>
        <div>
          <div
            style={{
              fontSize: 'var(--font-meta)',
              fontWeight: 'var(--fw-meta)',
              color: 'var(--text-subtle)',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}
          >
            VARIABLE TELEMETRY STATUS
          </div>
          <div
            style={{
              fontSize: 'var(--font-section)',
              fontWeight: 'var(--fw-section)',
              color: 'var(--text-main)',
            }}
          >
            NWP Wind Vector Telemetry Ingestion Pending
          </div>
        </div>
      </div>

      <p
        style={{
          fontSize: 'var(--font-body)',
          color: 'var(--text-muted)',
          lineHeight: 'var(--lh-relaxed)',
          margin: 0,
        }}
      >
        {message ||
          'Multi-model NWP 10m wind vector forecast datasets (u10, v10) and ground-station reference anemometer observations are not yet ingested in this repository. In accordance with SkyBlend AI scientific honesty standards, wind trajectories and validation metrics are strictly withheld rather than displaying synthetic or fabricated values.'}
      </p>

      {!compact && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '0.85rem',
            marginTop: '0.25rem',
          }}
        >
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '0.75rem 1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)' }}>
              <Database size={13} color="#94A3B8" />
              Required Data Source
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '3px' }}>
              ECMWF, GFS & ICON 10m wind speed / vector fields (m/s or km/h).
            </div>
          </div>

          <div
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '0.75rem 1rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)' }}>
              <ShieldCheck size={13} color="#34D399" />
              Scientific Policy
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '3px' }}>
              Zero synthetic fabrication: Architecture is ready, awaiting source data.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
