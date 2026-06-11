# FailureLens IQ Audit Report

## Repository Status: DEMO-READY MVP WITH AZURE PRODUCTION ADAPTERS

Date: June 2026

FailureLens IQ is now structured as a root-level project with backend, frontend, data, knowledge, docs, reports, Docker, and tests at the repository root.

## Implemented

- Root README with judge-oriented setup and demo flow.
- `.venv` removed from the Git index and ignored.
- Root `.gitignore` plus frontend `.gitignore`.
- `/health` contract with app mode and enabled integrations.
- `/agents` endpoint with six judge-facing agents.
- `/demo/run` endpoint with a complete judge report.
- `/experiments/upload` endpoint with Pydantic validation and in-memory persistence for demo analysis.
- Body-based `POST /analysis/run` plus compatible `POST /analysis/run/{experiment_id}`.
- Reasoning steps with `thought_type`, evidence objects, confidence, uncertainty, assumptions, and next action.
- Explicit `ExperimentHistorianAgent`.
- Azure adapter boundary under `backend/azure/`.
- Live Azure AI Search REST retrieval when credentials are configured.
- Live Azure OpenAI summary generation when credentials are configured.
- Live Cosmos DB trace storage and Blob report upload when credentials are configured.
- GitHub Actions CI for backend tests and frontend build.
- Frontend API client with real backend calls and honest mock fallback.
- Real SSE hook using `EventSource`.
- Root Dockerfile and docker-compose file.
- Contract tests for API, docs, frontend, grounding, reasoning traces, and no virtualenv artifacts.

## Azure Truthfulness

The app does not claim live Azure integration by default.

Demo mode uses local JSON and markdown files and labels grounding as `local_demo_grounding`.

Production mode has credential-gated live calls for Azure OpenAI, Azure AI Search, Azure Blob Storage, and Azure Cosmos DB. Those integrations are reported as enabled only when the required environment variables are present.

## Known Limitations

- Demo data is synthetic.
- Uploaded experiments use in-memory persistence for the demo session.
- Azure production calls are live when credentials are configured and return warnings when disabled or unreachable.
- The React app is a polished MVP dashboard, not a full enterprise admin suite.
- Docker Compose uses demo defaults; copy `.env.example` to `.env` for Azure credential demos.

## Verification Commands

```powershell
pytest tests -v
curl http://localhost:8000/health
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/demo/run
curl -X POST http://localhost:8000/analysis/run/EXP-1001
curl -N http://localhost:8000/analysis/stream/EXP-1001
```
