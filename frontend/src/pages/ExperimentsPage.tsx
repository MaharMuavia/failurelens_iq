import React, { useState, useEffect } from "react";
import { useApp } from "../AppContext";
import { Experiment } from "../api/client";
import { Search, Filter, ShieldAlert, Award, ArrowRight, Eye, ChevronRight } from "lucide-react";

interface ExperimentsPageProps {
  onNavigate: (path: string) => void;
  onSelectExperiment: (expId: string) => void;
}

export const ExperimentsPage: React.FC<ExperimentsPageProps> = ({ onNavigate, onSelectExperiment }) => {
  const { experiments } = useApp();
  const [filtered, setFiltered] = useState<Experiment[]>([]);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedReview, setSelectedReview] = useState("All");

  useEffect(() => {
    // Sync table filters
    let result = [...experiments];

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(e =>
        e.id.toLowerCase().includes(q) ||
        e.project.toLowerCase().includes(q) ||
        e.rootCause.toLowerCase().includes(q)
      );
    }

    if (selectedCategory !== "All") {
      result = result.filter(e => e.category === selectedCategory);
    }

    if (selectedReview !== "All") {
      result = result.filter(e => e.humanReview === selectedReview);
    }

    setFiltered(result);
  }, [experiments, search, selectedCategory, selectedReview]);

  const handleRowClick = (id: string) => {
    onSelectExperiment(id);
    onNavigate(`experiments/${id}`);
  };

  const categories = ["All", ...Array.from(new Set(experiments.map(e => e.category)))];
  const reviewStatuses = ["All", "Pending Review", "Approved", "Requires Audit"];

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
          Experiment Memory Table
        </h2>
        <p className="text-sm text-[#64748B]">
          Browse, query, and filter your historical failed model traces and remediation recipes.
        </p>
      </div>

      {/* FILTER CONTROLS GRID */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
        {/* Search */}
        <div className="md:col-span-5 relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search Project Name, ID, or Failure Details..."
            className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-10 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Filter Category */}
        <div className="md:col-span-3 flex items-center gap-2">
          <span className="text-xs font-semibold text-[#64748B] uppercase whitespace-nowrap hidden sm:inline">Category</span>
          <select
            className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] bg-white text-[#0F172A]"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map((cat, i) => (
              <option key={i} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Filter Review */}
        <div className="md:col-span-4 flex items-center gap-2">
          <span className="text-xs font-semibold text-[#64748B] uppercase whitespace-nowrap hidden sm:inline">Review Status</span>
          <select
            className="w-full rounded-xl border border-[#E2E8F0] p-2.5 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] bg-white text-[#0F172A]"
            value={selectedReview}
            onChange={(e) => setSelectedReview(e.target.value)}
          >
            {reviewStatuses.map((st, i) => (
              <option key={i} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      {/* RE-USABLE EXPERIMENTS DATA TABLE */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden">
        {filtered.length === 0 ? (
          <div className="text-center py-20 px-6">
            <ShieldAlert className="w-12 h-12 text-[#64748B] mx-auto opacity-50 mb-3" />
            <h4 className="text-base font-bold text-[#0f172a] font-heading">
              No Matching Records Found
            </h4>
            <p className="text-xs text-[#64748B] mt-1 max-w-md mx-auto">
              We couldn&apos;t find any failed experiment matching your query or filters. Get started by entering an error prompt in the Reasoning Chat!
            </p>
            <button
              onClick={() => onNavigate("chat")}
              className="mt-4 p-2.5 px-6 rounded-xl text-xs font-semibold text-white bg-[#7C3AED] hover:bg-[#6D28D9] shadow-sm transition-all hover-lift cursor-pointer"
            >
              Start New Analysis Trace
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="bg-[#FAFBFD] border-b border-[#E2E8F0] text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  <th className="p-4 pl-6">Experiment ID</th>
                  <th className="p-4">Project Name</th>
                  <th className="p-4">Model Pipeline Type</th>
                  <th className="p-4">Failure Category</th>
                  <th className="p-4">Agent Confidence</th>
                  <th className="p-4">Review Status</th>
                  <th className="p-4 text-right pr-6">Manage Trace</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {filtered.map((exp) => (
                  <tr
                    key={exp.id}
                    onClick={() => handleRowClick(exp.id)}
                    className="hover:bg-[#F8FAFC]/70 cursor-pointer transition-colors"
                  >
                    <td className="p-4 pl-6 font-mono font-bold text-[#2563EB]">{exp.id}</td>
                    <td className="p-4 font-bold text-[#0F172A]">{exp.project}</td>
                    <td className="p-4 text-[#64748B]">{exp.modelType}</td>
                    <td className="p-4">
                      <span className="p-1 px-2 rounded-lg bg-purple-50 text-[#7C3AED] font-bold text-[10px] tracking-wide uppercase border border-purple-150">
                        {exp.category}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold">{exp.confidence}%</span>
                        <div className="w-16 bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden hidden sm:inline-block">
                          <div className="bg-[#2563EB] h-full rounded-full" style={{ width: `${exp.confidence}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`p-1 px-2 rounded-md font-semibold text-[10px] ${
                        exp.humanReview === 'Approved' ? "bg-emerald-50 text-emerald-700" :
                        exp.humanReview === 'Requires Audit' ? "bg-rose-50 text-rose-700" :
                        "bg-amber-50 text-amber-700"
                      }`}>
                        {exp.humanReview}
                      </span>
                    </td>
                    <td className="p-4 text-right pr-6">
                      <button className="p-1 px-2.5 bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] rounded-lg text-[10.5px] font-bold group flex items-center gap-1 ml-auto">
                        <Eye className="w-3.5 h-3.5" /> Core Trace
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
