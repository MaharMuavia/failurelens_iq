import { Activity } from "lucide-react";
import { AgentTraceCard } from "./AgentTraceCard";
import type { reasoningSteps } from "../data/mockData";

type ReasoningPanelProps = {
  steps: typeof reasoningSteps;
};

export function ReasoningPanel({ steps }: ReasoningPanelProps) {
  return (
    <section className="panel reasoning-panel" aria-label="Agent reasoning">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Agent reasoning</p>
          <h2>Live trace</h2>
        </div>
        <span className="icon-chip neutral">
          <Activity size={18} />
        </span>
      </div>
      <div className="trace-list">
        {steps.map((step) => (
          <AgentTraceCard key={`${step.agent}-${step.finding}`} {...step} />
        ))}
      </div>
    </section>
  );
}
