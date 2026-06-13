import sys
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config):
    config.addinivalue_line("markers", "anyio: run async tests with anyio")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_app_state(monkeypatch):
    # Reset the global singletons to prevent state leakage between tests
    import backend.api.main as main
    
    # 1. Reset singletons
    main._GLOBAL_ORCHESTRATOR = None
    
    # 2. Build fresh app state for current test context/env/settings
    fresh_state = main.create_app_state_for_tests()
    
    # 3. Mirror fresh singletons to the app.state object
    for key, value in fresh_state.items():
        setattr(main.app.state, key, value)
        
    yield
    
    # Re-reset after test execution
    main._GLOBAL_ORCHESTRATOR = None
