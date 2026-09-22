# JARVIS Engineering — Architecture

## Decisions (stable for MVP)

1. **Monorepo** with `apps/`, `services/`, `packages/`, `infrastructure/`.
2. **Calculation authority** is Python code in `services/api/app/services/calculations/`. LLMs may *invoke* tools but never invent numeric results.
3. **Drawing source of truth** is JARVIS Drawing JSON (`drawings` + `drawing_nodes` + `drawing_edges`). React Flow is the editor; SVG/PNG are exports only.
4. **Auth** = JWT access + refresh; RBAC via ranked roles (`VIEWER` < `AUDITOR` < `TECHNICIAN` < `ENGINEER` < `ENGINEERING_DIRECTOR` < `ADMIN`).
5. **AI** abstracted behind `AIProvider`; production implementation is `XAIProvider` (OpenAI-compatible Grok API). Missing `XAI_API_KEY` → degraded responses, rest of app works.
6. **Object storage** = MinIO (S3 API) with local `/tmp` fallback if MinIO unreachable.
7. **Async jobs** = Celery + Redis for document ingest; API falls back to inline chunking if broker enqueue fails.
8. **RAG MVP** = bag-of-words overlap over `document_chunks` (no vector DB yet).
9. **Schema** created with SQLAlchemy `create_all` on startup; Alembic holds baseline revision `001` for future migrations.
10. **UI language** Spanish-first; code and comments English.
11. **Demo data** always flagged `is_demo=True` / labels containing `DEMO`.
12. **Secrets** only via environment (`.env.example` committed; `.env` gitignored).

## Runtime topology

```
Browser (Next.js :3000)
    │  REST + SSE
    ▼
FastAPI (:8000) ──► Postgres
    │                 Redis ◄── Celery worker
    │                 MinIO
    └──► xAI Grok (optional)
```

## Calculation envelope

Every calc returns and optionally persists:

| Field | Purpose |
|-------|---------|
| inputs | Numeric/categorical inputs |
| formula | Human-readable formula string |
| units | Unit map |
| assumptions | Explicit limits of the model |
| result | Outputs |
| check_status | PASS / WARN / FAIL |
| check_notes | Why |
| source | Standard / textbook reference |
| version | Engine version |
| engine_module | Python callable path |

## Frontend layout

```
┌──────────┬─────────────────────────┬──────────────┐
│ Left nav │ Workspace               │ JARVIS panel │
│          │ (page content)          │ chat/sources │
│          │                         │ /calcs       │
└──────────┴─────────────────────────┴──────────────┘
```

Theme toggle persists in `localStorage`.

## Security notes

- Passwords hashed with bcrypt (passlib).
- CORS limited to configured origins.
- Never commit real API keys.
- Audit events written on login, CRUD, calculate, chat.

## Extension points (COMING SOON)

- `services/cad` — DWG/IFC → Drawing JSON
- pgvector embeddings on `document_chunks.embedding`
- Multi-tenant billing / SSO
