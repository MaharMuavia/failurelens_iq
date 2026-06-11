from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.core.security import require_api_key
from backend.models.schemas import AgentContext

router = APIRouter()

@router.get("/manager/team/{team_id}")
async def manager_team(request: Request, team_id: str) -> dict[str, Any]:
    app_state = request.app.state
    experiments = app_state.data_loader.experiments_for_team(team_id)
    if not experiments:
        raise HTTPException(status_code=404, detail=f"Unknown team_id: {team_id}")
    ctx = await app_state.orchestrator.run(experiments[-1])
    return ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {}

@router.get("/manager/all")
async def manager_all(
    request: Request,
    refresh: bool = False,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    app = request.app
    # If not refresh, check if we have cached insights in app.state.manager_cache
    if not refresh and getattr(app.state, "manager_cache", None):
        return app.state.manager_cache

    result = {}
    manager_agent = app.state.orchestrator.manager
    
    # We run ONLY the manager agent on each team's last experiment using a dummy context.
    # This avoids running the other 7 agents in the pipeline, solving the O(N) scaling issue completely!
    for team_id in sorted(app.state.data_loader.team_profiles):
        experiments = app.state.data_loader.experiments_for_team(team_id)
        if not experiments:
            continue
        dummy_ctx = AgentContext(experiment=experiments[-1])
        await manager_agent.run(dummy_ctx)
        result[team_id] = dummy_ctx.team_insights.model_dump(mode="json") if dummy_ctx.team_insights else {}

    app.state.manager_cache = result
    return result
