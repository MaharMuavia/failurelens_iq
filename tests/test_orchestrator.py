import asyncio

from backend.core.orchestrator import Orchestrator
from backend.utils.data_loader import DataLoader


def test_exp_1001_full_pipeline_agent_trace():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-1001")))
    assert len(ctx.agent_trace) >= 7
    assert ctx.classification.failure_category.value != "Unknown"
    assert ctx.overall_confidence > 0


def test_sparse_001_requires_human_review_and_no_fabrication():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("SPARSE-001")))
    assert ctx.requires_human_review is True
    assert ctx.diagnosis.root_cause == "Insufficient evidence to determine root cause with required confidence."
    assert ctx.gate_passed is False


def test_team_b_recurring_pattern_alert_exists():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-2006")))
    assert ctx.team_insights.recurring_pattern_alert is not None
    assert "TEAM-B" in ctx.team_insights.recurring_pattern_alert
    assert "systematic" in ctx.team_insights.recurring_pattern_alert or "3" in ctx.team_insights.recurring_pattern_alert
