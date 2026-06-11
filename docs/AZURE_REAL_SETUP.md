# Azure Real Setup

## 1. Create Resource Group

Create a small demo resource group in the Azure portal, for example `rg-failurelens-demo`.

## 2. Create Azure AI Search

Create an Azure AI Search service. Use the Free tier for the hackathon demo if available.

## 3. Copy Search Endpoint And Key

Copy the Search endpoint and an admin key into your local `.env`.

## 4. Create Azure OpenAI Resource And Deployment

Create an Azure OpenAI resource and deploy a small model such as `gpt-4o-mini` if available.

## 5. Copy OpenAI Endpoint, Key, And Deployment

Copy `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT`.

## 6. Copy Environment Template

```powershell
copy .env.azure.example .env
```

Fill the real values manually. Do not commit `.env`.

## 7. Create Search Index

```powershell
python scripts/azure/check_azure_env.py
python scripts/azure/create_search_index.py
```

## 8. Seed Search Index

```powershell
python scripts/azure/seed_search_index.py
```

## 9. Test Query

```powershell
python scripts/azure/test_search_query.py
```

## 10. Start Backend

```powershell
uvicorn backend.api.main:app --reload --port 8000
```

## 11. Verify Health

```powershell
curl http://localhost:8000/health
```

Confirm `active_iq_provider` is `AzureFoundryIQProvider` and `microsoft_iq.azure_ai_search_configured` is `true`.

## 12. Verify Demo Run

```powershell
curl -X POST http://localhost:8000/demo/run
```

Confirm `grounding_summary.source_types` contains `azure_ai_search` and `azure_status.azure_ai_search_used` is `true`.
