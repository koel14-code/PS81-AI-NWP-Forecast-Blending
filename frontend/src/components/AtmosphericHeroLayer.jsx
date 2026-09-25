import React, { useEffect, useState } from 'react';

/**
 * AtmosphericHeroLayer
 * 
 * Cinematic Hybrid Visualization for SkyBlend AI:
 * 
 * DEPTH HIERARCHY:
 * - BACKGROUND: Very faint geographic / coordinate graticule & schematic South Asia coastline
 * - MIDGROUND: Silver atmospheric streamlines, cloud masses & Bay of Bengal cyclonic vortex
 * - FOREGROUND: Smooth moving particles via SVG animateMotion
 * - ACCENT: Restrained warm amber precipitation activity (Western Ghats & Bengal zones)
 * 
 * MODEL CONVERGENCE (Center):
 * - ECMWF IFS, NOAA GFS, DWD ICON streams flowing toward Central Nexus
 * - Confluence gate ('╬') visual alignment
 * - Central Nexus (● ADAPTIVE BLEND) with technical reticle and subtle pulse
 * - Direct continuation into '──► FORECAST'
 * 
 * ATMOSPHERIC WEATHER FIELD (Right):
 * - Recognizable schematic South Asia / Indian coastline outline
 * - Soft organic cloud masses with depth
 * - Rotating cyclonic circulation in the Bay of Bengal
 * - Restrained warm amber convective precipitation clusters
 */

