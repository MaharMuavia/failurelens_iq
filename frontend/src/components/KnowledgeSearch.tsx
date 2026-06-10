import { Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { knowledgeHits } from "../data/mockData";
import { searchKnowledge } from "../api/client";

export function KnowledgeSearch() {
  const [query, setQuery] = useState("minority f1 validation");
  const [hits, setHits] = useState(knowledgeHits);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      searchKnowledge(query).then((result) => setHits((result.data as any).hits || knowledgeHits));
    }, 250);
    return () => window.clearTimeout(timeout);
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
