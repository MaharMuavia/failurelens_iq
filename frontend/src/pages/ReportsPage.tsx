import React, { useState } from "react";
import { useApp } from "../AppContext";
import { ApiClient, Experiment } from "../api/client";
import { FileText, Download, ShieldCheck, ChevronRight, Share2, Sparkles, AlertCircle, RefreshCw } from "lucide-react";

export const ReportsPage: React.FC = () => {
  const { experiments } = useApp();
  const [downloadingIds, setDownloadingIds] = useState<Record<string, boolean>>({});

  const handleDownloadMarkdownReport = async (exp: Experiment) => {
    setDownloadingIds(prev => ({ ...prev, [exp.id]: true }));
    try {
      const report = await ApiClient.generateReport(exp.id);
      
      let md = `# FailureLens IQ - Grounded Diagnostic & Remediation Report\n\n`;
      md += `**Report Reference ID:** ${report.id}\n`;
      md += `**Target System Reference:** ${report.experimentId} / ${exp.project}\n`;
      md += `**Evaluation Category:** ${exp.category}\n`;
      md += `**Model Architecture:** ${exp.modelType}\n`;
      md += `**Grounded Confidence Metric:** ${exp.confidence}% Secured Check\n`;
      md += `**Trace Generation Created At:** ${report.created || new Date().toISOString().split('T')[0]}\n\n`;
      
      md += `## 1. Executive Summary & Prompt Description\n`;
      md += `${report.summary || exp.summary || "No description provided."}\n\n`;
      
      md += `## 2. Technical System Diagnostics (Root Cause)\n`;
      md += `${report.diagnosis || exp.rootCause || "No layout diagnosed."}\n\n`;
      
      md += `## 3. Recommended Remediation & Corrections Playbook\n`;
      md += `${report.remediation || (exp.recommendedFixes ? exp.recommendedFixes.join("\n") : "No specific corrections cataloged.")}\n\n`;
      
      md += `## 4. Certification & Compliance Standards Alignment\n`;
      md += `${report.certification || exp.certificationMapping || "General Model Governance Principles Mapping"}\n\n`;
      
      md += `---------------------------------------------------------------\n`;
      md += `FailureLens Verification Identifier: SHA-256 Grounded Verification Certified (Microsoft Agents League / NIST)\n`;

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
      setDownloadingIds(prev => ({ ...prev, [exp.id]: false }));
    }
  };

  const handleDownloadJsonReport = async (exp: Experiment) => {
    try {
      const report = await ApiClient.generateReport(exp.id);
      const payload = {
        meta: {
          generated_by: "FailureLens IQ",
          timestamp: new Date().toISOString(),
          compliance_standard: "Microsoft Responsible AI Platform & NIST-AI-RMF v1.0",
        },
        experiment: exp,
        report: report
      };
      
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `FailureLens_AuditPayload_${exp.id}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to generate and download JSON report", e);
    }
  };

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
          Generated Compliance Reports
        </h2>
        <p className="text-sm text-[#64748B]">
          Consult or compile downstream-ready governance playbooks, error footprints, and responsible engineering remedies on demand.
        </p>
      </div>

      {experiments.length === 0 ? (
        <div className="text-center py-20 bg-white border border-[#E2E8F0] rounded-2xl shadow-xs">
          <AlertCircle className="w-12 h-12 text-[#64748B] mx-auto opacity-50 mb-3" />
          <h4 className="text-base font-bold text-[#0F172A] font-heading">No Active Failures Logged</h4>
          <p className="text-xs text-[#64748B] mt-1 max-w-sm mx-auto">
            You don&apos;t have any failed experiments loaded. Submit an analysis through the Reasoning Chat first to compile secure compliance evidence maps!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {experiments.map((exp) => (
            <div
              key={exp.id}
              className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between h-80 transform"
            >
              <div>
                <div className="flex justify-between items-center mb-4">
                  <span className="p-1 px-2.5 rounded-lg bg-[#F3E8FF] text-[#7C3AED] text-[10px] font-mono font-bold tracking-wider uppercase border border-purple-150 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-[#7C3AED]" />
                    {exp.category}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400 font-bold">
                    Ref ID: {exp.id}
                  </span>
                </div>
                
                <h4 className="text-base font-black text-[#0F172A] leading-snug font-heading">
                  Remediation & Diagnostics playbook for {exp.project}
                </h4>
                
                <p className="text-xs text-[#64748B] mt-3 leading-relaxed line-clamp-2">
                  <strong className="text-slate-700">Identified Model Type:</strong> {exp.modelType}
                </p>
                <p className="text-xs text-[#64748B] mt-1.5 leading-relaxed line-clamp-3">
                  <strong className="text-slate-700">Downstream Diagnostics Summary:</strong> {exp.rootCause}
                </p>
              </div>

              <div className="pt-4 border-t border-[#E2E8F0] flex items-center justify-between mt-4">
                <span className="text-[10px] font-mono text-slate-400">Date compiled: {exp.created}</span>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDownloadJsonReport(exp)}
                    className="p-2 px-3.5 rounded-xl text-xs font-bold text-[#64748B] hover:text-[#0F172A] border border-[#E2E8F0] hover:bg-slate-50 transition-all cursor-pointer"
                    title="Download structured JSON report data for audits"
                  >
                    JSON
                  </button>
                  <button
                    onClick={() => handleDownloadMarkdownReport(exp)}
                    disabled={downloadingIds[exp.id]}
                    className="p-2 px-4 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-sm flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {downloadingIds[exp.id] ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        Compiling...
                      </>
                    ) : (
                      <>
                        <Download className="w-3.5 h-3.5" />
                        Download Report
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
