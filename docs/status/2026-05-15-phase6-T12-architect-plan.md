# Phase 6 T12 — Mobile bottom-drawer for ModelSelector — Architect Plan

**Date:** 2026-05-15
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T12 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T12 as "Replace the T13 stacked-below-on-mobile layout with a true bottom-drawer overlay for the model-selector panel at `<768px`. Includes scroll management, focus trap, overlay positioning. T13 verdict deferred this to Phase 6 explicitly").
**Status:** Awaiting Mark's direction on the one open question in §1.A (drawer trigger placement); then UI/UX dispatch (DESIGN_SYSTEM.md §8.2 extension required); CDA SME bypassed unless UI/UX introduces non-standard prose (see §6).

T12 is a **pure frontend chrome task** — no methodology surface, no data layer, no schema touch. It supersedes the T13 stacked-below mobile rule for the `.explorer-layout__selector` block with a dismissible bottom-drawer overlay that wraps the existing `ModelSelector` content. The inner `ModelSelector` component DOM is unchanged; only its mobile presentation envelope changes.

---

## §0. Reading list (mandatory before Coder dispatch)

Common to T12:

1. `/opt/lsb-agent/CLAUDE.md` §6 binding rules — **R10** (N/A — no viz, no point estimate; reviewer must not reject for missing CI), **R12** §1.5.4 forbidden vocabulary (applies to any LSB-authored visible or SR-only string T12 introduces), **R13** design-system gating (T12 specifically blocks on `DESIGN_SYSTEM.md` §8.2 extension by UI/UX), **R14** no spend gates (trivially N/A); §7 forbidden vocabulary table; §8 workflow (one commit per task; direct-to-master); §9 pitfall #6 (no inventing visual decisions — drawer direction, snap points, animation curve, trigger placement are all UI/UX's call), pitfall #7 (forbidden vocab in any committed text), pitfall #10 (no scope creep — T12 does NOT touch the inner ModelSelector logic).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact), §5.3 (Phase 6 framing).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` v0.4.7 — specifically §1 tokens (colors, spacing, font, border-radius, shadow tokens), §3.7 ModelSelector spec (inner-DOM untouched; T12 only changes the outer envelope at `<768px`), §7 accessibility floor (focus indicators, WCAG AA contrast, screen reader alternative, 44×44 touch target floor — T12 specifically tightens this to 48×48 to mirror §8.1 precedent), **§8.0** (the bullet "Control panel collapses to a bottom drawer on screens narrower than 768px" is T12's binding requirement), **§8.1** (the T11 hamburger spec is the directly-analogous precedent — many decisions mirror it; the Coder reads §8.1 carefully before reading the new §8.2), §11 component inventory (T12 adds `MobileModelSelectorDrawer.tsx` or UI/UX-named equivalent), §12.1 reveal cascade (T12 does NOT add or change a cascade slot — the drawer trigger renders inside DataExplorer's already-existing layout slot).
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T12 — original scope statement; §5 "DESIGN_SYSTEM.md / §8 Mobile bottom-drawer" line (kickoff phrasing: "Update — full spec replacing the T13 deferral note").
5. `/opt/lsb-agent/docs/status/2026-05-11-phase5-T13-uiux-verdict.md` — the "Five mobile gaps resolution" table (gap 4 is the desktop nav `display: none`, gap 5 is MDS viewBox; the deferral of bottom-drawer is documented in the T13 plan-level verdict and `DESIGN_SYSTEM.md` v0.4.4 changelog: "Records the mobile bottom-drawer deferral decision: §8 calls for a control panel bottom-drawer on `<768px`; T13 accepts the stacked-below layout as the Phase 5 mobile implementation; a true bottom-drawer overlay is deferred to Phase 6.").
6. `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-architect-plan.md` — directly-analogous precedent plan. Many decisions mirror.
7. `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-uiux-plan-verdict.md` — directly-analogous UI/UX verdict, including the M1 single-source-of-truth note posture.
8. `/opt/lsb-agent/apps/dashboard/src/components/DataExplorer.tsx` — current host of the `ModelSelector`. Lines 280–289 render the `.explorer-layout__selector` block; T12 inserts a conditional bottom-drawer wrapper at `<768px` while keeping the desktop inline rendering at `≥768px`. Lines 173–177 (Cite/Embed trigger refs) are the precedent pattern for `drawerTriggerRef`.
9. `/opt/lsb-agent/apps/dashboard/src/components/ModelSelector.tsx` — **the inner DOM is unchanged.** T12 wraps this component, does not modify it. Lines 145–259 are the JSX the drawer will host verbatim.
10. `/opt/lsb-agent/apps/dashboard/src/components/MobileNav.tsx` — **fresh T11 precedent.** The drawer reuses the same focus-trap pattern (`getFocusableElements` at lines 11–23; keydown effect at lines 43–73; close-button initial focus at lines 36–41; trigger focus-restore via parent's `useEffect`).
11. `/opt/lsb-agent/apps/dashboard/src/components/Header.tsx` — T11 precedent for the trigger button + state + focus-restore pattern (lines 77–134). The drawer follows the same `prevOpenRef` posture for focus restoration.
12. `/opt/lsb-agent/apps/dashboard/src/components/CiteModal.tsx` — older dialog precedent. `getFocusableElements` at lines 76–89 (the original; T11 copied this verbatim). Focus-trap keyboard effect at lines 220–264. Return-focus-on-close at lines 277–284. **Scroll lock is NOT present in CiteModal today** — T12 introduces it. The Coder is the first to add a body-scroll-lock pattern to this codebase.
13. `/opt/lsb-agent/apps/dashboard/src/styles/app.css` lines 659–692 (current `.explorer-layout` and the `@media (max-width: 768px)` stacked-below rule at 681–692 — this rule is REPLACED in T12, not retained); lines 694–862 (current `.model-selector__*` rules — touched only if mobile-specific touch-target rules need adding; UI/UX confirms in §8.2).
14. `/opt/lsb-agent/apps/dashboard/src/styles/mobile-nav.css` — T11 precedent for token-only CSS module structure.
15. `/opt/lsb-agent/apps/dashboard/src/copy/mobile_nav.ts` — T11 precedent for the copy module structure.
16. `/opt/lsb-agent/apps/dashboard/src/__tests__/t11-mobile-nav.test.tsx` — directly-analogous test pattern. T12's tester reuses the G1–G26 structure with model-drawer-specific renames.
17. Memory: `feedback_ui_polish_scope.md` (Phase 6 = minimum viable functional dashboard; UI/UX gating reduces to accessibility floor + R10 + readability — R10 N/A here).

---

## §1. Mark's binding directives + Phase 6 framing

1. **Phase 6 minimum-viable functional surface** (memory `feedback_ui_polish_scope.md`). Plain dialog mechanic, default tokens, no decorative animation beyond what UI/UX explicitly specifies, no microcopy work beyond accessibility-required strings.
2. **WCAG AA accessibility floor is the bar.** WCAG 2.1 AA. The SCs in scope:
   - 1.4.3 Contrast (Minimum) — AA — text inside the open drawer meets 4.5:1; the trigger button glyph (if any) meets 3:1 non-text contrast.
   - 1.4.11 Non-text Contrast — AA — focus indicators, the drawer trigger, the close affordance, the drawer top-edge separator all meet 3:1.
   - 2.1.1 Keyboard — A — every interaction reachable with a keyboard (Tab to trigger, Enter/Space to open, Tab cycles inside open drawer, Esc to close, every checkbox keyboard-reachable).
   - 2.1.2 No Keyboard Trap — A — Esc, outside-tap, and the close button all release focus.
   - 2.4.3 Focus Order — A — focus order matches DOM order inside the open drawer.
   - 2.4.7 Focus Visible — AA — every focusable element shows a visible focus ring (especially every checkbox row, "Select all", "Clear all", and the close button).
   - 2.5.5 Target Size — every touchable target ≥ 44×44 px at `<768px`. T12 mirrors §8.1's 48×48 px posture for trigger and close button, and `min-height: 48px` (or ≥44px floor — UI/UX's call) per checkbox row to mirror §8.1 `.mobile-nav__link` spec.
   - 4.1.2 Name, Role, Value — A — drawer trigger has accessible name; open/close state is announced via `aria-expanded`; the drawer panel itself has `role="dialog"` with `aria-modal="true"` and `aria-label`.
