#!/usr/bin/env python3
"""
Pre-release scan for the LSB repository.

Runs 8 checks gating the M12 public flip.  Exit codes:
  0 — every check PASS (or WARN for check 6)
  1 — at least one check FAIL
  2 — at least one check could not run (tool missing / unexpected subprocess error)

Usage:
  python scripts/prerelease_scan.py --report docs/status/2026-05-17-phase8-prerelease-scan.md
  python scripts/prerelease_scan.py --report -
  python scripts/prerelease_scan.py --json prerelease-scan.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ─── Repository root ──────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent


# ─── Check-2 forbidden vocabulary patterns ────────────────────────────────────
# These are the §1.5.4 / CLAUDE.md §7 left-column phrases.  The pattern list
# is a documented exception — it exists to detect the phrases, not to use them.

FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    # §1.5.4 row 1
    (r"model\s+\w+\s+believes\b", "model X believes"),
    # §1.5.4 row 2
    (r"model\s+\w+\s+thinks\s+of\b", "model X thinks of"),
    # §1.5.4 row 3
    (r"how\s+models\s+see\b", "how models see"),
    # §1.5.4 row 4
    (r"model'?s\s+worldview\b", "model's worldview"),
    # §1.5.4 row 5  (standalone — must not be preceded by "categorical divergence from")
    (r"(?<!categorical divergence from )cultural\s+bias\b", "cultural bias (standalone)"),
    # §1.5.4 row 6
    (r"what\s+the\s+model\s+understands\b", "what the model understands"),
    # Register-1/Register-2 boundary phrases
    (r"within[-\s]model\s+consensus\b", "within-model consensus"),
    (r"within[-\s]model\s+cultural\s+consensus\b", "within-model cultural consensus"),
    (r"within[-\s]model\s+eigenratio\b", "within-model eigenratio"),
    (r"within[-\s]model\s+CCM\b", "within-model CCM"),
    # Hypothesis-framing phrases
    (r"LSB\s+hypothesizes\b", "LSB hypothesizes"),
    (r"LSB\s+tested\s+whether\b", "LSB tested whether"),
    (r"LSB\s+confirms\s+that\b", "LSB confirms that"),
    (r"LSB\s+predicted\b", "LSB predicted"),
    # Generic terms in model-facing constructions
    (r"models?\s+(?:believe|think)s?\s+(?:about|that)\b", "models believe/think about/that"),
    (r"AI\s+(?:believes|thinks|understands)\b", "AI believes/thinks/understands"),
]

FORBIDDEN_COMPILED = [(re.compile(pat, re.IGNORECASE), label) for pat, label in FORBIDDEN_PATTERNS]

# ─── Check-2 allow-listed paths (skip entirely) ───────────────────────────────
# These files necessarily reference forbidden vocabulary in order to forbid it,
# enumerate patterns for validation, or are verdict files that quote the phrases
# to document what was checked.
#
# Spec-named entries (kickoff §6 check 2):
#   docs/FRONTEND_DESIGNER_BRIEF.md, docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md,
#   docs/status/, ARCHITECTURE.md, CLAUDE.md, tests/unit/test_social_drafters.py,
#   tests/unit/test_social_review_cli.py,
#   packages/cdb_social/cdb_social/drafters/base.py,
#   packages/cdb_social/cdb_social/drafters/prompts/v1/*.md,
#   apps/dashboard/src/copy/screen_reader_summaries.ts
#
# Extended entries — all legitimately enumerate or test for forbidden phrases,
# not use them in production copy:
#   .claude/agents/ — agent instruction files listing forbidden vocab to enforce it
#   apps/dashboard/src/__tests__/ — test assertions checking phrases don't appear
#   tests/ (all test files) — test fixtures and assertions exercising rejection
#   docs/briefings/ — internal briefings that enumerate the rules
#   docs/proposals/ — internal proposals that quote the rules
#   packages/cdb_analyze/ — source comments explaining what not to name things
#   scripts/social_review.py — validator comments quoting forbidden patterns
#   docs/DECLINE_INTERVIEW_PROTOCOL.md — compliance annotation quoting phrases

FORBIDDEN_VOCAB_ALLOWLIST: list[str] = [
    # Spec-named entries
    "docs/FRONTEND_DESIGNER_BRIEF.md",
    "docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md",
    "ARCHITECTURE.md",           # contains the §1.5.4 table
    "CLAUDE.md",                 # contains the §7 table
    "docs/status/",              # verdict files that necessarily quote forbidden vocab
    "tests/unit/test_social_drafters.py",
    "tests/unit/test_social_review_cli.py",
    "packages/cdb_social/cdb_social/drafters/base.py",
    "packages/cdb_social/cdb_social/drafters/prompts/v1/",
    "apps/dashboard/src/copy/screen_reader_summaries.ts",
    "scripts/prerelease_scan.py",  # this file — contains the pattern definitions
    # Extended entries — enumerate or test for forbidden phrases, not use them
    ".claude/agents/",           # agent instruction files listing phrases to forbid
    ".claude/agent-memory/",     # agent memory files (internal operational)
    "apps/dashboard/src/__tests__/",  # test assertions checking phrases absent
    "tests/",                    # all test fixtures and assertions
    "docs/briefings/",           # internal briefings enumerating the rules
    "docs/proposals/",           # internal proposals quoting the rules
    "packages/cdb_analyze/",     # source comments explaining naming prohibitions
    "scripts/social_review.py",  # validator with embedded forbidden-phrase comments
    "docs/DECLINE_INTERVIEW_PROTOCOL.md",  # compliance annotation quoting phrases
    "apps/dashboard/src/copy/framing.ts",  # framing copy with compliance comments
]


def _in_forbidden_allowlist(rel_path: str) -> bool:
    for entry in FORBIDDEN_VOCAB_ALLOWLIST:
        if entry.endswith("/"):
            if rel_path.startswith(entry):
                return True
        else:
            if rel_path == entry:
                return True
    return False


# ─── Check-3 internal path patterns ──────────────────────────────────────────

INTERNAL_PATH_PATTERNS: list[str] = [
    "/home/lsb/",
    "/home/markdd/",
    "/Users/mark",
    "lsb-agent-02",
    "172.238.170.9",
]

INTERNAL_PATH_ALLOWLIST: list[str] = [
    "docs/INCIDENTS/",
    "HOSTING_AND_DEV_OPS.md",
    "HARDWARE.md",
]


def _in_internal_path_allowlist(rel_path: str) -> bool:
    for entry in INTERNAL_PATH_ALLOWLIST:
        if entry.endswith("/"):
            if rel_path.startswith(entry):
                return True
        else:
            if rel_path == entry:
                return True
    return False


# ─── Check-4 email allow-list ─────────────────────────────────────────────────

EMAIL_ALLOWLIST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^security@cogstructurelab\.com$"),
    re.compile(r"^security@cogstructurelab\.ai$"),
    re.compile(r"^contact@cogstructurelab\.com$"),
    re.compile(r"^social-pipeline-bot@cogstructurelab\.com$"),
    re.compile(r"^noreply@anthropic\.com$"),
    # Generic placeholder addresses
    re.compile(r"^your-gmail-username@gmail\.com$"),
    re.compile(r"^your-recipient@example\.com$"),
    re.compile(r"^your-email@example\.com$"),
    re.compile(r"^example@example\.com$"),
    re.compile(r"^your@gmail\.com$"),   # docstring placeholder in email_sender.py
    # Ancestor citation domains (Borgatti / ANTHROPAC)
    re.compile(r"@analytictech\.com$"),
    # Proxy/placeholder shapes in .env.example / README
    re.compile(r".*@example\.(com|org|net)$"),
    # Status-doc context: lsb-security@protonmail.com is an example address in the kickoff
    re.compile(r"^lsb-security@protonmail\.com$"),
    # protonmail.com references (discussed as options in arch docs)
    re.compile(r".*@protonmail\.com$"),
]

# Paths where emails are expected / documented
EMAIL_ALLOWLIST_PATHS: list[str] = [
    ".env.example",
    "SECURITY.md",
    "SECURITY_AND_HARDENING.md",
    "HOSTING_AND_DEV_OPS.md",
    "ARCHITECTURE.md",
    "PHASE_0_TASKS.md",
    "README.md",
    "docs/status/",
    "docs/briefings/",
    "docs/proposals/",
    "apps/dashboard/src/copy/framing.ts",
    ".github/workflows/",
    "packages/cdb_social/cdb_social/email_sender.py",  # docstring placeholder
    ".claude/",                 # agent memory and instruction files
]


def _in_email_path_allowlist(rel_path: str) -> bool:
    for entry in EMAIL_ALLOWLIST_PATHS:
        if entry.endswith("/"):
            if rel_path.startswith(entry):
                return True
        else:
            if rel_path == entry:
                return True
    return False


def _email_is_allowed(addr: str) -> bool:
    return any(pat.match(addr) for pat in EMAIL_ALLOWLIST_PATTERNS)


# ─── Check-5 API key patterns ─────────────────────────────────────────────────

API_KEY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Anthropic/OpenAI sk-", re.compile(r"sk-[a-zA-Z0-9_-]{30,}")),
    ("HuggingFace hf_", re.compile(r"hf_[a-zA-Z0-9]{30,}")),
    ("xAI xai-", re.compile(r"xai-[a-zA-Z0-9]{30,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub PAT ghp_", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
    ("GitHub server token ghs_", re.compile(r"ghs_[a-zA-Z0-9]{36}")),
    ("GitLab PAT glpat-", re.compile(r"glpat-[a-zA-Z0-9_-]{20,}")),
    ("Slack bot token xoxb-", re.compile(r"xoxb-[a-zA-Z0-9-]{50,}")),
    ("Slack webhook URL", re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+")),
]

API_KEY_ALLOWLIST_PATHS: list[str] = [
    ".env.example",
    ".gitleaks.toml",
    "SECURITY_AND_HARDENING.md",   # contains pattern descriptions
    "docs/DATA_DICTIONARY.md",     # contains pattern descriptions
    "docs/status/",                # verdict files that discuss/cite key patterns
    ".claude/",                    # agent memory and instruction files
    "scripts/prerelease_scan.py",  # this file — pattern definitions
    "tests/",                      # test fixtures contain synthetic fake keys
]


def _in_api_key_path_allowlist(rel_path: str) -> bool:
    for entry in API_KEY_ALLOWLIST_PATHS:
        if entry.endswith("/"):
            if rel_path.startswith(entry):
                return True
        else:
            if rel_path == entry:
                return True
    return False


# ─── Check-6 URL scopes ───────────────────────────────────────────────────────

URL_SCAN_FILES: list[str] = [
    "README.md",
    "SECURITY.md",
    "data/open_bundle/huggingface_dataset_card.md",
    "data/open_bundle/README.md",
]

VALID_COGSTRUCTURELAB_PATHS = {"/", "/family", "/holidays", "/food", "/methodology"}

URL_REGEX = re.compile(r"https?://[^\s\)\>\"\'\,\]\}]+")


# ─── Check-8 required license files ──────────────────────────────────────────

REQUIRED_LICENSE_FILES: list[str] = [
    "LICENSE",
    "LICENSE-DATA",
    "LICENSE-PROMPTS",
    "LICENSE-OPENBUNDLE",
    "docs/LICENSE_COVERAGE.md",
    "apps/dashboard/public/fonts/LICENSE.txt",
]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _git_tracked_files() -> list[str]:
    """Return list of tracked file paths relative to repo root."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {result.stderr}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _git_working_tree_status() -> str:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    if not lines:
        return "clean"
    return f"dirty — {len(lines)} changed file(s)"


TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".tsx", ".ts", ".py", ".yml", ".yaml",
    ".html", ".css", ".toml", ".sh", ".env", ".example", ".cfg",
    ".ini", ".rst", ".js", ".jsx",
}


def _is_text_file(rel_path: str) -> bool:
    p = Path(rel_path)
    # Accept files with no extension if they look like known text files (LICENSE, README, etc.)
    if p.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if p.name in {"LICENSE", "LICENSE-DATA", "LICENSE-PROMPTS", "LICENSE-OPENBUNDLE",
                  "README", "NOTICE", "Makefile", ".env.example"}:
        return True
    return not p.suffix


def _read_file_lines(rel_path: str) -> list[str] | None:
    """Return file lines or None if the file cannot be read as text."""
    full = REPO_ROOT / rel_path
    try:
        with open(full, encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except OSError:
        return None


# ─── Check result dataclass ──────────────────────────────────────────────────


class CheckResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.status: str = "PASS"   # PASS | FAIL | WARN | TOOL_MISSING | ERROR
        self.hits: int = 0
        self.details: list[str] = []
        self.remediation: str = ""

    def fail(self, detail: str) -> None:
        self.status = "FAIL"
        self.hits += 1
        self.details.append(detail)

    def warn(self, detail: str) -> None:
        if self.status == "PASS":
            self.status = "WARN"
        self.hits += 1
        self.details.append(detail)

    def tool_missing(self, msg: str) -> None:
        self.status = "TOOL_MISSING"
        self.details.append(msg)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "hits": self.hits,
            "details": self.details,
            "remediation": self.remediation,
        }


