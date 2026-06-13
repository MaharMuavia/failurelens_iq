import React from "react";
import { BookOpen, Database, Network, Workflow, FileSpreadsheet } from "lucide-react";

type FoundryIQLayerDiagramProps = {
  mode?: string;
};

const steps = [
  { label: "Knowledge Sources", icon: BookOpen },
  { label: "Local Knowledge Base", icon: Database },
  { label: "Citation Retrieval", icon: Network },
  { label: "Reasoning Agents", icon: Workflow },
  { label: "Manager Report", icon: FileSpreadsheet }
];

export const FoundryIQLayerDiagram: React.FC<FoundryIQLayerDiagramProps> = ({ mode = "Foundry IQ Local Adapter Mode" }) => {
  return (
    <section className="foundry-layer-diagram p-4 rounded bg-[#071226]/40 text-white" aria-label="Foundry IQ local adapter architecture">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h4 className="font-semibold text-cyan-200">Foundry IQ Layer</h4>
          <p className="text-sm text-slate-400">Local adapter mode with citations and permission-aware metadata</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="text-xs uppercase tracking-[0.18em] text-cyan-300 bg-[#06263c] px-2 py-1 rounded">Foundry IQ Local Adapter</span>
          <span className="text-xs uppercase tracking-[0.18em] text-slate-200 bg-[#0b1220] border border-cyan-700 px-2 py-1 rounded">Adapter Ready</span>
          <span className="text-xs uppercase tracking-[0.18em] text-amber-200 bg-[#1f2937] px-2 py-1 rounded">Azure Quota Blocked</span>
          <span className="text-xs uppercase tracking-[0.18em] text-slate-200 bg-[#0f172a] px-2 py-1 rounded">Live Azure Not Active</span>
          {mode && <span className="text-xs uppercase tracking-[0.18em] text-cyan-300 bg-[#06263c] px-2 py-1 rounded">{mode}</span>}
        </div>
      </div>
      <div className="mt-4 text-sm">
        <ol className="list-decimal list-inside space-y-1 text-slate-300">
          <li>Knowledge Sources</li>
          <li>Local Knowledge Base</li>
          <li>Citation Retrieval</li>
          <li>Reasoning Agents</li>
          <li>Manager Report</li>
        </ol>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <article key={step.label} className="rounded-xl bg-[#0b1320]/80 p-3 border border-white/10 flex items-center gap-2">
              <Icon size={18} className="text-cyan-300" />
              <span className="text-sm text-slate-200">{step.label}</span>
            </article>
          );
        })}
      </div>
    </section>
  );
};

export default FoundryIQLayerDiagram;
