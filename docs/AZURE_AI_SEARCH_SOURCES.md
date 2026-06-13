# Azure AI Search Grounding Integration

This document outlines how the six FailureLens IQ knowledge sources are indexed, seeded, and queried inside Azure AI Search.

## Search Index Schema

The search index contains fields mapping to both technical experiment features and compliance metadata:

```json
[
  {"name": "id", "type": "Edm.String", "key": true, "filterable": true, "retrievable": true},
  {"name": "title", "type": "Edm.String", "searchable": true, "retrievable": true},
  {"name": "content", "type": "Edm.String", "searchable": true, "retrievable": true},
  {"name": "source_type", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "source_id", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "citation", "type": "Edm.String", "retrievable": true},
  {"name": "url", "type": "Edm.String", "retrievable": true},
  {"name": "chunk_id", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "experiment_id", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "skill_domain", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "failure_category", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "permission_scope", "type": "Edm.String", "filterable": true, "retrievable": true},
  {"name": "tags", "type": "Collection(Edm.String)", "filterable": true, "retrievable": true}
]
```

- **`permission_scope`**: Used to gate documents (e.g. only matching `demo` files during testing).
- **`tags`**: Multivalued field used by agents to search for specific failure topics (such as `accuracy-trap` or `class-imbalance`).

---

## Seeding & Verification Scripts

 Seeding scripts are located in `scripts/azure/`:
 
 1. **`create_search_index.py`**: Initializes or updates the index schema in Azure.
 2. **`seed_search_index.py`**: Parses local `.md` and `.json` files, extracts metadata tags, chunks them, and uploads them to the index.
 3. **`test_search_query.py`**: Verifies retrieval by querying the index for terms like "class imbalance" and checks for citations.

### Seeding Execution

To seed the index on Azure:
```bash
# Setup credentials in .env first
python scripts/azure/create_search_index.py
python scripts/azure/seed_search_index.py
python scripts/azure/test_search_query.py
```

---

## How the Adapter Switches Between Modes

The project uses the `FoundryIQLocalAdapter` (or `AzureFoundryIQProvider` in production when credentials are fully configured).

- **Demo/Local Mode**: Reads the `.md` and `.json` files directly from `knowledge/foundry_iq_sources/` and simulates TF-IDF and metadata-aware search.
- **Azure Production Mode**: Calls the Azure AI Search REST API endpoint, searching the index and utilizing semantic scoring.

To transition to live Azure:
Configure `.env` with:
```env
APP_MODE=production
IQ_PROVIDER=azure_foundry
AZURE_AI_SEARCH_ENDPOINT=https://<your-service>.search.windows.net
AZURE_AI_SEARCH_KEY=<your-api-key>
AZURE_AI_SEARCH_INDEX=failurelens-iq-knowledge
```
