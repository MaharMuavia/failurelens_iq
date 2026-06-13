import { renderHook, act } from "@testing-library/react";
import { describe, expect, it, vi, beforeAll } from "vitest";
import { usePromptAnalysis } from "./usePromptAnalysis";

describe("usePromptAnalysis hook", () => {
  beforeAll(() => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        prompt_id: "PROMPT-12345",
        original_prompt: "Test prompt",
        generated_experiment: { experiment_id: "PROMPT-12345" },
        analysis_result: { outcome: "failure" },
        interactive_report: { download_url: "/report/PROMPT-12345/interactive" }
      })
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  it("starts in empty state", () => {
    const { result } = renderHook(() => usePromptAnalysis());
    
    expect(result.current.isEmpty).toBe(true);
    expect(result.current.prompt).toBe("");
    expect(result.current.generatedExperiment).toBeNull();
    expect(result.current.isGenerating).toBe(false);
  });

  it("submits prompt and populates results", async () => {
    const { result } = renderHook(() => usePromptAnalysis());
    
    await act(async () => {
      await result.current.generateAnalysis("Test prompt");
    });
    
    expect(result.current.isEmpty).toBe(false);
    expect(result.current.prompt).toBe("Test prompt");
    expect(result.current.generatedExperiment).toEqual({ experiment_id: "PROMPT-12345" });
    expect(result.current.analysisResult).toEqual({ outcome: "failure" });
    expect(result.current.interactiveReport?.download_url).toBe("/report/PROMPT-12345/interactive");
  });
});
