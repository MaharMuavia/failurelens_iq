from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / ".env.azure")


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def require_search_env() -> tuple[str, str, str]:
    endpoint = env("AZURE_AI_SEARCH_ENDPOINT").rstrip("/")
    key = env("AZURE_AI_SEARCH_KEY")
    index = env("AZURE_AI_SEARCH_INDEX", "failurelens-knowledge")
    missing = [
        name
        for name, value in {
            "AZURE_AI_SEARCH_ENDPOINT": endpoint,
            "AZURE_AI_SEARCH_KEY": key,
            "AZURE_AI_SEARCH_INDEX": index,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing required Azure AI Search environment variables: {', '.join(missing)}")
    return endpoint, key, index
