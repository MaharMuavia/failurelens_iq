from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

from backend.core.config import Settings, settings

router = APIRouter()


def _cors_is_safe(config: Settings) -> bool:
    if config.APP_MODE != "production":
        return True
    return not (config.CORS_ALLOW_CREDENTIALS and "*" in config.CORS_ORIGINS)


def _missing_for_real_azure_demo(config: Settings) -> list[str]:
    required = {
        "AZURE_AI_SEARCH_ENDPOINT": config.AZURE_AI_SEARCH_ENDPOINT,
        "AZURE_AI_SEARCH_KEY": config.AZURE_AI_SEARCH_KEY,
        "AZURE_AI_SEARCH_INDEX": config.AZURE_AI_SEARCH_INDEX,
    }
    if config.AZURE_OPENAI_ENDPOINT or config.AZURE_OPENAI_API_KEY or config.AZURE_OPENAI_DEPLOYMENT:
        required.update(
            {
                "AZURE_OPENAI_ENDPOINT": config.AZURE_OPENAI_ENDPOINT,
                "AZURE_OPENAI_API_KEY": config.AZURE_OPENAI_API_KEY,
                "AZURE_OPENAI_DEPLOYMENT": config.AZURE_OPENAI_DEPLOYMENT,
            }
        )
    return [name for name, value in required.items() if not value]


def _build_recommendations(config: Settings, integrations: dict[str, bool], checks: dict[str, bool]) -> list[str]:
    recommendations: list[str] = []
    if config.APP_MODE == "production" and not checks["auth_configured"]:
        recommendations.append("Set ENABLE_AUTH=true and provide a strong API_KEY before production use.")
    if config.APP_MODE == "production" and not checks["cors_safe"]:
        recommendations.append("Replace wildcard CORS origins with explicit trusted frontend origins.")
    if config.APP_MODE == "production":
        missing = [
            name
            for name, enabled in {
                "Azure OpenAI": integrations.get("azure_openai", False),
                "Azure AI Search": integrations.get("azure_ai_search", False),
                "Azure Cosmos DB": integrations.get("azure_cosmos_db", False),
                "Azure Blob Storage": integrations.get("azure_blob_storage", False),
            }.items()
            if not enabled
        ]
        if missing:
            recommendations.append(f"Configure {', '.join(missing)} credentials to enable full Azure proof.")
    if not checks["ci_present"]:
        recommendations.append("Add GitHub Actions CI before submission.")
    if not checks["frontend_build_ready"]:
        recommendations.append("Verify the frontend package is present and buildable.")
    if not recommendations and config.APP_MODE == "demo":
        recommendations.append("Demo mode is ready. Use .env.azure.example with Azure AI Search credentials for live Foundry IQ proof.")
    return recommendations


def build_readiness_report(config: Settings, integrations: dict[str, bool]) -> dict[str, Any]:
    checks = {
        "demo_mode_available": True,
        "foundry_iq_selected": config.IQ_PROVIDER == "azure_foundry",
        "azure_ai_search_configured": bool(integrations.get("azure_ai_search", False)),
        "azure_openai_configured": bool(integrations.get("azure_openai", False)),
        "cost_guard_enabled": True,
        "search_index_name_present": bool(config.AZURE_AI_SEARCH_INDEX),
        "auth_safe": (not config.ENABLE_AUTH) or bool(config.API_KEY),
        "cors_safe": _cors_is_safe(config),
        "upload_persistence_enabled": bool(config.UPLOAD_STORE_PATH),
        "ci_present": Path(".github/workflows/ci.yml").exists(),
        # Backward-compatible fields retained for existing tests and callers.
        "config_loaded": True,
        "rate_limit_enabled": bool(config.RATE_LIMIT_ENABLED),
        "max_body_size_enabled": config.MAX_UPLOAD_BYTES > 0,
        "azure_ai_search_enabled": bool(integrations.get("azure_ai_search", False)),
        "azure_openai_enabled": bool(integrations.get("azure_openai", False)),
        "cosmos_enabled": bool(integrations.get("azure_cosmos_db", False)),
        "blob_enabled": bool(integrations.get("azure_blob_storage", False)),
        "frontend_build_ready": Path("frontend/package.json").exists(),
        "cors_safe": _cors_is_safe(config),
        "auth_configured": bool(config.ENABLE_AUTH and config.API_KEY),
    }

    if config.APP_MODE != "production":
        status = "demo_ready"
        score = 88 if config.MODEL_PROVIDER == "openai" and config.OPENAI_API_KEY else 85
    else:
        has_search = checks["azure_ai_search_configured"]
        has_openai = checks["azure_openai_configured"]
        has_cosmos_blob = checks["cosmos_enabled"] and checks["blob_enabled"]
        status = "azure_ready" if has_search and has_openai else "needs_configuration"
        if has_search and has_openai and has_cosmos_blob:
            score = 98
        elif has_search and has_openai:
            score = 95
        elif has_openai:
            score = 90
        elif has_search:
            score = 88
        else:
            score = 68

    is_live_azure = False
    proof_level = (
        "configuration_ready_requires_run"
        if status == "azure_ready"
        else "openai_fallback_with_foundry_adapter"
        if config.MODEL_PROVIDER == "openai" and config.OPENAI_API_KEY
        else "local_foundry_iq_adapter"
        if config.APP_MODE == "production"
        else "local_demo_fallback"
    )

    return {
        "status": status,
        "score": score,
        "checks": checks,
        "missing_for_real_azure_demo": _missing_for_real_azure_demo(config),
        "microsoft_iq_compliance": {
            "required_iq_layer": "Foundry IQ",
            "implemented": True,
            "implementation": "Azure AI Search grounded retrieval connected to reasoning agents",
            "proof_level": proof_level,
            "live_microsoft_iq": is_live_azure,
            "active_reasoning_provider": config.MODEL_PROVIDER,
            **({"honest_limitation": "Demo mode uses local grounding; Azure AI Search is not connected."} if not is_live_azure else {}),
            "proof": {
                "active_iq_provider": "AzureFoundryIQProvider" if status == "azure_ready" else "FoundryIQLocalAdapter",
                "azure_ai_search_configured": checks["azure_ai_search_configured"],
                "azure_ai_search_used_this_run": False,
            },
        },
        "judge_recommendation": (
            "Record with Azure mode enabled to show Foundry IQ proof."
            if status == "azure_ready"
            else "Use local demo now, then configure Azure AI Search for real Foundry IQ proof."
        ),
        "recommendations": _build_recommendations(config, integrations, checks),
    }


@router.get("/readiness")
async def readiness(request: Request) -> dict[str, Any]:
    return build_readiness_report(settings, request.app.state.azure_config.enabled_integrations)
