import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_agents_endpoint_returns_six_judge_facing_agents():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/agents")
    agents = response.json()
    names = {agent["name"] for agent in agents}
    assert len(agents) >= 6
    assert {
        "FailureClassifierAgent",
        "RootCauseAnalyzerAgent",
        "ExperimentHistorianAgent",
        "PrescriptiveCoachAgent",
        "CertificationEvaluatorAgent",
        "IntegrationManagerAgent",
    }.issubset(names)
    for agent in agents:
        assert {"name", "role", "judging_purpose", "input", "output", "trace_fields"}.issubset(agent)
