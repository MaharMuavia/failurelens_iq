# Architecture

FailureLens IQ is a FastAPI plus React MVP with a deterministic multi-agent backend and local demo grounding.

## Components

- `backend/api/main.py`: FastAPI app and endpoint contracts.
- `backend/core/orchestrator.py`: Agent orchestration and SSE event emission.
- `backend/agents/`: Reasoning agents and trace generation.
- `backend/azure/`: Credential-gated Azure adapter boundary.
- `backend/services/`: local knowledge index, scoring, reporting.
- `frontend/src/api/client.ts`: React API client.
- `frontend/src/hooks/useSSEStream.ts`: EventSource streaming hook.
- `data/`: synthetic experiment and team data.
- `knowledge/`: local markdown grounding corpus.

## Data Flow

```mermaid
flowchart LR
    Frontend["React dashboard"] --> API["FastAPI"]
    API --> Orchestrator["Orchestrator"]
    Orchestrator --> Agents["Reasoning agents"]
    Agents --> Trace["Agent trace"]
    Agents --> Grounding["GroundingAdapter"]
    Grounding --> Local["Demo local data"]
    Grounding --> Azure["Credential-gated Azure clients"]
    Trace --> Report["Demo/report response"]
```

## Modes

Demo mode is default and works without credentials. Production mode can enable Azure adapters when credentials are present. Missing credentials return warnings rather than fake Azure data.
