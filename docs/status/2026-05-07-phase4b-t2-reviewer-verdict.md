# Reviewer Verdict — Phase 4b T2

**Filed:** 2026-05-07
**Reviewer:** LSB Reviewer (Sonnet 4.6)
**Commit reviewed:** `628497d` — `feat(collect): phi-4 adaptive max_tokens + 5-cell rerun (Phase 4b T2)`
**Files changed:** 4 (adaptive_cap.py new, openrouter.py modified, rerun_phi4_phase4b_t2.py new, test_adaptive_cap.py new)
**Companion docs read:** CLAUDE.md §6–§7–§9–§11, ARCHITECTURE.md §1.5, SECURITY_AND_HARDENING.md §9 (R1–R12)

---

## Nine-Check Scorecard

```
REVIEWER VERDICT: PASS-WITH-NOTES

Check 1 — No LLM imports in cdb_analyze/:  PASS
Check 2 — Append-only JSONL:               PASS
Check 3 — No secrets:                      PASS
Check 4 — Forbidden vocabulary:            PASS
Check 5 — Schema + DATA_DICTIONARY:        N/A
Check 6 — New deps sign-off:               PASS
Check 7 — Prompt versioning:               N/A
Check 8 — Uncertainty in viz:              N/A
Check 9 — Prerequisite verdicts:           PASS
```

---

## Check 1 — No LLM imports in cdb_analyze/

**PASS.**

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returns only two comment lines in `cdb_analyze/__init__.py` (the standing "NO LLM CALLS PERMITTED" warning block, not actual import statements). No new LLM client imports introduced. The adaptive cap helper lives in `packages/cdb_collect/cdb_collect/adaptive_cap.py` — the correct package. The adapter wiring lives in `packages/cdb_collect/cdb_collect/adapters/openrouter.py`. Neither module crossed the collect/analyze boundary.

---

## Check 2 — Append-only JSONL

**PASS.**

`data/raw/informants.jsonl` is not tracked in git (runtime data file on disk). The commit stat shows 0 changes to any JSONL file — the 5 rerun rows were appended at runtime by the rerun script, not committed to git. The original rows are undisturbed: `wc -l` shows 126 total rows; the 5 new rows all carry `campaign_id=phase4b-phi4-rerun-2026-05-07` in `qa_notes`. Pre-existing rows were not touched.

`data/raw/failures.jsonl` was not modified: 6 phi-4 failure rows remain intact (confirmed by `grep -c 'microsoft/phi-4' data/raw/failures.jsonl` = 6).

---

## Check 3 — No secrets

**PASS.**

The commit diff contains one reference to `OPENROUTER_API_KEY`: it is `os.environ.get("OPENROUTER_API_KEY", "")` in `openrouter.py` — a pre-existing env-var lookup pattern, not a committed credential value. No API key literals, no webhook URLs (`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`), no tokens or passwords in any changed file.

---

## Check 4 — Forbidden vocabulary

**PASS.**

Full scan of the commit diff for CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
- `worldview`, `believes`, `thinks` (applied to models): NONE
- `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`: NONE
- `publishable` (for LSB findings): NONE
- `cultural bias` (standalone): NONE
- `what the model understands`, `how models see the world`, `model X believes...`, `model X thinks of...`: NONE
- `model X's worldview`: NONE

Commit message, docstrings, comments, and test descriptions all clear. No vocabulary violations detected.

---

## Check 5 — Schema + DATA_DICTIONARY

**N/A.**

`cdb_core/schemas.py` was not changed in this commit (confirmed via `git show 628497d -- packages/cdb_core/cdb_core/schemas.py` returns empty). No `InformantRecord`, `DomainResult`, `GroundingRef`, or `BootstrapEllipse` modifications. No `DATA_DICTIONARY.md` update required.

---

## Check 6 — New dependencies sign-off

**PASS.**

`pyproject.toml` was not changed in this commit. `uv.lock` was not changed. The adaptive cap helper uses only Python stdlib (`math`, `__future__`). No new top-level dependency was added to either the Python or npm dependency trees.

---

## Check 7 — Prompt versioning

**N/A.**

No prompt templates under `packages/cdb_collect/prompts/` were changed. The rerun uses the existing v1 prompts (and v1_s* variants for runs that had them). No in-place edits to versioned prompt directories.

---

## Check 8 — Uncertainty in visualizations

**N/A.**

This PR contains no frontend work. No new visualization components were added. No `apps/dashboard/` files were touched.

---

## Check 9 — Prerequisite verdicts

**PASS.**

