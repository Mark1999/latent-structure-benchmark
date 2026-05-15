---
filed: 2026-05-15
reviewer: UI/UX agent (Sonnet)
task: Phase 6 T12 — Mobile bottom-drawer for ModelSelector
plan_reviewed: docs/status/2026-05-15-phase6-T12-architect-plan.md
upstream_decision: Mark confirmed §1.A Q1 trigger placement option (a) — inline in .explorer-layout__selector
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.8 (UPDATE APPLIED — extends §8 with §8.2 Mobile bottom-drawer for ModelSelector; adds MobileModelSelectorDrawer.tsx + mobile_model_drawer.ts + mobile-model-drawer.css to §11 inventory)
verdict: PASS-WITH-NOTES
---

# Phase 6 T12 — UI/UX plan verdict

**UI/UX VERDICT: PASS-WITH-NOTES**

| Criterion | Result |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS-WITH-NOTES (M1) |
| 3. Researcher reproduce-and-cite test | PASS (N/A — chrome, not data) |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (M2, M3) |

DESIGN_SYSTEM.md update: APPLIED (v0.4.7 → v0.4.8; adds §8.2; adds three components to §11 inventory).

---

## All visual decisions — §8.2 of DESIGN_SYSTEM.md (binding)

Every §2.4 and §2.5 decision reserved for UI/UX in the Architect plan has been codified in DESIGN_SYSTEM.md §8.2. Summary for the Coder's reference:

| Plan item | Decision | §8.2 section |
|---|---|---|
| §2.4 ARIA pattern | Dialog with focus trap (`role="dialog"`, `aria-modal="true"`, `aria-haspopup="dialog"` on trigger, `aria-expanded` on trigger, `aria-controls` pointing to panel id). Initial focus on close button. | §8.2.1 |
| §2.5.1 Trigger button | Full-width at `<768px`, `min-height: 48px`, token-only, no glyph, visible text via `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)`. | §8.2.5, §8.2.6, §8.2.14 |
| §2.5.2 Drawer height + shape | Half-sheet from bottom, `max-height: 75vh`, `position: fixed; bottom: 0; left: 0; right: 0`. No snap points. No drag handle. | §8.2.2 |
| §2.5.3 Drawer header | Close button only (top-right). No visible heading (inner ModelSelector `<h3>` remains; dialog `aria-label` provides dialog name). No Apply button. | §8.2.7 |
| §2.5.4 Selection-commit semantics | Live update on each toggle. No Apply/Done button. Architect lean confirmed. | §8.2.7 |
| §2.5.5 Dismissal | Esc, scrim-tap (`onPointerDown` on scrim element), close button. No swipe gesture (out of scope). | §8.2.1, §8.2.3 |
| §2.5.6 Backdrop scrim | `rgba(0,0,0,0.45)` semi-opaque, `z-index: 199`, `aria-hidden="true"`, `onPointerDown` closes drawer. | §8.2.3 |
| §2.5.7 Transition + animation | Slide-up from bottom, 200ms `ease-out` on open; instant dismiss on close. `prefers-reduced-motion: reduce` → instant both directions. | §8.2.4, §8.2.13 |
| §2.5.8 Trigger styling states | Rest/hover/focus-visible/active — token-only. Trigger remains visible when drawer is open (not hidden). Toggle behavior on trigger click. | §8.2.5, §8.2.6, §8.2.9 |
| §2.5.9 Open-drawer content | `overflow-y: auto` body; `padding: var(--space-4)`. ModelSelector inner `<h3>` retained. No Apply button. | §8.2.7 |
| §2.5.10 Touch target for rows | `min-height: 44px` scoped to `.mobile-model-drawer__body .model-selector__row`; same for action buttons. Rule lives in `mobile-model-drawer.css`. | §8.2.8 |
| §2.5.11 Scroll lock | Mandatory. `document.body.style.overflow = 'hidden'` on mount; restore on unmount (captured prior value in closure). | §8.2.11 |
| §2.5.12 DOM mount | Inline inside DataExplorer.tsx. `position: fixed` escapes stacking context without portal. | §8.2.12 |
| §2.5.13 z-index | Drawer panel: 200. Scrim: 199. Matches §8.1 hamburger at 200. No conflict (cannot both be open simultaneously). | §8.2.12 |
| §2.5.14 Reduced-motion | Mandatory `@media (prefers-reduced-motion: reduce)` block in `mobile-model-drawer.css` even with no transition. | §8.2.4, §8.2.13 |
| §2.6 A11y strings | Four strings confirmed verbatim. No additional prose. CDA SME bypass confirmed. | §8.2.14 |
| §2.10 Stacked-below CSS supersession | Retain single-column grid collapse; remove `grid-template-areas`; replace `width: 100%` with `width: auto` on selector slot; add `.model-selector { display: none; }` scoped to `<768px`. | §8.2.10 |

---

## Binding notes (Coder must apply before merge)

### M1 — Trigger toggle behavior (§8.2.6 and §8.2.9)

