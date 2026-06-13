# Microsoft IQ Honest Compliance

FailureLens IQ follows strict honesty rules for Microsoft IQ claims.

- Do not claim live Microsoft IQ unless Azure AI Search and Azure OpenAI are both configured and used.
- The demo mode reports `local_foundry_iq_adapter` and `live_microsoft_iq=false`.
- OpenAI direct fallback may be used for reasoning, but is recorded separately as `OpenAI` provider.
# Microsoft IQ Honest Compliance

This project adheres to strict compliance and honesty guidelines regarding the usage of Microsoft Foundry IQ and Azure services.

## Core Rules

1. **No False Claims:** Live Microsoft IQ is not claimed unless Azure AI Search is active.
2. **Demo Mode:** Uses Foundry IQ Local Adapter Mode to mirror concepts.
3. **Azure Quota Blocked:** Azure OpenAI model deployment was blocked because model quota was 0.
4. **OpenAI Fallback:** Direct OpenAI calls are only used as fallback for agent reasoning, not as Microsoft IQ.
5. **Base Architecture:** The Foundry IQ base architecture (sources, index, retrieval, citations, and permission metadata) is fully implemented locally.
6. **Adapter Path:** The adapter can switch to Azure AI Search when credentials become available.
