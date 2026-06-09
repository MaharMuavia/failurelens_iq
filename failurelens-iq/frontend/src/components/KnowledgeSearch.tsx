import { Search, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { knowledgeHits } from "../data/mockData";

export function KnowledgeSearch() {
  const [query, setQuery] = useState("minority f1 validation");
  const hits = useMemo(() => {
    const needle = query.toLowerCase();
    const filtered = knowledgeHits.filter((hit) => `${hit.section_title} ${hit.excerpt}`.toLowerCase().includes(needle));
    return filtered.length ? filtered : knowledgeHits;
  }, [query]);

  return (
    <section className="panel knowledge-panel" aria-label="Knowledge search">
      <div className="panel-title-row">
        <div>
          <p className="eyebrow">Knowledge</p>
          <h2>Local IQ retrieval</h2>
        </div>
        <span className="icon-chip neutral">
          <Sparkles size={18} />
        </span>
      </div>

      <label className="knowledge-input">
        <Search size={16} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="Knowledge query" />
      </label>

      <div className="knowledge-results">
        {hits.map((hit) => (
          <article className="knowledge-hit" key={hit.citation}>
            <div>
              <strong>{hit.section_title}</strong>
              <span>{Math.round(hit.relevance_score * 100)}%</span>
            </div>
            <p>{hit.excerpt}</p>
            <small>{hit.citation}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
