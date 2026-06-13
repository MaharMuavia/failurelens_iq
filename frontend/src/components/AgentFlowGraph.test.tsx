import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AgentFlowGraph } from "./AgentFlowGraph";

describe("AgentFlowGraph component", () => {
  it("renders all nine judge-facing agents", () => {
    render(<AgentFlowGraph demoReport={{ agent_flow: [] }} />);

    expect(screen.getByText("Planner")).toBeInTheDocument();
    expect(screen.getByText("Foundry IQ Layer")).toBeInTheDocument();
    expect(screen.getByText("Failure Classifier")).toBeInTheDocument();
    expect(screen.getByText("Root Cause Analyzer")).toBeInTheDocument();
    expect(screen.getByText("Experiment Historian")).toBeInTheDocument();
    expect(screen.getByText("Prescriptive Coach")).toBeInTheDocument();
    expect(screen.getByText("Certification Evaluator")).toBeInTheDocument();
    expect(screen.getByText("Integration Manager")).toBeInTheDocument();
    expect(screen.getByText("Judge Report")).toBeInTheDocument();
  });
});
