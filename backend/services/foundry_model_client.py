from __future__ import annotations

import os
from openai import OpenAI
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FoundryModelClient:
    """
    Client for calling deployed Azure Foundry models directly using the OpenAI-compatible client pattern.
    """

    def __init__(self) -> None:
        self.endpoint = settings.AZURE_AI_PROJECT_ENDPOINT
        self.api_key = settings.AZURE_AI_API_KEY
        self.deployment_name = settings.AZURE_AI_MODEL_DEPLOYMENT_NAME

    async def call_model(self, system_prompt: str, user_prompt: str) -> str:
        """
        Calls the deployed model and returns the raw text response.
        If credentials are not configured, raises ValueError.
        """
        if not self.endpoint:
            raise ValueError(
                "AZURE_AI_PROJECT_ENDPOINT is not configured. "
                "Please configure it in your .env file or set FOUNDRY_CALL_MODE=mock."
            )
        if not self.api_key:
            raise ValueError(
                "AZURE_AI_API_KEY is not configured. "
                "Please configure it in your .env file or set FOUNDRY_CALL_MODE=mock."
            )

        # Standardise base URL to end with /openai/v1
        base_url = self.endpoint.rstrip("/")
        if not base_url.endswith("/openai/v1"):
            base_url = f"{base_url}/openai/v1"

        logger.info("Calling deployed model: %s at %s", self.deployment_name, base_url)

        try:
            # We use standard OpenAI client mapping to Azure AI Foundry OpenAI-compatible endpoint
            client = OpenAI(
                base_url=base_url,
                api_key=self.api_key,
            )
            
            # Since OpenAI call might be synchronous, we can run it in an executor or call it directly
            # For simplicity and robustness:
            response = client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            logger.error("Error calling Azure Foundry model endpoint: %s", str(e))
            raise RuntimeError(f"Azure Foundry model call failed: {e}") from e
