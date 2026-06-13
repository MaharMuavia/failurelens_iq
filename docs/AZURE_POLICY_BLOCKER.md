# Azure Policy Blocker

Some Azure subscriptions block resource creation in required regions or SKUs. FailureLens IQ remains runnable when that happens.

## Demo Behavior

- Local demo mode uses synthetic experiment history and local markdown grounding.
- Foundry IQ adapter paths remain implemented and credential-gated.
- Direct OpenAI can be used only as fallback reasoning.
- Direct OpenAI does not count as Microsoft IQ.

## Judge Language

If Azure is blocked, say:

> Azure resource deployment was blocked by subscription policy, so this demo uses local grounding while keeping the Foundry IQ adapter path ready and visible.

Do not say local demo fallback is live Azure IQ. The honest status is `local_demo_fallback` unless Azure AI Search and Azure OpenAI are configured and working.

## Verification

Use:

```powershell
curl http://localhost:8000/iq/status
curl http://localhost:8000/readiness
```