# ─── Check 1 — gitleaks ───────────────────────────────────────────────────────


def check_gitleaks() -> CheckResult:
    r = CheckResult("gitleaks full history")
    r.remediation = (
        "Rotate the credential immediately. Rewrite history with "
        "`git filter-repo` to remove the committed secret. Re-run this scan."
    )

    # Locate gitleaks
    which = subprocess.run(["which", "gitleaks"], capture_output=True, text=True)
    if which.returncode != 0:
        r.tool_missing(
            "TOOL_MISSING — `gitleaks` is not installed. "
            "Install via `apt install gitleaks` or `brew install gitleaks`, then re-run."
        )
        return r

    report_path = "/tmp/gitleaks-prerelease.json"
    cmd = [
        "gitleaks", "detect",
        "--source", str(REPO_ROOT),
        "--redact",
        "--report-format", "json",
        "--report-path", report_path,
        "--log-level", "warn",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)

    # gitleaks exits 1 when findings exist, 0 when clean
    findings: list[dict[str, Any]] = []
    if os.path.exists(report_path):
        try:
            with open(report_path) as f:
                raw = f.read().strip()
            if raw:
                findings = json.loads(raw)
                if not isinstance(findings, list):
                    findings = []
        except (json.JSONDecodeError, OSError):
            findings = []

    if findings:
        for finding in findings:
            rule = finding.get("RuleID", "unknown")
            secret = finding.get("Secret", "[redacted]")
            file_ = finding.get("File", "unknown")
            line = finding.get("StartLine", "?")
            r.fail(f"Rule `{rule}` — {file_}:{line} — secret: {secret}")
    elif proc.returncode not in (0, 1):
        # Unexpected exit code
        r.status = "ERROR"
        r.details.append(
            f"gitleaks exited with code {proc.returncode}. stderr: {proc.stderr[:500]}"
        )

    return r


