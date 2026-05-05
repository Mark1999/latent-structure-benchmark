# Tester Verdict — T4 Redo RD-2 Commit 1 (Confabulation Classification Scaffold)

**Date:** 2026-05-05
**Tester:** LSB Tester agent (Sonnet 4.6)
**Commit reviewed:** `148a620`
**Gap-coverage commit:** `014b999`
**Plan:** `docs/status/2026-05-05-t4-redo-architect-plan.md` §2 RD-2
**Reviewer verdict:** `docs/status/2026-05-05-t4-redo-rd2-reviewer-verdict.md` (PASS)
**Binding SME notes:** T1 (blind-spot framing), T2 (enum rename) from
  `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`

---

## VERDICT: PASS

---

## Item-by-item checklist

**Item 1 — Schema: each label accepted**
PASS. `test_valid_label_each_enum_value` (parametrized over 5 values) covers all
concrete label values. Each constructs a valid model instance and the assertion
checks the round-tripped label value.

**Item 2 — Schema: invalid label rejected**
PASS. `test_unclassified_sentinel_rejected_by_pydantic` and
`test_unknown_label_value_rejected_by_pydantic` both assert `ValidationError` on
non-Literal-member strings.

**Item 3 — Schema: rationale length cap enforced**
PASS. `test_rationale_at_200_chars_accepted` (boundary accepted) and
`test_rationale_at_201_chars_rejected` (one-over rejected). Both tests are
at-the-boundary assertions that would catch an off-by-one error in the validator.

**Item 4 — Schema: decline_interview_id non-empty enforced**
PASS. `test_empty_decline_interview_id_rejected` asserts `ValidationError` on
`decline_interview_id=""`. Note: the current validator uses `if not v` (truthy
check), which means whitespace-only IDs pass. This is documented in the new
gap-coverage test `test_whitespace_only_decline_interview_id_accepted_by_current_schema`
(added at `014b999`) rather than asserting rejection, since no schema change is
in scope.

**Item 5 — Loader round-trip: write fixture JSONL with all 5 labels + UNCLASSIFIED; load; assert types**
PASS. `test_loader_round_trip_all_labels` writes one row per concrete label to
`tmp_path`, loads them, and asserts each is a `ConfabulationClassification`
instance with the correct label. `test_loader_rejects_unclassified_sentinel`
separately confirms the UNCLASSIFIED sentinel is rejected on load.

**Item 6 — `validate_no_unclassified`: raises on UNCLASSIFIED; passes when all rows are concrete**
PASS. Three tests:
- `test_validate_no_unclassified_raises_on_unclassified` — force-patches sentinel
  via `object.__setattr__` and asserts `ValueError`.
- `test_validate_no_unclassified_passes_when_all_classified` — all five concrete
  labels present; no raise.
- `test_validate_no_unclassified_empty_list_passes` — empty list; no raise.

**Item 7 — Seed builder: produces 9-row UNCLASSIFIED on fresh run against fixture inputs**
PASS. `test_seed_builder_emits_correct_row_count` (with 3-row fixture; the count
logic scales to 9), plus individual field-value tests:
`test_seed_builder_emits_unclassified_sentinel`,
`test_seed_builder_emits_under_blind_spot_true`,
`test_seed_builder_emits_empty_rationale`,
`test_seed_builder_emits_classifier_id_mark`. The "9 rows" count is exercised
by the real seed JSONL in the commit (verified by Reviewer Item 18).

**Item 8 — Seed builder idempotence: rerun against existing seed → exit 1**
PASS. `test_seed_builder_exits_1_if_output_exists` runs the builder twice, with
a simulated partial hand-coding between runs, and asserts both exit code 1 and
that the output file content is not clobbered. `test_seed_builder_idempotence_guard_message`
additionally asserts the stderr message contains "Seed already exists" and
"remove it manually".

**Item 9 — CLI inspector `--summary`: correct counts-by-label**
PASS. `test_inspector_summary_counts_by_label` constructs a 6-row mixed seed
(3 UNCLASSIFIED, 1 safety_attribution_confabulation, 1 task_paradox_confabulation,
1 topic_sensitivity_confabulation), runs `--summary`, and asserts the output
contains the label name, the count "3", and the "Classified: 3" substring.

**Item 10 — CLI inspector `--unclassified-only`: filter works on mixed-state input**
PASS. `test_inspector_unclassified_only_filters_rows` uses a 2-row seed
(1 classified as `mixed_attribution`, 1 UNCLASSIFIED). Asserts the UNCLASSIFIED
row's ID appears in stdout and the classified row's ID does not. This IS a
mixed-state test — the scenario with some classified and some not is covered.

**Item 11 — SME T2 reversion guard: `test_safety_filter_confabulation_not_valid` exists and asserts ValidationError**
PASS. `test_safety_filter_confabulation_not_valid` (line 156) passes
`"safety_filter_confabulation"` to `ConfabulationClassification.model_validate()`
and asserts `ValidationError`. `test_safety_attribution_confabulation_is_valid`
additionally confirms the renamed value is accepted. Together these are a durable
guard against T2 reversion.

