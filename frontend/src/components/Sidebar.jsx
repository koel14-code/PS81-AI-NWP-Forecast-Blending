import React from 'react';
import { motion } from 'framer-motion';
import { 
  CloudRain, 
  LayoutDashboard, 
  CloudSun, 
  SlidersHorizontal, 
  Map, 
  BadgeCheck, 
  CloudLightning, 
  BookOpen 
} from 'lucide-react';

const PRIMARY_NAV = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'forecast', label: 'Forecast Intelligence', icon: CloudSun },
  { id: 'weights', label: 'Adaptive AI', icon: SlidersHorizontal },
  { id: 'spatial', label: 'Spatial Intelligence', icon: Map },
];

const SECONDARY_NAV = [
  { id: 'verification', label: 'Verification', icon: BadgeCheck },
  { id: 'extreme', label: 'Extreme Weather', icon: CloudLightning },
];

const METHODOLOGY_NAV = [
  { id: 'methodology', label: 'Methodology', icon: BookOpen },
];

export function Sidebar({ activeTab, setActiveTab, isBackendOnline = true }) {
  const renderNavGroup = (items) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`nav-item ${isActive ? 'active' : ''}`}
          >
            {isActive && (
              <motion.div
                layoutId="sidebar-active-pill"
                style={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.16)',
                }}
                transition={{ type: 'spring', stiffness: 350, damping: 30 }}
              />
            )}
            <Icon size={18} color={isActive ? '#F8FAFC' : 'var(--text-muted)'} style={{ zIndex: 1 }} />
            <span style={{ position: 'relative', zIndex: 1, fontSize: '0.84rem' }}>{item.label}</span>
          </button>
        );
      })}
    </div>
  );

  return (
    <aside className="sidebar">
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
        {/* Clean Logo Header */}
        <div style={{ paddingBottom: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.06)', marginBottom: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #334155, #475569)', 
              padding: '6px', 
              borderRadius: '10px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
            }}>
              <CloudRain size={18} color="#F8FAFC" />
            </div>
            <div>
              <div style={{ fontWeight: 900, fontSize: '0.92rem', color: 'var(--text-main)', letterSpacing: '-0.01em', lineHeight: 1.1 }}>
                SKYBLEND AI
              </div>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-subtle)', letterSpacing: '0.04em', textTransform: 'uppercase', marginTop: '2px' }}>
                AI WEATHER INTELLIGENCE
              </div>
            </div>
          </div>
        </div>

        {/* Primary Nav */}
        {renderNavGroup(PRIMARY_NAV)}

        <div style={{ height: '1px', background: 'rgba(255, 255, 255, 0.06)', margin: '12px 0' }} />

        {/* Secondary Nav */}
        {renderNavGroup(SECONDARY_NAV)}

        <div style={{ height: '1px', background: 'rgba(255, 255, 255, 0.06)', margin: '12px 0' }} />

        {/* Methodology Nav */}
        {renderNavGroup(METHODOLOGY_NAV)}
      </div>

      {/* Bottom System Status */}
      <div style={{ paddingTop: '0.85rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)', width: '100%' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.72rem',
          fontWeight: 800,
          color: isBackendOnline ? '#34D399' : '#EF4444',
          letterSpacing: '0.04em'
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: isBackendOnline ? '#34D399' : '#EF4444',
            boxShadow: `0 0 8px ${isBackendOnline ? '#34D399' : '#EF4444'}`
          }} />
          <span>{isBackendOnline ? 'SYSTEM ONLINE' : 'BACKEND OFFLINE'}</span>
        </div>
      </div>
    </aside>
  );
}
