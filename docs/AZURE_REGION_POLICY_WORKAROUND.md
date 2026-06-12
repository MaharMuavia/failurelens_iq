# Azure Region Policy Workaround

Some Azure subscriptions block specific regions or resource providers with `RequestDisallowedByAzure`. This is a subscription or tenant policy issue, not a FailureLens IQ code failure.

Try these regions first:

- East US
- East US 2
- West Europe
- North Europe
- UAE North
- Qatar Central

If Azure AI Search cannot be created, use the demo fallback and clearly explain the live Azure path: production mode connects the same grounding adapter to Azure AI Search, Azure OpenAI, Cosmos DB, and Blob Storage when credentials are available.

Do not fake Azure usage. Keep `/iq/status` honest: demo fallback should say Azure AI Search is not live, and live Azure proof should only appear when Azure AI Search is configured and used.
