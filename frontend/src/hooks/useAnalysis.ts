import { useEffect, useMemo, useState } from "react";
import { experiments as mockExperiments, reasoningSteps, type Experiment } from "../data/mockData";
import { API_BASE, generateReport, getCostEstimate, getHealth, getIQStatus, getReadiness, listExperiments, runAnalysisWithOptions, runDemo } from "../api/client";

export function useAnalysis(initialId = "EXP-1001") {
  const [selectedId, setSelectedId] = useState(initialId);
  const [experiments, setExperiments] = useState<Experiment[]>(mockExperiments);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [demoReport, setDemoReport] = useState<any | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [backendDisconnected, setBackendDisconnected] = useState(false);
  const [authRequired, setAuthRequired] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [readiness, setReadiness] = useState<any | null>(null);
  const [iqStatus, setIQStatus] = useState<any | null>(null);
  const [costEstimate, setCostEstimate] = useState<any | null>(null);

  useEffect(() => {
    let mounted = true;
    listExperiments().then((result) => {
      if (!mounted) return;
      setExperiments(result.data.items);
      setBackendDisconnected(result.disconnected);
      setAuthRequired(result.authRequired);
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
    setAuthRequired(result.authRequired);
    setStatusMessage(result.errorMessage || "");
    if (!result.disconnected) {
      setAnalysisResult(result.data);
    }
    setIsRunning(false);
  }

  async function runJudgeDemo() {
    setIsDemoRunning(true);
    const [iqResult, readinessResult, demoResult] = await Promise.all([getIQStatus(), getReadiness(), runDemo()]);
    setBackendDisconnected(iqResult.disconnected || readinessResult.disconnected || demoResult.disconnected);
    setAuthRequired(iqResult.authRequired || readinessResult.authRequired || demoResult.authRequired);
    setStatusMessage(demoResult.errorMessage || readinessResult.errorMessage || iqResult.errorMessage || "");
    setIQStatus(iqResult.data);
    setReadiness(readinessResult.data);
    setDemoReport(demoResult.data);
    setIsDemoRunning(false);
  }

  async function copyDemoSummary() {
    const summary = demoReport?.video_demo_summary || {
      problem: "Failed ML experiments disappear after bad metrics.",
      solution: "FailureLens IQ turns failures into reusable learning intelligence.",
      confidence,
      human_review_required: requiresReview
    };
    await navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
    setStatusMessage("Demo summary copied.");
  }

  async function downloadReport() {
    const result = await generateReport(selectedId);
    setBackendDisconnected(result.disconnected);
    setAuthRequired(result.authRequired);
    setStatusMessage(
      result.authRequired
        ? result.errorMessage || ""
        : result.disconnected
          ? "Backend is disconnected; report generation is unavailable in mock preview."
          : `Report generated: ${(result.data as any).path || "reports"}`
    );
  }

  async function checkBackendHealth() {
    const result = await getHealth();
    setBackendDisconnected(result.disconnected);
    setAuthRequired(result.authRequired);
    const state = result.disconnected ? "Backend is disconnected." : `Backend health: ${(result.data as any).status || "ok"}.`;
    setStatusMessage(state);
  }

  async function checkAzureReadiness() {
    const [readinessResult, iqResult] = await Promise.all([getReadiness(), getIQStatus()]);
    setBackendDisconnected(readinessResult.disconnected || iqResult.disconnected);
    setAuthRequired(readinessResult.authRequired || iqResult.authRequired);
    setReadiness(readinessResult.data);
    setIQStatus(iqResult.data);
    setStatusMessage(readinessResult.disconnected ? "Backend is disconnected." : `Readiness: ${(readinessResult.data as any).status}.`);
  }

  async function checkCostEstimate() {
    const result = await getCostEstimate();
    setBackendDisconnected(result.disconnected);
    setAuthRequired(result.authRequired);
    setCostEstimate(result.data);
    setStatusMessage(result.disconnected ? "Backend is disconnected." : "Cost estimate loaded.");
  }

  async function copyIqComplianceSummary() {
    const summary = {
      microsoft_iq_compliance: demoReport?.microsoft_iq_compliance,
      iqStatus,
      azure_status: demoReport?.azure_status,
      grounding_summary: demoReport?.grounding_summary,
      readiness,
      costEstimate
    };
    await navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
    setStatusMessage("IQ compliance summary copied.");
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
    authRequired,
    statusMessage,
    readiness,
    iqStatus,
    costEstimate,
    apiBase: API_BASE,
    analysisResult,
    demoReport,
    runAnalysis,
    runJudgeDemo,
    copyDemoSummary,
    downloadReport,
    checkBackendHealth,
    checkAzureReadiness,
    checkCostEstimate,
    copyIqComplianceSummary,
    reasoningSteps
  };
}
