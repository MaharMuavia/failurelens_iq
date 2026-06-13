import React from "react";
import { MOCK_AGENT_RUNS } from "../api/client";
import { GitBranch, Clock, ChevronRight, CheckCircle, HelpCircle, Activity } from "lucide-react";

interface AgentRunsPageProps {
  onNavigate: (path: string) => void;
  onSelectRun: (runId: string) => void;
}

export const AgentRunsPage: React.FC<AgentRunsPageProps> = ({ onNavigate, onSelectRun }) => {
  const runs = MOCK_AGENT_RUNS;

  const pipelineSteps = [
    "Planner",
    "Classifier",
    "Root Cause",
    "Historian",
    "Coach",
    "Certification",
    "Manager"
  ];

  const handleRowClick = (runId: string) => {
    onSelectRun(runId);
    onNavigate(`agent-runs/${runId}`);
  };

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
          Multi-Agent Runs & Traces
        </h2>
        <p className="text-sm text-[#64748B]">
          Trace chronological steps, diagnostic routines, confidence scores, and outputs of individual reasoning agent roles.
        </p>
      </div>

      {/* VISUAL PIPELINE FLOW SCHEMATIC */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm overflow-hidden space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
          <Activity className="w-5 h-5 text-[#7C3AED]" />
          <h3 className="text-sm font-bold text-[#0f172a] uppercase tracking-wider text-[#64748B]">
            FailReasoning Pipeline Standard Path
          </h3>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 py-4 text-xs font-semibold font-mono">
          {pipelineSteps.map((step, idx) => (
            <div key={idx} className="flex items-center">
              {idx > 0 && <ChevronRight className="w-4 h-4 text-slate-300 mx-1 shrink-0" />}
              <div className="p-2.5 px-4 rounded-xl border bg-[#F8FAFC] border-[#E2E8F0] text-[#0f172a] flex items-center gap-1.5 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-[#7C3AED]"></span>
                <span>{step}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AGENT RUNS LIST TABLE */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#FAFBFD] border-b border-[#E2E8F0] text-xs font-bold text-[#64748B] uppercase tracking-wider">
                <th className="p-4 pl-6">Run ID</th>
                <th className="p-4">Target Experiment ID</th>
                <th className="p-4">Execution Status</th>
                <th className="p-4">Confidence</th>
                <th className="p-4">Microsoft IQ Level</th>
                <th className="p-4">Completed Duration</th>
                <th className="p-4">Created Date</th>
                <th className="p-4 text-right pr-6">Trace Folder</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {runs.map((run) => (
                <tr
                  key={run.runId}
                  onClick={() => handleRowClick(run.runId)}
                  className="hover:bg-[#F8FAFC]/70 cursor-pointer transition-colors"
                >
                  <td className="p-4 pl-6 font-mono font-semibold text-[#2563EB]">{run.runId}</td>
                  <td className="p-4 font-semibold text-slate-600 font-mono">{run.experimentId}</td>
                  <td className="p-4">
                    <span className="p-1 px-2.5 rounded-md bg-emerald-50 text-emerald-700 font-bold text-[10px] tracking-wide inline-flex items-center gap-1 border border-emerald-100 uppercase">
                      <CheckCircle className="w-3 h-3 text-emerald-700" /> Completed
                    </span>
                  </td>
                  <td className="p-4 font-black">{run.confidence}% Verified</td>
                  <td className="p-4">
                    <span className="p-1 px-1.5 rounded-md text-[9px] font-mono font-bold bg-purple-150 text-[#7C3AED]">
                      Level {run.iqLevel} Grounded
                    </span>
                  </td>
                  <td className="p-4 font-mono text-slate-400">{run.duration}</td>
                  <td className="p-4 text-slate-500">{run.created}</td>
                  <td className="p-4 text-right pr-6">
                    <button className="p-1 px-2 bg-slate-100 hover:bg-[#EEF4FF] hover:text-[#2563EB] transition-colors rounded-lg text-[10px] font-bold">
                      Inspect Trace
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
