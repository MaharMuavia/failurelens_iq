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
  iqLevel: number;
  duration: string;
  created: string;
  trace: {
    [agentName: string]: {
      role: string;
      status: 'Completed' | 'Pending' | 'Active';
      confidence: number;
      steps: string[];
      evidence: string[];
      nextAction?: string;
    };
  };
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
