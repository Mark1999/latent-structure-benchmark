---
filed: 2026-05-15
reviewer: UI/UX agent (Sonnet)
task: Phase 6 T11 — Mobile hamburger nav
plan_reviewed: docs/status/2026-05-15-phase6-T11-architect-plan.md
upstream_verdict: Mark confirmed T1-dependency Option (b) — NAV_LINKS parity with desktop
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.7 (UPDATE APPLIED — adds §8.0 retaining existing §8 bullets; adds §8.1 hamburger menu full spec; adds MobileNav.tsx + Header.tsx + mobile_nav.ts + mobile-nav.css to §11 inventory)
verdict: PASS-WITH-NOTES
---

# Phase 6 T11 — UI/UX plan verdict

**UI/UX VERDICT: PASS-WITH-NOTES**

| Criterion | Result |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite test | PASS (N/A — chrome, not data) |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (M1) |

DESIGN_SYSTEM.md update: APPLIED (v0.4.6 → v0.4.7; adds §8.0 + §8.1; adds MobileNav-related entries to §11 inventory).

---

## All visual decisions (§8.1 of DESIGN_SYSTEM.md — binding)

Every §2.4–§2.9 decision reserved for UI/UX in the Architect plan has been codified in DESIGN_SYSTEM.md §8.1. Summary for the Coder's reference:

| Plan item | Decision |
|---|---|
| §2.4 ARIA pattern | Dialog with focus trap (`role="dialog"`, `aria-modal="true"`, `aria-haspopup="dialog"` on trigger, `aria-expanded` on trigger, `aria-controls` pointing to panel id). |
| §2.5.1 Glyph shape | Three horizontal lines, inline SVG, 20×16 viewBox, 2px stroke, 6px center-to-center gap. |
| §2.5.2 Glyph-to-X transform | None. Close affordance is a dedicated button inside the panel. |
| §2.5.3 Drawer direction | Full-screen overlay, `position: fixed; top:0; left:0; right:0; bottom:0`. |
| §2.5.4 Transition | None (instant). `prefers-reduced-motion` block in CSS as forward safety. |
| §2.5.5 Backdrop scrim | None (panel is full-bleed). |
| §2.5.6 Trigger button styling | 48×48 px; `background: transparent`; `border: 2px solid transparent`; hover: `var(--color-surface-hover)`; focus-visible: `outline: 2px solid var(--color-info)`. |
| §2.5.7 Open-panel link styling | `font-size: var(--font-size-lg)` (18px); `font-weight: var(--font-weight-medium)`; `color: var(--color-text-primary)`; `min-height: 48px`; separated by `var(--color-border)` dividers. |
| §2.5.8 Touch target size | 48×48 px for trigger and close button; `min-height: 48px` for each link. |
| §2.5.9 Trigger position when open | Hidden (`display: none` via React state). |
| §2.5.10 Visible heading inside panel | Omitted. `aria-label` on dialog only. |
| §2.6 A11y strings | Confirmed verbatim. No additional strings. CDA SME bypass applies. |
| §2.7 Reduced-motion | CSS block present in `mobile-nav.css` as forward safety; no transition to suppress currently. |
| §2.8 Scroll lock | None. Matches existing CiteModal posture. |
| §2.9 DOM mount | Inline inside Header.tsx (`position: fixed` escapes stacking context without portal). Panel z-index: 200. |

---

## Binding note (Coder must apply before merge)

### M1 — NAV_LINKS export (single-source-of-truth enforcement)

The Architect plan acceptance criterion 15 requires `MobileNav.tsx` to import `NAV_LINKS` from its single source of truth in `Header.tsx` rather than duplicating the link list. Currently `NAV_LINKS` (and the `NavLink` interface) at `Header.tsx` line 46 is a module-private `const` — it is not exported.

**Required fix (Coder picks one):**

- **Option A (preferred):** Add `export` to `NAV_LINKS` and `NavLink` in `Header.tsx`, then import them into `MobileNav.tsx` directly.
- **Option B:** Pass `NAV_LINKS` as a prop from `Header` to `MobileNav`. The prop type is `NavLink[]`; the `NavLink` interface must then be exported from `Header.tsx` for the prop type annotation.

Either option satisfies the single-source requirement. Option A is simpler. The Reviewer must verify that no copy of the link list exists in `MobileNav.tsx` or `mobile_nav.ts`.

---

## Advisory notes (non-blocking; confirm in commit body)

