import { BookOpenCheck, Database, FileText } from "lucide-react";
import type { Experiment } from "../data/mockData";

type EvidenceTableProps = {
  experiment: Experiment;
};

export function EvidenceTable({ experiment }: EvidenceTableProps) {
  const rows = [
    {
      label: "Observed failure",
      value: experiment.failure_observation,
      icon: FileText
    },
    {
      label: "Evidence fields",
      value: [
        "metrics",
        "baseline_metrics",
        "class_balance",
        ...experiment.drift_indicators,
        ...experiment.data_quality_signals,
        ...experiment.suspected_leakage_columns
      ]
        .filter(Boolean)
        .slice(0, 6)
        .join(", "),
      icon: Database
    },
    {
      label: "Grounded citations",
      value: "remediation_playbook.md, ml_failure_taxonomy.md, dp100_skill_guide.md",
      icon: BookOpenCheck
    }
  ];

  return (
    <section className="panel evidence-panel" aria-label="Evidence and citations">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Grounded citations</p>
          <h2>Evidence pack</h2>
        </div>
      </div>
      <div className="evidence-list">
        {rows.map((row) => {
          const Icon = row.icon;
          return (
            <div className="evidence-row" key={row.label}>
              <span className="evidence-icon">
                <Icon size={16} />
              </span>
              <div>
                <strong>{row.label}</strong>
                <p>{row.value || "No explicit signal recorded."}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
