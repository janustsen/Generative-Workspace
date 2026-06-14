"use client";

import type { Dropdown } from "@/lib/types";
import { Select } from "../Select";

interface Props {
  spec: Dropdown;
  value: string;
  onChange: (v: string) => void;
}

export function DropdownField({ spec, value, onChange }: Props) {
  const opts = spec.options ?? [];
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs uppercase tracking-wide text-[var(--muted)]">{spec.label}</span>
      <Select
        value={value ?? ""}
        ariaLabel={spec.label}
        className="w-full !bg-[var(--surface-elevated)] py-2 text-sm"
        options={[{ value: "", label: "Select…" }, ...opts.map((o) => ({ value: o, label: o }))]}
        onChange={onChange}
      />
    </div>
  );
}
