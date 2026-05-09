# Latent Structure Benchmark (LSB) — Design System & UI Specification

**Document name:** DESIGN_SYSTEM.md  
**Version:** v0.4  
**Status:** Draft — for review by Mark and Opus Architect agent  
**Audience:** UI/UX Agent, Coder agent, Reviewer agent, Mark  
**Companion docs:** `ARCHITECTURE.md` (v0.7+), `CLAUDE.md`

**This document is binding on all frontend work.** The Reviewer agent must reject any component that contradicts it. The UI/UX agent owns this document and must be consulted before any visual decision is made by the Coder agent.

**Changelog:**
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
--color-model-11: #b7950b;   /* extended palette — dark gold */
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
--color-text-secondary:  #7f8c8d;   /* captions, labels */
--color-text-muted:      #bdc3c7;   /* disabled states, placeholders */
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
- **"Read as table" toggle:** every visualization has a toggle that renders the underlying data as an accessible HTML table.
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

All five extended palette slots (`--color-model-7` through `--color-model-11`) pass WCAG AA 3:1 graphical contrast on white (#ffffff). Reviewer verifies with WebAIM Contrast Checker or equivalent before passing T4.

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

### 12.6 Phase 5 deferral of "Read as table" toggle

DESIGN_SYSTEM.md §7 requires a "Read as table" toggle on every visualization. `AccessibilityTableToggle.tsx` is listed as a Phase 6 component in §11 and is explicitly deferred by the Phase 5 plan.

**Ruling:** The deferral is accepted. The §7 requirement applies at Phase 6 completion, not as a Phase 5 gate.

**Minimum viable Phase 5 screen-reader posture (binding, enforced at T6 and T13):**
- The MDSPlot SVG container must carry a descriptive `aria-label`. Required format: `"MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."` This gives screen reader users the key finding without requiring the full table toggle.
- The Reviewer does not reject T13 for absence of `AccessibilityTableToggle.tsx`.
- The Reviewer does reject T6 for absence of a descriptive `aria-label` on the MDSPlot SVG container. This is the minimum viable posture.

---

*End of DESIGN_SYSTEM.md v0.4. This document is a living specification — update it before building any new component that requires a visual decision not covered here.*

*Binding rule: no visual decision is made by the Coder agent alone. If DESIGN_SYSTEM.md does not cover a case, the UI/UX agent resolves it before the Coder proceeds.*
