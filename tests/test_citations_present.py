import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_has_citations_and_agent_trace_citation_ids():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")

    payload = response.json()
    assert payload["iq_grounding_story"]["citations"]
    traces = payload["reasoning_timeline"]
    assert any(trace.get("grounding_citation_ids") for trace in traces)

