import { AlertTriangle, CheckCircle2, ShieldCheck } from "lucide-react";

type ConfidenceMeterProps = {
  score: number;
  requiresReview: boolean;
};

export function ConfidenceMeter({ score, requiresReview }: ConfidenceMeterProps) {
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

      <div className="meter-shell" style={{ "--score": percent } as React.CSSProperties}>
        <div className="meter-value">{percent}%</div>
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
