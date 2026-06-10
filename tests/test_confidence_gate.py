from backend.core.confidence_gate import ConfidenceGate
from backend.models.schemas import AgentContext, DiagnosisResult, ExecutionPlan, ExperimentLog, PlannerContext
from backend.utils.data_loader import DataLoader


def build_context(confidence: float, threshold: float) -> AgentContext:
    d = DataLoader()
    d.load_all()
    ctx = AgentContext(experiment=d.get_experiment("EXP-1001"))
    ctx.planner_context = PlannerContext(plan=ExecutionPlan(dynamic_threshold=threshold))
    ctx.diagnosis = DiagnosisResult(confidence=confidence)
    return ctx


def test_confidence_gate_halts_below_threshold():
    ctx = build_context(0.30, 0.45)
    passed, reason = ConfidenceGate().evaluate(ctx)
    assert passed is False
    assert "0.300" in reason
    assert "0.450" in reason
    assert ctx.requires_human_review is True


def test_confidence_gate_passes_at_exact_threshold():
    ctx = build_context(0.45, 0.45)
    passed, reason = ConfidenceGate().evaluate(ctx)
    assert passed is True
    assert reason is None