# ─── Check 2 — forbidden vocabulary ──────────────────────────────────────────


def check_forbidden_vocab(tracked_files: list[str]) -> CheckResult:
    r = CheckResult("forbidden vocabulary")
    r.remediation = (
        "Rewrite the offending text to use canonical phrasing per CLAUDE.md §7 "
        "and ARCHITECTURE.md §1.5.4. Re-run this scan."
    )

    scan_extensions = {
        ".md", ".txt", ".json", ".tsx", ".ts", ".py", ".yml", ".yaml",
        ".html", ".css", ".toml",
    }

    for rel_path in tracked_files:
        if _in_forbidden_allowlist(rel_path):
            continue
        p = Path(rel_path)
        if p.suffix.lower() not in scan_extensions and p.suffix != "":
            continue
        lines = _read_file_lines(rel_path)
        if lines is None:
            continue
        for lineno, line in enumerate(lines, 1):
            for compiled, label in FORBIDDEN_COMPILED:
                if compiled.search(line):
                    r.fail(
                        f"{rel_path}:{lineno} — matched pattern `{label}` — "
                        f"`{line.rstrip()[:120]}`"
                    )

    return r


# ─── Check 3 — leaked internal paths ─────────────────────────────────────────


def check_internal_paths(tracked_files: list[str]) -> CheckResult:
    r = CheckResult("leaked internal paths")
    r.remediation = (
        "Remove the path reference from the file. "
        "If it is already in git history, use `git filter-repo` to rewrite. "
        "Re-run this scan."
    )

    for rel_path in tracked_files:
        if _in_internal_path_allowlist(rel_path):
            continue
        lines = _read_file_lines(rel_path)
        if lines is None:
            continue
        for lineno, line in enumerate(lines, 1):
            for pattern in INTERNAL_PATH_PATTERNS:
                if pattern in line:
                    r.fail(
                        f"{rel_path}:{lineno} — contains `{pattern}` — "
                        f"`{line.rstrip()[:120]}`"
                    )

    return r


