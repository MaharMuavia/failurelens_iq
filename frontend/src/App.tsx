import React, { useState, useEffect } from "react";
import { useApp } from "./AppContext";
import { LandingPage } from "./pages/LandingPage";
import { SignInPage } from "./pages/SignInPage";
import { SignUpPage } from "./pages/SignUpPage";
import { ChatPage } from "./pages/ChatPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ExperimentsPage } from "./pages/ExperimentsPage";
import { ExperimentDetailPage } from "./pages/ExperimentDetailPage";
import { AgentRunsPage } from "./pages/AgentRunsPage";
import { AgentRunDetailPage } from "./pages/AgentRunDetailPage";
import { KnowledgeBasePage } from "./pages/KnowledgeBasePage";
import { MicrosoftIQProofPage } from "./pages/MicrosoftIQProofPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { AppShell } from "./components/layout/AppShell";

export default function App() {
  const { user, guestMode } = useApp();
  const [activePath, setActivePath] = useState<string>("landing");
  const [selectedExperimentId, setSelectedExperimentId] = useState<string>("");
  const [selectedRunId, setSelectedRunId] = useState<string>("");

  // Auto route signed-in session user straight to dashboard/chat
  useEffect(() => {
    if (user || guestMode) {
      if (activePath === "landing" || activePath === "signin" || activePath === "signup") {
        setActivePath("dashboard");
      }
    } else {
      // If user logs out, return to landing
      if (activePath !== "signin" && activePath !== "signup") {
        setActivePath("landing");
      }
    }
  }, [user, guestMode]);

  const handleNavigate = (path: string) => {
    if (path.startsWith("experiments/")) {
      const expId = path.split("/")[1];
      setSelectedExperimentId(expId);
    } else if (path.startsWith("agent-runs/")) {
      const runId = path.split("/")[1];
      setSelectedRunId(runId);
    }
    setActivePath(path);
  };

  const handleRunSampleDemo = () => {
    setActivePath("chat");
  };

  const handleNewAnalysis = () => {
    setActivePath("chat");
  };

  // Determine which page component to display
  const renderPage = () => {
    if (activePath === "chat") {
      return (
        <ChatPage
          onNavigate={handleNavigate}
          onSelectExperiment={setSelectedExperimentId}
        />
      );
    }
    if (activePath === "dashboard") {
      return (
        <DashboardPage
          onNavigate={handleNavigate}
          onSelectExperiment={setSelectedExperimentId}
        />
      );
    }
    if (activePath === "experiments") {
      return (
        <ExperimentsPage
          onNavigate={handleNavigate}
          onSelectExperiment={setSelectedExperimentId}
        />
      );
    }
    if (activePath.startsWith("experiments/") && selectedExperimentId) {
      return (
        <ExperimentDetailPage
          id={selectedExperimentId}
          onBack={() => handleNavigate("experiments")}
          onNavigate={handleNavigate}
        />
      );
    }
    if (activePath === "agent-runs") {
      return (
        <AgentRunsPage
          onNavigate={handleNavigate}
          onSelectRun={setSelectedRunId}
        />
      );
    }
    if (activePath.startsWith("agent-runs/") && selectedRunId) {
      return (
        <AgentRunDetailPage
          id={selectedRunId}
          onBack={() => handleNavigate("agent-runs")}
        />
      );
    }
    if (activePath === "knowledge") {
      return <KnowledgeBasePage />;
    }
    if (activePath === "iq-proof") {
      return <MicrosoftIQProofPage />;
    }
    if (activePath === "reports") {
      return <ReportsPage />;
    }
    if (activePath === "settings") {
      return <SettingsPage />;
    }

    // Default Fallback
    return (
      <DashboardPage
        onNavigate={handleNavigate}
        onSelectExperiment={setSelectedExperimentId}
      />
    );
  };

  // 1. Unauthenticated Workspace Routing Flow
  if (!user && !guestMode) {
    if (activePath === "signin") {
      return (
        <SignInPage
          onSuccess={() => setActivePath("dashboard")}
          onSignUpClick={() => setActivePath("signup")}
        />
      );
    }
    if (activePath === "signup") {
      return (
        <SignUpPage
          onSuccess={() => setActivePath("dashboard")}
          onSignInClick={() => setActivePath("signin")}
        />
      );
    }
    // Fallback: Show home landing page
    return (
      <LandingPage
        onStartDemo={() => setActivePath("signin")}
      />
    );
  }

  // 2. Authenticated Workspace Shell Routing Flow
  return (
    <AppShell
      activePath={activePath}
      onNavigate={handleNavigate}
      onRunSampleDemo={handleRunSampleDemo}
      onNewAnalysis={handleNewAnalysis}
    >
      {renderPage()}
    </AppShell>
  );
}
