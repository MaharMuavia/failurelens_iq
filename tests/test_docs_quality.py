from pathlib import Path


def test_readme_is_clean_for_submission():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "Permalink:" not in text
    assert "file:///" not in text
    assert "OpenAI direct API does not replace Microsoft IQ" in text
    assert "docs/MICROSOFT_IQ_HONEST_COMPLIANCE.md" in text


def test_required_submission_docs_exist():
    for doc in [
        "docs/GIT_HISTORY_CLEANUP.md",
        "docs/JUDGE_REVIEW_GUIDE.md",
        "docs/NO_SECRETS_POLICY.md",
        "docs/AZURE_POLICY_BLOCKER.md",
        "docs/OPENAI_FALLBACK_PROVIDER.md",
        "docs/MICROSOFT_IQ_HONEST_COMPLIANCE.md",
    ]:
        assert Path(doc).exists()
