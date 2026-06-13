"use client";

import type { Slider } from "@/lib/types";

interface Props {
  spec: Slider;
  value: number;
  onChange: (v: number) => void;
}

export function SliderField({ spec, value, onChange }: Props) {
  const current = typeof value === "number" ? value : spec.min;
  return (
    <label className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between text-xs uppercase tracking-wide text-[var(--muted)]">
        <span>{spec.label}</span>
        <span className="font-mono text-[var(--foreground)] normal-case tracking-normal">
          {current}
          {spec.unit ? ` ${spec.unit}` : ""}
        </span>
      </div>
      <input
        type="range"
        min={spec.min}
        max={spec.max}
        step={spec.step}
        value={current}
        onChange={(e) => onChange(Number(e.target.value))}
        className="accent-[var(--accent)]"
      />
    </label>
  );
}
