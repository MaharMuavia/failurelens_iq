import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_run_returns_full_judge_report():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run")
    payload = response.json()
    for key in [
        "demo_title",
        "executive_summary",
        "agent_workflow",
        "failure_classification",
        "root_cause_analysis",
        "historical_memory",
        "remediation_plan",
        "certification_readiness",
        "reasoning_timeline",
        "grounding_summary",
        "confidence_summary",
        "manager_summary",
        "judge_notes",
        "video_demo_summary",
        "winning_points",
        "demo_narration",
    ]:
        assert key in payload
    assert payload["demo_title"] == "Customer churn model failed validation gate"
    assert payload["agent_workflow"]
    assert payload["reasoning_timeline"]


@pytest.mark.anyio
async def test_demo_run_includes_video_demo_fields():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")
    payload = response.json()
    assert payload["video_demo_summary"]["best_screen_to_show"] == "Frontend Judge Demo panel"
    assert payload["video_demo_summary"]["agent_count"] >= 1
    assert "Structured reasoning traces" in payload["winning_points"]
    assert len(payload["demo_narration"]) >= 6
