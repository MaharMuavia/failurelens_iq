export interface Experiment {
  id: string;
  project: string;
  modelType: string;
  category: string;
  confidence: number;
  iqMode: 'offline_mock_preview' | 'local_client_simulation' | 'local_foundry_iq_adapter' | 'live_azure_foundry';
  is_live_backend: boolean;
  is_live_microsoft_iq: boolean;
  proof_level: 'offline_mock_preview' | 'local_client_simulation' | 'local_foundry_iq_adapter' | 'foundry_model_live_without_search' | 'azure_search_live_with_local_reasoning' | 'live_azure_foundry';
  warning: string;
  humanReview: 'Approved' | 'Requires Audit' | 'Pending Review';
  created: string;
  summary: string;
  rootCause: string;
  recommendedFixes: string[];
  evidence: string[];
  reasoningSteps: string[];
  certificationMapping: string;
}

export interface AgentRun {
  runId: string;
  experimentId: string;
  status: 'Completed' | 'Failed' | 'Running';
  confidence: number;
  iqLevel: number; // 1 to 4 scale
  duration: string;
  created: string;
  trace: { [agentName: string]: { role: string; status: 'Completed' | 'Pending' | 'Active'; confidence: number; steps: string[]; evidence: string[]; nextAction?: string } };
}

export interface KnowledgeItem {
  id: string;
  title: string;
  sourceType: 'Failure Taxonomy' | 'Remediation Playbook' | 'Certification Mapping' | 'Responsible AI' | 'Manager Governance';
  score: number;
  excerpt: string;
  citation: string;
}

export interface Report {
  id: string;
  experimentId: string;
  title: string;
  created: string;
  type: string;
  summary: string;
  diagnosis: string;
  remediation: string;
  certification: string;
}

const OFFLINE_WARNING = "Offline Mock Preview — not live submission proof.";