3. **No new dependencies.** No `@headlessui/react`, `react-aria`, `focus-trap-react`, `framer-motion`, `radix-ui`, `body-scroll-lock`, or similar. The `getFocusableElements` helper is duplicated from `MobileNav.tsx` (or extracted to a shared module; see §5). Reviewer R8 enforces.
4. **No methodology surface, no data surface, no schema touch.** T12 is chrome. CDA SME bypass per kickoff §2 T12; sole conditional gate is on any LSB-authored visible string (see §2.6).
5. **Forbidden vocabulary (§1.5.4) applies to every LSB-authored string T12 introduces** — the trigger button label, the SR-only "open model selector" / "close model selector" copy, any visible heading or microcopy inside the drawer. None are model-facing strings; the table's forbidden phrases (`worldview`, `believes`, `thinks`, `cultural bias`, `corpus lens`) are unlikely to bite. Reviewer's grep against the new copy module still runs.
6. **The breakpoint is `<768px`** — byte-identical with §8.1 hamburger breakpoint and with the existing T13 stacked-below `@media (max-width: 768px)` block at `app.css:681`. Two mirrored rules: (a) at `<768px`, hide the inline `.explorer-layout__selector` content and show the drawer trigger; (b) at `≥768px`, hide the drawer trigger and show the inline selector. The Coder verifies no dead-zone at exactly 768 px (exactly one of the two surfaces renders).
7. **Bundle budget: T12 adds ≤ 5 KB gzipped** against the post-T11 baseline (~95 KB per T11 plan §8). No new dep; plain TSX + token-only CSS. Phase 6 cumulative cap is 400 KB.
8. **No portal.** Mirror §8.1's inline-mount decision (`position: fixed` already escapes the stacking context; portal adds setup cost without value). If UI/UX overrides to portal in §8.2, the Coder follows.

---

## §1.A. Open question for Mark — drawer trigger placement (decision before UI/UX dispatch)

**Q1 (the only Mark-level question for T12):** Where does the drawer trigger button live on the page when `<768px`?

| Option | What it looks like | Pros | Cons |
|---|---|---|---|
| (a) **Inline in the explorer area** — a button rendered inside `.explorer-layout__selector` at `<768px`, replacing the full inline `ModelSelector`. The button reads "Select models (6 selected)" or similar; tapping it opens the drawer. | Local to where the user is interacting (the explorer). No global UI artifact. Mirrors §8.1's locality posture (the hamburger is inside the Header it controls). | If the user has scrolled past the explorer, they cannot re-open the drawer without scrolling back up. |
| (b) **Sticky to the bottom of the viewport at `<768px`** — a fixed-position button bar (e.g., "Select models (6 selected)") always visible. Tapping opens the drawer. | Always-available, regardless of scroll position. Standard mobile-app pattern. | Adds a permanent piece of chrome. Visually competes with the page. Z-index management. Larger surface area. |
| (c) **A floating action button (FAB)** in the bottom-right corner at `<768px`. | Compact; conventional. | Consumer-product idiom; the §0 design philosophy explicitly rejects this. |

**Architect recommendation: option (a).** Rationale:

1. **Locality matches §8.1 precedent.** The hamburger lives in the Header it controls; the drawer trigger should live in the explorer it controls. The user encountering the explorer encounters the trigger in the same scroll position where the inline selector renders on desktop.
2. **No new persistent chrome.** Option (b) introduces a permanent visual element that competes with the article's prose-reading posture; option (c) is explicitly contra-§0 ("no consumer-product idioms"). Option (a) is minimal-additive.
3. **The trigger does NOT need to be reachable from anywhere on the page** — the explorer is the only context in which model selection has semantic meaning, and the explorer's vertical extent is small enough on mobile that scrolling back to the trigger is one swipe. The current state (stacked-below selector, T13) has the same property; option (a) preserves the existing locality.
4. **Smaller scope.** Option (a) does not require a sticky positioned element, does not touch `app.css`'s body or layout containers, and does not require z-index coordination with `Header`, `Footer`, or `DownloadBar`.

**Decision authority:** Mark. The plan body below assumes option (a). If Mark picks (b), §2.4 (trigger placement) and §3 acceptance criteria 2–4 expand; if Mark picks (c), §2.4 changes shape and §0 design philosophy requires a written exception. Mark's confirmation unblocks UI/UX dispatch.

**Note on T11 dependency:** unlike T11's T1-dependency question, T12 has no upstream content dependency. The drawer hosts the existing `ModelSelector` component verbatim; that component is already complete and shipping.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Placement — **`<MobileModelSelectorDrawer>` rendered inside `DataExplorer.tsx`, controlled by DataExplorer state.**

Concrete:
- `DataExplorer.tsx` continues to own `selectedModels` / `onSelectionChange` state at lines 153–162. **No state moves.**
- A new local state `mobileSelectorOpen` (boolean) lives in `DataExplorer.tsx`, parallel to `isCiteOpen` / `isEmbedOpen` at lines 174–175. A new `drawerTriggerRef` parallels `citeTriggerRef` / `embedTriggerRef` at lines 176–177.
- At `≥768px`, the existing inline rendering of `<ModelSelector>` inside `.explorer-layout__selector` remains visible exactly as today (`DataExplorer.tsx` lines 280–289 unchanged in their `≥768px` form).
- At `<768px`, the inline `<ModelSelector>` block is hidden (via CSS `display: none` on `.explorer-layout__selector`, replacing the current stacked-below rule at `app.css:681–692`); a drawer trigger button is rendered in its place (via a new `.explorer-layout__mobile-selector-trigger` element inside the `.explorer-layout__selector` grid slot, conditionally `display: flex` only at `<768px`); the drawer panel (`<MobileModelSelectorDrawer>`) is conditionally mounted when `mobileSelectorOpen === true`, rendering the same `<ModelSelector>` component inside its dialog body.
- The same `selectedModels` / `onSelectionChange` / `modelColors` / `domainResult` props flow from `DataExplorer` to `ModelSelector` regardless of which envelope (inline or drawer) renders it. **There is exactly one source of truth for selection state.**

**Rationale:**
- `DataExplorer` is the binding owner of selection state (per §12.4 palette ownership and lines 153–162). The drawer is presentational; it does not own state.
- Wrapping (not replacing) `ModelSelector` keeps the component's interior DOM and behavior fully unchanged. T12 is purely a mobile-presentation envelope.

### §2.2. Cascade impact — **none.**

The reveal cascade for the explorer is handled at `App.tsx` (T13 cascade work). T12 adds no new cascade slot. The drawer, when open, is rendered as a positioned `position: fixed` child of `DataExplorer` and does not participate in the page-load cascade (it appears in response to user interaction).

Coder verifies the cascade order at mount is unchanged from post-T11 baseline.

### §2.3. Component split — **`MobileModelSelectorDrawer.tsx` is a new file under `apps/dashboard/src/components/`.**

The drawer wraps `<ModelSelector>` without changing its props or behavior. The drawer is responsible for:

- ARIA dialog semantics (`role="dialog"`, `aria-modal="true"`, `aria-label` or `aria-labelledby`).
- Focus trap (Tab/Shift+Tab cycle within drawer only).
- Initial focus on the close button on open (mirroring §8.1.1).
- Esc-to-close.
- Outside-tap (backdrop / scrim, if any) closes — UI/UX decides if the drawer has a scrim; if it does, scrim click closes.
- Body scroll lock on open; restore on close and on unmount.
- Visible close affordance (a dedicated close button mirroring `.mobile-nav__close`).

The drawer renders `<ModelSelector ...>` inside its content area, passing through all four props (`domainResult`, `selectedModels`, `onSelectionChange`, `modelColors`) verbatim. The drawer adds NO logic to selection state; it is a pure presentational envelope.

Wiring sketch (UI/UX may refine details in §8.2):

