import pytest
from backend.services.prompt_experiment_builder import PromptExperimentBuilder
from backend.models.schemas import ExperimentLog

@pytest.mark.anyio
async def test_deterministic_builder_churn_prompt():
    prompt = "Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14. Find the root cause."
    builder = PromptExperimentBuilder()
    log, meta = await builder.build(prompt)
    
    assert isinstance(log, ExperimentLog)
    assert log.project_name == "Customer Churn Prediction"
    assert log.model_type == "XGBoost Classifier"
    assert log.metrics["accuracy"] == 0.93
    assert log.metrics["minority_f1"] == 0.14
    assert log.outcome == "failure"
    assert "Generated from user prompt with assumptions." in log.engineer_notes
    
    # Check prompt_extraction metadata
    pe = meta["prompt_extraction"]
    assert "metrics" in pe["explicit_fields"]
    assert "project_name" in pe["explicit_fields"]
    assert "model_type" in pe["assumed_fields"]
    assert 0.0 <= pe["confidence"] <= 1.0

@pytest.mark.anyio
async def test_deterministic_builder_leakage_prompt():
    prompt = "Overfitting random forest classifier with potential data leakage in validation split."
    builder = PromptExperimentBuilder()
    log, meta = await builder.build(prompt)
    
    assert isinstance(log, ExperimentLog)
    assert log.project_name == "Regularized Classifier Experiment"
    assert log.model_type == "Random Forest"
    assert "target_leakage_col" in log.suspected_leakage_columns
    assert "overfitting_detected" in log.failure_symptoms or "data_leakage_symptom" in log.failure_symptoms
    
    pe = meta["prompt_extraction"]
    assert "suspected_leakage_columns" in pe["explicit_fields"]
