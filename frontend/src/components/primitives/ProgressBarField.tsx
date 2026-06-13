"use client";

import type { ProgressBar } from "@/lib/types";

interface Props {
  spec: ProgressBar;
  value: number;
}

export function ProgressBarField({ spec, value }: Props) {
  const max = spec.max || 1;
  const pct = Math.max(0, Math.min(1, (Number(value) || 0) / max));
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between text-xs uppercase tracking-wide text-[var(--muted)]">
        <span>{spec.label}</span>
        <span className="font-mono text-[var(--foreground)] normal-case tracking-normal">
          {Math.round(pct * 100)}%
        </span>
      </div>
      <div className="h-2 rounded-full bg-[var(--surface-elevated)] overflow-hidden">
        <div
          className="h-full rounded-full bg-[var(--accent)] transition-[width] duration-300 ease-out"
          style={{ width: `${pct * 100}%` }}
        />
      </div>
    </div>
  );
}
