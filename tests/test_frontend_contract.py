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
    ]:
        assert f"function {name}" in client
    assert 'import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"' in client


def test_use_analysis_is_not_only_mock_data():
    hook = Path("frontend/src/hooks/useAnalysis.ts").read_text(encoding="utf-8")
    assert "listExperiments()" in hook
    assert "runAnalysisWithOptions" in hook
    assert "Backend disconnected" not in hook
