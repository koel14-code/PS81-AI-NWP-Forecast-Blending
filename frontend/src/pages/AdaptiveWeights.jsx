import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { WeightChart } from '../components/WeightChart';

const LOCATIONS = [
  { id: 'kolkata', label: 'Kolkata' },
  { id: 'delhi', label: 'Delhi' },
  { id: 'mumbai', label: 'Mumbai' },
  { id: 'chennai', label: 'Chennai' },
  { id: 'guwahati', label: 'Guwahati' },
  { id: 'bengaluru', label: 'Bengaluru' },
];

function CircularGauge({ value = 0, color = '#CBD5E1', label = '', modelName = '' }) {
  const radius = 32;
  const stroke = 6;
  const normalizedRadius = radius - stroke * 0.5;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (value * circumference);

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.02)',
      border: '1px solid rgba(255, 255, 255, 0.06)',
      borderRadius: '16px',
      padding: '1.1rem 1.3rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1.25rem',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ position: 'relative', width: radius * 2, height: radius * 2, flexShrink: 0 }}>
        <svg height={radius * 2} width={radius * 2} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            stroke="rgba(255, 255, 255, 0.08)"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <motion.circle
            stroke={color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={circumference + ' ' + circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: 'easeOut' }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 'var(--font-body)',
          fontWeight: 'var(--fw-hero)',
          color: '#FFFFFF'
        }}>
          {(value * 100).toFixed(0)}%
        </div>
      </div>

      <div>
        <div style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-hero)', color, letterSpacing: '0.02em' }}>
          {modelName}
        </div>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', marginTop: '2px', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          {label}
        </div>
      </div>
    </div>
  );
}

export function AdaptiveWeights() {
  const [location, setLocation] = useState('kolkata');
  const [leadDay, setLeadDay] = useState(1);

  const { data, loading, error, retry } = useApi(
    () => api.getWeights(location, leadDay),
    [location, leadDay]
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
    >
      <SectionHeader
        eyebrow="DYNAMIC MODEL WEIGHTING"
        title="ADAPTIVE MODEL INTELLIGENCE"
        subtitle="How SkyBlend AI dynamically balances model contributions based on location, lead-time and historical skill."
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
      </div>

      {loading ? (
        <LoadingState message={`Calculating adaptive contribution weights for ${location.toUpperCase()}...`} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : (
        <>
          {/* Main Flowing Stream & Engine Process Composition */}
          <div className="split-panel-grid adaptive-grid">
            {/* Live Flowing Stream Visualization */}
            <motion.div layout transition={{ duration: 0.4 }}>
              <WeightChart
                series={data.series}
                title={`MODEL CONTRIBUTION FLOW — ${data.location.toUpperCase()} (Day ${data.lead_day})`}
              />
            </motion.div>

            {/* Right Panel: How the Engine Works + Formula Card */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Connected-Node Vertical Timeline */}
              <div className="glass-card" style={{ position: 'relative' }}>
                <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.1rem' }}>
                  HOW THE ENGINE WORKS
                </div>

                {/* Timeline Container */}
                <div style={{ position: 'relative', paddingLeft: '1.75rem' }}>
                  {/* Vertical Connecting Line */}
                  <div
                    style={{
                      position: 'absolute',
                      left: '11px',
                      top: '12px',
                      bottom: '24px',
                      width: '2px',
                      background: 'linear-gradient(180deg, #94A3B8 0%, #8B5CF6 50%, #10B981 100%)',
                    }}
                  />

                  {/* 5 Connected Steps */}
                  {[
                    { num: '01', title: 'Historical Skill', desc: 'Evaluates rolling error performance per source' },
                    { num: '02', title: 'Location Context', desc: 'Accounts for regional microclimates and topography' },
                    { num: '03', title: 'Lead-Time Context', desc: 'Adjusts trust based on 24h, 48h, 72h forecast decay' },
                    { num: '04', title: 'Adaptive Weight Engine', desc: 'Gradient boosting predicts expected error ê_m' },
                    { num: '05', title: 'Blended Forecast', desc: 'Combines predictions via normalized sum-to-1 weights' },
                  ].map((step, idx) => (
                    <div
                      key={step.num}
                      style={{
                        position: 'relative',
                        marginBottom: idx === 4 ? 0 : '1rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '2px'
                      }}
                    >
                      {/* Node Bullet Circle */}
                      <div style={{
                        position: 'absolute',
                        left: '-1.75rem',
                        top: '2px',
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: '#0D141D',
                        border: '2px solid #94A3B8',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 'var(--font-meta)',
                        fontWeight: 'var(--fw-hero)',
                        color: '#F8FAFC',
                      }}>
                        {step.num}
                      </div>

                      <div style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)' }}>
                        {step.title}
                      </div>
                      <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                        {step.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Formula Card */}
              <div className="glass-card" style={{
                background: 'rgba(255, 255, 255, 0.03)',
                borderColor: 'rgba(255, 255, 255, 0.12)',
                padding: '1.25rem',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--accent-purple)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                  BLENDING ENGINE FORMULA
                </div>
                <div style={{
                  fontSize: 'var(--font-section)',
                  fontWeight: 'var(--fw-hero)',
                  color: '#FFFFFF',
                  fontFamily: 'serif, STIXGeneral, "Times New Roman"',
                  letterSpacing: '0.04em',
                  margin: '0.3rem 0'
                }}>
                  F_blended = ∑ (w_i × F_i)
                </div>
                <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', fontFamily: 'monospace', marginBottom: '0.5rem' }}>
                  subject to  ∑ w_i = 1,  w_i ≥ 0
                </div>
                <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-main)', lineHeight: 'var(--lh-relaxed)' }}>
                  SkyBlend AI dynamically calculates contribution weights per forecast source and combines them into a single optimal prediction.
                </div>
              </div>
            </div>
          </div>

          {/* Current Adaptive Contribution Readout Gauges */}
          <div className="glass-card">
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
              CURRENT ADAPTIVE CONTRIBUTION READOUTS — {data.location.toUpperCase()} (DAY {data.lead_day})
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.1rem' }}>
              <CircularGauge
                modelName="ECMWF IFS"
                label="European Centre Model"
                value={data.means.ECMWF_IFS || 0}
                color="#64748B"
              />
              <CircularGauge
                modelName="NOAA GFS"
                label="US Global Forecast"
                value={data.means.NOAA_GFS || 0}
                color="#8B5CF6"
              />
              <CircularGauge
                modelName="DWD ICON"
                label="German Weather Service"
                value={data.means.DWD_ICON || 0}
                color="#34D399"
              />
            </div>
          </div>
        </>
      )}
    </motion.div>
  );
}
