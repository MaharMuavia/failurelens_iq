# Architecture

FailureLens IQ is an offline FastAPI reasoning-agent backend. It loads synthetic JSON experiment data, chunks local Markdown knowledge, runs deterministic agents, gates low-confidence diagnoses, and writes Markdown reports.

```text
data/*.json + knowledge/*.md
        |
DataLoader + KnowledgeIndex
        |
Planner -> Intake -> Classifier -> Diagnostic -> ConfidenceGate
        |                                      |
        |                         pass: Cert -> Remediation -> Assessment
        |                         halt: skip downstream learning agents
        |
ManagerAgent -> AgentContext -> REST / SSE / ReportService
```

The MVP uses no external LLM APIs, no vector database, no Redis, no Celery, and no database.
