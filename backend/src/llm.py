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
    Routes the prompt to an intent-appropriate template so different prompts
    produce genuinely different modules (see stub_templates.py).
    """
    from src.stub_templates import pick_template

    return json.dumps(pick_template(prompt))


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
