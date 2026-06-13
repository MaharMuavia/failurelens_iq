from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentName, EvidenceStrength, FailureCategory
from backend.models.schemas import AgentContext, DiagnosisResult
from backend.services.scoring_service import ScoringInputs


class DiagnosticAgent(BaseAgent):
    name = AgentName.DIAGNOSTIC

    def __init__(
        self,
        iq_provider: Any = None,
        scoring_service: Any = None,
        data_loader: Any = None,
        llm_reasoning_provider: Any = None,
    ) -> None:
        super().__init__(iq_provider, scoring_service, data_loader)
        self.llm_reasoning_provider = llm_reasoning_provider
        self.last_llm_result = None

    async def run(self, ctx: AgentContext) -> AgentContext:
        trace, started = self.start_trace()
        exp = ctx.experiment
        category = ctx.classification.failure_category if ctx.classification else FailureCategory.UNKNOWN
        query = f"{category.value} {exp.failure_observation} {exp.validation_strategy} {exp.class_balance} minority f1 fairness drift data quality"
        retrieval = await self.iq_provider.retrieve_failure_taxonomy(query, top_k=3)
        
        # Check LLM Reasoning
        llm_result = None
        if self.llm_reasoning_provider:
            llm_result = await self.llm_reasoning_provider.analyze_failure(exp, ctx.classification, retrieval, ctx.planner_context)
            self.last_llm_result = llm_result

        # Run scoring service
        planner_agreement = 1.0 if ctx.planner_context and ctx.planner_context.hypothesis.suspected_category == category else 0.0
        missing_penalty = len(ctx.intake_result.missing_critical_fields) / 6 if ctx.intake_result else 0.0
        
        orig_evidence = self._evidence(exp, category)
        orig_counter = self._counter_evidence(exp, category)
        
        score = self.scoring_service.compute(
            ScoringInputs(
                evidence_coverage=min(len(orig_evidence) / 5, 1.0),
                category_evidence=ctx.classification.confidence if ctx.classification else 0.0,
                metric_degradation=exp.metric_degradation_score,
                iq_relevance=retrieval.top_relevance,
                planner_agreement=planner_agreement,
                conflict_penalty=min(len(ctx.classification.conflicting_categories) * 0.2, 0.6) if ctx.classification else 0.0,
                missing_critical_fields_penalty=missing_penalty,
            )
        )
        threshold = ctx.planner_context.plan.dynamic_threshold if ctx.planner_context else 0.45

        if llm_result and llm_result.used_llm:
            root = llm_result.root_cause
            assumption = llm_result.violated_assumption
            gap = llm_result.knowledge_gap
            evidence = llm_result.evidence
            counter = llm_result.counter_evidence
            
            # Calibrate confidence
            final_confidence = round((llm_result.confidence + score.confidence) / 2.0, 4)
            requires_review = final_confidence < threshold or category == FailureCategory.UNKNOWN
            if requires_review:
                root = "Insufficient evidence to determine root cause with required confidence."
                assumption = "The available experiment record contains enough evidence for automated root-cause diagnosis."
                gap = "Evidence collection and review readiness before automated learning recommendations."
                
            reflections = [
                f"LLM Reasoning Provider: {llm_result.provider}",
                f"Evidence coverage check: {len(evidence)} direct evidence items were available from LLM.",
                f"Planner conflict check: planner agreement is {planner_agreement:.1f}.",
                f"Competing category check: conflicts are {ctx.classification.conflicting_categories if ctx.classification else []}.",
                f"IQ grounding strength check: top relevance is {retrieval.top_relevance:.3f}.",
                f"Confidence calibration check: LLM confidence {llm_result.confidence:.3f}, Scorer confidence {score.confidence:.3f}, Calibrated confidence {final_confidence:.3f} compared with threshold {threshold:.3f}.",
                f"Human review threshold check: review required is {requires_review}.",
            ]
            if retrieval.top_relevance < 0.35:
                reflections.append("Weak IQ grounding detected; confidence remains conservative.")
            
            steps = [
                self.build_reasoning_step(
                    number=1,
                    description="LLM checked experiment evidence",
                    finding=llm_result.reasoning_steps.get("evidence_check") or "Checked available experiment evidence.",
                    evidence_fields=["failure_observation", "classification"],
                    thought_type="evidence_check",
                ),
                self.build_reasoning_step(
                    number=2,
                    description="LLM inferred failure root cause",
                    finding=llm_result.reasoning_steps.get("inference") or llm_result.root_cause,
                    evidence_fields=["metrics", "validation_strategy"],
                    thought_type="inference",
                ),
                self.build_reasoning_step(
                    number=3,
                    description="LLM analyzed counter-evidence",
                    finding=llm_result.reasoning_steps.get("counter_evidence") or "Analyzed potential conflicts.",
                    evidence_fields=["baseline_metrics"],
                    thought_type="counter_evidence",
                ),
                self.build_reasoning_step(
                    number=4,
                    description="LLM assessed uncertainty and warnings",
                    finding=llm_result.reasoning_steps.get("uncertainty_check") or "Assessed model and taxonomy uncertainty.",
                    evidence_fields=["reflection_notes"],
                    thought_type="uncertainty_check",
                    uncertainty=llm_result.uncertainty,
                ),
                self.build_reasoning_step(
                    number=5,
                    description="LLM made final diagnostic decision",
                    finding=llm_result.reasoning_steps.get("decision") or f"Calibrated diagnosis at confidence {final_confidence:.3f}.",
                    evidence_fields=["planner_context.plan.dynamic_threshold"],
                    thought_type="decision",
                ),
                self.build_reasoning_step(
                    number=6,
                    description="LLM recommended next steps",
                    finding=llm_result.reasoning_steps.get("next_action") or llm_result.recommended_next_action,
                    evidence_fields=["recommended_next_actions"],
                    thought_type="next_action",
                    next_action=llm_result.recommended_next_action,
                ),
            ]
        else:
            evidence = orig_evidence
            counter = orig_counter
            root, assumption, gap = self._diagnosis_text(exp, category)
            final_confidence = score.confidence
            requires_review = final_confidence < threshold or category == FailureCategory.UNKNOWN
            if requires_review:
                root = "Insufficient evidence to determine root cause with required confidence."
                assumption = "The available experiment record contains enough evidence for automated root-cause diagnosis."
                gap = "Evidence collection and review readiness before automated learning recommendations."
            reflections = [
                f"Evidence coverage check: {len(evidence)} direct evidence items were available.",
                f"Planner conflict check: planner agreement is {planner_agreement:.1f}.",
                f"Competing category check: conflicts are {ctx.classification.conflicting_categories if ctx.classification else []}.",
                f"IQ grounding strength check: top relevance is {retrieval.top_relevance:.3f}.",
                f"Confidence calibration check: confidence {score.confidence:.3f} compared with threshold {threshold:.3f}.",
                f"Human review threshold check: review required is {requires_review}.",
            ]
            if retrieval.top_relevance < 0.35:
                reflections.append("Weak IQ grounding detected; confidence remains conservative.")
            steps = [
                self.build_reasoning_step(1, "Built grounded diagnostic query", query[:180], ["failure_observation", "classification"], 0.05),
                self.build_reasoning_step(2, "Retrieved local IQ grounding", f"Top relevance {retrieval.top_relevance:.3f}.", ["knowledge_index"], 0.08),
                self.build_reasoning_step(3, "Composed root-cause candidate", root, ["metrics", "validation_strategy"], 0.08),
                self.build_reasoning_step(4, "Checked counter-evidence", "; ".join(counter) or "No strong counter-evidence.", ["baseline_metrics", "deployment_context"], -0.02),
                self.build_reasoning_step(5, "Ran self-reflection checks", f"{len(reflections)} reflection notes recorded.", ["reflection_notes"], 0.0),
                self.build_reasoning_step(6, "Calibrated confidence against threshold", f"{score.confidence:.3f} vs {threshold:.3f}.", ["planner_context.plan.dynamic_threshold"], 0.0),
            ]

        ctx.diagnosis = DiagnosisResult(
            root_cause=root,
            violated_assumption=assumption,
            knowledge_gap=gap,
            evidence=evidence,
            counter_evidence=counter,
            hypothesis_conflict=planner_agreement < 1.0,
            reflection_notes=reflections,
            iq_retrieval=retrieval,
            confidence=final_confidence,
            evidence_strength=score.evidence_strength,
            requires_human_review=requires_review,
        )

        self.complete_trace(ctx, trace, started, steps, evidence or [self.cite_evidence("failure_observation", exp.failure_observation, "available diagnostic text")], final_confidence, [hit.citation for hit in retrieval.hits], counter, score.factors)
        ctx.requires_human_review = ctx.requires_human_review or requires_review
        if requires_review:
            ctx.human_review_reason = f"Diagnosis confidence {final_confidence:.3f} requires human review."
        return ctx

    def _evidence(self, exp, category: FailureCategory) -> list[str]:
        common = [self.cite_evidence("failure_observation", exp.failure_observation, "engineer observation")]
        if category == FailureCategory.EVALUATION_METHODOLOGY:
            return [
                self.cite_evidence("class_balance", exp.class_balance, "minority class risk"),
                self.cite_evidence("accuracy", exp.metrics.get("accuracy"), "headline metric can hide minority errors"),
                self.cite_evidence("minority_f1", exp.minority_f1, "minority performance weakness"),
                self.cite_evidence("validation_strategy", exp.validation_strategy, "holdout/non-stratified evidence"),
            ]
        if category == FailureCategory.RESPONSIBLE_AI:
            return common + [
                self.cite_evidence("metrics", exp.metrics, "group fairness evidence"),
                self.cite_evidence("engineer_notes", exp.engineer_notes, "responsible AI review signal"),
            ]
        if category == FailureCategory.DATA_LEAKAGE:
            return common + [self.cite_evidence("suspected_leakage_columns", exp.suspected_leakage_columns, "feature availability risk")]
        if category == FailureCategory.DEPLOYMENT_DRIFT:
            return common + [self.cite_evidence("drift_indicators", exp.drift_indicators, "production distribution shift")]
        if category == FailureCategory.DATA_QUALITY:
            return common + [self.cite_evidence("data_quality_signals", exp.data_quality_signals, "data contract risk")]
        if category == FailureCategory.FEATURE_ENGINEERING:
            return common + [self.cite_evidence("feature_set", exp.feature_set, "feature design signal")]
        return common if exp.failure_observation else []

    def _counter_evidence(self, exp, category: FailureCategory) -> list[str]:
        counter: list[str] = []
        if category != FailureCategory.DATA_LEAKAGE and not exp.suspected_leakage_columns:
            counter.append("suspected_leakage_columns=[] -> no direct leakage column evidence")
        if category != FailureCategory.DEPLOYMENT_DRIFT and not exp.drift_indicators:
            counter.append("drift_indicators=[] -> no direct deployment drift evidence")
        return counter

    def _diagnosis_text(self, exp, category: FailureCategory) -> tuple[str, str, str]:
        if category == FailureCategory.EVALUATION_METHODOLOGY:
            return (
                f"{exp.experiment_id} used {exp.validation_strategy} validation with class_balance={exp.class_balance}; accuracy={exp.metrics.get('accuracy')} hid minority_f1={exp.minority_f1}, so the evaluation method did not measure the failure mode that mattered.",
                "The reported accuracy represented operational quality for the minority class.",
                "Imbalanced classification evaluation, minority F1, and stratified validation practice.",
            )
        if category == FailureCategory.RESPONSIBLE_AI:
            return (
                f"{exp.experiment_id} contains protected attribute/fairness evidence with demographic parity or group metric weakness, indicating a responsible AI review gap.",
                "Aggregate model quality represented fairness across protected or demographic groups.",
                "Responsible AI fairness assessment, group metrics, and model card governance.",
            )
        if category == FailureCategory.DATA_LEAKAGE:
            return (f"{exp.experiment_id} includes leakage evidence from columns {exp.suspected_leakage_columns}.", "Validation features were available at prediction time.", "Feature availability and leakage prevention.")
        if category == FailureCategory.DEPLOYMENT_DRIFT:
            return (f"{exp.experiment_id} shows deployment or monitoring drift through {exp.drift_indicators}.", "Production distributions matched training and validation assumptions.", "Drift monitoring and deployment readiness.")
        if category == FailureCategory.DATA_QUALITY:
            return (f"{exp.experiment_id} shows data quality evidence through {exp.data_quality_signals}.", "Input data satisfied documented quality contracts.", "Data quality contracts and source-system checks.")
        if category == FailureCategory.FEATURE_ENGINEERING:
            return (f"{exp.experiment_id} points to feature engineering weakness in {exp.feature_set}.", "The feature representation captured the target signal reliably.", "Feature design, transformations, and ablation testing.")
        return ("Insufficient evidence to determine root cause with required confidence.", "Sufficient evidence existed.", "Evidence collection.")

