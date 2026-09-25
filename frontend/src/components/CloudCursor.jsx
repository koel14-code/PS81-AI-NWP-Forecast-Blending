import React, { useEffect, useState, useRef } from 'react';

export function CloudCursor() {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  const posRef = useRef({ x: -100, y: -100 });
  const reqRef = useRef(null);

  useEffect(() => {
    const touchQuery = window.matchMedia('(pointer: coarse)');
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    setIsTouchDevice(touchQuery.matches);
    setPrefersReducedMotion(motionQuery.matches);

    const handleTouchChange = (e) => setIsTouchDevice(e.matches);
    const handleMotionChange = (e) => setPrefersReducedMotion(e.matches);

    touchQuery.addEventListener('change', handleTouchChange);
    motionQuery.addEventListener('change', handleMotionChange);

    if (touchQuery.matches || motionQuery.matches) return;

    let animX = -100;
    let animY = -100;

    const updateLoop = () => {
      animX += (posRef.current.x - animX) * 0.4;
      animY += (posRef.current.y - animY) * 0.4;
      setPosition({ x: animX, y: animY });
      reqRef.current = requestAnimationFrame(updateLoop);
    };

    const handleMouseMove = (e) => {
      posRef.current = { x: e.clientX, y: e.clientY };
      if (!isVisible) setIsVisible(true);

      const target = e.target;
      if (target && target.closest) {
        const isInteractive = target.closest('button, a, select, input, option, .nav-item, .glass-card, [role="button"], .control-bar');
        setIsHovered(!!isInteractive);
      } else {
        setIsHovered(false);
      }
    };

    const handleMouseLeave = () => setIsVisible(false);
    const handleMouseEnter = () => setIsVisible(true);

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('mouseenter', handleMouseEnter);

    reqRef.current = requestAnimationFrame(updateLoop);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('mouseenter', handleMouseEnter);
      touchQuery.removeEventListener('change', handleTouchChange);
      motionQuery.removeEventListener('change', handleMotionChange);
      if (reqRef.current) cancelAnimationFrame(reqRef.current);
    };
  }, [isVisible]);

  if (isTouchDevice || prefersReducedMotion || !isVisible) {
    return null;
  }

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '24px',
        height: '24px',
        transform: `translate3d(${position.x + 10}px, ${position.y + 10}px, 0) scale(${isHovered ? 1.12 : 1.0})`,
        transition: 'transform 0.16s ease-out, opacity 0.2s ease',
        pointerEvents: 'none',
        zIndex: 99999,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        opacity: isVisible ? 0.75 : 0,
        filter: isHovered
          ? 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.4))'
          : 'drop-shadow(0 0 3px rgba(255, 255, 255, 0.2))',
      }}
    >
      {/* Monochrome Cloud SVG */}
      <svg
        width="22"
        height="14"
        viewBox="0 0 26 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ overflow: 'visible' }}
      >
        <path
          d="M6.5 14C3.46243 14 1 11.5376 1 8.5C1 5.73602 3.03719 3.44754 5.72758 3.06412C6.67139 1.25875 8.57143 0 10.7857 0C13.4344 0 15.6565 1.80282 16.2798 4.25925C16.9062 3.77884 17.6924 3.5 18.5 3.5C20.9853 3.5 23 5.51472 23 8C23 8.35123 22.9596 8.69299 22.8835 9.02052C24.6468 9.61058 25.5 11.3683 25.5 13C25.5 14 24.5 14 23.5 14H6.5Z"
          fill="url(#monoCloudGrad)"
          stroke={isHovered ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.4)'}
          strokeWidth="0.8"
        />
        <defs>
          <linearGradient id="monoCloudGrad" x1="1" y1="0" x2="25.5" y2="14" gradientUnits="userSpaceOnUse">
            <stop stopColor="#F8FAFC" />
            <stop offset="0.6" stopColor="#CBD5E1" />
            <stop offset="1" stopColor="#94A3B8" />
          </linearGradient>
        </defs>
      </svg>

      {/* Subtle Falling Raindrops */}
      <div
        style={{
          display: 'flex',
          gap: '4px',
          marginTop: '2px',
          opacity: 0.6,
        }}
      >
        <span
          className="cursor-raindrop"
          style={{
            width: '1.5px',
            height: '4px',
            borderRadius: '1px',
            background: 'linear-gradient(180deg, #CBD5E1 0%, rgba(148, 163, 184, 0.1) 100%)',
            animation: 'monoDropFall 0.8s infinite linear',
            animationDelay: '0s',
          }}
        />
        <span
          className="cursor-raindrop"
          style={{
            width: '1.5px',
            height: '5px',
            borderRadius: '1px',
            background: 'linear-gradient(180deg, #E2E8F0 0%, rgba(148, 163, 184, 0.1) 100%)',
            animation: 'monoDropFall 0.8s infinite linear',
            animationDelay: '0.3s',
          }}
        />
      </div>

      <style>{`
        @keyframes monoDropFall {
          0% { transform: translateY(0); opacity: 0.8; }
          70% { transform: translateY(6px); opacity: 0.5; }
          100% { transform: translateY(9px); opacity: 0; }
        }
      `}</style>
    </div>
  );
}
