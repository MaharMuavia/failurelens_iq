import pytest
from backend.api.main import create_app
from backend.core.config import settings

def test_cors_origins_loaded_from_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://domain1.com,http://domain2.com")
    monkeypatch.setattr(settings, "CORS_ORIGINS", ["http://domain1.com", "http://domain2.com"])
    app = create_app()
    # Find CORSMiddleware
    cors_mw = None
    for middleware in app.user_middleware:
        if "CORSMiddleware" in str(middleware.cls):
            cors_mw = middleware
            break
    assert cors_mw is not None
    assert "http://domain1.com" in cors_mw.kwargs["allow_origins"]
    assert "http://domain2.com" in cors_mw.kwargs["allow_origins"]

def test_production_rejects_unsafe_wildcard_with_credentials(monkeypatch):
    monkeypatch.setenv("APP_MODE", "production")
    monkeypatch.setenv("CORS_ORIGINS", "*")
    monkeypatch.setenv("CORS_CREDENTIALS", "true")
    
    monkeypatch.setattr(settings, "APP_MODE", "production")
    monkeypatch.setattr(settings, "CORS_ORIGINS", ["*"])
    monkeypatch.setattr(settings, "CORS_ALLOW_CREDENTIALS", True)
    
    with pytest.raises(ValueError) as excinfo:
        create_app()
    assert "CORS configuration is unsafe" in str(excinfo.value)
