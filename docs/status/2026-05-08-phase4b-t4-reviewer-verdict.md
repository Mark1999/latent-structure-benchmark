# Reviewer Verdict — Phase 4b T4 (Variance-Arm Campaign Driver)

**Date:** 2026-05-08
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `e3da1c6`
**Commit subject:** `feat(collect): Phase 4b T4 variance-arm campaign driver`
**Scope:** New script `scripts/run_phase4b_variance.py` (~1,254 lines) and
`tests/unit/test_run_phase4b_variance.py` (27 unit tests).

**Prerequisite gate verdict:**
`docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md` — PASS-WITH-NOTES.
The verdict body explicitly authorizes T4: "T4 (the main 20×8 variance run)
is gated only by T1 / T2 / T3 landing as plan-specified." T1, T2, and T3
are closed with Reviewer + Tester PASS verdicts. Gate satisfied.

---

## REVIEWER VERDICT: PASS

---

## 9-Check Scorecard (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

| Check | Description | Result |
|---|---|---|
| Check 1 | No LLM client imports in `cdb_analyze/` | PASS |
| Check 2 | `informants.jsonl` append-only invariant | PASS |
| Check 3 | No API keys or secrets in committed files | PASS |
| Check 4 | No forbidden vocabulary | PASS |
| Check 5 | Schema changes co-update `DATA_DICTIONARY.md` | N/A |
| Check 6 | No new dependencies without Architect sign-off | PASS (N/A) |
| Check 7 | Prompt templates versioned correctly | PASS (N/A) |
| Check 8 | No point estimates without uncertainty in visualizations | N/A |
| Check 9 | Prerequisite gate verdicts present | PASS |

---

## Detailed Check Results

### Check 1 — No LLM client imports in `cdb_analyze/`

```
grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/
```

Result: Two hits in `packages/cdb_analyze/cdb_analyze/__init__.py` lines 12–13.
Both are comment lines documenting the prohibition — not import statements.
No actual LLM client imports exist anywhere under `packages/cdb_analyze/`.

The new script lives in `scripts/` and imports only from `cdb_collect` and
`dotenv`. The test file has no LLM imports. **PASS.**

### Check 2 — `informants.jsonl` append-only invariant

`git diff 9471972..e3da1c6 --name-only` shows only two files changed:
`scripts/run_phase4b_variance.py` and `tests/unit/test_run_phase4b_variance.py`.
`data/raw/informants.jsonl` is not in the diff.

The script writes to `informants.jsonl` exclusively via `append_record()` from
`cdb_collect.jsonl`, which opens the file in `"a"` (append) mode (confirmed at
`packages/cdb_collect/cdb_collect/jsonl.py` line 22). The failures path is
written via `append_failure()` which also opens in `"a"` mode (line 123).
The `count_completed_cells()` and `compute_success_rates()` functions open
both files read-only (standard `open(..., encoding="utf-8")` with no write
mode). No code path seeks or rewrites existing lines. **PASS.**

### Check 3 — No API keys or secrets in committed files

