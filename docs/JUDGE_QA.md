# Judge Q&A

## Why agents?

FailureLens IQ separates the job into specialized reasoning agents: classification, root-cause analysis, historical memory, remediation coaching, certification evaluation, and final manager synthesis. That separation makes each step auditable and lets the app expose evidence, uncertainty, confidence, and review gates.

## Where is Microsoft IQ?

The selected IQ layer is Foundry IQ. In production mode, FailureLens IQ uses Azure AI Search as the grounded retrieval layer connected to the reasoning agents. The `/iq/status` endpoint and Microsoft IQ Proof panel show provider, proof level, source types, citations, and compliance status.

## What if Azure keys fail?

The local demo still works without Azure credentials. It uses a local knowledge index and synthetic experiment history, labels the result as `local_demo_fallback`, and clearly states that Azure AI Search is not live. The project does not fake Azure usage.

## How do you avoid hallucination?

The system grounds outputs in experiment data, local or Azure retrieval citations, structured reasoning traces, confidence scores, uncertainty notes, and a human review gate. Hidden chain-of-thought is not exposed; judges see safe summaries and audit entries.

## Why is this enterprise?

It includes readiness checks, cost guards, optional API-key auth, security headers, rate limits, Azure adapter boundaries, Cosmos trace storage, Blob report upload, manager summaries, and certification-aligned remediation.

## What remains for production?

Configure live Azure AI Search, Azure OpenAI, Cosmos DB, Blob Storage, production auth, trusted CORS origins, monitoring, and a real tenant data ingestion flow.

## How does certification mapping help?

Certification mapping turns a model failure into a measurable learning path. It connects root causes to Microsoft skill domains so managers can plan practice, coaching, and readiness checks instead of only fixing one model run.
