from pathlib import Path


def test_frontend_iq_panel_and_actions_exist():
    dashboard = Path("frontend/src/components/ManagerDashboard.tsx").read_text(encoding="utf-8")
    panel = Path("frontend/src/components/MicrosoftIQProofPanel.tsx").read_text(encoding="utf-8")
    hook = Path("frontend/src/hooks/useAnalysis.ts").read_text(encoding="utf-8")
    client = Path("frontend/src/api/client.ts").read_text(encoding="utf-8")
    assert "MicrosoftIQProofPanel" in dashboard
    assert "Foundry IQ Layer" in panel
    assert "Foundry IQ Local Adapter" in panel
    assert "Selected IQ Layer" in panel
    assert "Copy IQ Compliance Summary" in panel
    assert "CheckCostEstimate" not in dashboard
    assert "checkCostEstimate" in hook
    assert "checkAzureReadiness" in hook
    assert "copyIqComplianceSummary" in hook
    assert "getIQStatus" in hook
    assert "getCostEstimate" in client
    assert "getReadiness" in client
    assert "getIQStatus" in client
