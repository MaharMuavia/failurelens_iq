from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

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


def markdown_docs(path: Path, max_chunk_chars: int) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    docs = []
    for idx, chunk in enumerate(chunk_text(text, max_chunk_chars), start=1):
        rel = path.relative_to(ROOT).as_posix()
        docs.append(
            {
                "id": stable_id(f"{rel}:{idx}"),
                "title": path.stem.replace("_", " ").title(),
                "content": chunk,
                "source_type": "knowledge_markdown",
                "source_id": rel,
                "citation": f"{rel}#chunk-{idx}",
                "url": "",
                "chunk_id": f"{path.stem}-{idx}",
                "experiment_id": "",
                "skill_domain": path.stem.split("_")[0].upper() if "guide" in path.stem else "",
                "failure_category": "",
            }
        )
    return docs


def json_docs(path: Path, max_chunk_chars: int) -> list[dict[str, str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    records = raw if isinstance(raw, list) else raw.get("items", raw.get("experiments", [raw])) if isinstance(raw, dict) else []
    docs = []
    rel = path.relative_to(ROOT).as_posix()
    for idx, record in enumerate(records, start=1):
        content = json.dumps(record, ensure_ascii=False)[:max_chunk_chars]
        experiment_id = str(record.get("experiment_id", "")) if isinstance(record, dict) else ""
        failure_category = str(record.get("failure_category_label", "")) if isinstance(record, dict) else ""
        docs.append(
            {
                "id": stable_id(f"{rel}:{idx}:{experiment_id}"),
                "title": experiment_id or f"{path.stem} record {idx}",
                "content": content,
                "source_type": "experiment_json",
                "source_id": rel,
                "citation": f"{rel}#{experiment_id or idx}",
                "url": "",
                "chunk_id": f"{path.stem}-{idx}",
                "experiment_id": experiment_id,
                "skill_domain": "",
                "failure_category": failure_category,
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
