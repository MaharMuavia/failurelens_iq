import os


def test_no_virtualenv_paths_in_source_tree():
    forbidden = []
    ignored = {".git", "node_modules", "dist", ".pytest_cache", "__pycache__"}
    for root, dirs, _files in os.walk("."):
        dirs[:] = [directory for directory in dirs if directory not in ignored]
        if ".venv" in root.split(os.sep):
            forbidden.append(root)
    assert forbidden == []
