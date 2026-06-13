import httpx
import pytest
from backend.api.main import app

@pytest.mark.anyio
async def test_prompt_analysis_has_no_false_live_azure_verified_claim():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "prompt": "Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14. Find the root cause.",
            "team_id": "demo-team",
            "use_foundry_model": False,
            "generate_report": True
        }
        response = await client.post("/prompt/analyze", json=payload)
        
    assert response.status_code == 200
    res_data = response.json()
    
    # Assert no live claims unless Azure Search is used
    analysis = res_data["analysis_result"]
    compliance = analysis.get("microsoft_iq_compliance", {})
    
    assert compliance.get("live_microsoft_iq") is False
    assert "local" in compliance.get("foundry_iq_mode", "") or "local" in compliance.get("foundry_iq_adapter", "") or "local" in res_data["analysis_result"]["foundry_iq_layer"]["mode"]
