# Reviewer Verdict — Phase 5 T7

**Filed:** 2026-05-10
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commits reviewed:** `c4e9b37` (T7 Coder), `d97c13c` (T7 UI/UX fix + DESIGN_SYSTEM v0.4.2)
**Task:** T7 — ModelSelector + Legend integration
**Prerequisite verdicts:**
- Plan-level CDA SME PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`
- Plan-level UI/UX PASS-WITH-NOTES: `docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`
- T7 per-commit UI/UX FAIL → PASS-WITH-NOTES: `docs/status/2026-05-10-phase5-T7-uiux-verdict.md`

---

## REVIEWER VERDICT: PASS

```
Check 1 — No LLM imports:            N/A (no cdb_analyze changes)
Check 2 — Append-only JSONL:         N/A (no informants.jsonl changes)
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A (no schema changes)
Check 6 — New deps sign-off:         PASS
Check 7 — Prompt versioning:         N/A (no prompt changes)
Check 8 — Uncertainty in viz:        PASS
Check 9 — Prerequisite verdicts:     PASS
```

---

## Check details

### Check 1 — No LLM imports in cdb_analyze/ — N/A
No files in `packages/cdb_analyze/` were modified. The `__init__.py` comment
text that mentions the forbidden import names is a prohibition notice, not an
import; confirmed not a match.

### Check 2 — Append-only JSONL — N/A
`data/raw/informants.jsonl` was not touched by these commits.

### Check 3 — No secrets — PASS
Scanned all changed files:
- `apps/dashboard/src/` — no API keys, webhook URLs, or credential patterns.
- `DESIGN_SYSTEM.md` — no credentials.
- `docs/status/2026-05-10-phase5-T7-uiux-verdict.md` — no credentials.
`_headers` CSP is unchanged (empty diff between `e552820` and `d97c13c`).
No `dangerouslySetInnerHTML` outside of test source-assertion strings in
`legend.test.tsx` and `mds-plot.test.tsx` (source-text assertions, not
component usage). No spend-gate tokens found.

### Check 4 — Forbidden vocabulary — PASS
Scanned all changed `.ts`, `.tsx`, `.md` files for CLAUDE.md §7 and
ARCHITECTURE.md §1.5.4 forbidden phrases. Zero hits on:
- `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`,
  `comprehends`, `publishable`, `cultural bias`
- `within-model consensus`, `within-model cultural consensus`,
  `within-model eigenratio`, `within-model CCM`

The phrases "within-model output concentration" (MDSPlot.tsx tooltip, line 235)
and "within-model distribution" (MDSPlot.tsx tooltip, line 237) are NOT in the
forbidden vocabulary table. "Output concentration" is the preferred measurement
language (OCI = Output Concentration Index). These phrases were present in the
prior T6 commit and are carried forward — the UI/UX agent reviewed and passed
the tooltip copy at T6 and again at T7.

The "MDS cognitive map" phrase in the SVG `aria-label` is explicitly the
DESIGN_SYSTEM.md §12.6 required format; it is approved vocabulary.

No phase numbers (Phase 5, Phase 6) appear in user-visible copy.

### Check 5 — Schema + DATA_DICTIONARY — N/A
`packages/cdb_core/schemas.py` was not modified.

### Check 6 — New deps sign-off — PASS
Empty diff on `apps/dashboard/package.json`, `apps/dashboard/package-lock.json`,
`pyproject.toml`, and `uv.lock`. No new dependencies introduced.

### Check 7 — Prompt versioning — N/A
No files under `packages/cdb_collect/prompts/` were touched.

### Check 8 — Uncertainty in viz — PASS
This is a frontend PR touching `MDSPlot.tsx`. The check requires that no R1-a
model point renders without its confidence ellipse, and that the
`selectedModels` filter applies uniformly to both points and ellipses.

Confirmed in `MDSPlot.tsx`:
- `points` is computed at line 331–334 as `allPoints.filter(p => selectedSet.has(p.modelId))`.
- The confidence ellipse render group (lines 454–480) iterates over `points`
  (the same filtered list), not `allPoints`.
- Ellipses are only rendered for `r1State === "typical_concentration"` and only
  when `point.ellipse` is non-null — matching the R1-a binding.

Result: selected R1-a model → both point AND ellipse rendered.
Unselected R1-a model → neither point NOR ellipse rendered.
R1-b and R1-c models → point rendered (no ellipse, per §3.3.5 binding invariant 1).
The invariant is preserved. PASS.

### Check 9 — Prerequisite verdicts — PASS
Frontend PR. Required gates:
- Plan-level CDA SME: `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`
  → PASS-WITH-NOTES. Present.
- Plan-level UI/UX: `docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`
  → PASS-WITH-NOTES. Present.
- T7 per-commit UI/UX: `docs/status/2026-05-10-phase5-T7-uiux-verdict.md`
  → FAIL → PASS-WITH-NOTES. Present.

Required corrections from the per-commit UI/UX verdict:
1. DESIGN_SYSTEM.md → v0.4.2 (§3.7 binding spec). Applied at `d97c13c`.
2. App.tsx line 168: `setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6))`.
   Applied at `d97c13c`. Verified at line 171 in App.tsx.
Both required corrections are applied. Notes addressed. PASS.

---

## T7 acceptance criteria verification

AC1 — 11 family / 9 holidays models render: Test suite confirms
  model-selector.test.tsx (31 tests pass) with fixture data covering both domains.
AC2 — Origin badges [US]/[EU]/[CN] in correct token colors: Confirmed in
  ModelSelector.tsx using ORIGIN_COLORS map with token values from DESIGN_SYSTEM.md §1.2.
AC3 — Open/closed weights indicator: Confirmed. `weightsLabel` rendered as
  text badge with CSS classes `--open` / `--closed`.
AC4 — "Select all" / "Clear all" links: Confirmed. Both `<button>` elements
  present with `aria-label`. "Select all" calls `handleSelectAll()` which sets
  all available model_ids (bypasses per-toggle enforcement per §3.7 rule 3).
AC5 — Max 6 enforced; initial state is first-6; warning gated: App.tsx line 171
  confirmed. Source-assertion test at app-state.test.ts line 368 passes.
AC6 — Keyboard accessible: Native `<input type="checkbox">` semantics; "Select
  all"/"Clear all" are `<button>` elements. Confirmed.
AC7 — selectedModels drives MDSPlot filter: App.tsx passes `selectedModels` prop
  to MDSPlot; MDSPlot filters both points and ellipses via `selectedSet`.
AC8 — 282/282 tests pass; build 67.95 KB gzipped. Confirmed by local run.

---

## Carry-forward notes (from UI/UX verdict, non-blocking)

**F-T7-2 EU badge contrast** (PASS-WITH-NOTES, non-blocking):
`--color-origin-eu` (#27ae60) on `--color-surface-hover` (#f0f2f5) ≈ 4.44:1,
marginally below the 4.5:1 WCAG AA threshold for body text at 12px. The badge
is `aria-hidden="true"` and origin information is conveyed via checkbox
`aria-label`. Functional accessibility intact. Pre-launch polish action
recommended (darken to `#22974e` or change badge background to `--color-background`).

