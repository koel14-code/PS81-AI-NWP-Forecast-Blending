import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { ForecastChart } from '../components/ForecastChart';

const LOCATIONS = [
  { id: 'kolkata', label: 'Kolkata' },
  { id: 'delhi', label: 'Delhi' },
  { id: 'mumbai', label: 'Mumbai' },
  { id: 'chennai', label: 'Chennai' },
  { id: 'guwahati', label: 'Guwahati' },
  { id: 'bengaluru', label: 'Bengaluru' },
];

export function ForecastIntelligence() {
  const [location, setLocation] = useState('kolkata');
  const [leadDay, setLeadDay] = useState(1);

  const { data, loading, error, retry } = useApi(
    () => api.getForecast(location, leadDay),
    [location, leadDay]
  );

  const { data: verifData } = useApi(api.getVerification);

  const getMaeForModel = (approachName) => {
    if (!verifData || !verifData.table) return null;
    const row = verifData.table.find(r => r.Approach === approachName);
    return row ? Number(row.MAE).toFixed(4) : null;
  };

  const ecmwfMae = getMaeForModel('ECMWF_IFS') || '—';
  const gfsMae = getMaeForModel('NOAA_GFS') || '—';
  const iconMae = getMaeForModel('DWD_ICON') || '—';
  const blendMae = getMaeForModel('Adaptive_ML_Blend') || '—';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
    >
      <SectionHeader
        eyebrow="WORKSTATION ANALYSIS"
        title="FORECAST INTELLIGENCE"
        subtitle="Compare individual numerical weather prediction sources with the SkyBlend AI adaptive forecast."
      />

      {/* Minimal Control Bar */}
      <div className="control-bar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', margin: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: '200px' }}>
            <label className="form-label">LOCATION</label>
            <select
              className="form-select"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            >
              {LOCATIONS.map((loc) => (
                <option key={loc.id} value={loc.id}>{loc.label.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label className="form-label">LEAD TIME</label>
            <div style={{ display: 'flex', gap: '6px' }}>
              {[1, 2, 3].map((day) => (
                <button
                  key={day}
                  onClick={() => setLeadDay(day)}
                  style={{
                    padding: '6px 16px',
                    borderRadius: '8px',
                    fontSize: 'var(--font-body)',
                    fontWeight: 'var(--fw-section)',
                    cursor: 'pointer',
                    border: leadDay === day ? '1px solid rgba(255, 255, 255, 0.25)' : '1px solid rgba(255, 255, 255, 0.08)',
                    background: leadDay === day ? 'rgba(255, 255, 255, 0.12)' : 'rgba(255, 255, 255, 0.03)',
                    color: leadDay === day ? '#FFFFFF' : 'var(--text-muted)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  Day {day}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Legend Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', background: 'rgba(255, 255, 255, 0.025)', padding: '6px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <span style={{ fontSize: '0.75rem', color: '#475569', fontWeight: 600 }}>── ERA5 Reference</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>── ECMWF</span>
          <span style={{ fontSize: '0.75rem', color: '#8B5CF6', fontWeight: 600 }}>── GFS</span>
          <span style={{ fontSize: '0.75rem', color: '#34D399', fontWeight: 600 }}>── ICON</span>
          <span style={{ fontSize: '0.75rem', color: '#F8FAFC', fontWeight: 800 }}>━━ SkyBlend AI</span>
        </div>
      </div>

      {loading ? (
        <LoadingState message={`Fetching forecast signal for ${location.toUpperCase()} (Day ${leadDay})...`} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : (
        <>
          {/* Main Forecast Line Chart Surface occupying viewport */}
          <div style={{ minHeight: '380px' }}>
            <ForecastChart
              series={data.series}
              title={`Precipitation Trajectories — ${data.location.toUpperCase()} (Day ${data.lead_day} Horizon)`}
            />
          </div>

          {/* Model Skill Benchmarks */}
          <div className="glass-card">
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.85rem' }}>
              HISTORICAL MODEL SKILL PROFILE (JULY 2024 EVALUATION)
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.025)', padding: '0.9rem 1.1rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#94A3B8' }}>ECMWF IFS</div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-subtle)', marginTop: '2px', textTransform: 'uppercase' }}>SOURCE: ECMWF (EUROPE)</div>
                <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--text-main)', marginTop: '4px' }}>
                  {ecmwfMae} <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>mm/h MAE</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.025)', padding: '0.9rem 1.1rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#8B5CF6' }}>NOAA GFS</div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-subtle)', marginTop: '2px', textTransform: 'uppercase' }}>SOURCE: NOAA (USA)</div>
                <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--text-main)', marginTop: '4px' }}>
                  {gfsMae} <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>mm/h MAE</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.025)', padding: '0.9rem 1.1rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#34D399' }}>DWD ICON</div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-subtle)', marginTop: '2px', textTransform: 'uppercase' }}>SOURCE: DWD (GERMANY)</div>
                <div style={{ fontSize: '1.35rem', fontWeight: 900, color: 'var(--text-main)', marginTop: '4px' }}>
                  {iconMae} <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>mm/h MAE</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '0.9rem 1.1rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.16)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#F8FAFC' }}>SkyBlend AI</div>
                <div style={{ fontSize: '0.68rem', color: '#CBD5E1', marginTop: '2px', fontWeight: 800, textTransform: 'uppercase' }}>CONSENSUS BLEND</div>
                <div style={{ fontSize: '1.35rem', fontWeight: 900, color: '#F8FAFC', marginTop: '4px' }}>
                  {blendMae} <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#CBD5E1' }}>mm/h MAE</span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </motion.div>
  );
}