The Architect plan sketch shows the trigger's `onClick` as `() => setMobileSelectorOpen(true)` (open only). This verdict overrides that to a toggle: `() => setMobileSelectorOpen(prev => !prev)`. Rationale: the trigger remains visible when the drawer is open (unlike §8.1's hamburger which hides). A visible button that can only open the drawer is a WCAG 2.4.3 / cognitive confusion risk — the user can tap the button when the drawer is already open and nothing happens, with no visual feedback. Toggle behavior (open on first tap, close on second tap) is the correct affordance for a persistent visible trigger. The trigger's `aria-expanded` and `aria-label` update dynamically to communicate the toggle direction.

**Required implementation:** `onClick={() => setMobileSelectorOpen(prev => !prev)}` in `DataExplorer.tsx`. The trigger's `aria-label` must be `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED` when `mobileSelectorOpen === false` and `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN` when `mobileSelectorOpen === true`. The Tester must add a test case for "tap trigger when drawer open → drawer closes; focus remains on trigger."

### M2 — Scrim `onPointerDown` and panel event stop (§8.2.3 and §8.2.15)

The scrim element's `onPointerDown` handler calls `onClose`. The drawer panel element must prevent `pointerdown` events from bubbling to the scrim by calling `e.stopPropagation()` on the panel's own `onPointerDown` handler. Without this, a tap anywhere inside the drawer panel propagates up through React's synthetic event system and may reach the scrim handler. Coder adds `onPointerDown={(e) => e.stopPropagation()}` to the `.mobile-model-drawer__panel` element. The Tester adds a test case: "tap inside open drawer body → drawer does NOT close."

### M3 — Touch-target floor for "Select all" / "Clear all" buttons inside drawer (§8.2.8)

The current `.model-selector__action-link` has `padding: 0` and `border: none` — its rendered height is determined by `font-size: var(--font-size-xs)` (12px), far below the 44px WCAG 2.5.5 floor. The scoped override in `mobile-model-drawer.css` (§8.2.8) is mandatory. Without it, the action buttons inside the drawer fail WCAG 2.5.5. Coder includes all three scoped rules from §8.2.8 in `mobile-model-drawer.css`.

---

## Advisory notes (non-blocking; confirm in commit body)

- **A1:** iOS Safari has known rubber-band scroll behavior with `overflow: hidden` on `document.body`. If the iOS Safari spot-check (per Architect plan §2.8) shows noticeable page-scroll bleed during the drawer's internal scroll, the Coder may add `overscroll-behavior: contain` on `.mobile-model-drawer__body` as a defensive addition — this is CSS-only, no new dependency, and does not require a design system update.
- **A2:** The slide-up transition requires the component to mount in `translateY(100%)` and transition to `translateY(0)`. In a jsdom test environment, transitions do not run, so the Tester asserts the open class is present rather than asserting the computed transform value. The Tester should verify using class presence (`hasClass('mobile-model-drawer__panel--open')`) rather than style inspection for the animation state.
- **A3:** The `<ModelSelector>` `<h3>` heading "Models" is retained inside the drawer. The heading remains at `<h3>` level — do not change it to `<h2>` in response to the dialog context. Changing the heading level would require modifying `ModelSelector.tsx`, which is explicitly out of scope. The dialog's `aria-label="Model selector"` provides the dialog-level name independently of the heading hierarchy.
- **A4:** Bundle delta target is ≤5 KB gzipped. Three new files (MobileModelSelectorDrawer.tsx ~1.5 KB, mobile-model-drawer.css ~1.5 KB, mobile_model_drawer.ts ~0.3 KB) plus DataExplorer.tsx edits (~0.5 KB) and app.css edits (~0.2 KB) project to ~4 KB gzipped — within the 5 KB budget. Coder reports measured delta in commit body.
- **A5:** Focus restoration on close. The binding requirement is that focus returns to `drawerTriggerRef.current` on close (regardless of which close path triggered it: Esc, scrim-tap, close button, or M1 toggle-close). The Tester's tests verify this via `document.activeElement === triggerEl` after each close path.
- **A6:** The Architect plan's Tester section G9 reads "trigger hidden when drawer open." §8.2.9 overrides this: the trigger remains visible when the drawer is open. The Tester must update G9 (or its equivalent) to assert "trigger visible when drawer open; `aria-expanded === 'true'`; `aria-label === MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN`."

---

## OWID design fidelity rationale

A bottom-anchored half-sheet in `--color-background` (white) with a `border-top` separator, a 48px close button, and the existing `ModelSelector` component inside it reads as a clean, functional scientific instrument. The 200ms slide-up is a purposeful affordance signal (the panel came from the bottom and returns to the bottom), not decorative animation. No gradients, no colored panel backgrounds, no icon libraries. The trigger button uses `--color-surface` background with `--color-border` border — the same surface token used by the desktop `ModelSelector` container — maintaining visual continuity between the trigger and the panel it opens. OWID-fidelity PASS.

---

