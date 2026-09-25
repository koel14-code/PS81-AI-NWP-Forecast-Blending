import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ReferenceLine } from 'recharts';
import { CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';
import { VariableSelector } from '../components/VariableSelector';
import { WindUnavailableNotice } from '../components/WindUnavailableNotice';

const LOCATIONS = [
  { id: 'kolkata', label: 'Kolkata' },
  { id: 'delhi', label: 'Delhi' },
  { id: 'mumbai', label: 'Mumbai' },
  { id: 'chennai', label: 'Chennai' },
  { id: 'guwahati', label: 'Guwahati' },
  { id: 'bengaluru', label: 'Bengaluru' },
];

export function ExtremeWeather() {
  const [location, setLocation] = useState('kolkata');
  const [leadDay, setLeadDay] = useState(1);
  const [variable, setVariable] = useState('precipitation');

  const { data, loading, error, retry } = useApi(
    () => api.getExtremeSignal(location, leadDay, variable),
    [location, leadDay, variable]
  );

  const isWind = variable === 'wind';
  const isTemp = variable === 'temperature';
  const unit = isTemp ? '°C' : isWind ? 'km/h' : 'mm/h';

  const getStatusConfig = (status, isFlagged) => {
    const s = (status || '').toUpperCase();
    if (s.includes('NOT CONFIGURED') || s.includes('INSUFFICIENT')) {
      return {
        label: 'NOT CONFIGURED / INSUFFICIENT EVIDENCE',
        color: '#64748B',
        bg: 'rgba(100, 116, 139, 0.12)',
        border: 'rgba(100, 116, 139, 0.35)',
      };
    }
    if (s.includes('ACTIVE') || s.includes('HEAT') || s.includes('HIGH-WIND') || isFlagged) {
      return {
        label: isTemp ? 'HIGH-TEMPERATURE / HEAT-RISK SIGNAL' : isWind ? 'HIGH-WIND SPEED ANALYTICAL SIGNAL' : 'ACTIVE PRECIPITATION SIGNAL',
        color: '#EF4444',
        bg: 'rgba(239, 68, 68, 0.12)',
        border: 'rgba(239, 68, 68, 0.35)',
      };
    } else if (s.includes('MONITOR')) {
      return {
        label: 'MONITOR SIGNAL',
        color: '#F59E0B',
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.35)',
      };
    } else {
      return {
        label: isWind ? 'BELOW PROJECT HIGH-WIND THRESHOLD' : 'BELOW ANALYTICAL THRESHOLD',
        color: '#10B981',
        bg: 'rgba(16, 185, 129, 0.12)',
        border: 'rgba(16, 185, 129, 0.35)',
      };
    }
  };

  const chartSeries = (data?.series || []).map((item) => {
    let t = item.valid_time;
    if (t && t.includes('T')) {
      t = t.split('T')[1]?.substring(0, 5) || t;
    }
    return { ...item, timeLabel: t };
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
    >
      <SectionHeader
        eyebrow="ANALYTICAL SIGNAL MONITORING"
        title="EXTREME WEATHER GUIDANCE"
        subtitle="Analytical risk indicators derived from the blended forecast across precipitation, temperature, and wind."
      />

      {/* Control Bar */}
      <div className="control-bar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', margin: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <VariableSelector value={variable} onChange={(v) => setVariable(v)} />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: '180px' }}>
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

        {/* Mandatory Explicit Disclaimer Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          padding: '6px 14px',
          borderRadius: '8px',
          fontSize: '0.72rem',
          fontWeight: 800,
          color: '#F87171',
          letterSpacing: '0.04em',
          textTransform: 'uppercase'
        }}>
          <ShieldAlert size={14} color="#F87171" />
          <span>Analytical Signal — Not an Official Warning</span>
        </div>
      </div>

      {loading ? (
        <LoadingState message={`Analyzing ${variable} extreme guidance for ${location.toUpperCase()}...`} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : isWind && data?.status === 'unavailable' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-card hero-glass-panel" style={{ padding: '1.6rem', border: '1px solid rgba(100, 116, 139, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <AlertTriangle size={18} color="#94A3B8" />
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-main)' }}>
                HIGH-WIND SIGNAL: NOT CONFIGURED / INSUFFICIENT EVIDENCE
              </div>
            </div>
            <p style={{ fontSize: 'var(--font-body)', color: 'var(--text-muted)', margin: 0, lineHeight: 'var(--lh-relaxed)' }}>
              Wind speed telemetry is currently unavailable. To preserve scientific honesty, arbitrary wind thresholds are strictly withheld rather than displaying synthetic alerts.
            </p>
          </div>
          <WindUnavailableNotice compact />
        </div>
      ) : (
        <>
          {/* Top Monitoring Panel */}
          {(() => {
            const statusCfg = getStatusConfig(data?.status, data?.is_flagged);
            const currentVal = data?.max_blended || 0;
            const thresholdVal = data?.threshold || (isTemp ? 38.0 : isWind ? 40.0 : 1.0);
            const maxGaugeVal = isTemp
              ? Math.max(50.0, currentVal * 1.1)
              : isWind
              ? Math.max(60.0, thresholdVal * 1.5, currentVal * 1.2)
              : Math.max(thresholdVal * 2.5, currentVal * 1.2, 3.0);
            const currentPct = Math.min((currentVal / maxGaugeVal) * 100, 100);
            const thresholdPct = Math.min((thresholdVal / maxGaugeVal) * 100, 100);

            return (
              <div className="glass-card hero-glass-panel" style={{
                background: `linear-gradient(135deg, ${statusCfg.bg} 0%, rgba(10, 17, 28, 0.96) 100%)`,
                borderColor: statusCfg.border,
                padding: '1.6rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  <div>
                    <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      ANALYTICAL SIGNAL STATUS — {data?.location?.toUpperCase()} (DAY {data?.lead_day})
                    </div>
                    {/* Status Pill */}
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginTop: '8px',
                      padding: '6px 16px',
                      borderRadius: '20px',
                      background: statusCfg.bg,
                      border: `1.5px solid ${statusCfg.color}`
                    }}>
                      <span style={{ width: 10, height: 10, borderRadius: '50%', background: statusCfg.color }} />
                      <span style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-hero)', color: statusCfg.color, letterSpacing: '0.04em' }}>
                        {statusCfg.label}
                      </span>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                      {isTemp ? 'MAXIMUM BLENDED TEMPERATURE' : isWind ? 'MAXIMUM BLENDED 10M WIND SPEED' : 'MAXIMUM BLENDED PRECIPITATION'}
                    </div>
                    <div style={{ fontSize: 'var(--font-stat)', fontWeight: 'var(--fw-hero)', color: '#F8FAFC', lineHeight: 'var(--lh-tight)', marginTop: '2px' }}>
                      {currentVal.toFixed(1)} <span style={{ fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: 'var(--text-muted)' }}>{unit}</span>
                    </div>
                  </div>
                </div>

                {/* Explicit Disclaimer subtext */}
                <div style={{
                  fontSize: 'var(--font-small)',
                  color: 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)'
                }}>
                  <b>Notice:</b> Analytical Signal — Not an Official Warning. These indicators represent project diagnostic thresholds for decision-support prototypes.
                </div>

                {/* Horizontal Gauge Bar */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '0.2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)' }}>
                    <span>CURRENT BLENDED MAX: <strong style={{ color: '#F8FAFC' }}>{currentVal.toFixed(1)} {unit}</strong></span>
                    <span style={{ color: 'var(--accent-amber)' }}>
                      PROJECT ANALYTICAL THRESHOLD — {thresholdVal.toFixed(1)} {unit}
                    </span>
                  </div>

                  <div style={{ width: '100%', height: '14px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '7px', position: 'relative', overflow: 'hidden' }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${currentPct}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      style={{
                        height: '100%',
                        background: currentVal >= thresholdVal ? 'linear-gradient(90deg, #F59E0B, #EF4444)' : 'linear-gradient(90deg, #475569, #94A3B8)',
                        borderRadius: '7px'
                      }}
                    />
                    <div style={{
                      position: 'absolute',
                      left: `${thresholdPct}%`,
                      top: 0,
                      bottom: 0,
                      width: '2px',
                      background: '#F59E0B',
                      zIndex: 5
                    }} />
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Context Indicators Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            <div className="glass-card">
              <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                SIGNAL CONTEXT INDICATORS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {[
                  'Multi-model forecast consensus',
                  'Historical model reliability weighting',
                  'Location microclimate adjustment',
                  'Forecast horizon decay tracking'
                ].map((item, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: 'var(--font-body)', color: 'var(--text-main)' }}>
                    <CheckCircle2 size={16} color="var(--accent-green)" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card">
              <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--accent-amber)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                CALIBRATED THRESHOLD BASIS
              </div>
              <div style={{ fontSize: 'var(--font-body)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)' }}>
                {isTemp ? (
                  <>The <b>38.0°C threshold</b> is a calibrated project heat-risk indicator reflecting severe diurnal thermal stress across Indian urban centers.</>
                ) : isWind ? (
                  <>The <b>40.0 km/h threshold</b> (Beaufort Force 6 strong breeze) is an analytical project diagnostic threshold for surface wind velocity across Indian urban corridors. It is NOT an official IMD disaster warning.</>
                ) : (
                  <>The <b>1.0 mm/h threshold</b> is a calibrated project precipitation advisory threshold identifying non-trivial rain episodes across evaluation lead horizons.</>
                )}
              </div>
            </div>
          </div>

          {/* Time Series Line Chart */}
          <div className="glass-card">
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.85rem' }}>
              BLENDED {variable.toUpperCase()} TRAJECTORY VS THRESHOLD — {data?.location?.toUpperCase()} (DAY {data?.lead_day})
            </div>
            <div style={{ width: '100%', height: 340 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartSeries} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                  <XAxis dataKey="timeLabel" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                  <YAxis stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} unit={` ${unit}`} />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(14, 23, 38, 0.95)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '10px',
                      fontSize: '12px',
                      color: '#F8FAFC'
                    }}
                    labelStyle={{ color: '#F8FAFC', fontWeight: 700 }}
                    formatter={(val) => [`${typeof val === 'number' ? val.toFixed(2) : val} ${unit}`, '']}
                  />
                  <Legend wrapperStyle={{ color: '#94A3B8', fontSize: '12px', paddingTop: '8px' }} />
                  <ReferenceLine
                    y={data?.threshold || (isTemp ? 38.0 : isWind ? 40.0 : 1.0)}
                    label={{
                      value: `Project analytical threshold (${(data?.threshold || (isTemp ? 38.0 : isWind ? 40.0 : 1.0)).toFixed(1)} ${unit})`,
                      fill: '#EF4444',
                      fontSize: 11,
                      position: 'insideTopRight'
                    }}
                    stroke="#EF4444"
                    strokeDasharray="4 4"
                    strokeWidth={1.8}
                  />
                  {chartSeries[0]?.reference_precipitation !== undefined && (
                    <Line type="monotone" dataKey="reference_precipitation" name="ERA5 Reference" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.8} dot={false} />
                  )}
                  {chartSeries[0]?.reference_temperature !== undefined && (
                    <Line type="monotone" dataKey="reference_temperature" name="Station Ref" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.8} dot={false} />
                  )}
                  {chartSeries[0]?.reference_wind !== undefined && (
                    <Line type="monotone" dataKey="reference_wind" name="ERA5 Ref (10m)" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.8} dot={false} />
                  )}
                  <Line
                    type="monotone"
                    dataKey={isTemp ? 'blended_temperature' : isWind ? 'blended_wind' : 'blended_precipitation'}
                    name="SkyBlend AI Forecast"
                    stroke="#F8FAFC"
                    strokeWidth={2.8}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </motion.div>
  );
}
