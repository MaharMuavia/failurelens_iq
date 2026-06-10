# API Contract

Base URL: `http://localhost:8000`

## GET /health

Returns app mode, version, demo readiness, experiment count, knowledge chunk count, and enabled integrations.

## GET /agents

Returns the six judge-facing agents with `name`, `role`, `judging_purpose`, `input`, `output`, and `trace_fields`.

## POST /demo/run

Runs the complete EXP-1001 judge demo and returns:

- `demo_title`
- `executive_summary`
- `agent_workflow`
- `failure_classification`
- `root_cause_analysis`
- `historical_memory`
- `remediation_plan`
- `certification_readiness`
- `reasoning_timeline`
- `grounding_summary`
- `confidence_summary`
- `manager_summary`
- `judge_notes`

## POST /analysis/run

Body:

```json
{
  "experiment_id": "EXP-1001",
  "options": {
    "include_reasoning_trace": true,
    "include_grounding": true,
    "include_certification": true
  }
}
```

Returns the analysis context. If grounding is requested, includes `grounding_summary`.

## POST /analysis/run/{experiment_id}

Compatibility endpoint. Runs the same analysis for a path parameter experiment ID.

## GET /analysis/stream/{experiment_id}

Server-sent events stream. Emits pipeline and agent events as JSON in `data:` messages.

## POST /experiments/upload

Accepts an experiment JSON payload and validates it using the `ExperimentLog` Pydantic schema. The current MVP validates but does not persist uploaded experiments.

## GET /experiments

Lists experiments with optional filters:

- `page`
- `limit`
- `team_id`
- `outcome`
- `failure_category`

## GET /knowledge/search

Query params:

- `q`
- `top_k`
- `cert_filter`

Returns locally grounded knowledge hits in demo mode.

## Reports

- `POST /report/{experiment_id}/generate`
- `GET /report/{experiment_id}`
