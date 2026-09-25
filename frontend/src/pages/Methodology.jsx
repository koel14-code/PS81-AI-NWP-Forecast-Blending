import React from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { 
  Layers, 
  RefreshCw, 
  History, 
  CloudSun, 
  Cpu, 
  GitMerge, 
  SlidersHorizontal,
  BadgeCheck, 
  AlertTriangle,
  LayoutDashboard,
  HelpCircle,
  ShieldCheck,
  FlaskConical,
  Database
} from 'lucide-react';

const STAGE_VISUALS = {
  1: { icon: Layers, color: '#94A3B8' },
  2: { icon: RefreshCw, color: '#CBD5E1' },
  3: { icon: History, color: '#A855F7' },
  4: { icon: CloudSun, color: '#8B5CF6' },
  5: { icon: Cpu, color: '#F59E0B' },
  6: { icon: GitMerge, color: '#F8FAFC' },
  7: { icon: SlidersHorizontal, color: '#38BDF8' },
  8: { icon: AlertTriangle, color: '#EF4444' },
  9: { icon: BadgeCheck, color: '#10B981' },
  10: { icon: LayoutDashboard, color: '#34D399' },
};

export function Methodology() {
  const { data, loading, error, retry } = useApi(api.getMethodology);

  if (loading) return <LoadingState message="Loading system methodology..." />;
  if (error) return <ErrorState error={error} onRetry={retry} />;

  const pipelineStages = (data?.pipeline_stages || []).map((stage) => {
    const stepNum = typeof stage.step === 'number' ? stage.step : parseInt(stage.step, 10);
    const visual = STAGE_VISUALS[stepNum] || { icon: Layers, color: '#94A3B8' };
    return {
      step: String(stage.step).padStart(2, '0'),
      title: stage.title,
      desc: stage.desc,
      icon: visual.icon,
      color: visual.color,
    };
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.35rem' }}
    >
      <SectionHeader
        eyebrow="SYSTEM PIPELINE & ARCHITECTURE"
        title="HOW SKYBLEND AI WORKS"
        subtitle="End-to-end adaptive machine learning forecast blending architecture across multiple weather variables."
      />

      {/* Flowing Scientific Pipeline Grid from API */}
      <div className="glass-card" style={{ padding: '1.6rem' }}>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.25rem' }}>
          SYSTEM PROCESSING PIPELINE ({pipelineStages.length} STAGES)
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.15rem' }}>
          {pipelineStages.map((stage) => {
            const Icon = stage.icon;
            return (
              <div
                key={stage.step}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '14px',
                  padding: '1.2rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '10px',
                  position: 'relative'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-hero)', color: stage.color }}>{stage.step}</span>
                    <div style={{ background: 'rgba(255, 255, 255, 0.06)', padding: '6px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                      <Icon size={18} color={stage.color} />
                    </div>
                  </div>
                  <div style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)', marginBottom: '4px' }}>
                    {stage.title}
                  </div>
                </div>

                <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: 'var(--lh-relaxed)', fontWeight: 'var(--fw-body)' }}>
                  {stage.desc}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Production vs Research Transparency Card (Part 15 & Part 20) */}
      <div className="glass-card" style={{ padding: '1.6rem' }}>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
          PRODUCTION ARCHITECTURE VS. RESEARCH EXPERIMENTS
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {/* Production Validated */}
          <div style={{ background: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '12px', padding: '1.1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <ShieldCheck size={18} color="#34D399" />
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#34D399', letterSpacing: '0.04em' }}>
                PRODUCTION-VALIDATED (FROZEN BASELINES)
              </div>
            </div>
            <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              <li><b>Precipitation Blending</b>: Phase 6 HistGradientBoosting models in <code>models/expanded_full_year/</code> (α = 0.35, τ = 2.0 mm/h).</li>
              <li><b>10m Wind Speed Blending</b>: Historical-Error Weighted Blend (w_m ∝ 1/(MAE_m + ε)) over ECMWF, GFS, ICON.</li>
              <li><b>Dual Verification</b>: Held-out test evaluation (ERA5 reference) + independent Kolkata WMO 42807 physical ground-station validation.</li>
            </ul>
          </div>

          {/* Implemented Extension */}
          <div style={{ background: 'rgba(56, 189, 248, 0.04)', border: '1px solid rgba(56, 189, 248, 0.2)', borderRadius: '12px', padding: '1.1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <SlidersHorizontal size={18} color="#38BDF8" />
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#38BDF8', letterSpacing: '0.04em' }}>
                IMPLEMENTED EXTENSIONS
              </div>
            </div>
            <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              <li><b>2m Temperature Blending</b>: Continuous error prediction in <code>models/temperature/</code> (consensus without peak-lift).</li>
              <li><b>Station Benchmark</b>: WMO 42807 test (MAE 1.0144°C vs ECMWF 1.1180°C).</li>
              <li><b>Hazard Guidance</b>: Weather-regime context, 38.0°C heat-risk & 40.0 km/h wind-risk analytical signals.</li>
            </ul>
          </div>

          {/* Research Only */}
          <div style={{ background: 'rgba(168, 85, 247, 0.04)', border: '1px solid rgba(168, 85, 247, 0.2)', borderRadius: '12px', padding: '1.1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <FlaskConical size={18} color="#A855F7" />
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#A855F7', letterSpacing: '0.04em' }}>
                RESEARCH-ONLY (NOT IN PRODUCTION)
              </div>
            </div>
            <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              <li><b>Wind Research Models</b>: Wind GBDT error predictor & Wind Ridge blender (isolated research-only).</li>
              <li><b>Calibrated Rainfall Models</b>: Calib-1, Calib-2, and Calib-3 reliability models.</li>
              <li><b>Phase 10A / 10B / 11</b>: Experimental dual-gate and regime-gating research sandboxes.</li>
            </ul>
          </div>

          {/* Scientific Limitations & References */}
          <div style={{ background: 'rgba(100, 116, 139, 0.04)', border: '1px solid rgba(100, 116, 139, 0.2)', borderRadius: '12px', padding: '1.1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <Database size={18} color="#94A3B8" />
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#94A3B8', letterSpacing: '0.04em' }}>
                SCIENTIFIC SCOPE & LIMITATIONS
              </div>
            </div>
            <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: 'var(--font-small)', color: 'var(--text-muted)', lineHeight: '1.6' }}>
              <li><b>ERA5 Reference</b>: Reanalysis is a spatial areal proxy for multi-city evaluation, NOT ground truth.</li>
              <li><b>Physical Ground Truth</b>: Kolkata WMO 42807 surface station; no IMD operational telemetry claimed.</li>
              <li><b>Open-Meteo Streams</b>: Continuous hourly series; no physical forecast lead degradation claimed.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* WHY MULTIPLE MODELS? Visual Explanation Panel */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.02) 100%)',
        borderColor: 'rgba(255, 255, 255, 0.12)',
        padding: '1.6rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.65rem' }}>
          <HelpCircle size={22} color="var(--text-muted)" />
          <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            WHY MULTIPLE MODELS?
          </div>
        </div>

        <p style={{ fontSize: 'var(--font-body)', color: 'var(--text-main)', lineHeight: 'var(--lh-relaxed)', margin: 0, fontWeight: 'var(--fw-body)' }}>
          Numerical weather prediction models exhibit localized biases and varying skill depending on geographic region, season, forecast lead horizon, and weather situation. Rather than relying on a single static model or fixed average, <b>SkyBlend AI</b> dynamically learns how much contribution to assign to each forecast source for every specific situation.
        </p>
      </div>

      {/* Demonstration Scope Disclaimer */}
      <div className="disclaimer-box">
        <b>Validation Scope</b>: Demonstrated across 6 Indian cities, 3 NWP sources, and July 2024 monsoon historical evaluation data. Performance varies by variable, location, regime and evaluation period.
      </div>
    </motion.div>
  );
}
