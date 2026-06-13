import httpx
import pytest
from backend.api.main import app

@pytest.mark.anyio
async def test_prompt_analyze_endpoint():
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
    assert "prompt_id" in res_data
    assert res_data["original_prompt"] == payload["prompt"]
    assert "generated_experiment" in res_data
    assert "analysis_result" in res_data
    assert "interactive_report" in res_data
    
    report_meta = res_data["interactive_report"]
    assert report_meta["generated"] is True
    assert report_meta["format"] == "html"
    assert "download_url" in report_meta
    assert "local_path" in report_meta