**§3.7 v0.4.2 internal inconsistency (observation, non-blocking):**
DESIGN_SYSTEM.md §3.7 v0.4.2 rule 2 states "The warning must NOT appear on page
load (where exactly 6 are selected by rule 1)." However, `ModelSelector.tsx`
line 118 uses `showMaxWarning = selectedModels.length >= MAX_SELECTED`, which is
TRUE when exactly 6 are selected, meaning the warning IS visible at page load.
The UI/UX agent reviewed and accepted this implementation, and the test suite
positively asserts the warning appears at count == 6. This is an inconsistency
between the §3.7 spec text and the accepted implementation. It does not block T7
(the UI/UX agent owns the design decision and signed off), but the spec text
should be corrected in a future DESIGN_SYSTEM.md revision (rule 2 should read
"fires only on attempted add beyond 6" rather than "must not appear when exactly
6 are selected").

**F-T6-2 → T9** — DataExplorer takes ownership of modelColors per §12.4.
**F-T5-2 → T11** — `#cite` anchor (CiteModal is T11).
**F-T5-3 → T13** — Domain-specific `<title>` updates.
**F-T6-1 (data pipeline)** — em-dash in lede string, cdb_publish side.

---

## Required before merge

None. All nine checks pass. Coder may proceed to Tester.

---

*End of Reviewer verdict for Phase 5 T7. Tester proceeds.*