```tsx
// DataExplorer.tsx (sketch)
const [mobileSelectorOpen, setMobileSelectorOpen] = useState(false);
const drawerTriggerRef = useRef<HTMLButtonElement>(null);
const prevDrawerOpen = useRef(mobileSelectorOpen);

useEffect(() => {
  if (prevDrawerOpen.current && !mobileSelectorOpen) {
    drawerTriggerRef.current?.focus();
  }
  prevDrawerOpen.current = mobileSelectorOpen;
}, [mobileSelectorOpen]);

// In JSX:
<div className="explorer-layout__selector">
  {/* Desktop inline rendering (≥768px) — unchanged */}
  <ModelSelector
    domainResult={domainResult}
    selectedModels={selectedModels}
    onSelectionChange={setSelectedModels}
    modelColors={modelColors}
  />

  {/* Mobile drawer trigger (<768px) — CSS-gated via .explorer-layout__mobile-selector-trigger */}
  <button
    ref={drawerTriggerRef}
    type="button"
    className="explorer-layout__mobile-selector-trigger"
    aria-label={MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED}
    aria-expanded={mobileSelectorOpen}
    aria-controls="mobile-model-drawer-panel"
    aria-haspopup="dialog"
    onClick={() => setMobileSelectorOpen(true)}
  >
    {MOBILE_MODEL_DRAWER_TRIGGER_TEXT(selectedModels.length)}
  </button>
</div>

{mobileSelectorOpen && (
  <MobileModelSelectorDrawer
    id="mobile-model-drawer-panel"
    onClose={() => setMobileSelectorOpen(false)}
    triggerRef={drawerTriggerRef}
  >
    <ModelSelector
      domainResult={domainResult}
      selectedModels={selectedModels}
      onSelectionChange={setSelectedModels}
      modelColors={modelColors}
    />
  </MobileModelSelectorDrawer>
)}
```

The Coder may refactor (e.g., move the trigger button into a sibling `<MobileModelSelectorTrigger>` component) at their discretion; the binding constraint is single-source state in `DataExplorer` and exactly-one-`<ModelSelector>`-instance per render context.

### §2.4. ARIA pattern — **dialog with modal semantics + focus trap.**

Mirroring §8.1.1 verbatim. The drawer panel uses `role="dialog"`, `aria-modal="true"`, `aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}` (or `aria-labelledby` if UI/UX adds a visible heading). The trigger carries `aria-expanded`, `aria-controls`, `aria-haspopup="dialog"`.

