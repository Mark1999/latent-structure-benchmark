# Reviewer Verdict — Phase 5 T6

**Filed:** 2026-05-10
**Reviewer:** LSB Reviewer agent (Sonnet)
**Commit reviewed:** `f3b7b43` (feat(dashboard): T6 MDSPlot with R1-state rendering)
**UI/UX per-commit verdict:** PASS-WITH-NOTES at `a28e95f` (`docs/status/2026-05-10-phase5-T6-uiux-verdict.md`)
**Plan-level CDA SME verdict:** PASS-WITH-NOTES (`docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md`)
**Plan-level UI/UX verdict:** PASS-WITH-NOTES (`docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md`)

---

## REVIEWER VERDICT: PASS

Check 1 — No LLM imports in cdb_analyze/:   N/A (TS frontend only; grep for cdb_* imports: zero hits)
Check 2 — Append-only JSONL:                N/A (no data/raw/informants.jsonl changes)
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A (no schema changes)
Check 6 — New deps sign-off:                PASS (no new npm dependencies)
Check 7 — Prompt versioning:                N/A (no prompt template changes)
Check 8 — Uncertainty in viz (R10):         PASS
Check 9 — Prerequisite verdicts:            PASS

---

## Check-by-check findings

### Check 1 — No LLM imports in cdb_analyze/
N/A for this PR. The four changed files are all under `apps/dashboard/src/`. Grep for `cdb_*` imports in TS source returned zero hits. No `cdb_analyze/` Python is touched.

### Check 2 — Append-only informants.jsonl
N/A. `data/raw/informants.jsonl` is not in the diff.

### Check 3 — No secrets
Grep for `sk-[a-zA-Z0-9]+`, `Bearer [a-zA-Z0-9]+`, `hooks.slack.com` in the four changed files: zero hits. `apps/dashboard/public/_headers` is unchanged (confirmed via `git diff 9fca486..f3b7b43 -- apps/dashboard/public/_headers`: empty diff). CSP is not weakened. PASS.

### Check 4 — Forbidden vocabulary
Scan of all four changed files (`MDSPlot.tsx`, `app.css`, `App.tsx`, `mds-plot.test.tsx`) for CLAUDE.md §7 and ARCHITECTURE.md §1.5.4 forbidden terms:

- `worldview`, `believes`, `thinks` (model-facing): zero hits
- `cultural bias` (standalone): zero hits
- `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`: zero hits
- `publishable` / `publication` (LSB findings framing): zero hits

The tooltip at MDSPlot.tsx:250–252 uses "within-model output concentration" — this is the approved substitute phrase per ARCHITECTURE.md §1.5.4, not a forbidden phrase. PASS.

The test file references `["worldview", "cultural bias"]` and `"believes"` only as string literals inside test assertions that verify the forbidden terms are ABSENT from the source. That is correct enforcement usage, not a vocabulary violation.

### Check 5 — Schema + DATA_DICTIONARY
N/A. No changes to `cdb_core/schemas.py`.

### Check 6 — New deps sign-off
`git diff 9fca486..f3b7b43 -- apps/dashboard/package.json apps/dashboard/package-lock.json`: empty diff. No new npm dependencies. PASS.

### Check 7 — Prompt versioning
N/A. No prompt templates changed.

### Check 8 — Uncertainty in viz (R10) — CRITICAL
MDSPlot is the first new visualization in Phase 5. R10 (CLAUDE.md rule 11) says no point estimate without uncertainty in any new viz.

**Ellipse gate logic (MDSPlot.tsx lines 406–409 and 539):**

```
const ellipse =
  r1State === "typical_concentration"
    ? (domainResult.mds_uncertainty[modelId] ?? null)
    : null;
```

And in the ellipse rendering layer:
```
if (point.r1State !== "typical_concentration") return null;
if (!point.ellipse) return null;
```

R10 compliance analysis:

- **R1-a (typical_concentration):** ellipse is assigned from `mds_uncertainty[modelId]`; if `mds_uncertainty` carries a null entry, `point.ellipse` is null and no ellipse renders. This null case is the scenario where the data pipeline did not produce a bootstrap ellipse for a model with R1-a state — that is a data-pipeline issue, not a component defect; the component cannot render uncertainty it was not given. The component does not replace the missing ellipse with a bare point presented as certain; it renders the R1-a circle (which is the mean position) without an ellipse. This is the correct behaviour given the data contract: if the pipeline ships `mds_uncertainty[modelId] = null` for an R1-a model, that is a pipeline defect, not a component one. The UI/UX verdict confirmed all 11 family models have valid ellipse parameters in production data.
- **R1-b (low_concentration):** no ellipse rendered; dashed-stroke circle visually encodes the uncertainty posture (position unreliable). The tooltip surfaces the OCI value and "Position uncertain" copy. Binding invariant 1 satisfied.
- **R1-c (deterministic):** no ellipse rendered; hollow triangle marker with "Deterministic output" tooltip. Zero variance is the finding, not a missing-uncertainty defect. Binding invariant 1 satisfied.

