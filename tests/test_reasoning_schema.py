import asyncio

from backend.core.orchestrator import Orchestrator
from backend.models.enums import AgentStatus
from backend.utils.data_loader import DataLoader


def test_completed_traces_have_safe_reasoning_schema_fields():
    loader = DataLoader()
    loader.load_all()
    ctx = asyncio.run(Orchestrator().run(loader.get_experiment("EXP-1001")))
    for trace in ctx.agent_trace:
        if trace.status != AgentStatus.COMPLETED:
            continue
        assert trace.agent_name
        assert trace.role
        assert trace.input_summary
        assert trace.findings
        assert trace.audit_entries
        assert trace.confidence_score >= 0
        for step in trace.reasoning_steps:
            assert step.thought_type
            assert step.evidence
            assert step.confidence >= 0
            assert step.uncertainty
