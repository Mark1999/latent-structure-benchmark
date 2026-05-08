# Reviewer Verdict — SC-T1 (Strip Spend-Cap Mechanism from Variance Driver)

**Date:** 2026-05-08
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `cf555b1`
**Commit subject:** `fix(collect): SC-T1 strip spend-cap mechanism from variance driver`
**Scope:** `scripts/run_phase4b_variance.py` and `tests/unit/test_run_phase4b_variance.py`

**Prerequisite gate verdict:**
Architect plan committed at `acc66b9` —
`docs/status/2026-05-08-spend-cap-removal-architect-plan.md`. No CDA SME gate
required (no methodology change). No UI/UX gate required (non-frontend).
SC-T1 is cited in the commit message. Gate satisfied.

---

## REVIEWER VERDICT: PASS

---

## 9-Check Scorecard (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

| Check | Description | Result |
|---|---|---|
| Check 1 | No LLM client imports in `cdb_analyze/` | N/A |
| Check 2 | `informants.jsonl` append-only invariant | N/A |
| Check 3 | No API keys or secrets in committed files | PASS |
| Check 4 | No forbidden vocabulary | PASS |
| Check 5 | Schema changes co-update `DATA_DICTIONARY.md` | N/A |
| Check 6 | No new dependencies without Architect sign-off | N/A |
| Check 7 | Prompt templates versioned correctly | N/A |
| Check 8 | No point estimates without uncertainty in visualizations | N/A |
| Check 9 | Prerequisite gate verdicts present | PASS |

---

## Detailed Check Results

### Check 1 — No LLM client imports in `cdb_analyze/`

This commit does not touch `packages/cdb_analyze/`. N/A.

### Check 2 — Append-only `informants.jsonl`

This commit does not touch `data/raw/informants.jsonl` or any raw data file.
N/A.

### Check 3 — No API keys or secrets

```
grep -nE "sk-[a-zA-Z0-9]+|Bearer [a-zA-Z0-9]+|hooks\.slack\.com" \
  scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Zero hits. No LSB webhook URL, no LLM provider key, no Bearer token. **PASS.**

### Check 4 — No forbidden vocabulary

```
grep -nE "\b(believes|thinks|worldview|recognizes|interprets|perceives|publishable)\b" \
  scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Zero hits. ARCHITECTURE.md §1.5.4 SME additions also checked
("within-model consensus", "within-model eigenratio", "within-model CCM",
"publishable") — zero hits.

Commit message scanned: references spend-cap removal, SC-T1, and the architect
plan path. No forbidden vocabulary. **PASS.**

### Check 5 — Schema + DATA_DICTIONARY.md

```
git diff acc66b9..cf555b1 -- packages/cdb_core/cdb_core/schemas.py
```

No output. No schema changes. N/A.

### Check 6 — No new dependencies

```
git diff acc66b9..cf555b1 -- pyproject.toml uv.lock
```

No output. No dependency changes. N/A.

### Check 7 — Prompt template versioning

```
git diff acc66b9..cf555b1 -- packages/cdb_collect/cdb_collect/prompts/
```

No output. No prompt template changes. N/A.

### Check 8 — Uncertainty in visualizations

Non-frontend PR. No visualization components introduced or modified. N/A.

### Check 9 — Prerequisite gate verdicts present

Non-frontend task (no UI/UX gate required). Non-methodology task (no CDA SME
gate required for SC-T1). The Architect plan is committed at `acc66b9` and
the commit message references
`docs/status/2026-05-08-spend-cap-removal-architect-plan.md SC-T1`. **PASS.**

---

## SC-T1-Specific Reviewer Items (from plan §6)

### Item A — `provider_worker` no longer has `max_spend_usd` parameter

Confirmed. Post-commit `provider_worker` signature (lines 575–587 of
`scripts/run_phase4b_variance.py`):

```python
def provider_worker(
    provider_method: str,
    cell_queue: queue.Queue[VarianceCell | None],
    campaign_id: str,
    informants_path: Path,
    failures_path: Path,
    stats: CampaignStats,
    log_fh: IO[str],
    total_cells: int,
    cell_counter: list[int],
    counter_lock: threading.Lock,
) -> None:
```

No `max_spend_usd` parameter. The main caller (lines 1085–1095) no longer
passes `max_spend_usd` or `registry_map`. **PASS.**

### Item B — `CampaignStats` no longer has `total_spend_usd` / `add_spend`

Confirmed. Post-commit `CampaignStats` (lines 201–213) contains:
`n_pass: int = 0`, `n_failed: int = 0`, `n_skipped: int = 0`,
`cells_attempted`, `cells_remaining`, `_lock`. No `total_spend_usd` field,
no `add_spend` method. All three mandatory counters present. **PASS.**

### Item C — Exit code 3 removed from docstring

Confirmed. Post-commit exit-codes block (lines 47–51):

```
Exit codes:
    0 — clean run (complete or dry-run)
    1 — configuration error
    2 — run completed with at least one cell still failed (finding documented)
```

Only exit codes 0, 1, and 2 remain. Exit code 3 ("spend cap crossed") is
absent from both the docstring and the `return` statements in `main()`. **PASS.**

### Item D — `--dry-run` output produces sensible plan summary with no cost lines

Confirmed by running:

```
uv run python scripts/run_phase4b_variance.py --dry-run
```

