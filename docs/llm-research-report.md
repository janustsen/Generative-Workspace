# Trus LLM & Template Architecture — Design & Recommendation Report

**Author:** Lead architect · **Date:** 2026-06-15 · **Audience:** Diego (maintainer)

This report incorporates adversarial verification of all research. Where verification corrected the original findings, it is flagged inline with **[CORRECTED]**.

---

## 1. Executive Summary — Recommended End-State

Trus's LLM job is narrow and forgiving: turn a short prompt into one small `ModuleConfig` JSON (a 30-variant Pydantic discriminated union), with a static ~1.5–2k-token system prompt, validate-and-retry already in place, and a ~50-builder template library as both seed and offline fallback. This shape makes a cheap/local model entirely viable.

**The single most important architectural fact:** `src/llm.py` **already** implements a complete three-provider abstraction — `gemini`, `openai` (any OpenAI-compatible `/chat/completions`, zero new deps, stdlib HTTP), and `stub`. Provider selection is by env var. **Switching providers is a config change, not a code change.** Nearly every research finding that framed this as "a ~15-line edit" was overstating the work — it is `.env` only.

**Recommended default config (the cascade):**

| Tier | Provider | Model | When it runs |
|---|---|---|---|
| **Primary (zero cost, local)** | `openai` → Ollama `http://localhost:11434/v1` | **Qwen3-4B-Instruct-2507** (Q4_K_M, ~2.5 GB) | Default for all generation on Diego's Mac |
| **Escalation (quality)** | `gemini` | **gemini-3.1-flash-lite** (cheap, current) | On repeated validation failure or hard/novel prompts |
| **External-GPU (optional scale)** | `openai` → vLLM on RunPod | **Qwen3-30B-A3B-Instruct-2507** | Only if local resources must be freed or for higher fidelity |
| **Cheapest hosted fallback** | `openai` → Groq | `llama-3.1-8b-instant` | Likely free at this volume; drop-in if no local GPU |
| **Offline** | `stub` | keyword templates | No network / dev |

**Plus two no-code-path wins that compose with all of the above:**
1. **Real-time template growth** via a semantic cache over the existing SQLite DB (embed prompt → nearest stored `ModuleConfig` → use as seed; store every generation). Embedder: **fastembed** (ONNX, no PyTorch) with a pure-Python fallback. **Do not scrape.**
2. **Gemini cost control** if you stay on Gemini: pin a cheap explicit model + rely on implicit caching.

---

## 2. Cost — Recommended Default per Scenario

Token profile (measured/verified): ~800 input (≈1.5–2k-token system prompt embedding the shared `_COMPONENT_DOCS` block, plus short user text) + ~500 output per call. **[CORRECTED]** the original "2.5KB / 625-token" system-prompt assumption was wrong — the rendered prompts are ~1,500–2,000 tokens each. Rough monthly cost at **~2,000 generations/mo** (≈1.6M in / 1.0M out):

### (a) Free / local on Mac — **RECOMMENDED DEFAULT**
- **Ollama + Qwen3-4B-Instruct-2507 (Q4_K_M).** **$0/mo.** Runs on any 16 GB Apple Silicon Mac (~2.5 GB on disk, ~4 GB working set). Set `TRUS_LLM_BASE_URL=http://localhost:11434/v1`, `TRUS_LLM_MODEL=qwen3:4b-instruct-2507-q4_K_M`. Apache 2.0 (clean for a product).

### (b) External GPU
- **vLLM on RunPod serverless, Qwen3-30B-A3B-Instruct-2507.** RunPod serverless RTX 4090 ~$1.10/hr, billed per-second, ~$0 idle. At 2,000 short generations/mo this is a few dollars at most if scale-to-zero; an always-warm on-demand 4090 ($0.69/hr) is ~$500/mo and **not worth it** at this volume. **[CORRECTED]** the original "vLLM cannot run on macOS" is now technically false (a `vllm-metal` plugin exists as of 2026), but Ollama/MLX remain the right local choice — keep vLLM for the rented Linux/NVIDIA box only.

