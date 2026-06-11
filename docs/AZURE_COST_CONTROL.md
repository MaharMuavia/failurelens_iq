# Azure Cost Control

Use Azure AI Search Free tier for the demo if available.

Use a small Azure OpenAI deployment such as `gpt-4o-mini` if available. FailureLens IQ keeps demo summaries short with:

- `AZURE_OPENAI_MAX_TOKENS=500`
- `AZURE_OPENAI_TEMPERATURE=0.2`
- `AZURE_MAX_SEARCH_TOP_K=5`
- `AZURE_MAX_DOCS_TO_INDEX=200`
- `AZURE_MAX_CHUNK_CHARS=1800`

Disable Cosmos and Blob unless needed:

```env
ENABLE_AZURE_TRACE_STORAGE=false
ENABLE_AZURE_REPORT_UPLOAD=false
```

Set an Azure budget alert before recording the demo. Delete the resource group after the demo if you do not need the resources.
