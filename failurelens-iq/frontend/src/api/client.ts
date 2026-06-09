import { experiments, knowledgeHits, teamProfiles, type Experiment } from "../data/mockData";

const API_BASE = "/api";

async function request<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function fetchExperiments(): Promise<{ total: number; items: Experiment[] }> {
  return request("/experiments", { total: experiments.length, items: experiments });
}

export function fetchKnowledge(query: string) {
  const lowered = query.toLowerCase();
  const hits = knowledgeHits.filter((hit) => {
    const searchable = `${hit.section_title} ${hit.excerpt} ${hit.matched_terms.join(" ")}`.toLowerCase();
    return !query || searchable.includes(lowered);
  });
  return request(`/knowledge/search?q=${encodeURIComponent(query || "minority f1")}`, {
    query,
    hits: hits.length ? hits : knowledgeHits,
    top_relevance: (hits[0] || knowledgeHits[0]).relevance_score,
    retrieval_mode: "local_iq_simulation"
  });
}

export function fetchManagerSummary() {
  return request("/manager/all", {
    "TEAM-B": {
      team_id: "TEAM-B",
      failure_count: 6,
      failure_rate: 0.86,
      vulnerability_level: "high",
      recurring_pattern_alert: "Responsible AI / Bias recurred across recent slice evaluations.",
      recommended_action: "Schedule a fairness review and convert recurring gaps into DP-100/AI-102 practice work.",
      learning_velocity: "needs intervention"
    },
    profiles: teamProfiles
  });
}
