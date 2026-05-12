# Phase 6 T8 — Read-as-table toggle + ScreenReaderSummary — Architect Plan

**Save to:** `/opt/lsb-agent/docs/status/2026-05-12-phase6-T8-architect-plan.md`

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T8 only (kickoff §2 T8 — "the 'Read as table' toggle per DESIGN_SYSTEM.md §7 — every viz renders accessible HTML table when toggled; ScreenReaderSummary.tsx for hidden prose descriptions of each chart's key finding. Closes the §7 binding and the §12.6 Phase-5 deferral.").
**Status:** Awaiting CDA SME dispatch (REQUIRED — see §6); then UI/UX light-touch; then Coder dispatch on PASS. T4 (DriftTracker) is deferred so the drift table is out of scope (§5).

---

## §0. Reading list (mandatory before Coder dispatch)

1. `/opt/lsb-agent/CLAUDE.md` §6 (binding rules — especially R10 uncertainty-pairing, R11 no-LLM-imports, R12 SME-gated plans, R13 design system, R14 no-spend-gates), §7 (forbidden vocabulary), §9 (pitfalls 4, 5, 7, 8 — pitfall 8 R10 applies to the HTML-table representation of every point estimate, not just the SVG).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact, including hidden screen-reader prose and table captions), §1.5.4 forbidden vocabulary, §1.5.5 first-class-state framing (empty / R1-b / R1-c rows in tables), §4.5 (R10 binding — applies to HTML-table cells as much as to SVG points).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` v0.4.5 — **§7 (the binding text for this task; closes the deferral), §12.6 (Phase-5 deferral note T8 closes), §12.7 (MethodologySummary precedent — `<section aria-labelledby>` + token-only CSS), §12.8 (SimilarityHeatmap contrast precedent — pure-black token for cell text)**, §1 tokens (no new tokens introduced by T8), §2.1 page architecture (T8 lives inside each viz card, below the SVG, above the existing source attribution).
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T8 + §3 Q7 (the per-viz-vs-explorer-level open question).
5. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T0-architect-plan.md` (precedent — flat HTML-table semantics: `<table>` + `<caption>` + `<th scope>` are already in the T0 codebase via `InspectTable.tsx`; T8 reuses the semantic conventions but **does NOT depend on T0 components** — InspectRoot is the operator surface, T8 is the public-facing surface, and the components must stay separate).
6. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-architect-plan.md` and `2026-05-12-phase6-T7-architect-plan.md` (structural precedents; both are referenced for the cast-through-unknown pattern T8 inherits and for the verdict-format expectations).
7. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md` and `2026-05-12-phase6-T7-cda-sme-verdict.md` (forbidden-vocab spot-check precedent the CDA SME will apply to T8's copy module).
8. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T10-architect-plan.md` §2.4–§2.5 (copy-module-as-single-source-of-truth pattern T8 follows; CDA SME reviews `src/copy/screen_reader_summaries.ts` the same way it reviewed `src/copy/failures_findings.ts`).
9. `/opt/lsb-agent/apps/dashboard/public/data/family.json` and `holidays.json` — the data the tables render. Authority on shape; `data/types.ts` is **not** the authority (see §4).
10. `/opt/lsb-agent/apps/dashboard/src/components/{MDSPlot.tsx, FreeListCompare.tsx, FreeListColumn.tsx, SimilarityHeatmap.tsx, DataExplorer.tsx, VizSwitcher.tsx}` — the three active viz components T8 extends; the integration shape.
11. `/opt/lsb-agent/apps/dashboard/src/components/InspectRoot.tsx` (precedent only — T8 does **not** reuse these components; the public surface and the operator surface are kept separate per the T10 §2.6 ruling on InspectRoot scope).
12. `/opt/lsb-agent/apps/dashboard/src/styles/tokens.css` (existing tokens are sufficient; T8 introduces no new tokens).
13. Memory: `feedback_ui_polish_scope.md` (Phase 6 minimum-viable functional surface; UI/UX gating limited to accessibility floor + R10 + tokens + WCAG AA contrast + mobile), `feedback_visual_inspection.md`, `project_failures_are_findings.md`.

---

## §1. Mark's binding directives + Phase 6 framing

1. **T8 closes the §7 accessibility binding and the §12.6 Phase-5 deferral.** Every active visualization (MDS, FreeList, Similarity) gains a "Read as table" toggle plus a hidden ScreenReaderSummary. The drift viz is out of scope because T4 (DriftTracker) is deferred (kickoff §3 Q3); when T4 ships, a follow-up commit adds the fourth table renderer using T8's pattern.
2. **R10 binding still applies inside the tables (CLAUDE.md §6 R10 / ARCHITECTURE.md §4.5).** The tabular representation of a point estimate must include its uncertainty in an adjacent column. T8 is not exempted from R10 just because the visualization carries the uncertainty visually; the table is the *equivalent* representation, and the equivalence is the requirement.
3. **Phase 6 minimum-viable functional surface** (memory `feedback_ui_polish_scope.md`). Plain `<button>` + plain `<table>`, default tokens, no animation, no microcopy work beyond CDA-SME-approved button label + caption text, no aesthetic blocking by UI/UX. UI/UX reviews accessibility floor + R10 + tokens + WCAG AA contrast + mobile — and that's it.
4. **Forbidden vocabulary (§1.5.4) applies to every LSB-authored string T8 introduces** — button label, ScreenReaderSummary prose, table captions, aria-labels on the toggle button, empty-state strings inside tables. **Data field names from JSON (e.g., `model_id`, `csi`, `f_mentions`, `model_version_returned`) are exempt** because they are not LSB-authored prose.
5. **No new dependencies.** Plain React + TSX + token-driven CSS. Reuses `modelShortName` and the existing `modelColors` prop chain from DataExplorer where relevant (the FreeList table renders a model-color dot in each per-model sub-table header).
6. **No software-side spend gates (CLAUDE.md §6 R14).** N/A to a frontend accessibility task; restated for closure.
7. **`?inspect=...` operator surface (T0) is untouched.** T8 does not extend InspectRoot. The T10 §2.6 ruling stands: InspectRoot's "no `<details>`" / flat-table scope is operator-only; T8's public toggle is a separate concern.
8. **Bundle budget: T8 adds ≤ 8 KB gzipped.** Current ~85 KB; cap 400 KB.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Per-viz toggle vs explorer-level toggle — **per-viz toggle (one toggle inside each viz card).** Resolves kickoff §3 Q7.

**Decision:** Each of the three active viz components (`MDSPlot`, `FreeListCompare`, `SimilarityHeatmap`) carries its own "Read as table" toggle button. State is local to each viz component. Switching tabs in `VizSwitcher` does not preserve the read-as-table state across tabs — each viz starts in its visual mode by default.

**Rationale:**
1. **Matches the binding text in DESIGN_SYSTEM.md §7:** "every visualization has a toggle." The phrasing "every visualization has a toggle" reads as per-viz; an explorer-level toggle would be "the explorer has a toggle." The plain reading of the binding spec governs.
2. **Tables are different shapes per viz.** MDS coordinates table is wide-and-shallow (~11 rows × 8 columns); FreeList table is one-table-per-model (3 tables stacked vertically on a 3-model selection, ~150 rows × 4 columns each); Similarity table is a 3-column flat tuple list (~55 rows). A single explorer-level toggle that swaps the entire viz card to one giant page of three different table shapes is harder for a screen reader to navigate than three independent tables, each contextually paired with its viz. The screen-reader summary for each is also per-viz (§2.5), so the per-viz toggle composes more cleanly.
3. **Trade-off documented.** A journalist who wants tables on *every* viz must click the toggle three times (once per tab). The alternative (a single explorer-level toggle) is more discoverable but introduces three usability costs: (a) a single toggle that affects three different surfaces is non-obvious — the journalist clicks it inside the MDS tab and then doesn't know whether the FreeList tab will also be in table mode without switching tabs; (b) the screen-reader summary placement becomes ambiguous (above which table?); (c) Mark's `feedback_ui_polish_scope.md` posture is "functional, not polished" — surfacing one toggle per viz is functionally honest about the surface boundary.
4. **State location** — each viz component owns its `readAsTable: boolean` state via `useState`. No DataExplorer-level state pollution. No URL persistence — the toggle state is ephemeral (the permalink scheme already encodes domain + models + viz tab per T10; encoding the table-mode flag would require a permalink-scheme migration which is out of scope).

**Forward-compatibility note:** If Mark later wants an explorer-level umbrella toggle, the per-viz primitive components T8 ships are the building blocks — the umbrella becomes a parent that broadcasts to children, not a re-architecture.

### §2.2. Toggle UI placement — **small plain-text `<button>` placed below the visualization SVG / DOM block, left-aligned, above the existing source attribution / DownloadBar area.**

**Decision:** Each viz renders the visualization first, then a single-line `<button>` containing the text `"Read as table"` (CDA SME may revise — `"View as table"` is a candidate) below the SVG/DOM, left-aligned with the visualization's container, using `--font-size-sm` and `--color-text-caption` token at rest. No icon. The button has `aria-pressed="false"` at rest, `aria-pressed="true"` when the table is shown. When pressed, the label changes to `"Show visualization"` (CDA SME may revise) and the toggle re-presses to return to the visualization. The button uses semantic `<button>`, not `<a>` or a div-with-onclick.

**Why below the viz, not in the VizSwitcher row:**
1. The VizSwitcher tab bar is *about* switching visualizations (different data views of different aspects of the same data). The "Read as table" toggle is *about* the *same* viz rendered differently. Putting it in the VizSwitcher conflates two concerns.
2. The DownloadBar row already has CSV / PNG / Permalink / Cite / Embed actions — adding a sixth control there is cluttered and the "Read as table" toggle is conceptually a *view* control, not an *export* control. (The CSV download from the DownloadBar is *export*; the read-as-table is *render mode*.)
3. Placing the toggle directly below the viz keeps the affordance close to the thing it affects, which is the accessibility convention.

**Visual specification:**
- Container: `<div className="read-as-table-toggle">` immediately below the viz's SVG / root DOM, above the SourceAttribution row.
- Button: `<button type="button" aria-pressed={readAsTable} aria-controls={tableId} className="read-as-table-toggle__button">{label}</button>`.
- Label at rest: `"Read as table"`. Label when pressed: `"Show visualization"`. (CDA SME may revise; constants live in `src/copy/screen_reader_summaries.ts` — see §2.5.)
- Text token: `--color-text-caption` (#6c757d, WCAG AA pass at 14px per v0.4.3). Hover/focus: text becomes `--color-text-primary`; underline appears.
- Focus indicator: standard browser focus outline at minimum; `outline: 2px solid var(--color-info); outline-offset: 2px;` if the existing browser default fails WCAG AA 3:1 (per CLAUDE.md §6 R10 visual hygiene). UI/UX confirms at light-touch review.
- Touch target: `min-height: 44px` at `<768px` viewport widths per WCAG 2.5.5; padding `var(--space-2) var(--space-3)`.
- No icon. CDA SME may approve an icon in a future polish pass; T8 is functional.
- No animation on toggle. The viz/table swap is instantaneous.

**`aria-controls`:** points to the `id` of the table container (when the table is rendered) so a screen reader can navigate to the controlled region. The button is always in the DOM; the table is only in the DOM when `readAsTable === true`.

### §2.3. Three table shapes — one per active viz.

The three shapes share a binding rule (§9 R10 in the tables): **every point estimate has its uncertainty in an adjacent column**. Below, each table's columns are listed and the R10 pairing is explicit.

#### §2.3.1. MDS table (rendered by `MdsTable.tsx`)

**Shape:** wide table; one row per model in `selectedModels`; **R1-state column drives uncertainty representation**.

| Column | Source | R10 role |
|---|---|---|
| Model | `modelShortName(model_id)` | label |
| `model_id` (full) | `model_id` | label |
| `x` | `mds_coordinates[model_id][0]`, `.toFixed(3)` | point estimate |
| `y` | `mds_coordinates[model_id][1]`, `.toFixed(3)` | point estimate |
| Uncertainty mode | `display.r1_states[model_id]` (`typical_concentration` / `low_concentration` / `deterministic`) | uncertainty disclosure |
| Semi-major | `mds_uncertainty[model_id].semi_major`, `.toFixed(3)` if R1-a; `—` if R1-b / R1-c | **R10 pairing** for x/y |
| Semi-minor | `mds_uncertainty[model_id].semi_minor`, `.toFixed(3)` if R1-a; `—` if R1-b / R1-c | **R10 pairing** for x/y |
| Rotation (rad) | `mds_uncertainty[model_id].rotation_rad`, `.toFixed(3)` if R1-a; `—` otherwise | **R10 pairing** for x/y |
| n_bootstrap | `mds_uncertainty[model_id].n_bootstrap`; `—` for R1-b / R1-c | provenance |

**R10 binding satisfaction:** every (x, y) row has, in the same row, an adjacent set of cells encoding the ellipse — the same uncertainty the MDS visualization renders graphically. For R1-b / R1-c models, the table renders `—` in the ellipse columns (since the visualization renders no ellipse — binding invariant 1 from `MDSPlot.tsx` header comment); the Uncertainty mode column carries the first-class state per §1.5.5 (no "missing"/"placeholder" framing). The caption (§2.5) explains the `—` semantics in CDA-SME-approved plain English.

**Caption (LSB-authored, CDA-SME-reviewed):** `"Each row shows where a model lands on the MDS map and how confident the bootstrap is in that position. Rows showing '—' under semi-major/semi-minor have no confidence ellipse because their output had low variability (the bootstrap couldn't resample meaningful variance)."` — CDA SME will revise wording; this is the draft.

**Header / scope:** `<table>` with `<caption>` + `<thead><tr><th scope="col">…</th>…</tr></thead>`. Numeric cells use `--font-mono`. Sort order: same as MDS legend (lexicographic `model_id` per §12.4 palette assignment) — stable, deterministic.

#### §2.3.2. FreeList table (rendered by `FreeListTable.tsx`) — **per-model tables, not a long flat table**

**Shape:** one `<table>` per selected model (stacked vertically). Each table renders the model's full sorted-by-CSI term list.

**Decision: per-model tables.** Rationale: (a) the visualization is per-model columns; per-model tables preserve the model-by-model mental model. (b) A single flat table with a `model_id` column would be 4× longer (3 models × ~150 rows = ~450 rows in one screen-reader-navigable table) — screen readers announce table size on entry and a 450-row table announcement is hostile. (c) The shared-term glyph (`★`) from FreeListCompare is preserved per-model; a flat table would need a different cross-model-membership representation.

| Column | Source | R10 role |
|---|---|---|
| Rank | computed (1-indexed in descending-CSI order) | label |
| Term | `sutrop_csi[model_id][i].item` | data |
| Salience (CSI) | `.csi`, `.toFixed(2)` | point estimate |
| Inclusion frequency | `${f_mentions} of ${n_runs} runs` (string) | **R10 pairing** for salience |

**R10 binding satisfaction:** every term's CSI (point estimate) is paired with its run-frequency (the same uncertainty the FreeListCompare bar visualizes). The CDA SME approved the empirical-ratio fallback at T7 review (T7 plan §2.2; CDA SME PASS); T8 carries forward the same fallback in tabular form. **The wording in this table's "Inclusion frequency" column header and caption is CDA SME's binding language — the same vocabulary used in FreeListCompare's aria-label and R10 caption — to preserve cross-surface consistency.**

**Per-table caption:** `"{model short name} ranked terms, ordered by Sutrop salience score. The inclusion-frequency column shows the fraction of collection runs that produced each term."` — CDA SME may revise.

**Sub-table headers:** each table has a `<h4>` (sub-section of the viz's `<h3>`) above its `<caption>` containing `<span style="color: {modelColor}">●</span> {modelShortName}` — model-color dot + short name, matching the FreeListCompare column header pattern. Shared-term glyph (`★`) appended to the term cell when the term is in `sharedTerms` (computed identically to FreeListCompare).

**Empty cases:** Case B (no `sutrop_csi` for model) and Case C (`items: []` and `sutrop_csi: []`) render a single `<p>` below the sub-table heading containing the same caption used in FreeListCompare (`"(no salience data for this model)"` / `"(no terms produced)"`); no `<table>` element is rendered.

#### §2.3.3. Similarity table (rendered by `SimilarityTable.tsx`) — **flat 3-column tuple list, not a matrix table**

**Shape:** a single `<table>` with one row per unique unordered pair of selected models. For N models, `N * (N-1) / 2` rows. Self-similarity (diagonal) rows excluded — they convey no information.

**Decision: flat 3-column.** Rationale: (a) matrix tables (model × model with similarity in cells) are notoriously hard for screen readers to navigate — they require row-and-column-header announcements on every cell, and many screen readers don't handle nested-header tables consistently. (b) A flat tuple table announces row-by-row in a predictable narrative form (`"Claude versus GPT-4o, similarity 0.73, CI 0.65 to 0.81"`). (c) The flat form makes the R10 pairing visually obvious — three adjacent cells per row.

| Column | Source | R10 role |
|---|---|---|
| Model A | `modelShortName(selectedModels[i])` | label |
| Model B | `modelShortName(selectedModels[j])`, `j > i` | label |
| Similarity | `similarity_matrix[matrixI][matrixJ]`, `.toFixed(3)` | point estimate |
| 95% CI low | `similarity_ci[matrixI][matrixJ][0]`, `.toFixed(3)` or `—` if null | **R10 pairing** |
| 95% CI high | `similarity_ci[matrixI][matrixJ][1]`, `.toFixed(3)` or `—` if null | **R10 pairing** |

Index-translation matches the T5 plan §2.8 binding (the same `modelIndexMap` is used). Sort order: by Model A short-name ascending, then Model B short-name ascending — deterministic; matches the visualization's lexicographic-model-id ordering.

**R10 binding satisfaction:** every similarity row has its 95% CI in the same row. Null-CI cells render `—` and the caption explains the first-class state per §1.5.5.

**Caption:** `"Each row compares two models in the current selection. The similarity column shows their pairwise agreement; the 95% confidence interval columns show the range of plausible values from the bootstrap. Rows showing '—' could not produce a confidence interval (one or both models had too few non-degenerate bootstrap resamples)."` — CDA SME may revise.

**Caveat for the CDA SME:** the language `"too few non-degenerate bootstrap resamples"` is the working hypothesis for what null-CI means in the published JSON; the CDA SME confirms or specifies replacement language. If the SME prefers a different formulation, the constant is updated and re-shipped.

### §2.4. State management — **per-viz local `useState`, no DataExplorer state, no URL persistence.**

Each of `MDSPlot.tsx`, `FreeListCompare.tsx`, `SimilarityHeatmap.tsx` adds:

```ts
const [readAsTable, setReadAsTable] = useState<boolean>(false);
```

The toggle button calls `setReadAsTable(v => !v)`. The conditional render swaps the SVG (or DOM block in FreeList's case) for the table component when `readAsTable === true`.

**Rationale:**
1. No DataExplorer state pollution — the table-mode flag is an interaction concern internal to each viz, not a global explorer concern.
2. No URL persistence — the T10 permalink scheme encodes domain + models + viz tab. Adding a `&table=1` parameter is out of scope (would require permalink-scheme migration with its own gates). The trade-off: a permalink to a domain page restores reader-mode visualization, not table-mode. This is acceptable for Phase 6; Phase 7+ may revisit.
3. State resets on viz tab switch and on domain switch (component unmount/remount handles this naturally — `useState` initial value is `false`).

**SVG/DOM hiding when table is active:**
- MDSPlot: the `<svg>` wrapper gets `aria-hidden="true"` and `display: none` (CSS) when `readAsTable === true`. The hidden ScreenReaderSummary (§2.5) remains visible to screen readers.
- FreeListCompare: the columns container gets `aria-hidden="true"` and `display: none`.
- SimilarityHeatmap: same pattern as MDSPlot.

Hiding via `display: none` is preferable to `visibility: hidden` because it removes from the screen-reader tree as well (which is the goal — the table is the screen-reader-navigable alternative; double-announcement is worse than single).

### §2.5. ScreenReaderSummary design — **per-viz programmatic templates from `DomainResultPublished`, NOT lede regeneration.**

**Decision:** `ScreenReaderSummary.tsx` is a `sr-only` (visually hidden, screen-reader-accessible) `<div>` rendered as the first child of each viz component's root, immediately after the existing `<h2 className="sr-only">` bridge (the F-T5-A1 / F-T7-A1 binding). Each summary is composed by a small per-viz template function that reads numeric fields from `domainResult` and produces 2-3 sentences of plain prose.

**Why programmatic templates, not lede regeneration:**
1. The lede generator lives in `cdb_publish` (CLAUDE.md §9 pitfall #2 — explicitly preserved as the only LLM-touching publish-layer component). T8 is dashboard-only; bringing the lede generator into the dashboard would violate `cdb_publish` boundary cleanliness and require an LLM client at the dashboard build step.
2. The existing `generated_lede` field in published JSON (consumed by `ArticleHeader`) is per-domain, not per-viz. Reusing it for the MDS viz's screen-reader summary would be coherent; reusing it for FreeList and Similarity would be incoherent (a domain-level finding is not the same as "what this similarity heatmap shows").
3. Programmatic templates are deterministic, testable, and easy for the CDA SME to vet. The full template surface is small (3 functions, ≤ 200 chars each).

**Three template functions** in `src/copy/screen_reader_summaries.ts`:

```ts
// CDA SME reviews these templates before Coder dispatch.
// Forbidden vocabulary applies. Field names exempt.

export function mdsScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  // Returns 2–3 sentences describing what the MDS viz shows:
  // - How many models are plotted on the map.
  // - The consensus type (concentrated / contested / fragmented per consensus_type).
  // - The number of models with low-concentration or deterministic R1 states
  //   (informs the reader that some ellipses are absent for a reason).
  // Forbidden vocab check: must not say "believes", "thinks", "worldview", "sees".
}

