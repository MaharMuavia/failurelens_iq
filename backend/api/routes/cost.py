from __future__ import annotations

from fastapi import APIRouter

from backend.core.cost_guard import cost_estimate_payload

router = APIRouter()


@router.get("/cost/estimate")
async def cost_estimate() -> dict[str, object]:
    return cost_estimate_payload()
