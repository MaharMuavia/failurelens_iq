from __future__ import annotations

import contextvars
import json
import logging
import time
from uuid import uuid4
from starlette.types import ASGIApp, Scope, Receive, Send

request_context = contextvars.ContextVar("request_context", default={})

logger = logging.getLogger("failurelens_iq")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_log_context() -> dict:
    return request_context.get()

def log_structured(level: int, message: str, **kwargs):
    ctx = dict(get_log_context())
    ctx.update(kwargs)
    ctx["message"] = message
    # Filter out None values
    ctx = {k: v for k, v in ctx.items() if v is not None}
    logger.log(level, json.dumps(ctx))

class StructuredLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        path = scope.get("path", "")
        method = scope.get("method", "")
        
        token = request_context.set({
            "request_id": request_id,
            "path": path,
            "method": method,
            "agent": None,
            "experiment_id": None
        })
        
        start_time = time.perf_counter()
        status_code = 200
        
        async def logging_send(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, logging_send)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 3)
            ctx = dict(request_context.get())
            ctx["status_code"] = status_code
            ctx["duration_ms"] = duration_ms
            ctx["message"] = "request completed"
            ctx = {k: v for k, v in ctx.items() if v is not None}
            logger.info(json.dumps(ctx))
            request_context.reset(token)
