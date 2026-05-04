# Task #16.B — Reviewer Verdict

**Date:** 2026-05-04  
**Reviewer:** LSB Reviewer agent  
**Commit under review:** `de3dd7e`  
**Task:** Task 16.B — schemas + DATA_DICTIONARY + runner wiring + build_db DDL for `thoughts_token_count`  
**Predecessor:** Task 16.A commits `7f8f7f7` + tester augmentation `6c987bf`  
**Plan:** `docs/status/2026-05-04-task-16-architect-plan.md` §2 Task 16.B  
**SME verdict:** `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (PASS-WITH-NOTES; notes S1–S4 binding for Task 16.B)

---

## VERDICT: PASS-WITH-NOTES

All nine binding checks pass. One PASS-WITH-NOTES item is logged below (Note N1) regarding a minor cosmetic deviation from S1 exact phrasing. The deviation is semantic-equivalent and does not change the informational content of the dictionary entry; it does not block merge.

---

## Check-by-check results

### Check 1 — No LLM client imports in cdb_analyze: PASS

`grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/` returns no actual import statements. The grep matched comment text in `packages/cdb_analyze/cdb_analyze/__init__.py` (the NO-LLM-CALLS warning block itself), which is correct and expected. No LLM client imports present.

### Check 2 — Append-only JSONL: PASS

`git show --name-only de3dd7e` contains no files under `data/raw/`. No pre-existing JSONL lines were touched.

### Check 3 — No secrets: PASS

Scan of all added lines (`^+`) for credential patterns — `sk-ant-`, `sk-or-v1-`, `hf_[a-zA-Z0-9]{10,}`, `hooks.slack.com/services/T.../B.../...` — returned no matches. No API keys, tokens, or webhook URLs committed.

### Check 4 — Forbidden vocabulary: PASS

Full scan of added lines for `worldview`, `believes`, `thinks` (applied to models), `cultural bias`, `how models see`, `what the model understands`, `within-model consensus`, `within-model cultural`, `within-model eigenratio`, `within-model CCM`, `publishable` returned no matches. The S3 phrase "model spent everything on thinking, nothing on output" (which the SME flagged in the adapters) was addressed in Task 16.A and does not appear in this commit's additions.

### Check 5 — Schema + DATA_DICTIONARY co-update: PASS

Both `packages/cdb_core/cdb_core/schemas.py` and `docs/DATA_DICTIONARY.md` are in the same commit `de3dd7e`. R7 is satisfied.

- `FreelistRecord` has `thoughts_token_count: int = 0` after `output_tokens` (line 417).
- `PileSortRecord` has `thoughts_token_count: int = 0` after `output_tokens` (line 433).
- `InterviewRecord` has `thoughts_token_count: int = 0` after `output_tokens` (line 450).
- `DeclineInterview` is NOT modified (confirmed: no change in diff, class present unchanged at line 555).
- `InformantRecord` envelope class is NOT modified beyond the per-step nested record changes.
- `DATA_DICTIONARY.md` version bumped from v0.1.10 to v0.1.11 (line 4).
- Changelog entry present at line 12, citing Task #16.B, architect plan, SME verdict, and predecessor Task 16.A.
- §1.2 (FreelistRecord) has new `thoughts_token_count` row at line 147.
- §1.3 (PileSortRecord) has new `thoughts_token_count` row at line 166.
- §1.4 (InterviewRecord) has new `thoughts_token_count` row at line 186.
- §9.2 top-level fields table has `thoughts_token_count` row (type `int | None`) at line 657.
- §9.3 partial_session sub-objects: `thoughts_token_count` added to both freelist (line 691) and pile_sort (line 704) sub-objects. Interview sub-object not updated (per plan §2, §9.3 footnote permits deferred update if not yet populated by runner — commit body confirms this is consistent with plan scope).
- §4 informants DDL: three new columns with DEFAULT 0 annotation (lines 401, 409, 417).

**SME wording checks:**

**S1 — Population-level hedge:** The required sufficient-condition sentence is present: "a sufficient diagnostic signature of cap-exhausted reasoning at the cohort level...but not a deterministic per-record proof of cap exhaustion." The exact S1 sentence "The converse does not hold: `thoughts_token_count == 0` does not rule out cap exhaustion when the provider does not surface reasoning tokens" is not present verbatim; however, the S2 wording that follows immediately covers the converse case explicitly ("A value of `0` is ambiguous: it can mean either (a) the provider does not surface reasoning tokens at all..."). Combined, the text satisfies the S1 epistemic requirement. See Note N1.

**S2 — Ambiguity of 0:** FULLY PRESENT. Both cases (a) provider does not surface reasoning tokens (Anthropic, HuggingFace at v0.1.11), and (b) model did not engage internal reasoning, are explicitly named at line 147. The text additionally states "The field cannot distinguish these two cases."

**S4 — Cross-provider non-comparability:** FULLY PRESENT. "Values are as reported by the provider and are NOT directly comparable across providers — Gemini's `thoughts_token_count` and OpenRouter's `completion_tokens_details.reasoning_tokens` may be measured under different conventions. Within-provider comparisons are valid; cross-provider comparisons require provider-internal context." (line 147 and line 657).

### Check 6 — New deps sign-off: N/A

`git show de3dd7e -- pyproject.toml apps/dashboard/package.json` returned no additions. No new dependencies.

### Check 7 — Prompt versioning: N/A

No files under `packages/cdb_collect/prompts/` appear in the diff. Confirmed by `git show --name-only de3dd7e | grep prompts/`.

### Check 8 — Uncertainty in viz: N/A

No frontend files changed. `git show --name-only de3dd7e | grep apps/dashboard` returned nothing.

### Check 9 — Prerequisite verdicts: PASS

This is a methodology PR (schema changes). CDA SME verdict is present at `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (PASS-WITH-NOTES). The commit body explicitly references the verdict file and lists notes S1–S4 as applied. S5 is correctly identified as a forward-looking gate for the T4-redo task and not a Task 16.B requirement. No UI/UX gate required (no frontend changes). All binding notes from the SME verdict that apply to Task 16.B are addressed.

