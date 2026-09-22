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
  BadgeCheck, 
  AlertTriangle,
  HelpCircle
} from 'lucide-react';

const STAGES_8 = [
  { step: '01', title: 'NWP Forecast Sources', icon: Layers, desc: 'Ingests multi-model precipitation forecasts from ECMWF IFS, NOAA GFS, and DWD ICON.', color: '#94A3B8' },
  { step: '02', title: 'Data Harmonization', icon: RefreshCw, desc: 'Aligns spatio-temporal coordinates, common 1-hour time steps, and forecast lead horizons.', color: '#CBD5E1' },
  { step: '03', title: 'Historical Skill Analysis', icon: History, desc: 'Evaluates rolling historical forecast errors and skill profiles across lead times.', color: '#A855F7' },
  { step: '04', title: 'Weather / Context Features', icon: CloudSun, desc: 'Incorporates seasonal, precipitation regime, location, and temporal context indicators.', color: '#8B5CF6' },
  { step: '05', title: 'Adaptive Weight Engine', icon: Cpu, desc: 'Machine learning regressor predicts expected absolute error ê_m per model.', color: '#F59E0B' },
  { step: '06', title: 'Forecast Blending', icon: GitMerge, desc: 'Dynamically computes normalized sum-to-1 reliability weights to produce consensus forecast.', color: '#F8FAFC' },
  { step: '07', title: 'Held-out Verification', icon: BadgeCheck, desc: 'Validates blended predictions against ERA5 reanalysis reference on unseen evaluation period.', color: '#10B981' },
  { step: '08', title: 'Extreme Weather Guidance', icon: AlertTriangle, desc: 'Generates analytical rainfall signals based on project analytical threshold monitoring.', color: '#EF4444' },
];

export function Methodology() {
  const { data, loading, error, retry } = useApi(api.getMethodology);

  if (loading) return <LoadingState message="Loading system methodology..." />;
  if (error) return <ErrorState error={error} onRetry={retry} />;

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
        subtitle="End-to-end adaptive machine learning forecast blending architecture."
      />

      {/* 8-Stage Flowing Scientific Pipeline Grid */}
      <div className="glass-card" style={{ padding: '1.6rem' }}>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.25rem' }}>
          8-STAGE SYSTEM PROCESSING PIPELINE
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.15rem' }}>
          {STAGES_8.map((stage) => {
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
          Numerical weather prediction models exhibit localized biases and varying skill depending on geographic region, forecast lead horizon, and weather situation. Rather than relying on a single static model or fixed average, <b>SkyBlend AI</b> dynamically learns how much contribution to assign to each forecast source for every specific situation.
        </p>
      </div>

      {/* Demonstration Scope Disclaimer */}
      <div className="disclaimer-box">
        <b>Validation Scope</b>: Demonstrated across 6 Indian cities, 3 NWP sources, and July 2024 monsoon historical evaluation data.
      </div>
    </motion.div>
  );
}
