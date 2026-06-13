# OpenAI Fallback Provider

FailureLens IQ supports direct OpenAI as optional fallback reasoning.

## Enable

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
MICROSOFT_IQ_MODE=foundry_adapter_ready
```

The fallback is used only when `MODEL_PROVIDER=openai` and `OPENAI_API_KEY` exists.

## Truth Boundary

OpenAI direct API does not replace Microsoft IQ. It is only a fallback reasoning provider. The Microsoft IQ proof remains Azure AI Search plus Azure OpenAI through the Foundry adapter path.

## Output Safety

Prompts request structured JSON with evidence, uncertainty, confidence, and next action. The app exposes reasoning summaries only and does not expose hidden chain-of-thought.