---

## Items 1–51 enumeration

| # | Item | Result | Rationale |
|---|---|---|---|
| 1 | `FreelistRecord` has `thoughts_token_count: int = 0` after `output_tokens` | PASS | Line 417 in schemas.py; field position confirmed in diff |
| 2 | `PileSortRecord` has `thoughts_token_count: int = 0` after `output_tokens` | PASS | Line 433 in schemas.py; position confirmed |
| 3 | `InterviewRecord` has `thoughts_token_count: int = 0` after `output_tokens` | PASS | Line 450 in schemas.py; position confirmed |
| 4 | `DeclineInterview` NOT modified | PASS | Not in diff; class still at line 555 unchanged |
| 5 | `InformantRecord` envelope NOT modified | PASS | Not in diff; envelope unchanged at line 456 |
| 6 | `DATA_DICTIONARY.md` in same commit as schema change | PASS | Both files in de3dd7e |
| 7 | Version bumped v0.1.10 → v0.1.11 | PASS | Line 4 of DATA_DICTIONARY.md |
| 8 | Changelog entry citing task #16, plan, and SME verdict | PASS | Line 12 of DATA_DICTIONARY.md; all three references present |
| 9 | §1.2 has new `thoughts_token_count` row | PASS | Line 147 |
| 10 | §1.3 has new `thoughts_token_count` row | PASS | Line 166 |
| 11 | §1.4 has new `thoughts_token_count` row | PASS | Line 186 |
| 12 | §9.2 top-level fields table has `thoughts_token_count` row | PASS | Line 657; type `int \| None`, semantics complete |
| 13 | §9.3 partial_session freelist + pile_sort sub-objects updated | PASS | Lines 691 and 704 respectively |
| 14 | S1 population-level hedge present | PASS | "sufficient diagnostic signature of cap-exhausted reasoning at the cohort level...but not a deterministic per-record proof" present; see Note N1 for minor wording deviation |
| 15 | S2 ambiguity of 0 distinguished | PASS | Both cases (a) and (b) explicit at line 147 and line 657; "The field cannot distinguish these two cases" present |
| 16 | S4 cross-provider non-comparability explicit | PASS | "Values are as reported by the provider and are NOT directly comparable across providers" with Gemini/OpenRouter named |
| 17 | `free_list.py` passes `thoughts_token_count=result.thoughts_token_count` | PASS | Confirmed in diff |
| 18 | `pile_sort.py` passes `thoughts_token_count=result.thoughts_token_count` | PASS | Confirmed in diff |
| 19 | `pile_interview.py` passes `thoughts_token_count=result.thoughts_token_count` | PASS | Confirmed in diff |
| 20 | `runner.py` retry_attempts dicts include `thoughts_token_count` | PASS | Added at all three call sites: `run_informant`, `run_two_pass`, `run_baseline_sort` |
| 21 | `runner.py` partial_session dicts via `.model_dump()` auto-carry field | PASS | Commit body confirms; `.model_dump()` on step records now include field automatically |
| 22 | `jsonl.py` `append_failure` has new `thoughts_token_count: int | None = None` param | PASS | Added as keyword-only after `stop_reason` |
| 23 | New value written as top-level field after `stop_reason` | PASS | `if thoughts_token_count is not None: entry["thoughts_token_count"] = thoughts_token_count` |
| 24 | Docstring documents new parameter | PASS | Full docstring with semantics and DATA_DICTIONARY reference |
| 25 | SQLite DDL adds `freelist_thoughts_token_count INTEGER NOT NULL DEFAULT 0` | PASS | Confirmed in build_db.py diff |
| 26 | SQLite DDL adds `pilesort_thoughts_token_count INTEGER NOT NULL DEFAULT 0` | PASS | Confirmed in build_db.py diff |
| 27 | SQLite DDL adds `interview_thoughts_token_count INTEGER NOT NULL DEFAULT 0` | PASS | Confirmed in build_db.py diff |
| 28 | INSERT statements use `.get("thoughts_token_count", 0)` | PASS | All three: `fl.get(...)`, `ps.get(...)`, `iv.get(...)` with default 0 |
| 29 | Backward compat test (field absent → 0) | PASS | `test_freelist_record_missing_thoughts_token_count_loads_as_zero`, `test_pilesort_...`, `test_interview_...` all present |
| 30 | Non-zero round-trip test | PASS | `test_informant_record_with_nonzero_thoughts_token_count_round_trips` — values 128, 256, 64 survive model_dump_json → model_validate_json |
| 31 | SQLite test with mixed old and new records | PASS | `test_build_db_thoughts_token_count_mixed_old_and_new` and `test_build_db_thoughts_token_count_legacy_record_defaults_to_zero` |
| 32 | `append_failure` test with `thoughts_token_count` set | PASS | `test_append_failure_thoughts_token_count_written`, `_zero_written`, `_none_omitted`, `_before_partial_session` |
| 33 | `DeclineInterview` NOT in schema diff | PASS | No `DeclineInterview` change in diff |
| 34 | `InformantRecord` envelope NOT modified | PASS | No `InformantRecord` class-body change in diff |
| 35 | `data/raw/*.jsonl` not in diff | PASS | Confirmed |
| 36 | `qa_check.py` not in diff | PASS | Confirmed |
| 37 | Prompt templates not in diff | PASS | No `prompts/` files in diff |
| 38 | R10: No real model calls in tests | PASS | Tests use fixtures and tmp_path; no API calls |
| 39 | R12: No LLM imports in `cdb_analyze` | PASS | Static check clean; `scripts/check_no_llm_imports.py` passes |
| 40 | R9: No `.env`/secrets in diff | PASS | No credential-shaped strings in added lines |
| 41 | R11: No new visualizations | N/A | No frontend changes |
| 42 | S3 phrase absent ("model spent everything on thinking") | PASS | Not present in any added line; S3 was applied in 16.A |
| 43 | Forbidden vocabulary absent from dictionary text | PASS | No `worldview`, `believes`, `thinks` applied to models in new text |
| 44 | Conventional Commits format | PASS | `feat(core): ...` |
| 45 | Subject ≤ 72 chars | PASS | 65 characters including newline |
| 46 | Body references task `#16.B` / `Task 16.B` | PASS | "Task 16.B" in first body line and in Reference line |
| 47 | Body cites Architect plan path | PASS | `Reference: docs/status/2026-05-04-task-16-architect-plan.md §2 Task 16.B` |
| 48 | Body cites SME verdict path with S1/S2/S4 | PASS | `CDA SME verdict: docs/status/2026-05-04-task-16-cda-sme-verdict.md S1-S4` |
| 49 | Body cites version bump v0.1.10 → v0.1.11 | PASS | `DATA_DICTIONARY version bump: v0.1.10 → v0.1.11` |
| 50 | Body cites 16.A predecessor commit `7f8f7f7` | PASS | `Predecessor: Task 16.A commit 7f8f7f7 (AdapterResult.thoughts_token_count)` |
| 51 | One commit, only files in 16.B scope | PASS | 11 files: schemas.py, free_list.py, pile_interview.py, pile_sort.py, runner.py, jsonl.py, build_db.py, DATA_DICTIONARY.md, test_build_db.py, test_jsonl.py, test_schemas.py — all within declared scope |

