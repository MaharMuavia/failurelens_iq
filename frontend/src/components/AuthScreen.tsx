import React, { useEffect, useState } from "react";
import { ManagerDashboard } from "./ManagerDashboard";

export const AuthScreen: React.FC = () => {
  const [mode, setMode] = useState<"auth" | "dashboard">("auth");

  useEffect(() => {
    if (localStorage.getItem("failurelens_guest_mode") === "true") {
      setMode("dashboard");
    }
  }, []);
  const [view, setView] = useState<"signIn" | "signUp">("signIn");

  const continueAsGuest = () => {
    localStorage.setItem("failurelens_guest_mode", "true");
    setMode("dashboard");
  };

  if (mode === "dashboard") {
    return <ManagerDashboard activeTab={"Analysis"} onTabChange={() => {}} />;
  }

  return (
    <div className="min-h-screen bg-[#0b1220] flex items-center justify-center text-white">
      <div className="max-w-md w-full bg-[#071226]/60 p-6 rounded-xl backdrop-blur">
        <h1 className="text-2xl font-bold mb-2">FailureLens IQ</h1>
        <p className="text-sm text-cyan-200 mb-4">Learning Intelligence from Failed ML Experiments</p>

        <div className="space-y-4">
          {view === "signIn" ? (
            <div>
              <input className="w-full p-2 mb-2 rounded bg-[#0b1724]" placeholder="Email" />
              <input className="w-full p-2 mb-2 rounded bg-[#0b1724]" placeholder="Password" type="password" />
              <button className="w-full py-2 bg-cyan-500 rounded" onClick={() => setMode("dashboard")}>Sign In</button>
              <div className="mt-2 text-sm">
                <a onClick={() => setView("signUp")} className="text-cyan-300 cursor-pointer">Create account</a>
              </div>
            </div>
          ) : (
            <div>
              <input className="w-full p-2 mb-2 rounded bg-[#0b1724]" placeholder="Full name" />
              <input className="w-full p-2 mb-2 rounded bg-[#0b1724]" placeholder="Email" />
              <input className="w-full p-2 mb-2 rounded bg-[#0b1724]" placeholder="Password" type="password" />
              <button className="w-full py-2 bg-cyan-500 rounded" onClick={() => setMode("dashboard")}>Create Account</button>
              <div className="mt-2 text-sm">
                <a onClick={() => setView("signIn")} className="text-cyan-300 cursor-pointer">Already have an account?</a>
              </div>
            </div>
          )}

          <div className="pt-2 border-t border-[#123]">
            <button className="w-full py-2 mt-2 border border-cyan-600 rounded" onClick={continueAsGuest}>Continue as Guest</button>
            <p className="text-xs text-gray-300 mt-2">Demo mode only — no real authentication configured</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;
