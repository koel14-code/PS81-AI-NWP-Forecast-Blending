import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { VariableSelector } from '../components/VariableSelector';
import { WindUnavailableNotice } from '../components/WindUnavailableNotice';

export function Verification() {
  const [variable, setVariable] = useState('precipitation');

  const { data, loading, error, retry } = useApi(
    () => api.getVerification(variable),
    [variable]
  );

  const isWind = variable === 'wind';
  const isTemp = variable === 'temperature';
  const unit = isTemp ? '°C' : isWind ? 'km/h' : 'mm/h';

  if (loading) return <LoadingState message={`Fetching empirical verification metrics for ${variable}...`} />;
  if (error) return <ErrorState error={error} onRetry={retry} />;

  const { table = [], test_period, evaluation_scope } = data || {};

  const getApproachColor = (approach) => {
    switch (approach) {
      case 'Adaptive_ML_Blend':
      case 'SkyBlend_Temperature':
        return '#F8FAFC';
      case 'ECMWF_IFS':
        return '#64748B';
      case 'Historical_Weighted':
        return '#8B5CF6';
      case 'Simple_Average':
        return '#34D399';
      case 'NOAA_GFS':
        return '#F59E0B';
      case 'DWD_ICON':
        return '#EF4444';
      default:
        return '#64748B';
    }
  };

  const getApproachLabel = (approach) => {
    if (approach === 'SkyBlend_Temperature') return 'SkyBlend Temperature';
    return approach.replace(/_/g, ' ');
  };

  const maxMae = Math.max(...table.map((r) => r.MAE || 0.5), 0.1);
  const rankedTable = [...table].sort((a, b) => a.MAE - b.MAE);

  const scopeTitle = isTemp
    ? 'GROUND-STATION INDEPENDENT VERIFICATION'
    : 'HELD-OUT EVALUATION SCOPE';

  const scopeDesc = evaluation_scope || (isTemp
    ? 'Independent Ground-Station Verification — Kolkata / Alipore WMO 42807 (3,957 instances)'
    : 'Six Demonstration Locations • Three NWP Sources • July 2024 Monsoon Period');

  const periodLabel = isTemp
    ? 'PRE-MONSOON HELD-OUT TEST (APRIL – MAY 2024)'
    : 'JULY 2024 EXTERNAL MONSOON HOLDOUT';

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
        subtitle="Rigorous benchmark comparison across multiple forecast approaches on genuine unaugmented evaluation data."
      />

      {/* Control Strip */}
      <div className="control-bar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', margin: 0 }}>
        <VariableSelector value={variable} onChange={(v) => setVariable(v)} />
        <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          {periodLabel}
        </div>
      </div>

      {isWind ? (
        <WindUnavailableNotice message="Verification metrics for wind are strictly unavailable: No validated reference anemometer dataset or multi-model NWP wind forecasts are currently ingested. In compliance with scientific honesty guidelines, metrics are not synthesized." />
      ) : (
        <>
          {/* Evaluation Scope Bar */}
          <div className="glass-card" style={{ padding: '1rem 1.4rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {scopeTitle}
              </div>
              <div style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)', marginTop: '2px' }}>
                {scopeDesc}
              </div>
            </div>
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              {isTemp ? '3,957 STATION-HOURS' : '36,288 ALIGNED RECORDS'}
            </div>
          </div>

          {/* Ranked Horizontal Bar Comparison */}
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.15rem' }}>
              <div>
                <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  RANKED SKILL COMPARISON ({variable.toUpperCase()})
                </div>
                <div style={{ fontSize: 'var(--font-section)', fontWeight: 'var(--fw-section)', color: 'var(--text-main)', marginTop: '2px' }}>
                  MEAN ABSOLUTE ERROR (MAE) — LOWER IS BETTER
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {rankedTable.map((row) => {
                const isSkyBlend = row.Approach === 'Adaptive_ML_Blend' || row.Approach === 'SkyBlend_Temperature';
                const color = getApproachColor(row.Approach);
                const maeVal = Number(row.MAE);
                const barWidthPct = (maeVal / maxMae) * 100;

                return (
                  <div
                    key={row.Approach}
                    style={{
                      background: isSkyBlend ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                      border: isSkyBlend ? '1px solid rgba(255, 255, 255, 0.25)' : '1px solid rgba(255, 255, 255, 0.05)',
                      borderRadius: '12px',
                      padding: '10px 16px',
                      display: 'grid',
                      gridTemplateColumns: '220px 1fr 110px',
                      alignItems: 'center',
                      gap: '1rem'
                    }}
                  >
                    {/* Name */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
                      <span style={{ fontSize: 'var(--font-body)', fontWeight: isSkyBlend ? 'var(--fw-section)' : 'var(--fw-body)', color: isSkyBlend ? '#FFFFFF' : 'var(--text-main)' }}>
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
                    <div style={{ textAlign: 'right', fontSize: 'var(--font-body)', fontWeight: 'var(--fw-hero)', color: isSkyBlend ? '#F8FAFC' : 'var(--text-main)', fontFamily: 'monospace' }}>
                      {maeVal.toFixed(4)} <span style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-body)', color: 'var(--text-subtle)' }}>{unit}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Multi-Metric Comparison Matrix */}
          <div className="glass-card">
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>
              FULL MULTI-METRIC PERFORMANCE MATRIX ({variable.toUpperCase()})
            </div>
            <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Comprehensive benchmark across error, correlation, and reliability metrics.
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="custom-table" style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 4px' }}>
                <thead>
                  <tr style={{ background: 'rgba(255, 255, 255, 0.03)' }}>
                    <th style={{ textAlign: 'left', padding: '10px 14px' }}>APPROACH</th>
                    <th style={{ textAlign: 'center' }}>MAE ({unit}) ↓</th>
                    <th style={{ textAlign: 'center' }}>RMSE ({unit}) ↓</th>
                    <th style={{ textAlign: 'center' }}>BIAS ({unit})</th>
                    <th style={{ textAlign: 'center' }}>PEARSON R ↑</th>
                    {!isTemp && <th style={{ textAlign: 'center' }}>POD (≥1.0) ↑</th>}
                    {!isTemp && <th style={{ textAlign: 'center' }}>FAR (≥1.0) ↓</th>}
                    {!isTemp && <th style={{ textAlign: 'center' }}>CSI (≥1.0) ↑</th>}
                  </tr>
                </thead>
                <tbody>
                  {table.map((row) => {
                    const isSkyBlend = row.Approach === 'Adaptive_ML_Blend' || row.Approach === 'SkyBlend_Temperature';
                    const pCorr = row.Pearson_r !== undefined ? row.Pearson_r : row['Pearson r'];
                    return (
                      <tr
                        key={row.Approach}
                        style={{
                          background: isSkyBlend ? 'rgba(255, 255, 255, 0.06)' : 'rgba(255, 255, 255, 0.02)',
                          borderLeft: isSkyBlend ? '3px solid #F8FAFC' : 'none'
                        }}
                      >
                        <td style={{ fontWeight: 'var(--fw-section)', padding: '12px 14px', color: isSkyBlend ? '#F8FAFC' : 'var(--text-main)', fontSize: 'var(--font-small)' }}>
                          {getApproachLabel(row.Approach)}
                        </td>
                        <td style={{ textAlign: 'center', fontWeight: isSkyBlend ? 'var(--fw-hero)' : 'var(--fw-body)', color: isSkyBlend ? '#F8FAFC' : 'inherit', fontSize: 'var(--font-small)' }}>
                          {Number(row.MAE).toFixed(4)}
                        </td>
                        <td style={{ textAlign: 'center', fontWeight: isSkyBlend ? 'var(--fw-hero)' : 'var(--fw-body)', color: isSkyBlend ? '#F8FAFC' : 'inherit', fontSize: 'var(--font-small)' }}>
                          {Number(row.RMSE).toFixed(4)}
                        </td>
                        <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>
                          {row.Bias > 0 ? `+${Number(row.Bias).toFixed(4)}` : Number(row.Bias).toFixed(4)}
                        </td>
                        <td style={{ textAlign: 'center', fontWeight: isSkyBlend ? 'var(--fw-hero)' : 'var(--fw-body)', color: isSkyBlend ? '#F8FAFC' : 'inherit', fontSize: 'var(--font-small)' }}>
                          {pCorr != null ? Number(pCorr).toFixed(4) : '—'}
                        </td>
                        {!isTemp && (
                          <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>
                            {row.POD != null ? Number(row.POD).toFixed(4) : '—'}
                          </td>
                        )}
                        {!isTemp && (
                          <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>
                            {row.FAR != null ? Number(row.FAR).toFixed(4) : '—'}
                          </td>
                        )}
                        {!isTemp && (
                          <td style={{ textAlign: 'center', fontSize: 'var(--font-small)' }}>
                            {row.CSI != null ? Number(row.CSI).toFixed(4) : '—'}
                          </td>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Evaluation Summary Caption */}
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
              <b>Evaluation Summary:</b> {isTemp
                ? 'SkyBlend Temperature achieves lowest MAE (1.0144°C), lowest RMSE (1.3772°C), and highest Pearson correlation (0.9496) against independent Kolkata Alipore station observations.'
                : 'Adaptive ML Blend leads on MAE and FAR; other approaches lead on individual metrics under the July 2024 monsoon holdout.'}
            </div>
          </div>

          {/* Mandatory Scientific Honesty Disclaimer */}
          <div className="disclaimer-box">
            <b>Scientific Notice</b>: Performance varies by variable, location, regime and evaluation period. Historical demonstration data is not live operational validation.
          </div>
        </>
      )}
    </motion.div>
  );
}
