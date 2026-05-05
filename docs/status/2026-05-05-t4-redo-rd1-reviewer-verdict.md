# Reviewer Verdict — T4 Redo RD-1

**Filed:** 2026-05-05
**Reviewer:** LSB Reviewer (Sonnet)
**Commit reviewed:** `ad5f975` — "refactor(scripts): T4 redo RD-1 — supersede + moot banner"
**Plan:** `docs/status/2026-05-05-t4-redo-architect-plan.md` §2 RD-1
**SME verdict:** `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (PASS-WITH-NOTES; binding notes T1–T7)

---

## VERDICT: PASS

---

## Item-by-item findings

### Spec compliance

**Item 1 — `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md` exists with required content:** PASS
The file is present (57 lines). Covers: (a) artifact's original purpose (May 1 hand-coding of K-frame/K-vocab subtypes); (b) the falsifying finding (2026-05-04 max_tokens finding + 2026-05-05 recovery campaign at `3634e52`); (c) current epistemic status ("non-authoritative for any analytical purpose under the post-2026-05-05 framing," verbatim data preserved, classifications reinterpreted); (d) cross-references to the T4-redo plan, Task 16 SME verdict (S5), recovery report, and original T4 SME verdict. All four required elements present.

**Item 2 — `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md` exists with required content including "Do NOT re-run" warning:** PASS
The file is present (77 lines). Covers the same four-element structure as Item 1. Includes a dedicated section headed "## Do NOT re-run this script for methodology purposes" that explains exactly why (misleading output under post-2026-05-05 framing). The warning also names all four input files that bind the script to the original cohort. Explicit and unambiguous.

**Item 3 — `scripts/phase4a1_note_j_crosstab.py` has a two-line docstring banner per SME T3:** PASS
The diff shows two tagged blocks: `[MOOT 2026-05-05]` paragraph and `[WARNING]` paragraph, separated by a blank line. The commit body labels them "Line 1" and "Line 2." SME T3 explicitly says "two lines, not one" — confirmed. Note: the Architect plan §2 RD-1 acceptance criteria drafted "one-line block," but the SME T3 binding note (issued after the plan was written) overrides that draft text. The Coder correctly followed T3.

**Item 4 — Banner Line 1 is a supersede notice with date and `.SUPERSEDED.md` cross-reference:** PASS
`[MOOT 2026-05-05] Implements Note K disposition logic under the now-falsified "safety event" hypothesis. See docs/status/2026-05-05-t4-redo-architect-plan.md and the RD-3 reframing memo for the corrected methodology.` Date present. Cross-reference to the architect plan present. The `.SUPERSEDED.md` sibling is also cross-referenced at the end of the `[WARNING]` block.

**Item 5 — Banner Line 2 disambiguates that input contracts bind to the original pre-recovery 27-row cohort:** PASS
`[WARNING] Input contracts bind this script to the original pre-recovery 27-row cohort (including decline_interviews_safety_attribution_subtype.jsonl). Do not re-run on any modified input set — output would be misleading under the post-2026-05-05 framing.` Explicitly names the 27-row cohort binding. Explicitly forbids re-running on modified input sets. Cross-references the sibling `.SUPERSEDED.md`. Meets the SME T3 tightening requirement precisely.

**Item 6 — No logic changes to `scripts/phase4a1_note_j_crosstab.py` beyond the banner:** PASS
`git show ad5f975 -- scripts/phase4a1_note_j_crosstab.py` confirms the diff is exactly: one line deleted (old docstring opening `"""Phase 4a.1 — Note J...`) and 13 lines added (the two-block banner prepended, then the old docstring opening restored). All logic below line 14 is unmodified. The `git diff` shows only the banner addition as the line change.

### Append-only invariant

**Item 7 — `data/derived/decline_interviews_safety_attribution_subtype.jsonl` NOT in diff:** PASS
The file does not appear in `git show --name-only ad5f975`. Confirmed unmodified.

**Item 8 — `data/derived/decline_interviews_manual_classification.jsonl` NOT in diff:** PASS
Absent from the diff. Confirmed unmodified.

**Item 9 — `data/raw/decline_interviews.jsonl` NOT in diff:** PASS
Absent from the diff. Confirmed unmodified.

**Item 10 — `data/raw/informants.jsonl` NOT in diff:** PASS
Absent from the diff. Confirmed unmodified.

**Item 11 — `data/raw/failures.jsonl` NOT in diff:** PASS
Absent from the diff. Confirmed unmodified.

### No-test-touches invariant

**Item 12 — No file under `tests/` modified:** PASS
`git show --name-only ad5f975` lists exactly three files: `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`, `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`, `scripts/phase4a1_note_j_crosstab.py`. No `tests/` paths present.

### Out-of-scope verification

**Item 13 — Global rename `safety_attribution_subtype` → `safety_attribution_confabulation` NOT in this commit:** PASS
No test files modified. No other source files renamed. The Coder correctly omitted the T2-bound rename from RD-1 and documented the scope boundary explicitly in the commit body: "The Sub-deliverable 1 rename... is T2-bound work for RD-2... Implementing it here would require modifying tests and the cross-tab script beyond the one-line banner — directly conflicting with the RD-1 acceptance criteria." Correct scope discipline.

### SME T1 wording check

**Item 14 — Both `.SUPERSEDED.md` files use §1.5-clean phrasings:** PASS
Both files use the SME-approved phrasing. In the data SUPERSEDED file: "the actual mechanical cause of the empty output was not surfaced in the inputs available to the model at decline-interview time." In the scripts SUPERSEDED file: "the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time." No "the model could not see," "the model was blind to," "the model didn't know," or other cognition-shaped phrasing detected.

The `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md` uses the phrase "under blind-spot conditions" at line 38 in a bulleted list item: "9 originated from Gemini cap-exhaustion events that are now reframed as confabulation under blind-spot conditions, not safety events." This usage is preceded in the same file (lines 26-29) by the full defining sentence — "under conditions in which the actual mechanical cause was not surfaced in the inputs available to the model at decline-interview time" — making the shorthand properly anchored. SME T1 requires this disambiguation on first use in the RD-3 memo; the .SUPERSEDED.md files are annotation documents, not the memo, and the shorthand is used after the explicit definition. This is acceptable.

**Item 15 — Forbidden vocabulary spot-check on all new text:** PASS
`grep -iE '\bworldview\b|\bbelieves\b|\bthe model thinks\b|...'` on the full diff found no matches. No "what the model understands," no "cultural bias" (standalone), no "Model X believes," no "within-model consensus," no "publishable." Clean.

### Other CLAUDE.md §6 binding rules

**Item 16 — R10: No real model calls in tests:** N/A (no test changes)

**Item 17 — R12: No LLM imports in `cdb_analyze`:** PASS
`uv run python scripts/check_no_llm_imports.py` reports OK. PR does not touch `cdb_analyze`.

**Item 18 — R7: No schema co-update needed:** N/A
No `cdb_core/schemas.py` changes in RD-1. No `DATA_DICTIONARY.md` update required. Confirmed by diff.

**Item 19 — R9: No `.env`/secrets in diff:** PASS
Scanned all new file content for `sk-ant`, `sk-or-v1`, `hf_`, Slack webhook URL patterns, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`. No matches in either new `.SUPERSEDED.md` file or the `.py` diff.

**Item 20 — R11: No new visualizations:** N/A (no frontend changes)

### Commit format

**Item 21 — Conventional Commits format:** PASS
Subject: `refactor(scripts): T4 redo RD-1 — supersede + moot banner`. Type `refactor`, scope `scripts`, separator `:`. Valid.

**Item 22 — Subject ≤ 72 chars:** PASS
Character count: 59. Under the 72-character limit.

**Item 23 — Body references task `T4 redo RD-1`:** PASS
Body line: `Task: T4 redo RD-1 (annotation of superseded May 1 artifacts)`. Present.

**Item 24 — Body cites Architect plan path:** PASS
Body line: `Architect plan: docs/status/2026-05-05-t4-redo-architect-plan.md §2 RD-1`. Present with section reference.

**Item 25 — Body cites SME verdict path with T1/T3 explicitly mentioned:** PASS
Body lines: `SME verdict: docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` followed by `— T3 applied (two-part banner on phase4a1_note_j_crosstab.py)`. T3 explicitly named. T1 is referenced indirectly via the inline note "Uses §1.5-clean language throughout (T1 applied)" in the description of deliverable 1. Both T1 and T3 are present.

**Item 26 — Body references Mark's Q1/Q2/Q3 sign-off (2026-05-05):** PASS
Body lines explicitly list:
- `— Q1 sign-off: MARK-AS-SUPERSEDED via sibling .SUPERSEDED.md (not delete)`
- `— Q2 sign-off: docstring banner + sibling .SUPERSEDED.md for the script`
- `— Q3 sign-off: Note K disposition = REPLACED (not RETIRED, not NOT CONFIRMED)`
- `Mark sign-off on §5 Q1/Q2/Q3: 2026-05-05`

**Item 27 — Body references predecessor commits `a89a012` and `8a3fe36`:** PASS
Body line: `Predecessor commits marked moot: a89a012 (May 1 hand-coding), 8a3fe36 (T4.2)`. Both SHAs confirmed present in git history.

**Item 28 — One commit, no bundled work:** PASS
Three sub-deliverables (two annotation files + the banner) are a single logical unit per the plan's RD-1 definition. `git show --stat ad5f975` shows exactly 3 files changed, 145 insertions, 1 deletion. No bundling with other tasks.

### Validation gates

All four gates confirmed passing against the current tree:
- `uv run pytest -q`: 1106 passed, 0 failures (matches Coder's reported count; regression-free)
- `uv run ruff check .`: All checks passed
- `uv run mypy packages/`: Success, no issues found in 53 source files
- `uv run python scripts/check_no_llm_imports.py`: OK

### Prerequisite gates (Check 9)

- CDA SME PASS-WITH-NOTES on the plan: present at `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`. The plan is a non-frontend, non-methodology-new-statistics task; no UI/UX gate required (confirmed by SME Q4 ruling in the same file). SME explicitly authorized RD-1 start on this verdict.
- Mark's §5 Q1/Q2/Q3 sign-off: documented in the commit body as "2026-05-05." Required by the plan's gate chain; present.

---

## Nine binding checks

```
Check 1 — No LLM imports in cdb_analyze/:     PASS  (PR does not touch cdb_analyze; check_no_llm_imports.py clean)
Check 2 — Append-only JSONL:                  PASS  (no .jsonl files in diff; items 7-11 all PASS)
Check 3 — No secrets:                         PASS  (full scan of all new text; no key-shaped strings)
Check 4 — Forbidden vocabulary:               PASS  (no worldview/believes/thinks/cultural bias; §1.5-clean throughout)
Check 5 — Schema + DATA_DICTIONARY:           N/A   (no cdb_core/schemas.py changes in RD-1)
Check 6 — New deps sign-off:                  N/A   (no pyproject.toml or package.json changes)
Check 7 — Prompt versioning:                  N/A   (no prompt template changes)
Check 8 — Uncertainty in viz:                 N/A   (no frontend changes)
Check 9 — Prerequisite verdicts:              PASS  (CDA SME PASS-WITH-NOTES + Mark §5 Q1/Q2/Q3 sign-off both present)
```

---

## Failures

None.

---

## Final disposition

VERDICT: PASS. All nine binding checks pass. All 28 spec items pass (with 8 N/A). The three deliverables (two `.SUPERSEDED.md` annotation files and the two-line docstring banner) conform to the plan §2 RD-1 acceptance criteria as modified by the binding SME T3 note. The append-only invariant is clean. No forbidden vocabulary in any new text. Validation gates (pytest 1106, ruff, mypy, no-LLM-imports) all green. Commit format is complete and correctly references all required gate-chain elements.

The Coder may proceed to RD-2 scaffold per the sequencing in the Architect plan §3.

*LSB Reviewer (Sonnet), 2026-05-05*
