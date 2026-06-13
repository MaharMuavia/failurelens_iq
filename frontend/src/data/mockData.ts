export type Outcome = "failure" | "partial" | "success" | "unknown";

export type Experiment = {
  experiment_id: string;
  team_id: string;
  project_name: string;
  role: string;
  model_type: string;
  dataset_name: string;
  pipeline_stage: string;
  validation_strategy: string;
  class_balance: string;
  metrics: Record<string, number>;
  baseline_metrics: Record<string, number>;
  drift_indicators: string[];
  data_quality_signals: string[];
  failure_observation: string;
  suspected_leakage_columns: string[];
  engineer_notes: string;
  current_certifications: string[];
  outcome: Outcome;
  failure_category_label: string;
  timestamp: string;
};

export type TeamProfile = {
  team_id: string;
  team_name: string;
  domain: string;
  current_certifications: string[];
  sprint_load: string;
  team_size: number;
  compliance_sensitivity: string;
  ml_maturity: string;
};

export const experiments: Experiment[] = [
  {
    experiment_id: "EXP-1001",
    team_id: "TEAM-A",
    project_name: "Atlas retention risk model",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-a_synthetic_training",
    pipeline_stage: "evaluation",
    validation_strategy: "holdout",
    class_balance: "88/12",
    metrics: { accuracy: 0.93, minority_f1: 0.14, roc_auc: 0.72 },
    baseline_metrics: { accuracy: 0.89, minority_f1: 0.42, roc_auc: 0.77 },
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation:
      "Accuracy looked deceptive on an 88/12 class balance; minority class failures were hidden by a holdout validation report.",
    suspected_leakage_columns: [],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100"],
    outcome: "failure",
    failure_category_label: "Evaluation Methodology Failure",
    timestamp: "2026-06-07T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-2001",
    team_id: "TEAM-B",
    project_name: "Beacon eligibility review",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-b_synthetic_training",
    pipeline_stage: "evaluation",
    validation_strategy: "slice holdout",
    class_balance: "78/22",
    metrics: { accuracy: 0.86, demographic_parity: 0.41, group_fairness_score: 0.34 },
    baseline_metrics: { accuracy: 0.88, demographic_parity: 0.72, group_fairness_score: 0.7 },
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation:
      "Protected attribute fairness review found weak demographic parity and disparate error rates across groups.",
    suspected_leakage_columns: [],
    engineer_notes:
      "Fairness, protected attribute, demographic parity, and responsible AI review were discussed as team process gaps.",
    current_certifications: ["DP-100"],
    outcome: "failure",
    failure_category_label: "Responsible AI / Bias Failure",
    timestamp: "2026-06-06T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-3001",
    team_id: "TEAM-C",
    project_name: "CareSignal medication risk",
    role: "ML Engineer",
    model_type: "BERT",
    dataset_name: "team-c_synthetic_training",
    pipeline_stage: "deployment",
    validation_strategy: "holdout",
    class_balance: "80/20",
    metrics: { accuracy: 0.74, recall: 0.46 },
    baseline_metrics: { accuracy: 0.84, recall: 0.68 },
    drift_indicators: ["medication coding distribution drift"],
    data_quality_signals: ["late lab_result partition"],
    failure_observation:
      "Healthcare triage model degraded after medication coding distributions drifted in production monitoring.",
    suspected_leakage_columns: [],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100", "DP-203"],
    outcome: "failure",
    failure_category_label: "Deployment / Drift Failure",
    timestamp: "2026-06-05T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-4001",
    team_id: "TEAM-D",
    project_name: "Delta demand quality model",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-d_synthetic_training",
    pipeline_stage: "evaluation",
    validation_strategy: "holdout",
    class_balance: "80/20",
    metrics: { accuracy: 0.8, minority_f1: 0.31 },
    baseline_metrics: { accuracy: 0.84, minority_f1: 0.42 },
    drift_indicators: [],
    data_quality_signals: ["schema drift", "duplicate rows"],
    failure_observation:
      "Schema drift and duplicated rows reduced trust in the analytics training table.",
    suspected_leakage_columns: [],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100", "AI-102", "DP-203", "PL-300"],
    outcome: "failure",
    failure_category_label: "Data Quality Failure",
    timestamp: "2026-06-04T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-1002",
    team_id: "TEAM-A",
    project_name: "Atlas feature audit",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-a_synthetic_training",
    pipeline_stage: "training",
    validation_strategy: "holdout",
    class_balance: "80/20",
    metrics: { accuracy: 0.96, minority_f1: 0.88 },
    baseline_metrics: { accuracy: 0.84, minority_f1: 0.36 },
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation:
      "Validation jumped after a post-outcome renewal_status field entered the feature set, suggesting leakage.",
    suspected_leakage_columns: ["renewal_status_after_30d"],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100"],
    outcome: "failure",
    failure_category_label: "Data Leakage Failure",
    timestamp: "2026-06-03T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-3002",
    team_id: "TEAM-C",
    project_name: "CareSignal feature parser",
    role: "ML Engineer",
    model_type: "BERT",
    dataset_name: "team-c_synthetic_training",
    pipeline_stage: "feature_engineering",
    validation_strategy: "holdout",
    class_balance: "80/20",
    metrics: { accuracy: 0.73, f1: 0.48 },
    baseline_metrics: { accuracy: 0.81, f1: 0.62 },
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation:
      "Clinical text tokenization removed dosage units, weakening feature signal for risk prediction.",
    suspected_leakage_columns: [],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100", "DP-203"],
    outcome: "failure",
    failure_category_label: "Feature Engineering Failure",
    timestamp: "2026-06-01T08:00:00+00:00"
  },
  {
    experiment_id: "EXP-4006",
    team_id: "TEAM-D",
    project_name: "Delta control run",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-d_synthetic_training",
    pipeline_stage: "evaluation",
    validation_strategy: "holdout",
    class_balance: "80/20",
    metrics: { accuracy: 0.8, minority_f1: 0.31 },
    baseline_metrics: { accuracy: 0.84, minority_f1: 0.42 },
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation: "Successful control run preserved expected quality gates.",
    suspected_leakage_columns: [],
    engineer_notes: "Team review captured this as a process learning opportunity.",
    current_certifications: ["DP-100", "AI-102", "DP-203", "PL-300"],
    outcome: "success",
    failure_category_label: "Partial",
    timestamp: "2026-05-10T08:00:00+00:00"
  },
  {
    experiment_id: "SPARSE-001",
    team_id: "TEAM-D",
    project_name: "Sparse evidence sentinel",
    role: "ML Engineer",
    model_type: "XGBoost",
    dataset_name: "team-d_synthetic_training",
    pipeline_stage: "evaluation",
    validation_strategy: "holdout",
    class_balance: "50/50",
    metrics: {},
    baseline_metrics: {},
    drift_indicators: [],
    data_quality_signals: [],
    failure_observation: "Model did not work as expected.",
    suspected_leakage_columns: [],
    engineer_notes: "Sparse synthetic record intentionally lacks evidence.",
    current_certifications: [],
    outcome: "unknown",
    failure_category_label: "Unknown",
    timestamp: "2026-06-08T08:00:00+00:00"
  }
];