**Focus behavior** (mirrors §8.1.1's table):

| Event | Required behavior |
|---|---|
| Drawer opens | Initial focus moves to the close button inside the drawer. |
| Tab | Cycles forward through focusable elements inside the drawer only. The drawer contains the close button, every checkbox row, "Select all", and "Clear all" — substantially more focusable elements than §8.1's panel (which has just 5: close + 4 nav links). |
| Shift+Tab | Cycles backward within the drawer only. |
| Esc | Closes the drawer; focus returns to the drawer trigger. |
| Outside-tap (backdrop, if any) | Closes the drawer; focus returns to the drawer trigger. UI/UX decides whether there is a scrim (see §2.5.4). |
| Close button activated | Closes the drawer; focus returns to the drawer trigger. |
| Drawer closes (any path) | Focus restored to the drawer trigger via parent's `useEffect`. |

**Focus trap implementation:** reuse `getFocusableElements` from `MobileNav.tsx` (or extract to a shared `apps/dashboard/src/lib/focus-trap.ts` helper — see §5). The drawer's focusable set is large (1 close + N checkbox rows + 2 action buttons), where N is the number of available models (currently up to 11 per §12.4). The Tab cycle wraps from the last action button back to the close button; Shift+Tab from the close button wraps to the last action button.

**WCAG 2.1.2 compliance:** Esc and the close button are both always-available escape paths.

**Decision authority:** UI/UX may override the initial-focus target (e.g., first checkbox row instead of close button) in §8.2. The Architect's lean is the close button, mirroring §8.1.1.

### §2.5. Visual decisions reserved for UI/UX (Architect does NOT specify)

Per CLAUDE.md §9 pitfall #6 — the Architect does NOT invent visual decisions. The following are explicitly UI/UX's call, codified in `DESIGN_SYSTEM.md §8.2` extension before Coder dispatch:

1. **Drawer direction and shape.** Bottom-up half-sheet (drawer occupies bottom ~50% of viewport), bottom-up full-sheet (drawer fills viewport from bottom), top-down full-sheet (mirroring §8.1.4 hamburger), or center-modal (CiteModal-like, not really a drawer). Architect's lean: **bottom-up sheet** to match the kickoff phrase "bottom-drawer overlay," with UI/UX choosing half vs full and any snap points. UI/UX may select full-screen to maximize the focus-trap-friendly surface area for the ~11-model list.
2. **Drawer height behavior.** Fixed height (e.g., `max-height: 75vh`), full-screen, or with snap points. Whether the drawer scrolls internally or pushes content out the top. The model list can be ~11 rows + 2 group dividers + "Select all"/"Clear all" + the max-6 warning — this can exceed mobile viewport height; the drawer must scroll internally without spilling.
3. **Transition / animation curve and duration on open/close.** §8.1.5 chose "none / instant" — UI/UX may match this for §8.2 or introduce a `prefers-reduced-motion`-gated slide-up transform. Whatever UI/UX picks, the `@media (prefers-reduced-motion: reduce)` block in CSS is mandatory regardless.
4. **Backdrop / scrim color and opacity.** None (full-bleed panel covers everything, mirroring §8.1.5), or `rgba(0,0,0,*)` semi-opaque scrim above the underlying page. If there is a scrim, it must be a separate clickable element under `aria-hidden` (matching CiteModal's pattern) and must close the drawer on tap.
5. **Trigger button styling.** Token-only. Plausible: a full-width "Select models (N selected)" button inside `.explorer-layout__selector` at `<768px`, with `--color-surface` background, `--color-border` border, body-text styling. Touch target ≥48×48 px (mirroring §8.1.8 trigger).
6. **Trigger button label text.** The Architect proposes `"Select models (N selected)"` as a placeholder; UI/UX confirms or rewrites. Whatever string UI/UX picks must be exhaustively enumerated in the copy module (see §2.6) and CDA-SME-cleared if non-trivial.
7. **Open-drawer styling.** The drawer's background color, border, padding, separator above the close button, position of the close button (top-right per §8.1 precedent? or top-left? — UI/UX call).
8. **Close button styling.** Token-only. Architect's lean: identical to `.mobile-nav__close` (48×48 px, `×` glyph, `aria-label` from copy module).
9. **Visible heading inside the drawer.** Whether to show a `<h2>Models</h2>` or rely solely on `aria-label`. Note: `ModelSelector` itself already renders a `<h3 class="model-selector__heading">Models</h3>` at line 147 — UI/UX must decide whether to (a) hide that heading visually inside the drawer (`.sr-only`, since the dialog's aria-label provides the name) and add a separate dialog heading via `aria-labelledby`, or (b) keep the inner h3 visible and use it as the `aria-labelledby` target (changing it to `<h2>` and updating the section structure), or (c) leave the inner h3 alone and use `aria-label` on the dialog. Architect's lean: (c). UI/UX decides.
10. **Touch target floor for checkbox rows inside the open drawer.** WCAG 2.5.5 sets 44×44 px; §8.1.8 sets 48×48 px for nav links. The current `.model-selector__row` has `padding: var(--space-2) var(--space-2)` which is well below either floor on touch. UI/UX adds a `min-height: 48px` (or 44px) rule scoped to inside-the-drawer-only (so desktop's compact rows are unchanged). Whether this rule lives in `mobile-model-drawer.css` (scoped via `.mobile-model-drawer__body .model-selector__row { ... }`) or in `app.css`'s existing `@media (max-width: 768px)` block (which would also affect the now-hidden inline mobile rendering) is a UI/UX detail.
11. **Whether the drawer commits selection immediately on each toggle (live update, T13 posture)** or requires an explicit "Apply"/"Done" button before commit (modal pattern). Architect's lean: **live update** — matches the existing desktop behavior, requires no new state, the drawer is a presentational envelope and not a transaction.
12. **Where the drawer mounts in the DOM** — inside `DataExplorer.tsx`'s JSX (Architect's lean, mirroring §8.1's inline mount), or portal to `document.body`. UI/UX confirms in §8.2.

**The Coder MUST NOT invent any of these.** If `DESIGN_SYSTEM.md §8.2` is silent on a decision, the Coder pauses and routes back to UI/UX (CLAUDE.md §9 pitfall #6; §6 binding rule 13).

### §2.6. LSB-authored prose surface — exhaustive list for §1.5.4 + CDA-SME conditional review

T12 introduces accessibility + visible strings. **All such strings live in `apps/dashboard/src/copy/mobile_model_drawer.ts`** (mirroring `mobile_nav.ts` from T11). The drawer reuses `MOBILE_NAV_PANEL_LABEL` from `mobile_nav.ts` ONLY IF UI/UX explicitly wants identical phrasing — the Architect recommends NOT reusing, since the drawer's aria-label should distinguish the model-selector context from the site-nav context.

| Variable | Proposed value | §1.5.4 reading | Where it surfaces |
|---|---|---|---|
| `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED` | `"Open model selector"` | Descriptive, technical, no psychological attribution. Standard a11y phrasing. | `aria-label` on the trigger button when the drawer is closed. |
| `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN` | `"Close model selector"` | Same. | `aria-label` on the trigger button when the drawer is open (if UI/UX keeps a single button across states; if separate close affordance, this string surfaces on the close button). |
| `MOBILE_MODEL_DRAWER_PANEL_LABEL` | `"Model selector"` | Same. Generic; descriptive. | `aria-label` on the dialog. |
| `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)` (function returning string) | `"Select models (N selected)"` where N is `selectedModels.length` | Descriptive. "N" is a count, not a quality attribution. No forbidden vocab. | Visible text on the trigger button. |
| `MOBILE_MODEL_DRAWER_HEADING` (optional, only if UI/UX includes a visible dialog heading) | `"Models"` or `"Select models"` — UI/UX confirms or removes | Same. Mirrors the existing `<h3>Models</h3>` inside `ModelSelector.tsx` line 147. | Visible `<h2>` inside the drawer; `aria-labelledby` target if UI/UX uses it. |

**No model-facing strings.** No forbidden-vocab risk from the §1.5.4 table.

**CDA SME conditional review:** the four standard strings + the parameterized trigger text are short, generic, accessibility-required. **The Architect recommends bypassing CDA SME for T12** unless UI/UX flags one as needing CDA SME judgment. If UI/UX introduces any additional visible string beyond those listed (e.g., a tagline, a hint, an explanatory caption), the Architect re-routes to CDA SME for a one-string verdict before Coder dispatch.

**Reviewer's forbidden-vocab grep** runs against `mobile_model_drawer.ts` regardless (mirroring T11's posture on `mobile_nav.ts`).

### §2.7. Reduced-motion handling — **mandatory CSS block.**

DESIGN_SYSTEM.md §12.1 binding: `prefers-reduced-motion: reduce` → instant reveal, no animation. T12 carries this forward via a mandatory `@media (prefers-reduced-motion: reduce) { .mobile-model-drawer__panel { transition: none; animation: none; } }` block in `mobile-model-drawer.css`. The block must be present **even if §8.2 specifies "no transition"** as forward safety, mirroring §8.1.5's belt-and-suspenders declaration.

The Coder verifies via DevTools "Emulate CSS prefers-reduced-motion: reduce" that the drawer appears and disappears instantly (or with whatever fallback UI/UX specifies — if any) when this preference is set.

### §2.8. Scroll lock — **MANDATORY (key difference from T11).**

This is the **single substantive divergence from §8.1** (T11). The T11 hamburger menu has very little content (5 focusable elements, all visible above the fold on any reasonable mobile viewport) and does not need scroll lock. **The model-selector drawer hosts an 11-model list with origin group dividers, an "Apply" affordance, and a max-6 warning** — this content may exceed viewport height; the drawer scrolls internally; touch-scroll events that originate inside the drawer must NOT bleed to the underlying page.

**Binding implementation:**

1. On drawer open, set `document.body.style.overflow = 'hidden'`.
2. On drawer close (any path: Esc, outside-tap, close button), restore `document.body.style.overflow` to its prior value (capture in a ref before mutation; restore from ref on cleanup).
3. The `useEffect` cleanup function MUST restore overflow even if the component unmounts while the drawer is open (e.g., parent re-renders, route changes). The pattern:

```tsx
useEffect(() => {
  if (!isOpen) return;
  const prevOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  return () => {
    document.body.style.overflow = prevOverflow;
  };
}, [isOpen]);
```

4. The drawer's own content area is `overflow-y: auto` so the model list scrolls inside the drawer.
5. The Tester verifies (a) `document.body.style.overflow === 'hidden'` while drawer is open, (b) restored to its prior value after close, (c) restored after a forced unmount during open state.

**This is the first body-scroll-lock pattern in the codebase.** CiteModal and EmbedModal do NOT lock body scroll today (per §1.A of T11 plan). T12 introduces it. The Coder MUST NOT refactor CiteModal/EmbedModal to use the same pattern in the same commit (CLAUDE.md §8 one-commit-per-task); if extraction to a shared hook (e.g., `apps/dashboard/src/lib/useBodyScrollLock.ts`) is warranted, that is its own future task.

**Risk note:** body-scroll-lock has known iOS Safari edge cases (rubber-band bounce, position: fixed misbehavior). The vitest+jsdom test stack does not exercise these; the Coder spot-checks on a real iOS Safari before committing. If iOS Safari behaves badly, escalation back to UI/UX to consider alternatives (e.g., `touch-action: none` on the underlying body, or accepting some scroll bleed).

### §2.9. DOM mount location — **inline inside DataExplorer.tsx, not portal.**

Mirroring §8.1's inline-mount decision. `position: fixed` already escapes the stacking context. Z-index: the drawer is `z-index: 200` (matching `.mobile-nav__panel`); the underlying explorer content is in the default stacking context. The drawer sits above the sticky header (header `z-index: 100`).

UI/UX may override to portal in §8.2 if there is a stacking-context reason to (e.g., a parent transform creating a new stacking context that would clip `position: fixed`). The Coder follows whatever §8.2 specifies.

### §2.10. Replacement of the T13 stacked-below CSS rule

The existing `app.css:681–692` block:

```css
@media (max-width: 768px) {
  .explorer-layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "viz"
      "selector";
  }
  .explorer-layout__selector {
    width: 100%;
  }
}
```

Is **superseded** by T12. The Coder either:
- (a) Removes the `grid-template-columns: 1fr` / `grid-template-areas` overrides (since at `<768px` only the trigger button renders inside `.explorer-layout__selector`, not a full panel) and replaces them with `.explorer-layout__selector { width: auto; } .model-selector { display: none; }` (or scopes the desktop `ModelSelector` inline rendering behind a `@media (min-width: 769px)` rule); OR
- (b) Retains the layout collapse (single-column at `<768px`) for visual layout reasons and only hides the inline `.model-selector` content while showing the trigger button.

UI/UX confirms in §8.2 which approach. The plan's binding requirement is "no dead CSS rules left over"; the Reviewer checks that the post-T12 mobile CSS describes exactly the drawer-trigger-and-overlay state, not a vestigial stacked-below posture.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. At viewport width ≥ 768 px: the explorer renders exactly as today — `<ModelSelector>` is inline in `.explorer-layout__selector`; no drawer trigger button is visible; the `MobileModelSelectorDrawer` component is not mounted.
3. At viewport width < 768 px: the inline `<ModelSelector>` is NOT directly visible; a single drawer trigger button is visible inside `.explorer-layout__selector` (or wherever §8.2 specifies, per §1.A option chosen by Mark) reading the §2.6 trigger text.
4. The breakpoint is byte-identically `768px` on (a) the show-drawer-trigger rule, (b) the hide-inline-`.model-selector` rule, and (c) the existing `.site-header__nav` and `.explorer-layout` mobile rules elsewhere in `app.css`. Coder verifies no dead-zone at exactly 768 px (exactly one selector surface renders).
5. Drawer trigger button: `aria-label={MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED}` when closed; `aria-expanded={true|false}` reflects open/close state; `aria-controls="mobile-model-drawer-panel"` points to the panel id; `aria-haspopup="dialog"`.
6. Drawer trigger touch target: computed bounding-box width × height ≥ 44×44 px (Architect lean: 48×48 mirroring §8.1.8; UI/UX confirms in §8.2).
7. Drawer trigger keyboard activation: Enter and Space both open the drawer.
8. Drawer panel open semantics:
   - Panel has `role="dialog"`, `aria-modal="true"`, `aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}` (or `aria-labelledby` if UI/UX adds a visible heading per §2.5.9).
   - Panel has `id="mobile-model-drawer-panel"` matching the trigger's `aria-controls`.
   - Initial focus lands on the close button inside the drawer (Architect lean per §2.4; UI/UX may override to first checkbox).
   - Tab/Shift+Tab cycle within the drawer only; focus does NOT escape to underlying page content.
   - Esc closes the drawer; focus returns to the drawer trigger.
   - If §8.2 specifies a scrim: backdrop / outside-tap closes the drawer; focus returns to the trigger.
   - The close button closes the drawer; focus returns to the trigger.
9. Focus indicators: every focusable element inside the open drawer (close button, every checkbox, "Select all", "Clear all") has a visible focus ring at ≥3:1 non-text contrast (WCAG 1.4.11). Tokens only (`outline: 2px solid var(--color-info)` mirroring §8.1.7 and `.mobile-nav__close:focus-visible`).
10. WCAG AA contrast: every text element inside the open drawer meets 4.5:1 against its background. Glyphs and focus rings meet 3:1.
11. Touch targets inside the open drawer: every checkbox row, "Select all", "Clear all", and the close button has bounding box ≥44×44 px (Architect lean: 48×48 mirroring §8.1.8; UI/UX confirms in §8.2 per §2.5.10).
12. Mobile usable at 320 px viewport width: drawer content does not overflow horizontally; the model-selector inner DOM (long model short names, origin badges, weights badges) wraps or scrolls without horizontal page scroll.
13. **Body scroll lock (§2.8 mandatory):**
    - On drawer open, `document.body.style.overflow === 'hidden'`.
    - On drawer close (Esc, outside-tap if scrim, close button), `document.body.style.overflow` restored to its prior value.
    - On forced unmount while drawer is open (parent re-renders / route change simulated in tests), `document.body.style.overflow` restored.
    - The drawer's own content area is `overflow-y: auto`; the model list scrolls inside the drawer without bleeding to the page.
14. `prefers-reduced-motion: reduce` honored: the mandatory CSS block (`@media (prefers-reduced-motion: reduce) { .mobile-model-drawer__panel { transition: none; animation: none; } }`) is present in `mobile-model-drawer.css` per §2.7. Whether or not a transition is specified, the block is required.
15. No new dependencies in `package.json`. No `@headlessui/react`, `react-aria`, `focus-trap-react`, `framer-motion`, `radix-ui`, `body-scroll-lock`, or similar. Reviewer R8 spot-check passes.
16. The drawer renders exactly **one instance** of `<ModelSelector>` while open — there is no duplicate model list elsewhere in the DOM at `<768px`. The Coder MUST NOT duplicate any `ModelSelector` markup into `MobileModelSelectorDrawer.tsx`; the drawer composes `<ModelSelector>` via its child slot.
17. The selection state (`selectedModels`) flows from `DataExplorer` → `ModelSelector` regardless of whether the inline or drawer envelope renders. Toggling a checkbox inside the drawer immediately updates `selectedModels` in `DataExplorer` and, if the user resizes to ≥768 px, the inline `ModelSelector` reflects the new selection (Architect lean §2.5.11: live update; no Apply button).
18. The existing T13 stacked-below `.explorer-layout` rule at `app.css:681–692` is **superseded cleanly** — no dead CSS describing a single-column stacked layout for the model selector remains post-T12 (§2.10). The Reviewer reads the post-T12 CSS and confirms it describes the drawer-trigger-and-overlay state without vestigial rules.
19. No forbidden vocabulary in any T12 LSB-authored source string. `mobile_model_drawer.ts` passes a Reviewer grep against the §1.5.4 forbidden list. The five strings in §2.6 are pre-cleared.
20. The Coder does NOT touch: `cdb_core/schemas.py` (R6 not triggered), `apps/dashboard/src/data/types.ts` (no data shape changes), `ModelSelector.tsx` (the inner component is unchanged — T12 wraps, does not modify), `MDSPlot.tsx`, `FreeListCompare.tsx`, `SimilarityHeatmap.tsx`, `KeyFinding.tsx`, `Footer.tsx`, `VizSwitcher.tsx`, `ArticleHeader.tsx`, `DomainPicker.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `Header.tsx`, `MobileNav.tsx`, `CiteModal.tsx`, `EmbedModal.tsx`, `DownloadBar.tsx`, `SourceAttribution.tsx`, `App.tsx`, `InspectRoot.tsx`. (Exception: if §5's "shared focus-trap helper" extraction is taken, `MobileNav.tsx` and `CiteModal.tsx` may be refactored to import from the new module — see §5 for the binding constraint.)
21. The Coder DOES touch (surgical): `DataExplorer.tsx` (add drawer state + trigger + drawer mount), `app.css` (drawer trigger styles for the `<768px` rule; supersede the stacked-below rule per §2.10), new `MobileModelSelectorDrawer.tsx`, new `mobile_model_drawer.ts` copy module, new `mobile-model-drawer.css` (token-only).
22. `DESIGN_SYSTEM.md` §8.2 has been extended by UI/UX **before** Coder dispatch with a Mobile bottom-drawer for ModelSelector subsection (analogous in structure to §8.1). The Coder's commit references the §8.2 section in the file header comment of `MobileModelSelectorDrawer.tsx` and `mobile-model-drawer.css`.
23. Bundle delta ≤ 5 KB gzipped against the post-T11 baseline. Coder reports the measured delta in the commit body. Reviewer rejects if > 5 KB.
24. The reveal cascade is unaffected: T12 adds no cascade slot. Coder verifies the cascade order at mount is unchanged from post-T11.
25. **R10 N/A:** failure to render an uncertainty pairing is not a concern here — T12 is chrome on a control panel, not a viz. Reviewer must not reject T12 on R10 grounds. Documented.
26. **CSP / R2 compliance:** no `dangerouslySetInnerHTML`, no inline `<script>`, no `eval`. Any close-button glyph is an inline SVG or `×` text node mirroring `.mobile-nav__close`.
27. The single-source-of-truth invariant for the model list: there is exactly one `<ModelSelector>` instance per render (either inline at ≥768 px OR inside the drawer at <768 px when open). The Tester asserts (a) at <768 px with drawer closed, exactly 0 `.model-selector` instances render; (b) at <768 px with drawer open, exactly 1 `.model-selector` instance renders (inside the drawer); (c) at ≥768 px, exactly 1 `.model-selector` instance renders (inline).
28. **CLAUDE.md §11 done checklist:** see §11 below for the per-criterion mapping.

---

## §4. Files to touch

**New:**
- `/opt/lsb-agent/apps/dashboard/src/components/MobileModelSelectorDrawer.tsx` — the drawer envelope component (UI/UX may rename in §8.2; if so, all references update).
- `/opt/lsb-agent/apps/dashboard/src/copy/mobile_model_drawer.ts` — copy module with the four/five §2.6 strings (the parameterized `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)` function lives here).
- `/opt/lsb-agent/apps/dashboard/src/styles/mobile-model-drawer.css` — token-only styles for trigger + drawer panel + close button + the mandatory `prefers-reduced-motion` block.

**Edited (surgical):**
- `/opt/lsb-agent/apps/dashboard/src/components/DataExplorer.tsx` — add `mobileSelectorOpen` state + `drawerTriggerRef` + focus-restore effect + trigger button render + conditional `<MobileModelSelectorDrawer>` mount. The existing `<ModelSelector>` inline render at lines 280–289 stays (just CSS-hidden at `<768px` per §2.10).
- `/opt/lsb-agent/apps/dashboard/src/styles/app.css` — supersede the stacked-below `@media (max-width: 768px) .explorer-layout { ... }` block at lines 681–692 per §2.10; the existing T13 mobile gap rules at 1042–1070 are NOT modified except possibly to add a checkbox-row `min-height: 48px` rule scoped under a `.mobile-model-drawer__body` selector if §8.2 says so (otherwise that rule lives in `mobile-model-drawer.css`).
- `/opt/lsb-agent/DESIGN_SYSTEM.md` — UI/UX adds §8.2 Mobile bottom-drawer for ModelSelector subsection **before Coder dispatch**. This is UI/UX's edit, not the Coder's. The Coder does NOT edit `DESIGN_SYSTEM.md` in the implementation commit (mirroring T11's posture, where the UI/UX agent applied the §8.1 update in the verdict commit, not the Coder's implementation commit).

**Untouched:** `ModelSelector.tsx` (CRITICAL — inner component unchanged), every other file enumerated in acceptance criterion 20, every Python package, every schema/types file, every CI workflow, `ARCHITECTURE.md` (T14 doc sweep may add a §5.3 deliverable check-off after T12 ships; T12 does not pre-update), `package.json` (zero new deps).

---

## §5. Out of scope for T12

Explicitly excluded; do not partially address:

- **The T11 mobile hamburger nav.** Different surface (site nav, not selector). Different cascade scope. Different gate routing. T12 does NOT touch `Header.tsx` or `MobileNav.tsx`.
- **Refactoring `MobileNav.tsx`'s `getFocusableElements` helper into a shared module.** Architect leans toward letting the Coder optionally extract `apps/dashboard/src/lib/focus-trap.ts` and have both `MobileNav.tsx` and `MobileModelSelectorDrawer.tsx` import from it — **ONLY IF** the extraction is a pure mechanical move (no behavior change, all existing T11 tests pass unchanged). If the refactor is anything beyond mechanical, it is its own task. Mirroring T11 §5's posture on `CiteModal`/`EmbedModal` extraction.
- **Refactoring CiteModal / EmbedModal to use the same body-scroll-lock pattern.** Out of scope. Future task. T12 introduces the pattern in one place; consolidating later is a separate workstream.
- **Modifying `ModelSelector.tsx`'s inner DOM, props, or behavior.** The component is unchanged. If T12 needs a styling tweak inside `.model-selector__row` at mobile (e.g., `min-height: 48px`), the rule lives in `mobile-model-drawer.css` scoped under `.mobile-model-drawer__body .model-selector__row` so the desktop inline rendering is unaffected.
- **Adding an "Apply" / "Done" button to the drawer.** Architect lean §2.5.11: live update on each toggle, no commit step. UI/UX may override in §8.2; if so, the plan re-routes.
- **Drag-to-dismiss / swipe-to-close gestures.** Pure click/keyboard/screen-reader for v1. Phase 6 functional-surface posture.
- **Snap points / partial-height drawer states with drag handle.** UI/UX decides drawer height in §8.2; whatever shape is chosen, it is a static height/max-height, not a draggable interactive sheet. Adding gesture-driven snap points would require new dependencies or substantial custom-touch-event code; both out of scope.
- **History.pushState / popstate handling so browser-back-button closes the drawer.** Out of scope. Drawer closes by virtue of unmount on navigation.
- **A "fix mobile cite/embed modal scroll lock" follow-up.** That is a known divergence (CiteModal does not lock body scroll) and not T12's responsibility.
- **Touching `cdb_core/schemas.py`, `data/types.ts`, or any data shape.** T12 is schema-quiet.
- **`react-router-dom` or any router framework.** Phase 6 T1 owns that.
- **A custom transition / animation curve.** UI/UX specifies in §8.2; the Coder does not invent.
- **CDA SME review of any new visible string** unless UI/UX introduces one beyond the five §2.6 standard strings.
- **Documentation sweep (T14 concern).** T12 does NOT update `ARCHITECTURE.md`, `DATA_DICTIONARY.md`, or `CLAUDE.md`. T12 DOES extend `DESIGN_SYSTEM.md` §8.2 via UI/UX agent before Coder dispatch — that is part of T12's gate, not T14.
- **Inventing a tooltip on the drawer trigger, or a model-count badge with origin-color breakdown, or any other affordance not strictly required for opening the drawer.** v1 of T12 is a trigger that opens a drawer that hosts the existing selector. Any additional affordance is a scope-creep stop condition.

---

## §6. Gate routing

```
Architect (this plan) → [Mark resolves §1.A Q1 trigger placement]
                      → UI/UX (DESIGN_SYSTEM.md §8.2 extension + plan PASS)
                      → [conditional CDA SME if UI/UX introduces non-standard prose — see §2.6]
                      → Coder → Reviewer → Tester
```

- **Architect:** this plan. On Mark's confirmation of trigger placement option (a) (default), the orchestrator dispatches UI/UX. If Mark picks (b) or (c), §2.4 / §3 acceptance criteria expand and the plan re-circulates briefly.

- **UI/UX agent: REQUIRED — gate-blocking.**
  Rationale: T12 introduces a new mobile chrome pattern (bottom-drawer overlay) not yet codified in `DESIGN_SYSTEM.md` beyond a single §8.0 bullet. Per CLAUDE.md §6 R13 and kickoff §5 ("DESIGN_SYSTEM.md §8 Mobile bottom-drawer: Update — full spec replacing the T13 deferral note"), UI/UX MUST extend `DESIGN_SYSTEM.md` with a new `§8.2 Mobile bottom-drawer for ModelSelector` subsection before the Coder begins.

  UI/UX reviews this plan on the four-question scorecard:
  1. **OWID design fidelity** — drawer shape, trigger styling, transitions match the §0 "scientific instrument" posture.
  2. **30-second journalist test** — a mobile user reaching the dashboard for the first time can find and use the model selector within 30 seconds.
  3. **Researcher reproduce-and-cite test** — N/A here (chrome, not data) — trivially PASS.
  4. **WCAG AA accessibility** — all §3 acceptance criteria 5–14.

  Per `feedback_ui_polish_scope.md` memory, UI/UX gating is reduced to accessibility floor + R10 + readability. R10 N/A. Accessibility floor is the substantive review.

  In its §8.2 extension, UI/UX codifies:
  - The §2.4 ARIA pattern (mirroring §8.1.1 — Architect lean is verbatim mirror).
  - All §2.5 visual decisions (drawer direction, height, transition, scrim, trigger styling, trigger text, open-drawer styling, close button styling, visible heading, touch target floor for checkbox rows, commit semantics, DOM mount).
  - The §2.7 reduced-motion CSS block (mandatory).
  - The §2.8 body-scroll-lock posture (mandatory; this is the key §8.1 → §8.2 divergence).
  - The §2.10 stacked-below CSS supersession plan.
  - Exact CSS tokens for each surface, all from `tokens.css` v0.4.7.
  - The component inventory line in §11 (`MobileModelSelectorDrawer.tsx` + the copy module + the CSS module).

  Verdict format: PASS / PASS-WITH-NOTES / FAIL with the four-question scorecard. Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T12-uiux-plan-verdict.md`. PASS or PASS-WITH-NOTES (notes applied) clears Coder dispatch; FAIL bounces to the Architect.

- **CDA SME: CONDITIONAL — bypass by default, dispatch only if UI/UX introduces non-standard prose.**
  Per §2.6: the five proposed strings are short, generic, accessibility-required, pre-cleared by the Architect against §1.5.4. CDA SME bypass.

  **If UI/UX's §8.2 extension introduces any LSB-authored visible or SR-only string beyond those five** (e.g., a tagline, a hint, an explanatory caption inside the drawer, or a model-count breakdown microcopy), the Architect re-routes T12 to CDA SME for a one-string verdict before Coder dispatch. CDA SME reviews on the four axes (protocol — N/A; analytical — N/A; claims — yes; audience translation — yes), short-form.

- **Coder:** implements after UI/UX PASS AND any conditional CDA SME PASS. Reads:
  - The UI/UX-extended `DESIGN_SYSTEM.md §8.2` section (binding).
  - This plan.
  - `DataExplorer.tsx`, `ModelSelector.tsx`, `MobileNav.tsx` (focus-trap precedent), `CiteModal.tsx` (focus-trap origin and dialog precedent).
  - `mobile_model_drawer.ts` (created by the Coder; CDA-SME-bound only if UI/UX added non-standard strings).

  Rule reminders for the Coder:
  - **R10 N/A** — no viz, no point estimate. Reviewer must not reject for missing CI.
  - **R12 forbidden-vocabulary spot-check** runs against `mobile_model_drawer.ts`.
  - **R8 no-new-dependency:** no new packages. If the Coder believes one is essential, pause and surface to the Architect.
  - **R13 design-system gating:** every visual decision is in `DESIGN_SYSTEM.md §8.2`; if the Coder finds something not specified, pause and route back to UI/UX (CLAUDE.md §9 pitfall #6).
  - **R6 schema:** T12 does NOT touch `cdb_core/schemas.py`; no DATA_DICTIONARY.md co-update.
  - **R14 spend gates:** trivially N/A; do not introduce cost/budget framing.
  - **One commit per task** (CLAUDE.md §8) — no bundling with T11 follow-ups, T13, or shared-helper extractions beyond the strict §5 carve-out.

- **Reviewer:** standard nine-check sweep + R8 dependency check (zero new packages in `package.json`) + R12 forbidden-vocab grep on `mobile_model_drawer.ts` + R13 design-system reference check (the file header comment on `MobileModelSelectorDrawer.tsx` and `mobile-model-drawer.css` references `DESIGN_SYSTEM.md §8.2`) + viewport-emulation sanity check (acceptance criteria 2, 3, 4, 27 — desktop view shows inline selector, mobile view shows trigger, mobile drawer-open shows drawer with selector, breakpoint exactness, single-source-of-truth) + scroll-lock check (criterion 13). Reviewer rejects if any of the 19 untouched components (acceptance criterion 20) are modified outside the strict §5 carve-out, or if `data/types.ts` is touched, or if any new dep appears in `package.json`. Verdict saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T12-reviewer-verdict.md`.

- **Tester:** standard vitest + jsdom, reusing `t11-mobile-nav.test.tsx` patterns. T12's testable surface mirrors T11's G1–G26 with model-drawer renames plus scroll-lock additions. Suggested gap labels for T12:
  - G1: trigger ARIA at rest (`aria-label`, `aria-expanded`, `aria-controls`, `aria-haspopup`).
  - G2: click trigger → drawer renders (role="dialog", aria-modal, aria-label, id matches).
  - G3: trigger ARIA state flips on open (`aria-expanded="true"`, `aria-label` flips).
  - G4: initial focus lands on close button.
  - G5: Esc closes drawer; focus returns to trigger.
  - G6: close button click closes drawer; focus returns to trigger.
  - G7: Tab from last focusable wraps to close button (focus trap forward).
  - G8: Shift+Tab from close button wraps to last focusable (focus trap backward).
  - G9: trigger hidden when drawer open (via inline `style.display: none` or display:none CSS — UI/UX confirms).
  - G10: Enter on trigger opens drawer.
  - G11: Space on trigger opens drawer.
  - G12: drawer renders exactly 1 `<ModelSelector>` instance (single-source criterion 16 + 27).
  - G13: at ≥768px viewport, drawer is NOT rendered; inline `<ModelSelector>` is.
  - G14: at <768px viewport with drawer closed, inline `<ModelSelector>` is NOT rendered; trigger button is.
  - G15: `mobile_model_drawer.ts` constants byte-identical to §8.2 spec (`.toBe()`).
  - G16: `mobile_model_drawer.ts` exports exactly the spec-listed constants; no extra strings (no scope-crept microcopy).
  - G17: `mobile_model_drawer.ts` source passes forbidden-vocab grep.
  - G18: `MobileModelSelectorDrawer.tsx` file-header comment references `DESIGN_SYSTEM.md §8.2`.
  - G19: `MobileModelSelectorDrawer.tsx` does NOT contain a duplicate `<ModelSelector>` re-implementation or a duplicate model list (criterion 16).
  - G20: `mobile-model-drawer.css` contains the `@media (prefers-reduced-motion: reduce)` block per §2.7.
  - G21: **body scroll lock test (the key §8.1 → §8.2 divergence):**
    - On drawer open, `document.body.style.overflow === 'hidden'`.
    - On drawer close (Esc), `document.body.style.overflow` restored.
    - On drawer close (close-button click), `document.body.style.overflow` restored.
    - On forced unmount while open (`root.unmount()`), `document.body.style.overflow` restored.
  - G22: selection state flows from drawer toggle to `DataExplorer.selectedModels` (toggle a checkbox inside the drawer; assert the underlying state updates).
  - G23: drawer trigger text reflects the current selected count (`"Select models (6 selected)"` initially per §3.7 v0.4.2 first-6 default; updates when selection changes).
  - G24: T13 stacked-below CSS rule has been superseded — `app.css` does NOT contain the obsolete `grid-template-areas: "viz" "selector"` at the previous location (or, if retained for a different purpose per UI/UX §2.10 decision, is documented).
  - G25: `DESIGN_SYSTEM.md` version is incremented (≥ v0.4.8); §8.2 section present.
  - G26: `prefers-reduced-motion` stub: drawer still opens/closes with motion preference enabled.

  Tester verdict saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T12-tester-verdict.md`.

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | **No** | No | Not triggered |
| `apps/dashboard/src/data/types.ts` | **No** | No | Not triggered |
| `docs/DATA_DICTIONARY.md` | No | No | Not triggered |
| `ARCHITECTURE.md` | No (T14 doc sweep may add a §5.3 check-off note after T12 ships) | No | Not triggered |
| `DESIGN_SYSTEM.md` | **Yes — UI/UX adds §8.2 BEFORE Coder dispatch** | N/A (this is the design-system update, not a data-dict co-update) | Not triggered |
| `apps/dashboard/src/components/DataExplorer.tsx` | Yes — surgical | N/A | Not triggered |
| `apps/dashboard/src/styles/app.css` | Yes — surgical (§2.10 stacked-below rule supersession) | N/A | Not triggered |
| `apps/dashboard/src/components/MobileModelSelectorDrawer.tsx` | New file | N/A | Not triggered |
| `apps/dashboard/src/copy/mobile_model_drawer.ts` | New file | N/A | Not triggered |
| `apps/dashboard/src/styles/mobile-model-drawer.css` | New file (token-only) | N/A | Not triggered |
| `package.json` / `package-lock.json` | **No** — zero new deps | N/A | Reject any new dep |

**Architect sign-off needed for schema change: none** — T12 is schema-quiet.
**Architect sign-off needed for new dependency: none — and not granted.**

---

## §8. Bundle budget watch

Post-T11 baseline (commit `bff1754` + T11 commits): ~95 KB gzipped per T11 plan §8 (Phase 5 closed at 76.25 KB; T6 / T7 / T8 / T11 added ~15–18 KB cumulatively). T12 estimate:

- `MobileModelSelectorDrawer.tsx`: ~1.5–2 KB gzipped (smaller than `MobileNav.tsx` because the drawer hosts a child rather than rendering its own list; no NAV_LINKS map).
- `mobile_model_drawer.ts` copy module: ~0.3 KB gzipped (one more parameterized function vs `mobile_nav.ts`).
- `mobile-model-drawer.css`: ~1–1.5 KB gzipped (token-only; trigger + panel + close button + scroll-lock-related rules + reduced-motion block).
- `DataExplorer.tsx` edits: ~0.3–0.5 KB gzipped (drawer state + trigger button + drawer mount).
- `app.css` edits: ~0.1 KB gzipped (§2.10 rule supersession).
- No new dependency — zero bundle cost on the dep side.

**Expected delta: ~3–4 KB gzipped.** Under the 5 KB ceiling per acceptance criterion 23.

Phase 6 cumulative budget: 400 KB cap. Post-T12: ~98–101 KB total, ~25% of cap. Headroom preserved for T1/T2/T4/T5/T13.

The Coder reports the measured delta in the commit body. Reviewer rejects if >5 KB delta vs. post-T11 baseline.

---

## §9. Dependency order

**Upstream of T12:**

- **§1.A Q1 trigger-placement decision (Mark) — HARD DEPENDENCY (decision, not code).** Plan body assumes option (a) inline. If Mark picks (b) or (c), §2.4 and §3 acceptance criteria 3–4 expand before UI/UX dispatch.
- **UI/UX §8.2 extension to DESIGN_SYSTEM.md — HARD DEPENDENCY (UI/UX action, not Coder).** Coder cannot start until §8.2 exists and UI/UX has issued a PASS verdict on this plan.
- T11 (mobile hamburger nav) — soft dependency, **already shipped** (commit `bff1754` per kickoff). The `getFocusableElements` helper in `MobileNav.tsx` is T12's reusable reference; if §5's optional shared-helper extraction is taken, T11's code is the source. T11's CSS tokens (z-index, `--color-info` focus ring, etc.) are the precedent.
- T13 (Phase 5 closeout) — soft dependency, already shipped. The stacked-below rule T12 supersedes was introduced at T13.

**Downstream of T12:**

- T1 (routing + methodology page skeleton) — independent. T12 does NOT block T1.
- T4 / T5 (DriftTracker / SimilarityHeatmap) — independent. The drawer hosts the existing `ModelSelector` whose props are unchanged.
- T8 (`AccessibilityTableToggle` / `ScreenReaderSummary`) — independent. The table toggle is per-viz, not per-selector.
- T14 (documentation sweep) — adds a §5.3 Phase 6 deliverable check-off in `ARCHITECTURE.md` after T12 ships. The `DESIGN_SYSTEM.md §8.2` section is created during T12 (UI/UX), not at T14.

**Parallel with T12:**

- T1, T2, T3, T4, T5, T7, T11 follow-ups (if any). All independent of T12. Per kickoff §2 T12 sequencing note: "Can parallelize with T3 / T4 / T5 / T7 / T11."

---

## §10. Risks and watch-items

1. **Scroll-lock side-effect bleed.** Probability: moderate. This is T12's biggest technical risk, since it is the first body-scroll-lock pattern in the codebase. The cleanup function must restore overflow on every code path: Esc, outside-tap (if scrim), close button, parent re-render, route change, unmount-while-open. The pattern in §2.8 (capture prior value in a ref; restore in `useEffect` cleanup) handles the typical cases; the Tester's G21 covers all four. Real-iOS-Safari rubber-band scroll has known edge cases the jsdom test stack doesn't reach; the Coder spot-checks before commit.
2. **Focus-trap correctness with N+1 focusable elements.** Probability: low. The drawer's focusable set is up to 1 close + 11 checkboxes + 2 action buttons = 14 elements (vs. T11's 5). The `getFocusableElements` helper handles arbitrary counts (it queries by selector + filters by `aria-hidden`); the wrap-around logic is element-count-agnostic. Tester G7 / G8 explicitly verify wrap at the boundaries.
3. **Breakpoint dead-zone bug.** Probability: low; preventable. At exactly 768 px, the show-trigger and hide-inline-selector rules must agree. CSS `max-width: 768px` is inclusive of 768. The Coder verifies viewports at 767.5 / 768 / 768.5 px each show exactly one selector surface (trigger or inline).
4. **The T13 stacked-below CSS rule left dangling.** Probability: moderate (easy to forget). Acceptance criterion 18 + §2.10 binding require the Coder to supersede the existing `app.css:681–692` block. Reviewer reads the diff and confirms no vestigial single-column layout rules remain. If the Coder retains the rule "for safety" without justification, the Reviewer rejects.
5. **Touch-target regression on checkbox rows.** Probability: moderate (easy to miss). The current `.model-selector__row` `padding: var(--space-2) var(--space-2)` produces ~16-20 px tall rows at body font size — well below the 44×44 px floor on a finger touch. UI/UX must specify the mobile-only override in §8.2 (per §2.5.10). The Tester does not directly measure pixel heights in jsdom, but a static CSS scan can verify the rule exists.
6. **Reduced-motion oversight.** Probability: moderate (easy to forget). The `@media (prefers-reduced-motion: reduce)` block is mandatory regardless of whether a transition is specified (§2.7). Acceptance criterion 14 + Tester G20 catch.
7. **`role="dialog"` swallowing inner `<nav>` semantics — N/A here.** Unlike T11 (where the dialog wrapped a `<nav>`), T12's dialog wraps `<ModelSelector>` which is not a landmark element. No landmark-conflict risk.
8. **`ModelSelector.tsx` accidentally edited.** Probability: low. Acceptance criterion 20 + Reviewer enforces "no edits to ModelSelector.tsx." The Coder must wrap, not modify. If the Coder feels the urge to tweak inner styling for mobile, that styling goes in `mobile-model-drawer.css` scoped under `.mobile-model-drawer__body .model-selector__row`, NOT in `ModelSelector.tsx`.
9. **Bundle creep from "just one more affordance."** Probability: moderate. The Coder MUST resist adding model-count breakdowns by origin, animations, swipe gestures, or anything else not in §8.2. §5 out-of-scope is exhaustive.
10. **T11 and T12 simultaneously open?** Probability: low (the user would have to open the hamburger AND tap the model-selector trigger in sequence). Both are dialogs at `z-index: 200`. If both can be open, focus traps will fight each other (each listens for `keydown` on `document`). **Binding constraint:** when the hamburger is open, the drawer trigger button is unreachable (it lives inside the explorer, which the hamburger panel covers — full-screen overlay per §8.1.4); when the drawer is open, the hamburger trigger is `aria-hidden` underneath the drawer's surface (covered by `position: fixed`). Tester does not need a dedicated test — neither trigger is reachable while the other panel is open. If the future allows both to be open (e.g., side drawers from opposite edges), this becomes a real concern.
11. **Selection state mutation during scroll-lock window.** Probability: low. If a checkbox toggle re-renders the drawer mid-scroll-lock effect, the `useEffect` cleanup will run (or not run, depending on dep array) and could double-restore overflow. The §2.8 pattern is `useEffect` keyed on `[isOpen]` — toggling a checkbox does NOT change `isOpen` and does NOT re-run the effect. Safe.
12. **The "select models (N selected)" trigger label may need pluralization** (e.g., "1 model selected" vs. "6 models selected"). UI/UX decides in §8.2 whether to pluralize. If pluralization is required, the parameterized function in `mobile_model_drawer.ts` handles it; the CDA-SME-bypass status holds as long as the strings remain in the §2.6 vocabulary.

---

## §11. CLAUDE.md §11 "done" mapping

| §11 checkbox | T12 acceptance criterion | Notes |
|---|---|---|
| All acceptance criteria met | §3 1–28 | Reviewer + Tester verdicts cover. |
| Tests pass locally (`ruff`, `mypy`, `pytest`, no-LLM-imports static check, gitleaks) | §3 1 | T12 is frontend-only; Python checks unaffected but still run. |
| Frontend tests pass locally (`npm run build && npm run test && npm run lint`) | §3 1 | Mandatory before commit. |
| Reviewer PASS / PASS-WITH-NOTES verdict, notes addressed | §6 Reviewer | Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T12-reviewer-verdict.md`. |
| UI/UX PASS / PASS-WITH-NOTES verdict, notes addressed | §6 UI/UX | Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T12-uiux-plan-verdict.md`. |
| CDA SME PASS / PASS-WITH-NOTES verdict (for methodologically significant tasks) | §6 CDA SME | Bypassed unless UI/UX introduces non-standard prose. |
| Commit message follows Conventional Commits + references task ID + verdict file paths | CLAUDE.md §8 | `feat(dashboard): T12 mobile bottom-drawer for ModelSelector` or similar; commit body links §6 verdict files. |
| No forbidden vocabulary in any committed text | §3 19 | `mobile_model_drawer.ts` grep + Reviewer R12 spot-check. |
| No new dependency without Architect sign-off | §3 15 | Architect explicitly not granting any. |
| No schema change without DATA_DICTIONARY.md co-update | §7 schema impact | T12 schema-quiet. |
| One commit (not bundled) | CLAUDE.md §8 | Coder MUST NOT bundle T11 follow-ups, T13, viz-tab work, or shared-helper extractions beyond the strict §5 carve-out. Direct-to-master per CLAUDE.md §8 (no branch+PR exception triggered — not experimental, no schema touch, no dep bump). |

---

*End of T12 plan.*
