from pathlib import Path


def test_frontend_iq_panel_and_actions_exist():
    dashboard = Path("frontend/src/components/ManagerDashboard.tsx").read_text(encoding="utf-8")
    hook = Path("frontend/src/hooks/useAnalysis.ts").read_text(encoding="utf-8")
    client = Path("frontend/src/api/client.ts").read_text(encoding="utf-8")
    assert "Microsoft IQ / Foundry Proof" in dashboard
    assert "Selected IQ Layer" in dashboard
    assert "CheckCostEstimate" not in dashboard
    assert "checkCostEstimate" in hook
    assert "checkAzureReadiness" in hook
    assert "copyIqComplianceSummary" in hook
    assert "getCostEstimate" in client
    assert "getReadiness" in client
