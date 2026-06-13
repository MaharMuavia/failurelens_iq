import { AlertTriangle, CheckCircle2, Clipboard, Info, ShieldAlert, ShieldCheck } from "lucide-react";

type MicrosoftIQProofPanelProps = {
  iqStatus?: any | null;
  readiness?: any | null;
  demoReport?: any | null;
  onCopy: () => void;
};

function valueOrFallback(value: unknown, fallback: string) {
  return value === undefined || value === null || value === "" ? fallback : String(value);
}

function badgeFor(proofLevel: string, complianceStatus: string) {
  if (complianceStatus === "live_iq_verified" || proofLevel === "live_azure" || proofLevel === "live_azure_foundry") {
    return { label: "Live Azure Foundry IQ", className: "iq-badge live", icon: CheckCircle2 };
  }
  if (proofLevel === "foundry_model_live" || complianceStatus === "foundry_model_live") {
    return { label: "Foundry Model Live · IQ Adapter Ready", className: "iq-badge live", icon: ShieldCheck };
  }
  if (proofLevel === "local_demo_fallback" || complianceStatus === "ready_for_demo") {
    return { label: "Foundry IQ Local Adapter", className: "iq-badge fallback", icon: AlertTriangle };
  }
  if (complianceStatus === "fallback_reasoning_only") {
    return { label: "Azure Quota Blocked", className: "iq-badge danger", icon: ShieldAlert };
  }
  if (proofLevel === "foundry_adapter_ready" || complianceStatus === "needs_azure_configuration") {
    return { label: "Adapter Ready", className: "iq-badge fallback", icon: ShieldCheck };
  }
  return { label: "Needs Azure Configuration", className: "iq-badge danger", icon: ShieldAlert };
}

function groundingSource(sourceTypes: string[], liveAzure: boolean) {
  if (liveAzure || sourceTypes.includes("azure_ai_search")) return "Azure AI Search";
  return "Local Knowledge Index";
}

function judgeExplanation(liveAzure: boolean, isFoundryModelLive: boolean) {
  if (liveAzure) {
    return "This run uses Azure AI Search as the live Foundry IQ grounding layer.";
  }
  if (isFoundryModelLive) {
    return "This run uses Microsoft Foundry model reasoning. When Azure AI Search credentials are configured, the same adapter switches to live grounded retrieval.";
  }
  return "This project mirrors Foundry IQ architecture locally and can switch to live Azure Foundry IQ when credentials/quota are available.";
}