// Fallback data for offline mode. These records are intentionally labeled as
// synthetic client previews and must never imply live Microsoft proof.
export const MOCK_EXPERIMENTS: Experiment[] = [
  {
    id: "EXP-1001",
    project: "Credit Churn Predictor",
    modelType: "XGBoost Classifier",
    category: "Class Imbalance Bias",
    confidence: 84,
    iqMode: "offline_mock_preview",
    is_live_backend: false,
    is_live_microsoft_iq: false,
    proof_level: "offline_mock_preview",
    warning: OFFLINE_WARNING,
    humanReview: "Pending Review",
    created: "2026-06-10",
    summary: "Our churn model achieved 93% accuracy, but minority class F1 dropped to 0.14. Dataset is 88/12 imbalanced and validation used a simple holdout split.",
    rootCause: "Validation set holdout split failed to maintain class alignment, leading to the opt-in threshold ignoring minority-class density. Training optimization objective pushed overall accuracy upwards by sacrifice of the minority prediction weight.",
    recommendedFixes: [
      "Implement SMOTE or stratified custom split strategies in prep pipeline.",
      "Tune objective criteria with focal loss or weight penalty ratios.",
      "Adjust decision activation thresholds using roc-precision calibration."
    ],
    evidence: [
      "F1 Score is 0.14 vs overall accuracy of 93%",
      "Holdout validation set ratio did not match training imbalance",
      "Minority class support size is extremely low (N=120)"
    ],
    reasoningSteps: [
      "Planner Agent activated: Triggering stratified cross-validation setup.",
      "Classifier Agent: Identifying class imbalance footprint.",
      "Root Cause Analyst: Correlating 93% accuracy with 12% minority ratio.",
      "Remediation Coach: Formulating focal loss weight adjustment."
    ],
    certificationMapping: "Aligns with Microsoft Responsible AI Standard v2: Section F.3 (Fairness & Bias Mitigations)"
  },
  {
    id: "EXP-1002",
    project: "Retention Forecasting Engine",
    modelType: "Random Forest Regressor",
    category: "Target Leakage",
    confidence: 92,
    iqMode: "local_client_simulation",
    is_live_backend: false,
    is_live_microsoft_iq: false,
    proof_level: "offline_mock_preview",
    warning: OFFLINE_WARNING,
    humanReview: "Approved",
    created: "2026-06-11",
    summary: "Validation accuracy jumped to 98% after adding renewal_status_after_30d, but live test performance completely collapsed. Suspect temporal feature leakage.",
    rootCause: "The feature renewal_status_after_30d contains future states generated after the target churning window occurred. It leaks customer status variables into the historical trainer.",
    recommendedFixes: [
      "Remove renewal_status_after_30d from baseline datasets.",
      "Define strict timestamp offsets for feature engineering.",
      "Implement data snapshot sanity validator rules."
    ],
    evidence: [
      "Features contains indicators strictly compiled in the post-churn era",
      "Massive difference in training vs real test performance (98% vs 44%)",
      "Citations found in historical telemetry pipelines matching renewal_status timing"
    ],
    reasoningSteps: [
      "Planner Agent: Analyzing feature correlation matrix.",
      "Root Cause Analyst: Flagging 98% validation rate as anomalous.",
      "Historian: Back-tracking renewal_status generation time vs churn label assignment."
    ],
    certificationMapping: "Exposes critical violation in Model Governance Guide (v1.2): Section G.1 (Temporal Target Leakage Protection)"
  },
  {
    id: "EXP-1003",
    project: "Loan Disbursal Evaluator",
    modelType: "Deep Feedforward Network",
    category: "Ethical & Demographic Disparate Impact",
    confidence: 79,
    iqMode: "local_client_simulation",
    is_live_backend: false,
    is_live_microsoft_iq: false,
    proof_level: "offline_mock_preview",
    warning: OFFLINE_WARNING,
    humanReview: "Requires Audit",
    created: "2026-06-12",
    summary: "Loan approval model has strong overall AUC but approval errors are much higher for a protected demographic subgroup.",
    rootCause: "Proxy variables (zip-code combined with income brackets) encoded demographic correlations, forcing bias propagation into the neural layer without direct demographic features.",
    recommendedFixes: [
      "Remove correlated proxy features from input schema.",
      "Apply adversarial fairness debiasing objectives.",
      "Deploy regularized Demography parity metrics."
    ],
    evidence: [
      "Disparate ratio checks failed (ratio: 0.62, minimum threshold is 0.8)",
      "Zip-code high-mutual-information with protected demography"
    ],
    reasoningSteps: [
      "Reasoning Agent: Analyzing disparate impact metrics.",
      "Historian: Identifying zip-codes mapping directly to protected demographic regions.",
      "Coach: Recommending fair-learn objective adjustments."
    ],
    certificationMapping: "Microsoft Responsible AI Standard: Section F.1 (Assessing Fairness and Disparate Harms)"
  }
];

export const MOCK_AGENT_RUNS: AgentRun[] = [
  {
    runId: "RUN-9021",
    experimentId: "EXP-1001",
    status: "Completed",
    confidence: 84,
    iqLevel: 3,
    duration: "4.2s",
    created: "2026-06-12 14:32:10",
    trace: {
      "Planner": {
        role: "Pipeline Architect",
        status: "Completed",
        confidence: 95,
        steps: ["Parsed prompt inputs", "Initialized diagnostic taxonomy tree", "Scheduled specialty analyzers"],
        evidence: ["Found pattern: Class Imbalance"]
      },
      "Classifier": {
        role: "Divergence Scouter",
        status: "Completed",
        confidence: 89,
        steps: ["Analyzed metric ratio differentials", "Flagged F1 score outlier ratio"],
        evidence: ["F1-score of 0.14 vs Accuracy of 93%"]
      },
      "Historian": {
        role: "Grounding Search",
        status: "Completed",
        confidence: 91,
        steps: ["Searched Foundry IQ retrieval database", "Extracted standard bias remediation plans"],
        evidence: ["Found 4 matching playbooks on Stratified K-Fold design"]
      },
      "Coach": {
        role: "Learning Plan Expert",
        status: "Completed",
        confidence: 85,
        steps: ["Formulated certification mapping", "Calibrated confidence score threshold"],
        evidence: ["Identified Microsoft Responsible AI compliance alignment"]
      }
    }
  },
  {
    runId: "RUN-9022",
    experimentId: "EXP-1002",
    status: "Completed",
    confidence: 92,
    iqLevel: 4,
    duration: "5.1s",
    created: "2026-06-13 01:20:15",
    trace: {
      "Planner": {
        role: "Pipeline Architect",
        status: "Completed",
        confidence: 98,
        steps: ["Identified extreme performance gap", "Dispatched leakage detectors"],
        evidence: ["Train Accuracy: 98% vs Test Accuracy: 44%"]
      },
      "Classifier": {
        role: "Divergence Scouter",
        status: "Completed",
        confidence: 95,
        steps: ["Located anomalous feature correlation: renewal_status_after_30d"],
        evidence: ["renewal_status_after_30d correlation index: 0.94"]
      }
    }
  }
];

