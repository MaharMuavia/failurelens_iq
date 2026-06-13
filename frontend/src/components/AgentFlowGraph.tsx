import { useEffect, useMemo, useState } from "react";
import { Background, BaseEdge, Controls, Handle, Position, ReactFlow, getBezierPath, type EdgeProps, type NodeProps } from "@xyflow/react";
import { AlertTriangle, Brain, Check, Clock3, ShieldCheck, ShieldQuestion } from "lucide-react";
import "@xyflow/react/dist/style.css";

type AgentStatus = "waiting" | "running" | "completed" | "skipped" | "human_review";

export type AgentFlowEvent = {
  agent?: string;
  agent_name?: string;
  status?: string;
  event?: string;
  confidence?: number;
  confidence_score?: number;
  finding?: string;
  findings?: string[];
};

type AgentFlowNode = {
  id: string;
  label: string;
  status: AgentStatus;
  confidence?: number;
  summary?: string;
  foundry_iq_status?: string | null;
  duration_ms?: number | null;
};

const defaultFlow: AgentFlowNode[] = [
  { id: "planner", label: "Planner", status: "waiting", summary: "Builds execution plan and suspected failure mode." },
  { id: "foundry_iq", label: "Foundry IQ Layer", status: "waiting", summary: "Grounded retrieval and permission-aware metadata." },
  { id: "classifier", label: "Failure Classifier", status: "waiting", summary: "Classifies the failure mode." },
  { id: "root_cause", label: "Root Cause Analyzer", status: "waiting", summary: "Explains root cause and violated assumption." },
  { id: "historian", label: "Experiment Historian", status: "waiting", summary: "Finds prior failed-run patterns." },
  { id: "coach", label: "Prescriptive Coach", status: "waiting", summary: "Turns diagnosis into remediation." },
  { id: "certification", label: "Certification Evaluator", status: "waiting", summary: "Maps skill gap to Microsoft learning." },
  { id: "manager", label: "Integration Manager", status: "waiting", summary: "Packages the manager-ready action view." },
  { id: "judge_report", label: "Judge Report", status: "waiting", summary: "Final judge-ready submission report." }
];

function normalizeName(name: string) {
  const lowered = name.toLowerCase();
  if (lowered.includes("planner")) return "planner";
  if (lowered.includes("foundry") || lowered.includes("iq")) return "foundry_iq";
  if (lowered.includes("classifier")) return "classifier";
  if (lowered.includes("root") || lowered.includes("diagnostic")) return "root_cause";
  if (lowered.includes("historian")) return "historian";
  if (lowered.includes("coach") || lowered.includes("remediation")) return "coach";
  if (lowered.includes("cert") || lowered.includes("assessment")) return "certification";
  if (lowered.includes("manager") || lowered.includes("integration")) return "manager";
  if (lowered.includes("report") || lowered.includes("judge")) return "judge_report";
  return lowered;
}

function normalizeStatus(value?: string): AgentStatus {
  const lowered = String(value || "waiting").toLowerCase().replace(" ", "_");
  if (lowered === "running" || lowered === "agent_started") return "running";
  if (lowered === "completed" || lowered === "agent_completed") return "completed";
  if (lowered === "skipped") return "skipped";
  if (lowered === "human_review" || lowered === "human-review") return "human_review";
  return "waiting";
}

function flowFromReport(demoReport?: any | null): AgentFlowNode[] {
  const timeline: any[] = Array.isArray(demoReport?.reasoning_timeline) ? demoReport.reasoning_timeline : [];
  const durationMap = new Map<string, number>();
  for (const trace of timeline) {
    const id = normalizeName(String(trace.agent_name || trace.agent || ""));
    if (id && typeof trace.duration_ms === "number") durationMap.set(id, trace.duration_ms);
  }

  if (Array.isArray(demoReport?.agent_flow) && demoReport.agent_flow.length) {
    return defaultFlow.map((node) => {
      const match = demoReport.agent_flow.find((item: AgentFlowNode) => item.id === node.id || item.label === node.label);
      const merged = match ? { ...node, ...match, status: normalizeStatus(match.status) } : node;
      merged.duration_ms = durationMap.get(node.id) ?? merged.duration_ms ?? null;
      return merged;
    });
  }

  const workflow = Array.isArray(demoReport?.agent_workflow) ? demoReport.agent_workflow : [];
  return defaultFlow.map((node) => {
    const match = workflow.find((item: any) => normalizeName(String(item.agent_name || item.agent || "")) === node.id);
    if (!match) return { ...node, duration_ms: durationMap.get(node.id) ?? null };
    return {
      ...node,
      status: normalizeStatus(match.status),
      confidence: match.confidence_score ?? match.confidence,
      summary: match.findings?.[0] || node.summary,
      duration_ms: durationMap.get(node.id) ?? null,
    };
  });
}

function mergeEvents(flow: AgentFlowNode[], events: AgentFlowEvent[]) {
  if (!events.length) return flow;
  const latestByAgent = new Map<string, AgentFlowEvent>();
  events.forEach((event) => {
    latestByAgent.set(normalizeName(String(event.agent || event.agent_name || "")), event);
  });
  return flow.map((node) => {
    const event = latestByAgent.get(node.id);
    if (!event) return node;
    return {
      ...node,
      status: normalizeStatus(event.status || event.event),
      confidence: event.confidence_score ?? event.confidence ?? node.confidence,
      summary: event.finding || event.findings?.[0] || node.summary
    };
  });
}