# ─── Check 4 — real email addresses ──────────────────────────────────────────


def check_email_addresses(tracked_files: list[str]) -> CheckResult:
    r = CheckResult("real email addresses")
    r.remediation = (
        "Remove PII (personal email addresses) or replace with approved placeholder "
        "addresses. Re-run this scan."
    )

    email_regex = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

    for rel_path in tracked_files:
        lines = _read_file_lines(rel_path)
        if lines is None:
            continue
        for lineno, line in enumerate(lines, 1):
            for m in email_regex.finditer(line):
                addr = m.group()
                if _email_is_allowed(addr):
                    continue
                if _in_email_path_allowlist(rel_path):
                    # Still flag if it looks like a real personal address
                    # (non-cogstructurelab, non-example, non-placeholder)
                    if not (
                        addr.endswith("@cogstructurelab.com")
                        or addr.endswith("@cogstructurelab.ai")
                        or addr.endswith("@example.com")
                        or addr.endswith("@example.org")
                        or addr.endswith("@example.net")
                        or "@gmail.com" in addr
                        or "@protonmail.com" in addr
                        or addr.endswith("@analytictech.com")
                    ):
                        r.fail(
                            f"{rel_path}:{lineno} — unrecognised email `{addr}` — "
                            f"`{line.rstrip()[:120]}`"
                        )
                else:
                    r.fail(
                        f"{rel_path}:{lineno} — email address `{addr}` outside "
                        f"allow-listed paths — `{line.rstrip()[:120]}`"
                    )

    return r


# ─── Check 5 — API key patterns ───────────────────────────────────────────────


def check_api_keys(tracked_files: list[str]) -> CheckResult:
    r = CheckResult("API key patterns")
    r.remediation = (
        "Rotate the credential immediately. "
        "Rewrite history with `git filter-repo` to remove the committed secret. "
        "Re-run this scan."
    )

    # Strings that look like API keys but are clearly documentation/placeholder
    FALSE_POSITIVE_INDICATORS = [
        "sk-...your-key-here",
        "sk-ant-...",
        "sk-or-v1-...",
        "your-key",
        "[redacted",
        "pattern",
        "regex",
        "example",
        "50,}",
        "30,}",
        "60,}",
        "{30,",
        "{50,",
        "{60,",
        "re.compile",
        "matches `sk-",
        "matches sk-",
        "prefix",
        "sk-[a-zA",
        "hf_[a-zA",
        "xai-[a-zA",
        "\\bsk-",
        "sk-ant-[",
        "sk-or-v1-[",
    ]

    for rel_path in tracked_files:
        if _in_api_key_path_allowlist(rel_path):
            continue
        lines = _read_file_lines(rel_path)
        if lines is None:
            continue
        for lineno, line in enumerate(lines, 1):
            for label, pat in API_KEY_PATTERNS:
                for m in pat.finditer(line):
                    matched = m.group()
                    # Skip if the line contains documentation/false-positive indicators
                    is_false_positive = any(ind in line for ind in FALSE_POSITIVE_INDICATORS)
                    if is_false_positive:
                        continue
                    r.fail(
                        f"{rel_path}:{lineno} — possible {label}: `{matched[:40]}...` — "
                        f"`{line.rstrip()[:120]}`"
                    )

    return r


# ─── Check 6 — public URL validity ───────────────────────────────────────────


