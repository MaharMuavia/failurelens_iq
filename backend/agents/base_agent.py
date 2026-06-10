from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from backend.models.enums import AgentName, AgentStatus
from backend.models.schemas import AgentContext, AgentTraceEntry, AuditEntry, EvidenceRef, ReasoningStep
from backend.utils.safety import safe_process_language


AGENT_METADATA: dict[AgentName, dict[str, str]] = {
    AgentName.INTAKE: {
        "agent_name": "ExperimentIntakeAgent",
        "role": "Validate the experiment packet and summarize available evidence.",
    },
    AgentName.CLASSIFIER: {
        "agent_name": "FailureClassifierAgent",
        "role": "Classify the failed run into a repeatable ML failure category.",
    },
    AgentName.DIAGNOSTIC: {
        "agent_name": "RootCauseAnalyzerAgent",
        "role": "Explain the likely root cause with evidence, counter-evidence, and calibrated confidence.",
    },
    AgentName.HISTORIAN: {
        "agent_name": "ExperimentHistorianAgent",
        "role": "Find similar historical failures and convert them into team memory.",
    },
    AgentName.CERT_MAPPER: {
        "agent_name": "CertificationEvaluatorAgent",
        "role": "Map the failure to Microsoft certification skills and learning readiness.",
    },
    AgentName.REMEDIATION: {
        "agent_name": "PrescriptiveCoachAgent",
        "role": "Create a remediation plan that is tied to the failure evidence and team context.",
    },
    AgentName.ASSESSMENT: {
        "agent_name": "CertificationEvaluatorAgent",
        "role": "Generate evidence-bound readiness questions for the recommended learning path.",
    },
    AgentName.MANAGER: {
        "agent_name": "IntegrationManagerAgent",
        "role": "Assemble manager-ready learning intelligence and audit summaries.",
    },
}


class BaseAgent:
    name: AgentName

    def __init__(self, iq_provider: Any = None, scoring_service: Any = None, data_loader: Any = None) -> None:
        self.iq_provider = iq_provider
        self.scoring_service = scoring_service
        self.data_loader = data_loader

    def start_trace(self) -> tuple[AgentTraceEntry, float]:
        metadata = AGENT_METADATA.get(self.name, {"agent_name": self.name.value, "role": "Run one analysis step."})
        return (
            AgentTraceEntry(
                agent=self.name,
                agent_name=metadata["agent_name"],
                role=metadata["role"],
                status=AgentStatus.RUNNING,
            ),
            perf_counter(),
        )

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
        trace.confidence_score = confidence
        trace.confidence_factors = confidence_factors or {}
        trace.grounding_citations = grounding_citations or []
        trace.grounding_refs = trace.grounding_citations
        trace.input_summary = f"{ctx.experiment.experiment_id}: {safe_process_language(ctx.experiment.failure_observation)[:220]}"
        trace.findings = [step.finding for step in reasoning_steps]
        trace.uncertainty = sorted({item for step in reasoning_steps for item in step.uncertainty} | set(trace.counter_evidence))
        trace.recommended_next_actions = [step.next_action for step in reasoning_steps if step.next_action]
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
            agent_name=metadata["agent_name"] if (metadata := AGENT_METADATA.get(self.name)) else self.name.value,
            role=metadata["role"] if metadata else "Skipped analysis step.",
            input_summary=f"{ctx.experiment.experiment_id}: {safe_process_language(reason)}",
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
        thought_type: str = "inference",
        uncertainty: list[str] | None = None,
        assumptions: list[str] | None = None,
        next_action: str | None = None,
    ) -> ReasoningStep:
        evidence = [
            EvidenceRef(
                source_type="experiment_log",
                source_id=self.name.value,
                field_path=field,
                value=field,
                interpretation=safe_process_language(f"{field} was reviewed for this reasoning step."),
                confidence=max(0.0, min(1.0, 0.55 + confidence_delta)),
            )
            for field in evidence_fields
        ]
        return ReasoningStep(
            step_number=number,
            thought_type=thought_type,  # type: ignore[arg-type]
            description=safe_process_language(description),
            evidence=evidence,
            finding=safe_process_language(finding),
            confidence=max(0.0, min(1.0, 0.55 + confidence_delta)),
            evidence_fields=evidence_fields,
            confidence_delta=confidence_delta,
            uncertainty=[safe_process_language(item) for item in (uncertainty or ["No hidden chain-of-thought is exposed; this is an audit summary."])],
            assumptions=[safe_process_language(item) for item in (assumptions or ["Available experiment fields are accurate enough for this step."])],
            next_action=safe_process_language(next_action) if next_action else None,
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
