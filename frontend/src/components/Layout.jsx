import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { CloudCursor } from './CloudCursor';

export function Layout({ activeTab, setActiveTab, isBackendOnline, children }) {
  return (
    <div className="app-layout">
      {/* Custom Rain-Cloud Cursor */}
      <CloudCursor />

      {/* Layer 2 — Animated Atmospheric Morphing Mist & Cloud Blobs */}
      <div className="bg-blob bg-blob-1" />
      <div className="bg-blob bg-blob-2" />
      <div className="bg-blob bg-blob-3" />
      <div className="bg-blob bg-blob-4" />

      {/* Layer 2 (B) — Dual Soft Cloud Drift Ellipses */}
      <div className="cloud-drift-layer">
        <div className="cloud-ellipse" />
        <div className="cloud-ellipse cloud-ellipse-2" />
      </div>

      {/* Layer 3 — Subtle Atmospheric Grid Micro-texture */}
      <div className="bg-grid-texture" />

      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} isBackendOnline={isBackendOnline} />
      <div className="main-content">
        <Topbar activeTab={activeTab} isBackendOnline={isBackendOnline} />
        <main className="page-container">
          {children}
        </main>
      </div>
    </div>
  );
}
