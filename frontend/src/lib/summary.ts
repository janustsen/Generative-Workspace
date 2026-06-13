import type { Component, ModuleConfig } from "./types";

/** A one-line summary for a collapsed module (design doc II.2.1). */
export function deriveSummary(
  config: ModuleConfig,
  state: Record<string, unknown>,
): string {
  const byId = (id: string | null | undefined) =>
    config.components.find((c) => c.id === id);

  const target =
    byId(config.summary_component_id) ?? config.components[0] ?? null;

  if (!target) return "Empty module";
  return summarizeComponent(target, state);
}

function summarizeComponent(
  c: Component,
  state: Record<string, unknown>,
): string {
  const raw = state[c.id];
  switch (c.type) {
    case "progress_bar": {
      const source = c.bound_to ? state[c.bound_to] : raw;
      const pct = Math.round(((Number(source) || 0) / (c.max || 1)) * 100);
      return `${c.label}: ${Math.max(0, Math.min(100, pct))}%`;
    }
    case "number_input":
      return `${c.label}: ${raw ?? 0}${c.unit ? ` ${c.unit}` : ""}`;
    case "slider":
      return `${c.label}: ${raw ?? c.min}${c.unit ? ` ${c.unit}` : ""}`;
    case "checkbox":
      return `${c.label}: ${raw ? "✓" : "—"}`;
    case "list": {
      const n = Array.isArray(raw) ? raw.length : 0;
      return `${n} ${c.item_label.toLowerCase()}${n === 1 ? "" : "s"}`;
    }
    case "text_input":
      return raw ? String(raw) : c.label;
    case "metric":
      return `${c.label}: …`;
  }
}
