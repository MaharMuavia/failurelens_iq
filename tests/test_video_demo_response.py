import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_video_demo_response_contains_narration_and_winning_points():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")
    payload = response.json()
    assert response.status_code == 200
    assert payload["video_demo_summary"]["best_screen_to_show"] == "Animated Agent Flow"
    assert len(payload["demo_narration"]) >= 6
    assert "Evidence-grounded diagnosis" in payload["winning_points"]
    assert payload["microsoft_iq_compliance"]["adapter_ready"] is True
