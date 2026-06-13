from __future__ import annotations

import httpx
from typing import Any
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)


class FoundryOpenAIClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        deployment: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.deployment = deployment
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.api_key and self.deployment)

    async def chat_completion_raw(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """
        Sends a POST request to the Microsoft Foundry OpenAI-compatible chat completions endpoint.
        Returns a normalized dict response.
        """
        if not self.enabled:
            return {"ok": False, "detail": "Microsoft Foundry OpenAI client configuration is missing"}

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.deployment,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": max(settings.AZURE_OPENAI_MAX_TOKENS, 1800),
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout_seconds)) as client:
                response = await client.post(url, headers=headers, json=body)
        except httpx.HTTPError as exc:
            # Catching HTTP error without logging api_key
            logger.error("Foundry OpenAI client request failed due to HTTP connection error")
            return {"ok": False, "detail": f"Foundry OpenAI request failed: {exc}"}

        # Status code checks
        if response.status_code in (401, 403):
            logger.error("Foundry OpenAI client request failed: Authentication failure (%d)", response.status_code)
            return {"ok": False, "detail": f"Foundry OpenAI auth failure: status {response.status_code}"}
        
        if response.status_code == 404:
            logger.error("Foundry OpenAI client request failed: Endpoint or deployment not found (404)")
            return {"ok": False, "detail": "Foundry OpenAI endpoint or deployment not found (404)"}
            
        if response.status_code == 429:
            logger.error("Foundry OpenAI client request failed: Rate limit or quota exceeded (429)")
            return {"ok": False, "detail": "Foundry OpenAI rate limit or quota exceeded (429)"}

        if response.status_code >= 400:
            logger.error("Foundry OpenAI client request failed with server error: %d", response.status_code)
            return {"ok": False, "detail": f"Foundry OpenAI server error with status {response.status_code}: {response.text[:300]}"}

        # Non-JSON check
        try:
            payload = response.json()
        except Exception as exc:
            logger.error("Foundry OpenAI client response parsing failed: non-JSON response")
            return {"ok": False, "detail": f"Foundry OpenAI returned non-JSON response: {exc}"}

        # Missing fields checks
        try:
            choices = payload.get("choices")
            if not choices or not isinstance(choices, list):
                raise KeyError("choices field is missing or empty")
            message = choices[0].get("message")
            if not message or not isinstance(message, dict):
                raise KeyError("message field is missing in choices[0]")
            content = message.get("content")
            if content is None:
                raise KeyError("content field is missing in message")

            return {
                "ok": True,
                "provider": "MicrosoftFoundryOpenAI",
                "model": self.deployment,
                "content": content,
                "raw": payload
            }
        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Foundry OpenAI client response validation failed: %s", str(exc))
            return {"ok": False, "detail": f"Foundry OpenAI response format invalid: {exc}"}
