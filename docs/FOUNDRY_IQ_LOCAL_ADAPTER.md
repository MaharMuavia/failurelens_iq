# Foundry IQ Local Adapter Mode

This repository implements a local, citation-based, permission-aware adapter that mirrors the base architecture of Microsoft Foundry IQ. It provides:

- Knowledge sources (markdown/json files)
- Local retrieval and relevance scoring
- Citation metadata and permission scopes
- Grounding context delivered to reasoning agents
- Adapter-ready interface to swap in Azure AI Search later

This mode is the default in demo runs to avoid depending on Azure quota.
# Foundry IQ Local Adapter Mode

FailureLens IQ includes a Foundry IQ-compatible local intelligence layer for judge demos where Azure model quota is unavailable.

## How it works

The local adapter mimics the base Foundry IQ architecture:
- **Knowledge sources** in `knowledge/foundry_iq_sources/` (e.g., failure taxonomy, playbooks, certification mapping)
- **Local knowledge base index** using TF-IDF and term-overlap scoring
- **Agentic retrieval** that pulls relevant sources with citations
- **Metadata and permission scopes** (e.g. `permission_scope: "demo"`)
- **Grounded reasoning context** passed to classifier, root-cause, coach, certification, and manager agents

## Honest Architecture Compliance

- **Demo mode** uses Foundry IQ Local Adapter Mode.
- **Live Microsoft IQ** is not claimed unless Azure AI Search is active.
- **Azure quota was 0**, so live Azure OpenAI deployment was blocked.
- **OpenAI fallback** is used only for live reasoning, not as Microsoft IQ.
- **Foundry IQ base architecture** is implemented locally.
- **The adapter** can switch to Azure AI Search later.
