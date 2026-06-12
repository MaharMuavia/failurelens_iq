from pathlib import Path


def test_video_demo_docs_exist():
    for path in [
        "docs/VIDEO_DEMO_SCRIPT.md",
        "docs/VIDEO_DEMO_CHECKLIST.md",
        "docs/JUDGE_QA.md",
        "docs/DEMO_COMMANDS.md",
        "docs/SUBMISSION_CHECKLIST.md",
    ]:
        assert Path(path).exists(), f"{path} must exist"


def test_video_script_contains_required_pitch_lines():
    text = Path("docs/VIDEO_DEMO_SCRIPT.md").read_text(encoding="utf-8")
    assert "0:00-0:15" in text
    assert "FailureLens IQ implements Foundry IQ using Azure AI Search" in text
    assert "enterprise learning memory system" in text
