import type { Component, ComponentType } from "./types";

export const COMPONENT_TYPES: { type: ComponentType; label: string }[] = [
  { type: "text_input", label: "Text" },
  { type: "number_input", label: "Number" },
  { type: "checkbox", label: "Checkbox" },
  { type: "slider", label: "Slider" },
  { type: "progress_bar", label: "Progress bar" },
  { type: "list", label: "List" },
  { type: "metric", label: "Metric" },
];

let counter = 0;

/** Build a sensible default component of a given type with a unique id. */
export function makeComponent(type: ComponentType, label?: string): Component {
  const id = `field_${Date.now().toString(36)}_${counter++}`;
  switch (type) {
    case "text_input":
      return { id, type, label: label ?? "Text field", placeholder: "" };
    case "number_input":
      return { id, type, label: label ?? "Number", min: 0, step: 1 };
    case "checkbox":
      return { id, type, label: label ?? "Checkbox" };
    case "slider":
      return { id, type, label: label ?? "Slider", min: 0, max: 100, step: 1 };
    case "progress_bar":
      return { id, type, label: label ?? "Progress", max: 100 };
    case "list":
      return { id, type, label: label ?? "List", item_label: "Item" };
    case "metric":
      return { id, type, label: label ?? "Total", formula: "sum", source_component_id: "value" };
  }
}
