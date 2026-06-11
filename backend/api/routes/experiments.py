from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from backend.models.schemas import ExperimentLog
from backend.core.security import require_api_key

router = APIRouter()

@router.get("/experiments")
async def list_experiments(
    request: Request,
    page: int = 1,
    limit: int = 25,
    team_id: str | None = None,
    outcome: str | None = None,
    failure_category: str | None = None,
) -> dict[str, Any]:
    # clamp limit to max 100
    limit = min(limit, 100)
    
    store = request.app.state.experiment_store
    items = await store.list_experiments(
        limit=10000, # load all to filter and paginate
        team_id=team_id,
        outcome=outcome,
        failure_category=failure_category
    )
    
    start = max(page - 1, 0) * limit
    page_items = items[start : start + limit]
    
    return {
        "total": len(items),
        "page": page,
        "limit": limit,
        "items": [item.model_dump(mode="json") for item in page_items]
    }

@router.get("/experiments/{experiment_id}")
async def get_experiment(request: Request, experiment_id: str) -> dict[str, Any]:
    try:
        store = request.app.state.experiment_store
        exp = await store.get_experiment(experiment_id)
        return exp.model_dump(mode="json")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.post("/experiments/upload")
async def upload_experiment(
    request: Request,
    payload: ExperimentLog,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    store = request.app.state.experiment_store
    await store.save_uploaded_experiment(payload)
    return {
        "status": "stored",
        "experiment_id": payload.experiment_id,
        "next_step": "POST /analysis/run with this experiment_id",
        "persistence": str(store.storage_path)
    }
