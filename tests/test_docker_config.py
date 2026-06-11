import os
from pathlib import Path
import pytest
from backend.api.main import create_app

def test_docker_compose_has_healthchecks():
    dc_path = Path("docker-compose.yml")
    assert dc_path.exists()
    content = dc_path.read_text(encoding="utf-8")
    assert "healthcheck:" in content
    assert "test:" in content

def test_docker_compose_uses_demo_env_defaults():
    content = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert ".env.demo" in content
    assert Path(".env.demo").exists()
    assert Path("docker-compose.prod.yml").exists()

def test_app_starts_without_dotenv(monkeypatch):
    # Temporarily remove os.environ environment variables loaded from .env
    # so we simulate starting with default fallback settings
    env_keys = [
        "APP_MODE", "IQ_PROVIDER", "ENABLE_AUTH", "API_KEY", 
        "CORS_ORIGINS", "CORS_CREDENTIALS", "CORS_METHODS", "CORS_HEADERS"
    ]
    for key in env_keys:
        monkeypatch.delenv(key, raising=False)
        
    # Attempt app creation
    app = create_app()
    assert app is not None
    assert app.state.settings.APP_MODE == "demo"
    assert app.state.settings.ENABLE_AUTH is False
