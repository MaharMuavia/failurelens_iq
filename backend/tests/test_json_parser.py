from __future__ import annotations

from backend.services.json_parser import clean_and_extract_json, parse_and_validate_analysis

def test_clean_and_extract_json_direct():
    text = '{"key": "value"}'
    res = clean_and_extract_json(text)
    assert res == {"key": "value"}

def test_clean_and_extract_json_markdown():
    text = '```json\n{"key": "value"}\n```'
    res = clean_and_extract_json(text)
    assert res == {"key": "value"}

def test_clean_and_extract_json_preamble():
    text = 'Sure, here is the result:\n\n```\n{"key": "value"}\n```\nHope that helps!'
    res = clean_and_extract_json(text)
    assert res == {"key": "value"}

def test_parse_and_validate_analysis_success():
    raw = """
    {
        "failure_type": "Overfitting",
        "severity": "High",
        "confidence_score": 85,
        "reasoning_trace": [{"step": 1, "observation": "obs", "interpretation": "interp"}],
        "evidence_used": ["ev"],
        "root_causes": ["rc"],
        "uncertainty": {"level": "Low", "missing_information": [], "alternative_explanations": []},
        "recommended_fixes": ["fix"],
        "next_experiment_plan": ["next"],
        "certification_gap": {"skill_gap": "sg", "recommended_learning": "rl"},
        "iq_grounding": {"knowledge_sources_used": [], "matched_failure_patterns": [], "grounding_confidence": 0},
        "agent_metadata": {"call_mode": "mock", "agent_name": "", "model_deployment": "", "schema_version": "1.0"}
    }
    """
    res = parse_and_validate_analysis(raw, call_mode="model", agent_name="", model_deployment="grok-4")
    assert res.failure_type == "Overfitting"
    assert res.agent_metadata.call_mode == "model"
    assert res.agent_metadata.model_deployment == "grok-4"

def test_parse_and_validate_analysis_fallback():
    raw = "Invalid non-json response text"
    res = parse_and_validate_analysis(raw, call_mode="agent", agent_name="AgentName", model_deployment="deployment")
    assert res.failure_type == "Undetermined"
    assert res.confidence_score == 0
    assert res.agent_metadata.call_mode == "agent"
    assert res.agent_metadata.agent_name == "AgentName"
