# Trus

An AI-orchestrated personal operating system. Backend orchestrates Gemini to emit `ModuleConfig` JSON; the frontend renders that config with a trusted component library on an infinite canvas.

## Stack

- **Backend**: Python 3.11+, FastAPI, SQLite (stdlib), `google-genai` SDK
- **Frontend**: Next.js + TypeScript, Tailwind
- **Testing**: pytest + pytest-cov (backend)
- **Env**: `.env` at repo root — never commit it

## Project Layout

```
backend/
  src/        ← all application code (import as `src.*`)
  tests/      ← pytest test files
  requirements.txt
frontend/
  app/        ← Next.js App Router pages
  components/ ← module renderer + primitive component library
  lib/        ← API client, types
  package.json
```

## Common Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
cd backend && uvicorn src.main:app --reload   # http://localhost:8000

# Tests (backend)
cd backend && pytest --cov=src --cov-report=term-missing -q

# Coverage number only (used by AutoResearch Verify)
cd backend && python -m pytest --cov=src --cov-report=term-missing -q 2>/dev/null | grep TOTAL | awk '{print $4}' | tr -d '%'

# Frontend
cd frontend && npm install && npm run dev     # http://localhost:3000
```

## AutoResearch Configuration

Use these primitives when invoking `/autoresearch`:

```
Goal:    Improve backend test coverage for src/
Metric:  % lines covered (higher is better)
Scope:   backend/src/**/*.py backend/tests/**/*.py
Verify:  cd backend && python -m pytest --cov=src --cov-report=term-missing -q 2>/dev/null | grep TOTAL | awk '{print $4}' | tr -d '%'
Guard:   cd backend && python -m pytest -q 2>/dev/null && echo "passed"
```

## Conventions

- All backend modules live under `backend/src/` and are importable as `src.<module>`
- Tests mirror the src structure: `tests/test_<module>.py`
- Gemini calls go through `src/llm.py` — never call `google.genai` directly from route handlers
- Use `python-dotenv` to load env vars; never hardcode API keys
- FastAPI routes live in `src/routes/`; business logic in `src/services/`
- The orchestrator returns a `ModuleConfig` (Pydantic) — never raw HTML/CSS/JS. The frontend renders that config via a trusted component library.
- Frontend uses the Next.js App Router. Components are server-rendered by default; mark interactive pieces with `"use client"`.
