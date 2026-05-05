# Reviewer Verdict — T4 Redo RD-2 Commit 1 (Confabulation Classification Scaffold)

**Date:** 2026-05-05
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `148a620`
**Commit message subject:** `feat(analyze): T4 redo RD-2 — confabulation classification scaffold`
**Plan:** `docs/status/2026-05-05-t4-redo-architect-plan.md` §2 RD-2
**Binding SME verdict:** `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1 + T2 bind this commit)
**Predecessor commit:** `ad5f975` (RD-1)

---

## VERDICT: PASS

---

## Nine binding checks

```
Check 1 — No LLM imports in cdb_analyze/:     PASS
Check 2 — Append-only JSONL:                  PASS
Check 3 — No secrets:                         PASS
Check 4 — Forbidden vocabulary:               PASS
Check 5 — Schema + DATA_DICTIONARY:           PASS
Check 6 — New deps sign-off:                  N/A
Check 7 — Prompt versioning:                  N/A
Check 8 — Uncertainty in viz:                 N/A
Check 9 — Prerequisite verdicts:              PASS
```

---

## Item-by-item checklist (items 1–45)

### Spec compliance (plan §2 RD-2)

**Item 1 — Module exists with correct name**
PASS. `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/confabulation_classification.py` created (344 lines).

**Item 2 — `ConfabulationClassification` Pydantic model present**
PASS. Class defined at line 130 of the new module; inherits `BaseModel` with `ConfigDict(extra="forbid")`.

**Item 3 — Five fields present with correct names and types**
PASS. All five fields verified: `decline_interview_id: str`, `confabulation_label: ConfabulationLabelValue`, `confabulation_rationale: str`, `under_blind_spot: bool`, `classifier_id: str`.

**Item 4 — `confabulation_label` enum: 5 concrete values + `UNCLASSIFIED` sentinel**
PASS. `ConfabulationLabelValue` Literal covers exactly the five concrete values. `ALL_CONFABULATION_LABELS` tuple includes `UNCLASSIFIED`. The sentinel is intentionally outside the Pydantic Literal so Pydantic rejects it on model construction — this is the intended gate behavior.

**Item 5 — `load_confabulation_classifications(path)` loader present**
PASS. Loader defined, raises on `UNCLASSIFIED`, raises on duplicate `decline_interview_id`, raises on invalid JSON, raises on missing file, validates through Pydantic.

**Item 6 — `validate_no_unclassified(records)` raises if any UNCLASSIFIED**
PASS. Helper defined; raises `ValueError` naming offending IDs. Belt-and-suspenders gate for in-memory record lists.

**Item 7 — Seed builder script exists**
PASS. `scripts/build_confabulation_classification_seed.py` created (242 lines).

**Item 8 — Seed builder reads 9 IDs from the superseded May 1 artifact**
PASS. `DEFAULT_SOURCE` is `data/derived/decline_interviews_safety_attribution_subtype.jsonl`; only `decline_interview_id` fields are consumed (labels are explicitly not used).

**Item 9 — Seed builder writes 9-row UNCLASSIFIED seed at correct path**
PASS. `DEFAULT_OUTPUT` is `data/derived/decline_interviews_confabulation_classification.jsonl`. Verified: `under_blind_spot=True`, `classifier_id="mark"`, `confabulation_label="UNCLASSIFIED"`, `confabulation_rationale=""` for all 9 rows.

**Item 10 — Seed builder exits 1 if output already exists**
PASS. Idempotence guard implemented: checks `output_path.exists()`, prints message to stderr, returns 1.

**Item 11 — CLI inspector exists**
PASS. `scripts/inspect_confabulation_candidates.py` created (372 lines).

**Item 12 — Inspector reads seed + decline_interviews.jsonl + May 1 artifact**
PASS. Three default paths: `DEFAULT_SEED`, `DEFAULT_DECLINE_INTERVIEWS` (`data/raw/decline_interviews.jsonl`), `DEFAULT_MAY1_CROSSWALK` (`data/derived/decline_interviews_safety_attribution_subtype.jsonl`). All three loaded.

**Item 13 — Inspector per-row output: ID, response_verbatim, May 1 cross-walk (NON-AUTHORITATIVE), label legend, current label state**
PASS. Inspector smoke test run confirms all five elements rendered per row. May 1 cross-walk explicitly labeled "NON-AUTHORITATIVE — for cross-walk only". Label legend prints all five concrete values with descriptions. Current state shows `confabulation_label`, `confabulation_rationale`, `under_blind_spot`.

**Item 14 — `--summary` flag prints counts-by-label tally**
PASS. `--summary` confirmed working: reports 9 UNCLASSIFIED, Classified: 0/9, Remaining: 9/9.

**Item 15 — `--unclassified-only` flag filters to UNCLASSIFIED rows**
PASS. Flag implemented; filters `display_rows` to rows where `confabulation_label == UNCLASSIFIED`.

**Item 16 — Inspector is read-only (no JSONL writes)**
PASS. No file write calls anywhere in `inspect_confabulation_candidates.py`. The script only calls `open()` in read mode and prints to stdout/stderr.

**Item 17 — Tests file exists with 43 tests**
PASS. `tests/test_confabulation_classification.py` created (929 lines). Running the file yields exactly 43 tests, all passing.

**Item 18 — Seed JSONL exists with exactly 9 rows, all UNCLASSIFIED**
PASS. Verified via `git show`: 9 lines, each with `"confabulation_label": "UNCLASSIFIED"`. All rows: `under_blind_spot: true`, `classifier_id: "mark"`.

### Schema co-update (CLAUDE.md §6 R7)

**Item 19 — `docs/DATA_DICTIONARY.md` is in the commit**
PASS. Confirmed in `git show --stat 148a620`.

**Item 20 — Version bumped v0.1.11 → v0.1.12**
PASS. Header line updated from v0.1.11 to v0.1.12; confirmed in current file at line 4.

**Item 21 — Changelog entry added citing T4 redo RD-2 + plan + SME verdict**
PASS. v0.1.12 changelog entry present; cites `docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2` and `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`. Explicitly notes T1 wording rules and T2 enum naming applied.

**Item 22 — New §11 documents `ConfabulationClassification` with field table + all 6 enum values**
PASS. DATA_DICTIONARY §11 added: §11.1 field table (5 fields, all documented), §11.2 enum values table (all 6 values including UNCLASSIFIED sentinel), §11.3 artifact file description, §11.4 example entry.

Note: CLAUDE.md §6 R7 / SECURITY_AND_HARDENING.md §9 R7 strictly binds `InformantRecord` and `GroundingRef` schema changes in `cdb_core/schemas.py`. This commit does NOT modify `cdb_core/schemas.py` — the Architect plan explicitly states "Schema changes: NONE" (plan §7). The DATA_DICTIONARY update was added proactively to document the new `cdb_analyze`-scoped schema. This is correct and disciplined behavior.

### SME T2 — enum naming

**Item 23 — Enum value is `safety_attribution_confabulation`, NOT `safety_filter_confabulation`**
PASS. `ConfabulationLabelValue` Literal uses `"safety_attribution_confabulation"`. Confirmed in source.

**Item 24 — Other three concrete values keep their names**
PASS. `task_paradox_confabulation`, `topic_sensitivity_confabulation`, `mixed_attribution` all present unchanged.

**Item 25 — `not_confabulation` sentinel keeps its name**
PASS. `"not_confabulation"` in the Literal.

**Item 26 — `grep -r "safety_filter_confabulation"` returns zero enum-use results**
PASS. All occurrences of `safety_filter_confabulation` in the codebase are: (a) documentation comments noting it was renamed away from, (b) the T2-reversion-guard test that explicitly passes it to Pydantic and asserts `ValidationError` is raised. No use as an actual label value anywhere in schema, seed builder, inspector, or DATA_DICTIONARY.

### SME T1 — wording compliance

**Item 27 — "blind-spot conditions" defined on first use in the new module's docstring**
PASS. Module-level docstring defines: "**Blind-spot conditions** (defined on first use): conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time." This satisfies T1 exactly.

**Item 28 — No cognition-shaped phrasings in new files**
PASS. Full grep of `confabulation_classification.py`, `build_confabulation_classification_seed.py`, `inspect_confabulation_candidates.py`, `test_confabulation_classification.py`, and DATA_DICTIONARY §11 found no instances of "the model could not see", "model was blind", "model didn't know", "model feels", "model intends", "model wants", "model believed", "model thought". The only occurrences of "the model believed" are inside docstring comments explicitly listing it as a FORBIDDEN phrasing (e.g., "— never 'the model believed'"). This is compliant.

**Item 29 — Forbidden vocabulary spot-check (§7)**
PASS. No occurrences of `worldview`, `believes` (applied to models), `thinks` (applied to models), `what the model understands`, `cultural bias` (standalone), `how models see the world`, `within-model consensus`, `within-model eigenratio`, `within-model CCM`, `publishable` (for LSB findings) in any of the new files.

### No-LLM-imports invariant (CLAUDE.md §6 R12)

**Item 30 — New module in `cdb_analyze/` has no LLM client imports**
PASS. Verified by grep: the only imports in `confabulation_classification.py` are `__future__`, `json`, `pathlib`, `typing.Literal`, `pydantic.BaseModel`, `pydantic.ConfigDict`, `pydantic.field_validator`. No LLM client library imports.

**Item 31 — `scripts/check_no_llm_imports.py` passes**
PASS. Output: "OK: no LLM client imports found in /opt/lsb-agent/packages/cdb_analyze".

### Test coverage adequacy

**Item 32 — Schema validation tests: each label accepted; invalid label rejected; rationale length cap enforced**
PASS.
- `test_valid_label_each_enum_value` (parametrized over 5 values) — each concrete value accepted.
- `test_unclassified_sentinel_rejected_by_pydantic` — UNCLASSIFIED rejected.
- `test_unknown_label_value_rejected_by_pydantic` — unknown string rejected.
- `test_rationale_at_200_chars_accepted` — boundary accepted.
- `test_rationale_at_201_chars_rejected` — one-over boundary rejected.

**Item 33 — Loader round-trip test**
PASS. `test_loader_round_trip_all_labels` writes all 5 label variants to tmp JSONL, loads them, asserts equal. `test_loader_round_trip_re_emit_semantic_equality` also present.

**Item 34 — `validate_no_unclassified` tests**
PASS.
- `test_validate_no_unclassified_passes_when_all_classified` — no raise when all concrete.
- `test_validate_no_unclassified_raises_on_unclassified` — raises when UNCLASSIFIED is force-patched into a record via `object.__setattr__`.
- `test_validate_no_unclassified_empty_list_passes` — empty list passes.

**Item 35 — Seed builder produces 9-row UNCLASSIFIED on fresh run**
PASS. `test_seed_builder_emits_correct_row_count`, `test_seed_builder_emits_unclassified_sentinel`, `test_seed_builder_emits_under_blind_spot_true`, `test_seed_builder_emits_empty_rationale`, `test_seed_builder_emits_classifier_id_mark` all present and passing.

**Item 36 — Seed builder idempotence (exit 1 on existing seed)**
PASS. `test_seed_builder_exits_1_if_output_exists` and `test_seed_builder_idempotence_guard_message` both present and passing.

**Item 37 — CLI inspector tests (`--summary` correct counts; `--unclassified-only` filter works)**
PASS. `test_inspector_summary_counts_by_label` and `test_inspector_unclassified_only_filters_rows` both present and passing.

**Item 38 — Test using `safety_filter_confabulation` asserting it is REJECTED (T2 reversion guard)**
PASS. `test_safety_filter_confabulation_not_valid` (line 220) passes `"safety_filter_confabulation"` to `ConfabulationClassification.model_validate()` and asserts `ValidationError` is raised. `test_safety_attribution_confabulation_is_valid` additionally confirms the renamed value is accepted. These tests protect against T2 reversion.

**Item 39 — No real API calls in any test**
PASS. Test file docstring states "No real API calls." Confirmed by inspection: all tests use `tmp_path` fixtures or in-memory dict construction. No `httpx`, `anthropic`, `openai`, or other client library used. No calls to `data/raw/` production files.

**Item 40 — No reading of `data/raw/` from tests (only fixtures)**
PASS. Test file docstring: "No access to data/raw/ or data/derived/ production artifacts — every test that needs file data writes its own fixture files to `tmp_path`." Confirmed by inspection: all file-dependent tests write fixture JSONL to `tmp_path` rather than reading production data.

### Append-only invariants (CLAUDE.md §9 pitfall 10)

**Item 41 — `data/derived/decline_interviews_safety_attribution_subtype.jsonl` NOT in diff**
PASS. `git show 148a620 --name-only` does not include this file.

**Item 42 — `data/raw/decline_interviews.jsonl` NOT in diff**
PASS. Not in diff.

**Item 43 — `data/raw/informants.jsonl` NOT in diff**
PASS. Not in diff.

**Item 44 — `data/raw/failures.jsonl` NOT in diff**
PASS. Not in diff.

### `scripts/phase4a1_note_j_crosstab.py` invariant

**Item 45 — `scripts/phase4a1_note_j_crosstab.py` NOT in diff**
PASS. Not present in `git show 148a620 --name-only`. The RD-1 commit (`ad5f975`) already applied the moot banner; this commit correctly leaves it untouched.

### Other CLAUDE.md §6 binding rules

**Item 33 (schema+dict co-update, R7) — see Items 19–22 above**
PASS. Note: R7 strictly binds `cdb_core` schema changes; no `cdb_core` changes here. DATA_DICTIONARY was updated proactively and correctly.

**Item 34 (no real model calls in tests, R10) — see Item 39 above**
PASS.

**Item 35 (no secrets, R9)**
PASS. No `sk-ant-`, `sk-or-v1-`, `hf_`, Slack webhook URLs, or other credential patterns found in the diff.

**Item 36 (no new visualizations, R11)**
N/A. No frontend artifacts added.

### Commit format (CLAUDE.md §8)

**Item 37 — Conventional Commits format**
PASS. `feat(analyze):` prefix.

**Item 38 — Subject ≤ 72 chars**
PASS. Subject line is 67 characters.

**Item 39 — Body references `T4 redo RD-2 commit 1`**
PASS. "Task: T4 redo RD-2 commit 1 (scaffold)" present in commit body.

**Item 40 — Body cites Architect plan path**
PASS. "Architect plan: docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-2" present.

**Item 41 — Body cites SME verdict path with T1 + T2 explicitly mentioned**
PASS. "CDA SME verdict: docs/status/2026-05-05-t4-redo-cda-sme-verdict.md / T1 (blind-spot framing) + T2 (enum rename) applied." present.

**Item 42 — Body cites DATA_DICTIONARY version bump v0.1.11 → v0.1.12**
PASS. "DATA_DICTIONARY: v0.1.11 → v0.1.12" present.

**Item 43 — Body cites Mark sign-off date 2026-05-05**
PASS. "Mark sign-off: 2026-05-05 Q1/Q2/Q3 + CLI inspector + cross-walk interface" present.

**Item 44 — Body cites predecessor commit `ad5f975`**
PASS. "Predecessor: RD-1 commit ad5f975" present.

**Item 45 — One commit; no bundled work**
PASS. The commit contains exactly and only the RD-2 scaffold deliverables. RD-3 memo is not present. Mark's hand-coding is not present (seed JSONL has all rows as UNCLASSIFIED, which is the correct state before Mark's separate commit 2). `scripts/phase4a1_note_j_crosstab.py` is not in this diff.

### Validation gates (run results)

- `uv run pytest -q`: **1149 passed** (1106 baseline + 43 new). Clean.
- `uv run ruff check .`: **All checks passed**.
- `uv run mypy packages/`: **Success: no issues found in 54 source files**.
- `uv run python scripts/check_no_llm_imports.py`: **OK: no LLM client imports found in /opt/lsb-agent/packages/cdb_analyze**.
- `uv run python scripts/inspect_confabulation_candidates.py --summary`: **9 UNCLASSIFIED, Classified: 0/9, Remaining: 9/9**. Clean.

### Inspector smoke test (Mark's usability verification)

Inspector output for Row 1/9 (decline_interview_id `76be28c364a37aa0`) confirmed:
- Model ID displayed: `google/gemini-2.5-pro`
- `response_verbatim` printed in full (the narrative about the logical paradox / role-playing instruction)
- May 1 cross-walk displayed with explicit "NON-AUTHORITATIVE — for cross-walk only" label; May 1 rationale shown
- All five concrete label values printed with descriptions
- Current state: `confabulation_label: UNCLASSIFIED`, `confabulation_rationale: ''`, `under_blind_spot: True`

The interface is complete and usable for Mark's hand-coding session.

---

## Failures

None.

---

## Required before merge

None. All 45 items pass.

---

## Final disposition

PASS. The RD-2 scaffold commit is methodologically correct, technically clean, and fully compliant with all binding rules. T2 (SME enum rename `safety_attribution_confabulation`) is applied throughout — schema, seed builder, inspector, tests, DATA_DICTIONARY §11.2. T1 (blind-spot framing) is applied in the module-level docstring definition and throughout all §1.5-clean descriptions. The T2 reversion guard (`test_safety_filter_confabulation_not_valid`) is present and will catch any future attempt to roll back the rename.

The commit is appropriately scoped to the scaffold deliverable only. Mark's hand-coding commit (RD-2 commit 2) is the correct next step; it is not blocked by this verdict. All 1149 tests pass; lint, mypy, and the no-LLM-imports check are clean.

Coder may proceed to hand-coding instructions for Mark (commit 2). RD-3 (the reframing memo) requires Mark's hand-coded artifact to be complete before the Coder drafts §4, and RD-3 must subsequently route to the CDA SME for the S5-completing second PASS.

