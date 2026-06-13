import pytest
from pathlib import Path
from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter

def test_foundry_iq_sources_exist():
    sources_dir = Path("knowledge/foundry_iq_sources")
    assert sources_dir.exists()
    
    expected_files = [
        "failure_taxonomy.md",
        "experiment_history.json",
        "remediation_playbooks.md",
        "microsoft_certification_mapping.md",
        "responsible_ai_checklist.md",
        "manager_governance.md",
    ]
    for filename in expected_files:
        assert (sources_dir / filename).exists(), f"File {filename} is missing"

def test_foundry_iq_sources_are_loaded_correctly():
    adapter = FoundryIQLocalAdapter()
    sources = adapter.load_knowledge_sources()
    
    # 6 JSON experiments + 5 Markdown files = 11 sources
    assert len(sources) >= 11
    
    # Verify failure_taxonomy metadata
    taxonomy = next(s for s in sources if s["id"] == "failure-taxonomy-001")
    assert taxonomy["title"] == "Failure Taxonomy"
    assert taxonomy["source_type"] == "failure_taxonomy"
    assert taxonomy["permission_scope"] == "demo"
    assert "Evaluation Methodology Failure" in taxonomy["content"]
    assert "ml_failure" in taxonomy["tags"]
    assert "ClassifierAgent" in taxonomy["agent_usage_notes"]
    
    # Verify certification_mapping metadata
    cert = next(s for s in sources if s["id"] == "cert-mapping-001")
    assert "AI-900" in cert["content"]
    assert "AI-102" in cert["content"]
    assert "CertificationEvaluatorAgent" in cert["agent_usage_notes"]

    # Verify responsible_ai metadata
    rai = next(s for s in sources if s["id"] == "responsible-ai-001")
    assert "fairness" in rai["tags"]
    assert "transparency" in rai["tags"]
    
    # Verify experiment history
    exps = [s for s in sources if s["source_type"] == "experiment_history"]
    assert len(exps) == 6
    assert any(e["id"] == "exp-001" for e in exps)
    assert any(e["id"] == "exp-006" for e in exps)
