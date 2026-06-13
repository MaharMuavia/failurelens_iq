import React, { useState } from "react";
import { useApp } from "../AppContext";
import { MoveRight, Mail, Lock } from "lucide-react";

interface SignInPageProps {
  onSuccess: () => void;
  onSignUpClick: () => void;
}

export const SignInPage: React.FC<SignInPageProps> = ({ onSuccess, onSignUpClick }) => {
  const { signIn, signInAsGuest } = useApp();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill out all credential fields.");
      return;
    }
    setError("");
    // Log user in
    const extractedName = name || email.split("@")[0] || "ML Specialist";
    signIn(extractedName, email, "Data Scientist", "Workspace Team");
    onSuccess();
  };

  const handleGuest = () => {
    signInAsGuest();
    onSuccess();
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex text-[#0F172A] font-sans antialiased relative overflow-hidden">
      {/* Soft background glow blobs */}
      <div className="absolute top-[-100px] left-[-100px] w-96 h-96 rounded-full bg-purple-100/40 blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-[-150px] right-[-100px] w-[500px] h-[500px] rounded-full bg-blue-100/30 blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center min-h-screen">
        {/* Left column pitch block */}
        <div className="lg:col-span-6 hidden lg:flex flex-col justify-center text-left max-w-xl">
          <div className="flex items-center gap-2.5 mb-8">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#7C3AED] to-[#2563EB] flex items-center justify-center text-white font-bold text-sm">
              FL
            </div>
            <span className="text-sm font-bold tracking-tight text-[#0F172A]">FailureLens IQ</span>
          </div>

          <h2 className="text-4xl font-black tracking-tight text-[#0F172A] font-heading leading-tight">
            Turn failed ML experiments <br />
            into <span className="text-[#7C3AED]">reusable team memory</span>.
          </h2>
          <p className="mt-4 text-[#64748B] text-sm leading-relaxed">
            Connect to localized knowledge bases, perform multi-agent analysis checks, and generate complete interactive diagnostic reports suitable for corporate compliance reviews.
          </p>

          <div className="mt-8 space-y-4">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
              <span className="text-xs font-semibold text-[#64748B]">Microsoft Agents League Approved layout</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-[#2563EB]"></span>
              <span className="text-xs font-semibold text-[#64748B]">Continuous Target Leakage Scanner</span>
            </div>
          </div>
        </div>

        {/* Right column Form Card */}
        <div className="lg:col-span-6 flex justify-center w-full">
          <div className="w-full max-w-md bg-white border border-[#E2E8F0] rounded-3xl p-8 shadow-xl animate-slide-up">
            <div className="text-center sm:text-left mb-6">
              <h3 className="text-2xl font-extrabold tracking-tight text-[#0F172A] font-heading">
                Sign In to Platform
              </h3>
              <p className="text-xs text-[#64748B] mt-1">
                Enter your trial credentials or continue instantly as guest reviewer.
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-150 rounded-xl text-xs text-red-600 font-semibold">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1.5">
                  Full Name (Optional)
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Muhammad Muavia"
                    className="w-full rounded-xl border border-[#E2E8F0] p-3 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#64748B] absolute left-3.5 top-3.5" />
                  <input
                    type="email"
                    placeholder="judge@agents-league.live"
                    required
                    className="w-full rounded-xl border border-[#E2E8F0] p-3 pl-10 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1.5">
                  Access Keyword / Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#64748B] absolute left-3.5 top-3.5" />
                  <input
                    type="password"
                    placeholder="••••••••"
                    required
                    className="w-full rounded-xl border border-[#E2E8F0] p-3 pl-10 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full p-3.5 text-sm font-semibold rounded-xl text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm transition-all focus:ring-2 focus:ring-[#7C3AED]/20 cursor-pointer"
              >
                Sign In
              </button>
            </form>

            <div className="relative my-6 flex items-center justify-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#E2E8F0]"></div>
              </div>
              <span className="relative bg-white px-3 text-[10px] font-bold text-[#64748B] uppercase tracking-wider">
                Or Quick Access
              </span>
            </div>

            <button
              onClick={handleGuest}
              className="w-full p-3.5 text-sm font-semibold rounded-xl border border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              Continue as Guest Reviewer <MoveRight className="w-4 h-4 text-[#64748B]" />
            </button>

            <div className="mt-6 text-center">
              <button
                onClick={onSignUpClick}
                className="text-xs font-semibold text-[#2563EB] hover:underline"
              >
                Need to create a custom profile? Register here
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
