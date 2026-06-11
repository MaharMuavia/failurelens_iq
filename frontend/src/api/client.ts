import { experiments, knowledgeHits, type Experiment } from "../data/mockData";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DEMO_API_KEY = import.meta.env.VITE_DEMO_API_KEY || "";

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

export function getCostEstimate() {
  return request("/cost/estimate", { azure_openai: { cost_guard_enabled: true }, recommendations: [] });
}

export function listExperiments() {
  return request<{ total: number; items: Experiment[] }>("/experiments", { total: experiments.length, items: experiments });
}

export function runDemo() {
  return request("/demo/run", { demo_title: "Local mock preview", reasoning_timeline: [], agent_workflow: [] }, { method: "POST" });
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
  const lowered = q.toLowerCase();
  const hits = knowledgeHits.filter((hit) => `${hit.section_title} ${hit.excerpt} ${hit.matched_terms.join(" ")}`.toLowerCase().includes(lowered));
  return request(`/knowledge/search?q=${encodeURIComponent(q || "minority f1")}`, {
    query: q,
    hits: hits.length ? hits : knowledgeHits,
    top_relevance: (hits[0] || knowledgeHits[0]).relevance_score,
    retrieval_mode: "local_iq_simulation"
  });
}

export function generateReport(experimentId: string) {
  return request(`/report/${encodeURIComponent(experimentId)}/generate`, {}, { method: "POST" });
}

export { API_BASE, DEMO_API_KEY, authHeaders };
