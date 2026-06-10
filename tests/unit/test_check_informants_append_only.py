"""Tests for .claude/hooks/check_informants_append_only.py

Covers the PreToolUse guard that blocks Write/Edit/MultiEdit to
data/raw/informants.jsonl (CLAUDE.md §9 pitfall 10, SECURITY_AND_HARDENING.md §7.1).

All tests call the hook as a subprocess; this mirrors how Claude Code invokes it
and avoids importing mutable global state. No real API calls are made.

Doc-state tests (prefixed test_doc_) verify the text corrections described in the
PR: CLAUDE.md §9 pitfall 10 must NOT reference "CI append-only check" and must
accurately describe the PreToolUse hook; SECURITY_AND_HARDENING.md §7.1 item 2 must
NOT reference "pre-commit hook in CI (added in P0-T6)".
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude/hooks/check_informants_append_only.py"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
SECURITY_MD = REPO_ROOT / "SECURITY_AND_HARDENING.md"
TARGET = "data/raw/informants.jsonl"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _run_hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Fail-open / irrelevant-tool tests (happy path: exit 0)
# ---------------------------------------------------------------------------

def test_unparseable_stdin_exits_zero():
    """Malformed stdin must not crash or block (fail-open contract)."""
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="NOT VALID JSON {{{",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Hook should fail-open on bad stdin, got rc={result.returncode}"
    )


def test_non_edit_tool_exits_zero():
    """Bash or Read tool calls must be ignored (not Write/Edit/MultiEdit)."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": f"cat {TARGET}"},
    }
    result = _run_hook(payload)
    assert result.returncode == 0


def test_read_tool_exits_zero():
    """Read tool against informants.jsonl is not blocked."""
    payload = {
        "tool_name": "Read",
        "tool_input": {"file_path": f"{REPO_ROOT}/{TARGET}"},
    }
    result = _run_hook(payload)
    assert result.returncode == 0


def test_write_unrelated_file_exits_zero():
    """Write to a file that is NOT informants.jsonl must pass."""
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": f"{REPO_ROOT}/data/raw/other.jsonl", "content": "{}"},
    }
    result = _run_hook(payload)
    assert result.returncode == 0


def test_edit_unrelated_file_exits_zero():
    """Edit to a file that is NOT informants.jsonl must pass."""
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": f"{REPO_ROOT}/packages/cdb_core/cdb_core/schemas.py",
            "old_string": "x",
            "new_string": "y",
        },
    }
    result = _run_hook(payload)
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Block tests (error path: exit 2, stderr contains explanation)
# ---------------------------------------------------------------------------

def test_write_to_informants_blocked():
    """Write tool targeting informants.jsonl must exit 2 (BLOCKED)."""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": f"{REPO_ROOT}/{TARGET}",
            "content": '{"model_id": "fixture-model"}\n',
        },
    }
    result = _run_hook(payload)
    assert result.returncode == 2, (
        f"Write to informants.jsonl must be blocked (exit 2), got {result.returncode}"
    )
    assert "BLOCKED" in result.stderr
    assert "APPEND-ONLY" in result.stderr


def test_edit_to_informants_blocked():
    """Edit tool targeting informants.jsonl must exit 2 (BLOCKED)."""
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": f"{REPO_ROOT}/{TARGET}",
            "old_string": "old_value",
            "new_string": "new_value",
        },
    }
    result = _run_hook(payload)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_multiedit_to_informants_blocked():
    """MultiEdit tool targeting informants.jsonl must exit 2 (BLOCKED)."""
    payload = {
        "tool_name": "MultiEdit",
        "tool_input": {
            "file_path": f"{REPO_ROOT}/{TARGET}",
            "edits": [{"old_string": "a", "new_string": "b"}],
        },
    }
    result = _run_hook(payload)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_relative_path_to_informants_blocked():
    """Relative path ending in informants.jsonl must also be blocked."""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": TARGET,  # relative path, no repo-root prefix
            "content": "{}",
        },
    }
    result = _run_hook(payload)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_block_message_references_qa_passed():
    """Stderr block message must mention qa_passed=False (correct remediation path)."""
    payload = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": f"{REPO_ROOT}/{TARGET}",
            "content": "{}",
        },
    }
    result = _run_hook(payload)
    assert "qa_passed=False" in result.stderr, (
        "Block message must direct the agent to qa_passed=False path, not silent edit"
    )


