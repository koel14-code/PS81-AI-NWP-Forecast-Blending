import React from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const createCustomCityIcon = (loc, isSelected) => {
  const ecmwf = loc.mean_ECMWF_IFS_weight || 0.33;
  const gfs = loc.mean_NOAA_GFS_weight || 0.33;
  const icon = loc.mean_DWD_ICON_weight || 0.34;
  
  const circ = 100.53; // 2 * pi * 16
  const ecmwfDash = `${ecmwf * circ} ${circ}`;
  const gfsDash = `${gfs * circ} ${circ}`;
  const iconDash = `${icon * circ} ${circ}`;

  const ecmwfOffset = 0;
  const gfsOffset = -ecmwf * circ;
  const iconOffset = -(ecmwf + gfs) * circ;

  const html = `
    <div style="position: relative; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; transform: translate(-22px, -22px); cursor: pointer;">
      <svg width="44" height="44" viewBox="0 0 44 44" style="overflow: visible;">
        <circle cx="22" cy="22" r="20" fill="none" stroke="${isSelected ? '#F8FAFC' : 'rgba(255, 255, 255, 0.2)'}" stroke-width="${isSelected ? '2.5' : '1'}" opacity="0.8" />
        <g transform="rotate(-90 22 22)">
          <circle cx="22" cy="22" r="16" fill="none" stroke="#64748B" stroke-width="4.5" stroke-dasharray="${ecmwfDash}" stroke-dashoffset="${ecmwfOffset}" />
          <circle cx="22" cy="22" r="16" fill="none" stroke="#8B5CF6" stroke-width="4.5" stroke-dasharray="${gfsDash}" stroke-dashoffset="${gfsOffset}" />
          <circle cx="22" cy="22" r="16" fill="none" stroke="#10B981" stroke-width="4.5" stroke-dasharray="${iconDash}" stroke-dashoffset="${iconOffset}" />
        </g>
        <circle cx="22" cy="22" r="6" fill="${isSelected ? '#FFFFFF' : '#CBD5E1'}" filter="drop-shadow(0 0 6px ${isSelected ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.5)'})" />
      </svg>
      <div style="position: absolute; bottom: -18px; font-size: 10px; font-weight: 800; color: #F8FAFC; text-shadow: 0 2px 6px #000; white-space: nowrap; pointer-events: none; letter-spacing: 0.02em;">
        ${loc.name}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-city-marker',
    iconSize: [44, 44],
    iconAnchor: [22, 22],
  });
};

export function WeightMap({ locations = [], leadDay = 1, selectedLocationId = 'kolkata', onSelectLocation }) {
  const center = [22.0, 79.5];

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '520px', borderRadius: '20px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.08)', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)' }}>
      <MapContainer
        center={center}
        zoom={4.8}
        zoomControl={false}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%', background: '#0A0F15' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {locations.map((loc) => {
          const isSelected = (loc.location_id || loc.id) === selectedLocationId;
          const icon = createCustomCityIcon(loc, isSelected);

          return (
            <Marker
              key={loc.location_id || loc.id}
              position={[loc.latitude ?? loc.lat ?? 0, loc.longitude ?? loc.lon ?? 0]}
              icon={icon}
              eventHandlers={{
                click: () => onSelectLocation && onSelectLocation(loc),
              }}
            />
          );
        })}
      </MapContainer>

      {/* Floating Map Legend (Bottom-Left) */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'rgba(11, 16, 23, 0.88)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '8px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.4)'
      }}>
        <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          MODEL WEIGHTS
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', fontWeight: 800, color: '#94A3B8' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#64748B' }} /> ECMWF
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', fontWeight: 800, color: '#8B5CF6' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8B5CF6' }} /> GFS
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', fontWeight: 800, color: '#10B981' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981' }} /> ICON
        </div>
      </div>
    </div>
  );
}



