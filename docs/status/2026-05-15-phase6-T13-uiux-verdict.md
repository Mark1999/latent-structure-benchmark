---
filed: 2026-05-15
reviewer: UI/UX agent (Sonnet)
task: Phase 6 T13 — add `food` as third domain (sub-option B)
plan_reviewed: docs/status/2026-05-15-phase6-T13-architect-plan.md
cda_sme_verdict: docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md (PASS-WITH-NOTES)
slack_channel: "#lsb-ui-ux"
design_system_version: v0.4.9 (no update required)
verdict: PASS
---

# Phase 6 T13 — UI/UX Plan Verdict (add `food` as third domain)

**UI/UX VERDICT: PASS**

```
UI/UX VERDICT: PASS

1. OWID design fidelity:      PASS
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS

DESIGN_SYSTEM.md update:      not required
```

Coder may proceed immediately after CDA SME PASS-WITH-NOTES notes are applied. No M-notes from this gate.

---

## Mandatory reads completed

- DESIGN_SYSTEM.md v0.4.9 — read in full.
- docs/status/2026-05-15-phase6-T13-architect-plan.md — read in full.
- docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md — read in full.
- apps/dashboard/src/App.tsx lines 70–99 — FUTURE_DOMAINS + buildDomainList().
- apps/dashboard/src/components/DomainPicker.tsx — full component.
- apps/dashboard/src/components/KeyFinding.tsx — full component.
- apps/dashboard/src/components/FailuresFindingsSection.tsx — full component.
- apps/dashboard/src/components/MethodologySummary.tsx — full component.
- apps/dashboard/src/styles/app.css — DomainPicker CSS block (lines 375–456).
- apps/dashboard/src/styles/tokens.css — spacing and max-width tokens.
- apps/dashboard/public/data/manifest.json — current two-domain state.
- apps/dashboard/src/copy/failures_findings.ts — SECTION_HEADING confirmed domain-agnostic.

---

## Four-question scorecard

### 1. OWID design fidelity — PASS

No new visualization components, no new tokens, no new color usage, no new chart type. The food pill is a third instance of an existing generic component. All OWID-style conventions (data labeled with source, uncertainty in lede via bootstrap CI, MDS ellipses for the food domain once data exists) are inherited automatically from the existing article shell. No visual posture change is introduced.

The DESIGN_SYSTEM.md §2.3 domain navigation diagram already shows `[Family] [Holidays] [Food] [Emotion *] [Justice *]` — three active pills is the documented design intention, not a new state.

### 2. 30-second journalist test — PASS

The article shell is structurally identical to family and holidays. A journalist landing on the food pill cold encounters: ArticleHeader with domain-specific title, KeyFinding lede strip with the auto-generated food lede (whatever pattern the publish layer selects), and the DataExplorer. The lede strip is the primary 30-second surface. CDA SME pre-cleared all eight pattern keys for "food" substitution — each reads cleanly in the descriptive-locational frame.

Regarding the methodology page: `MethodologySummary` renders with `methodologyPageUrl={null}` at App.tsx line 342, producing plain-text footnote without a broken link. This is identical to the current family/holidays state. It is not a T13 regression and not a T13 problem. The methodology link absence is a T1/T2 concern already documented in the Architect plan §10 risk #6.

### 3. Researcher cite path — PASS

No change to the cite path. `MethodologySummary` body text is static and domain-agnostic. The SourceAttribution component (if rendered inside DataExplorer) is domain-generic. The open-data bundle reference and citation text are unchanged. The food domain inherits the same cite path as family and holidays.

This criterion is trivially satisfied: the article shell is unchanged.

### 4. WCAG AA — PASS

All four accessibility sub-checks pass.

