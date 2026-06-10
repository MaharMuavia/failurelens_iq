from pathlib import Path


def test_docs_do_not_claim_unverified_production_azure():
    text = "\n".join(path.read_text(encoding="utf-8") for path in [Path("README.md"), *Path("docs").glob("*.md")])
    forbidden = [
        "PRODUCTION-READY MVP",
        "production-ready MVP",
        "Production-ready with real Azure",
        "real Azure integration works by default",
        "Azure integration stubs",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "DEMO-READY MVP WITH AZURE PRODUCTION ADAPTERS" in text
    assert "Real Azure calls are enabled only when credentials are provided." in text


def test_docs_claim_dockerfile_only_when_present():
    text = Path("README.md").read_text(encoding="utf-8") + Path("docs/AUDIT_REPORT.md").read_text(encoding="utf-8")
    if "Dockerfile" in text:
        assert Path("Dockerfile").exists()
    if "docker-compose.yml" in text:
        assert Path("docker-compose.yml").exists()
