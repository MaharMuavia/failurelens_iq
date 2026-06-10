from __future__ import annotations

from pathlib import Path

from backend.models.schemas import AgentContext


class ReportService:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, ctx: AgentContext) -> Path:
        exp = ctx.experiment
        lines: list[str] = [
            f"# FailureLens IQ Report: {exp.experiment_id}",
            "",
            "## Experiment Summary",
            f"- Team: {exp.team_id}",
            f"- Project: {exp.project_name}",
            f"- Model: {exp.model_type}",
            f"- Stage: {exp.pipeline_stage}",
            f"- Outcome: {exp.outcome}",
            f"- Observation: {exp.failure_observation}",
            "",
        ]
        if ctx.planner_context:
            lines += [
                "## Planner Hypothesis",
                ctx.planner_context.hypothesis.hypothesis_statement,
                f"- Threshold: {ctx.planner_context.plan.dynamic_threshold:.3f}",
                "",
            ]
        lines += ["## Agent Reasoning Trace"]
        for trace in ctx.agent_trace:
            lines.append(f"### {trace.agent.value} - {trace.status.value}")
            if trace.skip_reason:
                lines.append(f"Skipped because: {trace.skip_reason}")
            for step in trace.reasoning_steps:
                lines.append(f"- Step {step.step_number}: {step.finding}")
            lines.append("")
        if ctx.classification:
            lines += [
                "## Classification Result",
                f"- Category: {ctx.classification.failure_category.value}",
                f"- Confidence: {ctx.classification.confidence:.3f}",
                f"- Conflict resolution: {ctx.classification.conflict_resolution}",
                "",
            ]
        if ctx.diagnosis:
            lines += [
                "## Diagnosis",
                ctx.diagnosis.root_cause,
                f"- Violated assumption: {ctx.diagnosis.violated_assumption}",
                f"- Knowledge gap: {ctx.diagnosis.knowledge_gap}",
                f"- Evidence strength: {ctx.diagnosis.evidence_strength.value}",
                "",
                "## Evidence Table",
                "| Evidence |",
                "|---|",
            ]
            lines += [f"| {item} |" for item in ctx.diagnosis.evidence]
            lines += ["", "## Counter-Evidence"]
            lines += [f"- {item}" for item in ctx.diagnosis.counter_evidence] or ["- No strong counter-evidence was found in the synthetic record."]
            lines += ["", "## Self-Reflection Notes"]
            lines += [f"- {item}" for item in ctx.diagnosis.reflection_notes]
            lines += ["", "## IQ Grounding"]
            lines += [f"- {hit.citation} ({hit.relevance_score:.3f})" for hit in ctx.diagnosis.iq_retrieval.hits] or ["- Retrieval was weak; human review should inspect the evidence record."]
            lines.append("")
        if ctx.cert_mapping:
            lines += [
                "## Certification Mapping",
                f"- Recommended: {ctx.cert_mapping.recommended_cert}",
                f"- Skill domain: {ctx.cert_mapping.skill_domain}",
                f"- Confidence: {ctx.cert_mapping.confidence:.3f}",
                "",
            ]
        else:
            lines += ["## Certification Mapping", f"Skipped because: {ctx.gate_halt_reason or 'downstream learning was not requested for this run.'}", ""]
        if ctx.remediation:
            lines += [
                "## Remediation Plan",
                f"- Plan type: {ctx.remediation.plan_type.value}",
                f"- Lab: {ctx.remediation.hands_on_lab}",
                f"- Manager note: {ctx.remediation.manager_note}",
                "",
            ]
        else:
            lines += ["## Remediation Plan", f"Skipped because: {ctx.gate_halt_reason or 'confidence-gated remediation was unavailable.'}", ""]
        if ctx.assessment:
            lines += ["## Assessment Questions"]
            for q in ctx.assessment.questions:
                lines.append(f"- {q.question_type}: {q.question}")
            lines.append("")
        else:
            lines += ["## Assessment Questions", f"Skipped because: {ctx.gate_halt_reason or 'assessment was not generated.'}", ""]
        if ctx.team_insights:
            lines += [
                "## Team Insights",
                f"- Failure rate: {ctx.team_insights.failure_rate:.0%}",
                f"- Vulnerability: {ctx.team_insights.vulnerability_level.value}",
                f"- Recurring alert: {ctx.team_insights.recurring_pattern_alert or 'No recurring category reached the alert threshold.'}",
                f"- Recommended action: {ctx.team_insights.recommended_action}",
                "",
            ]
        lines += [
            "## Human Review",
            ctx.human_review_reason if ctx.requires_human_review else "Automated diagnosis passed the confidence gate; human review remains optional.",
            "",
        ]
        if ctx.responsible_ai_flagged:
            lines += [
                "## Responsible AI Notice",
                "This experiment includes fairness, bias, or protected-attribute signals. Qualified human review is required before deployment or model update.",
                "",
            ]
        lines += ["## Audit Trail", "| Agent | Action | Output | Duration ms |", "|---|---|---|---|"]
        for audit in ctx.audit_trail:
            lines.append(f"| {audit.agent.value} | {audit.action} | {audit.output_summary} | {audit.duration_ms:.3f} |")
        path = self.output_dir / f"{exp.experiment_id}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
