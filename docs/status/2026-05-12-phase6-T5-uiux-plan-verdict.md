---
filed: 2026-05-12
reviewer: UI/UX agent (Sonnet)
plan_reviewed: docs/status/2026-05-12-phase6-T5-architect-plan.md
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.5 (UPDATE REQUIRED — adds §12.8 SimilarityHeatmap cell-text contrast specification + new token `--color-heatmap-cell-text-dark`)
verdict: PASS-WITH-NOTES
---

# UI/UX Plan-Level Verdict — Phase 6 T5 (SimilarityHeatmap)

**VERDICT: PASS-WITH-NOTES**

Review posture: light-touch per `feedback_ui_polish_scope.md`. Five criteria only: accessibility floor, R10 pairing, token consistency, WCAG AA contrast, mobile/touch posture.

| Criterion | Result |
|---|---|
| 1. Accessibility floor | PASS-WITH-NOTES |
| 2. Cell text contrast switch | PASS-WITH-NOTES (BINDING correction required) |
| 3. R10 pairing | PASS |
| 4. Token consistency | PASS |
| 5. Mobile/touch posture | PASS-WITH-NOTES (advisory) |

T5 is approved for Coder dispatch with three implementation notes (two BINDING, one advisory). DESIGN_SYSTEM.md update is required and applied in the same commit.

---

## 1. Accessibility floor — PASS-WITH-NOTES

Plan correctly specifies SVG `role="img"` + aria-label, sr-only `<h2>` bridge, heading order H1 → H2 with no skips, per-cell `aria-label` per §2.4, CDA SME N2 dashed-cell augmentation, null-CI and diagonal phrasing.

**Binding implementation note F-T5-A1:** The sr-only `<h2 className="sr-only">Similarity heatmap</h2>` must be the first child of the component root `<div>` wrapper, NOT a child of the `<svg>` element. HTML `<h2>` inside `<svg>` is non-conformant DOM. Match FreeListCompare.tsx line 157 pattern exactly. The `sr-only` CSS class already exists in the codebase; no new CSS required.

---

## 2. Cell text contrast switch — PASS-WITH-NOTES (BINDING correction)

**The single biggest WCAG AA risk in this plan. The §2.2 switch at 0.5 and fallback at 0.55 BOTH fail.**

### Contrast analysis

Cell background `rgba(44, 62, 80, similarity)` composited on white. Computed contrast at boundary values:

| similarity | L_bg | White text contrast | `--color-text-primary` contrast |
|---|---|---|---|
| 0.45 | 0.410 | 2.28:1 FAIL | 4.18:1 FAIL |
| 0.50 | 0.356 | 2.59:1 FAIL | 3.69:1 FAIL |
| 0.55 | 0.322 | 2.82:1 FAIL | 3.38:1 FAIL |
| 0.73 | 0.183 | **4.50:1 PASS** | 2.12:1 FAIL |

Mid-range zone ~0.40–0.73: neither text color passes 4.5:1. Both shipped domains have cells in this band: holidays.json model 6 (0.45–0.51), family.json model 9 (0.50–0.52).

