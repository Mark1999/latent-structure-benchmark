# Latent Structure Benchmark (LSB) — Design System & UI Specification

**Document name:** DESIGN_SYSTEM.md  
**Version:** v0.4.6  
**Status:** Draft — for review by Mark and Opus Architect agent  
**Audience:** UI/UX Agent, Coder agent, Reviewer agent, Mark  
**Companion docs:** `ARCHITECTURE.md` (v0.7+), `CLAUDE.md`

**This document is binding on all frontend work.** The Reviewer agent must reject any component that contradicts it. The UI/UX agent owns this document and must be consulted before any visual decision is made by the Coder agent.

**Changelog:**
- **v0.4.6** (T8 plan-level UI/UX verdict, 2026-05-12) closes §12.6 Phase-5 "Read as table" deferral. T8 implements the §7 binding for MDS, FreeList, and Similarity. Adds §12.9 (ReadAsTableToggle + ScreenReaderSummary visual specification): `aria-controls` DOM-presence requirement (U1), pressed-state non-text contrast (U2 — `border: 2px solid var(--color-info)`, ~7.3:1 on white, WCAG 1.4.11 PASS), and `.sr-only` reuse. No new tokens.
- **v0.4.5** (T5 plan-level UI/UX verdict, 2026-05-12) adds §12.8 (SimilarityHeatmap cell-text contrast specification) and introduces one component-scoped token `--color-heatmap-cell-text-dark: #000000`. The T5 plan's §2.2 binary text-color switch at similarity = 0.5 (fallback 0.55) fails WCAG AA 4.5:1 across the observed data range in both shipped domains. §12.8 specifies the corrected switch threshold of 0.73 and the `HEATMAP_TEXT_SWITCH_THRESHOLD` constant. The plan's "raise to 0.55" fallback is superseded.
- **v0.4.4** (T13 plan-level UI/UX verdict, 2026-05-11) adds §12.7 (MethodologySummary block visual specification). Specifies: component structure (`<section>` with `aria-labelledby`), heading element (`<h2 id="methodology-summary-heading">About this measurement</h2>`), tagline paragraph token (`--color-text-caption` not `--color-text-secondary` — the latter fails WCAG AA at 16px with ~3.40:1 contrast), body paragraph token (`--color-text-primary`), footnote conditional rendering (plain text when `methodologyPageUrl` is null; inline link when URL is set), CSS class names and spacing tokens, reveal cascade position (child 5, 240ms delay — requires adding a 6th cascade slot to `app.css`), mobile posture (max-width 680px renders full-width on narrow viewports automatically; no special mobile rule needed for the prose container). Records the mobile bottom-drawer deferral decision: §8 calls for a control panel bottom-drawer on `<768px`; T13 accepts the stacked-below layout as the Phase 5 mobile implementation; a true bottom-drawer overlay is deferred to Phase 6. Also records five mobile gaps the T13 Coder must close: DownloadBar touch targets (min-height: 44px at `<768px`), CiteModal/EmbedModal full-screen on mobile, ArticleHeader title font scale-down (48px → 32px at `<768px`), site header nav hide-on-mobile (display: none at `<768px`), MDSPlot viewBox verification.
- **v0.4.3** (T10 per-commit UI/UX review, 2026-05-10) adds `--color-text-caption: #6c757d` to §1.2 UI chrome tokens. The T10 `SourceAttribution.tsx` implementation used `--color-text-muted` (#bdc3c7) for the source attribution line text, producing a contrast ratio of approximately 1.75:1 on white at 12px — a WCAG AA failure (4.5:1 required). The existing `--color-text-secondary` (#7f8c8d) computes to approximately 3.40:1 on white, also insufficient for 12px regular-weight text. The new `--color-text-caption: #6c757d` computes to approximately 4.60:1 on white, passes WCAG AA for 12px text, and is the correct token for the SourceAttribution source line and small-n footnote. The `--color-text-secondary` annotation is updated to clarify it is appropriate for bold or large secondary labels (14px+); the `--color-text-muted` annotation is tightened to "disabled states and non-readable placeholders only — never for readable body or caption text."
- **v0.4.2** (T7 per-commit UI/UX review, 2026-05-10) adds the §3.7 initial-state and max-6 warning gating binding spec. The v0.4.1 §3.7 stated that max-6 was "enforced with an inline warning if exceeded" but did not specify the initial state — the T7 implementation defaulted to all-available models, causing the warning to appear on every page load before any user interaction. v0.4.2 adds three binding rules: (1) initial state is the first-6 model_ids by §12.4 lexicographic sort; (2) the warning fires only on interactive add to an already-at-6 selection; (3) "Select all" bypasses per-toggle and may legitimately trigger the warning. EU origin badge contrast (~4.44:1 on `--color-surface-hover`) is flagged as borderline pre-launch (badge is `aria-hidden="true"`, so functional accessibility via checkbox `aria-label` is intact).
- **v0.4.1** (T4 per-commit UI/UX review, 2026-05-10) corrects `--color-model-11` in §1.2 and §12.4 from `#b7950b` to `#9a7d0a`. The v0.4 assertion that `#b7950b` passes WCAG AA 3:1 graphical contrast on white was incorrect — computed contrast ratio was approximately 2.89:1, below the 3:1 minimum. The corrected value `#9a7d0a` passes at approximately 3.96:1. The hue family (dark gold) is preserved.
- **v0.4** (Phase 5 plan UI/UX gate, 2026-05-09) adds §12 (Phase 5 Visual Decisions) covering five visual decisions required by the Phase 5 architect plan that v0.3 did not specify: page-load reveal animation timing (§12.1), data fetch loading state (§12.2), VizSwitcher disabled-tab visual treatment with WCAG 2.1 SC 2.1.1 correction overriding the T8 plan spec (§12.3), model color assignment for >6 models with five new palette tokens (§12.4), and embed mode chrome suppression with frame-ancestors security gate (§12.5). Adds §12.6 (Phase 5 "Read as table" deferral and minimum viable screen-reader posture). Updates §3.2 MDSPlot library entry from "D3" to "D3 or React+SVG" (hand-rolled SVG approved for Phase 5; D3 zoom/pan deferred to Phase 6). Extends §1.2 color palette with `--color-model-7` through `--color-model-11`. Corrects vestigial footer label from v0.1 to v0.4.
- **v0.3** (post-PR-A UI/UX review, 2026-04-20) extends §3.3.5 with binding implementation requirements for the Register 1 annotations on Register 2 points: R1-c stroke width raised to 3px (WCAG AA fix for the orange/green palette slots at 10px marker size); R1-b dashed stroke specified at 100% model color opacity (only the fill is at 60%); tooltip copy for R1-c de-jargonized (schema identifiers moved to data dictionary + methodology page); legend marker-sample requirement added (text tags alone fail WCAG); all-deterministic edge-case copy specified as a named lede case; OCI low-concentration threshold config constant location specified at `apps/dashboard/src/config/analysis.ts`; §7 shape-encoding ambiguity clarified (model points remain filled circles; baseline markers use ★/◆; R1-c introduces state-encoded shape, not origin-encoded). Extends §5 CSV export spec to include `oci`, `deterministic_output`, `r1_state` columns. Mark-level decision resolved on 2026-04-20: hollow triangle (△) is the R1-c marker shape. No changes to design tokens, color palette, or page architecture.
- **v0.2** folds the multi-baseline-and-ungrounded-as-normal framing from `ARCHITECTURE.md` v0.7 §1.5.5 / §3.2 / §4.2.5 into the design system. The grounding section (§4) now leads with the explicit statement that **ungrounded is a normal first-class state for any domain, not a degraded fallback**, and that **a domain can carry zero, one, or many human baselines simultaneously** (published, researcher-submitted, or both). Updates §3.3 to reframe the four "Mode" rows as the four grounding-display *states* (matching `ARCHITECTURE.md` §4.5 terminology) and removes language that implied grounding was the default and ungrounded the exception. Updates §3.7 model selector panel copy to put the "Submit your data" affordance on equal footing with the baseline checkboxes rather than as a footer link. Updates §3.8 key finding conditional behavior to be explicit that the comparative-only finding is fully equivalent in status, not a degraded form. Updates §4.1 State 0 copy and label so it reads as "this domain is studied model-to-model" rather than as a "no baseline available yet" placeholder. Tightens §4.3 submission UI copy to emphasize that LSB exists *to* connect to the human CDA research community, not as a one-way data publisher. Updates §6.1 methodology page section 5 outline to lead with the multi-baseline framing and the contribution invitation. Adds a §4.4 cross-reference note pointing at `ARCHITECTURE.md` §4.2.5 (data layer) and §3.2 `GroundingRef` (schema). No design tokens, no component additions, no changes to the page architecture or accessibility requirements.
- v0.1 initial draft.

---

## 0. Design Philosophy

The LSB dashboard is a **scientific publication, not a product.** It is modeled explicitly on the Our World in Data (OWID) design language — specifically their Data Explorer pattern. Every design decision is made in service of three audiences arriving at the same URL simultaneously:

- **Journalists** — need to understand the finding in 30 seconds and export a shareable image
- **AI engineers** — want to filter models, compare results, and understand methodology
- **Researchers** — need to reproduce findings and access raw data. LSB releases verbatim prompts (CC0), verbatim model responses (CC-BY-4.0), reproducible numerics with bootstrap configuration documented, and code under permissive license (Apache 2.0). The design language must read as an open scientific instrument: a place where researchers form their own interpretations from reliably produced measurements.

The design succeeds when all three audiences leave satisfied without the interface having been dumbed down for any of them.

**The visual metaphor:** LSB produces cognitive maps — spatial representations of how AI models organize domain vocabulary. The design language should feel like a scientific instrument: precise, credible, minimal. No gradients, no dark mode hero sections, no decorative animation. Data is the decoration.

---

## 1. Design Tokens

All visual decisions derive from these tokens. They are defined once in `apps/dashboard/src/styles/tokens.css` and referenced throughout. No hardcoded colors, font sizes, or spacing values anywhere in the codebase.

### 1.1 Typography

```css
--font-body: 'Lato', sans-serif;
--font-mono: 'JetBrains Mono', monospace;  /* for data values and citations */

--font-size-xs:   12px;   /* source attribution, footnotes */
--font-size-sm:   14px;   /* secondary labels, legend text */
--font-size-base: 16px;   /* body text */
--font-size-lg:   18px;   /* lead paragraph, key finding */
--font-size-xl:   24px;   /* section headings */
--font-size-2xl:  32px;   /* page title */
--font-size-3xl:  48px;   /* hero stat (e.g., "12 models tested") */

--font-weight-regular: 400;
--font-weight-medium:  500;
--font-weight-bold:    700;

--line-height-tight:  1.3;   /* headings */
--line-height-body:   1.7;   /* prose */
--line-height-data:   1.4;   /* tables, lists */

--max-prose-width:    680px;  /* maximum line length for readable prose */
--max-chart-width:    900px;  /* maximum chart container width */
```

### 1.2 Color Palette

```css
/* Primary data colors — encode meaning, never decorative */
--color-model-1:  #3360a9;   /* primary model (Claude) — OWID blue */
--color-model-2:  #c0392b;   /* contrast model (GPT-4o) */
--color-model-3:  #e67e22;   /* third model */
--color-model-4:  #27ae60;   /* fourth model */
--color-model-5:  #8e44ad;   /* fifth model */
--color-model-6:  #16a085;   /* sixth model */

/* Extended palette (v0.4 — Phase 5 supports up to 11 models per chart) */
--color-model-7:  #d35400;   /* extended palette — dark orange */
--color-model-8:  #1a5276;   /* extended palette — dark blue */
--color-model-9:  #7d3c98;   /* extended palette — dark purple */
--color-model-10: #148f77;   /* extended palette — dark teal */
--color-model-11: #9a7d0a;   /* extended palette — dark gold (corrected v0.4.1; #b7950b failed WCAG AA 3:1 at ~2.89:1) */
/* Beyond slot 11: future-phase design system update extends further; never reuse colors within a chart */

/* Origin encoding (secondary, used alongside model colors) */
--color-origin-us: #3360a9;  /* US-origin models */
--color-origin-eu: #27ae60;  /* EU-origin models */
--color-origin-cn: #c0392b;  /* China-origin models */

/* Human baseline markers */
--color-baseline-published:   #2c3e50;   /* Retained for archival reference; not consumed by v1 components per the 2026-05-07 amendment. */
--color-baseline-researcher:  #7f8c8d;   /* Retained for archival reference; not consumed by v1 components per the 2026-05-07 amendment. */

/* Uncertainty */
--color-ellipse-fill:    rgba(51, 96, 169, 0.08);   /* per-model, use model color at 8% opacity */
--color-ellipse-stroke:  rgba(51, 96, 169, 0.25);   /* per-model, use model color at 25% opacity */

/* UI chrome */
--color-text-primary:    #2c3e50;   /* body text */
--color-text-secondary:  #7f8c8d;   /* secondary labels at 14px+ or bold — ~3.40:1 on white; use --color-text-caption for 12px regular-weight text */
--color-text-caption:    #6c757d;   /* source attribution, footnotes at 12px — ~4.60:1 on white, WCAG AA compliant (v0.4.3) */
--color-text-muted:      #bdc3c7;   /* disabled states and non-readable placeholders only — never for readable body or caption text (~1.75:1 on white) */
--color-border:          #dde1e7;   /* dividers, input borders */
--color-background:      #ffffff;   /* page background */
--color-surface:         #f8f9fa;   /* card backgrounds, panel backgrounds */
--color-surface-hover:   #f0f2f5;   /* hover states on surfaces */

/* Semantic */
--color-success:  #27ae60;
--color-warning:  #f39c12;
--color-error:    #c0392b;
--color-info:     #3360a9;
```

### 1.3 Spacing

```css
--space-1:   4px;
--space-2:   8px;
--space-3:   12px;
--space-4:   16px;
--space-6:   24px;
--space-8:   32px;
--space-10:  40px;
--space-12:  48px;
--space-16:  64px;
--space-20:  80px;   /* section separation */
--space-24:  96px;   /* major section separation */
```

### 1.4 Elevation and Borders

```css
--border-radius-sm:  4px;
--border-radius-md:  8px;
--border-radius-lg:  12px;

--shadow-sm:   0 1px 3px rgba(0,0,0,0.06);
--shadow-md:   0 4px 12px rgba(0,0,0,0.08);
--shadow-lg:   0 8px 24px rgba(0,0,0,0.10);

--border-width: 1px;
--border-color: var(--color-border);
```

---

## 2. Page Architecture

The LSB dashboard is structured as a **long-form publication page** with an embedded interactive explorer — exactly the OWID model. The page is not a single-page app dashboard; it is an article that contains an interactive chart.

### 2.1 Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                      │
│  [Logo: Cognitive Structure Lab]        [About] [Data] [Cite]│
├─────────────────────────────────────────────────────────────┤
│  ARTICLE HEADER (max-width: 780px, centered)                 │
│                                                              │
│  How AI models organize [domain] vocabulary                  │
│  [subtitle: one sentence on what the domain reveals]         │
│                                                              │
│  By Cognitive Structure Lab | April 2026 | [Cite] [License] │
├─────────────────────────────────────────────────────────────┤
│  KEY FINDING STRIP (full width, light background)            │
│  ╔══════════════════════════════════════════════════════╗   │
│  ║  "Claude and GPT-4o organize family terms similarly,  ║   │
│  ║   but DeepSeek clusters kinship roles in a pattern   ║   │
│  ║   distinct from US-origin models."                   ║   │
│  ╚══════════════════════════════════════════════════════╝   │
├─────────────────────────────────────────────────────────────┤
│  DATA EXPLORER (full width, max 1200px)                      │
│  [Interactive chart area — see Section 3]                    │
├─────────────────────────────────────────────────────────────┤
│  METHODOLOGY SUMMARY (max-width: 680px, centered)            │
│  Short prose explaining CDA methodology, corpus lens        │
│  concept, and known limitations. Links to full methodology  │
│  page.                                                       │
├─────────────────────────────────────────────────────────────┤
│  FOOTER                                                      │
│  [License] [Data download] [GitHub] [Cite] [Contact]        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation

Top navigation is minimal — OWID style. Logo left, three links right. No hamburger menus on desktop. Mobile collapses to logo + menu icon.

```
[Cognitive Structure Lab]    [Explore] [Methodology] [Data] [About]
```

### 2.3 Domain Navigation

Domains are navigated via horizontal pill buttons above the explorer, not via the top navigation. Selecting a domain updates the explorer, the key finding, and the URL (permalink).

```
[Family]  [Holidays]  [Food]  [Emotion *]  [Justice *]
                                            * coming soon
```

---

## 3. The Data Explorer

The Data Explorer is the primary interactive element. It replicates OWID's Data Explorer pattern — a visualization switcher, entity selector, domain/time controls, and download affordances — adapted for LSB's data model.

### 3.1 Explorer Layout

```
┌─────────────────────────────────────────────────────────────┐
│  VIZ SWITCHER                                                │
│  [MDS Plot ●] [Free Lists] [Similarity] [Drift]             │
├──────────────────────────────────┬──────────────────────────┤
│                                  │  CONTROL PANEL           │
│                                  │                          │
│  VISUALIZATION AREA              │  Models                  │
│  (D3 or Plotly renders here)     │  ☑ Claude Opus  [US] ●  │
│                                  │  ☑ GPT-4o       [US] ●  │
│  — confidence ellipses           │  ☑ DeepSeek     [CN] ●  │
│                                  │  ☐ Qwen         [CN] ●  │
│  — interactive hover tooltips    │  ☐ Mistral      [EU] ●  │
│  — zoom and pan                  │  ☐ Llama 3      [US] ●  │
│                                  │  [Show all 12 models]    │
│                                  │                          │
│                                  │  ─────────────────────   │
│                                  │  Human baselines         │
│                                  │  ─────────────────────   │
│                                  │  Filter by               │
│                                  │  Origin: [US][EU][CN]    │
│                                  │  Weights:[Open][Closed]  │
└──────────────────────────────────┴──────────────────────────┤
│  DOMAIN SLIDER                                               │
│  Family ──────●──────────────────────────── Justice         │
│               Holidays  Food  Emotion                        │
├─────────────────────────────────────────────────────────────┤
│  DATE SLIDER (shown only in Drift view)                      │
│  Jan 2026 ──────────────────●───────────── [today]          │
├─────────────────────────────────────────────────────────────┤
│  [📥 PNG] [📥 CSV] [🔗 Permalink] [</> Embed]              │
│  claude-opus-4-5 · GPT-4o · DeepSeek-V3 | family | v1.0   │
│  Collected Apr 2026 · Prompt v1.0 · Analysis v0.1           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Visualization Switcher

Four tabs. Selecting a tab animates the chart area transition (150ms fade). The URL updates to reflect the active view (e.g., `cogstructurelab.com/family#mds`).

| Tab | Component | Library | Description |
|---|---|---|---|
| MDS Plot | `MDSPlot.tsx` | D3 or React+SVG | Primary viz — models as points in cognitive space (Phase 5 ships hand-rolled React+SVG; Phase 6 may migrate to D3 for zoom/pan) |
| Free Lists | `FreeListCompare.tsx` | Custom | Side-by-side ranked term lists per model |
| Similarity | `SimilarityHeatmap.tsx` | Plotly | Model×model similarity matrix |
| Drift | `DriftTracker.tsx` | D3 | Longitudinal corpus lens shift over time |

### 3.3 MDS Plot — Detailed Specification

The MDS Plot is the signature visualization. It is the first thing a visitor sees.

**Visual elements, in z-order (back to front):**

1. **Grid lines** — light gray (#dde1e7), no axis labels on the grid itself
2. **Axis labels** — "MDS Dimension 1" and "MDS Dimension 2" in small muted text, with a footnote explaining these are relative dimensions, not named scales
3. **Confidence ellipses** — one per model, filled at 8% opacity of model color, stroked at 25% opacity. Rendered before points so points sit on top.
4. **Model points** — filled circles, 10px radius, model color. White 2px stroke border.
5. **Model labels** — short name (e.g., "Claude", "GPT-4o") in 12px Lato, positioned to minimize overlap using a label offset algorithm. Never overlap a point.
6. **Hover tooltip** — appears on point hover. Shows: full model name, provider, origin, collection date, top 5 free list terms for this model in this domain.

**Interactions:**
- Hover on point → tooltip appears, ellipse brightens
- Click on point → detail panel slides in from right
- Hover on ellipse → tooltip shows bootstrap parameters (n_bootstrap, CI level)
- Zoom with scroll wheel, pan with drag
- Double-click → reset zoom

**Conditional rendering — model-to-model only (2026-05-07 amendment):**

The MDS plot renders model-to-model. Per the 2026-05-07 amendment, no human baseline markers are rendered in v1. The State 0 visual specification below is the only state. The schema retains `DomainResult.groundings: list[GroundingRef]` for forward compatibility but the v1 published data ships with the field empty for all domains.

| State | Baseline marker(s) | Baseline ellipse(s) | Legend entry |
|---|---|---|---|
| **State 0 — model-to-model (the only v1 state)** | None rendered | None rendered | No baseline-related legend entry |

### 3.3.5 Register 1 (OCI) annotations on Register 2 points — added post-F1 SME review

The Register 2 MDS plot (§3.3 above) is the between-model map. Per the three-register framework in `ARCHITECTURE.md` §4.2.0 and the Option-2 annotated-uncertainty contract in `docs/BOOTSTRAP_DESIGN.md`, each model's Register 2 point carries Register 1 (within-model) annotation so a reader can see the model's output concentration alongside its cross-model position — not baked into the ellipse, which would overstate precision.

The following annotations apply to every Register 2 point; they are independent of the grounding state table above and compose with it.

**Three Register 1 states, keyed to `DomainResult.within_model_results[model_id]`:**

| State | Condition on `WithinModelResult` | Register 2 rendering |
|---|---|---|
| **R1-a — Typical concentration** | `deterministic_output == False` AND `oci >= 3.0` | Standard Register 2 ellipse (§3.3 item 3), full opacity. OCI badge in the hover tooltip: "OCI: 4.2" with a one-line explanation on first hover. |
| **R1-b — Low concentration** | `deterministic_output == False` AND `oci < 3.0` | **No confidence ellipse rendered.** The point is rendered with a dashed 2px stroke (not solid) and reduced 60% opacity on the fill. Tooltip surfaces: *"Position uncertain — this model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."* Legend entry under the point has a small italic "low OCI" tag. The final OCI threshold for this state is provisional at 3.0 pending the Phase 4b saturation analysis; see `docs/SME_REVIEW.md` open question 1. |
| **R1-c — Deterministic output** | `deterministic_output == True` | **Dedicated visual marker — not suppression.** The Register 2 point is rendered as a **hollow triangle (△)** instead of a filled circle, same color as the model, with a 3px solid stroke at 100% model color opacity (see Implementation requirements below). **No ellipse** (the model produced zero variance; there is nothing to bootstrap). Tooltip surfaces the approved copy in item 5 of the Implementation requirements block. Legend entry renders a 14px hollow triangle in model color with the label "deterministic output." The mismatch is the finding — the visual treatment flags that the model's zero variance is a property of the architecture (most likely a future deterministic architecture: neurosymbolic systems, zero-temperature models), not a confidence signal. |

**Binding invariants (Reviewer + UI/UX agent enforced):**

1. A reader should never see a Register 2 ellipse that implies more precision than the contributing model's Register 1 stability warrants. States R1-b and R1-c render **without** a Register 2 ellipse.
2. R1-c must be visually distinct from R1-a (different shape, not just different size). A deterministic model that happens to land in the same MDS region as a high-confidence model must be distinguishable at a glance.
3. R1-c is **not suppression.** The model still appears on the map. Its label is still rendered. Its tooltip is still available. The "mismatch is the finding" framing from `ARCHITECTURE.md` §1.5.2 and §1.5.6 applies — the model's deterministic-output behavior is a first-class finding about the architecture.
4. The R1-a / R1-b cutoff (currently OCI < 3.0) is provisional. The `DESIGN_SYSTEM.md` copy must not hard-code the specific value; the dashboard should read it from a config constant so tuning after Phase 4b doesn't require a UI code change.

**Interactions (compose with §3.3 base interactions):**

- Click on an R1-c point → detail panel shows the within-model distribution (Option B centroid run's pile sort) with a banner: "This model produced the same structure on every run. The displayed sort is one instance; the rest are identical."
- Hover on an R1-b point → OCI value and threshold shown inline in tooltip.
- Methodology page (§6 below) links to a short explainer on the three Register 1 states and what the dashboard treatment communicates.

**Why this convention exists:** the SME review of the post-F1 two-level pipeline (2026-04-20) flagged that a `DETERMINISTIC` model whose Register 2 point renders with a zero-width ellipse is visually indistinguishable from a high-N, high-confidence informant — when it is in fact the *least* informative case. This §3.3.5 convention encodes the fix before any zero-temperature or deterministic-architecture model enters the dataset. See `docs/briefings/2026-04-19-sme-implementation-response.md` §3 and the "Mark-level decisions" synthesis dated 2026-04-20.

**Implementation requirements (added post-PR-A UI/UX review — binding):**

1. **Shape decision for R1-c — resolved: hollow triangle (△).** Mark confirmed the UI/UX + CDA SME recommendation on 2026-04-20. Rationale: unambiguous visual vocabulary (no collision with existing ★ / ◆ baseline markers), legible at 10 px, no SVG "selected / hover" state confusion. Binding for all future `MDSPlot.tsx` and legend implementations.

2. **R1-c stroke width: 3px (binding).** The 2px value in the table above is superseded. R1-c markers use a **3px solid stroke at 100% model color opacity** across all palette slots. Rationale: at 10px marker size, a 2px hollow stroke produces insufficient ink coverage for the orange and green palette slots (`--color-model-3`, `--color-model-4`) to pass WCAG AA 3:1 graphical-object contrast on white background.

3. **R1-b dashed stroke opacity: 100% model color (binding).** The 60% reduced opacity applies to the fill only, not the stroke. The dashed stroke is rendered at 100% model color opacity so it passes WCAG AA contrast independently of the fill.

4. **Legend entries must include rendered marker samples (binding).** The legend entry for each R1 state must render a small (14px) visual sample of the actual marker — text tags alone do not satisfy WCAG non-text contrast:
   - R1-a: solid filled circle in model color (standard legend dot)
   - R1-b: dashed-stroke circle in model color with lighter interior, labeled "low output concentration"
   - R1-c: hollow triangle (△) in model color at 3px stroke, labeled "deterministic output"
   Each legend sample must meet 3:1 contrast against the legend background.

5. **Tooltip copy for R1-c (binding replacement).** Replace the parenthetical jargon text. Approved tooltip text:
   > *"Deterministic output — this model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."*

   The schema identifiers `OCI sentinel` and `ConsensusType = DETERMINISTIC` must not appear in the primary hover tooltip. They appear in the open data bundle data dictionary and the methodology page only.

6. **Edge case — all-visible models are R1-c (binding copy).** When every model visible on the Register 2 map is in state R1-c, the key finding strip renders the following copy in place of the standard lede:
   > *"All selected models produced deterministic output on this domain — the same categorical structure on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*

   This is not an error state. The lede generator receives this as a named case with its own template; it does not fall through to a generic "something went wrong" handler.

7. **Config constant location (binding).** The OCI low-concentration threshold is defined once, at `apps/dashboard/src/config/analysis.ts` as `export const OCI_LOW_CONCENTRATION_THRESHOLD = 3.0;`. This is the source of truth for all R1-b threshold comparisons in component code. The methodology page displays the current threshold value injected at build time from the published JSON manifest (which must carry this constant alongside the analysis version). **No component may reference `3.0` as a numeric literal; all must import from this config module.**

8. **§7 shape encoding vs R1-c shape encoding — clarification.** DESIGN_SYSTEM.md §7 states "model origin is encoded in both color and point shape." This refers to the baseline marker shapes (★ for published baselines, ◆ for researcher baselines) distinguishable by shape and color for accessibility. It does **not** require that model points themselves use distinct shapes per origin — §3.3 item 6 governs model point rendering (filled circles for all models in R1-a and R1-b states). R1-c introduces a third shape encoding axis (state, not origin). The Coder must not interpret §7 as requiring origin-specific point shapes for regular model markers.

### 3.4 Free List Compare — Detailed Specification

Side-by-side ranked columns, one per selected model. Maximum 6 models visible simultaneously; if more are selected, a horizontal scroll appears.

Each column shows:
- Model name as column header (colored dot + name)
- Ranked terms by salience (frequency × primacy)
- Each term shown as a pill/badge
- Terms that appear in ALL selected models highlighted with a shared color
- Terms unique to this model shown in model color
- Terms in the human baseline (if available) marked with a small ★ or ◆ inline

Hovering a term highlights that term across all columns simultaneously — showing where it ranks in every model's free list. This is the most powerful interaction in this view.

### 3.5 Domain Slider

The domain slider is not a time slider — it switches between cultural domains. Dragging it (or clicking domain labels) transitions the MDS plot to show the same set of models organized by the new domain.

The transition is animated: model points smoothly move to their new MDS positions over 400ms. This is the most visually compelling interaction in the dashboard — watching models reorganize as the domain shifts from Family to Food reveals corpus lens differences that a static chart cannot.

**Implementation note:** requires precomputed MDS coordinates for all domains in the static JSON. The animation interpolates between coordinate sets using D3 transitions.

**When to show the domain slider:** always, regardless of which viz tab is active. Domain selection is a global state that affects all views.

### 3.6 Date Slider (Drift view only)

Visible only when the Drift tab is active. Allows scrubbing through collection dates to see how model corpus lens positions have shifted over time.

Human baseline markers are **anchored** — they do not move when the date slider is dragged. They are reference points, not subjects. This must be visually obvious: baselines should appear as fixed landmarks while model points animate around them.

### 3.7 Model Selector Panel

The model selector is a persistent left-side panel (or collapsible on mobile). It has two sections:

**Models section:**
- Checkboxes for each of the 12 models in the slate
- Each checkbox has: colored dot (model color), model short name, origin badge ([US]/[EU]/[CN]), and open/closed weights indicator
- Models grouped loosely by origin, separated by thin dividers
- "Select all" / "Clear all" links
- Maximum 6 models selected simultaneously for readability (enforced with an inline warning if exceeded)

**Max-6 enforcement — initial state and warning gating (binding, added v0.4.2):**

The max-6 constraint is an interactive guardrail, not a permanent page-load state. The three rules below are binding on `App.tsx`, its successor `DataExplorer.tsx` (T9), and `ModelSelector.tsx`:

1. **Initial state (binding).** The initial `selectedModels` value on page load and on every domain switch must be the **first 6 model_ids by §12.4 lexicographic sort order** — not all-available. For a domain with 11 models, 6 are selected on load; for a domain with 9 models, 6 are selected on load. Implementation: `Object.keys(rawCoords).sort().slice(0, 6)`.

2. **Warning gating (binding).** The inline `role="alert"` warning fires only when the selection count is already at 6 AND the user attempts to add a further model via the per-row checkbox toggle. The warning must NOT appear on page load (where exactly 6 are selected by rule 1) and must NOT appear before any user interaction.

3. **"Select all" semantics (binding).** "Select all" sets the selection to all available `model_ids`, bypassing per-toggle enforcement. If the result exceeds 6, the warning will appear — this is expected behavior for an explicit user action, not an error. The warning remains visible until the user deselects enough models to bring the count below 6.


### 3.8 Key Finding Strip

The key finding sentence sits between the article header and the data explorer. It is not static copy — it updates based on the current domain and model selection.

The finding is fetched from the static JSON manifest where it was pre-generated by the lede generator (ARCHITECTURE.md §4.2.3). It is styled as:

```
Font: Lato, 20px, weight 500
Color: --color-text-primary
Background: --color-surface (light gray)
Padding: 24px 32px
Border-left: 4px solid --color-model-1
Max-width: 780px, centered
```

When the domain changes, the finding updates with a 200ms fade transition.

**Conditional behavior:** The key finding is comparative across the selected models. The lede generator (`ARCHITECTURE.md` §4.2.3) produces declarative, confident copy describing how the selected models organize the domain relative to each other.

---

## 4. Grounding display — removed (2026-05-07)

An earlier version of this design system (v0.2–v0.3) specified a four-state grounding display framework (State 0: no baselines, State 1: published baseline, State 2: researcher baseline, State 3: multiple baselines), each with marker shapes (★ published, ◆ researcher), ellipse rendering rules, a Grounding Detail Panel, and a Data Submission UI.

The 2026-05-07 amendment removed human grounding from the project (see `ARCHITECTURE.md` §1.5.5 for the framing rationale). The four-state framework collapses to "model-to-model only." Every v1 domain ships with `groundings: []` and the MDS plot renders no baseline markers, no baseline ellipses, and no "Submit your data" affordance.

`data/grounding/family/romney_1996/` retains historical reference data per the amendment plan but is not consumed by any v1 component. See `ARCHITECTURE.md` §4.2.5.

For the binding source-of-truth on the framing rationale, see `docs/status/2026-05-07-lsb-philosophy-and-framing.md` and `ARCHITECTURE.md` §1.5.5.

---

## 5. Download and Attribution Affordances

Every visualization has these controls below it, left-aligned:

```
[📥 Download PNG]  [📥 Download CSV]  [🔗 Permalink]  [</> Embed]

Source: claude-opus-4-5 · GPT-4o-2025-01 · DeepSeek-V3 · [+3 more]
Domain: family | Prompt: v1.0 | Analysis: v0.1 | Collected: Apr 2026
[CC-BY 4.0] [Cite this] [View raw data]
```

**PNG export spec:**
- 1600×900px for social sharing
- 2000×2000px for high-resolution download
- Watermark: "cogstructurelab.com" bottom right, 3% opacity
- Embeds tEXt metadata: domain, models, versions, timestamp

**CSV export:** downloads the underlying data for the current view and model selection.

- **MDS:** 2D coordinates per model, ellipse parameters (`semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap`) where available, plus three Register 1 metadata columns: `oci` (float — the model's Output Concentration Index), `deterministic_output` (boolean), and `r1_state` (string: `typical_concentration` | `low_concentration` | `deterministic`). Ellipse parameter columns are null for R1-b and R1-c rows; this null is intentional and documented in the CSV column headers. Without these metadata columns, a researcher exporting the Register 2 map could not reproduce the ellipse-suppression decision or report it accurately in a paper or slide.
- **Free lists:** ranked terms with salience scores.
- **Heatmap:** the full similarity matrix.

**Permalink:** copies a URL that encodes the current view state (domain, models selected, viz tab, date slider position). Any visitor with the link sees exactly what you were looking at.

**Embed:** copies an `<iframe>` snippet for embedding the current chart in any website.

**Cite this:** opens a modal with citation formatted in APA, MLA, Chicago, and BibTeX. Updates to reflect the current domain and analysis version.

---

## 6. Methodology Page

The methodology page is a first-class deliverable, not an afterthought. It is written by Mark personally — the Coder agent builds the template, Mark writes the prose.

### 6.1 Page Structure

```
1. What is the Latent Structure Benchmark?
   — The corpus lens concept in plain language
   — Why this matters for AI research

2. What is Cultural Domain Analysis?
   — Origins in cognitive anthropology
   — Romney, D'Andrade, Weller, Borgatti: named and cited
   — The three-step protocol: free listing, pile sorting, pile interview
   — Why applying CDA to LLMs is methodologically novel

3. How we collect data
   — The informant metaphor (and its limits)
   — What we record: the InformantRecord concept in plain language
   — Reproducibility: how to replicate any run

4. How we analyze data
   — Co-occurrence matrices
   — MDS: what proximity means and what it doesn't mean
   — Bootstrap uncertainty: why every point has an ellipse
   — Cultural consensus analysis

5. What this measures and what it does not
   — The shape of the model's output distribution under structured CDA elicitation
   — What the numbers (Smith's S, Romney CCM, MDS, Procrustes, OCI) describe:
     output-distribution shape — not cognition, belief, understanding, or cultural consensus
   — Why this is still worth doing: comparative model characterization, drift detection,
     stability under prompt rephrasing, confabulation under blind-spot conditions,
     reproducible public benchmark (per `ARCHITECTURE.md` §1.5.7 / philosophy doc §7)
   — The honest tagline: "LSB measures what frontier LLMs produce when asked to
     categorize, in a way that's reproducible, comparable across models, and
     trackable across time." (Quotable; source: `ARCHITECTURE.md` §1.5)
   — "The mismatch is the finding" framing (`ARCHITECTURE.md` §1.5.2 / §1.5.6)

6. Known limitations
   — English-only v1
   — Prompt sensitivity
   — Alignment confound
   — Corpus opacity
   — The "as-if informant" framing is methodological, not metaphysical

7. How to cite LSB
   — Citation formats
   — Data citation
   — Researcher submission citation
```

### 6.2 Tone

The methodology page is written in plain English, not academic jargon. It assumes a reader who is intelligent and curious but has not read cognitive anthropology. It does not assume the reader will believe the findings — it gives them the tools to evaluate the findings themselves. Every limitation is stated plainly. No defensiveness.

---

## 7. Accessibility Requirements

These are non-negotiable. The Reviewer agent enforces them.

- **Color + shape together:** model origin is encoded in both color and point shape. The MDS plot is interpretable in grayscale.
- **"Read as table" toggle:** every visualization has a toggle that renders the underlying data as an accessible HTML table. (implemented in Phase 6 T8; `ReadAsTableToggle.tsx`; binding visual spec in §12.9)
- **Keyboard navigation:** all interactive controls (sliders, checkboxes, tabs, buttons) are fully keyboard accessible.
- **ARIA labels:** every chart element has appropriate ARIA labels. D3 visualizations must use `role="img"` with descriptive `aria-label` on the SVG container.
- **Focus indicators:** visible focus rings on all interactive elements. Never `outline: none` without a replacement.
- **Minimum contrast:** all text meets WCAG AA contrast ratio (4.5:1 for body text, 3:1 for large text).
- **Screen reader alternative:** each chart has a "Screen reader summary" that provides a plain text description of the key finding and the data in prose form.

---

## 8. Mobile Behavior

The dashboard is desktop-first but mobile-readable. Not mobile-optimized — readable.

- **Control panel collapses** to a bottom drawer on screens narrower than 768px
- **Domain selector** wraps to two lines on mobile, does not scroll horizontally
- **MDS plot** renders at full width with pinch-to-zoom enabled
- **Free list compare** shows maximum 2 columns on mobile (others accessible via horizontal scroll)
- **Sliders** use large touch targets (minimum 44px height)
- **Download buttons** are full-width on mobile

---

## 9. Performance Requirements

- **Initial page load:** under 3 seconds on a 4G connection
- **Chart render:** under 500ms after data fetch completes
- **Domain transition animation:** 400ms, must not drop below 30fps
- **Static JSON files:** maximum 500KB per domain file (gzipped)
- **Bundle size:** maximum 400KB JavaScript (gzipped), excluding visualization libraries
- **Visualization libraries (D3, Plotly):** loaded asynchronously, not blocking initial render

---

## 10. UI/UX Agent Responsibilities

The UI/UX agent is a new member of the development team, sitting alongside the existing Architect / CDA SME / Coder / Reviewer / Tester agents.

**Role:** the UI/UX agent is the design conscience of the frontend. It reviews all component work before the Reviewer sees it, specifically for visual consistency, OWID design fidelity, accessibility compliance, and the three-audience usability test.

**Pipeline position:**
```
Architect → CDA SME → UI/UX agent (for frontend tasks) → Coder → Reviewer → Tester
```

For non-frontend tasks (collection, analysis, schemas), the UI/UX agent is skipped.

**System prompt summary:**
The UI/UX agent grounds every review in four questions:
1. Does this component match the OWID design language as specified in DESIGN_SYSTEM.md?
2. Does a journalist understand this in 30 seconds?
3. Does a researcher have everything they need to reproduce and cite?
4. Does this meet WCAG AA accessibility requirements?

**Verdict format:** same as CDA SME — PASS / PASS-WITH-NOTES / FAIL with specific notes.

**Slack channel:** `#lsb-ui-ux` — the UI/UX agent posts its review verdicts here. Mark monitors this channel for design decisions that require his input (e.g., copy decisions on the methodology page, color choices for new domains, grounding panel layout for a new submission).

---

## 11. Component Inventory

All components to be built, in implementation order:

**Phase 5 (minimum viable dashboard):**
- `DataExplorer.tsx` — the master explorer container
- `VizSwitcher.tsx` — tab bar for switching visualizations
- `MDSPlot.tsx` — primary D3 scatter plot with ellipses
- `ModelSelector.tsx` — checkbox panel with origin badges
- `DomainPicker.tsx` — horizontal pill buttons
- `KeyFinding.tsx` — the lede sentence strip
- `SourceAttribution.tsx` — source line below chart
- `DownloadBar.tsx` — PNG, CSV, permalink, embed buttons
- `CiteModal.tsx` — citation formats modal
- `EmbedModal.tsx` — embed code modal

**Phase 6 (full dashboard):**
- `FreeListCompare.tsx` — side-by-side ranked lists
- `SimilarityHeatmap.tsx` — Plotly heatmap with CI tooltips
- `DriftTracker.tsx` — longitudinal D3 chart with date slider
- `DateSlider.tsx` — scrubbing control for drift view
- `ModelDetailPanel.tsx` — slide-in panel for model detail
- `AccessibilityTableToggle.tsx` — chart → table switch
- `ScreenReaderSummary.tsx` — hidden prose for screen readers

**Methodology page (Phase 6, Mark writes prose):**
- `MethodologyPage.tsx` — long-form article template
- `CitationBlock.tsx` — formatted academic citation component
- `LimitationCard.tsx` — each known limitation as a card

---

## 12. Phase 5 Visual Decisions (v0.4 — 2026-05-09)

These decisions are required by the Phase 5 architect plan and were not covered by v0.3. All are binding on T4–T13 Coder tasks. Originated at the UI/UX agent plan-level review on 2026-05-09.

### 12.1 Page-load reveal animation

A single staggered CSS opacity + translateY cascade on page load is acceptable as page orchestration, not prohibited by the "no decorative animation" rule in §0. OWID itself uses staggered entry on chart load. The rule prohibits hover sparkles, parallax, scroll-triggered reveals, and looping animations — not a one-shot load reveal.

**Binding specification (all constraints required):**
- Total cascade duration: 600ms maximum from first paint to last element fully visible.
- Stagger offset between sequential elements: 80ms maximum.
- Easing: `ease-out` only. No `ease-in-out`, no spring physics.
- Animated properties: `opacity` (0 to 1) and `transform: translateY(8px to 0px)` only. No color, scale, blur, or rotation transitions on load.
- All interactive elements (domain picker, model checkboxes) must be pointer-responsive from first paint even while the cascade is running. The animation does not block interaction.
- The cascade fires once on page load. Domain switches trigger a 200ms fade on the KeyFinding strip only (§3.8); no full-page re-cascade.

### 12.2 Data fetch loading state

While the manifest.json or domain.json fetch is in flight, the page renders Header + Footer with a loading placeholder in the content area.

**Binding specification:**
- Loading text: `"Loading..."` in `--color-text-muted` at `--font-size-base`, in the same horizontal/vertical position as the KeyFinding strip.
- No spinner component. No skeleton shimmer (shimmer is a looping animation, prohibited per §0).
- Fetch error text: `"Could not load data. Refresh the page or check your connection."` in `--color-text-secondary`, same position.
- Neither state is flagged as a defect in the UI. Both are transient informational states, not error indicators.
- The loading and error states occupy the full content area (replacing KeyFinding + DataExplorer + MethodologySummary). Header and Footer remain visible.

### 12.3 VizSwitcher disabled-tab visual treatment

Phase 5 ships VizSwitcher with one active tab (MDS Plot) and three disabled tabs (Free Lists, Similarity, Drift).

**Binding specification (overrides T8 plan spec on focusability):**
- Disabled tab label text: `--color-text-muted`.
- Disabled tabs: `cursor: not-allowed`. The click action is suppressed.
- Disabled tabs are **focusable** (not `tabindex="-1"`). The T8 plan spec saying "not focusable" is superseded by this section. Rationale: WCAG 2.1 SC 2.1.1 requires keyboard users to be able to discover all visible interactive affordances. A disabled-but-visible tab that cannot receive focus is invisible to keyboard-only users.
- Each disabled tab carries `aria-disabled="true"`.
- A tooltip appears on both hover and focus: `"Coming in a future update"`. Do not use "Phase 6" or any version-specific language in user-visible copy; phase numbering is internal vocabulary.
- The active tab (MDS Plot) must be distinguishable from disabled tabs without relying on color alone: the active tab must have a visible non-color indicator (underline, background fill, or border) that the disabled tabs do not.

### 12.4 Model color assignment for >6 models

Phase 5 ships 11 models (family) and 9 models (holidays) simultaneously. The §1.2 palette (v0.4) covers 11 slots; this section specifies the assignment algorithm.

**Assignment algorithm (binding):**
- Sort all model_ids in the current domain result ascending by lexicographic string order.
- Assign palette slot 1 to the first model_id, slot 2 to the second, and so on.
- The assignment is stable: the same model_id always receives the same slot regardless of which other models are visible. Slots 1–6 use `--color-model-1` through `--color-model-6`; slots 7–11 use `--color-model-7` through `--color-model-11`.
- Colors are never reused within a single chart. If future phases add a 12th model, extend the palette further at that time with a Phase 6 design system update.
- `DataExplorer.tsx` owns palette assignment. It produces a `Map<model_id, cssColorValue>` at mount (before any child renders) and passes it as a prop to MDSPlot, ModelSelector, and Legend. No child component computes its own model color directly from model_id.

All five extended palette slots (`--color-model-7` through `--color-model-11`) pass WCAG AA 3:1 graphical contrast on white (#ffffff). Verified ratios: slot 7 (#d35400) ≈ 4.5:1; slot 8 (#1a5276) ≈ 7.2:1; slot 9 (#7d3c98) ≈ 5.0:1; slot 10 (#148f77) ≈ 4.0:1; slot 11 (#9a7d0a) ≈ 3.96:1. The v0.4 value for slot 11 (`#b7950b`) was corrected to `#9a7d0a` at v0.4.1 after the T4 per-commit review found it computed to ~2.89:1.

### 12.5 Embed mode (chrome suppression via ?embed=true)

The `?embed=true` URL parameter suppresses page chrome for iframe embedding.

**Binding specification:**
- Detection: `App.tsx` reads `new URLSearchParams(window.location.search).get('embed') === 'true'` on mount. The parameter key is `embed`.
- In embed mode: render only the `DataExplorer` component. Suppress Header, Footer, ArticleHeader, KeyFinding, MethodologySummary, and DownloadBar.
- The DataExplorer has no outer margin or padding in embed mode (full bleed within the iframe viewport).
- In embed mode: PNG and CSV download buttons are shown (useful for embed consumers). Permalink and Embed buttons are hidden.
- The embed page must include a `<title>` tag describing the view (e.g., `"Cognitive Structure Lab — Family domain — MDS Plot"`).
- The SVG container retains its `role="img"` and `aria-label` in embed mode.
- **Security prerequisite (T12 gate):** `apps/dashboard/public/_headers` currently specifies `frame-ancestors 'none'`. The embed mode `<iframe>` cannot function without a `frame-ancestors` relaxation for the embeddable path. This is a security decision. Before T12 can pass, the Coder must flag this to the Reviewer; the Reviewer must approve the `_headers` change per `SECURITY_AND_HARDENING.md` before it is committed. The Coder does not modify `_headers` unilaterally.

### 12.6 Phase 5 deferral of "Read as table" toggle — CLOSED (Phase 6 T8)

DESIGN_SYSTEM.md §7 requires a "Read as table" toggle on every visualization. This section recorded the Phase 5 deferral; T8 implements the §7 binding for MDS, FreeList, and Similarity visualizations.

**Status:** Deferral closed by Phase 6 T8 (2026-05-12). The §7 requirement is now fully satisfied for all three active visualizations. See §12.9 for the binding visual specification.

**Phase 5 SVG aria-label posture (retained):** The MDSPlot SVG container continues to carry a descriptive `aria-label` per T6/T13 binding. This minimum posture remains intact; T8 adds the full table toggle and ScreenReaderSummary on top of it.

**Forward-compatibility note:** When T4 (DriftTracker) ships in a future phase, the drift viz will add a fourth table renderer using T8's pattern (toggle + DriftTable + driftScreenReaderSummary). The T8 implementation provides the structural primitives (ReadAsTableToggle, ScreenReaderSummary) that the drift table will reuse.

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

---

### 12.8 SimilarityHeatmap cell-text contrast specification (v0.4.5 — T5, 2026-05-12)

The SimilarityHeatmap uses alpha-blended cell backgrounds: `rgba(44, 62, 80, similarity)` composited over white (#ffffff). This creates a continuous background-darkness gradient from near-white (similarity ≈ 0) to near-opaque dark (similarity ≈ 1). Standard dark text tokens fail WCAG AA 4.5:1 across the mid-range of this gradient. This section specifies the correct contrast-switch rule and the component-scoped token required to pass WCAG AA in both shipped domains.

**New token (add to `apps/dashboard/src/styles/tokens.css`):**

```css
/* SimilarityHeatmap cell text — pure black required for WCAG AA compliance
   across the dark-text arm of the alpha-blend gradient. See DESIGN_SYSTEM.md §12.8. */
--color-heatmap-cell-text-dark: #000000;
```

**Contrast-switch threshold (binding — overrides T5 plan §2.2 value of 0.5 and fallback of 0.55):**

```ts
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73;
// WCAG AA rationale (2026-05-12 UI/UX verdict):
// rgba(44,62,80,sim) composited on white gives background luminance:
//   sim=0.51 → L≈0.356 → white text 2.59:1 FAIL
//   sim=0.55 → L≈0.322 → white text 2.82:1 FAIL
//   sim=0.73 → L≈0.183 → white text 4.50:1 PASS (threshold)
//   sim=0.73 → L≈0.183 → black text 4.66:1 PASS (threshold)
//   --color-text-primary (#2c3e50, L≈0.060) passes only at sim≤0.40;
//   holidays.json min off-diagonal ≈ 0.45 (fails dark text).
```

**Cell text color selection (binding):**

```ts
textFill = similarity > HEATMAP_TEXT_SWITCH_THRESHOLD
  ? "var(--color-background)"                  // white, passes ≥4.5:1 at similarity > 0.73
  : "var(--color-heatmap-cell-text-dark)"      // black, passes ≥4.66:1 at similarity ≤ 0.73
```

**Diagonal cells** (similarity = 1.0) always receive white text (1.0 > 0.73).

**Why pure black, not `--color-text-primary`:** `--color-text-primary` (#2c3e50, relative luminance ≈ 0.060) only achieves 4.5:1 contrast on backgrounds lighter than approximately similarity = 0.40. Both shipped domains have off-diagonal cells in the 0.40–0.73 range (holidays.json minimum ≈ 0.45; family.json minimum ≈ 0.50). Pure black (L = 0) passes 4.66:1 at the threshold and improves monotonically for lighter backgrounds.

**Scope:** `--color-heatmap-cell-text-dark` is used only in `SimilarityHeatmap.tsx`. No other component references it.

---

### 12.9 ReadAsTableToggle + ScreenReaderSummary visual specification (v0.4.6 — T8, 2026-05-12)

Phase 6 T8 implements the §7 "Read as table" toggle and the §7 ScreenReaderSummary for all three active visualizations (MDS, FreeList, Similarity).

**Components:**
- `ReadAsTableToggle.tsx` — the toggle button primitive.
- `ScreenReaderSummary.tsx` — the visually-hidden prose renderer.
- `MdsTable.tsx`, `FreeListTable.tsx`, `SimilarityTable.tsx` — table renderers.
- `src/copy/screen_reader_summaries.ts` — single source of truth for all LSB-authored copy.

**U1 (BINDING — WAI-ARIA 1.2 §6.6.5 DOM-presence requirement):**

The table container `<div id={tableContainerId}>` is ALWAYS rendered in the DOM. `aria-controls` on the toggle button therefore always references an existing element.

When `readAsTable === false`: `aria-hidden="true"` + `display: none` on the container.
When `readAsTable === true`: container visible, viz element hidden (`aria-hidden` + `display: none`).

Implementation: Option A (always-present container). The Coder chose this option at T8.

**U2 (BINDING — WCAG 1.4.11 non-text contrast):**

A text-label change alone (rest → pressed) does not satisfy WCAG 1.4.11 3:1 non-text contrast. The following CSS rules are required and are binding in `read-as-table.css`:

```css
.read-as-table-toggle__button[aria-pressed="true"] {
  border: 2px solid var(--color-info);
  padding: calc(var(--space-2) - 2px) calc(var(--space-3) - 2px);
}
.read-as-table-toggle__button[aria-pressed="false"] {
  border: 2px solid transparent;
}
```

`--color-info` (#3360a9) on white ≈ 7.3:1 (WCAG 1.4.11 PASS). The transparent rest-border prevents layout shift. Padding compensation (-2px on each side) maintains the same visual box size in both states.

**ScreenReaderSummary placement (binding):**
- Always rendered immediately after the `<h2 className="sr-only">` bridge in each viz component's root.
- Present in both visualization mode and table mode — screen-reader users get the summary regardless of toggle state.
- Text is the output of the corresponding programmatic template function (not `generated_lede`).

**SR template boundary (CDA SME S11 binding):**
- `generated_lede` (per-domain finding) — used only in `ArticleHeader.tsx`. Not reused in any SR template.
- SR templates (per-viz structural summaries) — live in `src/copy/screen_reader_summaries.ts`. Deterministic, no LLM calls.

**`.sr-only` CSS class:** reused from `app.css` (established at T5/T7). No new visually-hidden class introduced by T8.

**Button labels (CDA SME §3 APPROVED verbatim):**
- Rest state: `"Read as table"`
- Pressed state: `"Show visualization"`

**Table captions (CDA SME §4 binding verbatim):** see `src/copy/screen_reader_summaries.ts`.

**R10 column adjacency (binding):**
- MdsTable: ellipse columns (semi-major, semi-minor, rotation, n_bootstrap) adjacent to x/y in each row.
- FreeListTable: inclusion-frequency column adjacent to Salience (CSI) in each row.
- SimilarityTable: 95% CI low / high adjacent to Similarity in each row.

**Follow-up: T14 doc-sweep** should wire a methodology-page link from the SimilarityTable caption's "no bootstrap interval available" phrase (or via a `?` affordance) to the section of the methodology page that explains the null-CI mechanism. T8 ships with the caption as plain text per Phase 6 minimum-viable surface posture.

---

*End of DESIGN_SYSTEM.md v0.4.6. This document is a living specification — update it before building any new component that requires a visual decision not covered here.*

*Binding rule: no visual decision is made by the Coder agent alone. If DESIGN_SYSTEM.md does not cover a case, the UI/UX agent resolves it before the Coder proceeds.*
