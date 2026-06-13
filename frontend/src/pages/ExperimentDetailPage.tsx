import React, { useState, useEffect } from "react";
import { useApp } from "../AppContext";
import { Experiment, ApiClient } from "../api/client";
import {
  Sparkles,
  ArrowLeft,
  Award,
  BookOpen,
  ClipboardList,
  Download,
  ShieldCheck,
  ChevronRight,
  GitBranch,
  Search,
  CheckSquare,
  Square
} from "lucide-react";

interface ExperimentDetailPageProps {
  id: string;
  onBack: () => void;
  onNavigate: (path: string) => void;
}

export const ExperimentDetailPage: React.FC<ExperimentDetailPageProps> = ({ id, onBack, onNavigate }) => {
  const { experiments } = useApp();
  const [exp, setExp] = useState<Experiment | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'reasoning' | 'evidence' | 'remediation' | 'certification' | 'report'>('overview');
  const [reportGenerating, setReportGenerating] = useState(false);
  const [reportReady, setReportReady] = useState(false);
  const [checklist, setChecklist] = useState<string[]>([]);

  useEffect(() => {
    // Find matching experiment
    const found = experiments.find(e => e.id === id);
    if (found) {
      setExp(found);
    }
  }, [experiments, id]);

  const toggleChecklist = (fix: string) => {
    setChecklist(prev =>
      prev.includes(fix) ? prev.filter(f => f !== fix) : [...prev, fix]
    );
  };

  const handleGenerateReport = async () => {
    setReportGenerating(true);
    await new Promise(r => setTimeout(r, 2000));
    setReportGenerating(false);
    setReportReady(true);
  };

  if (!exp) {
    return (
      <div className="text-center py-20 animate-fade-in select-none">
        <h3 className="text-xl font-bold text-[#0F172A]">Experiment Trace No Longer Synced</h3>
        <p className="text-xs text-[#64748B] mt-1">This experiment ID could not be loaded from active memory.</p>
        <button
          onClick={onBack}
          className="mt-4 p-2.5 px-6 rounded-xl text-xs font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm cursor-pointer"
        >
          Return to Workspace
        </button>
      </div>
    );
  }

  const tabs: Array<{ id: typeof activeTab; label: string }> = [
    { id: 'overview', label: 'Overview' },
    { id: 'reasoning', label: 'Reasoning Flow' },
    { id: 'evidence', label: 'Internal Evidence' },
    { id: 'remediation', label: 'Remediation Steps' },
    { id: 'certification', label: 'Certification Gate' },
    { id: 'report', label: 'Compliance Report' }
  ];

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      {/* Back click bar */}
      <div className="flex gap-2 items-center">
        <button
          onClick={onBack}
          className="p-1 px-3 text-xs font-semibold text-[#64748B] hover:text-[#0f172a] hover:bg-[#F1F5F9] border border-[#E2E8F0] rounded-xl flex items-center gap-1.5 cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Workspace
        </button>
        <span className="text-slate-300">/</span>
        <span className="text-xs font-mono font-semibold text-[#64748B] uppercase">{exp.id}</span>
      </div>

      {/* Title Segment Card */}
      <div className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm flex flex-wrap items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-1 px-2 rounded-md bg-purple-50 text-[#7C3AED] text-[10px] font-mono font-bold tracking-wide uppercase border border-purple-150">
              {exp.category}
            </span>
            <span className="text-xs font-mono text-[#64748B] font-semibold">{exp.id}</span>
          </div>
          <h2 className="text-2xl font-black text-[#0F172A] mt-2 font-heading">
            {exp.project}
          </h2>
          <p className="text-xs text-[#64748B] mt-1 inline-block">
            Model Base structure: <strong className="text-slate-700">{exp.modelType}</strong>
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] font-mono font-semibold text-[#64748B] uppercase">Citations Grounding</p>
            <p className="text-[#2563EB] font-mono font-bold text-sm">Foundry Verified (Lv. 3)</p>
          </div>
          <div className="p-3 bg-blue-50 text-[#2563EB] rounded-xl border border-blue-100">
            <Award className="w-5 h-5 animate-pulse" />
          </div>
        </div>
      </div>

      {/* SEGMENTED TAB BUTTONS ROW */}
      <div className="border-b border-[#E2E8F0] flex gap-2 overflow-x-auto pb-px">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`p-3 px-5 text-xs font-semibold whitespace-nowrap border-b-2 transition-all cursor-pointer ${
              activeTab === tab.id
                ? "border-[#7C3AED] text-[#7C3AED] font-bold"
                : "border-transparent text-[#64748B] hover:text-[#0F172A]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB CONTAINER WORKSPACE */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 md:p-8 shadow-sm">
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider text-[#64748B]">
                Fail Scenario Log
              </h3>
              <p className="text-xs text-[#0f172a] leading-relaxed mt-2 p-4 bg-slate-50 border border-slate-100 rounded-xl">
                &ldquo;{exp.summary}&rdquo;
              </p>
            </div>

            <div className="pt-4 border-t border-[#E2E8F0]">
              <h3 className="text-sm font-bold text-[#0f172a] uppercase tracking-wider text-[#64748B] flex items-center gap-1.5 font-heading">
                <Sparkles className="w-4 h-4 text-[#7C3AED]" /> Diagnostic Root Cause
              </h3>
              <p className="text-xs text-[#0F172A] leading-relaxed mt-3 bg-[#EEF4FF]/50 border border-[#BFDBFE]/40 p-4 rounded-xl">
                {exp.rootCause}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-[#E2E8F0]">
              <div className="bg-[#FFFDF9] border border-amber-100 p-4 rounded-2xl">
                <h4 className="text-xs font-bold text-[#D97706] uppercase tracking-wider">
                  Trace Details
                </h4>
                <div className="mt-3.5 space-y-2.5 text-xs text-[#64748B]">
                  <p>Timestamp logged: <strong className="text-slate-700">{exp.created}</strong></p>
                  <p>Model Confidence bounds: <strong className="text-slate-700">{exp.confidence}%</strong></p>
                  <p>Database Adapter Target: <strong className="text-slate-700">{exp.iqMode}</strong></p>
                </div>
              </div>

              <div className="bg-[#F8FAFC] border border-[#E2E8F0] p-4 rounded-2xl flex flex-col justify-between">
                <div>
                  <h4 className="text-xs font-bold text-[#64748B] uppercase tracking-wider">
                    Trace Status Checklist
                  </h4>
                  <p className="text-xs text-[#0F172A] mt-2 font-medium">Approved for league submission review.</p>
                </div>
                <button
                  onClick={() => setActiveTab('remediation')}
                  className="mt-4 p-2 px-3 bg-white border border-[#E2E8F0] hover:bg-[#EEF4FF] text-[#2563EB] transition-all text-[11px] font-bold rounded-lg w-fit cursor-pointer"
                >
                  Configure Remediation Playbook
                </button>
              </div>
            </div>
          </div>
        )}

        {/* REASONING FLOW TAB */}
        {activeTab === 'reasoning' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <GitBranch className="w-5 h-5 text-[#2563EB]" />
              <h3 className="text-base font-bold text-[#0F172A] font-heading">Reasoning Agent Sequence Path</h3>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed">
              Below is the serialized step trace calculated by FailureLens IQ specialists during prompt evaluation.
            </p>

            <div className="space-y-6 relative pl-6 border-l-2 border-dashed border-[#E2E8F0] mt-4 ml-2">
              {exp.reasoningSteps.map((step, idx) => (
                <div key={idx} className="relative">
                  {/* Dot */}
                  <span className="absolute left-[-31px] top-px bg-white border-2 border-[#7C3AED] w-4.5 h-4.5 rounded-full flex items-center justify-center text-[9px] font-bold text-[#7C3AED]">
                    {idx + 1}
                  </span>
                  
                  <div>
                    <h5 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider text-[#7C3AED]">
                      {step.split(':')[0]}
                    </h5>
                    <p className="text-xs text-[#64748B] mt-1">
                      {step.split(':')[1] || "Activating metric evaluations and citations scans."}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* EVIDENCE TAB */}
        {activeTab === 'evidence' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-3 mb-4">
              <BookOpen className="w-5 h-5 text-[#7C3AED]" />
              <h3 className="text-base font-bold text-[#0F172A] font-heading">Internal Evidence Sources</h3>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed">
              These factors were retrieved from user diagnostics prompts and correlated against standard Foundry knowledge playbooks.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
              {exp.evidence.map((ev, i) => (
                <div key={i} className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
                  <span className="p-1 px-1.5 rounded-md bg-purple-100 text-[#7C3AED] font-bold text-[8px] uppercase tracking-wider block w-fit mb-2">
                    Evidence Fact {i + 1}
                  </span>
                  <p className="text-xs text-[#0f172a] leading-relaxed font-semibold">
                    {ev}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* REMEDIATION TAB */}
        {activeTab === 'remediation' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-3 mb-4">
              <ClipboardList className="w-5 h-5 text-emerald-600" />
              <h3 className="text-base font-bold text-[#0f172a] font-heading">Recommended Playbooks Correction Checklist</h3>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed">
              Apply these configurations to mitigate future failures. Checking actions aggregates evidence toward league compliance score.
            </p>

            <div className="space-y-3.5 mt-4">
              {exp.recommendedFixes.map((fix, idx) => {
                const isChecked = checklist.includes(fix);
                return (
                  <button
                    key={idx}
                    onClick={() => toggleChecklist(fix)}
                    className={`w-full text-left p-4 rounded-xl border flex items-center gap-3.5 cursor-pointer leading-normal ${
                      isChecked
                        ? "bg-emerald-50/50 border-emerald-300 text-emerald-900"
                        : "bg-white border-[#E2E8F0] text-[#0f172a] hover:bg-slate-50"
                    }`}
                  >
                    {isChecked ? (
                      <CheckSquare className="w-5 h-5 text-emerald-600 shrink-0" />
                    ) : (
                      <Square className="w-5 h-5 text-[#64748B] shrink-0" />
                    )}
                    <span className="text-xs font-semibold">{fix}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* CERTIFICATION GATE TAB */}
        {activeTab === 'certification' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-3">
              <Award className="w-5 h-5 text-[#2563EB]" />
              <h3 className="text-base font-bold text-[#0F172A] font-heading">Microsoft Responsible AI Standards Gateway</h3>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed">
              Review and map compliance metrics directly required for judges evaluation sheets.
            </p>

            <div className="p-5 bg-purple-50 rounded-2xl border border-purple-150 relative overflow-hidden mt-4">
              <span className="p-1 px-2.5 rounded-full text-[9px] font-bold bg-[#7C3AED] text-white tracking-widest block w-fit mb-3 uppercase">
                Aligned Framework
              </span>
              <h4 className="text-sm font-bold text-slate-800 uppercase tracking-tight">
                {exp.certificationMapping}
              </h4>
              <p className="text-xs text-[#64748B] mt-2 leading-relaxed">
                This diagnostic flow maps directly to the active standard for responsible machine learning deployments. This check verifies that continuous model monitoring, proxy variable audits, and evaluation metrics thresholds comply with enterprise safety standards.
              </p>
            </div>
          </div>
        )}

        {/* COMPLIANCE REPORT TAB */}
        {activeTab === 'report' && (
          <div className="space-y-6 animate-fade-in text-center py-8">
            <ShieldCheck className="w-12 h-12 text-[#2563EB] mx-auto opacity-80 mb-3" />
            <h3 className="text-base font-black text-[#0f172a] font-heading">
              Interactive Diagnostic Report
            </h3>
            <p className="text-xs text-[#64748B] max-w-sm mx-auto leading-relaxed">
              Compile all reasoning traces, cited evidence metrics, and playbooks checkmarks into a clean compliance diagnostic report.
            </p>

            <div className="pt-4 flex justify-center gap-3">
              {!reportReady ? (
                <button
                  onClick={handleGenerateReport}
                  className="p-3 px-6 rounded-xl text-xs font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  disabled={reportGenerating}
                >
                  {reportGenerating ? "Compiling metadata..." : "Generate Diagnostic Report"}
                </button>
              ) : (
                <a
                  href={`data:text/plain;charset=utf-8,${encodeURIComponent(JSON.stringify(exp, null, 2))}`}
                  download={`FailureLens_Report_${exp.id}.json`}
                  className="p-3 px-6 rounded-xl text-xs font-semibold text-white bg-[#10B981] hover:bg-[#0D9488] shadow-sm flex items-center gap-1.5 cursor-pointer"
                >
                  <Download className="w-4 h-4" /> Download Compliance Report (.JSON)
                </a>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