Pure black (#000, L=0) on similarity=0.73 background: (0.233/0.050) = **4.66:1 PASS**. Black covers the entire dark-text arm.

### Required correction — F-T5-C1 (BINDING)

**Change 1:** Switch threshold raised from 0.5 (plan) / 0.55 (fallback) to **0.73**. Define `const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` with WCAG AA citation comment.

**Change 2:** Add new token `--color-heatmap-cell-text-dark: #000000` to `tokens.css`. Replace `--color-text-primary` in the dark-text arm.

Updated switch rule:
```ts
textFill = similarity > HEATMAP_TEXT_SWITCH_THRESHOLD
  ? "var(--color-background)"                  // white, ≥4.5:1 at >0.73
  : "var(--color-heatmap-cell-text-dark)"      // black, ≥4.66:1 at ≤0.73
```

The plan's "raise to 0.55 fallback" mechanism is **superseded**. Coder MUST NOT implement it.

The "no new color tokens" directive (plan §1) is overridden by the WCAG AA floor for this single component-scoped token. New component-scoped token is the correct resolution.

---

## 3. R10 pairing — PASS

- Visual: `similarity.toFixed(2)` in mono font on every cell.
- DOM: per-cell `aria-label` encodes similarity + CI. CDA SME N2 augments dashed cells with "; confidence interval includes the no-shared-structure value of 0.50".
- Null-CI: "confidence interval not available" (§2.7) is absence acknowledgment, not defect framing.
- Dashed border = §4.5 reduced-saturation rule.

---

## 4. Token consistency — PASS

All referenced tokens verified against `tokens.css`. `HEATMAP_BASE_RGB = "44, 62, 80"` is an acceptable documented token-extraction shortcut. New token `--color-heatmap-cell-text-dark` added per F-T5-C1.

---

## 5. Mobile/touch posture — PASS-WITH-NOTES

- `viewBox` + `preserveAspectRatio="xMidYMid meet"`: correct.
- `tabIndex={0}` + `focusin` for touch tooltip: correct.
- 11-model label suppression on narrow viewports: approved.

**Advisory note F-T5-M1 (NON-BLOCKING):** When CSS label suppression activates on narrow viewports, the `aria-label` attribute on `<rect>` cells must remain in the DOM unaffected. Suppression targets rendered `<text>` elements only. Coder confirms in commit body.

---

## Findings table

| ID | Severity | File | Issue | Required correction |
|---|---|---|---|---|
| F-T5-A1 | BINDING | `SimilarityHeatmap.tsx` | sr-only `<h2>` must be inside root `<div>`, not inside `<svg>` | Match FreeListCompare.tsx line 157 placement |
| F-T5-C1 | BINDING | `SimilarityHeatmap.tsx` + `tokens.css` | Plan's 0.5/0.55 switch fails WCAG AA across observed data range | Threshold raised to 0.73; new `--color-heatmap-cell-text-dark: #000000` token; plan fallback not implemented |
| F-T5-M1 | ADVISORY | `SimilarityHeatmap.tsx` + `similarity-heatmap.css` | Label suppression must not suppress aria-labels | Confirm aria-labels in DOM independent of label rendering; document in commit body |

---

## DESIGN_SYSTEM.md update — REQUIRED (v0.4.4 → v0.4.5)

The UI/UX agent owns DESIGN_SYSTEM.md. Three edits applied in the same T5 commit:

1. **Version header:** `**Version:** v0.4.4` → `**Version:** v0.4.5`
2. **Changelog entry** prepended before v0.4.4 bullet:
   - **v0.4.5** (T5 plan-level UI/UX verdict, 2026-05-12) adds §12.8 (SimilarityHeatmap cell-text contrast specification) and introduces one component-scoped token `--color-heatmap-cell-text-dark: #000000`. The T5 plan's §2.2 binary text-color switch at similarity = 0.5 (fallback 0.55) fails WCAG AA 4.5:1 across the observed data range in both shipped domains. §12.8 specifies the corrected switch threshold of 0.73 and the `HEATMAP_TEXT_SWITCH_THRESHOLD` constant. The plan's "raise to 0.55" fallback is superseded.
3. **New §12.8 section** inserted before footer (full text in DESIGN_SYSTEM.md after edit; see also F-T5-C1 above).
4. **Footer:** `v0.4.4` → `v0.4.5`.

DESIGN_SYSTEM.md §3.2 inventory line "Plotly" → T14 reconciliation per plan §2.1.

---

## Required before merge

1. F-T5-A1 applied — sr-only `<h2>` as first child of component root `<div>`, not inside `<svg>`.
2. F-T5-C1 applied — switch threshold = 0.73; `--color-heatmap-cell-text-dark: #000000` added to `tokens.css`; plan's 0.55 fallback NOT implemented.
3. DESIGN_SYSTEM.md v0.4.5 changes applied in same T5 commit.

Non-blocking (confirm in commit body):
- F-T5-M1: aria-labels unaffected by label suppression on narrow viewports.

---

## Escalation items for Mark

None. All findings are implementation-level corrections. The WCAG AA correction is well-scoped; the new token is component-local. DESIGN_SYSTEM.md update is within UI/UX agent authority.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict with all BINDING findings applied + DESIGN_SYSTEM.md v0.4.5 update in the same commit.*
