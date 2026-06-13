type IQEvidenceTrailProps = {
  demoReport?: any | null;
};

const agentBySource: Record<string, string> = {
  failure_taxonomy: "Classifier",
  experiment_history: "Root cause analyzer",
  remediation_playbook: "Prescriptive Coach",
  microsoft_certification_mapping: "Certification evaluator",
  responsible_ai_checklist: "Confidence gate",
  manager_governance: "Integration Manager"
};

export function IQEvidenceTrail({ demoReport }: IQEvidenceTrailProps) {
  const citations = demoReport?.iq_grounding_story?.citations || demoReport?.foundry_iq_layer?.citations || [];
  const visible = citations.slice(0, 5);

  if (!visible.length) {
    return null;
  }

  return (
    <section className="iq-evidence-trail" aria-label="Foundry IQ evidence trail">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">IQ Evidence Trail</p>
          <h2>Citations used by the reasoning agents</h2>
        </div>
      </div>
      <div className="iq-evidence-list">
        {visible.map((item: any) => (
          <article key={item.id || item.citation} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong style={{ fontSize: '12px', color: '#0f172a' }}>{item.id || "citation"}</strong>
              <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', background: '#f1f5f9', color: '#475569', fontWeight: 'bold' }}>
                {agentBySource[item.source_type] || "Reasoning Agent"}
              </span>
            </div>
            <p style={{ fontSize: '12px', color: '#334155', flexGrow: 1, lineBreak: 'anywhere' }}>{item.excerpt}</p>
            <footer style={{ display: 'flex', flexDirection: 'column', gap: '4px', borderTop: '1px solid #e2e8f0', paddingTop: '6px', marginTop: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#64748b' }}>
                <span>Type: {item.source_type}</span>
                <span>Scope: {item.permission_scope || "demo"}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#6d28d9', fontWeight: 'bold' }}>
                <span>{Math.round((item.relevance_score || 0) * 100)}% relevance</span>
              </div>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}
