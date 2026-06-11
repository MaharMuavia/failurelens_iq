# FailureLens IQ Demo Commands

## Backend

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Docker Demo

```powershell
docker compose up --build
```

## Verification

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/demo/run
curl -X POST http://localhost:8000/analysis/run/EXP-1001
curl -N http://localhost:8000/analysis/stream/EXP-1001
```

## Production Overlay

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env up --build
```
