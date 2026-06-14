"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Animate a number toward `value` (easeOutCubic). Skips the tween on first
 * render and when motion is reduced (honouring the app's data-motion override,
 * then the OS setting) so it never fights `prefers-reduced-motion`.
 */
export function useCountUp(value: number, ms = 600): number {
  const [display, setDisplay] = useState(value);
  const fromRef = useRef(value);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!Number.isFinite(value)) { setDisplay(value); return; }
    const motion = typeof document !== "undefined" ? document.documentElement.dataset.motion : undefined;
    const reduce =
      motion === "reduced" ||
      (motion !== "full" && typeof window !== "undefined" && !!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);
    const from = fromRef.current;
    if (reduce || from === value) { fromRef.current = value; setDisplay(value); return; }

    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / ms);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(from + (value - from) * eased);
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
      else fromRef.current = value;
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [value, ms]);

  return display;
}