export function AtmosphericHeroLayer() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mq.matches);
    const onChange = (e) => setReducedMotion(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  return (
    <div className="hero-atmospheric-layer" aria-hidden="true">
      <svg
        className="hero-atmospheric-svg"
        viewBox="0 0 1200 480"
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Gaussian Blur Filter for Soft Organic Clouds */}
          <filter id="cloudSoftBlur" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="22" />
          </filter>

          {/* Central Nexus Radial Glow Aura */}
          <radialGradient id="convergenceAura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.20" />
            <stop offset="50%" stopColor="#94A3B8" stopOpacity="0.06" />
            <stop offset="100%" stopColor="#94A3B8" stopOpacity="0" />
          </radialGradient>

          {/* Left Text Vignette Protection: Keeps headline and feature list 100% crisp */}
          <linearGradient id="leftContentVignette" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#080C14" stopOpacity="0.88" />
            <stop offset="35%" stopColor="#080C14" stopOpacity="0.75" />
            <stop offset="44%" stopColor="#080C14" stopOpacity="0.30" />
            <stop offset="54%" stopColor="#080C14" stopOpacity="0" />
          </linearGradient>

          {/* Outer Edge Vignette */}
          <radialGradient id="outerHeroVignette" cx="50%" cy="50%" r="65%">
            <stop offset="0%" stopColor="#080C14" stopOpacity="0" />
            <stop offset="72%" stopColor="#080C14" stopOpacity="0.12" />
            <stop offset="100%" stopColor="#080C14" stopOpacity="0.60" />
          </radialGradient>

          {/* Model Stream Path Definitions for animateMotion */}
          <path id="pathEcmwf" d="M 470,120 C 540,120 620,165 700,212" />
          <path id="pathGfs" d="M 455,220 C 540,220 620,220 700,220" />
          <path id="pathIcon" d="M 470,320 C 540,320 620,275 700,228" />
          <path id="pathForecast" d="M 735,220 C 810,220 870,205 940,215 C 1010,225 1080,240 1180,230" />
          <path id="pathMonsoon" d="M 790,225 C 840,260 890,320 950,335 C 1000,345 1040,335 1080,315" />
          <path id="pathHimalaya" d="M 770,210 C 830,175 900,150 990,150 C 1070,150 1130,165 1190,155" />
        </defs>

        {/* ================================================================= */}
        {/* 1. BACKGROUND LAYER: Geographic Graticule & India Outline         */}
        {/* ================================================================= */}

        {/* Lat/Lon Geographic Coordinates Graticule */}
        <g stroke="rgba(148, 163, 184, 0.09)" strokeWidth="0.9" strokeDasharray="3 5">
          {/* Latitude Parallels */}
          <line x1="720" y1="110" x2="1180" y2="110" />
          <text x="730" y="105" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">30°N</text>

          <line x1="710" y1="230" x2="1180" y2="230" />
          <text x="715" y="225" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">20°N</text>

          <line x1="730" y1="370" x2="1180" y2="370" />
          <text x="735" y="365" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">10°N</text>

          {/* Longitude Meridians */}
          <line x1="810" y1="70" x2="810" y2="440" />
          <text x="814" y="84" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">70°E</text>

          <line x1="950" y1="70" x2="950" y2="440" />
          <text x="954" y="84" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">80°E</text>

          <line x1="1090" y1="70" x2="1090" y2="440" />
          <text x="1094" y="84" fill="rgba(148, 163, 184, 0.36)" fontSize="7.5" fontWeight="500" fontFamily="monospace">90°E</text>
        </g>

        {/* Recognizable Schematic South Asia / India Coastline */}
        <g transform="translate(220, 0)">
          <path
            d="
              M 610,90
              C 600,130 575,170 565,195
              C 560,208 580,215 585,225
              C 580,240 590,265 595,280
              C 605,315 615,355 625,385
              C 635,415 655,440 665,445
              C 675,440 682,415 688,390
              C 695,355 725,320 745,305
              C 775,275 810,250 840,235
              C 865,228 880,235 895,245
              C 915,242 935,260 945,285
              C 960,320 970,360 975,390
              M 665,445
              C 660,430 670,405 680,390
              M 895,245
              C 905,210 930,175 955,165
              C 975,160 990,175 985,195
            "
            fill="none"
            stroke="rgba(203, 213, 225, 0.24)"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Sri Lanka Schematic Outline */}
          <ellipse cx="692" cy="438" rx="7" ry="12" fill="none" stroke="rgba(203, 213, 225, 0.22)" strokeWidth="1.1" transform="rotate(15 692 438)" />
        </g>

        {/* Regional Ocean Basin Identification */}
        <text x="760" y="340" fill="rgba(148, 163, 184, 0.28)" fontSize="8" fontWeight="600" letterSpacing="0.12em" fontFamily="sans-serif">
          ARABIAN SEA
        </text>
        <text x="1050" y="360" fill="rgba(148, 163, 184, 0.28)" fontSize="8" fontWeight="600" letterSpacing="0.12em" fontFamily="sans-serif">
          BAY OF BENGAL
        </text>

        {/* ================================================================= */}
        {/* 2. MIDGROUND LAYER: Cloud Masses, Vortex & Streamlines           */}
        {/* ================================================================= */}

        {/* Translucent Cloud Formations (25-35% Strengthened Depth) */}
        <g filter="url(#cloudSoftBlur)" pointerEvents="none">
          <ellipse cx="790" cy="235" rx="85" ry="42" fill="rgba(248, 250, 252, 0.048)" />
          <ellipse cx="960" cy="245" rx="105" ry="52" fill="rgba(248, 250, 252, 0.055)" />
          <ellipse cx="1060" cy="305" rx="95" ry="58" fill="rgba(148, 163, 184, 0.048)" />
          <ellipse cx="1140" cy="180" rx="75" ry="38" fill="rgba(248, 250, 252, 0.042)" />
          <ellipse cx="880" cy="380" rx="110" ry="45" fill="rgba(148, 163, 184, 0.042)" />
        </g>

        {/* Bay of Bengal Cyclonic Circulation (Visually Defined Vortex) */}
        <g transform="translate(1060, 310)" opacity="0.65" className="hero-vortex-group">
          {/* Vortex Eye */}
          <circle cx="0" cy="0" r="3.8" fill="none" stroke="rgba(248, 250, 252, 0.75)" strokeWidth="1" />
          <circle cx="0" cy="0" r="1.6" fill="rgba(248, 250, 252, 0.9)" />
          {/* Primary Spiral Streamline Arms */}
          <path
            d="M 0,0 C 25,-12 45,-5 55,20 C 65,45 45,75 15,82 C -20,90 -60,65 -70,25 C -80,-18 -50,-70 -5,-82 C 50,-96 115,-60 130,-5"
            fill="none"
            stroke="rgba(203, 213, 225, 0.42)"
            strokeWidth="1.2"
            strokeDasharray="4 6"
          />
          <path
            d="M 0,0 C -15,18 -32,15 -35,-5 C -40,-30 -15,-52 15,-50 C 50,-48 78,-10 65,28 C 50,70 -12,85 -60,60"
            fill="none"
            stroke="rgba(148, 163, 184, 0.35)"
            strokeWidth="1.0"
            strokeDasharray="3 5"
          />
          {/* Auxiliary Inflow Arm */}
          <path
            d="M -70,50 C -45,65 -15,55 5,30 C 18,12 15,-10 -2,-20 C -22,-32 -48,-18 -42,5"
            fill="none"
            stroke="rgba(203, 213, 225, 0.32)"
            strokeWidth="0.9"
            strokeDasharray="2 4"
          />
        </g>

        {/* Secondary Post-Convergence Synoptic Streamlines */}
        <path
          d="M 790,225 C 840,260 890,320 950,335 C 1000,345 1040,335 1080,315"
          className="hero-stream-base hero-secondary-stream"
        />
        <path
          d="M 790,225 C 840,260 890,320 950,335 C 1000,345 1040,335 1080,315"
          className="hero-stream-pulse hero-secondary-stream"
        />

        <path
          d="M 770,210 C 830,175 900,150 990,150 C 1070,150 1130,165 1190,155"
          className="hero-stream-base hero-secondary-stream"
        />
        <path
          d="M 770,210 C 830,175 900,150 990,150 C 1070,150 1130,165 1190,155"
          className="hero-stream-pulse hero-secondary-stream"
        />

        {/* ================================================================= */}
        {/* 3. ACCENT LAYER: Restrained Warm Amber Precipitation Clusters     */}
        {/* ================================================================= */}
        <g className="hero-weather-pulse">
          {/* Cluster 1: Bengal Convective Zone */}
          <g transform="translate(1075, 230)">
            <circle cx="0" cy="0" r="2.0" fill="rgba(245, 158, 11, 0.60)" />
            <circle cx="11" cy="-6" r="1.5" fill="rgba(245, 158, 11, 0.48)" />
            <circle cx="-9" cy="8" r="1.6" fill="rgba(245, 158, 11, 0.52)" />
            <line x1="-4" y1="-2" x2="-2" y2="4" stroke="rgba(245, 158, 11, 0.42)" strokeWidth="0.9" />
            <line x1="6" y1="4" x2="8" y2="10" stroke="rgba(245, 158, 11, 0.42)" strokeWidth="0.9" />
            <line x1="14" y1="-1" x2="16" y2="5" stroke="rgba(245, 158, 11, 0.35)" strokeWidth="0.8" />
          </g>

          {/* Cluster 2: Western Ghats Orographic Convective Band */}
          <g transform="translate(850, 335)">
            <circle cx="0" cy="0" r="1.8" fill="rgba(245, 158, 11, 0.52)" />
            <circle cx="4" cy="18" r="1.5" fill="rgba(245, 158, 11, 0.45)" />
            <circle cx="8" cy="38" r="1.4" fill="rgba(245, 158, 11, 0.40)" />
            <line x1="-1" y1="4" x2="1" y2="10" stroke="rgba(245, 158, 11, 0.40)" strokeWidth="0.8" />
            <line x1="3" y1="22" x2="5" y2="28" stroke="rgba(245, 158, 11, 0.40)" strokeWidth="0.8" />
          </g>

          {/* Sparse Illuminated Weather Activity Sparkles */}
          <g transform="translate(1110, 185)">
            <circle cx="0" cy="0" r="1.8" fill="rgba(251, 191, 36, 0.60)" />
            <circle cx="0" cy="0" r="4.5" fill="none" stroke="rgba(245, 158, 11, 0.25)" strokeWidth="0.6" strokeDasharray="2 2" />
          </g>
          <circle cx="940" cy="300" r="1.5" fill="rgba(251, 191, 36, 0.50)" />
        </g>

        {/* ================================================================= */}
        {/* 4. MODEL CONVERGENCE FLOWCHART (CENTER)                           */}
        {/* ================================================================= */}

        {/* --- MODEL 1: ECMWF IFS STREAM BUNDLE --- */}
        <path d="M 470,105 C 540,105 615,152 700,206" className="hero-stream-base hero-secondary-stream" />
        <path d="M 470,120 C 540,120 620,165 700,212" className="hero-stream-primary" />
        <path d="M 470,120 C 540,120 620,165 700,212" className="hero-stream-pulse" />

        {/* --- MODEL 2: NOAA GFS STREAM BUNDLE --- */}
        <path d="M 455,232 C 540,232 620,228 700,225" className="hero-stream-base hero-secondary-stream" />
        <path d="M 455,220 C 540,220 620,220 700,220" className="hero-stream-primary" />
        <path d="M 455,220 C 540,220 620,220 700,220" className="hero-stream-pulse" />

        {/* --- MODEL 3: DWD ICON STREAM BUNDLE --- */}
        <path d="M 470,335 C 540,335 615,288 700,234" className="hero-stream-base hero-secondary-stream" />
        <path d="M 470,320 C 540,320 620,275 700,228" className="hero-stream-primary" />
        <path d="M 470,320 C 540,320 620,275 700,228" className="hero-stream-pulse" />

        {/* --- CONFLUENCE GATE ('╬') AT X=700: Strengthened Visual Alignment --- */}
        <g className="hero-confluence-gate">
          {/* Vertical Alignment Crossbar */}
          <line x1="700" y1="200" x2="700" y2="240" stroke="rgba(203, 213, 225, 0.60)" strokeWidth="1.3" strokeDasharray="2 3" />
          {/* Confluence Alignment Ticks */}
          <line x1="694" y1="212" x2="706" y2="212" stroke="rgba(203, 213, 225, 0.60)" strokeWidth="1.3" />
          <line x1="692" y1="220" x2="708" y2="220" stroke="rgba(248, 250, 252, 0.85)" strokeWidth="1.5" />
          <line x1="694" y1="228" x2="706" y2="228" stroke="rgba(203, 213, 225, 0.60)" strokeWidth="1.3" />
          {/* Transition Funnel Leading into Nexus at (735, 220) */}
          <path d="M 700,212 C 712,216 724,220 735,220" fill="none" stroke="rgba(248, 250, 252, 0.75)" strokeWidth="1.5" />
          <path d="M 700,220 L 735,220" fill="none" stroke="#FFFFFF" strokeWidth="2.0" />
          <path d="M 700,228 C 712,224 724,220 735,220" fill="none" stroke="rgba(248, 250, 252, 0.75)" strokeWidth="1.5" />
        </g>

        {/* --- POST-CONVERGENCE CONSENSUS STREAM (──► FORECAST) --- */}
        <path d="M 735,220 C 810,220 870,205 940,215 C 1010,225 1080,240 1180,230" className="hero-stream-primary" />
        <path d="M 735,223 C 810,223 870,210 940,220 C 1010,230 1080,245 1180,235" className="hero-stream-base hero-secondary-stream" />
        <path d="M 735,220 C 810,220 870,205 940,215 C 1010,225 1080,240 1180,230" className="hero-stream-pulse" />

        {/* ================================================================= */}
        {/* 5. METEOROLOGICAL SOURCE NODES & LABELS (CENTER-LEFT)             */}
        {/* ================================================================= */}

        {/* Node 1: ECMWF IFS */}
        <g transform="translate(470, 120)">
          <circle cx="0" cy="0" r="3.2" fill="rgba(248, 250, 252, 0.95)" />
          <circle cx="0" cy="0" r="7.5" fill="none" stroke="rgba(203, 213, 225, 0.40)" strokeWidth="0.8" strokeDasharray="2 3" />
          <text x="-6" y="-11" fill="#F1F5F9" fontSize="8.5" fontWeight="700" letterSpacing="0.1em" fontFamily="sans-serif">
            ECMWF IFS
          </text>
          <text x="-6" y="-2" fill="rgba(148, 163, 184, 0.70)" fontSize="6.5" fontWeight="500" letterSpacing="0.08em" fontFamily="monospace">
            0.4° HRES
          </text>
        </g>

        {/* Node 2: NOAA GFS */}
        <g transform="translate(455, 220)">
          <circle cx="0" cy="0" r="3.2" fill="rgba(248, 250, 252, 0.95)" />
          <circle cx="0" cy="0" r="7.5" fill="none" stroke="rgba(203, 213, 225, 0.40)" strokeWidth="0.8" strokeDasharray="2 3" />
          <text x="-6" y="-11" fill="#F1F5F9" fontSize="8.5" fontWeight="700" letterSpacing="0.1em" fontFamily="sans-serif">
            NOAA GFS
          </text>
          <text x="-6" y="-2" fill="rgba(148, 163, 184, 0.70)" fontSize="6.5" fontWeight="500" letterSpacing="0.08em" fontFamily="monospace">
            0.25° GFS
          </text>
        </g>

        {/* Node 3: DWD ICON */}
        <g transform="translate(470, 320)">
          <circle cx="0" cy="0" r="3.2" fill="rgba(248, 250, 252, 0.95)" />
          <circle cx="0" cy="0" r="7.5" fill="none" stroke="rgba(203, 213, 225, 0.40)" strokeWidth="0.8" strokeDasharray="2 3" />
          <text x="-6" y="-11" fill="#F1F5F9" fontSize="8.5" fontWeight="700" letterSpacing="0.1em" fontFamily="sans-serif">
            DWD ICON
          </text>
          <text x="-6" y="-2" fill="rgba(148, 163, 184, 0.70)" fontSize="6.5" fontWeight="500" letterSpacing="0.08em" fontFamily="monospace">
            0.25° ICON
          </text>
        </g>

        {/* ================================================================= */}
        {/* 6. CENTRAL ADAPTIVE BLENDING NEXUS (10-15% MORE PROMINENT)        */}
        {/* ================================================================= */}
        <g transform="translate(735, 220)">
          {/* Subtle Radial Pulse Aura */}
          <circle cx="0" cy="0" r="34" fill="url(#convergenceAura)" />
          {/* Outer Precision Reticle Ring */}
          <circle cx="0" cy="0" r="21" fill="none" stroke="rgba(203, 213, 225, 0.42)" strokeWidth="0.9" strokeDasharray="2 3" />
          {/* Pulse Expansion Ring */}
          <circle cx="0" cy="0" r="14.5" fill="none" stroke="rgba(248, 250, 252, 0.32)" strokeWidth="0.9" className="hero-convergence-pulse" />
          {/* High Precision Solid Ring */}
          <circle cx="0" cy="0" r="7" fill="none" stroke="rgba(248, 250, 252, 0.82)" strokeWidth="1.1" />
          {/* Central Nexus Solid Core */}
          <circle cx="0" cy="0" r="3.8" fill="#FFFFFF" />
          {/* Central Active Blending Micro-Core */}
          <circle cx="0" cy="0" r="1.8" fill="#F59E0B" />

          {/* Micro Convergence Orbiting Dots */}
          <circle cx="-7.5" cy="-5.5" r="1.2" fill="rgba(248, 250, 252, 0.75)" />
          <circle cx="6.5" cy="-6.5" r="1.2" fill="rgba(248, 250, 252, 0.75)" />
          <circle cx="5.5" cy="6.5" r="1.2" fill="rgba(248, 250, 252, 0.75)" />
          <circle cx="-6.5" cy="6.5" r="1.2" fill="rgba(248, 250, 252, 0.75)" />

          {/* Nexus Header Title */}
          <text x="0" y="-15" fill="#FFFFFF" fontSize="9" fontWeight="800" letterSpacing="0.14em" textAnchor="middle" fontFamily="sans-serif">
            ADAPTIVE BLEND
          </text>
          {/* Technical Sub-label */}
          <text x="0" y="25" fill="rgba(203, 213, 225, 0.80)" fontSize="6.8" fontWeight="600" letterSpacing="0.12em" textAnchor="middle" fontFamily="sans-serif">
            MULTI-MODEL NEXUS
          </text>
        </g>

        {/* Direct Outgoing Label: ──► FORECAST */}
        <g transform="translate(805, 206)">
          <text x="0" y="0" fill="#FFFFFF" fontSize="9" fontWeight="800" letterSpacing="0.12em" fontFamily="sans-serif">
            ──► FORECAST
          </text>
          <text x="0" y="11" fill="rgba(203, 213, 225, 0.75)" fontSize="7" fontWeight="600" letterSpacing="0.1em" fontFamily="sans-serif">
            SYNOPTIC FIELD
          </text>
        </g>

        {/* ================================================================= */}
        {/* 7. FOREGROUND LAYER: Moving Stream Particles (SVG animateMotion)  */}
        {/* ================================================================= */}
        {!reducedMotion && (
          <g className="hero-particle-group">
            {/* ECMWF Incoming Stream Particles */}
            <circle r="2.0" fill="rgba(248, 250, 252, 0.95)" className="hero-particle">
              <animateMotion dur="7.5s" repeatCount="indefinite">
                <mpath href="#pathEcmwf" />
              </animateMotion>
            </circle>
            <circle r="1.4" fill="rgba(203, 213, 225, 0.70)" className="hero-particle">
              <animateMotion dur="7.5s" begin="3.75s" repeatCount="indefinite">
                <mpath href="#pathEcmwf" />
              </animateMotion>
            </circle>

            {/* GFS Incoming Stream Particles */}
            <circle r="2.0" fill="rgba(248, 250, 252, 0.95)" className="hero-particle">
              <animateMotion dur="7s" begin="0.8s" repeatCount="indefinite">
                <mpath href="#pathGfs" />
              </animateMotion>
            </circle>
            <circle r="1.4" fill="rgba(203, 213, 225, 0.70)" className="hero-particle">
              <animateMotion dur="7s" begin="4.3s" repeatCount="indefinite">
                <mpath href="#pathGfs" />
              </animateMotion>
            </circle>

            {/* ICON Incoming Stream Particles */}
            <circle r="2.0" fill="rgba(248, 250, 252, 0.95)" className="hero-particle">
              <animateMotion dur="8s" begin="0.4s" repeatCount="indefinite">
                <mpath href="#pathIcon" />
              </animateMotion>
            </circle>
            <circle r="1.4" fill="rgba(203, 213, 225, 0.70)" className="hero-particle">
              <animateMotion dur="8s" begin="4.4s" repeatCount="indefinite">
                <mpath href="#pathIcon" />
              </animateMotion>
            </circle>

            {/* Post-Convergence Consensus Field Particles */}
            <circle r="2.3" fill="#FFFFFF" className="hero-particle">
              <animateMotion dur="9.5s" repeatCount="indefinite">
                <mpath href="#pathForecast" />
              </animateMotion>
            </circle>
            <circle r="1.7" fill="#F59E0B" className="hero-particle">
              <animateMotion dur="9.5s" begin="3.1s" repeatCount="indefinite">
                <mpath href="#pathForecast" />
              </animateMotion>
            </circle>
            <circle r="1.5" fill="rgba(203, 213, 225, 0.75)" className="hero-particle">
              <animateMotion dur="9.5s" begin="6.2s" repeatCount="indefinite">
                <mpath href="#pathForecast" />
              </animateMotion>
            </circle>

            {/* Monsoon Inflow Particle Feeding into Vortex */}
            <circle r="1.6" fill="rgba(203, 213, 225, 0.75)" className="hero-particle hero-secondary-stream">
              <animateMotion dur="11s" begin="1.5s" repeatCount="indefinite">
                <mpath href="#pathMonsoon" />
              </animateMotion>
            </circle>
          </g>
        )}

        {/* 8. Protective Vignettes */}
        {/* Left Content Vignette Mask: Protects Headline & Feature List */}
        <rect x="0" y="0" width="560" height="480" fill="url(#leftContentVignette)" pointerEvents="none" />
        {/* Outer Edge Vignette */}
        <rect x="0" y="0" width="1200" height="480" fill="url(#outerHeroVignette)" pointerEvents="none" />
      </svg>
    </div>
  );
}
