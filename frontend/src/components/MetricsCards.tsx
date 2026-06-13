import { BarChart3, Crosshair, Gauge } from "lucide-react";
import type { Experiment } from "../data/mockData";

function percent(value?: number) {
  return value === undefined ? "n/a" : `${Math.round(value * 100)}%`;
}

export function MetricsCards({ experiment }: { experiment: Experiment }) {
  const accuracy = experiment.metrics.accuracy;
  const minorityF1 = experiment.metrics.minority_f1 ?? experiment.metrics.f1 ?? experiment.metrics.recall;
  const baselineMinority = experiment.baseline_metrics.minority_f1 ?? experiment.baseline_metrics.f1 ?? experiment.baseline_metrics.recall;
  const delta = minorityF1 !== undefined && baselineMinority !== undefined ? minorityF1 - baselineMinority : undefined;

  return (
    <section className="metrics-cards" aria-label="Experiment failure metrics">
      <article className="metric-card success">
        <Gauge size={18} />
        <span>Reported accuracy</span>
        <strong>{percent(accuracy)}</strong>
        <p>Looks healthy in aggregate.</p>
      </article>
      <article className="metric-card danger">
        <Crosshair size={18} />
        <span>Minority F1</span>
        <strong>{percent(minorityF1)}</strong>
        <p>Hidden slice failure.</p>
      </article>
      <article className="metric-card warning">
        <BarChart3 size={18} />
        <span>Vs baseline</span>
        <strong>{delta === undefined ? "n/a" : `${delta > 0 ? "+" : ""}${Math.round(delta * 100)} pts`}</strong>
        <p>Reasoning agents inspect the contradiction.</p>
      </article>
    </section>
  );
}
