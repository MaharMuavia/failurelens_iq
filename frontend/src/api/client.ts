import { experiments, knowledgeHits, reasoningSteps, type Experiment } from "../data/mockData";

const DEFAULT_API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV
    ? "/api"
    : (typeof window !== "undefined"
        ? window.location.port
          ? window.location.origin.replace(/:\d+$/, ":8000")
          : `${window.location.origin}:8000`
        : "")
  ) ||
  DEFAULT_API_BASE;
const DEMO_API_KEY = import.meta.env.VITE_DEMO_API_KEY || "";

const fallbackAgentFlow = [
  { id: "planner", label: "Planner", status: "completed", confidence: 0.82, summary: "Built execution plan and suspected evaluation failure." },
  { id: "classifier", label: "Failure Classifier", status: "completed", confidence: 0.79, summary: "Detected evaluation methodology failure." },
  { id: "root_cause", label: "Root Cause Analyzer", status: "completed", confidence: 0.83, summary: "Found aggregate accuracy masking minority-class collapse." },
  { id: "historian", label: "Experiment Historian", status: "completed", confidence: 0.76, summary: "Found similar failed validation patterns." },
  { id: "coach", label: "Prescriptive Coach", status: "completed", confidence: 0.8, summary: "Created 3-day and 7-day remediation plan." },
  { id: "certification", label: "Certification Evaluator", status: "completed", confidence: 0.78, summary: "Mapped gap to DP-100 evaluation skills." },
  { id: "manager", label: "Integration Manager", status: "completed", confidence: 0.81, summary: "Prepared manager action summary." },
  { id: "microsoft_iq", label: "Microsoft IQ / Foundry Proof", status: "completed", confidence: 0.9, summary: "Shows honest Foundry IQ local adapter proof.", foundry_iq_status: "local_demo_fallback" }
];

const fallbackCitations = [
  {
    id: "failure-taxonomy-001",
    title: "Evaluation methodology failure",
    source_type: "failure_taxonomy",
    citation: "knowledge/foundry_iq_sources/failure_taxonomy.md#failure-taxonomy-001",
    excerpt: "High accuracy can hide minority-class weakness. Require stratified validation and minority F1 review.",
    permission_scope: "demo",
    relevance_score: 0.91
  }
];