export function freeListScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  // Returns 2–3 sentences describing what FreeListCompare shows:
  // - Number of selected models compared.
  // - Approximate term-count range (min / max items across selected models).
  // - How many terms appear in all selected models (sharedTerms.size).
  // Forbidden vocab check: must not say "models believe", "what models think".
}

export function similarityScreenReaderSummary(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): string {
  // Returns 2–3 sentences describing what SimilarityHeatmap shows:
  // - Number of pairwise comparisons displayed.
  // - The min, max, and median off-diagonal similarity in the current selection.
  // - How many cells have CIs that span the no-agreement value (0.5).
  // Forbidden vocab check: must not say "agrees with", "thinks like".
}
```

**Exact template text is CDA SME's binding scope.** The Architect proposes the structure (2-3 sentences, numeric summary, no psychological attribution); the SME approves wording or revises. The Coder cannot ship without SME PASS or PASS-WITH-NOTES on this module.

**`sr-only` CSS rule:** the standard WebAIM technique:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

This class already exists in the codebase (`F-T5-A1` / `F-T7-A1` use it). T8 reuses it; no new CSS class.

**Composition with the existing `<h2 className="sr-only">` bridge:**

```tsx
<div className="mds-plot">
  <h2 className="sr-only">MDS plot</h2>
  <ScreenReaderSummary text={mdsScreenReaderSummary(domainResult, selectedModels)} />
  {/* ... rest of MDSPlot ... */}
