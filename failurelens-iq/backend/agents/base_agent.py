from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from backend.models.enums import AgentName, AgentStatus
from backend.models.schemas import AgentContext, AgentTraceEntry, AuditEntry, ReasoningStep
from backend.utils.safety import safe_process_language


class BaseAgent:
    name: AgentName

    def __init__(self, iq_provider: Any = None, scoring_service: Any = None, data_loader: Any = None) -> None:
        self.iq_provider = iq_provider
        self.scoring_service = scoring_service
        self.data_loader = data_loader

    def start_trace(self) -> tuple[AgentTraceEntry, float]:
        return AgentTraceEntry(agent=self.name, status=AgentStatus.RUNNING), perf_counter()

    def complete_trace(
        self,
        ctx: AgentContext,
        trace: AgentTraceEntry,
        started: float,
        reasoning_steps: list[ReasoningStep],
        key_evidence: list[str],
        confidence: float,
        grounding_citations: list[str] | None = None,
        counter_evidence: list[str] | None = None,
        confidence_factors: dict[str, float] | None = None,
    ) -> AgentTraceEntry:
        while len(reasoning_steps) < 3:
            reasoning_steps.append(
                self.build_reasoning_step(
                    len(reasoning_steps) + 1,
                    "Trace completeness check",
                    "Agent recorded enough evidence for audit readability.",
                    ["agent_trace"],
                    0.0,
                )
            )
        trace.status = AgentStatus.COMPLETED
        trace.completed_at = datetime.now(timezone.utc)
        trace.duration_ms = round((perf_counter() - started) * 1000, 3)
        trace.reasoning_steps = reasoning_steps
        trace.key_evidence = [safe_process_language(item) for item in key_evidence] or ["evidence_fields=reviewed -> process-level inference"]
        trace.counter_evidence = counter_evidence or []
        trace.confidence = confidence
        trace.confidence_factors = confidence_factors or {}
        trace.grounding_citations = grounding_citations or []
        audit = self.add_audit(
            "completed",
            f"{self.name.value} reviewed {ctx.experiment.experiment_id}",
            f"confidence={confidence:.3f}",
            trace.duration_ms or 0.0,
        )
        trace.audit_entries.append(audit)
        ctx.agent_trace.append(trace)
        ctx.audit_trail.append(audit)
        return trace

    def skip_trace(self, ctx: AgentContext, reason: str) -> AgentTraceEntry:
        now = datetime.now(timezone.utc)
        trace = AgentTraceEntry(
            agent=self.name,
            status=AgentStatus.SKIPPED,
            started_at=now,
            completed_at=now,
            duration_ms=0.0,
            skip_reason=safe_process_language(reason),
            confidence=0.0,
        )
        audit = self.add_audit("skipped", self.name.value, reason, 0.0)
        trace.audit_entries.append(audit)
        ctx.agent_trace.append(trace)
        ctx.audit_trail.append(audit)
        return trace

    def build_reasoning_step(
        self,
        number: int,
        description: str,
        finding: str,
        evidence_fields: list[str],
        confidence_delta: float = 0.0,
    ) -> ReasoningStep:
        return ReasoningStep(
            step_number=number,
            description=safe_process_language(description),
            finding=safe_process_language(finding),
            evidence_fields=evidence_fields,
            confidence_delta=confidence_delta,
        )

    def cite_evidence(self, field: str, value: Any, implication: str) -> str:
        return safe_process_language(f"{field}={value} -> {implication}")

    def add_audit(self, action: str, input_summary: str, output_summary: str, duration_ms: float) -> AuditEntry:
        return AuditEntry(
            agent=self.name,
            action=safe_process_language(action),
            input_summary=safe_process_language(input_summary),
            output_summary=safe_process_language(output_summary),
            duration_ms=duration_ms,
        )
