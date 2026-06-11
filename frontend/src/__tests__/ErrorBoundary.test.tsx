import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ErrorBoundary } from "../components/ErrorBoundary";

const ProblemChild = () => {
  throw new Error("Test error");
};

describe("ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <div>Test Content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("renders fallback UI when there is an error", () => {
    // Suppress console.error output in test logs for expected error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    
    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>
    );
    expect(screen.getByText("Something went wrong in the demo dashboard.")).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
});
