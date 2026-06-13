import React, { useState, useEffect } from "react";
import { MOCK_AGENT_RUNS, AgentRun } from "../api/client";
import { ArrowLeft, Clock, Code, ChevronRight, Play, AlertCircle, Cpu } from "lucide-react";

interface AgentRunDetailPageProps {
  id: string;
  onBack: () => void;
}

export const AgentRunDetailPage: React.FC<AgentRunDetailPageProps> = ({ id, onBack }) => {
  const [run, setRun] = useState<AgentRun | null>(null);
  const [showJson, setShowJson] = useState(false);

  useEffect(() => {
    const found = MOCK_AGENT_RUNS.find(r => r.runId === id);
    if (found) {
      setRun(found);
    } else {
      setRun(MOCK_AGENT_RUNS[0]);
    }
  }, [id]);

  if (!run) {
    return (
      <div className="text-center py-20 select-none">
        <h3 className="text-xl font-bold">Trace Loading...</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      {/* Back click bar */}
      <div className="flex gap-2 items-center">
        <button
          onClick={onBack}
          className="p-1 px-3 text-xs font-semibold text-[#64748B] hover:text-[#0f172a] hover:bg-[#F1F5F9] border border-[#E2E8F0] rounded-xl flex items-center gap-1.5 cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Runs
        </button>
        <span className="text-slate-300">/</span>
        <span className="text-xs font-mono font-semibold text-[#64748B] uppercase">{run.runId}</span>
      </div>

      {/* Header Info Block */}
      <div className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm flex flex-wrap items-center justify-between gap-6">
        <div>
          <span className="text-xs font-mono text-[#64748B] font-semibold uppercase">Run Trace Active</span>
          <h2 className="text-2xl font-black text-[#0F172A] mt-1 font-heading">
            Reasoning Pipeline {run.runId}
          </h2>
          <p className="text-xs text-[#64748B] mt-1.5 inline-block">
            Target diagnostics: <strong className="text-slate-700 font-mono">{run.experimentId}</strong>
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] font-mono font-semibold text-[#64748B]">Duration Logged</p>
            <p className="font-bold font-mono text-slate-800 text-sm">{run.duration}</p>
          </div>
          <div className="p-3 bg-purple-50 text-[#7C3AED] rounded-xl border border-purple-100">
            <Cpu className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* CHRONOLOGICAL SPECIALTY AGENT TRACKER CARDS */}
      <div className="space-y-6">
        <h3 className="text-base font-bold text-[#0F172A] border-b border-[#E2E8F0] pb-3 font-heading">
          Decentralized Agent Sequences Log
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(run.trace).map(([agentName, rawData]) => {
            const data = rawData as any;
            return (
              <div key={agentName} className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm relative overflow-hidden flex flex-col justify-between h-80">
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-sm font-black text-[#0F172A] font-heading">{agentName} Agent</h4>
                      <span className="text-[10.5px] text-[#64748B] font-medium block mt-0.5">{data.role}</span>
                    </div>
                    <span className="p-1 px-2 rounded-md bg-emerald-50 text-emerald-700 font-bold text-[9px] uppercase border border-emerald-100">
                      {data.status}
                    </span>
                  </div>

                  <div className="mt-5 space-y-3 text-xs">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-[#64748B] uppercase">Execution Steps</span>
                      <ul className="mt-1.5 space-y-1 text-slate-600 pl-3 list-disc">
                        {data.steps.map((st: string, i: number) => (
                          <li key={i} className="leading-tight">{st}</li>
                        ))}
                      </ul>
                    </div>

                    {data.evidence.length > 0 && (
                      <div className="pt-2">
                        <span className="text-[10px] font-mono font-bold text-[#64748B] uppercase">Compilations / Evidence</span>
                        <p className="text-xs text-[#0f172a] italic mt-1 font-medium leading-relaxed bg-[#F8FAFC] p-2 rounded-lg">
                          &ldquo;{data.evidence[0]}&rdquo;
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-[#E2E8F0] flex items-center justify-between text-[11px] font-semibold text-[#2563EB]">
                  <span>Self Confidence: {data.confidence}%</span>
                  {data.nextAction && (
                    <span className="text-[#64748B]">Next action: {data.nextAction}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* RAW JSON CONFIGS TOGGLE FOOTER */}
      <div className="bg-[#FAFBFD] border border-[#E2E8F0] rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-bold text-[#0F172A]">Raw Traces Configuration Data</h4>
            <p className="text-xs text-[#64748B]">Access the raw parameters calculated at epoch creation.</p>
          </div>
          <button
            onClick={() => setShowJson(!showJson)}
            className="p-2 px-4 bg-white hover:bg-slate-50 border border-[#E2E8F0] text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Code className="w-4 h-4 text-[#64748B]" /> {showJson ? "Collapse Trace JSON" : "Expand Trace JSON"}
          </button>
        </div>

        {showJson && (
          <div className="mt-6">
            <pre className="bg-[#1E1E24] text-[#F8F8F2] p-5 rounded-2xl text-xs overflow-x-auto font-mono select-text">
              {JSON.stringify(run, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
