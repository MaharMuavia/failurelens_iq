import { useMemo, useState } from "react";
import { experiments, reasoningSteps, type Experiment } from "../data/mockData";

export function useAnalysis(initialId = "EXP-1001") {
  const [selectedId, setSelectedId] = useState(initialId);
  const [isRunning, setIsRunning] = useState(false);

  const selectedExperiment = useMemo<Experiment>(() => {
    return experiments.find((experiment) => experiment.experiment_id === selectedId) || experiments[0];
  }, [selectedId]);

  const confidence = selectedExperiment.experiment_id === "SPARSE-001" ? 0.34 : selectedExperiment.outcome === "success" ? 0.68 : 0.81;
  const requiresReview =
    selectedExperiment.experiment_id === "SPARSE-001" ||
    selectedExperiment.failure_category_label.includes("Responsible AI");

  function runAnalysis() {
    setIsRunning(true);
    window.setTimeout(() => setIsRunning(false), 900);
  }

  return {
    selectedId,
    setSelectedId,
    selectedExperiment,
    confidence,
    requiresReview,
    isRunning,
    runAnalysis,
    reasoningSteps
  };
}
