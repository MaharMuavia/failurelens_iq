from pathlib import Path


def test_architecture_diagram_docs_exist():
    diagram_doc = Path("docs/ARCHITECTURE_DIAGRAM.md")
    mermaid_file = Path("docs/architecture-diagram.mmd")
    assert diagram_doc.exists()
    assert mermaid_file.exists()

    diagram_text = diagram_doc.read_text(encoding="utf-8")
    mermaid_text = mermaid_file.read_text(encoding="utf-8")
    assert "mermaid" in diagram_text
    assert "Azure AI Search" in diagram_text
    assert "Final Report + Reasoning Trace" in mermaid_text
