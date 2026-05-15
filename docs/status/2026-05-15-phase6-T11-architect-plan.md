# Phase 6 T11 — Mobile hamburger nav — Architect Plan

**Date:** 2026-05-15
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T11 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T11 as "Replace the T13 `display: none` site-header nav with a real hamburger menu at `<768px`. Closes the T13 mobile-deferral note. Includes focus trap, ARIA dialog semantics, and close-on-outside-tap per WCAG").
**Status:** Awaiting Mark's direction on the T1 dependency (see §1.A below); then UI/UX dispatch (DESIGN_SYSTEM.md §8 extension required); CDA SME bypassed unless Mark wants SME review of one short SR-only label string (see §6).

T11 is a **pure frontend chrome task** — no methodology surface, no data layer, no schema touch. It replaces a Phase-5 `display: none` workaround with a real accessible disclosure widget so the four site-header links (`Explore`, `Methodology`, `Data`, `About`) remain reachable on viewports `<768px`.

---

## §0. Reading list (mandatory before Coder dispatch)

Common to T11:

1. `/opt/lsb-agent/CLAUDE.md` §6 binding rules — especially **R10** (N/A — no viz), **R12** §1.5.4 forbidden vocabulary (applies to any SR-only label or aria-label string T11 introduces), **R13** design-system gating (T11 specifically blocks on `DESIGN_SYSTEM.md` §8 extension by UI/UX), **R14** no spend gates (N/A); §7 forbidden vocabulary table; §8 workflow (one commit per task; direct-to-master); §9 pitfalls #6 (no inventing visual decisions — the hamburger icon shape, drawer-from-which-edge, transition style are all UI/UX's call), #7 forbidden vocab in any committed text.
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact, including the SR-only "open navigation menu" label proposed in §2.6), §5.3 (Phase 6 framing).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` v0.4.6 — specifically §1 tokens (colors, spacing, font tokens), §2.2 site header current spec, §7 accessibility floor (focus indicators, WCAG AA contrast, screen reader alternative), §8 mobile behavior (**currently one sentence — UI/UX MUST extend before Coder dispatch**; see §6 below), §11 component inventory (T11 adds `MobileNav.tsx` or UI/UX-named equivalent), §12.1 reveal cascade (T11 is inside Header's cascade slot — does not add a new slot).
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T11 — original scope statement; §5 "DESIGN_SYSTEM.md / new §8.x Mobile hamburger menu" line.
5. `/opt/lsb-agent/docs/status/2026-05-11-phase5-T13-uiux-verdict.md` — origin of the `display: none` site-header nav (the `Five mobile gaps resolution` table, gap 4) and the deferral note pointing forward to Phase 6 T11.
6. `/opt/lsb-agent/apps/dashboard/src/components/Header.tsx` — current site header. Contains the four NAV_LINKS array and the `<nav className="site-header__nav">` block whose `display: none` mobile rule T11 will replace.
7. `/opt/lsb-agent/apps/dashboard/src/styles/app.css` lines 138–202 (site-header styles), lines 1004–1032 (current mobile @media block — gap 4 `display: none` at line 1029–1031).
8. `/opt/lsb-agent/apps/dashboard/src/components/CiteModal.tsx` and `/opt/lsb-agent/apps/dashboard/src/components/EmbedModal.tsx` — **precedent for ARIA dialog + focus trap + Escape close + backdrop click close + return-focus-to-trigger**. T11 reuses this pattern (or extracts a shared helper if UI/UX prefers). The `getFocusableElements` helper at `CiteModal.tsx` lines 76–89 is the canonical implementation; the keyboard-event effect at lines 220–264 is the canonical focus-trap implementation; the return-focus-on-close effect at lines 277–284 is the canonical pattern.
9. `/opt/lsb-agent/apps/dashboard/src/components/ReadAsTableToggle.tsx` — **precedent for `aria-pressed` button state** (T8). T11 may follow this pattern for the hamburger trigger (rest = closed, pressed = open) — UI/UX decides between `aria-expanded` (disclosure pattern) and `aria-pressed`/`role="dialog"` (modal pattern); see §2.4.
10. `/opt/lsb-agent/apps/dashboard/src/components/VizSwitcher.tsx` — precedent for tab/keyboard interaction.
11. `/opt/lsb-agent/apps/dashboard/src/__tests__/cite-modal.test.tsx` — the test patterns for Esc-closes, focus trap, focus restoration, initial focus, backdrop click — vitest + jsdom. T11's tester reuses these patterns.
12. Memory: `feedback_ui_polish_scope.md` (Phase 6 = minimum viable functional dashboard, not polished UI; UI/UX gating reduces to accessibility floor + R10 + readability — R10 does not apply here since there is no viz), `feedback_visual_inspection.md` (N/A — T11 is chrome, not a data surface).

---

## §1. Mark's binding directives + Phase 6 framing

1. **Phase 6 minimum-viable functional surface** (memory `feedback_ui_polish_scope.md`). Plain disclosure mechanic, default tokens, no decorative animation, no microcopy work beyond what is strictly accessibility-required, no aesthetic blocking by UI/UX beyond the four-question floor (accessibility, OWID fidelity, 30-second journalist test, researcher reproduce test).
2. **WCAG AA accessibility floor is the bar** — not "great UX design," not "matches a polished mobile reference." T11 must meet WCAG 2.1 AA. The specific WCAG SCs in scope:
   - 1.4.3 Contrast (Minimum) — AA — text in the open menu meets 4.5:1; the hamburger button glyph meets 3:1 non-text contrast.
   - 1.4.11 Non-text Contrast — AA — focus indicators, the hamburger glyph, the close affordance, and any state border meet 3:1.
   - 2.1.1 Keyboard — A — every interaction reachable with a keyboard (Tab in, Esc out, Tab cycles within open menu).
   - 2.1.2 No Keyboard Trap — A — Esc, outside-tap, and the close button all release focus.
   - 2.4.3 Focus Order — A — focus order matches DOM order inside the open menu.
   - 2.4.7 Focus Visible — AA — every focusable element shows a visible focus ring.
   - 2.5.5 Target Size (Enhanced) — AAA, but Phase 6 binding for touch surfaces — every touchable target ≥ 44×44 px at `<768px`.
   - 4.1.2 Name, Role, Value — A — hamburger button has accessible name; open/close state is announced.
3. **No new dependencies.** No `@headlessui/react`, no `react-aria`, no `focus-trap-react`, no `framer-motion`, no `radix-ui`. **The Architect does NOT sign off on any new package.** The CiteModal/EmbedModal focus-trap pattern is the working precedent — reuse it. Reviewer R8 (`SECURITY_AND_HARDENING.md` §9) enforces.
4. **No methodology surface, no data surface, no schema touch.** T11 is chrome. CDA SME bypass per kickoff §2 T11; sole conditional gate is on any LSB-authored visible string (see §6).
5. **Forbidden vocabulary (§1.5.4) applies to every LSB-authored string T11 introduces** — the hamburger button's `aria-label`, the SR-only "open navigation menu" / "close navigation menu" copy, any visible heading the open menu adds. None of these are model-facing strings, so the table's forbidden phrases (`worldview`, `believes`, `thinks`, `cultural bias`, etc.) are unlikely to bite. The Reviewer's grep against `failures_findings.ts`-style copy modules still runs.
6. **`MobileNav` (or UI/UX-named equivalent) lives inside `Header.tsx` or as a sibling file in `apps/dashboard/src/components/`.** Decision deferred to §2.3 / UI/UX preference.
7. **The breakpoint is `<768px`** — matching the existing T13 mobile-gap @media rule (`app.css:1004`). The hamburger button is hidden ≥768px (desktop nav visible); the desktop nav is hidden <768px (hamburger visible). Mirror-image rules. The breakpoint must be **byte-identical** across the show-hamburger and hide-desktop-nav rules to avoid the dead-zone bug where both or neither render at exactly 767–768 px.
8. **Bundle budget: T11 adds ≤ 5 KB gzipped** against the post-T10 baseline (~91–93 KB). No new dep, plain TSX + token-only CSS. Phase 6 cumulative cap is 400 KB.

---

## §1.A. CRITICAL — T1 dependency surface and Architect recommendation (read first)

**The kickoff lists T11 as depending on T1** ("Routing decision + methodology page skeleton + nav wiring") so that the hamburger menu's link targets are real routes or anchors, not dead links. **T1 is not done.** T1 is itself blocked on Mark's Open Questions 1–2 (single-page-scroll vs. multi-route methodology). The current `Header.tsx` ships four `<a href>` links — `/`, `/methodology`, `/data`, `/about` — and three of those four already point to dead targets in production today. The desktop nav has this property; T11 only inherits it.

**Three plausible options for handling the dependency:**

| Option | What it means | Pros | Cons |
|---|---|---|---|
| (a) **Defer T11 until T1 ships.** | Don't dispatch T11 to UI/UX or Coder until T1 has a routing decision. | Cleanest. Mobile hamburger targets real anchors/routes from day one. No follow-up rework. | Blocks T11 indefinitely on Mark's Open Questions 1–2 (routing shape). Mobile users continue to have a `display: none` nav with no replacement during Phase 6. |
| (b) **Build T11 with placeholder anchors that mirror the current desktop nav.** | Hamburger renders the same four links the desktop nav already renders. If those targets become valid (T1 lands), no change to T11 — the link list is the canonical source. If they stay dead, T11 ships the same dead-link posture mobile users already have on desktop today. | Unblocks T11 now. No new architectural assumption (T11 mirrors what the header is already doing). T1 swaps targets later without touching T11. | Ships a hamburger that opens to three dead links until T1 lands. The dead-link state is already present on desktop, so this is parity, not regression — but it's still parity at "broken." |
| (c) **Build T11 structurally but `aria-hidden` / disabled until T1 wires real targets.** | Hamburger button exists, focus trap exists, ARIA exists, but the trigger is `aria-disabled="true"` and the menu does not open until T1 ships. | Clean for an automated accessibility audit (no dead links surface). | Dead UI from the user's POV. The hamburger glyph appears but does nothing. Confusing. Likely worse than option (b). |

**Architect recommendation: Option (b).**

Rationale:
1. **Parity, not regression.** The desktop nav today renders four links, three of which target dead routes. The mobile hamburger that surfaces the same four links is not introducing a new defect — it is restoring keyboard / touch reachability of an already-present state. Mark already accepted this state on desktop; T11 brings mobile up to the same baseline.
2. **T11 stays decoupled from T1.** Option (b) makes T11's link list a single-source-of-truth import from `Header.tsx`'s existing `NAV_LINKS` array (line 46). When T1 later changes those targets (e.g., from `/methodology` → `#methodology-section` or → `/methodology-page`), T11 picks up the change automatically with zero edits.
3. **Mobile users are otherwise stuck.** Post-T13, mobile users have `display: none` site-header nav — no way to reach `Methodology`, `Data`, or `About` (even when they become valid in T1+T2) without a viewport resize. Deferring T11 to wait on T1 means mobile users lose access to the methodology page once it ships, until T11 ships separately. Option (b) gets the chrome ready so that the moment T1 lands, mobile reach is instant.
4. **The T13 verdict explicitly named Phase 6 T11 as the closeout for gap 4** (`docs/status/2026-05-11-phase5-T13-uiux-verdict.md`, table line 4 + comment in `app.css:1028`). Deferring T11 past T1 leaves that gap open longer than necessary.
5. **Option (c) is worst-of-both-worlds.** It builds the structural cost of the hamburger (focus trap, ARIA, tests, CSS, breakpoint plumbing) but ships dead UI. A visible button that does nothing is a UX bug; a button that opens to four links matching desktop is a status-quo mirror.

