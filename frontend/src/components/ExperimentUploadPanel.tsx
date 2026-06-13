import React, { useState } from "react";
import { uploadExperiment } from "../utils/api";

const SAMPLE = {
  experiment_id: "EXP-2001",
  team_id: "TEAM-A",
  project_name: "Customer Churn",
  role: "ML Engineer",
  model_type: "XGBoost",
  dataset_name: "churn_v2.csv",
  pipeline_stage: "validation",
  target: "churn",
  validation_strategy: "random split",
  class_balance: "86/14",
  preprocessing_steps: ["standard scaling", "one-hot encoding"],
  feature_set: ["tenure", "monthly_charges", "contract_type"],
  metrics: { accuracy: 0.93, minority_f1: 0.14, roc_auc: 0.72 },
  baseline_metrics: { accuracy: 0.86, minority_f1: 0.42 },
  error_logs: [],
  drift_indicators: ["feature drift on tenure"],
  data_quality_signals: ["minority class underrepresented"],
  training_config: { algorithm: "xgboost", class_weight: "none" },
  deployment_context: { environment: "staging" },
  failure_symptoms: ["minority class collapse", "misleading accuracy"],
  failure_observation: "High accuracy but minority churn prediction failed.",
  suspected_leakage_columns: [],
  engineer_notes: "Possible imbalance and validation methodology issue.",
  current_certifications: ["AI-900"],
  outcome: "failure",
  failure_category_label: "Evaluation Methodology",
  timestamp: new Date().toISOString(),
};

export const ExperimentUploadPanel: React.FC = () => {
  const [text, setText] = useState(JSON.stringify(SAMPLE, null, 2));
  const [message, setMessage] = useState<string | null>(null);

  const validate = (obj: any) => obj && obj.experiment_id && obj.metrics;

  const handleSubmit = async () => {
    try {
      const obj = JSON.parse(text);
      if (!validate(obj)) {
        setMessage("Invalid experiment JSON: missing required fields.");
        return;
      }
      await uploadExperiment(obj);
      setMessage("Stored successfully. You can now run analysis for this experiment.");
    } catch (err) {
      setMessage("Invalid JSON: " + (err as Error).message);
    }
  };

  return (
    <div className="p-4 bg-[#071226]/50 rounded">
      <h3 className="text-lg font-semibold text-cyan-200">Upload Experiment</h3>
      <div className="mt-2">
        <textarea value={text} onChange={(e) => setText(e.target.value)} className="w-full h-48 p-2 rounded bg-[#071226]" />
      </div>
      <div className="flex gap-2 mt-2">
        <button className="px-3 py-2 bg-cyan-500 rounded" onClick={handleSubmit}>Upload JSON</button>
        <button className="px-3 py-2 border rounded" onClick={() => setText(JSON.stringify(SAMPLE, null, 2))}>Load Sample Experiment</button>
      </div>
      {message && <div className="mt-2 text-sm text-yellow-200">{message}</div>}
    </div>
  );
};

export default ExperimentUploadPanel;
