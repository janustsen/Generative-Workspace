"use client";

import type { ReactNode } from "react";
import type { Component } from "@/lib/types";
import { Select } from "./Select";

interface Props {
  c: Component;
  components: Component[];
  onPatch: (patch: Record<string, unknown>) => void;
}

const inputCls =
  "w-full bg-[var(--surface)] border border-[var(--border)] rounded px-1.5 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/50";

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="flex flex-col gap-0.5 min-w-0 flex-1">
      <span className="text-[10px] uppercase tracking-wide text-[var(--muted)]">{label}</span>
      {children}
    </label>
  );
}

/** Type-specific knobs for a building block — rendered inside its inspector card. */
export function FieldOptions({ c, components, onPatch }: Props) {
  const Num = (label: string, key: string, val: number | null | undefined) => (
    <Field label={label}>
      <input type="number" value={val ?? ""} className={inputCls}
        onChange={(e) => onPatch({ [key]: e.target.value === "" ? null : Number(e.target.value) })} />
    </Field>
  );
  const Txt = (label: string, key: string, val: string | null | undefined, ph = "") => (
    <Field label={label}>
      <input value={val ?? ""} placeholder={ph} className={inputCls}
        onChange={(e) => onPatch({ [key]: e.target.value })} />
    </Field>
  );
  const Csv = (label: string, key: string, arr: string[] | undefined) => (
    <Field label={label}>
      <input value={(arr ?? []).join(", ")} placeholder="A, B, C" className={inputCls}
        onChange={(e) => onPatch({ [key]: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })} />
    </Field>
  );
  const Row = ({ children }: { children: ReactNode }) => (
    <div className="ml-4 flex items-end gap-1.5 flex-wrap">{children}</div>
  );

  switch (c.type) {
    case "number_input":
      return <Row>{Num("Min", "min", c.min)}{Num("Max", "max", c.max)}{Num("Step", "step", c.step)}{Txt("Unit", "unit", c.unit, "kg")}</Row>;
    case "slider":
      return <Row>{Num("Min", "min", c.min)}{Num("Max", "max", c.max)}{Num("Step", "step", c.step)}{Txt("Unit", "unit", c.unit, "%")}</Row>;
    case "gauge":
      return <Row>{Num("Min", "min", c.min)}{Num("Max", "max", c.max)}{Txt("Unit", "unit", c.unit, "%")}</Row>;
    case "progress_bar":
    case "ring":
      return <Row>{Num("Goal / max", "max", c.max)}</Row>;
    case "rating":
      return <Row>{Num("Stars", "max", c.max ?? 5)}</Row>;
    case "chart":
      return (
        <Row>
          <Field label="Chart type">
            <Select value={c.chart_type ?? "bar"} ariaLabel="Chart type"
              options={[{ value: "bar", label: "Bar" }, { value: "line", label: "Line" }, { value: "area", label: "Area" }, { value: "pie", label: "Pie" }]}
              onChange={(v) => onPatch({ chart_type: v })} />
          </Field>
          {Txt("Unit", "unit", c.unit)}
        </Row>
      );
    case "kpi":
    case "sparkline":
    case "heatmap":
      return <Row>{Txt("Unit", "unit", c.unit)}</Row>;
    case "metric":
      return (
        <Row>
          <Field label="Formula">
            <Select value={c.formula} ariaLabel="Formula"
              options={[{ value: "sum", label: "Sum" }, { value: "count", label: "Count" }, { value: "avg", label: "Average" }, { value: "max", label: "Max" }, { value: "min", label: "Min" }]}
              onChange={(v) => onPatch({ formula: v })} />
          </Field>
          {Txt("Tracks field id", "source_component_id", c.source_component_id, "value")}
          {Txt("Unit", "unit", c.unit)}
        </Row>
      );
    case "text_input":
      return <Row>{Txt("Placeholder", "placeholder", c.placeholder)}</Row>;
    case "note":
      return <Row>{Txt("Placeholder", "placeholder", c.placeholder)}</Row>;
    case "tags":
      return <Row>{Txt("Placeholder", "placeholder", c.placeholder)}</Row>;
    case "list":
      return <Row>{Txt("Item name", "item_label", c.item_label, "Item")}{Txt("Placeholder", "placeholder", c.placeholder)}</Row>;
    case "dropdown":
    case "choice_chips":
      return <Row>{Csv("Options", "options", c.options)}</Row>;
    case "table":
    case "kanban":
      return <Row>{Csv("Columns", "columns", c.columns)}</Row>;
    case "tracker":
      return (
        <Row>
          <Field label="Resets">
            <Select value={c.period ?? "day"} ariaLabel="Reset period"
              options={[{ value: "day", label: "Daily" }, { value: "week", label: "Weekly" }]}
              onChange={(v) => onPatch({ period: v })} />
          </Field>
          {Num("Goal", "goal", c.goal)}
        </Row>
      );
    case "date":
      return (
        <Row>
          <label className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
            <input type="checkbox" checked={!!c.include_time} onChange={(e) => onPatch({ include_time: e.target.checked })} />
            Include time
          </label>
        </Row>
      );
    case "button": {
      const isAct = c.action === "increment" || c.action === "add_item";
      return (
        <Row>
          <Field label="Does what">
            <Select value={c.action} ariaLabel="Button action"
              options={[{ value: "increment", label: "Counter (+1)" }, { value: "add_item", label: "Add to list" }, { value: "calculator", label: "Calculator" }, { value: "timer", label: "Timer" }]}
              onChange={(v) => onPatch({ action: v })} />
          </Field>
          {isAct && (
            <Field label="Target">
              <Select value={c.target ?? ""} ariaLabel="Target field"
                options={[{ value: "", label: "Itself" }, ...components.filter((x) => x.id !== c.id).map((x) => ({ value: x.id, label: x.label }))]}
                onChange={(v) => onPatch({ target: v === "" ? null : v })} />
            </Field>
          )}
        </Row>
      );
    }
    default:
      return null;
  }
}
