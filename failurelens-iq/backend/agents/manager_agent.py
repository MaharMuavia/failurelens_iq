from __future__ import annotations

from collections import Counter

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName, FailureCategory, VulnerabilityLevel
from backend.models.schemas import AgentContext, RankedGap, TeamInsights, TrendPoint


GAP_BY_CATEGORY = {
    FailureCategory.RESPONSIBLE_AI: ("Responsible AI fairness assessment", "AI-102"),
    FailureCategory.EVALUATION_METHODOLOGY: ("Imbalanced evaluation methodology", "DP-100"),
    FailureCategory.DATA_LEAKAGE: ("Feature leakage prevention", "DP-100"),
    FailureCategory.DEPLOYMENT_DRIFT: ("Deployment monitoring and drift response", "DP-100"),
    FailureCategory.FEATURE_ENGINEERING: ("Feature design and validation", "DP-100"),
    FailureCategory.DATA_QUALITY: ("Data quality contracts", "DP-203"),
    FailureCategory.UNKNOWN: ("Evidence collection discipline", "PL-300"),
}


class ManagerAgent(BaseAgent):
    name = AgentName.MANAGER

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        team_id = ctx.experiment.team_id
        experiments = self.data_loader.experiments_for_team(team_id) if self.data_loader else [ctx.experiment]
        total = len(experiments)
        failures = [exp for exp in experiments if exp.outcome in {"failure", "unknown"}]
        categories = [self.data_loader.infer_category(exp) if self.data_loader else FailureCategory.UNKNOWN for exp in failures]
        heatmap = Counter(category.value for category in categories)
        recent = [exp for exp in failures if (ctx.experiment.timestamp - exp.timestamp).days <= 30 or (exp.timestamp - ctx.experiment.timestamp).days <= 30]
        recent_counts = Counter((self.data_loader.infer_category(exp) if self.data_loader else FailureCategory.UNKNOWN).value for exp in recent)
        recurring = None
        for category, count in recent_counts.items():
            if count >= 3 and category != FailureCategory.UNKNOWN.value:
                recurring = f"{team_id} has {count} {category} failures in the last 30 days, indicating a systematic team skill area."
                break
        vulnerability = VulnerabilityLevel.CRITICAL if recurring else VulnerabilityLevel.HIGH if len(failures) / max(total, 1) > 0.65 else VulnerabilityLevel.MODERATE if failures else VulnerabilityLevel.LOW
        gaps = []
        for category_value, frequency in heatmap.most_common(3):
            category = next((item for item in FailureCategory if item.value == category_value), FailureCategory.UNKNOWN)
            gap, cert = GAP_BY_CATEGORY[category]
            urgency = "critical" if frequency >= 3 else "high" if frequency == 2 else "medium"
            gaps.append(RankedGap(knowledge_gap=gap, frequency=frequency, related_cert=cert, urgency=urgency))
        cert_scores = {"DP-100": 0.35, "AI-102": 0.25, "DP-203": 0.25, "PL-300": 0.15}
        for gap in gaps:
            cert_scores[gap.related_cert] = min(1.0, cert_scores.get(gap.related_cert, 0.0) + 0.2 * gap.frequency)
        trend = [
            TrendPoint(date=exp.timestamp.date().isoformat(), failure_count=1, categories=[self.data_loader.infer_category(exp) if self.data_loader else FailureCategory.UNKNOWN])
            for exp in sorted(failures, key=lambda item: item.timestamp)[-30:]
        ]
        learning_velocity = "worsening" if recurring else "stagnant" if len(failures) >= 3 else "improving"
        ctx.team_insights = TeamInsights(
            team_id=team_id,
            failure_count=len(failures),
            failure_rate=round(len(failures) / max(total, 1), 4),
            failure_heatmap=dict(heatmap),
            trend_30_days=trend,
            recurring_pattern_alert=recurring,
            vulnerability_level=vulnerability,
            top_knowledge_gaps=gaps,
            cert_relevance_scores={key: round(value, 3) for key, value in cert_scores.items()},
            recommended_action=(recurring or "Review the highest-frequency team process gap and add a sprint-level learning check."),
            learning_velocity=learning_velocity,
            sprint_adjusted_plan="Protect remediation time this sprint and review evidence traces during planning." if recurring else "Add one lightweight checklist item for the next experiment review.",
        )
        steps = [
            self.build_reasoning_step(1, "Aggregated team experiments", f"{total} experiments found for {team_id}.", ["team_id"], 0.04),
            self.build_reasoning_step(2, "Computed failure heatmap", str(dict(heatmap)), ["failure_category_label"], 0.06),
            self.build_reasoning_step(3, "Detected recurring patterns", recurring or "No recurring category reached threshold.", ["timestamp", "failure_category_label"], 0.08 if recurring else 0.0),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("recurring_pattern_alert", recurring, "manager intelligence")], 0.82 if recurring else 0.66)
        return ctx
