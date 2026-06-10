import {
  BarChart3,
  Bell,
  BookOpen,
  BrainCircuit,
  DatabaseZap,
  Download,
  FileWarning,
  Gauge,
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
import { useAnalysis } from "../hooks/useAnalysis";
import { useSSEStream } from "../hooks/useSSEStream";

const navItems = [
  { label: "Analysis", icon: LayoutDashboard },
  { label: "Experiments", icon: DatabaseZap },
  { label: "Manager", icon: Users },
  { label: "Knowledge", icon: BookOpen }
];

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function ManagerDashboard() {
  const analysis = useAnalysis("EXP-1001");
  const visibleSteps = useSSEStream(analysis.isRunning, analysis.selectedId, analysis.backendDisconnected);
  const selected = analysis.selectedExperiment;
  const team = teamProfiles.find((profile) => profile.team_id === selected.team_id) || teamProfiles[0];
  const experiments = analysis.experiments;

  const failedCount = experiments.filter((experiment) => experiment.outcome === "failure").length;
  const reviewQueue = experiments.filter(
    (experiment) => experiment.outcome === "unknown" || experiment.failure_category_label.includes("Bias")
  ).length;

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
          {navItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button className={index === 0 ? "nav-item active" : "nav-item"} key={item.label}>
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
            Backend disconnected: showing local mock preview.
          </section>
        )}

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
                  <button className="secondary-button" type="button">
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

            <ExperimentTable
              experiments={experiments}
              selectedId={analysis.selectedId}
              onSelect={analysis.setSelectedId}
            />
          </div>

          <aside className="detail-rail">
            <ConfidenceMeter score={analysis.confidence} requiresReview={analysis.requiresReview} />

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
          </aside>
        </section>

        <section className="lower-grid">
          <ReasoningPanel steps={visibleSteps} />
          <EvidenceTable experiment={selected} />
          <KnowledgeSearch />
        </section>

        {analysis.demoReport && (
          <section className="panel demo-summary" aria-label="Judge demo report">
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
      </main>
    </div>
  );
}
