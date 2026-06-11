import time
import pytest
from backend.core.config import Settings
from backend.core.rate_limit import RateLimitMiddleware

class DummyApp:
    async def __call__(self, scope, receive, send):
        pass


@pytest.mark.anyio
async def test_x_forwarded_for_used_when_trusted(monkeypatch):
    from backend.core.config import settings
    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    
    app = DummyApp()
    middleware = RateLimitMiddleware(app)
    
    scope = {
        "type": "http",
        "path": "/analysis/run",
        "client": ("127.0.0.1", 50000),
        "headers": [
            (b"x-forwarded-for", b"203.0.113.195, 70.41.3.18")
        ]
    }
    
    # Simulate a call to middleware
    # We can invoke it directly. It should register under "203.0.113.195:/analysis/run"
    async def mock_send(message):
        pass
    
    await middleware(scope, None, mock_send)
    assert "203.0.113.195:/analysis/run" in middleware.requests


@pytest.mark.anyio
async def test_x_forwarded_for_ignored_when_not_trusted(monkeypatch):
    from backend.core.config import settings
    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", False)
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    
    app = DummyApp()
    middleware = RateLimitMiddleware(app)
    
    scope = {
        "type": "http",
        "path": "/analysis/run",
        "client": ("127.0.0.1", 50000),
        "headers": [
            (b"x-forwarded-for", b"203.0.113.195")
        ]
    }
    
    async def mock_send(message):
        pass
    
    await middleware(scope, None, mock_send)
    assert "127.0.0.1:/analysis/run" in middleware.requests
    assert "203.0.113.195:/analysis/run" not in middleware.requests


@pytest.mark.anyio
async def test_max_key_eviction_works(monkeypatch):
    from backend.core.config import settings
    monkeypatch.setattr(settings, "RATE_LIMIT_MAX_KEYS", 2)
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    
    app = DummyApp()
    middleware = RateLimitMiddleware(app)
    
    async def mock_send(message):
        pass
        
    # Add two keys
    await middleware({"type": "http", "path": "/path1", "client": ("1.1.1.1", 80)}, None, mock_send)
    await middleware({"type": "http", "path": "/path2", "client": ("2.2.2.2", 80)}, None, mock_send)
    
    assert len(middleware.requests) == 2
    assert "1.1.1.1:/path1" in middleware.requests
    assert "2.2.2.2:/path2" in middleware.requests
    
    # Add a third key, which should evict the first key (1.1.1.1:/path1)
    await middleware({"type": "http", "path": "/path3", "client": ("3.3.3.3", 80)}, None, mock_send)
    
    assert len(middleware.requests) == 2
    assert "1.1.1.1:/path1" not in middleware.requests
    assert "2.2.2.2:/path2" in middleware.requests
    assert "3.3.3.3:/path3" in middleware.requests
