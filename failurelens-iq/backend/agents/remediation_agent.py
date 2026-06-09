from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName, FailureCategory, PlanType, VulnerabilityLevel
from backend.models.schemas import AgentContext, RemediationResult


class RemediationAgent(BaseAgent):
    name = AgentName.REMEDIATION

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        retrieval = await self.iq_provider.retrieve("remediation playbook micro balanced immersive manager note", top_k=3, cert_filter=None)
        profile = self.data_loader.get_team_profile(exp.team_id) if self.data_loader else {}
        high_load = profile.get("sprint_load") == "high"
        category = ctx.classification.failure_category if ctx.classification else FailureCategory.UNKNOWN
        recurring = ctx.team_insights.recurring_pattern_alert if ctx.team_insights else None
        high_risk = category == FailureCategory.RESPONSIBLE_AI or profile.get("compliance_sensitivity") == "high"
        if recurring or high_risk:
            plan_type = PlanType.IMMERSIVE
        elif high_load:
            plan_type = PlanType.MICRO
        else:
            plan_type = PlanType.BALANCED
        cert = ctx.cert_mapping.cert_code if ctx.cert_mapping else "target skill"
        ctx.remediation = RemediationResult(
            plan_type=plan_type,
            three_day_plan=[
                f"Day 1: review {category.value} evidence from {exp.experiment_id}.",
                f"Day 2: practice the {cert} skill area with the failed experiment fields.",
                "Day 3: add one review checklist change and inspect it with the team.",
            ],
            seven_day_plan=[
                "Day 1: collect evidence fields and counter-evidence.",
                "Day 2: study the grounded local IQ sections.",
                "Day 3: rerun evaluation or review using corrected assumptions.",
                "Day 4: pair review the reasoning trace and audit entries.",
                "Day 5: update model card or experiment checklist.",
                "Day 6: run a synthetic lab that mirrors the failure mode.",
                "Day 7: manager review of learning velocity and next sprint action.",
            ],
            hands_on_lab=f"Rebuild the {exp.experiment_id} decision using the cited evidence, then document what changed in the validation or review checklist.",
            experiment_connection=f"The plan targets {category.value} evidence from {exp.experiment_id}, especially {ctx.diagnosis.knowledge_gap if ctx.diagnosis else 'the recorded knowledge gap'}.",
            manager_note=f"Treat this as a team process gap and protect time for {plan_type.value} remediation.",
            responsible_ai_note="Responsible AI signals require qualified human review before deployment or model update." if category == FailureCategory.RESPONSIBLE_AI else None,
            grounding_citations=[hit.citation for hit in retrieval.hits] or ["remediation_playbook.md § Confidence-Gated Remediation"],
            confidence=min(0.84, max(0.45, (ctx.diagnosis.confidence if ctx.diagnosis else 0.4) + 0.1)),
        )
        steps = [
            self.build_reasoning_step(1, "Retrieved remediation playbook", f"{len(retrieval.hits)} playbook hits returned.", ["knowledge_index"], 0.05),
            self.build_reasoning_step(2, "Selected plan intensity", f"Plan type {plan_type.value} from load={profile.get('sprint_load')} and high_risk={high_risk}.", ["team_profile", "classification"], 0.06),
            self.build_reasoning_step(3, "Connected plan to experiment", ctx.remediation.experiment_connection, ["diagnosis.knowledge_gap"], 0.04),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("plan_type", plan_type.value, "learning intervention intensity")], ctx.remediation.confidence, ctx.remediation.grounding_citations)
        return ctx
