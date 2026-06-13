# Security Model

FailureLens IQ keeps secrets outside source control and uses environment variables for credentials.

Real Azure calls are enabled only when credentials are provided.

Demo mode does not require secrets and uses a local Foundry IQ-compatible adapter.
