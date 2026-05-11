# UI/UX Per-Commit Verdict — Phase 5 T12 (CiteModal + EmbedModal)

**Filed:** 2026-05-11
**Reviewer:** UI/UX agent (Sonnet)
**Commit reviewed:** `71f343c` — "feat(dashboard): T12 CiteModal + EmbedModal with embed=true chrome-hide"
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** v0.4.3 (no update required for T12)

---

## VERDICT: FAIL → PASS-WITH-NOTES (after F-T12-1 fix applied alongside this verdict)

| Criterion | Result (post-fix) |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS-WITH-NOTES (was FAIL on F-T12-1; corrected) |

**DESIGN_SYSTEM.md update:** not required. The "Copied!" state-feedback pattern was already established by previous DownloadBar tasks (T10 permalink, T11 PNG); this is a correct-application fix, not a new visual decision.

T12 was originally FAIL on F-T12-1 (WCAG 4.1.3 — copy success state not announced to screen readers). Correction applied alongside this verdict. T12 then proceeds to Reviewer + Tester.

**Note for Reviewer:** the `_headers` CSP relaxation (`frame-ancestors 'none'` → `frame-ancestors *`) is out of UI/UX scope. The Reviewer must perform the §9 R12 security review. UI/UX flags one related concern in the Carry-forward section.

---

## F-T12-1 — "Copied!" state not announced to screen readers (BLOCKING — fixed alongside this verdict)

**Issue:** In both modals, the copy button has a static `aria-label`. When the user activates copy, the button's inner text changes from "Copy" to "✓ Copied!" — but `aria-label` takes precedence over button text content, so screen readers continue to announce "Copy APA citation" / "Copy embed code" throughout. The state change is invisible to assistive technology. WCAG 4.1.3 (Status Messages) failure: a success notification meaningful to sighted users must be programmatically determinable without requiring focus.

**Fix applied (alongside this verdict):**

In `apps/dashboard/src/components/CiteModal.tsx` line 401:
```tsx
aria-label={
  copied
    ? `${tab.label} citation copied`
    : `Copy ${tab.label} citation`
}
```

In `apps/dashboard/src/components/EmbedModal.tsx` line 314:
```tsx
aria-label={copied ? "Embed code copied" : "Copy embed code"}
```

---

## F-T12-2 — `yearFromIso` fallback uses local-time `getFullYear()` (PASS-WITH-NOTES, non-blocking)

**Issue:** `citation.ts` `yearFromIso` fallback uses `new Date().getFullYear()` (local time zone). For a server-rendered or timezone-edge case where `generatedAt` is malformed, the fallback year could disagree with UTC year for a user in UTC+14 on December 31. Cosmetic in an edge case that should not occur in production (all real `generatedAt` strings are valid ISO-8601 and the regex extracts the year before fallback).

**Disposition:** Non-blocking. Note carried forward.

---

## Passing checks

**§1.6 naming compliance:** All four citation formats include both "Cognitive Structure Lab" and "LSB" per ARCHITECTURE.md §1.6 binding implication 4.

- **APA:** `Cognitive Structure Lab. (YYYY). LSB: {Domain} domain MDS [Data set]. ...`
- **MLA:** `Cognitive Structure Lab. "LSB: {Domain} domain MDS." Cognitive Structure Lab, ...`
- **Chicago:** `Cognitive Structure Lab. YYYY. "LSB: {Domain} domain MDS." Cognitive Structure Lab. ...`
- **BibTeX:** `author = {{Cognitive Structure Lab}}, title = {LSB: {Domain} domain MDS}, ...`

**BibTeX details:** Double-braces on author (`{{...}}`) prevent BibTeX from abbreviating the institution name — correct. Key `lsb_{domain}_{year}` is lowercase, slug-only, stable.

**Year extraction:** `yearFromIso` regex `/^(\d{4})/` extracts year from ISO-8601 string directly — correct for well-formed input.

**MLA "Accessed" date:** `accessDate()` produces `"DD Month YYYY"` with full month names. Present at `buildMla`.

**Tab pattern ARIA:** Full pattern present — `role="tablist"` with `aria-label="Citation formats"`, each tab has `role="tab"`, `aria-selected`, `aria-controls`; each panel has `role="tabpanel"`, `aria-labelledby`, and `hidden` attribute (not CSS `display:none`) for inactive panels.

