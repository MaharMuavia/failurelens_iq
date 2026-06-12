from pathlib import Path

from backend.api.main import create_app_state_for_tests


def test_startup_duration_uses_canonical_variable():
    source = Path("backend/api/main.py").read_text(encoding="utf-8")
    assert "_STARTUP_duration_ms" not in source
    assert '"startup_duration_ms": _STARTUP_DURATION_MS' in source


def test_startup_duration_state_is_numeric():
    state = create_app_state_for_tests()
    assert isinstance(state["startup_duration_ms"], float)
    assert state["startup_duration_ms"] >= 0.0
