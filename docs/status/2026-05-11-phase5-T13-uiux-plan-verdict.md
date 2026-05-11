---
filed: 2026-05-11
reviewer: UI/UX agent (Sonnet)
plan_reviewed: docs/status/2026-05-09-phase5-architect-plan.md §4 T13
cda_sme_upstream: PASS-WITH-NOTES at docs/status/2026-05-11-phase5-T13-cda-sme-verdict.md
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.4 (updated alongside this verdict — §12.7 added)
verdict: PASS-WITH-NOTES
---
```

# UI/UX Plan-Level Verdict — Phase 5 T13

**VERDICT: PASS-WITH-NOTES**

| Criterion | Result |
|---|---|
| 1. OWID design fidelity | PASS-WITH-NOTES |
| 2. 30-second journalist | PASS |
| 3. Researcher cite path | PASS |
| 4. WCAG AA | PASS-WITH-NOTES |

T13 is approved for Coder dispatch with the binding corrections in the F-T13 findings table below and the DESIGN_SYSTEM.md v0.4.4 update (§12.7). The CDA SME upstream PASS-WITH-NOTES prose is fixed and not reviewed here; this verdict covers rendering, integration, mobile, and accessibility only.

---

## 1. Four-criterion scorecard

### 1. OWID design fidelity — PASS-WITH-NOTES

The plan places MethodologySummary below the DataExplorer per §2.1, at max-width 680px. This is correct. The tagline renders as a separate paragraph above the body paragraph, which is correct per CDA SME carry-forward note 2. The footnote uses `--color-text-caption` per T10 precedent, which is correct.

Two PASS-WITH-NOTES items:

**F-T13-1 (BLOCKING):** The reveal cascade in `app.css` defines stagger delays only through `:nth-child(5)` (positions 1–5 at 0ms, 80ms, 160ms, 240ms, 320ms). The current cascade items are: (1) Header, (2) ArticleHeader, (3) DomainPicker, (4) content-area block, (5) Footer. When MethodologySummary is inserted as a new `reveal-cascade-item` wrapping element before Footer, it becomes child 5 and Footer becomes child 6. Child 6 has no explicit `animation-delay` rule — it inherits the base rule's delay of `0ms`, meaning Footer and MethodologySummary will both animate at 320ms delay, collapsing the cascade order. The CSS must be extended with a 6th delay slot: `.reveal-cascade-item:nth-child(6) { animation-delay: 320ms; }` with the existing child 5 entry staying at 240ms. This keeps MethodologySummary last in the cascade (the §12.1 requirement) and Footer appearing at or after it. Verified math: 280ms animation duration + 320ms delay = 600ms total — exactly at the §12.1 cap for child 6. The Coder must add the 6th entry and restructure App.tsx's cascade so MethodologySummary is child 5 (delay 320ms) and Footer is child 6 (delay 320ms as well — both at the same delay is acceptable since they are sequentially rendered).

Actually re-checking §12.1: "Stagger offset between sequential elements: 80ms maximum." If MethodologySummary is child 5 at 240ms and Footer is child 6 at 320ms, that is correct 80ms spacing. The comment in app.css notes the current cap was set to avoid 620ms; a 6th item at 320ms still produces 280ms + 320ms = 600ms — still within cap.

**F-T13-2 (PASS-WITH-NOTES):** The tagline paragraph visual treatment is not specified in the current design system. The CDA SME carry-forward note 2 says "set in a slightly larger pull-quote style" and defers the exact treatment to the UI/UX agent. The §12.7 amendment (below) specifies this: the tagline paragraph renders at `--font-size-base` (16px), `--font-weight-medium` (500), `--color-text-secondary`, with a `margin-bottom: var(--space-4)` gap before the body paragraph. This is not a lead-paragraph treatment (18px) — the KeyFinding strip above the explorer is the article lead; MethodologySummary is the method note below. Keeping the tagline at 16px medium-weight distinguishes it from body regular-weight without escalating to lead-paragraph scale.

### 2. 30-second journalist test — PASS

The six-sentence prose block passes all four journalist requirements:
- What is measured: "the corpus lens" named and defined in sentence 3.
- What CDA protocols do: free-list, pile-sort, rating named in sentence 2.
- That measurement uncertainty is shown: ellipses named explicitly in sentence 4.
- That this is exploratory not confirmatory: sentence 6 leads with "The originating question is exploratory."

The tagline at the head of the block gives the lede orientation in one sentence before the prose begins. The footnote tells the journalist where to read more (methodology page) without a fake-link WCAG problem (see F-T13-5 below).

One note: the journalist landing on the page sees: tagline (article header subtitle) → KeyFinding strip → DataExplorer → tagline again (MethodologySummary head) → methodology prose. The second tagline occurrence is redundant for the journalist who read it in the article header. This is intentional per the plan (single source of truth, two display contexts) and the CDA SME approved it. No action needed.

### 3. Researcher cite path — PASS

The methodology summary names: the corpus-lens five-link chain (sentence 3), bootstrap uncertainty (sentence 4, R10 binding), the exploratory posture (sentence 6, §1.5.7), and the open-data release (sentence 6, ARCHITECTURE.md commitment 9). The footnote names the specific measures (Smith's S, Romney CCM, MDS, Procrustes, OCI) and the academic credit roster. The Cite button is in the DownloadBar above the MethodologySummary. The researcher path is: read summary → see measures named in footnote → click Cite → get full citation. This is complete.

### 4. WCAG AA — PASS-WITH-NOTES

**F-T13-3 (BLOCKING):** The CDA SME carry-forward note 5 references a `--color-bg-article` token for footnote contrast verification. No such token exists in `tokens.css`. The article body background is `--color-background` (#ffffff). The Coder must verify footnote contrast against `--color-background: #ffffff`, not a non-existent token. Contrast of `--color-text-caption` (#6c757d) against #ffffff is approximately 4.60:1 — WCAG AA pass. The CDA SME note contains an error in the token name; the Coder resolves this by using `--color-background` as the background reference. No token addition is needed.

