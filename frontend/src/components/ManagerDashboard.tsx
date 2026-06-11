import {
  BarChart3,
  Bell,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Clipboard,
  DatabaseZap,
  Download,
  FileWarning,
  Gauge,
  HeartPulse,
  LayoutDashboard,
  Play,
  Search,
  Settings,
  ShieldAlert,
  Users
} from "lucide-react";
import { ConfidenceMeter } from "./ConfidenceMeter";
import { EvidenceTable } from "./EvidenceTable";
import { ExperimentTable } from "./ExperimentTable";
import { KnowledgeSearch } from "./KnowledgeSearch";
import { ReasoningPanel } from "./ReasoningPanel";
import { teamProfiles } from "../data/mockData";
import { VIDEO_DEMO_MODE } from "../config/demoMode";
import { useAnalysis } from "../hooks/useAnalysis";
import { useSSEStream } from "../hooks/useSSEStream";

const navItems = [
  { label: "Analysis", icon: LayoutDashboard },
  { label: "Experiments", icon: DatabaseZap },
  { label: "Manager", icon: Users },
  { label: "Knowledge", icon: BookOpen }
];

const demoAgents = [
  "Classifier",
  "Root cause",
  "Historian",
  "Coach",
  "Certification",
  "Integration"
];

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function ManagerDashboard({
  activeTab = "Analysis",
  onTabChange
}: {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}) {
  const analysis = useAnalysis("EXP-1001");
  const visibleSteps = useSSEStream(analysis.isRunning, analysis.selectedId, analysis.backendDisconnected);
  const selected = analysis.selectedExperiment;
  const team = teamProfiles.find((profile) => profile.team_id === selected.team_id) || teamProfiles[0];
  const experiments = analysis.experiments;

  const failedCount = experiments.filter((experiment) => experiment.outcome === "failure").length;
  const reviewQueue = experiments.filter(
    (experiment) => experiment.outcome === "unknown" || experiment.failure_category_label.includes("Bias")
  ).length;

  const changeTab = (label: string) => {
    if (onTabChange) {
      onTabChange(label);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <span className="brand-mark">
            <BrainCircuit size={22} />
          </span>
          <div>
            <strong>FailureLens IQ</strong>
            <span>Learning memory</span>
          </div>
        </div>

        <nav aria-label="Primary navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.label;
            return (
              <button
                className={isActive ? "nav-item active" : "nav-item"}
                key={item.label}
                onClick={() => changeTab(item.label)}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-card">
          <p>Retrieval mode</p>
          <strong>local_iq_simulation</strong>
          <span>25 experiments indexed</span>
        </div>
      </aside>

      <main className="workspace">
        {VIDEO_DEMO_MODE && (
          <section className="video-demo-banner" role="status">
            <CheckCircle2 size={18} />
            <strong>Judge Demo Ready</strong>
            <span>FailureLens IQ | Microsoft Agents League | Reasoning Agents Track</span>
          </section>
        )}

        <header className="topbar">
          <div>
            <p className="workspace-kicker">Analysis workspace</p>
            <h1>Experiment failure intelligence</h1>
          </div>

          <div className="topbar-actions">
            <label className="global-search">
              <Search size={17} />
              <input placeholder="Search runs, teams, citations" aria-label="Global search" />
            </label>
            <button className="icon-button" aria-label="Notifications" title="Notifications">
              <Bell size={18} />
            </button>
            <button className="icon-button" aria-label="Settings" title="Settings">
              <Settings size={18} />
            </button>
          </div>
        </header>

        <section className="status-strip" aria-label="FailureLens summary">
          <article className="stat-card">
            <span className="stat-icon teal">
              <FileWarning size={18} />
            </span>
            <div>
              <strong>{failedCount}</strong>
              <p>failed runs</p>
            </div>
          </article>
          <article className="stat-card">
            <span className="stat-icon amber">
              <ShieldAlert size={18} />
            </span>
            <div>
              <strong>{reviewQueue}</strong>
              <p>human review</p>
            </div>
          </article>
          <article className="stat-card">
            <span className="stat-icon blue">
              <Gauge size={18} />
            </span>
            <div>
              <strong>{formatPercent(analysis.confidence)}</strong>
              <p>selected confidence</p>
            </div>
          </article>
          <article className="stat-card">
            <span className="stat-icon red">
              <BarChart3 size={18} />
            </span>
            <div>
              <strong>{experiments.filter((experiment) => experiment.failure_category_label.includes("Bias")).length}</strong>
              <p>bias patterns</p>
            </div>
          </article>
        </section>

        {analysis.backendDisconnected && (
          <section className="connection-banner" role="status">
            Backend disconnected: showing local mock preview. Mock preview only. Start backend for real demo.
          </section>
        )}

        {analysis.authRequired && (
          <section className="connection-banner danger" role="alert">
            API key required. Set VITE_DEMO_API_KEY in frontend environment.
          </section>
        )}

        {analysis.statusMessage && (
          <section className="connection-banner neutral" role="status">
            {analysis.statusMessage}
          </section>
        )}

        {activeTab === "Analysis" && (
          <>
            <section className="dashboard-grid">
              <div className="primary-column">
                <section className="panel diagnosis-panel">
                  <div className="diagnosis-header">
                    <div>
                      <p className="eyebrow">Selected run</p>
                      <h2>
                        {selected.experiment_id} · {selected.failure_category_label}
                      </h2>
                    </div>
                    <div className="diagnosis-actions">
                      <button className="secondary-button" type="button" onClick={analysis.checkBackendHealth}>
                        <HeartPulse size={16} />
                        Health
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.checkAzureReadiness}>
                        <ShieldAlert size={16} />
                        Readiness
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.checkCostEstimate}>
                        <Gauge size={16} />
                        Cost
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.copyDemoSummary}>
                        <Clipboard size={16} />
                        Copy summary
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.copyIqComplianceSummary}>
                        <Clipboard size={16} />
                        Copy IQ
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.downloadReport}>
                        <Download size={16} />
                        Report
                      </button>
                      <button className="secondary-button" type="button" onClick={analysis.runJudgeDemo}>
                        <BrainCircuit size={16} />
                        {analysis.isDemoRunning ? "Building demo" : "Judge Demo"}
                      </button>
                      <button className="primary-button" type="button" onClick={analysis.runAnalysis}>
                        <Play size={16} />
                        {analysis.isRunning ? "Streaming" : "Run analysis"}
                      </button>
                    </div>
                  </div>

                  <div className="diagnosis-body">
                    <div>
                      <span className="category-band">{selected.pipeline_stage}</span>
                      <h3>{selected.failure_observation}</h3>
                      <p>
                        The system links this failure to {selected.validation_strategy} evidence, baseline comparison,
                        and team learning context for {team.team_name}.
                      </p>
                    </div>
                    <div className="metric-stack">
                      {Object.entries(selected.metrics).slice(0, 3).map(([metric, value]) => (
                        <div className="metric-row" key={metric}>
                          <span>{metric.replace("_", " ")}</span>
                          <strong>{formatPercent(value)}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              </div>

              <aside className="detail-rail">
                <ConfidenceMeter score={analysis.confidence} requiresReview={analysis.requiresReview} />
              </aside>
            </section>

            <section className="lower-grid-analysis" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginTop: "24px" }}>
              <ReasoningPanel steps={visibleSteps} />
              <EvidenceTable experiment={selected} />
            </section>

            <section className="demo-proof-grid" aria-label="Judge demo proof points" style={{ marginTop: "24px" }}>
              <section className="panel">
                <div className="panel-title-row">
                  <div>
                    <p className="eyebrow">Why this is not just a classifier</p>
                    <h2>Six reasoning agents split diagnosis from coaching and governance</h2>
                  </div>
                </div>
                <div className="agent-card-grid">
                  {demoAgents.map((agent, index) => (
                    <article className="agent-mini-card" key={agent}>
                      <span>{index + 1}</span>
                      <strong>{agent}</strong>
                      <p>{["Classifies failure mode", "Explains violated assumption", "Finds repeat patterns", "Builds remediation", "Maps Microsoft skills", "Packages leadership view"][index]}</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="panel">
                <div className="panel-title-row">
                  <div>
                    <p className="eyebrow">Microsoft IQ / Foundry Proof</p>
                    <h2>{analysis.demoReport?.microsoft_iq_compliance?.required_iq_layer || "Foundry IQ"}</h2>
                  </div>
                </div>
                <dl className="manager-list">
                  <div>
                    <dt>Selected IQ Layer</dt>
                    <dd>{analysis.demoReport?.microsoft_iq_compliance?.required_iq_layer || "Foundry IQ"}</dd>
                  </div>
                  <div>
                    <dt>Active Provider</dt>
                    <dd>{analysis.demoReport?.azure_status?.active_provider || "Local demo grounding"}</dd>
                  </div>
                  <div>
                    <dt>Azure AI Search</dt>
                    <dd>{analysis.demoReport?.azure_status?.azure_ai_search_used || analysis.readiness?.checks?.azure_ai_search_configured ? "Enabled" : "Disabled"}</dd>
                  </div>
                  <div>
                    <dt>Azure OpenAI</dt>
                    <dd>{analysis.demoReport?.azure_status?.azure_openai_used || analysis.readiness?.checks?.azure_openai_configured ? "Enabled" : "Disabled"}</dd>
                  </div>
                  <div>
                    <dt>Grounding Source Types</dt>
                    <dd>{(analysis.demoReport?.grounding_summary?.source_types || ["local_knowledge"]).join(", ")}</dd>
                  </div>
                  <div>
                    <dt>Citations Count</dt>
                    <dd>{analysis.demoReport?.grounding_summary?.citations_count ?? analysis.demoReport?.grounding_summary?.citations?.length ?? 0}</dd>
                  </div>
                  <div>
                    <dt>Mode</dt>
                    <dd>{analysis.demoReport?.grounding_summary?.mode || analysis.readiness?.status || "demo"}</dd>
                  </div>
                  <div>
                    <dt>Compliance</dt>
                    <dd>{analysis.demoReport?.microsoft_iq_compliance?.proof?.citations_present ? "Passed" : "Needs Azure Config"}</dd>
                  </div>
                </dl>
                {analysis.costEstimate && (
                  <p className="manager-note">
                    Cost guard: max {(analysis.costEstimate as any).azure_openai?.max_tokens_per_demo || 500} tokens per demo;
                    Search top-k capped at {(analysis.costEstimate as any).limits?.max_search_top_k || 5}.
                  </p>
                )}
                <p className="manager-note">
                  Demo mode uses local grounding so judges can run it without secrets. Production mode activates Azure AI Search,
                  Azure OpenAI, Cosmos DB, and Blob Storage only when credentials are configured.
                </p>
              </section>
            </section>

            {analysis.demoReport && (
              <section className="panel demo-summary" aria-label="Judge demo report" style={{ marginTop: "24px" }}>
                <div className="panel-title-row">
                  <div>
                    <p className="eyebrow">Judge demo</p>
                    <h2>{analysis.demoReport.demo_title}</h2>
                  </div>
                  <span className="icon-chip neutral">
                    <BrainCircuit size={18} />
                  </span>
                </div>
                <p>{analysis.demoReport.executive_summary}</p>
                {analysis.demoReport.video_demo_summary && (
                  <div className="video-summary-box">
                    <strong>{analysis.demoReport.video_demo_summary.solution}</strong>
                    <span>
                      {analysis.demoReport.video_demo_summary.reasoning_steps} reasoning steps |
                      {" "}{Math.round((analysis.demoReport.video_demo_summary.confidence || 0) * 100)}% confidence |
                      {" "}{analysis.demoReport.video_demo_summary.human_review_required ? "Human review gated" : "Auto-review ready"}
                    </span>
                  </div>
                )}
                <div className="demo-grid">
                  {(analysis.demoReport.agent_workflow || []).slice(0, 6).map((agent: any) => (
                    <article className="knowledge-hit" key={`${agent.agent_name}-${agent.status}`}>
                      <div>
                        <strong>{agent.agent_name}</strong>
                        <span>{Math.round((agent.confidence_score || 0) * 100)}%</span>
                      </div>
                      <p>{agent.findings?.[0] || agent.role}</p>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {activeTab === "Experiments" && (
          <section className="dashboard-grid">
            <div className="primary-column" style={{ width: "100%", maxWidth: "100%" }}>
              <ExperimentTable
                experiments={experiments}
                selectedId={analysis.selectedId}
                onSelect={analysis.setSelectedId}
              />
            </div>
          </section>
        )}

        {activeTab === "Manager" && (
          <section className="dashboard-grid">
            <div className="primary-column">
              <section className="panel manager-panel">
                <div className="panel-title-row">
                  <div>
                    <p className="eyebrow">Manager</p>
                    <h2>{team.team_id} risk summary</h2>
                  </div>
                </div>
                <dl className="manager-list">
                  <div>
                    <dt>Team</dt>
                    <dd>{team.team_name}</dd>
                  </div>
                  <div>
                    <dt>Domain</dt>
                    <dd>{team.domain}</dd>
                  </div>
                  <div>
                    <dt>Sprint load</dt>
                    <dd>{team.sprint_load}</dd>
                  </div>
                  <div>
                    <dt>Compliance</dt>
                    <dd>{team.compliance_sensitivity}</dd>
                  </div>
                </dl>
                <p className="manager-note">
                  Responsible AI risk is highest for TEAM-B. Convert repeated failure categories into sprint-level
                  review tasks and cert-aligned practice.
                </p>
              </section>
            </div>
          </section>
        )}

        {activeTab === "Knowledge" && (
          <section className="lower-grid" style={{ display: "block" }}>
            <KnowledgeSearch />
          </section>
        )}
      </main>
    </div>
  );
}
