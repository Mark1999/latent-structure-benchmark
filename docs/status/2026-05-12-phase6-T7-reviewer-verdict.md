---
filed: 2026-05-12
reviewer: Reviewer agent (Sonnet)
commit_reviewed: 7393d60
task: Phase 6 T7 — FreeListCompare with R10 inclusion-frequency bars
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md)
uiux_plan_level: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md)
---

# Reviewer Verdict — Phase 6 T7

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
| R1 | No edits to `data/raw/informants.jsonl` | PASS | Not in the commit's changed file list. Ten files only — all in `apps/dashboard/`. |
| R2 | Tests use fixtures, no real API calls | PASS | `freelist-compare.test.tsx` uses only inline `makeFixture()` builder; imports `vitest`, `react`, and the component under test. No `fetch`, no `vi.mock` of any network layer, no `axios`. All 852 tests pass in `npm run test`. |
| R3 | No LLM client imports in `cdb_analyze/` | PASS | T7 is a pure frontend task. Static grep of `packages/cdb_analyze/` confirms the only matches are the prohibition comments in `__init__.py` — no actual imports. Unchanged by this commit. |
| R4 | No secrets / API keys | PASS | Scanned all ten changed files for `api_key`, `secret`, `password`, `token`, `webhook`, `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`, `hooks.slack.com`, `xoxb-`: zero matches. The only "token" string present is in the `freelist-compare.css` comment block referencing "Token-only. No hardcoded colors" — describing the design-token approach, not a credential. |
| R5 | No point estimates without uncertainty in new viz | PASS | Every term pill renders the R10 inclusion-frequency bar adjacent (visual) and carries the `aria-label` disclosing `f_mentions / n_runs` (DOM). The CDA SME §5.1 binding caption appears verbatim. The bar is suppressed for Case B and Case C columns per plan §2.5, which carry no term pills. R10 is satisfied. See §5 below. |
| R6 | Schema changes co-update `DATA_DICTIONARY.md` | N/A | `cdb_core/schemas.py` is not in the commit. Plan §7 confirmed schema-quiet status. No `DATA_DICTIONARY.md` update required. |
| R7 | No new dependencies without Architect sign-off | N/A | `apps/dashboard/package.json` and `package-lock.json` are not in the commit. `npm run build` succeeds; no new library import is present in the source files. `modelShortName` reuse and existing prop chain confirmed. |
| R8 | Frontend PRs carry a UI/UX verdict | PASS | UI/UX PASS-WITH-NOTES at `docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md`. Both binding notes applied: F-T7-A1 (`<h2 className="sr-only">Free list comparison</h2>`) verified in source; F-T7-C1 (80% opacity) verified in CSS. |
| R9 | Researcher grounding submission PRs | N/A | No `data/grounding/` files in commit. |
| R10 | Webhook URL secrets never committed | PASS | No Slack webhook URLs in any changed file (confirmed under R4). |
| R11 | `SECURITY.md` not weakened | PASS | `SECURITY.md` not in commit. |
| R12 | §1.5.4 language guardrails | PASS | See §3 below. Full scan: zero forbidden-phrase matches in user-facing text of all ten changed files and commit body. |
| R13 | No software-side spend gates | PASS | No `CDB_MAX_SPEND_USD`, `spend_gate`, `cost_cap`, or cost-estimate paragraphs in any changed file or commit body. |

---

## 2. CLAUDE.md §6 specific checks

### Check 1 — No LLM imports in cdb_analyze
PASS. T7 touches no `packages/cdb_analyze/` files. Static grep confirms only the prohibition comments remain in `cdb_analyze/__init__.py`.

### Check 2 — Append-only JSONL
PASS. `data/raw/informants.jsonl` is not present in the commit's changed file list.

### Check 3 — No API keys or secrets
PASS. Full scan of all ten changed files: no credential pattern found. No Slack webhook URLs, no API tokens.

### Check 4 — No forbidden vocabulary
PASS. See §3 below.

