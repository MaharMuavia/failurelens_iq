import asyncio
import pytest
import httpx
from fastapi.testclient import TestClient
from backend.api.main import create_app
from backend.core.config import settings

@pytest.fixture
def auth_disabled_app(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "false")
    monkeypatch.setattr(settings, "ENABLE_AUTH", False)
    return create_app()

@pytest.fixture
def auth_enabled_app(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("API_KEY", "secret-test-key")
    monkeypatch.setattr(settings, "ENABLE_AUTH", True)
    monkeypatch.setattr(settings, "API_KEY", "secret-test-key")
    return create_app()


@pytest.mark.anyio
async def test_sse_stream_auth_disabled(auth_disabled_app):
    transport = httpx.ASGITransport(app=auth_disabled_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream("GET", "/analysis/stream/EXP-1001") as response:
            assert response.status_code == 200


@pytest.mark.anyio
async def test_sse_stream_auth_enabled_rejects(auth_enabled_app):
    transport = httpx.ASGITransport(app=auth_enabled_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # stream analysis without headers should fail
        response = await client.get("/analysis/stream/EXP-1001")
        assert response.status_code == 401


@pytest.mark.anyio
async def test_sse_stream_auth_enabled_accepts(auth_enabled_app):
    transport = httpx.ASGITransport(app=auth_enabled_app)
    headers = {"X-API-Key": "secret-test-key"}
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream("GET", "/analysis/stream/EXP-1001", headers=headers) as response:
            assert response.status_code == 200
