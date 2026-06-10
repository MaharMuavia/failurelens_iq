from __future__ import annotations

from backend.azure.config import AzureConfig


class AzureOpenAIClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_openai"]

    async def summarize(self, prompt: str) -> dict[str, object]:
        if not self.enabled:
            return {"used": False, "warning": "Azure OpenAI credentials are not configured; deterministic local summaries are used."}
        return {
            "used": False,
            "deployment": self.config.azure_openai_deployment,
            "warning": "Azure OpenAI adapter is configured; live model calls are intentionally disabled for offline test determinism.",
            "prompt_preview": prompt[:160],
        }
