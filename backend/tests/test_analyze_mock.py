from __future__ import annotations

import json
from pathlib import Path
import httpx
import pytest
from backend.app.main import app

@pytest.mark.anyio
async def test_analyze_endpoint_mock_overfitting():
    # Load sample input
    samples_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    with open(samples_dir / "overfitting_random_forest.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["failure_type"] == "Overfitting"
    assert data["severity"] == "Critical"
    assert data["confidence_score"] == 88
    assert len(data["reasoning_trace"]) == 3
    assert data["agent_metadata"]["call_mode"] == "mock"

@pytest.mark.anyio
async def test_analyze_endpoint_mock_leakage():
    # Load sample input
    samples_dir = Path(__file__).resolve().parents[1] / "data" / "samples"
    with open(samples_dir / "data_leakage_case.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["failure_type"] == "Data Leakage"
    assert data["severity"] == "Critical"
    assert data["confidence_score"] == 92
    assert data["agent_metadata"]["call_mode"] == "mock"
