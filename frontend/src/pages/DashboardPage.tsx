import React, { useState } from "react";
import { useApp } from "../AppContext";
import { MetricCard } from "../components/common/MetricCard";
import {
  TrendingUp,
  AlertTriangle,
  Award,
  BookOpen,
  FolderSync,
  Clock,
  ShieldAlert,
  Sparkles,
  CheckCircle,
  HelpCircle,
  Play
} from "lucide-react";

interface DashboardPageProps {
  onNavigate: (path: string) => void;
  onSelectExperiment: (expId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate, onSelectExperiment }) => {
  const { experiments, backendConnected, iqStatus } = useApp();
  const [actionQueue, setActionQueue] = useState([
    { id: "EXP-1001", project: "Credit Churn Predictor", issue: "Low minority class F1 bias checks fail.", priority: "High" },
    { id: "EXP-1003", project: "Loan Disbursal Engine", issue: "Demographic zipcode correlation trigger.", priority: "Medium" }
  ]);

  const handleActionResolve = (id: string) => {
    setActionQueue(prev => prev.filter(a => a.id !== id));
  };

  const handleExperimentClick = (id: string) => {
    onSelectExperiment(id);
    onNavigate(`experiments/${id}`);
  };

  // Compile calculations safely from experiments context
  const totalFailed = experiments.length ? experiments.length + 3 : 6;
  const humanAudits = actionQueue.length;
  const avgConfidence = experiments.length 
    ? Math.round(experiments.reduce((acc, curr) => acc + curr.confidence, 0) / experiments.length)
    : 81;

  return (
    <div className="space-y-8 select-none">
      
      {/* Page Header block */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
            Executive Dashboard
          </h2>
          <p className="text-sm text-[#64748B]">
            Systemic analysis, bias coverage trackers, and team learning certifications status.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="p-1 px-3 rounded-full text-xs font-mono font-bold bg-[#E6FDF9] text-[#0D9488] border border-teal-150">
            {backendConnected ? "Live Connection" : "Offline Simulator Active"}
          </span>
        </div>
      </div>

      {/* METRIC CARDS ROW GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Failed Runs Logged"
          value={totalFailed}
          change="+12% weekly"
          subtext="across diagnostic databases"
          icon={ShieldAlert}
          accentColor="text-rose-600"
        />

        <MetricCard
          title="Action Review Queue"
          value={humanAudits}
          change={humanAudits > 0 ? "Requires Audit" : "All Approved"}
          isPositive={humanAudits === 0}
          subtext="pending manager sign-off"
          icon={AlertTriangle}
          accentColor="text-amber-500"
        />

        <MetricCard
          title="Average Confidence Rating"
          value={`${avgConfidence}%`}
          change="Optimal"
          subtext="across reasoning agents"
          icon={TrendingUp}
          accentColor="text-[#2563EB]"
        />

        <MetricCard
          title="Microsoft IQ Proof Level"
          value={iqStatus.citations_count > 5 ? "Level 3 Gold" : "Level 1 Standard"}
          subtext="with grounded citations"
          icon={Award}
          accentColor="text-purple-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4">
        {/* RECENT ANALYSES LIST TABLE */}
        <div className="lg:col-span-8 bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-4">
            <h3 className="text-lg font-bold text-[#0F172A] font-heading">
              Latest Experiment Diagnostics Memory
            </h3>
            <button
              onClick={() => onNavigate("experiments")}
              className="text-xs font-bold text-[#2563EB] hover:underline"
            >
              See all logs
            </button>
          </div>

          <div className="divide-y divide-slate-100 overflow-x-auto">
            {experiments.slice(0, 5).map((exp) => (
              <div
                key={exp.id}
                onClick={() => handleExperimentClick(exp.id)}
                className="py-4 flex gap-4 items-center justify-between hover:bg-slate-50 hover:scale-[1.01] hover:shadow-xs hover:translate-x-1 p-2 rounded-xl transition-all duration-300 transform cursor-pointer min-w-[500px]"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-red-50 text-rose-600 font-bold text-xs uppercase transition-all duration-300 group-hover:scale-105">
                    Fail
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-[#0F172A]">
                      {exp.project}
                    </h4>
                    <p className="text-xs text-[#64748B] mt-0.5 max-w-sm truncate">
                      {exp.rootCause}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <span className="p-1 px-2.5 rounded-md bg-[#EEF4FF] text-[#2563EB] text-[10px] font-mono font-bold uppercase hover:scale-105 transition-transform duration-300">
                    {exp.category}
                  </span>
                  <div className="text-right">
                    <p className="text-xs font-mono font-bold">{exp.id}</p>
                    <p className="text-[10px] text-slate-400 font-mono">{exp.created}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MANAGER ACTION QUEUE RIGHT SIDEBAR */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300">
            <h3 className="text-base font-bold text-[#0f172a] border-b border-[#E2E8F0] pb-4 mb-4 font-heading">
              Manager Action Queue
            </h3>

            {actionQueue.length === 0 ? (
              <div className="text-center py-8 text-xs text-[#64748B]">
                <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                <p className="font-semibold text-[#0F172A]">Compliances all clear</p>
                <p className="mt-0.5">No audits currently waiting reviewer sign-off.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {actionQueue.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl border border-amber-100 bg-[#FFFDF9] hover:bg-[#FFFDF4] hover:-translate-y-1 hover:scale-[1.02] hover:shadow-md transition-all duration-300 transform flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="p-1 px-1.5 rounded-md bg-amber-100 text-[#D97706] text-[9px] font-bold tracking-wider uppercase">
                          {item.priority} Audit
                        </span>
                        <span className="text-[10px] font-mono font-bold font-semibold text-slate-400">
                          {item.id}
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-[#0F172A] mt-2 leading-tight">
                        {item.project}
                      </h4>
                      <p className="text-[10px] text-[#64748B] mt-1 leading-normal">
                        {item.issue}
                      </p>
                    </div>

                    <div className="mt-4 flex gap-2 justify-end">
                      <button
                        onClick={() => handleActionResolve(item.id)}
                        className="p-1.5 px-3 rounded-lg text-[10px] font-semibold text-white bg-emerald-600 hover:bg-emerald-700 hover:scale-[1.05] hover:shadow-xs transition-all duration-300 transform cursor-pointer"
                      >
                        Approve Path
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* TEAM LEARNING GAP MATRIX MOCK */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 hover:scale-[1.02] transition-all duration-300 transform">
            <h3 className="text-base font-bold text-[#0F172A] border-b border-[#E2E8F0] pb-3 mb-4 font-heading">
              Certification Gap Matrix
            </h3>

            <div className="space-y-3.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-[#64748B]">Target Leakage Guarding</span>
                <span className="font-semibold text-emerald-600">92% Compliance</span>
              </div>
              <div className="w-full bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '92%' }}></div>
              </div>

              <div className="flex justify-between items-center pt-1">
                <span className="text-[#64748B]">Demographic Fairness Coverage</span>
                <span className="font-semibold text-[#2563EB]">81% Compliance</span>
              </div>
              <div className="w-full bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden">
                <div className="bg-[#2563EB] h-full rounded-full" style={{ width: '81%' }}></div>
              </div>

              <div className="flex justify-between items-center pt-1">
                <span className="text-[#64748B]">Continuous Schema Verification</span>
                <span className="font-semibold text-rose-500">64% Compliance</span>
              </div>
              <div className="w-full bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full rounded-full" style={{ width: '64%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
