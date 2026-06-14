"use client";

import type { Checkbox } from "@/lib/types";

interface Props {
  spec: Checkbox;
  value: boolean;
  onChange: (v: boolean) => void;
}

export function CheckboxField({ spec, value, onChange }: Props) {
  return (
    <label className="flex items-center gap-3 cursor-pointer select-none">
      <input
        type="checkbox"
        checked={Boolean(value)}
        onChange={(e) => onChange(e.target.checked)}
        className={`h-4 w-4 rounded border-[var(--border)] bg-[var(--surface-elevated)] accent-[var(--accent)] ${value ? "animate-checkpop" : ""}`}
      />
      <span className="text-sm">{spec.label}</span>
    </label>
  );
}
