import { Brain, GitCompare, Search, ShieldCheck, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";

interface DemoReport {
  root_cause_analysis?: {
    root_cause?: string;
    violated_assumption?: string;
    confidence?: number;
    requires_human_review?: boolean;
    evidence?: string[];
    counter_evidence?: string[];
    hypothesis_conflict?: boolean;
  };
  failure_classification?: {
    failure_category?: string;
    confidence?: number;
    conflicting_categories?: string[];
    reasoning?: string;
  };
  agent_flow?: {
    id: string;
    label: string;
    status: string;
    confidence: number;
    summary: string;
  }[];
  confidence_summary?: {
    overall_confidence?: number;
    gate_passed?: boolean;
    requires_human_review?: boolean;
    human_review_reason?: string;
  };
}

function AnimatedConfidenceGauge({
  confidence,
  threshold,
  passed,
}: {
  confidence: number;
  threshold: number;
  passed: boolean;
}) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    let frame: number;
    const duration = 1500;
    const start = performance.now();
    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedValue(eased * confidence);
      if (progress < 1) frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [confidence]);

  const pct = Math.round(animatedValue * 100);
  const thresholdPct = Math.round(threshold * 100);
  const color = passed ? "var(--green)" : "var(--red)";
  const bgColor = passed ? "var(--green-soft)" : "var(--red-soft)";

  return (
    <div className="confidence-gate-visual">
      <div className="gate-gauge-track">
        <div
          className="gate-gauge-fill"
          style={{ width: `${pct}%`, background: color }}
        />
        <div
          className="gate-threshold-line"
          style={{ left: `${thresholdPct}%` }}
        >
          <span className="gate-threshold-label">T={thresholdPct}%</span>
        </div>
      </div>
      <div className="gate-gauge-labels">
        <span style={{ color }}>{pct}%</span>
        <span
          className={`gate-verdict ${passed ? "gate-passed" : "gate-failed"}`}
        >
          <span className="gate-verdict-dot" />
          {passed ? "GATE PASSED" : "HUMAN REVIEW REQUIRED"}
        </span>
      </div>
    </div>
  );
}

export function ConflictResolutionPanel({
  demoReport,
}: {
  demoReport?: DemoReport | null;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (demoReport?.root_cause_analysis) {
      const timer = setTimeout(() => setVisible(true), 100);
      return () => clearTimeout(timer);
    }
    setVisible(false);
  }, [demoReport?.root_cause_analysis]);

  if (!demoReport?.root_cause_analysis) return null;

  const diagnosis = demoReport.root_cause_analysis;
  const classification = demoReport.failure_classification;
  const planner = demoReport.agent_flow?.find((a) => a.id === "planner");
  const gate = demoReport.confidence_summary;
  const gatePassed = gate?.gate_passed !== false;
  const overallConfidence = gate?.overall_confidence ?? diagnosis.confidence ?? 0;
  const threshold =
    gatePassed && overallConfidence > 0.5 ? 0.45 : 0.55;

  const columns = [
    {
      key: "planner",
      icon: Search,
      title: "Planner Hypothesis",
      color: "var(--blue)",
      bg: "var(--blue-soft)",
      border: "rgba(96, 165, 250, 0.35)",
      confidence: planner?.confidence ?? 0.82,
      body: planner?.summary || "Suspected evaluation methodology failure.",
      detail: "Pre-pipeline hypothesis based on experiment signals",
    },
    {
      key: "classifier",
      icon: GitCompare,
      title: "Classifier Decision",
      color: "#a78bfa",
      bg: "rgba(167, 139, 250, 0.14)",
      border: "rgba(167, 139, 250, 0.38)",
      confidence: classification?.confidence ?? 0.79,
      body:
        classification?.failure_category?.replace(/_/g, " ") ||
        "Evaluation Methodology",
      detail: classification?.conflicting_categories?.length
        ? `Conflicts: ${classification.conflicting_categories.join(", ")}`
        : "No conflicting categories detected",
    },
    {
      key: "diagnostic",
      icon: diagnosis.requires_human_review ? ShieldAlert : Brain,
      title: "Diagnostic Resolution",
      color: diagnosis.requires_human_review ? "var(--red)" : "var(--green)",
      bg: diagnosis.requires_human_review
        ? "var(--red-soft)"
        : "var(--green-soft)",
      border: diagnosis.requires_human_review
        ? "rgba(251, 113, 133, 0.45)"
        : "rgba(52, 211, 153, 0.45)",
      confidence: diagnosis.confidence ?? 0.83,
      body:
        diagnosis.root_cause ||
        "Aggregate accuracy masked minority-class collapse.",
      detail: diagnosis.violated_assumption
        ? `Violated: ${diagnosis.violated_assumption}`
        : "Assumption validated",
    },
  ];

  return (
    <section className="panel conflict-resolution-panel" aria-label="Agent Reasoning Consensus">
      <div className="panel-title-row">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="consensus-dot" />
          <div>
            <p className="eyebrow">Agent Consensus</p>
            <h2>Agent Reasoning Consensus</h2>
          </div>
        </div>
        {gate && (
          <span
            className={`flow-badge ${gatePassed ? "" : "review"}`}
            style={{ fontSize: 11 }}
          >
            {gatePassed ? (
              <ShieldCheck size={14} />
            ) : (
              <ShieldAlert size={14} />
            )}
            {gatePassed ? "Consensus Reached" : "Review Required"}
          </span>
        )}
      </div>

      <div className="consensus-columns">
        {columns.map((col, i) => {
          const Icon = col.icon;
          return (
            <article
              key={col.key}
              className={`consensus-card ${visible ? "consensus-card-visible" : ""}`}
              style={{
                borderColor: col.border,
                transitionDelay: `${i * 150}ms`,
              }}
            >
              <div className="consensus-card-header">
                <span
                  className="consensus-card-icon"
                  style={{ color: col.color, background: col.bg }}
                >
                  <Icon size={16} />
                </span>
                <span className="consensus-card-confidence" style={{ color: col.color }}>
                  {Math.round(col.confidence * 100)}%
                </span>
              </div>
              <strong style={{ color: col.color }}>{col.title}</strong>
              <p className="consensus-card-body">{col.body}</p>
              <small className="consensus-card-detail">{col.detail}</small>
            </article>
          );
        })}
      </div>

      <AnimatedConfidenceGauge
        confidence={overallConfidence}
        threshold={threshold}
        passed={gatePassed}
      />
    </section>
  );
}
