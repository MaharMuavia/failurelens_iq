import httpx
import pytest
from backend.api.main import app

@pytest.mark.anyio
async def test_report_download_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # First, generate the report
        payload = {
            "prompt": "Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14. Find the root cause.",
            "team_id": "demo-team",
            "use_foundry_model": False,
            "generate_report": True
        }
        post_response = await client.post("/prompt/analyze", json=payload)
        assert post_response.status_code == 200
        run_id = post_response.json()["prompt_id"]
        
        # Test preview (without download=true)
        get_response = await client.get(f"/report/{run_id}/interactive")
        assert get_response.status_code == 200
        assert "text/html" in get_response.headers["content-type"]
        assert "<html" in get_response.text
        
        # Test download (with download=true)
        download_response = await client.get(f"/report/{run_id}/interactive?download=true")
        assert download_response.status_code == 200
        assert "content-disposition" in download_response.headers
        assert f"{run_id}.html" in download_response.headers["content-disposition"]
