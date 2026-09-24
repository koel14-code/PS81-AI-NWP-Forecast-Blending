import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { SectionHeader } from '../components/SectionHeader';
import { LoadingState, ErrorState } from '../components/LoadingState';
import { WeightMap } from '../components/WeightMap';
import { VariableSelector } from '../components/VariableSelector';
import { WindUnavailableNotice } from '../components/WindUnavailableNotice';

export function SpatialIntelligence() {
  const [leadDay, setLeadDay] = useState(1);
  const [selectedCityId, setSelectedCityId] = useState('kolkata');
  const [variable, setVariable] = useState('precipitation');

  const { data, loading, error, retry } = useApi(
    () => api.getSpatialWeights(leadDay, variable),
    [leadDay, variable]
  );

  const isWind = variable === 'wind';
  const isTemp = variable === 'temperature';

  const rawLocations = data?.locations || [];
  const hasLocations = Array.isArray(rawLocations) && rawLocations.length > 0;

  // Find currently selected city safely by location_id or id
  const currentCity = hasLocations
    ? rawLocations.find((l) => (l.location_id || l.id) === selectedCityId) || rawLocations[0]
    : null;

  // Normalize model weights safely from API response fields
  const ecmwfVal = currentCity ? (currentCity.mean_ECMWF_IFS_weight ?? currentCity.weights?.ECMWF_IFS ?? 0) : 0;
  const gfsVal = currentCity ? (currentCity.mean_NOAA_GFS_weight ?? currentCity.weights?.NOAA_GFS ?? 0) : 0;
  const iconVal = currentCity ? (currentCity.mean_DWD_ICON_weight ?? currentCity.weights?.DWD_ICON ?? 0) : 0;

  const ecmwfW = (ecmwfVal * 100).toFixed(1);
  const gfsW = (gfsVal * 100).toFixed(1);
  const iconW = (iconVal * 100).toFixed(1);

  const lat = currentCity ? (currentCity.latitude ?? currentCity.lat ?? 0) : 0;
  const lon = currentCity ? (currentCity.longitude ?? currentCity.lon ?? 0) : 0;
  const dominantModel = currentCity ? (currentCity.dominant_model || '').replace(/_/g, ' ') : '';

  const mapBadgeLabel = isTemp
    ? 'Temperature Consensus Map'
    : 'Precipitation production map';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', height: '100%' }}
    >
      <SectionHeader
        eyebrow="GEOSPATIAL BLENDING MATRIX"
        title="SPATIAL INTELLIGENCE"
        subtitle="Explore dynamic NWP model contribution weights across India's demonstration metros."
      />

      {/* Control Strip: Variable + Horizon + Color Legend */}
      <div className="control-bar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', margin: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <VariableSelector value={variable} onChange={(v) => setVariable(v)} />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              HORIZON
            </div>
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

        {/* Status / Color Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', background: 'rgba(255, 255, 255, 0.025)', padding: '6px 14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#F8FAFC', letterSpacing: '0.03em' }}>
            {mapBadgeLabel.toUpperCase()}
          </span>
          <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#94A3B8' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#64748B' }} />
            ECMWF
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#8B5CF6' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#8B5CF6' }} />
            GFS
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#34D399' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#34D399' }} />
            ICON
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingState message={`Rendering geospatial weight matrix for Day ${leadDay} (${variable})...`} />
      ) : error ? (
        <ErrorState error={error} onRetry={retry} />
      ) : isWind ? (
        <WindUnavailableNotice message="Spatial model weights for wind are unavailable because multi-model NWP 10m wind fields are pending ingestion." />
      ) : !hasLocations ? (
        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No geospatial model weight data available for Day {leadDay}.
        </div>
      ) : (
        <>
          {/* Split Map View (>70% Map Surface, Floating Right Drawer) */}
          <div className="split-panel-grid spatial-grid">
            {/* >70% Weather Map Surface */}
            <div className="glass-card" style={{ padding: 0, overflow: 'hidden', position: 'relative', minHeight: '520px', display: 'flex', flexDirection: 'column' }}>
              <WeightMap
                locations={rawLocations}
                leadDay={leadDay}
                selectedLocationId={selectedCityId}
                onSelectLocation={(loc) => setSelectedCityId(loc?.location_id || loc?.id || 'kolkata')}
              />
            </div>

            {/* Floating Right Detail Drawer */}
            {currentCity && (
              <div className="glass-card hero-glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1.25rem' }}>
                <div>
                  <div style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    LOCATION PROFILE
                  </div>
                  <div style={{ fontSize: 'var(--font-page-title)', fontWeight: 'var(--fw-title)', color: '#FFFFFF', marginTop: '2px', lineHeight: 'var(--lh-normal)' }}>
                    {currentCity.name ? currentCity.name.toUpperCase() : ''}
                  </div>
                  <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Day {leadDay} Horizon • Lat {lat.toFixed(2)}°, Lon {lon.toFixed(2)}°
                  </div>

                  {/* Dominant Model Badge */}
                  <div style={{
                    marginTop: '1rem',
                    padding: '8px 12px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span style={{ fontSize: 'var(--font-meta)', fontWeight: 'var(--fw-meta)', color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>DOMINANT SOURCE</span>
                    <span style={{ fontSize: 'var(--font-body)', fontWeight: 'var(--fw-hero)', color: '#F8FAFC' }}>{dominantModel}</span>
                  </div>

                  {/* Horizontal Weight Contribution Bars */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.4rem' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#94A3B8', marginBottom: '4px' }}>
                        <span>ECMWF IFS</span>
                        <span>{ecmwfW}%</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${ecmwfW}%` }}
                          transition={{ duration: 0.6 }}
                          style={{ height: '100%', background: '#64748B' }}
                        />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#8B5CF6', marginBottom: '4px' }}>
                        <span>NOAA GFS</span>
                        <span>{gfsW}%</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${gfsW}%` }}
                          transition={{ duration: 0.6, delay: 0.1 }}
                          style={{ height: '100%', background: '#8B5CF6' }}
                        />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-small)', fontWeight: 'var(--fw-section)', color: '#34D399', marginBottom: '4px' }}>
                        <span>DWD ICON</span>
                        <span>{iconW}%</span>
                      </div>
                      <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${iconW}%` }}
                          transition={{ duration: 0.6, delay: 0.2 }}
                          style={{ height: '100%', background: '#34D399' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-subtle)', lineHeight: 'var(--lh-relaxed)', fontStyle: 'italic', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '0.85rem' }}>
                  {data?.scope_disclaimer || 'Adaptive contributions vary by location and lead time based on local model skill.'}
                </div>
              </div>
            )}
          </div>

          {/* Scope Subtext */}
          <div style={{ fontSize: 'var(--font-small)', color: 'var(--text-subtle)', textAlign: 'center', marginTop: '0.25rem' }}>
            Demonstration scope: 6 selected metro locations • Zero fabricated spatial values.
          </div>
        </>
      )}
    </motion.div>
  );
}
