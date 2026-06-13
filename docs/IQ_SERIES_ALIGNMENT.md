# IQ Series Alignment

This project implements an initial local alignment to Foundry IQ concepts: knowledge sources, retrieval, citations, permission metadata, and grounded reasoning agents. The adapter is intentionally simple and designed to be replaced by Azure AI Search for production deployments.
# IQ Series Alignment

FailureLens IQ aligns with the Microsoft Agents League hackathon track requirements for Reasoning Agents.

## Alignment & Honesty

- **Demo mode** uses Foundry IQ Local Adapter Mode.
- **Live Microsoft IQ** is not claimed unless Azure AI Search is active.
- **Azure quota was 0**, so live Azure OpenAI deployment was blocked.
- **OpenAI fallback** is used only for live reasoning, not as Microsoft IQ.
- **Foundry IQ base architecture** is implemented locally.
- **The adapter** can switch to Azure AI Search later.