Output includes: campaign ID, cell counts, model registry check (all 20 models
validate OK via `MODEL_REGISTRY`), variant directories check (all 9 variants OK),
sample of first 10 plan cells, total cell count, log path. No "Spend cap" line,
no "Total spend" line, no "$" dollar-amount reference anywhere in the output.
Dry-run output terminates with "DRY RUN complete. No API calls made." **PASS.**

### Item E — Test count: 32 → 29 (three deleted tests exactly)

Pre-commit: 32 test functions. Post-commit: 29 test functions. Delta: −3.

Deleted tests confirmed as exactly:
1. `test_provider_worker_exits_when_spend_cap_reached` — named in the plan §6 E
2. `test_estimate_cell_cost_usd_known_model` — test for the deleted helper
3. `test_estimate_cell_cost_usd_missing_model` — test for the deleted helper

The orchestrator note in the task specification pre-explained items 2 and 3 as
a defensible scope expansion: `estimate_cell_cost_usd` itself was deleted per
plan §2 ("the helper `estimate_cell_cost_usd` and any callers of it"), making
these two tests non-viable importers. This is the correct outcome. No other
test functions were removed. **PASS.**

### Item F — Zero grep hits for spend-cap tokens

```
git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|DEFAULT_MAX_SPEND|spend_cap|cost_cap|cost-cap-usd|--max-spend|estimate_cell_cost_usd|total_spend_usd|add_spend' \
  -- scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Exit code 1 (grep found zero matches). **PASS.**

### Item G — Tests pass; mypy clean

```
uv run pytest tests/unit/test_run_phase4b_variance.py -v
```
Result: **29 passed** in 0.82 s.

```
uv run mypy packages/
```
Result: **Success: no issues found in 55 source files.**

Note: `uv run mypy scripts/run_phase4b_variance.py` directly produces one
error (`Cannot find implementation or library stub for module named "collect"`)
— this is a pre-existing path-resolution issue where `collect` is imported
without the package prefix when running mypy against the script directly rather
than via the packages tree. The standard LSB mypy target is `uv run mypy packages/`
(per CLAUDE.md §11), which reports clean. **PASS.**

---

## Coder's Reported Scope Deviation — Assessment

The Coder also removed `load_registry_map`, `REGISTRY_PATH`, the `registry_map`
parameter on `run_cell` and `provider_worker`, and orphaned `os` / `Any` imports.

**Assessment: legitimate and clean.**

`load_registry_map` had exactly one consumer: `estimate_cell_cost_usd`. With
`estimate_cell_cost_usd` deleted, `load_registry_map` had zero callers.
`REGISTRY_PATH` was referenced only inside `load_registry_map`. The `registry_map`
parameter on `run_cell` and `provider_worker` was passed only to
`estimate_cell_cost_usd`. Removing all four is the correct ruff-clean outcome.

The dry-run model registry check still validates all 20 models. It goes through
`MODEL_REGISTRY` imported from `cdb_collect` (line 86), not `load_registry_map`.
`MODEL_REGISTRY` is resolved from the `data/models/registry.json` file by the
`cdb_collect` package at import time. The `load_registry_map` helper was a
separate JSON reader used only for cost estimation — a second, redundant registry
read path. Removing it does not affect model discovery, preflight, or collection.

`os` and `Any` were imported only for the `os.environ.get("CDB_MAX_SPEND_USD")`
call and for `dict[str, Any]` type annotations on the registry dicts. Both are
correctly absent post-removal; `ruff check` confirms zero lint issues.

This deviation is fully within the plan §2 scope ("the helper
`estimate_cell_cost_usd` and any callers of it") and is necessary to satisfy
the ruff-clean acceptance criterion. **No scope concern.**

---

## Local Checks Summary

| Check | Command | Result |
|---|---|---|
| F — Grep for spend-cap tokens | `git grep -nE '...'` | 0 hits (exit 1) |
| G — Unit tests | `uv run pytest tests/unit/test_run_phase4b_variance.py -v` | 29 passed |
| G — Full test suite | `uv run pytest` | 1204 passed |
| G — mypy | `uv run mypy packages/` | 55 files, 0 issues |
| Ruff | `uv run ruff check scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py` | All checks passed |
| Dry-run | `uv run python scripts/run_phase4b_variance.py --dry-run` | 20 models OK, no cost lines |
| Secrets | `grep -nE "sk-...\|Bearer...\|hooks.slack.com"` | 0 hits |
| Vocab | `grep -nE "(believes\|thinks\|worldview\|...)"` | 0 hits |

---

## Commit Message Hygiene

Subject: `fix(collect): SC-T1 strip spend-cap mechanism from variance driver`
Character count: 60 (under 72 limit). Conventional Commits type `fix` with
scope `collect`. Body references the architect plan path, the task ID (SC-T1),
and explicitly documents the 32 → 29 test-count drop with per-test explanation.
**PASS.**

---

## Verdict: PASS

All nine binding checks pass or are N/A. All SC-T1-specific Reviewer items
(A through G) pass. The Coder's scope deviation (removal of
`load_registry_map`, `REGISTRY_PATH`, orphaned imports) is confirmed legitimate.
Registry validation is unaffected. Dry-run produces a clean plan summary with
zero cost framing. 29 unit tests pass; full 1204-test suite passes. Ruff and
mypy clean.

**Tester is next.** The orchestrator may proceed to dispatch the Tester agent
for SC-T1 and may launch Phase 4b T4 in parallel per the architect plan §9.

---

*Verdict filed by LSB Reviewer agent (Sonnet 4.6). Only Mark can override a FAIL.*
