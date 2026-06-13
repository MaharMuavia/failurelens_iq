# FailureLens IQ Frontend

Vite React client for FailureLens IQ.

## Run

```bash
npm install
npm run dev
```

`npm run dev` starts FastAPI on `http://127.0.0.1:8000`, waits for `/health`, then starts Vite on `http://127.0.0.1:5173`.

For frontend-only development, use:

```bash
npm run dev:frontend
```

The Vite dev proxy sends `/api/*` to `http://127.0.0.1:8000/*`. Override direct API calls with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Scripts

- `npm run dev` starts backend and frontend together.
- `npm run dev:backend` starts only FastAPI.
- `npm run dev:frontend` starts only Vite.
- `npm run test -- --run` runs Vitest once for CI.
- `npm run build` creates the static production bundle.
- `npm run lint` runs TypeScript checks.
