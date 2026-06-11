import importlib.util
import sys
from pathlib import Path


def test_azure_scripts_exist():
    for script in [
        "scripts/azure/check_azure_env.py",
        "scripts/azure/create_search_index.py",
        "scripts/azure/seed_search_index.py",
        "scripts/azure/test_search_query.py",
        "scripts/azure/delete_search_index.py",
    ]:
        assert Path(script).exists()


def test_seed_script_respects_document_limit(monkeypatch):
    script = Path("scripts/azure/seed_search_index.py")
    sys.path.insert(0, str(script.parent.resolve()))
    spec = importlib.util.spec_from_file_location("seed_search_index", script)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    monkeypatch.setenv("AZURE_MAX_DOCS_TO_INDEX", "3")
    docs = module.build_documents()
    assert len(docs) <= 3
    assert all("citation" in doc for doc in docs)
