import React, { useState } from "react";
import { useApp } from "../AppContext";
import { User, Mail, Lock, Shield } from "lucide-react";

interface SignUpPageProps {
  onSuccess: () => void;
  onSignInClick: () => void;
}

export const SignUpPage: React.FC<SignUpPageProps> = ({ onSuccess, onSignInClick }) => {
  const { signIn, signInAsGuest } = useApp();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("ML Engineer");
  const [organization, setOrganization] = useState("");
  const [error, setError] = useState("");

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      setError("Please fill in all required fields.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    signIn(fullName, email, role, organization || "Independent Workspace");
    onSuccess();
  };

  const handleGuest = () => {
    signInAsGuest();
    onSuccess();
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex text-[#0F172A] font-sans antialiased relative overflow-hidden">
      <div className="absolute top-[-100px] right-[-100px] w-96 h-96 bg-purple-100/35 blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-[-150px] left-[-100px] w-[500px] h-[500px] bg-blue-100/35 blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-7xl mx-auto px-6 flex items-center justify-center min-h-screen py-12">
        <div className="w-full max-w-lg bg-white border border-[#E2E8F0] rounded-3xl p-8 shadow-xl animate-slide-up">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-extrabold tracking-tight text-[#0F172A] font-heading">
              Create Analyst Account
            </h3>
            <p className="text-xs text-[#64748B] mt-1">
              Set up your profile for Microsoft Agents League evaluation tracking.
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-150 rounded-xl text-xs text-red-600 font-semibold text-left">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4 text-left">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#64748B] absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    placeholder="Muhammad Muavia"
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-9 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#64748B] absolute left-3 top-3" />
                  <input
                    type="email"
                    required
                    placeholder="muavia@example.com"
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-9 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Role
                </label>
                <select
                  className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] bg-white text-[#0F172A]"
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
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Organization
                </label>
                <div className="relative">
                  <Shield className="w-4 h-4 text-[#64748B] absolute left-3 top-3" />
                  <input
                    type="text"
                    placeholder="Microsoft Partner"
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-9 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#64748B] absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-9 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#64748B] uppercase tracking-wider mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#64748B] absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-9 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="w-full p-3.5 mt-4 text-sm font-semibold rounded-xl text-white bg-gradient-to-r from-[#7C3AED] to-[#2563EB] shadow-md hover:shadow-lg transition-all cursor-pointer"
            >
              Create Account
            </button>
          </form>

          <div className="relative my-6 flex items-center justify-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#E2E8F0]"></div>
            </div>
            <span className="relative bg-white px-3 text-[10px] font-bold text-[#64748B] uppercase tracking-wider">
              Or bypass
            </span>
          </div>

          <button
            onClick={handleGuest}
            className="w-full p-3 text-sm font-semibold rounded-xl border border-[#E2E8F0] text-[#0F172A] hover:bg-[#F8FAFC] transition-all cursor-pointer"
          >
            Continue as Guest Reviewer
          </button>

          <div className="mt-6 text-center">
            <button
              onClick={onSignInClick}
              className="text-xs font-semibold text-[#2563EB] hover:underline"
            >
              Already have an account? Sign In here
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