</div>
```

The bridge stays. ScreenReaderSummary is an additional sr-only `<p>` (the `<h2>` bridge announces the section name; ScreenReaderSummary announces the prose summary). Both are screen-reader-only; neither affects the visual layout.

**Always-present, not conditional on `readAsTable`.** The ScreenReaderSummary is in the DOM regardless of toggle state. Screen-reader users get the summary in both modes; sighted users see only the visualization (toggle controls table↔SVG).

### §2.6. `framing_note` / lede-generator boundary

The per-domain `generated_lede` field (consumed by `ArticleHeader` at the page-top) is a domain-level statement: "What does this domain reveal?" The per-viz `ScreenReaderSummary` is a viz-level statement: "What does this specific chart show?" They are complementary and serve different readers:

- `generated_lede` answers: "Why am I looking at this page?" (audience: journalist scanning the dashboard).
- `ScreenReaderSummary` answers: "What is encoded in this specific chart, for someone who cannot see the chart?" (audience: screen-reader user, audit auditor, journalist verifying that table mode preserves the finding).

The two surfaces share no source-of-truth and no template. They are intentionally separated; combining them would conflate audience and concern.

**Architectural boundary:** the lede generator stays in `cdb_publish`. T8 introduces only programmatic templates in the dashboard. No LLM call. CLAUDE.md §6 R11 not at risk.

### §2.7. Component breakdown — **5 new files + 4 edited files.**

**New files:**

1. **`apps/dashboard/src/components/ReadAsTableToggle.tsx`** — the toggle button primitive. Props: `pressed: boolean`, `onToggle: () => void`, `tableId: string`, `labels: { rest: string; pressed: string }`. Renders `<button type="button" aria-pressed={pressed} aria-controls={tableId} className="read-as-table-toggle__button">{pressed ? labels.pressed : labels.rest}</button>`. ~30 LoC.
2. **`apps/dashboard/src/components/ScreenReaderSummary.tsx`** — the hidden-prose renderer. Props: `text: string`. Renders `<p className="sr-only screen-reader-summary">{text}</p>`. ~15 LoC. (Trivial; could be folded into each viz, but a single component keeps the `sr-only` posture testable in one place.)
3. **`apps/dashboard/src/components/MdsTable.tsx`** — the MDS table renderer. Props: `domainResult: DomainResultPublished`, `selectedModels: string[]`, `modelColors: Record<string, string>`. Renders one `<table>` per §2.3.1. ~120 LoC.
4. **`apps/dashboard/src/components/FreeListTable.tsx`** — the FreeList tables renderer. Props: `domainResult: DomainResultPublished`, `selectedModels: string[]`, `modelColors: Record<string, string>`. Renders one `<table>` per selected model, or empty-state captions for Case B / Case C. ~150 LoC.
5. **`apps/dashboard/src/components/SimilarityTable.tsx`** — the Similarity flat-tuple table renderer. Props: `domainResult: DomainResultPublished`, `selectedModels: string[]`. Renders one `<table>` per §2.3.3. ~100 LoC.
6. **`apps/dashboard/src/copy/screen_reader_summaries.ts`** — single source of truth for the three template functions (§2.5) + the CDA-SME-approved button labels (`READ_AS_TABLE_LABEL_REST`, `READ_AS_TABLE_LABEL_PRESSED`) + the three captions for the three tables. **CDA SME reviews this file as a whole.** ~120 LoC.
7. **`apps/dashboard/src/styles/read-as-table.css`** — token-only CSS for the toggle button and the three table renderers. No new tokens. ~80 LoC.

**Edited files:**

1. **`apps/dashboard/src/components/MDSPlot.tsx`** — add `readAsTable` state + ScreenReaderSummary + conditional render of `<MdsTable>` (or hide-SVG with `aria-hidden` + `display: none`) + the `<ReadAsTableToggle>` below the SVG. Surgical: ~30 LoC delta.
2. **`apps/dashboard/src/components/FreeListCompare.tsx`** — same pattern: state + ScreenReaderSummary + conditional `<FreeListTable>` + `<ReadAsTableToggle>`. ~30 LoC delta.
3. **`apps/dashboard/src/components/SimilarityHeatmap.tsx`** — same pattern: state + ScreenReaderSummary + conditional `<SimilarityTable>` + `<ReadAsTableToggle>`. ~30 LoC delta.
4. **`apps/dashboard/src/data/types.ts`** — **DO NOT TOUCH.** Cast through `unknown` at the boundary (precedent: T0/T5/T7 plans §4; the existing patterns in `DataExplorer.tsx` lines 152/192/229 and the T7 `FreeListCompare.tsx` lines 78–80).

**Untouched:** `App.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ModelSelector.tsx`, `Legend.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `InspectRoot.tsx`, `InspectTable.tsx`, `InspectSection.tsx`, `FailuresInspectView.tsx`, `cdb_core/schemas.py`, `cdb_publish/build.py`, `manifest.json`, the published `data/*.json` files.

