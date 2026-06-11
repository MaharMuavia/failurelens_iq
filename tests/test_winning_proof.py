import pytest
import httpx
from backend.api.main import app

@pytest.mark.anyio
async def test_demo_endpoint_includes_winning_demo_proof():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")
    assert response.status_code == 200
    payload = response.json()
    
    # Assert winning_demo_proof is returned and has correct fields
    assert "winning_demo_proof" in payload
    proof = payload["winning_demo_proof"]
    assert "core_agent_llm_reasoning" in proof
    assert proof["microsoft_iq_layer"] == "Foundry IQ"
    assert "live_azure_grounding" in proof
    assert "reasoning_trace_steps" in proof
    assert proof["confidence_gate_used"] is True
    assert "human_review_gate_used" in proof
    assert proof["frontend_ready"] is True
    
    # Assert judge_script exists and is a non-empty list of narration lines
    assert "judge_script" in payload
    assert isinstance(payload["judge_script"], list)
    assert len(payload["judge_script"]) > 0
    assert any("Foundry IQ" in line for line in payload["judge_script"])
