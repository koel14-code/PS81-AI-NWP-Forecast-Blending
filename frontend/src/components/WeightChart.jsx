import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Helper to smooth path coordinates using cubic bezier curves
function buildSmoothPath(topPoints, bottomPoints) {
  if (!topPoints || topPoints.length === 0) return '';
  
  // Forward along top points
  let path = `M ${topPoints[0].x.toFixed(1)} ${topPoints[0].y.toFixed(1)}`;
  for (let i = 0; i < topPoints.length - 1; i++) {
    const curr = topPoints[i];
    const next = topPoints[i + 1];
    const mx = (curr.x + next.x) / 2;
    path += ` C ${mx.toFixed(1)} ${curr.y.toFixed(1)}, ${mx.toFixed(1)} ${next.y.toFixed(1)}, ${next.x.toFixed(1)} ${next.y.toFixed(1)}`;
  }

  // Connect to bottom points end
  const lastBottom = bottomPoints[bottomPoints.length - 1];
  path += ` L ${lastBottom.x.toFixed(1)} ${lastBottom.y.toFixed(1)}`;

  // Backward along bottom points
  for (let i = bottomPoints.length - 1; i > 0; i--) {
    const curr = bottomPoints[i];
    const prev = bottomPoints[i - 1];
    const mx = (curr.x + prev.x) / 2;
    path += ` C ${mx.toFixed(1)} ${curr.y.toFixed(1)}, ${mx.toFixed(1)} ${prev.y.toFixed(1)}, ${prev.x.toFixed(1)} ${prev.y.toFixed(1)}`;
  }

  path += ' Z';
  return path;
}

