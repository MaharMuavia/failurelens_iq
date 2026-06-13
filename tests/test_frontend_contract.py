from pathlib import Path


def test_frontend_api_client_exists_and_declares_required_functions():
    client = Path("frontend/src/api/client.ts").read_text(encoding="utf-8")
    for name in [
        "getHealth",
        "getAgents",
        "listExperiments",
        "runDemo",
        "runAnalysis",
        "streamAnalysis",
        "searchKnowledge",
        "generateReport",
        "getLiveIQProof",
        "runLiveIQProof",
    ]:
        assert f"function {name}" in client
    assert "CONFIGURED_API_BASE" in client
    assert "buildUrl(path" in client


def test_use_analysis_is_not_only_mock_data():
    hook = Path("frontend/src/hooks/useAnalysis.ts").read_text(encoding="utf-8")
    assert "listExperiments()" in hook
    assert "runAnalysisWithOptions" in hook
    assert "Backend disconnected" not in hook
