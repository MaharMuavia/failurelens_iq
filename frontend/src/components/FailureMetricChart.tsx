import { Bar, BarChart, CartesianGrid, Cell, Legend, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Experiment } from "../data/mockData";

type MetricStory = {
  headline?: string;
  accuracy?: number;
  minority_f1?: number;
  roc_auc?: number;
  callout?: string;
  message?: string;
};

type ChartRow = {
  metric: string;
  current: number;
  baseline?: number;
  fill: string;
};

function percent(value?: number) {
  return typeof value === "number" ? `${Math.round(value * 100)}%` : "n/a";
}

function metricValue(metricStory: MetricStory | undefined, experiment: Experiment, key: string, fallback: number) {
  const fromStory = metricStory?.[key as keyof MetricStory];
  if (typeof fromStory === "number") return fromStory;
  const fromExperiment = experiment.metrics[key];
  return typeof fromExperiment === "number" ? fromExperiment : fallback;
}

export function FailureMetricChart({ experiment, metricStory }: { experiment: Experiment; metricStory?: MetricStory }) {
  const accuracy = metricValue(metricStory, experiment, "accuracy", 0.93);
  const minorityF1 = metricValue(metricStory, experiment, "minority_f1", 0.14);
  const rocAuc = metricValue(metricStory, experiment, "roc_auc", 0.72);

  const rows: ChartRow[] = [
    { metric: "Accuracy", current: accuracy, baseline: experiment.baseline_metrics.accuracy, fill: "#22c55e" },
    { metric: "Minority F1", current: minorityF1, baseline: experiment.baseline_metrics.minority_f1, fill: "#ef4444" },
    { metric: "ROC AUC", current: rocAuc, baseline: experiment.baseline_metrics.roc_auc, fill: "#0078d4" }
  ];

  return (
    <section className="panel failure-metric-panel" aria-label="Failure metric visualization">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Failure Snapshot</p>
          <h2>{metricStory?.headline || "High accuracy hid minority-class failure"}</h2>
        </div>
      </div>

      <div className="metric-callout">
        <strong>{metricStory?.message || `${percent(accuracy)} accuracy hides ${percent(minorityF1)} minority F1.`}</strong>
        <span>Why this experiment failed despite high accuracy</span>
      </div>

      <div className="failure-chart-frame">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={rows} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="metric" stroke="#94a3b8" tick={{ fill: "#475569", fontSize: 11 }} />
            <YAxis stroke="#94a3b8" tickFormatter={percent} tick={{ fill: "#475569", fontSize: 11 }} domain={[0, 1]} />
            <Tooltip
              cursor={{ fill: "rgba(96, 165, 250, 0.08)" }}
              formatter={(value, name) => [percent(typeof value === "number" ? value : undefined), name === "current" ? "Current run" : "Baseline"]}
              contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, color: "#0f172a" }}
            />
            <Legend wrapperStyle={{ color: "#475569", fontSize: 12 }} />
            <ReferenceLine y={0.5} stroke="#f59e0b" strokeDasharray="4 4" />
            <Bar dataKey="baseline" name="Baseline" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="current" name="Current run" radius={[4, 4, 0, 0]}>
              {rows.map((row) => (
                <Cell key={row.metric} fill={row.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="metric-chart-note">{metricStory?.callout || "High accuracy hid minority-class failure."}</p>
    </section>
  );
}