export function WeightChart({ series = [], title = "ADAPTIVE WEIGHT STREAM GRAPH" }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  if (!series || series.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No model weight stream data available.
      </div>
    );
  }

  // Canvas dimensions
  const svgWidth = 720;
  const svgHeight = 320;
  const padLeft = 40;
  const padRight = 30;
  const padTop = 30;
  const padBottom = 40;

  const contentW = svgWidth - padLeft - padRight;
  const contentH = svgHeight - padTop - padBottom;
  const centerY = padTop + contentH / 2;
  const streamHeight = contentH * 0.85;

  const N = series.length;
  
  // Compute coordinates for each layer
  const ecmwfTop = [];
  const gfsTop = [];
  const iconTop = [];
  const streamBottom = [];

  const pointsData = series.map((item, idx) => {
    const x = padLeft + (idx / Math.max(1, N - 1)) * contentW;
    const wEcmwf = item.ECMWF_IFS_weight || 0;
    const wGfs = item.NOAA_GFS_weight || 0;
    const wIcon = item.DWD_ICON_weight || 0;

    const y0 = centerY - streamHeight / 2;
    const y1 = y0 + wEcmwf * streamHeight;
    const y2 = y1 + wGfs * streamHeight;
    const y3 = y2 + wIcon * streamHeight;

    ecmwfTop.push({ x, y: y0 });
    gfsTop.push({ x, y: y1 });
    iconTop.push({ x, y: y2 });
    streamBottom.push({ x, y: y3 });

    return {
      x,
      seq: item.index !== undefined ? item.index : idx,
      ecmwfPct: (wEcmwf * 100).toFixed(1),
      gfsPct: (wGfs * 100).toFixed(1),
      iconPct: (wIcon * 100).toFixed(1),
      validTime: item.valid_time || `Step ${idx + 1}`
    };
  });

  const pathEcmwf = buildSmoothPath(ecmwfTop, gfsTop);
  const pathGfs = buildSmoothPath(gfsTop, iconTop);
  const pathIcon = buildSmoothPath(iconTop, streamBottom);

  const activePoint = hoverIndex !== null ? pointsData[hoverIndex] : null;

  return (
    <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <div>
          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--text-subtle)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            DYNAMIC ADAPTIVE FLOW
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 900, color: 'var(--text-main)', marginTop: '2px' }}>
            {title}
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 800, color: '#94A3B8' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#64748B' }} />
            ECMWF IFS
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 800, color: '#8B5CF6' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#8B5CF6' }} />
            NOAA GFS
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 800, color: '#10B981' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10B981' }} />
            DWD ICON
          </div>
        </div>
      </div>

      {/* Flowing SVG Canvas Container */}
      <div style={{ width: '100%', overflowX: 'auto', position: 'relative' }}>
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ width: '100%', height: 'auto', display: 'block' }}
          onMouseLeave={() => setHoverIndex(null)}
        >
          <defs>
            {/* Gradients */}
            <linearGradient id="streamEcmwf" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#334155" stopOpacity="0.85" />
              <stop offset="50%" stopColor="#475569" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#64748B" stopOpacity="0.85" />
            </linearGradient>

            <linearGradient id="streamGfs" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#7C3AED" stopOpacity="0.85" />
              <stop offset="50%" stopColor="#8B5CF6" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#6D28D9" stopOpacity="0.85" />
            </linearGradient>

            <linearGradient id="streamIcon" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#059669" stopOpacity="0.85" />
              <stop offset="50%" stopColor="#10B981" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#047857" stopOpacity="0.85" />
            </linearGradient>

            {/* Subtle glow filter */}
            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Grid Lines */}
          {[0.2, 0.4, 0.6, 0.8].map((ratio, idx) => (
            <line
              key={idx}
              x1={padLeft}
              y1={padTop + ratio * contentH}
              x2={svgWidth - padRight}
              y2={padTop + ratio * contentH}
              stroke="rgba(255, 255, 255, 0.04)"
              strokeDasharray="4 4"
            />
          ))}

          {/* ECMWF Layer */}
          <motion.path
            d={pathEcmwf}
            fill="url(#streamEcmwf)"
            filter="url(#glowFilter)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          />

          {/* GFS Layer */}
          <motion.path
            d={pathGfs}
            fill="url(#streamGfs)"
            filter="url(#glowFilter)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          />

          {/* ICON Layer */}
          <motion.path
            d={pathIcon}
            fill="url(#streamIcon)"
            filter="url(#glowFilter)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          />

          {/* Interactive Touch / Hover Columns */}
          {pointsData.map((pt, idx) => (
            <rect
              key={idx}
              x={pt.x - (contentW / N) / 2}
              y={padTop}
              width={contentW / N}
              height={contentH}
              fill="transparent"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHoverIndex(idx)}
            />
          ))}

          {/* Hover Line & Marker */}
          {activePoint && (
            <g>
              <line
                x1={activePoint.x}
                y1={padTop}
                x2={activePoint.x}
                y2={svgHeight - padBottom}
                stroke="rgba(255, 255, 255, 0.6)"
                strokeDasharray="3 3"
                strokeWidth={1.5}
              />
              <circle
                cx={activePoint.x}
                cy={centerY}
                r={5}
                fill="#FFFFFF"
                stroke="#64748B"
                strokeWidth={2}
              />
            </g>
          )}

          {/* X Axis Sequence Labels */}
          {pointsData.filter((_, i) => i % Math.ceil(N / 6) === 0 || i === N - 1).map((pt) => (
            <text
              key={pt.seq}
              x={pt.x}
              y={svgHeight - 12}
              fill="#64748B"
              fontSize={10}
              fontWeight={700}
              textAnchor="middle"
            >
              t={pt.seq}
            </text>
          ))}
        </svg>

        {/* Floating Tooltip */}
        <AnimatePresence>
          {activePoint && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              style={{
                position: 'absolute',
                top: '16px',
                left: `${(activePoint.x / svgWidth) * 100}%`,
                transform: 'translateX(-50%)',
                background: 'rgba(10, 15, 22, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(12px)',
                borderRadius: '12px',
                padding: '10px 14px',
                pointerEvents: 'none',
                boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
                zIndex: 20,
                minWidth: '170px'
              }}
            >
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '4px' }}>
                SEQUENCE INDEX t={activePoint.seq}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontWeight: 800, color: '#94A3B8' }}>
                  <span>ECMWF IFS:</span>
                  <span>{activePoint.ecmwfPct}%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontWeight: 800, color: '#8B5CF6' }}>
                  <span>NOAA GFS:</span>
                  <span>{activePoint.gfsPct}%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', fontWeight: 800, color: '#10B981' }}>
                  <span>DWD ICON:</span>
                  <span>{activePoint.iconPct}%</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '0.65rem' }}>
        Continuous ribbon stream representing dynamic model weight distribution over sequence time steps. Hover any point to inspect individual source weights.
      </div>
    </div>
  );
}
