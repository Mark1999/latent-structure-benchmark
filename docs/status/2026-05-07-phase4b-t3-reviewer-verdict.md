# Reviewer Verdict — Phase 4b T3 (Tail Failures Diagnostic)

**Date:** 2026-05-07
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `d5cd30c`
**Commit subject:** `diag(collect): T3 unexplained-failures investigation (Phase 4b)`
**Scope:** Root-cause investigation and re-attempt of 3 Phase 4a failures
(2× `openai/gpt-5.4-mini` family, 1× `mistralai/mistral-small-2603` holidays).

**Prerequisite gate verdict:**
`docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md` — PASS-WITH-NOTES.
The verdict body explicitly authorizes T3: "T2 and T3 may proceed after T1."
T1 and T2 are closed (Reviewer + Tester PASS verdicts on file). Gate satisfied.

---

## REVIEWER VERDICT: PASS-WITH-NOTES

---

## 15-Rule Scorecard (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

| Check | Description | Result |
|---|---|---|
| Check 1 | No LLM client imports in `cdb_analyze/` | PASS |
| Check 2 | `informants.jsonl` append-only invariant | PASS |
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

Grep command run:

```
grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/
```

Result: Two hits in `packages/cdb_analyze/cdb_analyze/__init__.py` lines 12–13.
Both are comment lines documenting the prohibition, not import statements. No
actual import statements of any LLM client library found in any `.py` file under
`packages/cdb_analyze/`. **PASS.**

The rerun script (`scripts/rerun_t3_unexplained_phase4b.py`) correctly lives in
`scripts/` and imports from `cdb_collect` only. No LLM client imports present.

### Check 2 — `informants.jsonl` append-only invariant

`data/raw/` is in `.gitignore` and is not tracked by git. The append-only
invariant was verified by inspecting the live files directly:

```
grep -c 'phase4b-tail-rerun-2026-05-07' data/raw/informants.jsonl
# Result: 1  (expected: 1)

grep -c 'phase4b-tail-rerun-2026-05-07' data/raw/failures.jsonl
# Result: 2  (expected: 2)

grep -c 'f9cd5a4942550e8d' data/raw/informants.jsonl
# Result: 1  (mistral-small recovery record confirmed present)
```

The rerun script opens files via `append_record()` / `append_failure()` helpers
from `cdb_collect.jsonl`, which open in append mode. No code path in the script
reads, seeks, or rewrites existing lines. The idempotence check reads line-by-line
but does not write. **PASS.**

### Check 3 — No API keys or secrets in committed files

Grep scan for API keys, tokens, webhook URLs (`LSB_ALERTS_WEBHOOK_URL`,
`LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`), `sk-`, `ghp_`, `xoxb-`,
`hooks.slack.com` across both changed files: zero hits. **PASS.**

### Check 4 — Forbidden vocabulary

Full CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 scan on both changed files:

```
grep -E "worldview|believes|thinks|cultural bias|sees the world|what the model understands|
within-model consensus|within-model cultural|within-model eigenratio|within-model CCM|
publishable|Model X believes|Model X thinks" \
  docs/status/2026-05-07-phase4b-t3-tail-failures-memo.md \
  scripts/rerun_t3_unexplained_phase4b.py
```

Zero hits. Commit message body also reviewed: zero hits.

Extended scan per the task specification:

```
grep -E "could not see|was blind to|didn't know|the model recognized that|
the model identified the failure as|the model's understanding|the model's interpretation" \
  docs/status/2026-05-07-phase4b-t3-tail-failures-memo.md
```

Zero hits. The memo describes all events in operational, factual terms. The
OpenAI 429 error is documented as "provider billing quota exhaustion," not as
any model-state characterization. The mistral-small recovery is classified as
"non-deterministic model-side item omission" — a statistical behavior
description, not a cognitive attribution. **PASS.**

### Check 5 — Schema + DATA_DICTIONARY N/A

`git diff d5cd30c^ d5cd30c -- packages/cdb_core/cdb_core/schemas.py` produces
no output. No schema changes. **N/A.**

### Check 6 — No new dependencies N/A

`git diff d5cd30c^ d5cd30c -- pyproject.toml uv.lock` produces no output.
No dependency changes. **N/A.**

### Check 7 — Prompt versioning N/A

`git diff d5cd30c^ d5cd30c -- packages/cdb_collect/cdb_collect/prompts/`
produces no output. No prompt template changes. **N/A.**

### Check 8 — Uncertainty in viz N/A

Non-frontend PR. No visualization code introduced. **N/A.**

### Check 9 — Prerequisite gate verdicts present

This is a non-frontend, methodology-adjacent (diagnostic/operational) task.
The CDA SME PASS-WITH-NOTES verdict for the Phase 4b plan is on file at
`docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md` and explicitly
authorizes T3 dispatch. The commit body references "Phase 4b Architect plan
§7.2 + SME plan verdict (PASS-WITH-NOTES)." T1 and T2 prerequisite commits
are closed with Reviewer + Tester PASS verdicts. **PASS.**

---

## Memo Content Compliance

### Structure

Sections §1–§5 present and complete:
- §1 Header: instrument state, date, Stage 1.5b confirmation — present.
- §2 The Three Cells: per-cell tables with model_id, domain, run_index,
  original error info (timestamp, error_type, error_message, failures.jsonl
  line) — present. Note: `original request_id` and `original response_verbatim`
  are documented as "(not recorded in failures.jsonl — pre-verbatim-capture),"
  which is accurate and factually correct. Not a defect.
