# FailureLens IQ Video Demo Checklist

## Before Recording

- Backend running on `http://localhost:8000`.
- Frontend running on `http://localhost:5173`.
- Browser zoom set to 90% or 100%.
- Screen resolution set to 1920x1080 or another 16:9 resolution.
- Terminal commands prepared in separate tabs.
- `.env.demo` selected for no-secret demo mode.

## Endpoint Checks

- `GET /health` works.
- `GET /readiness` works.
- `GET /agents` works.
- `POST /demo/run` works.
- `POST /analysis/run/EXP-1001` works.
- `GET /analysis/stream/EXP-1001` streams events.

## Frontend Checks

- Dashboard loads without client error.
- No backend disconnected banner appears during the real demo.
- `Judge Demo` button works.
- `Copy summary` button works.
- `Report` button generates a report.
- `Health` button returns backend status.
- Video demo banner appears when `VITE_VIDEO_DEMO_MODE=true`.

## Fallback Plan

If Azure credentials fail, stay in demo mode and say: "The demo uses local grounding so the app remains judge-runnable without secrets. The Azure adapters are credential-gated and report enabled integrations through `/health` and `/readiness`."
