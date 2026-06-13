import httpx
import pytest

from backend.api.main import app
from backend.api.routes.readiness import build_readiness_report
from backend.core.config import Settings


@pytest.mark.anyio
async def test_demo_readiness_endpoint_works(monkeypatch):
    from backend.core.config import settings
    from backend.azure.config import AzureConfig
    from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

    orig_mode = settings.APP_MODE
    orig_config = app.state.azure_config
    orig_provider = app.state.iq_provider

    monkeypatch.setattr(settings, "APP_MODE", "demo")
    app.state.azure_config = AzureConfig(app_mode="demo")
    app.state.iq_provider = FoundryIQLocalAdapter()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/readiness")
        payload = response.json()
        assert response.status_code == 200
        assert payload["status"] == "demo_ready"
        assert payload["score"] == 85
        assert payload["checks"]["rate_limit_enabled"] is True
        assert payload["checks"]["upload_persistence_enabled"] is True
    finally:
        monkeypatch.setattr(settings, "APP_MODE", orig_mode)
        app.state.azure_config = orig_config
        app.state.iq_provider = orig_provider


def test_production_missing_auth_and_azure_gives_recommendations():
    config = Settings(
        APP_MODE="production",
        IQ_PROVIDER="azure_foundry",
        ENABLE_AUTH=False,
        API_KEY="",
        CORS_ORIGINS=["https://failurelens.example.com"],
    )
    report = build_readiness_report(
        config,
        {
            "local_iq": True,
            "azure_openai": False,
            "azure_ai_search": False,
            "azure_blob_storage": False,
            "azure_cosmos_db": False,
        },
    )
    assert report["status"] == "needs_configuration"
    assert report["checks"]["auth_configured"] is False
    assert report["checks"]["azure_openai_enabled"] is False
    assert any("API_KEY" in item for item in report["recommendations"])
    assert any("Azure OpenAI" in item for item in report["recommendations"])
