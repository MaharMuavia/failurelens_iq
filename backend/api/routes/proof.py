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

    if search_configured and model_live:
        proof_level = "live_azure_foundry"
        honest_limitation = "Azure AI Search is configured and used for live grounded retrieval."
    elif model_live:
        proof_level = "foundry_model_live_without_search"
        honest_limitation = "Microsoft Foundry/Azure model reasoning is configured, but grounding uses the local adapter."
    elif search_configured:
        proof_level = "local_foundry_iq_adapter"
        honest_limitation = "Azure AI Search is configured, but reasoning is running in local/deterministic mode."
    else:
        proof_level = "offline_mock_preview"
        honest_limitation = "Offline mock mode. No live Azure OpenAI or Azure AI Search connection exists."

    return {
        "selected_iq_layer": "Foundry IQ",
        "proof_level": proof_level,
        "live_microsoft_iq": search_configured,
        "azure_ai_search_configured": search_configured,
        "azure_ai_search_used_this_run": False,
        "foundry_model_configured": foundry_model_configured or foundry_agent_configured,
        "foundry_model_used_this_run": False,
        "active_reasoning_provider": config.MODEL_PROVIDER,
        "active_grounding_provider": "azure_ai_search" if search_configured else "local_iq",
        "citations_count": 0,
        "grounding_refs": [],
        "source_types": [],
        "run_id": "",
        "trace_ids": [],
        "warnings": [],
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

    # Check which reasoning provider was actually used
    used_llm = False
    provider = "deterministic_fallback"
    if ctx.diagnosis and ctx.diagnosis.reflection_notes:
        for note in ctx.diagnosis.reflection_notes:
            if "LLM Reasoning Provider: AzureOpenAI" in note:
                used_llm = True
                provider = "azure_openai"
                break
            elif "LLM Reasoning Provider: MicrosoftFoundryOpenAI" in note:
                used_llm = True
                provider = "foundry_openai"
                break
            elif "LLM Reasoning Provider: MicrosoftFoundryAgent" in note:
                used_llm = True
                provider = "foundry_agent"
                break
            elif "LLM Reasoning Provider: OpenAI" in note:
                used_llm = True
                provider = "openai"
                break

    foundry_model_configured = bool(
        (config.FOUNDRY_PROJECT_ENDPOINT or config.FOUNDRY_OPENAI_BASE_URL)
        and config.FOUNDRY_API_KEY
        and config.FOUNDRY_MODEL_DEPLOYMENT
    )
    foundry_agent_configured = bool(
        config.FOUNDRY_PROJECT_ENDPOINT
        and config.FOUNDRY_AGENT_NAME
    )
    model_live = used_llm and provider in ("azure_openai", "foundry_openai", "foundry_agent")

    if search_used and model_live:
        proof_level = "live_azure_foundry"
        honest_limitation = "Azure AI Search and Microsoft model reasoning completed successfully."
    elif model_live:
        proof_level = "foundry_model_live_without_search"
        honest_limitation = "Microsoft model reasoning worked, but grounding fell back to local memory."
    elif search_used:
        proof_level = "local_foundry_iq_adapter"
        honest_limitation = "Azure AI Search grounded retrieval completed, but model reasoning used local fallback."
    else:
        proof_level = "offline_mock_preview"
        honest_limitation = "Reasoning and grounding both fell back to local simulation."

    # Extract all warnings from grounding adapter
    warnings = list(app_state.grounding_adapter.warnings)
    if not used_llm:
        warnings.append(f"Reasoning provider failed or fell back to deterministic reasoning: {provider}")

    return {
        "selected_iq_layer": "Foundry IQ",
        "proof_level": proof_level,
        "live_microsoft_iq": search_used,
        "azure_ai_search_configured": search_configured,
        "azure_ai_search_used_this_run": search_used,
        "foundry_model_configured": foundry_model_configured or foundry_agent_configured,
        "foundry_model_used_this_run": used_llm and provider in ("foundry_openai", "foundry_agent"),
        "active_reasoning_provider": provider,
        "active_grounding_provider": "azure_ai_search" if search_used else "local_iq",
        "citations_count": len(citations),
        "grounding_refs": citations,
        "source_types": source_types,
        "run_id": ctx.run_id,
        "trace_ids": [trace.trace_id for trace in ctx.agent_trace],
        "warnings": warnings,
        "honest_limitation": honest_limitation
    }