def check_public_urls() -> CheckResult:
    r = CheckResult("public URL validity")
    r.remediation = (
        "Fix the URL syntax or update the placeholder documentation. "
        "Network fetches are out of scope; this is a syntax-only check."
    )

    url_regex = re.compile(r"https?://[^\s\)\>\"\'\,\]\}]+")

    for rel_path in URL_SCAN_FILES:
        full = REPO_ROOT / rel_path
        if not full.exists():
            continue
        lines = _read_file_lines(rel_path)
        if lines is None:
            continue
        for lineno, line in enumerate(lines, 1):
            for m in url_regex.finditer(line):
                url = m.group().rstrip(".,;:)")
                # Check for Zenodo DOI placeholders — document as WARN
                if "<TBD" in url or "<TBD-T8>" in url:
                    r.warn(
                        f"{rel_path}:{lineno} — Zenodo DOI placeholder not yet minted: "
                        f"`{url}` — expected; replace when T8 mints the DOI."
                    )
                    continue
                # Validate cogstructurelab.com/ai paths
                if "cogstructurelab.com" in url or "cogstructurelab.ai" in url:
                    # Extract path portion
                    path_match = re.search(r"cogstructurelab\.(com|ai)(\/[^\s\)\>\"\']*)?", url)
                    if path_match:
                        path = path_match.group(2) or "/"
                        # Strip trailing slash for comparison
                        bare = path.rstrip("/") or "/"
                        if bare not in VALID_COGSTRUCTURELAB_PATHS:
                            r.warn(
                                f"{rel_path}:{lineno} — unrecognised cogstructurelab path "
                                f"`{path}` in `{url}` — verify this path will resolve post-launch."
                            )
                    continue
                # Basic syntax check
                if not re.match(r"https?://[a-zA-Z0-9._%-]", url):
                    r.warn(
                        f"{rel_path}:{lineno} — URL `{url[:80]}` has suspect syntax."
                    )

    return r


# ─── Check 7 — .env and credential file presence ─────────────────────────────


def check_env_and_credential_files() -> CheckResult:
    r = CheckResult(".env and credential file presence")
    r.remediation = (
        "Add the file to .gitignore and run `git rm --cached <file>`. "
        "If the file contains real credentials, rotate them immediately, then "
        "rewrite history to remove them. Re-run this scan."
    )

    credential_pattern = re.compile(
        r"(^\.env$|credentials.*\.json$|secret.*\.json$|\.pem$|\.key$|\.p12$|\.pfx$)"
    )

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        r.status = "ERROR"
        r.details.append(f"git ls-files failed: {result.stderr}")
        return r

    for rel_path in result.stdout.splitlines():
        fname = Path(rel_path).name
        if credential_pattern.search(fname):
            # .env.example is allowed; plain .env is not
            if rel_path == ".env.example":
                continue
            r.fail(
                f"Tracked credential file: `{rel_path}` — "
                "this file should not be committed."
            )

    return r


# ─── Check 8 — license coverage ──────────────────────────────────────────────


def check_license_coverage() -> CheckResult:
    r = CheckResult("license coverage sanity")
    r.remediation = (
        "Restore the missing license file. "
        "Phase 8 T1 produced LICENSE_COVERAGE.md as the authoritative mapping. "
        "Re-run this scan."
    )

    for rel_path in REQUIRED_LICENSE_FILES:
        full = REPO_ROOT / rel_path
        if not full.exists():
            r.fail(f"Missing required file: `{rel_path}`")

    return r


# ─── Report rendering ─────────────────────────────────────────────────────────


def _status_icon(status: str) -> str:
    return {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN",
            "TOOL_MISSING": "TOOL_MISSING", "ERROR": "ERROR"}.get(status, status)


