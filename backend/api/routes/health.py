from __future__ import annotations

import time
from fastapi import APIRouter, Request
from backend.core.config import settings

router = APIRouter()

@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    app = request.app
    health_status = "ok"
    auth_misconfigured = False
    if settings.ENABLE_AUTH and not settings.API_KEY:
        auth_misconfigured = True
        health_status = "unhealthy"

    foundry_openai_configured = bool(hasattr(app.state, "foundry_openai_client") and app.state.foundry_openai_client.enabled)
    foundry_agent_configured = bool(hasattr(app.state, "foundry_agent_client") and app.state.foundry_agent_client.enabled)
    foundry_project_endpoint_configured = bool(settings.FOUNDRY_PROJECT_ENDPOINT)

    return {
        "status": health_status,
        "service": "FailureLens IQ API",
        "foundry_mode": settings.FOUNDRY_CALL_MODE,
        "credentials_configured": bool(settings.AZURE_AI_PROJECT_ENDPOINT and settings.AZURE_AI_API_KEY),
        "app_mode": settings.APP_MODE,
        "model_provider": settings.MODEL_PROVIDER,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "azure_openai_configured": app.state.azure_config.enabled_integrations["azure_openai"],
        "foundry_openai_configured": foundry_openai_configured,
        "foundry_project_endpoint_configured": foundry_project_endpoint_configured,
        "foundry_model_deployment": settings.FOUNDRY_MODEL_DEPLOYMENT,
        "foundry_agent_configured": foundry_agent_configured,
        "microsoft_iq_live": False,
        "foundry_adapter_ready": True,
        "azure_policy_blocker_documented": True,
        "active_iq_provider": type(app.state.iq_provider).__name__,
        "version": "1.0.0",
        "experiments_loaded": len(app.state.data_loader.experiments),
        "knowledge_chunks_indexed": len(app.state.knowledge_index.chunks),
        "enabled_integrations": app.state.azure_config.enabled_integrations,
        "demo_ready": True,
        "auth_misconfigured": auth_misconfigured,
        "startup_loaded": app.state.startup_loaded,
        "startup_duration_ms": app.state.startup_duration_ms,
        "microsoft_iq": {
            "selected_layer": "Foundry IQ",
            "provider": type(app.state.iq_provider).__name__,
            "proof_level": "configuration_ready_requires_run" if (
                settings.APP_MODE == "production"
                and app.state.azure_config.enabled_integrations["azure_ai_search"]
                and app.state.azure_config.enabled_integrations["azure_openai"]
            ) else "local_demo_fallback",
            "live_microsoft_iq": False,
            "azure_ai_search_configured": app.state.azure_config.enabled_integrations["azure_ai_search"],
            "azure_ai_search_used_this_run": False,
            "azure_openai_configured": app.state.azure_config.enabled_integrations["azure_openai"],
            "production_grounding_ready": (
                settings.APP_MODE == "production"
                and type(app.state.iq_provider).__name__ == "AzureFoundryIQProvider"
                and app.state.azure_config.enabled_integrations["azure_ai_search"]
            ),
        },
    }
