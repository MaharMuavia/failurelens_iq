# Microsoft AI Foundry Credentials Setup

This document outlines the steps to configure and run FailureLens IQ with the OpenAI-compatible Microsoft Foundry endpoint and optional Foundry Agent connection.

## Local Environment Configuration

To run FailureLens IQ in production-ready mode using Microsoft Foundry model reasoning, create or update a `.env` file in the root directory of the project.

> [!WARNING]
> Do NOT commit your `.env` file to git. It is ignored by `.gitignore` to prevent accidental credential leaks.

### `.env` Setup Example

Copy the following settings to your `.env` file and replace the placeholder credentials with your actual keys:

```env
APP_MODE=production
IQ_PROVIDER=azure_foundry
MODEL_PROVIDER=foundry_openai

# Microsoft Foundry API Configurations
FOUNDRY_PROJECT_ENDPOINT=https://maviakhan6622-2791-resource.services.ai.azure.com/api/projects/maviakhan6622-2791
FOUNDRY_OPENAI_BASE_URL=https://maviakhan6622-2791-resource.services.ai.azure.com/openai/v1
FOUNDRY_API_KEY=PASTE_KEY_HERE
FOUNDRY_MODEL_DEPLOYMENT=grok-4-20-reasoning
FOUNDRY_AGENT_NAME=FailureLens1
FOUNDRY_AGENT_VERSION=1
```

---

## Security Warnings

> [!CAUTION]
> **Do Not Commit Keys**: Never commit your `.env` file or write hardcoded secrets directly into your codebase. If you accidentally commit keys, rotate them immediately.
> 
> **Enterprise Production Security**: In enterprise production deployments, do not use flat `.env` files. Retrieve secrets dynamically from Azure Key Vault.

---

## Model Reasoning vs. Grounding

> [!IMPORTANT]
> **Foundry Model Reasoning is not the same as live Foundry IQ Grounding**:
> - **Model Reasoning** uses the Grok model hosted in Microsoft Foundry through the OpenAI-compatible `/openai/v1` endpoint to structure predictions and diagnose error logs.
> - **Foundry IQ Grounding** uses search indexes (e.g. Azure AI Search) to retrieve relevant documentation and playbooks.
> 
> The system operates honestly: if Azure AI Search credentials are not configured, it falls back to TF-IDF local knowledge indexing and alerts the user that live grounding is not active, even when model reasoning is live.
