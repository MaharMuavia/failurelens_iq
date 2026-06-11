# Live Azure Demo

FailureLens IQ runs locally in demo mode without credentials. For a live Microsoft IQ / Azure AI Foundry demonstration, switch to production mode and configure only the Azure services you want to prove.

## Azure Resources Needed

- Azure AI Search service with an index for experiment and remediation knowledge.
- Azure OpenAI resource with a chat deployment.
- Azure Cosmos DB account, database, and container for reasoning traces.
- Azure Storage account and Blob container for report artifacts.

Each service is credential-gated. Missing credentials produce warnings instead of fake Azure results.

## Azure AI Search Index

Create an Azure AI Search index with these fields:

| Field | Type | Notes |
|---|---|---|
| `id` | `Edm.String` | Key field. |
| `title` | `Edm.String` | Searchable title. |
| `content` | `Edm.String` | Searchable chunk text. |
| `experiment_id` | `Edm.String` | Filterable experiment identifier. |
| `source_type` | `Edm.String` | Example: `experiment_log`, `playbook`, `assessment`. |
| `url` | `Edm.String` | Optional citation URL. |

Use semantic search with a semantic configuration named `default` when available. If semantic search is not enabled, FailureLens IQ automatically falls back to a simple Azure AI Search query.

## Environment Variables

Copy the sample file first:

```bash
cp .env.example .env
```

Set these values for a full live demo:

```bash
APP_MODE=production
IQ_PROVIDER=azure_foundry

AZURE_AI_SEARCH_ENDPOINT=https://<search-name>.search.windows.net
AZURE_AI_SEARCH_KEY=<admin-or-query-key>
AZURE_AI_SEARCH_INDEX=<index-name>

AZURE_OPENAI_ENDPOINT=https://<openai-name>.openai.azure.com
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=<chat-deployment-name>

AZURE_COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/
AZURE_COSMOS_KEY=<key>
AZURE_COSMOS_DATABASE=failurelens
AZURE_COSMOS_CONTAINER=reasoning_traces

AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_BLOB_CONTAINER=failurelens-iq
```

## Run And Verify

Start the API:

```bash
uvicorn backend.api.main:app --reload
```

Verify health:

```bash
curl http://localhost:8000/health
```

Expected proof points:

- `app_mode` is `production`.
- `active_iq_provider` is `AzureFoundryIQProvider`.
- `enabled_integrations.azure_ai_search` is `true` when AI Search credentials are set.

Run the judge demo:

```bash
curl -X POST http://localhost:8000/demo/run
```

Expected proof points:

- `grounding_summary.source_types` includes `azure_ai_search` when AI Search returns results.
- `grounding_summary.azure_services_used` lists the enabled Azure services used by the run.
- `trace_storage.stored` is `true` when Cosmos DB is configured and reachable.
- `azure_status.azure_openai_used` is `true` when Azure OpenAI generated the executive summary.
- `azure_status.blob_report_uploaded` is `true` when Blob Storage uploaded the markdown report.

## Judge Demo Script

1. Show `/health` and point out `active_iq_provider`.
2. Run `/demo/run` and show the multi-agent reasoning timeline.
3. Open `grounding_summary` and highlight Azure AI Search citations.
4. Open `trace_storage` and show Cosmos DB persistence status.
5. Open `report_artifact.blob_upload` and show the uploaded report URL or blob name.