```
grep -nE "sk-[a-zA-Z0-9]+|Bearer [a-zA-Z0-9]+|hooks\.slack\.com" scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Zero hits across both files. No `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`,
`LSB_UI_UX_WEBHOOK_URL`, or any credential-shaped string present. **PASS.**

### Check 4 — No forbidden vocabulary

Full scan per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4:

```
grep -nE "(believes|thinks|worldview|recognizes|interprets|perceives|publishable)" scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```

Zero hits. Extended vocabulary per ARCHITECTURE.md §1.5.4 SME additions also
checked: "within-model consensus", "within-model cultural consensus",
"within-model eigenratio", "within-model CCM" — zero hits.

Commit message scanned: "20 models × 9 variants × 5 runs × 2 domains = 1,800
target cells. Script implements per-provider preflight, resume-from-existing,
$50/session spend cap, P2 success-rate computation, P5 no-mid-flight
discipline." — zero forbidden vocabulary. **PASS.**

### Check 5 — Schema + DATA_DICTIONARY.md

```
git diff 9471972..e3da1c6 -- packages/cdb_core/cdb_core/schemas.py
```

No output. No schema changes in this commit. **N/A.**

### Check 6 — No new dependencies

```
git diff 9471972..e3da1c6 -- pyproject.toml uv.lock
```

No output. No new Python dependencies introduced. The script imports only from
`cdb_collect`, `cdb_core`, `dotenv`, and stdlib. All are pre-existing. **N/A (PASS).**

### Check 7 — Prompt template versioning

```
git diff 9471972..e3da1c6 -- packages/cdb_collect/cdb_collect/prompts/
```

No output. No prompt template directories added or modified. `VARIANCE_PROMPT_VERSIONS`
is a fixed list of pre-existing directory names (`v1_s1`–`v1_s8`, `v2_soft1`)
defined at module level (line 128); no runtime injection. **N/A (PASS). P5 satisfied.**

### Check 8 — Uncertainty in visualizations

Non-frontend PR. The script produces tabular JSONL/log output and terminal
progress lines. No visualization components introduced. **N/A.**

### Check 9 — Prerequisite gate verdicts present

Non-frontend task — UI/UX gate not required. This is a data-collection driver
script, not methodology text — no per-T4 CDA SME content gate is required
(the plan verdict PASS-WITH-NOTES explicitly authorizes T4 dispatch after
T1/T2/T3 land). T1, T2, T3 all have Reviewer + Tester PASS verdicts on file.
The commit body references the correct plan path and SME plan verdict path.
**PASS.**

---

## Plan-Specific Obligation Checks (from task specification)

### Item 1 — No LLM imports in `cdb_analyze/`
Verified above. **PASS.**

### Item 2 — Append-only `informants.jsonl`
Verified above; writes via `append_record()`/`append_failure()` in append mode;
reads are read-only. **PASS.**

### Item 3 — No new dependencies
Verified above. **PASS.**

### Item 4 — No schema changes to `cdb_core/schemas.py`
Verified above: zero diff on `schemas.py`. **PASS.**

### Item 5 — No edits to existing prompt templates
Verified above: zero diff on `packages/cdb_collect/cdb_collect/prompts/`.
`VARIANCE_PROMPT_VERSIONS` is a fixed constant, not a runtime-injected value. **PASS.**

### Item 6 — No real API calls in tests
All 27 tests use synthetic inline dicts as fixtures. API calls are mocked
via `unittest.mock.patch`:
- `test_preflight_excludes_all_models_of_quota_exhausted_provider` patches
  `run_phase4b_variance._check_provider_available`
- `test_preflight_dry_run_returns_all_models` patches with an
  `AssertionError` side-effect to confirm the probe is never called
- `test_preflight_all_providers_healthy` and `test_preflight_openai_quota_exhausted`
  patch with `return_value=True` / mock function
No direct provider client instantiation found. **PASS.**

### Item 7 — No API keys in code
Verified by grep. Zero hits for `sk-`, `Bearer`, `hooks.slack.com` patterns. **PASS.**

### Item 8 — No forbidden vocabulary
Verified above. **PASS.**

### Item 9 — No point estimates without uncertainty in visualizations
No visualizations in this PR. The success-rate output is a terminal table with
`passed`, `failed`, and `n_attempts_targeted` columns — the denominator context
is present in every row. **N/A.**

### Item 10 — `max_tokens` not hardcoded to 4096
Grep for `4096` in `scripts/run_phase4b_variance.py`: zero hits. The script
calls `run_informant()` from `cdb_collect.runner` (line 479–485), which has
used the post-fix `max_tokens_used` field since commit `75917d0`. The campaign
driver inherits the fixed behaviour without re-introducing the hardcode. **PASS.**

### Item 11 — `model_id` vs `model_version_returned` discipline
The campaign driver tracks cells by `(model_id, prompt_version, domain)` triples,
which is correct: the variance arm groups by `model_id` per the plan §3 CLAUDE.md
§9 pitfall 1 framing. Recording of `model_version_returned` happens inside
`run_informant()` in the runner (line 224 of `runner.py`: the runner reads the
provider's returned version string and stores it on the `InformantRecord`). The
driver does not suppress or override that field. Test fixture at line 59 includes
`"model_version_returned": f"{model_id}-returned"` confirming both fields are
represented. **PASS.**

### Item 12 — Per-provider preflight with 429 detection
`_check_provider_available()` (lines 282–322) issues a probe and returns `False`
for any response containing `"429"`, `"quota"`, `"rate limit"`,
`"too many requests"`, or `"resource_exhausted"` in the exception string.
`run_preflight()` (lines 325–364) excludes all models on a quota-exhausted
provider. Unit test `test_preflight_excludes_all_models_of_quota_exhausted_provider`
confirms this logic. **PASS.**

### Item 13 — Idempotent / resume-from-existing
`count_completed_cells()` (lines 371–436) scans both `informants.jsonl` and
`failures.jsonl` for the `campaign_marker` substring before building the run
plan. `build_run_plan()` (lines 443–461) skips triples with `n >= N_RUNS_PER_CELL`
completions. The idempotence check runs at startup before any API call is issued.
Six unit tests cover resume/skip behaviour. **PASS.**

### Item 14 — Spend cap via `CDB_MAX_SPEND_USD`
`DEFAULT_MAX_SPEND_USD = 50.0` (line 153). Loaded at startup:
`max_spend_usd = float(os.environ.get("CDB_MAX_SPEND_USD", DEFAULT_MAX_SPEND_USD))`
(line 981). Spend cap is checked in each `provider_worker` thread before every
cell (lines 664–675); when crossed the worker exits and main returns exit code 3.
**PASS.**

### Item 15 — Retry budget = 2 per cell
`MAX_ATTEMPTS_PER_CELL: int = 2` (line 147). The retry loop in `run_cell()`
iterates `range(1, MAX_ATTEMPTS_PER_CELL + 1)` (line 515). After two failed
attempts the failure is appended to `failures.jsonl`. **PASS.**

### Item 16 — `campaign_id=phase4b-real-2026-05-{MM}` substring in `qa_notes`
The campaign_id is set at runtime: `campaign_id = f"phase4b-real-{today}"`
where `today = datetime.now(tz=UTC).strftime("%Y-%m-%d")` (lines 975–976). On
launch on 2026-05-08 this produces `phase4b-real-2026-05-08`, which contains
the SME-approved `phase4b-real-2026-05` substring per Q6 ruling. The
`campaign_marker = f"campaign_id={campaign_id}"` string (line 978) is used for
idempotence matching and will appear in `qa_notes` via the `campaign_id=`
argument passed to `run_informant()`. **PASS.**

### Item 17 — P2 success-rate definition alignment
`compute_success_rates()` (lines 704–803) implements exactly the P2-bound
definition:
- Successful: `InformantRecord` in `informants.jsonl` with `qa_passed=True`
  AND campaign_marker in `qa_notes`
- Failed: record in `failures.jsonl` OR `InformantRecord` with `qa_passed=False`
- Denominator: `n_attempts_targeted=5` (the fixed `N_RUNS_PER_CELL` constant)

Unit test `test_success_rate_qa_failed_informant_counted_as_failed` explicitly
verifies the qa_passed=False-as-failed case. **PASS.**

### Item 18 — P5 no mid-flight prompt iteration
`VARIANCE_PROMPT_VERSIONS` is a fixed module-level constant (line 128); no
CLI argument, no environment variable, and no runtime code path can modify it.
No new prompt-version directories appear in the diff (verified in Check 7).
**PASS.**

### Item 19 — Append-only PROMPT_EVOLUTION_LOG.md update
`append_success_rates_to_log()` (lines 810–883) reads the existing file content
with `log_path.read_text()`, walks the lines, and inserts new rows only at the
placeholder marker `"*(Phase 4b T4 — pending)*"`. It never removes or modifies
any line that does not match the insertion point. **PASS.**

---

## Local Checks

```
uv run pytest tests/unit/test_run_phase4b_variance.py -v
```
Result: **27 passed** in 0.79 s.

```
uv run ruff check scripts/run_phase4b_variance.py tests/unit/test_run_phase4b_variance.py
```
Result: **All checks passed.**

```
git diff 9471972..e3da1c6 -- packages/cdb_core/cdb_core/schemas.py
git diff 9471972..e3da1c6 -- pyproject.toml uv.lock
git diff 9471972..e3da1c6 -- packages/cdb_collect/cdb_collect/prompts/
```
All produce no output.

---

## Commit Message Hygiene

Subject line: `feat(collect): Phase 4b T4 variance-arm campaign driver`
Character count: 54 (under 72 limit — PASS).
Conventional Commits type `feat` with scope `collect` — PASS.
Body references plan path (`docs/status/2026-05-07-phase4b-architect-plan.md §8 T4`)
and SME verdict path (`docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md
(PASS-WITH-NOTES, P1-P8)`) — PASS.

---

## Verdict: PASS

All nine binding checks pass or are N/A. All 19 plan-specific obligation checks
pass. 27 unit tests pass. Ruff clean. No schema changes. No new dependencies.
No LLM imports. No secrets. No forbidden vocabulary.

**Tester is next.** Mark may dispatch the Tester agent for the full test-suite
run confirmation. Live launch of the campaign on Linode proceeds via the
orchestrator separately, per the commit body.

---

*Verdict filed by LSB Reviewer agent (Sonnet 4.6). Only Mark can override a FAIL.*
