import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_run_includes_runtime_checks_and_azure_status():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run")
    payload = response.json()
    assert payload["demo_runtime_checks"]["agents_completed"] >= 6
    assert payload["demo_runtime_checks"]["reasoning_steps"] >= 10
    assert payload["demo_runtime_checks"]["grounding_refs"] >= 1
    assert payload["demo_runtime_checks"]["trace_storage_attempted"] is True
    assert payload["azure_status"]["active_provider"] in {"LocalIQProvider", "AzureFoundryIQProvider"}
    assert payload["azure_status"]["azure_ai_search_used"] is False
    assert payload["repo_readiness"]["demo_mode_runs_without_credentials"] is True
    assert len(payload["judge_talk_track"]) == 5
