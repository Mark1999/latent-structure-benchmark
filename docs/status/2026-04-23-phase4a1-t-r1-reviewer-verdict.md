# Reviewer Verdict — Phase 4a.1 T-R1: correct `_is_recursive_decline()` for output-classification role

**Date:** 2026-05-04
**Reviewer:** LSB Reviewer (Sonnet)
**Commit:** `ce3da31`
**Task:** Phase 4a.1 T-R1 (#21.T-R1)
**Spec sources:**
- `docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md` Q1 (binding spec)
- `docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md` §2 T-R1 (acceptance criteria + test cases)

---

## VERDICT: PASS-WITH-NOTES

One cosmetic note (non-blocking). All nine binding checks pass. All 27 item-level checks pass or are N/A. Coder may merge; note below is advisory and does not require a follow-up commit before the next task (T-R2).

---

## Nine binding checks

```
REVIEWER VERDICT: PASS-WITH-NOTES

Check 1 — No LLM imports in cdb_analyze/:     PASS
Check 2 — Append-only JSONL:                  PASS
Check 3 — No secrets:                         PASS
Check 4 — Forbidden vocabulary:               PASS
Check 5 — Schema + DATA_DICTIONARY:           N/A
Check 6 — New deps sign-off:                  N/A
Check 7 — Prompt versioning:                  N/A
Check 8 — Uncertainty in viz:                 N/A
Check 9 — Prerequisite verdicts:              PASS
```

---

## Per-check rationale

**Check 1 — No LLM imports in `cdb_analyze/`:** PASS. This PR touches only
`scripts/run_decline_backfill.py` and `tests/test_run_decline_backfill.py`.
Neither file is under `packages/cdb_analyze/`. Static grep confirmed no LLM
client imports in that package.

**Check 2 — Append-only JSONL:** PASS. `git show ce3da31 -- data/raw/informants.jsonl`,
`data/raw/failures.jsonl`, and `data/raw/decline_interviews.jsonl` all returned no diff.
None of those files were touched.

**Check 3 — No secrets:** PASS. Diff scanned for API key patterns
(`sk-ant`, `sk-or-v1`, `hf_`), webhook URL shapes
(`hooks.slack.com/services/...`), and named webhook env vars
(`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`).
None found. All new content is test fixtures and code constants.

**Check 4 — Forbidden vocabulary:** PASS. Full diff scanned for `worldview`,
`believes`, `thinks of`, `how models see`, `what the model understands`,
`cultural bias` (standalone), `within-model consensus`, `within-model cultural`,
`within-model eigenratio`, `within-model CCM`, `publishable`. None found in
added lines. The new docstrings and test docstrings are about the decline
detector's behavior; no model-facing claims are made.

**Check 5 — Schema + DATA_DICTIONARY:** N/A. No changes to `cdb_core/schemas.py`.

**Check 6 — New deps sign-off:** N/A. No changes to `pyproject.toml`,
`apps/dashboard/package.json`, or any lockfile.

**Check 7 — Prompt versioning:** N/A. No changes to prompt templates under
`packages/cdb_collect/prompts/`.

**Check 8 — Uncertainty in viz:** N/A. No frontend changes; no new visualizations.

**Check 9 — Prerequisite verdicts:** PASS. This is a non-frontend task.
CDA SME re-review is explicitly waived by Amendment 2 §6, which quotes the
T3B-detector verdict: "R1–R7 are binding incorporation-into-spec items.
None require SME re-review." The commit body cites both the SME verdict
(`docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md`) and the
Architect plan (`docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md §2 T-R1`),
satisfying CLAUDE.md §8 commit-body convention for methodology-adjacent changes.

---

## Item-level checks (27 items from task brief)

**1. `MIN_SUBSTANTIVE_RESPONSE_LEN = 40` at module level with SME Q1.B docstring:** PASS.
Present at `/opt/lsb-agent/scripts/run_decline_backfill.py` line 137.
Docstring quotes SME T3B-detector verdict Q1.B verbatim, including "Anywhere in
30-60 is defensible; 40 is fixed and may not drift without SME re-review."

**2. `RECURSIVE_DECLINE_PHRASES` tuple — verbatim phrases, correct order:** PASS.
Present at lines 148–177. The tuple contains 28 strings, which matches the
authoritative count in SME Q1.C (lines 77–104 of the verdict file). The Architect
plan Amendment 2 §2 T-R1 says "27 phrases" — this is a counting error in the plan
document, not in the code. The authoritative source is the SME Q1.C list in
`docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md`, which has 28
entries; the code faithfully reproduces all 28 verbatim in the specified order.
Spot-check first 5 (match SME Q1.C lines 77–81): "i cannot describe", "i can't
describe", "i won't describe", "i am unable to describe", "i'm unable to describe"
— all PASS. Spot-check last 5 (match SME Q1.C lines 100–104): "i'm not going to",
"i am not going to", "i'd rather not", "i would rather not", "i prefer not to" —
all PASS.

**3. `_is_recursive_decline()` body — three-clause check, `any()` semantics-preserving:** PASS.
The function implements all three clauses per Q1.D pseudocode: (a) empty/whitespace
check, (b) length-floor check, (c) allowlist substring match. The implementation
uses `any(phrase in rv_lower for phrase in RECURSIVE_DECLINE_PHRASES)` instead of an
explicit for-loop. This is semantics-preserving: `any()` with a generator expression
does the same case-insensitive substring scan over the tuple as the Q1.D for-loop,
short-circuiting on first match. Verified by manual analysis and execution test.

**4. `_is_recursive_decline()` no longer references `SAFETY_FILTER_MARKERS`:** PASS.
The function body contains no reference to `SAFETY_FILTER_MARKERS`. The docstring
mentions it only to distinguish roles, which is correct documentation.
Grep of function body confirms: only `MIN_SUBSTANTIVE_RESPONSE_LEN`,
`rv_stripped`, `rv_lower`, and `RECURSIVE_DECLINE_PHRASES` appear.

**5. Docstring cites SME verdict file path:** PASS.
Docstring contains `See: docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md Q1`
at line 1299.

**6. `SAFETY_FILTER_MARKERS` definition unchanged:** PASS.
Lines 102–122 are not in the diff. The constant is intact at the same location
with the same 12 entries (including `"jailbreak"` per SME A2).

**7. `should_include_failure()` body unchanged:** PASS.
The function at line 188 is not in the diff. Verified by inspection: it still
uses `for marker in SAFETY_FILTER_MARKERS:` at line 237.

**8. `packages/cdb_collect/decline_detection.py` not in the diff:** PASS.
`git show ce3da31 -- packages/cdb_collect/cdb_collect/decline_detection.py`
returned no output.

**9. `data/raw/decline_interviews.jsonl` not in the diff:** PASS. Confirmed above.

**10. No edits to `informants.jsonl` or `failures.jsonl`:** PASS. Confirmed above.

**11. `TestIsRecursiveDeclineCorrected` class exists:** PASS.
Class is defined at `tests/test_run_decline_backfill.py` line 2577.

**12. All 5 T3B false-positive samples assert False:** PASS.
- `test_gemini_safety_protocols_narrative_is_not_recursive_decline` — present, asserts False.
- `test_gemini_blocked_negotiating_narrative_is_not_recursive_decline` — present, asserts False.
- `test_glm_safety_filter_false_trigger_narrative_is_not_recursive_decline` — present, asserts False.
- `test_llama_output_empty_other_words_narrative_is_not_recursive_decline` — present, asserts False.
- `test_gpt_in_other_words_task_narrative_is_not_recursive_decline` — present, asserts False.
All 5 inputs clear the 60-char safety margin specified in Amendment 2 Risk R-A2.1.
All 5 pass in the test run.

**13. At least 3 synthetic genuine recursive-decline cases assert True:** PASS.
- `test_cannot_describe_is_recursive_decline`: "I cannot describe what happened in that exchange." → True (Q1.C trigger).
- `test_sorry_short_response_is_recursive_decline`: "Sorry." → True (Q1.B length-floor, 5 chars < 40).
- `test_wont_engage_is_recursive_decline`: "I won't engage with this." → True (Q1.C trigger).

**14. At least 2 third-person attribution cases assert False:** PASS.
- `test_third_person_could_not_process_is_not_recursive_decline`: "The model's response indicated it could not process the request." (63 chars, no allowlist match) → False.
- `test_third_person_declined_to_provide_is_not_recursive_decline`: "The original output declined to provide the list, citing safety concerns." (72 chars, no allowlist match) → False.

**15. `TestExecutePath.test_execute_recursive_decline_counted` update is legitimate:** PASS.
Old fixture: "This content was blocked by the safety filter." (46 chars).
Under the corrected detector: 46 chars > 40 (passes length-floor); "blocked" is NOT in
`RECURSIVE_DECLINE_PHRASES` (passes allowlist check) → returns False. The old fixture
was testing miscalibrated behavior and its replacement is correct.
New fixture: "I cannot describe what happened in that exchange." (49 chars).
Under the corrected detector: 49 chars > 40 (passes length-floor); "i cannot describe" IS
in `RECURSIVE_DECLINE_PHRASES` → returns True. This is a genuine Q1.C trigger.
The update is legitimate: old fixture tested a behavior that the corrected detector
correctly does NOT exhibit; new fixture tests genuine recursive-decline detection.

**16. R10 — No real model calls in tests:** PASS. All test fixtures are string literals.
No network calls, no adapter imports, no `httpx` requests. Verified by reading the
test class and the full test run (no network activity).

**17. R12 — No LLM imports in `cdb_analyze/`:** N/A (this PR does not touch `cdb_analyze/`).
Static check confirmed `cdb_analyze/__init__.py` has no real LLM imports (the comment
mentioning LLM libraries is the prohibition notice, not an import).

**18. R7 — Schema changes co-update DATA_DICTIONARY:** N/A. No schema changes.

**19. R9 — No `.env`/secret leakage:** PASS. Confirmed under Check 3 above.

**20. R11 — No new visualizations:** N/A. No frontend changes.

**21. Forbidden vocabulary spot-check:** PASS. All added lines scanned. No
`worldview`, `believes`, `thinks` applied to models, `what the model understands`,
`cultural bias`, `within-model consensus`, `within-model cultural consensus`,
`within-model eigenratio`, `within-model CCM`, or `publishable` found.

**22. Conventional Commits format:** PASS. Subject: `fix(scripts): correct _is_recursive_decline output classification (T-R1)`.

**23. Subject line ≤ 72 characters:** PASS. Exactly 72 characters confirmed by `wc -c`.

**24. Body references task ID:** PASS. Body contains `Task: Phase 4a.1 T-R1 (#21.T-R1)`.

**25. Body cites SME verdict file path:** PASS. Body contains `SME verdict: docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md`.

**26. Body cites Amendment 2 file path:** PASS. Body contains `Architect plan: docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md §2 T-R1`.

**27. One commit per task — no bundled work:** PASS. The diff touches exactly two
files (`scripts/run_decline_backfill.py`, `tests/test_run_decline_backfill.py`),
both within scope of T-R1. No out-of-scope changes present.

---

## Test execution results

- `uv run pytest tests/test_run_decline_backfill.py -v`: **131 passed** (119 prior + 12 new). 0 failures.
- `uv run pytest` (full suite): **1036 passed**, 26313 warnings (numeric from sklearn/numpy, not test failures). 0 failures.
- `uv run ruff check scripts/run_decline_backfill.py tests/test_run_decline_backfill.py`: **All checks passed**.
- `uv run mypy packages/`: **Success: no issues found in 53 source files**.

---

## Failures

None. No blocking issues.

---

## Notes (non-blocking)

**Note 1 — Pre-existing test `TestSafetyMarkerCommentA2N3::test_is_recursive_decline_safety_marker_match` has a stale docstring.**
The test asserts `_is_recursive_decline("This was blocked by the filter.") is True`. Under the corrected detector, this returns True via the **length-floor branch** (31 chars < 40), not via the `SAFETY_FILTER_MARKERS` branch (which no longer exists in `_is_recursive_decline`). The test was not modified by this commit (it is in a pre-existing test class not in scope for T-R1), and it still passes — but the docstring now says "Text containing SAFETY_FILTER_MARKERS substring -> recursive decline" which is misleading about the actual mechanism. This is cosmetic and does not affect correctness. Recommended: update the docstring in a future commit if/when that test class is touched again. Not blocking.

**Note 2 — Amendment 2 plan document count error (cosmetic, in the plan doc not the code).**
Amendment 2 §2 T-R1 says "27 phrases verbatim from SME verdict Q1.C." The SME verdict Q1.C list has 28 entries, as does the code. The code faithfully matches the authoritative SME spec; the count in the plan document is a minor transcription error. The code is correct. No action required.

---

## Required before merge

None. PASS-WITH-NOTES with no blocking corrections. Coder may merge.

---

## Disposition

PASS-WITH-NOTES. The implementation is correct in all binding respects. The two notes above are cosmetic (stale docstring in an unmodified test, counting error in the plan document). Neither note requires correction before T-R2 may proceed.

T-R2 may start immediately per Amendment 2 §3 dependency chain.

---

*Reviewer verdict filed per CLAUDE.md §4, §11. Only Mark can override a Reviewer rejection; this is a PASS-WITH-NOTES, so no override is needed.*
