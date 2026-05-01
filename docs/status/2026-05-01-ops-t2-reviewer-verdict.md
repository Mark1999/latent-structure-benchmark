# Reviewer Verdict — OPS-T2 Ops Dashboard Record Loader

**Task:** OPS-T2 — `apps/ops_dashboard/lib/loader.py` + 25 tests
**Commit:** `4fc1d4ac81cca7143efd461ca9a05eceb7e17b31`
**Date:** 2026-05-01
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)
**Verdict:** PASS

---

## Scorecard

```
REVIEWER VERDICT: PASS

Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check-by-check findings

### Check 1 — No LLM client imports in `cdb_analyze/`
PASS. The two grep hits in `packages/cdb_analyze/cdb_analyze/__init__.py` (lines 12–13)
are inside a comment that *lists* the prohibited libraries — they are not import
statements. No actual `import anthropic`, `import openai`, `from anthropic`, etc.
appear anywhere in `packages/cdb_analyze/`. The new `apps/ops_dashboard/lib/loader.py`
imports only `json` (stdlib), `pathlib.Path` (stdlib), and `cdb_core.schemas.InformantRecord`
(workspace package). No LLM client library anywhere in the commit.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` is not present in the commit's changed file list.
The string "data/raw/informants.jsonl" appears only in: the commit body (documentation),
the module docstring of `loader.py`, and the module docstring of the test file — all
are prose, not file operations. No modification to any pre-existing line.

### Check 3 — No secrets
PASS. All three changed files scanned:

- `apps/ops_dashboard/lib/loader.py` — no key-shaped strings, no webhook URLs,
  no credentials of any kind.
- `tests/test_ops_dashboard_loader.py` — the `sha256_manifest` values are `"0" * 64`
  (64 ASCII zeros), which does not match any real key pattern. `provider_request_id`
  values are `f"req_{informant_id}"` — clearly synthetic. No API keys, no tokens.
- `pyproject.toml` — the `mypy_path` addition contains only filesystem paths to
  workspace source roots. No key-shaped strings, no webhook URLs.

### Check 4 — Forbidden vocabulary
PASS. All diff lines scanned for the full table from CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4:

- `worldview`, `believes`, `thinks` (applied to models) — not present
- `"Model X believes..."`, `"Model X thinks of..."`, `"How models see the world"` — not present
- `"Model X's worldview"`, `"Cultural bias"` (standalone) — not present
- `"What the model understands"` — not present
- `"within-model consensus"`, `"within-model cultural consensus"`,
  `"within-model eigenratio"`, `"within-model CCM"` — not present
- `"publishable"` (for LSB findings) — not present

No forbidden vocabulary in docstrings, comments, the commit body, or any other
generated text.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` is not present in the commit. `docs/DATA_DICTIONARY.md`
is not present. No schema changes to evaluate.

### Check 6 — New dependencies sign-off
PASS. Three aspects evaluated:

**C1 (workspace members):** `apps/ops_dashboard` is absent from `[tool.uv.workspace]
members` in root `pyproject.toml`. Confirmed by inspection — members are
`packages/cdb_core`, `packages/cdb_collect`, `packages/cdb_analyze`,
`packages/cdb_publish`, `packages/cdb_social` only. OPS-T1 constraint C1 upheld.

**C2 (no new pip deps):** Root `pyproject.toml` diff contains only the `mypy_path`
stanza addition under `[tool.mypy]`. The `[project.dependencies]` block is unchanged.
No new entry in `[dependency-groups]`. The `apps/ops_dashboard/pyproject.toml` is
not touched in this commit (the existing Streamlit dep from OPS-T1 is unchanged).
Loader uses only `json` (stdlib), `pathlib` (stdlib), and `cdb_core` (workspace
internal). OPS-T1 constraint C2 upheld.

**`mypy_path` vs. lockfile rule (OPS-T1 N2):** The `mypy_path` stanza is a pure
mypy configuration entry under `[tool.mypy]`. It is not read by `uv` when
resolving or locking the dependency graph. This is the same class of change as the
`[[tool.mypy.overrides]]` stanza added in OPS-T1 for Streamlit. OPS-T1 Reviewer
note N2 explicitly classified such stanzas as outside the "lockfile update required"
rule. The Coder correctly cited this note. The Reviewer's position is consistent
with OPS-T1: no `uv.lock` update required.

### Check 7 — Prompt versioning
N/A. No files under `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
N/A. No frontend files (`apps/dashboard/`) in this commit. No new visualization
components, no MDS plots, no heatmap cells. The ops dashboard pages are not bound
by the public dashboard uncertainty requirement.

