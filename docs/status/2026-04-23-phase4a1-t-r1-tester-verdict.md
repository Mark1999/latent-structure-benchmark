# Tester Verdict — Phase 4a.1 T-R1: correct `_is_recursive_decline()` for output-classification role

**Date:** 2026-05-04
**Tester:** LSB Tester (Sonnet)
**Commit reviewed:** `ce3da31`
**Follow-up commit (Reviewer Note 1 cleanup):** `03bbd7f`
**Task:** Phase 4a.1 T-R1 (#21.T-R1)
**Spec sources:**
- `docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md` Q1.E (binding test requirements)
- `docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md` §2 T-R1 (test coverage requirements)
- `docs/status/2026-04-23-phase4a1-t-r1-reviewer-verdict.md` (PASS-WITH-NOTES, Note 1)

---

## VERDICT: PASS

All 10 binding coverage items PASS. All 3 fixture hygiene items PASS. Test execution
confirms the expected counts. Reviewer Note 1 addressed in a separate follow-up commit
(`03bbd7f`), per option (b).

---

## Coverage adequacy — 10 binding items (SME Q1.E / Amendment 2 §2 T-R1)

**Item 1 — 5 false-positive samples from T3B run log present and assert False: PASS**

All five named false-positive samples from the T3B run log §"Representative verbatim
samples" are present as individual test methods in `TestIsRecursiveDeclineCorrected`:

- `test_gemini_safety_protocols_narrative_is_not_recursive_decline` — asserts False. Input: 175 chars. Substantive narrative with "safety protocols" in a third-person/impersonal construction.
- `test_gemini_blocked_negotiating_narrative_is_not_recursive_decline` — asserts False. Input: 198 chars. Contains "I was blocked" as historical description of originating event, not first-person refusal of current task.
- `test_glm_safety_filter_false_trigger_narrative_is_not_recursive_decline` — asserts False. Input: 176 chars. Meta-discussion of a safety filter; third-person attribution shape.
- `test_llama_output_empty_other_words_narrative_is_not_recursive_decline` — asserts False. Input: 169 chars. "In other words" ordinary prose; no allowlist match.
- `test_gpt_in_other_words_task_narrative_is_not_recursive_decline` — asserts False. Input: 158 chars. Same "other words" false-positive shape.

All five inputs clear the 60-char safety margin mandated by Amendment 2 Risk R-A2.1
(each asserts `len(sample.strip()) >= 60` before the False assertion). This ensures the
allowlist branch is exercised — not the length-floor branch — for the False assertions.

**Item 2 — At least 3 synthetic genuine recursive-decline cases assert True, covering Q1.A empty, Q1.B length-floor, Q1.C allowlist: PASS**

Three synthetic cases present:

- `test_cannot_describe_is_recursive_decline`: "I cannot describe what happened in that exchange." → True. Q1.C trigger ("i cannot describe"). 49 chars > 40 (length-floor passed), match on allowlist phrase.
- `test_sorry_short_response_is_recursive_decline`: "Sorry." → True. Q1.B length-floor trigger (6 chars < 40).
- `test_wont_engage_is_recursive_decline`: "I won't engage with this." → True. Q1.C trigger ("i won't engage with"). 25 chars < 40 — technically also a Q1.B trigger, but the allowlist would have caught it if the floor were lower. Both branches agree; acceptable overlap.

Q1.A (empty/whitespace) is covered by `test_empty_string_is_recursive_decline` and
`test_whitespace_only_is_recursive_decline`. These are also present as preserved existing
cases in the pre-existing `TestSafetyMarkerCommentA2N3` class.

**Item 3 — At least 2 third-person attribution cases assert False: PASS**

Two present:

- `test_third_person_could_not_process_is_not_recursive_decline`: "The model's response indicated it could not process the request." (63 chars) → False. Contains "could not" which is not in `RECURSIVE_DECLINE_PHRASES`.
- `test_third_person_declined_to_provide_is_not_recursive_decline`: "The original output declined to provide the list, citing safety concerns." (72 chars) → False. Contains "declined to" in third-person object position; not a first-person refusal locution.

Both clear the 40-char floor, confirmed by inline assertions. Both exercising the allowlist branch.

**Item 4 — Each sample is sufficiently distinct: PASS**

The five false-positive samples cover four distinct false-positive shapes: (a) safety-vocabulary in narrative prose (two Gemini samples, different phrases and different attributions), (b) "blocked" in historical attribution, (c) safety-filter meta-discussion with hypothetical framing, (d) "other words" ordinary connective. The SME Q1.E list covers different providers (Gemini, glm-5.1, llama-4-maverick, gpt-5.4-mini) with different failure shapes. Not merely minor variations.

**Item 5 — Length-floor branch exercised (Q1.B): at least one short-but-non-empty test case: PASS**

`test_sorry_short_response_is_recursive_decline` uses "Sorry." (6 chars after strip, clear of the empty-string branch but well below 40). This is the canonical Q1.B case. The pre-existing `TestSafetyMarkerCommentA2N3::test_is_recursive_decline_length_floor_trigger` (post-cleanup, see Note 1) also exercises the length-floor branch at 31 chars.

**Item 6 — Empty-string branch exercised (Q1.A): at least one truly empty case: PASS**

`test_empty_string_is_recursive_decline` uses `""` (zero chars). Exercises the
`not rv_stripped` branch at line (a) of the function.

**Item 7 — Allowlist branch exercised (Q1.C): multiple distinct phrases from the 28-entry tuple: PASS**

Two distinct allowlist phrases exercised across the True-asserting synthetic cases:
- "i cannot describe" (test_cannot_describe_is_recursive_decline)
- "i won't engage with" / "i won't engage with" (test_wont_engage_is_recursive_decline — matches "i won't engage with")

The False-asserting cases additionally confirm that non-allowlist third-person vocabulary ("could not," "declined to," "blocked from") does NOT match, validating the list boundary. Coverage is not exhaustive across all 28 phrases, but the SME binding requirement (Q1.E item 4) specifies "at least 3 synthetic cases" not a full phrase-by-phrase sweep, which is met.

---

## Fixture hygiene

**Item 8 — No real API calls. Test inputs are string literals. No network mocking that suggests a real call shape: PASS**

All test inputs in `TestIsRecursiveDeclineCorrected` are Python string literals. There are
no mock imports, no `pytest-mock` patterns, no `httpx` client references, no adapter
imports, and no network activity. The function `_is_recursive_decline` is a pure
deterministic string function. This fully satisfies CLAUDE.md §6 rule 10 (no real API
calls in tests) and §9 pitfall 9.

**Item 9 — No reading of `data/raw/decline_interviews.jsonl` from the test: PASS**

Grep of `TestIsRecursiveDeclineCorrected` and the full `test_run_decline_backfill.py`
confirms no file open or read call targeting `decline_interviews.jsonl` in the new test
class. The file is not referenced; string literals are used directly.

**Item 10 — No reading of `data/raw/informants.jsonl` or `data/raw/failures.jsonl`: PASS**

No reference to those files in the new test class. The Reviewer's diff check (Check 2)
confirmed the JSONL files were not in the ce3da31 diff at all.

---

## Test execution results

```
uv run pytest tests/test_run_decline_backfill.py -v -k TestIsRecursiveDeclineCorrected
  12 passed, 119 deselected in 0.67s

uv run pytest tests/test_run_decline_backfill.py -v
  131 passed in 0.97s        (confirms Coder's reported count)

uv run pytest -q             (full project suite)
  1036 passed, 26313 warnings in 14.41s
```

All counts match expectations. The 26313 warnings are numeric precision warnings from
sklearn/numpy in the MDS/pipeline tests; they are pre-existing and not test failures.

---

## Reviewer Note 1 — decision and action

**Decision: (b) — Make the test-only fix in a follow-up commit within T-R1 scope.**

Rationale: the Reviewer explicitly offered option (b) and noted the change is within the
Tester's authority (test docstring and method name, no production code). The misleading
docstring is actively harmful to future contributors: someone reading
`test_is_recursive_decline_safety_marker_match` would conclude that `SAFETY_FILTER_MARKERS`
still participates in `_is_recursive_decline()`, which is exactly the role-change
miscalibration that T-R1 corrected. The class name `TestSafetyMarkerCommentA2N3`
references SME A2 and Reviewer N3, which pertain to the content of `SAFETY_FILTER_MARKERS`
itself — a still-valid concern. Only the one method had a stale docstring; renaming the
class would overstate the problem.

**Action taken:** Renamed `test_is_recursive_decline_safety_marker_match` to
`test_is_recursive_decline_length_floor_trigger` and replaced the single-line docstring
with an explanatory block documenting: (a) the actual mechanism (Q1.B length-floor,
31 chars < 40), (b) the pre-T-R1 history, (c) cross-reference to the Reviewer verdict
Note 1.

No other changes. No production code touched. Class name `TestSafetyMarkerCommentA2N3`
left unchanged (it still correctly exercises `SAFETY_FILTER_MARKERS` content via the
other three methods in the class). All 131 tests pass after the edit.

**Commit:** `03bbd7f`
**Commit subject:** `test(collect): rename stale safety-marker test to length-floor-trigger (T-R1 cleanup)`
**Files changed:** `tests/test_run_decline_backfill.py` only (1 file, 12 insertions, 2 deletions)
**Linting:** `uv run ruff check` — All checks passed
**Types:** `uv run mypy packages/` — Success: no issues found in 53 source files

---

## Coverage gaps

None. All 10 binding coverage items from SME Q1.E and Amendment 2 §2 T-R1 are present
and pass. The allowlist coverage does not exercise all 28 phrases individually, but that
is not required by the binding spec, which asks for at minimum 3 synthetic genuine-decline
cases (met) and the named SME Q1.E cases (all met).

A possible future augmentation (not required and not in scope here): a parametrized test
sweeping all 28 `RECURSIVE_DECLINE_PHRASES` entries to confirm each triggers True. This
would increase confidence in the allowlist completeness but is not mandated by any binding
spec item.

---

## Summary

- **VERDICT: PASS** on commit `ce3da31` (all 10 coverage items, all 3 fixture hygiene items).
- **Follow-up commit `03bbd7f`** addresses Reviewer Note 1 with a test-only rename/re-docstring of the stale `test_is_recursive_decline_safety_marker_match` method.
- **T-R2 may proceed** per Amendment 2 §3 dependency chain.

---

*Tester verdict filed per CLAUDE.md §4, §11.*
