from pathlib import Path


def test_readme_has_no_local_file_links():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "file:///" not in content
    assert "docs/PRODUCTION_HARDENING.md" in content
    assert "docs/SECURITY_MODEL.md" in content


def test_video_demo_docs_exist():
    for doc in [
        "docs/VIDEO_DEMO_SCRIPT.md",
        "docs/VIDEO_DEMO_CHECKLIST.md",
        "docs/JUDGE_QA.md",
        "docs/DEMO_COMMANDS.md",
    ]:
        assert Path(doc).exists()
