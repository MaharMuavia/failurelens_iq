from __future__ import annotations
import re
import json
import logging
from datetime import datetime, timezone
from typing import Any, Tuple

from backend.models.schemas import ExperimentLog
from backend.services.foundry_openai_client import FoundryOpenAIClient
from backend.services.json_parser import clean_and_extract_json

logger = logging.getLogger(__name__)

class PromptExperimentBuilder:
    async def build(self, prompt: str, foundry_openai_client: FoundryOpenAIClient | None = None) -> Tuple[ExperimentLog, dict[str, Any]]:
        # Check if we should use Foundry model
        use_foundry = foundry_openai_client is not None and foundry_openai_client.enabled
        
        if use_foundry:
            try:
                log, metadata = await self._build_with_foundry(prompt, foundry_openai_client)
                return log, metadata
            except Exception as e:
                logger.warning(f"Foundry model parsing failed, falling back to deterministic: {e}")
                # Fall back to deterministic
        
        return self._build_deterministic(prompt)

    async def _build_with_foundry(self, prompt: str, client: FoundryOpenAIClient) -> Tuple[ExperimentLog, dict[str, Any]]:
        system_prompt = (
            "You are a structured ML metadata extractor. Convert a natural-language description of a failed ML experiment "
            "into a JSON object matching the Pydantic schema of an ML experiment log. "
            "Be precise. Identify fields that are explicitly mentioned in the prompt, and for any fields that are missing, "
            "generate realistic values (assumptions) based on the context. "
            "Do NOT pretend assumptions came from the user. Any assumed fields must be listed in metadata. "
            "Your output MUST be a JSON object with the following structure:\n"
            "{\n"
            '  "project_name": "Inferred or generated project name",\n'
            '  "model_type": "Inferred model type",\n'
            '  "dataset_name": "Inferred dataset name",\n'
            '  "pipeline_stage": "Inferred stage (e.g. validation)",\n'
            '  "target": "Inferred target label (e.g. target)",\n'
            '  "validation_strategy": "Inferred validation strategy",\n'
            '  "class_balance": "Inferred class balance (e.g. 90/10)",\n'
            '  "preprocessing_steps": ["step1", "step2"],\n'
            '  "feature_set": ["feat1", "feat2"],\n'
            '  "metrics": {"metric_name": value},\n'
            '  "baseline_metrics": {"metric_name": value},\n'
            '  "error_logs": ["log line"],\n'
            '  "drift_indicators": ["drift indicator"],\n'
            '  "data_quality_signals": ["data quality signal"],\n'
            '  "training_config": {},\n'
            '  "deployment_context": {},\n'
            '  "failure_symptoms": ["symptom1"],\n'
            '  "failure_observation": "Detailed failure observation",\n'
            '  "suspected_leakage_columns": ["col1"],\n'
            '  "engineer_notes": "Generated notes",\n'
            '  "current_certifications": ["AI-900"],\n'
            '  "failure_category_label": null,\n'
            '  "prompt_extraction": {\n'
            '    "explicit_fields": ["list of fields explicitly present in the prompt"],\n'
            '    "assumed_fields": ["list of fields generated as assumptions"],\n'
            '    "confidence": 0.9\n'
            '  }\n'
            "}\n"
            "DO NOT return markdown code blocks or any other explanation."
        )
        
        response = await client.chat_completion_raw(system_prompt, f"User Prompt: {prompt}")
        if not response.get("ok"):
            raise ValueError(f"Foundry OpenAI failed: {response.get('detail')}")
        
        content = response.get("content", "")
        parsed = clean_and_extract_json(content)
        if not parsed:
            raise ValueError("Failed to extract JSON from Foundry OpenAI response")
            
        # Extract prompt_extraction metadata if it exists
        pe_metadata = parsed.pop("prompt_extraction", None)
        if not pe_metadata or not isinstance(pe_metadata, dict):
            pe_metadata = {
                "explicit_fields": ["failure_observation"],
                "assumed_fields": [],
                "confidence": 0.7
            }
            
        # Ensure generated fields are strictly set/overwritten per rules
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        parsed["experiment_id"] = f"PROMPT-{timestamp_str}"
        parsed["team_id"] = "demo-team"
        parsed["role"] = "ML Engineer"
        parsed["outcome"] = "failure"
        parsed["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Append assumption note if any fields are assumed
        notes = parsed.get("engineer_notes", "")
        assumption_note = "Generated from user prompt with assumptions."
        if assumption_note not in notes:
            parsed["engineer_notes"] = f"{assumption_note} {notes}".strip()
            
        # Validate using Pydantic ExperimentLog
        log = ExperimentLog.model_validate(parsed)
        return log, {"prompt_extraction": pe_metadata}

    def _build_deterministic(self, prompt: str) -> Tuple[ExperimentLog, dict[str, Any]]:
        # Lowercase prompt for keyword matching
        lowered = prompt.lower()
        
        # Fields tracking
        explicit_fields = ["failure_observation", "outcome", "role", "team_id", "experiment_id", "timestamp"]
        assumed_fields = []
        
        # 1. Project Name
        if "churn" in lowered:
            project_name = "Customer Churn Prediction"
            explicit_fields.append("project_name")
        elif "loan" in lowered:
            project_name = "Loan Risk Assessment"
            explicit_fields.append("project_name")
        elif "fraud" in lowered:
            project_name = "Fraud Detection Pipeline"
            explicit_fields.append("project_name")
        elif "overfitting" in lowered:
            project_name = "Regularized Classifier Experiment"
            explicit_fields.append("project_name")
        else:
            project_name = "ML Experimentation Model"
            assumed_fields.append("project_name")
            
        # 2. Model Type
        if "random forest" in lowered or "randomforest" in lowered:
            model_type = "Random Forest"
            explicit_fields.append("model_type")
        elif "xgboost" in lowered or "xgb" in lowered:
            model_type = "XGBoost"
            explicit_fields.append("model_type")
        elif "lightgbm" in lowered or "lgbm" in lowered:
            model_type = "LightGBM"
            explicit_fields.append("model_type")
        elif "logistic" in lowered:
            model_type = "Logistic Regression"
            explicit_fields.append("model_type")
        elif "neural" in lowered or "deep learning" in lowered:
            model_type = "Deep Neural Network"
            explicit_fields.append("model_type")
        else:
            model_type = "XGBoost Classifier"
            assumed_fields.append("model_type")
            
        # 3. Dataset Name
        if "churn" in lowered:
            dataset_name = "customer_churn_data"
            explicit_fields.append("dataset_name")
        elif "loan" in lowered:
            dataset_name = "loan_applications"
            explicit_fields.append("dataset_name")
        elif "fraud" in lowered:
            dataset_name = "transactions_fraud"
            explicit_fields.append("dataset_name")
        else:
            dataset_name = "model_training_dataset"
            assumed_fields.append("dataset_name")
            
        # 4. Target
        if "churn" in lowered:
            target = "churn_status"
            explicit_fields.append("target")
        elif "loan" in lowered:
            target = "default_risk"
            explicit_fields.append("target")
        elif "fraud" in lowered:
            target = "is_fraud"
            explicit_fields.append("target")
        else:
            target = "target_label"
            assumed_fields.append("target")
            
        # 5. Validation Strategy
        if "cross validation" in lowered or "k-fold" in lowered or "kfold" in lowered:
            validation_strategy = "5-fold Cross Validation"
            explicit_fields.append("validation_strategy")
        else:
            validation_strategy = "Train-Test Split (80/20)"
            assumed_fields.append("validation_strategy")
            
        # 6. Class Balance
        class_balance = "50/50"
        if "90/10" in lowered:
            class_balance = "90/10"
            explicit_fields.append("class_balance")
        elif "95/5" in lowered:
            class_balance = "95/5"
            explicit_fields.append("class_balance")
        elif "80/20" in lowered:
            class_balance = "80/20"
            explicit_fields.append("class_balance")
        elif "imbalance" in lowered or "minority" in lowered:
            class_balance = "90/10"
            assumed_fields.append("class_balance")
        else:
            assumed_fields.append("class_balance")
            
        # 7. Metrics parsing
        accuracy_val = 0.93
        accuracy_match = re.search(r"(?:accuracy|acc)\s*(?:of|reached|dropped to|is)?\s*(\d+(?:\.\d+)?)\s*%?", lowered)
        if not accuracy_match:
            accuracy_match = re.search(r"(\d+(?:\.\d+)?)\s*%?\s*(?:accuracy|acc)", lowered)
            
        if accuracy_match:
            val_str = accuracy_match.group(1)
            try:
                val = float(val_str)
                if "%" in accuracy_match.group(0) or val > 1.0:
                    val /= 100.0
                accuracy_val = val
                explicit_fields.append("metrics")
            except ValueError:
                assumed_fields.append("metrics")
        else:
            assumed_fields.append("metrics")
            
        minority_f1_val = 0.14
        f1_match = re.search(r"(?:minority f1|f1 minority|f1 score|f1)\s*(?:of|dropped to|is)?\s*(\d+(?:\.\d+)?)\s*%?", lowered)
        if not f1_match:
            f1_match = re.search(r"(\d+(?:\.\d+)?)\s*%?\s*(?:minority f1|f1 minority|f1 score|f1)", lowered)
            
        if f1_match:
            val_str = f1_match.group(1)
            try:
                val = float(val_str)
                if "%" in f1_match.group(0) or val > 1.0:
                    val /= 100.0
                minority_f1_val = val
                explicit_fields.append("metrics")
            except ValueError:
                pass
        
        metrics = {"accuracy": accuracy_val, "minority_f1": minority_f1_val}
        baseline_metrics = {"accuracy": min(0.99, accuracy_val + 0.02), "minority_f1": max(0.65, minority_f1_val + 0.50)}
        assumed_fields.append("baseline_metrics")
        
        # 8. Drift indicators
        drift_indicators = []
        if "drift" in lowered:
            drift_indicators.append("Feature drift detected in validation set")
            explicit_fields.append("drift_indicators")
        else:
            assumed_fields.append("drift_indicators")
            
        # 9. Leakage
        suspected_leakage_columns = []
        if "leakage" in lowered or "leak" in lowered:
            suspected_leakage_columns.append("target_leakage_col")
            explicit_fields.append("suspected_leakage_columns")
        else:
            assumed_fields.append("suspected_leakage_columns")
            
        # 10. Symptoms
        failure_symptoms = []
        if "overfitting" in lowered or "overfit" in lowered:
            failure_symptoms.append("overfitting_detected")
            explicit_fields.append("failure_symptoms")
        elif "drift" in lowered:
            failure_symptoms.append("data_drift_symptom")
            explicit_fields.append("failure_symptoms")
        elif "leakage" in lowered or "leak" in lowered:
            failure_symptoms.append("data_leakage_symptom")
            explicit_fields.append("failure_symptoms")
        elif "imbalance" in lowered or "minority" in lowered:
            failure_symptoms.append("low_minority_f1")
            explicit_fields.append("failure_symptoms")
        else:
            failure_symptoms.append("unexpected_performance_drop")
            assumed_fields.append("failure_symptoms")
            
        # 11. Data Quality Signals
        data_quality_signals = []
        if "noisy" in lowered or "noise" in lowered:
            data_quality_signals.append("High level of noisy labels in minority class")
            explicit_fields.append("data_quality_signals")
        else:
            assumed_fields.append("data_quality_signals")
            
        preprocessing_steps = ["StandardScaler", "OneHotEncoder"]
        feature_set = ["feature_1", "feature_2", "feature_3"]
        training_config = {"max_depth": 6, "learning_rate": 0.1}
        deployment_context = {"environment": "staging"}
        current_certifications = []
        assumed_fields.extend([
            "preprocessing_steps", "feature_set", "training_config",
            "deployment_context", "current_certifications"
        ])
        
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
        
        log_data = {
            "experiment_id": f"PROMPT-{timestamp_str}",
            "team_id": "demo-team",
            "project_name": project_name,
            "role": "ML Engineer",
            "model_type": model_type,
            "dataset_name": dataset_name,
            "pipeline_stage": "validation",
            "target": target,
            "validation_strategy": validation_strategy,
            "class_balance": class_balance,
            "preprocessing_steps": preprocessing_steps,
            "feature_set": feature_set,
            "metrics": metrics,
            "baseline_metrics": baseline_metrics,
            "error_logs": [],
            "drift_indicators": drift_indicators,
            "data_quality_signals": data_quality_signals,
            "training_config": training_config,
            "deployment_context": deployment_context,
            "failure_symptoms": failure_symptoms,
            "failure_observation": prompt,
            "suspected_leakage_columns": suspected_leakage_columns,
            "engineer_notes": "Generated from user prompt with assumptions.",
            "current_certifications": current_certifications,
            "outcome": "failure",
            "failure_category_label": None,
            "timestamp": timestamp,
        }
        
        # Calculate confidence
        confidence = 0.5 + (0.05 * len(set(explicit_fields).difference({"outcome", "role", "team_id", "experiment_id", "timestamp"})))
        confidence = round(min(0.95, confidence), 2)
        
        log = ExperimentLog.model_validate(log_data)
        return log, {
            "prompt_extraction": {
                "explicit_fields": sorted(list(set(explicit_fields))),
                "assumed_fields": sorted(list(set(assumed_fields))),
                "confidence": confidence
            }
        }