**Arrow-key tab navigation:** `ArrowRight` / `ArrowLeft` cycle through tabs with wrap — follows ARIA Authoring Practices Guide roving tabindex pattern.

**Modal ARIA:** Both modals carry `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to the heading's `id`.

**Escape closes:** Both modals handle `e.key === "Escape"` via document keydown listener.

**Backdrop click closes:** Both modals check `e.target === e.currentTarget` on the backdrop div's `onClick` before calling `onClose()`.

**Focus trap:** Both modals implement `getFocusableElements()` scanning focusable descendants. Tab/Shift+Tab intercepted to cycle within modal.

**Initial focus:** Sensible first element. CiteModal focuses the first tab button (APA); EmbedModal focuses the close button.

**Focus return on close:** Both modals track `prevIsOpen` and call `triggerRef?.current?.focus()` when `isOpen` transitions true → false. `DataExplorer.tsx` correctly wires `citeTriggerRef` / `embedTriggerRef` to the DownloadBar trigger buttons.

**New DownloadBar button focus-visible:** `app.css` includes `.download-bar__cite-btn:focus-visible` and `.download-bar__embed-btn:focus-visible` rules in the established T10/T11 pattern block.

**Embed mode detection:** `App.tsx` reads `new URLSearchParams(window.location.search).get("embed") === "true"` on mount. Embed mode renders only `DataExplorer` with `isEmbed={true}`. DownloadBar hides Permalink and Embed buttons when `isEmbed=true`; CSV and PNG remain visible per §12.5.

**EmbedModal snippet includes current model selection:** `buildEmbedSnippet` encodes `models` as a URL param from `selectedModels`. The embedded view receives the same model selection.

**Snippet visual treatment:** `<pre><code>` with `var(--color-surface)` background, monospace font, 1px border — minimal, editorial. No decorative gradients or animations.

**Embed iframe defaults:** 900×700, `frameborder="0"`, `loading="lazy"` — reasonable.

**CC-BY attribution note:** "Embed code permitted by CC-BY 4.0; please retain the LSB attribution." Meets requirement.

**Modal backdrop:** `rgba(0,0,0,0.5)` — not a gradient.

**Modal max-width:** CiteModal 560px, EmbedModal 580px — fit comfortably on 1366px desktop.

**Design-system tokens:** Both modals use tokens throughout — no hardcoded colors, font sizes, or spacing.

**No decorative animation:** Beyond 150ms `background-color` hover on buttons (consistent with existing pattern), neither modal introduces animation or transitions.

**Forbidden vocabulary:** Zero matches for `believes`, `thinks`, `worldview`, `recognizes`, `interprets`, `perceives`, `comprehends` in `CiteModal.tsx`, `EmbedModal.tsx`, or `citation.ts`.

**30-second journalist test:** Cite button discoverable next to CSV/PNG in DownloadBar. Modal defaults to APA (journalist-friendly). Copy button immediately visible. Paste-ready output in all four formats.

**Researcher cite path:** All four formats include domain, analysis_version (in BibTeX `note`), year, and URL. BibTeX `note` records `Analysis version {X}; models: {a,b,c}` for full data provenance.

---

## Required before Reviewer passes T12

Correction applied alongside this verdict:

1. `apps/dashboard/src/components/CiteModal.tsx` line 401 — dynamic `aria-label` for copied state.
2. `apps/dashboard/src/components/EmbedModal.tsx` line 314 — dynamic `aria-label` for copied state.

Reviewer verifies build remains green after these fixes.

---

## Carry-forward to T13 and Reviewer

- **F-T12-2** (non-blocking): `yearFromIso` fallback could use `getUTCFullYear()`. Opportunistic cleanup.
- **Reviewer attention — `_headers` CSP**: T12 relaxes `frame-ancestors 'none'` → `frame-ancestors *`. Per Reviewer rule R12 (no `_headers` modification without security review), the Reviewer should audit the security justification in the commit body AND verify whether the legacy `X-Frame-Options: DENY` header is still present in `_headers` — if so, it will override the relaxed `frame-ancestors` in older browsers and acceptance criterion 3 (iframe embed working) will fail in practice. Out of UI/UX scope; flagging for Reviewer.
- **T13 gate**: `MethodologySummary` prose requires CDA SME review in addition to UI/UX. T12 introduces no new methodology claims.

---

*End of T12 per-commit UI/UX verdict. Posted to `#lsb-ui-ux`. Reviewer + Tester proceed after this commit.*
