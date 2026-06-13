from __future__ import annotations

import httpx
from typing import Any
from backend.core.config import settings


class OpenAIClient:
    """Credential-gated direct OpenAI fallback for reasoning only."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self._model = model or settings.OPENAI_MODEL

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self._model)

    @property
    def model(self) -> str:
        return self._model

    async def chat_completion_raw(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "detail": "OpenAI API key or model not configured"}

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": min(settings.AZURE_OPENAI_MAX_TOKENS, 700),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=float(settings.REQUEST_TIMEOUT_SECONDS)) as client:
                response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        except httpx.HTTPError as exc:
            return {"ok": False, "detail": f"OpenAI fallback request failed: {exc}"}

        if response.status_code >= 400:
            return {"ok": False, "detail": f"OpenAI fallback failed with {response.status_code}: {response.text[:300]}"}

        try:
            payload = response.json()
            message = payload.get("choices", [])[0].get("message", {})
            content = message.get("content") or message.get("text") or ""
            return {"ok": True, "provider": "OpenAI", "model": self.model, "content": content}
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return {"ok": False, "detail": f"OpenAI fallback returned an unexpected response: {exc}"}
