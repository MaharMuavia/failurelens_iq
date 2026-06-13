# OpenAI Fallback Demo

When `MODEL_PROVIDER=openai` and `OPENAI_API_KEY` is provided, FailureLens IQ will use direct OpenAI API calls as a fallback reasoning provider only. This does NOT claim live Microsoft IQ. The OpenAI fallback is used strictly for live LLM reasoning when Azure OpenAI is unavailable.

Set environment variables to enable:

```
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

The demo keeps a clear honesty boundary in `/iq/status` and `/demo/run` outputs.
# OpenAI Fallback Demo

This document describes the optional OpenAI reasoning fallback provider.

## Configuration

To enable the fallback reasoning provider, set the following environment variables in `.env`:

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
MICROSOFT_IQ_MODE=foundry_local_adapter
```

## Compliance & Honesty

- **Demo mode** uses Foundry IQ Local Adapter Mode.
- **Live Microsoft IQ** is not claimed unless Azure AI Search is active.
- **Azure quota was 0**, so live Azure OpenAI deployment was blocked.
- **OpenAI fallback** is used only for live reasoning, not as Microsoft IQ.
- **Foundry IQ base architecture** is implemented locally.
- The adapter can switch to Azure AI Search later.