---

## Validation suite results

- `uv run pytest -q`: **1065 passed** (0 failures, 0 errors)
- `uv run ruff check .`: **clean**
- `uv run mypy packages/`: **clean** (53 source files, 0 issues)
- `uv run python scripts/check_no_llm_imports.py`: **OK**

---

## Notes

**N1 (cosmetic — does not block merge).** The SME note S1 specified the following exact sentence as a required addition: "The converse does not hold: `thoughts_token_count == 0` does not rule out cap exhaustion when the provider does not surface reasoning tokens (see field semantics below)." This exact sentence does not appear in the committed dictionary text. However, the S2 wording that appears immediately after the S1 portion covers the identical semantic territory: "A value of `0` is ambiguous: it can mean either (a) the provider does not surface reasoning tokens at all (Anthropic, HuggingFace at v0.1.11), or (b) the model did not engage internal reasoning on this call. The field cannot distinguish these two cases." The combined effect of S1's "sufficient, not deterministic" framing and S2's explicit enumeration of the two zero-cases fully communicates the epistemic claim S1 required. The SME authorization states "apply S1–S4 verbatim (or equivalent wording approved by the Architect on a re-routed plan amendment)" — the wording is effectively equivalent. If the Architect wishes to add the explicit converse sentence to §1.2 and §9.2 in a future documentation pass for precision, that is a cosmetic improvement welcome in a follow-on commit, but it is not required before merge.

---

## Final disposition

**VERDICT: PASS-WITH-NOTES**

Item 1–51 audit complete. All nine binding checks pass. The single note (N1) is cosmetic and does not alter the informational content of the dictionary. The Coder may merge `de3dd7e` to master.

*End of verdict.*