### (c) Cheapest hosted fallback
- **Groq `llama-3.1-8b-instant`** — paid $0.05/$0.08 per 1M → **~$0.13/mo**; its free tier (~14,400 req/day, no card) likely makes 2,000/mo **entirely free**. Fast (good for the real-time goal).
- Cheaper-still paid tokens: **Novita** (~$0.02/1M, likely Diego's "VueNot" — *unverified guess, treat as a guess not fact*) ~$0.05/mo; **DeepInfra** (~$0.02–0.05/1M) ~$0.07/mo. All are OpenAI-compatible → **config-only** swap. **[CORRECTED]** these are *not* "new code branches" as the research claimed — the `openai` provider already exists.

### (d) Stay on Gemini but cheaper
- **Pin `gemini-3.1-flash-lite`** (~$0.25/$1.50 per 1M, GA/stable) → **~$1.90/mo**. **[CORRECTED — most serious correction in the whole report]:** the original rank-1 pick, `gemini-2.5-flash-lite`, is **scheduled for shutdown 2026-07-22** (and `gemini-2.5-flash` even sooner, 2026-06-17). Pinning a model that dies in weeks defeats the "eliminate drift" goal. Use `gemini-3.1-flash-lite`. The win is still large because `gemini-flash-latest` (the current alias in `DEFAULT_MODEL`) has drifted to a Gemini-3.x Flash tier (~$0.50–1.50 in / ~$3–9 out), so pinning a Lite model is a **~5–20× cut**.
- **Implicit caching** is automatic on 2.5+/3.x, no storage fee, and the ~1.5–2k-token prefix clears the 1,024-token minimum. **[CORRECTED]** the discount is **75%** for *implicit* caching (the research's "90%" is the *explicit*-cache figure), and `gemini-2.5-flash-lite` cached input is **$0.01/1M**, not the $0.025 the research repeated. Re-verify the cache rate for whichever 3.x Lite model you pin.
- Skip explicit caching (complexity, implicit already covers it) and skip Batch API (interactive UX can't absorb the ~24h turnaround).

**Bottom-line:** at 2,000 generations/mo every option is single-digit dollars or free. **Optimize for reliable JSON output + a clean swap, not for cheapest token.** The recommended path costs **$0** (local primary) with a **~$2/mo** Gemini-3.1-flash-lite escalation tail.

---

## 3. Recommended Local Model + Serving + Structured-Output Guarantee

**Serving framework: Ollama.** Lowest friction on Apple Silicon (`brew install ollama`, runs as a Metal-accelerated background service), OpenAI-compatible at `:11434/v1` so it drops straight into the existing `openai` provider. Alternative for more tok/s: MLX (`mlx_lm.server`) or LM Studio's MLX backend — same provider, just a different `TRUS_LLM_BASE_URL`. **[CORRECTED]** Ollama core is MIT but the desktop GUI ships under separate terms; irrelevant for a headless backend.

**Model: Qwen3-4B-Instruct-2507 (Q4_K_M).** Apache 2.0, non-thinking (no `<think>` blocks to strip — ideal for a JSON-only endpoint), strong instruction-following for its size, ~2.5 GB. Step-up for 32 GB+ Mac or rented GPU: **Qwen3-30B-A3B-Instruct-2507** (MoE, ~3.3B active params → small-model speed at ~30B quality). **[CORRECTED]** Qwen2.5-7B (the original pick) is fine but no longer the newest small model; Qwen3 is the current choice. MIT alternative: Phi-4-mini 3.8B. Avoid Llama for a product on license grounds (Meta Community License, not OSI-open) — though practically irrelevant for a single dev.

**How valid JSON is guaranteed (two layers):**
1. **Schema-guided decoding.** Ollama enforces structure via **llama.cpp's native GBNF grammar engine** (token-distribution masking) — **[CORRECTED]** *not* XGrammar, which the research repeatedly misattributed; XGrammar is a separate library used by vLLM/SGLang. GBNF is a CFG engine, so it handles the recursive `list[Component]` union that FSM engines (Outlines) flatten or reject. The `openai` provider already supports this via `TRUS_LLM_JSON_MODE=schema` → `response_format: json_schema`. Empirically ~93–96% schema coverage on realistic schemas; near-100% on simple ones.
2. **Pydantic validate-and-retry.** Already present in `orchestrator._generate_validated` / `_parse_modules`. This is the safety net for the residual misses and for the array-returning decompose path (where `json_object` mode is correctly skipped).

**Three schema-side mitigations (important for THIS app's discriminated union):**
- **Do NOT hand the engine the raw `ModuleConfig.model_json_schema()`.** It emits `oneOf` + `$ref` + `minItems`/ranges. On vLLM/SGLang these force xgrammar to silently fall back to the slower (and historically buggy) outlines backend; on GBNF they bloat the grammar. Constrain only the discriminator `type` enum + a permissive object, then Pydantic-validate. The existing `strict: False` flag in `_openai_chat` is the right posture.
- **Leave `state: dict[str, Any]` unconstrained** — it's structurally unconstrainable; let the model fill it free-form, validate after.
- **Keep the template seed in the prompt** — it does more for component-choice quality than any decoder setting.

**Honest quality verdict vs Gemini:** Constrained decoding guarantees a *valid* `ModuleConfig`, never a *good* one. The real gap is **semantic** — picking kanban-vs-table for the intent, icon/accent variety, 1-vs-6 module decomposition. A 4–8B model lands an estimated **10–25% behind Gemini Flash** on these subjective calls (*low-confidence estimate — needs an eval*). The app already closes most of this gap because it **seeds every call with a template skeleton** (turning "choose a component" into the easier "edit this skeleton") and **validates/retries**. **Verdict: local-first is a sound default for Trus** — but ship it behind a **cascade to gemini-3.1-flash-lite** on repeated validation failure or low-confidence intents, and gate the rollout on a small eval (reuse the ~50 templates as labeled intents; require ≥~85–90% of Flash on component-choice match before going local-only).

---

## 4. Recommended Real-Time Template Architecture

**Verdict on scraping: do NOT do it.** Notion's marketplace terms prohibit copying template functionality and redistribution; scraped templates are HTML / proprietary block JSON that don't map to Trus's 30-type `ModuleConfig` (each would need heavy LLM re-translation, re-introducing the very API cost you're cutting); scrapers are brittle and a maintenance burden for one dev. It provides ~nothing over self-growing the library. If you want external *inspiration*, use MIT-licensed JSON-schema/form corpora (SurveyJS Form Library, FormEngine Core) as design references for hand-writing new builders — **[CORRECTED]** note `jsonform` is unmaintained (last release 2021), and SurveyJS's *builder* product is commercial (only the runtime library is MIT).

**Do this instead: a semantic cache + self-growing library on the existing SQLite DB.** Scale is decisive: the live `trus.db` has only **133 modules / 218 versions**, so brute-force cosine over a few hundred float32 vectors in NumPy is sub-millisecond — **no vector index, no sqlite-vec needed** (revisit only past ~10k templates).

Architecture:
1. **New table** in `db.py` (stdlib `sqlite3`, matching existing style): `templates(id TEXT PK, prompt TEXT, kind TEXT, config_json TEXT, embedding BLOB, created_at TEXT)` where `kind` ∈ `single`|`system` (mirrors `pick_template` vs `pick_system`).
2. **`embed(text)->list[float]` helper.** Default **fastembed** (`bge-small-en-v1.5`, 384-dim, ONNX, no PyTorch, ~90 MB one-time download) — **[CORRECTED]** prefer bge-small (MIT) over all-MiniLM as the default (cleaner training-data license). Pure-Python char-ngram hashing fallback when fastembed isn't installed, so offline/stub mode keeps working. (If Ollama is already running, `nomic-embed-text` via `/api/embed` is an alternative — but **[CORRECTED]** its context as served by Ollama is **2K, not 8K**.)
3. **Retrieval as seed.** In `orchestrator._seeded_prompt` / `_seeded_system`: embed the user prompt, brute-force cosine over stored embeddings; if top match ≥ ~0.45 use that stored `ModuleConfig` as the seed instead of the keyword builder; keep `pick_template`/`pick_system` as the fallback when the store is sparse.
4. **Grow automatically.** After every successful generation in `generate_module`/`generate_modules`, store prompt + config_json + embedding. Seed the store once with the existing ~50 builders so day one isn't cold.
5. **Optional exact-cache cost cut.** If top-match similarity ≥ ~0.95, return the stored config and skip the model call entirely — with a "regenerate / make it different" path that bypasses the cache. (Thresholds 0.45/0.95 are starting heuristics tuned to embedding-score distribution; tune empirically.)

**Embedding choice (decisive):** **fastembed (bge-small, ONNX)** — the only zero-PyTorch local option, fits the project's lean `requirements.txt`. Pure-Python char-ngram as the true zero-dependency fallback.

---

## 5. Prioritized Implementation Checklist (mapped to this codebase)

**P0 — Cheap wins, config-only, do today**
1. **Pin a current cheap Gemini model.** Set `GEMINI_MODEL=gemini-3.1-flash-lite` in `.env` (read by `llm.py:_gemini_generate`; `DEFAULT_MODEL` is the fallback). **Do not** pin the deprecated `gemini-2.5-flash-lite`. Verify the alias drift in AI Studio. → *verify: `provider_info()` reports the pinned model; tests pass.*
2. **Cap output / confirm caching.** Add `max_output_tokens` (~1,200–1,536) to `GenerateContentConfig` in `_gemini_generate`/`_gemini_generate_file` (output is priced 4× input). Log `response.usage_metadata.cached_content_token_count` once to confirm implicit-cache hits. → *verify: large decompose still returns full arrays.*

**P1 — Local model (zero new deps, config-only)**
3. `brew install ollama && ollama pull qwen3:4b-instruct-2507-q4_K_M`. Set `TRUS_LLM_BASE_URL=http://localhost:11434/v1`, `TRUS_LLM_MODEL=qwen3:4b-instruct-2507-q4_K_M`, `TRUS_LLM_JSON_MODE=schema`. The `openai` provider in `llm.py` activates automatically (`_resolve_provider` picks `openai` when `TRUS_LLM_BASE_URL` is set). **No code change.** → *verify: `pytest`; generate a few real prompts; check Pydantic validity rate.*
4. **Build a small eval set** from the ~50 builders as labeled intents; measure component-choice match vs Gemini. → *verify: local ≥ ~85–90% of Flash before going local-only.*

**P2 — Cascade fallback (small code change in `llm.py`/orchestrator)**
5. Add an escalation branch: on repeated `ValidationError`/`LLMError` from the local path, retry once via the Gemini path. The funnel is already centralized (`generate`), so this is localized. Keep `stub` as the final offline fallback. → *verify: kill Ollama → confirm cascade to Gemini, then to templates.*

**P3 — Semantic cache + growing library**
6. Add `templates` table to `db.py` (stdlib sqlite3). 
7. Add `embed()` helper (fastembed default + pure-Python fallback); add `fastembed` to `requirements.txt` (ONNX, no torch). 
8. Wire retrieval into `_seeded_prompt`/`_seeded_system`; persist every generation in `generate_module`/`generate_modules`; seed once from the ~50 builders. 
9. (Optional) Add the ≥0.95 exact-cache short-circuit with a regenerate bypass. → *verify: paraphrased prompts ("track my habits" vs "habit tracker") retrieve the same seed; store grows; cache-hit returns skip the model.*

**Skip:** explicit Gemini caching (below value vs implicit), Batch API (interactive UX), sqlite-vec (unnecessary at 133 vectors), scraping (legal/format/maintenance).

---

## 6. Feasibility & Appropriateness Table

| Recommendation | Feasible? | Appropriate? | Single biggest risk |
|---|---|---|---|
| **Local Qwen3-4B via Ollama as primary** | Yes — config-only, provider exists | Yes — tiny output, seed+validate close the gap | Semantic quality on ambiguous prompts (mitigated by cascade) |
| **Schema-guided decoding (GBNF) + Pydantic retry** | Yes — built into Ollama + existing validator | Yes | Raw discriminated-union schema confuses grammar → constrain only `type`, validate rest |
| **Cascade to gemini-3.1-flash-lite** | Yes — small code add at the funnel | Yes — caps cost, keeps Flash quality for hard cases | Two paths to keep behaviorally consistent |
| **vLLM + Qwen3-30B-A3B on RunPod (external GPU)** | Yes (serverless, per-second) | Only if scale/offload needed | Always-warm GPU = recurring cost the goal was to cut; use scale-to-zero |
| **Pin gemini-3.1-flash-lite + implicit caching (stay-on-Gemini)** | Yes — `.env` one-liner | Yes — ~5–20× cut, zero deps | Alias/deprecation drift → must pin explicit, re-check on Google's schedule |
| **Cheapest hosted (Groq free tier)** | Yes — config-only | Yes — likely free at this volume | Free-tier rate limits/throttling on bursts (offline templates already cover) |
| **Semantic cache + self-growing library (SQLite)** | Yes — 133 rows, brute-force NumPy | Yes — directly delivers "real-time/growing" | Cold start + threshold tuning (mitigated by seeding from ~50 builders) |
| **fastembed (bge-small, ONNX) embedder** | Yes — no PyTorch | Yes — fits lean deps | One-time ~90 MB HF download needs network |
| **Scraping productivity-app templates** | Low | **No** | ToS/legal + format mismatch + maintenance; ~zero benefit over self-growing |

---

### Key corrections the verification forced (so they aren't lost)
- **`gemini-2.5-flash-lite` is deprecated (shutdown 2026-07-22)** → pin **`gemini-3.1-flash-lite`** instead. *(Most serious; the original rank-1 pick self-destructs in weeks.)*
- **Provider abstraction already exists** in `llm.py` — all non-Gemini swaps are **config-only**, not "new code branches."
- **Ollama uses GBNF, not XGrammar** for structured output.
- **Implicit Gemini caching = 75% discount** (not 90%); flash-lite cached input = **$0.01/1M** (not $0.025).
- **Qwen3** (not Qwen2.5) is the current small-model pick; Apache-2.0.
- **System prompts are ~1.5–2k tokens** (not 2.5KB/625) — they clear the implicit-cache minimum.
- **"VueNot"/"Banana Pro" are unverifiable guesses** (Novita / defunct Banana.dev respectively) — do not treat as fact; the recommendations don't depend on them.

Relevant files: `/Users/Diego/Generative-Workspace/backend/src/llm.py`, `/Users/Diego/Generative-Workspace/backend/src/services/orchestrator.py`, `/Users/Diego/Generative-Workspace/backend/src/stub_templates.py`, `/Users/Diego/Generative-Workspace/backend/src/db.py`, `/Users/Diego/Generative-Workspace/backend/src/schema.py`, `/Users/Diego/Generative-Workspace/backend/requirements.txt`.