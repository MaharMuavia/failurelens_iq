from __future__ import annotations

from backend.models.schemas import AgentContext


class ConfidenceGate:
    def evaluate(self, ctx: AgentContext) -> tuple[bool, str | None]:
        threshold = ctx.planner_context.plan.dynamic_threshold if ctx.planner_context else 0.45
        confidence = ctx.diagnosis.confidence if ctx.diagnosis else 0.0
        if confidence >= threshold:
            ctx.gate_passed = True
            ctx.gate_halt_reason = None
            return True, None
        reason = (
            f"Diagnosis confidence {confidence:.3f} is below dynamic threshold {threshold:.3f}; "
            "human review is required before downstream learning actions."
        )
        ctx.requires_human_review = True
        ctx.human_review_reason = reason
        ctx.gate_passed = False
        ctx.gate_halt_reason = reason
        return False, reason
