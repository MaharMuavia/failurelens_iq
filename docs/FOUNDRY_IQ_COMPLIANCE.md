# Foundry IQ Compliance

For the Microsoft IQ requirement, FailureLens IQ implements Foundry IQ using Azure AI Search as the grounded retrieval layer for the agents.

The hackathon requires at least one Microsoft IQ layer. FailureLens IQ uses Foundry IQ because failed experiment analysis needs agentic retrieval over ML failure taxonomy, remediation playbooks, experiment logs, and Microsoft certification material.

Implementation proof:

- `IQ_PROVIDER=azure_foundry` activates `AzureFoundryIQProvider`.
- `AzureFoundryIQProvider` retrieves grounded knowledge through `GroundingAdapter`.
- `GroundingAdapter` uses Azure AI Search in production mode when credentials exist.
- Grounding references include citations, source types, confidence, retrieval system, and grounding mode.
- Azure OpenAI is optional and provides production executive summaries.
- Cosmos DB and Blob Storage are optional enterprise trace and artifact layers.

Agent outputs include citations, uncertainty, evidence, confidence, and human-review gates. The app exposes safe reasoning summaries and does not expose hidden chain-of-thought.
