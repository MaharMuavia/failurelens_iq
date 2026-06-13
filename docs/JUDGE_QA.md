# Judge Q&A

## Why not a simple classifier?

A classifier can label a failure. FailureLens IQ separates planning, classification, root-cause analysis, historical memory, remediation, certification mapping, and manager synthesis so each step can expose evidence, uncertainty, confidence, and audit entries.

## Where are the agents?

The frontend Mission Control view shows seven agents in the animated flow. The backend also returns agent traces in `/demo/run`, `/analysis/run`, and `/analysis/stream/{experiment_id}`.

## What is Microsoft IQ here?

The selected IQ layer is Foundry IQ. The implemented path uses Azure AI Search for grounded retrieval and Azure OpenAI for live Azure reasoning when credentials are configured.

## What if Azure was blocked?

The demo remains runnable without Azure credentials. It reports `local_demo_fallback` or `foundry_adapter_ready`, and the Microsoft IQ panel shows the honest limitation. Use this line in the video: "Azure resource deployment was blocked by subscription policy, so this demo uses local grounding while keeping the Foundry IQ adapter path ready and visible."

## Does OpenAI count as Microsoft IQ?

No. OpenAI direct API does not replace Microsoft IQ. It is only a fallback reasoning provider. Live Microsoft IQ proof requires Azure AI Search and Azure OpenAI through the Foundry adapter path.

## How do you avoid hallucination?

Outputs are grounded in experiment data, local or Azure retrieval citations, structured reasoning summaries, confidence scores, uncertainty notes, and a human review gate. Hidden chain-of-thought is not exposed.

## What should judges click first?

Click `Run Judge Demo`. It runs the full multi-agent reasoning pipeline, fills the animated graph, loads the Microsoft IQ proof panel, and prepares the judge-ready report.

## Why is this enterprise?

It includes readiness checks, cost guards, optional API-key auth, security headers, rate limits, Azure adapter boundaries, optional Cosmos trace storage, optional Blob report upload, manager summaries, and certification-aligned remediation.

## What remains for production?

Configure live Azure AI Search, Azure OpenAI, Cosmos DB, Blob Storage, production auth, trusted CORS origins, monitoring, and a real tenant data ingestion flow.