- §3 Diagnostic Re-attempt: per-cell rerun outcomes with campaign_id, retry
  budget, CDB_MAX_SPEND_USD guard, root-cause classification — present.
- §4 Disposition: corpus delta tables, coverage summary — present.
- §5 Forward Carry: OpenAI quota finding, no-adapter-bugs finding,
  no-parser-bugs finding — present.

### Root-cause classification

All three cells carry the required classification:
- Cell A: (a) transport/API — billing quota exhaustion
- Cell B: (a) transport/API — billing quota exhaustion (same event)
- Cell C: (b) non-deterministic model-side item omission, non-recurring

### Voice

Factual and neutral throughout. No speculative interpretation beyond verbatim
data. The 429 finding is stated as an operational billing-state event, not
attributed to model behavior. The Cell C recovery is stated as a single-
occurrence omission that did not recur, not as a claim about model reliability.

### T8 (descriptive shape) / T9 (no softer-than-thinks verbs)

No causal or introspective framing found. All descriptions are observational.
No verbs weaker than "produced," "returned," "completed," "failed." T8 and T9
honored.

### OpenAI 429 finding documented as operational fact

§5 explicitly documents: "The 2026-05-07 HTTP 429 failures are a billing-quota
state on the OpenAI account at the time of the T3 re-attempt, not a persistent
model behavior issue." Disposition noted: "Whether to schedule this re-attempt
depends on whether n=3 is sufficient for the Phase 4b G1 variance-arm analysis.
This is an Architect-scoped decision, not T3 scope." Correctly escalated.

---

## Cell-Tagging Verification

| File | Expected | Actual | Result |
|---|---|---|---|
| `data/raw/informants.jsonl` (campaign tag count) | 1 | 1 | PASS |
| `data/raw/failures.jsonl` (campaign tag count) | 2 | 2 | PASS |
| `data/raw/informants.jsonl` (informant_id f9cd5a4942550e8d) | 1 | 1 | PASS |

---

## Test Gate (Independent Verification)

`uv run pytest --tb=no -q` result: **1175 passed** (matches Coder's report of
1175 unchanged from baseline). Ruff check on new script: clean.
`uv run mypy packages/`: **0 errors in 55 source files** (the packages/ scope
is the standard scope per CLAUDE.md §11). Two mypy issues exist if the script
is checked in isolation (`import-not-found` for `collect`, `arg-type` for
`append_record` return type), but these are pre-existing patterns common to
run scripts in this repo and are not a regression introduced by this commit.

---

## Commit Message Hygiene

Subject line: `diag(collect): T3 unexplained-failures investigation (Phase 4b)`
Character count: 63 (under 72 limit — PASS).

**NOTE (for Mark's awareness):** The `diag` type is not in the canonical list
in CLAUDE.md §8 (`feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`,
`perf`). The commit body is otherwise exemplary — references the plan section
(§7.2), recovery report (§7.3), all three cells with outcomes, cost, hard-stop
guard, and verdict file path. The Reviewer rates this as a minor stylistic
deviation, not a blocking violation. The nearest canonical equivalent would be
`chore(collect):`. No re-commit required; flagged for information only.

---

## OpenAI Billing Quota — Forward-Carry Note for Mark

The 2026-05-07 HTTP 429 failures are a billing-quota state on the OpenAI
account at the time of re-attempt, not a model behavior defect or adapter bug.
Three LSB models route through the OpenAI-compat adapter: `openai/gpt-5.4`,
`openai/gpt-5.4-mini`, and `openai/gpt-5.2`. If the quota applies to the
OpenAI account (not the OpenRouter path), all three models are blocked from
direct-API collection until the billing cycle resets or the plan is upgraded.

The two affected cells (`openai/gpt-5.4-mini` × family × run_index ∈ {0, 2})
remain in `failures.jsonl` per the failures-as-findings posture. `gpt-5.4-mini`
has n=3 valid family-domain records (runs 1, 3, 4), which may be sufficient for
Phase 4b G1 variance-arm analysis. Whether to schedule a re-attempt after
quota restoration is an Architect-scoped decision. T3 is complete regardless.

---

## Notes for Coder (PASS-WITH-NOTES)

N1. **Commit type.** `diag` is not in the CLAUDE.md §8 canonical list. Future
diagnostic commits should use `chore(scope):` or `fix(scope):` depending on
whether the investigation produced a fix. No re-commit required for T3.

N2. **CDB_MAX_SPEND_USD programmatic check.** The script documents the guard
in the usage block and memo but does not enforce it programmatically at
`main()` startup (e.g., `if not os.environ.get("CDB_MAX_SPEND_USD"): sys.exit(1)`).
This matches the predecessor script's pattern and is therefore not a new
regression. Future recovery scripts should add the programmatic check.
No re-commit required for T3.

---

## Verdict: PASS-WITH-NOTES

All nine binding checks pass or are N/A. Two notes (N1 commit type, N2 spend
guard pattern) are documentation/style observations that do not block merge
and require no re-commit for T3. The notes are forward-carry guidance for
future scripts.

**Tester is next.** Mark decides separately on T4 dispatch and the OpenAI
quota remediation path.

---

*Verdict filed by LSB Reviewer agent (Sonnet 4.6). Only Mark can override a FAIL.*
