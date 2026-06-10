import { useEffect, useMemo, useState } from "react";
import { experiments as mockExperiments, reasoningSteps, type Experiment } from "../data/mockData";
import { listExperiments, runAnalysisWithOptions, runDemo } from "../api/client";

export function useAnalysis(initialId = "EXP-1001") {
  const [selectedId, setSelectedId] = useState(initialId);
  const [experiments, setExperiments] = useState<Experiment[]>(mockExperiments);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [demoReport, setDemoReport] = useState<any | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [backendDisconnected, setBackendDisconnected] = useState(false);

  useEffect(() => {
    let mounted = true;
    listExperiments().then((result) => {
      if (!mounted) return;
      setExperiments(result.data.items);
      setBackendDisconnected(result.disconnected);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const selectedExperiment = useMemo<Experiment>(() => {
    return experiments.find((experiment) => experiment.experiment_id === selectedId) || experiments[0] || mockExperiments[0];
  }, [experiments, selectedId]);

  const confidence = analysisResult?.overall_confidence ?? (selectedExperiment.experiment_id === "SPARSE-001" ? 0.34 : selectedExperiment.outcome === "success" ? 0.68 : 0.81);
  const fallbackRequiresReview =
    selectedExperiment.experiment_id === "SPARSE-001" ||
    selectedExperiment.failure_category_label.includes("Responsible AI");
  const requiresReview = analysisResult?.requires_human_review ?? fallbackRequiresReview;

  async function runAnalysis() {
    setIsRunning(true);
    const result = await runAnalysisWithOptions(selectedId);
    setBackendDisconnected(result.disconnected);
    if (!result.disconnected) {
      setAnalysisResult(result.data);
    }
    setIsRunning(false);
  }

  async function runJudgeDemo() {
    setIsDemoRunning(true);
    const result = await runDemo();
    setBackendDisconnected(result.disconnected);
    setDemoReport(result.data);
    setIsDemoRunning(false);
  }

  return {
    selectedId,
    setSelectedId,
    selectedExperiment,
    experiments,
    confidence,
    requiresReview,
    isRunning,
    isDemoRunning,
    backendDisconnected,
    analysisResult,
    demoReport,
    runAnalysis,
    runJudgeDemo,
    reasoningSteps
  };
}
