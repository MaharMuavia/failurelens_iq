import json
from pathlib import Path

import httpx
import pytest

from backend.api.main import app


@pytest.mark.anyio
async def test_health_returns_25_experiments():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json()["experiments_loaded"] == 25


@pytest.mark.anyio
async def test_health_returns_min_24_chunks():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json()["knowledge_chunks_indexed"] >= 24


@pytest.mark.anyio
async def test_knowledge_search_returns_hits():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/knowledge/search", params={"q": "imbalanced classification minority f1"})
    assert response.json()["hits"]


@pytest.mark.anyio
async def test_sse_stream_order():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream("GET", "/analysis/stream/EXP-1001") as response:
            events = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    events.append(event["event"])
                    if event["event"] == "pipeline_completed":
                        break
    assert events[0] == "pipeline_started"
    assert events[-1] == "pipeline_completed"


@pytest.mark.anyio
async def test_report_generation_creates_file():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/report/EXP-1001/generate")
    path = Path(response.json()["path"])
    assert path.exists()
    assert "Agent Reasoning Trace" in path.read_text(encoding="utf-8")
