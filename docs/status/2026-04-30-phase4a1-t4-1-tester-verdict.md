# Tester Verdict — Phase 4a.1 T4.1 Safety Attribution Subtype Scaffold

**Date:** 2026-05-01
**Task:** #21.T4.1 (safety attribution subtype scaffold)
**Tester:** LSB Tester (claude-sonnet-4-6)
**Verdict:** AUGMENTED-PASS
**Coder commit audited:** `6aa0986`
**Reviewer verdict:** `docs/status/2026-04-30-phase4a1-t4-1-reviewer-verdict.md`

---

## Audit scope

Files audited:
- `/opt/lsb-agent/tests/test_safety_subtype.py` (31 Coder-authored tests)
- `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/safety_subtype.py`
- `/opt/lsb-agent/scripts/build_safety_subtype_seed.py`
- Baseline: `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` §3.1 acceptance criteria

---

## Acceptance criteria coverage (§3.1 check)

| Criterion | Status |
|---|---|
| Both subtype values valid | PASS — `test_valid_subtype_each_enum_value` parametrized over both |
| Sentinel rejected by loader | PASS — two tests (UNCLASSIFIED word + row ID check) |
| Parent-join enforced: non-safety parent rejected | PASS — `test_loader_rejects_non_safety_parent_classification` |
| Parent-join enforced: non-safety parent names actual classification | PASS — `test_loader_rejects_non_safety_names_actual_classification` |
| Parent-join enforced: ID not in parent rejected | PASS — `test_loader_rejects_id_not_in_parent` |
| Missing parent artifact errors clearly (FileNotFoundError) | PASS — `test_loader_raises_on_missing_parent_artifact` |
| Missing subtype artifact errors clearly (FileNotFoundError) | PASS — `test_loader_raises_on_missing_subtype_artifact` |
| ≤200-char rationale boundary: 200 accepted | PASS — `test_rationale_at_200_chars_accepted` |
| ≤200-char rationale boundary: 201 rejected | PASS — `test_rationale_at_201_chars_rejected` |
| Empty rationale rejected | PASS — `test_empty_rationale_rejected` |
| Build script emits only safety rows | PASS — `test_seed_builder_emits_only_safety_rows` |
| Deterministic byte-equality on repeat builds | PASS — `test_seed_builder_deterministic` |
| Round-trip load → dict → re-emit | PASS — `test_loader_round_trip_re_emit_semantic_equality` |
| Duplicate decline_interview_id rejected | PASS — `test_loader_raises_on_duplicate_decline_interview_id` |
| No LLM imports in cdb_analyze module | PASS — `test_module_has_no_llm_imports` |
| Seed builder importable without .env | PASS — `test_seed_builder_module_importable_without_dotenv` |

---

## Gaps identified and closed

### Gap 1 — Sentinel rejection: operator-friendly message not pinned

**Finding:** `test_loader_rejects_unclassified_sentinel` checks `match="UNCLASSIFIED"` and
`test_loader_rejects_unclassified_names_the_row` checks `match="safety-id-002"`. The actual
implementation error message reads: `"Safety attribution subtype incomplete: row {did!r} is still
UNCLASSIFIED. Mark must hand-code all 9 rows before T4.2 runs."` The task audit specification
explicitly requires verifying that the test checks the operator-friendly instructional phrase, and
flags tests that only assert `pytest.raises(SomeError)` as shallow. Neither existing test pins
the "Mark must hand-code" phrase — it can silently disappear in a future refactor without a test
failure.

**Closed by:** `test_loader_unclassified_error_message_names_hand_code_instruction` —
asserts `match="Mark must hand-code"` against the same sentinel scenario.

### Gap 2 — 9-row simultaneous round-trip (Reviewer note 1)

**Finding:** The Reviewer verdict flagged "Consider a 9-row simultaneous round-trip fixture for
T4.2 test planning." The existing round-trip tests cover 1 row (semantic equality) and 2 rows
(field content). No test loads all 9 rows at once. 9 is the real artifact size; a 9-row test
exercises the loader's dict-building loop at realistic scale and establishes the T4.2 fixture
prototype.

**Closed by:** `test_loader_9row_simultaneous_round_trip` — builds a parent fixture with
9 safety rows + 2 non-safety rows, loads a 9-row subtype JSONL with the expected B11
distribution (5 k_frame, 4 k_vocab_without_k_frame), asserts all 9 keys, correct subtype counts,
and correct classifier IDs.

---

## Items verified as not gaps

- **Sentinel message**: Two existing tests do collectively cover word + row-ID; gap was the
  instructional phrase only.
- **Parent-join "missing parent" path**: `FileNotFoundError` propagates naturally from both
  `load_manual_classifications` and `subtype_path.open()`; tests cover both. Bare
  `pytest.raises(FileNotFoundError)` is appropriate for OS-level errors.
- **Non-safety parent error message**: Names the actual classification
  (`no_prior_context_acknowledgment`) — tested.
- **Determinism test**: Runs `build_seed` twice, asserts `content1 == content2` bytes. The
  script uses `sort_keys=True` in `json.dumps` and sorts rows by `decline_interview_id`,
  making key ordering stable across Python builds. Correct.
- **Round-trip semantic equality**: `test_loader_round_trip_re_emit_semantic_equality` compares
  field-by-field via `model_dump()`. Not byte-equal (Pydantic ordering may differ); the spec
  says "if Pydantic introduces ordering changes, compare semantic equality not bytes" — correct.
- **`test_seed_builder_module_importable_without_dotenv`**: Asserts `callable(build_seed)`.
  The seed builder has no `.env`-dependent imports at module scope; the test is correctly scoped.
- **No-LLM-imports**: Reads source file and checks for all four forbidden token strings. Correct.

---

## Test count delta

31 → 33 (two tests added)

## Test suite result

`uv run pytest tests/test_safety_subtype.py -v`: **33 passed in 0.18s**
`uv run pytest tests/`: **747 passed** (no regressions)

## Commit

`test(analyze): augment safety subtype scaffold tests (task #21.T4.1)`

References: `docs/status/2026-04-30-phase4a1-t4-1-reviewer-verdict.md`

Gaps closed:
1. Pin "Mark must hand-code" instructional phrase in sentinel rejection error message
2. Add 9-row simultaneous round-trip (Reviewer note 1, T4.2 fixture prototype)
