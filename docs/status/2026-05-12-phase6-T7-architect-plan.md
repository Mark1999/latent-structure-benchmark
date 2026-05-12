# Phase 6 T7 — FreeListCompare — Architect Plan

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T7 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T7 as "side-by-side ranked-term-list viz tab per DESIGN_SYSTEM.md §3.4; each column = one selected model; terms ranked by Sutrop CSI salience; per-term R10 uncertainty mandatory").
**Status:** Awaiting CDA SME dispatch (REQUIRED — see §6); then UI/UX light-touch (§6); then Coder dispatch on PASS.

---

## §0. Reading list (mandatory before Coder dispatch)

Common to T7:

1. `/opt/lsb-agent/CLAUDE.md` §6 (binding rules — especially R8 keys, R9 fixtures, **R10 uncertainty in viz — load-bearing for this task**, R13 design system), §7 (forbidden vocabulary — applies to the column captions and the empty-state caption), §9 (pitfalls 3, 4, 5, 7, 8 — especially #8 "no point estimate without uncertainty").
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact — column headers and captions count), §1.5.4 forbidden vocabulary, §1.5.5 (model-to-model framing — relevant if an empty free list is rendered), §4.5 (R10 binding — no point estimates without uncertainty in any new viz).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` §3.4 (FreeListCompare detailed spec — column structure, hover-highlight interaction, shared-color rule, mobile horizontal-scroll posture), §1 (tokens), §3.2 (component library — Custom render strategy), §7 (accessibility floor), §12.4 (model color assignment — palette ownership lives in `DataExplorer.tsx`, not in `FreeListCompare`).
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T7 + §2 T7a (the R10 conditional dependency).
5. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T0-architect-plan.md` (precedent for this plan's structure and acceptance-criteria style; also §4 documents the `data/types.ts` shape mismatches deferred to T14 — FreeListCompare may hit the same).
6. Memory: `feedback_ui_polish_scope.md` (Phase 6 minimum-viable functional surface; UI/UX gating reduced to accessibility floor + R10 + tokens only), `project_phase4a1_empty_freelist_propagation.md` (the empty-freelist case exists in the corpus and must be handled as a first-class state, not "missing data").
7. `/opt/lsb-agent/apps/dashboard/public/data/family.json` and `/opt/lsb-agent/apps/dashboard/public/data/holidays.json` — actual JSON shapes. Note: `family.json` is the authority where it disagrees with `data/types.ts` (see §4 below).
8. `/opt/lsb-agent/apps/dashboard/src/components/DataExplorer.tsx`, `/opt/lsb-agent/apps/dashboard/src/components/VizSwitcher.tsx` — the integration point. The `ActiveVizTab` type widens from `"mds"` to `"mds" | "freelist"` in this task; tab enablement removes from `VizSwitcher`'s `TABS` array.
9. `/opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx` — architectural style precedent (hand-rolled, accessible, token-only, R1-state composition). FreeListCompare follows the same posture: no chart libraries, plain TSX + CSS using existing tokens.
10. `/opt/lsb-agent/apps/dashboard/src/lib/modelShortName.ts` — reuse for column headers (no per-component re-implementation).

---

## §1. Mark's binding directives + Phase 6 functional-surface framing

1. **Phase 6 minimum-viable functional surface (memory `feedback_ui_polish_scope.md`).** No microcopy work, no decorative animation, no aesthetic blocking by UI/UX. UI/UX reviews accessibility floor (semantic HTML + ARIA), R10 pairing, token consistency, WCAG AA contrast — and that's it.
2. **R10 binding is non-negotiable (CLAUDE.md §6 R10; ARCHITECTURE.md §4.5).** No point estimate without uncertainty. This task's R10 mechanism is established in §2.4 and the methodology trade-off is documented in §2.2 for CDA SME review.
3. **Empty free lists are first-class states.** The corpus contains records where `free_lists[model_id].items` is `[]` (memory `project_phase4a1_empty_freelist_propagation.md`). Render verbatim with a caption that does **not** use "missing" / "placeholder" / "no data yet" / "pending" framing (CLAUDE.md §9 pitfalls 4 and 5 binding). The empty column is the finding.
4. **Forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4) applies to every piece of generated text on the page** — column captions, tooltip text if any, the empty-state caption, the R10 description sentence. Field names from the data (e.g., `"sutrop_csi"`, term strings like `"mother"`) are not LSB-authored prose and are exempt.
5. **No new dependencies.** Implement using existing React + TSX + token-driven CSS. No `d3`, no `framer-motion`, no `react-window`. Reuse `modelShortName` and the existing `modelColors` prop from `DataExplorer`. The hand-rolled SVG/HTML precedent from `MDSPlot.tsx` applies.
6. **`?inspect=...` operator surface (T0) is untouched.** T7 lives behind `activeVizTab === "freelist"` only. The inspect mode already surfaces `free_lists` and `sutrop_csi` per T0 §2.4.
7. **No software-side spend gates (CLAUDE.md §6 R14).** N/A to a frontend viz, restated for closure.
8. **Bundle budget: T7 adds ≤ 8 KB gzipped** (matches kickoff §8 estimate for FreeListCompare). Coder reports measured delta in the commit body. Plan ceiling: 8 KB.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Tab integration — replace the disabled `freelist` slot in `VizSwitcher`; widen `ActiveVizTab`; conditional render in `DataExplorer`.

