import { AlertTriangle, ArrowRight, CheckCircle2, Eye, HelpCircle, Lightbulb, Search, ShieldX, Target, XCircle } from "lucide-react";

type NestedStep = {
  thought_type?: string;
  finding?: string;
  description?: string;
  evidence_fields?: string[];
  uncertainty?: string[];
  next_action?: string | null;
  confidence_delta?: number;
};

type TimelineStep = {
  agent?: string;
  agent_name?: string;
  status?: string;
  confidence?: number;
  confidence_score?: number;
  finding?: string;
  findings?: string[];
  evidence?: string[];
  counter_evidence?: string[];
  key_evidence?: string[];
  reasoning_steps?: NestedStep[];
  recommended_next_actions?: string[];
};

const thoughtConfig: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  observation: { icon: Eye, color: "var(--muted)", label: "Observation" },
  hypothesis: { icon: Lightbulb, color: "var(--blue)", label: "Hypothesis" },
  evidence_check: { icon: CheckCircle2, color: "var(--green)", label: "Evidence" },
  inference: { icon: Target, color: "var(--teal)", label: "Inference" },
  counter_evidence: { icon: XCircle, color: "var(--red)", label: "Counter" },
  uncertainty_check: { icon: HelpCircle, color: "var(--muted)", label: "Uncertainty" },
  decision: { icon: ShieldX, color: "#a78bfa", label: "Decision" },
  next_action: { icon: ArrowRight, color: "var(--amber)", label: "Next Action" },
};

function ThoughtBadge({ type }: { type: string }) {
  const cfg = thoughtConfig[type] || thoughtConfig.inference;
  return (
    <span className="thought-badge" style={{ color: cfg.color, borderColor: cfg.color }}>
      {cfg.label}
    </span>
  );
}

export function ReasoningTimeline({ steps = [] }: { steps: TimelineStep[] }) {
  const normalized = steps.slice(0, 7).map((step) => ({
    agent: step.agent || step.agent_name || "Reasoning agent",
    status: step.status || "completed",
    confidence: step.confidence ?? step.confidence_score ?? 0.74,
    finding: step.finding || step.findings?.[0] || "Evidence, uncertainty, confidence, and next action were captured.",
    evidence: step.key_evidence || step.evidence || [],
    counterEvidence: step.counter_evidence || [],
    reasoningSteps: step.reasoning_steps || [],
    nextActions: step.recommended_next_actions || [],
  }));

  return (
    <section className="panel reasoning-timeline-panel" aria-label="Reasoning timeline">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Root Cause and Evidence</p>
          <h2>Judge-facing reasoning summaries</h2>
        </div>
      </div>
      <div className="trace-list">
        {normalized.map((step) => {
          const Icon = step.status === "completed" ? CheckCircle2 : AlertTriangle;
          return (
            <article className="trace-card" key={`${step.agent}-${step.finding}`}>
              <div className="trace-marker">
                <Icon size={15} />
              </div>
              <div className="trace-body">
                <div className="trace-heading">
                  <strong>{step.agent}</strong>
                  <span>{Math.round(step.confidence * 100)}%</span>
                </div>
                <p>{step.finding}</p>

                {step.reasoningSteps.length > 0 && (
                  <div className="thought-steps">
                    {step.reasoningSteps.slice(0, 6).map((rs, i) => {
                      const tt = rs.thought_type || "inference";
                      const cfg = thoughtConfig[tt] || thoughtConfig.inference;
                      const StepIcon = cfg.icon;
                      return (
                        <div className="thought-step-row" key={i}>
                          <StepIcon size={12} style={{ color: cfg.color, flexShrink: 0 }} />
                          <ThoughtBadge type={tt} />
                          <span
                            className="thought-step-text"
                            style={tt === "uncertainty_check" ? { fontStyle: "italic", color: "var(--muted)" } : undefined}
                          >
                            {rs.finding || rs.description || "Step completed."}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}

                <div className="tag-row">
                  {step.evidence.slice(0, 3).map((item) => (
                    <span className="tag tag-evidence" key={item}>
                      <CheckCircle2 size={10} /> {item}
                    </span>
                  ))}
                  {step.counterEvidence.slice(0, 2).map((item) => (
                    <span className="tag tag-counter" key={item}>
                      <XCircle size={10} /> {item}
                    </span>
                  ))}
                  {step.nextActions.slice(0, 1).map((item) => (
                    <span className="tag tag-action" key={item}>
                      <ArrowRight size={10} /> {item}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
