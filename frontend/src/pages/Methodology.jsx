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

const STAGE_VISUALS = {
  1: { icon: Layers, color: '#94A3B8' },
  2: { icon: RefreshCw, color: '#CBD5E1' },
  3: { icon: History, color: '#A855F7' },
  4: { icon: CloudSun, color: '#8B5CF6' },
  5: { icon: Cpu, color: '#F59E0B' },
  6: { icon: GitMerge, color: '#F8FAFC' },
  7: { icon: BadgeCheck, color: '#10B981' },
  8: { icon: AlertTriangle, color: '#EF4444' },
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
        subtitle="End-to-end adaptive machine learning forecast blending architecture."
      />

      {/* Flowing Scientific Pipeline Grid from API */}
      <div className="glass-card" style={{ padding: '1.6rem' }}>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.25rem' }}>
          SYSTEM PROCESSING PIPELINE ({pipelineStages.length} STAGES)
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.15rem' }}>
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