Concretely:

- **`VizSwitcher.tsx` changes (small surgical edits):**
  - Widen the exported type: `export type ActiveVizTab = "mds" | "freelist";`
  - In the `TABS` array (lines 43–48), change the `freelist` entry from `{ id: "freelist", label: "Free Lists", active: false, disabled: true }` to `{ id: "freelist", label: "Free Lists", active: false, disabled: false }`. The `active` flag is derived from `activeTab` at render time, so the `active: false` on the entry definition is the unchanged "not the default tab" state — not "always inactive."
  - Remove `"freelist"` from the `DISABLED_FRAGMENTS` set (line 51). `#freelist` becomes a valid URL fragment.
  - Update `resolveFragmentOnMount()` (lines 61–78) to return `"freelist"` when the fragment is `"freelist"`; keep `"similarity"` and `"drift"` in the disabled set (they remain Phase-6-T5 / Phase-6-T4 territory).
  - Update `onClick` and `handleKeyDown` so the activation guard `if (!tab.disabled && tab.id === "mds")` is replaced by `if (!tab.disabled && (tab.id === "mds" || tab.id === "freelist"))`. The MDS-only check was a Phase-5 artifact.

- **`DataExplorer.tsx` changes:**
  - The `<div className="explorer-layout__viz">` block (lines 250–258) currently always renders `MDSPlot`. T7 adds conditional rendering on `activeVizTab`:
    ```
    {activeVizTab === "mds" && <MDSPlot ... />}
    {activeVizTab === "freelist" && <FreeListCompare domainResult={domainResult} modelColors={modelColors} selectedModels={selectedModels} />}
    ```
  - The `modelColors` and `selectedModels` props passed to `FreeListCompare` follow the §12.4 ownership rule unchanged: `DataExplorer` owns the palette, children consume.
  - **No router work, no new state, no new URL parameters.** The existing `writePermalinkState` effect (line 207) already writes `activeVizTab` into the permalink scheme; the only new concrete behavior is that `#freelist` now restores to a real tab on permalink-decode mount.

- **`#freelist` permalink scheme.** Already exists in `encodePermalink` / `decodePermalink` per T10. No change.

**Rationale:** Surgical changes; no architectural drift. The `freelist` tab transitions from disabled-with-tooltip to active-and-rendering by toggling one boolean and adding one conditional branch. This matches the §3.2 dispatch pattern from T8/T9.

### §2.2. R10 uncertainty methodology — **fallback: use `f_mentions / n_runs` from `sutrop_csi` as the per-term inclusion-frequency proxy.** (CDA SME review REQUIRED.)

**The problem.** ARCHITECTURE.md §4.5 (R10 binding) requires every point estimate in a new viz to carry adjacent uncertainty. The kickoff §2 T7 flagged: "the per-term bootstrap inclusion-frequency is **not yet** in the published JSON — `free_lists` is the consensus list, no per-bootstrap-sample data." Without resolution, T7 cannot ship without violating R10 — or T7a (a `cdb_publish` backend extension to emit per-term per-bootstrap-sample inclusion frequencies) becomes a prerequisite.

**Architect's proposal.** Use the existing `sutrop_csi[model_id][i].f_mentions / sutrop_csi[model_id][i].n_runs` ratio as the per-term inclusion-frequency representation:

- This data **is already in the published JSON** (verified against `apps/dashboard/public/data/family.json` line 10026 and `holidays.json` line 8240).
- The ratio **is methodologically defensible** as a per-term frequency-over-runs: it is the fraction of independent free-list collection runs (typically 4) in which the term appeared for that model. This is the empirical inclusion frequency — the direct measurement the Sutrop CSI formula already uses internally.
- The Coder renders, adjacent to each term pill: a small horizontal bar whose width is `(f_mentions / n_runs) * 100%`, with the numeric ratio (`"3 of 4 runs"` or `"f = 0.75"`) as the accessible label.

