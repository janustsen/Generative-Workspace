import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _isolate_db(monkeypatch):
    """Each test gets a fresh SQLite file so state never leaks across tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("TRUS_DB_PATH", path)
    yield
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def _isolate_llm_env(monkeypatch):
    """Don't let a developer's local-model .env (e.g. TRUS_LLM_BASE_URL pointing
    at Ollama) leak into tests — provider resolution must be deterministic, and
    no test should hit a live endpoint. Tests opt into a provider explicitly."""
    for k in ("TRUS_LLM_PROVIDER", "TRUS_LLM_BASE_URL", "TRUS_LLM_MODEL",
              "TRUS_LLM_API_KEY", "TRUS_LLM_JSON_MODE",
              "TRUS_VISION_MODEL", "TRUS_VISION_BASE_URL", "TRUS_VISION_API_KEY"):
        monkeypatch.delenv(k, raising=False)
