"""Turn a natural-language prompt into a ModuleConfig.

The orchestrator never returns UI code. It returns a structured ModuleConfig
that the frontend renders with its trusted component library.
"""
from __future__ import annotations

import json

from pydantic import ValidationError

from src import llm
from src.schema import ClarifyingQuestion, ModuleConfig, RefusalError

_COMPONENT_DOCS = """Available component types (use exactly these "type" values):
- text_input   — free-text field.   Fields: id, label, type, placeholder?
- number_input — numeric entry.     Fields: id, label, type, min?, max?, step?, unit?
- checkbox     — boolean toggle.    Fields: id, label, type
- slider       — bounded number.    Fields: id, label, type, min, max, step, unit?
- progress_bar — visual progress.   Fields: id, label, type, max, bound_to? (intra-module component id),
                                    source_module_id? (cross-module: reads that module's bound_to field)
- list         — free-text items.   Fields: id, label, type, item_label, placeholder?
- metric       — READ-ONLY derived number aggregated across ALL session modules.
                 Fields: id, label, type, formula ("sum"|"count"|"avg"|"max"|"min"),
                 source_component_id (the component id to aggregate), unit?
                 Use metric when the user wants a running total, average, or count
                 across multiple modules (e.g. total calories across meal logs)."""

SYSTEM_PROMPT = f"""You are the Trus orchestrator. Your job is to turn a user's intent
into a ModuleConfig — a JSON document that the frontend renders using a fixed component
library. You do not write HTML, CSS, JavaScript, or any UI code.

{_COMPONENT_DOCS}

Output JSON ONLY, with this shape:
{{
  "title": "Module title (short, human-readable)",
  "components": [ {{ "id": "stable_snake_case_id", "type": "...", "label": "...", ... }}, ... ],
  "state": {{ "component_id": <prefilled value> }},
  "layout": {{ "x": 0, "y": 0, "width": 360, "height": 320 }},
  "summary_component_id": "id of the component that best represents this module at a glance (optional)"
}}

Rules:
1. Use only the component types above. No others.
2. ids are stable, snake_case, unique within a module.
3. ADAPT TO THE SPECIFIC REQUEST — tailor fields, labels, units, ranges to what was asked.
   Prefill "state" with any concrete values mentioned. Use the user's own terms for labels.
   A seed skeleton may be provided; reshape it freely.
4. If existing modules are listed, prefer metric/progress_bar cross-module bindings where
   they add real value (e.g. a dashboard that aggregates workout totals).
5. Prefer 3-6 components unless the request clearly needs more.
6. If the request is too vague to produce a useful module — AND one short question would
   unlock it — output exactly: {{ "question": "<one short, specific question>" }}
   Only do this when the answer genuinely changes the module structure (e.g. you cannot
   pick sensible fields, units, or ranges without knowing). If you can make a reasonable
   default, do so instead.
7. Do not narrate. Output the JSON object and nothing else.
8. If the request is illicit or structurally impossible, output exactly:
   {{ "refusal": "<one-sentence reason>" }}
"""


