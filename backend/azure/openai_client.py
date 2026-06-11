from __future__ import annotations

from typing import Any
import json

import httpx

from backend.azure.config import AzureConfig
from backend.core.config import settings
from backend.models.schemas import AgentContext


class AzureOpenAIClient:
    def __init__(self, config: AzureConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.enabled_integrations["azure_openai"]

    async def summarize(self, prompt: str) -> dict[str, object]:
        if not self.enabled:
            fallback = self._deterministic_summary_from_text(prompt)
            fallback["warning"] = "Azure OpenAI credentials are not configured; deterministic local summaries are used."
            return fallback
        response = await self._chat_completion(prompt)
        if not response["ok"]:
            fallback = self._deterministic_summary_from_text(prompt)
            fallback["warning"] = response["detail"]
            return fallback
        return {"used": True, "deployment": self.config.azure_openai_deployment, "summary": response["content"]}

    async def summarize_failure_report(self, ctx: AgentContext) -> dict[str, object]:
        if not self.enabled:
            return self._deterministic_summary(ctx)
        prompt = self._build_failure_report_prompt(ctx)
        response = await self._chat_completion(prompt)
        if not response["ok"]:
            fallback = self._deterministic_summary(ctx)
            fallback["warning"] = response["detail"]
            return fallback
        return {"used": True, "deployment": self.config.azure_openai_deployment, "summary": response["content"]}

    async def _chat_completion(self, prompt: str) -> dict[str, Any]:
        endpoint = self.config.azure_openai_endpoint.rstrip("/")
        deployment = self.config.azure_openai_deployment
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
        body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You summarize ML failure analysis for enterprise leaders. Provide concise reasoning summaries only; never reveal hidden chain of thought.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": settings.AZURE_OPENAI_TEMPERATURE,
            "max_tokens": settings.AZURE_OPENAI_MAX_TOKENS,
        }
        headers = {"api-key": self.config.azure_openai_api_key, "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=float(settings.REQUEST_TIMEOUT_SECONDS)) as client:
                response = await client.post(url, headers=headers, json=body)
        except httpx.HTTPError as exc:
            return {"ok": False, "detail": f"Azure OpenAI request failed: {exc}"}
        if response.status_code >= 400:
            return {"ok": False, "detail": f"Azure OpenAI failed with {response.status_code}: {response.text[:500]}"}
        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return {"ok": False, "detail": f"Azure OpenAI returned an unexpected response: {exc}"}
        return {"ok": True, "content": self._parse_summary_content(content)}

    def _build_failure_report_prompt(self, ctx: AgentContext) -> str:
        diagnosis = ctx.diagnosis.root_cause if ctx.diagnosis else "Diagnosis unavailable."
        category = ctx.classification.failure_category.value if ctx.classification else "Unknown"
        remediation = ctx.remediation.manager_note if ctx.remediation else "No remediation note generated."
        return (
            "Return compact JSON with keys executive_summary, risk_summary, next_best_action, confidence_caveat. "
            "Use only the fields below. Do not expose hidden chain-of-thought.\n\n"
            f"Experiment: {ctx.experiment.experiment_id}\n"
            f"Project: {ctx.experiment.project_name}\n"
            f"Observed failure: {ctx.experiment.failure_observation}\n"
            f"Failure category: {category}\n"
            f"Root cause: {diagnosis}\n"
            f"Overall confidence: {ctx.overall_confidence:.2f}\n"
            f"Human review required: {ctx.requires_human_review}\n"
            f"Manager note: {remediation}"
        )

    def _deterministic_summary(self, ctx: AgentContext) -> dict[str, object]:
        category = ctx.classification.failure_category.value if ctx.classification else "Unknown"
        root_cause = ctx.diagnosis.root_cause if ctx.diagnosis else "the root cause needs review"
        next_action = ctx.remediation.three_day_plan[0] if ctx.remediation else "Review the evidence packet before retraining."
        return {
            "used": False,
            "summary": {
                "executive_summary": f"{ctx.experiment.experiment_id} failed because {root_cause}",
                "risk_summary": f"The active failure category is {category}; confidence is {ctx.overall_confidence:.2f}.",
                "next_best_action": next_action,
                "confidence_caveat": ctx.human_review_reason or "Automated reasoning passed the current confidence gate; human review remains available.",
            },
            "warning": "Azure OpenAI credentials are not configured; deterministic local summary was used.",
        }

    def _deterministic_summary_from_text(self, prompt: str) -> dict[str, object]:
        return {
            "used": False,
            "summary": {
                "executive_summary": prompt[:220],
                "risk_summary": "Azure OpenAI was unavailable, so the local deterministic fallback was used.",
                "next_best_action": "Review the evidence packet and remediation plan.",
                "confidence_caveat": "No live Azure OpenAI summary was generated.",
            },
        }

    def _parse_summary_content(self, content: str) -> dict[str, object]:
        try:
            parsed = json.loads(content)
        except ValueError:
            return {
                "executive_summary": "Azure OpenAI returned a concise summary.",
                "risk_summary": "Review the raw summary for risk details.",
                "next_best_action": "Review the evidence packet and remediation plan.",
                "confidence_caveat": "Model response was plain text, so structured fields were safely backfilled.",
                "raw": content,
            }
        if not isinstance(parsed, dict):
            return {
                "executive_summary": "Azure OpenAI returned an unstructured summary.",
                "risk_summary": "Review the raw summary for risk details.",
                "next_best_action": "Review the evidence packet and remediation plan.",
                "confidence_caveat": "Model response was not an object, so structured fields were safely backfilled.",
                "raw": content,
            }
        return {
            "executive_summary": str(parsed.get("executive_summary") or parsed.get("summary") or ""),
            "risk_summary": str(parsed.get("risk_summary") or ""),
            "next_best_action": str(parsed.get("next_best_action") or ""),
            "confidence_caveat": str(parsed.get("confidence_caveat") or ""),
            **({"raw": content} if not all(parsed.get(k) for k in ["executive_summary", "risk_summary", "next_best_action", "confidence_caveat"]) else {}),
        }
