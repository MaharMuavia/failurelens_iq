from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Query, Request

router = APIRouter()

@router.get("/knowledge/search")
async def knowledge_search(
    request: Request,
    q: str = Query(..., min_length=1),
    top_k: int = 3,
    cert_filter: str | None = None,
) -> dict[str, Any]:
    # limit top_k to max 20
    top_k = min(top_k, 20)
    
    app_state = request.app.state
    retrieval = await app_state.iq_provider.retrieve(q, top_k=top_k, cert_filter=cert_filter)
    return retrieval.model_dump(mode="json")

@router.get("/knowledge/sources")
async def knowledge_sources(request: Request) -> list[dict[str, object]]:
    return request.app.state.knowledge_index.sources()
