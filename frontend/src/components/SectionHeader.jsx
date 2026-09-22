import React from 'react';

export function SectionHeader({ title, subtitle, eyebrow }) {
  return (
    <div style={{ marginBottom: '1.25rem' }}>
      {eyebrow && (
        <div style={{
          fontSize: 'var(--font-meta)',
          fontWeight: 'var(--fw-meta)',
          lineHeight: 'var(--lh-meta)',
          color: 'var(--text-subtle)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: '0.25rem'
        }}>
          {eyebrow}
        </div>
      )}
      <h2 style={{
        fontSize: 'var(--font-page-title)',
        fontWeight: 'var(--fw-title)',
        lineHeight: 'var(--lh-normal)',
        color: 'var(--text-main)',
        letterSpacing: '-0.02em',
        marginBottom: '0.25rem'
      }}>
        {title}
      </h2>
      {subtitle && (
        <p style={{
          fontSize: 'var(--font-body)',
          fontWeight: 'var(--fw-body)',
          lineHeight: 'var(--lh-relaxed)',
          color: 'var(--text-muted)'
        }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}
