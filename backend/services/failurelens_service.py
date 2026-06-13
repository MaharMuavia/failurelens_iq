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

    def _get_mock_response(self, exp: Any) -> FailureAnalysisResponse:
        """
        Generates a realistic mock analysis based on experiment input.
        """
        # Determine case type from model name or notes
        model_name = getattr(exp, "model", "").lower()
        notes = getattr(exp, "notes", "").lower()
        train_acc = getattr(exp, "train_accuracy", 0.0)
        val_acc = getattr(exp, "validation_accuracy", 0.0)
        test_acc = getattr(exp, "test_accuracy", 0.0)
        
        # 1. Overfitting case
        if "overfit" in notes or (train_acc > 0.9 and val_acc < 0.75):
            return FailureAnalysisResponse(
                failure_type="Overfitting",
                severity="Critical",
                confidence_score=88,
                reasoning_trace=[
                    ReasoningStep(
                        step=1,
                        observation=f"Train accuracy ({train_acc}) is drastically higher than validation ({val_acc}) and test ({test_acc})",
                        interpretation="Classic sign of high-variance model that memorizes training data but fails to generalize."
                    ),
                    ReasoningStep(
                        step=2,
                        observation=f"Dataset has {getattr(exp, 'dataset_size', 2000)} samples with {getattr(exp, 'feature_count', 120)} features using default {getattr(exp, 'model', 'RandomForestClassifier')} hyperparameters",
                        interpretation="Model capacity greatly exceeds data complexity; unconstrained trees exploit noise in high-dimensional space."
                    ),
                    ReasoningStep(
                        step=3,
                        observation="No cross-validation, no feature selection, and no regularization were applied",
                        interpretation="Absence of standard anti-overfitting practices allowed spurious correlations to dominate learning."
                    )
                ],
                evidence_used=[
                    f"{round((train_acc - val_acc) * 100)}-point train-validation accuracy gap",
                    f"High-dimensional feature space: {getattr(exp, 'feature_count', 120)} features for {getattr(exp, 'dataset_size', 2000)} samples",
                    f"Default sklearn {getattr(exp, 'model', 'RandomForestClassifier')} parameters such as unlimited depth and min_samples_leaf=1",
                    "Explicit lack of cross-validation and feature selection in experiment notes"
                ],
                root_causes=[
                    "Excessive model capacity from unconstrained decision trees",
                    "High dimensionality without feature selection",
                    "Lack of regularization and proper validation methodology"
                ],
                uncertainty=UncertaintyBlock(
                    level="Low",
                    missing_information=[
                        "Class distribution and potential imbalance",
                        "Nature of features: categorical versus continuous",
                        "Data collection and splitting methodology"
                    ],
                    alternative_explanations=[
                        "Possible heavy label noise in validation or test sets",
                        "Non-representative train, validation, or test splits"
                    ]
                ),
                recommended_fixes=[
                    "Tune regularization hyperparameters such as max_depth, min_samples_leaf, max_features, and ccp_alpha using cross-validation",
                    "Perform feature selection using permutation importance, Boruta, or recursive feature elimination",
                    "Switch from a single validation split to k-fold cross-validation",
                    "Add constraints such as min_samples_leaf >= 5 and max_depth limits"
                ],
                next_experiment_plan=[
                    "Run Optuna or RandomizedSearchCV with 5-fold cross-validation focused on regularization parameters",
                    "Conduct feature selection and retrain the baseline model",
                    "Compare regularized Random Forest against simpler models such as logistic regression with feature selection",
                    "Analyze feature importances and validation error patterns"
                ],
                certification_gap=CertificationGap(
                    skill_gap="Weak understanding of Random Forest regularization techniques and rigorous experimental validation practices",
                    recommended_learning="Study ensemble regularization, cross-validation, and systematic ablation studies for tabular ML experiments."
                ),
                iq_grounding=IQGrounding(
                    knowledge_sources_used=[
                        "ml_failure_patterns.md",
                        "certification_rubric.md",
                        "enterprise_ml_playbook.md"
                    ],
                    matched_failure_patterns=[
                        "overfitting",
                        "high variance",
                        "insufficient validation protocol"
                    ],
                    grounding_confidence=90
                ),
                agent_metadata=AgentMetadata(
                    call_mode="mock",
                    agent_name=self.agent_name,
                    model_deployment=self.model_deployment,
                    schema_version="1.0"
                )
            )
            
        # 2. Data Leakage case
        elif "leak" in notes or "timestamp" in notes or (train_acc > 0.95 and val_acc > 0.95 and test_acc < 0.6):
            return FailureAnalysisResponse(
                failure_type="Data Leakage",
                severity="Critical",
                confidence_score=92,
                reasoning_trace=[
                    ReasoningStep(
                        step=1,
                        observation="Extremely high training accuracy (0.99) and validation accuracy (0.98) but very low test accuracy (0.52)",
                        interpretation="Indicates target information is leaking into features, which are available during training/validation but missing or scrambled in the test split."
                    ),
                    ReasoningStep(
                        step=2,
                        observation="Notes mention a feature derived from target timestamp",
                        interpretation="Temporal features containing future target context violate causal ordering, leading to artificial score inflation."
                    )
                ],
                evidence_used=[
                    "Discrepancy of 46% accuracy between validation and test sets",
                    "Feature timestamp leakage mentioned in experiment notes",
                    "Perfect training-time performance on a complex problem"
                ],
                root_causes=[
                    "Temporal target leakage: feature depends on future values of the target variable",
                    "Lack of strict chronologically stratified splitting validation"
                ],
                uncertainty=UncertaintyBlock(
                    level="Low",
                    missing_information=["Full feature list and preprocessing pipeline definitions"],
                    alternative_explanations=["Severe distribution shift in test set features"]
                ),
                recommended_fixes=[
                    "Remove timestamp-derived target features from training set",
                    "Enforce strict out-of-time validation or temporal train-test splits",
                    "Audit preprocessing pipelines to ensure no statistics from validation/test sets leak into training"
                ],
                next_experiment_plan=[
                    "Retrain Logistic Regression baseline with timestamp feature removed",
                    "Configure MLflow tracker to monitor feature target correlation metrics",
                    "Conduct a data timeline audit to verify feature causality"
                ],
                certification_gap=CertificationGap(
                    skill_gap="Data validation and leakage prevention methodology",
                    recommended_learning="Review feature engineering best practices, data leakage detection guidelines, and time-series cross-validation."
                ),
                iq_grounding=IQGrounding(
                    knowledge_sources_used=[
                        "ml_failure_patterns.md",
                        "certification_rubric.md"
                    ],
                    matched_failure_patterns=["data leakage", "temporal split violation"],
                    grounding_confidence=95
                ),
                agent_metadata=AgentMetadata(
                    call_mode="mock",
                    agent_name=self.agent_name,
                    model_deployment=self.model_deployment,
                    schema_version="1.0"
                )
            )

        # 3. Class Imbalance case
        elif "imbalance" in notes or "recall" in notes or "split" in notes:
            return FailureAnalysisResponse(
                failure_type="Class Imbalance",
                severity="High",
                confidence_score=85,
                reasoning_trace=[
                    ReasoningStep(
                        step=1,
                        observation="High overall accuracies (train=0.95, val=0.93) but recall on minority class is extremely low (0.12)",
                        interpretation="Classic symptom of class imbalance where the model predicts the majority class to maximize accuracy while neglecting the minority class."
                    ),
                    ReasoningStep(
                        step=2,
                        observation="Notes state a 95/5 class split in the dataset",
                        interpretation="Extreme class imbalance dominates loss function gradients, causing model to fail to learn minority class patterns."
                    )
                ],
                evidence_used=[
                    "Minority class recall is 0.12",
                    "95/5 target class imbalance split",
                    "High overall classification accuracy (0.95) despite poor recall"
                ],
                root_causes=[
                    "Target distribution imbalance causing majority-class bias",
                    "Use of overall accuracy as primary optimization metric instead of F1 or Recall"
                ],
                uncertainty=UncertaintyBlock(
                    level="Medium",
                    missing_information=["Minority class sample features", "Precision score metrics"],
                    alternative_explanations=["Lack of feature representation for minority class samples"]
                ),
                recommended_fixes=[
                    "Use class weights (class_weight='balanced') in model initialization",
                    "Switch evaluation metrics to Stratified F1-score, Precision-Recall AUC, or Balanced Accuracy",
                    "Apply SMOTE over-sampling or down-sampling techniques using imbalanced-learn pipelines"
                ],
                next_experiment_plan=[
                    "Retrain SVM using balanced class weights",
                    "Generate Precision-Recall curve to determine optimal classification threshold",
                    "Implement Stratified K-Fold cross-validation to maintain class ratios"
                ],
                certification_gap=CertificationGap(
                    skill_gap="Imbalanced data handling techniques and appropriate metric selection",
                    recommended_learning="Study imbalanced classification methods, cost-sensitive learning, and class weighting."
                ),
                iq_grounding=IQGrounding(
                    knowledge_sources_used=[
                        "ml_failure_patterns.md",
                        "certification_rubric.md"
                    ],
                    matched_failure_patterns=["class imbalance", "metric mismatch"],
                    grounding_confidence=88
                ),
                agent_metadata=AgentMetadata(
                    call_mode="mock",
                    agent_name=self.agent_name,
                    model_deployment=self.model_deployment,
                    schema_version="1.0"
                )
            )

        # 4. Default / Underfitting case
        else:
            return FailureAnalysisResponse(
                failure_type="Underfitting",
                severity="High",
                confidence_score=80,
                reasoning_trace=[
                    ReasoningStep(
                        step=1,
                        observation=f"Low accuracy across all splits (train={train_acc}, val={val_acc}, test={test_acc})",
                        interpretation="Model has high bias and is too simple to capture the underlying relationships or patterns in the data."
                    ),
                    ReasoningStep(
                        step=2,
                        observation="Linear model used on highly non-linear data with only 8 features",
                        interpretation="Insufficient model capacity and lack of non-linear transformations prevent proper learning."
                    )
                ],
                evidence_used=[
                    "Low training accuracy (0.52)",
                    "Minimal difference between training and validation accuracy",
                    "Simple model choice for non-linear data"
                ],
                root_causes=[
                    "Inadequate model capacity (underparameterized model)",
                    "Insufficient feature representation or engineering"
                ],
                uncertainty=UncertaintyBlock(
                    level="Medium",
                    missing_information=["Feature engineering details", "Actual distribution of target variable"],
                    alternative_explanations=["Extremely high level of noise in features or labels"]
                ),
                recommended_fixes=[
                    "Increase model capacity by switching to a non-linear model (e.g., Random Forest, XGBoost, Neural Net)",
                    "Perform feature engineering (e.g. polynomial features, interactions)",
                    "Review features to identify additional predictive signals"
                ],
                next_experiment_plan=[
                    "Train a baseline Gradient Boosting classifier/regressor",
                    "Add polynomial features and interaction terms to linear baseline"
                ],
                certification_gap=CertificationGap(
                    skill_gap="Model capacity selection and feature engineering principles",
                    recommended_learning="Study bias-variance tradeoff, non-linear machine learning models, and advanced feature engineering."
                ),
                iq_grounding=IQGrounding(
                    knowledge_sources_used=[
                        "ml_failure_patterns.md",
                        "certification_rubric.md"
                    ],
                    matched_failure_patterns=["underfitting", "insufficient model capacity"],
                    grounding_confidence=85
                ),
                agent_metadata=AgentMetadata(
                    call_mode="mock",
                    agent_name=self.agent_name,
                    model_deployment=self.model_deployment,
                    schema_version="1.0"
                )
            )

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
        if diagnosis and diagnosis.uncertainty:
            missing_info = diagnosis.uncertainty
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
        if diagnosis and diagnosis.reflection_notes:
            for note in diagnosis.reflection_notes:
                if "LLM Reasoning Provider: AzureOpenAI" in note:
                    call_mode = "model"
                    break
                elif "LLM Reasoning Provider: MicrosoftFoundryOpenAI" in note:
                    call_mode = "model"
                    break
                elif "LLM Reasoning Provider: MicrosoftFoundryAgent" in note:
                    call_mode = "agent"
                    break

        agent_metadata = AgentMetadata(
            call_mode=call_mode,
            agent_name=settings.FOUNDRY_AGENT_NAME or settings.AZURE_AI_AGENT_NAME,
            model_deployment=settings.FOUNDRY_MODEL_DEPLOYMENT or settings.AZURE_AI_MODEL_DEPLOYMENT_NAME,
            schema_version="1.0",
        )

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
        )
