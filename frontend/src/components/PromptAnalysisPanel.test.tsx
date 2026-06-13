import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PromptAnalysisPanel } from "./PromptAnalysisPanel";

describe("PromptAnalysisPanel component", () => {
  it("renders prompt instructions, textarea, and suggestions", () => {
    render(<PromptAnalysisPanel onGenerate={vi.fn()} isGenerating={false} error={null} />);
    
    expect(screen.getByText("Describe a failed ML experiment")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Example: Analyze a churn model/i)).toBeInTheDocument();
    expect(screen.getByText("Generate FailureLens Analysis")).toBeInTheDocument();
    expect(screen.getByText("High accuracy but low minority F1")).toBeInTheDocument();
  });

  it("calls onGenerate with prompt when submitted", () => {
    const handleGenerate = vi.fn();
    render(<PromptAnalysisPanel onGenerate={handleGenerate} isGenerating={false} error={null} />);
    
    const textarea = screen.getByPlaceholderText(/Example: Analyze a churn model/i);
    fireEvent.change(textarea, { target: { value: "Test prompt context" } });
    
    const submitBtn = screen.getByText("Generate FailureLens Analysis");
    fireEvent.click(submitBtn);
    
    expect(handleGenerate).toHaveBeenCalledWith("Test prompt context");
  });

  it("shows loading state when generating", () => {
    render(<PromptAnalysisPanel onGenerate={vi.fn()} isGenerating={true} error={null} />);
    expect(screen.getByText("Generating FailureLens Analysis...")).toBeInTheDocument();
  });

  it("shows error alert when error is provided", () => {
    render(<PromptAnalysisPanel onGenerate={vi.fn()} isGenerating={false} error="Connection failure" />);
    expect(screen.getByText("Connection failure")).toBeInTheDocument();
  });
});