**F-T13-4 (PASS-WITH-NOTES):** Heading hierarchy. The current page structure is: `<Header>` (site chrome), `<ArticleHeader>` which renders an `<h1>`, then the DataExplorer, then MethodologySummary. If MethodologySummary renders a heading, it must be `<h2>` — not `<h3>` or lower, since there is no intervening `<h2>` in the current component tree. The plan text says "probably `<h2>`" — this is confirmed here as binding. The heading text per the plan should be something like "About this measurement" or "Methodology" — the exact heading text is not specified in the CDA SME verdict (the prose is not the heading). The §12.7 amendment specifies the heading element and text (see below).

**F-T13-5 (PASS-WITH-NOTES):** The "coming in Phase 6" footnote must not use fake-link styling. The `methodologyPageUrl` prop approach from CDA SME carry-forward note 4 is correct: when `methodologyPageUrl` is `null` (Phase 5 launch), render the footnote as plain text `<p>` with `--color-text-caption`. Do not render it as an `<a href="#">` or as a styled span that visually resembles a link without a real destination. A link with `href="#"` navigates to page top, which is confusing. A span with link styling but no `href` confuses keyboard users who find it in the tab order. The §12.7 amendment specifies the conditional rendering rule.

**F-T13-6 (PASS-WITH-NOTES):** The `prefers-reduced-motion: reduce` handling for MethodologySummary is already covered by the existing `app.css` rule that sets `animation: none; opacity: 1; transform: none;` for all `.reveal-cascade-item` elements. Since MethodologySummary will be wrapped in a `reveal-cascade-item` div, it inherits the reduced-motion override. No additional CSS is needed for this specifically — but the Coder must confirm the `reveal-cascade-item` wrapper is added at the `App.tsx` level (as the pattern shows for all other elements), not inside `MethodologySummary.tsx` itself, so the override applies consistently.

---

## 2. F-T13 findings table

