import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from backend.api.main import app
from backend.azure.openai_client import AzureOpenAIClient
from backend.core.config import settings
from backend.services.llm_reasoning_provider import LLMReasoningProvider, LLMReasoningResult
from backend.models.schemas import ExperimentLog
from backend.agents.diagnostic_agent import DiagnosticAgent
from backend.models.enums import FailureCategory

class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


@pytest.mark.anyio
async def test_llm_reasoning_fallback_when_disabled():
    # When AzureOpenAI is disabled, it should return used_llm=False and fall back deterministically
    config = MagicMock()
    config.enabled_integrations = {"azure_openai": False}
    openai_client = AzureOpenAIClient(config)
    
    provider = LLMReasoningProvider(openai_client)
    exp = MagicMock(spec=ExperimentLog)
    exp.experiment_id = "EXP-TEST"
    exp.failure_observation = "accuracy is good but minority collapse"
    
    result = await provider.analyze_failure(exp, None, None, None)
    assert result.used_llm is False
    assert result.provider == "deterministic_fallback"
    assert "configured" in result.warning


@pytest.mark.anyio
async def test_llm_reasoning_success(monkeypatch):
    # Mock chat completions for AzureOpenAI raw completion
    async def mock_chat_completion_raw(self, system_prompt, user_prompt):
        return {
            "ok": True,
            "content": """
            {
              "root_cause": "Imbalanced evaluation hiding minority F1 collapse.",
              "violated_assumption": "Headline accuracy is representative.",
              "knowledge_gap": "Imbalanced classification metrics.",
              "evidence": ["accuracy=0.92", "minority_f1=0.12"],
              "counter_evidence": ["accuracy looks high"],
              "uncertainty": ["Sample size is small"],
              "confidence": 0.95,
              "recommended_next_action": "Use stratified validation.",
              "raw_summary": "LLM diagnosis complete.",
              "reasoning_steps": {
                "evidence_check": "Checked F1.",
                "inference": "Accuracy hides minority error.",
                "counter_evidence": "No counter evidence.",
                "uncertainty_check": "Low uncertainty.",
                "decision": "Imbalanced category identified.",
                "next_action": "Recommend DP-100."
              }
            }
            """
        }
        
    monkeypatch.setattr(AzureOpenAIClient, "chat_completion_raw", mock_chat_completion_raw)
    
    config = MagicMock()
    config.enabled_integrations = {"azure_openai": True}
    config.azure_openai_endpoint = "https://test.openai"
    config.azure_openai_api_key = "key"
    config.azure_openai_deployment = "gpt"
    openai_client = AzureOpenAIClient(config)
    
    original_provider = settings.MODEL_PROVIDER
    settings.MODEL_PROVIDER = "azure_openai"
    provider = LLMReasoningProvider(openai_client)
    exp = MagicMock(spec=ExperimentLog)
    exp.experiment_id = "EXP-TEST"
    exp.failure_observation = "accuracy is good but minority collapse"
    exp.project_name = "churn"
    exp.model_type = "classification"
    exp.validation_strategy = "holdout"
    exp.class_balance = "90/10"
    exp.metrics = {"accuracy": 0.92, "minority_f1": 0.12}
    exp.baseline_metrics = {"accuracy": 0.94}
    exp.drift_indicators = []
    exp.data_quality_signals = []
    exp.suspected_leakage_columns = []
    exp.engineer_notes = ""
    
    try:
        result = await provider.analyze_failure(exp, None, None, None)
    finally:
        settings.MODEL_PROVIDER = original_provider
    assert result.used_llm is True
    assert result.provider == "AzureOpenAI"
    assert result.root_cause == "Imbalanced evaluation hiding minority F1 collapse."
    assert result.confidence == 0.95


@pytest.mark.anyio
async def test_llm_reasoning_malformed_json_fallback(monkeypatch):
    # If the response is malformed JSON, it should not crash but fall back safely
    async def mock_chat_completion_raw(self, system_prompt, user_prompt):
        return {
            "ok": True,
            "content": "this is not json"
        }
        
    monkeypatch.setattr(AzureOpenAIClient, "chat_completion_raw", mock_chat_completion_raw)
    
    config = MagicMock()
    config.enabled_integrations = {"azure_openai": True}
    openai_client = AzureOpenAIClient(config)
    
    original_provider = settings.MODEL_PROVIDER
    settings.MODEL_PROVIDER = "azure_openai"
    provider = LLMReasoningProvider(openai_client)
    exp = MagicMock(spec=ExperimentLog)
    exp.experiment_id = "EXP-TEST"
    exp.failure_observation = "accuracy is good but minority collapse"
    exp.project_name = "churn"
    exp.model_type = "classification"
    exp.validation_strategy = "holdout"
    exp.class_balance = "90/10"
    exp.metrics = {"accuracy": 0.92, "minority_f1": 0.12}
    exp.baseline_metrics = {"accuracy": 0.94}
    exp.drift_indicators = []
    exp.data_quality_signals = []
    exp.suspected_leakage_columns = []
    exp.engineer_notes = ""
    
    try:
        result = await provider.analyze_failure(exp, None, None, None)
    finally:
        settings.MODEL_PROVIDER = original_provider
    assert result.used_llm is False
    assert result.provider == "deterministic_fallback"
    assert "parse" in result.warning or "Failed to parse" in result.warning


@pytest.mark.anyio
async def test_demo_endpoint_includes_llm_reasoning_proof():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/demo/run?force_refresh=true")
    payload = response.json()
    assert "llm_reasoning_proof" in payload
    proof = payload["llm_reasoning_proof"]
    assert proof["agent"] == "RootCauseAnalyzerAgent"
    assert "core_agent_used_llm" in proof
    assert "provider" in proof
