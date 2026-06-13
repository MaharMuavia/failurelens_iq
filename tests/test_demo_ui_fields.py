import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_demo_run_includes_frontend_friendly_ui_fields():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")

    payload = response.json()

    assert payload["agent_flow"]
    assert [node["id"] for node in payload["agent_flow"]] == [
        "planner",
        "foundry_iq",
        "classifier",
        "root_cause",
        "historian",
        "coach",
        "certification",
        "manager",
        "judge_report",
    ]
    iq_node = payload["agent_flow"][1]
    assert iq_node["label"] == "Foundry IQ Layer"
    assert iq_node["foundry_iq_status"] in {
        "live_azure_foundry",
        "openai_fallback_with_foundry_adapter",
        "foundry_adapter_ready",
        "local_demo_fallback",
    }
    assert payload["metric_story"]["headline"] == "High accuracy hid minority-class failure"
    assert payload["metric_story"]["accuracy"] == pytest.approx(0.93)
    assert payload["metric_story"]["minority_f1"] == pytest.approx(0.14)
    assert payload["metric_story"]["roc_auc"] == pytest.approx(0.72)
    assert "learning memory system" in payload["ui_summary"]["judge_hook"]
