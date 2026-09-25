import React, { useEffect, useMemo, useRef, useState } from 'react';
import { MapContainer, GeoJSON, Circle, Marker, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import indiaRegionData from '../assets/geo/india_region.json';

// Helper component to auto-fit India bounds and handle container resizing
function MapController({ locations, resetTrigger }) {
  const map = useMap();
  const hasFittedRef = useRef(false);

  const fitIndiaBounds = () => {
    // Lat: 7.5°N to 33.5°N, Lon: 68.0°E to 95.5°E
    const bounds = L.latLngBounds(
      L.latLng(7.5, 68.0),
      L.latLng(33.5, 95.5)
    );
    map.fitBounds(bounds, { padding: [16, 16], maxZoom: 6 });
  };

  useEffect(() => {
    map.invalidateSize();
    if (!hasFittedRef.current) {
      fitIndiaBounds();
      hasFittedRef.current = true;
    }
  }, [map, locations]);

  useEffect(() => {
    if (resetTrigger > 0) {
      fitIndiaBounds();
    }
  }, [resetTrigger]);

  return null;
}

// City-specific label offsets to prevent collision between geographically close metros (e.g. Bengaluru & Chennai)
const CITY_LABEL_OFFSETS = {
  bengaluru: { xOffset: -46, yOffset: 6 },
  chennai: { xOffset: 46, yOffset: 6 },
  delhi: { xOffset: 0, yOffset: 4 },
  kolkata: { xOffset: -8, yOffset: 4 },
  mumbai: { xOffset: -12, yOffset: 4 },
  guwahati: { xOffset: 32, yOffset: 4 },
};

// Custom City Marker showing 3-segment weight ring, city label, and model percentages
const createCustomCityIcon = (loc, isSelected) => {
  const locId = (loc.location_id || loc.id || '').toLowerCase();
  const ecmwf = loc.mean_ECMWF_IFS_weight ?? loc.weights?.ECMWF_IFS ?? 0.33;
  const gfs = loc.mean_NOAA_GFS_weight ?? loc.weights?.NOAA_GFS ?? 0.33;
  const icon = loc.mean_DWD_ICON_weight ?? loc.weights?.DWD_ICON ?? 0.34;

  const ecPct = (ecmwf * 100).toFixed(0);
  const gfsPct = (gfs * 100).toFixed(0);
  const iconPct = (icon * 100).toFixed(0);

  const circ = 100.53; // 2 * pi * 16
  const ecmwfDash = `${ecmwf * circ} ${circ}`;
  const gfsDash = `${gfs * circ} ${circ}`;
  const iconDash = `${icon * circ} ${circ}`;

  const ecmwfOffset = 0;
  const gfsOffset = -ecmwf * circ;
  const iconOffset = -(ecmwf + gfs) * circ;

  const cityName = (loc.name || loc.location_id || '').toUpperCase();
  const offset = CITY_LABEL_OFFSETS[locId] || { xOffset: 0, yOffset: 4 };

  const html = `
    <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; pointer-events: auto;">
      <!-- Concentric Weight Arc Ring -->
      <div style="position: relative; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;">
        <svg width="44" height="44" viewBox="0 0 44 44" style="overflow: visible; filter: drop-shadow(0 2px 10px rgba(0,0,0,0.9));">
          <circle cx="22" cy="22" r="20" fill="rgba(8, 12, 18, 0.92)" stroke="${isSelected ? '#FFFFFF' : 'rgba(255, 255, 255, 0.25)'}" stroke-width="${isSelected ? '2.5' : '1.2'}" />
          <g transform="rotate(-90 22 22)">
            <circle cx="22" cy="22" r="16" fill="none" stroke="#64748B" stroke-width="4.5" stroke-dasharray="${ecmwfDash}" stroke-dashoffset="${ecmwfOffset}" />
            <circle cx="22" cy="22" r="16" fill="none" stroke="#8B5CF6" stroke-width="4.5" stroke-dasharray="${gfsDash}" stroke-dashoffset="${gfsOffset}" />
            <circle cx="22" cy="22" r="16" fill="none" stroke="#10B981" stroke-width="4.5" stroke-dasharray="${iconDash}" stroke-dashoffset="${iconOffset}" />
          </g>
          <circle cx="22" cy="22" r="5" fill="${isSelected ? '#FFFFFF' : '#CBD5E1'}" />
        </svg>
      </div>

      <!-- City Badge & Adaptive Model Weights -->
      <div style="
        transform: translate(${offset.xOffset}px, ${offset.yOffset}px);
        background: ${isSelected ? 'rgba(15, 23, 36, 0.96)' : 'rgba(11, 16, 25, 0.92)'};
        border: 1px solid ${isSelected ? '#FFFFFF' : 'rgba(255, 255, 255, 0.16)'};
        box-shadow: 0 4px 16px rgba(0,0,0,0.8);
        border-radius: 7px;
        padding: 3px 8px;
        min-width: 96px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1px;
        white-space: nowrap;
        pointer-events: none;
        transition: transform 0.2s ease, border-color 0.2s ease;
      ">
        <span style="font-size: 10.5px; font-weight: 800; color: ${isSelected ? '#FFFFFF' : '#F1F5F9'}; letter-spacing: 0.04em; white-space: nowrap;">
          ${cityName}
        </span>
        <div style="display: flex; align-items: center; justify-content: center; gap: 5px; font-size: 9px; font-weight: 700; white-space: nowrap;">
          <span style="color: #94A3B8;">${ecPct}%</span>
          <span style="color: rgba(255,255,255,0.25);">•</span>
          <span style="color: #A78BFA;">${gfsPct}%</span>
          <span style="color: rgba(255,255,255,0.25);">•</span>
          <span style="color: #34D399;">${iconPct}%</span>
        </div>
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-city-marker',
    iconSize: [140, 72],
    iconAnchor: [70, 22],
  });
};

// Subtle ambient water body label for synoptic meteorological context
const createWaterLabel = (text) => {
  return L.divIcon({
    html: `<div style="font-size: 11px; font-weight: 700; color: rgba(148, 163, 184, 0.35); letter-spacing: 0.22em; text-transform: uppercase; white-space: nowrap; pointer-events: none; user-select: none;">${text}</div>`,
    className: 'water-label',
    iconSize: [140, 20],
    iconAnchor: [70, 10],
  });
};

// Edge coordinate graticule label
const createGraticuleLabel = (text) => {
  return L.divIcon({
    html: `<div style="font-size: 9px; font-weight: 600; color: rgba(100, 116, 139, 0.4); letter-spacing: 0.05em; pointer-events: none; user-select: none;">${text}</div>`,
    className: 'graticule-label',
    iconSize: [40, 16],
    iconAnchor: [20, 8],
  });
};

const WATER_BODIES = [
  { id: 'arabian-sea', name: 'Arabian Sea', lat: 16.5, lon: 68.2 },
  { id: 'bay-of-bengal', name: 'Bay of Bengal', lat: 15.5, lon: 89.2 },
  { id: 'indian-ocean', name: 'Indian Ocean', lat: 5.5, lon: 78.5 },
];

const GRATICULES = [
  // Parallels (Latitudes)
  { id: 'lat-10', pts: [[10, 65], [10, 98]] },
  { id: 'lat-20', pts: [[20, 65], [20, 98]] },
  { id: 'lat-30', pts: [[30, 65], [30, 98]] },
  // Meridians (Longitudes)
  { id: 'lon-70', pts: [[6, 70], [36, 70]] },
  { id: 'lon-80', pts: [[6, 80], [36, 80]] },
  { id: 'lon-90', pts: [[6, 90], [36, 90]] },
];

const GRATICULE_LABELS = [
  { id: 'lbl-lat-10', text: '10°N', lat: 10, lon: 66.2 },
  { id: 'lbl-lat-20', text: '20°N', lat: 20, lon: 66.2 },
  { id: 'lbl-lat-30', text: '30°N', lat: 30, lon: 66.2 },
  { id: 'lbl-lon-70', text: '70°E', lat: 34.5, lon: 70 },
  { id: 'lbl-lon-80', text: '80°E', lat: 34.5, lon: 80 },
  { id: 'lbl-lon-90', text: '90°E', lat: 34.5, lon: 90 },
];

export function WeightMap({ locations = [], leadDay = 1, selectedLocationId = 'kolkata', onSelectLocation }) {
  const center = [21.5, 80.5];
  const [resetTrigger, setResetTrigger] = useState(0);
  const mapInstanceRef = useRef(null);

  // Distinct graphite/charcoal styling for geographic boundary vectors
  const geoJsonStyle = useMemo(() => (feature) => {
    const isNeighbor = feature?.properties?.type === 'neighbor';
    if (isNeighbor) {
      return {
        fillColor: '#090E17',
        fillOpacity: 0.7,
        color: '#1E293B',
        weight: 1,
        dashArray: '3, 4',
      };
    }
    // Indian state territory
    return {
      fillColor: '#131D2D',
      fillOpacity: 0.92,
      color: 'rgba(255, 255, 255, 0.13)',
      weight: 1.15,
    };
  }, []);

  const onEachFeature = (feature, layer) => {
    const name = feature?.properties?.name;
    if (name) {
      layer.bindTooltip(name, {
        className: 'map-state-tooltip',
        sticky: true,
        direction: 'top',
        offset: [0, -10],
      });
    }
  };

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100%',
      minHeight: '520px',
      borderRadius: '20px',
      overflow: 'hidden',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
      background: '#070A10'
    }}>
      <MapContainer
        center={center}
        zoom={4.6}
        zoomControl={false}
        scrollWheelZoom={false}
        style={{ height: '100%', width: '100%', background: '#070A10' }}
        ref={mapInstanceRef}
      >
        <MapController locations={locations} resetTrigger={resetTrigger} />

        {/* Synoptic Meteorological Graticule Grid (Parallels & Meridians) */}
        {GRATICULES.map((g) => (
          <Polyline
            key={g.id}
            positions={g.pts}
            pathOptions={{
              color: 'rgba(148, 163, 184, 0.07)',
              weight: 1,
              dashArray: '4, 8',
              interactive: false
            }}
          />
        ))}

        {/* Graticule Degree Labels */}
        {GRATICULE_LABELS.map((gl) => (
          <Marker
            key={gl.id}
            position={[gl.lat, gl.lon]}
            icon={createGraticuleLabel(gl.text)}
            interactive={false}
          />
        ))}

        {/* Verified Geographic Boundaries for India & South Asia context */}
        {indiaRegionData && (
          <GeoJSON
            key={`geo-${leadDay}`}
            data={indiaRegionData}
            style={geoJsonStyle}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Ambient Oceanic Labels */}
        {WATER_BODIES.map((w) => (
          <Marker
            key={w.id}
            position={[w.lat, w.lon]}
            icon={createWaterLabel(w.name)}
            interactive={false}
          />
        ))}

        {/* City Markers & Spatial Weighting Influence Halos */}
        {locations.map((loc) => {
          const locId = (loc.location_id || loc.id || '').toLowerCase();
          const isSelected = locId === selectedLocationId.toLowerCase();
          const lat = loc.latitude ?? loc.lat ?? 0;
          const lon = loc.longitude ?? loc.lon ?? 0;

          // Dominant model color: ECMWF (Slate #64748B), GFS (Purple #8B5CF6), ICON (Emerald #10B981)
          const dominant = loc.dominant_model || '';
          const haloColor = dominant === 'NOAA_GFS'
            ? '#8B5CF6'
            : dominant === 'DWD_ICON'
            ? '#10B981'
            : '#64748B';

          // Radius in meters: selected city has larger prominent influence halo (160km vs 110km)
          const haloRadius = isSelected ? 165000 : 115000;

          return (
            <React.Fragment key={locId}>
              {/* Subtle Influence/Weight Halo */}
              <Circle
                center={[lat, lon]}
                radius={haloRadius}
                pathOptions={{
                  fillColor: haloColor,
                  fillOpacity: isSelected ? 0.22 : 0.09,
                  color: isSelected ? '#FFFFFF' : haloColor,
                  weight: isSelected ? 1.8 : 1,
                  dashArray: isSelected ? '4, 4' : null,
                }}
                eventHandlers={{
                  click: () => onSelectLocation && onSelectLocation(loc),
                }}
              />

              {/* Multi-model composite City Marker */}
              <Marker
                position={[lat, lon]}
                icon={createCustomCityIcon(loc, isSelected)}
                eventHandlers={{
                  click: () => onSelectLocation && onSelectLocation(loc),
                }}
              />
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Sleek Custom Map Action Controls (Top-Right) */}
      <div style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <button
          onClick={() => {
            if (mapInstanceRef.current) {
              mapInstanceRef.current.zoomIn();
            }
          }}
          title="Zoom In"
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(11, 16, 23, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.14)',
            color: '#F8FAFC',
            fontSize: '16px',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            transition: 'background 0.15s ease'
          }}
        >
          +
        </button>
        <button
          onClick={() => {
            if (mapInstanceRef.current) {
              mapInstanceRef.current.zoomOut();
            }
          }}
          title="Zoom Out"
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(11, 16, 23, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.14)',
            color: '#F8FAFC',
            fontSize: '16px',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            transition: 'background 0.15s ease'
          }}
        >
          −
        </button>
        <button
          onClick={() => setResetTrigger(prev => prev + 1)}
          title="Reset View (Re-center India)"
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(11, 16, 23, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.14)',
            color: '#94A3B8',
            fontSize: '14px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            transition: 'background 0.15s ease'
          }}
        >
          ⤢
        </button>
      </div>

      {/* Floating Map Legend (Bottom-Left) */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'rgba(11, 16, 23, 0.92)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '8px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
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