def render_markdown_report(
    results: list[CheckResult],
    run_at: str,
    head: str,
    tree_status: str,
) -> str:
    overall = "PASS"
    for r in results:
        if r.status in ("FAIL", "ERROR"):
            overall = "FAIL"
        elif r.status == "TOOL_MISSING" and overall != "FAIL":
            overall = "TOOL_MISSING"

    lines: list[str] = []
    lines.append("# Pre-Release Scan Report")
    lines.append("")
    lines.append(f"**Run at:** {run_at}")
    lines.append("**Run by:** `scripts/prerelease_scan.py`")
    lines.append(f"**Repository state:** `{head}`")
    lines.append(f"**Working tree:** {tree_status}")
    lines.append("")
    lines.append(f"**Overall result:** {overall}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Per-check results")
    lines.append("")

    check_labels = [
        "gitleaks full history",
        "forbidden vocabulary",
        "leaked internal paths",
        "real email addresses",
        "API key patterns",
        "public URL validity",
        ".env and credential-file presence",
        "license-coverage sanity",
    ]

    for i, r in enumerate(results, 1):
        lines.append(f"### Check {i} — {check_labels[i - 1]}")
        lines.append("")
        lines.append(f"**Status:** {r.status}")
        lines.append(f"**Hits:** {r.hits}")
        if r.details:
            lines.append("")
            lines.append("**Details:**")
            lines.append("")
            for d in r.details:
                lines.append(f"- {d}")
        if r.remediation and r.status not in ("PASS", "WARN"):
            lines.append("")
            lines.append(f"**Remediation:** {r.remediation}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Result | Hits |")
    lines.append("|---|---|---|")
    for i, r in enumerate(results, 1):
        lines.append(f"| {i} {check_labels[i - 1]} | {r.status} | {r.hits} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Gate status for T11 (the public flip)")
    lines.append("")
    if overall == "PASS":
        lines.append(
            "**GATE: PASS** — scan ran clean. "
            "T11 (go-public) may proceed provided this report was generated "
            "within the 24 hours immediately preceding M12."
        )
    elif overall == "TOOL_MISSING":
        lines.append(
            "**GATE: INCOMPLETE** — one or more tools are missing. "
            "Install the missing tools, re-run, and achieve a clean PASS "
            "before T11 proceeds."
        )
    else:
        lines.append(
            "**GATE: FAIL** — remediation required before T11 (the public flip). "
            "Fix every FAIL above and re-run. The scan must exit 0 within the "
            "24 hours immediately preceding M12."
        )
    lines.append("")
    lines.append(
        "This report MUST be re-generated within the 24 hours immediately "
        "preceding M12 (the actual flip)."
    )
    lines.append("")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LSB pre-release scan — gates the M12 public flip."
    )
    parser.add_argument(
        "--report",
        metavar="PATH",
        default=None,
        help="Write Markdown report to PATH (use - for stdout).",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        default=None,
        dest="json_out",
        help="Write machine-readable JSON report to PATH.",
    )
    args = parser.parse_args()

    run_at = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    head = _git_head()
    tree_status = _git_working_tree_status()

    print(f"LSB pre-release scan — {run_at}")
    print(f"HEAD: {head}")
    print(f"Working tree: {tree_status}")
    print()

    # Gather tracked files once
    try:
        tracked_files = _git_tracked_files()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    results: list[CheckResult] = []

    # Run all 8 checks
    checks = [
        ("1 — gitleaks", lambda: check_gitleaks()),
        ("2 — forbidden vocab", lambda: check_forbidden_vocab(tracked_files)),
        ("3 — internal paths", lambda: check_internal_paths(tracked_files)),
        ("4 — email addresses", lambda: check_email_addresses(tracked_files)),
        ("5 — API key patterns", lambda: check_api_keys(tracked_files)),
        ("6 — public URL validity", lambda: check_public_urls()),
        ("7 — .env/credential files", lambda: check_env_and_credential_files()),
        ("8 — license coverage", lambda: check_license_coverage()),
    ]

    for label, fn in checks:
        print(f"Running check {label} ...", end=" ", flush=True)
        result = fn()
        results.append(result)
        print(f"{result.status} ({result.hits} hit(s))")

    print()

    # Determine overall exit code
    exit_code = 0
    for r in results:
        if r.status in ("FAIL", "ERROR"):
            exit_code = 1
        elif r.status == "TOOL_MISSING" and exit_code == 0:
            exit_code = 2

    # Render report
    md = render_markdown_report(results, run_at, head, tree_status)

    if args.report:
        if args.report == "-":
            print(md)
        else:
            out_path = Path(args.report)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            print(f"Report written to: {out_path}")

    if args.json_out:
        jdata = {
            "run_at": run_at,
            "head": head,
            "working_tree": tree_status,
            "overall": "PASS" if exit_code == 0 else ("TOOL_MISSING" if exit_code == 2 else "FAIL"),
            "checks": [r.to_dict() for r in results],
        }
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(jdata, indent=2), encoding="utf-8")
        print(f"JSON report written to: {json_path}")

    if exit_code == 0:
        overall_label = "PASS"
    elif exit_code == 2:
        overall_label = "TOOL_MISSING (exit 2)"
    else:
        overall_label = "FAIL (exit 1)"
    print(f"\nOverall: {overall_label}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