**Counter-argument acknowledged:** Option (b) means shipping a hamburger that, until T1 lands, opens to a menu whose three of four entries 404. That is genuinely ugly. It is also exactly the state of the desktop site today. The cure is T1, not T11.

**Decision authority:** Mark. If Mark prefers (a), the plan is shelved until T1 ships. If Mark prefers (c), §2.4 below has an explicit fallback in the dialog/disclosure trade-off. **The plan body below assumes option (b)** and is structured so that switching to (a) is a "do not dispatch" decision, and switching to (c) is an isolated change to §2.4 + §2.5 + one acceptance criterion.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Placement — **`<MobileNav>` rendered inside `Header.tsx`, controlled by the same Header.**

Concrete:
- `Header.tsx` continues to own the logo + desktop `<nav className="site-header__nav">` block. A **new sibling element** — the hamburger trigger button — renders **inside** `.site-header__inner`, positioned to the right of the logo on mobile.
- A new component `MobileNav.tsx` (UI/UX may rename) renders the panel/drawer/dropdown content (depending on UI/UX's choice — see §2.4). Mounted in the DOM at all viewport widths; visibility controlled by a combination of `@media (max-width: 768px)` (visibility of the trigger button itself) and React state (visibility of the panel).
- The desktop nav `.site-header__nav` continues to hide on `<768px` via the existing rule at `app.css:1028–1031`. T11 does NOT remove or modify that rule — the desktop nav remains the source for `≥768px`, the hamburger is the source for `<768px`. **Two mirrored show/hide rules, byte-identical breakpoint.**
- The hamburger trigger button is `display: none` at `≥768px` and `display: flex` (or equivalent) at `<768px`. The Coder verifies the dead-zone case (viewport at exactly 768.5 px — desktop nav showing, hamburger hidden — and at 767.5 px — hamburger showing, desktop nav hidden) shows exactly one nav surface, never zero, never two.

**Rationale:**
- Header.tsx is the binding location of NAV_LINKS (line 46). Co-locating the mobile rendering keeps single-source-of-truth — the same `NAV_LINKS` array drives both desktop and mobile.
- Sibling-of-desktop-nav (not replacement-of) preserves the desktop nav unchanged. T11 is purely additive on desktop, purely replacement on mobile.
- DESIGN_SYSTEM.md §2.2 currently describes the desktop nav only ("Logo left, four navigation links right. No hamburger menu on desktop."). The §8 extension UI/UX writes will say "mobile collapses to logo + hamburger; nav links move into the hamburger panel." Concordant.

### §2.2. Cascade impact — **none.**

The reveal cascade slot for `Header` is slot 1 (0ms delay, `app.css:93`). T11 adds content *inside* Header — it does NOT add a new cascade slot. The MobileNav panel itself, when open, is rendered as a portal or as a positioned child of Header — it does not participate in the page-load cascade (it appears in response to user interaction, after the cascade has completed). No `nth-child` renumber.

Coder verifies the cascade order at mount remains: Header → ArticleHeader → DomainPicker → KeyFinding/DataExplorer → MethodologySummary → FailuresFindingsSection → Footer.

### §2.3. Component split — **`MobileNav.tsx` is a new file under `apps/dashboard/src/components/`.**

The trigger button stays inside `Header.tsx`. The panel/drawer content moves to `MobileNav.tsx`. Wiring:

```tsx
// Header.tsx (sketch — Coder may refactor)
const [mobileNavOpen, setMobileNavOpen] = useState(false);
const triggerRef = useRef<HTMLButtonElement>(null);

return (
  <header className="site-header" role="banner">
    <div className="site-header__inner">
      <a href="/" className="site-header__logo" …>…</a>

      {/* Desktop nav — unchanged from current Header.tsx, hides at <768px */}
      <nav className="site-header__nav" aria-label="Site navigation">…</nav>

      {/* New: hamburger trigger — hidden at ≥768px */}
      <button
        ref={triggerRef}
        type="button"
        className="site-header__hamburger"
        aria-label={MOBILE_NAV_TRIGGER_LABEL_CLOSED} // see §2.6
        aria-expanded={mobileNavOpen}
        aria-controls="mobile-nav-panel"
        onClick={() => setMobileNavOpen(true)}
      >
        {/* Glyph: UI/UX decides shape (three lines, dots, etc.) */}
        <HamburgerGlyph />
      </button>
    </div>

    {/* New: panel — UI/UX decides whether dialog, disclosure, drawer-from-which-edge */}
    <MobileNav
      isOpen={mobileNavOpen}
      onClose={() => setMobileNavOpen(false)}
      links={NAV_LINKS}
      triggerRef={triggerRef}
    />
  </header>
);
```

**The Coder may merge MobileNav into Header.tsx** if simpler. UI/UX preference governs; the Architect leaves this to UI/UX in the §8 extension. Either way, **`NAV_LINKS` is the single source of truth** — both desktop nav and MobileNav iterate over the same array (Header.tsx line 46). No duplication.

### §2.4. ARIA pattern — **UI/UX decides between disclosure and dialog. Architect's lean: dialog with modal semantics.**

This is a UI/UX call per kickoff §2 T11 ("UI/UX extends DESIGN_SYSTEM.md §8 before Coder dispatch"). The two viable patterns:

| Pattern | When appropriate | T11 implications |
|---|---|---|
| **Disclosure** (`aria-expanded` on the trigger, `aria-controls` pointing to the panel; panel is a navigation region, not a dialog) | Best when the panel does not visually obscure page content; when keyboard users should be able to Tab past the disclosure into page content. | Lighter ARIA. No `role="dialog"`. No focus trap (Tab can escape to page content). Esc still closes (recommended). Outside-tap closes (recommended). Per WAI-ARIA APG "Disclosure (Show/Hide)" pattern. |
| **Dialog** (`role="dialog"` + `aria-modal="true"` on the panel, `aria-labelledby` pointing to a heading inside the panel; backdrop overlay; focus trap inside; focus restoration on close) | Best when the panel visually obscures all or most of the page; when the open state is a modal interruption. | Heavier ARIA. Focus trap mandatory (Tab cycles inside panel only). Backdrop click closes. Esc closes. Same pattern as CiteModal/EmbedModal — reuse the helper. |

**Architect's lean: dialog with modal semantics.** Rationale:
1. The orchestrator's prompt explicitly lists "focus trap inside open menu, Esc closes, outside-tap closes, focus restored to hamburger button on close, ARIA dialog or disclosure pattern (UI/UX will decide which)" — the focus trap requirement strongly implies a dialog, since disclosure patterns conventionally do not trap focus.
2. The mobile hamburger on a viewport `<768px` typically overlays most of the screen real estate (drawer-from-top covers ~50–100% of viewport height; drawer-from-side covers ~80% of viewport width). Visual modality matches semantic modality.
3. CiteModal and EmbedModal are existing, tested precedents in this exact codebase. Reusing the focus-trap helper from `CiteModal.tsx` lines 76–89 (`getFocusableElements`) is the smallest-incremental-cost path.

**UI/UX may override** — if UI/UX prefers the disclosure pattern, the focus trap is replaced with a "Tab escapes naturally into page content" behavior; Esc and outside-tap still close. The acceptance criteria in §3 accommodate either pattern with a single conditional (Tab behavior is the only differing criterion).

**Decision authority:** UI/UX, codified in DESIGN_SYSTEM.md §8 extension before Coder dispatch.

### §2.5. Visual decisions reserved for UI/UX (Architect does NOT specify)

Per CLAUDE.md §9 pitfall #6 — the Architect does NOT invent visual decisions. The following are explicitly UI/UX's call, codified in DESIGN_SYSTEM.md §8 extension before Coder dispatch:

1. **Hamburger glyph shape.** Three lines, dots, "Menu" text label, or a hybrid. Stroke weight, line gap.
2. **Glyph-to-X transformation on open.** Is there one, or does the glyph stay the same and a separate close button appear inside the panel?
3. **Drawer direction.** Slide from top, slide from left, slide from right, full-screen overlay, dropdown beneath header.
4. **Transition / animation curve and duration.** Per §0 design philosophy "no decorative animation," likely a simple opacity + transform with short duration; UI/UX confirms or designs.
5. **Backdrop / scrim color and opacity.** CiteModal uses `rgba(0,0,0,0.5)` — UI/UX may reuse or pick differently for mobile chrome consistency.
6. **Trigger button styling.** Background, border, hover/focus/active treatments. Token-only.
7. **Open-state link styling within the panel.** Font size, weight, color, spacing between links.
8. **Touch target size beyond the 44×44 px floor.** WCAG 2.5.5 sets the floor; UI/UX may set a comfortable target (e.g., 48 px or 56 px).
9. **Whether the trigger button stays in its position when the panel is open, or hides behind the close affordance inside the panel.**
10. **Whether a visible heading ("Menu", "Navigation") appears inside the open panel** above the link list, or whether the panel relies solely on `aria-label` / `aria-labelledby` for the dialog name.

**The Coder MUST NOT invent any of these.** If the DESIGN_SYSTEM.md §8 extension is silent on a decision the Coder needs to make, the Coder pauses and routes the question back to UI/UX (CLAUDE.md §9 pitfall #6; §6 binding rule 13).

### §2.6. LSB-authored prose surface — exhaustive list for §1.5.4 + CDA-SME conditional review

T11 introduces a small number of accessibility strings. **All such strings live in `apps/dashboard/src/copy/mobile_nav.ts`** (single source of truth; precedent: `apps/dashboard/src/copy/failures_findings.ts` from T10, `apps/dashboard/src/copy/methodology_summary.ts` from T13).

| Variable | Proposed value | §1.5.4 reading | Where it surfaces |
|---|---|---|---|
| `MOBILE_NAV_TRIGGER_LABEL_CLOSED` | `"Open navigation menu"` | Descriptive, technical, no psychological attribution; no forbidden vocabulary. Standard a11y phrasing. | `aria-label` on the hamburger button when the panel is closed. |
| `MOBILE_NAV_TRIGGER_LABEL_OPEN` | `"Close navigation menu"` | Same. | `aria-label` on the hamburger button when the panel is open (if UI/UX keeps a single button for open/close); or on the close-X button inside the panel (if UI/UX uses a separate close affordance). |
| `MOBILE_NAV_PANEL_LABEL` | `"Site navigation"` | Same. Already used by the desktop nav's `aria-label` on `<nav className="site-header__nav">` (`Header.tsx` line 62). Reusing the same value preserves consistency. | `aria-label` on the `<nav>` or `aria-labelledby`/dialog-name on the open panel. |
| `MOBILE_NAV_HEADING` (optional — only if UI/UX includes a visible heading inside the panel) | `"Menu"` or `"Navigation"` — UI/UX confirms or removes | Same. | Visible `<h2>` inside the panel; `aria-labelledby` target. |

**No model-facing strings.** No forbidden-vocabulary risk on the §1.5.4 table (`worldview`, `believes`, `thinks`, `cultural bias`, `corpus lens`, etc.) — T11's strings are pure chrome.

**CDA SME conditional review:** the four strings above are short, generic, accessibility-required. **The Architect recommends bypassing CDA SME for T11** unless UI/UX flags one of these as needing CDA SME judgment (e.g., if UI/UX proposes a non-standard label like "Open menu of methodology references" or similar that would benefit from §1.5.4 review). If UI/UX adds NO new visible LSB-authored prose beyond the four standard a11y strings above, CDA SME is bypassed. If UI/UX proposes any additional visible string (e.g., a heading or descriptive text inside the panel), the Architect re-routes to CDA SME for a one-string verdict before Coder dispatch.

**Reviewer's forbidden-vocab grep** runs against `mobile_nav.ts` regardless — same posture as T10's `failures_findings.ts`.

### §2.7. Reduced-motion handling — **mandatory.**

DESIGN_SYSTEM.md §12.1 binding: "`prefers-reduced-motion: reduce` → instant reveal, no animation." T11 carries this forward to whatever transition UI/UX specifies on the open/close of the panel:

- The CSS for any open/close transition must be wrapped in `@media (prefers-reduced-motion: no-preference)` OR include an explicit `@media (prefers-reduced-motion: reduce) { .mobile-nav__panel { transition: none; animation: none; } }` override.
- The Coder verifies via DevTools "Emulate CSS prefers-reduced-motion: reduce" that the panel appears and disappears instantly without animation.

### §2.8. Scroll lock — **UI/UX decides; default is no scroll lock.**

The orchestrator's prompt says "no scroll-lock issues" as an acceptance criterion. There are two viable postures:

| Posture | Implication |
|---|---|
| **No scroll lock** | When the panel is open, the underlying page remains scrollable behind/beneath the panel. Simpler. No `document.body.style.overflow = 'hidden'` side effect. Risk: on a tall page, a user with the panel open could accidentally scroll the underlying content. |
| **Scroll lock on open** | `document.body.style.overflow = 'hidden'` on panel open; restore on close (and on unmount, in cleanup). Mirrors typical modal pattern. CiteModal does NOT implement scroll lock today (grep confirms `overflow: hidden` is only used inside `CiteModal.tsx`'s `dialogStyle` — not on body). T11 may introduce the body-lock pattern; if so, it should be in a reusable helper since CiteModal/EmbedModal may want to adopt it later. |

**Architect's lean: no scroll lock for v1.** Rationale: keeps T11's surface minimal; matches existing CiteModal posture; "no scroll-lock issues" in the orchestrator prompt is plausibly read as "don't introduce scroll-lock bugs" rather than "must implement scroll lock." UI/UX overrides if needed; if scroll lock is added, the cleanup-on-unmount handling is a binding requirement (Coder must guarantee that `body.style.overflow` is restored even if the component unmounts while open — Tester covers).

### §2.9. Where the panel mounts in the DOM — **inside Header, OR as a portal — UI/UX decides.**

Two options:

| Option | Implication |
|---|---|
| **Inline inside Header.tsx** | Simpler. Z-index needs care (panel must visually overlap subsequent page content; `.site-header { position: sticky; z-index: 100 }` is already in `app.css:138–144`). Panel inherits site-header's containing block. |
| **Portal to `document.body`** | Matches CiteModal/EmbedModal pattern. Z-index isolated from header's stacking context. More flexibility for drawer positioning. Slightly more setup. |

Architect's lean: **portal**, matching CiteModal/EmbedModal precedent and giving UI/UX freedom on drawer-from-which-edge without z-index hassles. UI/UX confirms in §8 extension.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. At viewport width ≥ 768 px: site header renders exactly as today (logo + four `.site-header__nav-link` anchors visible; no hamburger button visible).
3. At viewport width < 768 px: the four `.site-header__nav-link` anchors are NOT directly visible; a single hamburger trigger button is visible on the right side of the header.
4. The breakpoint is byte-identically `768px` on both the show-hamburger-trigger rule and the hide-desktop-nav rule (which is already at `app.css:1004`). Coder verifies no dead-zone (viewport at exactly 768 px shows exactly one nav surface).
5. Hamburger trigger button: `aria-label={MOBILE_NAV_TRIGGER_LABEL_CLOSED}` when panel is closed; `aria-expanded={true|false}` reflects panel open/close state; `aria-controls="mobile-nav-panel"` points to the panel's `id`. Either `aria-expanded` (disclosure pattern) or `aria-haspopup="dialog"` (dialog pattern) — UI/UX-decided in §2.4; either way, the trigger announces its state and target.
6. Hamburger trigger touch target: computed bounding-box width × height ≥ 44 × 44 px at `<768px` viewport.
7. Hamburger trigger keyboard activation: Enter and Space both open the panel. Pressing the trigger again while the panel is open closes it (or, if UI/UX uses a separate close button inside the panel, the trigger is unfocused while panel is open and the inside-close button is the canonical close).
8. **Panel open semantics — dialog pattern (Architect's lean per §2.4):**
   - Panel has `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to a heading (or `aria-label={MOBILE_NAV_PANEL_LABEL}` if no visible heading is rendered).
   - Initial focus lands on the first focusable element inside the panel (the close affordance, or the first nav link — UI/UX-decided).
   - Tab/Shift+Tab cycle within the panel; focus does NOT escape to page content while the panel is open.
   - Esc key closes the panel. Focus returns to the hamburger trigger.
   - Backdrop click / outside-tap closes the panel. Focus returns to the hamburger trigger.
   - The close affordance (if separate from the trigger) closes the panel. Focus returns to the hamburger trigger.
   - **Alternative — disclosure pattern (if UI/UX overrides to disclosure):** panel has `role="navigation"` or stays as a `<nav>` element; Tab cycles naturally into page content (no trap); Esc still closes and focus still restores to the trigger; outside-tap still closes. Other criteria above adapt accordingly.
9. Every focusable element inside the open panel has a visible focus indicator at ≥ 3 : 1 non-text contrast (WCAG 1.4.11). Tokens only — reuse `--color-info` outline pattern from `app.css:44–48` and `:198–202`.
10. WCAG AA contrast: every text element inside the open panel meets 4.5 : 1 (body text) against its background. The hamburger glyph meets 3 : 1 non-text contrast against its background.
11. Touch targets inside the open panel: every nav link's computed bounding box ≥ 44 × 44 px at `<768px` (WCAG 2.5.5).
12. Mobile usable at 320 px viewport width: panel content does not overflow horizontally; long link labels wrap or are sized to fit.
13. `prefers-reduced-motion: reduce` honored: any open/close transition is suppressed; panel appears and disappears instantly. Coder verifies via DevTools emulation.
14. No new dependencies in `package.json`. No `@headlessui/react`, `react-aria`, `focus-trap-react`, `framer-motion`, `radix-ui`, or similar. Reviewer R8 spot-check passes.
15. The panel renders the four `NAV_LINKS` entries from `Header.tsx`'s existing const array — single source of truth. The Coder MUST NOT duplicate the link list into `MobileNav.tsx`; either import the const or pass it as a prop.
16. **Option (b) parity check:** the four mobile links target the exact same `href` values as the desktop nav. If the desktop nav links are dead today, the mobile links are dead too (intentional — per §1.A). If T1 later updates `NAV_LINKS`, both desktop and mobile pick up the change automatically.
17. No forbidden vocabulary in any T11 LSB-authored source string. The `mobile_nav.ts` copy module passes a Reviewer grep against the §1.5.4 forbidden list. The four strings in §2.6 are pre-cleared.
18. The Coder does NOT touch `cdb_core/schemas.py` (CLAUDE.md R6 not triggered), does NOT touch `apps/dashboard/src/data/types.ts` (no data shape changes), does NOT touch `MDSPlot.tsx`, `FreeListCompare.tsx`, `SimilarityHeatmap.tsx`, `ModelSelector.tsx`, `KeyFinding.tsx`, `Footer.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ArticleHeader.tsx`, `DomainPicker.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `InspectRoot.tsx`.
19. The Coder DOES touch (surgical): `Header.tsx` (insert hamburger trigger + MobileNav wiring), `app.css` (hamburger trigger styles + the existing `@media (max-width: 768px) .site-header__nav { display: none; }` rule stays unchanged at line 1029–1031), new `MobileNav.tsx`, new `mobile_nav.ts` copy module, new `mobile-nav.css` (token-only).
20. `DESIGN_SYSTEM.md` §8 has been extended by UI/UX **before** Coder dispatch with a hamburger-spec subsection (`§8.x` per kickoff §5). The Coder's commit references the §8.x section in the file header comment of `MobileNav.tsx`.
21. Bundle delta ≤ 5 KB gzipped against the post-T10 baseline. Coder reports the measured delta in the commit body. Reviewer rejects if > 5 KB.
22. The reveal cascade is unaffected: T11 adds content inside Header (cascade slot 1), not a new cascade slot. Coder verifies cascade order at mount remains Header → ArticleHeader → DomainPicker → KeyFinding/DataExplorer → MethodologySummary → FailuresFindingsSection → Footer.
23. **R10 N/A:** failure to render an uncertainty pairing is not a concern here — the hamburger is chrome with no point estimate. The Reviewer must not reject T11 on R10 grounds. Documented for the record.
24. **CSP / R2 compliance:** no `dangerouslySetInnerHTML`, no inline `<script>`, no `eval`. The hamburger glyph is an inline `<svg>` (matching the `LogoGlyph` pattern in `Header.tsx` lines 12–39). React text nodes for every label.
25. **CLAUDE.md §11 done checklist:** see §11 below for the per-criterion mapping.

---

## §4. Files to touch

**New:**
- `/opt/lsb-agent/apps/dashboard/src/components/MobileNav.tsx` — the panel component (or fold into `Header.tsx` if UI/UX prefers; Coder's call per §2.3 once UI/UX §8 extension lands).
- `/opt/lsb-agent/apps/dashboard/src/copy/mobile_nav.ts` — single source for the four LSB-authored a11y strings (§2.6).
- `/opt/lsb-agent/apps/dashboard/src/styles/mobile-nav.css` — token-only styles for the trigger + panel.

**Edited (surgical):**
- `/opt/lsb-agent/apps/dashboard/src/components/Header.tsx` — add hamburger trigger button + state + MobileNav wiring.
- `/opt/lsb-agent/apps/dashboard/src/styles/app.css` — site-header rule additions for hamburger trigger; the existing `@media (max-width: 768px) .site-header__nav { display: none; }` at lines 1029–1031 is preserved unchanged. The comment at line 1028 ("Phase 6 adds hamburger") gets updated to reference T11 + the §8.x DESIGN_SYSTEM.md section.
- `/opt/lsb-agent/DESIGN_SYSTEM.md` — UI/UX extends §8 with a hamburger-spec subsection **before Coder dispatch**. This is UI/UX's edit, not the Coder's.

**Untouched:** `cdb_core/schemas.py`, `apps/dashboard/src/data/types.ts`, every component file enumerated in acceptance criterion 18, every Python package in `packages/`, every fixture, every CI workflow, `ARCHITECTURE.md` (T14 doc sweep may add a §5.3 Phase 6 deliverable check-off after T11 ships; T11 does not pre-update).

---

## §5. Out of scope for T11

Explicitly excluded; do not partially address:

- **The T12 mobile bottom-drawer for ModelSelector.** Different surface (selector panel, not site nav). Different cascade scope. Different gate routing. T11 does NOT touch `ModelSelector.tsx` or `DataExplorer.tsx`.
- **T1's routing decision.** T11 does NOT pick `react-router-dom` vs anchor-scroll vs separate-Vite-entry. The hamburger renders whatever `href` values are in `NAV_LINKS`; T1 changes those values later.
- **T1's methodology page skeleton.** T11 does NOT create the methodology page route or anchor. The hamburger's `/methodology` link continues to target wherever the desktop nav's `/methodology` link targets — dead today, alive after T1.
- **Updating `NAV_LINKS` to add or remove items.** T11 mirrors the current four-link list. If Mark wants to add a fifth link or remove one, that is a separate Architect decision (kickoff §3 Open Question — not bonus, but unraised here).
- **A theme toggle, language switcher, search affordance, or any other non-nav chrome inside the hamburger.** v1 of T11 is nav links only. Adding any of those is a scope-creep stop condition (CLAUDE.md §8).
- **A separate close-X icon font.** Inline SVG (matching the LogoGlyph pattern) is the only acceptable rendering. No `@material-ui/icons`, no `react-icons`, no external icon imports.
- **Touching the desktop nav.** The desktop nav's visual treatment, link order, and styling are unchanged.
- **Touching `CiteModal.tsx` or `EmbedModal.tsx`.** T11 may reuse the focus-trap pattern by copying the helper into a shared module (e.g., `apps/dashboard/src/lib/focus-trap.ts`) — at Coder's discretion. If a shared helper is extracted, the Coder MAY refactor CiteModal/EmbedModal to use it in the same commit ONLY IF the refactor is a pure mechanical extraction (no behavior change, all existing tests pass unchanged). If the refactor is anything beyond mechanical, it is its own task and is rejected at review (CLAUDE.md §8 one-commit-per-task; no bundling).
- **A "skip to content" link.** Useful accessibility affordance, but its own concern; out of scope here. Future task.
- **Touch gestures (swipe to open, swipe to close).** Pure click/keyboard/screen-reader for v1. Phase 6 functional-surface posture.
- **Browser-back-button-closes-panel semantics.** Out of scope; would require a history.pushState or popstate handler that T11 does not introduce. If a user navigates back while the panel is open, the panel closes by virtue of unmount; no special handling needed.
- **Page scroll lock by default** (per §2.8). UI/UX may add it; Architect's default is no scroll lock.
- **`react-router-dom` or any router framework.** Phase 6 T1 owns that decision.
- **A custom transition / animation curve beyond the Phase-6 minimum.** UI/UX specifies; the Coder does not invent.
- **CDA SME re-review of any new visible string** unless UI/UX introduces one beyond the four §2.6 standard a11y strings.
- **Documentation sweep** (T14 concern). T11 does NOT update `ARCHITECTURE.md`, `DATA_DICTIONARY.md`, or `CLAUDE.md`. T11 DOES extend `DESIGN_SYSTEM.md` §8 via UI/UX agent, before Coder dispatch — that is part of T11's gate, not T14.

---

## §6. Gate routing

```
Architect (this plan) → [Mark resolves §1.A T1-dependency option (a/b/c)]
                      → UI/UX (DESIGN_SYSTEM.md §8.x extension + plan PASS)
                      → [conditional CDA SME if UI/UX introduces non-standard prose — see §2.6]
                      → Coder → Reviewer → Tester
```

- **Architect:** this plan. On Mark's confirmation of option (b) (or override to (a)/(c)), the orchestrator dispatches the next gate.

- **UI/UX agent: REQUIRED — gate-blocking.**
  Rationale: T11 is purely chrome but introduces a new mobile chrome pattern not yet codified in `DESIGN_SYSTEM.md`. Per CLAUDE.md §6 R13 and kickoff §2 T11 ("DESIGN_SYSTEM.md §8 needs a hamburger spec section — currently only one sentence; UI/UX extends it before Coder dispatch"), UI/UX MUST extend `DESIGN_SYSTEM.md` §8 with a `§8.x Mobile hamburger menu` subsection before the Coder begins.

  UI/UX reviews this plan on the four-question scorecard:
  1. **OWID design fidelity** — the hamburger glyph, drawer style, transitions match the OWID-style "scientific instrument, not a product" §0 posture.
  2. **30-second journalist test** — a mobile user reaching the dashboard for the first time can find the nav within 30 seconds.
  3. **Researcher reproduce-and-cite test** — N/A here (chrome, not data) — trivially PASS.
  4. **WCAG AA accessibility** — all the §3 acceptance criteria 5–13.

  Per `feedback_ui_polish_scope.md` memory, the UI/UX agent's gating is reduced to accessibility floor + R10 + readability. R10 is N/A here. Accessibility floor is the substantive review.

  In its §8.x extension, UI/UX codifies:
  - The §2.4 ARIA pattern choice (dialog vs disclosure).
  - The §2.5 visual decisions (glyph shape, drawer direction, transition style, scrim opacity, trigger styling, open-panel styling, touch target size, header presence, panel-mount-location).
  - The §2.8 scroll-lock posture.
  - The §2.9 portal-vs-inline choice.
  - The exact CSS tokens to use for each surface (color, spacing, font tokens — all from `tokens.css` v0.4.6).
  - Component inventory line in DESIGN_SYSTEM.md §11 (`MobileNav.tsx`).

  Verdict format: PASS / PASS-WITH-NOTES / FAIL with the four-question scorecard. Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-uiux-plan-verdict.md`. PASS or PASS-WITH-NOTES (notes applied) clears Coder dispatch; FAIL bounces to the Architect for re-plan.

- **CDA SME: CONDITIONAL — bypass by default, dispatch only if UI/UX introduces non-standard prose.**
  Per §2.6: the four standard a11y strings (`"Open navigation menu"`, `"Close navigation menu"`, `"Site navigation"`, and an optional `"Menu"`/`"Navigation"` heading) are pre-cleared by the Architect against §1.5.4. They are generic accessibility phrasing with zero psychological-attribution risk. CDA SME bypass.

  **If UI/UX's §8.x extension introduces any LSB-authored visible or SR-only string beyond those four** (e.g., a custom heading, a descriptive tagline inside the panel, a "Methodology" sub-section heading), the Architect re-routes T11 to CDA SME for a one-string verdict before Coder dispatch. CDA SME reviews on the four axes (protocol validity — N/A; analytical validity — N/A; claims validity — yes; audience translation — yes), short-form.

- **Coder:** implements after UI/UX PASS (or PASS-WITH-NOTES with applied notes) AND any conditional CDA SME PASS. The Coder reads:
  - The UI/UX-extended DESIGN_SYSTEM.md §8.x section (binding).
  - This plan.
  - `Header.tsx`, `CiteModal.tsx` (for the focus-trap helper pattern), `ReadAsTableToggle.tsx` (for the `aria-pressed` precedent if disclosure pattern chosen).
  - `mobile_nav.ts` (created by the Coder; CDA-SME-bound only if UI/UX added non-standard strings).

  Rule reminders for the Coder (additionally):
  - **R10 N/A** — no viz, no point estimate. Reviewer must not reject for missing CI.
  - **R12 forbidden-vocabulary spot-check** runs against `mobile_nav.ts`.
  - **R8 no-new-dependency:** no `@headlessui/react`, `react-aria`, `focus-trap-react`, `framer-motion`, `radix-ui`, or similar. The Architect is NOT signing off on any new package. If the Coder believes a new dep is essential, the Coder pauses and surfaces back to the Architect.
  - **R13 design-system gating** — every visual decision is in DESIGN_SYSTEM.md §8.x; if the Coder finds something not specified, the Coder pauses and routes back to UI/UX (CLAUDE.md §9 pitfall #6).
  - **R6 schema:** T11 does NOT touch `cdb_core/schemas.py`; no DATA_DICTIONARY.md co-update needed.
  - **R14 spend gates:** trivially N/A; do not introduce any cost, budget, max_tokens, rate_limit, or spend-cap framing in any string or comment.
  - **One commit per task** (CLAUDE.md §8) — no bundling with T12 (mobile bottom-drawer) even though both are mobile chrome.

- **Reviewer:** standard nine-check sweep + R8 dependency check (zero new packages in `package.json`) + R12 forbidden-vocab grep on `mobile_nav.ts` + R13 design-system reference check (the file header comment on `MobileNav.tsx` references DESIGN_SYSTEM.md §8.x) + a viewport-emulation sanity check (acceptance criteria 2, 3, 4 — desktop view shows nav, mobile view shows hamburger, breakpoint exactness). Reviewer rejects if any of the 12 untouched components (acceptance criterion 18) are modified, or if `data/types.ts` is touched, or if any new dep appears in `package.json`. Verdict saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-reviewer-verdict.md`.

- **Tester:** standard vitest + jsdom. T11's testable surface (reusing the cite-modal.test.tsx patterns):
  - Hamburger button renders at `<768px` viewport (use `Object.defineProperty(window, 'innerWidth', ...)` or matchMedia mock).
  - Hamburger button does NOT render at `≥768px` viewport.
  - Click hamburger → panel opens (asserted by panel element appearing in DOM or visibility change).
  - `aria-expanded` toggles correctly.
  - Esc key closes the panel; focus returns to the hamburger trigger.
  - Backdrop click closes the panel (if dialog pattern) — assert focus restoration.
  - Tab/Shift+Tab cycles within panel (if dialog pattern with focus trap) — assert that the last-element + Tab wraps to the first element and first-element + Shift+Tab wraps to the last.
  - Enter and Space on the hamburger both open the panel.
  - The four nav links render with the exact `href` and `label` values from `NAV_LINKS`.
  - `mobile_nav.ts` exports the four §2.6 strings byte-identical to the spec.
  - `prefers-reduced-motion: reduce` test: stub `matchMedia` and assert the transition is suppressed (computed style assertion is brittle; the Coder may instead unit-test the CSS class assignment or a transition-disable hook).
  - No real network fetches; the test is fully isolated chrome behavior (CLAUDE.md R9 — N/A by default, no API calls in this surface).

  Tester verdict saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-tester-verdict.md`.

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | **No** | No | Not triggered |
| `apps/dashboard/src/data/types.ts` | **No** | No | Not triggered |
| `docs/DATA_DICTIONARY.md` | No | No | Not triggered |
| `ARCHITECTURE.md` | No (T14 doc sweep may add a §5.3 check-off note after T11 ships) | No | Not triggered |
| `DESIGN_SYSTEM.md` | **Yes — UI/UX adds §8.x Mobile hamburger menu subsection BEFORE Coder dispatch** | N/A (this is the design-system update, not a data-dict co-update) | Not triggered |
| `apps/dashboard/src/components/Header.tsx` | Yes — surgical | N/A | Not triggered |
| `apps/dashboard/src/styles/app.css` | Yes — surgical | N/A | Not triggered |
| `apps/dashboard/src/components/MobileNav.tsx` | New file | N/A | Not triggered |
| `apps/dashboard/src/copy/mobile_nav.ts` | New file | N/A | Not triggered |
| `apps/dashboard/src/styles/mobile-nav.css` | New file (token-only) | N/A | Not triggered |
| `package.json` / `package-lock.json` | **No** — zero new deps | N/A | Reject any new dep |

**Architect sign-off needed for schema change: none** — T11 is schema-quiet.
**Architect sign-off needed for new dependency: none — and not granted.**

---

## §8. Bundle budget watch

Post-T10 baseline (commit `bff1754`): ~91–93 KB gzipped (extrapolated from kickoff §8 estimate and T8 closeout). T11 estimate:

- `MobileNav.tsx`: ~2 KB gzipped of TSX after tree-shaking.
- `mobile_nav.ts` copy module: ~0.2 KB gzipped.
- `mobile-nav.css`: ~1–1.5 KB gzipped (token-only; no large declarations).
- `Header.tsx` edits: ~0.3 KB gzipped (hamburger trigger inline SVG + handler).
- `app.css` edits: ~0.1 KB gzipped (hamburger trigger media-query rule).
- No new dependency in `package.json` — zero bundle cost on the dep side.

**Expected delta: ~3–4 KB gzipped.** Under the 5 KB ceiling per acceptance criterion 21.

Phase 6 cumulative budget: 400 KB cap. Post-T11: ~94–97 KB total, ~24% of cap. Headroom preserved for T1/T2/T4/T5/T12/T13.

The Coder reports the measured delta in the commit body. Reviewer rejects if > 5 KB delta vs. post-T10 baseline.

---

## §9. Dependency order

**Upstream of T11:**

- **§1.A T1-dependency decision (Mark) — HARD DEPENDENCY (decision, not code).** Mark must resolve option (a)/(b)/(c) before UI/UX is dispatched. The plan body assumes (b). If Mark picks (a), T11 is shelved. If Mark picks (c), §2.4 / §2.5 / acceptance criterion 8 are adjusted before UI/UX dispatch.
- **UI/UX §8.x extension to DESIGN_SYSTEM.md — HARD DEPENDENCY (UI/UX action, not Coder).** Coder cannot start until §8.x exists and UI/UX has issued a PASS verdict on this plan.
- T13 (Phase 5 closeout) — soft dependency, already shipped. The `display: none .site-header__nav` rule that T11 replaces is from T13.

**Downstream of T11:**

- T1 (routing + methodology page skeleton) — when T1 changes `NAV_LINKS` to point to real anchors or routes, T11 picks up the change automatically (no edits). T11 does NOT block T1.
- T12 (mobile bottom-drawer for ModelSelector) — independent. Can ship in parallel.
- T14 (documentation sweep) — adds a §5.3 Phase 6 deliverable check-off in `ARCHITECTURE.md` after T11 ships. The DESIGN_SYSTEM.md §8.x section is created during T11 (UI/UX), not at T14.

**Parallel with T11:**

- T1, T2, T3, T4, T5, T12. All independent of T11.

---

## §10. Risks and watch-items

1. **Dead links until T1 ships** (per §1.A option (b)). Probability: certainty. Three of four hamburger links 404 until T1 wires the methodology / data / about routes or anchors. Mitigation: this is parity with the existing desktop state, not a regression. T11 acceptance criterion 16 documents the parity. If Mark wants to mask this (e.g., disable the three dead links until T1), that is an option (c)-style override and triggers a re-plan.

2. **Breakpoint dead-zone bug.** Probability: low; preventable. At exactly 768 px, the show-hamburger and hide-desktop-nav rules must agree on the threshold. CSS `max-width: 768px` is inclusive of 768. The hamburger's `display: flex` should be inside `@media (max-width: 768px)` and the desktop nav's `display: none` should be inside the same `@media (max-width: 768px)` block. Coder verifies viewport at 767.5 / 768 / 768.5 px shows exactly one nav surface.

3. **Focus trap incompatibility with native browser shortcuts.** Probability: low. Some browsers' Tab handling on mobile keyboards (especially iOS Safari with external Bluetooth keyboards) interacts oddly with focus-trap loops. Tester verifies in vitest + jsdom (synthetic), Coder spot-checks on a real iOS Safari and Android Chrome before committing.

4. **Scroll lock side-effect bleed.** Probability: low if §2.8 default (no scroll lock) is kept. If UI/UX adds scroll lock, the Coder must ensure `document.body.style.overflow` is restored on every code path that closes the panel (Esc, outside-tap, close button, unmount) and that cleanup runs even if the component unmounts in an unexpected state (e.g., parent re-renders during open state).

5. **Reduced-motion oversight.** Probability: moderate (easy to forget). The DESIGN_SYSTEM.md §12.1 reduced-motion binding is mandatory; the Coder must explicitly handle it in the CSS, not rely on the default. Acceptance criterion 13 catches this.

6. **`role="dialog"` vs `<nav>` semantics conflict.** Probability: moderate. If UI/UX picks the dialog pattern (Architect lean), the panel cannot also be a `<nav>` element with `role="navigation"` — `role="dialog"` overrides. Internal structure: `<div role="dialog"><nav>...links...</nav></div>` is acceptable; the dialog has the modal semantics, the inner `<nav>` provides the navigation landmark. UI/UX confirms the structure in §8.x.

7. **`NAV_LINKS` drift.** Probability: low. If a future PR (T1 most likely) adds a fifth nav link to `NAV_LINKS`, T11 picks it up automatically only if it imports / receives the const. Acceptance criterion 15 binds this to a single source of truth. Reviewer R12 spot-checks that no duplicate link array exists in `MobileNav.tsx`.

8. **The "dead UI" perception risk** (option (b)). If a journalist visits the dashboard on mobile during the T11 → T1 gap and taps the hamburger, they see a panel whose three of four entries 404. That is a real user-facing posture. Mitigation: T11 acceptance criterion 16 makes it intentional and traceable; the four-question journalist test still passes (the user reaches the nav surface within 30 seconds and can return to the Explore link, which works). The dead-link state is a T1 issue, not a T11 issue.

9. **Bundle creep from "just one more affordance."** Probability: moderate (analogous to T10). The Coder MUST resist adding theme toggles, language switchers, search inputs, or any non-nav chrome inside the hamburger. T11 is a viewport-narrow proxy for the desktop nav — nothing more. §5 out-of-scope list is exhaustive.

10. **Accidental regression on the desktop nav.** Probability: low. T11 is purely additive on desktop (new hamburger button is `display: none` at ≥768px; existing `.site-header__nav` rules untouched). Reviewer spot-checks via the existing tests that the desktop nav renders identically pre- and post-T11.

---

## §11. CLAUDE.md §11 "done" mapping

| §11 checkbox | T11 acceptance criterion | Notes |
|---|---|---|
| All acceptance criteria met | §3 1–25 | Reviewer + Tester verdicts cover. |
| Tests pass locally (`ruff`, `mypy`, `pytest`, no-LLM-imports static check, gitleaks) | §3 1 | T11 is frontend-only; Python checks unaffected but still run as per CLAUDE.md §8. |
| Frontend tests pass locally (`npm run build && npm run test && npm run lint`) | §3 1 | Mandatory before commit. |
| Reviewer PASS / PASS-WITH-NOTES verdict, notes addressed | §6 Reviewer | Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-reviewer-verdict.md`. |
| UI/UX PASS / PASS-WITH-NOTES verdict, notes addressed | §6 UI/UX | Saved to `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-uiux-plan-verdict.md`. |
| CDA SME PASS / PASS-WITH-NOTES verdict (for methodologically significant tasks) | §6 CDA SME | Bypassed unless UI/UX introduces non-standard prose (§2.6). |
| Commit message follows Conventional Commits + references task ID + verdict file paths | CLAUDE.md §8 | `feat(dashboard): T11 mobile hamburger nav` or similar; commit body links to the §6 verdict files. |
| No forbidden vocabulary in any committed text | §3 17 | `mobile_nav.ts` grep + Reviewer R12 spot-check. |
| No new dependency without Architect sign-off | §3 14 | Architect explicitly not granting any. |
| No schema change without DATA_DICTIONARY.md co-update | §7 schema impact | T11 schema-quiet. |
| One commit (not bundled) | CLAUDE.md §8 | Coder MUST NOT bundle T12 even though both are mobile chrome. Direct-to-master per CLAUDE.md §8 (no branch+PR exception triggered — not experimental, no schema touch, no dep bump). |

---

*End of T11 plan.*
