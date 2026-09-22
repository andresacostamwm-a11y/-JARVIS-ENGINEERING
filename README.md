# JARVIS Engineering Professional MVP

Engineering platform for MEP / electrical / hydraulic / energy workflows: assets, verified calculations, React Flow diagrams, document RAG, and Grok chat with tool calling.

Spanish-first UI · English code/comments · Deterministic Python calc engine (never LLM math).

## Quick start

```bash
cp .env.example .env
# Optional: set XAI_API_KEY for Grok chat (degrades gracefully if missing)

docker compose up --build
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:3000 |
| API + OpenAPI | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 |

### Demo credentials

| User | Password | Role |
|------|----------|------|
| `demo@jarvis.local` | `demo1234` | ENGINEER |
| `admin@jarvis.local` | `admin1234` | ADMIN |

All seed data is labeled **DEMO**.

## Stack

- **apps/web** — Next.js App Router, React, TypeScript, Tailwind, Zustand, TanStack Query, RHF+Zod, React Flow
- **services/api** — FastAPI, SQLAlchemy, Alembic, JWT+RBAC, SSE chat
- **services/worker** — Celery + Redis (document ingest / chunking)
- **postgres**, **redis**, **minio** via Docker Compose
- **AI** — `AIProvider` + `XAIProvider` (Grok) with tool calling; optional `XAI_API_KEY`

## MVP API (`/api/v1`)

- `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
- `CRUD /assets`, `CRUD /projects`
- `POST /documents/upload`, `GET /documents`, `GET /documents/{id}`
- `POST /calculations/electrical|hydraulic|energy` — verified engines
- `CRUD /drawings` + export JSON / SVG
- `POST /chat`, `POST /chat/stream` (SSE), `POST /agents/run`
- `POST /rag/search`
- `GET /audit/events`
- `GET /health`

## Calculation engine

Real Python modules under `services/api/app/services/calculations/`.
Every result persists: **INPUT / FORMULA / UNITS / ASSUMPTIONS / RESULT / CHECK / SOURCE / VERSION**.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pytest
PYTHONPATH=services/api pytest tests/calculations -v
```

**Verified:** 11/11 unit tests passed (2026-09-21).

## Drawing source of truth

**JARVIS Drawing JSON** (nodes + edges in Postgres) — not raster images.
React Flow editor can save/edit and export JSON + SVG.

## RBAC roles

`ADMIN` · `ENGINEERING_DIRECTOR` · `ENGINEER` · `TECHNICIAN` · `AUDITOR` · `VIEWER`

## DONE vs COMING SOON

### DONE (MVP)

- Auth (JWT login/refresh) + RBAC
- Assets / projects / CAPEX fields + DEMO seed (~20 assets)
- Document upload + chunk ingest (Celery or inline fallback)
- Bag-of-words RAG search
- Electrical / hydraulic / energy verified calcs + persistence + unit tests
- React Flow drawings CRUD + JSON/SVG export
- Grok chat + tool calling (calcs, asset search, RAG); graceful degrade without API key
- SSE streaming endpoint
- Audit event log
- Light/dark theme, left nav + workspace + right JARVIS panel
- Docker Compose stack, OpenAPI, Alembic baseline

### COMING SOON (stubbed)

- Full BIM / IFC / DWG CAD import (`services/cad`)
- PDF/DOCX OCR extraction
- Vector embeddings / pgvector RAG
- Clash detection & quantity takeoff
- Advanced CAPEX scheduling
- Full BMS/BACnet live integration
- Multi-org SaaS billing

## Known limits

- Calc engines use simplified design formulae (not a substitute for stamped PE design).
- RAG is lexical (bag-of-words), not semantic embeddings.
- Chat without `XAI_API_KEY` returns a degraded message or tool-result summary.
- SVG export is a schematic rendering of Drawing JSON (JSON remains SoT).

## License

MIT — see [LICENSE](LICENSE).
