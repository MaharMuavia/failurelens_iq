import { useEffect, useMemo, useState } from "react";
import { experiments as mockExperiments, reasoningSteps, type Experiment } from "../data/mockData";
import { API_BASE, authHeaders, generateReport, getCostEstimate, getHealth, getIQStatus, getReadiness, listExperiments, runAnalysisWithOptions, runDemo } from "../api/client";
import { VIDEO_DEMO_MODE } from "../config/demoMode";

export interface InteractiveReportMetadata {
  generated: boolean;
  format: string;
  download_url: string;
  local_path: string;
}

export function useAnalysis(initialId = "EXP-1001") {
  // Empty guest state if guest mode is true
  const [isEmpty, setIsEmpty] = useState(() => localStorage.getItem("failurelens_guest_mode") === "true");
  const [prompt, setPrompt] = useState("");
  const [generatedExperiment, setGeneratedExperiment] = useState<any | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [interactiveReport, setInteractiveReport] = useState<InteractiveReportMetadata | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedIdState, setSelectedIdState] = useState(() => {
    const isGuest = localStorage.getItem("failurelens_guest_mode") === "true";
    if (isGuest) return "";
    return VIDEO_DEMO_MODE ? "EXP-1001" : initialId;
  });
  const [experiments, setExperiments] = useState<Experiment[]>(mockExperiments);
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

    const isGuest = localStorage.getItem("failurelens_guest_mode") === "true";
    if (!isGuest) {
      runDemo().then((result) => {
        if (!mounted) return;
        setDemoReport(result.data);
        setBackendDisconnected((prev) => prev || result.disconnected);
        setIQStatus(result.data?.microsoft_iq_compliance || null);
      });
    }
    return () => {
      mounted = false;
    };
  }, []);

  const selectedExperiment = useMemo<Experiment>(() => {
    if (isEmpty) {
      return {
        experiment_id: "",
        team_id: "demo-team",
        project_name: "",
        role: "ML Engineer",
        model_type: "",
        dataset_name: "",
        pipeline_stage: "validation",
        target: "",
        validation_strategy: "",
        class_balance: "50/50",
        metrics: {},
        baseline_metrics: {},
        failure_observation: "",
        failure_category_label: "",
        outcome: "failure",
        timestamp: new Date().toISOString()
      } as any;
    }
    return experiments.find((experiment) => experiment.experiment_id === selectedIdState) || experiments[0] || mockExperiments[0];
  }, [experiments, selectedIdState, isEmpty]);

  const finalDemoReport = analysisResult ?? demoReport;

  const confidence = finalDemoReport?.overall_confidence ?? (selectedExperiment.experiment_id === "SPARSE-001" ? 0.34 : selectedExperiment.outcome === "success" ? 0.68 : 0.81);
  const fallbackRequiresReview =
    selectedExperiment.experiment_id === "SPARSE-001" ||
    (selectedExperiment.failure_category_label || "").includes("Responsible AI");
  const requiresReview = finalDemoReport?.requires_human_review ?? fallbackRequiresReview;

  async function generateAnalysis(userPrompt: string) {
    setIsGenerating(true);
    setError(null);
    setPrompt(userPrompt);
    setStatusMessage("Generating experiment and running agents...");

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
          use_foundry_model: false,
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
      setSelectedIdState(data.prompt_id);
      
      setExperiments((prev) => {
        const exists = prev.some((e) => e.experiment_id === data.prompt_id);
        if (exists) return prev;
        
        const ge = data.generated_experiment;
        const newExp = {
          experiment_id: ge.experiment_id,
          team_id: ge.team_id,
          project_name: ge.project_name,
          role: ge.role,
          model_type: ge.model_type,
          dataset_name: ge.dataset_name,
          pipeline_stage: ge.pipeline_stage,
          target: ge.target,
          validation_strategy: ge.validation_strategy,
          class_balance: ge.class_balance,
          metrics: ge.metrics,
          baseline_metrics: ge.baseline_metrics,
          failure_observation: ge.failure_observation,
          failure_category_label: data.analysis_result?.ui_summary?.failure_category || "Unknown",
          outcome: ge.outcome,
          timestamp: ge.timestamp,
          drift_indicators: ge.drift_indicators || [],
          data_quality_signals: ge.data_quality_signals || [],
          suspected_leakage_columns: ge.suspected_leakage_columns || [],
          engineer_notes: ge.engineer_notes || "",
          current_certifications: ge.current_certifications || [],
        };
        return [newExp, ...prev];
      });
      
      setIsEmpty(false);
      setStatusMessage("Agent reasoning complete.");
    } catch (err: any) {
      setError(err.message || "An error occurred during generation");
      setStatusMessage("Generation failed.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function runAnalysis() {
    setIsRunning(true);
    const result = await runAnalysisWithOptions(VIDEO_DEMO_MODE ? "EXP-1001" : selectedIdState);
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
    setSelectedIdState("EXP-1001");
    setIsEmpty(false);
    setStatusMessage("Demo started.");
    const iqResult = await getIQStatus();
    setIQStatus(iqResult.data);
    setStatusMessage(iqResult.disconnected ? "Backend offline fallback." : "IQ proof loaded.");
    const readinessResult = await getReadiness();
    setReadiness(readinessResult.data);
    const demoResult = await runDemo();
    setBackendDisconnected(iqResult.disconnected || readinessResult.disconnected || demoResult.disconnected);
    setAuthRequired(iqResult.authRequired || readinessResult.authRequired || demoResult.authRequired);
    setDemoReport(demoResult.data);
    if (demoResult.disconnected) {
      setStatusMessage("Backend offline fallback.");
    } else if (demoResult.authRequired) {
      setStatusMessage(demoResult.errorMessage || "API key required.");
    } else {
      setStatusMessage("Agent reasoning complete.");
      window.setTimeout(() => setStatusMessage("Report ready."), 700);
    }
    setIsDemoRunning(false);
  }

  async function resetDemo() {
    setAnalysisResult(null);
    setDemoReport(null);
    setReadiness(null);
    setCostEstimate(null);
    setPrompt("");
    setGeneratedExperiment(null);
    setInteractiveReport(null);
    setSelectedIdState("EXP-1001");
    setIsEmpty(false);
    setStatusMessage("Demo reset.");
    await runJudgeDemo();
  }

  async function copyDemoSummary() {
    const summary = finalDemoReport?.video_demo_summary || {
      problem: "Failed ML experiments disappear after bad metrics.",
      solution: "FailureLens IQ turns failures into reusable learning intelligence.",
      confidence,
      human_review_required: requiresReview
    };
    await navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
    setStatusMessage("Demo summary copied.");
  }

  async function downloadReport() {
    const result = await generateReport(VIDEO_DEMO_MODE ? "EXP-1001" : selectedIdState);
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
      microsoft_iq_compliance: finalDemoReport?.microsoft_iq_compliance,
      iqStatus,
      azure_status: finalDemoReport?.azure_status,
      grounding_summary: finalDemoReport?.grounding_summary,
      readiness,
      costEstimate
    };
    await navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
    setStatusMessage("IQ compliance summary copied.");
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
    
    selectedId: selectedIdState,
    setSelectedId: (id: string) => {
      setSelectedIdState(VIDEO_DEMO_MODE ? "EXP-1001" : id);
      setIsEmpty(false);
    },
    selectedExperiment,
    experiments: isEmpty ? [] : experiments,
    confidence: isEmpty ? 0 : confidence,
    requiresReview: isEmpty ? false : requiresReview,
    isRunning,
    isDemoRunning,
    backendDisconnected,
    authRequired,
    statusMessage,
    readiness,
    iqStatus: finalDemoReport?.microsoft_iq_compliance ?? iqStatus,
    costEstimate,
    apiBase: API_BASE,
    demoReport: finalDemoReport,
    runAnalysis,
    runJudgeDemo,
    resetDemo,
    copyDemoSummary,
    downloadReport,
    checkBackendHealth,
    checkAzureReadiness,
    checkCostEstimate,
    copyIqComplianceSummary,
    reasoningSteps
  };
}
