# Azure Integration

## Current Mode

FailureLens IQ runs in demo mode by default.

Demo mode:

- Uses `data/synthetic/*.json` for experiments and team context.
- Uses `knowledge/foundry_docs/*.md` for local grounding.
- Labels grounding refs as `local_demo_grounding`.
- Returns the message: "Demo mode: local grounding simulates Microsoft IQ retrieval."

## Adapter Boundary

Implemented files:

- `backend/azure/config.py`
- `backend/azure/grounding_adapter.py`
- `backend/azure/openai_client.py`
- `backend/azure/ai_search_client.py`
- `backend/azure/blob_client.py`
- `backend/azure/cosmos_client.py`

## Environment Detection

`GET /health` reports:

```json
{
  "enabled_integrations": {
    "local_iq": true,
    "azure_openai": false,
    "azure_ai_search": false,
    "azure_blob_storage": false,
    "azure_cosmos_db": false
  }
}
```

An Azure integration becomes `true` only when its required environment variables are present.

## Required Variables

- Azure OpenAI: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- Azure AI Search: `AZURE_AI_SEARCH_ENDPOINT`, `AZURE_AI_SEARCH_KEY`, `AZURE_AI_SEARCH_INDEX`
- Azure Blob Storage: `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_BLOB_CONTAINER`
- Azure Cosmos DB: `AZURE_COSMOS_ENDPOINT`, `AZURE_COSMOS_KEY`, `AZURE_COSMOS_DATABASE`, `AZURE_COSMOS_CONTAINER`

## Production Behavior

When `APP_MODE=production`, the grounding adapter checks configured Azure clients. If credentials are missing, it returns warnings instead of fake results.

This repository does not claim live Azure production behavior unless credentials are supplied and the relevant adapter reports enabled.
