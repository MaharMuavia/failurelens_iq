import { ArrowDownUp, CircleDot, Search } from "lucide-react";
import type { Experiment } from "../data/mockData";

type ExperimentTableProps = {
  experiments: Experiment[];
  selectedId: string;
  onSelect: (experimentId: string) => void;
};

function metricSummary(experiment: Experiment) {
  const entries = Object.entries(experiment.metrics);
  if (!entries.length) {
    return "No metrics";
  }
  return entries
    .slice(0, 2)
    .map(([key, value]) => `${key.replace("_", " ")} ${(value * 100).toFixed(0)}%`)
    .join(" / ");
}

function riskClass(experiment: Experiment) {
  if (experiment.outcome === "success") return "success";
  if (experiment.outcome === "unknown") return "warning";
  if (experiment.failure_category_label.includes("Bias")) return "danger";
  return "attention";
}

export function ExperimentTable({ experiments, selectedId, onSelect }: ExperimentTableProps) {
  return (
    <section className="panel table-panel" aria-label="Experiment triage table">
      <div className="panel-title-row table-toolbar">
        <div>
          <p className="eyebrow">Experiment triage</p>
          <h2>Recent failure memory</h2>
        </div>
        <div className="toolbar-actions">
          <label className="search-box">
            <Search size={16} />
            <input aria-label="Search experiments" placeholder="Search experiments" />
          </label>
          <button className="icon-button" aria-label="Sort experiments" title="Sort experiments">
            <ArrowDownUp size={17} />
          </button>
        </div>
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Experiment</th>
              <th>Team</th>
              <th>Category</th>
              <th>Stage</th>
              <th>Metric signal</th>
              <th>Gate</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((experiment) => (
              <tr
                className={experiment.experiment_id === selectedId ? "selected-row" : ""}
                key={experiment.experiment_id}
                onClick={() => onSelect(experiment.experiment_id)}
              >
                <td>
                  <button className="row-title" type="button">
                    <span>{experiment.experiment_id}</span>
                    <small>{experiment.model_type}</small>
                  </button>
                </td>
                <td>{experiment.team_id}</td>
                <td>{experiment.failure_category_label}</td>
                <td>{experiment.pipeline_stage}</td>
                <td>{metricSummary(experiment)}</td>
                <td>
                  <span className={`status-dot ${riskClass(experiment)}`}>
                    <CircleDot size={14} />
                    {experiment.outcome}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
