# Latent Structure Benchmark (LSB) — Design System & UI Specification

**Document name:** DESIGN_SYSTEM.md  
**Version:** v0.3  
**Status:** Draft — for review by Mark and Opus Architect agent  
**Audience:** UI/UX Agent, Coder agent, Reviewer agent, Mark  
**Companion docs:** `ARCHITECTURE.md` (v0.7+), `CLAUDE.md`

**This document is binding on all frontend work.** The Reviewer agent must reject any component that contradicts it. The UI/UX agent owns this document and must be consulted before any visual decision is made by the Coder agent.

**Changelog:**
- **v0.3** (post-PR-A UI/UX review, 2026-04-20) extends §3.3.5 with binding implementation requirements for the Register 1 annotations on Register 2 points: R1-c stroke width raised to 3px (WCAG AA fix for the orange/green palette slots at 10px marker size); R1-b dashed stroke specified at 100% model color opacity (only the fill is at 60%); tooltip copy for R1-c de-jargonized (schema identifiers moved to data dictionary + methodology page); legend marker-sample requirement added (text tags alone fail WCAG); all-deterministic edge-case copy specified as a named lede case; OCI low-concentration threshold config constant location specified at `apps/dashboard/src/config/analysis.ts`; §7 shape-encoding ambiguity clarified (model points remain filled circles; baseline markers use ★/◆; R1-c introduces state-encoded shape, not origin-encoded). Extends §5 CSV export spec to include `oci`, `deterministic_output`, `r1_state` columns. Mark-level decision: hollow square (◻) vs hollow triangle (△) for R1-c marker — UI/UX recommends △ (no SVG collision with selected/hover state); pending Mark's sign-off before Coder implements `MDSPlot.tsx` R1-c rendering. No changes to design tokens, color palette, or page architecture.
- **v0.2** folds the multi-baseline-and-ungrounded-as-normal framing from `ARCHITECTURE.md` v0.7 §1.5.5 / §3.2 / §4.2.5 into the design system. The grounding section (§4) now leads with the explicit statement that **ungrounded is a normal first-class state for any domain, not a degraded fallback**, and that **a domain can carry zero, one, or many human baselines simultaneously** (published, researcher-submitted, or both). Updates §3.3 to reframe the four "Mode" rows as the four grounding-display *states* (matching `ARCHITECTURE.md` §4.5 terminology) and removes language that implied grounding was the default and ungrounded the exception. Updates §3.7 model selector panel copy to put the "Submit your data" affordance on equal footing with the baseline checkboxes rather than as a footer link. Updates §3.8 key finding conditional behavior to be explicit that the comparative-only finding is fully equivalent in status, not a degraded form. Updates §4.1 State 0 copy and label so it reads as "this domain is studied model-to-model" rather than as a "no baseline available yet" placeholder. Tightens §4.3 submission UI copy to emphasize that LSB exists *to* connect to the human CDA research community, not as a one-way data publisher. Updates §6.1 methodology page section 5 outline to lead with the multi-baseline framing and the contribution invitation. Adds a §4.4 cross-reference note pointing at `ARCHITECTURE.md` §4.2.5 (data layer) and §3.2 `GroundingRef` (schema). No design tokens, no component additions, no changes to the page architecture or accessibility requirements.
- v0.1 initial draft.

---

## 0. Design Philosophy

The LSB dashboard is a **scientific publication, not a product.** It is modeled explicitly on the Our World in Data (OWID) design language — specifically their Data Explorer pattern. Every design decision is made in service of three audiences arriving at the same URL simultaneously:

- **Journalists** — need to understand the finding in 30 seconds and export a shareable image
- **AI engineers** — want to filter models, compare results, and understand methodology
- **Researchers** — need to reproduce findings, access raw data, and contribute their own human CDA data alongside the model results. LSB exists in part *to* connect to the human CDA research community; the researcher submission path (§4.3) is a first-class affordance, not an afterthought, and the design language must read as an open scientific instrument rather than a closed publication.

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
/* Additional models use a generated palette — never reuse colors within a chart */

