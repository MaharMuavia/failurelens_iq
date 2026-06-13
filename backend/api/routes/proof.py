from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Request, Depends
from backend.core.config import settings
from backend.core.security import require_api_key
from backend.models.schemas import ExperimentLog
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


MICROSOFT_REASONING_PROVIDERS = {"azure_openai", "foundry_openai", "foundry_agent"}
FOUNDRY_REASONING_PROVIDERS = {"foundry_openai", "foundry_agent"}


def _foundry_or_azure_model_configured(config: Any, integrations: dict[str, bool]) -> bool:
    foundry_model_configured = bool(
        (config.FOUNDRY_PROJECT_ENDPOINT or config.FOUNDRY_OPENAI_BASE_URL)
        and config.FOUNDRY_API_KEY
        and config.FOUNDRY_MODEL_DEPLOYMENT
    )
    foundry_agent_configured = bool(
        config.FOUNDRY_PROJECT_ENDPOINT
        and config.FOUNDRY_AGENT_NAME
    )
    return foundry_model_configured or foundry_agent_configured or bool(integrations.get("azure_openai"))


def _provider_from_context(ctx: Any) -> tuple[bool, str]:
    used_llm = False
    provider = "deterministic_fallback"
    if ctx.diagnosis and ctx.diagnosis.reflection_notes:
        for note in ctx.diagnosis.reflection_notes:
            if "LLM Reasoning Provider: AzureOpenAI" in note:
                return True, "azure_openai"
            if "LLM Reasoning Provider: MicrosoftFoundryOpenAI" in note:
                return True, "foundry_openai"
            if "LLM Reasoning Provider: MicrosoftFoundryAgent" in note:
                return True, "foundry_agent"
            if "LLM Reasoning Provider: OpenAI" in note:
                return True, "openai"
    return used_llm, provider


def _proof_level(search_used: bool, microsoft_reasoning_used: bool) -> str:
    if search_used and microsoft_reasoning_used:
        return "live_azure_foundry"
    if microsoft_reasoning_used:
        return "foundry_model_live_without_search"
    if search_used:
        return "azure_search_live_with_local_reasoning"
    return "local_foundry_iq_adapter"

@router.get("/proof/live-iq")
async def get_live_iq_proof(request: Request) -> dict[str, Any]:
    app_state = request.app.state
    config = app_state.settings
    integrations = app_state.azure_config.enabled_integrations

    search_configured = bool(integrations.get("azure_ai_search"))
    foundry_model_configured = bool(
        (config.FOUNDRY_PROJECT_ENDPOINT or config.FOUNDRY_OPENAI_BASE_URL)
        and config.FOUNDRY_API_KEY
        and config.FOUNDRY_MODEL_DEPLOYMENT
    )
    foundry_agent_configured = bool(
        config.FOUNDRY_PROJECT_ENDPOINT
        and config.FOUNDRY_AGENT_NAME
    )
    model_live = foundry_model_configured or foundry_agent_configured or bool(integrations.get("azure_openai"))

    model_configured = _foundry_or_azure_model_configured(config, integrations)
    proof_level = "configuration_only"
    honest_limitation = (
        "Configuration status only. Run POST /proof/live-iq/run to verify whether Azure AI Search "
        "returns real grounding refs during an analysis."
    )

    return {
        "selected_iq_layer": "Foundry IQ",
        "proof_level": proof_level,
        "live_microsoft_iq": False,
        "is_live_backend": True,
        "is_live_microsoft_iq": False,
        "azure_ai_search_configured": search_configured,
        "azure_ai_search_used_this_run": False,
        "foundry_model_configured": model_configured,
        "foundry_model_used_this_run": False,
        "active_reasoning_provider": config.MODEL_PROVIDER,
        "active_grounding_provider": "azure_ai_search" if search_configured else "local_iq",
        "citations_count": 0,
        "grounding_refs": [],
        "source_types": [],
        "run_id": "",
        "trace_ids": [],
        "warnings": [honest_limitation],
        "warning": honest_limitation,
        "honest_limitation": honest_limitation
    }

