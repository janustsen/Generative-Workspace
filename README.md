# Trus

An AI-orchestrated personal operating system: describe what you need to organize, and the system shapes the exact tool for it in front of you.

**North star:** the exact tool you need, in the shape of your life, for the cost of a sentence — and you stay in the driver's seat the entire time.

## Architecture

- **Backend** — Python 3.11+ / FastAPI. Gemini orchestrates pre-built components by returning a `ModuleConfig` (JSON), never raw UI code. SQLite for persistence.
- **Frontend** — Next.js + TypeScript. An infinite canvas renders modules from `ModuleConfig` using a trusted component library. Anonymous session via signed cookie.

## Run it

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn src.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:3000.
