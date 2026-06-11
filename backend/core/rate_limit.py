from __future__ import annotations

import json
import time
from starlette.types import ASGIApp, Scope, Receive, Send
from backend.core.config import settings

class RateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.requests: dict[str, list[float]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if not settings.RATE_LIMIT_ENABLED:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in ("/health", "/agents"):
            await self.app(scope, receive, send)
            return

        client_host = "unknown"
        if settings.TRUST_PROXY_HEADERS:
            headers = dict(scope.get("headers", []))
            x_forwarded_for = headers.get(b"x-forwarded-for")
            if x_forwarded_for:
                ips = x_forwarded_for.decode("utf-8", errors="ignore").split(",")
                if ips:
                    client_host = ips[0].strip()

        if client_host == "unknown":
            client = scope.get("client")
            client_host = client[0] if client else "unknown"

        key = f"{client_host}:{path}"

        # Evict oldest entry if size limit exceeded
        if key not in self.requests and settings.RATE_LIMIT_MAX_KEYS > 0 and len(self.requests) >= settings.RATE_LIMIT_MAX_KEYS:
            oldest_key = next(iter(self.requests))
            self.requests.pop(oldest_key, None)

        now = time.time()
        if key in self.requests:
            self.requests[key] = [t for t in self.requests[key] if now - t < 60]
        else:
            self.requests[key] = []

        if len(self.requests[key]) >= settings.RATE_LIMIT_PER_MINUTE:
            retry_after = 60 - (now - self.requests[key][0])
            retry_after_seconds = int(max(1, retry_after))
            
            body_bytes = json.dumps({
                "error": "rate_limit_exceeded",
                "retry_after_seconds": retry_after_seconds
            }).encode("utf-8")
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body_bytes)).encode("ascii")),
                    (b"retry-after", str(retry_after_seconds).encode("ascii"))
                ]
            })
            await send({
                "type": "http.response.body",
                "body": body_bytes,
                "more_body": False
            })
            return

        self.requests[key].append(now)
        await self.app(scope, receive, send)
