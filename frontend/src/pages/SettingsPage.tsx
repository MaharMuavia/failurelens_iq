import React, { useState } from "react";
import { useApp, AccentTheme } from "../AppContext";
import { User, Palette, Cpu, Award, RefreshCw, Layers, Check, Info } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const {
    user,
    signIn,
    themeAccent,
    setThemeAccent,
    compactMode,
    setCompactMode,
    animationsEnabled,
    setAnimationsEnabled,
    backendConnected,
    iqStatus,
    refreshExperiments
  } = useApp();

  const [activeTab, setActiveTab] = useState<'profile' | 'appearance' | 'api' | 'iq' | 'demo' | 'about'>('profile');
  
  // Local state form variables
  const [name, setName] = useState(user?.name || "Guest Practitioner");
  const [email, setEmail] = useState(user?.email || "guest@microsoft-league.ai");
  const [role, setRole] = useState(user?.role || "ML Specialist");
  const [org, setOrg] = useState(user?.org || "Reviewer Workspace");
  const [successMsg, setSuccessMsg] = useState("");

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    signIn(name, email, role, org);
    showNotification("Profile configurations stored in localStorage!");
  };

  const showNotification = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(""), 3000);
  };

  const handleResetDemoState = () => {
    localStorage.removeItem("failurelens_experiments");
    refreshExperiments();
    showNotification("Local demo experiments cache flushed successfully!");
  };

  const tabs: Array<{ id: typeof activeTab; icon: any; label: string }> = [
    { id: 'profile', icon: User, label: "Profile" },
    { id: 'appearance', icon: Palette, label: "Appearance" },
    { id: 'api', icon: Cpu, label: "API / Backend" },
    { id: 'iq', icon: Award, label: "Microsoft IQ" },
    { id: 'demo', icon: RefreshCw, label: "Demo Control" },
    { id: 'about', icon: Info, label: "About" }
  ];

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
          SaaS Settings
        </h2>
        <p className="text-sm text-[#64748B]">
          Configure user sessions, light visual accents, backend API indicators, and diagnostic parameters templates.
        </p>
      </div>

      {successMsg && (
        <div className="p-3 bg-semibold rounded-2xl bg-emerald-50 border border-emerald-150 text-emerald-800 text-xs flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* TABS SIDE BY SIDE GRIDS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left column nav tab links */}
        <div className="lg:col-span-3 bg-white border border-[#E2E8F0] p-4 rounded-2xl shadow-sm space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 p-3 px-4 rounded-xl text-xs font-semibold tracking-wide transition-all cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-[#EEF4FF] text-[#2563EB] font-bold shadow-sm"
                    : "text-[#64748B] hover:bg-slate-50 hover:text-[#0f172a]"
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Right column Form content panels */}
        <div className="lg:col-span-9 bg-white border border-[#E2E8F0] p-6 lg:p-8 rounded-2xl shadow-sm">
          
          {/* PROFILE PANEL */}
          {activeTab === 'profile' && (
            <form onSubmit={handleSaveProfile} className="space-y-5 animate-fade-in">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                Profile Configurations
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-[#64748B] uppercase mb-1.5">User Full Name</label>
                  <input
                    type="text"
                    required
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-xs text-[#0F172A] focus:outline-none focus:border-[#7C3AED]"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#64748B] uppercase mb-1.5">Email Address</label>
                  <input
                    type="email"
                    required
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-xs text-[#0F172A] focus:outline-none focus:border-[#7C3AED]"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-[#64748B] uppercase mb-1.5">Role Select</label>
                  <select
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-xs bg-white text-[#0F172A] focus:outline-none focus:border-[#7C3AED]"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  >
                    <option value="ML Engineer">ML Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                    <option value="Team Lead">Team Lead</option>
                    <option value="Student / Researcher">Student / Researcher</option>
                    <option value="Judge / Reviewer">Judge / Reviewer</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#64748B] uppercase mb-1.5">Organization</label>
                  <input
                    type="text"
                    required
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-xs text-[#0F172A] focus:outline-none focus:border-[#7C3AED]"
                    value={org}
                    onChange={(e) => setOrg(e.target.value)}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="p-2.5 px-6 rounded-xl text-xs font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] select-none shadow-sm transition-all hover-lift cursor-pointer mt-2"
              >
                Save Profile Parameters
              </button>
            </form>
          )}

          {/* APPEARANCE PANEL */}
          {activeTab === 'appearance' && (
            <div className="space-y-6 animate-fade-in">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                Appearance & Custom Theming
              </h3>

              {/* Accent pickers */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-[#64748B] uppercase">Accent Brand Color</label>
                <div className="flex gap-2.5">
                  {(['purple', 'blue', 'cyan'] as AccentTheme[]).map((col) => (
                    <button
                      key={col}
                      type="button"
                      onClick={() => setThemeAccent(col)}
                      className={`p-2.5 px-5 rounded-xl border text-xs font-semibold uppercase tracking-wider cursor-pointer transition-all ${
                        themeAccent === col
                          ? "bg-purple-50 text-[#7C3AED] border-[#7C3AED] font-bold"
                          : "bg-white border-[#E2E8F0] text-slate-500 hover:bg-slate-50"
                      }`}
                    >
                      {col} Accent
                    </button>
                  ))}
                </div>
              </div>

              {/* Switches */}
              <div className="pt-4 border-t border-slate-100 space-y-4 text-xs font-semibold text-slate-600">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[#0F172A]">Theme Option Mode</p>
                    <p className="text-[10.5px] text-[#64748B] font-normal">Light theme only (Preferred design default for league judges)</p>
                  </div>
                  <span className="p-1 px-2.5 rounded-md bg-emerald-50 text-emerald-900 border border-emerald-150 uppercase text-[9.5px]">Light Only</span>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div>
                    <p className="text-[#0F172A]">Compact Compactness spacing</p>
                    <p className="text-[10.5px] text-[#64748B] font-normal">Squeeze padding slightly inside listing cards table modules</p>
                  </div>
                  <button
                    onClick={() => setCompactMode(!compactMode)}
                    className={`p-1.5 px-3 rounded-xl border text-[10.5px] font-bold cursor-pointer transition-all ${
                      compactMode ? "bg-purple-50 border-purple-200 text-[#7C3AED]" : "bg-white border-[#E2E8F0] text-slate-400"
                    }`}
                  >
                    {compactMode ? "Compact Active" : "Normal spacing"}
                  </button>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div>
                    <p className="text-[#0F172A]">Visual transitions and loaders animations</p>
                    <p className="text-[10.5px] text-[#64748B] font-normal">Enable micro hover lifts, blobs animations background panels</p>
                  </div>
                  <button
                    onClick={() => setCompactMode(!animationsEnabled)}
                    className="p-1.5 px-3 rounded-xl border text-[10.5px] font-bold cursor-pointer transition-all bg-purple-50 border-purple-200 text-[#7C3AED]"
                  >
                    Enabled
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* API BACKEND PANEL */}
          {activeTab === 'api' && (
            <div className="space-y-6 animate-fade-in">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                Backend Service Integrations
              </h3>

              <div className="bg-[#FAFBFD] p-4 rounded-xl border border-[#E2E8F0]">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs font-bold text-[#64748B] uppercase">Backend Status Diagnostic</span>
                  <span className={`p-1 px-2.5 rounded-md text-[9px] font-bold ${
                    backendConnected ? "bg-emerald-50 text-emerald-700 border border-emerald-100" : "bg-red-50 text-red-700 border border-red-100"
                  } uppercase`}>
                    {backendConnected ? "OK Connected" : "Disconnected Mock"}
                  </span>
                </div>

                <div className="text-xs space-y-1.5 text-[#64748B]">
                  <p>API Endpoint Server base: <strong className="text-slate-800 font-mono">window.location.origin</strong></p>
                  <p>GCP Local Foundry Adapter: <strong className="text-slate-800 font-mono">OK Active (simulation matches)</strong></p>
                  <p>Gemini LLM Analyzer Mode: <strong className="text-slate-800 font-mono">{backendConnected ? "Live FullStack Node Compiler" : "Mock Model Provider fallback"}</strong></p>
                </div>
              </div>

              <div className="space-y-3.5">
                <div>
                  <label className="block text-xs font-bold text-[#64748B] uppercase mb-1.5">Environment Access Token / Demo Key</label>
                  <input
                    type="password"
                    disabled
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-xs text-slate-400 bg-slate-50 cursor-not-allowed font-mono"
                    value="••••••••••••••••••••••••••••••••••"
                  />
                  <p className="text-[10px] text-[#64748B] mt-1">Credentials token is injected securely via AI Studio environmental parameters; not exposed to UI.</p>
                </div>
              </div>
            </div>
          )}

          {/* MICROSOFT IQ PANEL */}
          {activeTab === 'iq' && (
            <div className="space-y-5 animate-fade-in text-xs font-semibold text-[#64748B]">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                Microsoft IQ Setup Requirements
              </h3>

              <p className="leading-relaxed font-normal text-[#64748B]">
                The workspace structures metadata maps for compliance testing review. Verify structural checklists indicators below:
              </p>

              <div className="bg-slate-50 border border-slate-100 p-4 rounded-2xl space-y-3 font-mono text-[10.5px]">
                <div className="flex justify-between border-b border-slate-200/50 pb-2">
                  <span className="text-[#0F172A] font-bold">APP_MODE</span>
                  <span className="text-[#2563EB]">Fullstack Express + React</span>
                </div>
                <div className="flex justify-between border-b border-slate-200/50 pb-2">
                  <span className="text-[#0F172A] font-bold">IQ_PROVIDER</span>
                  <span>{iqStatus.provider}</span>
                </div>
                <div className="flex justify-between border-b border-slate-200/50 pb-2">
                  <span className="text-[#0F172A] font-bold">IQ_MODE</span>
                  <span>{iqStatus.iq_mode}</span>
                </div>
                <div className="flex justify-between border-b border-slate-200/50 pb-2">
                  <span className="text-[#0F172A] font-bold">MODEL_PROVIDER</span>
                  <span className="text-purple-600">Gemini (GoogleGenAI TypeScript SDK)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#0F172A] font-bold">AZURE_AI_INDEX</span>
                  <span>Foundry_Responsible_AI_Index_v3</span>
                </div>
              </div>
            </div>
          )}

          {/* DEMO CONTROL PANEL */}
          {activeTab === 'demo' && (
            <div className="space-y-6 animate-fade-in">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                Demo Cache Control
              </h3>

              <p className="text-xs text-[#64748B] leading-relaxed">
                Resetting pre-seeded items flushes local storage cache and restores baseline diagnostic mock indicators, returning workspace to fresh install.
              </p>

              <div className="p-4 rounded-2xl border border-red-100 bg-red-50/50 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h4 className="text-xs font-bold text-red-900">Flush Local Experiments Diagnostics Cache</h4>
                  <p className="text-[10.5px] text-red-600 mt-1">This operation cannot be reversed. Cached items are wiped.</p>
                </div>
                <button
                  type="button"
                  onClick={handleResetDemoState}
                  className="p-2.5 px-5 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs shadow-sm transition-all cursor-pointer"
                >
                  Confirm Reset Data Cache
                </button>
              </div>
            </div>
          )}

          {/* ABOUT PANEL */}
          {activeTab === 'about' && (
            <div className="space-y-4 animate-fade-in">
              <h3 className="text-base font-bold text-[#0F172A] border-b border-slate-100 pb-3 font-heading">
                About & Portfolio Credits
              </h3>

              <div className="p-1 px-3 w-fit rounded-full text-[10px] font-mono tracking-widest font-bold bg-[#E6FDF9] text-[#0D9488] border border-teal-150 uppercase">
                Microsoft Agents League Entry
              </div>

              <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                FailureLens IQ is engineered as an enterprise diagnostic trace intelligence system, mapping structural target leakage, Imbalance biases, and pipeline categorical divergences for machine learning runs.
              </p>

              <div className="pt-4 border-t border-slate-100 text-xs space-y-2 text-[#64748B]">
                <p>Architect Design inspiration: <a href="https://www.muhammadmuavia.me/" target="_blank" rel="noreferrer" className="text-[#2563EB] hover:underline font-bold">muhammadmuavia.me</a></p>
                <p>Category Track: <strong className="text-slate-700 font-bold">Reasoning Agents Track</strong></p>
                <p>Version compilation: <strong className="text-slate-700 font-mono">v1.2.4-Standard-Release</strong></p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
