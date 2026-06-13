import React from "react";
import { Award, ShieldAlert, Sparkles, MoveRight, Layers, ArrowRight, GitBranch } from "lucide-react";

interface LandingPageProps {
  onStartDemo: () => void;
  onViewArchitecture?: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStartDemo, onViewArchitecture }) => {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] selection:bg-[#7C3AED]/20 relative overflow-hidden font-sans">
      {/* Decorative Blur Blobs to match portfolio branding */}
      <div className="absolute top-[-200px] left-[-100px] w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-[#7C3AED]/10 to-[#2563EB]/10 blur-[130px] animate-pulse-blob-1 pointer-events-none z-0"></div>
      <div className="absolute top-[400px] right-[-100px] w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-[#06B6D4]/10 to-[#7C3AED]/10 blur-[120px] animate-pulse-blob-2 pointer-events-none z-0"></div>

      {/* Top Header / Nav standard client */}
      <header className="relative max-w-7xl mx-auto px-6 h-20 flex items-center justify-between z-10 border-b border-[#E2E8F0]/50">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#2563EB] flex items-center justify-center text-white font-bold text-lg shadow-md">
            FL
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-[#0F172A]">FailureLens IQ</h1>
            <span className="text-[9px] font-mono tracking-wider font-bold text-[#64748B] uppercase block">
              REASONING AGENTS LEAGUE
            </span>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#64748B]">
          <a href="#problem" className="hover:text-[#2563EB] transition-colors">Core Problem</a>
          <a href="#workflow" className="hover:text-[#2563EB] transition-colors">Agent Workflow</a>
          <a href="#micro-iq" className="hover:text-[#2563EB] transition-colors">Microsoft IQ Proof</a>
          <a href="#value" className="hover:text-[#2563EB] transition-colors">Enterprise Value</a>
        </nav>

        <div>
          <button
            onClick={onStartDemo}
            className="p-2.5 px-5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-[#7C3AED] to-[#2563EB] hover:shadow-lg hover:shadow-purple-500/10 hover-lift transition-all cursor-pointer"
          >
            Launch Demo App
          </button>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="relative max-w-7xl mx-auto px-6 pt-16 md:pt-24 pb-20 z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7 flex flex-col justify-center text-left">
          {/* Track Badges */}
          <div className="flex flex-wrap gap-2 mb-6">
            <span className="p-1 px-3.5 rounded-full text-[11px] font-bold bg-[#F3E8FF] text-[#7C3AED] border border-purple-200 tracking-wide uppercase">
              🏆 Microsoft Agents League
            </span>
            <span className="p-1 px-3.5 rounded-full text-[11px] font-bold bg-[#E0F2FE] text-[#2563EB] border border-blue-200 tracking-wide uppercase">
              🧠 Reasoning Agents Track
            </span>
            <span className="p-1 px-3.5 rounded-full text-[11px] font-bold bg-[#E6FDF9] text-[#0D9488] border border-teal-200 tracking-wide uppercase">
              ⚡ Foundry IQ Ready
            </span>
          </div>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-[#0F172A] leading-[1.1] font-heading font-sans">
            Learning intelligence from <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#7C3AED] via-[#2563EB] to-[#06B6D4]">
              failed ML experiments
            </span>
          </h2>

          <p className="mt-6 text-sm sm:text-base text-[#64748B] leading-relaxed max-w-xl">
            Diagnose failed machine learning runs, expose structural root causes, retrieve grounded evidence, and convert downstream mistakes into certification-ready learning plans automatically.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <button
              onClick={onStartDemo}
              className="p-4 px-8 rounded-full text-sm font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-lg shadow-purple-500/20 hover-lift transition-all flex items-center gap-2 cursor-pointer"
            >
              Start Diagnostic Demo <MoveRight className="w-4 h-4" />
            </button>
            <a
              href="#workflow"
              className="p-4 px-8 rounded-full text-sm font-semibold text-[#64748B] hover:text-[#0F172A] border border-[#E2E8F0] hover:bg-white bg-transparent transition-all hover-lift flex items-center gap-2"
            >
              View Agent Diagram <Layers className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Hero Right Visual Mockup Card */}
        <div className="lg:col-span-5 flex justify-center">
          <div className="w-full max-w-md bg-white border border-[#E2E8F0] rounded-3xl p-6 md:p-8 shadow-xl relative animate-slide-up hover-lift">
            <div className="flex items-center justify-between mb-6">
              <span className="text-xs font-mono font-bold text-[#64748B] tracking-wide uppercase">
                Active Analysis Run
              </span>
              <span className="p-1 px-2.5 rounded-md text-[10px] font-mono font-bold bg-[#E6FDF9] text-[#0D9488] border border-teal-150 uppercase">
                EXP-1001 Trace
              </span>
            </div>

            {/* Simulated Reasoning Pipeline */}
            <div className="space-y-4">
              <div className="flex gap-3.5">
                <div className="w-7 h-7 rounded-full bg-purple-100 border border-purple-200 text-[#7C3AED] font-bold text-xs flex items-center justify-center shrink-0">
                  1
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#0F172A]">Planner Scans Log</h4>
                  <p className="text-xs text-[#64748B] mt-0.5">Diagnosing minority drop weight outliers & imbalance bias indicators.</p>
                </div>
              </div>

              <div className="border-l-2 border-dashed border-[#E2E8F0] ml-3.5 h-4 my-1"></div>

              <div className="flex gap-3.5">
                <div className="w-7 h-7 rounded-full bg-blue-100 border border-blue-200 text-[#2563EB] font-bold text-xs flex items-center justify-center shrink-0">
                  2
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#0F172A]">Demographic Audits Active</h4>
                  <p className="text-xs text-[#64748B] mt-0.5">Analyzing zipcode proxy mutual values against label datasets.</p>
                </div>
              </div>

              <div className="border-l-2 border-dashed border-[#E2E8F0] ml-3.5 h-4 my-1"></div>

              <div className="flex gap-3.5">
                <div className="w-7 h-7 rounded-full bg-teal-100 border border-teal-200 text-[#0D9488] font-bold text-xs flex items-center justify-center shrink-0">
                  3
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#0F172A]">Microsoft IQ Proof Generated</h4>
                  <p className="text-xs text-[#64748B] mt-0.5">Grounded citations compiled with Local Foundry index.</p>
                </div>
              </div>
            </div>

            {/* Glowing Proof Rating Badge */}
            <div className="mt-8 pt-6 border-t border-[#E2E8F0] flex items-center justify-between">
              <div>
                <p className="text-[10px] font-mono font-bold text-[#64748B] uppercase tracking-wide">
                  Analysis Confidence
                </p>
                <p className="text-2xl font-black text-[#2563EB]">84% Accredited</p>
              </div>
              <div className="p-2 bg-[#F3E8FF] rounded-xl border border-purple-200 text-[#7C3AED]">
                <Award className="w-5 h-5" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CORE PROBLEM SECTION */}
      <section id="problem" className="relative max-w-7xl mx-auto px-6 py-20 border-t border-[#E2E8F0]/50 z-10">
        <div className="text-center max-w-3xl mx-auto">
          <span className="text-xs font-bold text-[#7C3AED] uppercase tracking-wider">The Engineering Gap</span>
          <h3 className="text-3xl font-bold tracking-tight text-[#0F172A] mt-2 font-heading">
            Why Do Failed Runs Go Untracked?
          </h3>
          <p className="mt-4 text-sm text-[#64748B] leading-relaxed">
            In modern machine learning production lines, error monitoring is often relegated to raw stack traces or unlogged console prints. Important governance intelligence, bias indicators, and systemic training failures are forgotten.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          <div className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm">
            <div className="p-3 w-12 h-12 rounded-xl bg-orange-50 border border-orange-200 text-[#F59E0B] flex items-center justify-center mb-5">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#0F172A] mb-2 font-heading">Invisible Target Leakage</h4>
            <p className="text-xs text-[#64748B] leading-relaxed">
              Models achieve 99% accuracy offline by memorizing future variables. They pass checks but fail instantaneously in customer-serving scenarios.
            </p>
          </div>

          <div className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm">
            <div className="p-3 w-12 h-12 rounded-xl bg-purple-50 border border-purple-200 text-[#7C3AED] flex items-center justify-center mb-5">
              <Sparkles className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#0F172A] mb-2 font-heading">Latent Proxy Discrimination</h4>
            <p className="text-xs text-[#64748B] leading-relaxed">
              Removing direct sensitive demographic indicators fails to prevent bias when zipcode structures act as high-correlation proxies.
            </p>
          </div>

          <div className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm">
            <div className="p-3 w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 text-[#2563EB] flex items-center justify-center mb-5">
              <Layers className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-[#0F172A] mb-2 font-heading">Diverged Schema Pipeline</h4>
            <p className="text-xs text-[#64748B] leading-relaxed">
              Categorical mapping encoding differences between train parameters and service gateways continuously crash real-time inferences silently.
            </p>
          </div>
        </div>
      </section>

      {/* CORE AGENT WORKFLOW */}
      <section id="workflow" className="relative bg-white py-20 border-y border-[#E2E8F0]/60 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider font-mono">Architectural Flow</span>
            <h3 className="text-3xl font-extrabold tracking-tight text-[#0F172A] mt-2 font-heading">
              Multi-Agent Collaboration Engine
            </h3>
            <p className="mt-3 text-sm text-[#64748B] leading-relaxed">
              FailureLens IQ coordinates a league of specialized, reasoning agents designed to inspect code, correlate error patterns, search grounding playbooks, and map findings to Microsoft parameters.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-center">
            {/* Agent Descriptions */}
            <div className="lg:col-span-2 space-y-6">
              <div className="p-5 p-px border border-transparent hover:border-[#E2E8F0] hover:bg-[#F8FAFC] rounded-2xl transition-all cursor-pointer">
                <div className="p-4 flex gap-4">
                  <div className="w-10 h-10 rounded-xl bg-purple-50 text-[#7C3AED] flex items-center justify-center shrink-0 border border-purple-100 font-bold text-sm">
                    PL
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-[#0F172A]">Pipeline Planner Agent</h5>
                    <p className="text-[11px] text-[#64748B] mt-1">Accepts logs, structures core trace sequences, and flags anomaly signatures early.</p>
                  </div>
                </div>
              </div>

              <div className="p-5 p-px border border-transparent hover:border-[#E2E8F0] hover:bg-[#F8FAFC] rounded-2xl transition-all cursor-pointer">
                <div className="p-4 flex gap-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center shrink-0 border border-blue-100 font-bold text-sm">
                    RC
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-[#0F172A]">Root Cause Analyst Agent</h5>
                    <p className="text-[11px] text-[#64748B] mt-1">Cross-correlates datasets statistics differentials and identifies leakage timestamps.</p>
                  </div>
                </div>
              </div>

              <div className="p-5 p-px border border-transparent hover:border-[#E2E8F0] hover:bg-[#F8FAFC] rounded-2xl transition-all cursor-pointer">
                <div className="p-4 flex gap-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-[#0D9488] flex items-center justify-center shrink-0 border border-teal-100 font-bold text-sm">
                    IQ
                  </div>
                  <div>
                    <h5 className="text-sm font-bold text-[#0F172A]">Foundry Standard Historian</h5>
                    <p className="text-[11px] text-[#64748B] mt-1">Fetches exact matching citations from industry responsible AI standard frameworks.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Visual Canvas mock */}
            <div className="lg:col-span-3 bg-[#FAFBFD] border border-[#E2E8F0] p-6 lg:p-8 rounded-3xl relative overflow-hidden flex flex-col justify-between h-[380px]">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold text-[#64748B] uppercase tracking-wider">
                  Trace Pipeline Diagram
                </span>
                <span className="status-dot status-dot-active"></span>
              </div>

              {/* Visual graph layout */}
              <div className="my-auto flex items-center justify-center gap-4 relative">
                <div className="flex flex-col items-center z-10">
                  <div className="p-4 rounded-2xl bg-white border border-[#E2E8F0] pointer-events-none flex flex-col items-center gap-1.5 shadow-sm">
                    <span className="text-[10px] font-mono font-bold text-[#7C3AED]">Plan</span>
                    <p className="text-xs font-bold text-[#0F172A]">Planner Agent</p>
                  </div>
                </div>

                <div className="w-6 border-t-2 border-dashed border-[#E2E8F0]"></div>

                <div className="flex flex-col items-center z-10">
                  <div className="p-4 rounded-2xl bg-[#EEF4FF] border border-[#BFDBFE] pointer-events-none flex flex-col items-center gap-1.5 shadow-sm">
                    <span className="text-[10px] font-mono font-bold text-[#2563EB]">Audit</span>
                    <p className="text-xs font-bold text-[#0F172A]">Root Cause Analyst</p>
                  </div>
                </div>

                <div className="w-6 border-t-2 border-dashed border-[#E2E8F0]"></div>

                <div className="flex flex-col items-center z-10">
                  <div className="p-4 rounded-2xl bg-white border border-[#E2E8F0] pointer-events-none flex flex-col items-center gap-1.5 shadow-sm">
                    <span className="text-[10px] font-mono font-bold text-[#0D9488]">Proof</span>
                    <p className="text-xs font-bold text-[#0F172A]">Foundry Historian</p>
                  </div>
                </div>
              </div>

              <div className="border-t border-[#E2E8F0] pt-4 flex items-center justify-between text-xs text-[#64748B]">
                <span>Status: Grounding validated</span>
                <span>Foundry SDK: OK</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative bg-[#0F172A] text-white py-16 z-10 text-center select-none">
        <div className="max-w-7xl mx-auto px-6 flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#7C3AED] to-[#2563EB] flex items-center justify-center text-white font-bold text-lg mb-4">
            FL
          </div>
          <h4 className="text-lg font-bold tracking-wider uppercase font-heading">
            FailureLens IQ
          </h4>
          <p className="text-xs text-slate-400 mt-2 max-w-md">
            Built by Muhammad Muavia for the Microsoft Agents League (Reasoning Agents Track). Reusable team memory engine.
          </p>
          <div className="mt-8 pt-8 border-t border-slate-800 w-full text-[11px] text-slate-500">
            © 2026 FailureLens IQ. All rights reserved. Do not upload confidential database records.
          </div>
        </div>
      </footer>
    </div>
  );
};
