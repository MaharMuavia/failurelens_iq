import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_trace_timeline_returns_agent_events_after_demo_run():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        demo = await client.post("/demo/run?force_refresh=true")
        run_id = demo.json()["run_id"]
        response = await client.get(f"/trace/{run_id}")
    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "completed"
    assert payload["timeline"]
    assert "agent_name" in payload["timeline"][0]
