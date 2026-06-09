# FailureLens IQ

FailureLens IQ turns failed ML experiments into organizational learning memory. It diagnoses root cause with cited evidence fields, grounds recommendations in local Microsoft-style Markdown knowledge, maps skill gaps to certifications, streams agent reasoning over SSE, produces manager intelligence, and generates audit-ready reports.

## Why This Is a Reasoning-Agent System

It is not just a classifier. The planner forms a hypothesis, the classifier evaluates six competing rules, the diagnostic agent retrieves grounding and runs self-reflection checks, and the confidence gate changes the code path when evidence is weak. `SPARSE-001` proves the system can say it does not know.

## Architecture

```text
JSON data -> DataLoader
Markdown docs -> KnowledgeIndex -> LocalIQProvider
Experiment -> Planner -> Intake -> Classifier -> Diagnostic -> ConfidenceGate
                                      pass -> CertMapper -> Remediation -> Assessment
                                      halt -> skipped learning agents
ManagerAgent -> TeamInsights
AgentContext -> REST, SSE, Markdown report
```

## Setup

```bash
pip install -r requirements.txt
uvicorn backend.api.main:app --reload --port 8000
pytest tests/ -v --tb=short
```

## API Examples

```bash
curl http://localhost:8000/health
curl http://localhost:8000/experiments/EXP-1001
curl -X POST http://localhost:8000/analysis/run/EXP-1001
curl -N http://localhost:8000/analysis/stream/EXP-1001
curl "http://localhost:8000/knowledge/search?q=imbalanced+classification+minority+f1"
curl http://localhost:8000/manager/team/TEAM-B
curl -X POST http://localhost:8000/analysis/run/SPARSE-001
curl -X POST http://localhost:8000/report/EXP-1001/generate
```

## SSE Event Shape

```json
{
  "event": "agent_reasoning",
  "run_id": "...",
  "agent": "DiagnosticAgent",
  "timestamp": "...",
  "data": {
    "step_number": 3,
    "finding": "..."
  }
}
```

## Quality Gates

- `/health` returns 25 experiments and at least 24 knowledge chunks.
- `EXP-1001` returns a non-Unknown classification and at least seven trace entries.
- Completed traces include reasoning steps and key evidence.
- `SPARSE-001` requires human review and does not fabricate a root cause.
- TEAM-B produces recurring Responsible AI / Bias manager intelligence.
- Local knowledge queries return grounded citations.
- `pytest tests/ -v --tb=short` passes.

## Limitations

The MVP is intentionally offline and deterministic. Azure Foundry integration is represented by an offline adapter class only. The frontend scaffold exists, but implementation is deferred until the backend remains stable.
