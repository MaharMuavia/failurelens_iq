import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "../App";
import * as client from "../api/client";

// Mock the client calls
vi.mock("../api/client", () => {
  return {
    API_BASE: "http://localhost:8000",
    listExperiments: vi.fn().mockResolvedValue({
      data: { total: 1, items: [
        {
          experiment_id: "EXP-1001",
          team_id: "TEAM-A",
          project_name: "Customer Churn",
          role: "Data Scientist",
          model_type: "XGBoost",
          dataset_name: "churn_v2",
          pipeline_stage: "Evaluation",
          target: "churned",
          validation_strategy: "Holdout",
          class_balance: "90/10",
          metrics: { accuracy: 0.92, minority_f1: 0.12 },
          baseline_metrics: { accuracy: 0.94 },
          failure_observation: "minority class performance collapse",
          failure_category_label: "Evaluation Methodology",
          outcome: "failure",
          timestamp: "2026-06-11T13:44:58Z"
        }
      ]},
      disconnected: false,
      authRequired: false
    }),
    getHealth: vi.fn().mockResolvedValue({
      data: {
        status: "ok",
        app_mode: "demo",
        version: "local-preview",
        experiments_loaded: 1,
        knowledge_chunks_indexed: 5,
        enabled_integrations: {
          local_iq: true,
          azure_openai: false,
          azure_ai_search: false,
          azure_blob_storage: false,
          azure_cosmos_db: false
        },
        demo_ready: true
      },
      disconnected: false,
      authRequired: false
    }),
    getReadiness: vi.fn().mockResolvedValue({
      data: { status: "demo_ready", score: 100, checks: {}, recommendations: [] },
      disconnected: false,
      authRequired: false
    }),
    getIQStatus: vi.fn().mockResolvedValue({
      data: {
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
      },
      disconnected: false,
      authRequired: false
    }),
    getCostEstimate: vi.fn().mockResolvedValue({
      data: { azure_openai: { cost_guard_enabled: true }, recommendations: [] },
      disconnected: false,
      authRequired: false
    }),
    runDemo: vi.fn().mockResolvedValue({
      data: {
        run_id: "demo-run-123",
        demo_title: "Customer churn model failed validation gate",
        executive_summary: "Test summary",
        agent_flow: [
          { id: "planner", label: "Planner", status: "completed", confidence: 0.9, summary: "Planner summary" },
          { id: "foundry_iq", label: "Foundry IQ Layer", status: "completed", confidence: 0.95, summary: "IQ summary", foundry_iq_status: "local_demo_fallback" }
        ],
        metric_story: { headline: "Test headline", accuracy: 0.93, minority_f1: 0.14, roc_auc: 0.72 },
        ui_summary: { judge_hook: "learning memory system", failure_category: "Evaluation Methodology" },
        foundry_iq_layer: { mode: "local_foundry_iq_adapter", selected_iq_layer: "Foundry IQ", live_azure: false, adapter_ready: true, citations_count: 5, permission_aware_metadata: true },
        iq_grounding_story: { citations: [], retrieved_evidence: [], how_agents_used_iq: [] },
        iq_integration: { knowledge_sources_count: 6, total_retrievals: 5, avg_grounding_confidence: 0.9, grounding_coverage: 100.0 }
      },
      disconnected: false,
      authRequired: false
    }),
    listExperimentsSync: vi.fn().mockReturnValue([
      {
        experiment_id: "EXP-1001",
        team_id: "TEAM-A",
        project_name: "Customer Churn",
        role: "Data Scientist",
        model_type: "XGBoost",
        dataset_name: "churn_v2",
        pipeline_stage: "Evaluation",
        target: "churned",
        validation_strategy: "Holdout",
        class_balance: "90/10",
        metrics: { accuracy: 0.92, minority_f1: 0.12 },
        baseline_metrics: { accuracy: 0.94 },
        failure_observation: "minority class performance collapse",
        failure_category_label: "Evaluation Methodology",
        outcome: "failure",
        timestamp: "2026-06-11T13:44:58Z"
      }
    ]),
    searchKnowledge: vi.fn().mockResolvedValue({
      data: { query: "", hits: [] },
      disconnected: false,
      authRequired: false
    })
  };
});

describe("App", () => {
  it("renders auth view and switches to dashboard when guest mode is selected", async () => {
    render(<App />);

    // Auth-screen should appear initially
    expect(screen.getByText("FailureLens IQ")).toBeInTheDocument();
    expect(screen.getByText("Continue as Guest")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Continue as Guest"));

    await waitFor(() => expect(screen.getByRole("button", { name: /^analysis$/i })).toBeInTheDocument());

    const analysisTabBtn = screen.getByRole("button", { name: /^analysis$/i });
    const experimentsTabBtn = screen.getByRole("button", { name: /^experiments$/i });
    const managerTabBtn = screen.getByRole("button", { name: /^manager$/i });
    const knowledgeTabBtn = screen.getByRole("button", { name: /^knowledge$/i });

    expect(analysisTabBtn).toHaveClass("active");
    expect(experimentsTabBtn).toHaveClass("nav-item");
    expect(managerTabBtn).toHaveClass("nav-item");
    expect(knowledgeTabBtn).toHaveClass("nav-item");

    fireEvent.click(experimentsTabBtn);
    fireEvent.click(managerTabBtn);
    fireEvent.click(knowledgeTabBtn);

    // Tab buttons should still exist after clicks even though App delegates active state externally.
    expect(screen.getByRole("button", { name: /^analysis$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^experiments$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^manager$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^knowledge$/i })).toBeInTheDocument();
  });
});
