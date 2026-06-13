from __future__ import annotations

import json
from pathlib import Path
from backend.models.analysis import FailureAnalysisResponse

def test_golden_output_validation():
    # Path to golden output file
    golden_path = Path(__file__).resolve().parents[1] / "data" / "golden_outputs" / "overfitting_random_forest_output.json"
    
    assert golden_path.exists(), f"Golden output file not found at {golden_path}"
    
    with open(golden_path, "r", encoding="utf-8") as f:
        golden_data = json.load(f)
        
    # Validating the JSON matches FailureAnalysisResponse
    model = FailureAnalysisResponse.model_validate(golden_data)
    
    assert model.failure_type == "Overfitting"
    assert model.severity == "Critical"
    assert model.confidence_score == 88
    assert len(model.reasoning_trace) == 3
    assert model.reasoning_trace[0].step == 1
    assert model.uncertainty.level == "Low"
    assert model.certification_gap.skill_gap == "Weak understanding of Random Forest regularization techniques and rigorous experimental validation practices"
    assert model.iq_grounding.grounding_confidence == 90
    assert model.agent_metadata.model_deployment == "grok-4-20-reasoning"
