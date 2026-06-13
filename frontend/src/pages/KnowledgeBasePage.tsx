import React, { useState, useEffect } from "react";
import { ApiClient, KnowledgeItem } from "../api/client";
import { Search, BookOpen, AlertCircle, HelpCircle, Eye } from "lucide-react";

export const KnowledgeBasePage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<string>("All");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchKnowledge();
  }, [query, selectedFilter]);

  const fetchKnowledge = async () => {
    setLoading(true);
    // Mimic micro response timing
    await new Promise(r => setTimeout(r, 600));
    try {
      let data = await ApiClient.searchKnowledge(query);
      if (selectedFilter !== "All") {
        data = data.filter(k => k.sourceType === selectedFilter);
      }
      setItems(data);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const filters = [
    "All",
    "Failure Taxonomy",
    "Remediation Playbook",
    "Certification Mapping",
    "Responsible AI",
    "Manager Governance"
  ];

  return (
    <div className="space-y-6 select-none animate-fade-in text-left">
      <div>
        <h2 className="text-3xl font-black tracking-tight text-[#0F172A] font-heading">
          Foundry IQ Diagnostics Knowledge Base
        </h2>
        <p className="text-sm text-[#64748B]">
          Consult historical failure taxonomies, temporal target leakage playbooks, and Microsoft compliance checklists.
        </p>
      </div>

      {/* SEARCH AND FILTERS BUTTON ROW */}
      <div className="bg-white border border-[#E2E8F0] p-5 rounded-2xl shadow-sm space-y-4">
        <div className="relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search failure patterns, temporal leakage playbooks, proxy bias rules..."
            className="w-full rounded-xl border border-[#E2E8F0] p-2.5 pl-10 text-sm focus:outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED] text-[#0F172A]"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>

        <div className="flex gap-2.5 overflow-x-auto pb-1">
          {filters.map((fl) => (
            <button
              key={fl}
              onClick={() => setSelectedFilter(fl)}
              className={`p-2 px-3.5 rounded-full text-xs font-semibold whitespace-nowrap border cursor-pointer transition-all ${
                selectedFilter === fl
                  ? "bg-[#7C3AED] text-white border-transparent shadow-sm font-bold"
                  : "bg-white border-[#E2E8F0] text-[#64748B] hover:text-[#0f172a] hover:bg-[#F8FAFC]"
              }`}
            >
              {fl}
            </button>
          ))}
        </div>
      </div>

      {/* RETRIEVED LIST RESULTS */}
      <div className="space-y-4">
        {loading ? (
          // Skeleton loader
          <div className="space-y-4 animate-pulse">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-white border border-[#E2E8F0] p-6 rounded-2xl h-36">
                <div className="w-1/3 h-4.5 bg-slate-100 rounded mb-3"></div>
                <div className="w-2/3 h-3 bg-slate-100 rounded mb-2"></div>
                <div className="w-1/2 h-3 bg-slate-100 rounded"></div>
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20 bg-white border border-[#E2E8F0] rounded-2xl">
            <AlertCircle className="w-12 h-12 text-[#64748B] mx-auto opacity-50 mb-3" />
            <h4 className="text-base font-bold text-[#0F172A]">Excerpts Directory Empty</h4>
            <p className="text-xs text-[#64748B] mt-1 max-w-sm mx-auto">
              We couldn&apos;t match any Foundry playbooks. Refine search keywords.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {items.map((it) => (
              <div
                key={it.id}
                className="bg-white border border-[#E2E8F0] p-6 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between h-56"
              >
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className="p-1 px-2 rounded-lg bg-[#EEF4FF] text-[#2563EB] text-[9px] font-mono font-bold tracking-wider uppercase border border-blue-150">
                      {it.sourceType}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 font-bold">
                      Match: {Math.round(it.score * 100)}%
                    </span>
                  </div>
                  <h4 className="text-sm font-black text-[#0F172A] leading-snug font-heading">{it.title}</h4>
                  <p className="text-xs text-[#64748B] mt-2 leading-relaxed line-clamp-3">
                    {it.excerpt}
                  </p>
                </div>

                <div className="pt-3 border-t border-[#E2E8F0] text-[10.5px] font-semibold text-slate-400 font-mono truncate">
                  Source: {it.citation}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
