"""Tests for prompt template loading and substitution."""

from pathlib import Path

_PROMPTS_DIR = (
    Path(__file__).resolve().parents[2]
    / "packages" / "cdb_collect" / "cdb_collect" / "prompts"
)


def test_free_list_template_exists():
    path = _PROMPTS_DIR / "v1" / "free_list.md"
    assert path.exists(), f"Prompt template not found: {path}"


def test_free_list_template_has_placeholder():
    path = _PROMPTS_DIR / "v1" / "free_list.md"
    content = path.read_text()
    assert "{{domain_seed}}" in content


def test_free_list_template_substitution():
    path = _PROMPTS_DIR / "v1" / "free_list.md"
    content = path.read_text()
    prompt = content.replace("{{domain_seed}}", "type of family relationship or family member")
    assert "type of family relationship or family member" in prompt
    assert "{{domain_seed}}" not in prompt
    assert "numbered list" in prompt