/* Origin encoding (secondary, used alongside model colors) */
--color-origin-us: #3360a9;  /* US-origin models */
--color-origin-eu: #27ae60;  /* EU-origin models */
--color-origin-cn: #c0392b;  /* China-origin models */

/* Human baseline markers */
--color-baseline-published:   #2c3e50;   /* black-ish — published data (Romney et al.) */
--color-baseline-researcher:  #7f8c8d;   /* gray — researcher-submitted data */

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
│  — human baseline markers        │  ☐ Qwen         [CN] ●  │
│  — interactive hover tooltips    │  ☐ Mistral      [EU] ●  │
│  — zoom and pan                  │  ☐ Llama 3      [US] ●  │
│                                  │  [Show all 12 models]    │
│                                  │                          │
│                                  │  ─────────────────────   │
│                                  │  Human baselines         │
│                                  │  ☑ Romney 1996 (★)      │
│                                  │  ☐ Tanaka 2026 (◆)      │
│                                  │  [+ Submit your data]    │
│                                  │                          │
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
| MDS Plot | `MDSPlot.tsx` | D3 | Primary viz — models as points in cognitive space |
| Free Lists | `FreeListCompare.tsx` | Custom | Side-by-side ranked term lists per model |
| Similarity | `SimilarityHeatmap.tsx` | Plotly | Model×model similarity matrix |
| Drift | `DriftTracker.tsx` | D3 | Longitudinal corpus lens shift over time |

### 3.3 MDS Plot — Detailed Specification

The MDS Plot is the signature visualization. It is the first thing a visitor sees.

**Visual elements, in z-order (back to front):**

