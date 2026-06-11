# FailureLens IQ Judge Q&A

## Why agents?

The work is naturally multi-step: classify the failure, explain root cause, compare history, recommend remediation, map certification readiness, and package the manager view. Separate agents make each step auditable with evidence, confidence, and uncertainty.

## Where is Microsoft IQ?

Demo mode uses local Microsoft-aligned grounding files so the app runs without secrets. Production mode can use Azure AI Search, Azure OpenAI, Cosmos DB, and Blob Storage when credentials are configured.

## What happens when confidence is low?

The confidence gate marks the run for human review and the report keeps uncertainty visible instead of pretending the system is certain.

## How do you prevent hallucination?

Outputs are bound to experiment fields, local or Azure grounding references, deterministic rule evidence, and explicit confidence. The app exposes concise reasoning summaries, not hidden chain-of-thought.

## How do you handle responsible AI?

Responsible AI failures are explicit categories. The workflow flags bias and compliance-sensitive cases for review and includes manager-level escalation guidance.

## What is production-ready?

This is a production-hardened MVP: configuration, auth hooks, CORS validation, rate limiting, max body size, security headers, structured logging, Docker healthchecks, and CI are present.

## What remains for enterprise deployment?

Enterprise deployment still needs Entra ID, RBAC, managed persistence, Key Vault-backed secrets, centralized observability, deployment runbooks, and formal audit workflows.

## Why is this better than a dashboard?

A dashboard shows metrics. FailureLens IQ explains failure, connects evidence to root cause, finds repeated patterns, and turns the result into action for engineers and managers.

## How does certification mapping help?

It turns an experiment failure into a measurable learning path. Managers can see whether repeated failures point to DP-100, AI-102, DP-203, or PL-300 skill gaps.

## What would you build next?

Add Azure ML or MLflow ingestion, Entra ID auth, database-backed traces, team workspaces, observability dashboards, and richer report exports.