**Total estimated LoC: ~600–750 across new + edited files.** No new dependencies in `package.json`. No new tokens in `tokens.css`. No CSS class collisions with existing T5/T7/T13/T10 components.

### §2.8. Forbidden vocabulary discipline + LSB-authored prose surface

All LSB-authored prose strings introduced by T8 live in **one file**: `src/copy/screen_reader_summaries.ts`. This is the precedent from T13 (`methodology_summary.ts`) and T10 (`failures_findings.ts`).

The strings CDA SME reviews:

| Variable | Proposed value | §1.5.4 notes |
|---|---|---|
| `READ_AS_TABLE_LABEL_REST` | `"Read as table"` | Descriptive, no model-state attribution. |
| `READ_AS_TABLE_LABEL_PRESSED` | `"Show visualization"` | Symmetric label. |
| `MDS_TABLE_CAPTION` | per §2.3.1 draft | First-class-state framing on `—` rows. |
| `FREELIST_TABLE_CAPTION_TEMPLATE` | per §2.3.2 draft | Per-model rendering. |
| `SIMILARITY_TABLE_CAPTION` | per §2.3.3 draft | First-class-state framing on null CI rows. |
| `MDS_SR_SUMMARY` template body | per §2.5 | Must avoid "believes", "thinks", "worldview", "sees", "perceives". |
| `FREELIST_SR_SUMMARY` template body | per §2.5 | Same forbidden-vocab discipline. |
| `SIMILARITY_SR_SUMMARY` template body | per §2.5 | Same; must avoid "agrees with", "thinks like". |
| `MDS_TABLE_EMPTY_NO_MODELS` | `"Select one or more models to see the MDS coordinates table."` | UX instruction, not defect framing. |
| `FREELIST_TABLE_EMPTY_NO_MODELS` | `"Select one or more models to see the ranked-term tables."` | Same. |
| `SIMILARITY_TABLE_EMPTY_LT_2_MODELS` | `"Select at least two models to see the similarity table."` | Same; similarity requires N≥2 pairs. |
| FreeList Case B caption | `"(no salience data for this model)"` | Carry-forward from T7 §2.5. |
| FreeList Case C caption | `"(no terms produced)"` | Carry-forward from T7 §2.5. |
| Table column headers (LSB-authored) | "Model" / "Rank" / "Term" / "Salience (CSI)" / "Inclusion frequency" / "Model A" / "Model B" / "Similarity" / "95% CI low" / "95% CI high" / "Uncertainty mode" / "Semi-major" / "Semi-minor" / "Rotation (rad)" / "n_bootstrap" | All technical; CDA SME may revise. |

