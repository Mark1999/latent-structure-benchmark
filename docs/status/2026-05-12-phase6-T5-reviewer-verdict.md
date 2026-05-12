---
filed: 2026-05-12
reviewer: Reviewer agent (Sonnet)
commit_reviewed: bbe3f40
task: Phase 6 T5 — SimilarityHeatmap with WCAG-AA-compliant contrast switch
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md)
uiux_plan_level: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md)
---

# Reviewer Verdict — Phase 6 T5

## REVIEWER VERDICT: PASS

---

## Nine Binding Checks

```
Check 1 — No LLM imports in cdb_analyze:   PASS
Check 2 — Append-only JSONL:               PASS
Check 3 — No secrets:                       PASS
Check 4 — Forbidden vocabulary:             PASS
Check 5 — Schema + DATA_DICTIONARY:         N/A
Check 6 — New deps sign-off:                N/A (no new deps)
Check 7 — Prompt versioning:                N/A
Check 8 — Uncertainty in viz:               PASS
Check 9 — Prerequisite verdicts:            PASS

Failures: none
Required before merge: none
```

---

## 1. Rules table (R1–R13, SECURITY_AND_HARDENING.md §9)

| Rule | Check | Result | Notes |
|---|---|---|---|
| R1 | No edits to `data/raw/informants.jsonl` | PASS | Not in the commit's changed file list. Eleven files — all in `apps/dashboard/` or `DESIGN_SYSTEM.md`. |
| R2 | Tests use fixtures, no real API calls | PASS | `viz-switcher.test.tsx` and `permalink.test.ts` use only inline `vi.fn()` mocks and jsdom DOM rendering; no `fetch`, no network mocking, no real API calls. All 893 tests pass in `npm run test`. |
| R3 | No LLM client imports in `cdb_analyze/` | PASS | T5 is a pure frontend task. Static grep of `packages/cdb_analyze/` confirms the only matches are the prohibition comments in `__init__.py` — no actual imports. Unchanged by this commit. |
| R4 | No secrets / API keys | PASS | Scanned all eleven changed files for credential patterns (`api_key`, `secret`, `password`, `token`, `webhook`, `hooks.slack.com`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`): zero matches. |
| R5 | No point estimates without uncertainty in new viz | PASS | See §5 (R10 pairing) below. Every `<rect>` cell carries both a visual point estimate (`similarity.toFixed(2)` in `<text>`) and a DOM uncertainty disclosure (per-cell `aria-label` encoding 95% CI). Dashed cells additionally carry the CDA SME N2 null-crossing suffix. |
| R6 | Schema changes co-update `DATA_DICTIONARY.md` | N/A | `cdb_core/schemas.py` not in commit. `data/types.ts` intentionally deferred to T14 per plan §4 and commit body. |
| R7 | No new dependencies without Architect sign-off | N/A | `apps/dashboard/package.json` unchanged. No new library imports in any source file. `SimilarityHeatmap.tsx` imports only `react`, `../data/types`, `../lib/modelShortName`, `../config/analysis`, and `../styles/similarity-heatmap.css` — all existing. |
| R8 | Frontend PRs carry a UI/UX verdict | PASS | UI/UX PASS-WITH-NOTES at `docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md`. All two BINDING notes applied (F-T5-A1, F-T5-C1) and advisory F-T5-M1 confirmed in commit body. |
| R9 | Researcher grounding submission PRs | N/A | No `data/grounding/` files in commit. |
| R10 | Webhook URL secrets never committed | PASS | No Slack webhook URLs in any changed file (confirmed under R4). |
| R11 | `SECURITY.md` not weakened | PASS | `SECURITY.md` not in commit. |
| R12 | §1.5.4 language guardrails | PASS | See §3 below. Full scan: zero forbidden-phrase matches in user-facing text of all eleven changed files and commit body. |
| R13 | No software-side spend gates | PASS | No `CDB_MAX_SPEND_USD`, `spend_gate`, `cost_cap`, or cost-estimate paragraphs in any changed file or commit body. |

---

## 2. CLAUDE.md §6 specific checks

### Check 1 — No LLM imports in cdb_analyze
PASS. T5 touches no `packages/cdb_analyze/` files. Static grep confirms only the prohibition comments remain in `cdb_analyze/__init__.py` (`import anthropic`, `import openai`, etc. listed as explicitly forbidden — no actual imports present).

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` is not present in the commit's changed file list.

### Check 3 — No API keys or secrets
PASS. Full scan of all eleven changed files: no credential pattern found. No Slack webhook URLs, no API tokens, no passwords.

### Check 4 — No forbidden vocabulary
PASS. See §3 below.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` untouched. `data/types.ts` untouched per plan §4 T14 deferral. `docs/DATA_DICTIONARY.md` co-update not required.

### Check 6 — New dependencies
N/A. `apps/dashboard/package.json` and `package-lock.json` unchanged. No new `pyproject.toml` changes. `SimilarityHeatmap.tsx` imports only existing codebase modules and the new `similarity-heatmap.css` (part of this commit, not an external dependency).

### Check 7 — Prompt versioning
N/A. No prompt templates in `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
PASS. R10 pairing is complete on both visual and DOM axes. See §5 below.

### Check 9 — Prerequisite verdicts
PASS. Both required gate verdicts are present and all binding notes applied. See §6 below.

---

## 3. Forbidden vocabulary confirmation

Scanned all eleven changed files (new and modified) plus the commit message against the full CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 forbidden table:

| Forbidden phrase | Present in user-facing text? | Notes |
|---|---|---|
| `worldview` / `believes` / `thinks` (model-applied) | No | Appear only as quoted forbidden-vocab in docstrings ("Forbidden vocabulary compliance: no 'worldview', 'believes', 'thinks'...") — not as LSB assertions about models. |
| `How models see the world` / `How models see` | No | — |
| `What the model understands` | No | — |
| `Cultural bias` (standalone) | No | — |
| `within-model consensus` / `within-model cultural` / `within-model eigenratio` / `within-model CCM` | No | — |
| `publishable` (for LSB findings) | No | — |
| `missing` / `placeholder` / `no data yet` / `pending` (empty-state framing) | No | Empty state uses "Select one or more models to see the similarity heatmap." — clean. |
| `agrees` / `share a worldview` / `models agree` (cognitive consensus) | No | — |

Caption text (CDA SME §5.1 binding): "Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value." — "organize" is §1.5.4 approved at line 166; "structure" is data-relation language; no consensus framing. PASS.

Tooltip text: `"similarity: X.XX, 95% CI [X.XX, X.XX]"` — data values only, no methodology narration, no forbidden vocabulary. PASS.

Aria-label templates: `"${shortNameA} versus ${shortNameB}: similarity X.XX, 95 percent confidence interval X.XX to X.XX"` — data-relation only. Dashed-cell suffix: `"; confidence interval includes the no-shared-structure value of 0.50"` — no consensus framing. PASS.

PASS on vocabulary.

---

## 4. CDA SME binding notes verification (§5.1–§5.5)

| Note | Required correction | Applied? | Evidence |
|---|---|---|---|
| §5.1 (N1) | Caption verbatim: `"Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value."` | PASS | `SimilarityHeatmap.tsx` lines 492–496: `<p className="similarity-heatmap__caption">Each cell shows how similarly two models organize this domain (1.00 ={" "}identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value.</p>` — JSX `{" "}` emits a space, rendering identical to binding text. Exact character match confirmed. |
| §5.2 (N2) | Dashed-cell aria-label suffix: `"; confidence interval includes the no-shared-structure value of 0.50"` when `ci_lower < SIMILARITY_NULL_VALUE < ci_upper` | PASS | `SimilarityHeatmap.tsx` lines 129–144: `cellAriaLabel()` function appends `"; confidence interval includes the no-shared-structure value of 0.50"` when `ciCrossesNull(ci)` returns true. `ciCrossesNull()` at lines 108–111 implements `ci[0] < SIMILARITY_NULL_VALUE && SIMILARITY_NULL_VALUE < ci[1]` — exactly the binding condition. |
| §5.3 | Tooltip text — no change required | PASS | Tooltip lines 1–2 are data-only (`"${nameA} vs ${nameB}"` and `"similarity: X.XX, 95% CI [X.XX, X.XX]"`). No methodology narration. |
| §5.4 (N4) | T14 ARCHITECTURE.md §4.5 replacement text in commit body | PASS | Commit body contains the verbatim replacement sentence under "T14 follow-up text (N4)": `"Heatmap cells carry tooltips showing \`similarity ± 95% CI\`. Cells whose CI crosses the null value..."` — matches the CDA SME §5.4 binding suggestion exactly. |
| §5.5 (N5) | No on-page methodology narration — no tooltip, info-icon, or expandable section | PASS | No `info-icon`, no `accordion`, no `details`/`summary`, no expandable panel in `SimilarityHeatmap.tsx`. The single methodology surface is the §5.1 caption. The per-cell tooltip contains only data values. |

---

## 5. UI/UX binding and advisory note verification

| Finding | Severity | Applied? | Evidence |
|---|---|---|---|
| F-T5-A1 | BINDING | PASS | `SimilarityHeatmap.tsx` line 304 (empty state) and line 317 (normal state): `<h2 className="sr-only">Similarity heatmap</h2>` is the first child of the root `<div className="similarity-heatmap">` in both code paths — before the `<div className="similarity-heatmap__svg-container">` and before the `<svg>`. NOT inside `<svg>`. Matches FreeListCompare.tsx line 157 pattern. |
| F-T5-C1 | BINDING | PASS | `const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` at line 72 with WCAG AA citation comment. `cellTextFill()` at lines 98–102: `sim > 0.73` → `var(--color-background)` (white); `≤ 0.73` → `var(--color-heatmap-cell-text-dark)` (black). `--color-heatmap-cell-text-dark: #000000` added to `tokens.css` lines 118–121 with DESIGN_SYSTEM.md §12.8 citation. Plan's `0.55` fallback is NOT present as executable code — references to `0.55` appear only in WCAG AA comment blocks explaining why that value was rejected. |
| F-T5-M1 | ADVISORY | PASS (confirmed) | `similarity-heatmap.css` lines 67–74: `@media (max-width: 480px) { .similarity-heatmap__cell-label { display: none; } }` — suppression targets `.similarity-heatmap__cell-label` (`<text>` elements) only. The `<rect>` elements carry `aria-label` as a DOM attribute; `display: none` on a sibling `<text>` has no effect on `<rect>` attributes. Commit body confirms: "suppression does not touch the rect elements." |

---

## 6. Prerequisite verdict check

| Gate | Status | Binding notes addressed? |
|---|---|---|
| CDA SME | PASS-WITH-NOTES (`docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md`) | Yes — N1 caption (§5.1), N2 aria-label (§5.2), N4 T14 text (§5.4), N5 no narration (§5.5) all confirmed applied. §5.3 required no edits. All five notes resolved. |
| UI/UX | PASS-WITH-NOTES (`docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md`) | Yes — F-T5-A1 (BINDING) applied; F-T5-C1 (BINDING) applied with corrected threshold 0.73 and new token; F-T5-M1 (ADVISORY) confirmed in commit body. DESIGN_SYSTEM.md v0.4.5 update present (3 lines: version header, changelog entry, footer). |

DESIGN_SYSTEM.md scope verification: commit adds exactly 3 lines to DESIGN_SYSTEM.md (version bump `v0.4.4` → `v0.4.5`, changelog entry, footer version update). The §12.8 section content was added by the prior UI/UX agent verdict commit `bca02e7` — not duplicated or modified by this commit. Scope is correct.

---

## 7. R10 uncertainty rendering (Check 8 detail)

The SimilarityHeatmap R10 compliance is verified on three axes:

**Visual point estimate:** `<text className="similarity-heatmap__cell-label">` renders `{similarity.toFixed(2)}` in `var(--font-mono)` at `var(--font-size-xs)` on every cell including diagonal cells. Visible on every cell above the 480px mobile breakpoint.

**DOM uncertainty (aria-label):** Every `<rect>` cell carries `aria-label={ariaLabelValue}`. For off-diagonal cells with CI: `"${shortNameA} versus ${shortNameB}: similarity X.XX, 95 percent confidence interval X.XX to X.XX"`. For null-CI cells: `"${shortNameA} versus ${shortNameB}: similarity X.XX, confidence interval not available"` — absence acknowledged, not silent. For diagonal cells: `"${shortName} self-similarity: 1.00 by construction"` — appropriate for deterministic diagonal. For dashed cells (CI crosses null): base label plus `"; confidence interval includes the no-shared-structure value of 0.50"` (CDA SME N2).

**Dashed-border treatment (§4.5 binding):** `ciCrossesNull()` fires when `ci[0] < SIMILARITY_NULL_VALUE && SIMILARITY_NULL_VALUE < ci[1]`. Cells meeting this condition receive `strokeDasharray="3,2"`, `strokeWidth=1.5`, and the N2 aria-label augmentation. Null-CI cells receive the solid border (not dashed). Diagonal cells receive the solid border (not dashed). Implementation correctly distinguishes all three cell types.

**No methodology narration in tooltip:** Tooltip line 2 is `"similarity: X.XX, 95% CI [X.XX, X.XX]"` — data values only. No explanation of why 0.5 is the null. CDA SME §5.5 satisfied.

R10 PASS.

---

## 8. Design-system token audit (no hardcoded values)

Reviewed `similarity-heatmap.css` and inline styles in `SimilarityHeatmap.tsx`:

- All CSS properties in `similarity-heatmap.css` use `var(--...)` custom property references. No hex color literals, no `rgb()` / `rgba()` in CSS property declarations (the `rgba()` value in `cellBackground()` is an inline style computed from the documented `HEATMAP_BASE_RGB = "44, 62, 80"` constant which is explicitly annotated as sourced from `--color-text-primary`).
- `--color-heatmap-cell-text-dark: #000000` added to `tokens.css` with component-scope annotation and DESIGN_SYSTEM.md §12.8 citation.
- Structural layout constants (`CELL_SIZE`, `HEADER_SIZE`, `CELL_PADDING`, `SVG_PADDING`) are architectural geometry constants sanctioned by the plan §2.5 spec, not design-token violations.
- `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` is a WCAG AA threshold constant, not a color or spacing token.

PASS on token consistency.

---

## 9. Build / test / lint summary

| Check | Result |
|---|---|
| `npm run lint` | Clean — no ESLint errors or warnings |
| `npm run build` | Success — 82.79 KB JS (gzip) + 4.52 KB CSS (gzip) |
| `npm run test` | 893/893 pass (30 test files) |
| Bundle delta (JS only) | +1.60 KB gzipped (82.79 KB vs 81.19 KB post-T7 baseline) |
| Bundle ceiling (plan §1 directive 8) | 8 KB — PASS |

Bundle delta independently confirmed: `npm run build` output shows `dist/assets/index-CPbGuXGM.js 270.84 kB │ gzip: 82.79 kB` — matches Coder's reported +1.60 KB exactly.

---

## 10. Additional spot-checks

| Check | Result | Evidence |
|---|---|---|
| `cdb_core/schemas.py` not touched | PASS | Not in 11-file changed list. |
| `data/types.ts` not touched | PASS | Not in changed file list. Shape mismatches documented in commit body and `SimilarityHeatmap.tsx` file header for T14 follow-up. |
| `MDSPlot.tsx` not touched | PASS | Not in changed file list. |
| `FreeListCompare.tsx` not touched | PASS | Not in changed file list. |
| `ModelSelector.tsx` not touched | PASS | Not in changed file list. |
| `Legend.tsx` not touched | PASS | Not in changed file list. |
| `data/raw` / `data/results` paths in new files | PASS | Zero matches in grep of new/modified files. |
| No `0.55` as executable code | PASS | `0.55` appears only in WCAG AA commentary comments — not in any conditional, assignment, or comparison. |
| No literal `0.5` for null purpose in component | PASS | All null comparisons use `SIMILARITY_NULL_VALUE` imported from `config/analysis.ts`. The string `"0.50"` in the dashed-cell aria-label suffix is presentational text per CDA SME §5.2 binding spec, not a threshold literal. |
| DESIGN_SYSTEM.md modifications scope | PASS | Exactly 3 lines added: version header, changelog entry, footer. §12.8 section content was added by prior UI/UX verdict commit `bca02e7` — not duplicated here. |
| Commit message follows Conventional Commits | PASS | `feat(dashboard): T5 SimilarityHeatmap with WCAG-AA-compliant contrast switch` — correct type, correct scope, under 72 characters. |
| Commit body references plan + CDA SME + UI/UX verdicts | PASS | Body cites all three by file path; recites F-T5-A1, F-T5-C1 by ID with WCAG arithmetic; confirms F-T5-M1 advisory; documents T14 follow-up text. |
| Bundle delta in commit body | PASS | `+1.60 KB gzipped (82.79 KB vs 81.19 KB post-T7 baseline)`. Independently confirmed. |
| No new `package.json` dependencies | PASS | `package.json` not in changed file list. Build succeeds without new dependencies. |
| No methodology narration (CDA SME §5.5) | PASS | No info-icon, tooltip explaining null choice, accordion, or expandable section in `SimilarityHeatmap.tsx`. |

---

## 11. Notes / required follow-ups

None. No blocking issues found.

T14 follow-up items documented in the commit body are not Reviewer-blocking:
1. `data/types.ts` shape mismatches (similarity_matrix and similarity_ci) — T14 doc-sweep concern.
2. `ARCHITECTURE.md` §4.5 text refinement — T14 doc-sweep concern; target replacement text is in the commit body per CDA SME §5.4.
3. `DESIGN_SYSTEM.md` §3.2 "Plotly" inventory line reconciliation — T14 doc-sweep concern; target replacement text is in the commit body.

---

*End of Reviewer verdict for Phase 6 T5 commit `bbe3f40`. Coder may merge.*

— Reviewer agent (Sonnet), 2026-05-12
