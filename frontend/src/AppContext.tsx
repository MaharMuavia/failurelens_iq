import React, { createContext, useContext, useState, useEffect } from "react";
import { ApiClient, Experiment } from "./api/client";

export type AccentTheme = 'purple' | 'blue' | 'cyan';

interface AppContextType {
  user: { name: string; email: string; role: string; org: string } | null;
  guestMode: boolean;
  themeAccent: AccentTheme;
  compactMode: boolean;
  animationsEnabled: boolean;
  experiments: Experiment[];
  backendConnected: boolean;
  iqStatus: { status: string; provider: string; iq_mode: string; live_search: boolean; citations_count: number };
  refreshExperiments: () => Promise<void>;
  signIn: (name: string, email: string, role: string, org: string) => void;
  signInAsGuest: () => void;
  signOut: () => void;
  setThemeAccent: (accent: AccentTheme) => void;
  setCompactMode: (val: boolean) => void;
  setAnimationsEnabled: (val: boolean) => void;
  addExperiment: (exp: Experiment) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AppContextType["user"]>(null);
  const [guestMode, setGuestMode] = useState<boolean>(false);
  const [themeAccent, setThemeAccentState] = useState<AccentTheme>("purple");
  const [compactMode, setCompactModeState] = useState<boolean>(false);
  const [animationsEnabled, setAnimationsEnabledState] = useState<boolean>(true);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [backendConnected, setBackendConnected] = useState<boolean>(true);
  const [iqStatus, setIqStatus] = useState<AppContextType["iqStatus"]>({
    status: "local-simulation",
    provider: "Local Foundry IQ Adapter",
    iq_mode: "Local Mode (No Azure Grounding Connection)",
    live_search: false,
    citations_count: 3
  });

  useEffect(() => {
    // Load local storage session details
    const storedUser = localStorage.getItem("failurelens_user");
    const storedGuest = localStorage.getItem("failurelens_guest_mode");
    const storedAccent = localStorage.getItem("failurelens_theme_accent") as AccentTheme;
    const storedCompact = localStorage.getItem("failurelens_compact_mode");
    const storedAnimations = localStorage.getItem("failurelens_animations_enabled");

    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else if (storedGuest === "true") {
      setGuestMode(true);
    }

    if (storedAccent) {
      setThemeAccentState(storedAccent);
    }
    if (storedCompact) {
      setCompactModeState(storedCompact === "true");
    }
    if (storedAnimations) {
      setAnimationsEnabledState(storedAnimations === "true");
    }

    // Healthchecks and backend checks
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const health = await ApiClient.getHealth();
      setBackendConnected(health.status !== "offline-mock");
      const iq = await ApiClient.getIQStatus();
      setIqStatus(iq);
    } catch {
      setBackendConnected(false);
    }
    await refreshExperiments();
  };

  const refreshExperiments = async () => {
    try {
      const data = await ApiClient.listExperiments();
      setExperiments(data);
    } catch {
      setExperiments([]);
    }
  };

  const signIn = (name: string, email: string, role: string, org: string) => {
    const usr = { name, email, role, org };
    setUser(usr);
    setGuestMode(false);
    localStorage.setItem("failurelens_user", JSON.stringify(usr));
    localStorage.removeItem("failurelens_guest_mode");
  };

  const signInAsGuest = () => {
    setGuestMode(true);
    setUser({
      name: "Guest Practitioner",
      email: "guest@microsoft-league.ai",
      role: "ML Specialist",
      org: "Reviewer Workspace"
    });
    localStorage.setItem("failurelens_guest_mode", "true");
    localStorage.removeItem("failurelens_user");
  };

  const signOut = () => {
    setUser(null);
    setGuestMode(false);
    localStorage.removeItem("failurelens_user");
    localStorage.removeItem("failurelens_guest_mode");
  };

  const setThemeAccent = (accent: AccentTheme) => {
    setThemeAccentState(accent);
    localStorage.setItem("failurelens_theme_accent", accent);
  };

  const setCompactMode = (val: boolean) => {
    setCompactModeState(val);
    localStorage.setItem("failurelens_compact_mode", val ? "true" : "false");
  };

  const setAnimationsEnabled = (val: boolean) => {
    setAnimationsEnabledState(val);
    localStorage.setItem("failurelens_animations_enabled", val ? "true" : "false");
  };

  const addExperiment = (exp: Experiment) => {
    setExperiments(prev => [exp, ...prev]);
  };

  // Synchronize CSS class for theme selection
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("accent-purple", "accent-blue", "accent-cyan");
    root.classList.add(`accent-${themeAccent}`);
    
    // Dynamically adjust CSS variable overrides based on accent
    if (themeAccent === 'purple') {
      root.style.setProperty('--primary', '#7C3AED');
      root.style.setProperty('--primary-blue', '#2563EB');
      root.style.setProperty('--accent', '#06B6D4');
    } else if (themeAccent === 'blue') {
      root.style.setProperty('--primary', '#2563EB');
      root.style.setProperty('--primary-blue', '#1D4ED8');
      root.style.setProperty('--accent', '#8B5CF6');
    } else if (themeAccent === 'cyan') {
      root.style.setProperty('--primary', '#0EA5E9');
      root.style.setProperty('--primary-blue', '#2563EB');
      root.style.setProperty('--accent', '#10B981');
    }
  }, [themeAccent]);

  return (
    <AppContext.Provider
      value={{
        user,
        guestMode,
        themeAccent,
        compactMode,
        animationsEnabled,
        experiments,
        backendConnected,
        iqStatus,
        refreshExperiments,
        signIn,
        signInAsGuest,
        signOut,
        setThemeAccent,
        setCompactMode,
        setAnimationsEnabled,
        addExperiment
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
