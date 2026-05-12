---
filed: 2026-05-12
reviewer: UI/UX agent (Sonnet)
task: Phase 6 T8 — Read-as-table toggle + ScreenReaderSummary
plan_reviewed: docs/status/2026-05-12-phase6-T8-architect-plan.md
upstream_verdict: CDA SME PASS-WITH-NOTES (S1–S11 binding)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.6 (UPDATE REQUIRED — adds §12.9, closes §12.6 deferral)
verdict: PASS-WITH-NOTES
---

# Phase 6 T8 — UI/UX light-touch plan verdict

**UI/UX VERDICT: PASS-WITH-NOTES**

| Criterion | Result |
|---|---|
| 1. Accessibility floor | PASS-WITH-NOTES (U1) |
| 2. R10 pairing | PASS |
| 3. Token consistency | PASS |
| 4. WCAG AA contrast | PASS-WITH-NOTES (U2) |
| 5. Mobile/touch posture | PASS |

DESIGN_SYSTEM.md update: REQUIRED (v0.4.5 → v0.4.6; adds §12.9 codifying U1+U2; closes §12.6 deferral; annotates §7).

---

## Binding notes (Coder must apply before merge)

### U1 — `aria-controls` DOM-presence requirement (Accessibility floor)

The plan's `<button aria-controls={tableId}>` is rendered unconditionally, but `<div id={tableId}>` is only inserted into the DOM when `readAsTable === true`. WAI-ARIA 1.2 §6.6.5 requires `aria-controls` to reference a currently-existing element.

**Required fix (Coder picks one):**
- **Option A:** Always render `<div id={tableId}>` in the DOM. When `readAsTable === false`: `aria-hidden="true"` + `display: none` on the container; inner table component conditionally rendered.
- **Option B:** Replace `aria-controls` with `aria-expanded={pressed}` and omit `aria-controls` entirely.

Update plan AC #5 and the Tester vitest snapshot to assert the chosen ARIA in both states.

### U2 — Pressed-state non-text visual indicator (WCAG 1.4.11)

A text-label change alone does not satisfy 3:1 non-text contrast. Required CSS additions:

```css
.read-as-table-toggle__button[aria-pressed="true"] {
  border: 2px solid var(--color-info);
  padding: calc(var(--space-2) - 2px) calc(var(--space-3) - 2px);
}
.read-as-table-toggle__button[aria-pressed="false"] {
  border: 2px solid transparent;
}
```

`--color-info` (#3360a9) on white ≈ 7.3:1 (WCAG 1.4.11 PASS). Transparent rest-border prevents layout shift.

---

## Advisory notes (non-blocking; confirm in commit body)

- **A1:** `.sr-only` class must already exist in global stylesheet (T5/T7 established). Confirm before commit.
- **A2:** FreeListTable's `<h4>` per-model headings require `<h3>` parent in FreeListCompare viz. Verify rendered DOM heading chain.
- **A3:** Plan's 28 acceptance criteria cover all assertions — no gaps.

---

## R10 verification

| Table | Point estimate | Adjacent uncertainty | R10 |
|---|---|---|---|
| MdsTable | x, y | semi_major, semi_minor, rotation_rad, n_bootstrap | PASS |
| FreeListTable | Salience (CSI) | Inclusion frequency (f_mentions/n_runs) | PASS |
| SimilarityTable | Similarity | 95% CI low / 95% CI high | PASS |

---

## Token audit — PASS

All plan CSS references (`--color-text-caption`, `--color-text-primary`, `--color-info`, `--color-background`, `--color-surface`, `--color-border`, `--space-2`, `--space-3`, `--font-mono`, `--font-size-sm`) exist in `tokens.css`. No phantom tokens. No new tokens introduced.

---

## DESIGN_SYSTEM.md update (v0.4.5 → v0.4.6)

Four edits required, applied by Coder in T8 commit:

1. **Version header:** v0.4.5 → v0.4.6
2. **Changelog entry** (prepend before v0.4.5):
   > **v0.4.6** (T8 plan-level UI/UX verdict, 2026-05-12) closes §12.6 Phase-5 "Read as table" deferral. T8 implements the §7 binding for MDS, FreeList, and Similarity. Adds §12.9 (ReadAsTableToggle + ScreenReaderSummary visual specification): `aria-controls` DOM-presence requirement (U1), pressed-state non-text contrast (U2 — `border: 2px solid var(--color-info)`, ~7.3:1 on white, WCAG 1.4.11 PASS), and `.sr-only` reuse. No new tokens.
3. **§7 "Read as table" bullet:** append "(implemented in Phase 6 T8; `ReadAsTableToggle.tsx`; binding visual spec in §12.9)"
4. **§12.6 body:** replace deferral text with closure note pointing to §12.9 (Phase 5 SVG aria-label posture remains intact for MDSPlot)
5. **New §12.9:** codifies U1 + U2 binding (full text in plan + verdict for reference)
6. **Footer:** v0.4.5 → v0.4.6

---

## Required before merge

1. Apply U1: aria-controls DOM-presence (Option A or B).
2. Apply U2: pressed-state border CSS rules.
3. Apply CDA SME S1–S11 (Coder's responsibility per upstream verdict).
4. Apply DESIGN_SYSTEM.md v0.4.6 changes in same T8 commit.

---

## Escalation items for Mark

None. Both BINDING findings resolvable within existing tokens. CDA SME and UI/UX bindings are well-scoped for Coder dispatch.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict with all BINDING findings applied + DESIGN_SYSTEM.md v0.4.6 update in same commit.*
