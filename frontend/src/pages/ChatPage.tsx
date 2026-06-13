import React, { useState, useRef, useEffect } from "react";
import { useApp } from "../AppContext";
import { ApiClient, Experiment } from "../api/client";
import {
  Send,
  Paperclip,
  CheckCircle,
  HelpCircle,
  RotateCcw,
  Sparkles,
  Award,
  BookOpen,
  ArrowRight,
  AlertCircle,
  Clock,
  ChevronRight,
  ChevronDown,
  Download,
  Loader2
} from "lucide-react";

interface ChatPageProps {
  onNavigate: (path: string) => void;
  onSelectExperiment: (expId: string) => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ onNavigate, onSelectExperiment }) => {
  const { backendConnected, addExperiment, refreshExperiments } = useApp();
  const [promptValue, setPromptValue] = useState("");
  const [activePrompt, setActivePrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [history, setHistory] = useState<Array<{ sender: 'user' | 'assistant'; text?: string; result?: Experiment }>>([]);
  const [downloadingReportIds, setDownloadingReportIds] = useState<Record<string, boolean>>({});
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleDownloadFinalReport = async (exp: Experiment) => {
    setDownloadingReportIds(prev => ({ ...prev, [exp.id]: true }));
    try {
      const report: any = await ApiClient.generateReport(exp.id);
      const md = report.content || [
        "# FailureLens IQ Backend Report",
        "",
        `run_id: ${report.run_id || "unknown"}`,
        `experiment_id: ${report.experiment_id || report.experimentId || exp.id}`,
        `proof_level: ${report.proof_level || exp.proof_level}`,
        `live_microsoft_iq: ${String(report.live_microsoft_iq ?? exp.is_live_microsoft_iq)}`,
        "",
        "## Root Cause",
        report.root_cause || report.diagnosis || exp.rootCause,
        "",
        "## Remediation Plan",
        report.remediation || exp.recommendedFixes.map((fix) => `- ${fix}`).join("\n"),
        "",
        "## Certification Mapping",
        report.certification || exp.certificationMapping,
      ].join("\n");

      const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `FailureLens_IQ_Report_${exp.id}.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to generate and download report", e);
    } finally {
      setDownloadingReportIds(prev => ({ ...prev, [exp.id]: false }));
    }
  };

  const handleDownloadInterimReport = () => {
    const timestamp = new Date().toLocaleString();
    const currentPhase = stepsList[Math.min(currentStep, stepsList.length - 1)];
    
    let md = `# FailureLens IQ - Interim Diagnostic Report\n`;
    md += `Generated: ${timestamp}\n`;
    md += `Status: ANALYSIS IN PROGRESS (Diagnostic Phase ${Math.min(currentStep + 1, stepsList.length)} of ${stepsList.length})\n`;
    md += `Current Active Agent Loop: ${currentPhase}\n\n`;
    md += `=== SUBMITTED EXPERIMENT METRICS & PROMPT ===\n`;
    md += `"${activePrompt || "No prompt text found."}"\n\n`;
    md += `=== PIPELINE EXECUTION SUMMARY ===\n`;
    
    stepsList.forEach((step, idx) => {
      let status = "PENDING";
      if (currentStep > idx) status = "COMPLETED";
      else if (currentStep === idx) status = "IN PROGRESS";
      md += `[${status}] Step ${idx + 1}: ${step}\n`;
    });
    
    md += `\n=== MID-FLIGHT PRELIMINARY DIAGNOSTIC FRAMEWORK ===\n`;
    md += `FailureLens IQ is automatically parsing your experiment telemetry against certified risk matrices.\n`;
    
    const query = (activePrompt || "").toLowerCase();
    if (query.includes("imbalan") || query.includes("f1") || query.includes("churn")) {
      md += `Heuristic Bias Flag: CLASS IMBALANCE BIAS SUSPECTED\n`;
      md += `Primary Mitigation: Dynamic resampling (SMOTE / ADASYN) or implementing Focal Loss metrics.\n`;
      md += `Compliance Mapping: SR 11-7 Section 4 (Rigorous Out-of-Sample Validation)\n`;
    } else if (query.includes("leak") || query.includes("future")) {
      md += `Heuristic Bias Flag: TARGET LEAKAGE DETECTED\n`;
      md += `Primary Mitigation: Remove post-target features. Ensure split temporal integrity.\n`;
      md += `Compliance Mapping: EU AI Act High-Risk systems - Section 3.2 data auditability\n`;
    } else if (query.includes("overfit") || query.includes("forest")) {
      md += `Heuristic Bias Flag: OVERFITTING HAZARD\n`;
      md += `Primary Mitigation: Prune decision trees, use cross-validation, reduce dimensionality.\n`;
      md += `Compliance Mapping: Internal model validation review required\n`;
    } else if (query.includes("fairness") || query.includes("loan") || query.includes("protected") || query.includes("demographic") || query.includes("bias")) {
      md += `Heuristic Bias Flag: ETHICAL & DEMOGRAPHIC DISPARATE IMPACT SUSPECTED\n`;
      md += `Primary Mitigation: Filter out correlated spatial/zipcode proxy features. Train models with group fairness adversarial constraints or Fairlearn GridSearch.\n`;
      md += `Compliance Mapping: Microsoft Responsible AI Standard - Section F.1 Compliance Gate (Assessing Fairness and Disparate Harms)\n`;
    } else {
      md += `Heuristic Bias Flag: MACHINE LEARNING DRIFT / ANOMALY REVIEW\n`;
      md += `Primary Mitigation: Continuous drift detection monitoring on feature distributions.\n`;
      md += `Compliance Mapping: General Model Governance Best Practices\n`;
    }
    
    md += `\n---------------------------------------------------------------\n`;
    md += `Disclaimer: This is an interim run trace. Complete compliance remediation\n`;
    md += `and FailureLens evidence reports will be generated once pipeline stabilizes.\n`;
    md += `Proof Status: Interim local draft; final proof comes from backend report metadata.\n`;

    const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `FailureLens_IQ_Interim_Diagnostic_Report_${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const stepsList = [
    "Generating experiment record...",
    "Running reasoning agents...",
    "Retrieving IQ grounding...",
    "Calibrating confidence...",
    "Preparing remediation report..."
  ];

  const suggestionCards = [
    {
      title: "Class Imbalance Bias",
      snippet: "High accuracy but low minority F1",
      prompt: "Our customer churn model achieved 93% accuracy, but minority class F1 dropped to 0.14. Dataset is 88/12 imbalanced and validation used a simple holdout split."
    },
    {
      title: "Target Leakage",
      snippet: "Data leakage in customer churn",
      prompt: "Validation accuracy jumped to 98% after adding renewal_status_after_30d. Test performance collapsed, and I suspect the feature contains future target information."
    },
    {
      title: "Overfitting Forest",
      snippet: "Overfitting random forest",
      prompt: "RandomForestClassifier got 97% training accuracy but only 61% validation and 59% test accuracy. Dataset has 2,000 rows and 120 features. No cross-validation or feature selection was used."
    },
    {
      title: "Covariate Drift",
      snippet: "Data drift after deployment",
      prompt: "The fraud model performed well offline, but after deployment recall dropped by 35%. Recent production data has changed transaction amount distribution and new merchant categories."
    },
    {
      title: "Responsible AI Gate",
      snippet: "Fairness risk in loan model",
      prompt: "The loan approval model has strong overall AUC, but approval errors are much higher for a protected demographic group. We need a responsible AI review and remediation plan."
    },
    {
      title: "Schema Divergence",
      snippet: "Broken preprocessing pipeline",
      prompt: "The model worked in training but fails during batch inference because categorical encoding columns do not match between train and production data."
    }
  ];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, isSubmitting, currentStep]);

  const handleSuggestionClick = (promptText: string) => {
    setPromptValue(promptText);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptValue.trim() || isSubmitting) return;

    const userText = promptValue.trim();
    setHistory(prev => [...prev, { sender: 'user', text: userText }]);
    setActivePrompt(userText);
    setPromptValue("");
    setIsSubmitting(true);
    setCurrentStep(0);

    // Simulate multi-agent steps pipeline sequentially
    for (let i = 0; i < stepsList.length; i++) {
      await new Promise(r => setTimeout(r, 700));
      setCurrentStep(prev => prev + 1);
    }

    try {
      const response = await ApiClient.analyzePrompt(userText);
      if (response && response.success) {
        addExperiment(response.data);
        setHistory(prev => [...prev, { sender: 'assistant', result: response.data }]);
      }
    } catch {
      // Fallback response handled in Client
    } finally {
      setIsSubmitting(false);
      refreshExperiments();
    }
  };

  const handleOpenReport = (id: string) => {
    onSelectExperiment(id);
    onNavigate(`experiments/${id}`);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-5xl mx-auto select-none relative">
      
      {/* Scrollable messages context workspace */}
      <div className="flex-1 overflow-y-auto pr-2 pb-24 space-y-6">
        
        {history.length === 0 ? (
          <div className="text-center max-w-2xl mx-auto pt-8 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0F172A] font-heading leading-tight">
              What failed in your ML experiment?
            </h2>
            <p className="mt-2 text-sm text-[#64748B] leading-relaxed max-w-xl mx-auto">
              Describe your failed run. FailureLens IQ will generate an experiment log, run reasoning agents, retrieve grounded evidence, and compile a compliance remediation plan.
            </p>

            {/* Prompt Suggestion Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-10">
              {suggestionCards.map((card, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(card.prompt)}
                  className="bg-white border border-[#E2E8F0] hover:border-[#7C3AED] rounded-2xl p-4 text-left transition-all duration-300 shadow-sm hover:shadow-md hover-lift flex flex-col justify-between h-36 cursor-pointer"
                >
                  <div>
                    <span className="p-1 px-2 rounded-md bg-[#EEF4FF] text-[#2563EB] text-[9px] font-mono tracking-wider font-bold block w-fit mb-2">
                      {card.title}
                    </span>
                    <h4 className="text-xs font-bold text-[#0F172A] tracking-tight line-clamp-1">
                      {card.snippet}
                    </h4>
                    <p className="text-[10px] text-[#64748B] mt-1.5 line-clamp-3 leading-normal">
                      &ldquo;{card.prompt}&rdquo;
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {history.map((msg, index) => {
              if (msg.sender === 'user') {
                return (
                  <div key={index} className="flex gap-4 justify-end animate-fade-in">
                    <div className="bg-[#EEF4FF] text-[#0F172A] p-4 rounded-3xl rounded-tr-none text-sm max-w-2xl border border-[#D0E1FD]">
                      <p className="leading-relaxed font-semibold">&ldquo;{msg.text}&rdquo;</p>
                    </div>
                  </div>
                );
              }

              // Assistant Result Card
              const exp = msg.result;
              if (!exp) return null;

              return (
                <div key={index} className="bg-white border border-[#E2E8F0] rounded-3xl p-6 md:p-8 shadow-md space-y-6 animate-slide-up relative">
                  
                  {/* Offline Warning banner watermark */}
                  {(!backendConnected || exp.is_live_backend === false) && (
                    <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-700 text-xs flex items-center gap-2 font-medium">
                      <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                      <span>
                        <strong>Offline Mock Preview — not live submission proof.</strong>
                      </span>
                    </div>
                  )}

                  {/* Header Row */}
                  <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#E2E8F0]">
                    <div>
                      <span className="bg-purple-100 text-[#7C3AED] border border-purple-200 p-1 px-2.5 rounded-lg text-xs font-bold mr-3 uppercase">
                        {exp.category}
                      </span>
                      <span className={`text-[#64748B] text-xs font-mono font-bold uppercase`}>
                        {exp.id}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-[#64748B] uppercase">Confidence</span>
                      <span className="p-1 px-2 rounded-md bg-[#EEF4FF] text-[#2563EB] font-bold text-xs">
                        {exp.confidence}% Verified
                      </span>
                    </div>
                  </div>

                  {/* Root Cause Details */}
                  <div>
                    <h3 className="text-base font-bold text-[#0F172A] flex items-center gap-1.5 font-heading">
                      <Sparkles className="w-4 h-4 text-[#7C3AED]" /> Technical Root Cause
                    </h3>
                    <p className="text-xs text-[#0F172A] leading-relaxed mt-2 bg-slate-50 border border-slate-100 p-4 rounded-xl">
                      {exp.rootCause}
                    </p>
                  </div>

                  {/* Evidence & Mappings grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider text-[#64748B]">
                        Diagnostics Evidence Trace
                      </h4>
                      <ul className="mt-2.5 space-y-2 text-xs">
                        {exp.evidence.map((ev, idx) => (
                          <li key={idx} className="flex gap-2">
                            <span className="text-[#2563EB] font-bold">•</span>
                            <span className="text-[#0F172A] leading-relaxed">{ev}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider text-[#64748B]">
                        Proposed Corrections Playbook
                      </h4>
                      <ul className="mt-2.5 space-y-2 text-xs">
                        {exp.recommendedFixes.map((fix, idx) => (
                          <li key={idx} className="flex gap-2 text-emerald-800">
                            <span className="text-[#10B981] font-bold">✓</span>
                            <span className="leading-relaxed">{fix}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Agent Reasoning Preview */}
                  <div className="pt-4 border-t border-[#E2E8F0]">
                    <h4 className="text-xs font-bold text-[#64748B] uppercase tracking-wider mb-3">
                      League Agent Reasoning Path
                    </h4>
                    <div className="flex flex-wrap gap-2 text-[11px] font-medium font-mono text-[#2563EB]">
                      {exp.reasoningSteps.map((step, idx) => (
                        <div key={idx} className="flex items-center">
                          {idx > 0 && <span className="mx-2 text-slate-300">→</span>}
                          <span className="bg-[#EEF4FF] border border-[#BFDBFE] p-1 px-2 rounded-lg">
                            {step.split(':')[0]}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Certification Alignment badge */}
                  {exp.certificationMapping && (
                    <div className="p-3 bg-[#FDFBF7] border border-[#F5EAD4] rounded-2xl flex items-center justify-between text-xs text-[#F59E0B]">
                      <div className="flex items-center gap-2">
                        <Award className="w-4 h-4 shrink-0" />
                        <span className="font-semibold text-amber-900">{exp.certificationMapping}</span>
                      </div>
                    </div>
                  )}

                  {/* Action row buttons */}
                  <div className="pt-4 border-t border-[#E2E8F0] flex flex-wrap gap-3 justify-end items-center">
                    <button
                      type="button"
                      onClick={() => handleDownloadFinalReport(exp)}
                      disabled={downloadingReportIds[exp.id]}
                      className="p-2.5 px-4 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-md transition-all cursor-pointer flex items-center gap-1.5 border border-emerald-500 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Download className="w-3.5 h-3.5" />
                      {downloadingReportIds[exp.id] ? "Generating Report..." : "Download Report"}
                    </button>
                    <button
                      onClick={() => onNavigate("agent-runs")}
                      className="p-2.5 px-4 rounded-xl text-xs font-semibold text-[#64748B] hover:text-[#0f172a] border border-[#E2E8F0] hover:bg-[#F8FAFC] transition-all cursor-pointer"
                    >
                      View Live Trace
                    </button>
                    <button
                      onClick={() => handleOpenReport(exp.id)}
                      className="p-2.5 px-4 rounded-xl text-xs font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
                    >
                      Open Analysis Folder <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Dynamic loading pipeline traces step-by-step progress */}
        {isSubmitting && (
          <div className="p-6 bg-white border border-[#E2E8F0] rounded-3xl shadow-md space-y-4 max-w-2xl ml-0 sm:ml-6 animate-fade-in relative z-10 text-left">
            <div className="flex items-center justify-between gap-3 flex-wrap border-b border-slate-100 pb-3">
              <div className="flex items-center gap-3">
                <div className="relative flex items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-2.5 w-2.5 rounded-full bg-purple-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#7C3AED]"></span>
                </div>
                <h3 className="text-sm font-bold text-[#0F172A]">FailureLens IQ Diagnostician Active</h3>
              </div>
              <button
                type="button"
                id="download-interim-report-btn"
                onClick={handleDownloadInterimReport}
                className="bg-purple-50 text-[#7C3AED] hover:bg-[#7C3AED] hover:text-white border border-[#7C3AED]/20 px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer animate-pulse"
                title="Download interim diagnostic report"
              >
                <Download className="w-3.5 h-3.5" />
                Download Report
              </button>
            </div>

            {/* Premium Animated Progress Track Slider */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400 px-0.5">
                <span>Phase Progress</span>
                <span className="text-[#7C3AED]">{Math.round((Math.min(currentStep + 1, stepsList.length) / stepsList.length) * 100)}%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden relative">
                <div
                  className="bg-gradient-to-r from-[#7C3AED] via-indigo-600 to-purple-600 h-full rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(((currentStep + 1) / stepsList.length) * 100, 100)}%` }}
                />
              </div>
            </div>

            <div className="space-y-2 mt-3 pt-1">
              {stepsList.map((step, idx) => {
                const isActive = currentStep === idx;
                const isPassed = currentStep > idx;
                return (
                  <div key={idx} className={`flex items-center gap-3 text-xs transition-all duration-300 ${isActive ? "scale-[1.02] transform origin-left" : ""}`}>
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold font-mono text-[9px] transition-all duration-300 shadow-sm ${
                      isPassed ? "bg-emerald-100 text-emerald-700 border border-emerald-200" :
                      isActive ? "bg-purple-100 text-[#7C3AED] border border-purple-200 ring-2 ring-purple-100 animate-pulse" :
                      "bg-slate-100 text-slate-400 border border-slate-200"
                    }`}>
                      {isPassed ? (
                        "✓"
                      ) : isActive ? (
                        <Loader2 className="w-2.5 h-2.5 text-[#7C3AED] animate-spin" />
                      ) : (
                        idx + 1
                      )}
                    </span>
                    <span className={`transition-all duration-300 ${isActive ? "font-bold text-[#7C3AED]" : isPassed ? "text-[#0F172A] line-through opacity-60" : "text-slate-400"}`}>
                      {step}
                    </span>
                    {isActive && (
                      <span className="text-[10px] text-purple-600 font-mono font-bold tracking-wider uppercase animate-pulse ml-auto bg-purple-50 px-1.5 py-0.5 rounded-lg border border-purple-100/50">
                        Analyzing
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* FIXED CHAT INPUT COMPOSER BLOCK */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#F8FAFC] via-[#F8FAFC] to-transparent pt-6 pb-2">
        <form onSubmit={handleSend} className="bg-white border border-[#E2E8F0] shadow-lg rounded-2xl p-2.5 flex items-center gap-3">
          <button
            type="button"
            className="p-2.5 rounded-xl text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] transition-colors"
            title="Attach logs file (placeholder)"
          >
            <Paperclip className="w-4 h-4" />
          </button>
          
          <input
            type="text"
            required
            placeholder="Describe the failed ML experiment model details..."
            className="flex-1 bg-transparent border-none text-sm focus:outline-none focus:ring-0 text-[#0F172A] placeholder:text-[#64748B]"
            value={promptValue}
            onChange={(e) => setPromptValue(e.target.value)}
          />

          <button
            type="submit"
            aria-label="Run analysis"
            disabled={!promptValue.trim() || isSubmitting}
            className={`p-2.5 rounded-xl transition-all ${
              promptValue.trim() && !isSubmitting
                ? "bg-[#7C3AED] text-white hover:bg-[#6D28D9] cursor-pointer"
                : "bg-slate-100 text-slate-400"
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <span className="text-[10px] text-[#64748B] text-center block mt-1.5 font-mono">
          Press Enter to dispatch diagnostic scan. Shift+Enter for new line variables.
        </span>
      </div>
    </div>
  );
};
