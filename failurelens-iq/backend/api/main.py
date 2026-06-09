from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.core.orchestrator import Orchestrator
from backend.models.enums import RetrievalMode
from backend.models.schemas import ExperimentLog
from backend.services.knowledge_index import KnowledgeIndex
from backend.services.local_iq_provider import LocalIQProvider
from backend.services.report_service import ReportService
from backend.services.scoring_service import ScoringService
from backend.utils.data_loader import DataLoader


def create_app_state_for_tests() -> dict[str, Any]:
    data_loader = DataLoader()
    data_loader.load_all()
    knowledge_index = KnowledgeIndex(Path("knowledge/foundry_docs"))
    iq_provider = LocalIQProvider(knowledge_index)
    scoring_service = ScoringService()
    state = {
        "data_loader": data_loader,
        "knowledge_index": knowledge_index,
        "iq_provider": iq_provider,
        "scoring_service": scoring_service,
        "orchestrator": None,
        "report_service": ReportService(Path("reports")),
    }
    state["orchestrator"] = Orchestrator(state)
    return state


def create_app() -> FastAPI:
    app = FastAPI(title="FailureLens IQ", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    state = create_app_state_for_tests()
    for key, value in state.items():
        setattr(app.state, key, value)

    def loader() -> DataLoader:
        return app.state.data_loader

    def orchestrator() -> Orchestrator:
        return app.state.orchestrator

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "version": "1.0.0",
            "experiments_loaded": len(loader().experiments),
            "knowledge_chunks_indexed": len(app.state.knowledge_index.chunks),
            "retrieval_mode": RetrievalMode.LOCAL.value,
            "mock_mode": False,
            "iq_provider": "LocalIQProvider",
        }

    @app.get("/experiments")
    async def list_experiments(
        page: int = 1,
        limit: int = 25,
        team_id: str | None = None,
        outcome: str | None = None,
        failure_category: str | None = None,
    ) -> dict[str, Any]:
        items = loader().experiments
        if team_id:
            items = [item for item in items if item.team_id == team_id]
        if outcome:
            items = [item for item in items if item.outcome == outcome]
        if failure_category:
            items = [item for item in items if (item.failure_category_label or "") == failure_category]
        start = max(page - 1, 0) * limit
        page_items = items[start : start + limit]
        return {"total": len(items), "page": page, "limit": limit, "items": [item.model_dump(mode="json") for item in page_items]}

    @app.get("/experiments/{experiment_id}")
    async def get_experiment(experiment_id: str) -> dict[str, Any]:
        try:
            return loader().get_experiment(experiment_id).model_dump(mode="json")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/analysis/run/{experiment_id}")
    async def run_analysis(experiment_id: str) -> dict[str, Any]:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        ctx = await orchestrator().run(exp)
        return ctx.model_dump(mode="json")

    @app.get("/analysis/stream/{experiment_id}")
    async def stream_analysis(experiment_id: str) -> StreamingResponse:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        queue: asyncio.Queue = asyncio.Queue()

        async def runner() -> None:
            await orchestrator().run(exp, queue)

        async def events():
            task = asyncio.create_task(runner())
            try:
                while True:
                    event = await queue.get()
                    yield f"data: {json.dumps(event)}\n\n"
                    if event["event"] in {"pipeline_completed", "pipeline_failed"}:
                        break
            finally:
                await task

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/analysis/custom")
    async def custom_analysis(payload: dict[str, Any]) -> dict[str, Any]:
        exp = ExperimentLog.model_validate(payload)
        ctx = await orchestrator().run(exp)
        return ctx.model_dump(mode="json")

    @app.get("/manager/team/{team_id}")
    async def manager_team(team_id: str) -> dict[str, Any]:
        experiments = loader().experiments_for_team(team_id)
        if not experiments:
            raise HTTPException(status_code=404, detail=f"Unknown team_id: {team_id}")
        ctx = await orchestrator().run(experiments[-1])
        return ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {}

    @app.get("/manager/all")
    async def manager_all() -> dict[str, Any]:
        result = {}
        for team_id in sorted(loader().team_profiles):
            experiments = loader().experiments_for_team(team_id)
            ctx = await orchestrator().run(experiments[-1])
            result[team_id] = ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {}
        return result

    @app.get("/knowledge/search")
    async def knowledge_search(
        q: str = Query(..., min_length=1),
        top_k: int = 3,
        cert_filter: str | None = None,
    ) -> dict[str, Any]:
        retrieval = await app.state.iq_provider.retrieve(q, top_k=top_k, cert_filter=cert_filter)
        return retrieval.model_dump(mode="json")

    @app.get("/knowledge/sources")
    async def knowledge_sources() -> list[dict[str, object]]:
        return app.state.knowledge_index.sources()

    @app.post("/report/{experiment_id}/generate")
    async def generate_report(experiment_id: str) -> dict[str, Any]:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        ctx = await orchestrator().run(exp)
        path = app.state.report_service.generate(ctx)
        return {"experiment_id": experiment_id, "path": str(path), "bytes": path.stat().st_size}

    @app.get("/report/{experiment_id}")
    async def get_report(experiment_id: str) -> dict[str, Any]:
        path = Path("reports") / f"{experiment_id}.md"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Report has not been generated yet.")
        return {"experiment_id": experiment_id, "path": str(path), "content": path.read_text(encoding="utf-8")}

    return app


app = create_app()