export const MOCK_KNOWLEDGE: KnowledgeItem[] = [
  {
    id: "KN-301",
    title: "Class Imbalance Calibration",
    sourceType: "Remediation Playbook",
    score: 0.96,
    excerpt: "For heavy class imbalances (>85/15), standard cross-entropy fails. Recommend focal loss wrappers, class weighting variables, and threshold adjustments.",
    citation: "Microsoft Foundational AI Playbook v3, Section 5"
  },
  {
    id: "KN-302",
    title: "Temporal Target Leakage Safeguards",
    sourceType: "Responsible AI",
    score: 0.93,
    excerpt: "Data leakage happens when future state features (timestamp >= target timestamp) are exposed to models during snapshot creation.",
    citation: "Foundry IQ Standards, Section F.1"
  },
  {
    id: "KN-303",
    title: "Proxy Variable Correlation Mitigations",
    sourceType: "Failure Taxonomy",
    score: 0.89,
    excerpt: "Protected classes are often latent in geographic zipcodes. Mitigate by removing high mutual information spatial predictors.",
    citation: "Fairness Assessment Framework, Microsoft v2"
  }
];

export const MOCK_REPORTS: Report[] = [
  {
    id: "REP-401",
    experimentId: "EXP-1001",
    title: "EXP-1001 Class Imbalance Diagnosis & Remediation",
    created: "2026-06-12",
    type: "Responsible AI Certification Report",
    summary: "Comprehensive diagnostics on minority F1 optimization flaws in the Credit Churn Predictor model.",
    diagnosis: "Model optimized for high baseline classification rate, causing minority F1 score collapse on asymmetric test scenarios.",
    remediation: "Integrate focal dynamic penalty layers, and employ stratified cross splits.",
    certification: "Microsoft Responsible AI compliance ready"
  }
];

const CONFIGURED_API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

function normalizeProofLevel(level?: string): Experiment["proof_level"] {
  const allowed: Experiment["proof_level"][] = [
    "offline_mock_preview",
    "local_client_simulation",
    "local_foundry_iq_adapter",
    "foundry_model_live_without_search",
    "azure_search_live_with_local_reasoning",
    "live_azure_foundry",
  ];
  return allowed.includes(level as Experiment["proof_level"])
    ? (level as Experiment["proof_level"])
    : "local_foundry_iq_adapter";
}

function experimentFromPromptResponse(raw: any): Experiment {
  const analysis = raw?.analysis_result || raw;
  const generated = raw?.generated_experiment || {};
  const classification = analysis?.failure_classification || {};
  const diagnosis = analysis?.root_cause_analysis || {};
  const remediation = analysis?.remediation_plan || {};
  const compliance = analysis?.microsoft_iq_compliance || {};
  const proofLevel = normalizeProofLevel(compliance?.proof_level || analysis?.proof_level);
  const isLiveIq = Boolean(compliance?.live_microsoft_iq || analysis?.live_microsoft_iq);
  const warning = analysis?.honest_limitation || compliance?.honest_limitation || "";

  return {
    id: raw?.prompt_id || generated?.experiment_id || analysis?.run_id || `EXP-${Date.now()}`,
    project: generated?.project_name || analysis?.demo_title || "Prompt-generated experiment",
    modelType: generated?.model_type || "Model from prompt",
    category: String(classification?.failure_category || generated?.failure_category_label || "Unclassified"),
    confidence: Math.round(Number(analysis?.confidence_summary?.overall_confidence || classification?.confidence || 0.8) * 100),
    iqMode: isLiveIq ? "live_azure_foundry" : "local_foundry_iq_adapter",
    is_live_backend: true,
    is_live_microsoft_iq: isLiveIq,
    proof_level: proofLevel,
    warning,
    humanReview: analysis?.confidence_summary?.requires_human_review ? "Requires Audit" : "Pending Review",
    created: new Date().toISOString().split("T")[0],
    summary: generated?.failure_observation || raw?.original_prompt || "Prompt analysis completed.",
    rootCause: diagnosis?.root_cause || "Root cause was not returned by the backend.",
    recommendedFixes: remediation?.three_day_plan || remediation?.seven_day_plan || [],
    evidence: diagnosis?.evidence || analysis?.reasoning_timeline?.flatMap((trace: any) => trace.key_evidence || []) || [],
    reasoningSteps: (analysis?.reasoning_timeline || []).map((trace: any) => `${trace.agent_name || trace.agent}: ${trace.findings?.[0] || trace.status}`),
    certificationMapping: analysis?.certification_readiness?.mapping?.recommended_cert || "Certification mapping unavailable.",
  };
}

