# Judging Alignment

FailureLens IQ targets the Microsoft Agents League Hackathon 2026 Reasoning Agents track.

## Reasoning Agents

The implemented judge-facing agents are exposed through `GET /agents`:

- `FailureClassifierAgent`
- `RootCauseAnalyzerAgent`
- `ExperimentHistorianAgent`
- `PrescriptiveCoachAgent`
- `CertificationEvaluatorAgent`
- `IntegrationManagerAgent`

Planner and ConfidenceGate remain orchestration components.

## Trace Quality

`POST /demo/run` and `POST /analysis/run/EXP-1001` return `agent_trace` entries with:

- `agent_name`
- `role`
- `input_summary`
- `reasoning_steps`
- `findings`
- `uncertainty`
- `confidence_score`
- `grounding_refs`
- `recommended_next_actions`
- `audit_entries`

Each reasoning step includes `thought_type`, `evidence`, `confidence`, `uncertainty`, `assumptions`, and `next_action`.

## Enterprise Scenario

The demo report includes:

- Executive summary
- Failure classification
- Root-cause analysis
- Historical memory
- Remediation plan
- Certification readiness
- Manager summary
- Grounding summary
- Confidence summary
- Judge notes

## Microsoft IQ / Azure Foundry

FailureLens IQ is honest about integration status:

- Demo mode uses local JSON and markdown grounding.
- Demo grounding refs use `source_type: "local_demo_grounding"`.
- `/health` reports Azure integrations as `false` unless credentials are configured.
- Adapter classes exist for Azure AI Search, Azure OpenAI, Azure Blob Storage, and Azure Cosmos DB.
- Missing credentials produce warnings, not fake Azure data.

## Demo Proof

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/demo/run
curl -X POST http://localhost:8000/analysis/run/EXP-1001
curl -N http://localhost:8000/analysis/stream/EXP-1001
```

## Why It Fits The Track

The product shows agentic reasoning over failed ML experiments, not just a dashboard. The agents decompose the task, preserve uncertainty, ground claims in evidence, and turn the failure into a reusable team learning artifact.