const fallbackDemoReport = {
  demo_title: "Local mock preview",
  run_id: "mock-preview-exp-1001",
  demo_mode_label: "Mock preview only",
  executive_summary: "EXP-1001 failed because high aggregate accuracy hid minority-class failure.",
  agent_flow: fallbackAgentFlow,
  agent_workflow: fallbackAgentFlow.map((agent) => ({
    agent_name: agent.label,
    role: agent.summary,
    status: agent.status,
    confidence_score: agent.confidence,
    findings: [agent.summary],
    recommended_next_actions: ["Run slice-level validation and preserve this learning trace."]
  })),
  reasoning_timeline: reasoningSteps,
  metric_story: {
    headline: "High accuracy hid minority-class failure",
    accuracy: 0.93,
    minority_f1: 0.14,
    roc_auc: 0.72,
    message: "93% accuracy hides 14% minority F1.",
    callout: "The model looked successful until the minority class was inspected."
  },
  ui_summary: {
    main_takeaway: "EXP-1001 failed because aggregate accuracy hid class-level failure.",
    business_value: "The failed run becomes reusable team memory instead of disappearing after a bad metric.",
    next_best_action: "Run slice-level validation, preserve the reasoning trace, and assign the 7-day remediation plan.",
    judge_hook: "This is not just a classifier; it is a learning memory system."
  },
  foundry_iq_layer: {
    mode: "local_foundry_iq_adapter",
    label: "Foundry IQ Local Adapter Mode",
    selected_iq_layer: "Foundry IQ",
    live_azure: false,
    adapter_ready: true,
    knowledge_sources: [],
    citations_count: fallbackCitations.length,
    permission_aware_metadata: true,
    judge_safe_explanation: "This demo mirrors Foundry IQ locally and can switch to live Azure when quota is approved."
  },
  iq_grounding_story: {
    query: "EXP-1001 evaluation methodology minority F1 remediation certification",
    retrieved_evidence: fallbackCitations,
    citations: fallbackCitations,
    how_agents_used_iq: [
      "Classifier used taxonomy evidence",
      "Root cause analyzer used experiment history",
      "Coach used remediation playbook",
      "Certification evaluator used Microsoft skill mapping"
    ]
  },
  root_cause_analysis: {
    root_cause: "EXP-1001 used holdout validation with class_balance=88/12; accuracy=0.93 hid minority_f1=0.14, so the evaluation method did not measure the failure mode that mattered.",
    violated_assumption: "The reported accuracy represented operational quality for the minority class.",
    knowledge_gap: "Imbalanced classification evaluation, minority F1, and stratified validation practice.",
    confidence: 0.83,
    requires_human_review: false,
    evidence: ["class_balance=88/12 → minority class risk", "accuracy=0.93 → headline metric can hide minority errors", "minority_f1=0.14 → minority performance weakness"],
    counter_evidence: ["suspected_leakage_columns=[] → no direct leakage column evidence", "drift_indicators=[] → no direct deployment drift evidence"],
    hypothesis_conflict: false,
  },
  failure_classification: {
    failure_category: "evaluation_methodology",
    confidence: 0.79,
    conflicting_categories: [],
    reasoning: "Evaluation methodology is strongest among six rules; leakage and drift signals are not active.",
  },
  confidence_summary: {
    overall_confidence: 0.81,
    requires_human_review: false,
    gate_passed: true,
    human_review_reason: ""
  },
  microsoft_iq_compliance: {
    required_iq_layer: "Foundry IQ",
    proof_level: "local_demo_fallback",
    foundry_iq_label: "Foundry IQ Local Adapter Mode",
    foundry_iq_mode: "local_foundry_iq_adapter",
    compliance_status: "ready_for_demo",
    live_microsoft_iq: false,
    source_types: ["local_foundry_iq_adapter"],
    honest_limitation: "Azure quota is 0, so this demo uses local Foundry IQ adapter mode.",
    judge_explanation:
      "FailureLens IQ implements the base architecture of Foundry IQ locally: knowledge sources, retrieval, citations, permission metadata, and grounded reasoning agents."
  },
  grounding_summary: {
    source_types: ["local_foundry_iq_adapter"],
    citations_count: 3
  },
  video_demo_summary: {
    solution: "FailureLens IQ turns failed experiments into learning intelligence with reasoning agents, grounding, confidence gates, and certification mapping.",
    reasoning_steps: 21,
    confidence: 0.81,
    human_review_required: false
  }
};

export type ApiState<T> = {
  data: T;
  disconnected: boolean;
  authRequired: boolean;
  status?: number;
  errorMessage?: string;
};

function authHeaders(): Record<string, string> {
  return DEMO_API_KEY ? { "X-API-Key": DEMO_API_KEY } : {};
}

async function request<T>(path: string, fallback: T, init?: RequestInit): Promise<ApiState<T>> {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...((init?.headers || {}) as Record<string, string>)
    };
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers
    });
    if (response.status === 401) {
      return {
        data: fallback,
        disconnected: false,
        authRequired: true,
        status: response.status,
        errorMessage: "API key required. Set VITE_DEMO_API_KEY in frontend environment."
      };
    }
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return { data: (await response.json()) as T, disconnected: false, authRequired: false, status: response.status };
  } catch (error) {
    return {
      data: fallback,
      disconnected: true,
      authRequired: false,
      errorMessage: error instanceof Error ? error.message : "Backend disconnected"
    };
  }
}

