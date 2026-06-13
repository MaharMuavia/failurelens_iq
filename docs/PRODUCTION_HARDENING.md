# Production Hardening

FailureLens IQ is a DEMO-READY MVP WITH AZURE PRODUCTION ADAPTERS.

## Honest Azure Status

Demo mode uses a local Foundry IQ-compatible adapter. Live Microsoft IQ is only claimed when Azure AI Search grounding references are returned from a real configured Azure provider.

OpenAI direct API does not replace Microsoft IQ.

## Production Checklist

- Configure Azure AI Search endpoint and key.
- Configure Azure Blob Storage if report persistence is needed.
- Configure Cosmos DB if trace persistence is needed.
- Run proof checks before claiming live Microsoft IQ.
- Keep secrets in environment variables, never in source control.
