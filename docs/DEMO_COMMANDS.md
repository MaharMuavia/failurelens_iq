# Demo Commands

## Backend

```powershell
copy .env.demo .env
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest tests -v
uvicorn backend.api.main:app --reload --port 8000
```

## Backend Checks

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl http://localhost:8000/iq/status
curl -X POST http://localhost:8000/demo/run
curl -N http://localhost:8000/analysis/stream/EXP-1001
```

## Frontend

```powershell
cd frontend
npm install
npm run test -- --run
npm run build
npm run dev
```

Open `http://localhost:5173`, click `Run Judge Demo`, show the animated agent graph, then show the Microsoft IQ Proof panel.

## Docker

```powershell
docker compose up --build
```

## Optional Observability

```powershell
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up --build
```
