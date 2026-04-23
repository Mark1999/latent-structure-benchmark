# Reviewer Verdict — Phase 4a.1 T1-update (task #21.T1-update)

**Date:** 2026-04-23
**Reviewer:** LSB Reviewer (Sonnet 4.6)
**Commit reviewed:** `1f0210c` — `feat(collect): T1-update exclusion filter + $10 cap (task #21.T1-update)`
**Files reviewed:**
- `/opt/lsb-agent/scripts/run_decline_backfill.py` (1038 lines post-update, diff: +540 lines)
- `/opt/lsb-agent/tests/test_run_decline_backfill.py` (1622 lines post-update, diff: +710 lines)
- `/opt/lsb-agent/tests/fixtures/failures_mixed_sample.jsonl` (new, 9 lines)
- `/opt/lsb-agent/tests/fixtures/failures_unclassified_saturation.jsonl` (new, 3 lines)

**Prerequisite documents read:**
- `CLAUDE.md` §6 (15 binding rules), §7 (forbidden vocabulary table), §8 (commit conventions)
- `ARCHITECTURE.md` §1.5.4 (forbidden vocabulary superset)
- `SECURITY_AND_HARDENING.md` §9 (Reviewer rules table R1–R12)
- `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md` (Amendment 1 spec)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (SME PASS-WITH-NOTES, binding notes A1–A8)
- `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md` (prior T1 PASS, for regression baseline)

---

## REVIEWER VERDICT: PASS-WITH-NOTES

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

**Amendment-binding-note scorecard (A1–A8):**

| Note | Status |
|---|---|
| A1 — Safety-filter-before-infrastructure precedence | PASS |
| A2 — `jailbreak` in SAFETY_FILTER_MARKERS | PASS |
| A3 — empty_response distinct branch + correct matcher + documented refinement | PASS |
| A4 — unclassified-saturation tripwire: >2 → SURFACE-TO-SME exit 2 | PASS |
| A5 — T5 §5 by-identifier enumeration (design-level; Section 3b is source material) | PASS |
| A6 — T3A recursive-decline inspection before T3B (documented, operator gate) | PASS |
| A7 — Section 3b controlled-vocabulary header with all 6 rationale keys | PASS |
| A8 — Dual cost projections (full + post-exclusion); pre-flight gate uses post-exclusion | PASS |

**Commit subject check:** PASS (72 characters, at the limit; see note below)

**Supplementary finding (non-blocking):** The `SAFETY_FILTER_MARKERS` constant includes `"OTHER"` (Gemini generic content-block finish_reason), which will case-insensitively match any error message containing the substring "other" (e.g., "Connection error due to another provider"). The review scope explicitly requires the code to document this behavior with a comment. The current comment reads only `# Gemini's generic content-block finish_reason` with no warning about the false-positive risk. The unclassified-saturation fixture is correctly crafted to avoid this edge case. No test relies on "other" being matched or unmatched in a fragile way. This is a SME-acknowledged known trade-off; the documentation gap is a minor note, not a blocking defect.

---

## Notes (all non-blocking)

### N1 — Commit subject deviates from Architect plan specification (style note)

The Architect plan Amendment 1 §6 specified the exact commit subject as:
```
feat(collect): T1-update exclusion filter + $10 cap + 3b/3c audit (task #21.T1-update)
```
(86 characters — itself over the 72-char limit from the plan document)

The committed subject is:
```
feat(collect): T1-update exclusion filter + $10 cap (task #21.T1-update)
```
(72 characters, exactly at the limit)

The Coder shortened the subject to fit the 72-char rule, dropping `+ 3b/3c audit`. This is a correct application of §8 conventions. The plan's specified subject was itself over the limit; the Coder's adjustment is the right call. Non-blocking.

### N2 — Commit body does not reference the prior T1 reviewer verdict file