1. **Grid lines** — light gray (#dde1e7), no axis labels on the grid itself
2. **Axis labels** — "MDS Dimension 1" and "MDS Dimension 2" in small muted text, with a footnote explaining these are relative dimensions, not named scales
3. **Confidence ellipses** — one per model, filled at 8% opacity of model color, stroked at 25% opacity. Rendered before points so points sit on top.
4. **Human baseline ellipses** — only when raw subject data is available. Dashed stroke, no fill. Published baseline uses `--color-baseline-published`, researcher baseline uses `--color-baseline-researcher`.
5. **Human baseline markers** — published baseline: black star (★), larger than model points. Researcher baseline: gray diamond (◆). Both have a white halo stroke to separate from background.
6. **Model points** — filled circles, 10px radius, model color. White 2px stroke border.
7. **Model labels** — short name (e.g., "Claude", "GPT-4o") in 12px Lato, positioned to minimize overlap using a label offset algorithm. Never overlap a point.
8. **Hover tooltip** — appears on point hover. Shows: full model name, provider, origin, collection date, top 5 free list terms for this model in this domain, distance to human baseline if available.

**Interactions:**
- Hover on point → tooltip appears, ellipse brightens
- Click on point → detail panel slides in from right
- Hover on ellipse → tooltip shows bootstrap parameters (n_bootstrap, CI level)
- Zoom with scroll wheel, pan with drag
- Double-click → reset zoom
- Hover on human baseline marker → tooltip shows citation, n_informants, population, year

**Conditional rendering by grounding state:**

The MDS plot supports four grounding states, defined identically to `ARCHITECTURE.md` §4.5 and §4 below. State 0 (no human baselines) is a normal, first-class state for any domain — not a degraded fallback. A domain may have zero, one, or many baselines simultaneously (`DomainResult.groundings` is a list per `ARCHITECTURE.md` §3.2), and the MDS plot must render each state without ever implying the domain is incomplete or broken.

| State | Baseline marker(s) | Baseline ellipse(s) | Legend entry |
|---|---|---|---|
| **State 0** — No baselines | None rendered | None rendered | "This domain is studied model-to-model. Have human CDA data for [domain]? **Submit yours →**" — never reads as a missing-content placeholder |
| **State 1** — Published only | Black star (★) | Dashed, only when raw subject data is available | "Human baseline — Romney et al. 1996, n=122, US college students" |
| **State 2** — Researcher only | Gray diamond (◆) | Dashed, only when raw subject data is available | "Researcher baseline — [Name], [Institution], [Year], n=[N]" |
| **State 3** — Multiple baselines | All applicable markers visible together | All available ellipses rendered | One legend entry per baseline, visually grouped, with a short note: "Multiple human baselines — each reflects a different population." |

### 3.3.5 Register 1 (OCI) annotations on Register 2 points — added post-F1 SME review

The Register 2 MDS plot (§3.3 above) is the between-model map. Per the three-register framework in `ARCHITECTURE.md` §4.2.0 and the Option-2 annotated-uncertainty contract in `docs/BOOTSTRAP_DESIGN.md`, each model's Register 2 point carries Register 1 (within-model) annotation so a reader can see the model's output concentration alongside its cross-model position — not baked into the ellipse, which would overstate precision.

The following annotations apply to every Register 2 point; they are independent of the grounding state table above and compose with it.

**Three Register 1 states, keyed to `DomainResult.within_model_results[model_id]`:**

| State | Condition on `WithinModelResult` | Register 2 rendering |
|---|---|---|
| **R1-a — Typical concentration** | `deterministic_output == False` AND `oci >= 3.0` | Standard Register 2 ellipse (§3.3 item 3), full opacity. OCI badge in the hover tooltip: "OCI: 4.2" with a one-line explanation on first hover. |
| **R1-b — Low concentration** | `deterministic_output == False` AND `oci < 3.0` | **No confidence ellipse rendered.** The point is rendered with a dashed 2px stroke (not solid) and reduced 60% opacity on the fill. Tooltip surfaces: *"Position uncertain — this model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."* Legend entry under the point has a small italic "low OCI" tag. The final OCI threshold for this state is provisional at 3.0 pending the Phase 4b saturation analysis; see `docs/SME_REVIEW.md` open question 1. |
| **R1-c — Deterministic output** | `deterministic_output == True` | **Dedicated visual marker — not suppression.** The Register 2 point is rendered as a hollow square (◻) instead of a filled circle, same color as the model, with a 2px solid stroke. **No ellipse** (the model produced zero variance; there is nothing to bootstrap). Tooltip surfaces: "Deterministic output — this model produced near-identical pile-sort structure on every run (OCI sentinel; ConsensusType = DETERMINISTIC). See methodology page §[Three registers] for why this is the *least* informative case, not the most." Legend entry carries a visible "deterministic" tag. The mismatch is the finding — the visual treatment flags that the model's zero variance is a property of the architecture (most likely a future deterministic architecture: neurosymbolic systems, zero-temperature models), not a confidence signal. |

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

1. **Shape decision for R1-c — Mark-level, unresolved.** The shape for the R1-c marker is subject to Mark's sign-off before the Coder implements it. Two candidates:
   - **Hollow square (◻)** — original spec. Risk: may be confused with "selected" or "hover" state in SVG rendering at small size.
   - **Hollow triangle (△)** — UI/UX recommendation. Unambiguous, no collision with existing marker vocabulary, legible at 10px.
   The Coder pauses on R1-c marker shape until Mark records a decision here. All other R1 requirements below may proceed.

2. **R1-c stroke width: 3px (binding).** The 2px value in the table above is superseded. R1-c markers use a **3px solid stroke at 100% model color opacity** across all palette slots. Rationale: at 10px marker size, a 2px hollow stroke produces insufficient ink coverage for the orange and green palette slots (`--color-model-3`, `--color-model-4`) to pass WCAG AA 3:1 graphical-object contrast on white background.

3. **R1-b dashed stroke opacity: 100% model color (binding).** The 60% reduced opacity applies to the fill only, not the stroke. The dashed stroke is rendered at 100% model color opacity so it passes WCAG AA contrast independently of the fill.

4. **Legend entries must include rendered marker samples (binding).** The legend entry for each R1 state must render a small (14px) visual sample of the actual marker — text tags alone do not satisfy WCAG non-text contrast:
   - R1-a: solid filled circle in model color (standard legend dot)
   - R1-b: dashed-stroke circle in model color with lighter interior, labeled "low output concentration"
   - R1-c: hollow [square/triangle — pending Mark's shape decision] in model color, labeled "deterministic output"
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

**Human baselines section:**
- Separated from models by a labeled divider: "Human baselines"
- Each available baseline shown as a checkbox with its marker shape (★ or ◆), source label, and year
- Multiple baselines per domain are fully supported and listed together — published and researcher submissions appear in the same list, distinguished by their marker shape
- **"+ Submit your data"** appears as a persistent action affordance at the bottom of the section in *every* state (with baselines or without). It reads as an invitation to contribute, not as a fallback link. Visual treatment: same weight as a checkbox row, dashed border on the icon to distinguish it from data rows.
- When the current domain has no baselines (State 0 per §3.3 and §4.1), the section shows a short, neutral line above the submit affordance: "This domain is studied model-to-model. Researcher contributions welcome." — *not* "no data available" or "missing baselines" or "no baselines yet" or anything that frames the absence as a defect or as an interim state pending arrival.

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

**Conditional behavior** (driven by `DomainResult.groundings` and `selected_baseline_id` per `ARCHITECTURE.md` §3.2):

- **State 0 — no baselines:** finding is comparative ("Claude and GPT-4o organize family terms most similarly; DeepSeek diverges sharpest..."). This is a complete, equivalent-status finding — not a placeholder for a richer one. The lede generator (`ARCHITECTURE.md` §4.2.3) is given the same instructions for State 0 as for any other state and produces declarative, confident copy.
- **State 1 — published baseline:** finding may reference the human baseline ("Claude sits closest to the 1996 Romney US human consensus on family terms...").
- **State 2 — researcher baseline:** finding may reference the researcher baseline with attribution ("...closest to the [Researcher] [Year] [Population] consensus...").
- **State 3 — multiple baselines:** finding references whichever baseline produces the most narratively significant result for the current model selection. The user can toggle the "selected baseline" via the Grounding Selector (§3.7) and the finding regenerates from the precomputed alternatives in the static JSON.

Under no circumstances does the comparative-only finding (State 0) read as a degraded form of the grounded finding. They are different findings, both first-class.

---

## 4. Grounding Display Specification

**Binding framing (added v0.2, mirrors `ARCHITECTURE.md` v0.7 §1.5.5):** Human grounding is **per-domain optional and multi-baseline by default**. A domain may carry zero, one, or many human baselines simultaneously. Each of these is a normal, first-class state:

- **Zero baselines (State 0)** is a normal state. Many LSB domains will never have a published human CDA dataset and may never receive a researcher submission. The dashboard renders these domains as fully complete model-to-model comparisons. The interface must never imply that an ungrounded domain is broken, missing data, awaiting completion, or in any way less valid than a grounded one. The work LSB does on an ungrounded domain — comparing how different models organize the same vocabulary — is the floor of the project's contribution and stands on its own.
- **One baseline (States 1 or 2)** is a normal state. Family terms in v1 has Romney 1996 (published, State 1). Other domains may launch with a single researcher submission instead.
- **Many baselines (State 3)** is a normal state. Family terms could have Romney 1996 *and* a hypothetical Tanaka 2026 Kyoto kinship submission at the same time. These are not in tension — they are two different human populations whose categorical structure is itself an interesting comparison.

The data layer is designed for all of this from Phase 1: `DomainResult.groundings` is a `list[GroundingRef]` (`ARCHITECTURE.md` §3.2), not a singleton; `data/grounding/{domain}/{baseline_id}/` is a multi-baseline directory layout (`ARCHITECTURE.md` §4.2.5); the four display states below are driven directly by the contents of that list with no special-casing for the empty case.

**No empty states. No broken layouts. No placeholder content that looks like missing content.** State 0 is an active state with its own copy and its own affordances, not a stub waiting for data to arrive.

### 4.1 The Four Grounding States

**State 0 — No human baselines for this domain (a normal state)**

Many LSB domains live here permanently and that is fine. The MDS plot shows model points and ellipses with no human reference markers. The Human baselines section of the model selector (§3.7) shows:

```
This domain is studied
model-to-model.

Researcher contributions
welcome.

+ Submit your data
```

The key finding (§3.8) is comparative and complete in its own right — it does not gesture at an absent baseline or read as the comparative half of a missing whole. Under no circumstances does any visible copy in State 0 say "no human baseline available," "missing baseline data," "awaiting human grounding," "ungrounded," or any phrasing that frames the absence as a defect rather than a property of the domain.

**State 1 — One published baseline (a normal state)**

Family terms ships in v1 in this state with Romney 1996. Black star (★) marker appears in the MDS plot. Legend entry reads:
"★ Human baseline — Romney, Boyd, Moore et al. (1996), n=122, US college students, 1990s"

Clicking the star opens the Grounding Detail Panel (see §4.2). The Human baselines section of the model selector still shows the persistent "+ Submit your data" affordance — additional baselines are always welcome alongside an existing one.

**State 2 — One researcher-submitted baseline (a normal state)**

A domain may launch with a researcher submission and no published baseline, or accumulate a researcher submission later. Gray diamond (◆) marker appears. Legend entry reads:
"◆ [Researcher Name], [Institution] ([Year]), n=[N], [Population]"

Clicking opens the Grounding Detail Panel with full researcher attribution. The "+ Submit your data" affordance is again persistent.

**State 3 — Multiple baselines (a normal state)**

Two or more baselines visible at once: published + researcher, multiple published (rare but possible — same domain studied by independent groups), or multiple researcher submissions from different populations. All applicable markers visible together. The legend has one entry per baseline, visually grouped, with a short note: "Multiple human baselines available — each reflects a different population." The Grounding Selector (§3.7) lets the user toggle which baseline is the *selected* one for the current view; the key finding (§3.8) regenerates from precomputed alternatives. Non-selected baselines remain visible on the MDS plot at reduced visual weight (lower opacity on the marker, no ellipse) so the user can see all baselines at a glance while one is foregrounded.

### 4.2 Grounding Detail Panel

Slides in from the right when a baseline marker is clicked. Same panel pattern used for model detail.

**Published grounding panel:**
```
★ Human Baseline

Romney, Boyd, Moore, Batchelder & Brazill (1996)
Culture as Shared Cognitive Representations
PNAS 93(10), 4699–4705
DOI: 10.1073/pnas.93.10.4699
[Full text at PubMed Central ↗]

Population: n=122, US college students, early 1990s
Method: Pairwise similarity judgments
Item set: [list of items in the intersection]
Intersection with LSB item set: 18 of 25 items (72%)

Distance to nearest model: 0.23 (Claude Opus)
Distance to farthest model: 0.71 (DeepSeek-V3)

Note: Uncertainty ellipse not available — published
aggregate only, individual subject data not provided.

[Download grounding data] [Cite this source]
```

**Researcher grounding panel:**
```
◆ Researcher Baseline

[Researcher Name], [Institution]
[Project title if available]
[Year] · [Link to project/publication ↗]

Population: n=[N], [Population description]
Method: Pile sort (Romney protocol)
Collection date: [Date]
IRB: [Yes/No/Not applicable]
Item set: [items]
Intersection with LSB item set: [N] of [total] ([%])

[uncertainty ellipse line — if raw data submitted]
Bootstrap ellipse available (n=[N] subjects resampled
B=500 times).

Note: This dataset was submitted by an independent
researcher. LSB has verified format but not
independently replicated the collection.

[Download submitted data] [Cite researcher's work]
[Submit your own data →]
```

### 4.3 Data Submission UI

The "Submit your data" entry point appears in three places — and is persistent in all four grounding states, never hidden behind an "if no baseline" condition:

1. The model selector panel's Human baselines section (§3.7), persistent in all four states
2. The Grounding Detail Panel footer (§4.2), shown alongside any existing baseline
3. The methodology page, in the human grounding section (§6.1)

Clicking it opens a modal:

```
Submit Human CDA Data

LSB exists in part to connect AI corpus-lens findings
to the broader CDA research community. If you have
collected pile sort or free list data from human
subjects for any domain LSB measures — or any domain
LSB doesn't measure yet — you can submit it for
display alongside the model results.

Your data will appear on the dashboard with full
attribution. You retain all rights to your data.
LSB redistributes under CC-BY-4.0 with attribution.

Requirements:
• Raw pile sort decisions per subject (CSV format),
  or an aggregate co-occurrence matrix at minimum
• Subject count and population description  
• Collection method and protocol
• Your name, affiliation, and contact
• Ethics approval documentation if applicable

[Download submission template →]
[Open submission form on GitHub →]

Questions? [Contact us]
```

The modal copy is deliberately phrased to invite contributions for domains LSB does not yet measure, not only the ones it does. A submission for a new domain triggers an Architect-agent decision about whether to add the domain to the v1 slate or queue it for v2; either way, the researcher's data is acknowledged, not refused.

### 4.4 Cross-references to ARCHITECTURE.md

The data layer that backs everything in §4 lives in `ARCHITECTURE.md` v0.7. The design system assumes that document and does not duplicate it. Specifically:

- **`ARCHITECTURE.md` §1.5.5** — the binding scientific framing for grounding: per-domain optional, multi-baseline by default, ungrounded as a normal first-class state, researcher submissions as a v1 feature.
- **`ARCHITECTURE.md` §3.2** — the `GroundingRef` schema (with `baseline_id`, `baseline_kind`, submitter fields, IRB status, population description, item-set alignment fields) and the `DomainResult.groundings: list[GroundingRef]` plus `selected_baseline_id` fields that drive every state in §4.1 above.
- **`ARCHITECTURE.md` §4.2.5** — the `data/grounding/{domain}/{baseline_id}/` directory layout, the published vs researcher kinds, the full v1 GitHub-PR researcher submission workflow (validation in CI, CDA SME review, Mark merges), and the citation discipline rules.
- **`ARCHITECTURE.md` §4.5** — the architectural contract that every `DomainResult` carries enough information to render any of the four states without an extra fetch, and the rule that `DESIGN_SYSTEM.md` is authoritative for visual decisions while `ARCHITECTURE.md` is authoritative for data and component structure decisions.

If anything in §4 above appears to disagree with `ARCHITECTURE.md`, that is a bug to be flagged on the next architecture pass — not a license for the Coder to invent an interpretation. The UI/UX agent is responsible for keeping the two documents in sync.

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

5. Human grounding
   — Why grounding matters when it's available (relative vs absolute claims)
   — Why ungrounded is also a complete first-class result, not a missing piece
   — A domain may carry zero, one, or many baselines — all equivalent in status
   — Published baselines: Romney et al. 1996 (cited in full), how they were extracted
   — Researcher submissions: how they appear, how they are attributed, how to contribute
   — How to submit: link to the GitHub submission template, the requirements,
     the review process (CDA SME + Mark), the CC-BY-4.0 redistribution terms
   — What "no grounding" means for interpretation — and what it doesn't mean

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
- `GroundingSelector.tsx` — human baseline checkboxes + submit link
- `DomainPicker.tsx` — horizontal pill buttons
- `KeyFinding.tsx` — the lede sentence strip
- `SourceAttribution.tsx` — source line below chart
- `DownloadBar.tsx` — PNG, CSV, permalink, embed buttons
- `GroundingDetailPanel.tsx` — slide-in panel for baseline detail
- `CiteModal.tsx` — citation formats modal
- `EmbedModal.tsx` — embed code modal

**Phase 6 (full dashboard):**
- `FreeListCompare.tsx` — side-by-side ranked lists
- `SimilarityHeatmap.tsx` — Plotly heatmap with CI tooltips
- `DriftTracker.tsx` — longitudinal D3 chart with date slider
- `DateSlider.tsx` — scrubbing control for drift view
- `ModelDetailPanel.tsx` — slide-in panel for model detail
- `SubmitGroundingModal.tsx` — researcher submission modal
- `AccessibilityTableToggle.tsx` — chart → table switch
- `ScreenReaderSummary.tsx` — hidden prose for screen readers

**Methodology page (Phase 6, Mark writes prose):**
- `MethodologyPage.tsx` — long-form article template
- `CitationBlock.tsx` — formatted academic citation component
- `LimitationCard.tsx` — each known limitation as a card

---

*End of DESIGN_SYSTEM.md v0.1. This document is a living specification — update it before building any new component that requires a visual decision not covered here.*

*Binding rule: no visual decision is made by the Coder agent alone. If DESIGN_SYSTEM.md does not cover a case, the UI/UX agent resolves it before the Coder proceeds.*