### Check 5 — Schema + DATA_DICTIONARY
N/A. `cdb_core/schemas.py` untouched. `data/types.ts` untouched (per plan §4 / AC #18 / T14 deferral). `docs/DATA_DICTIONARY.md` co-update not required.

### Check 6 — New dependencies
N/A. `package.json` and `package-lock.json` unchanged. No new `pyproject.toml` changes. No new JS dependencies introduced.

### Check 7 — Prompt versioning
N/A. No prompt templates in `packages/cdb_collect/prompts/` touched.

### Check 8 — Uncertainty in visualizations
PASS. R10 pairing is complete on both visual and DOM axes:
- Every `<li>` in the term list carries an `aria-label` containing the `Sutrop salience score` (CSI) point estimate **and** the `included in X of Y collection runs` uncertainty disclosure.
- The R10 inclusion-frequency bar (width = `inclusionFrequency × 100%`) renders immediately adjacent to each term pill.
- The column-level R10 caption (CDA SME §5.1 binding wording, verbatim) appears once per column for columns with terms; it is correctly suppressed for Case B/C columns.
- `opacity: 0.8` on `freelist-column__freq-fill` (F-T7-C1 adjustment, documented in commit body and CSS header comment).

### Check 9 — Prerequisite verdicts
PASS. Both required gate verdicts are present and all binding notes are applied:
- CDA SME PASS-WITH-NOTES: `docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md`. Five binding notes (§5.1–§5.5). All five applied — §5.1 caption wording verbatim, §5.2 aria-label wording verbatim, §5.4 T14 follow-up text in commit body verbatim, §5.5 no methodology narration (no tooltip/info-icon found in components). §5.3 required no edits.
- UI/UX PASS-WITH-NOTES: `docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md`. Two findings: F-T7-A1 (BINDING) applied; F-T7-C1 (ADVISORY) applied with documentation. Both cited by ID in commit body.

---

## 3. Forbidden vocabulary confirmation

Scanned all ten changed files (new and modified) plus the commit message against the full CLAUDE.md §7 + ARCHITECTURE.md §1.5.4 forbidden table:

| Forbidden phrase | Present in user-facing text? | Notes |
|---|---|---|
| `worldview` / `believes` / `thinks` (model-applied) | No | Appear only as quoted forbidden-vocab in docstrings ("Forbidden vocabulary: no 'worldview', 'believes', 'thinks'") — not as LSB assertions about models. |
| `How models see the world` / `How models see` | No | — |
| `What the model understands` | No | — |
| `Cultural bias` (standalone) | No | — |
| `within-model consensus` / `within-model cultural` / `within-model eigenratio` / `within-model CCM` | No | — |
| `publishable` (for LSB findings) | No | — |
| `missing` / `placeholder` / `no data yet` / `pending` (empty-state framing) | No | The three empty-state captions (`"Select one or more models to see their free lists."`, `"(no salience data for this model)"`, `"(no terms produced)"`) are clean. |

User-facing generated text in the commit: column description `"Each column lists the terms one model produced for this domain, ordered by Sutrop salience (Sutrop CSI)."` — vocabulary clean. R10 caption: `"Bar shows the fraction of this model's collection runs that produced this term."` — vocabulary clean (uses "model's collection runs" possessively about runs, not about cognition; "produced" not "believed/thought").

PASS on vocabulary.

---

## 4. CDA SME binding notes verification (§5.1–§5.5)

| Note | Required correction | Applied? | Evidence |
|---|---|---|---|
| §5.1 | R10 caption verbatim: `"Bar shows the fraction of this model's collection runs that produced this term."` | PASS | `FreeListColumn.tsx` line 105 (in commit diff): `<p className="freelist-column__r10-caption">Bar shows the fraction of this model&apos;s collection runs that produced this term.</p>` — HTML entity `&apos;` correctly escapes the apostrophe; rendered text is verbatim. |
| §5.2 | `aria-label`: `"${item}, Sutrop salience score ${csi.toFixed(2)}, included in ${f_mentions} of ${n_runs} collection runs"` | PASS | `FreeListColumn.tsx`: `const baseLabel = \`${record.item}, Sutrop salience score ${record.csi.toFixed(2)}, included in ${record.f_mentions} of ${record.n_runs} collection runs\`;` — exact template matches. |
| §5.3 | Empty-state captions — no changes required | PASS | Case A/B/C captions confirmed unchanged from plan §2.5 wording. |
| §5.4 | T14 ARCHITECTURE.md §4.5 replacement text in commit body | PASS | Commit body contains the verbatim replacement text paragraph with correct `docs/status/` reference path. |
| §5.5 | No methodology narration tooltip/info-icon/expandable | PASS | No `tooltip`, `popover`, `accordion`, `details`/`summary`, or info-icon pattern in `FreeListCompare.tsx` or `FreeListColumn.tsx`. The single methodology surface is the §5.1 R10 caption. |

---

## 5. UI/UX binding and advisory note verification

| Finding | Severity | Applied? | Evidence |
|---|---|---|---|
| F-T7-A1 | BINDING | PASS | `FreeListCompare.tsx`: `<h2 className="sr-only">Free list comparison</h2>` is the first child element inside the `.freelist-compare` root `<div>` (before the description `<p>` and the columns row). `freelist-compare.css` defines `.sr-only` as the standard visually-hidden pattern (position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap). |
| F-T7-C1 | ADVISORY | PASS | `freelist-compare.css`: `.freelist-column__freq-fill { opacity: 0.8; }`. Commit body documents the 60% failure calculation and 80% pass calculation for both model-3 (#e67e22) and model-4 (#27ae60). CSS file header comment contains the full contrast arithmetic. |

---

## 6. Deviation review: DownloadBar.tsx and permalink.ts

Both deviations are type-only widening changes, not behavioral changes:

**`DownloadBar.tsx`:** A single prop type change: `activeVizTab: "mds"` → `activeVizTab: "mds" | "freelist"`. No logic change, no new behavior, no new state. This is a necessary consequence of the `ActiveVizTab` type widening in `VizSwitcher.tsx` — the Coder correctly widened the downstream consumer to match rather than leaving a type error. No scope-creep concern.

**`permalink.ts`:** Three changes: (1) `vizTab: "mds"` → `vizTab: "mds" | "freelist"` on `PermalinkState`; (2) validation guard widens from `!== "mds"` to also permit `"freelist"`; (3) decode result adds `vizTab: "freelist"` when fragment is `"freelist"`. This is the minimal behavioral extension required to make `#freelist` a valid permalink fragment per plan §2.1. No unrelated behavior changes. The plan §2.1 explicitly states: `decodePermalink accepts "freelist" as valid fragment`. These changes are within declared scope.

Verdict on deviations: **not scope creep.** Both are necessary downstream consequences of the `VizSwitcher.tsx` type widening. The commit body lists them accurately as modifications.

---

## 7. Design-system token audit (no hardcoded values)

Reviewed `freelist-compare.css` for hardcoded values:
- All CSS properties use `var(--...)` custom property references.
- No hex color literals, no `rgb()`, no `rgba()`, no literal font-family strings in CSS property values (comments referencing hex values for the contrast calculation are in `/* ... */` blocks, not property declarations).
- Structural sizes `min-width: 200px`, `max-width: 280px`, `width: 40px`, `height: 4px`, `width: 8px`, `height: 8px`, `border-radius: 2px`, `border-radius: 50%`, `@media (max-width: 767px)` — these are layout primitives, not color/font/spacing tokens. They match the plan §2.3 spec exactly and were sanctioned by the architect plan.
- `FreeListColumn.tsx` uses `style={{ backgroundColor: modelColor }}` and `style={{ width: barWidth, backgroundColor: modelColor }}` — both reference the `modelColor` prop from the `DataExplorer` §12.4 palette chain, not hardcoded hex values. This is the correct pattern per the design system.

PASS on token consistency.

---

## 8. Build / test / lint summary

| Check | Result |
|---|---|
| `npm run lint` | Clean — no ESLint errors or warnings |
| `npm run build` | Success — 81.19 KB JS (gzip) + 4.32 KB CSS (gzip) |
| `npm run test` | 852/852 pass (29 test files) |
| Bundle delta (JS only) | +1.13 KB gzipped (81.19 KB vs 80.06 KB baseline per Coder) |
| Bundle delta (combined JS+CSS vs T0 baseline) | ~+1.59 KB — well within the 8 KB ceiling |
| Bundle ceiling (plan §1 directive 8) | 8 KB — PASS |

---

## 9. Additional spot-checks

| Check | Result | Evidence |
|---|---|---|
| `cdb_core/schemas.py` not touched | PASS | Not in changed file list (10 files, all in `apps/dashboard/`) |
| `data/types.ts` not touched | PASS | Not in changed file list. Shape mismatches documented in commit body and `FreeListCompare.tsx` file header for T14 follow-up. |
| `MDSPlot.tsx` not touched | PASS | Not in changed file list. |
| `ModelSelector.tsx` not touched | PASS | Not in changed file list. |
| `Legend.tsx` not touched | PASS | Not in changed file list. |
| `SimilarityHeatmap`, `DriftTracker` not touched | PASS | Not in changed file list. |
| No `data/raw` or `data/results` paths in new files | PASS | Zero matches in grep of new/modified files. |
| Commit message follows Conventional Commits | PASS | `feat(dashboard): T7 FreeListCompare with R10 inclusion-frequency bars` — correct type, correct scope, 69 characters (under 72). |
| Commit body references plan + CDA SME + UI/UX verdicts | PASS | Body cites all three by file path; recites F-T7-A1 and F-T7-C1 by ID with full documentation. |
| Bundle delta reported in commit body | PASS | Body reports `+1.13 KB gzipped (81.19 KB vs 80.06 KB baseline)`. |
| CDA SME §5.4 T14 text in commit body | PASS | Body contains the verbatim replacement text paragraph for ARCHITECTURE.md §4.5 line 1111. |
| No new `package.json` dependencies | PASS | `package.json` and `package-lock.json` not in commit. |

---

## 10. Notes / required follow-ups

None. No blocking issues found. No PASS-WITH-NOTES conditions attached.

T14 follow-up items documented in the commit body are not Reviewer-blocking:
1. `data/types.ts` shape mismatches — T14 doc-sweep concern.
2. `ARCHITECTURE.md` §4.5 line 1111 text — T14 doc-sweep concern; target replacement text is in the commit body per CDA SME §5.4.

---

*End of Reviewer verdict for Phase 6 T7 commit `7393d60`. Coder may merge.*

— Reviewer agent (Sonnet), 2026-05-12
