# Azure Quota Blocker

This demo was developed under an Azure subscription that did not have TPM quota for chat-capable models. As a result:

- Live Azure OpenAI model deployment is not possible in this environment.
- The demo uses Foundry IQ Local Adapter Mode instead of live Azure AI Search.
- The code keeps Azure adapters and wiring for future enablement; no Azure credentials are required to run the demo locally.
# Azure Quota Blocker

This document details the real-world subscription constraints encountered during development and how they were resolved.

## Subscription Issue

- **Azure model deployment failed** because the subscription has 0 TPM quota for available chat models.
- Dependance on live Azure OpenAI for the demo was not possible.
- **Azure quota was 0**, so live Azure OpenAI deployment was blocked.

## Workaround

- We implemented a strong, honest **Foundry IQ Local Adapter Mode**.
- We added an optional **OpenAI API fallback** for live reasoning.
- Live Microsoft IQ is not claimed unless Azure AI Search is active.
- OpenAI fallback is used only for live reasoning, not as Microsoft IQ.
- Foundry IQ base architecture is implemented locally.
- The adapter can switch to Azure AI Search later.
