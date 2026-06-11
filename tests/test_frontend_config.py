from pathlib import Path

def test_vite_proxy_uses_env_var():
    config_path = Path("frontend/vite.config.ts")
    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    assert "VITE_PROXY_TARGET" in content
    assert "process.env" in content

def test_api_client_uses_vite_api_base_url():
    client_path = Path("frontend/src/api/client.ts")
    assert client_path.exists()
    content = client_path.read_text(encoding="utf-8")
    assert "VITE_API_BASE_URL" in content

def test_error_boundary_exists():
    eb_path = Path("frontend/src/components/ErrorBoundary.tsx")
    assert eb_path.exists()
    content = eb_path.read_text(encoding="utf-8")
    assert "class ErrorBoundary" in content
    assert "componentDidCatch" in content