def _strip_codefence(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.endswith("```"):
            s = s.rsplit("```", 1)[0]
        if s.startswith("json\n"):
            s = s[5:]
    return s.strip()


REFINE_SYSTEM_PROMPT = f"""You are the Trus orchestrator. Your task is to update an existing
ModuleConfig based on the user's instruction.

The current config is provided as JSON. Apply the requested change and return the updated
ModuleConfig as JSON — same format, same output rules as generation.

{_COMPONENT_DOCS}

Rules:
1. Use only the component types above.
2. Preserve state values for any component that survives the edit unchanged (same id, same type).
3. Add, remove, rename, or reorder components to match the instruction.
4. New ids must be snake_case and not collide with surviving ids.
5. If other session modules are listed, use metric/cross-module bindings where helpful.
6. Do not narrate. Output the JSON object and nothing else.
7. If the request is illicit or structurally impossible, return:
   {{ "refusal": "<one-sentence reason>" }}
"""

SYNTHESIZE_SYSTEM_PROMPT = f"""You are the Trus orchestrator. The user has multiple modules
on their canvas. Generate a single dashboard ModuleConfig that surfaces the most important
cross-module insights using metric and progress_bar (cross-module) components.

{_COMPONENT_DOCS}

Rules:
1. Use metric components to aggregate numeric values across modules (totals, averages, counts).
2. Use progress_bar with source_module_id to show a specific module's progress.
3. Prefer 4-8 components. Title it something like "Dashboard" or domain-specific ("Fitness Overview").
4. Do not narrate. Output the JSON object and nothing else.
5. If there is nothing meaningful to synthesize, output:
   {{ "refusal": "Not enough data across modules to synthesize a dashboard." }}
"""


def _module_context(modules: list[ModuleConfig]) -> str:
    if not modules:
        return ""
    lines = [f"- {m.title}: {', '.join(c.id for c in m.components)}" for m in modules]
    return "\n\nExisting modules on canvas (reference their component ids for cross-module bindings):\n" + "\n".join(lines)


def _seeded_prompt(prompt: str, existing_modules: list[ModuleConfig] | None = None) -> str:
    """Ground generation with the nearest preloaded skeleton, which the model is
    told to adapt to the request. This is "preloaded templates that adjust to the
    user's content" — a seed, not a fixed answer."""
    from src.stub_templates import pick_template

    seed = json.dumps(pick_template(prompt))
    context = _module_context(existing_modules or [])
    return (
        f"User request: {prompt}\n\n"
        f"Nearest starting skeleton (adapt freely — reshape fields, labels, ranges, "
        f"and prefill state to match the request; do not just return it as-is):\n{seed}"
        f"{context}\n\n"
        f"Return the adapted ModuleConfig JSON."
    )


def _parse_module_config(raw: str) -> ModuleConfig:
    cleaned = _strip_codefence(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RefusalError(f"The model returned non-JSON output: {e.msg}") from e
    if isinstance(data, dict) and "refusal" in data:
        raise RefusalError(str(data["refusal"]))
    if isinstance(data, dict) and "question" in data and len(data) == 1:
        raise ClarifyingQuestion(str(data["question"]))
    try:
        return ModuleConfig.model_validate(data)
    except ValidationError as e:
        raise RefusalError(f"The model produced an invalid ModuleConfig: {e.errors()[0]['msg']}") from e


def generate_module(
    prompt: str,
    existing_modules: list[ModuleConfig] | None = None,
) -> ModuleConfig:
    raw = llm.generate(_seeded_prompt(prompt, existing_modules), system=SYSTEM_PROMPT)
    return _parse_module_config(raw)


def refine_module(
    config: ModuleConfig,
    prompt: str,
    existing_modules: list[ModuleConfig] | None = None,
) -> ModuleConfig:
    # Stub mode: Gemini isn't available, so return the config unchanged.
    if llm.is_stub_mode():
        return config
    context = _module_context(existing_modules or [])
    user_message = (
        f"Current ModuleConfig:\n{config.model_dump_json()}\n\n"
        f"User instruction: {prompt}"
        f"{context}\n\n"
        f"Return the updated ModuleConfig JSON."
    )
    raw = llm.generate(user_message, system=REFINE_SYSTEM_PROMPT)
    return _parse_module_config(raw)


def synthesize_workspace(modules: list[ModuleConfig]) -> ModuleConfig:
    """Generate a dashboard module that aggregates values across all session modules."""
    if llm.is_stub_mode():
        from src.schema import Metric
        return ModuleConfig(
            title="Dashboard",
            components=[
                Metric(id="total_metric", label="Total (stub)", formula="sum",
                       source_component_id="value"),
            ],
        )
    summaries = json.dumps([m.model_dump() for m in modules])
    user_message = (
        f"Session modules (JSON):\n{summaries}\n\n"
        f"Generate a dashboard ModuleConfig that surfaces the most important "
        f"cross-module insights using metric and progress_bar components."
    )
    raw = llm.generate(user_message, system=SYNTHESIZE_SYSTEM_PROMPT)
    return _parse_module_config(raw)
