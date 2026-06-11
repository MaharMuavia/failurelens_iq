from __future__ import annotations

import asyncio
import json
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from backend.models.schemas import ExperimentLog
from backend.core.security import require_api_key

router = APIRouter()

class AnalysisOptions(BaseModel):
    include_reasoning_trace: bool = True
    include_grounding: bool = True
    include_certification: bool = True


class AnalysisRunRequest(BaseModel):
    experiment_id: str
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


async def get_experiment_by_id(request: Request, experiment_id: str) -> ExperimentLog:
    store = request.app.state.experiment_store
    try:
        return await store.get_experiment(experiment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def analyze_experiment(request: Request, experiment_id: str) -> Any:
    exp = await get_experiment_by_id(request, experiment_id)
    orchestrator = request.app.state.orchestrator
    return await orchestrator.run(exp)


@router.post("/analysis/run/{experiment_id}")
async def run_analysis(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    ctx = await analyze_experiment(request, experiment_id)
    return ctx.model_dump(mode="json")


@router.post("/analysis/run")
async def run_analysis_body(
    request: Request,
    payload: AnalysisRunRequest,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    ctx = await analyze_experiment(request, payload.experiment_id)
    result = ctx.model_dump(mode="json")
    if payload.options.include_grounding:
        refs = await request.app.state.grounding_adapter.retrieve_experiment_context(payload.experiment_id)
        result["grounding_summary"] = await request.app.state.grounding_adapter.build_grounding_summary(refs)
    return result


@router.get("/analysis/stream/{experiment_id}")
async def stream_analysis(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> StreamingResponse:
    exp = await get_experiment_by_id(request, experiment_id)
    orchestrator = request.app.state.orchestrator
    queue: asyncio.Queue = asyncio.Queue()

    async def runner() -> None:
        await orchestrator.run(exp, queue)

    async def events():
        task = asyncio.create_task(runner())
        try:
            while True:
                if await request.is_disconnected():
                    task.cancel()
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=0.5)
                    yield f"data: {json.dumps(event)}\n\n"
                    if event["event"] in {"pipeline_completed", "pipeline_failed"}:
                        break
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            task.cancel()
            raise
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    return StreamingResponse(events(), media_type="text/event-stream")


@router.post("/analysis/custom")
async def custom_analysis(
    request: Request,
    payload: dict[str, Any],
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    exp = ExperimentLog.model_validate(payload)
    orchestrator = request.app.state.orchestrator
    ctx = await orchestrator.run(exp)
    return ctx.model_dump(mode="json")
