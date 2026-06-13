import React, { useState } from "react";
import { useApp } from "../../AppContext";
import {
  MessageSquare,
  LayoutDashboard,
  Compass,
  GitBranch,
  BookOpen,
  Award,
  FileText,
  Settings,
  LogOut,
  Search,
  Menu,
  X,
  Database,
  CheckCircle,
  AlertTriangle,
  Play
} from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
  activePath: string;
  onNavigate: (path: string) => void;
  onRunSampleDemo?: () => void;
  onNewAnalysis?: () => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activePath,
  onNavigate,
  onRunSampleDemo,
  onNewAnalysis
}) => {
  const { user, signOut, backendConnected, iqStatus } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const navigationItems = [
    { name: "Reasoning Chat", path: "chat", icon: MessageSquare },
    { name: "Executive Dashboard", path: "dashboard", icon: LayoutDashboard },
    { name: "Experiment Memory", path: "experiments", icon: Compass },
    { name: "Agent Runs & Traces", path: "agent-runs", icon: GitBranch },
    { name: "Foundry IQ Retrieval", path: "knowledge", icon: BookOpen },
    { name: "Microsoft IQ Proof", path: "iq-proof", icon: Award },
    { name: "Generated Reports", path: "reports", icon: FileText },
    { name: "SaaS Settings", path: "settings", icon: Settings },
  ];

  const handleNav = (path: string) => {
    onNavigate(path);
    setMobileMenuOpen(false);
  };

  const currentIqBadgeStyle = () => {
    if (!backendConnected || !iqStatus || !iqStatus.iq_mode) {
      return { bg: "bg-red-50 text-red-600 border-red-200", label: "Offline Mock Preview" };
    }
    const mode = iqStatus.iq_mode.toLowerCase();
    if (mode.includes("azure-live") || mode.includes("azure_live") || mode.includes("azure live") || mode.includes("live_azure") || mode.includes("live-azure")) {
      return { bg: "bg-emerald-50 text-emerald-600 border-emerald-200", label: "Live Azure Grounding" };
    }
    if (mode.includes("foundry") || mode.includes("local-foundry") || mode.includes("local_foundry")) {
      return { bg: "bg-purple-50 text-purple-600 border-purple-200", label: "Local Foundry Adapter" };
    }
    return { bg: "bg-sky-50 text-sky-600 border-sky-200", label: "Microsoft IQ Ready" };
  };

  const iqStyle = currentIqBadgeStyle();

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex text-[#0F172A] font-sans antialiased">
      {/* DESKTOP SIDEBAR */}
      <aside className="hidden lg:flex flex-col w-[280px] border-r border-[#E2E8F0] bg-white h-screen sticky top-0 shrink-0 select-none z-30">
        {/* Logo / Header */}
        <div className="p-6 border-b border-[#E2E8F0] flex flex-col justify-start">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#7C3AED] to-[#2563EB] flex items-center justify-center text-white font-bold text-base shadow-md">
              FL
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-[#0F172A]">FailureLens IQ</h1>
              <span className="text-[10px] font-mono font-semibold tracking-wider text-[#64748B] uppercase block">
                Reasoning Agents League
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Modules */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePath === item.path || (item.path === 'experiments' && activePath.startsWith('experiments/')) || (item.path === 'agent-runs' && activePath.startsWith('agent-runs/'));
            return (
              <button
                key={item.path}
                onClick={() => handleNav(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 transform ${
                  isActive
                    ? "bg-[#EEF4FF] text-[#2563EB] shadow-sm font-semibold hover:scale-[1.02] hover:translate-x-0.5"
                    : "text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A] hover:scale-[1.03] hover:translate-x-1"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-[#2563EB]" : "text-[#64748B]"}`} />
                {item.name}
              </button>
            );
          })}
        </nav>

        {/* User Card */}
        <div className="p-4 border-t border-[#E2E8F0] bg-[#FAFBFD]">
          <div className="flex items-center gap-3 p-2 rounded-xl">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#7C3AED] to-[#06B6D4] text-white flex items-center justify-center font-bold text-sm">
              {user ? user.name.charAt(0) : "G"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-[#0F172A] truncate">
                {user ? user.name : "Guest Practitioner"}
              </p>
              <p className="text-[10px] font-mono text-[#64748B] truncate">
                {user ? user.role : "ML Specialist"}
              </p>
            </div>
            <button
              onClick={signOut}
              title="Sign Out"
              className="p-1 px-2 text-[#64748B] hover:text-[#EF4444] rounded-lg hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* MOBILE HEADER */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-[#E2E8F0] flex items-center justify-between px-4 z-40 select-none">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#7C3AED] to-[#2563EB] flex items-center justify-center text-white font-bold text-sm">
            FL
          </div>
          <h1 className="text-base font-bold text-[#0F172A]">FailureLens IQ</h1>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 border border-[#E2E8F0] rounded-xl text-[#0F172A]"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* MOBILE DRAWER */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 bg-[#0F172A]/40 backdrop-blur-sm z-35 lg:hidden animate-fade-in" onClick={() => setMobileMenuOpen(false)}>
          <div className="w-[280px] bg-white h-full flex flex-col pt-20" onClick={(e) => e.stopPropagation()}>
            <nav className="flex-1 px-4 py-4 space-y-1.5 overflow-y-auto">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = activePath === item.path;
                return (
                  <button
                    key={item.path}
                    onClick={() => handleNav(item.path)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      isActive
                        ? "bg-[#EEF4FF] text-[#2563EB]"
                        : "text-[#64748B] hover:bg-[#F8FAFC]"
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {item.name}
                  </button>
                );
              })}
            </nav>
            <div className="p-4 border-t border-[#E2E8F0]">
              <button
                onClick={signOut}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-red-200 text-red-600 hover:bg-red-50 text-sm font-medium"
              >
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex flex-col min-w-0 pt-16 lg:pt-0">
        {/* TOP COMMAND BAR */}
        <header className="h-16 bg-white border-b border-[#E2E8F0] hidden sm:flex items-center justify-between px-6 sticky top-0 z-20">
          <div className="flex items-center gap-3 w-1/3 min-w-[200px]">
            <Search className="w-4 h-4 text-[#64748B]" />
            <input
              type="text"
              placeholder="Search experiments, traces, agents..."
              className="bg-transparent border-none text-sm focus:outline-none focus:ring-0 w-full text-[#0F172A] placeholder:text-[#64748B]"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchQuery) {
                  onNavigate(`experiments?search=${encodeURIComponent(searchQuery)}`);
                }
              }}
            />
          </div>

          <div className="flex items-center gap-3">
            {/* Connection badge */}
            <div className={`p-1.5 px-3 rounded-full text-xs font-mono font-medium border flex items-center gap-1.5 ${iqStyle.bg}`}>
              {backendConnected ? (
                <CheckCircle className="w-3.5 h-3.5 text-inherit" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-inherit" />
              )}
              {iqStyle.label}
            </div>

            {/* Run sample demo CTA */}
            {onRunSampleDemo && (
              <button
                onClick={onRunSampleDemo}
                className="flex items-center gap-1.5 p-1.5 px-3 rounded-lg text-xs font-medium border border-[#E2E8F0] hover:bg-[#EEF4FF] text-[#2563EB] bg-white transition-all duration-300 hover:-translate-y-0.5 hover:scale-[1.04] hover:shadow-sm transform cursor-pointer"
              >
                <Play className="w-3 h-3 fill-[#2563EB]" /> Run Sample Demo
              </button>
            )}

            {/* New Analysis */}
            {onNewAnalysis && (
              <button
                onClick={onNewAnalysis}
                className="p-1.5 px-3 rounded-lg text-xs font-medium text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm hover:-translate-y-0.5 hover:scale-[1.04] hover:shadow-md transition-all duration-300 transform cursor-pointer"
              >
                New Analysis
              </button>
            )}
          </div>
        </header>

        {/* PAGE BODY */}
        <main className="flex-1 overflow-y-auto px-4 py-6 md:p-8 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
};
