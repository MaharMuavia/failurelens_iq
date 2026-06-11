from pathlib import Path


def test_frontend_client_sends_api_key_header_when_configured():
    client = Path("frontend/src/api/client.ts").read_text(encoding="utf-8")
    assert "VITE_DEMO_API_KEY" in client
    assert "X-API-Key" in client
    assert "...authHeaders()" in client


def test_frontend_has_video_demo_mode_config():
    config = Path("frontend/src/config/demoMode.ts").read_text(encoding="utf-8")
    assert "VITE_VIDEO_DEMO_MODE" in config
    assert "VIDEO_DEMO_MODE" in config
