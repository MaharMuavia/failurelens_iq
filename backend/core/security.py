from __future__ import annotations

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from backend.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> str | None:
    if not settings.ENABLE_AUTH:
        return None
        
    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is misconfigured: ENABLE_AUTH is true but API_KEY is not set."
        )
        
    if not api_key_header or api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key."
        )
        
    return api_key_header