**Trade-off — what's preserved:**

- Per-term R10 pairing is satisfied: every term pill has an uncertainty representation alongside it.
- The uncertainty is **empirical** (raw frequencies from the actual collection runs) — no bootstrap-resample interpolation, no statistical inference, no risk of "we tuned the bootstrap and changed the answer."
- The data is published, stable, and survives schema drift (per the T0 "Other top-level fields" safety net pattern).

**Trade-off — what's lost:**

- This is **run-level frequency**, not bootstrap-resample frequency. The two are related but not identical: a bootstrap-resample inclusion frequency would aggregate across `B` (typically 2,000) resamples of the run set, smoothing the {0, 0.25, 0.5, 0.75, 1.0} discrete values that `f_mentions / n_runs` produces with n_runs=4.
- **Per-term confidence intervals are NOT available** under this fallback. The reader sees the point frequency, not its CI. For domains with n_runs ≥ 30, a Wilson-score interval could be computed client-side — but for the 0.2 corpus's n_runs = 4, the Wilson interval would be wider than the [0, 1] support in most cases and would mislead more than inform.
- The Sutrop CSI score itself is rendered as a point estimate (the column ordering metric). The R10 pairing is provided **on the inclusion frequency**, not on the CSI score. The Architect's reading is that the inclusion frequency IS the uncertainty representation for the free-list ranking — the CSI score is a derived measure of which the frequency component is the empirical primitive.

**Fallback-of-the-fallback if CDA SME rejects:** T7a (a `cdb_publish` extension) becomes a prerequisite. T7a would emit per-term per-model bootstrap inclusion frequencies (the fraction of bootstrap-resamples of the run set in which the term appeared) into a new field on `DomainResultPublished` or a sibling file. T7 then consumes that field and renders bars + CIs. The Architect prefers the in-JSON fallback because (a) it avoids a backend round-trip with its own CDA SME + Reviewer + Tester cycle, (b) the empirical ratio is more honest than a bootstrap smoothing over 4 runs would be, and (c) the n_runs = 4 case makes the bootstrap path produce illusory precision.

**CDA SME's binding scope on this question:** approve / reject the empirical-frequency fallback. PASS means T7 proceeds as planned. FAIL means T7a is required and T7 is blocked until T7a ships.

### §2.3. Component breakdown — **2 components (`FreeListCompare`, `FreeListColumn`) + 1 CSS file.**

Flat structure, mirroring the T0 precedent. No utility library expansion, no hook beyond `useState` + `useMemo`.

1. **`apps/dashboard/src/components/FreeListCompare.tsx`**
   - Props: `domainResult: DomainResultPublished`, `modelColors: Record<string, string>`, `selectedModels: string[]`.
   - Computes, with `useMemo` keyed on `[domainResult, selectedModels]`:
     - For each selected model, build a sorted array of `{ item, csi, f_mentions, n_runs, inclusionFrequency }` records from `sutrop_csi[modelId]`, sorted by `csi` descending.
     - A `Set<string>` of terms that appear in ALL selected models (`§3.4 "Terms that appear in ALL selected models highlighted with a shared color"`). Computed once at the parent level and passed down to each `FreeListColumn`.
   - Manages `hoveredTerm: string | null` state for the cross-column highlight (§3.4 "Hovering a term highlights that term across all columns simultaneously").
   - Layout: a horizontally-scrollable flex row of `FreeListColumn` instances, one per selected model. On viewports `<768px`, the row scrolls horizontally (CSS `overflow-x: auto`); on desktop, all columns are visible side-by-side (or scroll if more than ~6 columns at typical viewport widths).
   - Empty-state header at the top of the component: a single short caption identifying what the reader is looking at — `<p>Each column lists the terms one model produced for this domain, ordered by Sutrop salience (Sutrop CSI).</p>`. No "below is", no "explore", no marketing copy. Plain functional sentence.