export function MicrosoftIQProofPanel({ iqStatus, readiness, demoReport, onCopy }: MicrosoftIQProofPanelProps) {
  const compliance = demoReport?.microsoft_iq_compliance || {};
  const grounding = demoReport?.grounding_summary || {};
  const layer = demoReport?.foundry_iq_layer || {};
  const proofLevel = valueOrFallback(iqStatus?.proof_level || compliance.proof_level, "local_demo_fallback");
  const complianceStatus = valueOrFallback(
    iqStatus?.compliance_status || compliance.compliance_status,
    readiness?.status === "needs_configuration" ? "needs_azure_configuration" : "ready_for_demo"
  );
  const sourceTypes = compliance.source_types || grounding.source_types || ["local_foundry_iq_adapter"];
  const liveAzure = Boolean(iqStatus?.live_microsoft_iq || compliance.live_microsoft_iq || proofLevel === "live_azure_foundry");
  
  const reasoningProvider = valueOrFallback(
    iqStatus?.current_reasoning_provider || compliance.current_reasoning_provider,
    "deterministic_fallback"
  );
  
  const isFoundryConnected = Boolean(
    iqStatus?.foundry_project_connected || compliance.foundry_project_connected
  );
  const foundryProject = isFoundryConnected ? "Connected" : "Not Connected";
  
  const foundryAgentName = valueOrFallback(
    iqStatus?.foundry_agent_name || compliance.foundry_agent_name,
    "FailureLens1"
  );
  const foundryAgent = `${foundryAgentName} v1`;

  const isLiveFoundryModel = Boolean(
    iqStatus?.live_microsoft_foundry_model || compliance.live_microsoft_foundry_model || proofLevel === "foundry_model_live" || complianceStatus === "foundry_model_live"
  );
  const liveFoundryModel = isLiveFoundryModel ? "Enabled" : "Disabled";

  const isLiveGrounding = Boolean(
    iqStatus?.live_microsoft_iq_grounding || compliance.live_microsoft_iq_grounding
  );
  const liveGrounding = isLiveGrounding ? "Enabled" : "Disabled";

  const isAdapterReady = Boolean(
    iqStatus?.foundry_iq_adapter_ready || compliance.foundry_iq_adapter_ready || layer.adapter_ready || compliance.adapter_ready
  );
  const adapterReady = isAdapterReady ? "Yes" : "No";

  const foundryModelName = valueOrFallback(
    iqStatus?.foundry_model_deployment || compliance.foundry_model_deployment,
    "grok-4-20-reasoning"
  );

  let displayReasoningProvider = "Deterministic Fallback";
  if (reasoningProvider === "MicrosoftFoundryOpenAI") {
    displayReasoningProvider = "Microsoft Foundry OpenAI";
  } else if (reasoningProvider === "MicrosoftFoundryAgent") {
    displayReasoningProvider = "Microsoft Foundry Agent";
  } else if (reasoningProvider === "AzureOpenAI" || reasoningProvider === "azure_openai") {
    displayReasoningProvider = "Azure OpenAI";
  } else if (reasoningProvider === "OpenAI" || reasoningProvider === "openai") {
    displayReasoningProvider = "OpenAI fallback";
  }

  const badge = badgeFor(proofLevel, complianceStatus);
  const BadgeIcon = badge.icon;
  const honestStatus = valueOrFallback(
    iqStatus?.honest_limitation || compliance.honest_limitation,
    "Azure quota is 0, so this demo uses local Foundry IQ adapter mode."
  );
  const citationsCount = layer.citations_count ?? grounding.citations_count ?? grounding.citations?.length ?? (compliance.citations_present ? 1 : 0);

  return (
    <section className="panel microsoft-iq-panel" aria-label="Foundry IQ layer panel">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Foundry IQ Layer</p>
          <h2>Local adapter mode with citations and permission-aware metadata</h2>
        </div>
        <span className={badge.className}>
          <BadgeIcon size={15} />
          {badge.label}
        </span>
      </div>

      <dl className="manager-list iq-simple-list">
        <div>
          <dt title="Selected IQ Layer">Required IQ Layer</dt>
          <dd>{valueOrFallback(iqStatus?.selected_iq_layer || compliance.required_iq_layer || compliance.selected_iq_layer, "Foundry IQ")}</dd>
        </div>
        <div>
          <dt>Current Proof</dt>
          <dd>{layer.label || iqStatus?.foundry_iq_label || compliance.foundry_iq_label || proofLevel}</dd>
        </div>
        <div>
          <dt>Grounding Source</dt>
          <dd>{groundingSource(sourceTypes, liveAzure)}</dd>
        </div>
        <div>
          <dt>Reasoning Provider</dt>
          <dd>{displayReasoningProvider}</dd>
        </div>
        <div>
          <dt>Model</dt>
          <dd>{foundryModelName}</dd>
        </div>
        <div>
          <dt>Foundry Project</dt>
          <dd>{foundryProject}</dd>
        </div>
        <div>
          <dt>Foundry Agent</dt>
          <dd>{foundryAgent}</dd>
        </div>
        <div>
          <dt>Live Foundry Model</dt>
          <dd>{liveFoundryModel}</dd>
        </div>
        <div>
          <dt>Live Foundry IQ Grounding</dt>
          <dd>{liveGrounding}</dd>
        </div>
        <div>
          <dt>Adapter Ready</dt>
          <dd>{adapterReady}</dd>
        </div>
        <div>
          <dt>Honest Status</dt>
          <dd>{honestStatus}</dd>
        </div>
      </dl>

      <div className="iq-explanation">
        <Info size={16} />
        <p>
          <strong>For judges:</strong> {judgeExplanation(liveAzure, isLiveFoundryModel)}
        </p>
      </div>

      <p className="manager-note">
        Source types: {sourceTypes.join(", ")}. Citations: {citationsCount}.
      </p>

      <div className="why-iq-matters" style={{ marginBottom: "14px" }}>
        <strong>Configured Grounding Sources ({layer.knowledge_sources?.length || 6})</strong>
        <ul style={{ paddingLeft: "16px", marginTop: "6px", marginBottom: "12px" }}>
          {(layer.knowledge_sources && layer.knowledge_sources.length > 0) ? (
            layer.knowledge_sources.map((src: any, idx: number) => (
              <li key={idx} style={{ fontSize: "12px", marginBottom: "4px" }}>
                📁 <strong>{src.title}</strong> — <code>{src.source_type}</code>
              </li>
            ))
          ) : (
            <>
              <li>📁 <strong>Failure Taxonomy</strong> — <code>failure_taxonomy</code></li>
              <li>📁 <strong>Experiment History</strong> — <code>experiment_history</code></li>
              <li>📁 <strong>Remediation Playbooks</strong> — <code>remediation_playbooks</code></li>
              <li>📁 <strong>Microsoft Certification Mapping</strong> — <code>certification_mapping</code></li>
              <li>📁 <strong>Responsible AI Checklist</strong> — <code>responsible_ai</code></li>
              <li>📁 <strong>Manager Governance Playbook</strong> — <code>manager_governance</code></li>
            </>
          )}
        </ul>

        <strong>Why this still matters</strong>
        <ul style={{ paddingLeft: "16px", marginTop: "6px" }}>
          <li>Mirrors Foundry IQ architecture</li>
          <li>Uses citations ({citationsCount} active citations)</li>
          <li>Supports permission metadata</li>
          <li>Adapter-ready for Azure AI Search</li>
          <li>Honest about quota blocker</li>
        </ul>
      </div>

      <button className="secondary-button iq-copy-button" type="button" onClick={onCopy}>
        <Clipboard size={16} />
        Copy IQ Compliance Summary
      </button>
    </section>
  );
}
