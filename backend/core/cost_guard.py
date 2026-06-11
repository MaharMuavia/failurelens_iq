from __future__ import annotations

from backend.core.config import settings


def clamp_search_top_k(top_k: int) -> int:
    return max(1, min(int(top_k), settings.AZURE_MAX_SEARCH_TOP_K))


def clamp_chunk(text: str) -> str:
    return text[: settings.AZURE_MAX_CHUNK_CHARS]


def cost_estimate_payload() -> dict[str, object]:
    return {
        "azure_ai_search": "Free tier recommended for hackathon demo",
        "azure_openai": {
            "max_tokens_per_demo": settings.AZURE_OPENAI_MAX_TOKENS,
            "estimated_demo_calls": 1,
            "cost_guard_enabled": True,
            "temperature": settings.AZURE_OPENAI_TEMPERATURE,
        },
        "limits": {
            "max_docs_to_index": settings.AZURE_MAX_DOCS_TO_INDEX,
            "max_chunk_chars": settings.AZURE_MAX_CHUNK_CHARS,
            "max_search_top_k": settings.AZURE_MAX_SEARCH_TOP_K,
        },
        "recommendations": [
            "Use Azure AI Search Free tier",
            "Use gpt-4o-mini or smallest available model deployment",
            "Keep demo prompts short",
            "Disable Cosmos and Blob if credits are limited",
        ],
    }