Phase 4b plan-level CDA SME verdict: PASS-WITH-NOTES, filed at `docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md`. The verdict explicitly authorizes T2: "T2 and T3 may proceed after T1." T1 has a Reviewer PASS (`docs/status/2026-05-07-phase4b-t1-reviewer-verdict.md`) and a Tester PASS (`docs/status/2026-05-07-phase4b-t1-tester-verdict.md`). All prerequisite gates are satisfied for T2 dispatch.

T2 is an operational infrastructure task (adaptive cap helper + rerun), not a methodology task requiring a dedicated CDA SME content verdict. The plan verdict covers it.

---

## Adaptive Cap Correctness Assessment

**Formula implementation:** The helper in `packages/cdb_collect/cdb_collect/adaptive_cap.py` correctly implements:

```
estimated_input = ceil(len(prompt_text) / 4.0)
budget = context_length - estimated_input - safety_margin
effective = min(max_output_tokens_config, max(min_output_tokens, budget))
```

Constants match the plan §7.1 spec: `MAX_OUTPUT_TOKENS_CONFIG=16384`, `_SAFETY_MARGIN=512`, `MIN_OUTPUT_TOKENS=1024`.

**Tokenizer decision:** The module intentionally omits tokenizer-based estimation, using the 4-chars-per-token approximation unconditionally across all providers. This is defensible: LSB calls models across providers with different tokenizers; a conservative single approximation that slightly over-estimates input tokens is the safe direction (the output budget is marginally smaller than optimal, but it never overflows the context window). The docstring documents this tradeoff explicitly.

**Phi-4 case:** `compute_effective_max_tokens("x"*8000, context_length=16384)` → `16384 - 2000 - 512 = 13872`. Confirmed correct and within the plan's "~13.5K" range. The 18-test suite passes this and all boundary/floor/idempotence/override cases. All 18 tests pass independently verified (1171 total suite passes, up from 1153 baseline as reported by Coder — +18 confirms exact test count).

**Stateless / pure function:** Confirmed. No I/O, no side effects, no global mutation. The function imports `math` locally (inside function body at line 105). This is a minor style point (the import would conventionally appear at the module level) but is not a bug: `math` is stdlib, no import cost, the function remains pure and testable.

**Type hints / mypy:** `mypy packages/cdb_collect/cdb_collect/adaptive_cap.py` reports "Success: no issues found in 2 source files." All parameters and return type are annotated.

---

## Adapter Wiring Assessment

**PASS.**

`OpenRouterAdapter.__init__` gains an optional `context_length: int | None = None` parameter. When `None` (all existing callers), the internal `_context_length` is set to `MAX_OUTPUT_TOKENS_CONFIG * 100 = 1,638,400` — effectively unconstrained. `compute_effective_max_tokens(prompt, 1638400)` always returns `MAX_OUTPUT_TOKENS_CONFIG` (16384) for any realistic prompt, preserving the Task #16 flat-cap behavior for all current models.

`_do_call()` computes `effective_max_tokens = compute_effective_max_tokens(prompt_text=prompt, context_length=self._context_length)` per-call, with the current prompt. This is the correct location: the computation uses the actual prompt being sent, not a cached or stale estimate.

The rerun script at `scripts/rerun_phi4_phase4b_t2.py` passes `context_length=phi4_context_length` (read from `data/models/registry.json`) to `OpenRouterAdapter`, so phi-4 cells get the adaptive cap. All other production callers are unaffected.

**Pre-existing max_tokens record issue (NOTED, NOT A T2 REGRESSION):** The `InformantRecord.max_tokens` field is hardcoded to `4096` in `runner.py` line 238 (`max_tokens=4096, # see docs/status/2026-04-22-phase4a-adapter-fix-verdict.md`). This means the 5 rerun records store `max_tokens=4096` even though the actual API call used ~13872. This is a pre-existing data accuracy gap introduced before T2 (not in commit `628497d` — `runner.py` was not changed). The actual effective cap is nonetheless computed correctly in the adapter and sent to the API. This discrepancy should be addressed in a future task as a data-accuracy cleanup (runner.py should record the actual per-call max_tokens rather than a nominal constant), but it is not a T2 regression and does not block this verdict.

---

## 5-Cell Rerun Outcomes — Failures-as-Findings Posture

**PASS.**

Campaign ID `phase4b-phi4-rerun-2026-05-07` confirmed in informants.jsonl via `grep -c` = 5 rows.

| run_index | domain_slug | qa_passed | qa_notes (excerpt) |
|---|---|---|---|
| 0 | family | True | campaign_id=phase4b-phi4-rerun-2026-05-07 |
| 1 | family | False | label_count_mismatch:20/24; campaign_id=... |
| 2 | family | False | label_count_mismatch:5/0; campaign_id=... |
| 3 | family | False | label_count_mismatch:24/6; campaign_id=... |
| 4 | family | True | campaign_id=phase4b-phi4-rerun-2026-05-07 |