**Forbidden-vocab spot-check the Coder runs before commit:** grep T8's source files for `"worldview"`, `"believes"`, `"thinks"` (applied to models), `"How models see"`, `"What the model understands"`, `"cultural bias"` (standalone), `"refuses"` (LSB-authored), `"missing"`, `"placeholder"`, `"no data yet"`, `"pending"`, `"yet to be"`, `"perceives"`, `"intends"`, `"sees"` (when applied to models). None may appear in LSB-authored prose. Data field names and Sutrop/Romney/Smith terminology are exempt.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. Loading `<dev-server>/` and clicking the "Read as table" toggle inside the MDS tab renders `<MdsTable>` per §2.3.1; the SVG is hidden via `aria-hidden="true"` and `display: none`; clicking again restores the SVG.
3. Same behavior in the FreeList tab: toggle renders `<FreeListTable>` (one `<table>` per selected model) per §2.3.2; toggle again restores the FreeListCompare columns.
4. Same behavior in the Similarity tab: toggle renders `<SimilarityTable>` (flat 3+CI-columns tuple list) per §2.3.3; toggle again restores the heatmap.
5. The toggle button is a semantic `<button>` with `aria-pressed` reflecting state and `aria-controls` pointing to the table's `id` (when rendered).
6. The toggle button has `min-height: 44px` at `<768px` viewport widths per WCAG 2.5.5.
7. The toggle button is keyboard-accessible: Tab focuses; Enter and Space toggle. Visible focus indicator at WCAG AA 3:1 contrast.
8. Each viz contains a `<ScreenReaderSummary>` rendered as the first child of the viz root (after the `<h2 className="sr-only">` bridge), present in both modes (visualization and table); the prose is the output of the corresponding template function in `src/copy/screen_reader_summaries.ts`.
9. R10 in tables: the MDS table's ellipse columns are adjacent to the (x, y) columns in the same row; the FreeList table's inclusion-frequency column is adjacent to the CSI column in the same row; the Similarity table's 95% CI columns are adjacent to the similarity column in the same row. **Reviewer verifies this on the rendered DOM, not just the source code.**
10. Tables use semantic HTML: `<table>` + `<caption>` + `<thead>` + `<tbody>` + `<th scope="col">` on column headers (and `<th scope="row">` if any row-header cells are used). No `<div role="table">` substitutes.
11. Heading hierarchy: page `<h1>` (Header) → article `<h2>` (existing) → viz `<h3>` (existing per Phase 5/T7/T5) → table `<caption>` (sub-section name). No `<h4>` skipping under `<h3>`; the FreeList sub-tables per-model use `<h4>` with the model name (per §2.3.2). No heading levels are skipped.
12. The MDS table empty-state (`selectedModels.length === 0`) renders the `MDS_TABLE_EMPTY_NO_MODELS` caption; no `<table>` rendered.
13. The FreeList table empty-states: Case A renders `FREELIST_TABLE_EMPTY_NO_MODELS`; Case B renders the per-model Case B caption inside the column slot (no `<table>` for that model); Case C renders the per-model Case C caption (no `<table>` for that model).
14. The Similarity table empty-state (`selectedModels.length < 2`) renders the `SIMILARITY_TABLE_EMPTY_LT_2_MODELS` caption; no `<table>` rendered.
15. WCAG AA contrast: every LSB-authored text string in T8 (button label, captions, ScreenReaderSummary prose — when visible, which it never is by design, but assertable via the `sr-only` rule — and column headers) meets 4.5:1 against its background. Tested against `--color-text-caption` / `--color-text-primary` on `--color-background` / `--color-surface`. Numeric cell values in tables use `--font-mono`; contrast unchanged from existing precedent.
16. Mobile usable at 320px viewport width: tables overflow horizontally with native scroll (no special treatment beyond `overflow-x: auto` on the table container); no layout breakage. Touch targets on the toggle button satisfy 44px floor.
17. The toggle button labels and captions come from `src/copy/screen_reader_summaries.ts`. No string literal in any T8 component file (other than the copy module) contains any LSB-authored prose.
18. No forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4) anywhere in `screen_reader_summaries.ts` or any T8 component. The Reviewer's grep against the §2.8 forbidden list passes. Field names (`model_id`, `csi`, `f_mentions`, `n_runs`, `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap`, `similarity`) and standard statistical terminology are exempt.
19. The Coder does NOT touch `apps/dashboard/src/data/types.ts` (T14 doc-sweep concern; cast through `unknown` per §4).
20. The Coder does NOT touch `cdb_core/schemas.py` (CLAUDE.md R6 not triggered; schema-quiet).
21. The Coder does NOT touch `App.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ModelSelector.tsx`, `Legend.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `InspectRoot.tsx`, `InspectTable.tsx`, `InspectSection.tsx`, `FailuresInspectView.tsx`. Reviewer rejects T8 commits modifying any of these.
22. No `<meta name="robots">` change. T8 lives at the canonical URL; the inspect-mode `noindex` is untouched.
23. Reveal cascade unchanged. T8 introduces no new `.reveal-cascade-item` wrappers; the toggle and ScreenReaderSummary live inside existing viz components and follow the existing cascade timing.
24. Bundle delta ≤ 8 KB gzipped against the post-T10 baseline (~85 KB after T0 + T7 + T5 + T10; T9 was backend-only). Coder reports the measured delta in the commit body. Reviewer rejects if > 8 KB.
25. No new dependencies in `package.json`. No `react-router-dom`, no chart libraries, no markdown libraries, no table libraries.
26. Per-viz state isolation: switching the VizSwitcher tab resets `readAsTable` for each viz (component unmounts/remounts on tab swap; state reinitializes to `false`). Tester verifies via render-cycle test.
27. Tester writes vitest coverage for: ReadAsTableToggle (aria-pressed toggling, click/keyboard activation), ScreenReaderSummary (sr-only rendering, text content), MdsTable (R10 columns present, R1-b/R1-c `—` rendering, caption renders, empty-state), FreeListTable (per-model tables, Case A/B/C empty states, shared-term glyph), SimilarityTable (flat 3-row tuple form, CI null `—`, empty-state at N=1), and an integration test on each of MDSPlot / FreeListCompare / SimilarityHeatmap that the toggle hides the SVG / shows the table.
28. CSP compliance: T8 introduces no `eval`, no inline `<script>`, no `dangerouslySetInnerHTML`. All text rendered via React text nodes.

---

## §4. Known shape disagreements (Coder note, not a blocker)

T8 inherits the T0/T5/T7 `data/types.ts` shape mismatches:
1. `similarity_matrix` typed `Record<string, Record<string, number>>`; live JSON is `number[][]`.
2. `similarity_ci` typed `Record<string, Record<string, [number, number] | null>>`; live JSON is `Array<Array<[number, number] | null>>`.
3. `mds_coordinates` typed `Record<string, [[number, number]]>`; live JSON is `Record<string, [number, number]>`.
4. `mds_uncertainty[model_id]` shape (semi_major / semi_minor / rotation_rad / n_bootstrap) — present in live JSON; `data/types.ts` may not fully model it.
5. `display.r1_states[model_id]` — typed `R1State` in `data/types.ts`; live JSON matches; safe to use without cast.
6. `sutrop_csi` typed `Record<string, Record<string, number>>`; live JSON is `Record<string, Array<{ item, csi, f_mentions, n_runs, mean_position }>>` (per T7 plan §4).
7. `free_lists` typed `Record<string, string[]>`; live JSON is the object-per-model shape (per T7 plan §4).

**T8 follows the files, not the types.** The Coder casts through `unknown` at the boundary in each table renderer:

```ts
const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
const rawUncertainty = domainResult.mds_uncertainty as unknown as Record<string, {
  semi_major: number | null;
  semi_minor: number | null;
  rotation_rad: number | null;
  n_bootstrap: number | null;
  ci_level?: number | null;
}>;
const rawSimilarityMatrix = domainResult.similarity_matrix as unknown as number[][];
const rawSimilarityCi = domainResult.similarity_ci as unknown as Array<Array<[number, number] | null>>;
const rawSutropCsi = domainResult.sutrop_csi as unknown as Record<string, Array<{
  item: string; csi: number; f_mentions: number; n_runs: number; mean_position: number;
}>>;
```

**Coder MUST NOT "fix" `data/types.ts` in T8.** T14 doc-sweep concern. Reviewer rejects T8 commits modifying it. The disagreement is surfaced in the T8 commit body for T14 follow-up.

---

## §5. Out of scope for T8

Explicitly excluded; do not partially address:

- **Drift table (DriftTracker T4 territory).** T4 is deferred per kickoff §3 Q3. When T4 ships, a follow-up commit adds `DriftTable.tsx` using T8's pattern (toggle + table + screen-reader summary). The T8 implementation does not stub or scaffold the drift table.
- **Explorer-level umbrella toggle.** §2.1 selected per-viz. An umbrella toggle is a future-phase concern; T8 ships per-viz primitives that could later be composed under an umbrella without re-architecture.
- **URL persistence of `readAsTable` state.** The permalink scheme is unchanged. A reader who shares a URL of a table-mode view gets the recipient back to the viz-mode view; this is a known limitation, acceptable for Phase 6.
- **InspectRoot extension.** T0's operator surface is untouched. The T10 §2.6 ruling stands: operator surface and public surface are kept separate.
- **CSV / JSON export from inside the table view.** The DownloadBar already provides CSV / PNG / Permalink / Cite / Embed. T8 does not add a "Download this table" button. The DownloadBar's CSV is the export path.
- **Pagination, sort, filter, search affordances inside tables.** Plain `<table>` only. Mark's `feedback_inspection.md` posture: tables are readers; filter-and-search is the inspect surface.
- **Sticky table headers on scroll.** Out of scope.
- **Methodology page link from table captions.** The methodology page does not exist yet (T1/T2). T14 doc-sweep may wire links from captions when T1 ships.
- **A new visualization library (Plotly, d3-table, react-table, etc.).** No new dependencies.
- **Touching `data/types.ts` or any of the 11 untouchable components enumerated in acceptance criterion 21.**
- **CSS animation on toggle.** Phase 6 functional-surface posture.
- **A reader-facing setting that opens all viz cards in table mode by default (an accessibility-preference toggle).** Future-phase concern.
- **A second Vite entry, `react-router-dom`, or any router framework.** Phase 6 T1 owns that decision; T8 uses the existing infrastructure.

---

## §6. Gate routing

- **Architect:** this plan. On Mark's acceptance, the orchestrator dispatches the gates below.

- **CDA SME: REQUIRED.** Rationale: T8 introduces LSB-authored prose strings rendered to readers as text *about* the models — the three ScreenReaderSummary templates, the three table captions, the button labels, the empty-state copy, the column header strings. The §1.5.4 forbidden-vocabulary discipline applies, and the templates additionally express claims about what each viz *shows* (the audience-translation axis). The CDA SME's binding scope:
  1. **§2.5 ScreenReaderSummary templates** — the three template function bodies in `screen_reader_summaries.ts`. Per-template four-axis review:
     - **Protocol validity:** is the summary accurate about what was collected and analyzed?
     - **Analytical validity:** does the summary correctly describe what the visualization encodes (numeric ranges, consensus types, similarity bounds, etc.)?
     - **Claims validity:** does the summary avoid overclaiming about model cognition / belief / worldview? Does it describe corpus-lens findings, not psychological states?
     - **Audience translation:** would a journalist / AI engineer / accessibility auditor reading the summary understand the chart's key information without seeing it?
  2. **§2.3 table captions** — the three table caption strings. CDA SME confirms the wording is accurate (especially the first-class-state framing for `—` rows in MDS and Similarity tables, and the empirical-frequency framing in FreeList — carrying forward T7's CDA SME PASS).
  3. **§2.2 button labels** — `"Read as table"` / `"Show visualization"`. CDA SME may revise to `"View as table"` / `"View visualization"` or other phrasing. The constraint is forbidden-vocab clean; the choice is a copy decision.
  4. **§2.8 empty-state captions** — the three "select N or more models" instructions. Forbidden-vocab clean; UX-instruction framing.
  5. **§2.8 column header strings** — the LSB-authored column headers in the three tables. Carry-forward from existing T7 / T5 vocabulary where applicable; CDA SME confirms cross-surface consistency.
  Four-axis verdict format per T5 / T7 / T10 precedent. PASS → Coder dispatches after UI/UX PASS. PASS-WITH-NOTES → Coder applies notes; verdict saved to `docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md`. FAIL → re-plan.

- **UI/UX agent: light-touch only — accessibility floor + R10 in tables + token consistency + WCAG AA contrast + mobile/touch.** Per `feedback_ui_polish_scope.md`. The UI/UX agent reviews:
  1. The toggle is a semantic `<button>` with `aria-pressed` and `aria-controls`; keyboard accessible; visible focus indicator at WCAG AA 3:1 contrast.
  2. Each table is `<table>` + `<caption>` + `<th scope>`; no `<div role="table">` substitute; heading hierarchy intact (page H1 → article H2 → viz H3 → table caption / FreeList H4).
  3. R10 in tables: the Reviewer's binding rule is also enforced by UI/UX — uncertainty columns adjacent to point-estimate columns in the same row. Verified by inspecting the rendered DOM of each table renderer in the three vitest snapshots.
  4. WCAG AA contrast on all LSB-authored text: button label (`--color-text-caption` at 14px ≥ 4.5:1 verified at v0.4.3), captions, table cells. Verified empirically against `--color-background` and `--color-surface`.
  5. Tokens only: no hardcoded colors, fonts, or spacings. The new `read-as-table.css` references only existing tokens.
  6. Touch targets: toggle button `min-height: 44px` at `<768px`. Table cells inherit existing token sizing; no separate touch-target floor for `<td>` cells (passive content).
  7. Mobile (320px viewport): toggle button does not break layout; tables overflow horizontally with native scroll; `<pre>`-style content (none in T8) is not needed.
  8. The `sr-only` ScreenReaderSummary uses the existing `.sr-only` class verbatim; no new visually-hidden styling pattern.
  UI/UX issues PASS / PASS-WITH-NOTES / FAIL on those eight checks alone. **No design critique beyond them.** No "the tables feel sparse" / "the toggle could be styled more polished" verdicts permitted.

- **Coder:** implements after CDA SME PASS (or PASS-WITH-NOTES with applied notes) AND UI/UX PASS (or PASS-WITH-NOTES with applied notes).

- **Reviewer:** standard nine-check sweep. Specific attention to:
  - R6: no `cdb_core/schemas.py` change; no `data/types.ts` change.
  - R7: no `DATA_DICTIONARY.md` change required (T8 introduces no new published fields).
  - R10: rendered DOM of each table renderer has uncertainty columns adjacent to point-estimate columns (assertable via vitest snapshot text).
  - R11: no `anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, or any LLM client import in T8 files.
  - R12 (§1.5.4 forbidden vocabulary): grep the `screen_reader_summaries.ts` module and the three table renderers against the §2.8 forbidden list. Spot-check rendered DOM via vitest snapshots.
  - R13 (no spend-cap framing): grep T8 files for `cost`, `$`, `usd`, `spend`, `budget`, `max_tokens`, `rate_limit` — N/A to a frontend accessibility task; restated for completeness.
  - R2 (no `dangerouslySetInnerHTML`): all text rendered as React text nodes.
  - Reviewer rejects any commit that touches `data/types.ts` or any of the 11 untouchable components enumerated in acceptance criterion 21.

