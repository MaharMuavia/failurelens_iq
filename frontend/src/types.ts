export interface Experiment {
  id: string;
  project: string;
  modelType: string;
  category: string;
  confidence: number;
  iqMode: 'offline-mock' | 'local-foundry' | 'foundry-live' | 'azure-live';
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
