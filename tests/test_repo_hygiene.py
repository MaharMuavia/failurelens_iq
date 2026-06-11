import os
from pathlib import Path

def test_repo_hygiene():
    root = Path(__file__).resolve().parents[1]
    
    # 1. Playwright MCP directory should not exist
    playwright_mcp = root / ".playwright-mcp"
    assert not playwright_mcp.exists()
    
    # 2. Audit report complete should not exist
    audit_report = root / "AUDIT_REPORT_COMPLETE.md"
    assert not audit_report.exists()
    
    # 3. Old failurelens-iq folder should not exist
    old_iq = root / "failurelens-iq"
    assert not old_iq.exists()
    
    # 4. Committed PNG screenshots at root should not exist
    current_build_png = root / "failurelens-dashboard-current-build.png"
    smoke_png = root / "failurelens-dashboard-smoke.png"
    assert not current_build_png.exists()
    assert not smoke_png.exists()
    
    # 5. .env file should be gitignored
    gitignore_content = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore_content
    assert ".playwright-mcp/" in gitignore_content
    assert "*.png" in gitignore_content