- **Tester:** standard vitest. T8's testable surface:
  - `ReadAsTableToggle`: aria-pressed toggling, click and keyboard activation, label switch.
  - `ScreenReaderSummary`: sr-only class present, text content equals the template output.
  - `MdsTable`: R10 column adjacency, R1-b/R1-c `—` rendering, caption renders, empty-state caption when `selectedModels.length === 0`, sort order is lexicographic by model_id.
  - `FreeListTable`: one `<table>` per selected model, sort within table by CSI descending with deterministic tie-breaks, Case A / B / C empty-state captions, shared-term `★` glyph appears when term is in `sharedTerms`.
  - `SimilarityTable`: flat 3-column tuple form (one row per unordered pair, no diagonal), null CI `—` rendering, empty-state when `selectedModels.length < 2`.
  - Integration tests on `MDSPlot` / `FreeListCompare` / `SimilarityHeatmap`: toggle press hides the SVG (or columns container) via `aria-hidden` + `display: none` and shows the corresponding table; toggle again restores the original view.
  - State isolation: switching the viz tab and returning resets `readAsTable` to `false`.
  - No real network fetches; inline fixtures matching the existing T0 `MOCK_DOMAIN` pattern.

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | **No** | No | Not triggered |
| `apps/dashboard/src/data/types.ts` | **No** (T14 doc-sweep concern) | No | Not triggered |
| `docs/DATA_DICTIONARY.md` | No (no new published fields) | No | Not triggered |
| `ARCHITECTURE.md` | No (T14 may sharpen §1.5 if SME revises summary templates) | No | Not triggered |
| `DESIGN_SYSTEM.md` | No (T14 adds §12.x for ReadAsTableToggle codification + closes §12.6 deferral; T8 does not pre-codify) | No | Not triggered |
| `apps/dashboard/src/components/{ReadAsTableToggle,ScreenReaderSummary,MdsTable,FreeListTable,SimilarityTable}.tsx` | New files | N/A | Not triggered |
| `apps/dashboard/src/copy/screen_reader_summaries.ts` | New file (CDA SME single source of truth) | N/A | Not triggered |
| `apps/dashboard/src/styles/read-as-table.css` | New file (token-only) | N/A | Not triggered |
| `apps/dashboard/src/components/{MDSPlot,FreeListCompare,SimilarityHeatmap}.tsx` | Yes — surgical (state + toggle + ScreenReaderSummary + conditional render) | N/A | Not triggered |
| `apps/dashboard/src/components/App.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ModelSelector.tsx`, `Legend.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `InspectRoot.tsx`, `InspectTable.tsx`, `InspectSection.tsx`, `FailuresInspectView.tsx` | **No** | N/A | Not triggered |

**Architect sign-off needed for schema change: none** — T8 is schema-quiet.

---

## §8. Bundle budget watch

Post-T10 baseline (after T0 + T7 + T5 + T10; T9 backend-only): ~85 KB gzipped. The kickoff §8 estimate was "AccessibilityTableToggle + ScreenReaderSummary ~4 KB." With three table renderers (MdsTable, FreeListTable, SimilarityTable), the realistic estimate is higher:

- `ReadAsTableToggle.tsx`: ~0.5 KB gzipped.
- `ScreenReaderSummary.tsx`: ~0.2 KB gzipped.
- `MdsTable.tsx`: ~1.5 KB gzipped.
- `FreeListTable.tsx`: ~2 KB gzipped (per-model loop + shared-term computation).
- `SimilarityTable.tsx`: ~1.5 KB gzipped (dual-index translation + N*(N-1)/2 row generation).
- `screen_reader_summaries.ts`: ~1 KB gzipped (templates + caption strings + labels).
- `read-as-table.css`: ~1 KB gzipped.
- Edits to MDSPlot / FreeListCompare / SimilarityHeatmap: ~0.5 KB total.
- No new dependency in `package.json`.

**Expected delta: ~7–8 KB gzipped.** At the 8 KB ceiling Mark set; tight but achievable. The Coder must report the measured delta in the commit body. If the delta exceeds 8 KB, the candidate optimization is to fold `ReadAsTableToggle.tsx` and `ScreenReaderSummary.tsx` into their consumers (these are tiny components; the wrapper overhead may be larger than the inlined code).

Phase 6 cumulative budget: 400 KB cap. Post-T8: ~93 KB total, ~23% of cap. Headroom preserved for T4 (DriftTracker), T11 (hamburger), T12 (bottom-drawer), T13 (new content), T14 (doc sweep).

---

## §9. Dependency order

**Upstream of T8 (HARD dependencies — must ship before T8 Coder dispatch):**
- **T7 (FreeListCompare) — HARD.** T8 extends FreeListCompare; the component must exist. **T7 has shipped per the orchestrator's report.**
- **T5 (SimilarityHeatmap) — HARD.** T8 extends SimilarityHeatmap; the component must exist. **T5 has shipped per the orchestrator's report.**
- T0 (InspectRoot) — soft precedent only; T8 reuses semantic conventions but not components.

**Downstream of T8:**
- T4 (DriftTracker) — when T4 ships, a follow-up commit adds `DriftTable.tsx` using T8's pattern. T4 itself is not blocked by T8.
- T14 (documentation sweep) — updates `DESIGN_SYSTEM.md` §11 component inventory (move `AccessibilityTableToggle.tsx` and `ScreenReaderSummary.tsx` out of the Phase 6 backlog), closes the §12.6 Phase 5 deferral note, adds §12.x codifying T8's visual decisions, updates `ARCHITECTURE.md` §4.5 if R10-in-tables needs codification.

**Parallel with T8:** T1 (methodology page skeleton), T2 (methodology page prose), T3 (drift data layer), T4 (DriftTracker), T9 / T10 (failures; T9 and T10 have shipped per orchestrator), T11 (hamburger), T12 (bottom-drawer), T13 (new content).

---

## §10. Risks and watch-items

1. **CDA SME revises ScreenReaderSummary templates substantially.** Probability: moderate. The templates encode claims about what each viz shows — a SME PASS-WITH-NOTES that revises wording is the realistic baseline. Mitigation: all template text lives in one file (`screen_reader_summaries.ts`); a SME-driven revision is a one-file edit, no component-code change required. The Coder dispatches only after PASS or PASS-WITH-NOTES with notes integrated.

2. **CDA SME flags the MDS table's `—` rendering for R1-b / R1-c as confusing.** Probability: low-to-moderate. The semantic — "this model's ellipse is absent because the bootstrap couldn't resample meaningful variance" — is non-obvious. Mitigation: the MDS table caption (§2.3.1 draft) carries the first-class-state explanation; the Uncertainty mode column carries the R1 state verbatim; CDA SME may revise wording.

3. **Per-viz state isolation breaks if a future task moves the table-mode state into a context or URL.** Low probability. The §2.4 decision explicitly localizes state. The Coder must not introduce a context provider; if a future task wants cross-viz state, that's a separate plan.

4. **The 8 KB bundle ceiling is tight.** Three table renderers + a toggle + a screen-reader-summary component + a copy module + CSS. The Coder reports the measured delta; if > 8 KB, the optimization is to inline the smallest components (ReadAsTableToggle, ScreenReaderSummary) into their consumers and remove the wrapper components.

5. **Cross-cutting forbidden-vocab discipline.** The three template functions describe what each viz shows in plain English — the highest concentration of LSB-authored model-describing text in Phase 6 outside the methodology page. The grep check is the safety net; the CDA SME review is the primary defense. The Coder must run the §2.8 grep before commit.

6. **Cell text contrast at edges.** Numeric cells in tables use `--font-mono` at `--font-size-sm` or `--font-size-base`; both pass WCAG AA on `--color-background` (~16:1) and on `--color-surface` (~14:1) per existing precedent. No edge case anticipated.

7. **Mobile horizontal scroll on tables.** The MDS table has 9 columns; at 320px viewport width, the table will overflow horizontally with native scroll. Acceptable per Phase 6 functional-surface posture. UI/UX verifies no layout breakage; tables remain accessible by keyboard.

8. **Screen reader announces both the SVG (`<h2 className="sr-only">{viz} plot</h2>`) and the table caption when the table is visible.** This is mitigated by the SVG hide pattern (`aria-hidden="true"` + `display: none` on the SVG wrapper when `readAsTable === true`). The Coder must verify with VoiceOver / NVDA / JAWS-compatible inspection that double-announcement doesn't occur. The vitest snapshot covers the DOM-tree-level assertion (SVG `display: none` + `aria-hidden="true"`); manual screen-reader testing is the final check.

9. **Bundle creep from "just one more cell formatter."** The Coder MUST resist adding number-formatting libraries (numeral.js, d3-format), date-formatting libraries (date-fns, dayjs), or copy-to-clipboard utilities. `.toFixed()` is sufficient. T8 is a viewer, not a tool.

10. **Toggle button label semantics.** "Read as table" vs "View as table" vs "Show table" are all candidates. The CDA SME may choose. Whatever the chosen label, the symmetric pressed-state label must convey "return to visualization" — `"Show visualization"` is the proposed inverse; SME may revise.

---

*End of T8 plan.*

---

# Report back to Mark

**One-paragraph summary.**
Phase 6 T8 closes the DESIGN_SYSTEM.md §7 accessibility binding and the §12.6 Phase-5 deferral by adding a per-viz "Read as table" toggle plus a hidden `ScreenReaderSummary` to each of the three active visualizations (MDS, FreeList, Similarity). Per-viz toggle (not explorer-level) per the §7 plain reading and to keep screen-reader navigation per-table clean. Three distinct table shapes are defined: MDS = wide row-per-model with adjacent ellipse parameters (R10 satisfied by `semi_major` / `semi_minor` / `rotation_rad` next to `x` / `y`, with `—` rendered for R1-b / R1-c as a first-class state per §1.5.5); FreeList = one `<table>` per selected model with the T7-approved empirical-frequency representation (`f_mentions / n_runs`) as the R10 pairing for Sutrop CSI; Similarity = a flat 3-column-plus-CI-columns tuple list (one row per unordered pair, no matrix, no diagonal), chosen because matrix tables are notoriously hard for screen readers. State lives locally in each viz (`useState`), not in DataExplorer, not in the URL. ScreenReaderSummary uses programmatic per-viz templates pulled from `domainResult` fields — NOT lede regeneration, to keep the LLM boundary at `cdb_publish`. Drift table is out of scope because T4 is deferred (kickoff §3 Q3). Bundle budget tight at ≤ 8 KB; CDA SME REQUIRED on the copy module (`screen_reader_summaries.ts`) and table captions; UI/UX light-touch for accessibility floor + R10-in-tables + tokens + WCAG AA + mobile.

**Key decisions:**
1. **Per-viz toggle, not explorer-level** (resolves kickoff §3 Q7). Matches §7 plain reading; cleaner SR navigation; trade-off documented.
2. **Toggle placement: below the viz, left-aligned, plain-text `<button>` with `aria-pressed`** — not in VizSwitcher (conflates concerns), not in DownloadBar (clutter; different conceptual category).
3. **Three distinct table shapes** with explicit R10 column adjacency in each. MDS = ellipse-adjacent. FreeList = per-model tables with inclusion-frequency-adjacent. Similarity = flat 3-column tuple form (matrix tables rejected for SR navigation reasons).
4. **State management: per-viz `useState`, no DataExplorer state, no URL persistence.** Tables reset on tab swap.
5. **ScreenReaderSummary: programmatic templates from JSON, not lede regeneration.** Keeps LLM boundary at `cdb_publish`. Three template functions in `src/copy/screen_reader_summaries.ts`. CDA SME's single review surface.
6. **`framing_note` / lede boundary documented:** the per-domain `generated_lede` (ArticleHeader) and the per-viz ScreenReaderSummary are complementary, share no source-of-truth, and serve different audiences. No combination.
7. **R10 binding extended to HTML tables explicitly.** Reviewer verifies on rendered DOM, not just source code. Listed as acceptance criterion 9.
8. **Drift table deferred with T4.** Out of scope §5. When T4 ships, a follow-up commit adds `DriftTable.tsx` using T8's pattern.

**Component breakdown:**
- New: `/opt/lsb-agent/apps/dashboard/src/components/ReadAsTableToggle.tsx`
- New: `/opt/lsb-agent/apps/dashboard/src/components/ScreenReaderSummary.tsx`
- New: `/opt/lsb-agent/apps/dashboard/src/components/MdsTable.tsx`
- New: `/opt/lsb-agent/apps/dashboard/src/components/FreeListTable.tsx`
- New: `/opt/lsb-agent/apps/dashboard/src/components/SimilarityTable.tsx`
- New: `/opt/lsb-agent/apps/dashboard/src/copy/screen_reader_summaries.ts` (CDA SME reviews this file as a whole)
- New: `/opt/lsb-agent/apps/dashboard/src/styles/read-as-table.css` (token-only)
- Edited: `/opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx` (state + toggle + SR summary + conditional render)
- Edited: `/opt/lsb-agent/apps/dashboard/src/components/FreeListCompare.tsx` (same pattern)
- Edited: `/opt/lsb-agent/apps/dashboard/src/components/SimilarityHeatmap.tsx` (same pattern)

Untouched: `cdb_core/schemas.py`, `apps/dashboard/src/data/types.ts`, `App.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ModelSelector.tsx`, `Legend.tsx`, `MethodologySummary.tsx`, `FailuresFindingsSection.tsx`, `InspectRoot.tsx`, `InspectTable.tsx`, `InspectSection.tsx`, `FailuresInspectView.tsx`.

**Escalation items for Mark:**

1. **Button label.** Architect proposed `"Read as table"` / `"Show visualization"`; CDA SME may revise to `"View as table"` / `"View visualization"` or other phrasing. **Not blocking dispatch** — copy lives in a single file.
2. **MDS table's `—` rendering for R1-b / R1-c.** Architect chose to render `—` with a first-class-state caption (carries forward the §1.5.5 binding). The CDA SME may prefer an explicit string ("ellipse suppressed: low concentration") in the column instead of `—`; not blocking, surfaced for SME review at axis 4 of §6.
3. **Drift table out of scope.** Calling this out explicitly: T8 ships three tables (MDS, FreeList, Similarity); the fourth (Drift) lands as a follow-up commit when T4 ships. Mark may want to bundle Drift's table into T4 itself when T4 is planned; that's a Phase 6 sequencing decision, not a T8 decision.
4. **Bundle ceiling is tight at 8 KB.** Three table renderers + a toggle + a copy module is realistic at the ceiling. If the measured delta exceeds 8 KB, the Coder folds ReadAsTableToggle and ScreenReaderSummary into their consumers (these are small components; wrapper overhead may exceed the inlined code). Surfaced as Risk 4; not blocking dispatch.
5. **Save path.** The system instruction blocked me from writing the .md file to disk; the plan is delivered as this final-message text. The parent agent should save the content above (between the leading `# Phase 6 T8` heading and the trailing `*End of T8 plan.*`) to `/opt/lsb-agent/docs/status/2026-05-12-phase6-T8-architect-plan.md` verbatim.

No other concerns. T5 and T7 have shipped per the orchestrator's report; T8 is unblocked. CDA SME and UI/UX dispatch can begin once Mark accepts.