**Item 12 — Module-has-no-LLM-imports static test exists**
PASS. `test_confabulation_classification_module_has_no_llm_imports` reads the
module source file and asserts none of `anthropic`, `openai`, `google.generativeai`,
`huggingface_hub`, `InferenceClient` appear in the content. This protects against
future accidental import of any LLM client library into `cdb_analyze`, catching
it at test time rather than at the Reviewer's static import check alone.

**Item 13 — No real API calls**
PASS. Confirmed by inspection: all tests use `tmp_path` fixtures or in-memory
dict construction. No HTTP client libraries used anywhere in the test file.

**Item 14 — No reading of `data/raw/` from tests**
PASS. Test file docstring explicitly states the constraint; confirmed by
inspection: all file-dependent tests write fixture JSONL to `tmp_path`. No
production paths referenced.

**Item 15 — Fixture hygiene: synthesized JSONL strings or `tmp_path`-based tempfiles**
PASS. All file-creating tests use `tmp_path` (pytest built-in). No inline
real-looking model IDs, real-looking dates, or plausible SHA256 manifests.
Fixture IDs use clearly synthetic forms (`test-id-001`, `src-id-001`, etc.).

---

## Gap analysis

### Gap 1 — `--unclassified-only` with mixed-state input
ALREADY COVERED. `test_inspector_unclassified_only_filters_rows` uses a 2-row
seed with one classified row and one UNCLASSIFIED row. Asserts only the
UNCLASSIFIED row appears in output. No new test needed.

### Gap 2 — Seed builder error paths for missing/malformed source
PARTIALLY COVERED in original 43 tests (`test_seed_builder_source_not_found_exits_2`).
Added at `014b999`:
- `test_seed_builder_invalid_json_in_source_exits_2` — confirms exit 2 and
  no output file when source contains a malformed line.
- `test_seed_builder_empty_source_emits_zero_rows` — documents that an empty
  source JSONL produces a zero-row seed with exit 0 (silent success).

### Gap 3 — Pydantic whitespace edge cases
Added at `014b999` as behavioral documentation tests:
- `test_whitespace_only_classifier_id_accepted_by_current_schema` — documents
  that `classifier_id="   "` passes the `if not v` validator. Not asserting
  rejection (that would require a schema change outside Tester scope).
- `test_whitespace_only_decline_interview_id_accepted_by_current_schema` — same
  for `decline_interview_id`.

These tests ensure any future schema tightening (adding `.strip()`) is deliberate
rather than accidental — the tests will fail and require explicit update.

### Gap 4 — Pydantic coercion of `under_blind_spot="true"` (string)
NOT ADDED. Pydantic v2 coerces the string `"true"` to `True` for `bool` fields.
Adding a test asserting rejection would be a false assertion — the current behavior
is correct Pydantic coercion. The existing `test_under_blind_spot_true_accepted`
and `test_under_blind_spot_false_accepted` cover the canonical forms.

### Gap 5 — Inspector production-data smoke test
NOT ADDED. Out of scope per task brief: reading from `data/raw/` violates fixture
hygiene rules. The production data is exercised by Mark's hand-coding workflow.

---

## Test run output

```
# Target test file only (post-gap-coverage commit):
uv run pytest tests/test_confabulation_classification.py -v
47 passed in 0.23s

# Full suite:
uv run pytest -q
1153 passed, 26313 warnings in 13.36s

# Lint:
uv run ruff check .
All checks passed!

# Type check:
uv run mypy packages/
Success: no issues found in 54 source files
```

---

## Tests written (at `014b999`)

- `/opt/lsb-agent/tests/test_confabulation_classification.py`: `test_whitespace_only_classifier_id_accepted_by_current_schema` — behavioral documentation of `if not v` validator; whitespace-only classifier_id is currently accepted
- `/opt/lsb-agent/tests/test_confabulation_classification.py`: `test_whitespace_only_decline_interview_id_accepted_by_current_schema` — same for decline_interview_id
- `/opt/lsb-agent/tests/test_confabulation_classification.py`: `test_seed_builder_empty_source_emits_zero_rows` — seed builder exits 0 with zero-row output for empty source file
- `/opt/lsb-agent/tests/test_confabulation_classification.py`: `test_seed_builder_invalid_json_in_source_exits_2` — seed builder exits 2 and does not create output when source contains a malformed line

---

## Coverage gaps remaining

None that materially affect correctness or regression protection.

The whitespace-ID edge case is a latent schema behavior noted but not changed
(schema changes require Architect sign-off per CLAUDE.md §6 rule 7; the Tester
scope is tests only). If the operator decides to tighten the validator, the two
whitespace documentation tests (`014b999`) will catch the change.

---

## Final disposition

PASS. The original 43 tests at commit `148a620` provide complete coverage of
the spec requirements (plan §2 RD-2 acceptance criteria, SME T1/T2 binding notes,
Reviewer item-by-item checklist). The 4 gap-coverage tests at `014b999` add
behavioral documentation for edge cases in the non-empty validators and complete
the seed builder's error-path coverage. The suite is at 1153 tests, all passing.
Lint and mypy are clean. No production code was modified.
