import { AlertTriangle, CheckCircle2, Clipboard, Info, ShieldAlert } from "lucide-react";

type MicrosoftIQProofPanelProps = {
  iqStatus?: any | null;
  readiness?: any | null;
  demoReport?: any | null;
  onCopy: () => void;
};

function valueOrFallback(value: unknown, fallback: string) {
  return value === undefined || value === null || value === "" ? fallback : String(value);
}

function getBadge(status: string, proofLevel: string) {
  if (status === "live_iq_verified" || proofLevel === "live_azure") {
    return { label: "Live Azure IQ Verified", className: "iq-badge live", icon: CheckCircle2 };
  }
  if (status === "needs_azure_configuration") {
    return { label: "Needs Azure Configuration", className: "iq-badge danger", icon: ShieldAlert };
  }
  return { label: "Local Demo Fallback", className: "iq-badge fallback", icon: AlertTriangle };
}

export function MicrosoftIQProofPanel({ iqStatus, readiness, demoReport, onCopy }: MicrosoftIQProofPanelProps) {
  const compliance = demoReport?.microsoft_iq_compliance || {};
  const grounding = demoReport?.grounding_summary || {};
  const liveServices = iqStatus?.live_services || {};
  const sourceTypes = compliance.source_types || grounding.source_types || ["local_demo_grounding"];
  const citationsCount = grounding.citations_count ?? grounding.citations?.length ?? (compliance.citations_present ? 1 : 0);
  const proofLevel = valueOrFallback(iqStatus?.proof_level || compliance.proof_level, "local_demo_fallback");
  const complianceStatus = valueOrFallback(
    iqStatus?.compliance_status || compliance.compliance_status,
    readiness?.status === "needs_configuration" ? "needs_azure_configuration" : "ready_for_demo"
  );
  const badge = getBadge(complianceStatus, proofLevel);
  const BadgeIcon = badge.icon;

  return (
    <section className="panel microsoft-iq-panel" aria-label="Microsoft IQ proof panel">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Microsoft IQ / Foundry Proof</p>
          <h2>Foundry IQ grounded retrieval proof</h2>
        </div>
        <span className={badge.className}>
          <BadgeIcon size={15} />
          {badge.label}
        </span>
      </div>

      <dl className="manager-list">
        <div>
          <dt>Selected IQ Layer</dt>
          <dd>{valueOrFallback(iqStatus?.selected_iq_layer || compliance.selected_iq_layer || compliance.required_iq_layer, "Foundry IQ")}</dd>
        </div>
        <div>
          <dt>Active Provider</dt>
          <dd>{valueOrFallback(iqStatus?.active_provider || compliance.active_provider || demoReport?.azure_status?.active_provider, "LocalIQProvider")}</dd>
        </div>
        <div>
          <dt>Proof Level</dt>
          <dd>{proofLevel}</dd>
        </div>
        <div>
          <dt>Azure AI Search</dt>
          <dd>{liveServices.azure_ai_search || demoReport?.azure_status?.azure_ai_search_used || readiness?.checks?.azure_ai_search_configured ? "Enabled" : "Disabled"}</dd>
        </div>
        <div>
          <dt>Azure OpenAI</dt>
          <dd>{liveServices.azure_openai || demoReport?.azure_status?.azure_openai_used || readiness?.checks?.azure_openai_configured ? "Enabled" : "Disabled"}</dd>
        </div>
        <div>
          <dt>Source Types</dt>
          <dd>{sourceTypes.join(", ")}</dd>
        </div>
        <div>
          <dt>Citations Count</dt>
          <dd>{citationsCount}</dd>
        </div>
        <div>
          <dt>Compliance Status</dt>
          <dd>{complianceStatus}</dd>
        </div>
      </dl>

      <div className="iq-explanation">
        <Info size={16} />
        <p>{valueOrFallback(iqStatus?.honest_limitation || compliance.honest_limitation, "Demo mode uses local grounding; Azure AI Search is not live.")}</p>
      </div>
      <p className="manager-note">
        {valueOrFallback(
          iqStatus?.judge_explanation || compliance.judge_explanation,
          "FailureLens IQ implements Foundry IQ using grounded retrieval for reasoning agents."
        )}
      </p>

      <button className="secondary-button iq-copy-button" type="button" onClick={onCopy}>
        <Clipboard size={16} />
        Copy IQ Compliance Summary
      </button>
    </section>
  );
}