export const teamProfiles: TeamProfile[] = [
  {
    team_id: "TEAM-A",
    team_name: "Atlas Validation",
    domain: "enterprise retention",
    current_certifications: ["DP-100"],
    sprint_load: "medium",
    team_size: 7,
    compliance_sensitivity: "moderate",
    ml_maturity: "intermediate"
  },
  {
    team_id: "TEAM-B",
    team_name: "Beacon Fairness",
    domain: "financial eligibility",
    current_certifications: ["DP-100"],
    sprint_load: "high",
    team_size: 8,
    compliance_sensitivity: "high",
    ml_maturity: "developing"
  },
  {
    team_id: "TEAM-C",
    team_name: "CareSignal ML",
    domain: "healthcare",
    current_certifications: ["DP-100", "DP-203"],
    sprint_load: "medium",
    team_size: 9,
    compliance_sensitivity: "high",
    ml_maturity: "advanced"
  },
  {
    team_id: "TEAM-D",
    team_name: "Delta Applied AI",
    domain: "manufacturing and demand",
    current_certifications: ["DP-100", "AI-102", "DP-203", "PL-300"],
    sprint_load: "low",
    team_size: 6,
    compliance_sensitivity: "moderate",
    ml_maturity: "advanced"
  }
];

export const knowledgeHits = [
  {
    source_file: "remediation_playbook.md",
    section_title: "Imbalanced Evaluation",
    relevance_score: 0.92,
    citation: "remediation_playbook.md#imbalanced-evaluation",
    excerpt:
      "When accuracy rises while minority F1 falls, require stratified validation, slice metrics, and explicit class-level review before release.",
    matched_terms: ["minority_f1", "accuracy", "validation"]
  },
  {
    source_file: "ml_failure_taxonomy.md",
    section_title: "Responsible AI / Bias Failure",
    relevance_score: 0.88,
    citation: "ml_failure_taxonomy.md#responsible-ai-bias-failure",
    excerpt:
      "Bias failures require protected attribute review, disparity checks, group error analysis, and escalation when compliance sensitivity is high.",
    matched_terms: ["fairness", "protected", "demographic"]
  },
  {
    source_file: "dp100_skill_guide.md",
    section_title: "Model Monitoring",
    relevance_score: 0.81,
    citation: "dp100_skill_guide.md#model-monitoring",
    excerpt:
      "Production drift should be connected to data freshness, feature distribution, and retraining readiness, not only model accuracy.",
    matched_terms: ["drift", "monitoring", "freshness"]
  }
];

