import { Check, Clock3 } from "lucide-react";

type AgentTraceCardProps = {
  agent: string;
  status: string;
  confidence: number;
  finding: string;
  evidence: string[];
};

export function AgentTraceCard({ agent, status, confidence, finding, evidence }: AgentTraceCardProps) {
  const Icon = status === "completed" ? Check : Clock3;

  return (
    <article className="trace-card">
      <div className="trace-marker">
        <Icon size={15} />
      </div>
      <div className="trace-body">
        <div className="trace-heading">
          <strong>{agent}</strong>
          <span>{Math.round(confidence * 100)}%</span>
        </div>
        <p>{finding}</p>
        <div className="tag-row">
          {evidence.slice(0, 3).map((item) => (
            <span className="tag" key={item}>
              {item}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}