2. **`apps/dashboard/src/components/FreeListColumn.tsx`**
   - Props: `modelId: string`, `modelColor: string`, `terms: TermRecord[]` (the sorted records), `sharedTerms: Set<string>`, `hoveredTerm: string | null`, `onTermHover: (term: string | null) => void`.
   - Where `TermRecord = { item: string; csi: number; f_mentions: number; n_runs: number; inclusionFrequency: number }`.
   - Renders:
     - A `<header>` with the model color dot (8px circle, color = `modelColor`) and the short model name (`modelShortName(modelId)`).
     - A small caption immediately below the header: `<span>{terms.length} terms</span>` for the count, or `<span>(no terms produced)</span>` when `terms.length === 0` (the §2.5 empty-state caption).
     - A `<ol>` (ordered list — the rank IS the ordering) of `<li>` term pills. Each `<li>` contains:
       - The term text (the `item` string) styled as a pill (rounded rectangle, surface background, model-color-tinted border).
       - The R10 inclusion-frequency bar: a 40px-wide × 4px-tall horizontal bar, filled to `inclusionFrequency × 100%` width using the model color at 60% opacity. The bar is rendered IMMEDIATELY adjacent to the pill (right side; on mobile, below).
       - An accessible label: `aria-label={\`\${item}, salience \${csi.toFixed(2)}, included in \${f_mentions} of \${n_runs} runs\`}` on the `<li>`. This is the R10 disclosure for assistive tech — frequency is paired with the point estimate at the DOM level, not just visually.
   - Hover behavior:
     - On `mouseenter` / `focusin` on a term `<li>`, calls `onTermHover(term)`.
     - On `mouseleave` / `focusout`, calls `onTermHover(null)`.
     - When `hoveredTerm === item`, the pill applies an outline (`outline: 2px solid var(--color-text-primary)`) — the cross-column highlight.
     - Shared-terms (those in `sharedTerms` Set) get a small `★` glyph after the term text — the §3.4 "Terms that appear in ALL selected models highlighted with a shared color" requirement, implemented as a glyph + tooltip rather than a special color (which would conflict with R1-state color encoding).

3. **`apps/dashboard/src/styles/freelist-compare.css`**
   - Token-only. No hardcoded values. Imports nothing; all custom-properties referenced are existing.
   - Layout: `display: flex; gap: var(--space-4); overflow-x: auto;` on the container; `min-width: 200px; max-width: 280px;` on each column; `min-height: 44px;` on each `<li>` for touch targets per WCAG 2.5.5 (touch target size — minimum on mobile).
   - Term pills use `--color-surface` for background, `--color-text-primary` for the term text, `--color-text-caption` for the caption text (`{terms.length} terms`), `--font-mono` for the inclusion-frequency numeric label (the small `"3/4"` text next to each bar).
   - The inclusion-frequency bar uses the column's model color at `opacity: 0.6` for the filled portion and `var(--color-border)` for the unfilled track.

**Total estimated LoC: ~280–360 across the three files.** No new utilities, no shared state with `MDSPlot`, no impact on `ModelSelector`.

### §2.4. Field rendering — exact specification

**Column order:** by the §12.4 lexicographic `model_id` order (same as `MDSPlot` palette assignment). `selectedModels` may be in any order; the component sorts internally.

**Within a column — ordering rule:** by `csi` descending. Ties broken by `mean_position` ascending (earlier mention = more salient). Ties broken again by `item` lexicographic ascending (stable, deterministic).

**How many terms per column:** **all terms in `sutrop_csi[modelId]`, no cap.** Per the kickoff and Mark's "max info" preference, no truncation, no "show more" affordance, no `<details>` collapse. The largest observed list per model is ~150 Sutrop CSI entries (verified against `family.json`); rendering all of them in a flex column with a vertical scrollbar (browser-native on a column whose content exceeds viewport height) is the expected layout. If a future domain produces >500 terms per model, a follow-up commit may add virtualization — out of scope now.

**R10 pairing — exact spec:**

- Each term pill renders the term name + (immediately adjacent) the inclusion-frequency bar + the numeric ratio (`"3/4"` or similar, in `var(--font-mono)` at `var(--font-size-xs)`).
- The bar's filled portion is `(f_mentions / n_runs) * 100%` of the bar's total width.
- The accessible label on the `<li>` (`aria-label`) encodes the full triple: term + CSI score + "included in X of Y runs."
- Below the column header, a single small caption explains the bar: `<p class="freelist-column__r10-caption">Bar shows fraction of collection runs that produced this term.</p>` — rendered once per column, not per pill. Forbidden-vocab-safe wording (no "the model included", just "produced").

