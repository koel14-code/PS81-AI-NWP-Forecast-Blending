import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../api/client';
import { useAnimatedNumber } from '../hooks/useAnimatedNumber';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { ArrowRight, ChevronDown, ChevronUp, HelpCircle, Clock, Calendar } from 'lucide-react';
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

const getRainConditionLabel = (val) => {
  const n = parseFloat(val);
  if (isNaN(n) || n === 0) return 'DRY / STABLE';
  if (n < 0.25) return 'LIGHT PRECIPITATION';
  if (n < 1.0) return 'MODERATE RAINFALL';
  if (n < 3.0) return 'HEAVY MONSOON STREAM';
  return 'EXTREME PRECIPITATION';
};

const getTempConditionLabel = (val) => {
  const n = parseFloat(val);
  if (isNaN(n)) return '—';
  if (n >= 42.0) return 'SEVERE HEAT HAZARD';
  if (n >= 38.0) return 'HIGH THERMAL RISK';
  if (n >= 30.0) return 'WARM / TROPICAL';
  if (n >= 20.0) return 'MODERATE / TEMPERATE';
  return 'COOL / STABLE';
};

export function Overview({ onNavigate }) {
  const [location, setLocation] = useState('kolkata');
  const [leadDay, setLeadDay] = useState(1);
  const [variable, setVariable] = useState('precipitation');
  const [showDetails, setShowDetails] = useState(false);

  const [overviewData, setOverviewData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [weightsData, setWeightsData] = useState(null);
  const [verifData, setVerifData] = useState(null);
  const [spatialData, setSpatialData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [ov, fc, wt, verif, sp] = await Promise.all([
        api.getOverview(variable),
        api.getForecast(location, leadDay, variable),
        api.getWeights(location, leadDay, variable),
        api.getVerification(variable),
        api.getSpatialWeights(leadDay, variable),
      ]);
      setOverviewData(ov);
      setForecastData(fc);
      setWeightsData(wt);
      setVerifData(verif);
      setSpatialData(sp);
    } catch (err) {
      setError(err.message || 'Failed to load weather workstation data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [location, leadDay, variable]);

  const series = forecastData?.series || [];

  // Compute variable-aware peak / max
  let rawMax = null;
  let unit = 'mm/h';
  let metricTitle = `PEAK RAINFALL INTENSITY — ${location.toUpperCase()} (DAY ${leadDay})`;
  let conditionLabel = '—';

  if (variable === 'temperature') {
    unit = '°C';
    metricTitle = `MAXIMUM TEMPERATURE — ${location.toUpperCase()} (DAY ${leadDay})`;
    rawMax = series.length > 0 ? Math.max(...series.map((s) => s.blended_temperature || 0)) : null;
    conditionLabel = rawMax != null ? getTempConditionLabel(rawMax) : '—';
  } else if (variable === 'wind') {
    unit = 'km/h';
    metricTitle = `MAXIMUM WIND SPEED — ${location.toUpperCase()} (DAY ${leadDay})`;
    rawMax = null;
    conditionLabel = 'TELEMETRY PENDING';
  } else {
    unit = 'mm/h';
    metricTitle = `PEAK RAINFALL INTENSITY — ${location.toUpperCase()} (DAY ${leadDay})`;
    rawMax = series.length > 0 ? Math.max(...series.map((s) => s.blended_precipitation || 0)) : null;
    conditionLabel = rawMax != null ? getRainConditionLabel(rawMax) : '—';
  }

  const animatedMax = useAnimatedNumber(rawMax != null ? rawMax : 0, variable === 'temperature' ? 1 : 2, 800);
  const maxDisplay = rawMax != null ? animatedMax : '—';

  const isWind = variable === 'wind';

  const formattedTrajectory = series.map((item) => {
    let t = item.valid_time;
    if (t && t.includes('T')) {
      t = t.split('T')[1]?.substring(0, 5) || t;
    }
    return { ...item, timeLabel: t };
  });

  const ecmwfPct = weightsData?.means?.ECMWF_IFS != null && !isWind ? Math.round(weightsData.means.ECMWF_IFS * 100) : null;
  const gfsPct = weightsData?.means?.NOAA_GFS != null && !isWind ? Math.round(weightsData.means.NOAA_GFS * 100) : null;
  const iconPct = weightsData?.means?.DWD_ICON != null && !isWind ? Math.round(weightsData.means.DWD_ICON * 100) : null;

  const targetDate = forecastData?.target_date || '—';
  const runTime = forecastData?.forecast_run_time ? forecastData.forecast_run_time.substring(0, 10) + ' 00:00 UTC' : '—';

  const getCityTopWeight = (loc) => {
    if (!loc) return '—';
    const dom = loc.dominant_model || 'ECMWF_IFS';
    let modelName = 'ECMWF';
    let weight = loc.mean_ECMWF_IFS_weight;
    if (dom.includes('GFS')) {
      modelName = 'GFS';
      weight = loc.mean_NOAA_GFS_weight;
    } else if (dom.includes('ICON')) {
      modelName = 'ICON';
      weight = loc.mean_DWD_ICON_weight;
    }
    return weight != null ? `${modelName} ${Math.round(weight * 100)}%` : '—';
  };

  const cityPreviews = spatialData?.locations && spatialData.locations.length > 0
    ? spatialData.locations.map((loc) => ({
        name: loc.name || loc.location_id,
        top: getCityTopWeight(loc),
      }))
    : LOCATIONS.map((l) => ({
        name: l.label,
        top: isWind ? 'Pending' : '—',
      }));

  if (loading) return <LoadingState message="Connecting to Weather Intelligence Workstation..." />;
  if (error) return <ErrorState error={error} onRetry={fetchData} />;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}
    >
      {/* 1. HEADER AREA */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            OPERATIONAL WORKSTATION
          </div>
          <h1 style={{ fontSize: 'var(--font-page-title)', fontWeight: 'var(--fw-title)', color: 'var(--text-main)', margin: '2px 0 2px 0', letterSpacing: '-0.02em' }}>
            SKYBLEND AI — WEATHER INTELLIGENCE
          </h1>
          <p style={{ fontSize: 'var(--font-body)', color: 'var(--text-muted)' }}>
            Adaptive multi-model forecast blending for precipitation, temperature and wind.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(255, 255, 255, 0.03)', padding: '6px 14px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-small)', color: 'var(--text-subtle)' }}>
            <Clock size={13} color="var(--text-subtle)" />
            <span>RUN: {runTime}</span>
          </div>
          <span className="status-pill online">● ONLINE</span>
        </div>
      </div>

      {/* 2. MAIN FORECAST HERO SURFACE */}
      <div className="hero-glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Controls Bar: Variable + Location + Lead Time */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
            <VariableSelector value={variable} onChange={(v) => setVariable(v)} />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: '170px' }}>
              <label style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                LOCATION
              </label>
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
              <label style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                FORECAST HORIZON
              </label>
              <div style={{ display: 'flex', gap: '6px' }}>
                {[1, 2, 3].map((day) => (
                  <button
                    key={day}
                    onClick={() => setLeadDay(day)}
                    style={{
                      padding: '6px 14px',
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

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-small)', color: 'var(--text-muted)' }}>
            <Calendar size={14} color="var(--text-muted)" />
            <span>Target Date: <strong style={{ color: '#FFFFFF' }}>{targetDate}</strong></span>
          </div>
        </div>

        {/* Hero Rate & Model Contribution Bar */}
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.06)', paddingBottom: '1rem' }}>
          <div>
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {metricTitle}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '2px' }}>
              <span style={{ fontSize: 'var(--font-hero)', fontWeight: 'var(--fw-hero)', color: '#F8FAFC', lineHeight: 'var(--lh-tight)', letterSpacing: '-0.03em' }}>
                {maxDisplay}
              </span>
              <span style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: 'var(--text-muted)' }}>{unit}</span>
              <span style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-section)', color: '#CBD5E1', textTransform: 'uppercase', marginLeft: '12px' }}>
                {conditionLabel}
              </span>
            </div>
          </div>

          {/* Model Contribution Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'rgba(255, 255, 255, 0.03)', padding: '8px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <span style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>CONTRIBUTIONS:</span>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#94A3B8' }}>ECMWF {ecmwfPct != null ? `${ecmwfPct}%` : isWind ? '—' : '—'}</span>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#A855F7' }}>GFS {gfsPct != null ? `${gfsPct}%` : isWind ? '—' : '—'}</span>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#10B981' }}>ICON {iconPct != null ? `${iconPct}%` : isWind ? '—' : '—'}</span>
          </div>
        </div>

        {/* 24H Trajectory Line Chart OR Wind Notice */}
        {isWind ? (
          <WindUnavailableNotice compact message="NWP 10m wind speed telemetry is currently pending ingestion. The dynamic forecast chart will activate upon dataset attachment." />
        ) : (
          <div>
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
              {variable === 'temperature' ? 'TEMPERATURE TRAJECTORY (24H HORIZON)' : 'PRECIPITATION TRAJECTORY (24H HORIZON)'}
            </div>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedTrajectory} margin={{ top: 5, right: 15, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.04)" />
                  <XAxis dataKey="timeLabel" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 10 }} />
                  <YAxis stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 10 }} unit={` ${unit}`} />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(15, 23, 34, 0.96)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '10px',
                      fontSize: '12px',
                      color: '#F8FAFC'
                    }}
                    labelStyle={{ color: '#F8FAFC', fontWeight: 700 }}
                    formatter={(val) => [`${typeof val === 'number' ? val.toFixed(2) : val} ${unit}`, '']}
                  />
                  {formattedTrajectory[0]?.reference_precipitation !== undefined && (
                    <Line type="monotone" dataKey="reference_precipitation" name="ERA5 Reference" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.5} dot={false} isAnimationActive={true} animationDuration={1000} />
                  )}
                  {formattedTrajectory[0]?.reference_temperature !== undefined && (
                    <Line type="monotone" dataKey="reference_temperature" name="Station 42807 Ref" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.5} dot={false} isAnimationActive={true} animationDuration={1000} />
                  )}
                  <Line type="monotone" dataKey="ECMWF_IFS" name="ECMWF IFS" stroke="#64748B" strokeWidth={1.4} dot={false} opacity={0.7} isAnimationActive={true} animationDuration={1000} />
                  <Line type="monotone" dataKey="NOAA_GFS" name="NOAA GFS" stroke="#A855F7" strokeWidth={1.4} dot={false} opacity={0.7} isAnimationActive={true} animationDuration={1000} />
                  <Line type="monotone" dataKey="DWD_ICON" name="DWD ICON" stroke="#10B981" strokeWidth={1.4} dot={false} opacity={0.7} isAnimationActive={true} animationDuration={1000} />
                  <Line
                    type="monotone"
                    dataKey={variable === 'temperature' ? 'blended_temperature' : 'blended_precipitation'}
                    name="SkyBlend AI"
                    stroke="#F8FAFC"
                    strokeWidth={2.8}
                    dot={false}
                    isAnimationActive={true}
                    animationDuration={1200}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* 3. UNDERSTANDING SKYBLEND SECTION */}
      <div className="glass-card" style={{ padding: '1.35rem', background: 'linear-gradient(135deg, rgba(18, 25, 38, 0.85) 0%, rgba(14, 20, 30, 0.9) 100%)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HelpCircle size={18} color="var(--text-muted)" />
            <div style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: '#FFFFFF' }}>
              WHAT DOES SKYBLEND DO?
            </div>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: 'var(--text-muted)',
              borderRadius: '8px',
              padding: '4px 10px',
              fontSize: 'var(--font-small)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'all 0.15s ease'
            }}
          >
            <span>{showDetails ? 'Hide details' : 'Understand this'}</span>
            {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {/* Compact Process Flow Strip */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', background: 'rgba(255, 255, 255, 0.02)', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <div style={{ fontSize: '0.78rem', color: '#F8FAFC', fontWeight: 700 }}>
            ECMWF + GFS + ICON
          </div>
          <ArrowRight size={14} color="#64748B" />
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Historical skill + location + lead time
          </div>
          <ArrowRight size={14} color="#64748B" />
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Adaptive weights
          </div>
          <ArrowRight size={14} color="#64748B" />
          <div style={{ fontSize: '0.78rem', color: '#F8FAFC', fontWeight: 800 }}>
            One blended forecast
          </div>
          <ArrowRight size={14} color="#64748B" />
          <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700 }}>
            Held-out verification
          </div>
        </div>

        <div style={{ fontSize: 'var(--font-body)', color: 'var(--text-muted)', marginTop: '0.75rem', lineHeight: 'var(--lh-relaxed)' }}>
          Numerical weather prediction models exhibit localized biases depending on location, season, and forecast horizon. <b>SkyBlend AI</b> dynamically determines normalized reliability weights for each model based on predicted accuracy under similar forecast context, combining multiple weather sources into a single optimal consensus prediction.
        </div>

        {/* Expandable Technical Details Drawer */}
        <AnimatePresence>
          {showDetails && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25 }}
              style={{ overflow: 'hidden', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.85rem' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ fontSize: 'var(--font-meta)', color: '#F8FAFC', textTransform: 'uppercase', fontWeight: 700 }}>1. Multi-Model Inputs</div>
                  <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginTop: '2px' }}>Ingests raw numerical forecasts from ECMWF IFS (Europe), NOAA GFS (USA), and DWD ICON (Germany).</div>
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ fontSize: 'var(--font-meta)', color: 'var(--text-main)', textTransform: 'uppercase', fontWeight: 700 }}>2. Context-Aware Weighting</div>
                  <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginTop: '2px' }}>Gradient boosting regressors predict absolute error ê_m using rolling skill, location microclimate, and lead time.</div>
                </div>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ fontSize: 'var(--font-meta)', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>3. Dynamic Consensus</div>
                  <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginTop: '2px' }}>Weights are normalized to sum to 1.0 (w_i ≥ 0), producing an optimal convex combination tailored to each variable.</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 4. EXPLAINABILITY & GEOSPATIAL MAP PREVIEW */}
      <div className="split-panel-grid">
        {/* Explainability Card */}
        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>
            EXPLAINABILITY ANALYSIS
          </div>
          <div style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: '#FFFFFF', marginBottom: '0.75rem' }}>
            WHY THIS FORECAST FOR {location.toUpperCase()}?
          </div>

          {isWind ? (
            <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', padding: '1rem 0' }}>
              Model contributions for wind will be computed upon attachment of multi-model 10m wind vector telemetry.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', color: 'var(--text-main)', marginBottom: '4px' }}>
                  <span>ECMWF IFS Model Trust</span>
                  <strong style={{ color: '#94A3B8' }}>{ecmwfPct != null ? `${ecmwfPct}%` : '—'}</strong>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${ecmwfPct || 0}%`, background: '#64748B' }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', color: 'var(--text-main)', marginBottom: '4px' }}>
                  <span>NOAA GFS Model Trust</span>
                  <strong style={{ color: '#A855F7' }}>{gfsPct != null ? `${gfsPct}%` : '—'}</strong>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${gfsPct || 0}%`, background: '#A855F7' }} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', color: 'var(--text-main)', marginBottom: '4px' }}>
                  <span>DWD ICON Model Trust</span>
                  <strong style={{ color: '#10B981' }}>{iconPct != null ? `${iconPct}%` : '—'}</strong>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${iconPct || 0}%`, background: '#10B981' }} />
                </div>
              </div>

              <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)', marginTop: '0.4rem', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '0.65rem' }}>
                <b>Supported Decision Factors:</b> {ecmwfPct != null && gfsPct != null && iconPct != null
                  ? `Higher weight assigned to ${ecmwfPct >= iconPct && ecmwfPct >= gfsPct ? 'ECMWF IFS' : iconPct >= gfsPct ? 'DWD ICON' : 'NOAA GFS'} based on predicted model reliability for ${location.toUpperCase()} under Day ${leadDay} lead horizon.`
                  : 'Awaiting model contribution data...'}
              </div>
            </div>
          )}
        </div>

        {/* Spatial Map Navigation Preview */}
        <div
          className="glass-card"
          onClick={() => onNavigate && onNavigate('spatial')}
          style={{
            padding: '1.25rem',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            background: 'linear-gradient(135deg, rgba(16, 23, 35, 0.9) 0%, rgba(11, 16, 25, 0.95) 100%)',
            borderColor: 'rgba(255, 255, 255, 0.1)'
          }}
        >
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
              <div>
                <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  GEOSPATIAL BLENDING MATRIX
                </div>
                <div style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)' }}>
                  SIX DEMONSTRATION METROS
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#F8FAFC' }}>
                <span>OPEN MAP</span>
                <ArrowRight size={14} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', margin: '0.75rem 0' }}>
              {cityPreviews.map((c) => (
                <div key={c.name} style={{ background: 'rgba(255, 255, 255, 0.025)', padding: '7px 10px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#CBD5E1' }} />
                    <span style={{ fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#F8FAFC' }}>{c.name}</span>
                  </div>
                  <div style={{ fontSize: 'var(--font-meta)', color: 'var(--text-subtle)', marginTop: '2px' }}>{c.top}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-subtle)', fontStyle: 'italic' }}>
            Click preview card to open full interactive Spatial Intelligence Map
          </div>
        </div>
      </div>
    </motion.div>
  );
}
