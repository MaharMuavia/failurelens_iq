from backend.api.routes.iq_status import build_iq_status_report
from backend.core.config import Settings


def test_openai_fallback_does_not_claim_live_microsoft_iq():
    config = Settings(APP_MODE="demo", MODEL_PROVIDER="openai", OPENAI_API_KEY="sk-test")
    payload = build_iq_status_report(
        config,
        {
            "local_iq": True,
            "azure_ai_search": False,
            "azure_openai": False,
            "azure_cosmos_db": False,
            "azure_blob_storage": False,
        },
        "FoundryIQLocalAdapter",
    )
    assert payload["active_reasoning_provider"] == "openai"
    assert payload["proof_level"] == "openai_fallback_with_foundry_adapter"
    assert payload["live_microsoft_iq"] is False
    assert "does not count as live Microsoft IQ" in payload["honest_limitation"]
