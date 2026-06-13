from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict
from backend.core.config import settings
import logging
from backend.models.experiment import ExperimentInput
from backend.models.analysis import FailureAnalysisResponse, UncertaintyBlock, CertificationGap, IQGrounding, AgentMetadata, ReasoningStep
from backend.models.schemas import ExperimentLog
from backend.services.foundry_agent_client import FoundryAgentClient
from backend.services.foundry_model_client import FoundryModelClient
from backend.services.json_parser import parse_and_validate_analysis

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are FailureLens IQ, an enterprise reasoning agent for diagnosing failed machine learning experiments.

Analyze failed ML experiment logs, metrics, configs, dataset summaries, and notes.

Return ONLY valid JSON matching the required schema.

Rules:
* Do not return markdown.
* Do not return text outside JSON.
* Do not give generic advice.
* Use the provided experiment evidence.
* Explain reasoning as concise structured steps, not hidden chain-of-thought.
* Clearly state uncertainty and missing information.
* Include IQ grounding based on known ML failure patterns.
* Map the failure to an enterprise learning or certification gap.

Required JSON keys:
failure_type, severity, confidence_score, reasoning_trace, evidence_used, root_causes, uncertainty, recommended_fixes, next_experiment_plan, certification_gap, iq_grounding, agent_metadata.
"""

class FailureLensService:
    def __init__(self) -> None:
        self.call_mode = settings.FOUNDRY_CALL_MODE
        self.agent_name = settings.AZURE_AI_AGENT_NAME
        self.model_deployment = settings.AZURE_AI_MODEL_DEPLOYMENT_NAME
        
        self.agent_client = FoundryAgentClient()
        self.model_client = FoundryModelClient()

    async def analyze(self, request: Any, payload: ExperimentInput) -> FailureAnalysisResponse:
        """
        Main entry point for analyzing a failed experiment.
        Runs the full orchestrator multi-agent reasoning pipeline.
        """
        exp_details = payload.experiment
        
        logger.info(
            "Starting unified analysis for experiment %s",
            exp_details.experiment_id
        )

        notes_lower = exp_details.notes.lower() if exp_details.notes else ""
        
        # Build ExperimentLog to match Orchestrator's schema
        exp = ExperimentLog(
            experiment_id=exp_details.experiment_id,
            team_id="demo-team",
            project_name="Loan disbursal evaluator" if "loan" in notes_lower else "Credit churn predictor" if "churn" in notes_lower else "Retention forecasting",
            role="ML Engineer",
            model_type=exp_details.model,
            dataset_name="churn_data.csv" if "churn" in notes_lower else "loan_data.csv" if "loan" in notes_lower else "retention_data.csv",
            pipeline_stage="evaluation",
            target="target",
            validation_strategy="k-fold cross validation" if "cross-val" in notes_lower else "random split",
            class_balance="88/12" if "imbalance" in notes_lower else "50/50",
            preprocessing_steps=["standard scaling"],
            feature_set=["f1", "f2"],
            metrics={
                "accuracy": exp_details.validation_accuracy,
                "validation_accuracy": exp_details.validation_accuracy,
                "train_accuracy": exp_details.train_accuracy,
                "test_accuracy": exp_details.test_accuracy,
                "minority_f1": 0.14 if "imbalance" in notes_lower or "f1" in notes_lower else 0.0,
            },
            baseline_metrics={
                "accuracy": 0.95,
                "validation_accuracy": 0.95,
                "train_accuracy": 0.95,
                "test_accuracy": 0.95,
            },
            error_logs=[],
            drift_indicators=[],
            data_quality_signals=[],
            training_config={},
            deployment_context={},
            failure_symptoms=[],
            failure_observation=exp_details.notes or "Model failed validation gate",
            suspected_leakage_columns=["timestamp"] if "leak" in notes_lower else [],
            engineer_notes=exp_details.notes or "",
            current_certifications=[],
            outcome="failure",
            timestamp=datetime.now(timezone.utc),
        )

        # Save to experiment store
        app_state = request.app.state
        await app_state.experiment_store.save_uploaded_experiment(exp)

        # Run orchestrator
        ctx = await app_state.orchestrator.run(exp)
        refs = []
        refs.extend(await app_state.grounding_adapter.retrieve_experiment_context(exp.experiment_id))
        refs.extend(await app_state.grounding_adapter.retrieve_historical_failures(
            ctx.diagnosis.knowledge_gap if ctx.diagnosis else "ml failure",
            top_k=5,
        ))
        source_types = {ref.source_type for ref in refs}

        # Map AgentContext back to FailureAnalysisResponse
        classification = ctx.classification
        diagnosis = ctx.diagnosis
        remediation = ctx.remediation
        cert_mapping = ctx.cert_mapping

        # Build reasoning trace steps
        reasoning_steps = []
        step_idx = 1
        for trace in ctx.agent_trace:
            if trace.status == "completed":
                for rstep in trace.reasoning_steps:
                    reasoning_steps.append(
                        ReasoningStep(
                            step=step_idx,
                            observation=rstep.description,
                            interpretation=rstep.finding,
                        )
                    )
                    step_idx += 1

        # Extract evidence_used
        evidence_used = []
        for trace in ctx.agent_trace:
            if trace.status == "completed" and trace.key_evidence:
                evidence_used.extend(trace.key_evidence)
        evidence_used = list(set(evidence_used))

        # Extract root causes
        root_causes = [diagnosis.root_cause] if diagnosis and diagnosis.root_cause else ["Root cause undetermined."]
        if diagnosis and diagnosis.violated_assumption:
            root_causes.append(f"Violated assumption: {diagnosis.violated_assumption}")

        # Uncertainty block
        missing_info = []
        alt_explanations = []
        level = "Medium"
        if diagnosis and diagnosis.reflection_notes:
            missing_info = diagnosis.reflection_notes
        if classification and classification.conflicting_categories:
            alt_explanations = [f"Possible alternative category: {c.value}" for c in classification.conflicting_categories]
            level = "High" if len(classification.conflicting_categories) > 1 else "Medium"

        uncertainty = UncertaintyBlock(
            level=level,
            missing_information=missing_info or ["No critical missing information identified."],
            alternative_explanations=alt_explanations or ["No alternative explanations found."],
        )

        # Recommended fixes
        fixes = []
        if remediation:
            fixes.extend(remediation.three_day_plan)
            fixes.extend(remediation.seven_day_plan)
        if not fixes:
            fixes = ["Review validation strategy."]

        # Next experiment plan
        next_plan = remediation.seven_day_plan if remediation else ["Audit train-test splits."]

        # Certification gap
        skill_gap = cert_mapping.skill_domain if cert_mapping else "ML Evaluation Strategy"
        recommended_learning = cert_mapping.recommended_cert if cert_mapping else "DP-100: Microsoft Azure Data Scientist"
        certification_gap = CertificationGap(
            skill_gap=skill_gap,
            recommended_learning=recommended_learning,
        )

        # IQ Grounding
        knowledge_sources = []
        matched_patterns = []
        if classification and classification.grounding_citations:
            knowledge_sources.extend(classification.grounding_citations)
        if diagnosis and diagnosis.reflection_notes:
            matched_patterns.extend(diagnosis.reflection_notes)

        iq_grounding = IQGrounding(
            knowledge_sources_used=list(set(knowledge_sources)) or ["failure_taxonomy.md"],
            matched_failure_patterns=list(set(matched_patterns)) or [classification.failure_category.value if classification else "ML Failure"],
            grounding_confidence=int((classification.confidence if classification else 0.8) * 100),
        )

        # Agent metadata
        call_mode = settings.FOUNDRY_CALL_MODE
        active_reasoning_provider = "deterministic_fallback"
        if diagnosis and diagnosis.reflection_notes:
            for note in diagnosis.reflection_notes:
                if "LLM Reasoning Provider: AzureOpenAI" in note:
                    call_mode = "model"
                    active_reasoning_provider = "azure_openai"
                    break
                elif "LLM Reasoning Provider: MicrosoftFoundryOpenAI" in note:
                    call_mode = "model"
                    active_reasoning_provider = "foundry_openai"
                    break
                elif "LLM Reasoning Provider: MicrosoftFoundryAgent" in note:
                    call_mode = "agent"
                    active_reasoning_provider = "foundry_agent"
                    break
                elif "LLM Reasoning Provider: OpenAI" in note:
                    call_mode = "model"
                    active_reasoning_provider = "openai"
                    break

        agent_metadata = AgentMetadata(
            call_mode=call_mode,
            agent_name=settings.FOUNDRY_AGENT_NAME or settings.AZURE_AI_AGENT_NAME,
            model_deployment=settings.FOUNDRY_MODEL_DEPLOYMENT or settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
            schema_version="1.0",
        )

        azure_ai_search_used = "azure_ai_search" in source_types
        microsoft_reasoning_used = active_reasoning_provider in {"azure_openai", "foundry_openai", "foundry_agent"}
        if azure_ai_search_used and microsoft_reasoning_used:
            proof_level = "live_azure_foundry"
        elif microsoft_reasoning_used:
            proof_level = "foundry_model_live_without_search"
        elif azure_ai_search_used:
            proof_level = "azure_search_live_with_local_reasoning"
        else:
            proof_level = "local_foundry_iq_adapter"
        warnings = list(getattr(app_state.grounding_adapter, "warnings", []))
        if not azure_ai_search_used:
            warnings.append("Azure AI Search was not used for this run; live Microsoft IQ is false.")

        return FailureAnalysisResponse(
            failure_type=classification.failure_category.value if classification else "Unknown",
            severity="Critical" if classification and classification.failure_category.value in ("Data Leakage", "Responsible AI") else "High",
            confidence_score=int((ctx.overall_confidence or 0.8) * 100),
            reasoning_trace=reasoning_steps,
            evidence_used=evidence_used,
            root_causes=root_causes,
            uncertainty=uncertainty,
            recommended_fixes=fixes,
            next_experiment_plan=next_plan,
            certification_gap=certification_gap,
            iq_grounding=iq_grounding,
            agent_metadata=agent_metadata,
            active_reasoning_provider=active_reasoning_provider,
            active_grounding_provider="azure_ai_search" if azure_ai_search_used else "local_iq",
            proof_level=proof_level,
            live_microsoft_iq=azure_ai_search_used,
            azure_ai_search_used_this_run=azure_ai_search_used,
            foundry_model_used_this_run=microsoft_reasoning_used,
            warnings=warnings,
        )
