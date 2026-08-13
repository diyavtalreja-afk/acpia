# ACPIA — Agentic Child Protection Investigation Assistant

**MOCK/DEMO prototype** — agentic triage pipeline for digital-forensics investigators.
Built for the Kerala Police Cyberdome hackathon. All data is synthetic; all
detection outputs are labeled MOCK/DEMO. Decision-support only: the agent flags
and explains, the human investigator decides.

## Quickstart

```bash
# 1. Backend
cd acpia
pip install -r requirements.txt
python scripts/generate_mock_device.py      # build mock device + known-hash DB + manifest
python -m uvicorn backend.main:app --port 8000

# 2. Frontend (dev mode, optional — prod build is served by FastAPI)
cd frontend
npm install
npm run build        # builds dist/ — served automatically at http://localhost:8000
# or: npm run dev    # Vite dev server on :5173 with /api proxy to :8000

# 3. Tests
python -m pytest backend/tests -q
```

Open http://localhost:8000 — click **Start scan** (or use the pre-scanned case),
then explore: flagged list → file detail → plain-English queries → knowledge graph.

## LLM integration (optional, graceful fallback)

Explanations and NL→query translation use the LLM when configured, and fall back
to deterministic template providers automatically (same output schema, labeled
in the UI):

```bash
export ANTHROPIC_API_KEY=sk-...      # or
export OPENAI_API_KEY=sk-...
export ACPIA_LLM_TIMEOUT=8           # seconds, default 8
# optional model overrides:
export ANTHROPIC_MODEL=claude-sonnet-4-20250514
export OPENAI_MODEL=gpt-4o-mini
```

With no key, everything works via the template path — the demo must not die
on a network error.

## Demo queries (planted answers, deterministic)

| Question | Expected answer |
|---|---|
| "Show me every conversation mentioning Harbour Line in the last 30 days." | 15 messages across 2 conversations (arun_manoj, sneha_deepa) |
| "Who was the most active contact at night?" | Manoj P — 14 messages between 00:00–04:00 |
| "Find images similar to flag-3." | Perceptual neighbors of the 3rd-highest-risk flag (e.g., IMG_4471_original 100%, IMG_4471.jpg 91%) |

## Scale

The mock device ships with **146 files** (38 images, 60 documents, 20 data
files, 12 PDFs, 12 audio clips, 4 chat exports). Full scan completes in a few
seconds (parallel fingerprinting, throttled progress events, one-time cached
graph layout). All flaggable content scales independently of volume — adjust
the targets in `scripts/generate_mock_device.py` and the pipeline stays O(n).

## Architecture

```
mock_device/  →  INGESTION (SHA-256 + perceptual hash, metadata, chat parse)
              →  HASH-MATCH (mock known-hash DB: exact + visual)
              →  SYNTHETIC-MEDIA CHECK (mock artifact detector, labeled)
              →  RISK SCORING (rule-based; flag.score == SUM(rule points))
              →  EXPLANATIONS (LLM → template fallback; source shown in UI)
              →  KNOWLEDGE GRAPH (NetworkX: file/message/person/location/known)
              →  AGENT (ReAct loop with visible reasoning log)
              →  NL QUERY + DASHBOARD (React, Mission Control design)
```

## Key files

| File | Purpose |
|---|---|
| `scripts/generate_mock_device.py` | builds `mock_device/`, `data/mock_known_hashes.json`, `data/manifest.json` |
| `backend/artifact_spec.py` | planted-artifact contract (single source of truth for the mock scorer) |
| `backend/scan/pipeline.py` | orchestrates a scan, emits SSE progress |
| `backend/scan/risk.py` | rule engine; traceable scores |
| `backend/explain/` | LLM + template explanation providers |
| `backend/agent/` | ReAct loop, tools, NL→plan translation |
| `backend/main.py` | FastAPI app (API + serves frontend) |
| `backend/tests/test_modules.py` | 11 tests; manifest-driven |

## Honesty rules (enforced)

- All flags/explanations carry `mock: true`; UI shows MOCK/DEMO badges.
- Known-hash DB contains **invented placeholder hashes only** — never real
  (NCMEC/PhotoDNA/ICSE) databases.
- Images are PIL placeholders (colors, gradients, shapes) — no people.
- The synthetic-media scorer detects a **planted, documented artifact** as a
  stand-in for a GAN fingerprint — it is labeled a MOCK artifact detector.
- The agent never acts autonomously: it flags, explains, and the investigator
  decides (Mark for review / Escalate / Dismiss).