| ID | Severity | Component / File | Issue | Required correction |
|---|---|---|---|---|
| F-T13-1 | BLOCKING | `apps/dashboard/src/styles/app.css` | Cascade CSS only defines 5 `nth-child` delay slots. Adding MethodologySummary as a 6th reveal item produces incorrect delay for Footer (both animate at 0ms or incorrect timing). | Add `.reveal-cascade-item:nth-child(6) { animation-delay: 320ms; }` to `app.css`. Restructure cascade in `App.tsx` so MethodologySummary is child 5 (240ms) and Footer is child 6 (320ms). Verify total cascade = 280ms + 320ms = 600ms — within §12.1 cap. |
| F-T13-2 | PASS-WITH-NOTES | `apps/dashboard/src/components/MethodologySummary.tsx` + `app.css` | Tagline paragraph visual treatment not specified in design system before T13. | Apply §12.7 tagline treatment: `--font-size-base`, `--font-weight-medium`, `--color-text-secondary`, `margin-bottom: var(--space-4)`. Not lead-paragraph weight. See §12.7 MethodologySummary spec. |
| F-T13-3 | BLOCKING | `apps/dashboard/src/components/MethodologySummary.tsx` | CDA SME carry-forward note 5 references a `--color-bg-article` token that does not exist in `tokens.css`. | Use `--color-background` (#ffffff) as the background reference for footnote contrast verification. Contrast of `--color-text-caption` (#6c757d) against #ffffff = ~4.60:1. WCAG AA pass. No new token needed. |
| F-T13-4 | PASS-WITH-NOTES | `apps/dashboard/src/components/MethodologySummary.tsx` | Heading element and text for MethodologySummary not specified. | Render `<h2 className="methodology-summary__heading">About this measurement</h2>`. Must be `<h2>` (no `<h2>` currently exists in page structure between site `<h1>` and this block). See §12.7. |
| F-T13-5 | PASS-WITH-NOTES | `apps/dashboard/src/components/MethodologySummary.tsx` | "Coming in Phase 6" footnote must not use fake-link styling or `href="#"`. | When `methodologyPageUrl` prop is `null`: render footnote as plain `<p className="methodology-summary__footnote">` with `--color-text-caption`. When `methodologyPageUrl` is a non-empty string: render as `<p>...<a href={methodologyPageUrl}>Read the full methodology page</a></p>`. No link when URL is absent. |
| F-T13-6 | PASS-WITH-NOTES | `apps/dashboard/src/App.tsx` | `prefers-reduced-motion` override depends on `reveal-cascade-item` wrapper being at `App.tsx` level, not inside `MethodologySummary.tsx`. | Wrap `<MethodologySummary>` in `<div className="reveal-cascade-item">` inside `App.tsx`, consistent with the existing cascade pattern for all other components. Do not add `reveal-cascade-item` inside `MethodologySummary.tsx`. |

---

## 3. Mobile audit — gaps T13 must close

This is the first full integration test of the mobile layout. The existing CSS establishes a grid-to-single-column collapse at 768px. The following gaps must be verified and corrected in T13:

| Component | §8 requirement | Current CSS state | Gap |
|---|---|---|---|
| ModelSelector | Collapses to "bottom drawer" | `app.css` collapses to single-column grid (`"viz" / "selector"` stacking) — selector renders below the viz, not as an overlay bottom drawer | The §8 spec says "control panel collapses to bottom drawer." The existing implementation produces a stacked layout, not a true bottom drawer. This is a scope question the plan did not explicitly resolve. **Ruling (this verdict):** for Phase 5, the stacked-below layout is accepted as the mobile implementation. A true bottom-drawer overlay adds significant complexity (scroll management, focus trap, overlay positioning) that is Phase 6 work. §12.7 records this as deferred. The Coder does NOT need to implement a bottom-drawer overlay for T13. The "stacked below" layout is the binding Phase 5 mobile pattern. |
| MDSPlot SVG | Full-width, fixed aspect ratio | `app.css` `.mds-plot__svg { width: 100%; height: auto; }` — aspect ratio is SVG viewBox-driven | Verify the SVG `viewBox` is set (not just `width`/`height` attributes) so the SVG scales correctly at narrow widths. If viewBox is absent, the SVG will not maintain aspect ratio. Coder verifies in `MDSPlot.tsx`. |
| Legend | Wraps to multiple rows | `.mds-plot__legend { flex-wrap: wrap; }` — correct | No gap. Confirm wrap works at 375px viewport by visual check. |
| DownloadBar | Buttons wrap to multiple lines; touch targets ≥ 44×44px | No mobile-specific CSS for DownloadBar currently exists in `app.css` | **Gap:** the DownloadBar buttons need `min-height: 44px` at `<768px` to meet WCAG touch-target minimum. The Coder adds a `@media (max-width: 768px)` rule for `.download-bar` buttons. |
| CiteModal / EmbedModal | Full-screen or near-full-screen on mobile | No mobile-specific CSS for modals in `app.css` | **Gap:** modals should use `width: 100%; max-height: 90vh; overflow-y: auto` at `<768px`. Coder adds modal mobile rules. |
| MethodologySummary | Stays at article-prose max-width, full-width readable | New component — no existing CSS | Correctly use `max-width: var(--max-prose-width)` (680px) centered, which is narrower than most viewports even on mobile (375px viewport will naturally go full-width since 680px > 375px — CSS max-width means it will be full-width on mobile automatically). No special mobile rule needed for the prose container itself. |
| ArticleHeader title | Scales down at `<768px` | Current CSS: `font-size: var(--font-size-3xl)` = 48px — no mobile scale-down | **Gap:** 48px title on a 375px viewport takes ~3 lines and dominates the screen. Add `@media (max-width: 768px) { .article-header__title { font-size: var(--font-size-2xl); } }` (32px) — still prominent but not overwhelming. |
| Site header nav | Collapses to logo + menu icon | Current CSS shows nav links in a flex row — no mobile collapse | **Gap:** the site header nav links overflow at narrow widths. Add `@media (max-width: 768px) { .site-header__nav { display: none; } }` as a minimum acceptable Phase 5 mobile treatment. (Phase 6 adds a hamburger menu.) The logo remains visible. |

**Mobile summary:** five gaps must be closed in T13 — DownloadBar touch targets, CiteModal/EmbedModal full-screen, ArticleHeader title font scale, site header nav hide-on-mobile, and MDSPlot viewBox verification. The bottom-drawer pattern is deferred to Phase 6 per this verdict.

---

## 4. Final a11y sweep checklist

The Coder and Reviewer must verify each item on the implemented T13 commit:

**Focus indicators**
- [ ] Every interactive element has a visible `:focus-visible` ring (2px solid `--color-info`, 2px offset). Verify: nav links, domain pills, model checkboxes, viz switcher tabs (including disabled), download bar buttons (CSV, PNG, PNG hi-res, Permalink, Cite, Embed), CiteModal tabs, CiteModal copy buttons, EmbedModal copy button, modal close buttons.
- [ ] No `outline: none` without a replacement focus indicator anywhere in the codebase.

**Tab order**
- [ ] Tab order through the full page (keyboard-only) is logical: Header nav → ArticleHeader links → DomainPicker pills → VizSwitcher tabs → (within DataExplorer) ModelSelector checkboxes → DownloadBar buttons → MethodologySummary (if any interactive elements) → Footer links.
- [ ] CiteModal focus trap: Tab cycles within the modal when open; Escape closes it.
- [ ] EmbedModal focus trap: same.
- [ ] Keyboard-only navigation activates every interactive element (Enter/Space for buttons and checkboxes, Enter for links).

**Heading hierarchy**
- [ ] Page heading order: site `<h1>` (if present in Header) → article `<h1>` (in ArticleHeader) → DataExplorer section heading (if any, should be `<h2>`) → MethodologySummary `<h2 "About this measurement">`. No skipped levels. If Header has no `<h1>` and ArticleHeader is the `<h1>`, the DataExplorer heading (if present) is `<h2>` and MethodologySummary is `<h2>`. Two siblings at `<h2>` level is valid.
- [ ] Confirm: ModelSelector heading (currently `.model-selector__heading` styled as uppercase label) — if this is a `<p>` or `<div>` it is fine; if it is a `<h3>` or higher without a parent `<h2>`, that is a hierarchy violation. Verify the element type.

**ARIA**
- [ ] MDSPlot SVG container has `role="img"` and `aria-label="MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."` per §12.6 binding.
- [ ] All buttons have either visible text or `aria-label`.
- [ ] CiteModal and EmbedModal have `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` pointing to the modal heading.
- [ ] Decorative separators (`aria-hidden="true"`) are confirmed on byline separators.
- [ ] Origin badges in ModelSelector are confirmed `aria-hidden="true"` (already noted in v0.4.2 — verify carries forward).
- [ ] Disabled domain pills have `aria-disabled="true"`.
- [ ] Disabled VizSwitcher tabs have `aria-disabled="true"` per §12.3.
- [ ] Max-6 warning has `role="alert"` per §3.7.

**Images and non-text content**
- [ ] All `<img>` elements have `alt` text or `aria-hidden="true"` if decorative.
- [ ] Logo glyph (`.site-header__logo-glyph`): if it is an SVG inline, it has `aria-hidden="true"` and the parent link has an `aria-label`.
- [ ] R1-state legend marker samples (SVG elements in the legend): each must have a text label alongside the sample; the SVG element itself can be `aria-hidden="true"` since the text label is the accessible name.

**Reduced motion**
- [ ] `prefers-reduced-motion: reduce` is honored for all cascade items (existing `app.css` rule covers this — verify no new animations have been added outside the rule).
- [ ] KeyFinding fade animation is inside the `prefers-reduced-motion` rule in `app.css`.
- [ ] No new CSS animations or transitions added in T13 outside the existing reduced-motion overrides.

**Contrast**
- [ ] MethodologySummary heading: `--color-text-primary` (#2c3e50) on `--color-background` (#ffffff) = approximately 11.5:1. WCAG AA pass.
- [ ] Tagline paragraph: `--color-text-secondary` (#7f8c8d) on `--color-background` = approximately 3.40:1. This is below WCAG AA 4.5:1 for small text. **The tagline at 16px regular-weight at `--color-text-secondary` fails WCAG AA.** See F-T13-7 below.

Wait — this is a new finding from the contrast check. Let me add it to the findings table.

**F-T13-7 (BLOCKING):** The tagline paragraph treatment specified above (`--color-text-secondary`, 16px, weight 500) must be re-evaluated for contrast. `--color-text-secondary` (#7f8c8d) on white (#ffffff) computes to approximately 3.40:1. WCAG AA requires 4.5:1 for text under 18pt (24px) regular weight or 14pt (18.67px) bold. At 16px / weight 500, WCAG AA requires 4.5:1. This fails. The correct token for the tagline paragraph is `--color-text-caption` (#6c757d, approximately 4.60:1) — the same token used for footnotes and source attribution at 12px, which also passes at 16px. Alternatively, use `--color-text-primary` (#2c3e50, approximately 11.5:1) if the tagline should be treated as primary content. Given the tagline is the orientation hook above the methodology prose — a semi-prominent, non-body element — `--color-text-caption` (#6c757d) at 16px medium-weight is the appropriate choice: slightly receded from primary but still clearly readable and WCAG AA compliant.

Update to F-T13-2: tagline uses `--color-text-caption` (not `--color-text-secondary`).

---

Revised findings table entries (updated):

| ID | Severity | Component / File | Issue | Required correction |
|---|---|---|---|---|
| F-T13-2 | PASS-WITH-NOTES | `apps/dashboard/src/components/MethodologySummary.tsx` + `app.css` | Tagline paragraph visual treatment not specified; `--color-text-secondary` at 16px fails WCAG AA (3.40:1 < 4.5:1). | Apply §12.7 tagline treatment: `--font-size-base` (16px), `--font-weight-medium` (500), `--color-text-caption` (#6c757d, ~4.60:1 on white — WCAG AA pass), `margin-bottom: var(--space-4)`. |
| F-T13-7 | BLOCKING | `apps/dashboard/src/components/MethodologySummary.tsx` + DESIGN_SYSTEM.md §12.7 | `--color-text-secondary` (#7f8c8d) at 16px/500 weight = ~3.40:1 contrast on white — WCAG AA failure for that size/weight combination. | Use `--color-text-caption` (#6c757d) for the tagline paragraph. Already the correct token for 16px text where a slightly-receded-but-readable treatment is intended. §12.7 specifies this. |

---

## 5. Performance final pass

**Bundle size projection:**
- Current: 75.20 KB gzipped.
- T13 additions: `MethodologySummary.tsx` (one functional component, two paragraphs, no new dependencies — estimated ~1.5 KB uncompressed, ~0.8 KB gzipped); `methodology_summary.ts` (three string constants, ~1.2 KB uncompressed, ~0.7 KB gzipped); CSS additions for MethodologySummary classes and mobile rules (~2 KB uncompressed, ~0.9 KB gzipped).
- Projected total: ~75.20 + ~2.4 = ~77.6 KB gzipped.
- Cap: 400 KB. T13 is at ~19% of cap. No performance concern.

**Font subset confirmation:**
- `tokens.css` confirms Lato (regular 400, bold 700) and JetBrains Mono (regular 400, bold 700) — all four weights — are self-hosted from `/fonts/` with `@font-face` declarations and explicit `unicode-range` subset.
- No new fonts are introduced by T13. Font budget is unaffected.
- Confirm `public/fonts/lato/lato-regular.woff2`, `lato-bold.woff2`, `jetbrains-mono/jetbrains-mono-regular.woff2`, `jetbrains-mono/jetbrains-mono-bold.woff2` are present in the build output (the T4 scaffold should have placed them; T13 adds no new font references).

**No new external resource loads:** MethodologySummary is pure static text from a TypeScript constant. No images, no external requests, no additional CDN references.

---

## 6. MethodologySummary component spec

This is the exact layout specification for the Coder. Source of truth is §12.7 (added to DESIGN_SYSTEM.md with this verdict).

**Component signature:**

```typescript
interface MethodologySummaryProps {
  methodologyPageUrl?: string | null;
}
export function MethodologySummary({ methodologyPageUrl = null }: MethodologySummaryProps)
```

**Rendered structure (semantic HTML):**

```html
<section
  className="methodology-summary"
  aria-labelledby="methodology-summary-heading"
>
  <h2 id="methodology-summary-heading" className="methodology-summary__heading">
    About this measurement
  </h2>

  <p className="methodology-summary__tagline">
    {taglineQuote}
  </p>

  <p className="methodology-summary__body">
    {methodologySummary}
  </p>

  <p className="methodology-summary__footnote">
    {methodologyPageUrl
      ? <>A full methodology page ... <a href={methodologyPageUrl}>Read the full methodology page →</a></>
      : methodologyFootnote
    }
  </p>
</section>
```

**CSS classes and token usage:**

```css
.methodology-summary {
  max-width: var(--max-prose-width);   /* 680px — article prose width */
  margin: var(--space-16) auto 0;      /* 64px top gap from DataExplorer above */
  padding: 0 var(--space-6);
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--space-8);
}

.methodology-summary__heading {
  font-size: var(--font-size-xl);       /* 24px */
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.methodology-summary__tagline {
  font-size: var(--font-size-base);     /* 16px */
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-body);
  color: var(--color-text-caption);     /* #6c757d — ~4.60:1 on white, WCAG AA */
  margin-bottom: var(--space-4);
}

.methodology-summary__body {
  font-size: var(--font-size-base);     /* 16px */
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-body);
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
}

.methodology-summary__footnote {
  font-size: var(--font-size-xs);       /* 12px */
  line-height: var(--line-height-body);
  color: var(--color-text-caption);     /* #6c757d — ~4.60:1 on white, WCAG AA at 12px */
}

.methodology-summary__footnote a {
  color: var(--color-info);
  text-decoration: underline;
}

.methodology-summary__footnote a:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}
```

**Reveal cascade position:** MethodologySummary is wrapped in `<div className="reveal-cascade-item">` at the `App.tsx` level, positioned after DataExplorer and before Footer. It is child 5 in the cascade (240ms delay). Footer becomes child 6 (320ms delay). The CSS must add a 6th slot (F-T13-1).

**Embed mode:** Per existing §12.5 spec in `App.tsx` (already annotated: "suppress Header, Footer, ArticleHeader, KeyFinding, MethodologySummary"), the MethodologySummary is excluded in embed mode. No additional change needed — the embed-mode path in `App.tsx` does not render MethodologySummary.

**Unit test requirement (from CDA SME carry-forward note 3, binding):**
File `apps/dashboard/src/copy/methodology_summary.test.ts` must contain an assertion that `taglineQuote === TAGLINE` (importing both from their respective modules). This keeps the single-source-of-truth invariant honest.

---

## 7. DESIGN_SYSTEM.md v0.4.4 amendment

The following amendment must be applied to DESIGN_SYSTEM.md. Update the version header from v0.4.3 to v0.4.4. Add the changelog entry. Add §12.7. Update the footer.

**Changelog entry to add (insert at top of Changelog block, before the v0.4.3 entry):**

```
- **v0.4.4** (T13 plan-level UI/UX verdict, 2026-05-11) adds §12.7 (MethodologySummary block visual specification). Specifies: component structure (`<section>` with `aria-labelledby`), heading element (`<h2 id="methodology-summary-heading">About this measurement</h2>`), tagline paragraph token (`--color-text-caption` not `--color-text-secondary` — the latter fails WCAG AA at 16px with ~3.40:1 contrast), body paragraph token (`--color-text-primary`), footnote conditional rendering (plain text when `methodologyPageUrl` is null; inline link when URL is set), CSS class names and spacing tokens, reveal cascade position (child 5, 240ms delay — requires adding a 6th cascade slot to `app.css`), mobile posture (max-width 680px renders full-width on narrow viewports automatically; no special mobile rule needed for the prose container). Records the mobile bottom-drawer deferral decision: §8 calls for a control panel bottom-drawer on `<768px`; T13 accepts the stacked-below layout as the Phase 5 mobile implementation; a true bottom-drawer overlay is deferred to Phase 6. Also records five mobile gaps the T13 Coder must close: DownloadBar touch targets (min-height: 44px at `<768px`), CiteModal/EmbedModal full-screen on mobile, ArticleHeader title font scale-down (48px → 32px at `<768px`), site header nav hide-on-mobile (display: none at `<768px`), MDSPlot viewBox verification.
```

**§12.7 section to append before the closing footer of DESIGN_SYSTEM.md:**

```markdown
### 12.7 MethodologySummary block (v0.4.4 — T13, 2026-05-11)

The MethodologySummary is the article-bottom methodology note rendered below the DataExplorer per §2.1 page architecture. It is the "method note" level of the page — below the "lead" (KeyFinding strip), below the "visualization" (DataExplorer), above the Footer. It is not a section of the methodology *page* (Phase 6 §6); it is the in-article summary block.

**Component:** `apps/dashboard/src/components/MethodologySummary.tsx`
**Source constants:** `apps/dashboard/src/copy/methodology_summary.ts` (SME-approved, do not paraphrase)

**Placement in page cascade:**
- Positioned after DataExplorer, before Footer.
- Wrapped in `<div className="reveal-cascade-item">` at `App.tsx` level (not inside the component).
- Cascade position: child 5 → 240ms delay. Footer: child 6 → 320ms delay.
- `app.css` must add `.reveal-cascade-item:nth-child(6) { animation-delay: 320ms; }` to accommodate the 6th cascade item without breaking the §12.1 600ms total cap.
- **Excluded in embed mode** per §12.5.

**Rendered structure:**

```html
<section className="methodology-summary" aria-labelledby="methodology-summary-heading">
  <h2 id="methodology-summary-heading" className="methodology-summary__heading">
    About this measurement
  </h2>
  <p className="methodology-summary__tagline">{taglineQuote}</p>
  <p className="methodology-summary__body">{methodologySummary}</p>
  <p className="methodology-summary__footnote">
    {methodologyPageUrl ? (live link variant) : (plain text variant)}
  </p>
</section>
```

**Heading:** `<h2>` is required. The heading text "About this measurement" is binding for Phase 5. Phase 6 may update it when the full methodology page exists. The `aria-labelledby` attribute on the `<section>` pointing to the heading id makes the section landmark accessible to screen readers.

**Tagline paragraph:** `--font-size-base` (16px), `--font-weight-medium` (500), `--color-text-caption` (#6c757d, ~4.60:1 on white — WCAG AA pass at 16px), `margin-bottom: var(--space-4)`. The tagline is NOT rendered at `--font-size-lg` (lead weight) — the KeyFinding strip above the explorer is the article lead; this is the method note. The tagline appears here as a brief orientation hook at slightly-receded-but-readable weight, separate from the body prose paragraph.

**Body paragraph:** `--font-size-base` (16px), `--font-weight-regular` (400), `--color-text-primary`, `line-height: var(--line-height-body)`. One paragraph containing all six SME-approved sentences. Do not split into multiple paragraphs without CDA SME re-review.

**Footnote paragraph:** `--font-size-xs` (12px), `--color-text-caption` (#6c757d, ~4.60:1 on white — WCAG AA pass at 12px per v0.4.3). Conditional rendering:
- `methodologyPageUrl === null` (Phase 5 launch): render as plain `<p>` with no link, no fake-link styling.
- `methodologyPageUrl` is a non-empty string (Phase 6+): render the footnote text with an inline `<a href={methodologyPageUrl}>Read the full methodology page →</a>` appended, using `--color-info` color and underline.

**Max-width:** `var(--max-prose-width)` (680px), centered (`margin: auto`). This is the article-prose width — narrower than the DataExplorer container (1200px). On mobile viewports `<680px`, the container goes naturally full-width; no special mobile rule is needed for the prose container itself.

**Top margin from DataExplorer:** `margin-top: var(--space-16)` (64px), plus a `border-top: var(--border-width) solid var(--color-border)` visual separator to signal the section break from the interactive explorer.

**Mobile posture:** No special rule needed for the MethodologySummary prose container. The max-width of 680px renders as full-width on narrow viewports automatically.

**Mobile bottom-drawer deferral (binding ruling):** DESIGN_SYSTEM.md §8 calls for the control panel to "collapse to a bottom drawer on screens narrower than 768px." T13 ships the stacked-below layout (ModelSelector below MDSPlot in a single-column grid) as the Phase 5 mobile implementation. A true bottom-drawer overlay — with scroll management, focus trap, and overlay positioning — is deferred to Phase 6 and should be listed in the Phase 6 feature plan. The Reviewer does not reject T13 for absence of a bottom-drawer overlay.

**Five mobile gaps closed in T13 (binding, all must be present in the T13 commit):**
1. **DownloadBar touch targets:** `@media (max-width: 768px)` rule adds `min-height: 44px` to all DownloadBar button elements (CSV, PNG, Permalink, Cite, Embed buttons).
2. **CiteModal/EmbedModal mobile:** `@media (max-width: 768px)` rule sets modal container to `width: calc(100% - 32px); max-height: 90vh; overflow-y: auto`.
3. **ArticleHeader title font scale:** `@media (max-width: 768px) { .article-header__title { font-size: var(--font-size-2xl); } }` (48px → 32px).
4. **Site header nav hide-on-mobile:** `@media (max-width: 768px) { .site-header__nav { display: none; } }` (Phase 6 adds hamburger menu).
5. **MDSPlot viewBox:** Verify `MDSPlot.tsx` sets a `viewBox` attribute on the `<svg>` element so aspect ratio is maintained at all viewport widths. The `width: 100%; height: auto` in `app.css` depends on viewBox being set.

**Unit test requirement (binding, from CDA SME carry-forward note 3):**
`apps/dashboard/src/copy/methodology_summary.test.ts` must assert `taglineQuote === TAGLINE` (importing from `./methodology_summary` and `./framing` respectively).
```

**Update to DESIGN_SYSTEM.md footer:** Replace the existing closing footer:
```
*End of DESIGN_SYSTEM.md v0.4.2. This document is a living specification — update it before building any new component that requires a visual decision not covered here.*
```
with:
```
*End of DESIGN_SYSTEM.md v0.4.4. This document is a living specification — update it before building any new component that requires a visual decision not covered here.*
```

---

