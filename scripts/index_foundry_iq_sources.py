from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any
import httpx

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()

def chunk_text(text: str, size: int) -> list[str]:
    chunks: list[str] = []
    cursor = 0
    while cursor < len(text):
        chunks.append(text[cursor : cursor + size])
        cursor += size
    return chunks

def parse_markdown_doc(path: Path, max_chunk_chars: int) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    content_lines = []
    in_content = False
    
    for line in text.splitlines():
        if not in_content and ":" in line:
            key, val = line.split(":", 1)
            norm_key = key.strip().lower().replace(" ", "_")
            if norm_key in {
                "id", "citation", "agent_usage_notes", "title", "source_type",
                "permission_scope", "citation_id", "tags", "relevance_tags",
                "content", "example_evidence"
            }:
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
    chunks = chunk_text(content_body, max_chunk_chars)
    for idx, chunk in enumerate(chunks, start=1):
        rel = path.relative_to(ROOT).as_posix()
        docs.append(
            {
                "id": stable_id(f"{rel}:{idx}"),
                "source_id": rel,
                "title": title,
                "content": chunk,
                "citation": f"{citation_base}#chunk-{idx}" if "#" not in citation_base else f"{citation_base}-chunk-{idx}",
                "source_type": source_type,
                "chunk_id": f"{path.stem}-{idx}",
                "permission_scope": permission_scope,
                "tags": tags,
                "url": ""
            }
        )
    return docs

def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Azure AI Search Index for FailureLens IQ")
    parser.add_argument("--dry-run", action="store_true", help="Perform a local dry run without uploading to Azure")
    parser.add_argument("--verbose", action="store_true", help="Log detail information about parsed chunks")
    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "").strip().rstrip("/")
    key = os.getenv("AZURE_AI_SEARCH_KEY", "").strip()
    index = os.getenv("AZURE_AI_SEARCH_INDEX", "failurelens-iq-knowledge").strip()
    max_chunk_chars = int(os.getenv("AZURE_MAX_CHUNK_CHARS", "1800"))

    # Print log without secrets
    print("=== Azure AI Search Indexing Script ===")
    print(f"Index target: {index}")
    print(f"Search endpoint: {endpoint or 'Not Configured'}")
    print(f"Search key: {'Set (Hidden)' if key else 'Not Configured'}")
    print(f"Dry-run mode: {args.dry_run}")
    print("=======================================")

    if not args.dry_run:
        if not endpoint or not key:
            print("Error: Missing AZURE_AI_SEARCH_ENDPOINT or AZURE_AI_SEARCH_KEY. Please configure them or run with --dry-run.")
            return 1

    directories = [
        ROOT / "knowledge" / "foundry_iq_sources",
        ROOT / "knowledge" / "foundry_docs"
    ]

    documents = []
    for directory in directories:
        if not directory.exists():
            print(f"Warning: Directory {directory} does not exist. Skipping.")
            continue
        print(f"Scanning directory: {directory.relative_to(ROOT)}")
        for path in directory.glob("*.md"):
            try:
                parsed_docs = parse_markdown_doc(path, max_chunk_chars)
                documents.extend(parsed_docs)
                print(f"  Parsed {path.name} -> {len(parsed_docs)} chunks")
            except Exception as e:
                print(f"  Error parsing {path.name}: {e}")

    print(f"Total compiled chunks: {len(documents)}")

    if args.verbose:
        for idx, doc in enumerate(documents, start=1):
            print(f"[{idx}] ID: {doc['id']}, Title: {doc['title']}, Citation: {doc['citation']}")

    if args.dry_run:
        print("Dry run complete. No documents were uploaded.")
        return 0

    print(f"Uploading {len(documents)} documents to index '{index}' on Azure AI Search...")
    url = f"{endpoint}/indexes/{index}/docs/index?api-version=2023-11-01"
    headers = {
        "api-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "value": [
            {
                "@search.action": "mergeOrUpload",
                **doc
            }
            for doc in documents
        ]
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code >= 400:
            print(f"Upload failed (status {response.status_code}):")
            print(response.text)
            return 1
        print("Index seed successfully completed.")
        return 0
    except Exception as e:
        print(f"Upload failed due to connection error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
