import React from 'react';
import { RefreshCw, AlertTriangle } from 'lucide-react';

export function LoadingState({ message = "Loading forecast intelligence..." }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 2rem',
      background: 'var(--bg-card)',
      borderRadius: '16px',
      border: '1px solid var(--border-subtle)',
      textAlign: 'center'
    }}>
      <RefreshCw className="animate-spin" size={32} style={{ color: 'var(--accent-purple)', marginBottom: '1rem' }} />
      <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
        {message}
      </div>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
        Retrieving real weather intelligence artifacts...
      </div>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem 2rem',
      background: 'rgba(244, 63, 94, 0.08)',
      borderRadius: '16px',
      border: '1px solid rgba(244, 63, 94, 0.3)',
      textAlign: 'center',
      maxWidth: '600px',
      margin: '2rem auto'
    }}>
      <AlertTriangle size={40} style={{ color: 'var(--accent-crimson)', marginBottom: '0.75rem' }} />
      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
        Unable to connect to SkyBlend backend.
      </div>
      <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.5rem', marginBottom: '1rem' }}>
        {error || 'Make sure the FastAPI backend server is running at http://127.0.0.1:8000.'}
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn-retry">
          <RefreshCw size={16} /> Retry Connection
        </button>
      )}
    </div>
  );
}
