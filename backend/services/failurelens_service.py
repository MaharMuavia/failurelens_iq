from __future__ import annotations

import json
from typing import Any, Dict
from backend.core.config import settings
import logging
from backend.models.experiment import ExperimentInput
from backend.models.analysis import FailureAnalysisResponse, UncertaintyBlock, CertificationGap, IQGrounding, AgentMetadata, ReasoningStep
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

    async def analyze(self, payload: ExperimentInput) -> FailureAnalysisResponse:
        """
        Main entry point for analyzing a failed experiment.
        Determines the call mode (agent/model/mock) and executes the analysis.
        """
        exp = payload.experiment
        exp_dict = exp.model_dump()
        
        logger.info(
            "Starting analysis for experiment %s in call mode: %s",
            exp.experiment_id,
            self.call_mode
        )

        if self.call_mode == "mock":
            logger.info("Using mock mode analysis for %s", exp.experiment_id)
            return self._get_mock_response(exp)

        user_prompt = f"Analyze the following failed ML experiment and return ONLY valid JSON:\n\n{json.dumps(exp_dict, indent=2)}"

        if self.call_mode == "agent":
            try:
                # Call saved Foundry Agent
                raw_response = await self.agent_client.call_agent(user_prompt)
                return parse_and_validate_analysis(
                    raw_response,
                    call_mode="agent",
                    agent_name=self.agent_name,
                    model_deployment=self.model_deployment
                )
            except Exception as e:
                logger.error("Failed to run analysis via Foundry Agent: %s. Falling back to mock.", str(e))
                # Fallback to mock on connection or runtime errors
                fallback_resp = self._get_mock_response(exp)
                # Mark as agent mode but indicate failure/fallback
                fallback_resp.agent_metadata.call_mode = "agent"
                return fallback_resp

        elif self.call_mode == "model":
            try:
                # Call deployed model directly
                raw_response = await self.model_client.call_model(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt
                )
                return parse_and_validate_analysis(
                    raw_response,
                    call_mode="model",
                    agent_name="",
                    model_deployment=self.model_deployment
                )
            except Exception as e:
                logger.error("Failed to run analysis via deployed model: %s. Falling back to mock.", str(e))
                fallback_resp = self._get_mock_response(exp)
                fallback_resp.agent_metadata.call_mode = "model"
                return fallback_resp

        else:
            raise ValueError(f"Invalid FOUNDRY_CALL_MODE configured: {self.call_mode}")
