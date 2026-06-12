import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_run_includes_microsoft_iq_and_submission_readiness():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")

    payload = response.json()
    compliance = payload["microsoft_iq_compliance"]
    assert compliance["required_by_hackathon"] is True
    assert compliance["selected_iq_layer"] == "Foundry IQ"
    assert compliance["reasoning_trace_present"] is True
    assert compliance["uncertainty_present"] is True
    assert compliance["confidence_present"] is True
    assert "submission_readiness" in payload
    assert payload["submission_readiness"]["demo_video_ready"] is True


@pytest.mark.anyio
async def test_demo_run_includes_demo_mode_citations():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")

    payload = response.json()
    assert payload["grounding_summary"]["citations"]
    assert payload["microsoft_iq_compliance"]["citations_present"] is True
