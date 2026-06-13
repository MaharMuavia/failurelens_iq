import pytest
from pathlib import Path
from scripts.azure.seed_search_index import build_documents

def test_build_documents_includes_new_sources_with_required_metadata():
    docs = build_documents()
    assert len(docs) > 0
    
    # Check that every doc has the required fields
    for doc in docs:
        assert "id" in doc
        assert "title" in doc
        assert "content" in doc
        assert "source_type" in doc
        assert "citation" in doc
        assert "permission_scope" in doc
        assert "tags" in doc
        assert isinstance(doc["tags"], list)
        
    # Verify that files in foundry_iq_sources were successfully parsed
    foundry_iq_docs = [d for d in docs if "foundry_iq_sources" in d.get("source_id", "")]
    assert len(foundry_iq_docs) > 0
    
    # Verify taxonomy metadata chunk
    tax_docs = [d for d in foundry_iq_docs if d["source_type"] == "failure_taxonomy"]
    assert len(tax_docs) > 0
    for doc in tax_docs:
        assert doc["permission_scope"] == "demo"
        assert "ml_failure" in doc["tags"]
        
    # Verify experiment history records
    exp_docs = [d for d in foundry_iq_docs if d["source_type"] == "experiment_history"]
    assert len(exp_docs) == 6
    for doc in exp_docs:
        assert doc["permission_scope"] == "demo"
        assert len(doc["tags"]) > 0
