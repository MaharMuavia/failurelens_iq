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
    getHealth: vi.fn(),
    getReadiness: vi.fn(),
    getCostEstimate: vi.fn(),
    runDemo: vi.fn(),
    listExperimentsSync: vi.fn(),
    searchKnowledge: vi.fn().mockResolvedValue({
      data: { query: "", hits: [] },
      disconnected: false,
      authRequired: false
    })
  };
});

describe("App", () => {
  it("renders workspace, and switches tabs when navigation buttons are clicked", async () => {
    render(<App />);

    // Check brand name exists
    expect(screen.getByText("FailureLens IQ")).toBeInTheDocument();
    
    // Tab switching check
    const analysisTabBtn = screen.getByRole("button", { name: /^analysis$/i });
    const experimentsTabBtn = screen.getByRole("button", { name: /^experiments$/i });
    const managerTabBtn = screen.getByRole("button", { name: /^manager$/i });
    const knowledgeTabBtn = screen.getByRole("button", { name: /^knowledge$/i });

    // Assert that active class is on Analysis button
    expect(analysisTabBtn).toHaveClass("active");
    expect(experimentsTabBtn).not.toHaveClass("active");

    // Click on "Experiments" tab
    fireEvent.click(experimentsTabBtn);
    expect(experimentsTabBtn).toHaveClass("active");
    expect(analysisTabBtn).not.toHaveClass("active");

    // Click on "Manager" tab
    fireEvent.click(managerTabBtn);
    expect(managerTabBtn).toHaveClass("active");
    expect(experimentsTabBtn).not.toHaveClass("active");
    
    // Click on "Knowledge" tab
    fireEvent.click(knowledgeTabBtn);
    expect(knowledgeTabBtn).toHaveClass("active");
    expect(managerTabBtn).not.toHaveClass("active");
  });
});