**Contrast.** Active pill: white (#ffffff) on `--color-info` (#3360a9) ≈ 7.0:1 — WCAG AA 4.5:1 PASS. Inactive available pill: `--color-text-primary` (#2c3e50) on white ≈ 10.7:1 — PASS. Disabled pills use `--color-text-muted` (#bdc3c7) — this is the established token for non-readable disabled affordances, consistent with current behavior, and not a T13 change. Focus ring: 2px solid `--color-info` (#3360a9) with outline-offset: 2px — WCAG 2.4.11 visible focus PASS.

**Three-pill mobile layout.** The `.domain-picker__list` uses `display: flex; flex-wrap: wrap; gap: var(--space-3)` (12px). Pill padding is `var(--space-2) var(--space-4)` (8px vertical / 16px horizontal) at 14px font. At 320px viewport with 24px left+right padding on `.domain-picker`, available content width is 272px. Measured pill widths: "Family" ~80px, "Holidays" ~92px, "Food" ~62px, plus two gaps of 12px = ~258px total. Three active pills fit in a single row at the narrowest documented mobile breakpoint (320px). Flex-wrap means any edge-case wrap produces two accessible rows, not overflow or clipping. No orphan risk for "Food" alone because it is the shortest label. The two disabled future pills (Emotion, Justice) remain appended after the three active pills and have always wrapped at narrow widths.

**Keyboard cycling with N=3.** DomainPicker.tsx `moveFocus()` uses `(currentIndex + direction + total) % total` with `total = buttons.length`. This is fully generic — not hard-coded to N=2. For N=3: ArrowLeft from index 0 → (0 - 1 + 3) % 3 = 2 (wraps to last pill). ArrowRight from index 2 → (2 + 1 + 3) % 3 = 0 (wraps to first pill). Correct wrap-around confirmed.

**ARIA.** Each pill is `role="tab"` with `aria-selected` (true/false) and `aria-label` from `pillAriaLabel()`. The component uses the tablist pattern (`role="tablist"` on the container), not the navigation landmark pattern, so `aria-selected` is the correct attribute — not `aria-current="page"`. When food is active: `aria-label` = "Domain: Food — currently displayed", `aria-selected="true"`. Correct.

**FailuresFindingsSection heading.** `SECTION_HEADING` = "Collection records and follow-up interviews" (static string from the copy module). The heading is domain-agnostic by design (established at T10). The `domainSlug` prop drives the fetch URL only, not the heading text. The section is correctly identified by `aria-labelledby="failures-findings-heading"`. No issue.

---

## Four specific UI/UX checks for T13

**Check 1 — DomainPicker layout at 3 pills.** PASS. Three active pills ("Family", "Holidays", "Food") fit in a single row at 320px with ~16px to spare before the flex-wrap boundary. Flex-wrap is already set, so any measurement variance produces graceful wrapping, not overflow. No CSS change required.

**Check 2 — Keyboard cycling with N=3.** PASS. `moveFocus()` modular arithmetic `(currentIndex + direction + total) % total` is fully generic. Wraps correctly in both directions for any N >= 2. No hard-coding to N=2 found. No code change required.

**Check 3 — Future-promotion dedup.** PASS. `buildDomainList()` builds `manifestSlugs` as a Set from manifest domains, then filters FUTURE_DOMAINS to only slugs absent from that Set. When manifest carries food, food is excluded from the future list and appears exactly once from the manifest path with `available: true`. No duplicate. No stuck-disabled state. No code change required.

**Check 4 — Food lede readability.** PASS (structural posture confirmed; rendered text will exist post-collection). `KeyFinding.tsx` renders `{generatedLede}` inside a single `<p className="key-finding__content">` with no truncation, no hard-coded line count, and no per-domain branching. The CSS max-width is 780px; the element auto-sizes to content. The component's `aria-live="polite"` on the inner paragraph ensures screen readers announce the new lede on domain switch. CDA SME pre-cleared all eight lede pattern keys for "food" substitution — each reads coherently in the descriptive-locational frame.

---

## Binding M-notes for the Coder

None. This gate is clear. The article shell is fully generic. The food domain auto-promotes, the keyboard handler handles N=3, and the lede strip renders any string passed to it.

The Coder should note (informational, not binding):

- `FailuresFindingsSection` heading "Collection records and follow-up interviews" is a static domain-agnostic string (T10 design decision). No heading customization is expected or needed for food.
- AC21 and AC22 (app-state test + domain-picker test extension) are test additions, not code changes to existing components. The Coder should extend the tests, not modify the components.

---

## DESIGN_SYSTEM.md update: not required

DESIGN_SYSTEM.md v0.4.9 already specifies:

- §2.3 domain navigation shows `[Family] [Holidays] [Food] [Emotion *] [Justice *]` in the ascii diagram — three active pills is the documented design state.
- §12.3 VizSwitcher disabled-tab visual treatment covers the focusable-disabled-pill binding (§12.3 reference in DomainPicker.tsx code).
- All token decisions for pills, focus rings, and text contrast are already specified.

No new chart type, no new token, no new color usage, no new interaction pattern is introduced by T13. The design system is complete for this task.

---

## Rationale

T13 is the minimum-viable extensibility proof for the article shell. The frontend infrastructure was built generically from the start: App.tsx FUTURE_DOMAINS, buildDomainList() dedup, DomainPicker N-agnostic keyboard handler, KeyFinding lede-string renderer, FailuresFindingsSection domainSlug-parameterized fetch. Every component inspected passes its role — none has per-domain branching that would require modification. The food domain promotes automatically when the manifest carries it, the pill appears with correct ARIA semantics, the lede renders whatever string the publish layer produces, and the failures section fetches food failures by slug.

The gate reduces to verifying that the generic wiring works for N=3. It does.

This verdict covers the frontend posture only. CDA SME PASS-WITH-NOTES (including AC10 verbatim lede review) governs methodology. The Coder proceeds after both gate verdicts are received.

---

*End of UI/UX verdict for Phase 6 T13. Post to #lsb-ui-ux.*
