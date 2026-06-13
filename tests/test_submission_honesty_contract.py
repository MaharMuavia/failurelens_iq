import httpx
import pytest

from backend.api.main import app


ANALYZE_PAYLOAD = {
    "experiment": {
        "experiment_id": "EXP-CONTRACT-1",
        "model": "RandomForestClassifier",
        "train_accuracy": 0.97,
        "validation_accuracy": 0.61,
        "test_accuracy": 0.59,
        "dataset_size": 2000,
        "feature_count": 120,
        "notes": "No cross-validation or feature selection was used.",
    }
}


@pytest.mark.anyio
async def test_api_analyze_uses_orchestrator(monkeypatch):
    calls = {"count": 0}
    original_run = app.state.orchestrator.run

    async def tracked_run(*args, **kwargs):
        calls["count"] += 1
        return await original_run(*args, **kwargs)

    monkeypatch.setattr(app.state.orchestrator, "run", tracked_run)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/analyze", json=ANALYZE_PAYLOAD)

    assert response.status_code == 200
    assert calls["count"] == 1
    payload = response.json()
    assert payload["proof_level"] in {
        "local_foundry_iq_adapter",
        "foundry_model_live_without_search",
        "azure_search_live_with_local_reasoning",
        "live_azure_foundry",
    }


@pytest.mark.anyio
async def test_no_live_iq_claim_without_search_refs():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/proof/live-iq")

    assert response.status_code == 200
    payload = response.json()
    assert payload["live_microsoft_iq"] is False
    assert payload["azure_ai_search_used_this_run"] is False
    assert payload["proof_level"] == "configuration_only"


@pytest.mark.anyio
async def test_proof_run_returns_trace_ids():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/proof/live-iq/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"]
    assert payload["trace_ids"]
    assert payload["live_microsoft_iq"] == payload["azure_ai_search_used_this_run"]


@pytest.mark.anyio
async def test_offline_mode_is_honest():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/proof/live-iq/run")

    assert response.status_code == 200
    payload = response.json()
    if not payload["azure_ai_search_used_this_run"]:
        assert payload["live_microsoft_iq"] is False
        assert payload["proof_level"] in {
            "local_foundry_iq_adapter",
            "foundry_model_live_without_search",
        }
        assert payload["warnings"]


@pytest.mark.anyio
async def test_prompt_analysis_outputs_evidence_uncertainty_confidence():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/prompt/analyze",
            json={
                "prompt": "RandomForestClassifier got 97% training accuracy but only 61% validation accuracy. No cross-validation was used.",
                "generate_report": False,
                "use_foundry_model": False,
            },
        )

    assert response.status_code == 200
    analysis = response.json()["analysis_result"]
    assert analysis["root_cause_analysis"]["evidence"]
    assert analysis["root_cause_analysis"]["uncertainty"]
    assert analysis["confidence_summary"]["overall_confidence"] > 0
