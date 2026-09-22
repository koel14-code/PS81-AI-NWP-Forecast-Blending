import React from 'react';

export function StatusBadge({ online = true }) {
  return (
    <div className={`status-pill ${online ? 'online' : 'offline'}`}>
      <span className="status-dot"></span>
      {online ? 'SYSTEM ONLINE' : 'BACKEND OFFLINE'}
    </div>
  );
}
