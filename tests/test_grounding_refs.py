import asyncio

from backend.azure.grounding_adapter import GroundingAdapter


def test_demo_mode_returns_local_demo_grounding_refs():
    from backend.azure.config import AzureConfig
    config = AzureConfig(app_mode="demo")
    adapter = GroundingAdapter(config=config)
    refs = asyncio.run(adapter.retrieve_experiment_context("EXP-1001"))
    assert refs
    assert all(ref.source_type == "local_demo_grounding" for ref in refs)
    summary = asyncio.run(adapter.build_grounding_summary(refs))
    assert summary["message"] == "Demo mode: local grounding simulates Microsoft IQ retrieval."
