from __future__ import annotations

import sys
import hashlib
import json
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import httpx

from azure_env import ROOT, env, require_search_env


SOURCES = [
    "knowledge/foundry_docs/ml_failure_taxonomy.md",
    "knowledge/foundry_docs/remediation_playbook.md",
    "knowledge/foundry_docs/dp100_skill_guide.md",
    "knowledge/foundry_docs/ai102_skill_guide.md",
    "knowledge/foundry_docs/pl300_skill_guide.md",
    "knowledge/foundry_docs/dp203_skill_guide.md",
    "data/synthetic/ml_experiment_logs.json",
    "data/synthetic/team_profiles.json",
    "data/synthetic/work_context.json",
    "data/ontology/semantic_model.json",
    "knowledge/foundry_iq_sources/failure_taxonomy.md",
    "knowledge/foundry_iq_sources/experiment_history.json",
    "knowledge/foundry_iq_sources/remediation_playbooks.md",
    "knowledge/foundry_iq_sources/microsoft_certification_mapping.md",
    "knowledge/foundry_iq_sources/responsible_ai_checklist.md",
    "knowledge/foundry_iq_sources/manager_governance.md",
]


def stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def chunk_text(text: str, size: int) -> list[str]:
    chunks: list[str] = []
    cursor = 0
    while cursor < len(text):
        chunks.append(text[cursor : cursor + size])
        cursor += size
    return chunks


def markdown_docs(path: Path, max_chunk_chars: int) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    content_lines = []
    in_content = False
    for line in text.splitlines():
        if not in_content and ":" in line:
            key, val = line.split(":", 1)
            norm_key = key.strip().lower().replace(" ", "_")
            if norm_key in {"id", "citation", "agent_usage_notes", "title", "source_type", "permission_scope", "citation_id", "tags", "relevance_tags", "content", "example_evidence"}:
                metadata[norm_key] = val.strip()
                continue
        in_content = True
        content_lines.append(line)
        
    content_body = "\n".join(content_lines).strip()
    if content_body.startswith("content:") or content_body.startswith("content: |"):
        content_body = content_body.split(":", 1)[1].strip()
        if content_body.startswith("|"):
            content_body = content_body[1:].strip()
            
    tags_str = metadata.get("tags") or metadata.get("relevance_tags") or ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
    if not tags:
        tags = [path.stem.replace("_", "-")]
        
    permission_scope = metadata.get("permission_scope") or "demo"
    source_type = metadata.get("source_type") or "knowledge_markdown"
    title = metadata.get("title") or path.stem.replace("_", " ").title()
    citation_base = metadata.get("citation") or metadata.get("id") or path.relative_to(ROOT).as_posix()
    
    docs = []
    for idx, chunk in enumerate(chunk_text(content_body, max_chunk_chars), start=1):
        rel = path.relative_to(ROOT).as_posix()
        docs.append(
            {
                "id": stable_id(f"{rel}:{idx}"),
                "title": title,
                "content": chunk,
                "source_type": source_type,
                "source_id": rel,
                "citation": f"{citation_base}#chunk-{idx}" if "#" not in citation_base else f"{citation_base}-chunk-{idx}",
                "url": "",
                "chunk_id": f"{path.stem}-{idx}",
                "experiment_id": "",
                "skill_domain": path.stem.split("_")[0].upper() if "guide" in path.stem else "",
                "failure_category": "",
                "permission_scope": permission_scope,
                "tags": tags,
            }
        )
    return docs


def json_docs(path: Path, max_chunk_chars: int) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    records = raw if isinstance(raw, list) else raw.get("items", raw.get("experiments", [raw])) if isinstance(raw, dict) else []
    docs = []
    rel = path.relative_to(ROOT).as_posix()
    for idx, record in enumerate(records, start=1):
        content = json.dumps(record, ensure_ascii=False)[:max_chunk_chars]
        experiment_id = str(record.get("experiment_id", "") or record.get("id", "")) if isinstance(record, dict) else ""
        failure_category = str(record.get("failure_category_label", "") or record.get("failure_category", "")) if isinstance(record, dict) else ""
        permission_scope = str(record.get("permission_scope", "demo")) if isinstance(record, dict) else "demo"
        source_type = str(record.get("source_type", "experiment_json")) if isinstance(record, dict) else "experiment_json"
        title = str(record.get("title", "")) if isinstance(record, dict) else ""
        citation = str(record.get("citation", "")) if isinstance(record, dict) else ""
        tags = record.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
            
        docs.append(
            {
                "id": stable_id(f"{rel}:{idx}:{experiment_id}"),
                "title": title or experiment_id or f"{path.stem} record {idx}",
                "content": content,
                "source_type": source_type,
                "source_id": rel,
                "citation": citation or f"{rel}#{experiment_id or idx}",
                "url": "",
                "chunk_id": f"{path.stem}-{idx}",
                "experiment_id": experiment_id,
                "skill_domain": "",
                "failure_category": failure_category,
                "permission_scope": permission_scope,
                "tags": tags,
            }
        )
    return docs


def build_documents() -> list[dict[str, str]]:
    max_docs = int(env("AZURE_MAX_DOCS_TO_INDEX", "200"))
    max_chunk_chars = int(env("AZURE_MAX_CHUNK_CHARS", "1800"))
    documents: list[dict[str, str]] = []
    for source in SOURCES:
        path = ROOT / source
        if not path.exists():
            continue
        documents.extend(markdown_docs(path, max_chunk_chars) if path.suffix == ".md" else json_docs(path, max_chunk_chars))
    return documents[:max_docs]


def main() -> int:
    endpoint, key, index = require_search_env()
    documents = build_documents()
    print(f"Uploading {len(documents)} documents to Azure AI Search index {index}")
    url = f"{endpoint}/indexes/{index}/docs/index?api-version=2023-11-01"
    payload = {"value": [{"@search.action": "mergeOrUpload", **doc} for doc in documents]}
    response = httpx.post(url, headers={"api-key": key, "Content-Type": "application/json"}, json=payload, timeout=60)
    if response.status_code >= 400:
        print(response.text)
        return 1
    print("Seed complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
