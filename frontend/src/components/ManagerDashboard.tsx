import { BarChart3, BookOpen, BrainCircuit, DatabaseZap, FileWarning, Gauge, LayoutDashboard, ShieldAlert, Users } from "lucide-react";
import { AgentFlowGraph } from "./AgentFlowGraph";
import { ConflictResolutionPanel } from "./ConflictResolutionPanel";
import { DemoCommandPanel } from "./DemoCommandPanel";
import { EvidenceTable } from "./EvidenceTable";
import { ExperimentTable } from "./ExperimentTable";
import { FailureMetricChart } from "./FailureMetricChart";
import { FailureTrendChart } from "./FailureTrendChart";
import { FoundryIQLayerDiagram } from "./FoundryIQLayerDiagram";
import { IQEvidenceTrail } from "./IQEvidenceTrail";
import { IQGroundingPanel } from "./IQGroundingPanel";
import { KnowledgeSearch } from "./KnowledgeSearch";
import { MetricsCards } from "./MetricsCards";
import { MicrosoftIQProofPanel } from "./MicrosoftIQProofPanel";
import { ReasoningTimeline } from "./ReasoningTimeline";
import { Toast } from "./Toast";
import { VideoDemoBanner } from "./VideoDemoBanner";
import { teamProfiles } from "../data/mockData";
import { useAnalysis } from "../hooks/useAnalysis";
import { useSSEStream } from "../hooks/useSSEStream";
import { PromptAnalysisPanel } from "./PromptAnalysisPanel";
import { InteractiveReportDownload } from "./InteractiveReportDownload";

const navItems = [
  { label: "Analysis", icon: LayoutDashboard },
  { label: "Experiments", icon: DatabaseZap },
  { label: "Manager", icon: Users },
  { label: "Knowledge", icon: BookOpen }
];

const agentProof = [
  ["Planner", "Plans evidence checks"],
  ["Classifier", "Classifies failure mode"],
  ["Root cause", "Explains violated assumption"],
  ["Historian", "Finds repeat patterns"],
  ["Coach", "Builds remediation"],
  ["Certification", "Maps Microsoft skills"],
  ["Integration", "Packages leadership view"],
  ["Microsoft IQ", "Shows honest Foundry proof"]
];

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function firstPlanItem(value: unknown, fallback: string) {
  if (Array.isArray(value) && value.length) return String(value[0]);
  if (typeof value === "string" && value) return value;
  return fallback;
}

