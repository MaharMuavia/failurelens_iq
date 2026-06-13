from pathlib import Path


SECRET_PATTERNS = [
    "AZURE_OPENAI_API_KEY=sk-",
    "AZURE_AI_SEARCH_KEY=sk-",
    "FOUNDRY_API_KEY=sk-",
    "FOUNDRY_API_KEY=api-",
    "-----BEGIN PRIVATE KEY-----",
    "AccountKey=",
]


def test_no_secret_like_values_committed():
    root = Path(__file__).resolve().parents[1]
    ignored = {".env", ".env.local", "node_modules", ".git", ".pytest_cache", "__pycache__"}
    for path in root.rglob("*"):
        if path.name == "test_no_secrets_committed.py":
            continue
        if any(part in ignored for part in path.parts):
            continue
        if not path.is_file() or path.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".json", ".md", ".yml", ".yaml", ".example", ".demo"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            assert pattern not in text, f"Secret-like pattern found in {path}"
