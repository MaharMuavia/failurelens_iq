import pytest
from pathlib import Path
from backend.services.interactive_report_service import InteractiveReportService
from backend.services.prompt_experiment_builder import PromptExperimentBuilder
from backend.api.main import app

@pytest.mark.anyio
async def test_interactive_report_generation():
    # Setup context using actual orchestrator
    app_state = app.state
    builder = PromptExperimentBuilder()
    prompt = "Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14."
    exp, extract_meta = await builder.build(prompt)
    ctx = await app_state.orchestrator.run(exp)
    
    # Mock analysis result (similar to demo response)
    from backend.api.routes.prompt_analysis import analyze_prompt
    import httpx
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/prompt/analyze", json={
            "prompt": prompt,
            "team_id": "demo-team",
            "use_foundry_model": False,
            "generate_report": False
        })
    assert response.status_code == 200
    res_json = response.json()
    analysis_result = res_json["analysis_result"]
    
    report_service = InteractiveReportService()
    html_content = report_service.generate_html(ctx, prompt, extract_meta, analysis_result)
    
    # Verify key sections exist
    assert "FailureLens" in html_content
    assert "Original Prompt" in html_content
    assert "Failure Diagnosis" in html_content
    assert "Agent Workflow" in html_content
    assert "Grounded Evidence" in html_content
    assert "Remediation &amp; Certs" in html_content or "Remediation" in html_content
    assert "Proof &amp; Disclaimers" in html_content or "Proof" in html_content
    assert "calibrated confidence" in html_content.lower() or "confidence" in html_content.lower()
