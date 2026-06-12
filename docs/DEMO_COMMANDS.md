# Demo Commands

## Backend

```powershell
copy .env.demo .env
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
curl -X POST http://localhost:8000/analysis/run/EXP-1001
```

## Frontend

```powershell
cd frontend
npm install
npm run test -- --run
npm run build
npm run dev
```

Open `http://localhost:5173`, click Judge Demo, then show the Microsoft IQ Proof panel.
