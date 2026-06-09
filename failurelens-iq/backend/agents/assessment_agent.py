from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName
from backend.models.schemas import AgentContext, AssessmentResult, PracticeQuestion


class AssessmentAgent(BaseAgent):
    name = AgentName.ASSESSMENT

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        category = ctx.classification.failure_category.value if ctx.classification else "Unknown"
        cert = ctx.cert_mapping.cert_code if ctx.cert_mapping else "DP-100"
        citation = (ctx.cert_mapping.grounding[0] if ctx.cert_mapping and ctx.cert_mapping.grounding else "local IQ citation")
        options = [
            "Review the metric against the failure mode and cited evidence.",
            "Trust the highest aggregate accuracy without slice checks.",
            "Deploy because the experiment has a model artifact.",
            "Remove audit trail entries to reduce review time.",
        ]
        questions = [
            PracticeQuestion(question_type="conceptual", question=f"Which concept best explains the {category} signal in {exp.experiment_id}?", options=options, correct_answer=options[0], explanation="The diagnosis is tied to evidence fields and the failure mode.", distractor_reasoning="The wrong answers ignore evidence, governance, or auditability.", difficulty="beginner", citation=citation, skill_domain=cert, experiment_connection=exp.failure_observation),
            PracticeQuestion(question_type="diagnostic", question=f"Which field should be inspected first for {exp.experiment_id}?", options=["failure_observation", "logo_color", "frontend_route", "package_version"], correct_answer="failure_observation", explanation="The observation carries the initial diagnostic signal.", distractor_reasoning="The distractors do not describe experiment evidence.", difficulty="intermediate", citation=citation, skill_domain=cert, experiment_connection=str(exp.metrics)),
            PracticeQuestion(question_type="application", question=f"What team action best preserves learning from {exp.experiment_id}?", options=["Add a checklist item tied to the evidence.", "Hide the failed run.", "Use only success metrics.", "Skip human review for low confidence."], correct_answer="Add a checklist item tied to the evidence.", explanation="Organizational memory improves when evidence becomes a reusable process control.", distractor_reasoning="The wrong answers reduce trust or ignore confidence.", difficulty="intermediate", citation=citation, skill_domain=cert, experiment_connection=ctx.diagnosis.knowledge_gap if ctx.diagnosis else category),
            PracticeQuestion(question_type="code_review", question=f"Which code review note would help prevent repeat {category}?", options=["Assert the validation and feature assumptions in tests.", "Delete counter-evidence from the report.", "Use a single global metric for every case.", "Bypass CORS and audit logging."], correct_answer="Assert the validation and feature assumptions in tests.", explanation="Tests and review gates make the learning durable.", distractor_reasoning="The wrong answers weaken governance or methodology.", difficulty="advanced", citation=citation, skill_domain=cert, experiment_connection=exp.experiment_id),
        ]
        ctx.assessment = AssessmentResult(
            questions=questions,
            target_cert=cert,
            skill_gaps_assessed=[ctx.diagnosis.knowledge_gap if ctx.diagnosis else category],
            confidence=0.78,
        )
        steps = [
            self.build_reasoning_step(1, "Selected four required question types", "conceptual, diagnostic, application, and code_review created.", ["cert_mapping"], 0.04),
            self.build_reasoning_step(2, "Bound questions to experiment evidence", f"Questions reference {exp.experiment_id}.", ["experiment_id", "metrics"], 0.04),
            self.build_reasoning_step(3, "Attached citations and skill domain", f"Target certification is {cert}.", ["cert_mapping.grounding"], 0.03),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("questions", len(questions), "assessment generated")], ctx.assessment.confidence, [citation])
        return ctx