# ---------------------------------------------------------------------------
# Doc-state tests: verify the text corrections made by this PR
# ---------------------------------------------------------------------------

def test_claude_md_pitfall10_no_ci_append_only_claim():
    """CLAUDE.md §9 pitfall 10 must NOT claim 'CI append-only check rejects any PR'.

    The accurate description is the three-layer enforcement: gitignore path
    segregation, PreToolUse hook, and append-mode-only in cdb_collect. The old
    claim about a CI check was false and has been replaced.
    """
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert "CI append-only check rejects any PR" not in text, (
        "CLAUDE.md §9 pitfall 10 still contains the false CI-append-only claim. "
        "This should have been replaced by the PreToolUse hook description."
    )


def test_claude_md_pitfall10_references_pretooluse_hook():
    """CLAUDE.md §9 pitfall 10 must reference the PreToolUse hook as enforcement."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert "PreToolUse" in text, (
        "CLAUDE.md §9 pitfall 10 must describe the PreToolUse hook enforcement mechanism."
    )


def test_security_md_section71_no_pre_commit_ci_claim():
    """SECURITY_AND_HARDENING.md §7.1 item 2 must NOT reference 'pre-commit hook in CI'.

    The old text said 'A pre-commit hook in CI (added in P0-T6)' which was false.
    The accurate description is the PreToolUse hook for Claude Code agents.
    """
    text = SECURITY_MD.read_text(encoding="utf-8")
    # Check for the specific false claim pattern (item 2 in §7.1)
    assert "pre-commit hook in CI" not in text, (
        "SECURITY_AND_HARDENING.md §7.1 still contains the false 'pre-commit hook in CI' claim. "
        "It should describe the PreToolUse hook instead."
    )


def test_security_md_section71_references_pretooluse_hook():
    """SECURITY_AND_HARDENING.md §7.1 must reference the PreToolUse hook."""
    text = SECURITY_MD.read_text(encoding="utf-8")
    assert "PreToolUse" in text, (
        "SECURITY_AND_HARDENING.md §7.1 must describe the PreToolUse hook as the "
        "enforcement mechanism replacing the false 'pre-commit hook in CI' claim."
    )


def test_security_md_section71_no_p0_t6_parenthetical():
    """SECURITY_AND_HARDENING.md §7.1 item 2 must not contain the false P0-T6 parenthetical."""
    text = SECURITY_MD.read_text(encoding="utf-8")
    assert "added in P0-T6" not in text, (
        "SECURITY_AND_HARDENING.md §7.1 still contains the false '(added in P0-T6)' "
        "historical parenthetical. It should be removed along with the CI-hook claim."
    )


def test_hook_file_exists_and_is_active():
    """The hook file must exist and contain the ACTIVE wiring comment."""
    assert HOOK.exists(), f"Hook file not found at {HOOK}"
    content = HOOK.read_text(encoding="utf-8")
    assert "ACTIVE" in content, "Hook file must contain ACTIVE status comment"
    assert "check_informants_append_only" in HOOK.name


def test_hook_wired_in_settings_json():
    """The hook must be wired in .claude/settings.json PreToolUse array."""
    settings = REPO_ROOT / ".claude/settings.json"
    assert settings.exists(), ".claude/settings.json not found"
    data = json.loads(settings.read_text(encoding="utf-8"))
    pre_tool_hooks = data.get("hooks", {}).get("PreToolUse", [])
    all_commands = []
    for entry in pre_tool_hooks:
        for h in entry.get("hooks", []):
            all_commands.append(h.get("command", ""))
    assert any("check_informants_append_only" in cmd for cmd in all_commands), (
        "check_informants_append_only.py is not wired into .claude/settings.json PreToolUse"
    )
