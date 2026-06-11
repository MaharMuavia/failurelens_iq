from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from backend.api.main import create_app

def test_manager_all_does_not_call_orchestrator():
    app = create_app()
    original_run = app.state.orchestrator.run
    app.state.orchestrator.run = AsyncMock()
    try:
        client = TestClient(app)
        response = client.get("/manager/all")
        assert response.status_code == 200
        
        # Verify orchestrator.run was not called
        assert app.state.orchestrator.run.call_count == 0
        
        # Check that we received summaries for all loaded teams
        data = response.json()
        assert len(data) > 0
        for team_id, insights in data.items():
            assert "team_id" in insights or insights == {}
    finally:
        app.state.orchestrator.run = original_run
