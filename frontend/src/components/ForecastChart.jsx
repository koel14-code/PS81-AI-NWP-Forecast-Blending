import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

export function ForecastChart({ series = [], title = "Forecast Signal" }) {
  if (!series || series.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No forecast series available.
      </div>
    );
  }

  const formattedData = series.map((item) => {
    let t = item.valid_time;
    if (t && t.includes('T')) {
      t = t.split('T')[1]?.substring(0, 5) || t;
    }
    return {
      ...item,
      timeLabel: t,
    };
  });

  return (
    <div className="glass-card">
      <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.85rem' }}>
        {title}
      </div>
      <div style={{ width: '100%', height: 380 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
            <XAxis dataKey="timeLabel" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} />
            <YAxis stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 11 }} unit=" mm/h" />
            <Tooltip
              contentStyle={{
                background: 'rgba(18, 24, 32, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '10px',
                boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                color: '#F8FAFC',
                fontSize: '12px'
              }}
              labelStyle={{ color: '#F8FAFC', fontWeight: 700 }}
            />
            <Legend wrapperStyle={{ color: '#94A3B8', fontSize: '12px', paddingTop: '8px' }} />
            
            <Line type="monotone" dataKey="reference_precipitation" name="ERA5 Reference" stroke="#475569" strokeDasharray="4 4" strokeWidth={1.8} dot={false} />
            {formattedData[0]?.ECMWF_IFS !== undefined && (
              <Line type="monotone" dataKey="ECMWF_IFS" name="ECMWF IFS" stroke="#64748B" strokeWidth={1.6} dot={false} opacity={0.8} />
            )}
            {formattedData[0]?.NOAA_GFS !== undefined && (
              <Line type="monotone" dataKey="NOAA_GFS" name="NOAA GFS" stroke="#8B5CF6" strokeWidth={1.6} dot={false} opacity={0.8} />
            )}
            {formattedData[0]?.DWD_ICON !== undefined && (
              <Line type="monotone" dataKey="DWD_ICON" name="DWD ICON" stroke="#10B981" strokeWidth={1.6} dot={false} opacity={0.8} />
            )}
            <Line type="monotone" dataKey="blended_precipitation" name="SkyBlend AI" stroke="#F8FAFC" strokeWidth={2.8} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

