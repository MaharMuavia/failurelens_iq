from __future__ import annotations

import json
import logging
from pydantic import BaseModel, Field
from typing import Any

from backend.azure.openai_client import AzureOpenAIClient
from backend.core.config import settings
from backend.models.schemas import ExperimentLog, ClassificationResult, RetrievalResult, PlannerContext
from backend.services.openai_client import OpenAIClient
from backend.services.foundry_openai_client import FoundryOpenAIClient
from backend.services.foundry_agent_client import FoundryAgentClient

logger = logging.getLogger(__name__)


class LLMReasoningResult(BaseModel):
    used_llm: bool = False
    provider: str = "deterministic_fallback"
    root_cause: str
    violated_assumption: str
    knowledge_gap: str
    evidence: list[str]
    counter_evidence: list[str]
    uncertainty: list[str]
    confidence: float
    recommended_next_action: str
    raw_summary: str
    warning: str | None = None
    reasoning_steps: dict[str, str] = Field(default_factory=dict)
    model: str | None = None


class LLMReasoningProvider:
    def __init__(
        self,
        azure_openai_client: AzureOpenAIClient,
        openai_client: OpenAIClient | None = None,
        foundry_openai_client: FoundryOpenAIClient | None = None,
        foundry_agent_client: FoundryAgentClient | None = None,
    ) -> None:
        self.azure_openai_client = azure_openai_client
        self.openai_client = openai_client or OpenAIClient()
        self.foundry_openai_client = foundry_openai_client
        self.foundry_agent_client = foundry_agent_client

    def _select_client(self) -> tuple[Any | None, str, str]:
        provider = settings.MODEL_PROVIDER
        if provider == "foundry_openai":
            return self.foundry_openai_client, "MicrosoftFoundryOpenAI", "Microsoft Foundry OpenAI"
        if provider == "foundry_agent":
            if self.foundry_agent_client and self.foundry_agent_client.enabled:
                try:
                    from azure.ai.projects import AIProjectClient
                    return self.foundry_agent_client, "MicrosoftFoundryAgent", "Microsoft Foundry Agent"
                except ImportError:
                    logger.warning("SDK auth is not configured: azure-ai-projects or azure-identity is not installed. Falling back to foundry_openai.")
                    return self.foundry_openai_client, "MicrosoftFoundryOpenAI", "Microsoft Foundry OpenAI"
            else:
                logger.warning("Foundry Agent client is not enabled. Falling back to foundry_openai.")
                return self.foundry_openai_client, "MicrosoftFoundryOpenAI", "Microsoft Foundry OpenAI"
        if provider == "azure_openai":
            return self.azure_openai_client, "AzureOpenAI", "Azure OpenAI"
        if provider == "openai":
            return self.openai_client, "OpenAI", "OpenAI fallback"
        return None, "deterministic_fallback", "local deterministic fallback"

    async def analyze_failure(
        self,
        experiment: ExperimentLog,
        classification: ClassificationResult | None,
        retrieval: RetrievalResult | None,
        planner_context: PlannerContext | None,
    ) -> LLMReasoningResult:
        client, provider_name, provider_label = self._select_client()
        if client is None or not client.enabled:
            return LLMReasoningResult(
                used_llm=False,
                provider="deterministic_fallback",
                root_cause="Insufficient evidence to determine root cause with required confidence.",
                violated_assumption="The available experiment record contains enough evidence for automated root-cause diagnosis.",
                knowledge_gap="Evidence collection and review readiness before automated learning recommendations.",
                evidence=[],
                counter_evidence=[],
                uncertainty=[f"No live {provider_label} connection available."],
                confidence=0.45,
                recommended_next_action="Enable Azure OpenAI or direct OpenAI fallback credentials for LLM-grounded reasoning.",
                raw_summary=f"{provider_label} credentials are not configured; falling back to deterministic reasoning.",
                warning=f"{provider_label} credentials are not configured; deterministic local fallbacks are used.",
            )

        system_prompt = (
            "You are the RootCauseAnalyzerAgent in FailureLens IQ. You are a senior MLOps and Azure AI reasoning agent. "
            "Analyze the failure details and output a structured JSON response. "
            "Your output MUST be a single, valid JSON object with the following keys and structure:\n"
            "{\n"
            '  "root_cause": "Detailed explanation of the root cause.",\n'
            '  "violated_assumption": "The core assumption that was violated.",\n'
            '  "knowledge_gap": "The training/concept gap for the team.",\n'
            '  "evidence": ["Evidence point 1", "Evidence point 2"],\n'
            '  "counter_evidence": ["Counter evidence 1", "Counter evidence 2"],\n'
            '  "uncertainty": ["Uncertainty point 1"],\n'
            '  "confidence": 0.85,\n'
            '  "recommended_next_action": "Recommended immediate action.",\n'
            '  "raw_summary": "A clean narrative summarizing the findings.",\n'
            '  "reasoning_steps": {\n'
            '    "evidence_check": "Detailed finding from evidence check step.",\n'
            '    "inference": "Detailed finding from inference step.",\n'
            '    "counter_evidence": "Detailed finding from checking counter evidence.",\n'
            '    "uncertainty_check": "Detailed finding from uncertainty assessment.",\n'
            '    "decision": "Detailed finding from decision/calibration step.",\n'
            '    "next_action": "Detailed finding regarding next action."\n'
            '  }\n'
            "}\n"
            "DO NOT add markdown formatting (like ```json) or any conversational text before or after the JSON."
        )

        # Build user prompt with safety guidelines (never send raw traces/secrets, only structured info)
        grounding_docs = []
        if retrieval and retrieval.hits:
            for hit in retrieval.hits:
                grounding_docs.append(f"- File: {hit.source_file}, Title: {hit.section_title}, Citation: {hit.citation}\nExcerpt: {hit.excerpt}")
        grounding_str = "\n\n".join(grounding_docs) or "No grounding documents retrieved."

        classification_str = "None"
        if classification:
            classification_str = f"Category: {classification.failure_category.value}, Confidence: {classification.confidence}"

        planner_str = "None"
        if planner_context:
            planner_str = f"Hypothesis Suspected Category: {planner_context.hypothesis.suspected_category.value}, Plan Dynamic Threshold: {planner_context.plan.dynamic_threshold}"

        user_prompt = (
            f"Please analyze the following failure:\n\n"
            f"Experiment ID: {experiment.experiment_id}\n"
            f"Project: {experiment.project_name}\n"
            f"Model Type: {experiment.model_type}\n"
            f"Validation Strategy: {experiment.validation_strategy}\n"
            f"Class Balance: {experiment.class_balance}\n"
            f"Metrics: {json.dumps(experiment.metrics)}\n"
            f"Baseline Metrics: {json.dumps(experiment.baseline_metrics)}\n"
            f"Drift Indicators: {json.dumps(experiment.drift_indicators)}\n"
            f"Data Quality Signals: {json.dumps(experiment.data_quality_signals)}\n"
            f"Suspected Leakage Columns: {json.dumps(experiment.suspected_leakage_columns)}\n"
            f"Failure Observation: {experiment.failure_observation}\n"
            f"Engineer Notes: {experiment.engineer_notes}\n\n"
            f"--- Classification ---\n"
            f"{classification_str}\n\n"
            f"--- Planner Context ---\n"
            f"{planner_str}\n\n"
            f"--- Grounding Knowledge (Taxonomy) ---\n"
            f"{grounding_str}\n\n"
            f"Analyze this data and return the JSON object."
        )

        response = await client.chat_completion_raw(system_prompt, user_prompt)
        
        # If agent auth failed because SDK auth not configured, fall back to foundry_openai
        if not response["ok"] and settings.MODEL_PROVIDER == "foundry_agent" and "SDK auth is not configured" in response.get("detail", ""):
            logger.warning("Foundry Agent call failed due to missing SDK auth. Falling back to foundry_openai client.")
            if self.foundry_openai_client and self.foundry_openai_client.enabled:
                response = await self.foundry_openai_client.chat_completion_raw(system_prompt, user_prompt)
                provider_name = "MicrosoftFoundryOpenAI"
                provider_label = "Microsoft Foundry OpenAI"

        if not response["ok"]:
            return LLMReasoningResult(
                used_llm=False,
                provider="deterministic_fallback",
                root_cause="Insufficient evidence to determine root cause with required confidence.",
                violated_assumption="The available experiment record contains enough evidence for automated root-cause diagnosis.",
                knowledge_gap="Evidence collection and review readiness before automated learning recommendations.",
                evidence=[],
                counter_evidence=[],
                uncertainty=[f"{provider_label} error: {response.get('detail', 'Unknown error')}"],
                confidence=0.45,
                recommended_next_action="Review API key or network setup.",
                raw_summary=f"{provider_label} call failed; falling back to deterministic reasoning.",
                warning=response.get("detail", f"{provider_label} call failed."),
            )

        try:
            content = response["content"].strip()
            # Clean possible markdown wrapping
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed = json.loads(content)
            
            # Map the model configuration for reasoning result
            model_val = None
            if provider_name in ("MicrosoftFoundryOpenAI", "MicrosoftFoundryAgent"):
                model_val = settings.FOUNDRY_MODEL_DEPLOYMENT
            elif provider_name == "AzureOpenAI":
                model_val = settings.AZURE_OPENAI_DEPLOYMENT
            elif provider_name == "OpenAI":
                model_val = settings.OPENAI_MODEL

            # Ensure keys exist or set defaults
            return LLMReasoningResult(
                used_llm=True,
                provider=provider_name,
                root_cause=parsed.get("root_cause") or "Root cause undetermined by LLM.",
                violated_assumption=parsed.get("violated_assumption") or "Assumption check was not formulated.",
                knowledge_gap=parsed.get("knowledge_gap") or "Knowledge gap was not formulated.",
                evidence=parsed.get("evidence") or [],
                counter_evidence=parsed.get("counter_evidence") or [],
                uncertainty=parsed.get("uncertainty") or [],
                confidence=float(parsed.get("confidence") if parsed.get("confidence") is not None else 0.8),
                recommended_next_action=parsed.get("recommended_next_action") or "Review details.",
                raw_summary=parsed.get("raw_summary") or parsed.get("root_cause") or "No raw summary.",
                reasoning_steps=parsed.get("reasoning_steps") or {},
                model=model_val
            )
        except Exception as exc:
            return LLMReasoningResult(
                used_llm=False,
                provider="deterministic_fallback",
                root_cause="Insufficient evidence to determine root cause with required confidence.",
                violated_assumption="The available experiment record contains enough evidence for automated root-cause diagnosis.",
                knowledge_gap="Evidence collection and review readiness before automated learning recommendations.",
                evidence=[],
                counter_evidence=[],
                uncertainty=[f"Failed to parse {provider_label} response: {exc}"],
                confidence=0.45,
                recommended_next_action="Review LLM output format.",
                raw_summary="Failed to parse LLM response; falling back to deterministic reasoning.",
                warning=f"Failed to parse {provider_label} response: {exc}",
            )