function applyAnimation(flow: AgentFlowNode[], activeIndex: number, isAnimating: boolean) {
  if (!isAnimating || activeIndex < 0) return flow;
  return flow.map((node, index) => {
    if (index < activeIndex) return { ...node, status: "completed" as AgentStatus, confidence: node.confidence ?? 0.78 };
    if (index === activeIndex) return { ...node, status: "running" as AgentStatus };
    return { ...node, status: "waiting" as AgentStatus };
  });
}

function statusIcon(status: AgentStatus) {
  if (status === "completed") return <Check size={15} />;
  if (status === "human_review") return <ShieldQuestion size={15} />;
  if (status === "running") return <Brain size={15} />;
  if (status === "skipped") return <AlertTriangle size={15} />;
  return <Clock3 size={15} />;
}

function AgentNode({ data }: NodeProps) {
  const node = data as unknown as AgentFlowNode;
  const confidence = typeof node.confidence === "number" ? `${Math.round(node.confidence * 100)}%` : "pending";
  const citationsCount = (node as any).citationsCount ?? 5;
  return (
    <article className={`agent-flow-node agent-${node.id} ${node.status} ${node.id === "foundry_iq" ? "iq-node" : ""}`}>
      <Handle className="agent-handle" type="target" position={Position.Left} />
      <div className="agent-flow-node-top">
        <span>{statusIcon(node.status)}</span>
        <small>{node.status.replace("_", " ")}</small>
      </div>
      <strong>{node.label}</strong>
      <p>{node.summary}</p>
      <div className="agent-flow-node-meta">
        <span>{confidence}</span>
        {typeof node.duration_ms === "number" && (
          <span className="agent-duration">{node.duration_ms < 1000 ? `${Math.round(node.duration_ms)}ms` : `${(node.duration_ms / 1000).toFixed(1)}s`}</span>
        )}
        {node.id === "foundry_iq" && (
          <span className="agent-citations" style={{ padding: '1px 5px', borderRadius: '4px', background: '#e0e7ff', color: '#4338ca', fontSize: '10px', fontWeight: 'bold' }}>
            {citationsCount} Citations
          </span>
        )}
      </div>
      <Handle className="agent-handle" type="source" position={Position.Right} />
    </article>
  );
}

function FlowEdge(props: EdgeProps) {
  const [edgePath] = getBezierPath(props);
  return <BaseEdge path={edgePath} className={props.selected ? "agent-flow-edge selected" : "agent-flow-edge"} />;
}

const nodeTypes = { agentNode: AgentNode };
const edgeTypes = { flowEdge: FlowEdge };

export function AgentFlowGraph({
  events = [],
  demoReport,
  isAnimating = false
}: {
  events?: AgentFlowEvent[];
  demoReport?: any | null;
  isAnimating?: boolean;
}) {
  const [activeIndex, setActiveIndex] = useState(-1);
  const hasReview = Boolean(demoReport?.confidence_summary?.requires_human_review);
  const proofLevel = demoReport?.microsoft_iq_compliance?.proof_level || demoReport?.agent_flow?.find((node: AgentFlowNode) => node.foundry_iq_status)?.foundry_iq_status;

  useEffect(() => {
    if (!isAnimating) {
      setActiveIndex(-1);
      return;
    }
    setActiveIndex(0);
    const timer = window.setInterval(() => {
      setActiveIndex((current) => (current >= defaultFlow.length - 1 ? current : current + 1));
    }, 520);
    return () => window.clearInterval(timer);
  }, [isAnimating]);

  const flow = useMemo(() => {
    const fromReport = flowFromReport(demoReport);
    const withEvents = mergeEvents(fromReport, events);
    return applyAnimation(withEvents, activeIndex, isAnimating);
  }, [activeIndex, demoReport, events, isAnimating]);

  const nodes = useMemo(
    () =>
      flow.map((node, index) => ({
        id: node.id,
        type: "agentNode",
        position: { x: index * 236, y: index % 2 === 0 ? 18 : 140 },
        data: {
          ...node,
          citationsCount: demoReport?.foundry_iq_layer?.citations_count ?? demoReport?.iq_grounding_story?.citations?.length ?? 5
        },
        draggable: false,
        selectable: false
      })),
    [flow, demoReport]
  );

  const edges = useMemo(
    () =>
      flow.slice(0, -1).map((node, index) => ({
        id: `${node.id}-${flow[index + 1].id}`,
        source: node.id,
        target: flow[index + 1].id,
        type: "flowEdge",
        animated: node.status === "completed" || node.status === "running",
        className: node.status === "completed" ? "completed" : ""
      })),
    [flow]
  );

  return (
    <section className="panel agent-flow-panel" aria-label="Animated agent reasoning flow">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Animated Agent Flow</p>
          <h2>Planner to manager, one evidence-grounded chain</h2>
        </div>
        <div className="flow-badge-row">
          <span className={hasReview ? "flow-badge review" : "flow-badge"}>
            {hasReview ? "Human review gate" : "Confidence gate active"}
          </span>
          <span className="flow-badge iq">
            <ShieldCheck size={14} />
            {proofLevel || "Foundry IQ status"}
          </span>
        </div>
      </div>
      <div className="agent-flow-canvas" data-testid="agent-flow-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.18 }}
          minZoom={0.45}
          maxZoom={1.25}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#cbd5e1" gap={22} size={1} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </section>
  );
}
