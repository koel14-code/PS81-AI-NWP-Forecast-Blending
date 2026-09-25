import { useState, useEffect } from 'react';

export function useAnimatedNumber(targetValue, decimals = 2, duration = 800) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const end = parseFloat(targetValue);
    if (isNaN(end)) return;

    let startTimestamp = null;
    const startValue = 0;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // Ease-out cubic formula
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const value = startValue + (end - startValue) * easeOut;
      setCurrent(value);

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    window.requestAnimationFrame(step);
  }, [targetValue, duration]);

  return current.toFixed(decimals);
}