2/5 `qa_passed=True`, 3/5 `qa_passed=False` with `label_count_mismatch`.

**Failures-as-findings posture is correct.** CLAUDE.md §9 pitfall 4 and §1 commitment 8 require that failed/refused/partial runs be preserved verbatim. The 3 QA-failed cells are in `informants.jsonl` with `qa_passed=False` and verbatim capture intact — not in `failures.jsonl`. This is the right posture: the data is preserved, the QA failure is documented as a finding (phi-4 output characteristic: pile-interview label counts don't match pile counts), and no data is suppressed.

The `label_count_mismatch` QA failures are phi-4 output behavior, not a schema regression or an adaptive-cap malfunction. The runs succeeded (200 OK from the API, records assembled), but phi-4's pile interview responses contain label counts that don't match the actual pile structure. This is a finding to surface in T7 (completion report), not a T2 defect.

**5-vs-6 disposition:** The 6 `failures.jsonl` rows represent 5 unique `(model_id, domain_slug, run_index)` cells — 5 × HTTPStatusError + 1 × ValueError on the same `(phi-4, family, 4)` cell. Running the 5 unique cells is the correct unit of work. The 6th failure row is a duplicate key; the single rerun of `(phi-4, family, 4)` closes both failure rows. This is methodologically defensible.

---

## Commit Hygiene

**PASS.**

- Subject line: `feat(collect): phi-4 adaptive max_tokens + 5-cell rerun (Phase 4b T2)` — 66 chars, within the 72-char limit. Conventional Commits format with correct scope (`collect`).
- Body: references plan §7.1, CDA SME verdict, recovery report §7.4 forward-carry, Task #16 predecessor, placement rationale, test count (18), rerun outcomes (5/5 recovered, 3/5 `qa_passed=False`), actual cost ($0.0032).
- Gate verdict references: both the architect plan and the CDA SME plan verdict are cited by file path. T1 Reviewer + Tester verdicts are in docs/status/ and confirm the T1 prerequisite was satisfied before T2.

---

## Notes for Tester (T2)

The Tester should verify:

1. All 18 tests in `tests/unit/test_adaptive_cap.py` pass.
2. `test_adapter_context_length_default_is_unconstrained` and `test_adapter_phi4_context_length_produces_reduced_cap` confirm adapter wiring without real API calls.
3. The `_context_length` attribute is accessible on `OpenRouterAdapter` instances (the tests inspect it directly; Tester may confirm this is an intended public-enough attribute for the wiring tests).
4. Confirm the pre-existing `max_tokens=4096` hardcode in `runner.py` is noted in a follow-up task (data accuracy cleanup) — the Tester is not required to fix it, but should confirm the note is surfaced.

## Notes for SME Content Review (T7)

The 3/5 `label_count_mismatch` outcomes on phi-4 (runs 1, 2, 3) are phi-4 output characteristics that should be documented in the T7 completion report as a per-model behavioral note. Specifically:

- Run 2 shows `label_count_mismatch:5/0` which is extreme (pile interview returns 5 labels but 0 piles were named, or vice versa). This warrants a per-run inspection in T7.
- The T7 prose must not use forbidden vocabulary when discussing these failures (no "phi-4 failed to understand", no "phi-4 believes its piles are...").
- These are `qa_passed=False` records and should be treated as data, not excluded from the corpus.

---

## VERDICT: PASS-WITH-NOTES

**The PR passes all nine binding checks.** The adaptive cap helper is correctly implemented, stateless, pure, and fully unit-tested. Adapter wiring is correct: phi-4 gets the adaptive cap (~13872 effective max_tokens for a ~2K-token prompt), all existing callers are unaffected. The 5-cell rerun produced 5 rows in `informants.jsonl` with the correct campaign_id, correct failures-as-findings posture (3 QA-failed records preserved verbatim, not suppressed). No secrets, no forbidden vocabulary, no LLM imports in cdb_analyze, no schema changes, no new dependencies, no prompt template edits.

**Notes (non-blocking, addressed in future tasks):**

1. **NOTED (future task):** `runner.py` line 238 hardcodes `max_tokens=4096` in the `InformantRecord`, meaning the stored `max_tokens` field does not reflect the actual per-call adaptive value (~13872 for phi-4). This is a pre-existing data accuracy gap, not a T2 regression. A future task should update `runner.py` to record the actual effective max_tokens computed by the adapter, so the InformantRecord accurately reflects what was sent to the API. This does not block T2 merge or Tester dispatch.

2. **NOTED (T7):** The 3/5 `label_count_mismatch` outcomes, especially run 2's `5/0` pattern, warrant specific per-run inspection and documentation in the T7 completion report.

**Coder may merge. Tester is next.**
