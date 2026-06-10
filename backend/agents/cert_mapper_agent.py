from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName, FailureCategory
from backend.models.schemas import AgentContext, CertMappingResult


CERTS = {
    "dp100": ("DP-100", "DP-100: Designing and Implementing a Data Science Solution on Azure", "ML evaluation and model operations"),
    "ai102": ("AI-102", "AI-102: Designing and Implementing a Microsoft Azure AI Solution", "Responsible AI and fairness"),
    "dp203": ("DP-203", "DP-203: Data Engineering on Microsoft Azure", "Data quality and pipeline reliability"),
    "pl300": ("PL-300", "PL-300: Microsoft Power BI Data Analyst", "Manager analytics and dashboard interpretation"),
}


class CertMapperAgent(BaseAgent):
    name = AgentName.CERT_MAPPER

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        category = ctx.classification.failure_category if ctx.classification else FailureCategory.UNKNOWN
        query = f"{category.value} {ctx.diagnosis.knowledge_gap if ctx.diagnosis else ''} certification skill guide"
        retrieval = await self.iq_provider.retrieve(query, top_k=3)
        top_file = retrieval.hits[0].source_file.lower() if retrieval.hits else ""
        if "responsible" in query.lower() or category == FailureCategory.RESPONSIBLE_AI:
            top_file = "ai102_skill_guide.md"
        elif category in {FailureCategory.DATA_QUALITY}:
            top_file = "dp203_skill_guide.md"
        elif category in {FailureCategory.EVALUATION_METHODOLOGY, FailureCategory.DATA_LEAKAGE, FailureCategory.DEPLOYMENT_DRIFT, FailureCategory.FEATURE_ENGINEERING} and not top_file:
            top_file = "dp100_skill_guide.md"
        key = "ai102" if "ai102" in top_file else "dp203" if "dp203" in top_file else "pl300" if "pl300" in top_file else "dp100"
        cert_code, recommended, domain = CERTS[key]
        already_held = cert_code in exp.current_certifications
        fallback_cert = None
        fallback_reason = None
        if already_held:
            fallback_cert = "AI-102" if cert_code == "DP-100" and category == FailureCategory.RESPONSIBLE_AI else "PL-300"
            fallback_reason = f"Team already holds {cert_code}; use an advanced applied learning path."
        fallback_used = retrieval.top_relevance < 0.35
        confidence = 0.32 if fallback_used else max(0.45, min(0.86, retrieval.top_relevance + 0.25))
        ctx.cert_mapping = CertMappingResult(
            recommended_cert=recommended,
            cert_code=cert_code,
            skill_domain=domain,
            already_held=already_held,
            fallback_cert=fallback_cert,
            fallback_reason=fallback_reason,
            learning_path=[
                f"Review {domain} concepts using local IQ citations.",
                f"Apply the concepts to {exp.experiment_id} evidence fields.",
                "Add the resulting checklist item to the next experiment review.",
            ],
            fallback_used=fallback_used,
            grounding=[hit.citation for hit in retrieval.hits] or [f"{top_file} § certification mapping"],
            confidence=round(confidence, 4),
        )
        steps = [
            self.build_reasoning_step(1, "Retrieved certification grounding", f"Top source was {top_file or 'weak retrieval'}.", ["iq_retrieval"], 0.08),
            self.build_reasoning_step(2, "Mapped source to certification", f"Selected {cert_code}.", ["source_file"], 0.1),
            self.build_reasoning_step(3, "Checked existing certifications", f"Already held: {already_held}.", ["current_certifications"], -0.02 if already_held else 0.02),
        ]
        self.complete_trace(ctx, trace, started, steps, [self.cite_evidence("cert_code", cert_code, "recommended skill path")], ctx.cert_mapping.confidence, ctx.cert_mapping.grounding)
        return ctx