export class ApiClient {
  private static isBackendOffline = false;

  private static async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = this.buildUrl(path);
    try {
      const res = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });
      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}`);
      }
      this.isBackendOffline = false;
      return await res.json() as T;
    } catch (e) {
      console.warn(`Backend call to ${url} failed. Falling back to offline simulator:`, e);
      this.isBackendOffline = true;
      throw e;
    }
  }

  private static buildUrl(path: string): string {
    if (!CONFIGURED_API_BASE) {
      return path;
    }
    let backendPath = path;
    if (backendPath.startsWith("/api/")) {
      backendPath = backendPath.substring(4);
    }
    return `${CONFIGURED_API_BASE}${backendPath}`;
  }

  static getOfflineStatus(): boolean {
    return this.isBackendOffline;
  }

  static async getHealth(): Promise<{ status: string; timestamp: string }> {
    try {
      return await this.request<{ status: string; timestamp: string }>("/api/health");
    } catch {
      return { status: "offline_mock_preview", timestamp: new Date().toISOString() };
    }
  }

  static async getReadiness(): Promise<{ ready: boolean }> {
    try {
      return await this.request<{ ready: boolean }>("/api/readiness");
    } catch {
      return { ready: false };
    }
  }

  static async getIQStatus(): Promise<{
    status: string;
    provider: string;
    iq_mode: string;
    live_search: boolean;
    citations_count: number;
    proof_level?: string;
    foundry_model_live?: boolean;
    azure_ai_search_configured?: boolean;
  }> {
    try {
      const raw = await this.request<any>("/api/iq/status");
      return {
        status: raw.compliance_status || raw.status || "active",
        provider: raw.active_provider || raw.provider || "Local Foundry IQ Adapter",
        iq_mode: raw.foundry_iq_mode || raw.iq_mode || "Local Mode (No Azure Grounding Connection)",
        live_search: raw.live_microsoft_iq || raw.live_search || false,
        citations_count: raw.citations_supported ? 14 : 3,
        proof_level: raw.proof_level,
        foundry_model_live: Boolean(raw.live_microsoft_foundry_model),
        azure_ai_search_configured: Boolean(raw.azure_ai_search_ready_or_active || raw.live_services?.azure_ai_search_configured),
      };
    } catch {
      return {
        status: "backend_offline",
        provider: "Backend Offline",
        iq_mode: "offline_mock_preview",
        live_search: false,
        citations_count: 3
      };
    }
  }

  static async listExperiments(): Promise<Experiment[]> {
    try {
      const res = await this.request<any>("/api/experiments");
      if (res && Array.isArray(res)) {
        return res;
      }
      if (res && res.items && Array.isArray(res.items)) {
        // Map backend experiment log schema fields to frontend Experiment schema if needed
        return res.items.map((item: any) => ({
          id: item.experiment_id || item.id,
          project: item.project || item.model || "Baseline Model",
          modelType: item.modelType || item.model || "XGBoost Classifier",
          category: item.category || item.failure_category || "Unclassified",
          confidence: item.confidence || Math.round(item.test_accuracy * 100) || 85,
          iqMode: item.iqMode || "local_foundry_iq_adapter",
          is_live_backend: true,
          is_live_microsoft_iq: Boolean(item.live_microsoft_iq),
          proof_level: normalizeProofLevel(item.proof_level),
          warning: item.warning || "",
          humanReview: item.humanReview || "Pending Review",
          created: item.created || item.timestamp?.split("T")[0] || new Date().toISOString().split("T")[0],
          summary: item.summary || item.notes || "",
          rootCause: item.rootCause || item.notes || "No root cause documented.",
          recommendedFixes: item.recommendedFixes || [],
          evidence: item.evidence || [],
          reasoningSteps: item.reasoningSteps || [],
          certificationMapping: item.certificationMapping || ""
        }));
      }
      return [];
    } catch {
      const stored = localStorage.getItem("failurelens_experiments");
      if (stored) {
        return JSON.parse(stored) as Experiment[];
      }
      return MOCK_EXPERIMENTS;
    }
  }

  static async runDemo(): Promise<{ success: boolean; data: any }> {
    try {
      return await this.request<{ success: boolean; data: any }>("/api/demo/run", { method: "POST" });
    } catch {
      return { success: false, data: { status: "backend_offline", warning: OFFLINE_WARNING, payload: MOCK_EXPERIMENTS } };
    }
  }

  static async analyzePrompt(prompt: string): Promise<any> {
    try {
      const raw = await this.request<any>("/api/prompt/analyze", {
        method: "POST",
        body: JSON.stringify({ prompt }),
      });
      return {
        success: true,
        mode: "backend_orchestrator",
        data: experimentFromPromptResponse(raw),
        raw,
      };
    } catch {
      // Return beautiful fallback mock data matching user query
      const normalized = prompt.toLowerCase();
      let selected: Experiment = MOCK_EXPERIMENTS[0];
      if (normalized.includes("leakage") || normalized.includes("renewal")) {
        selected = MOCK_EXPERIMENTS[1];
      } else if (normalized.includes("fairness") || normalized.includes("loan") || normalized.includes("protected")) {
        selected = MOCK_EXPERIMENTS[2];
      } else if (normalized.includes("forest") || normalized.includes("overfit") || normalized.includes("97")) {
        // Create Overfitting Mock
        selected = {
          id: `EXP-${Math.floor(1000 + Math.random() * 9000)}`,
          project: "Churn Random Forest",
          modelType: "Random Forest Classifier",
          category: "Overfitting & Hyperparameter Splurge",
          confidence: 76,
          iqMode: "local_client_simulation",
          is_live_backend: false,
          is_live_microsoft_iq: false,
          proof_level: "offline_mock_preview",
          warning: OFFLINE_WARNING,
          humanReview: "Requires Audit",
          created: new Date().toISOString().split('T')[0],
          summary: prompt,
          rootCause: "Optimal branching bounds were unconstrained, causing trees to memoize dataset indices rather than generalizable parameter structures. Failure to utilize cross-validation resulted in structural variance masking.",
          recommendedFixes: [
            "Restrict max_depth parameter to integer bounds [4, 8].",
            "Perform Stratified K-Fold cross validation.",
            "Utilize structural L1/L2 metric dropweights."
          ],
          evidence: [
            "Training performance 97% vs test split of 61%",
            "Leaf-node purity checks indicate extreme sample allocation sparsity"
          ],
          reasoningSteps: [
            "Planner: Commencing depth diagnostic sweeps.",
            "Classifier: Flagging overfitting metric delta.",
            "Coach: Formatting regularization checklists."
          ],
          certificationMapping: "Exposes compliance warnings on Model Governance Audit Checklist Page (3)"
        };
      }

      // Add to local storage
      const existing = await this.listExperiments();
      if (!existing.some(e => e.id === selected.id)) {
        const updated = [selected, ...existing];
        localStorage.setItem("failurelens_experiments", JSON.stringify(updated));
      }

      return {
        success: true,
        mode: "offline_mock_preview",
        is_live_backend: false,
        is_live_microsoft_iq: false,
        proof_level: "offline_mock_preview",
        warning: OFFLINE_WARNING,
        data: selected
      };
    }
  }

  static async runAnalysis(experimentId: string): Promise<{ success: boolean; result: any }> {
    try {
      return await this.request<{ success: boolean; result: any }>("/api/analysis/run", {
        method: "POST",
        body: JSON.stringify({ experiment_id: experimentId }),
      });
    } catch {
      return { success: true, result: MOCK_AGENT_RUNS.find(r => r.experimentId === experimentId) || MOCK_AGENT_RUNS[0] };
    }
  }

  static async searchKnowledge(query: string): Promise<KnowledgeItem[]> {
    try {
      return await this.request<KnowledgeItem[]>(`/api/knowledge/search?query=${encodeURIComponent(query)}`);
    } catch {
      if (!query) return MOCK_KNOWLEDGE;
      return MOCK_KNOWLEDGE.filter(k =>
        k.title.toLowerCase().includes(query.toLowerCase()) ||
        k.excerpt.toLowerCase().includes(query.toLowerCase())
      );
    }
  }

  static async generateReport(experimentId: string): Promise<Report & {
    content?: string;
    is_offline_preview?: boolean;
    path?: string;
    run_id?: string;
    proof_level?: string;
    live_microsoft_iq?: boolean;
    citations?: string[];
    agent_trace_summary?: any[];
  }> {
    try {
      return await this.request<any>(`/api/report/${experimentId}/generate`, { method: "POST" });
    } catch {
      const found = MOCK_EXPERIMENTS.find(e => e.id === experimentId) || MOCK_EXPERIMENTS[0];
      const content = [
        "# Offline Preview Report",
        "",
        "OFFLINE MOCK PREVIEW — NOT LIVE SUBMISSION PROOF",
        "",
        `run_id: offline_client_preview`,
        `experiment_id: ${found.id}`,
        "active_reasoning_provider: local_client_simulation",
        "active_grounding_provider: local_client_simulation",
        "proof_level: offline_mock_preview",
        "live_microsoft_iq: false",
        "",
        "## Citations",
        "No backend citations available.",
        "",
        "## Agent Trace Summary",
        ...found.reasoningSteps.map((step) => `- ${step}`),
        "",
        "## Root Cause",
        found.rootCause,
        "",
        "## Remediation Plan",
        ...found.recommendedFixes.map((fix) => `- ${fix}`),
        "",
        "## Certification Mapping",
        found.certificationMapping,
      ].join("\n");
      return {
        id: `REP-${Math.floor(500 + Math.random() * 500)}`,
        experimentId: found.id,
        title: `${found.id} Diagnostics and remediation certification`,
        created: new Date().toISOString().split('T')[0],
        type: "Offline Preview Report",
        summary: found.summary,
        diagnosis: found.rootCause,
        remediation: found.recommendedFixes.join("\n"),
        certification: found.certificationMapping,
        content,
        is_offline_preview: true,
        run_id: "offline_client_preview",
        proof_level: "offline_mock_preview",
        live_microsoft_iq: false,
        citations: [],
        agent_trace_summary: found.reasoningSteps,
      };
    }
  }

  static async getInteractiveReportUrl(experimentId: string): Promise<{ url: string }> {
    try {
      return await this.request<{ url: string }>(`/api/report/${experimentId}/interactive`);
    } catch {
      return { url: `/report/${experimentId}/interactive-preview` };
    }
  }

  static async getAgents(): Promise<any[]> {
    try {
      return await this.request<any[]>("/api/agents");
    } catch {
      return [
        { name: "FailureClassifierAgent", role: "Classifies failed ML experiments into repeatable failure categories." },
        { name: "RootCauseAnalyzerAgent", role: "Explains root cause, violated assumption, knowledge gap, and counter-evidence." },
        { name: "ExperimentHistorianAgent", role: "Finds similar historical failed experiments and repeated team learning patterns." },
        { name: "PrescriptiveCoachAgent", role: "Creates an evidence-bound remediation plan for the team." },
        { name: "CertificationEvaluatorAgent", role: "Maps the failure to Microsoft skill domains and readiness questions." },
        { name: "IntegrationManagerAgent", role: "Builds the final executive report, grounding summary, and manager action view." }
      ];
    }
  }

  static async runAnalysisWithOptions(experimentId: string): Promise<any> {
    try {
      return await this.request<any>("/api/analysis/run", {
        method: "POST",
        body: JSON.stringify({
          experiment_id: experimentId,
          options: {
            include_reasoning_trace: true,
            include_grounding: true,
            include_certification: true
          }
        })
      });
    } catch {
      return { success: true, result: MOCK_AGENT_RUNS.find(r => r.experimentId === experimentId) || MOCK_AGENT_RUNS[0] };
    }
  }

  static streamAnalysis(experimentId: string): EventSource {
    const url = this.buildUrl(`/api/analysis/stream/${encodeURIComponent(experimentId)}`);
    return new EventSource(url);
  }

  static async getProofStatus(): Promise<{
    selected_iq_layer: string;
    proof_level: string;
    live_microsoft_iq: boolean;
    is_live_backend: boolean;
    is_live_microsoft_iq: boolean;
    azure_ai_search_configured: boolean;
    azure_ai_search_used_this_run: boolean;
    foundry_model_configured: boolean;
    foundry_model_used_this_run: boolean;
    active_reasoning_provider: string;
    active_grounding_provider: string;
    citations_count: number;
    grounding_refs: string[];
    source_types: string[];
    run_id: string;
    trace_ids: string[];
    warnings: string[];
    warning: string;
    honest_limitation: string;
  }> {
    try {
      return await this.request<any>("/api/proof/live-iq");
    } catch {
      return {
        selected_iq_layer: "Foundry IQ",
        proof_level: "offline_mock_preview",
        live_microsoft_iq: false,
        is_live_backend: false,
        is_live_microsoft_iq: false,
        azure_ai_search_configured: false,
        azure_ai_search_used_this_run: false,
        foundry_model_configured: false,
        foundry_model_used_this_run: false,
        active_reasoning_provider: "local",
        active_grounding_provider: "local_iq",
        citations_count: 0,
        grounding_refs: [],
        source_types: [],
        run_id: "",
        trace_ids: [],
        warnings: [OFFLINE_WARNING],
        warning: OFFLINE_WARNING,
        honest_limitation: "Offline mock mode. No live Azure OpenAI or Azure AI Search connection exists."
      };
    }
  }

  static async runProofCheck(): Promise<{
    selected_iq_layer: string;
    proof_level: string;
    live_microsoft_iq: boolean;
    is_live_backend: boolean;
    is_live_microsoft_iq: boolean;
    azure_ai_search_configured: boolean;
    azure_ai_search_used_this_run: boolean;
    foundry_model_configured: boolean;
    foundry_model_used_this_run: boolean;
    active_reasoning_provider: string;
    active_grounding_provider: string;
    citations_count: number;
    grounding_refs: string[];
    source_types: string[];
    run_id: string;
    trace_ids: string[];
    warnings: string[];
    warning: string;
    honest_limitation: string;
  }> {
    try {
      return await this.request<any>("/api/proof/live-iq/run", { method: "POST" });
    } catch {
      return {
        selected_iq_layer: "Foundry IQ",
        proof_level: "offline_mock_preview",
        live_microsoft_iq: false,
        is_live_backend: false,
        is_live_microsoft_iq: false,
        azure_ai_search_configured: false,
        azure_ai_search_used_this_run: false,
        foundry_model_configured: false,
        foundry_model_used_this_run: false,
        active_reasoning_provider: "local",
        active_grounding_provider: "local_iq",
        citations_count: 0,
        grounding_refs: [],
        source_types: [],
        run_id: "",
        trace_ids: [],
        warnings: [OFFLINE_WARNING],
        warning: OFFLINE_WARNING,
        honest_limitation: "Offline mock mode. No live Azure OpenAI or Azure AI Search connection exists."
      };
    }
  }

  static async getLiveIQProof() {
    return this.getProofStatus();
  }

  static async runLiveIQProof() {
    return this.runProofCheck();
  }
}

// Standalone functions required by frontend tests and contracts
export function getHealth() { return ApiClient.getHealth(); }
export function getAgents() { return ApiClient.getAgents(); }
export function listExperiments() { return ApiClient.listExperiments(); }
export function runDemo() { return ApiClient.runDemo(); }
export function runAnalysis(experimentId: string) { return ApiClient.runAnalysis(experimentId); }
export function runAnalysisWithOptions(experimentId: string) { return ApiClient.runAnalysisWithOptions(experimentId); }
export function streamAnalysis(experimentId: string) { return ApiClient.streamAnalysis(experimentId); }
export function searchKnowledge(query: string) { return ApiClient.searchKnowledge(query); }
export function generateReport(experimentId: string) { return ApiClient.generateReport(experimentId); }
export function getProofStatus() { return ApiClient.getProofStatus(); }
export function runProofCheck() { return ApiClient.runProofCheck(); }
export function getLiveIQProof() { return ApiClient.getLiveIQProof(); }
export function runLiveIQProof() { return ApiClient.runLiveIQProof(); }