**Shared-term glyph:** `★` is appended to the term text inline. `aria-label` adds `"; in every selected model"` to the accessibility string. The glyph color is `var(--color-text-primary)`; the shared-term computation is `Set.intersection`-equivalent (all selected models' term lists). If `selectedModels.length === 1`, no terms are shared (single model is not "all selected"); the glyph is suppressed. If `selectedModels.length === 0`, the component renders the §2.5 zero-state caption — see below.

### §2.5. Empty-state handling — three distinct cases

These are first-class states, not error / placeholder framing (CLAUDE.md §9 pitfalls 4 and 5; ARCHITECTURE.md §1.5.5):

**Case A — `selectedModels.length === 0`:** The user has deselected every model in the `ModelSelector`. Render the `<header>` + container, then a single line: `<p>Select one or more models to see their free lists.</p>`. This is a UX instruction, not a defect framing.

**Case B — `sutrop_csi[modelId]` is missing or empty for some model_id in `selectedModels`:** The column renders with its header + color dot, then the caption `<span>(no salience data for this model)</span>` in `var(--color-text-caption)`. The R10 caption is suppressed for that column. The column has no pills. This case is **defensive** — the live family.json and holidays.json have `sutrop_csi` for every model — but the JSON schema does not strictly guarantee it, and the safety net is cheap.

**Case C — `free_lists[modelId].items` is `[]` and `sutrop_csi[modelId]` is `[]` (the z-ai/glm-5.1 empty-freelist case from memory `project_phase4a1_empty_freelist_propagation.md`):** The column renders with its header + color dot, then the caption `<span>(no terms produced)</span>` in `var(--color-text-caption)`. This is the **finding** — the model produced no free-list terms in this domain — and is rendered as a first-class state per Mark's 2026-04-23 "failures are findings" directive. The caption deliberately avoids "missing," "no data," "pending," "placeholder," "not yet available," "fails to," and any defect framing.

**Note on the actual published 0.2 corpus:** verified against `apps/dashboard/public/data/family.json` and `holidays.json` — neither contains any `"items": []` records. The z-ai/glm-5.1 empty-freelist records exist in `data/raw/` but were not published through the analysis pipeline for these domains. Case C is therefore **defensive coding for forward compatibility**; the Coder must implement it but no current test fixture in the public data exercises it. The Tester writes a synthetic-fixture test for Case C.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. The `freelist` tab in `VizSwitcher` is no longer disabled — clicking it activates the FreeListCompare view; `aria-disabled` is absent from that tab.
3. Loading `<dev-server>/#freelist` on the `family` domain mounts `FreeListCompare` on first paint without flicker to MDSPlot.
4. With 6 default-selected models on `family`, every column renders the model's full `sutrop_csi` list in descending-CSI order with every term as a pill + R10 inclusion-frequency bar + accessible label.
5. Hover on a term in column A triggers the outline highlight on the same term in every column where it appears (columns B, C, …). Hover-out clears all highlights.
6. Keyboard focus on a term pill triggers the same cross-column highlight as hover (per §7 accessibility — focus parity).
7. Each `<li>` term pill has `aria-label` containing `item`, the CSI score, and `"included in X of Y runs"`. The R10 bar visible on screen and the `aria-label` visible to screen readers convey the same uncertainty information.
8. A synthetic fixture domain with `sutrop_csi: { "model-x": [] }` for one model triggers the Case B caption (`"(no salience data for this model)"`). A synthetic fixture with `free_lists.items: []` and `sutrop_csi: []` for one model triggers Case C (`"(no terms produced)"`). Both captions appear in the rendered DOM exactly as specified.
9. The `Set.intersection` of all selected models' term sets is computed correctly: terms in all selected columns receive the `★` glyph; terms in only some columns do not.
10. With `selectedModels.length === 0`, the component renders the Case A instruction (`"Select one or more models to see their free lists."`) and no columns.
11. WCAG AA: every `<header>` is a `<header>` element; the model name is a `<h3>` (heading order: page `<h1>` → article `<h2>` → column header `<h3>` — no skips). The container has `aria-label="Side-by-side free lists"`. Touch targets on `<li>` pills are `min-height: 44px` at viewport widths `<768px` per WCAG 2.5.5. Text contrast: term pills (text on `--color-surface`) and captions (`--color-text-caption` on `--color-background`) meet WCAG AA 4.5:1.
12. The `<meta name="robots">` tag is unaffected (T7 lives at the canonical URL, not the `?inspect` operator surface).
13. Bundle delta ≤ 8 KB gzipped against the post-T0 baseline. Coder reports the delta in the commit body.
14. No new dependencies in `package.json`. No `react-router-dom`, no chart libraries. Coder reuses `modelShortName` from `src/lib/modelShortName.ts` and `modelColors` from the existing `DataExplorer` prop chain.
15. No forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4) anywhere in component prose: column captions, R10 caption, empty-state captions, accessible labels, the optional tooltip text. Field names (`csi`, `f_mentions`, `n_runs`) are exempt as data identifiers. The Reviewer's spot check passes.
16. The text `"worldview"`, `"believes"`, `"thinks"` (applied to models), `"How models see"`, `"What the model understands"`, `"Cultural bias"` (standalone), `"missing"`, `"placeholder"`, `"no data yet"`, `"pending"` do not appear in any T7 source file.
17. Reviewer rule R6 (`SECURITY_AND_HARDENING.md` §9) is not triggered — no `cdb_core/schemas.py` changes; no `DATA_DICTIONARY.md` co-update required.
18. The Coder does NOT touch `apps/dashboard/src/data/types.ts` to "fix" the `free_lists` or `sutrop_csi` type shapes. See §4. (T14 doc-sweep concern.)
19. The Coder does NOT touch `MDSPlot.tsx`, `ModelSelector.tsx`, `Legend.tsx`, or any T5/T4-territory file (SimilarityHeatmap, DriftTracker — those tabs remain disabled).
20. Mobile viewport (`<768px`): the column row scrolls horizontally with no scroll-snap (smooth native scroll); touch targets meet the 44px floor; no layout breakage in viewport widths down to 320px.

