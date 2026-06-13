import { BrainCircuit, Clipboard, Download, Gauge, HeartPulse, Play, RotateCcw, ShieldAlert, SlidersHorizontal } from "lucide-react";

type DemoCommandPanelProps = {
  isRunning: boolean;
  isDemoRunning: boolean;
  onHealth: () => void;
  onReadiness: () => void;
  onCost: () => void;
  onCopySummary: () => void;
  onCopyIQ: () => void;
  onDownload: () => void;
  onJudgeDemo: () => void;
  onRunAnalysis: () => void;
  onResetDemo: () => void;
};

export function DemoCommandPanel({
  isRunning,
  isDemoRunning,
  onHealth,
  onReadiness,
  onCost,
  onCopySummary,
  onCopyIQ,
  onDownload,
  onJudgeDemo,
  onRunAnalysis,
  onResetDemo
}: DemoCommandPanelProps) {
  return (
    <section className="demo-command-panel" aria-label="Demo command panel">
      <button className="reset-demo-button" type="button" onClick={onResetDemo}>
        <RotateCcw size={15} />
        Reset Demo
      </button>
      <div className="judge-demo-action">
        <button className="primary-button command-primary" type="button" onClick={onJudgeDemo}>
          <BrainCircuit size={18} />
          {isDemoRunning ? "Running Sample Demo" : "Run Sample Demo"}
        </button>
        <p>Runs the complete multi-agent workflow and prepares the judge-ready report.</p>
      </div>

      <details className="advanced-checks">
        <summary>
          <SlidersHorizontal size={16} />
          Advanced checks
        </summary>
        <div className="advanced-check-grid">
          <button className="secondary-button" type="button" onClick={onHealth}>
            <HeartPulse size={16} />
            Health
          </button>
          <button className="secondary-button" type="button" onClick={onReadiness}>
            <ShieldAlert size={16} />
            Readiness
          </button>
          <button className="secondary-button" type="button" onClick={onCost}>
            <Gauge size={16} />
            Cost
          </button>
          <button className="secondary-button" type="button" onClick={onCopySummary}>
            <Clipboard size={16} />
            Copy summary
          </button>
          <button className="secondary-button" type="button" onClick={onCopyIQ}>
            <Clipboard size={16} />
            Copy IQ
          </button>
          <button className="secondary-button" type="button" onClick={onDownload}>
            <Download size={16} />
            Report
          </button>
          <button className="secondary-button" type="button" onClick={onRunAnalysis}>
            <Play size={16} />
            {isRunning ? "Running analysis" : "Run analysis"}
          </button>
        </div>
      </details>
    </section>
  );
}