### Check 9 — Prerequisite verdicts
PASS. This commit is not a frontend PR (no `apps/dashboard/` files) and is not a
methodology PR (no analysis measures, no gate thresholds, no schema methodology
fields, no lede templates, no ARCHITECTURE.md §1.5.x content). No CDA SME or UI/UX
gate verdict is required.

The OPS-T1 predecessor verdict (`docs/status/2026-05-01-ops-t1-reviewer-verdict.md`)
is referenced in the commit body. That verdict was PASS-WITH-NOTES; the Coder
applied all propagated constraints (C1–C5). The commit body documents compliance
with each constraint explicitly.

---

## Coder-flagged items evaluated

### Item 1 — `index_by_run_id` naming vs. `informant_id` schema field

The function is named `index_by_run_id` while the underlying key is
`InformantRecord.informant_id`. The docstring at
`apps/ops_dashboard/lib/loader.py` lines 57–64 explicitly documents the
mapping:

> "The key is InformantRecord.informant_id, which is the unique run
> identifier (see DATA_DICTIONARY.md §1.1). The parameter and function
> name use 'run_id' to match the ops dashboard's internal vocabulary;
> the underlying field on the schema is informant_id."

The implementation correctly uses `rec.informant_id` as the dict key
(confirmed by reading the function body). The naming is an ops-dashboard
internal vocabulary choice, not a user-facing schema identifier, and the
docstring bridges the gap unambiguously.

Verdict on item 1: ACCEPTABLE as-is. The docstring is the canonical mapping
record. OPS-T3+ may continue to use `run_id` as the ops-dashboard internal
term or may prefer `informant_id` — either is fine as long as the function
docstring documents the mapping. This is a note, not a required correction.

### Item 2 — `mypy_path` addition consistency with OPS-T1 N2

Confirmed consistent. See Check 6 above. The `mypy_path` entry is a
`[tool.mypy]` configuration stanza, not a dependency entry. No `uv.lock`
update required. The Coder's reasoning is correct.

---

## OPS-T1 constraints — compliance check

| Constraint | Requirement | Status |
|---|---|---|
| C1 | `apps/ops_dashboard/` outside uv workspace `members` | PASS — confirmed absent |
| C2 | No new pip deps in workspace or workspace root `[project.dependencies]` | PASS — only `mypy_path` mypy config added |
| C3 | Viz point estimates require uncertainty or documented rationale | N/A — no visualizations in this commit |
| C4 | Read-only invariant — loader.py has no write opens, no sqlite destructive ops | PASS — only `open("r", ...)` in loader.py; `open("w", ...)` in test helper `_write_jsonl` writes to `tmp_path` only, not to data files |
| C5 | Commit subject ≤72 characters | PASS — 50 characters: `feat(ops): add record loader and indexers (OPS-T2)` |

---

## Conventional Commits check

Subject: `feat(ops): add record loader and indexers (OPS-T2)` — 50 characters.
Scope `ops` adopted per OPS-T1 N3 recommendation. PASS.

---

## Failures

None.

---

## Required before merge

None. All nine checks pass.

---

## Constraints propagating to OPS-T3+

All constraints from OPS-T1 continue to propagate unchanged:

- **C1:** `apps/ops_dashboard/` must remain outside uv workspace `members`.
- **C2:** Any new pip dependency requires in-session Architect authorization
  documented in the commit body.
- **C3:** Visualizations displaying point estimates require associated uncertainty
  or a documented rationale for why the ops-tool context makes the §4.5 rule
  inapplicable.
- **C4:** The read-only invariant is a binding constraint. No `open(..., "w" | "a")`
  in production code under `apps/ops_dashboard/` (test helpers writing to `tmp_path`
  are exempt).
- **C5:** Commit subjects ≤72 characters. Scope token `ops`.

**New from OPS-T2:** The `index_by_run_id` / `informant_id` mapping convention
is established. Future OPS-Tx code that refers to this function should be aware
that the key is `informant_id` despite the function name. If OPS-T3+ adds a
function that surfaces this as a user-facing label in the dashboard UI, prefer
`informant_id` (the canonical schema vocabulary) over `run_id`.

---

*Verdict issued by LSB Reviewer agent. Only Mark can override a FAIL.
Verdict: PASS — Coder may merge.*
