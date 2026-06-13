import { AlertTriangle, CheckCircle2, ShieldCheck } from "lucide-react";

type ConfidenceMeterProps = {
  score: number;
  requiresReview: boolean;
  factors?: Record<string, number>;
  threshold?: number;
};

const defaultFactors = {
  evidence_coverage: 0.78,
  category_evidence: 0.74,
  metric_degradation: 0.7,
  iq_relevance: 0.68,
  planner_agreement: 0.82,
  conflict_penalty: 0.08,
  missing_critical_fields: 0.05,
};

const positiveFactors = new Set(["evidence_coverage", "category_evidence", "metric_degradation", "iq_relevance", "planner_agreement"]);

function scoreClass(score: number) {
  if (score >= 0.7) return "score-high";
  if (score >= 0.4) return "score-medium";
  return "score-low";
}

export function ConfidenceMeter({ score, requiresReview, factors = defaultFactors, threshold = 0.45 }: ConfidenceMeterProps) {
  const percent = Math.round(score * 100);
  const status = requiresReview ? "Human review" : "Gate passed";
  const Icon = requiresReview ? AlertTriangle : CheckCircle2;

  return (
    <section className="panel confidence-panel" aria-label="Confidence gate">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Confidence gate</p>
          <h2>{status}</h2>
        </div>
        <span className={requiresReview ? "icon-chip warning" : "icon-chip success"}>
          <Icon size={18} />
        </span>
      </div>

      <div className="confidence-score-row">
        <div className={`confidence-score-number ${scoreClass(score)}`}>{percent}%</div>
        <span>Dynamic Threshold: {Math.round(threshold * 100)}%</span>
      </div>

      <div className="confidence-factor-list">
        {Object.entries(factors).map(([name, value]) => {
          const isPositive = positiveFactors.has(name);
          const width = Math.round(Math.max(0, Math.min(1, value)) * 100);
          return (
            <div className="confidence-factor-row" key={name}>
              <span>{name.replace(/_/g, " ")}</span>
              <div>
                <i className={isPositive ? "factor-positive" : "factor-penalty"} style={{ width: `${width}%` }} />
              </div>
              <strong>{width}%</strong>
            </div>
          );
        })}
      </div>

      <div className="confidence-copy">
        <ShieldCheck size={16} />
        <span>
          {requiresReview
            ? "Evidence is sensitive or sparse. Keep the recommendation gated until reviewer sign-off."
            : "Evidence strength is sufficient for diagnosis, remediation, and manager intelligence."}
        </span>
      </div>
    </section>
  );
}