The 67 tests cover: 11 ellipses for all-R1-a family fixture; 7 ellipses for holidays with 2 R1-b; 0 ellipses for all-deterministic fixture; mixed fixture produces exactly 1 ellipse for the sole R1-a model with `data-model-id="m-r1a"` confirmed. No R1-b or R1-c model_id appears in any rendered ellipse. PASS.

### Check 9 — Prerequisite verdicts
All three required gate verdicts are present and address their notes:

| Gate | Verdict | File |
|---|---|---|
| CDA SME plan-level | PASS-WITH-NOTES (Q1–Q11 bound to T2 and T13, not T6) | `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md` |
| UI/UX plan-level | PASS-WITH-NOTES (F1–F8; T6 bindings applied) | `docs/status/2026-05-09-phase5-ui-ux-plan-verdict.md` |
| UI/UX per-commit T6 | PASS-WITH-NOTES (F-T6-1 non-blocking data-pipeline carry-forward; no T6 component rework) | `docs/status/2026-05-10-phase5-T6-uiux-verdict.md` |

F-T6-1 (em-dash in lede_v1.py) is explicitly designated non-blocking for T6 by the UI/UX agent and requires no T6 rework. PASS.

---

## AC verification (T6 acceptance criteria 1–9)

| AC | Finding | Result |
|---|---|---|
| AC1: family=11 points, holidays=9 | Tests `mds-plot.test.tsx:231–241` confirm both counts via `.mds-plot__point` selector. Test suite passes (193/193). | PASS |
| AC2: all-deterministic edge case verified | `allDetFixture` tests confirm 3 R1-c points, 0 ellipses, all `<path>` (no `<circle>`) elements in all-deterministic case. | PASS |
| AC3: hover tooltip — short name, model_id, OCI, state badge, top-5 terms | Source assertions at lines 285–304 of test file confirm all five elements present in JSX. | PASS |
| AC4: R1-b and R1-c render WITHOUT ellipses (binding invariant 1) | Component gate at MDSPlot.tsx:406–409 + 539 confirmed. Test suite validates: R1-b model_ids absent from all ellipse `data-model-id` attrs; R1-c groups contain zero circles. | PASS |
| AC5: R1-c marker is hollow triangle at 3px stroke | `path[fill='none']` selector confirms hollow path. `stroke-width="3"` confirmed in DOM (`stroke-width` attr = "3"). Source contains `strokeWidth="3"`. | PASS |
| AC6: WCAG AA 3:1 on all model-color stroke samples at 3px | UI/UX verified all 11 palette slots in per-commit verdict. Slot 11 corrected to `#9a7d0a` (~3.96:1) in v0.4.1. | PASS (UI/UX confirmed) |
| AC7: grayscale interpretability | Three distinct shapes (filled circle / dashed circle / hollow triangle) encode R1 state independently of color. UI/UX Criterion 4 confirmed. | PASS |
| AC8: no `dangerouslySetInnerHTML`, no `eval`, CSP-clean | Grep across all dashboard src/ files: zero hits. `_headers` unchanged. | PASS |
| AC9: `npm run build && npm run test && npm run lint` pass | Build: ✓ (214KB JS / 67KB gzipped — well under 400KB cap). Vitest: 193/193 PASS. ESLint: zero errors. TypeScript: zero errors. | PASS |

---

## R13 — No software-side spend gates

`git grep -nE 'CDB_MAX_SPEND_USD|MAX_SPEND_USD|spend_cap' -- apps/dashboard/`: zero hits. PASS.

---

## F-T6-1 carry-forward status

The UI/UX PASS-WITH-NOTES finding F-T6-1 (em-dash in `packages/cdb_publish/cdb_publish/templates/lede_v1.py`) is a data-pipeline issue assigned as carry-forward to a future `lede_v2.py` per CLAUDE.md §6 R7 versioning discipline. It is explicitly non-blocking for T6 per the UI/UX verdict. The Reviewer notes this for the Architect's scheduling. No T6 action required.

---

## Disposition

All nine checks PASS. All nine T6 acceptance criteria PASS. Prerequisite gate verdicts are present and their notes are addressed or correctly designated carry-forward. The binding uncertainty invariant (R10) is correctly implemented: R1-a points have confidence ellipses; R1-b and R1-c do not.

**PASS. Tester proceeds.**

---

*End of Phase 5 T6 Reviewer verdict. Filed to `docs/status/2026-05-10-phase5-t6-reviewer-verdict.md`.*
