import { Line, LineChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Experiment } from "../data/mockData";

type TrendRow = {
  metric: string;
  current: number;
  baseline: number;
};

function percent(value?: number) {
  return typeof value === "number" ? `${Math.round(value * 100)}%` : "n/a";
}

export function FailureTrendChart({ experiment }: { experiment: Experiment }) {
  const rows: TrendRow[] = [
    {
      metric: "Accuracy",
      current: experiment.metrics.accuracy ?? 0,
      baseline: experiment.baseline_metrics.accuracy ?? 0
    },
    {
      metric: "Minority F1",
      current: experiment.metrics.minority_f1 ?? experiment.metrics.f1 ?? 0,
      baseline: experiment.baseline_metrics.minority_f1 ?? experiment.baseline_metrics.f1 ?? 0
    },
    {
      metric: "ROC AUC",
      current: experiment.metrics.roc_auc ?? experiment.metrics.recall ?? 0,
      baseline: experiment.baseline_metrics.roc_auc ?? experiment.baseline_metrics.recall ?? 0
    }
  ];

  const minorityF1 = experiment.metrics.minority_f1 ?? experiment.metrics.f1 ?? 0;
  const baselineMinority = experiment.baseline_metrics.minority_f1 ?? experiment.baseline_metrics.f1 ?? 0;

  return (
    <section className="panel failure-trend-panel" aria-label="Metric trend comparison">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Metric trend</p>
          <h2>Current run vs baseline performance</h2>
        </div>
      </div>
      <div className="trend-chart-frame">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={rows} margin={{ top: 10, right: 20, left: -24, bottom: 0 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="metric" stroke="#94a3b8" tick={{ fill: "#cbd5e1", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tickFormatter={percent} tick={{ fill: "#cbd5e1", fontSize: 11 }} domain={[0, 1]} />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8, color: "#e2e8f0" }} formatter={(value: any) => percent(typeof value === "number" ? value : undefined)} />
            <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
            <Line type="monotone" dataKey="baseline" name="Baseline" stroke="#64748b" strokeWidth={3} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="current" name="Current" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="metric-callout">
        <strong>
          {minorityF1 < baselineMinority
            ? `Minority F1 is ${percent(minorityF1)} versus baseline ${percent(baselineMinority)} — a key signal for grounded failure.`
            : `Current performance is consistent with baseline, but the local adapter still inspects hidden failure evidence.`}
        </strong>
      </div>
    </section>
  );
}