export const reasoningSteps = [
  {
    agent: "Planner",
    agent_name: "Planner",
    status: "completed",
    confidence: 0.72,
    duration_ms: 12,
    finding: "Opened evaluation-focused plan because reported accuracy conflicts with minority-class performance.",
    key_evidence: ["metrics.accuracy", "metrics.minority_f1", "class_balance"],
    evidence: ["metrics.accuracy", "metrics.minority_f1", "class_balance"],
    counter_evidence: [],
    reasoning_steps: [
      { thought_type: "observation", finding: "accuracy=0.93 conflicts with minority_f1=0.14", evidence_fields: ["metrics"] },
      { thought_type: "hypothesis", finding: "Suspected evaluation methodology failure from metric disagreement.", evidence_fields: ["class_balance"] },
    ],
    recommended_next_actions: ["Investigate evaluation strategy"]
  },
  {
    agent: "ClassifierAgent",
    agent_name: "Failure Classifier",
    status: "completed",
    confidence: 0.79,
    duration_ms: 18,
    finding: "Evaluation methodology is strongest among six rules; leakage and drift signals are not active.",
    key_evidence: ["validation_strategy", "baseline_metrics.minority_f1"],
    evidence: ["validation_strategy", "baseline_metrics.minority_f1"],
    counter_evidence: ["suspected_leakage_columns=[] → no direct leakage evidence"],
    reasoning_steps: [
      { thought_type: "evidence_check", finding: "Checked 6 classification rules against experiment fields.", evidence_fields: ["metrics", "validation_strategy"] },
      { thought_type: "inference", finding: "evaluation_methodology scored highest; data_leakage and drift ruled out.", evidence_fields: ["classification"] },
      { thought_type: "decision", finding: "Classified as evaluation_methodology with confidence 0.79.", evidence_fields: ["classification"] },
    ],
    recommended_next_actions: ["Validate with diagnostic agent"]
  },
  {
    agent: "DiagnosticAgent",
    agent_name: "Root Cause Analyzer",
    status: "completed",
    confidence: 0.83,
    duration_ms: 45,
    finding: "Root cause points to aggregate accuracy masking class-level regression on an imbalanced target.",
    key_evidence: ["failure_observation", "class_balance=88/12"],
    evidence: ["failure_observation", "remediation_playbook.md"],
    counter_evidence: ["drift_indicators=[] → no deployment drift evidence"],
    reasoning_steps: [
      { thought_type: "evidence_check", finding: "Checked available experiment evidence from metrics and observation.", evidence_fields: ["failure_observation", "classification"] },
      { thought_type: "inference", finding: "Holdout validation with 88/12 imbalance masked minority-class collapse.", evidence_fields: ["metrics", "validation_strategy"] },
      { thought_type: "counter_evidence", finding: "No leakage or drift signals; counter-evidence is weak.", evidence_fields: ["baseline_metrics"] },
      { thought_type: "uncertainty_check", finding: "Weak IQ grounding detected; confidence remains conservative.", evidence_fields: ["reflection_notes"] },
      { thought_type: "decision", finding: "Calibrated diagnosis at confidence 0.830 vs threshold 0.450.", evidence_fields: ["planner_context.plan.dynamic_threshold"] },
      { thought_type: "next_action", finding: "Run stratified validation and add minority-class slice metrics.", evidence_fields: ["recommended_next_actions"], next_action: "Run stratified validation" },
    ],
    recommended_next_actions: ["Add slice-level metrics", "Run stratified validation"]
  },
  {
    agent: "ConfidenceGate",
    agent_name: "Confidence Gate",
    status: "completed",
    confidence: 0.81,
    duration_ms: 2,
    finding: "Confidence gate passed with moderate evidence strength and grounded citations.",
    key_evidence: ["grounding_citations", "evidence_strength"],
    evidence: ["grounding_citations", "evidence_strength"],
    counter_evidence: [],
    reasoning_steps: [
      { thought_type: "decision", finding: "Confidence 0.83 exceeds dynamic threshold 0.45 — gate passed.", evidence_fields: ["confidence", "threshold"] },
    ],
    recommended_next_actions: ["Proceed with downstream agents"]
  }
];
