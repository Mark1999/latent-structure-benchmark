---
filed: 2026-05-12
reviewer: UI/UX agent (Sonnet)
plan_reviewed: docs/status/2026-05-12-phase6-T10-architect-plan.md
cda_sme_upstream: PASS-WITH-NOTES (docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.5 (no update required)
verdict: PASS-WITH-NOTES
---

# UI/UX Plan-Level Verdict — Phase 6 T10 (Failures-as-findings UI surface)

**VERDICT: PASS-WITH-NOTES**

Review posture: light-touch per `feedback_ui_polish_scope.md`. Five criteria: accessibility floor, R10 pairing, token consistency, WCAG AA contrast, mobile/touch.

| Criterion | Result |
|---|---|
| 1. Accessibility floor | PASS-WITH-NOTES (advisory) |
| 2. R10 pairing | N/A (failures carry no point estimates) |
| 3. Token consistency | PASS-WITH-NOTES (BINDING — phantom token names) |
| 4. WCAG AA contrast | PASS-WITH-NOTES (BINDING — 12px regular text contrast) |
| 5. Mobile/touch posture | PASS |

T10 is approved for Coder dispatch with two BINDING corrections + one advisory.

---

## Findings

### F-T10-T1 (BINDING) — Phantom CSS custom property names

The plan §2.4 (lines 124, 126, 149) and the CDA SME S1 specification reference two custom properties that do not exist in `apps/dashboard/src/styles/tokens.css`:

| Phantom name | Actual token | Source |
|---|---|---|
| `--font-family-mono` | `--font-mono` | tokens.css line 55, DESIGN_SYSTEM.md §1.1 |
| `--font-family-base` | `--font-body` | tokens.css line 54, DESIGN_SYSTEM.md §1.1 |

If the Coder writes `var(--font-family-mono)` or `var(--font-family-base)`, both resolve to empty string and fall back silently to browser default — the mono/prose font distinction disappears with no build error. Silent styling failure.

**Required correction:** throughout `failures-findings.css` and component TSX inline styles:
- `font-family: var(--font-mono)` for `model_id`, `originating_outcome_class` enum, Provenance IDs
- `font-family: var(--font-body)` for S1 field-shape descriptor prose (`error_message: {N} chars`)

### F-T10-C1 (BINDING) — `--color-text-secondary` at 12px regular fails WCAG AA

CDA SME S1 specifies `--color-text-secondary` at `--font-size-xs` for the field-shape descriptor.

Contrast: `--color-text-secondary` (#7f8c8d, L≈0.236) on `--color-background` (#ffffff): ~3.67:1. WCAG AA at 12px regular requires 4.5:1.

DESIGN_SYSTEM.md §1.2 explicitly directs: "secondary labels at 14px+ or bold — ~3.40:1 on white; use `--color-text-caption` for 12px regular-weight text."

**Required correction:** use `--color-text-caption` (#6c757d, ~4.60:1) instead of `--color-text-secondary` for:
- S1 field-shape descriptor (`error_message: {N} chars`)
- Defensive error captions (`ERROR_FRAMING_MISSING`, `ERROR_FETCH_FAILED`) if rendered at 16px or below
- Provenance IDs sub-block if rendered at `--font-size-xs`

### F-T10-A1 (ADVISORY) — `<summary>:focus-visible` rule unspecified

Browser default `<summary>` focus indicators vary across Chromium/Firefox/Safari. WCAG 2.4.11 Focus Appearance risk if native defaults fail 3:1 non-text contrast.

**Advisory:** add `summary:focus-visible { outline: 2px solid var(--color-info); outline-offset: 2px; }` to `failures-findings.css`. Confirm in commit body.

---

## Findings table

| ID | Severity | File | Issue | Required correction |
|---|---|---|---|---|
| F-T10-T1 | BINDING | `failures-findings.css` + TSX inline styles | Phantom tokens `--font-family-mono` and `--font-family-base` | Use `--font-mono` and `--font-body` |
| F-T10-C1 | BINDING | `failures-findings.css` | `--color-text-secondary` at 12px regular fails WCAG AA 4.5:1 (3.67:1) | Use `--color-text-caption` |
| F-T10-A1 | ADVISORY | `failures-findings.css` | `<summary>:focus-visible` rule unspecified | Add explicit focus-ring rule |

---

## DESIGN_SYSTEM.md update

**Not required.** Existing tokens cover T10. No new visual decisions outside §3.x and §12.x. Version remains v0.4.5.

---

## Required before Coder implementation

1. F-T10-T1: replace `--font-family-mono` → `--font-mono` and `--font-family-base` → `--font-body` everywhere.
2. F-T10-C1: replace `--color-text-secondary` → `--color-text-caption` everywhere it would apply to 12px or smaller body/caption text.

Non-blocking (confirm in commit body):
- F-T10-A1: explicit `<summary>:focus-visible` rule.

---

## Escalation items for Mark

None. Both BINDING findings are CSS-level corrections.

---

*Posted to #lsb-ui-ux. Coder may proceed on receipt of this verdict with all BINDING findings applied.*