export function getHealth() {
  return request("/health", {
    status: "disconnected",
    app_mode: "demo",
    version: "local-preview",
    experiments_loaded: experiments.length,
    knowledge_chunks_indexed: knowledgeHits.length,
    enabled_integrations: {
      local_iq: true,
      azure_openai: false,
      azure_ai_search: false,
      azure_blob_storage: false,
      azure_cosmos_db: false
    },
    demo_ready: false
  });
}

export function getAgents() {
  return request("/agents", []);
}

export function getReadiness() {
  return request("/readiness", { status: "demo_ready", score: 0, checks: {}, recommendations: [] });
}

export function getIQStatus() {
  return request("/iq/status", {
    required_by_hackathon: true,
    selected_iq_layer: "Foundry IQ",
    implementation: "Azure AI Search grounded retrieval connected to FailureLens reasoning agents",
    current_mode: "local_foundry_iq_adapter",
    foundry_iq_label: "Foundry IQ Local Adapter Mode",
    active_provider: "FoundryIQLocalAdapter",
    active_iq_provider: "FoundryIQLocalAdapter",
    active_reasoning_provider: "local",
    live_microsoft_iq: false,
    proof_level: "local_demo_fallback",
    adapter_ready: true,
    foundry_iq_base_architecture: true,
    knowledge_sources_configured: true,
    permission_metadata_supported: true,
    agentic_retrieval_supported: true,
    implemented_paths: {
      azure_ai_search_adapter: true,
      azure_openai_adapter: true,
      local_grounding_fallback: true,
      openai_fallback_provider: true
    },
    live_services: {
      azure_ai_search: false,
      azure_openai: false,
      azure_cosmos_db: false,
      azure_blob_storage: false
    },
    demo_services: {
      local_knowledge_index: true,
      synthetic_experiment_history: true
    },
    compliance_status: "ready_for_demo",
    citations_supported: true,
    reasoning_trace_supported: true,
    uncertainty_supported: true,
    confidence_supported: true,
    honest_limitation: "Azure quota is 0, so this demo uses local Foundry IQ adapter mode.",
    judge_explanation:
      "FailureLens IQ implements the base architecture of Foundry IQ locally: knowledge sources, retrieval, citations, permission metadata, and grounded reasoning agents."
  });
}

export function getCostEstimate() {
  return request("/cost/estimate", { azure_openai: { cost_guard_enabled: true }, recommendations: [] });
}

export function listExperiments() {
  return request<{ total: number; items: Experiment[] }>("/experiments", { total: experiments.length, items: experiments });
}

export function runDemo() {
  return request("/demo/run", fallbackDemoReport, { method: "POST" });
}

export function runAnalysis(experimentId: string) {
  return request(`/analysis/run/${encodeURIComponent(experimentId)}`, {}, { method: "POST" });
}

export function runAnalysisWithOptions(experimentId: string) {
  return request(
    "/analysis/run",
    {},
    {
      method: "POST",
      body: JSON.stringify({
        experiment_id: experimentId,
        options: {
          include_reasoning_trace: true,
          include_grounding: true,
          include_certification: true
        }
      })
    }
  );
}

export function streamAnalysis(experimentId: string) {
  return new EventSource(`${API_BASE}/analysis/stream/${encodeURIComponent(experimentId)}`);
}

export function searchKnowledge(q: string) {
  const safeQuery = q || "minority f1";
  const lowered = safeQuery.toLowerCase();
  const hits = knowledgeHits.filter((hit) => `${hit.section_title} ${hit.excerpt} ${hit.matched_terms.join(" ")}`.toLowerCase().includes(lowered));
  return request(`/knowledge/search?q=${encodeURIComponent(safeQuery)}`, {
    query: safeQuery,
    hits: hits.length ? hits : knowledgeHits,
    top_relevance: (hits[0] || knowledgeHits[0]).relevance_score,
    retrieval_mode: "local_iq_simulation"
  });
}

export function generateReport(experimentId: string) {
  return request(`/report/${encodeURIComponent(experimentId)}/generate`, {}, { method: "POST" });
}

export { API_BASE, DEMO_API_KEY, authHeaders };
