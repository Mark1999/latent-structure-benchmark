"""Tests for the cdb_analyze no-LLM-imports static check.

See PHASE_0_TASKS.md P0-T6: "The static check has its own unit test that
creates a temporary file with a forbidden import and verifies the check
rejects it."
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from scripts.check_no_llm_imports import check_file, main


def _write_temp_py(content: str) -> Path:
    """Write content to a temporary .py file and return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
    return Path(f.name)


def test_clean_file_passes():
    path = _write_temp_py("import os\nimport json\n")
    assert check_file(path) == []


def test_import_anthropic_rejected():
    path = _write_temp_py("import anthropic\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "anthropic" in violations[0]


def test_from_openai_rejected():
    path = _write_temp_py("from openai import ChatCompletion\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "openai" in violations[0]


def test_from_google_generativeai_rejected():
    path = _write_temp_py("from google.generativeai import GenerativeModel\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "google.generativeai" in violations[0]


def test_from_litellm_rejected():
    path = _write_temp_py("import litellm\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "litellm" in violations[0]


def test_from_langchain_rejected():
    path = _write_temp_py("from langchain import LLMChain\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "langchain" in violations[0]


def test_from_llama_index_rejected():
    path = _write_temp_py("from llama_index import VectorStoreIndex\n")
    violations = check_file(path)
    assert len(violations) == 1
    assert "llama_index" in violations[0]


def test_numpy_scipy_sklearn_allowed():
    path = _write_temp_py(
        "import numpy\nimport scipy\nfrom sklearn.manifold import MDS\n"
    )
    assert check_file(path) == []


def test_main_passes_on_clean_dir(tmp_path: Path):
    (tmp_path / "clean.py").write_text("import os\n", encoding="utf-8")
    assert main(target_dir=tmp_path) == 0


def test_main_fails_on_dirty_dir(tmp_path: Path):
    (tmp_path / "bad.py").write_text("import anthropic\n", encoding="utf-8")
    assert main(target_dir=tmp_path) == 1


def test_main_passes_on_actual_cdb_analyze():
    """The real cdb_analyze directory should be clean."""
    assert main() == 0