- **A1:** The `role="dialog"` panel wraps an inner `<nav aria-label={MOBILE_NAV_PANEL_LABEL}>`. This dual-landmark structure (dialog + nav) is intentional per §8.1.16 and the Architect's §10 risk 6 note. The Coder should verify that VoiceOver and NVDA announce the dialog correctly before committing; jsdom tests are sufficient for focus-trap coverage but do not replace a brief AT spot-check.
- **A2:** The trigger's `style={{ display: isOpen ? 'none' : undefined }}` pattern hides the button from sighted users when the panel is open. Verify this does not produce a flash of the button becoming visible when the panel closes (focus-restore runs after the button reappears). A `useLayoutEffect` or `useEffect` with no timeout dependency should be sufficient.
- **A3:** The close button's glyph is `×` (U+00D7 MULTIPLICATION SIGN), rendered as a React text node inside a `<span aria-hidden="true">`. The button's accessible name comes from `aria-label={MOBILE_NAV_TRIGGER_LABEL_OPEN}`. Confirm the rendered glyph size at 48×48 px touch target does not clip at `font-size: var(--font-size-xl)` (24px).
- **A4:** Bundle delta target is ≤5 KB gzipped. Three new files (`MobileNav.tsx` ~2 KB, `mobile-nav.css` ~1–1.5 KB, `mobile_nav.ts` ~0.2 KB) plus `Header.tsx` edits (~0.3 KB) project to ~3.5–4 KB — within budget. Coder reports measured delta in commit body.
- **A5:** The dead-link posture (three of four nav entries 404 until T1 ships) is intentional per Option (b) acceptance and criterion 16 of the plan. The 30-second journalist test still passes: the user reaches the nav surface within 30 seconds and the Explore link (`/`) works. The dead-link state is a T1 concern, not T11.

---

## OWID design fidelity rationale

A full-screen, instant-open nav overlay in `--color-background` with `--color-text-primary` links at `--font-size-lg` reads as a clean scientific instrument, not a consumer product. No gradients, no decorative animation, no colored panel background. The three-line glyph is the universal nav-menu convention and does not introduce consumer-product idioms. The close-button "×" is a text character, not an icon library call. OWID-fidelity PASS.

---

## 30-second journalist test rationale

At `<768px`, the hamburger button is visible in the header immediately on page load (above the fold, top-right of the header bar). It is 48×48 px and labeled "Open navigation menu" for AT users. A journalist landing on mobile can tap it within seconds, see the four links, and navigate. The Explore link works immediately. PASS.

---

## WCAG AA coverage

| SC | Requirement | Satisfied by |
|---|---|---|
| 1.4.3 (Contrast Minimum) | 4.5:1 for link text in panel | `--color-text-primary` (#2c3e50) on `--color-background` (#ffffff) ≈ 12.6:1. PASS. |
| 1.4.11 (Non-text Contrast) | 3:1 for glyph, focus indicators | Glyph `currentColor` inherits `--color-text-primary` ≈ 12.6:1. Focus ring `--color-info` ≈ 7.3:1. PASS. |
| 2.1.1 (Keyboard) | All interactions keyboard-accessible | Trigger: Enter/Space; Esc closes; Tab cycles within panel. PASS. |
| 2.1.2 (No Keyboard Trap) | Esc always escapes | Esc closes panel. Close button always reachable via Tab. PASS. |
| 2.4.3 (Focus Order) | Focus order matches DOM order | Close button first (initial focus), then links in DOM order. PASS. |
| 2.4.7 (Focus Visible) | Visible focus ring on all focusable elements | `outline: 2px solid var(--color-info)` on all interactive elements. PASS. |
| 2.5.5 (Target Size — floor) | ≥44×44 px | 48×48 px for trigger and close; 48px min-height for links. PASS. |
| 4.1.2 (Name, Role, Value) | Accessible name + state on trigger and panel | Trigger has `aria-label`, `aria-expanded`, `aria-haspopup`, `aria-controls`. Panel has `role="dialog"`, `aria-modal`, `aria-label`. PASS. |

---

## Required before merge

1. Apply M1: export `NAV_LINKS` and `NavLink` from `Header.tsx` (Option A or B).
2. DESIGN_SYSTEM.md v0.4.7 changes already applied at the plan-review stage (this commit). The Coder's T11 implementation commit does not need to re-update DESIGN_SYSTEM.md; it must reference §8.1 in `MobileNav.tsx`'s file header comment per acceptance criterion 20.
3. Confirm no duplicate link array exists anywhere in `MobileNav.tsx` or `mobile_nav.ts` (Reviewer R12 spot-check).

---

## Escalation items for Mark

None. All decisions are resolvable within existing tokens and the minimum-viable-surface posture. CDA SME bypass confirmed (no non-standard visible strings introduced). The dead-link state (three of four entries 404 until T1) is documented as intentional and does not require escalation.

---

## Verdict rationale

T11 is a pure chrome task on the accessibility floor + readability axis. The plan is well-structured and addresses every required decision point. The four WCAG SCs with the highest risk on mobile (1.4.3 text contrast in the open panel, 2.4.7 focus visibility, 2.5.5 touch target size, 4.1.2 ARIA semantics) are all satisfied by the token-only styling codified in §8.1. The single binding note (M1) is a one-line code change (`export const NAV_LINKS`) that does not affect behavior. PASS-WITH-NOTES is appropriate: the plan clears all four scorecard criteria with one minor correction to apply before the Coder commits.

---

*Posted to #lsb-ui-ux. DESIGN_SYSTEM.md v0.4.7 update posted to #lsb-ui-ux simultaneously. Coder may proceed on receipt of this verdict with M1 applied; DESIGN_SYSTEM.md v0.4.7 update is in this same commit.*