The commit body references:
- `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md` ✓
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` ✓

It does not reference:
- `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md` (prior T1 PASS closure)

CLAUDE.md §8 requires commit bodies to reference "the gate verdicts." The prior T1 reviewer verdict is part of the amendment's authorization chain (T1 closed → Amendment 1 triggered → T1-update). A reference to the prior T1 verdict file would make the audit chain explicit. However, the real-data dry-run result in the commit body (`32 detected, 5 excluded, 27 post-exclusion, $1.35 < $8.00, GO`) implicitly establishes continuity with T1. The SME and Amendment 1 plan are both referenced. Non-blocking, but future commits in this chain should carry the full verdict chain for traceability.

### N3 — "OTHER" marker false-positive behavior not documented in code comment

The `SAFETY_FILTER_MARKERS` constant includes `"OTHER"` at line 108 of `scripts/run_decline_backfill.py` with the comment:
```python
"OTHER",                  # Gemini's generic content-block finish_reason
```

The review scope requires: "The comment in the code documents this behavior" (referring to the known false-positive risk: any error message containing the substring "other" case-insensitively will be matched and INCLUDE-d). The current comment does not warn about this. The fixture crafting correctly avoids this edge case, and no test relies on "other" being matched or unmatched in a fragile way. The SME explicitly noted this is a known trade-off. A comment like `# NOTE: case-insensitive; will match any message containing "other" substring` would satisfy the requirement. Non-blocking given SME acknowledgment.

---

## Check-by-check findings

### Check 1 — No LLM imports: PASS

Grepped all changed files in the diff for `import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`, `google.generativeai`. No matches in the diff. Confirmed `packages/cdb_analyze/` has no live LLM imports (the `__init__.py` guard comment is not an import). The script imports only stdlib, `pathlib`, `argparse`, `json`, `collections`, and `cdb_collect.decline_detection`. PASS.

### Check 2 — Append-only JSONL: PASS

`git show 1f0210c --name-only` lists exactly four files: `scripts/run_decline_backfill.py`, `tests/test_run_decline_backfill.py`, `tests/fixtures/failures_mixed_sample.jsonl` (new), `tests/fixtures/failures_unclassified_saturation.jsonl` (new). Neither `data/raw/informants.jsonl` nor `data/raw/failures.jsonl` appear in the commit. Exclusion is filter-at-consume as specified. The test suite includes `TestSection3bExcludedAudit` and `TestSection3cUnclassified` tests that verify the dry-run path does not write to output files. PASS.

### Check 3 — No secrets: PASS

All `+` lines in the diff scanned for: API keys, tokens, webhook URLs (`LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`), passwords, `sk-` prefixes, `Bearer` tokens, credential-shaped strings. No matches in the script, test file, or fixture files. The fixture JSONL files contain only synthetic model identifiers (`microsoft/phi-4`, `google/gemini-2.5-pro`, etc.) and plausible error messages — no credential patterns. PASS.

### Check 4 — Forbidden vocabulary: PASS

Full diff scanned for CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
- `worldview`, `believes`, `thinks` (as model agency): not found
- `cultural bias` (standalone): not found
- `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`: not found
- `publishable` (for LSB findings): not found
- `How models see the world`, `Model X's worldview`, `What the model understands`: not found

The commit uses `refusal`, `refusals`, `safety-filter refusals` — these are approved protocol terms per the CDA instrument description (the SME verdict explicitly uses these terms). "Declined" and "decline-interview" are approved. PASS.

### Check 5 — Schema + DATA_DICTIONARY: N/A

No changes to `cdb_core/schemas.py` or any Pydantic model. Confirmed by `git show 1f0210c --name-only`.

### Check 6 — New deps sign-off: N/A

`pyproject.toml` and `apps/dashboard/package.json` not in the diff. The script uses only packages already in the project's dependency set (`cdb_collect` internal, stdlib). No new top-level dependencies.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/prompts/`. Confirmed by `git show 1f0210c --name-only`.

### Check 8 — Uncertainty in viz: N/A

No frontend or visualization code in this commit. Scripts-only.

### Check 9 — Prerequisite verdicts: PASS

This commit is a methodology-adjacent task (exclusion criteria for the decline-interview backfill). The CDA SME PASS-WITH-NOTES verdict on Amendment 1 §2 exclusion rule is present at `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md`. The commit body references both the Amendment 1 plan and the SME verdict by path. The binding notes A1–A8 from the SME are all addressed (see amendment-binding-note scorecard above). The prior T1 reviewer PASS is on file at `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md`. PASS.

---

## Amendment-binding-note verification detail

### A1 — Safety-filter-before-infrastructure precedence: PASS

