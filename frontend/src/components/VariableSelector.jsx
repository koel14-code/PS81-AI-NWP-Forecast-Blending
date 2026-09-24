import React from 'react';
import { CloudRain, Thermometer, Wind } from 'lucide-react';

export const VARIABLES = [
  { id: 'precipitation', label: 'Precipitation', unit: 'mm/h', icon: CloudRain },
  { id: 'temperature', label: 'Temperature', unit: '°C', icon: Thermometer },
  { id: 'wind', label: 'Wind', unit: 'km/h', icon: Wind },
];

export function VariableSelector({ value = 'precipitation', onChange }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <label
        style={{
          fontSize: 'var(--font-meta)',
          fontWeight: 'var(--fw-meta)',
          color: 'var(--text-subtle)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}
      >
        FORECAST VARIABLE
      </label>
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {VARIABLES.map((v) => {
          const Icon = v.icon;
          const isSelected = value === v.id;
          return (
            <button
              key={v.id}
              type="button"
              onClick={() => onChange && onChange(v.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: 'var(--font-body)',
                fontWeight: 'var(--fw-section)',
                cursor: 'pointer',
                border: isSelected
                  ? '1px solid rgba(255, 255, 255, 0.3)'
                  : '1px solid rgba(255, 255, 255, 0.08)',
                background: isSelected
                  ? 'rgba(255, 255, 255, 0.14)'
                  : 'rgba(255, 255, 255, 0.03)',
                color: isSelected ? '#FFFFFF' : 'var(--text-muted)',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={14} color={isSelected ? '#FFFFFF' : 'var(--text-muted)'} />
              <span>{v.label}</span>
              <span
                style={{
                  fontSize: '0.68rem',
                  color: isSelected ? '#CBD5E1' : 'var(--text-subtle)',
                  marginLeft: '2px',
                  opacity: 0.85,
                }}
              >
                ({v.unit})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
