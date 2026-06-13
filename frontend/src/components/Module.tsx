"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Component, StoredModule } from "@/lib/types";
import { api } from "@/lib/api";
import { CheckboxField } from "./primitives/CheckboxField";
import { ListFieldComponent } from "./primitives/ListFieldComponent";
import { NumberInputField } from "./primitives/NumberInputField";
import { ProgressBarField } from "./primitives/ProgressBarField";
import { SliderField } from "./primitives/SliderField";
import { TextInputField } from "./primitives/TextInputField";

interface Props {
  module: StoredModule;
  onChange: (updated: StoredModule) => void;
  onDragStart: (e: React.PointerEvent, moduleId: string) => void;
}

export function Module({ module, onChange, onDragStart }: Props) {
  const [state, setState] = useState<Record<string, unknown>>(
    module.config.state ?? {},
  );
  const persistTimer = useRef<number | null>(null);

  useEffect(() => {
    setState(module.config.state ?? {});
  }, [module.id, module.config.state]);

  const schedulePersist = useCallback(
    (nextState: Record<string, unknown>) => {
      if (persistTimer.current) window.clearTimeout(persistTimer.current);
      persistTimer.current = window.setTimeout(async () => {
        try {
          const saved = await api.patchModule(module.id, {
            ...module.config,
            state: nextState,
          });
          onChange(saved);
        } catch (err) {
          console.error("Failed to persist module state", err);
        }
      }, 400);
    },
    [module, onChange],
  );

  const setField = useCallback(
    (id: string, value: unknown) => {
      setState((prev) => {
        const next = { ...prev, [id]: value };
        schedulePersist(next);
        return next;
      });
    },
    [schedulePersist],
  );

  const renderComponent = (c: Component) => {
    switch (c.type) {
      case "text_input":
        return (
          <TextInputField
            key={c.id}
            spec={c}
            value={(state[c.id] as string) ?? ""}
            onChange={(v) => setField(c.id, v)}
          />
        );
      case "number_input":
        return (
          <NumberInputField
            key={c.id}
            spec={c}
            value={(state[c.id] as number | "") ?? ""}
            onChange={(v) => setField(c.id, v)}
          />
        );
      case "checkbox":
        return (
          <CheckboxField
            key={c.id}
            spec={c}
            value={Boolean(state[c.id])}
            onChange={(v) => setField(c.id, v)}
          />
        );
      case "slider":
        return (
          <SliderField
            key={c.id}
            spec={c}
            value={(state[c.id] as number) ?? c.min}
            onChange={(v) => setField(c.id, v)}
          />
        );
      case "progress_bar": {
        const sourceVal = c.bound_to
          ? (state[c.bound_to] as number) ?? 0
          : (state[c.id] as number) ?? 0;
        return <ProgressBarField key={c.id} spec={c} value={sourceVal} />;
      }
      case "list":
        return (
          <ListFieldComponent
            key={c.id}
            spec={c}
            value={(state[c.id] as string[]) ?? []}
            onChange={(v) => setField(c.id, v)}
          />
        );
    }
  };

  const { layout } = module.config;

  return (
    <div
      className="absolute rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-lg shadow-black/30 flex flex-col"
      style={{
        left: layout.x,
        top: layout.y,
        width: layout.width,
        minHeight: layout.height,
      }}
    >
      <div
        className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)] cursor-grab active:cursor-grabbing select-none"
        onPointerDown={(e) => onDragStart(e, module.id)}
      >
        <h3 className="text-sm font-semibold tracking-tight">
          {module.config.title}
        </h3>
        <span className="text-xs text-[var(--muted)] font-mono">
          {module.config.components.length} fields
        </span>
      </div>
      <div className="p-4 flex flex-col gap-4">
        {module.config.components.map(renderComponent)}
      </div>
    </div>
  );
}
