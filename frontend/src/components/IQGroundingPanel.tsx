import { BookOpenCheck, ChevronDown } from "lucide-react";

type IQGroundingPanelProps = {
  demoReport?: any | null;
};

function percent(value: unknown) {
  const numeric = typeof value === "number" ? value : Number(value || 0);
  return `${Math.round((numeric <= 1 ? numeric * 100 : numeric) || 0)}%`;
}

function sourceRows(demoReport?: any | null) {
  const citations = demoReport?.iq_grounding_story?.citations || demoReport?.iq_grounding_story?.retrieved_evidence || [];
  return citations.slice(0, 5).map((item: any, index: number) => ({
    id: item.id || item.citation_id || `${item.citation || "source"}-${index}`,
    document: item.citation || item.source || item.source_file || item.title || "Foundry IQ source",
    section: item.title || item.section_heading || item.source_type || "Grounded evidence",
    score: Number(item.relevance_score || item.grounding_confidence || 0),
    excerpt: item.excerpt || "Grounded evidence was retrieved for this reasoning step.",
    matchedTerms: item.matched_terms || [],
  }));
}

export function IQGroundingPanel({ demoReport }: IQGroundingPanelProps) {
  const metrics = demoReport?.iq_integration || {};
  const rows = sourceRows(demoReport);

  return (
    <section className="iq-grounding-panel" aria-label="Microsoft Foundry IQ grounding">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Microsoft Foundry IQ</p>
          <h2>Grounding proof</h2>
        </div>
        <span className="iq-grounding-icon">
          <BookOpenCheck size={18} />
        </span>
      </div>

      <div className="iq-metric-grid">
        <article>
          <span>Knowledge sources</span>
          <strong>{metrics.knowledge_sources_count ?? 6}</strong>
        </article>
        <article>
          <span>Total retrievals</span>
          <strong>{metrics.total_retrievals ?? 0}</strong>
        </article>
        <article>
          <span>Avg confidence</span>
          <strong>{percent(metrics.avg_grounding_confidence)}</strong>
        </article>
        <article>
          <span>Coverage</span>
          <strong>{percent(metrics.grounding_coverage)}</strong>
        </article>
      </div>

      <div className="iq-source-list">
        {rows.map((row: any) => (
          <details key={row.id} className="iq-source-row">
            <summary>
              <div>
                <strong>{row.document}</strong>
                <span>{row.section}</span>
              </div>
              <ChevronDown size={16} />
            </summary>
            <div className="iq-source-score" aria-label={`Relevance ${percent(row.score)}`}>
              <span style={{ width: percent(row.score) }} />
            </div>
            <p>
              {row.excerpt}
              {row.matchedTerms.length > 0 && <mark> {row.matchedTerms.slice(0, 4).join(", ")}</mark>}
            </p>
          </details>
        ))}
      </div>
    </section>
  );
}
