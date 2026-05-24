# LSB Reviewer Verdict — Phase 9a T9: PileComparison Frontend (second pass)

**Date:** 2026-05-24
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Task:** Phase 9a T9 — PileComparison frontend component
**Review pass:** Second pass (re-review after FAIL on first pass)
**First-pass FAIL verdict:** `docs/status/2026-05-24-phase9a-T9-reviewer-verdict.md` (overwritten by this document)
**Gate verdicts received:**
- CDA SME: PASS-WITH-NOTES — `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`
- UI/UX: PASS-WITH-NOTES — `docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md`
- T5-mini Reviewer: PASS — `docs/status/2026-05-24-phase9a-T5mini-reviewer-verdict.md`

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        PASS
Check 9 — Prerequisite verdicts:     PASS
```

**First-pass failures — both resolved:**

```
Copy in dedicated files:             PASS (was FAIL)
Absent placeholder placement:        PASS (was FAIL)
```

---

## Check Details

### Check 1 — No LLM imports in cdb_analyze/

This is a frontend-only PR. No Python files in `packages/cdb_analyze/` were modified. The grep for
`import anthropic`, `import openai`, `from anthropic`, `from openai`, `InferenceClient`, and
`google.generativeai` in `packages/cdb_analyze/` returns only comment text (in `__init__.py`
documenting what is forbidden), not live imports. PASS.

### Check 2 — Append-only JSONL

`data/raw/informants.jsonl` is not in the working tree diff. No pre-existing lines were modified.
PASS.

### Check 3 — No secrets

All changed files scanned (`apps/dashboard/src/copy/pile_comparison.ts`,
`apps/dashboard/src/components/PileComparison.tsx`). No API keys, webhook URLs, tokens,
passwords, or credential-pattern strings found. PASS.

### Check 4 — Forbidden vocabulary

Scanned both changed files and the broader new-file set
(`PileComparisonTable.tsx`, `pile-comparison.css`, `t9-pile-comparison.test.tsx`) for all
CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden phrases:
- `worldview`, `believes`, `thinks` (model-applied): not present in user-facing context
- `how models see the world`, `cultural bias` (standalone), `what the model understands`: absent
- `within-model consensus/cultural/eigenratio/CCM`, `publishable`: absent

The `pile_comparison.ts` copy file comments and `PileComparison.tsx` header comments *name* the
forbidden terms only to document they were scanned and are clean — this is internal documentation,
not model-facing text. PASS.

### Check 5 — Schema + DATA_DICTIONARY

N/A. This PR does not touch `cdb_core/schemas.py`. The schema work for `centroid_piles`
was handled in the prior T5-mini commit (carrying its own Reviewer PASS).

### Check 6 — New deps sign-off

N/A. `apps/dashboard/package.json`, `apps/dashboard/package-lock.json`, and `pyproject.toml`
are unmodified. No new dependencies introduced.

### Check 7 — Prompt versioning

N/A. No files under `packages/cdb_collect/prompts/` were modified.

### Check 8 — Uncertainty in viz (R10)

The pile comparison is a categorical (not numeric) display. Uncertainty is expressed via three
stability tiers (solid / dashed-medium / dashed-low border classes) on every term pill, with a
tooltip on every pill showing placement percentage (or the unavailable fallback from
`PILE_COMPARISON_STABILITY_TOOLTIP_UNAVAILABLE`). The legend row explains the three tiers.
No bare point estimates without uncertainty indicators. PASS.

### Check 9 — Prerequisite verdicts

Both required gate verdicts are present and carry PASS-WITH-NOTES (acceptable per CLAUDE.md §11):
- CDA SME PASS-WITH-NOTES: `docs/status/2026-05-24-phase9a-cda-sme-verdict.md` — M7 binding
  implemented correctly (all columns equal width/weight, no "agreement score" in this view).
- UI/UX PASS-WITH-NOTES: `docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md` — all six binding
  notes (N1–N6) implemented. The two notes that produced the first-pass FAIL are now resolved
  (see below). PASS.

---

## First-Pass Failure Resolution Verification

### Failure 1 resolved — Three inline strings moved to copy file

**Original failure:** `"Pile structure comparison"` (line 226), `"Select model to view"` (line 256),
and `` `Stability data not available for ${shortName}.` `` (line 492) were inline in
`PileComparison.tsx`.

**Fix verified:**
- `/opt/lsb-agent/apps/dashboard/src/copy/pile_comparison.ts` lines 77, 80, 83–85:
  `PILE_COMPARISON_SR_HEADING`, `PILE_COMPARISON_MODEL_SWITCHER_ARIA_LABEL`, and
  `PILE_COMPARISON_STABILITY_TOOLTIP_UNAVAILABLE` are now exported from the copy file.
- `/opt/lsb-agent/apps/dashboard/src/components/PileComparison.tsx` lines 69–71: all three
  are imported from `../copy/pile_comparison`.
- `/opt/lsb-agent/apps/dashboard/src/components/PileComparison.tsx` lines 229, 259, 495:
  the three constants/functions are used in place of the former inline strings.
- `grep` for the literal inline strings (`"Pile structure comparison"`,
  `"Select model to view"`, `"Stability data not available"`) in `PileComparison.tsx` returns
  no results. Confirmed clean.

### Failure 2 resolved — Absent-term placeholder now renders in first pile card only

**Original failure:** The absent placeholder rendered in every pile card when a term was absent
from a model with multiple piles — N pills per column instead of 1.

**Fix verified:**
- `/opt/lsb-agent/apps/dashboard/src/components/PileComparison.tsx` lines 524–535:
  The guard condition is `pileIdx === sortedPileIndices[0] && hoveredTerm !== null &&
  allTermsAcrossModels.has(hoveredTerm) && !ownTerms.has(hoveredTerm)`.
  The `pileIdx === sortedPileIndices[0]` guard is the first condition, so the placeholder
  renders exactly once per column (in the first pile card by sort order).
  This matches DESIGN_SYSTEM.md §12.10 binding specification.

---

## No New Issues Introduced

The two fixes are mechanical and isolated:
1. Three constant declarations added to `pile_comparison.ts`; three import names added to the
   existing import block in `PileComparison.tsx`; three usage sites updated.
2. One additional boolean guard prepended to the existing absent-placeholder condition.

No logic changes, no new dependencies, no new tokens, no schema changes. All nine checks confirm
PASS. Coder may merge.

---

*End of Reviewer verdict (second pass). Coder may merge. Only Mark can override.*
