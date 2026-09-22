import React from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';

export function Verification() {
  const { data, loading, error, retry } = useApi(api.getVerification);

  if (loading) return <LoadingState message="Fetching empirical verification metrics..." />;
  if (error) return <ErrorState error={error} onRetry={retry} />;

  const { table = [], test_period } = data;

  const getApproachColor = (approach) => {
    switch (approach) {
      case 'Adaptive_ML_Blend': return '#F8FAFC';
      case 'ECMWF_IFS': return '#64748B';
      case 'Historical_Weighted': return '#8B5CF6';
      case 'Simple_Average': return '#34D399';
      case 'NOAA_GFS': return '#F59E0B';
      case 'DWD_ICON': return '#EF4444';
      default: return '#64748B';
    }
  };

  const getApproachLabel = (approach) => {
    return approach.replace(/_/g, ' ');
  };

  const adaptiveRow = table.find((row) => row.Approach === 'Adaptive_ML_Blend') || table[0];
  const maxMae = Math.max(...table.map(r => r.MAE || 0.5));

  // Sort by MAE ascending (best first)
  const rankedTable = [...table].sort((a, b) => a.MAE - b.MAE);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
    >
      <SectionHeader
        eyebrow="EMPIRICAL VALIDATION"
        title="HELD-OUT VERIFICATION"
        subtitle="Rigorous benchmark comparison across 6 approaches on unseen evaluation data."
      />

      {/* Evaluation Scope Bar */}
      <div className="glass-card" style={{ padding: '1rem 1.4rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            HELD-OUT EVALUATION SCOPE
          </div>
          <div style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)', marginTop: '2px' }}>
            Six Demonstration Locations • Three NWP Sources • July 2024 Monsoon Period
          </div>
        </div>
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          36,288 ALIGNED RECORDS
        </div>
      </div>

      {/* Ranked Horizontal Bar Comparison */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.15rem' }}>
          <div>
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              RANKED SKILL COMPARISON
            </div>
            <div style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)', marginTop: '2px' }}>
              MEAN ABSOLUTE ERROR (MAE) — LOWER IS BETTER
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          {rankedTable.map((row) => {
            const isAdaptive = row.Approach === 'Adaptive_ML_Blend';
            const color = getApproachColor(row.Approach);
            const maeVal = Number(row.MAE);
            const barWidthPct = (maeVal / maxMae) * 100;

            return (
              <div
                key={row.Approach}
                style={{
                  background: isAdaptive ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: isAdaptive ? '1px solid rgba(255, 255, 255, 0.25)' : '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '10px 16px',
                  display: 'grid',
                  gridTemplateColumns: '200px 1fr 110px',
                  alignItems: 'center',
                  gap: '1rem'
                }}
              >
                {/* Name */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
                  <span style={{ fontSize: 'var(--font-body)', fontWeight: isAdaptive ? 'var(--fw-section)' : 'var(--fw-body)', color: isAdaptive ? '#FFFFFF' : 'var(--text-main)' }}>
                    {getApproachLabel(row.Approach)}
                  </span>
                </div>

                {/* Horizontal Bar */}
                <div style={{ width: '100%', height: '12px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidthPct}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    style={{
                      height: '100%',
                      background: color,
                      borderRadius: '6px'
                    }}
                  />
                </div>

                {/* Value */}
                <div style={{ textAlign: 'right', fontSize: 'var(--font-body)', fontWeight: 'var(--fw-hero)', color: isAdaptive ? '#F8FAFC' : 'var(--text-main)', fontFamily: 'monospace' }}>
                  {maeVal.toFixed(4)} <span style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-body)', color: 'var(--text-subtle)' }}>mm/h</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Full Multi-Metric Comparison Matrix */}
      <div className="glass-card">
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>
          FULL MULTI-METRIC PERFORMANCE MATRIX
        </div>
        <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Comprehensive held-out evaluation across error, correlation, and categorical contingency metrics.
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="custom-table" style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 4px' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.03)' }}>
                <th style={{ textAlign: 'left', padding: '10px 14px' }}>APPROACH</th>
                <th style={{ textAlign: 'center' }}>MAE (mm/h) ↓</th>
                <th style={{ textAlign: 'center' }}>RMSE (mm/h) ↓</th>
                <th style={{ textAlign: 'center' }}>BIAS (mm/h)</th>
                <th style={{ textAlign: 'center' }}>PEARSON R ↑</th>
                <th style={{ textAlign: 'center' }}>POD ↑</th>
                <th style={{ textAlign: 'center' }}>FAR ↓</th>
                <th style={{ textAlign: 'center' }}>CSI ↑</th>
              </tr>
            </thead>
            <tbody>
              {table.map((row) => {
                const isAdaptive = row.Approach === 'Adaptive_ML_Blend';
                const pCorr = row.Pearson_r !== undefined ? row.Pearson_r : row['Pearson r'];
                return (
                  <tr
                    key={row.Approach}
                    style={{
                      background: isAdaptive ? 'rgba(255, 255, 255, 0.06)' : 'rgba(255, 255, 255, 0.02)',
                      borderLeft: isAdaptive ? '3px solid #F8FAFC' : 'none'
                    }}
                  >
                    <td style={{ fontWeight: 'var(--fw-section)', padding: '12px 14px', color: isAdaptive ? '#F8FAFC' : 'var(--text-main)', fontSize: 'var(--font-small)' }}>
                      {getApproachLabel(row.Approach)}
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: isAdaptive ? 'var(--fw-hero)' : 'var(--fw-body)', color: isAdaptive ? '#F8FAFC' : 'inherit', fontSize: 'var(--font-small)' }}>
                      {Number(row.MAE).toFixed(4)}
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: row.Approach === 'Historical_Weighted' ? 'var(--fw-hero)' : 'var(--fw-body)', color: row.Approach === 'Historical_Weighted' ? 'var(--accent-purple)' : 'inherit', fontSize: 'var(--font-small)' }}>
                      {Number(row.RMSE).toFixed(4)}
                    </td>
                    <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>{Number(row.Bias).toFixed(4)}</td>
                    <td style={{ textAlign: 'center', fontWeight: row.Approach === 'ECMWF_IFS' ? 'var(--fw-hero)' : 'var(--fw-body)', color: row.Approach === 'ECMWF_IFS' ? '#94A3B8' : 'inherit', fontSize: 'var(--font-small)' }}>
                      {Number(pCorr).toFixed(4)}
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: row.Approach === 'ECMWF_IFS' ? 'var(--fw-hero)' : 'var(--fw-body)', color: row.Approach === 'ECMWF_IFS' ? '#94A3B8' : 'inherit', fontSize: 'var(--font-small)' }}>
                      {Number(row.POD).toFixed(4)}
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: isAdaptive ? 'var(--fw-hero)' : 'var(--fw-body)', color: isAdaptive ? '#F8FAFC' : 'inherit', fontSize: 'var(--font-small)' }}>
                      {Number(row.FAR).toFixed(4)}
                    </td>
                    <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>{Number(row.CSI).toFixed(4)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Required Evaluation Summary Caption */}
        <div style={{
          marginTop: '1rem',
          padding: '10px 14px',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.025)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          fontSize: 'var(--font-small)',
          color: 'var(--text-main)',
          fontWeight: 'var(--fw-section)'
        }}>
          <b>Evaluation Summary Caption:</b> Adaptive ML Blend leads on MAE and FAR; other approaches lead on individual metrics.
        </div>
      </div>

      {/* Mandatory Scope Disclaimer */}
      <div className="disclaimer-box">
        <b>Scientific limitation</b>: Results are demonstrated on the selected July 2024 six-location evaluation scope and should not be interpreted as nationwide validation.
      </div>
    </motion.div>
  );
}