@router.post("/proof/live-iq/run")
async def run_live_iq_proof(request: Request, _auth: Any = Depends(require_api_key)) -> dict[str, Any]:
    app_state = request.app.state
    config = app_state.settings
    integrations = app_state.azure_config.enabled_integrations

    # Fetch a default experiment to test the pipeline
    try:
        exp = await app_state.experiment_store.get_experiment("EXP-1001")
    except KeyError:
        # Construct a default mock experiment if EXP-1001 is missing
        exp = ExperimentLog(
            experiment_id="EXP-1001",
            team_id="demo-team",
            project_name="Credit Churn Predictor",
            role="ML Specialist",
            model_type="XGBoost Classifier",
            dataset_name="churn_data.csv",
            pipeline_stage="evaluation",
            target="churn",
            validation_strategy="holdout",
            class_balance="88/12",
            preprocessing_steps=["standard scaling"],
            feature_set=["f1", "f2"],
            metrics={"accuracy": 0.93, "minority_f1": 0.14},
            baseline_metrics={"accuracy": 0.95},
            failure_observation="Our churn model reached 93% accuracy, but minority class F1 dropped to 0.14.",
            outcome="failure",
            timestamp=datetime.now(timezone.utc)
        )

    # Run the orchestrator
    ctx = await app_state.orchestrator.run(exp)

    # Gather citation information from grounding refs
    refs = []
    refs.extend(await app_state.grounding_adapter.retrieve_experiment_context(exp.experiment_id))
    refs.extend(await app_state.grounding_adapter.retrieve_historical_failures(
        ctx.diagnosis.knowledge_gap if ctx.diagnosis else "ml failure", 
        top_k=5
    ))

    source_types = list(set(ref.source_type for ref in refs))
    citations = [ref.citation for ref in refs]
    
    search_configured = bool(integrations.get("azure_ai_search"))
    search_used = search_configured and "azure_ai_search" in source_types

    used_llm, provider = _provider_from_context(ctx)
    microsoft_reasoning_used = used_llm and provider in MICROSOFT_REASONING_PROVIDERS
    model_configured = _foundry_or_azure_model_configured(config, integrations)
    proof_level = _proof_level(search_used, microsoft_reasoning_used)

    if proof_level == "live_azure_foundry":
        honest_limitation = "Azure AI Search and Microsoft model reasoning completed successfully."
    elif proof_level == "foundry_model_live_without_search":
        honest_limitation = "Microsoft model reasoning worked, but grounding did not return Azure AI Search refs."
    elif proof_level == "azure_search_live_with_local_reasoning":
        honest_limitation = "Azure AI Search grounded retrieval completed, but model reasoning used local deterministic fallback."
    else:
        honest_limitation = "Local adapter mode. No live Azure AI Search grounding refs were returned for this run."

    # Extract all warnings from grounding adapter
    warnings = list(app_state.grounding_adapter.warnings)
    if not used_llm:
        warnings.append(f"Reasoning provider failed or fell back to deterministic reasoning: {provider}")
    if not search_used:
        warnings.append("Azure AI Search was not used for this run; live Microsoft IQ is false.")

    return {
        "selected_iq_layer": "Foundry IQ",
        "proof_level": proof_level,
        "live_microsoft_iq": search_used,
        "is_live_backend": True,
        "is_live_microsoft_iq": search_used,
        "azure_ai_search_configured": search_configured,
        "azure_ai_search_used_this_run": search_used,
        "foundry_model_configured": model_configured,
        "foundry_model_used_this_run": microsoft_reasoning_used,
        "active_reasoning_provider": provider,
        "active_grounding_provider": "azure_ai_search" if search_used else "local_iq",
        "citations_count": len(citations),
        "grounding_refs": citations,
        "source_types": source_types,
        "run_id": ctx.run_id,
        "trace_ids": [trace.trace_id for trace in ctx.agent_trace],
        "warnings": warnings,
        "warning": " ".join(warnings) if warnings else "",
        "honest_limitation": honest_limitation
    }
