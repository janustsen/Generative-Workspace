import json
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

_client = None


def _is_stub_key(key: str | None) -> bool:
    return not key or key.startswith("stub-") or key == "your_key_here"


def _stub_module_for(prompt: str) -> str:
    """Canned ModuleConfig for dev when no real Gemini key is set.

    Lets the full pipeline (frontend → backend → orchestrator → renderer) be
    exercised locally without burning real LLM credits or needing an API key.
    """
    title_words = prompt.strip().split()[:4]
    title = " ".join(w.capitalize() for w in title_words) or "Tracker"
    return json.dumps(
        {
            "title": f"{title} Tracker",
            "components": [
                {"id": "name", "type": "text_input", "label": "Name", "placeholder": "e.g. Bench press"},
                {"id": "sets", "type": "number_input", "label": "Sets", "min": 0, "step": 1},
                {"id": "weight", "type": "slider", "label": "Weight", "min": 0, "max": 300, "step": 5, "unit": "lb"},
                {"id": "done_today", "type": "checkbox", "label": "Done today"},
                {"id": "history", "type": "list", "label": "History", "item_label": "Entry", "placeholder": "Today: 3x5 @ 135"},
                {"id": "weekly", "type": "progress_bar", "label": "Weekly target", "max": 5, "bound_to": "sets"},
            ],
            "state": {},
            "layout": {"x": 80, "y": 120, "width": 380, "height": 460},
            "summary_component_id": "weekly",
        }
    )


def _get_client():
    global _client
    if _client is None:
        from google import genai

        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def generate(prompt: str, system: Optional[str] = None) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if _is_stub_key(key):
        return _stub_module_for(prompt)
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    response = _get_client().models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )
    return response.text
