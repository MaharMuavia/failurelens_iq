import re
from pathlib import Path


def test_env_example_includes_settings_used_by_backend_config():
    config = Path("backend/core/config.py").read_text(encoding="utf-8")
    env_example = Path(".env.example").read_text(encoding="utf-8")
    declared = {
        line.split("=", 1)[0].strip()
        for line in env_example.splitlines()
        if line and not line.startswith("#") and "=" in line
    }
    used = set(re.findall(r'os\.getenv\("([^"]+)"', config))
    settings_fields = set(re.findall(r"^\s{4}([A-Z][A-Z0-9_]+):", config, flags=re.MULTILINE))
    aliases = {"CORS_ALLOW_CREDENTIALS", "CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS"}
    missing = (used | settings_fields) - aliases - declared
    assert missing == set()


def test_env_demo_has_no_secret_values():
    content = Path(".env.demo").read_text(encoding="utf-8")
    assert "change-me-for-production" not in content
    assert "AZURE_OPENAI_API_KEY=" in content
    assert "AZURE_COSMOS_KEY=" in content
