"use client";

import type { Metric } from "@/lib/types";
import { useCountUp } from "@/lib/useCountUp";

interface Props {
  spec: Metric;
  value: number;
}

const FORMULA_LABEL: Record<Metric["formula"], string> = {
  sum: "Total",
  count: "Count",
  avg: "Avg",
  max: "Max",
  min: "Min",
};

export function MetricField({ spec, value }: Props) {
  const animated = useCountUp(value);
  const display =
    Number.isFinite(value)
      ? value % 1 === 0
        ? Math.round(animated).toLocaleString()
        : animated.toFixed(1)
      : "—";

  return (
    <div className="flex flex-col gap-0.5">
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-[var(--muted)]">{spec.label}</span>
        <span className="text-[10px] text-[var(--muted)] font-mono uppercase tracking-wide">
          {FORMULA_LABEL[spec.formula]}
        </span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-semibold tabular-nums leading-none">
          {display}
        </span>
        {spec.unit && (
          <span className="text-xs text-[var(--muted)]">{spec.unit}</span>
        )}
      </div>
    </div>
  );
}