---

## §4. Known shape disagreements (Coder note, not a blocker)

`apps/dashboard/src/data/types.ts` and the live published JSON disagree in two T7-relevant places (in addition to the three already documented in the T0 plan §4):

1. **`free_lists` is typed as `Record<string, string[]>`** (`types.ts` line 126) but the live JSON is `Record<string, { run_id, model, domain_slug, items: string[], raw_order: string[] }>` — an object per model_id, not a string array per model_id.
2. **`sutrop_csi` is typed as `Record<string, Record<string, number>>`** (`types.ts` line 150) but the live JSON is `Record<string, Array<{ item, csi, f_mentions, n_runs, mean_position }>>` — an array of structured records per model_id, not a flat term-to-number map.

**T7 follows the files, not the types.** The Coder uses the cast-through-unknown pattern already established in `DataExplorer.tsx` (lines 152, 192, 229) and the T0 `InspectRoot.tsx` precedent:

```
const rawFreeLists = domainResult.free_lists as unknown as Record<string, { items: string[]; raw_order: string[] }>;
const rawSutropCsi = domainResult.sutrop_csi as unknown as Record<string, Array<{ item: string; csi: number; f_mentions: number; n_runs: number; mean_position: number }>>;
```

The Coder **MUST NOT "fix" `data/types.ts` in T7** — that is a T14 doc-sweep concern; touching it now would expand T7 scope per CLAUDE.md §8 ("No surprise scope creep") and would couple T7 to a Phase-6-T14 closing-task review. Surface this disagreement in the commit body for T14 follow-up.

---

## §5. Out of scope for T7

Explicitly excluded; do not partially address:

- **T7a (`cdb_publish` bootstrap-inclusion field).** Out of scope under the §2.2 fallback. Only becomes scope if CDA SME rejects the fallback at plan review; in that case T7 blocks until T7a ships.
- **DriftTracker (T4) and SimilarityHeatmap (T5).** Those tabs remain disabled with the `"Coming in a future update"` tooltip. T7 only enables `freelist`.
- **Methodology page link from FreeListCompare.** The methodology page does not yet exist (T1/T2). No link from FreeListCompare in this commit. T8/T10/T14 may wire it in when T1 ships.
- **`AccessibilityTableToggle.tsx` (T8) for the free-list view.** Phase 5 §12.6 deferral remains active for T7; the "Read as table" toggle is T8 territory. The `aria-label` on each `<li>` is the Phase-6-T7 minimum-viable screen-reader posture; T8 adds the full HTML-table alternative.
- **Mobile bottom-drawer for `ModelSelector` (T12).** Unrelated to T7.
- **Hamburger nav (T11).** Unrelated to T7.
- **Search / filter / sort within columns.** Plain ranked list only. No filter inputs, no search bars.
- **Per-term tooltips with mean position, CSI numeric, and methodology link.** Out of scope. The accessible label on the `<li>` (item + CSI + f_mentions/n_runs) is sufficient for the functional surface. Tooltips are a polish-pass concern.
- **Animation on column entry, on term hover, or on tab switch.** No animation. The Phase-5 §12.1 page-load cascade does not extend to viz-tab switches.
- **Bootstrap CIs on Sutrop CSI scores per term.** Not in the published JSON; not computed from `f_mentions / n_runs` at n_runs=4. Out of scope.
- **Touching `data/types.ts`.** T14 doc-sweep concern; see §4.
- **Touching `MDSPlot.tsx`, `ModelSelector.tsx`, `Legend.tsx`, or any other Phase-5 component.** Surgical edits to `VizSwitcher.tsx` and `DataExplorer.tsx` are the only T7-permitted touches outside the new files.
- **`react-router-dom` or any router framework.** Phase 6 T1 owns that decision; T7 uses the existing `#fragment` permalink scheme unchanged.
- **CSV / JSON export of free-list data.** The existing `DownloadBar` (per T10) handles the full domain CSV download; FreeListCompare itself has no export affordance.
- **A second Vite entry.** Same reason as T0.

