from __future__ import annotations

from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.core.security import require_api_key

router = APIRouter()

@router.post("/report/{experiment_id}/generate")
async def generate_report(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    app_state = request.app.state
    try:
        exp = await app_state.experiment_store.get_experiment(experiment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ctx = await app_state.orchestrator.run(exp)
    path = app_state.report_service.generate(ctx)
    blob = await app_state.grounding_adapter.blob_client.upload_report(
        experiment_id,
        path.read_text(encoding="utf-8")
    )
    return {
        "experiment_id": experiment_id,
        "path": str(path),
        "bytes": path.stat().st_size,
        "blob_upload": blob
    }

@router.get("/report/{experiment_id}")
async def get_report(
    request: Request,
    experiment_id: str,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    # Sanitize path to prevent path traversal
    filename = f"{experiment_id}.md"
    # Ensure no path traversal components are present
    if "/" in experiment_id or "\\" in experiment_id or experiment_id == "..":
        raise HTTPException(status_code=400, detail="Invalid experiment_id.")
        
    path = Path("reports") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report has not been generated yet.")
    return {
        "experiment_id": experiment_id,
        "path": str(path),
        "content": path.read_text(encoding="utf-8")
    }
