from __future__ import annotations

from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.core.security import require_api_key
from backend.core.config import settings

router = APIRouter()


def _reasoning_provider_from_context(ctx: Any) -> tuple[bool, str]:
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
    return False, "deterministic_fallback"


def _proof_level(search_used: bool, microsoft_reasoning_used: bool) -> str:
    if search_used and microsoft_reasoning_used:
        return "live_azure_foundry"
    if microsoft_reasoning_used:
        return "foundry_model_live_without_search"
    if search_used:
        return "azure_search_live_with_local_reasoning"
    return "local_foundry_iq_adapter"

@router.post("/report/{experiment_id}/generate")
async def generate_report(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    app_state = request.app.state
    try:
        exp = await app_state.experiment_store.get_experiment(experiment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ctx = await app_state.orchestrator.run(exp)
    path = app_state.report_service.generate(ctx)
    content = path.read_text(encoding="utf-8")
    blob = await app_state.grounding_adapter.blob_client.upload_report(experiment_id, content)
    refs = []
    refs.extend(await app_state.grounding_adapter.retrieve_experiment_context(experiment_id))
    refs.extend(await app_state.grounding_adapter.retrieve_historical_failures(
        ctx.diagnosis.knowledge_gap if ctx.diagnosis else "ml failure",
        top_k=5,
    ))
    source_types = sorted({ref.source_type for ref in refs})
    citations = [ref.citation for ref in refs if ref.citation]
    used_llm, provider = _reasoning_provider_from_context(ctx)
    microsoft_reasoning_used = used_llm and provider in {"azure_openai", "foundry_openai", "foundry_agent"}
    azure_search_used = "azure_ai_search" in source_types
    proof_level = _proof_level(azure_search_used, microsoft_reasoning_used)
    warnings = list(getattr(app_state.grounding_adapter, "warnings", []))
    if not azure_search_used:
        warnings.append("Azure AI Search was not used for this report run; live Microsoft IQ is false.")
    return {
        "id": f"REP-{experiment_id}",
        "experiment_id": experiment_id,
        "run_id": ctx.run_id,
        "path": str(path),
        "bytes": path.stat().st_size,
        "content": content,
        "blob_upload": blob,
        "active_reasoning_provider": provider,
        "active_grounding_provider": "azure_ai_search" if azure_search_used else "local_iq",
        "proof_level": proof_level,
        "live_microsoft_iq": azure_search_used,
        "azure_ai_search_configured": bool(app_state.azure_config.enabled_integrations.get("azure_ai_search")),
        "azure_ai_search_used_this_run": azure_search_used,
        "foundry_model_configured": bool(
            (settings.FOUNDRY_PROJECT_ENDPOINT or settings.FOUNDRY_OPENAI_BASE_URL)
            and settings.FOUNDRY_API_KEY
            and settings.FOUNDRY_MODEL_DEPLOYMENT
        ),
        "foundry_model_used_this_run": microsoft_reasoning_used,
        "citations": citations,
        "citations_count": len(citations),
        "source_types": source_types,
        "agent_trace_summary": [
            {
                "trace_id": trace.trace_id,
                "agent_name": trace.agent_name,
                "status": trace.status,
                "confidence_score": trace.confidence_score,
                "findings": trace.findings[:2],
            }
            for trace in ctx.agent_trace
        ],
        "root_cause": ctx.diagnosis.root_cause if ctx.diagnosis else "",
        "remediation_plan": ctx.remediation.model_dump(mode="json") if ctx.remediation else {},
        "certification_mapping": ctx.cert_mapping.model_dump(mode="json") if ctx.cert_mapping else {},
        "warnings": warnings,
        "honest_limitation": (
            "Live Microsoft IQ proof requires Azure AI Search refs in this report run."
            if not azure_search_used
            else "Azure AI Search returned refs for this report run."
        ),
    }

@router.get("/report/{experiment_id}")
async def get_report(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    # Sanitize path to prevent path traversal
    filename = f"{experiment_id}.md"
    # Ensure no path traversal components are present
    if "/" in experiment_id or "\\" in experiment_id or experiment_id == "..":
        raise HTTPException(status_code=400, detail="Invalid experiment_id.")
        
    path = Path("reports") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report has not been generated yet.")
    return {
        "experiment_id": experiment_id,
        "path": str(path),
        "content": path.read_text(encoding="utf-8")
    }