`should_include_failure()` at `scripts/run_decline_backfill.py` lines 171–182 confirms Step 1 (safety-filter substring scan) executes before Step 2 (HTTP infrastructure check). The test `test_safety_filter_blocked_overrides_httpstatuserror` directly covers the case where `HTTPStatusError` with `"blocked"` in the message → INCLUDE rather than EXCLUDE. PASS.

### A2 — `jailbreak` in SAFETY_FILTER_MARKERS: PASS

Line 104: `"jailbreak",  # SME A2: canonical refusal-vocabulary term`. Test `test_safety_filter_jailbreak_marker` at line ~1108 uses an error message containing `"jailbreak"` and no earlier safety marker, asserting `include is True` and `"jailbreak" in rationale`. PASS.

### A3 — Empty-response cohort distinct branch + correct matcher + documented refinement: PASS

The dedicated branch appears at lines 188–207, BEFORE the `PARSE_EXHAUSTION_MARKERS` step (Step 5). Matcher logic: `error_type == "ValueError"`, sentinel `"Could not extract valid JSON from response: "` is in `error_message`, and the fragment after the sentinel position is blank/whitespace-only. Returns `"empty_response:likely_silent_safety_block"`.

The Coder's refinement is documented in a multi-line comment at lines 196–201 explaining why the spec pseudocode's `endswith(":")` check would false-positive on partial-output messages like `'Could not extract valid JSON from response: {"foo":'`. The tighter test (whitespace-only after sentinel) is demonstrably more correct.

Test `test_empty_response_likely_silent_safety_block` verifies the exact Gemini input shape routes to `"empty_response:likely_silent_safety_block"`. Test `test_empty_response_distinct_from_parse_exhaustion` verifies that `'Could not extract valid JSON from response: {"foo":'` does NOT route to `empty_response` (it falls to parse_exhaustion). The partial-output message contains the sentinel prefix but has non-blank content after it. Logic traced:
- `after_sentinel = '{"foo":'`
- `after_sentinel.strip() = '{"foo":'` (non-empty → does not match empty_response branch)
- Falls to Step 5: `"Could not extract valid JSON from response"` is in the message → `parse_exhaustion:Could not extract valid JSO`

Also verified: fixture line 5 (`error_message = "Could not extract valid JSON from response: \nSAFETY filter applied."`) routes to Step 1 safety-filter match (`"safety"` or `"SAFETY"` substring) rather than to the empty_response branch — correct because the content after the sentinel is `"\nSAFETY filter applied."` which is non-blank. PASS.

### A4 — Unclassified-saturation tripwire: PASS

`surface_to_sme` flag is set at lines 760–770 when `source != "informants"` and `n_unclassified > 2`. When `surface_to_sme` is True, the disposition is `"SURFACE-TO-SME"` and the function returns 2.

Tests verify:
- `test_section3c_surface_to_sme_when_exceeds_2`: 3 unclassified (from fixture) → exit 2, `"SURFACE-TO-SME"` in output
- `test_section3c_at_exactly_2_still_go`: exactly 2 unclassified → no `"SURFACE-TO-SME"` in output
- `test_cost_guard_surface_overrides_go`: unclassified saturation + cost under threshold → still SURFACE-TO-SME

The `failures_unclassified_saturation.jsonl` fixture has 3 entries with `WeirdError`, `StrangeError`, `UnknownError` error types and error messages that contain no substring matching any SAFETY_FILTER_MARKERS (confirmed: none contain "safety", "blocked", "other", "jailbreak", etc.). PASS.

### A5 — T5 §5 by-identifier enumeration (design-level): PASS

The `should_include_failure()` docstring explicitly documents:
> Note on T5/T3A/T3B (SME A5): Section 3b output (identifier + rationale) is the source material for T5 §5 "Exclusion rule applied" by-identifier enumeration. The identifier is produced by _failure_identifier() as: failure|<model_id>|<domain>|<run_index>|<timestamp>

Section 3b audit rows emit `(identifier, error_type, rationale)` per excluded record. The identifier format is stable and round-trippable. PASS.

### A6 — T3A recursive-decline inspection before T3B (operator gate): PASS

Documented in the commit body:
> A6 — T3A recursive-decline inspection before T3B authorization is an operator/SME protocol gate; A6 binds at T3B authorization time

And in the module docstring at lines 34–36. The gate is correctly identified as outside the code's scope — it is an operator/SME protocol gate. PASS.

