import { useState } from "react";
import { API_BASE, authHeaders } from "../api/client";

export interface InteractiveReportMetadata {
  generated: boolean;
  format: string;
  download_url: string;
  local_path: string;
}

export function usePromptAnalysis() {
  const [isEmpty, setIsEmpty] = useState(true);
  const [prompt, setPrompt] = useState("");
  const [generatedExperiment, setGeneratedExperiment] = useState<any | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [interactiveReport, setInteractiveReport] = useState<InteractiveReportMetadata | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generateAnalysis(userPrompt: string) {
    setIsGenerating(true);
    setError(null);
    setPrompt(userPrompt);

    try {
      const response = await fetch(`${API_BASE}/prompt/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify({
          prompt: userPrompt,
          team_id: "demo-team",
          use_foundry_model: false, // Default to deterministic locally
          generate_report: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate analysis: status ${response.status}`);
      }

      const data = await response.json();
      setGeneratedExperiment(data.generated_experiment);
      setAnalysisResult(data.analysis_result);
      setInteractiveReport(data.interactive_report);
      setIsEmpty(false);
    } catch (err: any) {
      setError(err.message || "An error occurred during generation");
    } finally {
      setIsGenerating(false);
    }
  }

  function reset() {
    setIsEmpty(true);
    setPrompt("");
    setGeneratedExperiment(null);
    setAnalysisResult(null);
    setInteractiveReport(null);
    setError(null);
    setIsGenerating(false);
  }

  return {
    isEmpty,
    prompt,
    generatedExperiment,
    analysisResult,
    interactiveReport,
    isGenerating,
    error,
    generateAnalysis,
    reset,
  };
}
