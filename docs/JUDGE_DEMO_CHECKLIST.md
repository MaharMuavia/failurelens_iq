# Judge Demo Checklist

## Before The Demo

- Confirm the repo root contains `backend/`, `frontend/`, `data/`, `knowledge/`, `docs/`, `reports/`, `README.md`, `.env.example`, `.gitignore`, `Dockerfile`, `docker-compose.yml`, and `requirements.txt`.
- Run `pytest tests -v`.
- Start the backend with `uvicorn backend.api.main:app --reload --port 8000`.
- Start the frontend with `cd frontend; npm run dev`.
- Open `http://localhost:5173`.

## API Checks

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/demo/run
curl -X POST http://localhost:8000/analysis/run/EXP-1001
curl -N http://localhost:8000/analysis/stream/EXP-1001
```

## What To Show

- `/health` shows `app_mode: demo`, `local_iq: true`, and Azure integrations disabled by default.
- `/agents` lists the six judge-facing agents.
- `/demo/run` returns the full judge report.
- Frontend Judge Demo button renders the report summary.
- SSE stream shows real backend reasoning events.

## Honest Azure Statement

Say: "FailureLens IQ runs in demo mode with local grounding by default. Azure adapter boundaries are implemented for AI Search, Azure OpenAI, Blob Storage, and Cosmos DB. Real Azure calls are enabled only when credentials are provided."