### A7 — Section 3b controlled-vocabulary header with all 6 rationale keys: PASS

Lines 657–684 of the script print the rationale taxonomy header before the per-record rows. All six keys are present:
- `http_infrastructure:{exception_type}`
- `adapter_pre_generation_parse:{exception_type}`
- `safety_filter:matched:{marker}`
- `parse_exhaustion:{marker}`
- `empty_response:likely_silent_safety_block`
- `unclassified:default_include:{exception_type}`

Test `test_section3b_header_present_with_taxonomy` asserts all six keys appear in captured output. PASS.

### A8 — Dual cost projections, pre-flight gate uses post-exclusion: PASS

Section 5 (lines 820–866) prints:
- `Full-count projection: $ (N * 0.05) = $X.XX`
- `Post-exclusion projection: $ (M * 0.05) = $Y.YY`

Pre-flight gate uses `post_excl_cost >= escalation_threshold` (not `full_cost`).

Tests verify:
- `test_summary_prints_both_projections`: both projection lines present in output
- `test_cost_guard_uses_post_exclusion_count`: 5 excluded HTTPStatusError failures → gate input is post-exclusion count ($0.15), not full count
- `test_cost_guard_go_under_post_exclusion_threshold`: 3 informants + 5 excluded failures → GO
- `test_cost_guard_stop_at_post_exclusion_threshold`: 160 informants-origin → STOP at $8.00

PASS.

---

## Scope discipline checks

**`--execute` path still raises `NotImplementedError`:** Confirmed at lines 1021–1023. The error message now points to the Amendment 1 plan document. PASS.

**Frozen files untouched:** `decline_detection.py`, `run_decline_interview.py`, `jsonl.py`, `schemas.py` — none appear in `git show 1f0210c --name-only`. PASS.

**No new dependencies:** `pyproject.toml` not in diff. Script's new imports are only stdlib additions (`collections.defaultdict` was already in scope). PASS.

**Fixtures are synthetic:** Both new fixture files contain clearly synthetic model IDs (`some/model`, `microsoft/phi-4`, `google/gemini-2.5-pro`) and timestamp values in 2026 test ranges. No real data. PASS.

---

## Coder deviation disclosure verification

The one documented deviation: the empty-response matcher uses `not after_sentinel.strip()` (whitespace-only after sentinel) rather than the spec pseudocode's `rstrip().endswith(":")` or `rstrip().endswith(": ")`.

Verification:
1. The tightened matcher correctly isolates the Gemini empty-response cohort: `"Could not extract valid JSON from response: "` (trailing space, empty after) passes; `"Could not extract valid JSON from response: {"foo":"` (non-blank after) does not.
2. Both test cases pass: `test_empty_response_likely_silent_safety_block` (empty) and `test_empty_response_distinct_from_parse_exhaustion` (partial output).
3. The docstring at lines 196–201 documents the refinement clearly and explains why the spec pseudocode would have produced false positives.

The deviation is a correctness tightening, not a weakening. Documentation is present. PASS.

---

## Prior T1 regression check

All nine checks from `docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md` were re-verified against the current state of the script and test suite. No regressions introduced. The `originating_step` column added in commit `24102fd` remains intact in the Section 3 output. The existing 46 tests still cover the original T1 acceptance criteria.

---

## T1-update disposition

**T1-update is PASS-WITH-NOTES.** Three non-blocking notes recorded (N1, N2, N3). None require rework before merge. All nine checks PASS. All eight SME binding notes (A1–A8) are addressed.

**Notes N1–N3 disposition:**
- N1 (commit subject): No action. Coder correctly shortened to fit §8 72-char limit.
- N2 (missing prior T1 verdict reference): Carry-forward note for T2 and subsequent commits; include the full verdict chain `2026-04-23-phase4a1-t1-reviewer-verdict.md` in future commit bodies for this task chain.
- N3 (`OTHER` marker comment): Coder may add a terse inline warning comment to `SAFETY_FILTER_MARKERS` at line 108 in a follow-up commit or as part of T2. Not required before proceeding.

**Next task:** T2 — execute path filter + per-source counters.

---

*Verdict saved to `docs/status/2026-04-23-phase4a1-t1-update-reviewer-verdict.md`. Binding for task #21.T1-update.*
