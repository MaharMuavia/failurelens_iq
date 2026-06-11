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

    return {
        "status": health_status,
        "app_mode": settings.APP_MODE,
        "active_iq_provider": type(app.state.iq_provider).__name__,
        "version": "1.0.0",
        "experiments_loaded": len(app.state.data_loader.experiments),
        "knowledge_chunks_indexed": len(app.state.knowledge_index.chunks),
        "enabled_integrations": app.state.azure_config.enabled_integrations,
        "demo_ready": True,
        "auth_misconfigured": auth_misconfigured,
        "startup_loaded": app.state.startup_loaded,
        "startup_duration_ms": app.state.startup_duration_ms,
    }
