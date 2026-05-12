---
filed: 2026-05-12
reviewer: UI/UX agent (Sonnet)
plan_reviewed: docs/status/2026-05-12-phase6-T7-architect-plan.md
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.4 (no update required — §3.4 FreeListCompare spec is honored; no new visual decisions outside it)
verdict: PASS-WITH-NOTES
---

# UI/UX Plan-Level Verdict — Phase 6 T7 (FreeListCompare)

**VERDICT: PASS-WITH-NOTES**

Review posture: light-touch per `feedback_ui_polish_scope.md`. Five criteria only: accessibility floor, R10 pairing, token consistency, WCAG AA contrast, mobile/touch posture. No aesthetic critique, no OWID fidelity gating, no journalist/cite-path gating.

| Criterion | Result |
|---|---|
| 1. Accessibility floor | PASS-WITH-NOTES |
| 2. R10 pairing | PASS |
| 3. Token consistency | PASS |
| 4. WCAG AA contrast | PASS-WITH-NOTES |
| 5. Mobile/touch posture | PASS |

T7 is approved for Coder dispatch. Two binding implementation notes below must be applied during implementation. Neither requires plan revision or re-routing to any gate.

---

## 1. Accessibility floor — PASS-WITH-NOTES

**What the plan specifies correctly:**

- `<header>` element for each column header: plan §2.3 FreeListColumn item 1 specifies a semantic `<header>` element with color dot + model name.
- `<ol>` for ranked term list: plan §2.3 FreeListColumn item 2 specifies `<ol>` (ordered list). Rank IS the ordering.
- Container `aria-label`: acceptance criteria #11 specifies `aria-label="Side-by-side free lists"` on the FreeListCompare root.
- Each `<li>` aria-label: plan §2.4 and acceptance criteria #7 specify the CDA SME §5.2 binding wording. item + CSI + frequency triple all present.
- Hover/focus parity: plan §2.3 hover behavior specifies both `mouseenter`/`mouseleave` and `focusin`/`focusout` wired to `onTermHover`.
- Shared-term glyph accessibility: `aria-label` suffix `"; in every selected model"` carries the information; the glyph is decorative redundancy.

**Binding implementation note F-T7-A1 (BINDING):** `<h2>` bridge required in FreeListCompare before column `<h3>` headers.

The plan's acceptance criteria #11 requires heading order `<h1>` → `<h2>` → `<h3>` with no skips. The plan's column headers are `<h3>`. The DataExplorer section has no `<h2>` antecedent — verified against `apps/dashboard/src/components/DataExplorer.tsx`. The only `<h2>` in the main page flow is `MethodologySummary`'s "About this measurement" heading (§12.7), which appears AFTER the DataExplorer in DOM order.

The Coder MUST add a screen-reader-only `<h2>` at the top of `FreeListCompare.tsx`:

```tsx
<h2 className="sr-only">Free list comparison</h2>
```

placed as the first child inside the FreeListCompare root element, before the descriptive `<p>` caption and the column flex row. The `sr-only` CSS class must use the standard visually-hidden pattern. If `sr-only` is not already defined in the codebase, the Coder adds it to `freelist-compare.css`.

(Note: `ModelSelector.tsx` has a pre-existing `<h3>` with the same heading-order gap. Out of T7 scope; T14 heading-hierarchy sweep target.)

---

## 2. R10 pairing — PASS

The CDA SME PASS-WITH-NOTES verdict approved the `f_mentions / n_runs` empirical-frequency fallback. The plan's R10 implementation is correct on both visual and DOM axes:

**Visual axis:** each term pill renders the inclusion-frequency bar immediately adjacent (plan §2.3, §2.4). The column-level R10 caption is the CDA SME §5.1 binding text: "Bar shows the fraction of this model's collection runs that produced this term."

**DOM axis:** each `<li>` aria-label includes the frequency disclosure per CDA SME §5.2: `"${item}, Sutrop salience score ${csi.toFixed(2)}, included in ${f_mentions} of ${n_runs} collection runs"`.

R10 satisfied.

---

## 3. Token consistency — PASS

All CSS custom properties referenced in plan §2.3 verified against `apps/dashboard/src/styles/tokens.css`:

| Token | Exists | Value |
|---|---|---|
| `--color-surface` | Yes | #f8f9fa |
| `--color-text-primary` | Yes | #2c3e50 |
| `--color-text-caption` | Yes | #6c757d |
| `--color-background` | Yes | #ffffff |
| `--color-border` | Yes | #dde1e7 |
| `--font-mono` | Yes | 'JetBrains Mono', monospace |
| `--font-size-xs` | Yes | 12px |
| `--space-4` | Yes | 16px |

No phantom tokens (the T0 plan review caught `--color-bg-surface` and `--font-family-mono`; this plan correctly uses the actual names).

---

## 4. WCAG AA contrast — PASS-WITH-NOTES

**Term pill text — PASS:** `--color-text-primary` on `--color-surface` ≈ 10.8:1.

**Caption text — PASS:** `--color-text-caption` (#6c757d) on `--color-background` (#ffffff) ≈ 4.60:1.

**R10 caption — PASS:** Same token combination as caption text.

**Touch targets — PASS:** `min-height: 44px` specified on `<li>` elements at `<768px`.

**Advisory note F-T7-C1 (NON-BLOCKING):** Inclusion-frequency bar fill at 60% opacity may not meet 3:1 graphical contrast against `--color-border` (#dde1e7) for the two lightest model slots (`--color-model-3` #e67e22 and `--color-model-4` #27ae60). Because the same information is carried by the adjacent numeric label and `aria-label`, the bar is supplemental visual reinforcement — WCAG SC 1.4.11 risk is reduced. The Coder verifies contrast during implementation. If a slot fails 3:1, raise opacity to 80% for that slot or use a solid (100%) fill. Document result in commit body.

---

## 5. Mobile/touch posture — PASS

- Horizontal scroll on `<768px`: `overflow-x: auto` on the container.
- Touch hover via `focusin`/`focusout`: plan §2.3 specifies both event sets.
- Touch targets: `min-height: 44px` per WCAG 2.5.5.
- No animation, no decorative motion. Consistent with the minimum-viable functional surface posture.

**Non-blocking note on `★` glyph (plan §3 risk #3):** cross-platform rendering inconsistency (Windows emoji vs. macOS text-color glyph) acceptable for the functional surface. The information is also carried by the `aria-label` suffix; the glyph is decorative reinforcement. T14 polish-pass concern.

---

## Findings table

| ID | Severity | File | Issue | Required correction |
|---|---|---|---|---|
| F-T7-A1 | BINDING | `FreeListCompare.tsx` + `freelist-compare.css` | `<h3>` column headers have no antecedent `<h2>` in the DataExplorer section — heading-order skip violates acceptance criteria #11 | Add `<h2 className="sr-only">Free list comparison</h2>` as first child of FreeListCompare root; define `sr-only` in `freelist-compare.css` if not already present |
| F-T7-C1 | ADVISORY | `freelist-compare.css` | Bar fill at 60% opacity may not meet 3:1 non-text contrast for lightest model slots (model-3, model-4) | Verify contrast at 60% opacity during implementation; raise to 80% or use solid fill on failing slots; document in commit body |

---

## DESIGN_SYSTEM.md update

**Not required.** §3.4 specifies FreeListCompare in sufficient detail. No new visual decisions outside the existing spec. Version remains v0.4.4. T14 documentation sweep may add §12.10 to codify T7's implementation choices.

---

## Escalation items for Mark

None. Both findings are implementation-level corrections.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict with both findings applied.*
