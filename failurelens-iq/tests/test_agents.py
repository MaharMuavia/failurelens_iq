import asyncio

from backend.core.orchestrator import Orchestrator
from backend.models.enums import AgentStatus
from backend.utils.data_loader import DataLoader


def test_classifier_evaluates_exactly_6_rules():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-1001")))
    assert len(ctx.classification.rules_evaluated) == 6


def test_diagnostic_reflection_notes_at_least_5():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-2001")))
    assert len(ctx.diagnosis.reflection_notes) >= 5


def test_completed_traces_have_reasoning_and_evidence():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-1001")))
    for trace in ctx.agent_trace:
        if trace.status == AgentStatus.COMPLETED:
            assert len(trace.reasoning_steps) >= 3
            assert trace.key_evidence


def test_no_blame_language_in_outputs():
    d = DataLoader()
    d.load_all()
    forbidden = ["engineer failed", "developer mistake", "person responsible", "individual error", "fault", "your mistake", "you failed"]
    for exp_id in ["EXP-1001", "EXP-2001", "EXP-3001", "SPARSE-001"]:
        ctx = asyncio.run(Orchestrator().run(d.get_experiment(exp_id)))
        full_text = ctx.model_dump_json().lower()
        for phrase in forbidden:
            assert phrase not in full_text
