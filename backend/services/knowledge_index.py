from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from backend.models.enums import RetrievalMode
from backend.models.schemas import KnowledgeHit

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9-]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


@dataclass
class KnowledgeChunk:
    source_file: str
    section_title: str
    text: str
    tokens: Counter[str]


class KnowledgeIndex:
    def __init__(self, docs_dir: Path) -> None:
        self.docs_dir = docs_dir
        self.chunks: list[KnowledgeChunk] = []
        self.document_frequency: Counter[str] = Counter()
        self._load()

    def _load(self) -> None:
        self.chunks.clear()
        scan_dirs = []
        if self.docs_dir.exists():
            scan_dirs.append(self.docs_dir)
        
        iq_sources_dir = self.docs_dir.parent / "foundry_iq_sources"
        if iq_sources_dir.exists() and iq_sources_dir != self.docs_dir:
            scan_dirs.append(iq_sources_dir)

        for directory in scan_dirs:
            for path in sorted(directory.glob("*.md")):
                text = path.read_text(encoding="utf-8")
                sections = re.split(r"(?m)^##\s+", text)
                if len(sections) == 1:
                    title = path.stem.replace("_", " ").title()
                    lines = text.splitlines()
                    clean_lines = []
                    in_content = False
                    for line in lines:
                        if not in_content and ":" in line:
                            key, _ = line.split(":", 1)
                            if key.strip().lower() in {"id", "citation", "agent_usage_notes", "title", "source_type", "permission_scope", "citation_id", "tags", "relevance_tags", "content", "example_evidence"}:
                                continue
                        in_content = True
                        clean_lines.append(line)
                    content_body = "\n".join(clean_lines).strip()
                    if content_body.startswith("content:") or content_body.startswith("content: |"):
                        content_body = content_body.split(":", 1)[1].strip()
                        if content_body.startswith("|"):
                            content_body = content_body[1:].strip()
                    clean = content_body.strip()
                    if not clean:
                        continue
                    tokens = Counter(tokenize(f"{title} {clean}"))
                    chunk = KnowledgeChunk(path.name, title, clean, tokens)
                    self.chunks.append(chunk)
                    self.document_frequency.update(set(tokens))
                else:
                    for section in sections[1:]:
                        title, _, body = section.partition("\n")
                        clean = body.strip()
                        if not clean:
                            continue
                        tokens = Counter(tokenize(f"{title} {clean}"))
                        chunk = KnowledgeChunk(path.name, title.strip(), clean, tokens)
                        self.chunks.append(chunk)
                        self.document_frequency.update(set(tokens))

    def _score(self, query_tokens: Counter[str], chunk: KnowledgeChunk) -> tuple[float, list[str]]:
        if not query_tokens or not chunk.tokens:
            return 0.0, []
        total_chunks = max(len(self.chunks), 1)
        matched = sorted(set(query_tokens).intersection(chunk.tokens))
        weighted = 0.0
        query_norm = 0.0
        chunk_norm = 0.0
        for term in set(query_tokens).union(chunk.tokens):
            idf = math.log((1 + total_chunks) / (1 + self.document_frequency.get(term, 0))) + 1
            q = query_tokens.get(term, 0) * idf
            c = chunk.tokens.get(term, 0) * idf
            weighted += q * c
            query_norm += q * q
            chunk_norm += c * c
        cosine = weighted / (math.sqrt(query_norm) * math.sqrt(chunk_norm)) if query_norm and chunk_norm else 0.0
        # A small matched-term boost helps short certification queries rank intuitively.
        boost = min(len(matched) / max(len(query_tokens), 1), 1.0) * 0.25
        return min(cosine + boost, 1.0), matched[:12]

    def search(self, query: str, top_k: int = 3, cert_filter: str | None = None) -> list[KnowledgeHit]:
        query_tokens = Counter(tokenize(query))
        scored: list[tuple[float, KnowledgeChunk, list[str]]] = []
        for chunk in self.chunks:
            if cert_filter and cert_filter.lower().replace("-", "") not in chunk.source_file.lower().replace("-", ""):
                continue
            score, matched = self._score(query_tokens, chunk)
            if score > 0:
                scored.append((score, chunk, matched))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            KnowledgeHit(
                source_file=chunk.source_file,
                section_title=chunk.section_title,
                relevance_score=round(score, 4),
                excerpt=chunk.text[:400],
                matched_terms=matched,
                citation=f"{chunk.source_file} § {chunk.section_title}",
                retrieval_mode=RetrievalMode.LOCAL,
            )
            for score, chunk, matched in scored[:top_k]
        ]

    def sources(self) -> list[dict[str, object]]:
        grouped: dict[str, list[str]] = {}
        for chunk in self.chunks:
            grouped.setdefault(chunk.source_file, []).append(chunk.section_title)
        return [{"source_file": source, "sections": sections} for source, sections in sorted(grouped.items())]
