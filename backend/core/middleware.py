from __future__ import annotations

import json
from starlette.types import ASGIApp, Receive, Scope, Send
from backend.core.config import settings

class MaxBodySizeMiddleware:
    def __init__(self, app: ASGIApp, max_body_size: int | None = None) -> None:
        self.app = app
        self.max_body_size = max_body_size if max_body_size is not None else settings.MAX_UPLOAD_BYTES

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length_val = headers.get(b"content-length")
        if content_length_val:
            try:
                if int(content_length_val) > self.max_body_size:
                    await self._send_413(scope, send)
                    return
            except ValueError:
                pass

        if scope["method"] in ("POST", "PUT", "PATCH"):
            body = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body += message.get("body", b"")
                    if len(body) > self.max_body_size:
                        await self._send_413(scope, send)
                        return
                    if not message.get("more_body", False):
                        break
                else:
                    break
            
            async def cached_receive():
                return {"type": "http.request", "body": body, "more_body": False}
            
            await self.app(scope, cached_receive, send)
        else:
            await self.app(scope, receive, send)

    async def _send_413(self, scope: Scope, send: Send) -> None:
        body_bytes = json.dumps({
            "error": "payload_too_large",
            "detail": f"Request body exceeds maximum size of {self.max_body_size} bytes."
        }).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body_bytes)).encode("ascii"))
            ]
        })
        await send({
            "type": "http.response.body",
            "body": body_bytes,
            "more_body": False
        })


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def security_send(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"referrer-policy", b"no-referrer"))
                
                path = scope.get("path", "")
                if path.startswith("/"):
                    headers.append((b"cache-control", b"no-store"))
                
                headers.append((b"content-security-policy", b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' ws: wss:;"))
                
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, security_send)