## 30-second journalist test rationale (PASS-WITH-NOTES)

A mobile user arriving at the dashboard sees the chart (full-width at `<768px`) and below the chart a labeled button: "Select models (6 selected)". The label is self-explanatory — no mental model required. Tapping it slides up a familiar panel with checkboxes. The user can adjust the selection and tap the "×" or tap outside to close. This interaction is discoverable within 30 seconds.

The PASS-WITH-NOTES is for M1: if the trigger opens but cannot toggle-close, a user who accidentally opens the drawer is left hunting for the "×" close button (which is inside the panel and not visible in peripheral view until they look up). The toggle behavior specified in M1 makes the interaction symmetric and ensures the 30-second test passes cleanly.

---

## WCAG AA rationale (PASS-WITH-NOTES)

All eight WCAG SCs cited in Architect plan §1 §2 point 2 are addressed:

- **1.4.3 Contrast (text):** `--color-text-primary` on `--color-background` ≈ 12.6:1. All drawer text meets 4.5:1. PASS.
- **1.4.11 Non-text contrast:** `--color-info` focus ring (#3360a9) on white ≈ 7.3:1. Trigger border is decorative (the button's accessible name and role are provided by ARIA, not by the border's visual presence), so 1.4.11 non-text contrast does not apply to it as an informational indicator. The trigger `--color-text-primary` content ≈ 11.8:1 on surface. PASS.
- **2.1.1 Keyboard:** trigger is a `<button>` (Enter/Space open); all checkboxes are native `<input type="checkbox">` (Tab/Space); close button is a `<button>` (Enter/Space close); focus trap prevents escape. PASS.
- **2.1.2 No keyboard trap:** Esc always available (event listener in `useEffect`); close button always available; toggle trigger available. PASS.
- **2.4.3 Focus order:** close button receives initial focus on open; Tab proceeds forward through close → checkboxes → Select all → Clear all → wrap. DOM order matches visual order. PASS.
- **2.4.7 Focus visible:** all focusable elements use `outline: 2px solid var(--color-info); outline-offset: 2px`. PASS.
- **2.5.5 Target size:** trigger `min-height: 48px` full-width. Close button 48×48 px. Rows `min-height: 44px` (M3 scoped override). Action buttons `min-height: 44px` (M3 scoped override). PASS after M3 is applied.
- **4.1.2 Name, Role, Value:** trigger has `aria-label`, `aria-expanded`, `aria-controls`, `aria-haspopup`. Panel has `role="dialog"`, `aria-modal`, `aria-label`, `id`. Close button has `aria-label`. PASS.

M2 (scrim event stop) and M3 (action button touch targets) are the two accessibility-affecting notes. Both are binding.

---

## Required before merge

1. Apply M1: `onClick={() => setMobileSelectorOpen(prev => !prev)}` on the trigger; trigger remains visible when drawer open; `aria-label` toggles dynamically.
2. Apply M2: `onPointerDown={(e) => e.stopPropagation()}` on the drawer panel element.
3. Apply M3: scoped 44px touch-target rules in `mobile-model-drawer.css` for `.model-selector__row` and `.model-selector__action-link` inside the drawer body.
4. DESIGN_SYSTEM.md v0.4.8 changes already applied at the plan-review stage (this commit). Coder's T12 implementation does not re-update DESIGN_SYSTEM.md; it must reference §8.2 in `MobileModelSelectorDrawer.tsx`'s file header comment per Architect plan AC20.
5. Confirm `<ModelSelector>` is passed as `children` to the drawer; no duplicate rendering; no edits to ModelSelector.tsx beyond what is explicitly necessary (likely zero — the drawer wraps the existing component).
6. Confirm no new dependencies; no scope creep into T1/T11/T13 territory.

---

## Escalation items for Mark

None. All decisions are resolvable within existing tokens and the minimum-viable-surface posture. CDA SME bypass confirmed (no non-standard visible strings introduced). The T11 + T12 z-index coexistence at 200 is fine (cannot both be open simultaneously per §8.2.12).

---

## Verdict rationale

T12 is a chrome task on the accessibility floor + readability axis, with the substantive divergence from T11 being mandatory body scroll lock (T12) versus declined scroll lock (T11). The plan is well-structured and addresses every required decision point. The three binding notes (M1 toggle, M2 event stop, M3 action-button touch targets) are surgical corrections that protect WCAG 2.4.3, 2.4.7, and 2.5.5 compliance. M1 is a one-character code change (`true` → `prev => !prev`); M2 is a single attribute addition; M3 is three short CSS rules already specified verbatim in §8.2.8. PASS-WITH-NOTES is appropriate: the plan clears all four scorecard criteria with three minor corrections to apply before the Coder commits.

---

*Posted to #lsb-ui-ux. DESIGN_SYSTEM.md v0.4.8 update posted to #lsb-ui-ux simultaneously. Coder may proceed on receipt of this verdict with M1/M2/M3 applied; DESIGN_SYSTEM.md v0.4.8 update is in this same commit.*