---

## §6. Gate routing

- **Architect:** this plan. Once Mark approves, the orchestrator dispatches the gates below.
- **CDA SME: REQUIRED.** Rationale: §2.2 introduces a methodology decision — the R10 fallback uses `f_mentions / n_runs` as the uncertainty representation rather than bootstrap-resample inclusion frequencies. This is methodology-adjacent (CDA SME routing trigger per the Architect's responsibility spec). The four-axis review applies:
  1. **Protocol validity** — is `f_mentions / n_runs` a valid per-term uncertainty representation for a free-list collection protocol?
  2. **Analytical validity** — does the empirical ratio adequately stand in for what a bootstrap-resample inclusion frequency would produce at the 0.2 corpus's n_runs = 4?
  3. **Claims validity** — does the R10 caption ("Bar shows fraction of collection runs that produced this term") accurately describe what the bar encodes? Does the accessible label ("included in X of Y runs") avoid overclaiming?
  4. **Audience translation** — will a journalist or AI engineer reading the column understand that the bar is run-frequency, not bootstrap-CI? Is the §1.5 framing intact?
  - PASS → T7 proceeds as planned.
  - PASS-WITH-NOTES → T7 proceeds; notes apply to caption wording or accessible-label exact text.
  - FAIL → T7a becomes a prerequisite; T7 is blocked until T7a ships and is re-planned to consume the new published field.
- **UI/UX agent: light-touch only — accessibility floor + R10 + token consistency + WCAG AA contrast.** Per `feedback_ui_polish_scope.md` memory. The UI/UX agent reviews:
  1. Every `<header>` is semantic; heading order is correct (no `<h3>` without an enclosing `<h2>`); the container has an `aria-label`.
  2. Text contrast on column captions, term pills, and the R10 caption meets WCAG AA against the chosen background tokens.
  3. R10 pairing: every term pill renders its inclusion-frequency bar adjacent (visual) and its accessible label includes the X/Y-runs disclosure (DOM).
  4. Tokens only: no hardcoded colors, fonts, or spacings; everything via `var(--color-…)` / `var(--space-…)` / `var(--font-…)`.
  5. Touch targets on `<li>` pills are `min-height: 44px` at `<768px`.
  UI/UX issues PASS / PASS-WITH-NOTES / FAIL on those five checks alone. **No design critique** beyond them. No "the layout feels cramped" verdict permitted. The DESIGN_SYSTEM.md §3.4 spec is the authority for column structure; UI/UX may flag deviation from §3.4 but not propose enhancements beyond it.
- **Coder:** implements after CDA SME PASS (or PASS-WITH-NOTES with applied notes) AND UI/UX PASS (or PASS-WITH-NOTES with applied notes).
- **Reviewer:** standard nine-check sweep. Includes the CLAUDE.md §7 forbidden-vocabulary spot check on captions, accessible labels, and the R10 caption. Validates R10 binding (acceptance criteria 4, 7, 11).
- **Tester:** standard vitest. T7's testable surface includes tab activation, column rendering with synthetic 2-model fixture, sort order with deterministic tie-breaks, all three empty-state cases, hover/focus parity, shared-term glyph, accessible label content. No real network fetches; inline fixtures matching the T0 `MOCK_DOMAIN` pattern.

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? |
|---|---|---|
| `cdb_core/schemas.py` | **No** | No |
| `docs/DATA_DICTIONARY.md` | No (no new published fields under the §2.2 fallback) | No |
| `ARCHITECTURE.md` | No (the §4.5 FreeListCompare uncertainty subsection in the kickoff §5 list is updated at T14, not at T7) | No |
| `DESIGN_SYSTEM.md` | No — §3.4 is honored; no new visual decisions outside it. T14 may add §12.10 (new) Free List visual subsection codifying T7's choices. | No |
| `apps/dashboard/src/data/types.ts` | **No** — the §4 disagreements are explicitly deferred to T14 | No |

**Architect sign-off needed for schema change:** **none** — T7 is schema-quiet under the §2.2 fallback. If CDA SME rejects the fallback and T7a is required, T7a will be a separate plan with its own schema-impact section.

---

## §8. Bundle budget watch

Phase 5 closed at 76.25 KB gzipped. T0 added +4.16 KB (verified 2026-05-12 Reviewer verdict). Post-T0 baseline: ~80.4 KB.

T7 estimate:
- `FreeListCompare.tsx` + `FreeListColumn.tsx`: ~4–5 KB gzipped of TSX after tree-shaking.
- `freelist-compare.css`: ~1–2 KB gzipped.
- `VizSwitcher.tsx` edits: net-zero (removing fragments from a Set; widening a type).
- `DataExplorer.tsx` edits: ~0.1 KB (one conditional, one new import).
- No new dependency in `package.json` — zero bundle cost on the dep side.

**Expected delta: ~5–7 KB gzipped.** Under the 8 KB ceiling Mark set for T7.

Phase 6 cumulative budget: 400 KB cap. After T0 + T7: ~85–87 KB total, ~22% of cap. Lots of headroom for T4/T5/T8/T10/T11/T12.

The Coder reports the measured delta in the commit body. Reviewer rejects if > 8 KB delta vs. post-T0 baseline.

---

## §9. Dependency order

**Upstream of T7:**
- T0 (shipped 2026-05-12, commit `39d8a05`) — established the `?inspect=` URL-state precedent, but T7 does not depend on it.
- T7a (`cdb_publish` bootstrap-inclusion field) — **conditional dependency**; required only if CDA SME rejects the §2.2 fallback. The Architect's expectation is PASS, in which case T7a is not built.
- No other Phase-6 task is upstream of T7.

**Downstream of T7:**
- T8 (`AccessibilityTableToggle.tsx` + `ScreenReaderSummary.tsx`) — adds the HTML-table alternative for the free-list view.
- T14 (documentation sweep) — updates `DESIGN_SYSTEM.md` §11 inventory and adds §12.10 codifying T7's visual decisions; updates `ARCHITECTURE.md` §4.5 with the FreeListCompare uncertainty subsection.

**Parallel with T7:**
- T3 (drift data layer), T4 (DriftTracker), T5 (SimilarityHeatmap), T6 (heatmap color tokens), T9 (failures-as-findings data) — all independent of T7 and can dispatch in parallel.

---

## §10. Risks and watch-items

1. **CDA SME rejects the §2.2 fallback.** Probability: low-to-moderate. The empirical ratio is methodologically conservative — strictly weaker claim than a bootstrap-resample interval — and the alternative bootstrap path at n_runs = 4 produces illusory precision. If rejected, T7a becomes a prerequisite and T7 is re-planned to consume the new field.

2. **`data/types.ts` mismatch (§4) tempts the Coder to "fix it while I'm there."** Per CLAUDE.md §8 "No surprise scope creep," the Coder must not. Reviewer rejects T7 commits that touch `data/types.ts`.

3. **The `★` shared-term glyph may render as a system-default emoji on some platforms** (full-color emoji on Windows; monochrome glyph on macOS). The fallback is the Unicode `BLACK STAR (U+2605)` rendered as text in the body font, which most systems will display as a monochrome glyph in the surrounding text color. If UI/UX prefers, an inline SVG star is acceptable; either is within the design system.

4. **Column count vs. viewport.** With 11 models selected on the family domain (max), 11 columns of ~250px-each = ~2,750px horizontal — exceeds typical desktop viewports. The `overflow-x: auto` on the container handles this with native scroll. The §3.4 spec calls out "horizontal scroll appears" for >6 models; T7 honors this.

5. **Hover state on touch devices.** `mouseenter` doesn't fire on touch-only devices; `focusin` is the keyboard / touch-tap equivalent. The Coder must wire both.

6. **Cross-column highlight performance with 11 columns and ~150 pills each.** ~1,650 DOM nodes consult the `hoveredTerm` state. React re-render cost is bounded — each `FreeListColumn` only re-renders when `hoveredTerm` changes, and the cost is dominated by the outline class toggle.

7. **Bundle creep from "just one more interaction."** The Coder MUST resist adding tooltips with mean-position / methodology-link / per-term CSI numerics. T7 is a viewer. Mark's `feedback_ui_polish_scope.md` framing applies.

8. **Sutrop CSI ordering edge case.** If `sutrop_csi[modelId]` has duplicate `(csi, mean_position, item)` triples, the sort is stable. `Array.prototype.sort()` is guaranteed stable in V8 since 2018.

---

*End of T7 plan.*
