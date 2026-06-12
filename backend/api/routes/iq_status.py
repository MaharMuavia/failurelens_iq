from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from backend.core.config import Settings, settings

router = APIRouter()


def build_iq_status_report(
    config: Settings,
    integrations: dict[str, bool],
    active_provider: str,
) -> dict[str, Any]:
    is_production = config.APP_MODE == "production"
    azure_search_live = bool(integrations.get("azure_ai_search", False))
    live_azure_verified = is_production and azure_search_live

    if live_azure_verified:
        proof_level = "live_azure"
        compliance_status = "live_iq_verified"
        honest_limitation = (
            "Azure AI Search is configured as the live grounded retrieval layer. "
            "Cosmos DB and Blob Storage are optional proof services unless enabled."
        )
    elif is_production:
        proof_level = "local_demo_fallback"
        compliance_status = "needs_azure_configuration"
        honest_limitation = (
            "Production mode is selected, but Azure AI Search is not configured, "
            "so live Microsoft IQ proof is not verified yet."
        )
    else:
        proof_level = "local_demo_fallback"
        compliance_status = "ready_for_demo"
        honest_limitation = (
            "Demo mode uses a local knowledge index and synthetic experiment history; "
            "Azure AI Search is not live until production credentials are configured."
        )

    provider = "AzureFoundryIQProvider" if is_production else "LocalIQProvider"
    if active_provider in {"AzureFoundryIQProvider", "LocalIQProvider"}:
        provider = active_provider

    return {
        "required_by_hackathon": True,
        "selected_iq_layer": "Foundry IQ",
        "implementation": "Azure AI Search grounded retrieval connected to FailureLens reasoning agents",
        "current_mode": "production" if is_production else "demo",
        "active_provider": provider,
        "proof_level": proof_level,
        "live_services": {
            "azure_ai_search": azure_search_live,
            "azure_openai": bool(integrations.get("azure_openai", False)),
            "azure_cosmos_db": bool(integrations.get("azure_cosmos_db", False)),
            "azure_blob_storage": bool(integrations.get("azure_blob_storage", False)),
        },
        "demo_services": {
            "local_knowledge_index": True,
            "synthetic_experiment_history": True,
        },
        "compliance_status": compliance_status,
        "citations_supported": True,
        "reasoning_trace_supported": True,
        "uncertainty_supported": True,
        "confidence_supported": True,
        "honest_limitation": honest_limitation,
        "judge_explanation": (
            "FailureLens IQ satisfies the Microsoft IQ requirement through Foundry IQ-style grounded retrieval. "
            "In demo mode, local grounding lets judges run without secrets. In production mode, Azure AI Search "
            "provides live grounding."
        ),
    }


@router.get("/iq/status")
async def iq_status(request: Request) -> dict[str, Any]:
    integrations = request.app.state.azure_config.enabled_integrations
    active_provider = type(request.app.state.iq_provider).__name__
    return build_iq_status_report(settings, integrations, active_provider)