export function ManagerDashboard({
  activeTab = "Analysis",
  onTabChange
}: {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}) {
  const analysis = useAnalysis("EXP-1001");
  const visibleSteps = useSSEStream(analysis.isRunning || analysis.isDemoRunning, analysis.selectedId, analysis.backendDisconnected);
  const selected = analysis.selectedExperiment;
  const team = teamProfiles.find((profile) => profile.team_id === selected.team_id) || teamProfiles[0];
  const experiments = analysis.experiments;
  const report = analysis.demoReport;

  const failedCount = experiments.filter((experiment) => experiment.outcome === "failure").length;
  const reviewQueue = experiments.filter(
    (experiment) => experiment.outcome === "unknown" || (experiment.failure_category_label || "").includes("Bias")
  ).length;

  const changeTab = (label: string) => {
    if (onTabChange) onTabChange(label);
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
              <button className={isActive ? "nav-item active" : "nav-item"} key={item.label} onClick={() => changeTab(item.label)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-card">
          <p>Retrieval mode</p>
          <strong>{analysis.iqStatus?.proof_level || "local_demo_fallback"}</strong>
          <span>{report?.video_demo_summary?.reasoning_steps || 20} reasoning steps ready</span>
        </div>
      </aside>

      <main className="workspace">
        <VideoDemoBanner />

        <header className="demo-hero">
          <div className="demo-hero-copy">
            <div className={analysis.backendDisconnected ? "backend-mode-badge mock" : "backend-mode-badge"}>
              {analysis.backendDisconnected ? "Mock preview only" : "Live backend demo"}
            </div>
            <h1>FailureLens IQ</h1>
            <p>Turns failed ML experiments into learning intelligence</p>
            <strong>{report?.ui_summary?.judge_hook || "This is not just a classifier; it is a learning memory system."}</strong>
          </div>

          <DemoCommandPanel
            isRunning={analysis.isRunning}
            isDemoRunning={analysis.isDemoRunning}
            onHealth={analysis.checkBackendHealth}
            onReadiness={analysis.checkAzureReadiness}
            onCost={analysis.checkCostEstimate}
            onCopySummary={analysis.copyDemoSummary}
            onCopyIQ={analysis.copyIqComplianceSummary}
            onDownload={analysis.downloadReport}
            onJudgeDemo={analysis.runJudgeDemo}
            onRunAnalysis={analysis.runAnalysis}
            onResetDemo={analysis.resetDemo}
          />
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
              <strong>{experiments.filter((experiment) => (experiment.failure_category_label || "").includes("Bias")).length}</strong>
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
        <Toast message={analysis.statusMessage && !analysis.backendDisconnected && !analysis.authRequired ? analysis.statusMessage : ""} />

        {activeTab === "Analysis" && (
          analysis.isEmpty ? (
            <div className="flex flex-col items-center gap-6 py-10 w-full max-w-4xl mx-auto">
              <div className="text-center max-w-2xl px-4 mb-4">
                <h2 className="text-xl font-bold mb-2 text-white">No analysis yet</h2>
                <p className="text-gray-400 text-sm">
                  Start by describing a failed ML experiment. FailureLens IQ will generate the experiment record, run reasoning agents, retrieve grounded evidence, and create a downloadable report.
                </p>
              </div>
              <PromptAnalysisPanel
                onGenerate={analysis.generateAnalysis}
                isGenerating={analysis.isGenerating}
                error={analysis.error}
              />
            </div>
          ) : (
            <>
              {/* Active Prompt Analysis Panel and Download Buttons */}
              <div className="mb-6 flex flex-col md:flex-row gap-6 items-center justify-between bg-[#071226]/40 p-5 border border-[#1e2d42] rounded-xl backdrop-blur-md w-full max-w-5xl mx-auto">
                <div className="flex-1 w-full">
                  <h3 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">Active Prompt Analysis</h3>
                  <p className="text-sm italic text-gray-200">"{analysis.prompt}"</p>
                </div>
                <div className="flex justify-end w-full md:w-auto">
                  <InteractiveReportDownload
                    downloadUrl={analysis.interactiveReport?.download_url || null}
                    isEnabled={!!analysis.interactiveReport}
                  />
                </div>
              </div>

              <section className="failure-snapshot-grid" aria-label="Failure snapshot">
                <div className="mission-left">
                  <section className="panel diagnosis-panel">
                    <div className="diagnosis-header">
                      <div>
                        <p className="eyebrow">Failure Snapshot</p>
                        <h2>
                          {selected.experiment_id} - {selected.failure_category_label}
                        </h2>
                      </div>
                      <span className="category-band">{selected.pipeline_stage}</span>
                    </div>
                    <h3>{selected.failure_observation}</h3>
                    <p>
                      The system links this failure to {selected.validation_strategy} evidence, baseline comparison, and team learning context for {team.team_name}.
                    </p>
                    <div className="snapshot-callout">
                      {report?.ui_summary?.main_takeaway || "EXP-1001 failed because aggregate accuracy hid class-level failure."}
                    </div>
                  </section>
                  <MetricsCards experiment={selected} />
                </div>

                <FailureMetricChart experiment={selected} metricStory={report?.metric_story} />
                <FailureTrendChart experiment={selected} />
              </section>

              <AgentFlowGraph events={visibleSteps as any[]} demoReport={report} isAnimating={analysis.isDemoRunning || analysis.isRunning} />

              <ConflictResolutionPanel demoReport={report as any} />

              <IQGroundingPanel demoReport={report} />

              <section className="lower-grid-analysis">
                <ReasoningTimeline steps={(report?.reasoning_timeline || report?.agent_workflow || visibleSteps) as any[]} />
                <EvidenceTable experiment={selected} />
              </section>

              <MicrosoftIQProofPanel
                iqStatus={analysis.iqStatus}
                readiness={analysis.readiness}
                demoReport={report}
                onCopy={analysis.copyIqComplianceSummary}
              />
              <section className="panel foundry-iq-explainer">
                <FoundryIQLayerDiagram mode={report?.foundry_iq_layer?.label || analysis.iqStatus?.foundry_iq_label} />
                <IQEvidenceTrail demoReport={report} />
              </section>

              <section className="demo-proof-grid" aria-label="Judge demo proof points">
                <section className="panel">
                  <div className="panel-title-row">
                    <div>
                      <p className="eyebrow">Remediation + Certification</p>
                      <h2>3-day fix, 7-day learning plan, Microsoft skill mapping</h2>
                    </div>
                  </div>
                  <div className="remediation-plan-grid">
                    <article>
                      <span>3-day plan</span>
                      <p>{firstPlanItem(report?.remediation_plan?.three_day_plan, "Add slice metrics, stratified validation, and review minority-class failure evidence.")}</p>
                    </article>
                    <article>
                      <span>7-day plan</span>
                      <p>{firstPlanItem(report?.remediation_plan?.seven_day_plan, "Convert the failed run into a reusable evaluation checklist and team learning exercise.")}</p>
                    </article>
                    <article>
                      <span>Microsoft mapping</span>
                      <p>
                        {report?.certification_readiness?.mapping?.cert_code || "DP-100"} -{" "}
                        {report?.certification_readiness?.mapping?.skill_domain || "Evaluate and monitor models"}
                      </p>
                    </article>
                  </div>
                  <div className="agent-card-grid">
                    {agentProof.map(([agent, detail], index) => (
                      <article className="agent-mini-card" key={agent}>
                        <span>{index + 1}</span>
                        <strong>{agent}</strong>
                        <p>{detail}</p>
                      </article>
                    ))}
                  </div>
                </section>

                <section className="panel manager-summary-panel">
                  <div className="panel-title-row">
                    <div>
                      <p className="eyebrow">Manager Summary</p>
                      <h2>{team.team_name} action view</h2>
                    </div>
                  </div>
                  <dl className="manager-list">
                    <div>
                      <dt>Business risk</dt>
                      <dd>{report?.ui_summary?.business_value || "Repeat evaluation failures stay invisible."}</dd>
                    </div>
                    <div>
                      <dt>Team learning gap</dt>
                      <dd>{report?.historical_memory?.team_learning_gap || "Class-level evaluation review needs reinforcement."}</dd>
                    </div>
                    <div>
                      <dt>Next action</dt>
                      <dd>{report?.ui_summary?.next_best_action || "Assign remediation and preserve the trace."}</dd>
                    </div>
                    <div>
                      <dt>Sprint load</dt>
                      <dd>{team.sprint_load}</dd>
                    </div>
                  </dl>
                </section>
              </section>

              {analysis.costEstimate && (
                <section className="panel cost-guard-panel">
                  <div className="panel-title-row">
                    <div>
                      <p className="eyebrow">Cost guard</p>
                      <h2>Demo usage limits</h2>
                    </div>
                  </div>
                  <p className="manager-note">
                    Cost guard: max {(analysis.costEstimate as any).azure_openai?.max_tokens_per_demo || 500} tokens per demo; Search top-k capped at{" "}
                    {(analysis.costEstimate as any).limits?.max_search_top_k || 5}.
                  </p>
                </section>
              )}
            </>
          )
        )}

        {activeTab === "Experiments" && (
          <section className="dashboard-grid">
            <div className="primary-column">
              <ExperimentTable experiments={experiments} selectedId={analysis.selectedId} onSelect={analysis.setSelectedId} />
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
                  Responsible AI risk is highest for TEAM-B. Convert repeated failure categories into sprint-level review tasks and cert-aligned practice.
                </p>
              </section>
            </div>
          </section>
        )}

        {activeTab === "Knowledge" && (
          <section className="lower-grid knowledge-grid">
            <KnowledgeSearch />
          </section>
        )}
      </main>
    </div>
  );
}
