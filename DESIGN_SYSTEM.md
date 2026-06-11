# Latent Structure Benchmark (LSB) — Design System & UI Specification

**Document name:** DESIGN_SYSTEM.md  
**Version:** v0.23.0  
**Status:** Draft -- for review by Mark and Opus Architect agent  
**Audience:** UI/UX Agent, Coder agent, Reviewer agent, Mark  
**Companion docs:** `ARCHITECTURE.md` (v0.7+), `CLAUDE.md`

**This document is binding on all frontend work.** The Reviewer agent must reject any component that contradicts it. The UI/UX agent owns this document and must be consulted before any visual decision is made by the Coder agent.

**Changelog:**
- **v0.23.0** (PROMOTE-FOOD-V02 visual disclosure patterns, 2026-06-11) adds §23 specifying three new visual patterns required for the food v0.2 promotion: (a) §23.1 consensus-type override badge (`.content-area__override-badge`) with left-accent `--color-warning` border treatment, `--color-text-primary` text, `--color-surface` background, and methodology-page deep-link anchor; (b) §23.2 CI-disclosure line (`.content-area__ci-disclosure`) and small-n line (`.content-area__small-n-line`) both using `--color-text-caption` at `--font-size-xs`, with byte-identical F3-R3-C and F3-R3-D display strings sourced from a dedicated copy module; (c) §23.3 SimilarityHeatmap model-exclusion caption (`.heatmap-exclusion-caption`) rendered in ContentArea.tsx below the heatmap, using `displayModel()` in visible text and full `model_id` in aria-label per §18.5. No new CSS custom properties. All tokens confirmed present in `tokens.css`. WCAG AA: override badge text 12.34:1 PASS; CI-disclosure and small-n lines 4.60:1 PASS; exclusion caption 4.60:1 PASS. CDA SME PASS-WITH-NOTES (`docs/status/2026-06-11-promote-food-v02-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-11-promote-food-v02-uiux-verdict.md`).
- **v0.22.0** (F5-T1 degenerate bootstrap ellipse converged-state treatment, 2026-06-11) adds implementation requirement 12 to §3.3.5, documenting the R1-a degenerate-bootstrap sub-state (semi_major <= 0) as the LIMIT case of a high-stability R1-a sample where the bootstrap converged on a near-point. Visual treatment: minimum-radius ellipse floor (rx=3, ry=3 px) rendered at the data point, same fill/stroke/opacity as standard R1-a ellipse, tagged data-degenerate-bootstrap="true". Dot marker: same circle as standard R1-a but additionally carries data-r1-state="typical_concentration", data-degenerate-bootstrap="true", and S2 aria-label. MDSPlot tooltip shows S1 (UI/UX-corrected) body for degenerate models. S3 disclosure threads through .term-dot aria-label in TermMap (NOT .term-ellipse, which has pointer-events=none). S4 disclosure threads through family-member inner circle in Focus2FamilySimilarity. Three components updated: MDSPlot.tsx, TermMap.tsx, Focus2FamilySimilarity.tsx. No new tokens. WCAG AA: minimum-radius ellipse uses same provider color token as standard R1-a ellipse (3:1 graphical-object contrast confirmed by existing T15 token audit). CDA SME PASS-WITH-NOTES (S1-S4 bound strings, B1-B10 binding notes; `.claude/agent-memory/cda_sme/project_f5_degenerate_ellipse_verdict.md`); UI/UX PASS-WITH-NOTES (minimum-radius option (a) selected, impl req 12 this update, S1 corrected per §3.3.5 impl req 5 removing "R1-a sample" jargon). Gate verdicts: docs/status/2026-06-10-codebase-review-fixes-verdicts.md F5 section.
- **v0.21.1** (footnote band visual design, TM-D, 2026-06-11) adds §3.1.1(d) specifying the `.term-map-cluster-footnotes` band as a designed component with a load-bearing constant-height contract. Stylesheet file: `app.css`. CSS class `.term-map-cluster-footnotes` (ol) and `.term-map-cluster-footnotes__empty` (placeholder li modifier). Height: 48px CONSTANT (BINDING, oscillation-safety). All inline styles removed from TermMap.tsx. No new tokens. Tokens used: `--font-size-xs`, `--font-weight-regular`, `--line-height-data`, `--color-text-caption`, `--color-border`, `--color-background`, `--space-1`, `--space-6` (all confirmed present in tokens.css). WCAG AA: `--color-text-caption` (#6c757d, 4.60:1 on white, PASS at 12px regular weight). Gate verdicts: CDA SME PASS-WITH-NOTES (routing-only, docs/status/2026-06-10-termmap-layout-verdicts.md TM-D section); UI/UX PASS-WITH-NOTES (this update, 2026-06-11).
- **v0.21.0** (chart-to-record provenance pivot, G7-FOLLOWUP-T1, 2026-06-11) adds §19.19 specifying the pivot affordance that lets a researcher click from MDSPlot tooltip or Focus 1 individual-model header to the Collection records tab, scrolled and highlighted to the matching per-model summary row for the current domain. New CSS classes: `.chart-tooltip__pivot-btn` (app.css), `@keyframes pivot-arrival-fade` (failures-findings.css), `.failures-findings__successes-tr--pivot-arrival` (failures-findings.css), `.failures-findings__pivot-arrival-caption` (failures-findings.css), `.failures-findings__pivot-arrival-notice` (failures-findings.css). No new tokens. MDSPlot tooltip affordance is pointer-enhancement-only (N4 keyboard/SR ruling); Focus 1 header affordance is the keyboard-accessible path. WCAG AA token correction: `.failures-findings__pivot-arrival-notice` uses `--color-text-caption` (#6c757d, 4.60:1 on white) NOT `--color-text-secondary` (#7f8c8d, 3.40:1 -- WCAG AA fail at 14px regular weight). Gate verdicts: CDA SME PASS-WITH-NOTES (`.claude/agent-memory/cda_sme/project_g7_followup_t1_plan_verdict.md`); UI/UX PASS-WITH-NOTES (this update, 2026-06-11).
- **v0.20.6** (T-MDS-R1 geometry and prop pins, 2026-06-10) adds implementation requirements 9, 10, 11 to §3.3.5, pins the R1-b stroke-dasharray value, pins the R1-c triangle polygon geometry, specifies the new ociValues prop contract for MDSPlot.tsx, and corrects the em-dash-containing tooltip copy in the R1-b table entry and implementation requirements 5 and 6 to the CDA SME F3/F4/F8 approved em-dash-free versions. No new tokens. Gate verdict: UI/UX PASS-WITH-NOTES (this update, 2026-06-10); CDA SME binding strings per T-MDS-R1 SME verdict.
- **v0.20.5** (SVG hex literal migration to design tokens, T15, 2026-06-10) adds seven new SVG chrome tokens to §1.2 (placement: after `--color-surface-hover`, before the sequential scale block). Token block: `--color-svg-grid-line` (#f0f0ec, TermMap warm-white grid lines), `--color-svg-grid-line-neutral` (#eeeeee, MDSPlot/Focus2 neutral gray grid lines; erratum 2026-06-10: the first T15 commit consolidated these onto #f0f0ec against the UI/UX ruling, corrected same day), `--color-svg-axis-caption` (#a0a098, axis label text; pre-existing WCAG fail at 11px preserved zero-delta, remediation deferred), `--color-svg-label-secondary` (#4a4a4a, model/term label text in MDS components), `--color-svg-marker-stroke` (#888888, fallback neutral stroke in FreeListCompare/PileStructure/Focus1SelfConsistencyOverview/Focus2FamilyOverview), `--color-svg-gray-branch` (#999999, cross-cluster branch in ClusterTree; consolidation ruling: #888 and #999 stay on separate tokens), `--color-svg-dot-stroke` (#ffffff, dot outline stroke in TermMap/MDSPlot/Focus2FamilySimilarity). Components updated: TermMap.tsx, MDSPlot.tsx, Focus2FamilySimilarity.tsx, SimilarityHeatmap.tsx, ClusterTree.tsx, FreeListCompare.tsx, PileStructure.tsx, Focus1RunDistribution.tsx, Focus2FamilyOverview.tsx, Focus1SelfConsistencyOverview.tsx. All values byte-identical to migrated literals: zero visual delta. New test: `__tests__/tokens-defined.test.ts` (pitfall-15 guard). Gate verdicts: CDA SME PASS (routing not required, no methodology surface); UI/UX PASS-WITH-NOTES (notes binding, see `docs/status/2026-06-10-codebase-review-fixes-verdicts.md` T15 section). Commit: `refactor(dashboard): migrate SVG hex literals to design tokens (T15)`.
- **v0.20.3** (Per-attempt retry-transcript block, CR-T8, 2026-06-10) adds §19.18 specifying the attempts block rendered inside a failure record's expanded body when `retry_attempts` is non-empty. Layout: labeled section with framing paragraph followed by one card per attempt, each showing `attempt_index` heading (0-indexed), response verbatim in a `<pre>`, and an optional provenance list for `stop_reason` and `parse_error_message` (labeled "LSB parser-state diagnosis"). New CSS classes in `failures-findings.css`: `.failures-findings__attempts`, `.failures-findings__attempts-framing`, `.failures-findings__attempt`, `.failures-findings__attempt-heading`. WCAG AA ruling: `.failures-findings__attempt-heading` uses `--color-text-primary` (NOT `--color-text-secondary`). No new tokens. Six new vitest cases (41-46); case 40 (case 9 extended) further extended to materialise the attempts block and scan its chrome. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T8 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T8 section).
- **v0.20.3** (Term Map label declutter, TM-C, 2026-06-10) implements
  §3.1.1(c) label-declutter rule. Six changes from TM-C UI/UX gate:
  (1) Cluster label font changed from ad-hoc 26px/20px to `var(--font-body)`
  at `var(--font-size-sm)` (14px) + weight 600, per §3.1.1(c) binding spec.
  (2) Cluster label color changed from hardcoded `#000000` to
  `var(--color-text-primary)`, per §3.1.1(c).
  (3) Fallback variant elected: greedy displacement with leader lines (D1).
  Leader line color corrected from `var(--color-border)` (~1.13:1, WCAG FAIL)
  to `var(--color-text-caption)` (#6c757d, ~4.60:1, WCAG 1.4.11 PASS).
  (4) Hidden cluster labels rendered in `<ol className="term-map-cluster-footnotes">`
  below chart with `aria-label="Cluster labels not shown on map due to space
  constraints."` (footnote-list fallback per D1 election).
  (5) Zoom-dependent term-label density: top-50% salience at k=1, all at k>=1.5,
  linear step between. Salience source: published Sutrop CSI field (CDA SME N2).
  (6) CDA SME N1 caption: "Labels shown for top-salience terms at this zoom
  level. Zoom in or hover with the magnifying lens to see all terms." Rendered
  at k<=1.5 only. No new tokens. Pitfall 15 token pre-check: all `var(--...)`
  references confirmed present in `tokens.css`. Gate verdicts: CDA SME
  PASS-WITH-NOTES; UI/UX PASS-WITH-NOTES
  (`docs/status/2026-06-10-termmap-layout-verdicts.md`, TM-C section).
- **v0.20.2** (Per-record raw-exchange detail surface, CR-T7, 2026-06-10) adds §19.17 specifying the per-record expand affordance on the successful-records summary table, the per-record detail body structure, the step-section layout, the provenance block, and mobile/accessibility rules. Navigation pattern decision: expand button in a new rightmost column of the §19.15 per-model table, revealing a sibling full-width detail row (colSpan={6}). New CSS classes in `failures-findings.css`: `.failures-findings__detail-row`, `.failures-findings__detail-cell`, `.failures-findings__expand-btn`, `.failures-findings__detail-step`, `.failures-findings__detail-step-heading`. No new tokens. Eight new vitest cases (33-40); case 9 extended over the expanded detail DOM. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T7 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T7 section).
- **v0.20.1** (ChartToolbar chrome and lede-column overflow ruling, TM-B UI/UX gate, 2026-06-10)
  amends §3.1.1(b)(ii) with binding ChartToolbar visual chrome rules: background
  `var(--color-surface)`, border-bottom `1px solid var(--color-border)` only (no top border, no
  box-shadow). Amends §3.1.1(b)(iii) lede-column scroll note to specify `overflow-y: auto` on the
  lede column wrapper and confirm no `prefers-reduced-motion` exception is required. No new tokens.
  Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-termmap-layout-verdicts.md`,
  TM-B section).
- **v0.20.0** (Chart-area hierarchy amendment, TM-A, 2026-06-10) adds §3.1.1 "Chart-area hierarchy
  on the Explore page" between §3.1 and §3.2. Establishes three binding rule families: (a) chart-area
  minimum height of 70vh on desktop and above-the-fold rule; (b) control-row consolidation rules
  (SHOWING chips removed from all VizTabs, unified chart toolbar for TermMap controls, lede paragraph
  moved beside/below chart per breakpoint); (c) label-declutter rule for Term Map (collision-aware
  cluster-label placement, zoom-dependent term-label density). CDA SME M1/M2/M3 mandatory notes
  all addressed in amendment text. §3.3.5 R1-a/R1-b/R1-c invariants, §15.2 cluster-color ellipse
  rule, §3.3.5 binding invariant 1, ARCHITECTURE.md §1.5 framing, and CLAUDE.md pitfall 15 all
  explicitly preserved. No new tokens. Six-sub-point lede preservation clause included (M1).
  Gate verdicts: CDA SME PASS-WITH-NOTES; UI/UX PASS-WITH-NOTES
  (`docs/status/2026-06-10-termmap-layout-verdicts.md`).
- **v0.19.5** (Counts caption update, CR-T6, 2026-06-10) amends §19.4 step 6 (counts caption): caption now names parsed-primary-step-response count using Option C (no leading total; CDA SME N1 binding). `countsCaptionText()` in `copy/failures_findings.ts` gains an optional `nParsedResponses?: number` parameter (N5). Four-cell empty-state matrix (N3): (n_records > 0, parsed > 0) full three-clause; (n_records > 0, parsed === 0 or undefined) failure-clause-only; (n_records === 0, parsed > 0) S-clause-only; (n_records === 0, parsed === 0 or undefined) caption omitted. Records-not-ready state preserves failures-only caption (N4). Adds new §19.16 specifying the caption template, four-cell matrix, and render conditions. Six new vitest cases (27-32); case 9 extended with N6 affirmative check. No new CSS classes. No new tokens. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T6 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T6 section).
- **v0.19.4** (Successful-records summary section, CR-T5, 2026-06-10) amends §19.4 content order: adds step 8 (successful-records summary section) below the failures/decline-interviews list (and below EMPTY_CAPTION when n_records === 0). Adds new §19.15 specifying the successful-records summary section structure, element spec, CSS classes, fetch coupling, and vitest cases. TAXONOMY_BLOCK.topLevel[0].description updated (SME N6 conditional revision): drops stale "when the successes section ships" phrasing; now reads "...Surfaced in the per-model summary section below..." New CSS classes in `failures-findings.css`: `.failures-findings__successes`, `.failures-findings__successes-heading`, `.failures-findings__successes-framing`, `.failures-findings__successes-empty`, `.failures-findings__successes-table-wrapper`, `.failures-findings__successes-table`, `.failures-findings__successes-th`, `.failures-findings__successes-tr`, `.failures-findings__successes-td`, `.failures-findings__successes-td--num`, `.failures-findings__successes-code`, `.failures-findings__successes-caption`, `.failures-findings__successes-status`, `.sr-only`. No new tokens. Seven new vitest cases (20-26); case 9 extended. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T5 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T5 section).
- **v0.19.3** (Taxonomy block, CR-T3, 2026-06-10) amends §19.4 content order: inserts taxonomy block (`TAXONOMY_BLOCK`) as new step 4 (between `IMPACT_PARAGRAPH_FAILURES` step 3 and `framing_note` step 5); former steps 4-6 renumber to 5-7. Adds new §19.14 specifying the taxonomy block structure, element spec, CSS classes, and placement. New CSS classes in `failures-findings.css`: `.failures-findings__taxonomy`, `.failures-findings__taxonomy-heading`, `.failures-findings__taxonomy-bridge`, `.failures-findings__taxonomy-list`, `.failures-findings__taxonomy-enum-label`. No new tokens. Taxonomy block renders in `ready` state including the empty-state path (n_records === 0); does not render in loading/fetch-failed/malformed states. Element structure: `<section aria-labelledby>` + `<h2>` heading + bridge `<p>` + two `<ul>` lists (top-level outcomes and enum values). Four new vitest cases (16-19). Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T3 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T3 section).
- **v0.19.2** (Follow-up interviews impact paragraph, CR-T2, 2026-06-10) amends §19.4 content order: step 6 (records list) is now split into two groups with the follow-up impact paragraph (`IMPACT_PARAGRAPH_FOLLOWUPS`) inserted between them. Failure records render in a first `<ol className="failures-findings__list">`, then conditionally (when at least one `decline_interview` record is present) the `IMPACT_PARAGRAPH_FOLLOWUPS` `<p className="failures-findings__impact">` renders, then decline records render in a second `<ol className="failures-findings__list">`. CSS class reuses `.failures-findings__impact` (no new class, no new tokens). Follow-up impact paragraph renders only when `data.records.some(r => r.record_type === 'decline_interview')` is true; does not render in loading/fetch-failed/malformed states or when zero decline_interview records are present. Two new vitest cases added: byte-identity under `familyJson` (case 14), absent under `foodJson` (case 15). Also corrects pre-existing closing-line version string from `v0.19.0` to `v0.19.2`. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T2 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T2 section).
- **v0.19.1** (Impact paragraph for collection failures, CR-T1, 2026-06-10) amends §19.4 content order: inserts "Impact paragraph (`IMPACT_PARAGRAPH_FAILURES`) `<p>`" as new step 3 (between heading step 1 and domain selector step 2); old steps 3-5 renumber to 4-6. Adds new CSS class `.failures-findings__impact` to `failures-findings.css` (tokens: `--font-size-base`, `--color-text-primary`, `--line-height-body`, `--space-6`, `--max-prose-width`). No new tokens. The paragraph renders inside the `ready` fetch state only (AC4); renders in the empty-state path (n_records === 0, AC3). Three new vitest cases added: byte-identity (case 11), empty-state paragraph present (case 12), absent in loading state (case 13). Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T1 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T1 section).
- **v0.19.0** (About page, M2, 2026-06-10) adds `AboutPage.tsx` (Mark-authored text). Adds NavBar fifth tab "About" at rightmost position (binding least-prominent slot: benchmark and data presentation remain primary; About entry must not dominate the nav). Mirrors `MethodologyPage.tsx` class structure (`.methodology-page`, `.methodology-page__container`, `.methodology-page__section`, `.methodology-page__heading`, `.methodology-page__text`); no new tokens, no new CSS. Adds §22 About page spec. Updates §11 Component Inventory. Corrects pre-existing closing-line version string from `v0.17.0` to `v0.19.0` (UI/UX N3 advisory). Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md` M2 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md` M2 section).
- **v0.18.0** (Methodology rewrite + provenance section move — M1, 2026-06-10) replaces the v0.17.0 Coder-built placeholder prose in sections 1-6 of `MethodologyPage.tsx` with Mark-authored final text (eight sections; CDA tradition, forebears credit with verified links). Moves the §15.5(a) `Data provenance` section and the §16.2 `Cross-model term map and uncertainty` section from `MethodologyPage.tsx` to `DataPage.tsx` (placement: after Section H Provenance pointer). Adds a new "Provenance" pointer section at the end of `MethodologyPage.tsx` (in-app `/data` link, §6.3). Fixes a duplicate-id defect introduced by the move (DataPage Section H heading id renamed to `data-provenance-pointer-heading`). Adds §6.3 (provenance-pointer note, in §6 methodology page architecture section). Updates §15.5(a), §16.2 placement paragraphs, and §11 inventory entries. No new tokens. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md`).
- **v0.17.0** (Published lede wire-up — Phase 9a T2, 2026-06-09) adds §21 (`.chart-lede` binding token spec). `ContentArea.tsx` Focus-3 lede strip now renders `domain.generated_lede` verbatim in a single `<p className="chart-lede" aria-live="polite">`. Inline-computed lede block (lines 199-220, `selectedModelIds.size` branching, "Consensus baseline (all tested models):" label, inline Smith's S computation) removed. WCAG AA contrast fix: `.chart-lede` color changed from `var(--color-text-secondary)` (~3.40:1, FAILS AA) to `var(--color-text-caption)` (~4.60:1, PASS). R1-b low-output-concentration disclosure restored on family and food domains. §12.9 SR-template boundary note updated: `generated_lede` now rendered in `ContentArea.tsx` (not only `ArticleHeader.tsx`). No new tokens. Gate verdicts: CDA SME PASS (`docs/status/2026-06-08-phase9a-T2-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T2-uiux-verdict.md`).
- **v0.16.0** (Data download tab — Phase 9a task 6, 2026-06-09) adds §20 and the `--color-surface-note` semantic alias token (§1.2). New component `DataPage.tsx` replaces the `navTab === 'data'` placeholder. Section render order B/D/A/C/E/F/G/H (UI/UX binding). No new dependencies. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-data-tab-ui-ux-verdict.md`).
- **v0.15.0** (Collection records tab — Phase 9a T1, 2026-06-09) adds §19. New top-level NavBar tab "Collection records" at position [Explore][Methodology][Collection records][Data]. New files: `FailuresFindings.tsx`, `copy/failures_findings.ts`, `styles/failures-findings.css`, `__tests__/FailuresFindings.test.tsx`. No new tokens. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T1-failures-restore-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T1-failures-restore-uiux-verdict.md`).
- **v0.14.0** (displayModel canonical label — T8, 2026-06-08) adds §18. Single canonical
  export `displayModel(modelId)` in familyUtils.ts; bans component-local re-implementation;
  collapses the 16 drifted shortName/shortModelName/shortModelDisplayName helpers. Strip rule (Mark's ruling):
  org prefix + `claude-` only. No new tokens. UI/UX PASS-WITH-NOTES.
- **v0.13.1** (T3 undefined `--font-size-md` token fix, 2026-06-08) amends §1.1 to add a clarifying note that there is deliberately no `--font-size-md` token (the scale steps base 16px → lg 18px; pitfall #15 silent-fallback guard). Adds §13.12 binding `.f1-model-heading` typography spec: `--font-size-base` (16px) + `--font-weight-bold` (700) + `--color-text-primary`. No new tokens. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-T3-font-size-md-uiux-verdict.md`). Recurrence-guard CI check deferred (out of scope per UI/UX gate — Architect backlog item).
- **v0.13.0** (term-map drag-pan re-add + bottom-clipping fix, 2026-06-04) amends §17.4 (replaces "Drag-pan REMOVED" paragraph with re-added drag-pan spec); adds §17.11 (updateScrollableModifier + useLayoutEffect k=1 overflow fix + drag-pan handler contract) and §17.12 (cursor CSS: `grab`/`grabbing` + `--dragging` class + reduced-motion guard). No new tokens. `pad.b` raised from 40 → 52; SVG footer annotation `y=H-6` → `y=H-14`. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-06-04-drag-pan-clipping-uiux-verdict.md`).
- **v0.12.0** (food promotion provenance surfaces, 2026-05-31) amends §15.5(b): `ProvenanceFooter.tsx` date suffix now sourced from `provenance.json` top-level `generated_at_utc` (`.slice(0,10)`); `generated_at_utc?: string` added to `ProvenanceData` interface; date span render-nothing when field absent. Adds §16.2 (term-MDS disclosure placement: stub section in MethodologyPage.tsx with M4a sentence + C3 n-count disclosure). No new tokens. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-31-food-promote-ui-ux-verdict.md`); CDA SME PASS-WITH-NOTES (`docs/status/2026-05-31-food-promote-cda-sme-verdict.md`).
- **v0.11.0** (TermMap Stage 2 scrollbar zoom model, 2026-05-31) replaces §17.4 "reserved" placeholder with the full Stage 2 spec; adds §17.8 (pan-viewport scrollbar CSS) and §17.9 (prefers-reduced-motion forward-guard). New CSS classes: `.term-map-pan-viewport`, `.term-map-pan-viewport--scrollable`. Drag-pan handlers removed; viewBox-zoom → content-scale model (SVG viewBox frozen, `<g id="term-content" transform="scale(k)">`). Lens auto-disabled at k>1.02 (Q2 LOCKED). No new tokens. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-31-termmap-stage2-uiux-verdict.md`); Architect plan (`docs/status/2026-05-31-termmap-redesign-architect-plan.md`). Stage 2 automated tests deferred to T7 (no vitest harness).
- **v0.10.0** (TermMap layout+zoom Stage 1, 2026-05-31) adds §17 (TermMap container height bounding, Ctrl+wheel zoom gate, keyboard +/−/Reset zoom buttons, hint text, aria-live). Two new CSS classes: `.term-map-controls__zoom-btn`, `.term-map-controls__zoom-reset`. No new tokens. Stage 2 scrollbar model reserved (§17.4). Gate verdicts: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-31-termmap-layout-zoom-uiux-verdict.md`); Architect plan (`docs/status/2026-05-31-termmap-redesign-architect-plan.md`).
- **v0.9.0** (PROMOTE-2 provenance surfaces, 2026-05-30) adds `ProvenanceFooter.tsx` and `MethodologyPage.tsx` to §11 Component Inventory; adds §16 (provenance surfaces: §15.5(a) methodology "Data provenance" section, §15.5(b) global per-domain conditional footer). `body` CSS gains `display: flex; flex-direction: column`; `.app-main` changes from `height: calc(100vh - 48px)` to `flex: 1 1 0; min-height: 0`. No new tokens. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-30-promote2-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-30-promote-ui-ux-verdict.md`); Architect sign-off (`docs/status/2026-05-30-provenance-json-architect-signoff.md`).
- **v0.8.1** (Remedy B T4 copy cleanup, 2026-05-29) corrects §11 `CentralityTable.tsx` column inventory: removes the "Bootstrap N" column (the published `centrality_ci` is a bare `[lo, hi]` tuple; B=500 is a domain-wide quantity stated in the SR summary and table caption, not a per-model column). No new tokens, no visual decisions. Applies CDA SME M1/M2 + Reviewer Item 3 from `docs/status/2026-05-28-remedy-b-t4-cda-sme-verdict.md`.
- **v0.8.0** (viz-fixes fix-forward, 2026-05-28) adds §15 (Term stability pill tiers, TermMap uncertainty ellipse color, `.term-map-controls` inline-style grandfather, tooltip font-size exception). No new color tokens. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-28-viz-fixes-ui-ux-verdict.md` items 2–4).
- **v0.7.0** (F2-T1–T7 UI/UX gate, 2026-05-27) adds §14 (Focus 2 — Within-Provider Family Comparison visual decisions). Three-pill focus selector (§14.1), family sidebar single-select (§14.2), family overview cards with pairwise/mean labeling per CDA SME notes (§14.3), mini heatmap (§14.4), MDS ring highlight (§14.5), salience/pile reuse (§14.6), focus ordering rule (§14.7), model color retention (§14.8), Focus 2 tab IDs (§14.9), description paragraphs (§14.10), cite path (§14.11), single-family state (§14.12), forbidden vocabulary (§14.13). No new tokens.
- **v0.6.0** (F1-T5 through F1-T9 UI/UX gate, 2026-05-27) adds §13 (Focus 1 — Individual Model Consistency visual decisions). Introduces: focus-level selector navigation (§13.1), single-select sidebar mode for Focus 1 (§13.2), ranked-list Self-Consistency Overview layout (§13.3), concentration tier badge vocabulary and color treatment (§13.4, no semantic color — border intensity only), OCI display with CI fallback and underestimation caveat affordance (§13.5), run agreement heatmap color scale assignment (§13.6, reuses existing sequential scale), run MDS specification with CDA SME S3 suppression rule and non-color centroid discriminator (§13.7), term stability dashed-border tier treatment (§13.8, mirrors §12.10), Focus 1 ActiveVizTab extensions (§13.9), journalist description paragraph copy (§13.10), and cite-path SourceAttribution/CSV requirements (§13.11). Two new constants added to `apps/dashboard/src/config/analysis.ts`: `OCI_CONCENTRATED_THRESHOLD`, `OCI_MODERATE_THRESHOLD`. No new color tokens. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-27-F1-T5toT9-uiux-verdict.md`).
- **v0.5.2** (Phase 9a T6+T7, 2026-05-24) adds `TermMDSPlot.tsx`, `TermMDSTable.tsx`, `term-mds-plot.css`, `Dendrogram.tsx`, `DendrogramTable.tsx`, `dendrogram.css` to §11 Component Inventory. Introduces cluster color palette tokens (`--color-cluster-1` through `--color-cluster-8`) in §1.2. Extends `ActiveVizTab` to include `"term-mds"` and `"cluster-tree"`. VizSwitcher tab count: 6 → 8 (Term Map at index 1, Cluster Tree at index 2). Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md`).
- **v0.5.1** (Phase 9a T9, 2026-05-24) adds `PileComparison.tsx`, `PileComparisonTable.tsx`, and `pile-comparison.css` to §11 Component Inventory. Adds §12.10 PileComparison visual specification. Extends `ActiveVizTab` to include `"piles"` and `PermalinkState.vizTab` to include `"piles"`. VizSwitcher tab count: 5 → 6 (Pile Structure inserted at index 4). No new tokens. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md`).
- **v0.5.0** (Phase 9a T10, 2026-05-24) adds `CentralityChart.tsx`, `CentralityTable.tsx`, and `centrality-chart.css` to §11 Component Inventory. Introduces dark inverted tooltip token set (`--color-tooltip-dark-bg`, `--color-tooltip-dark-text`, `--color-tooltip-dark-divider`) in §1.2 for dense multi-line data tooltips. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-T10-ui-ux-verdict.md`).
- **v0.4.10** (T14 documentation sweep, 2026-05-16) extends §11 Component Inventory with ten Phase 6 components shipped in T0/T7/T8/T9/T10 that were not yet listed: `FailuresFindingsSection.tsx` (T10), `FailuresInspectView.tsx` (T0+T10), `FreeListColumn.tsx` (T7), `FreeListTable.tsx` (T8), `InspectRoot.tsx` (T0), `InspectSection.tsx` (T0), `InspectTable.tsx` (T0), `MdsTable.tsx` (T8), `ReadAsTableToggle.tsx` (T8), `SimilarityTable.tsx` (T8). `ScreenReaderSummary.tsx` already listed; not re-added (M1). `AccessibilityTableToggle.tsx` pending entry annotated as renamed to `ReadAsTableToggle.tsx` per T8 UI/UX verdict. Verification pass (AC7): all Phase 6 tokens confirmed present in §1.2 and `tokens.css` — no tokens missing. Verification pass (AC8): §2.3 domain nav confirmed `[Family] [Holidays] [Food] [Emotion *] [Justice *]`, no edit required. Internal-consistency verification: §12.8 vs. v0.4.9 CONSISTENT; §12.9 vs. v0.4.6 CONSISTENT; §8.1 vs. v0.4.7 CONSISTENT; §8.2 vs. v0.4.8 CONSISTENT. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-16-phase6-T14-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-16-phase6-T14-uiux-plan-verdict.md`). No new tokens. No new visual decisions.
- **v0.4.9** (T6 plan-level UI/UX verdict, 2026-05-15) introduces the §1.2 sequential color scale token set (`--color-scale-seq-0` through `--color-scale-seq-4`) as a perceptually-graded OWID-style single-hue blue ramp (light gray-blue → deep navy). Mark's Posture B choice: replaces the T5 alpha-blend formula `rgba(44, 62, 80, similarity)` with a 5-stop discrete-binning model. SimilarityHeatmap.tsx is reworked: `cellBackground()` now maps similarity to one of five named hex stops via bin boundaries [0, 0.20, 0.40, 0.60, 0.80, 1.00]; `HEATMAP_TEXT_SWITCH_THRESHOLD` changes from 0.73 to 0.60 (dark text on stops 0–2, white text on stops 3–4, both arms ≥4.5:1 WCAG AA). §12.8 rewritten for the new palette with full WCAG AA contrast table. CI-crosses-null dashed-border treatment retained verbatim from T5 (T14 follow-up per CDA SME T5 §5.4). Stops 0–2 do not pass WCAG 3:1 standalone-swatch contrast on white; documented as compositional-only (used only as heatmap cell fills with adjacent cell borders and similarity text, not as standalone swatches). Token `--color-heatmap-cell-text-dark: #000000` retained (pure black required; `--color-text-primary` fails at stop 2 at 3.31:1). No diverging scale added. See `docs/status/2026-05-15-phase6-T6-uiux-plan-verdict.md`.
- **v0.4.8** (T12 plan-level UI/UX verdict, 2026-05-15) extends §8 with §8.2 (Mobile bottom-drawer for ModelSelector — full specification). Adds `MobileModelSelectorDrawer.tsx`, `apps/dashboard/src/copy/mobile_model_drawer.ts`, and `apps/dashboard/src/styles/mobile-model-drawer.css` to §11 component inventory. Codifies: ARIA dialog pattern with focus trap (mirroring §8.1.1); half-sheet panel from bottom (max-height: 75vh, position: fixed bottom edge); semi-opaque backdrop scrim above panel; close button inside panel receives initial focus; live-update selection semantics (no Apply button); Esc + scrim-tap + close-button dismissal; scroll lock on open (body overflow hidden — key divergence from §8.1); inline DOM mount inside DataExplorer.tsx (position: fixed escapes stacking context); z-index: 200 (matching §8.1.14 hamburger, both surfaces cannot co-render at <768px); slide-up transition 200ms ease-out, gated by prefers-reduced-motion (instant when reduced-motion set); trigger button styling 48×48 px touch target, full-width at <768px; min-height: 44px on .model-selector__row inside drawer; stacked-below app.css rule superseded; confirmed a11y strings verbatim; no visible heading inside drawer (aria-label on dialog panel only); no Apply button (live update); no swipe gesture; no drag handle. No new tokens.
- **v0.4.7** (T11 plan-level UI/UX verdict, 2026-05-15) extends §8 with §8.0 (general mobile behavior, retaining existing bullets) and §8.1 (Mobile hamburger menu — full specification). Adds `MobileNav.tsx`, `Header.tsx` (T11 update), `apps/dashboard/src/copy/mobile_nav.ts`, and `apps/dashboard/src/styles/mobile-nav.css` to §11 component inventory. Codifies: ARIA dialog pattern with focus trap; three-line hamburger glyph (inline SVG, 20×16 viewBox, 2px stroke, 6px center-to-center gap); no glyph-to-X transform (single close button inside panel, initial focus lands there); full-screen overlay panel from top; instant open/close (no transition, `prefers-reduced-motion` trivially satisfied); no backdrop scrim (full-bleed panel); trigger button styling (tokens only); open-panel link styling (tokens only); 48×48 px touch targets; trigger hidden when panel open; no visible heading inside panel (aria-label only); confirmed a11y strings verbatim; no scroll lock; inline mount inside Header.tsx (not a portal). No new tokens.
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
/* NOTE: There is deliberately no --font-size-md token. The scale steps directly
   from base (16px) to lg (18px). Sub-view headings that need a step between body
   and lede text use --font-size-base + --font-weight-bold — not a phantom `md`.
   Any var(--font-size-md) reference is undefined and invalid at computed-value
   time; because font-size is an inherited property, it silently falls back to
   the inherited value (the parent's font-size), not the initial value
   (pitfall #15). */

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

/* Cluster color palette — term-level cluster encoding (Phase 9a T6/T7, 2026-05-24) */
/* Semantically distinct from model colors (--color-model-*). Never mix these      */
/* two palettes in the same legend. All pass WCAG AA 3:1 on white. 8 slots;        */
/* 9th+ clusters get --color-text-secondary with a numeric label.                  */
--color-cluster-1: #e05c2e;   /* warm orange-red;  ~4.4:1 on white */
--color-cluster-2: #2e7d4f;   /* forest green;     ~5.1:1 on white */
--color-cluster-3: #b5590a;   /* dark amber;       ~4.2:1 on white */
--color-cluster-4: #5c3298;   /* dark violet;      ~7.2:1 on white */
--color-cluster-5: #1d6b8f;   /* steel blue;       ~5.0:1 on white */
--color-cluster-6: #8f1d55;   /* dark rose;        ~5.7:1 on white */
--color-cluster-7: #4a6e1a;   /* olive green;      ~5.4:1 on white */
--color-cluster-8: #6b3a1f;   /* dark brown;       ~6.1:1 on white */

/* Tooltip — dark inverted variant (Phase 9a T10, 2026-05-24) */
/* Used by CentralityChart for dense multi-line tooltips where a light     */
/* background would compete with the chart. White text on dark background  */
/* exceeds WCAG AA 7:1. Divider separates tooltip sections.               */
--color-tooltip-dark-bg:      var(--color-text-primary);  /* reuses body-text color as background */
--color-tooltip-dark-text:    var(--color-background);    /* white text on dark bg */
--color-tooltip-dark-divider: rgba(255, 255, 255, 0.15);  /* subtle section divider */

/* UI chrome */
--color-text-primary:    #2c3e50;   /* body text */
--color-text-secondary:  #7f8c8d;   /* secondary labels at 14px+ or bold — ~3.40:1 on white; use --color-text-caption for 12px regular-weight text */
--color-text-caption:    #6c757d;   /* source attribution, footnotes at 12px — ~4.60:1 on white, WCAG AA compliant (v0.4.3) */
--color-text-muted:      #bdc3c7;   /* disabled states and non-readable placeholders only — never for readable body or caption text (~1.75:1 on white) */
--color-border:          #dde1e7;   /* dividers, input borders */
--color-background:      #ffffff;   /* page background */
--color-surface:         #f8f9fa;   /* card backgrounds, panel backgrounds */
--color-surface-hover:   #f0f2f5;   /* hover states on surfaces */

/* SVG chrome tokens (v0.20.5, T15, 2026-06-10)                               */
/* Byte-identical to the hex literals they replace; zero visual delta.         */
/* Components: TermMap, MDSPlot, Focus2FamilySimilarity, Focus1RunDistribution,*/
/*   ClusterTree, FreeListCompare, PileStructure, Focus1SelfConsistencyOverview,*/
/*   Focus2FamilyOverview                                                       */
/* Consolidation ruling: #888 and #999 stay on separate tokens (UI/UX T15).   */
/* WCAG advisory: --color-svg-axis-caption is a pre-existing fail at 11px      */
/*   regular-weight text; remediation deferred to a dedicated accessibility task.*/
--color-svg-grid-line:        #f0f0ec;   /* TermMap warm-white grid lines */
--color-svg-grid-line-neutral: #eeeeee;  /* MDSPlot/Focus2 neutral gray grid lines */
--color-svg-axis-caption:     #a0a098;   /* axis label text (pre-existing WCAG fail at 11px, deferred) */
--color-svg-label-secondary:  #4a4a4a;   /* model/term label text in MDS components */
--color-svg-marker-stroke:    #888888;   /* #888 fallback neutral stroke */
--color-svg-gray-branch:      #999999;   /* #999 cross-cluster branch color (ClusterTree) */
--color-svg-dot-stroke:       #ffffff;   /* dot stroke white (TermMap, MDSPlot, Focus2FamilySimilarity) */

/* Sequential color scale — heatmap (v0.4.9 — T6, 2026-05-15) */
/* OWID-style single-hue blue ramp. 5 discrete stops indexed by lightness:   */
/* 0 = lightest (similarity 0.00 reference), 4 = darkest (similarity 1.00).  */
/* Runtime use: SimilarityHeatmap.tsx maps similarity to a stop via discrete  */
/* bins [0,0.20), [0.20,0.40), [0.40,0.60), [0.60,0.80), [0.80,1.00].       */
/* Compositional-only for stops 0–2 (contrast on white: 1.13:1, 1.64:1,     */
/* 2.89:1 — below WCAG 3:1 standalone threshold; used only as area fills     */
/* with adjacent cell borders and inline similarity text as discriminators).  */
/* Stops 3–4 pass WCAG AA 3:1 standalone: 5.47:1 and 11.65:1.               */
/* Cross-reference: DESIGN_SYSTEM.md §12.8.                                  */
--color-scale-seq-0: #eaf0f8;   /* similarity 0.00 ref — near-white blue tint; sRGB rel. luminance 0.877 */
--color-scale-seq-1: #b8cce4;   /* similarity 0.25 ref — light blue; L≈0.590 */
--color-scale-seq-2: #6b9dc8;   /* similarity 0.50 ref — mid blue; L≈0.314 */
--color-scale-seq-3: #2e6da4;   /* similarity 0.75 ref — medium-dark blue; L≈0.142; WCAG AA 3:1 standalone PASS (5.47:1 on white) */
--color-scale-seq-4: #1a3a5c;   /* similarity 1.00 ref — deep navy; L≈0.040; WCAG AA 3:1 standalone PASS (11.65:1 on white) */

/* Semantic */
--color-success:  #27ae60;
--color-warning:  #f39c12;
--color-error:    #c0392b;
--color-info:     #3360a9;
```

**Sequential scale — usage rules.** The five `--color-scale-seq-*` tokens are the runtime fill palette for `SimilarityHeatmap.tsx`; the Coder maps each cell's similarity value to a stop via equal-width bins (see §12.8). Stops 0–2 are compositional-only: they are used only as heatmap cell fills where the adjacent cell border (`--color-border`) and the inline similarity text value together provide sufficient visual discrimination; they must not be used as standalone swatches in a legend, download artifact, or print rendering without adding a visible border. The sequential scale does not include a diverging arm; `--color-scale-div-*` tokens are deferred to T4 DriftTracker.

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

### 3.1.1 Chart-area hierarchy on the Explore page (v0.20.0, TM-A, 2026-06-10)

This subsection establishes the binding page-hierarchy rules for the Explore page. Prior gates
approved each row of the page individually; this subsection governs the composed layout.

**Background:** The live Explore page (screenshot: `/opt/lsb-agent/screenshots/currentlayout.png`,
Family domain, Focus 3, Term Map tab) shows the signature visualization compressed to approximately
the lower 55-60% of the viewport. Above the chart sit, in stack order: NavBar, FocusSelector pills,
VizTabs row, SelectionBar (SHOWING model chips), the four-line `chart-lede` paragraph, and the
TermMap controls row. Each was approved individually; the composed layout violates the §0 principle
that the chart is "the first thing a visitor sees." This subsection closes that gap.

**Preservation clause (BINDING, CDA SME M1/M2):** The layout changes specified in this subsection
do NOT relax any of the following rules. Each is re-asserted at its new position:

- **§3.3.5 R1-a invariant:** standard Register 2 ellipse at full opacity, OCI badge in tooltip.
  The Show-uncertainty toggle default remains ON.
- **§3.3.5 R1-b invariant:** no confidence ellipse rendered; dashed 2px stroke at 100% model color
  opacity; fill at 60% opacity. The R1-b tooltip copy is unchanged.
- **§3.3.5 R1-c invariant:** hollow triangle (triangle) marker, 3px solid stroke at 100% model color
  opacity, no ellipse. The R1-c tooltip copy is unchanged.
- **§3.3.5 binding invariant 1:** a reader must never see a Register 2 ellipse that implies more
  precision than the contributing model's Register 1 stability warrants.
- **§15.2 cluster-color ellipse rule:** cluster-color ellipses retain their z-order, opacity, and
  color assignments regardless of toolbar consolidation.
- **ARCHITECTURE.md §1.5 corpus-lens framing:** any label, tooltip, or aria-label string introduced
  by the consolidated toolbar must not use forbidden vocabulary (§1.5.4). M3 verbatim strings
  listed in §3.1.1(b)(ii) have been pre-grepped against §1.5.4.
- **CLAUDE.md pitfall 15:** any token referenced in this subsection has been confirmed present in
  `apps/dashboard/src/styles/tokens.css` before this subsection was authored. No phantom tokens.

#### (a) Chart-area minimum height and above-the-fold rule (BINDING)

**Desktop minimum height (binding):** The `.chart-area` flex container on the Explore page MUST
have `min-height: 70vh` at viewport widths >= 768px. This is the binding value; the 70vh figure
was selected to guarantee the signature visualization is visible in the first viewport on a standard
laptop screen (1280x800 or taller) after the NavBar (48px) and FocusSelector+VizTabs row (approx.
88px combined) are accounted for. The remaining approximately 664px at 1000px viewport height
exceeds the 70vh floor.

**Implementation note (§17.1 non-regression, CDA SME A2 addressed):** The 70vh rule applies to
the `.chart-area` parent flex container. The `.term-map-container` inner element retains
`flex:1 1 320px; min-height:0; height:100%` unchanged from §17.1. The 70vh rule MUST NOT be
applied to `.term-map-container` directly. Applying it there would re-introduce the
height-compounding ResizeObserver bug that §17.1 was authored to fix.

**Above-the-fold rule (binding):** The chart area is the largest single element above the fold on
the Explore page on desktop. No element between the NavBar and the chart area may have a rendered
height that, in combination with the other above-chart elements, pushes the top edge of the chart
below the first viewport.

**Desktop vs. mobile breakpoint (§8 consistent):** At viewport widths < 768px, the `min-height:
70vh` rule does NOT apply. Mobile layout is governed by §8; on mobile the chart area inherits
its height from the flex context (`flex:1 1 0`). The 70vh rule is desktop-only.

**CSS rule (binding, TM-B implementation target):**
```css
@media (min-width: 768px) {
  .chart-area {
    min-height: 70vh;
  }
}
```

#### (b) Control-row consolidation rules (BINDING)

Three sub-rules govern the consolidation of above-chart controls. TM-B implements all three.

**(i) SHOWING model chips removed from all VizTabs (binding).**

The `SelectionBar` component (currently rendering "SHOWING: [model chip] [model chip] ..." above
the VizTabs row) is removed from the Explore page layout for all VizTabs, not only the Term Map.
Rationale: the SHOWING chips duplicate information already available in the ModelSelector sidebar
(§3.7). The sidebar owns model selection; the chips were a redundant read-out that added vertical
height above the chart without adding information. Scope is all VizTabs; the Sidebar already
communicates the active selection via checked checkboxes.

**(ii) Unified chart toolbar for TermMap controls (binding).**

The following four controls currently rendered separately are merged into one compact chart toolbar
rendered at the top edge of the `.chart-area` when the Term Map VizTab is active:
- Overlay category names selector (currently an inline `<select>` above the chart)
- Show uncertainty toggle (currently inside `TermMap.tsx` controls row, approx. line 1140-1198)
- Show cluster labels toggle (currently same controls row)
- Magnifying lens toggle (currently same controls row)

The unified toolbar renders as a single `<div className="chart-toolbar">` row. All four controls
are visible simultaneously; no overflow, no accordion. Touch targets: minimum 44px height for each
control at < 768px (WCAG 2.5.5).

**Verbatim aria-label strings for toolbar elements (M3 pre-grepped against §1.5.4):**
- Overlay selector: `aria-label="Overlay category names"`
- Show uncertainty toggle: `aria-label="Show uncertainty ellipses"` (default: checked/ON)
- Show cluster labels toggle: `aria-label="Show cluster labels"` (default: checked/ON)
- Magnifying lens toggle: `aria-label="Magnifying lens"` (default: unchecked/OFF)

None of the above strings contain §1.5.4 forbidden vocabulary.

**(iii) Lede paragraph position (binding).**

The `chart-lede` paragraph (`<p className="chart-lede" aria-live="polite">`) moves from its
current position above the chart area to a position BESIDE the chart on desktop and BELOW the
chart on mobile.

**Desktop layout (>= 768px):** The Explore area renders as a two-column flex row. Left column:
lede paragraph in a prose column of fixed 280px width. Right column: chart area filling the
remaining width, minimum `min(calc(100% - 280px), 900px)` (`--max-chart-width` token). The lede
column scrolls independently if the prose is taller than the chart.

**Mobile layout (< 768px):** The two-column row collapses to a single column. The chart area
renders first (full width), the lede paragraph renders below it. The 280px prose column
constraint does not apply at < 768px.

**Lede preservation clause (M1 BINDING - six sub-points):**

The position change does NOT alter any of the following. All §21 rules carry forward at the new
position:

1. **Verbatim render element shape retained:** the lede renders as
   `<p className="chart-lede" aria-live="polite">{domain.generated_lede}</p>` with no structural
   change.
2. **`aria-live="polite"` retained:** the lede changes on domain switch; screen readers must
   announce the new content at the new position.
3. **`class="chart-lede"` retained:** the class name is stable so that `§21.1` token rule
   (`color: var(--color-text-caption)`) continues to apply.
4. **No inline lede logic introduced:** no component may reconstruct a lede client-side at the
   new position. The lede generator lives in `cdb_publish` (CLAUDE.md §6 rule 11). Any future lede
   change goes through a `cdb_publish` re-generation, not a component edit.
5. **Single continuous paragraph retained:** the published lede may contain two sentences (the main
   finding plus the R1-b low-output-concentration disclosure). Do NOT split them at the new
   position. Do NOT style the R1-b sentence differently.
6. **Double-hyphen separator untouched:** the published `generated_lede` contains "--" (double-
   hyphen ASCII) as a clause separator. This is approved published copy (§21.3). Render verbatim.

#### (c) Label-declutter rule for the Term Map (BINDING, TM-C implementation target)

The Term Map must apply collision-aware cluster-label placement and zoom-dependent term-label
density. This subsection is the spec-level rule; TM-C implements the bug fix against the existing
§3.3 item 5 violation visible in the screenshot (`/opt/lsb-agent/screenshots/currentlayout.png`
right-center region: Great-great-grandchildren / Great-grand-relatives collision).

**Cluster-label placement (binding):**
Cluster labels must not overlap each other or occlude term point markers. The placement algorithm
must detect collision between rendered label bounding boxes and retry with offsets before
falling back to a footnote list. Minimum separation between any two cluster labels: 16px.
Cluster labels use `var(--color-text-primary)` and `var(--font-body)` at `--font-size-sm` (14px).

**Fallback variant (D1, UI/UX TM-C election, binding):** greedy displacement with leader lines.
When a cluster label cannot be placed cleanly on the map without violating the 16px minimum
separation or occluding a term-point marker, it is moved to a non-conflicting position with a
leader line connecting it to its anchor point. Leader lines use `var(--color-text-caption)`
(#6c757d, ~4.60:1 on white, WCAG 1.4.11 PASS) at 1px stroke. If no placement satisfies bounds
and separation after all displacement candidates are exhausted, the cluster label is omitted from
the map and appended to the `<ol className="term-map-cluster-footnotes">` below the chart, with
`aria-label="Cluster labels not shown on map due to space constraints."` The footnote list
uses `var(--font-size-xs)` at `var(--color-text-caption)`.

**Term-label density (binding):**
At zoom level k = 1, term labels are shown for all terms whose salience rank is in the top 50%
for the active domain-model pair. At k >= 1.5, all term labels are shown. The density step is
linear between k=1 and k=1.5. This rule applies per-model; a term visible for one model may be
suppressed for another at the same zoom level if its relative salience rank is below threshold.
Salience source: published Sutrop CSI field (`domain.sutrop_csi` in the domain JSON) -- not
recomputed client-side (CDA SME N2 binding).

**CDA SME N1 caption (binding):** At k <= 1.5, the following caption renders below the chart
(or below the footnote list if present):
"Labels shown for top-salience terms at this zoom level. Zoom in or hover with the magnifying
lens to see all terms."
The literal substring 'top-salience' must appear in the AC4 render path. The caption does not
render at k > 1.5. CSS: `var(--font-size-xs)`, `var(--color-text-caption)`.

**Interaction with §3.3 item 5 (binding):**
§3.3 item 5 ("Model labels - positioned to minimize overlap") applies to model-level labels.
This §3.1.1(c) rule applies to cluster-level labels and term-level labels. The two rules compose
without conflict.

Gate verdicts: CDA SME PASS-WITH-NOTES; UI/UX PASS-WITH-NOTES
(`docs/status/2026-06-10-termmap-layout-verdicts.md`, TM-C section).

#### (d) Footnote band visual design -- .term-map-cluster-footnotes (BINDING, TM-D, 2026-06-11)

The `.term-map-cluster-footnotes` band is a designed component with a load-bearing constant-height
contract. It renders below the Term Map chart area when `showClusterLabels` is true, displaying
the fallback list of cluster labels that could not be placed on the map (the D1 election from
§3.1.1(c)). Its constant height is the geometric break in the render-feedback oscillation
documented in the 2026-06-10 post-deploy hotfix trail (commits 1ac0b7b, aed6206, aaaba0b). Any
design that allows item count, hover state, label length, empty state, or scroll position to change
the band's rendered height re-introduces the footnote-to-chart feedback loop and is REJECTED.

**Stylesheet file (binding):** `app.css` (placement: with all other `.term-map-*` class
definitions, after `.term-map-stress` block).

**CSS classes (binding):**
- `.term-map-cluster-footnotes` -- the `<ol>` element
- `.term-map-cluster-footnotes__empty` -- modifier on the placeholder `<li>` (empty-state)

**Constant-height contract (BINDING -- do not parameterize on content):**

The band height is a compile-time CONSTANT: `height: 48px`. This value is the shipped constant
from the 2026-06-10 hotfix trail and is confirmed stable. Item count is not a CSS input. The
following are PROHIBITED on `.term-map-cluster-footnotes`: `vh`, `%`, `calc()` involving children,
`auto`, `min-content`, `max-content`, `fit-content` for the `height` property; any `:hover` rule
that changes `height`, `min-height`, `max-height`, `padding`, `border`, or `margin` on the `<ol>`;
any `transition` targeting any geometric property on the `<ol>`. Any design that parameterizes
height on content re-introduces the oscillation failure mode.

**Full CSS spec for `.term-map-cluster-footnotes` (binding):**
```css
.term-map-cluster-footnotes {
  height: 48px;
  overflow-y: auto;
  flex: none;
  border-top: 1px solid var(--color-border);
  margin-top: var(--space-1);
  padding: var(--space-1) 0;
  padding-left: var(--space-6);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-regular);
  line-height: var(--line-height-data);
  color: var(--color-text-caption);
}
```

**Full CSS spec for `.term-map-cluster-footnotes__empty` (binding):**
```css
.term-map-cluster-footnotes__empty {
  list-style: none;
  margin-left: calc(-1 * var(--space-6));
  padding-left: 0;
  font-style: italic;
}
```

**Inline style removal (binding):** The `style={{ height: '48px', overflowY: 'auto', flex: 'none',
... }}` object on the `<ol>` in TermMap.tsx and the `style={{ listStyle: 'none', marginLeft:
'-20px' }}` on the placeholder `<li>` are removed in their entirety. All styling moves to the CSS
classes above.

**Empty-state presentation (binding, CDA SME routing-only PASS):** The placeholder `<li>` text is
preserved byte-identically: 'All cluster labels are shown on the map.' The `<li>` receives
`className='term-map-cluster-footnotes__empty'`.

**aria-label (binding, byte-identical):** `aria-label='Cluster labels not shown on map due to
space constraints.'`

**Typography (binding):** `var(--font-size-xs)` (12px), `var(--font-weight-regular)` (400),
`var(--line-height-data)` (1.4).

**Color (binding, WCAG AA):** `var(--color-text-caption)` (#6c757d, 4.60:1 on white at 12px
regular weight, WCAG AA PASS). Top border: `var(--color-border)`. Background:
`var(--color-background)` (inherited).

**Separator (binding):** top border `1px solid var(--color-border)` on the `<ol>` (constant, not
`:hover` conditional).

**Scroll affordance:** native `overflow-y: auto`. No custom scrollbar styling.

**Mutation watch (AC14 binding):** no animation, transition, or hover effect on this component may
mutate the band's outer box. Internal scroll position changes are fine. Any `:hover` or `:focus`
rule MUST target only `<li>` inner content (color/opacity), never geometric properties of the
`<ol>`.

**Token pre-check (pitfall 15, confirmed):** All `var(--...)` references above are confirmed
present in `apps/dashboard/src/styles/tokens.css`: `--font-size-xs` (line 57),
`--font-weight-regular` (line 65), `--line-height-data` (line 71), `--color-text-caption`
(line 156), `--color-border` (line 158), `--color-background` (line 159), `--space-1` (line 187),
`--space-6` (line 191). No new tokens introduced.

**Loop-breaking history reference:** see `docs/status/2026-06-10-termmap-layout-verdicts.md`
post-deploy hotfix trail for the originating oscillation incident. The ResizeObserver equality
guard (TermMap.tsx lines 810-823), the 8px quantization (lines 432-439), and the
`setHiddenClusterLabels` equality guard (lines 798-802) are independent loop-breakers that MUST
NOT be removed or weakened.

Gate verdicts: CDA SME PASS-WITH-NOTES (routing-only); UI/UX PASS-WITH-NOTES
(`docs/status/2026-06-10-termmap-layout-verdicts.md`, TM-D section).

---

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
| **R1-b: Low concentration** | `deterministic_output == False` AND `oci < 3.0` | **No confidence ellipse rendered.** The point is rendered with a dashed 2px stroke (not solid) and reduced 60% opacity on the fill. Tooltip surfaces: *"Position uncertain. This model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."* Legend entry under the point has a small italic "low OCI" tag. The final OCI threshold for this state is provisional at 3.0 pending the Phase 4b saturation analysis; see `docs/SME_REVIEW.md` open question 1. |
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
   > *"Deterministic output. This model produced the same categorical structure on every run. Its position on the map is consistent, but there is no uncertainty range to show. See the methodology page for why this is the least informative case, not the most."*

   The schema identifiers `OCI sentinel` and `ConsensusType = DETERMINISTIC` must not appear in the primary hover tooltip. They appear in the open data bundle data dictionary and the methodology page only.

6. **Edge case — all-visible models are R1-c (binding copy).** When every model visible on the Register 2 map is in state R1-c, the key finding strip renders the following copy in place of the standard lede:
   > *"All selected models produced deterministic output on this domain. The same categorical structure appeared on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*

   This is not an error state. The lede generator receives this as a named case with its own template; it does not fall through to a generic "something went wrong" handler.

7. **Config constant location (binding).** The OCI low-concentration threshold is defined once, at `apps/dashboard/src/config/analysis.ts` as `export const OCI_LOW_CONCENTRATION_THRESHOLD = 3.0;`. This is the source of truth for all R1-b threshold comparisons in component code. The methodology page displays the current threshold value injected at build time from the published JSON manifest (which must carry this constant alongside the analysis version). **No component may reference `3.0` as a numeric literal; all must import from this config module.**

8. **§7 shape encoding vs R1-c shape encoding — clarification.** DESIGN_SYSTEM.md §7 states "model origin is encoded in both color and point shape." This refers to the baseline marker shapes (★ for published baselines, ◆ for researcher baselines) distinguishable by shape and color for accessibility. It does **not** require that model points themselves use distinct shapes per origin — §3.3 item 6 governs model point rendering (filled circles for all models in R1-a and R1-b states). R1-c introduces a third shape encoding axis (state, not origin). The Coder must not interpret §7 as requiring origin-specific point shapes for regular model markers.

9. **R1-b stroke-dasharray value: "4 2" (binding, T-MDS-R1).** The dashed stroke for R1-b markers uses `stroke-dasharray="4 2"` (4px dash, 2px gap). This value is pinned here because the §3.3.5 table and prior implementation requirements described a dashed stroke without specifying the dash/gap ratio. The "4 2" value is consistent with the existing dashed-ring usage in TermMap.tsx (`'4 2'`) and provides sufficient ink density for a 6px-radius circle boundary. No other stroke-dasharray value is acceptable for R1-b without a new UI/UX gate verdict. The Coder must use `stroke-dasharray="4 2"` verbatim in the SVG string template. Test assertion: the R1-b test in MDSPlot.test.tsx must assert `strokeDasharray === "4 2"` or `getAttribute("stroke-dasharray") === "4 2"`.

10. **R1-c triangle polygon geometry: circumradius 8px, apex-up (binding, T-MDS-R1).** The hollow triangle for R1-c markers is an equilateral triangle centered at `(cx, cy)` with circumradius 8px and apex pointing up. The three polygon vertices in SVG coordinate space (y increases downward) are: top `(cx, cy-8)`, bottom-left `(cx-6.93, cy+4)`, bottom-right `(cx+6.93, cy+4)`. The Coder MUST use a `<polygon>` element (not a `<path>`) with `points="{cx},{cy-8} {cx-6.93},{cy+4} {cx+6.93},{cy+4}"` where cx and cy are the same scale-projected coordinates used for R1-a and R1-b circles at the same model_id. The triangle is centered identically to the R1-a/R1-b circle: the centroid of the triangle polygon coincides with the data point. Rationale for circumradius 8px: at 10px logical size (diameter 20px), an equilateral triangle with circumradius 8px has a total bounding height of 12px and width of 13.86px, providing optical weight broadly equivalent to the 6px-radius R1-a circle (area ~113 sq px vs triangle area ~83 sq px, partially compensated by the more visually prominent 3px solid stroke). The 6.93 value is floor(8 * sin(60deg) * 100) / 100 = floor(6.9282 * 100) / 100 = 6.92; use 6.93 for correct rounding. The Coder must not use a different circumradius or a path-based implementation without a new UI/UX gate verdict.

11. **ociValues prop required for R1-b tooltip OCI display (binding, T-MDS-R1).** The CDA SME F3 binding specifies that the R1-b tooltip must display the actual OCI value inline: "OCI = X.X". This value is not available through the r1States prop (which carries only the state classification, not the raw numeric). A second new prop is required on MDSPlot.tsx: `ociValues: Record<string, number>`, carrying the per-model OCI score as a display value. This prop is display-only: the component MUST NOT use ociValues to compute or reclassify the R1 state (A5 prohibition). ContentArea.tsx must wire this prop by extracting OCI values from `domain.within_model_results` (the `WithinModelResult[]` array already present in DomainResultPublished at the `within_model_results` field) and constructing the record: `Object.fromEntries(domain.within_model_results.map(r => [r.model_id, r.oci]))`. The defensive fallback in ContentArea is `ociValues={ociValues ?? {}}` where `ociValues` is computed from `domain.within_model_results`. When a model_id is absent from ociValues (legacy JSON edge case), the tooltip omits the OCI value clause rather than rendering "OCI = NaN" or "OCI = undefined". The acceptance criterion A1 in the Architect plan must be understood as amended: MDSPlot.tsx gains TWO new required props: `r1States: Record<string, R1State>` and `ociValues: Record<string, number>`. The R1-b tooltip template is: "Position uncertain. This model's within-model output concentration is low (OCI = {ociValues[m.model_id]?.toFixed(1) ?? 'n/a'}; higher means runs converge on one structure). See model profile for within-model distribution." The Coder must use `.toFixed(1)` for consistent one-decimal display matching the §3.3.5 table example "OCI = X.X".

12. **R1-a degenerate-bootstrap sub-state: minimum-radius ellipse floor (binding, F5-T1).** When a model's (or term's) bootstrap ellipse has `semi_major <= 0` and the R1 state is `typical_concentration` (or not set, i.e., TermMap and Focus2FamilySimilarity which do not carry R1 state), this is the LIMIT case of a high-stability R1-a sample where the bootstrap CONVERGED on a near-point. Per CDA SME T-MDS-R1 F2: re-classifying this as R1-b would be a category error. This is an R1-a SUB-STATE, not a fourth R1 state. The visual treatment is a minimum-radius ellipse floor: render the ellipse at rx=3, ry=3 (pixels, before any scale transform) using the same fill, stroke, and opacity as the standard R1-a ellipse. The degenerate ellipse carries `data-degenerate-bootstrap="true"`. The dot marker for MDSPlot additionally carries `data-r1-state="typical_concentration"` and `data-degenerate-bootstrap="true"` plus the S2 aria-label. In TermMap, disclosure threads through the `.term-dot` circle aria-label (NOT `.term-ellipse`, which has `pointer-events="none"`). In Focus2FamilySimilarity, disclosure threads through the family-member inner circle aria-label. Disclosure strings (byte-identical to CDA SME F5-T1 bound strings): S2 MDSPlot dot: `"{displayName}, high positional stability. Bootstrap resamples converged on a near-point; confidence region is too small to display."`; S3 TermMap term-dot: `"{term}, high positional stability across bootstrap resamples."`; S4 Focus2FamilySimilarity family-member circle: `"{displayName}, high positional stability across bootstrap resamples."`. MDSPlot tooltip body S1 (UI/UX-corrected per this impl req, removing schema identifier "R1-a sample"): `"Position highly stable. Bootstrap resamples converged on a near-point, so the confidence region is too small to show as an ellipse. This is the limit case of a high-stability sample, not missing uncertainty."` The S1 correction rule: tooltip and aria-label copy MUST NOT use internal schema identifiers like "R1-a sample"; plain-language phrasing ("high-stability sample") is required. Bare-point fall-through is structurally impossible: the `if (!u) return;` guard returns early only when u is null/undefined; when u is present but semi_major <= 0, the degenerate treatment renders. R10 invariant is preserved: a visible artifact (minimum-radius ellipse) is always present for any model/term with u != null. Test assertion: vitest suites in MDSPlot.test.tsx (F5 describe block), TermMap.test.tsx (F5 A5a-c), and Focus2FamilySimilarity.test.tsx (F5 A5a-d) enforce these invariants mechanically. Gate verdicts: CDA SME PASS-WITH-NOTES (S1-S4 bound strings per `.claude/agent-memory/cda_sme/project_f5_degenerate_ellipse_verdict.md`); UI/UX PASS-WITH-NOTES (minimum-radius option (a) selected over distinct marker option (b); S1 jargon correction binding); Reviewer/Tester verdicts: docs/status/2026-06-10-codebase-review-fixes-verdicts.md F5 section.

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

### 6.3 Provenance pointer section (M1, 2026-06-10)

The methodology page closes with a single-sentence "Provenance" section that links readers to the Data page for detailed technical provenance. This section replaced the previously embedded `Data provenance` and `Cross-model term map and uncertainty` sections, which moved to `DataPage.tsx` (see §15.5(a) and §16.2).

**Section structure:**
- Container: `.methodology-page__section` with `aria-labelledby="provenance-pointer-heading"`
- Heading: `<h2 id="provenance-pointer-heading">Provenance</h2>` (sentence case)
- Paragraph: single sentence linking to `/data` (root-relative in-app SPA route)
- Link: `<a href="/data" className="methodology-page__link">Data page</a>`
- **No `target="_blank"` on this link** — it is an in-app SPA route, not an external resource. The UI/UX §20.6 external-link contract applies only to `href^="http"` links.

The pointer section follows section 8 ("Do not take my word for it"), which is Mark's deliberate closing rhetorical beat. The provenance pointer is mechanical wayfinding and must not interrupt the closing section. See §11 Component Inventory entry for `MethodologyPage.tsx`.

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

### 8.0 General mobile layout

- **Control panel collapses** to a bottom drawer on screens narrower than 768px
- **Domain selector** wraps to two lines on mobile, does not scroll horizontally
- **MDS plot** renders at full width with pinch-to-zoom enabled
- **Free list compare** shows maximum 2 columns on mobile (others accessible via horizontal scroll)
- **Sliders** use large touch targets (minimum 44px height)
- **Download buttons** are full-width on mobile

### 8.1 Mobile hamburger menu (v0.4.7 — T11, 2026-05-15)

**Breakpoint:** `max-width: 768px`. The hamburger trigger is `display: none` at `≥768px`; the desktop nav (`.site-header__nav`) is `display: none` at `<768px` (existing rule, `app.css` line 1029). Breakpoint value must be byte-identical on both rules to prevent dead-zone rendering.

---

#### 8.1.1 ARIA pattern — dialog with focus trap

The mobile nav panel uses the **dialog pattern**: `role="dialog"`, `aria-modal="true"`, `aria-label={MOBILE_NAV_PANEL_LABEL}` (no visible heading; see §8.1.10). The trigger button carries `aria-expanded={boolean}` (reflecting panel open/close state), `aria-controls="mobile-nav-panel"`, and `aria-haspopup="dialog"`.

**Rationale:** the full-screen overlay visually occludes the entire page, making modal semantics correct. The existing `CiteModal`/`EmbedModal` focus-trap helper (`getFocusableElements`, `CiteModal.tsx` lines 76–89) is the canonical reuse pattern.

**Focus behavior:**

| Event | Required behavior |
|---|---|
| Panel opens | Initial focus moves to the close button inside the panel (the first and immediately obvious interactive element). |
| Tab | Cycles forward through focusable elements inside the panel only. Does not escape to page content while panel is open. |
| Shift+Tab | Cycles backward within the panel only. |
| Esc | Closes the panel; focus returns to the hamburger trigger button. |
| Backdrop / outside-tap | N/A — no scrim; panel is full-bleed. See §8.1.5. |
| Close button activated | Closes the panel; focus returns to the hamburger trigger button. |
| Panel closes (any path) | Focus restored to the hamburger trigger element via `triggerRef.current?.focus()`. |

**Focus trap implementation:** reuse the `getFocusableElements` / `keydown` handler pattern from `CiteModal.tsx` lines 220–264. The panel has exactly two categories of focusable elements: the close button and the four nav link anchors. Tab wraps from last link back to close button; Shift+Tab from close button wraps to last link.

**WCAG 2.1.2 compliance:** Esc and the close button are both always-available escape paths. The focus trap does not prevent Esc from closing.

---

#### 8.1.2 Hamburger glyph shape — three horizontal lines (inline SVG)

The glyph is three horizontal lines, rendered as an inline SVG following the `LogoGlyph` pattern (no external icon dependency).

**Binding SVG specification:**

```tsx
<svg
  viewBox="0 0 20 16"
  width="20"
  height="16"
  aria-hidden="true"
  focusable="false"
  xmlns="http://www.w3.org/2000/svg"
>
  <line x1="0" y1="2"  x2="20" y2="2"  stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  <line x1="0" y1="8"  x2="20" y2="8"  stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  <line x1="0" y1="14" x2="20" y2="14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
</svg>
```

- **Viewbox:** 20×16 px (width × height of the three-line field)
- **Stroke weight:** 2px
- **Line gap:** 6px (center-to-center; lines at y=2, y=8, y=14)
- **Color:** `currentColor` — inherits from the button's `color: var(--color-text-primary)` so it automatically meets WCAG 1.4.11 3:1 non-text contrast against `--color-background` (#ffffff). `--color-text-primary` (#2c3e50) on white ≈ 12.6:1.
- **`aria-hidden="true"` and `focusable="false"`** — the button's accessible name is provided by `aria-label` on the `<button>` element; the SVG is decorative.

---

#### 8.1.3 Glyph-to-X transformation — none

The hamburger glyph does NOT transform to an X on open. The trigger button remains in its rest-state appearance when the panel opens. The close affordance is a dedicated close button **inside the panel** (§8.1.9). The `aria-label` on the trigger button changes dynamically (`MOBILE_NAV_TRIGGER_LABEL_CLOSED` / `MOBILE_NAV_TRIGGER_LABEL_OPEN`) to communicate state to screen readers.

**Rationale:** a glyph-to-X CSS transform requires additional animation CSS that violates the Phase 6 minimum-viable surface posture. A dedicated close button inside the panel provides a larger, clearer close target on touch surfaces and is the simpler implementation path.

---

#### 8.1.4 Panel direction and shape — full-screen overlay from top

The panel renders as a **full-screen overlay** that covers the entire viewport from the top edge downward. It is positioned `fixed`, `top: 0; left: 0; right: 0; bottom: 0`. It is not a side drawer.

**Rationale:** full-screen is the simplest z-index story (one stacking context, no slide-in animation required), matches the "scientific instrument" aesthetic (avoids the consumer-product side-drawer idiom), and is fully compatible with the site-header's `position: sticky; z-index: 100` stacking context since the panel uses `position: fixed` and sits above all page content.

The panel sits on top of the sticky header itself (panel `z-index: 200`, above header `z-index: 100`). The panel background covers the header.

---

#### 8.1.5 Transition and backdrop scrim — instant open/close, no scrim

**Transition:** none. The panel appears and disappears instantly on trigger activation and close-button activation. CSS: no `transition` or `animation` properties on `.mobile-nav__panel`. This trivially satisfies `prefers-reduced-motion: reduce` — there is nothing to suppress.

**Backdrop scrim:** none. The panel is full-bleed (`background: var(--color-background)`, full viewport), so a separate scrim layer would be invisible beneath it. No `rgba(0,0,0,*)` overlay element.

**`prefers-reduced-motion` CSS block (still required as a belt-and-suspenders declaration, for forward safety if a transition is ever added):**

```css
@media (prefers-reduced-motion: reduce) {
  .mobile-nav__panel {
    transition: none;
    animation: none;
  }
}
```

This block must appear in `mobile-nav.css` regardless of whether a transition is currently specified. It ensures any future addition of a transition is automatically gated.

---

#### 8.1.6 Trigger button styling

The hamburger trigger button uses token-only styling. No new tokens are introduced.

```css
.site-header__hamburger {
  display: none;                          /* hidden on desktop */
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
  background: transparent;
  border: 2px solid transparent;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  color: var(--color-text-primary);
  flex-shrink: 0;
}

.site-header__hamburger:hover {
  background: var(--color-surface-hover);
  border-color: transparent;
}

.site-header__hamburger:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}

.site-header__hamburger:active {
  background: var(--color-surface);
}

@media (max-width: 768px) {
  .site-header__hamburger {
    display: flex;
  }
}
```

**Contrast verification:** `--color-text-primary` (#2c3e50) on `--color-background` (#ffffff) ≈ 12.6:1 for the glyph (WCAG 1.4.11 3:1 PASS). `--color-surface-hover` (#f0f2f5) on white for the hover background is a non-text surface (no contrast requirement on hover backgrounds per WCAG). The `--color-info` focus ring (#3360a9) on white ≈ 7.3:1 (WCAG 1.4.11 PASS).

---

#### 8.1.7 Open-panel link styling

Links inside the open panel are styled for touch-first readability.

```css
.mobile-nav__panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 200;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
  padding: var(--space-4) var(--space-6);
  overflow-y: auto;
}

.mobile-nav__close {
  align-self: flex-end;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
  background: transparent;
  border: 2px solid transparent;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  line-height: 1;
  flex-shrink: 0;
}

.mobile-nav__close:hover {
  background: var(--color-surface-hover);
}

.mobile-nav__close:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}

.mobile-nav__links {
  display: flex;
  flex-direction: column;
  margin-top: var(--space-6);
  gap: 0;
}

.mobile-nav__link {
  display: flex;
  align-items: center;
  min-height: 48px;
  padding: 0 var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);
  color: var(--color-text-primary);
  text-decoration: none;
  border-bottom: var(--border-width) solid var(--color-border);
}

.mobile-nav__link:first-child {
  border-top: var(--border-width) solid var(--color-border);
}

.mobile-nav__link:hover {
  color: var(--color-info);
  background: var(--color-surface-hover);
}

.mobile-nav__link:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: -2px;
  border-radius: var(--border-radius-sm);
}
```

**Typography tokens used:** `--font-size-lg` (18px), `--font-weight-medium` (500), `--line-height-tight` (1.3), `--color-text-primary` (#2c3e50).

**Contrast:** `--color-text-primary` (#2c3e50) on `--color-background` (#ffffff) ≈ 12.6:1 (WCAG 1.4.3 4.5:1 PASS). `--color-info` (#3360a9) on white ≈ 7.3:1 (hover color — WCAG AA PASS).

---

#### 8.1.8 Touch target size — 48×48 px

- **Hamburger trigger button:** 48×48 px (explicit `width` and `height` on `.site-header__hamburger`). Above the 44×44 px WCAG 2.5.5 floor.
- **Close button inside panel:** 48×48 px (explicit `width` and `height` on `.mobile-nav__close`). Above the floor.
- **Each nav link in the open panel:** `min-height: 48px` on `.mobile-nav__link`. Full-width tap target. Above the floor.

---

#### 8.1.9 Trigger position when panel is open — hidden

When the panel is open, the hamburger trigger button is hidden (`display: none` applied via React state). The close affordance is the `.mobile-nav__close` button at the top-right corner of the open panel. This is the only close affordance visible when the panel is open (in addition to Esc).

**Implementation note:** the `aria-label` on the trigger still toggles between `MOBILE_NAV_TRIGGER_LABEL_CLOSED` and `MOBILE_NAV_TRIGGER_LABEL_OPEN` via React state for correctness, even though the trigger is hidden when open. The close button inside the panel does not need an `aria-expanded` attribute; it is a plain close button with `aria-label={MOBILE_NAV_TRIGGER_LABEL_OPEN}` (i.e., "Close navigation menu").

**Close button glyph:** the close button renders the "×" character as a React text node (`×`, Unicode U+00D7). No external icon dependency. `aria-hidden="true"` on the character span if used; the button's accessible name comes from its `aria-label`.

---

#### 8.1.10 Visible heading inside panel — omitted

The open panel does NOT include a visible `<h2>` heading. The panel's accessible name is provided solely by `aria-label={MOBILE_NAV_PANEL_LABEL}` ("Site navigation") on the `role="dialog"` element. This avoids adding visible heading-level chrome that could confuse the page's existing heading hierarchy (which belongs to the article content, not the navigation overlay).

**No `MOBILE_NAV_HEADING` constant is introduced.** The `mobile_nav.ts` copy module exports exactly three strings (§8.1.11).

---

#### 8.1.11 Confirmed accessibility strings

All three strings are confirmed verbatim. No additional visible or SR-only prose is introduced beyond these. CDA SME bypass applies (Architect §2.6 rationale confirmed).

| Export name | Value | Usage |
|---|---|---|
| `MOBILE_NAV_TRIGGER_LABEL_CLOSED` | `"Open navigation menu"` | `aria-label` on trigger when `isOpen === false` |
| `MOBILE_NAV_TRIGGER_LABEL_OPEN` | `"Close navigation menu"` | `aria-label` on trigger when `isOpen === true`; also `aria-label` on the close button inside panel |
| `MOBILE_NAV_PANEL_LABEL` | `"Site navigation"` | `aria-label` on `role="dialog"` panel |

---

#### 8.1.12 Reduced-motion handling

See §8.1.5. The panel has no transition by default. The `prefers-reduced-motion: reduce` CSS block in `mobile-nav.css` is required regardless as a forward-safety guard.

---

#### 8.1.13 Scroll lock — none

No scroll lock is applied when the panel is open. `document.body.style.overflow` is not modified. This matches the existing `CiteModal`/`EmbedModal` posture and keeps T11's surface minimal. Users can scroll the underlying page while the panel is open; given the full-screen panel covers all content, this is an acceptable Phase 6 posture.

---

#### 8.1.14 DOM mount — inline inside Header.tsx

The `MobileNav` panel mounts **inline inside `Header.tsx`**, not as a portal to `document.body`. The panel uses `position: fixed` with `z-index: 200` (above the header's `z-index: 100`), so it overlays the full page correctly from within the header's containing block. Portal complexity is not required.

**Rationale for diverging from Architect lean (portal):** the panel's `position: fixed` already escapes the normal document flow and the header's stacking context. The added complexity of `createPortal` is not justified for a full-viewport fixed-position element. This also keeps the component tree simpler (no portal target management) and matches the minimum-viable-surface posture.

**`z-index` values (binding):**
- Site header: `z-index: 100` (existing, `app.css` line 143)
- Mobile nav panel: `z-index: 200` (new, in `mobile-nav.css`)

---

#### 8.1.15 NAV_LINKS export requirement

Acceptance criterion 15 in the Architect plan requires the Coder to use `NAV_LINKS` as a single source of truth — no duplication in `MobileNav.tsx`. Currently `NAV_LINKS` is a module-private `const` in `Header.tsx` (line 46). **The Coder must export `NAV_LINKS` from `Header.tsx`** (add `export` keyword) so `MobileNav.tsx` can import it, OR pass it as a prop from `Header` to `MobileNav`. Either approach satisfies the single-source requirement. The `NavLink` interface must also be exported. This is a binding implementation requirement arising from the design system's single-source-of-truth rule.

---

#### 8.1.16 Component structure summary

```
Header.tsx
  <header className="site-header">
    <div className="site-header__inner">
      <a> (logo — unchanged)
      <nav className="site-header__nav"> (desktop nav — unchanged, hidden <768px)
      <button className="site-header__hamburger"
              aria-label={isOpen ? MOBILE_NAV_TRIGGER_LABEL_OPEN : MOBILE_NAV_TRIGGER_LABEL_CLOSED}
              aria-expanded={isOpen}
              aria-controls="mobile-nav-panel"
              aria-haspopup="dialog"
              style={{ display: isOpen ? 'none' : undefined }}  /* hidden when panel open */
              onClick={openPanel}
      >
        <HamburgerGlyph />   /* inline SVG per §8.1.2 */
      </button>
    </div>

    {isOpen && (
      <MobileNav
        id="mobile-nav-panel"
        links={NAV_LINKS}
        onClose={closePanel}
        triggerRef={triggerRef}
      />
    )}
  </header>

MobileNav.tsx
  <div role="dialog"
       aria-modal="true"
       aria-label={MOBILE_NAV_PANEL_LABEL}
       id={id}
       className="mobile-nav__panel"
  >
    <button className="mobile-nav__close"
            aria-label={MOBILE_NAV_TRIGGER_LABEL_OPEN}
            onClick={onClose}
    >
      <span aria-hidden="true">×</span>
    </button>
    <nav className="mobile-nav__links" aria-label={MOBILE_NAV_PANEL_LABEL}>
      {links.map(link => (
        <a key={link.href} href={link.href} className="mobile-nav__link">
          {link.label}
        </a>
      ))}
    </nav>
  </div>
```

Note: `role="dialog"` overrides any native element semantics. The inner `<nav>` provides the navigation landmark for AT users who navigate by landmark; the outer `dialog` provides modal semantics. This structure matches the Architect's §10 risk note 6 guidance: `<div role="dialog"><nav>…</nav></div>`.

---

### 8.2 Mobile bottom-drawer for ModelSelector (v0.4.8 — T12, 2026-05-15)

**Breakpoint:** `max-width: 768px`. The drawer trigger is visible and the inline `ModelSelector` is hidden at `<768px`. At `≥768px`, the inline `ModelSelector` is visible and the drawer trigger is hidden. The breakpoint value must be byte-identical on both rules to prevent dead-zone rendering. This supersedes the T13 stacked-below rule at `app.css:681–692` — see §8.2.10.

---

#### 8.2.1 ARIA pattern — dialog with focus trap

The drawer panel uses the **dialog pattern**: `role="dialog"`, `aria-modal="true"`, `aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}` (no visible heading; see §8.2.10). The trigger button carries `aria-expanded={boolean}` (reflecting drawer open/close state), `aria-controls="mobile-model-drawer-panel"`, `aria-haspopup="dialog"`.

**Rationale:** the drawer overlays the page content below it and uses a semi-opaque backdrop scrim, making modal semantics correct. The `getFocusableElements` helper from `MobileNav.tsx` (or extracted to a shared module) is the reuse pattern. The Architect plan §2.4 lean (close button as initial focus, dialog pattern) is confirmed.

**Focus behavior:**

| Event | Required behavior |
|---|---|
| Drawer opens | Initial focus moves to the close button inside the drawer. |
| Tab | Cycles forward through focusable elements inside the drawer only. Does not escape to page content while drawer is open. |
| Shift+Tab | Cycles backward within the drawer only. |
| Esc | Closes the drawer; focus returns to the drawer trigger button. |
| Scrim / outside-tap | Closes the drawer; focus returns to the drawer trigger button. |
| Close button activated | Closes the drawer; focus returns to the drawer trigger button. |
| Drawer closes (any path) | Focus restored to the drawer trigger via parent's `useEffect` (`prevDrawerOpen` ref posture per Architect plan §2.3 sketch). |

**Focus trap implementation:** reuse `getFocusableElements` from `MobileNav.tsx` (or extract to `apps/dashboard/src/lib/focus-trap.ts` per plan §5's optional extraction, which is the preferred path if the Coder takes it). The drawer's focusable set is: close button (1) + all enabled checkbox rows (up to 11) + "Select all" button (1) + "Clear all" button (1) = up to 14 focusable elements. Tab from the last element ("Clear all") wraps to the close button; Shift+Tab from the close button wraps to "Clear all".

**WCAG 2.1.2 compliance:** Esc and the close button are both always-available escape paths. The scrim tap is an additional dismissal path. The focus trap does not prevent Esc from closing.

---

#### 8.2.2 Drawer direction and shape — half-sheet from bottom

The drawer panel renders as a **bottom-anchored half-sheet**: `position: fixed; bottom: 0; left: 0; right: 0; max-height: 75vh`. It rises from the bottom edge upward. It is not full-screen (contrast with §8.1.4 which is full-screen from top). It is not a side drawer.

**Rationale:** the ModelSelector list can contain up to 11 model rows plus origin-group dividers, max-6 warning, "Select all", and "Clear all" — this content can exceed a short mobile viewport but does not need full-screen to be usable. A 75vh cap gives the list room to scroll internally on tall phones and does not completely bury the page context on short phones (a narrow strip of scrimmed page content remains visible above the drawer, reinforcing the modal-overlay relationship). Full-screen was considered but rejected: for a single control panel, full-screen increases perceived cognitive overhead for what is a brief interaction (select a few models, close). Half-sheet is lighter and matches the "scientific instrument" posture better than a full-coverage take-over for a filter panel.

**No snap points.** The drawer is a static `max-height: 75vh` — not draggable, not resizable, no peek state. Snap points require touch event listeners and either new dependencies or substantial custom code; both are out of scope for Phase 6 per the plan §5 out-of-scope list.

**No drag handle.** A drag handle implies draggable snap behavior. Not present.

**Internal scroll:** the drawer content area (`mobile-model-drawer__body`) is `overflow-y: auto` so the model list scrolls inside the drawer without pushing content out the top or spilling to the page.

**Panel width:** full viewport width (`left: 0; right: 0`). No horizontal margin at `<768px`.

**Top border-radius:** `border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0` (12px on top-left and top-right corners only; square at bottom since the drawer is flush to the viewport bottom edge).

---

#### 8.2.3 Backdrop scrim — semi-opaque overlay above the page

A semi-opaque backdrop scrim is placed between the page content and the drawer panel. The scrim element is `aria-hidden="true"` (it is a presentational overlay, not an interactive control for AT users — the Esc key and the close button serve keyboard and screen-reader users; the scrim serves sighted touch users).

**Scrim specification:**

```css
.mobile-model-drawer__scrim {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 199;                          /* one below the drawer panel at z-index 200 */
  background: rgba(0, 0, 0, 0.45);
}
```

**Scrim interaction:** a `pointerdown` event on the scrim (outside the drawer panel) calls `onClose`. This provides touch-dismissal without an `onClick` on the `document` body. The scrim element sits below the drawer in z-order (z-index: 199 vs. z-index: 200 on the panel), so clicks/taps that land on the visible drawer panel do not reach the scrim.

**Rationale for `rgba(0,0,0,0.45)`:** this opacity is sufficient to visually recede the page content and signal the modal state without making it fully invisible. The scrim itself carries no WCAG contrast requirement (it is `aria-hidden`, non-interactive). The 45% opacity is the minimum that reads clearly as a page overlay on both light and dark ambient page content.

**Contrast of text above scrim:** the scrim does not cover the drawer panel; it covers only the page content behind the drawer. Text inside the drawer panel sits on `--color-background` (#ffffff) and is unaffected by the scrim.

---

#### 8.2.4 Transition — 200ms slide-up, gated by prefers-reduced-motion

The drawer panel slides up from the bottom edge of the viewport on open, and is dismissed instantly (no slide-down animation) on close. This asymmetric animation (animate in, instant out) follows a common mobile-sheet pattern and avoids the user waiting for a close animation before regaining page access.

**Open transition:**

```css
.mobile-model-drawer__panel {
  transform: translateY(100%);
}

.mobile-model-drawer__panel--open {
  transform: translateY(0);
  transition: transform 200ms ease-out;
}
```

**Implementation note for Coder:** the slide-up is triggered by adding the `--open` modifier class immediately after mount (one `requestAnimationFrame` delay to allow the browser to paint the initial `translateY(100%)` state before transitioning). OR — simpler and equally correct — the component conditionally mounts only when `mobileSelectorOpen === true` (per the Architect plan §2.3 sketch), so the `--open` class can be applied at mount via a `useEffect` with a 0ms timeout or via a CSS animation keyframe.

**Scrim:** the scrim appears instantly at mount (no fade-in). Phase 6 minimum-viable posture.

**`prefers-reduced-motion: reduce` handling (mandatory CSS block, belt-and-suspenders):**

```css
@media (prefers-reduced-motion: reduce) {
  .mobile-model-drawer__panel {
    transition: none;
    animation: none;
  }
}
```

This block is required in `mobile-model-drawer.css` even if a different approach is used, as a forward-safety guard. When `prefers-reduced-motion: reduce` is set, the drawer appears instantly with no transform animation.

**Rationale for slide-up:** the §0 "no decorative animation" rule prohibits hover sparkles, parallax, and looping animations. A one-shot 200ms entry transition on a bottom-sheet is standard affordance signaling — it communicates that the panel came from the bottom edge and can be dismissed via the bottom direction. It is not decorative. The OWID design language does not prohibit purposeful motion affordances; it prohibits motion as decoration. This is the one animation T12 introduces; it is gated by `prefers-reduced-motion`.

---

#### 8.2.5 Drawer trigger button styling

The trigger button is displayed inside `.explorer-layout__selector` at `<768px`, replacing the inline `ModelSelector` visually (the inline `ModelSelector` is `display: none` at `<768px`; the trigger is `display: flex` at `<768px`).

**Token-only CSS:**

```css
.explorer-layout__mobile-selector-trigger {
  display: none;                          /* hidden on desktop */
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 48px;
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-align: center;
  gap: var(--space-2);
}

.explorer-layout__mobile-selector-trigger:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

.explorer-layout__mobile-selector-trigger:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-md);
}

.explorer-layout__mobile-selector-trigger:active {
  background: var(--color-surface);
}

@media (max-width: 768px) {
  .explorer-layout__mobile-selector-trigger {
    display: flex;
  }
}
```

**Touch target:** the trigger is full-width at `<768px` with `min-height: 48px`. Touch-target height is 48px, meeting the WCAG 2.5.5 44px floor and mirroring the §8.1.8 posture.

**No glyph.** The trigger renders visible text only (the parameterized `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)` string). No icon or glyph is added. Rationale: a model-selector affordance does not have a universally recognized icon; text is more legible than a guessable glyph. The "scientific instrument" posture prefers plain labeled controls over icon-guessing.

**Contrast verification:** `--color-text-primary` (#2c3e50) on `--color-surface` (#f8f9fa) ≈ 11.8:1 (WCAG 1.4.3 4.5:1 PASS). `--color-border` (#dde1e7) on `--color-background` (#ffffff) for the border is a non-text element; the border's contrast against the surrounding background (#f8f9fa surface on #ffffff page) is minimal but the border is a decorative separator, not an informational indicator on its own — the button's accessible name and role are provided via ARIA. `--color-info` (#3360a9) focus ring on white ≈ 7.3:1 (WCAG 1.4.11 3:1 PASS).

---

#### 8.2.6 Trigger button states

| State | CSS behavior |
|---|---|
| Rest | `background: var(--color-surface)`; `border: 1px solid var(--color-border)` |
| Hover | `background: var(--color-surface-hover)` |
| Focus-visible | `outline: 2px solid var(--color-info); outline-offset: 2px` |
| Active (pressed) | `background: var(--color-surface)` (same as rest; no additional treatment) |
| Trigger when drawer open | The trigger remains visible (it is NOT hidden when the drawer is open — contrast with §8.1.9 which hides the hamburger). Rationale: the drawer is a half-sheet, not full-screen; the trigger above the drawer tells the user where to look. The `aria-expanded="true"` on the trigger communicates the open state to screen readers. |

**Trigger visibility when drawer open:** the trigger button remains visible at `<768px` regardless of drawer state. The trigger text updates to reflect the current selection count (via `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)`); `aria-expanded` reflects state; `aria-label` updates via `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED` / `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN`.

**Trigger toggle (binding M1):** the trigger's `onClick` is `() => setMobileSelectorOpen(prev => !prev)` — toggle, NOT open-only. Tapping the trigger when the drawer is open closes the drawer. This is required because the trigger remains visible when the drawer is open; a visible-but-noop trigger would be a WCAG 2.4.3 / cognitive confusion risk.

---

#### 8.2.7 Open-drawer panel styling

The drawer panel (`role="dialog"`) contains: a header row (close button, no visible heading), a scrollable body (the `<ModelSelector>` component), and no footer (live-update semantics; no Apply button).

**Panel CSS:**

```css
.mobile-model-drawer__panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 75vh;
  z-index: 200;
  background: var(--color-background);
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
  border-top: var(--border-width) solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.mobile-model-drawer__header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: var(--space-2) var(--space-4);
  border-bottom: var(--border-width) solid var(--color-border);
  flex-shrink: 0;
}

.mobile-model-drawer__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
  background: transparent;
  border: 2px solid transparent;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  line-height: 1;
  flex-shrink: 0;
}

.mobile-model-drawer__close:hover {
  background: var(--color-surface-hover);
}

.mobile-model-drawer__close:focus-visible {
  outline: 2px solid var(--color-info);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}

.mobile-model-drawer__body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  -webkit-overflow-scrolling: touch;
}
```

**Close button glyph:** the close button renders `×` (U+00D7) as a text node inside a `<span aria-hidden="true">`, identical to `.mobile-nav__close` per §8.1. The button's accessible name comes from its `aria-label` attribute.

**Close button position:** top-right corner of the drawer header (`justify-content: flex-end` on `.mobile-model-drawer__header`). This mirrors the §8.1 close-button-at-top convention.

**No visible heading inside the drawer.** The panel's accessible name is provided solely by `aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}` on the `role="dialog"` element. The `<ModelSelector>` component already renders an inner `<h3 class="model-selector__heading">Models</h3>` at line 147 — this heading remains visible inside the drawer without modification. The dialog's `aria-label` overrides any `aria-labelledby` fallback for the dialog role itself.

**No Apply/Done button.** Selection is live-update: each checkbox toggle inside the drawer immediately calls `onSelectionChange` in `DataExplorer`, updating `selectedModels` state. The drawer is a presentational envelope, not a transaction. This matches the existing desktop behavior. No commit step is introduced.

**Panel event propagation (binding M2):** the drawer panel element MUST add `onPointerDown={(e) => e.stopPropagation()}` to prevent `pointerdown` events from bubbling up to the scrim's `onPointerDown={onClose}` handler. Without this, a tap anywhere inside the drawer panel propagates through React's synthetic event system and may dismiss the drawer.

**Contrast:** `--color-text-primary` (#2c3e50) on `--color-background` (#ffffff) ≈ 12.6:1 (WCAG 1.4.3 PASS). `--color-info` (#3360a9) focus ring on white ≈ 7.3:1 (WCAG 1.4.11 PASS).

---

#### 8.2.8 Touch target size — 44px floor for rows, 48px for close button (binding M3)

- **Drawer trigger button:** `min-height: 48px`, full-width. Above the 44px WCAG 2.5.5 floor.
- **Close button inside drawer:** 48×48 px (explicit `width` and `height` on `.mobile-model-drawer__close`). Mirrors §8.1.8.
- **`.model-selector__row` inside the open drawer:** `min-height: 44px` rule scoped to `.mobile-model-drawer__body .model-selector__row`. The current `.model-selector__row` uses `padding: var(--space-2) var(--space-2)` (8px top + 8px bottom = 16px padding) — insufficient to guarantee a 44px touch target on short content. The scoped override ensures each row meets the WCAG 2.5.5 minimum without modifying the desktop row styling.
- **"Select all" and "Clear all" buttons:** these are small action buttons inside `.model-selector__actions`. They do not reach 44px individually. Apply `min-height: 44px; padding: var(--space-2) var(--space-3)` scoped to `.mobile-model-drawer__body .model-selector__actions` and `.mobile-model-drawer__body .model-selector__action-link` to ensure WCAG 2.5.5 compliance inside the drawer.

**All scoped touch-target rules live in `mobile-model-drawer.css`**, not in `app.css`. This keeps desktop row sizing unchanged and scopes the mobile override precisely.

```css
/* Touch-target floor for rows inside the open drawer — WCAG 2.5.5 */
.mobile-model-drawer__body .model-selector__row {
  min-height: 44px;
}

/* Touch-target floor for action buttons inside the open drawer — WCAG 2.5.5 */
.mobile-model-drawer__body .model-selector__actions {
  margin-top: var(--space-4);
}

.mobile-model-drawer__body .model-selector__action-link {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  padding: var(--space-2) var(--space-3);
}
```

---

#### 8.2.9 Trigger visibility when drawer open

The trigger button remains visible when the drawer is open (contrast with §8.1.9's hamburger which hides). The drawer is a partial-height sheet; the trigger sitting above the scrim visually anchors what opened the drawer. `aria-expanded="true"` on the trigger communicates the open state to screen readers.

The trigger's `aria-label` updates when the drawer opens: `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN` ("Close model selector") surfaces on the trigger when `mobileSelectorOpen === true`. Tapping the trigger while the drawer is open closes the drawer (toggle behavior per M1; the trigger's `onClick` toggles `mobileSelectorOpen`).

---

#### 8.2.10 Stacked-below CSS rule supersession

The existing `app.css:681–692` rule:

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

Is **replaced** by T12. The Coder applies this replacement approach:

1. **Retain the single-column grid collapse** (`grid-template-columns: 1fr`) so the viz area is full-width at `<768px`.
2. **Remove `grid-template-areas`** — with only the trigger visible in the selector slot, stacking order is implicit from DOM order.
3. **Replace `width: 100%` on `.explorer-layout__selector`** with `width: auto` (the trigger is `width: 100%` via its own class rule).
4. **Hide the inline ModelSelector** at `<768px` by adding `.explorer-layout__selector .model-selector { display: none; }` in the `@media (max-width: 768px)` block. The `<ModelSelector>` remains in the DOM at `<768px` (desktop-fallback rendering posture) but is visually hidden; only the trigger button is visible.

The post-T12 `@media (max-width: 768px)` block in `app.css` replaces the old rule exactly; the Reviewer confirms no residual `grid-template-areas: "viz" "selector"` remains.

---

#### 8.2.11 Scroll lock — mandatory (key divergence from §8.1)

T12 introduces body scroll lock. This is the single substantive divergence from §8.1.13 (which specifies no scroll lock for the hamburger menu).

**Rationale:** the ModelSelector list can exceed mobile viewport height; the drawer scrolls internally; touch-scroll gestures inside the drawer must not bleed to the underlying page body.

**Implementation pattern (binding):**

```tsx
useEffect(() => {
  const prevOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  return () => {
    document.body.style.overflow = prevOverflow;
  };
}, []);
```

The `useEffect` runs on mount (when `mobileSelectorOpen === true` triggers mounting of `MobileModelSelectorDrawer`). The cleanup function runs on unmount (when the drawer closes via any path: Esc, scrim-tap, close button, or parent re-render / route change). The prior overflow value is captured in the closure before mutation and restored from the closure on cleanup. No ref is needed when the cleanup captures `prevOverflow` directly.

**Tester verification:** (a) `document.body.style.overflow === 'hidden'` immediately after drawer mounts; (b) value restored after Esc close; (c) value restored after close-button click; (d) value restored after forced `root.unmount()` while drawer open.

---

#### 8.2.12 DOM mount — inline inside DataExplorer.tsx

The `MobileModelSelectorDrawer` panel mounts **inline inside `DataExplorer.tsx`**, not as a portal to `document.body`. The panel uses `position: fixed` with `z-index: 200`, which escapes the normal document flow and DataExplorer's stacking context. Portal complexity is not justified.

**z-index values (binding):**

| Element | z-index | Source |
|---|---|---|
| Site header | 100 | `app.css` (existing) |
| Mobile nav panel (§8.1) | 200 | `mobile-nav.css` (T11) |
| Mobile model drawer scrim | 199 | `mobile-model-drawer.css` (T12) |
| Mobile model drawer panel | 200 | `mobile-model-drawer.css` (T12) |

**T11 + T12 coexistence:** both the hamburger nav panel and the model-drawer panel use z-index 200. They cannot both be open simultaneously: the hamburger is in the `<header>` and visible only via a trigger in the header; the drawer is in `DataExplorer` and visible only at `<768px`. There is no code path where both are open at the same time. No stacking conflict.

---

#### 8.2.13 Reduced-motion handling

See §8.2.4. The mandatory CSS block is:

```css
@media (prefers-reduced-motion: reduce) {
  .mobile-model-drawer__panel {
    transition: none;
    animation: none;
  }
}
```

This block must appear in `mobile-model-drawer.css` regardless. When `prefers-reduced-motion: reduce` is set, the drawer appears and disappears instantly.

---

#### 8.2.14 Confirmed accessibility strings

All strings are confirmed verbatim. No additional visible or SR-only prose is introduced beyond these. CDA SME bypass applies (all four are short, generic, accessibility-required, with no model-facing or methodology-flavored language).

| Export name | Value | Usage |
|---|---|---|
| `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED` | `"Open model selector"` | `aria-label` on trigger when drawer is closed (`mobileSelectorOpen === false`) |
| `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN` | `"Close model selector"` | `aria-label` on trigger when drawer is open (`mobileSelectorOpen === true`); also `aria-label` on the close button inside the drawer |
| `MOBILE_MODEL_DRAWER_PANEL_LABEL` | `"Model selector"` | `aria-label` on `role="dialog"` panel |
| `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n: number): string` | `` `Select models (${n} selected)` `` | Visible text on the trigger button; `n` is `selectedModels.length` |

**`MOBILE_MODEL_DRAWER_HEADING` is not introduced.** No visible dialog heading is added; inner `<h3>` from `ModelSelector` remains; dialog `aria-label` on the panel.

**§1.5.4 forbidden vocabulary check:** "Select models (N selected)" — descriptive, count-based, no psychological attribution. "Open model selector" / "Close model selector" / "Model selector" — technical a11y phrasing, no forbidden terms. All four pre-cleared.

---

#### 8.2.15 Component structure summary

```
DataExplorer.tsx
  <div className="data-explorer">
    ...
    <div className="explorer-layout">
      <div className="explorer-layout__viz"> ... </div>
      <div className="explorer-layout__selector">

        {/* Desktop inline rendering (≥768px, CSS-controlled via display:none at <768px) */}
        <ModelSelector
          domainResult={domainResult}
          selectedModels={selectedModels}
          onSelectionChange={setSelectedModels}
          modelColors={modelColors}
        />

        {/* Mobile drawer trigger (<768px only, display: none at ≥768px via CSS) */}
        <button
          ref={drawerTriggerRef}
          type="button"
          className="explorer-layout__mobile-selector-trigger"
          aria-label={mobileSelectorOpen
            ? MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN
            : MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED}
          aria-expanded={mobileSelectorOpen}
          aria-controls="mobile-model-drawer-panel"
          aria-haspopup="dialog"
          onClick={() => setMobileSelectorOpen(prev => !prev)}
        >
          {MOBILE_MODEL_DRAWER_TRIGGER_TEXT(selectedModels.length)}
        </button>

      </div>
    </div>

    {/* Mobile model drawer — conditionally mounted, inline (not portal) */}
    {mobileSelectorOpen && (
      <MobileModelSelectorDrawer
        id="mobile-model-drawer-panel"
        onClose={() => setMobileSelectorOpen(false)}
      >
        <ModelSelector
          domainResult={domainResult}
          selectedModels={selectedModels}
          onSelectionChange={setSelectedModels}
          modelColors={modelColors}
        />
      </MobileModelSelectorDrawer>
    )}

  </div>


MobileModelSelectorDrawer.tsx
  /* Scrim */
  <div
    className="mobile-model-drawer__scrim"
    aria-hidden="true"
    onPointerDown={onClose}
  />
  /* Panel */
  <div
    ref={panelRef}
    role="dialog"
    aria-modal="true"
    aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}
    id={id}
    className="mobile-model-drawer__panel mobile-model-drawer__panel--open"
    onPointerDown={(e) => e.stopPropagation()}
  >
    <div className="mobile-model-drawer__header">
      <button
        ref={closeBtnRef}
        className="mobile-model-drawer__close"
        aria-label={MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN}
        onClick={onClose}
        type="button"
      >
        <span aria-hidden="true">{"×"}</span>
      </button>
    </div>
    <div className="mobile-model-drawer__body">
      {children}   {/* <ModelSelector> passed in from DataExplorer */}
    </div>
  </div>
```

Note: the scrim element uses `onPointerDown` (not `onClick`) for lower latency on touch devices. The panel uses `onPointerDown={(e) => e.stopPropagation()}` to prevent scrim-dismissal when the user taps inside the panel (binding M2).

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
- `FailuresFindingsSection.tsx` — domain-page failures-as-findings entry point (T10). File: `apps/dashboard/src/components/FailuresFindingsSection.tsx`.
- `FailuresInspectView.tsx` — operator inspection variant for failures (T0 + T10). File: `apps/dashboard/src/components/FailuresInspectView.tsx`.
- `FreeListColumn.tsx` — single-model ranked list column, sibling of `FreeListCompare` (T7). File: `apps/dashboard/src/components/FreeListColumn.tsx`.
- `FreeListCompare.tsx` — side-by-side ranked lists
- `FreeListTable.tsx` — read-as-table rendering for `FreeListCompare` (T8). File: `apps/dashboard/src/components/FreeListTable.tsx`.
- `InspectRoot.tsx` — operator inspection-mode root (T0). File: `apps/dashboard/src/components/InspectRoot.tsx`.
- `InspectSection.tsx` — operator inspection-mode section wrapper (T0). File: `apps/dashboard/src/components/InspectSection.tsx`.
- `InspectTable.tsx` — operator inspection-mode tabular rendering (T0). File: `apps/dashboard/src/components/InspectTable.tsx`.
- `MdsTable.tsx` — read-as-table rendering for `MDSPlot` (T8). File: `apps/dashboard/src/components/MdsTable.tsx`.
- `ReadAsTableToggle.tsx` — toggle component for chart/table switch (T8). File: `apps/dashboard/src/components/ReadAsTableToggle.tsx`.
- `ScreenReaderSummary.tsx` — hidden prose for screen readers
- `SimilarityHeatmap.tsx` — Plotly heatmap with CI tooltips
- `SimilarityTable.tsx` — read-as-table rendering for `SimilarityHeatmap` (T8). File: `apps/dashboard/src/components/SimilarityTable.tsx`.
- `DriftTracker.tsx` — longitudinal D3 chart with date slider
- `DateSlider.tsx` — scrubbing control for drift view
- `ModelDetailPanel.tsx` — slide-in panel for model detail
- `AccessibilityTableToggle.tsx` — renamed to `ReadAsTableToggle.tsx` per T8 UI/UX verdict; see §12.9. (Legacy name retained as historical pointer.)
- `MobileNav.tsx` — mobile hamburger nav panel (full-screen overlay, dialog pattern, focus trap; `<768px` only). Spec: DESIGN_SYSTEM.md §8.1.
- `Header.tsx` — updated in T11 to add hamburger trigger state + `MobileNav` wiring.
- `apps/dashboard/src/copy/mobile_nav.ts` — three a11y strings (`MOBILE_NAV_TRIGGER_LABEL_CLOSED`, `MOBILE_NAV_TRIGGER_LABEL_OPEN`, `MOBILE_NAV_PANEL_LABEL`).
- `apps/dashboard/src/styles/mobile-nav.css` — token-only styles for trigger + panel.
- `MobileModelSelectorDrawer.tsx` — mobile bottom-drawer overlay for ModelSelector (`<768px` only). Half-sheet from bottom, dialog pattern, focus trap, scroll lock. Spec: DESIGN_SYSTEM.md §8.2.
- `apps/dashboard/src/copy/mobile_model_drawer.ts` — four a11y strings/functions (`MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED`, `MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN`, `MOBILE_MODEL_DRAWER_PANEL_LABEL`, `MOBILE_MODEL_DRAWER_TRIGGER_TEXT(n)`).
- `apps/dashboard/src/styles/mobile-model-drawer.css` — token-only styles for trigger, scrim, drawer panel, close button, touch-target floor rules, and mandatory `prefers-reduced-motion` block.

**Phase 9a (visualization gap closure):**
- `CentralityChart.tsx` — ranked horizontal bar chart of cultural centrality scores with error bars (T10). File: `apps/dashboard/src/components/CentralityChart.tsx`. Uses dark inverted tooltip (`--color-tooltip-dark-bg/text/divider`). Spec: UI/UX verdict `docs/status/2026-05-24-phase9a-T10-ui-ux-verdict.md`.
- `CentralityTable.tsx` — read-as-table rendering for `CentralityChart` (T10). File: `apps/dashboard/src/components/CentralityTable.tsx`. Columns: Rank, Model, model_id, Centrality score, 95% CI lower/upper, Notes.
- `apps/dashboard/src/styles/centrality-chart.css` — token-only styles for CentralityChart. Uses `--color-tooltip-dark-bg`, `--color-tooltip-dark-text`, `--color-tooltip-dark-divider`.
- `PileComparison.tsx` — side-by-side pile structure comparison across models (T9). File: `apps/dashboard/src/components/PileComparison.tsx`. Cross-column hover highlight, stability tiers, mobile model-switcher. No new tokens. Spec: §12.10 and UI/UX verdict `docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md`.
- `PileComparisonTable.tsx` — read-as-table rendering for `PileComparison` (T9). File: `apps/dashboard/src/components/PileComparisonTable.tsx`. Columns: Model, Pile label, Term, Stability (%).
- `apps/dashboard/src/styles/pile-comparison.css` — token-only styles for PileComparison. No new tokens.
- `apps/dashboard/src/copy/pile_comparison.ts` — all visible UI strings for PileComparison (T9).
- `TermMDSPlot.tsx` — term-level MDS scatter plot with cluster coloring, greedy label placement, hover ellipses, cluster region labels (T6). File: `apps/dashboard/src/components/TermMDSPlot.tsx`. Uses `--color-cluster-*` palette and dark inverted tooltips. Spec: UI/UX verdict `docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md`.
- `TermMDSTable.tsx` — read-as-table rendering for `TermMDSPlot` (T6). Columns: Term, Cluster, MDS X, MDS Y, CI semi-major, CI semi-minor, CI rotation (deg), Bootstrap N.
- `apps/dashboard/src/styles/term-mds-plot.css` — token-only styles for TermMDSPlot.
- `Dendrogram.tsx` — left-to-right hierarchical clustering tree with BP annotations and cluster coloring (T7). File: `apps/dashboard/src/components/Dendrogram.tsx`. Uses `--color-cluster-*` palette, dashed branches below 70% BP. Spec: UI/UX verdict `docs/status/2026-05-24-phase9a-T6T7-ui-ux-verdict.md`.
- `DendrogramTable.tsx` — read-as-table rendering for `Dendrogram` (T7). Columns: Cluster, Term, Subtree depth, Bootstrap support (%).
- `apps/dashboard/src/styles/dendrogram.css` — token-only styles for Dendrogram.

**Data download tab (Phase 9a task 6, 2026-06-09):**
- `DataPage.tsx` — static Data download tab; all prose verbatim from `data/open_bundle/README.md`, `huggingface_dataset_card.md`, and `ARCHITECTURE.md` §6.6. Section render order B/D/A/C/E/F/G/H per UI/UX verdict §20. Uses `--color-surface-note` for the size-warning callout. Carries the moved `Data provenance` (§15.5(a)) and `Cross-model term map and uncertainty` (§16.2) sections from `MethodologyPage.tsx` (M1, 2026-06-10). File: `apps/dashboard/src/components/DataPage.tsx`. Spec: §20, §15.5(a), §16.2.
- `apps/dashboard/src/__tests__/DataPage.test.tsx` — 18-case vitest suite (no fetch). Spec: Architect plan §6 + M1 additions (2026-06-10).

**Methodology page (Phase 6, Mark writes prose):**
- `MethodologyPage.tsx` — long-form article template; eight Mark-authored sections (M1, 2026-06-10). Final section is a single pointer paragraph to the Data page (§6.3, M1, 2026-06-10). The previously-included "Data provenance" section (PROMOTE-2, 2026-05-30) moved to `DataPage.tsx` (M1, 2026-06-10). File: `apps/dashboard/src/components/MethodologyPage.tsx`. Spec: §6 and §6.3.
- `CitationBlock.tsx` — formatted academic citation component
- `LimitationCard.tsx` — each known limitation as a card

**About page (M2, 2026-06-10):**
- `AboutPage.tsx` — long-form article for the About tab; Mark-authored text (M2, 2026-06-10). Single `<section>` with one h2 heading "About Mark Dawson", body as `<p>` elements one per source paragraph, verbatim apart from heading-case normalization and the header comment block. Deliberately shares `.methodology-page*` class structure with `MethodologyPage.tsx` (no `.about-page__*` parallel class tree). No own CSS file, no new tokens. File: `apps/dashboard/src/components/AboutPage.tsx`. Spec: §22.
- `apps/dashboard/src/__tests__/AboutPage.test.tsx` — 9-case vitest suite (no fetch). Includes NavBar integration cases for the fifth tab. Spec: Architect plan M2 §3.5.

**Provenance surfaces (PROMOTE-2, 2026-05-30):**
- `ProvenanceFooter.tsx` — global `<footer>` landmark; reads versions and domains from `/data/provenance.json`; `--font-size-xs` / `--color-text-caption`; per-domain conditional (renders nothing if active domain is not in provenance.json's `domains` block); every screen. File: `apps/dashboard/src/components/ProvenanceFooter.tsx`. Spec: §15.5(b) and §16.

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

### 12.8 SimilarityHeatmap cell-text contrast specification (v0.4.9 — T6, 2026-05-15; supersedes v0.4.5 T5; dashed-stroke contrast ruling added T3, 2026-06-09)

The SimilarityHeatmap uses a 5-stop discrete-binning model (T6, Posture B). Each cell's similarity value is mapped to one of five named hex stops from `--color-scale-seq-0` through `--color-scale-seq-4` via equal-width bins. This section specifies the WCAG AA contrast compliance for each stop and the binding text-color switch threshold.

**Cell background mapping (binding — replaces T5 alpha-blend formula):**

```ts
// Bin boundaries: [0, 0.20, 0.40, 0.60, 0.80, 1.00]
// sim ∈ [0.00, 0.20) → --color-scale-seq-0  (#eaf0f8)
// sim ∈ [0.20, 0.40) → --color-scale-seq-1  (#b8cce4)
// sim ∈ [0.40, 0.60) → --color-scale-seq-2  (#6b9dc8)
// sim ∈ [0.60, 0.80) → --color-scale-seq-3  (#2e6da4)
// sim ∈ [0.80, 1.00] → --color-scale-seq-4  (#1a3a5c)
// Diagonal cells (similarity = 1.00 by construction) always land in stop 4.
```

**WCAG AA contrast table — F-T6-C1 BINDING (supersedes F-T5-C1):**

All luminance values are sRGB relative luminance (WCAG 2.1 definition). Contrast ratios use (L_lighter + 0.05) / (L_darker + 0.05). White text = `var(--color-background)` (#ffffff, L=1.0). Dark text = `var(--color-heatmap-cell-text-dark)` (#000000, L=0.0).

| Stop | Hex | L_bg | White text contrast | Dark text contrast | Text arm used |
|---|---|---|---|---|---|
| seq-0 | #eaf0f8 | 0.877 | 1.13:1 FAIL | 18.54:1 PASS | Dark (#000000) |
| seq-1 | #b8cce4 | 0.590 | 1.64:1 FAIL | 12.79:1 PASS | Dark (#000000) |
| seq-2 | #6b9dc8 | 0.314 | 2.89:1 FAIL | 7.27:1 PASS | Dark (#000000) |
| seq-3 | #2e6da4 | 0.142 | 5.47:1 PASS | 3.84:1 FAIL | White (#ffffff) |
| seq-4 | #1a3a5c | 0.040 | 11.65:1 PASS | 1.80:1 FAIL | White (#ffffff) |

**Contrast-switch threshold (binding — replaces T5 threshold of 0.73):**

```ts
const HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60;
// WCAG AA rationale (2026-05-15 UI/UX verdict — F-T6-C1 BINDING):
// Discrete-binning model: sim < 0.60 → stop 0/1/2 (L ≥ 0.314) → dark text.
// sim ≥ 0.60 → stop 3/4 (L ≤ 0.142) → white text.
//   stop 2 (sim ∈ [0.40,0.60)): dark text 7.27:1 PASS, white text 2.89:1 FAIL
//   stop 3 (sim ∈ [0.60,0.80)): white text 5.47:1 PASS, dark text 3.84:1 FAIL
// Both arms satisfy WCAG AA 4.5:1 at their respective stops.
// The previous T5 threshold of 0.73 is SUPERSEDED and must not be used.
```

**Cell text color selection (binding — replaces T5 rule):**

```ts
textFill = similarity >= HEATMAP_TEXT_SWITCH_THRESHOLD
  ? "var(--color-background)"                  // white, passes ≥5.47:1 at stop 3/4
  : "var(--color-heatmap-cell-text-dark)"      // black, passes ≥7.27:1 at stop 0/1/2
```

Note: the T5 rule used `similarity > 0.73`; the T6 rule uses `similarity >= 0.60` (inclusive lower bound, matching the bin-boundary convention where 0.60 falls into the [0.60, 0.80) bin → stop 3 → white text).

**Diagonal cells** (similarity = 1.0) always land in stop 4 → white text 11.65:1 PASS.

**Component-scoped token (retained from v0.4.5):**

```css
/* Pure black required for WCAG AA compliance across the dark-text arm. See §12.8. */
--color-heatmap-cell-text-dark: #000000;
```

`--color-text-primary` (#2c3e50, L≈0.060) is not a valid replacement: at stop 2 it achieves (0.314+0.05)/(0.060+0.05) = 0.364/0.110 = 3.31:1 — a WCAG AA failure for normal-weight text at 12px.

**Standalone-swatch constraint (binding):**

Stops 0–2 do not pass WCAG AA 3:1 graphical-object contrast on `--color-background` (#ffffff):

| Stop | Standalone contrast on white | Standalone use |
|---|---|---|
| seq-0 | 1.13:1 | Compositional-only — NOT for standalone legend swatches |
| seq-1 | 1.64:1 | Compositional-only — NOT for standalone legend swatches |
| seq-2 | 2.89:1 | Compositional-only — NOT for standalone legend swatches |
| seq-3 | 5.47:1 | Standalone swatch permitted |
| seq-4 | 11.65:1 | Standalone swatch permitted |

If a future legend or downloadable PNG uses these stops as swatches, stops 0–2 must have a 1px `--color-border` (#dde1e7) outline added to provide boundary discrimination.

**R1-marker collision check:**

The sequential scale occupies the blue hue family. The following model palette colors share this family:

| Model token | Hex | L | Nearest sequential stop | L_stop | Contrast between them |
|---|---|---|---|---|---|
| --color-model-1 | #3360a9 | 0.119 | seq-3 (#2e6da4) | 0.142 | 1.15:1 |
| --color-model-8 | #1a5276 | 0.076 | seq-4 (#1a3a5c) | 0.040 | 1.47:1 |

Stop 3 and model-1 are in the same blue hue family and similar luminance (1.15:1 ratio). Stop 4 and model-8 are both dark blue (1.47:1 ratio). These are below the 3:1 threshold that would distinguish them as separate graphical objects if used adjacently as same-size swatches.

**Mitigation and acceptance:** The collision is operationally acceptable because:
1. SimilarityHeatmap and MDSPlot occupy separate VizSwitcher tabs and are never simultaneously visible in the same viewport.
2. Stop 3 and stop 4 appear as 52×52 px solid area fills in cells; model-1 and model-8 appear as small legend dots (~10–12px circles). The shape encoding provides secondary discrimination beyond hue.
3. Each heatmap cell carries a printed similarity value (mono font, center-aligned) that provides a textual discriminator independent of color.
4. No information is conveyed by sequential-scale color alone — the numeric similarity value and the cell position (row/column model labels) together communicate the full finding.

Non-blue model palette colors (model-2 through model-7, model-9 through model-11) are in distinct hue families (red, orange, green, purple, teal, dark orange, dark purple, dark teal, dark gold) and are not in perceptual collision with any sequential stop.

**CI-crosses-null treatment (RESTORED — T3, 2026-06-09):**

The 2026-05-25 rebuild dropped this treatment; Phase 9a T3 restores it. Implementation site: `apps/dashboard/src/components/SimilarityHeatmap.tsx`. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T3-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T3-uiux-verdict.md`).

**Dashed-border spec (binding — restored from T5, adapted for T6 5-stop palette):**

| Condition | stroke | strokeWidth | strokeDasharray |
|---|---|---|---|
| Crossing (`!isDiagonal && ciCrossesNull(ci)`) | `dashStroke` (see below) | 1.5 | "3,2" |
| Non-crossing / null CI / diagonal | `var(--color-border)` | 0.5 | none |

Diagonal cells are NEVER dashed: self-similarity = 1.0 is an identity fact, not a measurement. Short-circuit on `isDiagonal` before `ciCrossesNull(ci)` check is a hard methodological invariant (CDA SME T3 §4b).

**dashStroke contrast rule (UI/UX T3 verdict — binding, WCAG 1.4.11 3:1 non-text):**

```ts
const dashStroke = ciCrossesNull
  ? (sim >= HEATMAP_TEXT_SWITCH_THRESHOLD
      ? 'var(--color-background)'   // white on seq-3/seq-4: 5.47 / 11.67:1 PASS
      : 'var(--color-text-primary)') // dark on seq-0/1/2: 8.43 / 5.82 / 3.31:1 PASS
  : 'var(--color-border)';          // non-crossing solid
```

| Cell stop | Hex | dashStroke | Contrast | WCAG 1.4.11 |
|---|---|---|---|---|
| seq-0 (#eaf0f8) | sim in [0.00, 0.20) | `var(--color-text-primary)` (#2c3e50) | 8.43:1 | PASS |
| seq-1 (#b8cce4) | sim in [0.20, 0.40) | `var(--color-text-primary)` (#2c3e50) | 5.82:1 | PASS |
| seq-2 (#6b9dc8) | sim in [0.40, 0.60) | `var(--color-text-primary)` (#2c3e50) | 3.31:1 | PASS (marginal; numeric value + labels provide redundancy) |
| seq-3 (#2e6da4) | sim in [0.60, 0.80) | `var(--color-background)` (#ffffff) | 5.47:1 | PASS |
| seq-4 (#1a3a5c) | sim in [0.80, 1.00] | `var(--color-background)` (#ffffff) | 11.67:1 | PASS |

No new tokens. Reuses `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60` (existing constant). Token refs by `var(--...)` name; no hardcoded hex (CLAUDE.md pitfall #15).

**Caption (CDA SME T3 §3 binding — two-sentence paired unit, verbatim):**

Rendered in `ContentArea.tsx` `chart-wrap__desc` paragraph ONLY. NOT inside `SimilarityHeatmap.tsx` (no duplication).

> "Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value of 0.50."

**Aria-label templates (CDA SME T3 §2 — four variants, verbatim binding):**

Variant A (off-diagonal, CI present, NOT crossing null):
> `${shortA} versus ${shortB}: similarity ${sim.toFixed(2)}, 95 percent confidence interval ${ci[0].toFixed(2)} to ${ci[1].toFixed(2)}`

Variant B (off-diagonal, CI present, crosses null — the dashed cell):
> `${shortA} versus ${shortB}: similarity ${sim.toFixed(2)}, 95 percent confidence interval ${ci[0].toFixed(2)} to ${ci[1].toFixed(2)}; confidence interval includes the no-shared-structure value of 0.50`

Variant C (off-diagonal, CI null/missing):
> `${shortA} versus ${shortB}: similarity ${sim.toFixed(2)}, confidence interval not available`

Variant D (diagonal):
> `${shortA} self-similarity: 1.00 by construction`

"versus" is the approved non-cognitive connective. "no-shared-structure value of 0.50" provides consistent vocabulary between caption and cell for screen-reader users. "95 percent" written out (not "95%") for screen-reader speech clarity. "1.00 by construction" is load-bearing — do not soften to "self-similarity: 1.00" alone.

**ciCrossesNull strict inequalities (binding — test case 6):**

`ci[0] < 0.5 && 0.5 < ci[1]` — closed-boundary cases ([0.5, 0.501], [0.499, 0.5]) return false.

The §4.5 doc-text refinement (CDA SME T5 §5.4 suggested replacement sentence: replace "shown with reduced saturation" with the dashed-border description) remains a T14 follow-up.

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
- `generated_lede` (per-domain finding) — rendered in `ContentArea.tsx` as the Focus-3 chart lede strip (Phase 9a T2). Not reused in any SR template.
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

---

### 12.10 PileComparison visual specification (v0.5.1 — T9, 2026-05-24)

Phase 9a T9 adds `PileComparison.tsx`, which shows how different models partition domain terms into different categories with different labels. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`, Decision 7, M7); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-T9-ui-ux-verdict.md`).

**CDA SME M7 binding (binding throughout this section):**
- No model is ground truth. All columns visually equal (same width, font weight, hierarchy).
- Divergence is a finding, not a failure.
- No "agreement score" between models (use SimilarityHeatmap for that).
- No Sankey/alluvial diagram (imports directionality framing, violates M7 symmetry).

**Layout:**
- Column grid: `minmax(220px, 1fr)` CSS grid, one column per selected model. `align-items: start`.
- All columns equal width/weight.
- At `≥1024px`: full column grid rendered.
- At `<1024px`: single-column with model-switcher pill row (radio group). Grid collapses to `display: block`.
- At `<480px`: pile labels truncated to 28 chars (handled in JS via `truncate()` helper). CSS ensures overflow graceful.

**Column anatomy (top to bottom):**
1. Column header: model color dot (8px circle) + model short name (font-weight-medium, truncated if needed).
2. Pile cards: pile list sorted by pile size descending; alphabetical tiebreak on label.

**Pile cards:**
- Background: `--color-surface`, border: `1px solid var(--color-border)`, radius: `--border-radius-md`.
- Padding: `--space-3`, gap between cards: `--space-3`.
- Pile label at top: `--font-size-sm`, `--font-weight-medium`, truncated at 40 chars desktop / 28 chars `<480px`.
- Empty label: "(no label)" in `--color-text-muted` italic.

**Term pills:**
- Background: `--color-background`, border: `1px solid var(--color-border)`, radius: `--border-radius-sm`.
- Padding: `2px var(--space-2)`, font: `--font-size-xs`, `white-space: nowrap`.
- Each pill: `tabindex="0"`, `role="button"` for keyboard accessibility.

**Cross-column hover highlight (binding):**
- Hover/focus a term pill → ALL instances of that term across ALL visible columns highlight simultaneously.
- Highlight: pill background → `--color-surface-hover`, pill border → `1px solid var(--color-text-secondary)`, containing card → `box-shadow: var(--shadow-sm)`.
- If term absent from another model: show dashed muted placeholder pill ON HOVER ONLY (not by default). CSS class: `.pile-comparison__pill--absent`. Tooltip: "This term was not produced by [model short name] in this domain."
- Absent placeholder placed in the pile card of the first pile in that column (or at column root if no piles exist).

**Term stability (R10 uncertainty) — dashed border tiers (binding per R10):**
- `≥0.8`: default pill — solid border `1px solid var(--color-border)`.
- `0.6 to <0.8`: CSS class `.pile-comparison__pill--stability-medium` — `1px dashed var(--color-border)`.
- `<0.6`: CSS class `.pile-comparison__pill--stability-low` — `1px dashed var(--color-text-secondary)`, text color `--color-text-caption`.
- Tooltip on ALL pills: "Placed here in [N]% of runs for [model short name]." Provided via `title` attribute and `aria-label`.
- R10 compliance: no bare point-estimate placement without the stability tier class. The tier classes are the R10 display mechanism for pile uncertainty.

**Legend row below grid (binding):**
```
Term stability:  [solid pill] ≥80% of runs    [dashed faint] 60–79%    [dashed medium] below 60%
```
- Font: `--font-size-xs`, color: `--color-text-caption`.
- `aria-hidden="true"` (decorative legend; stability is also communicated via tooltip on each pill).

**Mobile model-switcher (`<1024px`):**
- Horizontal pill row above the single column.
- Each pill: model color dot (8px) + short name, `min-height: 44px` (WCAG 2.5.5 touch target floor).
- Container: `role="radiogroup"`, `aria-label="Select model to view"`.
- Each pill: `role="radio"`, `aria-checked={boolean}`.
- Active pill: `--color-info` background + `--color-background` text + dot color.
- CSS class: `.pile-comparison__model-pill` (rest), `.pile-comparison__model-pill--active` (selected).

**VizSwitcher tab:**
- Label: "Pile Structure". Fragment: `#piles`. Active (not disabled).
- Inserts after "Centrality" tab (index 4 in the 6-tab list: MDS Plot, Free Lists, Similarity, Centrality, Pile Structure, Drift).

**Description paragraph (visible, above columns — binding per journalist test):**
"How models organize [domain] vocabulary into categories: each column shows one model's groupings from its most representative run. Hover any term to see where it appears across models."

**Empty states:**
- Zero models selected: "Select one or more models to see how they structure [domain] terms."
- No pile data: "Pile structure data is not available for the selected models in this domain."

**ReadAsTableToggle table (`PileComparisonTable.tsx`):**
- 4 columns: Model | Pile label | Term | Stability (%)
- Sort: model order → pile index → term lexicographic.
- Caption: "How models categorize [domain] terms: pile assignments from each model's centroid run. Stability indicates how often each placement appeared across runs."

**Copy files:**
- `apps/dashboard/src/copy/pile_comparison.ts` — all visible UI strings.
- `apps/dashboard/src/copy/screen_reader_summaries.ts` → `pileComparisonScreenReaderSummary(domainSlug, nModels)` added.

**Components added:**
- `PileComparison.tsx` — main component.
- `PileComparisonTable.tsx` — ReadAsTableToggle table.
- `apps/dashboard/src/styles/pile-comparison.css` — token-only CSS.

**No new tokens introduced.** All visual decisions use existing tokens from `tokens.css`.

---

## 13. Focus 1 — Individual Model Consistency visual decisions (v0.6.0 — F1-T5–T9, 2026-05-27)

These decisions cover the five Focus 1 frontend tasks (F1-T5 through F1-T9). All are binding on the Coder.

### 13.1 Focus-level selector navigation

A separate horizontal bar between the domain navigation row and the VizTabs row. Two pill buttons; Focus 2 deferred (do not render a disabled stub).

- Active pill: `background: var(--color-info)`, `color: var(--color-background)`, `font-weight: var(--font-weight-medium)`.
- Inactive pill: `background: var(--color-surface)`, `color: var(--color-text-primary)`, `border: 1px solid var(--color-border)`.
- Focus ring: `outline: 2px solid var(--color-info); outline-offset: 2px`.
- Min height: 36px. Min touch target: 44px via padding.
- ARIA: `role="radiogroup"` on container, `aria-label="Analysis focus"`. Each pill: `role="radio"`, `aria-checked`.
- CSS class: `.focus-selector`.

### 13.2 Model selection in Focus 1

When Focus 1 is active, sidebar transitions to single-select (`role="listbox"`, `aria-multiselectable="false"`). Selected row: filled model color dot. Unselected: hollow dot. Heading: "Select a model". Auto-select first model by lexicographic order from current set when Focus 1 activates. Restore multi-select state when returning to Focus 3.

### 13.3 Self-Consistency Overview — ranked list layout

Ranked vertical list of model cards sorted by OCI descending. Not a grid.

Card anatomy (left to right): rank number → model color dot → model name → concentration tier badge (right-aligned). Below: OCI value row, supplementary stats (salience rho, n_runs), deterministic badge when applicable.

- Card: `background: var(--color-surface)`, `border: 1px solid var(--color-border)`, `border-radius: var(--border-radius-md)`, `padding: var(--space-4)`.
- Keyboard-focusable: `role="button"`, `tabindex="0"`. Enter/Space sets selected model.
- Gap: `var(--space-3)`.

### 13.4 Concentration tier badge (CDA SME S6 — no evaluative framing)

| OCI range | Label | Badge text color | Border |
|---|---|---|---|
| OCI >= `OCI_CONCENTRATED_THRESHOLD` | "concentrated" | `--color-text-primary` | `1px solid var(--color-border)` |
| OCI >= `OCI_MODERATE_THRESHOLD` | "moderate" | `--color-text-caption` | `1px solid var(--color-border)` |
| OCI < `OCI_MODERATE_THRESHOLD` | "diffuse" | `--color-text-caption` | `1px dashed var(--color-border)` |

Badge: outline-only pill, `--font-size-xs`, `--font-weight-medium`, `padding: 2px var(--space-2)`. No `--color-success`/`--color-warning`/`--color-error`.

Constants in `apps/dashboard/src/config/analysis.ts`: `OCI_CONCENTRATED_THRESHOLD = 50`, `OCI_MODERATE_THRESHOLD = 10`.

### 13.5 OCI display with CI and n_runs context (R10 + S5)

Spell out "Output Concentration Index" in full. When `oci_ci` non-null: show `X.XX (95% CI [X.XX, X.XX], N = XX runs)`. When null: show `X.XX (N = XX runs; confidence interval unavailable at this run count)`.

Info button `ⓘ` triggers popover with BOOTSTRAP_DESIGN.md §2 caveat: "Register 1 confidence intervals underestimate uncertainty because runs are correlated draws from the same model. See the methodology page for details."

### 13.6 Run agreement heatmap color scale

Reuses existing sequential scale (`--color-scale-seq-0` through `--color-scale-seq-4`) from §12.8. Same text contrast rules.

### 13.7 Run MDS — suppression rule and discriminators (S3)

When n_runs >= 5: render scatter plot. Centrality loading mapped to `--color-scale-seq-0` through `--color-scale-seq-4`. Centroid run: `2px solid var(--color-text-primary)` ring. Axis labels: "MDS Dimension 1/2". Stress footnote below.

When n_runs < 5: suppress plot, show text: "Run map unavailable: fewer than 5 runs recorded for this model (N = [n_runs])."

### 13.8 Term Stability — dashed-border tier treatment

| Stability | Border style | Text color |
|---|---|---|
| >= 0.80 | `1px solid var(--color-border)` | `--color-text-primary` |
| 0.60 to < 0.80 | `1px dashed var(--color-border)` | `--color-text-caption` |
| < 0.60 | `1px dashed var(--color-text-secondary)` | `--color-text-caption` |

Display: "appears in X/N runs". Within-model term MDS displayed alongside the stability list in the same tab.

### 13.9 Focus 1 ActiveVizTab extensions

Three new tab values when Focus 1 active: `f1-self-consistency`, `f1-run-distribution`, `f1-term-stability`. Labels: "Self-Consistency", "Run Distribution", "Term Stability".

### 13.10 Focus 1 description paragraphs

Each tab carries a visible description paragraph. Copy in `apps/dashboard/src/copy/focus1.ts`.

- Self-Consistency: "How consistently each model organizes [domain] vocabulary across independent runs. The Output Concentration Index measures how concentrated the model's output distribution is — higher values mean the model produces nearly the same categorical structure each time."
- Run Distribution: "How similar each pair of runs is for the selected model. The agreement matrix and run map show whether the model produces stable or variable categorical structures across runs."
- Term Stability: "How reliably each term appears in the same structural position across runs for the selected model. Terms that appear in 80% or more of runs in the same position are considered structurally stable."

### 13.11 Cite path — SourceAttribution and CSV

Focus 1 source line: "Individual consistency data: {domain}-focus1.json · Analysis: v{analysis_version}". CSV columns: model_id, n_runs, oci, oci_ci_lower (nullable), oci_ci_upper (nullable), salience_stability_rho, deterministic_output, concentration_tier.

### 13.12 `.f1-model-heading` typography (binding — T3, 2026-06-08)

The model-name heading shown at the top of the Focus 1 Run Distribution and Term Stability sub-views uses `--font-size-base` (16px) + `--font-weight-bold` (700) + `--color-text-primary`.

Rationale: `.f1-model-heading` is a sub-view heading one level below the section heading (`--font-size-xl`, 24px). `--font-size-lg` (18px) is reserved for the editorial lede and key-finding strip; using it for a per-model sub-view heading would overstate that heading's prominence in the page hierarchy. `--font-size-base` + bold achieves the correct visual step between body text and `xl` section headings without a phantom `--font-size-md` token (which does not exist in the scale — see §1.1 note).

CSS class binding:

```css
.f1-model-heading {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}
```

---

## 14. Focus 2 — Within-Provider Family Comparison visual decisions (v0.7.0 — F2-T1–T7, 2026-05-27)

### 14.1 Focus selector — three pills

Order: `[Focus 3: Cross-model] [Focus 2: Within-family] [Focus 1: Individual model]` — broadest to narrowest. Same pill styling as §13.1. Focus 2 label: "Focus 2: Within-family".

### 14.2 Sidebar in Focus 2

Shows a provider family list. Multi-model families (2+): clickable rows with model count badge and provider color dot. Single-model families: grayed, non-clickable, "(1 model)" note. Click a family to enter provider-detail mode (sidebar shows selected family name + its models listed, non-interactive). "Back to all families" link above. Hide per-model checkboxes and filters (same pattern as §13.2 Focus 1 guard).

### 14.3 Family Overview cards — pairwise labeling (CDA SME binding)

Ranked vertical list by within-family similarity descending. Card anatomy:
- Provider name + color dot + model count
- Similarity display (varies by family size per CDA SME notes 1-3):
  - N=1: No similarity shown. Note: "Single-model provider — no within-family comparison available."
  - N=2: "Pairwise similarity (1 pair): X.XX (95% CI [X.XX, X.XX])"
  - N=3: "Mean pairwise similarity (3 pairs): X.XX" with individual pairs listed as sub-rows
- Individual pairwise scores visible by default (CDA SME note 7), not collapsed
- Click navigates to Similarity tab for that family
- Card styling: same as §13.3 (surface background, border, keyboard-focusable)

### 14.4 Mini heatmap

Reuses `SimilarityHeatmap.tsx` unchanged for 2×2 or 3×3 within-family slice. Same color scale (§12.8), same text contrast rules. No new component needed — pass filtered model list and matrix subset.

### 14.5 MDS family highlight

When a family is selected, the cross-model MDS shows:
- Family members: existing filled circle (r=6) + outer ring (separate `<circle>` element, r=9, `fill: none`, `stroke: 2px var(--color-text-primary)` at 35% opacity). Non-color shape discriminator.
- Non-family points: opacity reduced to 0.45 on the `<g>` element containing both ellipse and point.
- Legend note: "Ring indicates selected provider family. Non-family models dimmed."
- No convex hull (CDA SME note 4: visual grouping must not look like cluster boundary).

### 14.6 Salience and Piles tabs

Reuse existing `FreeListCompare` and `PileStructure` components scoped to the selected family's models. With 2-3 models, existing layouts work directly. No new components needed — pass filtered props.

### 14.7 Focus selector ordering rule

The pill order `3 → 2 → 1` is binding. It reflects analytical scope (all models → provider family → single model) and reading order (the broadest comparison is the default landing view).

### 14.8 Model colors in Focus 2

Family members retain their existing §12.4 `--color-model-*` colors. No shared "provider color." The ring treatment (§14.5) distinguishes family membership using shape, not color. Cross-focus color stability: same model = same color in Focus 1, 2, and 3.

### 14.9 Focus 2 ActiveVizTab extensions

Four tab IDs: `f2-overview`, `f2-similarity`, `f2-salience`, `f2-piles`. Labels: "Overview", "Similarity", "Salience", "Piles".

### 14.10 Focus 2 description paragraphs

Copy in `apps/dashboard/src/copy/focus2.ts`:

- Overview: "How models from the same provider compare. Within-family similarity shows whether models sharing a training pipeline produce similar categorical structures, or whether model tier and generation shift the output."
- Similarity: "Pairwise similarity between models from the selected provider family. The heatmap shows structural agreement between each pair of family members. The model map highlights family members in the full cross-model space."
- Salience: "Term salience rankings for models from the selected provider family. Compare which terms each family member ranks as most prominent."
- Piles: "Pile structures from each family member's centroid run. Compare how models from the same provider group domain vocabulary."

### 14.11 Cite path

Source line: "Within-family comparison: {domain}.json · Analysis: v{analysis_version}". CSV for Overview: provider, n_models, mean_pairwise_similarity, mean_pairwise_ci_lower (nullable), mean_pairwise_ci_upper (nullable). CSV for Similarity: provider, model_a, model_b, similarity, ci_lower (nullable), ci_upper (nullable).

### 14.12 Single-family state

Single-model families (DeepSeek, Meta, Microsoft) are a normal first-class state, not a "data gap." Card shows provider name, single model name, and note: "Within-family comparison requires two or more models from the same provider." No "coming soon" or "not yet available."

### 14.13 Forbidden vocabulary additions (Focus 2)

| Don't say | Say instead |
|---|---|
| "Provider consensus" | "Within-family similarity" |
| "Family agreement" | "Within-family pairwise similarity" |
| "Cluster of [provider] models" (on MDS) | "[Provider] models in the map" |

---

## 15. Viz-fixes visual decisions (v0.8.0 — 2026-05-28)

Captures four visual decisions introduced by the viz-fixes change set and ratified by the UI/UX agent (PASS-WITH-NOTES verdict `docs/status/2026-05-28-viz-fixes-ui-ux-verdict.md` items 1–4).

### 15.1 Term stability pill tiers

`PileStructure.tsx` (and related components) renders a stability badge on each pile term. Three tiers based on stability score, encoded via both border-style AND text-color (not color alone — satisfies WCAG 1.4.1):

| Tier | Condition | Border | Text color |
|---|---|---|---|
| **High** | stability ≥ 0.80 | `1px solid var(--color-border)` | `var(--color-text-primary)` |
| **Medium** | 0.50 ≤ stability < 0.80 | `1px dashed var(--color-border)` | `var(--color-text-primary)` |
| **Low** | stability < 0.50 | `1px dashed var(--color-text-secondary)` | `var(--color-text-caption)` |

The legend for pill tiers is `aria-hidden="true"` — screen readers access stability values via `aria-label` on each pill. The two-channel encoding (border-style + text-color) is the sole discriminator; no background-color difference between tiers.

### 15.2 TermMap uncertainty ellipses — cluster color

When `showUncertainty === true`, each term's confidence ellipse is filled/stroked using `getClusterColor(t.cluster)` (the cluster palette from §1.2, `--color-cluster-1` through `--color-cluster-8`). This is defensible because cluster color is already the term's primary positional encoding in the term map; using the same color for the uncertainty region avoids introducing a second independent color encoding that would compete with it.

This decision is NOT a precedent for using cluster colors in non-term-map contexts. The cluster palette (`--color-cluster-*`) and the model palette (`--color-model-*`) must never appear in the same legend within a single chart.

### 15.3 `.term-map-controls` inline-style layout (grandfathered)

The `.term-map-controls` row in `TermMap.tsx` uses inline `style` attributes for its flex layout. This is grandfathered as-is because the values map directly to existing design tokens:

- `gap: '12px'` → `--space-3`
- `gap: '8px'` → `--space-2`
- `gap: '16px'` → `--space-4`
- `gap: '6px'` → not a named spacing token but within the established `--space-1`/`--space-2` range
- `fontSize: '12px'` → `--font-size-xs`
- `fontFamily: 'var(--font-body)'` → uses token already
- `color: 'var(--color-text-primary)'` → uses token already

**The grandfathering is frozen.** No additional inline styles may be added to `.term-map-controls`. Any new control added to this row must use CSS class rules referencing tokens, not inline styles.

### 15.4 Tooltip font-size exception — supplementary text at 10px

Inside the dark-inverted tooltip (`.centrality-chart__tooltip`, using `--color-tooltip-dark-bg` / `--color-tooltip-dark-text`), supplementary footnote text (e.g., bootstrap sample count labels) may use `fontSize: '10px'` — below the `--font-size-xs: 12px` floor. This exception is allowed only under these three conditions simultaneously:

1. The element is inside the dark-inverted tooltip container (background `var(--color-tooltip-dark-bg)`).
2. The text is supplementary, non-primary information (the primary reading path is at `--font-size-xs` or larger).
3. The element has an accessible counterpart at full size (table path or `aria-label`).

This exception does NOT apply anywhere outside the dark-inverted tooltip. Any 10px text outside this context is a WCAG AA violation and must be corrected.

---

## 16. Provenance surfaces (v0.9.0 — PROMOTE-2, 2026-05-30)

Visual decisions and component specifications for the two provenance surfaces shipped with the family+holidays re-baseline promotion. Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-05-30-promote2-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-05-30-promote-ui-ux-verdict.md`); Architect sign-off (`docs/status/2026-05-30-provenance-json-architect-signoff.md`). No new tokens.

### §15.5(a) "Data provenance" section (moved to DataPage.tsx — M1, 2026-06-10)

**Amendment (M1, 2026-06-10):** this section has moved from `MethodologyPage.tsx` to `DataPage.tsx`. The `MethodologyPage.tsx` closing pointer section (§6.3) links to `/data` for readers who want provenance details.

The `DataPage.tsx` component contains a `<section>` with its own `<h2 id="data-provenance-heading">Data provenance</h2>`. The paragraph text is verbatim from CDA SME PROMOTE-2 verdict §3 Option 1 (byte-locked; do not paraphrase). The link to `/data/provenance.json` is:

- `href="/data/provenance.json"` (root-relative — prevents 404 from the `/data` route)
- `target="_blank" rel="noopener noreferrer"`
- Link text: "provenance.json" followed by "(JSON)" as a visible affordance (outside the `<a>` but adjacent), since the target is a raw JSON file, not HTML
- `aria-label` via `<span class="sr-only">` inside the `<a>`: "(opens data provenance manifest in new tab)"

No new tokens. Section container reuses `.data-page__section` CSS class. Heading reuses `.data-page__heading`. Paragraph reuses `.data-page__text`. Link uses `.data-page__link` (color: `--color-info`).

### §15.5(b) Global provenance footer landmark

The `ProvenanceFooter.tsx` component renders a `<footer>` landmark in the global shell (outside `<main>`, after both the explore and non-explore branches in `App.tsx`). Properties:

- Fetches `/data/provenance.json` at mount; renders nothing on fetch failure or absent fields (render-nothing fallback — never renders stale strings or "NaN").
- Versions (`numpy_version`, `scipy_version`) are sourced from the fetched file — not hardcoded. One-click link to `/data/provenance.json` (A6/A8 from PROMOTE-1, carried forward).
- **Per-domain conditional behavior (CDA SME PROMOTE-2 B5b):** accepts an `activeDomain` prop. If `activeDomain` is a non-null/non-undefined string that is NOT present in `provenance.json`'s `domains` block, the component renders `null`. This prevents a false provenance claim on the food domain (not yet promoted under the pinned toolchain). When `activeDomain` is `null` (non-explore routes such as methodology), the footer renders if versions are available.
- Single line, `height: 32px`, `flex-shrink: 0`.
- Tokens: `--font-size-xs` (12px), `--color-text-caption` (~4.60:1 on white — WCAG AA at 12px regular), `--color-border` (top border), `--color-background`. No new tokens.
- Baseline date suffix: sourced from `provenance.json` top-level `generated_at_utc` field (display `.slice(0,10)` — e.g., `"2026-05-29"`). If the field is absent, the date span is not rendered (render-nothing; never "baseline undefined"). `generated_at_utc?: string` is added to the `ProvenanceData` interface. **Amendment v0.12.0:** replaces the v0.9.0 hardcoded `"· baseline 2026-05-30"` string; sourcing from the manifest ensures all promoted domains show the correct rebaseline date without future hardcoding. Gate verdict: UI/UX PASS-WITH-NOTES F2 (`docs/status/2026-05-31-food-promote-ui-ux-verdict.md`).
- Date suffix hidden at `max-width: 600px` (avoids wrapping on mobile).
- `body` CSS is `display: flex; flex-direction: column` and `.app-main` is `flex: 1 1 0; min-height: 0` (replaces the previous `height: calc(100vh - 48px)`) so the footer occupies its natural 32px and the main content flexes to fill the remaining space.

**Note:** Footer vitest tests deferred to T7 (per task acceptance). Per-domain conditional rendering is mechanically enforced by the `activeDomain` prop check at runtime.

### §16.2 Term-MDS disclosure placement (moved to DataPage.tsx — M1, 2026-06-10)

**Amendment (M1, 2026-06-10):** this section has moved from `MethodologyPage.tsx` to `DataPage.tsx`. The binding prose is byte-identical to the v0.12.0 content; only the CSS class-name prefix changed from `.methodology-page__*` to `.data-page__*`.

A `<section aria-labelledby="term-mds-heading">` with heading "Cross-model term map and uncertainty" is present in `DataPage.tsx`, after the `Data provenance` section (§15.5(a)), carrying two binding disclosures:

1. **M4a sentence (Phase 9a binding, CDA SME C4):** "Term position confidence reflects agreement across models, not within-model sampling variance." This sentence was a carry-forward obligation from Phase 9a sign-off and must be present for all three domains (family, holidays, food).

2. **C3 n-count sentence (CDA SME C3):** "The cross-model term map is computed from 15 model informants on family, 14 on holidays, and 8 on food; ellipse widths and branch-probability values are derived from model-resample bootstrap (B=200), so a sparser informant pool produces a different bootstrap envelope shape than a denser one even when the per-model agreement is similar." This closes the audience-translation gap: readers who notice food's bootstrap ellipse shapes may otherwise incorrectly attribute the difference to consensus strength rather than informant-pool size.

**Placement:** at the end of `DataPage.tsx`, after the `Data provenance` section. Both sentences reuse `.data-page__section`, `.data-page__heading`, and `.data-page__text` CSS classes — no new visual decisions. No new tokens.

**Researcher cite-path requirement (UI/UX F3a):** this section is the minimum viable cite path for food's term-MDS. Without it, a researcher citing the food term-MDS has no page anchor to reference for the model-resample bootstrap framing.

Gate verdicts (original): UI/UX PASS-WITH-NOTES F3a (`docs/status/2026-05-31-food-promote-ui-ux-verdict.md`); CDA SME PASS-WITH-NOTES C3/C4 (`docs/status/2026-05-31-food-promote-cda-sme-verdict.md`).
Gate verdicts (M1 move): CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-site-copy-verdicts.md`).

---

## 17. TermMap layout + zoom interaction (v0.10.0 — Stage 1, 2026-05-31)

Visual decisions for the TermMap container height fix, Ctrl+wheel zoom gate, and keyboard zoom controls. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-31-termmap-layout-zoom-uiux-verdict.md`). Architect plan: `docs/status/2026-05-31-termmap-redesign-architect-plan.md`.

### 17.1 Container height bounding (Stage 1 — layout fix)

**The bug:** `render()` sizes the SVG from `wrapRef.getBoundingClientRect().height` and emits `<svg height=H>`. The container chain (`.chart-area` overflow-y:auto, `.chart-wrap` overflow:visible) had no height bound, so the SVG's output grew the parent, the ResizeObserver re-fired `render()`, and height compounded (observed: 23k → 26k px).

**Fix (binding):**

- `.term-map-container` CSS: `display:flex; flex-direction:column; flex:1 1 320px; min-height:0; height:100%`. The `flex-basis:320px` provides the 320px floor for small screens; `min-height:0` enables the flex-shrink path. Do NOT combine a separate `min-height:320px` with `min-height:0` — use flex-basis only.
- `.term-map-container > .chart-wrap` CSS: `flex:1 1 0; min-height:0; overflow:hidden`. This scopes the overflow containment to the term-map path only, so sibling tabs (Free Lists, Similarity, Centrality, Pile Structure, Cluster Tree) retain their `overflow-y:auto` scrolling via the parent `.chart-area`.
- `.chart-area` CSS: retains `overflow-y:auto; overflow-x:hidden` unchanged — do NOT change to `overflow:hidden` globally, as that would break sibling tab scrolling.
- `render()` defensive cap: `H = Math.min(Math.max(rect.height || 400, 400), window.innerHeight)`. Makes the growth loop impossible even if CSS regresses.

**Why `.chart-wrap` overflow is scoped, not global:** the generic `.chart-wrap` class is used by Centrality, Similarity, and Cluster Tree wrappers that use `position:absolute` tooltips and overflow-visible SVGs; changing global `.chart-wrap` to `overflow:hidden` would clip those tooltips. The CSS selector `.term-map-container > .chart-wrap` targets only the TermMap's chart-wrap.

### 17.2 Ctrl+wheel zoom gate (WCAG Level-A scroll-trap fix)

Plain `wheel` events on the term map must **not** call `preventDefault()` and must **not** zoom. Native page scrolling passes through. Zoom only fires when `e.ctrlKey === true` (which browsers also set for trackpad pinch gestures).

The `passive: false` listener registration is retained so that the Ctrl+wheel path can still call `preventDefault()` (preventing the browser's native Ctrl+scroll page-zoom behavior while applying the chart-level viewBox zoom instead).

**Binding implementation:**

```ts
function handleWheel(e: WheelEvent) {
  if (!e.ctrlKey) return;   // plain scroll → pass through; no preventDefault
  e.preventDefault();
  // … existing zoom logic …
}
```

### 17.3 Keyboard zoom controls (WCAG 2.1.1 compliance)

**Zoom step constant:** `ZOOM_STEP = 1.25` (multiplicative). Same file as `MIN_ZOOM` / `MAX_ZOOM`.

**− button:** class `.term-map-controls__zoom-btn`. Multiplies zoom by `1 / ZOOM_STEP`. Disabled when `zoomDisplay <= MIN_ZOOM + 0.01`. `aria-label="Zoom out"`.

**+ button:** class `.term-map-controls__zoom-btn`. Multiplies zoom by `ZOOM_STEP`. Disabled when `zoomDisplay >= MAX_ZOOM - 0.01`. `aria-label="Zoom in"`.

Both buttons zoom toward the **viewport center** of the current viewBox (not a cursor point — keyboard users have no cursor anchor). Logic:

```ts
const centerX = z.vbX + z.vbW / 2;
const centerY = z.vbY + z.vbH / 2;
const newX = centerX - newW / 2;
const newY = centerY - newH / 2;
```

**Reset zoom button:** class `.term-map-controls__zoom-reset`. Shown only when `zoomDisplay > 1.02`. Sets viewBox back to `0 0 W H` and `zoomDisplay` to `1`. `aria-label="Reset zoom to 100%"`. Double-click also calls the same reset logic (shared `resetZoom` callback).

**"Ctrl + scroll to zoom" hint:** static text in the `.term-map-stress` bar. Token: `--color-text-caption` / `--font-size-xs`.

**aria-live:** the `.term-map-stress` div carries `aria-live="polite"` so zoom level changes are announced to AT users. `aria-label="Map controls: stress statistic and zoom level"`.

**Mount location:** −/+ buttons and Reset button are in the right-side group of the `.term-map-stress` bar (not inside `.term-map-controls`). The hint text is inline in the `.term-map-stress` bar alongside the stress statistic.

### 17.4 Scrollbar zoom model (Stage 2 — shipped v0.11.0)

**Shipped Stage 2.** Mark overrode the UI/UX gate recommendation to retain drag-pan and instead requires native scrollbars when zoomed. Gate verdict: UI/UX PASS-WITH-NOTES (`docs/status/2026-05-31-termmap-stage2-uiux-verdict.md`).

**DOM structure (binding):**
```
.term-map-container
  .term-map-controls        ← outside pan-viewport (stays fixed via DOM order)
  .chart-wrap               ← outer border container; ResizeObserver target
    .term-map-pan-viewport  ← scroll container (overflow:hidden at k=1)
      svg#term-svg          ← viewBox frozen "0 0 W H"; width/height = W*k × H*k
        g#term-content      ← transform="scale(k)"; ALL visual content here
  .term-map-stress          ← outside pan-viewport (stays fixed via DOM order)
```

**Zoom model:**
- SVG `viewBox` is **frozen** at `"0 0 W H"` and **never mutated** by zoom.
- Zoom changes `k` (the scale factor). The `<g id="term-content">` `transform` attribute is set to `scale(k)`. The SVG `width`/`height` attributes are set to `W*k` and `H*k`.
- Pan-viewport base class: `overflow:hidden`. When `k > 1.02`, the `.term-map-pan-viewport--scrollable` modifier is added → `overflow:auto` → native scrollbars appear.
- At `k=1`: pan-viewport has `overflow:hidden` → pixel-identical to Stage 1, no scrollbars.

**Scroll-anchor zoom math (ctrl+wheel):** keep the content point under the cursor fixed:
```ts
const vpOffsetX = e.clientX - panVp.getBoundingClientRect().left;
const logicalX  = (panVp.scrollLeft + vpOffsetX) / oldK;
panVp.scrollLeft = logicalX * newK - vpOffsetX;
// (same for Y)
```

**Keyboard zoom (buttons):** anchors to viewport center:
```ts
const logicalX = (panVp.scrollLeft + panVp.clientWidth / 2) / oldK;
panVp.scrollLeft = logicalX * newK - panVp.clientWidth / 2;
```

**Double-click reset + Reset button:** `scrollTo(0,0)` FIRST, then `k←1`, then remove `--scrollable` modifier. Order is binding — removing the modifier before scrolling would hide the stale scroll offset under `overflow:hidden`.

**Drag-pan RE-ADDED (§17.11 — 2026-06-04).** `handleMouseDown` / `handleMouseMovePan` / `handleMouseUpPan` / `handleMouseLeavePan` handlers are present; grab/grabbing cursor styles are active. Drag-pan coexists with native scrollbars (additive). See §17.11 for the full contract.

**FREEZE RULE (binding):** label layout (compass positions, `data-ox`/`data-oy`) is computed once at `k=1` inside `render()` and frozen. The zoom path (`applyScale`) mutates ONLY the `<g transform>` attribute and the SVG `width`/`height` attributes. It must NOT call `render()` or re-run the compass label algorithm.

**Q2 LOCKED — Lens auto-disable at k>1.02:** The magnifying lens checkbox is rendered `disabled` with `title="Zoom out to 100% to use the magnifying lens"` when `k > 1.02`. If the lens was active when the user zooms in, the parent's `onLensToggle` callback is called automatically to deactivate it. The lens coordinate math (via `clientToSVGCoords`/`getScreenCTM`) is only correct at k=1; making it work under content-scale would require inverting the `/z` compensation (TermMap.tsx ~775–777) with a real "lens collapse / explosion" hazard (WCAG 2.3.1 motion). The disable-when-zoomed approach is the LOCKED decision.

**Q3 — Touch/pinch:** Native pinch gesture → browsers synthesize `ctrlKey=true` wheel events → the existing ctrl+wheel handler covers it. Two-finger drag → native pan-viewport scroll. Keyboard +/−/Reset buttons are the a11y path. No extra touch handlers required.

### 17.5 CSS class rules for zoom buttons (binding, Stage 1)

Added to `apps/dashboard/src/styles/app.css`. Classes use tokens exclusively — no hardcoded values. Summary:

**`.term-map-controls__zoom-btn`:**
- `font-family: var(--font-body)` / `font-size: var(--font-size-xs)` / `font-weight: var(--font-weight-medium)`
- `color: var(--color-text-primary)` / `background: var(--color-background)`
- `border: var(--border-width) solid var(--color-border)` / `border-radius: var(--border-radius-sm)`
- `padding: 2px 7px` / `min-width: 24px` / `line-height: 1.4` / `cursor: pointer`
- Hover: `background: var(--color-surface-hover)` / `border-color: var(--color-text-secondary)`
- Focus-visible: `outline: 2px solid var(--color-info)` / `outline-offset: 1px`
- Disabled: `opacity: 0.4` / `cursor: default`

**`.term-map-controls__zoom-reset`:**
- `font-family: var(--font-body)` / `font-size: var(--font-size-xs)` / `font-weight: var(--font-weight-regular)`
- `color: var(--color-info)` / `background: none` / `border: none`
- `padding: 2px var(--space-2)` / `cursor: pointer` / `text-decoration: underline` / `line-height: 1.4`
- Hover: `color: var(--color-text-primary)`
- Focus-visible: `outline: 2px solid var(--color-info)` / `outline-offset: 1px` / `border-radius: var(--border-radius-sm)`

**`.term-map-controls__zoom-group`:**
- Groups the −, +, and Reset buttons in a flex row without inline styles
- `display: flex` / `align-items: center` / `gap: var(--space-1)`

**No inline styles for these buttons** (enforced by §15.3 freeze on `.term-map-controls`). The "Ctrl + scroll to zoom" hint uses `style` attributes inline because it is supplementary text within an existing layout element, consistent with the §15.3 grandfather of inline styles for values that map to existing tokens.

### 17.6 No new tokens (Stage 1)

Stage 1 introduces no new design tokens. All styling uses existing tokens from `tokens.css`. The `--color-text-caption`, `--font-size-xs`, `--color-info`, `--color-border`, `--color-background`, `--color-surface-hover`, `--color-text-primary`, `--border-width`, `--border-radius-sm`, `--font-body`, `--font-weight-medium`, `--font-weight-regular`, `--space-2` tokens are all defined in `tokens.css`.

### 17.7 Stage 1 automated test deferral

Task 1.5 (regression tests: layout no-grow, ctrl-wheel gate, keyboard zoom) is deferred to T7 when the vitest harness is established. Manual browser verification by Mark is the acceptance gate for Stage 1.

### 17.8 Pan-viewport scrollbar CSS (Stage 2, binding)

Added to `apps/dashboard/src/styles/app.css` after the existing zoom-button CSS block.

**`.term-map-pan-viewport` (base):**
- `width: 100%; height: 100%; overflow: hidden`
- No transitions (scroll/scale are instantaneous; see §17.9)

**`.term-map-pan-viewport--scrollable` (k>1.02 modifier):**
- `overflow: auto`
- `box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.06)` — scroll-shadow at 0.06 opacity signals scrollable edges
- `scrollbar-width: thin` — Firefox thin scrollbar
- `scrollbar-color: var(--color-border) transparent` — Firefox scrollbar color
- `::-webkit-scrollbar { width: 4px; height: 4px }` — WebKit thin scrollbar (mirrors `.sidebar` precedent, 4px vs sidebar's 3px)
- `::-webkit-scrollbar-thumb { background: var(--color-border); border-radius: 2px }` — border token for thumb, consistent with sidebar

**No new tokens.** Uses only `--color-border` (existing token, defined in `tokens.css`).

### 17.9 prefers-reduced-motion forward-guard (Stage 2, binding)

```css
@media (prefers-reduced-motion: reduce) {
  .term-map-pan-viewport,
  .term-map-pan-viewport--scrollable {
    transition: none;
    animation: none;
  }
}
```

No motion is currently applied to these elements; the guard is forward-looking so any future transition added to the pan-viewport is automatically suppressed for users who have `prefers-reduced-motion: reduce` set. Required by WCAG 2.3.1 (Motion from Animations, Level AAA — also best practice at AA).

### 17.10 Stage 2 automated test deferral

Stage 2 automated tests (content-scale correctness, scroll-anchor math, lens disable gate) are deferred to T7 when the vitest harness is established. Manual browser verification by Mark is the acceptance gate for Stage 2.

### 17.11 Drag-pan re-add + bottom-clipping fix (v0.13.0 — 2026-06-04)

Root cause: at k=1 the `.term-map-pan-viewport` had `overflow:hidden` AND Stage 2 removed drag-pan → content below the viewport bottom (e.g., "Foster family", "Step-family relations", SVG footer at `y=H-6`) was unreachable. Two independent fixes:

**Fix A — `updateScrollableModifier(k)` helper** replaces the old `applyScale` class-toggle:

```ts
function updateScrollableModifier(k: number) {
  // k>1.02: always scrollable
  if (k > 1.02) {
    panVp.classList.add('term-map-pan-viewport--scrollable');
    return;
  }
  // k=1: scrollable only if SVG actually overflows the viewport
  const svg = panVp.querySelector<SVGSVGElement>('#term-svg');
  if (svg && (svg.scrollWidth > panVp.clientWidth || svg.scrollHeight > panVp.clientHeight)) {
    panVp.classList.add('term-map-pan-viewport--scrollable');
  } else {
    panVp.classList.remove('term-map-pan-viewport--scrollable');
  }
}
```

`applyScale` is kept as an alias for all existing call sites.

**Fix B — `useLayoutEffect` after `svgContent` changes** re-checks for k=1 overflow once React commits the new SVG to the DOM (so `svg.scrollWidth/scrollHeight` are accurate):

```ts
useLayoutEffect(() => {
  updateScrollableModifier(kRef.current);
}, [svgContent, updateScrollableModifier]);
```

**Fix C — Bottom padding and footer position:**
- `pad.b`: 40 → 52 (more bottom margin for the compass label penalty zone)
- SVG footer annotation: `y="${H - 6}"` → `y="${H - 14}"` (keeps text inside the padded bounds)

**Drag-pan handler contract (binding):**
- Active only when `.term-map-pan-viewport--scrollable` class is present.
- Left button only (`e.button !== 0` → return).
- Guard: `if (target.classList.contains('term-dot')) return` — don't drag from a dot; preserves click/hover on dots.
- `e.preventDefault()` on mousedown to suppress text-select during drag.
- Drag translates `scrollLeft/scrollTop` by `-Δx/-Δy` from drag-start scroll position.
- `window` listeners for `mousemove` and `mouseup` so fast drags outside the viewport don't leave drag state stuck.
- `panVp` listeners for `mousedown` and `mouseleave`.
- Toggle `.term-map-pan-viewport--dragging` on the viewport during drag.
- All four listeners removed in useEffect cleanup.

**Coexistence with Stage 2 scroll model:** drag-pan and native scrollbars both translate `scrollLeft/scrollTop` — they operate on the same property, so they coexist without conflict. The lens and drag-pan operate on independent props (lens = SVG coordinate displacement; drag-pan = scrollLeft/scrollTop) — no conflict.

### 17.12 Cursor CSS for drag-pan (v0.13.0 — 2026-06-04)

Added to `apps/dashboard/src/styles/app.css`:

```css
/* §17.11: grab cursor signals that drag-pan is available */
.term-map-pan-viewport--scrollable {
  cursor: grab;
}

/* §17.12: dragging state — applied imperatively during drag-pan */
.term-map-pan-viewport--dragging {
  cursor: grabbing;
  user-select: none;
}

/* prefers-reduced-motion guard for dragging state */
@media (prefers-reduced-motion: reduce) {
  .term-map-pan-viewport--dragging {
    transition: none;
    animation: none;
  }
}
```

`cursor: grab` is added to the existing `.term-map-pan-viewport--scrollable` rule (the `overflow: auto` + `box-shadow` rule from §17.8). The `--dragging` class is new. No new tokens.

---

## 18. Model display label canonical form (v0.14.0 — T8, 2026-06-08)

### 18.1 Problem
The dashboard previously computed a model's short label via 13 copy-pasted local helpers
(`shortName` ×6, `shortModelName` ×7) that had drifted — `claude-opus-4-5` rendered as
`claude-opus-4-5` on some tabs and `opus-4-5` on others. This section is binding.

### 18.2 Single canonical export
`export function displayModel(modelId: string): string` lives ONLY in
`apps/dashboard/src/lib/familyUtils.ts`. No component may define a local `shortName` /
`shortModelName` / equivalent. The Reviewer rejects any new component that reintroduces one
(enforced by the T8 vitest re-drift grep guards).

### 18.3 The transform (pure, never throws)
1. **Org-prefix strip:** if the id contains `/`, discard everything up to and including the
   last `/`.
2. **House-prefix strip:** if the result starts with `claude-`, remove that prefix. Only
   `claude-` is stripped — no other model-family token (`gpt-`, `gemini-`, `grok-`, `phi-`,
   `mistral-`, `deepseek-`, `llama-`) is removed, so single-token model names remain
   distinct and no two models collide on the same label.
3. **Empty guard:** if the result is empty, return the original input.

### 18.4 Worked examples (binding)
`claude-opus-4-5`→`opus-4-5`; `claude-sonnet-4-6`→`sonnet-4-6`; `openai/gpt-5.2`→`gpt-5.2`;
`google/gemini-2.5-pro`→`gemini-2.5-pro`; `meta-llama/llama-4-maverick`→`llama-4-maverick`;
`x-ai/grok-4`→`grok-4`; `mistralai/mistral-large-2512`→`mistral-large-2512`;
`deepseek/deepseek-v3.2`→`deepseek-v3.2`; `microsoft/phi-4`→`phi-4`;
`unknown-model`→`unknown-model`; `org/unknown-model`→`unknown-model`; `""`→`""`.

### 18.5 Accessibility
The visual chip uses `displayModel(modelId)`. Two surfaces use a more verbose form:
1. **SimilarityHeatmap per-cell `aria-label`** uses the full `model_id` for both row and
   column (cell-by-cell SR navigation has no spatial context).
2. **CentralityChart SR summary sentence** uses `displayModel(id) (id)` on first mention of
   each model, then `displayModel(id)` after.
All other aria-labels / tooltips / chips use `displayModel(modelId)` directly.

### 18.6 Notable visible change
ProviderTree previously abbreviated `deepseek-`→`ds-`. Under this rule
`deepseek/deepseek-v3.2`→`deepseek-v3.2` (label changes `ds-v3.2`→`deepseek-v3.2`).
Deliberate correction.
TermMap previously used a local `shortModelDisplayName` helper that produced Title-Case
branded labels (`Claude Opus 4 5`, `Grok 4`). That helper was removed (round 2 of T8,
2026-06-08) in favour of canonical `displayModel`. TermMap pile-label dropdown now renders
`opus-4-5`, `grok-4` etc. — consistent with all other tabs. Mark's ruling.

### 18.7 New providers
If a provider whose id carries a different house-prefix convention is added (e.g. a future
case where the org token IS the display identity), route a new UI/UX gate pass before it
appears on any surface. Do not invent a component-local workaround.

### 18.8 Sites using displayModel (all import from familyUtils.ts, none define a local copy)
Total: 16 sites (13 from round 1 + 3 added in round 2 of T8, 2026-06-08).

shortName family (6): MDSPlot:43, CentralityTable:10, CentralityChart:44,
Focus2FamilySimilarity:31, SimilarityHeatmap:33, Focus1SelfConsistencyOverview:35.
shortModelName family (7): Focus2FamilyOverview:36, PileStructure:48, FreeListCompare:49,
ContentArea:50, Focus1RunDistribution:176, Focus1TermStability:18, ProviderTree:47.
ContentArea:113 special case: `shortName: shortModelName(...)` → `shortName: displayModel(...)`
(the SelectionBar.ModelInfo `shortName` FIELD name is preserved — it is a typed field).
Round-2 additions (3):
- Sidebar.tsx:128 — inline `m.model_id.split('/').pop() || m.model_id` (showed full id bug).
- Timeline.tsx:47+63 — inline `id.split('/').pop()?.replace(/^[a-z]+-/, '')` (grok-4→4,
  phi-4→4 COLLISIONS removed; both the single-model path and the sorted-list path fixed).
- TermMap.tsx — `shortModelDisplayName` (Title-Case branded form, third helper-function name)
  removed entirely; call site at ~line 1201 now uses `displayModel`. Per Mark's 2026-06-08 ruling.

---

## 19. Collection records tab (v0.15.0, Phase 9a T1, 2026-06-09; §19.4 amended v0.19.1, CR-T1, 2026-06-10; further amended v0.19.2, CR-T2, 2026-06-10; further amended v0.19.3, CR-T3, 2026-06-10; further amended v0.19.4, CR-T5, 2026-06-10; further amended v0.19.5, CR-T6, 2026-06-10; §19.17 added v0.20.2, CR-T7, 2026-06-10; §19.18 added v0.20.4, CR-T8, 2026-06-10)

Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T1-failures-restore-cda-sme-verdict.md`, M1-M4); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-T1-failures-restore-uiux-verdict.md`, N1-N7).

### 19.1 Tab label and nav order (binding N1 / CDA SME M1)

Tab label: `"Collection records"` (CDA SME M1 Option A preferred; exported as `FAILURES_TAB_LABEL` from `copy/failures_findings.ts`).

Nav order (binding): `[Explore] [Methodology] [Collection records] [Data]`.

`NavTab` type: `'explore' | 'methodology' | 'collection-records' | 'data'`. The `'collection-records'` value is the tab route key. `aria-current="page"` on the active tab button.

### 19.2 Domain selector (binding N1 / CDA SME M3)

The Collection records tab owns its own domain state, defaulting to `'family'`. It is NOT inherited from the Explore tab's domain.

Element: `<select id="failures-domain-select">` with `<label htmlFor="failures-domain-select">`. The `id` must be distinct from the Sidebar domain picker's id. Label text: `"Domain"` (M3 compliant).

Three domain options: Family / Holidays / Food (same set as Explore).

### 19.3 Page heading (binding CDA SME M2 / T10 SECTION_HEADING verbatim)

`<h1>` element with text `"Collection records and follow-up interviews"` byte-for-byte. This is the T10 SECTION_HEADING string; it is the tab's primary heading.

### 19.4 Content order (binding N1; amended v0.19.1 / CR-T1 2026-06-10; further amended v0.19.2 / CR-T2 2026-06-10; further amended v0.19.3 / CR-T3 2026-06-10; further amended v0.19.4 / CR-T5 2026-06-10; further amended v0.19.5 / CR-T6 2026-06-10)

Within the tab region, content renders in this order:
1. `<h1>` heading (§19.3).
2. Domain selector row (§19.2) -- rendered below the heading, before impact paragraph.
3. Impact paragraph (`IMPACT_PARAGRAPH_FAILURES`) `<p className="failures-findings__impact">`: Mark-authored, approved verbatim 2026-06-10; renders in the `ready` fetch state only (not in loading/fetch-failed/malformed states); renders in the empty-state path (n_records === 0, AC3). See v0.19.1 CR-T1 for the CSS class spec.
4. Taxonomy block (`TAXONOMY_BLOCK`) `<section className="failures-findings__taxonomy">`: exports from `copy/failures_findings.ts`; renders in the `ready` fetch state only (not in loading/fetch-failed/malformed states); renders in the empty-state path (n_records === 0) -- the taxonomy is a property of the LSB pipeline, not of the per-domain data. See §19.14 for full spec.
5. `framing_note` `<p>` -- verbatim, byte-identity from the JSON field. First data-sourced content paragraph (T9 §5.1 / AC5).
6. Counts caption `<p className="failures-findings__counts">` -- four-cell matrix per CR-T6 / §19.16: rendered when `countsCaptionText()` returns a non-empty string; omitted when both `n_records === 0` and `nParsedResponses === 0` (or undefined). The `nParsedResponses` argument is sourced from `recordsFetchState.data.n_informants` when records side is ready; `undefined` when not ready (preserves failures-only caption, CDA SME N4). See §19.16 for the full caption template and empty-state matrix.
7. When `n_records > 0`, records render in two grouped lists with the follow-up impact paragraph between them:
   a. Failure records `<ol className="failures-findings__list">`: all `record_type === 'failure'` records.
   b. Follow-up interviews impact paragraph (`IMPACT_PARAGRAPH_FOLLOWUPS`) `<p className="failures-findings__impact">`: Mark-authored, approved verbatim 2026-06-10; renders ONLY when at least one `decline_interview` record is present (`data.records.some(r => r.record_type === 'decline_interview')`). Does not render when zero decline_interview records exist. CSS class reuses `.failures-findings__impact` (no new tokens).
   c. Decline-interview records `<ol className="failures-findings__list">`: all `record_type === 'decline_interview'` records. Rendered only when at least one such record exists (same condition as 7b).
   When `n_records === 0`: empty-state `<p>` only (§19.9); no grouped lists.
8. Successful-records summary section (`<section aria-labelledby="records-summary-heading">`): fetched independently from `/data/records/{domain}.json`; renders in its own `RecordsFetchState` independent of the failures-side state; renders BELOW the failures list (below EMPTY_CAPTION when n_records === 0). See §19.15 for full spec.

No chart-lede, no Smith's S, no SelectionBar, no VizTabs, no consensus-score strings (M4 / N7 chrome isolation).

### 19.5 Badge tokens (binding N3)

Two badge variants, implemented with CSS class modifiers on `.failures-findings__badge`:

| Badge | Border + text token | Background |
|---|---|---|
| "Collection failure" | `var(--color-error)` (10.23:1 on white, WCAG AAA) | `var(--color-background)` |
| "Follow-up interview" | `var(--color-border)` / `var(--color-text-secondary)` | `var(--color-background)` |

Pill shape: `--space-2` horizontal padding, `--border-radius-sm`. **No new tokens.**

### 19.6 `<details>`/`<summary>` pattern (binding N4)

Native `<details>`/`<summary>` elements. No `role` override. Summary collapsed state contains:
- Badge (§19.5).
- `model_id` in `<code>` (mono).
- `collection_date` as YYYY-MM-DD.
- For failures: `error_type` + "error_message: N chars".
- For decline interviews: "originating_outcome_class: `<code>{enum}</code>`".

**NO verbatim model bytes in summary rows** (T10 S1 binding). The full verbatim content is only exposed in the expanded `<details>` body.

Focus ring on summary: `.failures-findings__summary:focus-visible { outline: 2px solid var(--color-info); outline-offset: 2px; }`.

### 19.7 `<pre>` container (binding N5)

Class: `.failures-findings__pre`. Properties:
- `font-family: var(--font-mono)`
- `font-size: var(--font-size-xs)`
- `background: var(--color-surface)`
- `border: var(--border-width) solid var(--color-border)`
- `border-radius: var(--border-radius-sm)`
- `padding: var(--space-3)`
- `white-space: pre-wrap`
- `word-break: break-word`
- `overflow-y: auto`
- `max-height: 320px`

### 19.8 Block labels (T10 S4b + S6 verbatim)

All block labels are exported from `copy/failures_findings.ts`:
- `"Originating context"`
- `"Follow-up prompt LSB sent"`
- `"Model output to the follow-up prompt"`
- `"Reasoning trace the provider surfaced"` (shown only when `thinking_verbatim` is non-empty)
- `"Provenance IDs"`

### 19.9 Empty state (binding T10 S2 verbatim)

When `n_records === 0` (e.g., food domain): render the `EMPTY_CAPTION` string byte-for-byte:

> "This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."

No error icon, no greyout, no skeleton, no "coming soon." The absence is a first-class observation (ARCHITECTURE.md §1.5.6 / CLAUDE.md §9 pitfall #4).

### 19.10 Loading and error states (first-class)

Three fetch states beyond `ready`:
- **loading:** `LOADING_TEXT = "Loading collection records…"`
- **fetch-failed:** `FETCH_FAILED_TEXT = "Could not load collection records for this domain. Check that the data file is present."`
- **malformed:** `MALFORMED_TEXT = "Collection records data for this domain could not be parsed."`

These are first-class states. No "missing"/"pending"/"placeholder" language (AC10).

### 19.11 No new tokens

This section introduces no new CSS custom properties. All styling is token-only via existing `tokens.css` definitions.

### 19.12 New files (binding inventory)

| File | Role |
|---|---|
| `apps/dashboard/src/components/FailuresFindings.tsx` | Collection records tab component |
| `apps/dashboard/src/copy/failures_findings.ts` | CDA-SME-approved copy strings |
| `apps/dashboard/src/styles/failures-findings.css` | Token-only styles |
| `apps/dashboard/src/__tests__/FailuresFindings.test.tsx` | 10-case vitest suite |

Edited files:
- `apps/dashboard/src/components/NavBar.tsx` — adds `'collection-records'` tab; exports `NavTab` type.
- `apps/dashboard/src/App.tsx` — imports `NavTab` from NavBar; adds `<FailuresFindings />` branch.
- `apps/dashboard/src/data/types.ts` — adds `FailureOutcomeClass`, `FailureRecord`, `DeclineInterviewRecord`, `FailuresRecord`, `FailuresFile` types.
- `apps/dashboard/src/styles/app.css` — imports `failures-findings.css`.

### 19.13 Chrome isolation (M4 / N7)

The rendered Collection records tab text content (excluding `<pre>` verbatim model bytes) must not contain: `consensus`, `Smith's S`, `agree`, `believe`, `think` (as \bthink), `worldview`, `categoriz`. The vitest suite's case 9 enforces this with a DOM-walk that excludes `<pre>` nodes.

### 19.14 Taxonomy block (binding, CR-T3, v0.19.3)

The taxonomy block is a CDA-SME-approved static disclosure surface that names the three top-level collection outcomes and the seven `originating_outcome_class` enum values. It renders as step 4 in §19.4 content order.

**Element structure (binding F1):**

```tsx
<section
  aria-labelledby="taxonomy-block-heading"
  className="failures-findings__taxonomy"
>
  <h2
    id="taxonomy-block-heading"
    className="failures-findings__taxonomy-heading"
  >
    {TAXONOMY_BLOCK.heading}
  </h2>
  <p className="failures-findings__taxonomy-bridge">
    {TAXONOMY_BLOCK.bridge}
  </p>
  <ul className="failures-findings__taxonomy-list">
    {TAXONOMY_BLOCK.topLevel.map(row => (
      <li key={row.term}>
        <strong>{row.term}</strong>{' '}{row.description}
      </li>
    ))}
  </ul>
  <p className="failures-findings__taxonomy-enum-label">
    <code>originating_outcome_class</code>{' '}ENUM VALUES (seven, byte-identical to the schema):
  </p>
  <ul className="failures-findings__taxonomy-list">
    {TAXONOMY_BLOCK.enumValues.map(row => (
      <li key={row.id}>
        <code>{row.id}</code>{' '}{row.description}
      </li>
    ))}
  </ul>
</section>
```

**Heading level (binding F1):** `<h2>` is required. The tab has one `<h1>` per §19.3; the taxonomy block is a major conceptual section warranting `<h2>` for correct document outline and screen-reader navigation. A `<p>` with `<strong>` heading would break WCAG 2.4.6 (headings and labels).

**Element choice rationale (binding F1):** `<ul>` is used over `<dl>` because no `<dl>`/`<dt>`/`<dd>` CSS rules exist in `failures-findings.css`; introducing `<dl>` would require new CSS class definitions with no semantic gain over `<ul>` + `<strong>`/`<code>` markers for a taxonomy list on this surface.

**CSS classes (binding F2, all token-only, no new tokens):**

- `.failures-findings__taxonomy` -- section container; `margin-bottom: var(--space-8)`; `max-width: var(--max-prose-width)`.
- `.failures-findings__taxonomy-heading` -- h2 heading; `font-size: var(--font-size-base)`; `font-weight: var(--font-weight-bold)`; `color: var(--color-text-primary)`; `line-height: var(--line-height-tight)`; `margin-bottom: var(--space-3)`.
- `.failures-findings__taxonomy-bridge` -- bridge sentence paragraph; `font-size: var(--font-size-sm)`; `color: var(--color-text-primary)`; `line-height: var(--line-height-body)`; `margin-bottom: var(--space-4)`.
- `.failures-findings__taxonomy-list` -- both ul elements; `list-style: disc`; `padding-left: var(--space-6)`; `margin-bottom: var(--space-4)`; `display: flex`; `flex-direction: column`; `gap: var(--space-2)`.
- `.failures-findings__taxonomy-list li` -- list items; `font-size: var(--font-size-sm)`; `color: var(--color-text-primary)`; `line-height: var(--line-height-body)`.
- `.failures-findings__taxonomy-list li code` -- inline code in list items; `font-family: var(--font-mono)`; `font-size: var(--font-size-xs)`; `color: var(--color-text-primary)`.
- `.failures-findings__taxonomy-enum-label` -- subheading paragraph for enum section; `font-size: var(--font-size-sm)`; `color: var(--color-text-secondary)`; `font-weight: var(--font-weight-medium)`; `margin-bottom: var(--space-2)`; `margin-top: var(--space-2)`.
- `.failures-findings__taxonomy-enum-label code` -- the originating_outcome_class identifier in the subheading; `font-family: var(--font-mono)`; `font-size: var(--font-size-xs)`; `color: var(--color-text-primary)`.

**TAXONOMY_BLOCK export shape (binding F5):**

The `TAXONOMY_BLOCK` export in `copy/failures_findings.ts` is a structured object literal (`as const`):

- `heading: string` -- SME-approved heading text
- `bridge: string` -- SME-approved bridge sentence
- `topLevel: Array<{ term: string; description: string }>` -- three rows
- `enumSubheading: string` -- SME-approved subheading (with `originating_outcome_class` named)
- `enumValues: Array<{ id: string; description: string }>` -- seven rows; id is byte-identical to schema enum

All string values are the CDA SME-approved wording (T3 verdict). The seven `id` values are byte-identical to `cdb_core/schemas.py` lines 734-742: `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`.

**Render conditions (binding F4):**
- Renders inside `fetchState.kind === 'ready'` branch only.
- Renders when `n_records === 0` (empty-state path) -- the taxonomy is a property of the LSB pipeline.
- Does NOT render in `loading`, `fetch-failed`, or `malformed` states.
- NOT gated on `n_records > 0`.

**Vitest cases (binding F6):**
- Case 16: byte-identity -- TAXONOMY_BLOCK heading text, bridge text, and all seven enum `id` values are present in the rendered DOM under familyJson fixture.
- Case 17: each of the seven originating_outcome_class enum identifier strings appears inside a `<code>` element in the rendered DOM under familyJson fixture.
- Case 18: taxonomy block renders (heading text present) in the food empty-state path (foodJson fixture, n_records === 0).
- Case 19: taxonomy block does NOT render in loading state (mirrors case 13 pattern -- never-resolving fetch mock).
- Case 9 (existing): chrome-isolation DOM-walk passes unchanged; SME wording contains zero instances of §19.13 forbidden substrings.

**Accessible landmark (binding F1):** `aria-labelledby="taxonomy-block-heading"` on the `<section>` provides a named landmark for screen-reader navigation. The `id="taxonomy-block-heading"` on the `<h2>` is required and must be present in the rendered DOM.

**No new tokens (binding §19.11 posture):** All CSS rules use only tokens already defined in `tokens.css`. No new `--*` custom properties introduced by this section.

### 19.15 Successful-records summary section (binding, CR-T5, v0.19.4)

The successful-records summary section is a CDA-SME-approved per-model table surfacing the `/data/records/{domain}.json` summary artifact. It renders as step 8 in §19.4 content order -- below the failures/decline-interviews list, or below EMPTY_CAPTION when n_records === 0. "Successful" means the LSB pipeline parsed a primary-step response; it is NOT a quality judgment on the model output (CR-T4 N5 / DATA_DICTIONARY.md §12.6 carry-forward).

**Element structure (binding, UI/UX CR-T5):**

```tsx
<section
  aria-labelledby="records-summary-heading"
  className="failures-findings__successes"
>
  <h2
    id="records-summary-heading"
    className="failures-findings__taxonomy-heading failures-findings__successes-heading"
  >
    {RECORDS_SECTION_HEADING}
  </h2>
  <p className="failures-findings__framing-note failures-findings__successes-framing">
    {data.framing_note}  {/* verbatim from JSON, byte-identical (AC6) */}
  </p>
  {data.by_model.length === 0 ? (
    <p className="failures-findings__empty failures-findings__successes-empty">
      {RECORDS_EMPTY_OBSERVATION}
    </p>
  ) : (
    <div className="failures-findings__successes-table-wrapper">
      <table className="failures-findings__successes-table">
        <caption className="sr-only">{RECORDS_SECTION_HEADING}</caption>
        <thead>...</thead>
        <tbody>...</tbody>
      </table>
    </div>
  )}
  <p className="failures-findings__successes-caption">
    {RECORDS_LINK_OUT_CAPTION}
  </p>
</section>
```

**Section heading (binding, CDA SME N1):** `<h2>` with `RECORDS_SECTION_HEADING = "Per-model summary of parsed primary-step responses"`. Reuses `.failures-findings__taxonomy-heading` for the heading style (same level, same visual weight). The additional `.failures-findings__successes-heading` class provides `margin-bottom: var(--space-4)` spacing.

**WCAG accessible name (binding, UI/UX WCAG gap):** `<caption className="sr-only">` inside the `<table>` element provides a programmatic accessible name per WCAG 1.3.1. The `<section aria-labelledby>` provides the landmark name but does not automatically label the table inside it.

**Column labels (binding, CDA SME N2):** Model | Provider | Runs | QA-pass count | Model version returned. Exported from `copy/failures_findings.ts` as `RECORDS_COL_*` constants. No sortable column headers (AC16 / CDA SME -- no ranking signal).

**Cell rendering (binding, AC7):** `model_id`, `provider`, and `model_version_returned` render inside `<code className="failures-findings__successes-code">` elements. `n_runs` and `n_qa_passed` render as plain integers. `model_version_returned_count` is NOT rendered in the table (CR-T4 lex-greatest selection is a property of the summary as documented in DATA_DICTIONARY §12.6).

**Row order (binding, AC16):** Lexicographic by `model_id` ascending, determined by the artifact's `by_model` array order. No client-side sorting. No `<th onClick>` handlers. No sort state.

**Mobile overflow (binding, UI/UX CR-T5):** `.failures-findings__successes-table` uses `display: block` to enable native browser horizontal scroll on narrow viewports (375px with 5 columns will overflow). `thead` and `tbody` use `display: table` to preserve table layout. No JavaScript scroll handler required.

**Fetch coupling (binding, AC2, AC3):** Both `/data/failures/{domain}.json` and `/data/records/{domain}.json` are fetched via `Promise.allSettled` against the same `AbortController`. Domain change cancels both in-flight requests. Two independent sub-state variables (`fetchState: FetchState` and `recordsFetchState: RecordsFetchState`) handle rendering independently. A failures-side error does NOT suppress the successes section; a records-side error does NOT suppress the failures section.

**Independent fetch states (binding, AC3):** `RecordsFetchState` union mirrors `FetchState`: `idle | loading | fetch-failed | malformed | ready`. Each state maps to a distinct render:
- `idle`: renders nothing.
- `loading`: renders `RECORDS_LOADING_TEXT` as `<p className="failures-findings__status failures-findings__successes-status">`.
- `fetch-failed`: renders `RECORDS_FETCH_FAILED_TEXT` as `<p className="failures-findings__status failures-findings__successes-status">`.
- `malformed`: renders `RECORDS_MALFORMED_TEXT` as `<p className="failures-findings__status failures-findings__successes-status">`.
- `ready`: renders the section with heading, framing_note, table (or zero-runs observation), and link-out caption.

**Zero-runs first-class state (binding, AC8):** When `by_model: []`, the section renders `RECORDS_EMPTY_OBSERVATION` using `.failures-findings__empty .failures-findings__successes-empty`. The `framing_note` still renders above it. Table chrome does NOT render. This is binding-equivalent to the existing failures empty-state pattern (CR-T4 N3 carry-forward).

**Link-out caption (binding, AC12):** `RECORDS_LINK_OUT_CAPTION` renders as `<p className="failures-findings__successes-caption">` below the table (or below the empty-state observation). Uses `--color-text-caption` (~4.60:1 on white, WCAG AA at 12px). Do NOT use `--color-text-secondary` (~3.40:1, fails 4.5:1 at 12px regular weight). Caption points to the Data tab; does not link out to external URLs directly.

**CSS classes (binding, all token-only, no new tokens):**

- `.failures-findings__successes` -- section container; `margin-top: var(--space-8)`; `max-width: var(--max-prose-width)`.
- `.failures-findings__successes-heading` -- h2 spacing modifier; `margin-bottom: var(--space-4)`.
- `.failures-findings__successes-framing` -- framing note paragraph; `margin-bottom: var(--space-4)` (reuses `.failures-findings__framing-note` for color/size).
- `.failures-findings__successes-empty` -- zero-runs observation; `margin-bottom: var(--space-4)` (reuses `.failures-findings__empty` for color/size).
- `.failures-findings__successes-table-wrapper` -- overflow container; `overflow-x: auto`; `margin-bottom: var(--space-4)`.
- `.failures-findings__successes-table` -- `display: block` (mobile scroll); `border-collapse: collapse`; `font-size: var(--font-size-sm)`.
- `.failures-findings__successes-table thead, .failures-findings__successes-table tbody` -- `display: table`; `width: 100%`; `table-layout: fixed`.
- `.failures-findings__successes-th` -- column headers; `font-weight: var(--font-weight-medium)`; `color: var(--color-text-secondary)`; `font-size: var(--font-size-xs)`; `padding: var(--space-2) var(--space-3)`; `border-bottom: var(--border-width) solid var(--color-border)`; `white-space: nowrap`.
- `.failures-findings__successes-tr:hover` -- `background: var(--color-surface-hover)`.
- `.failures-findings__successes-td` -- data cells; `padding: var(--space-2) var(--space-3)`; `border-bottom: var(--border-width) solid var(--color-border)`; `font-size: var(--font-size-sm)`; `color: var(--color-text-primary)`.
- `.failures-findings__successes-td--num` -- numeric cells (n_runs, n_qa_passed); `text-align: right`; `white-space: nowrap`.
- `.failures-findings__successes-code` -- inline code in cells; `font-family: var(--font-mono)`; `font-size: var(--font-size-xs)`; `color: var(--color-text-primary)`; `word-break: break-all`.
- `.failures-findings__successes-caption` -- link-out caption; `font-size: var(--font-size-xs)`; `color: var(--color-text-caption)`; `line-height: var(--line-height-body)`; `max-width: var(--max-prose-width)`.
- `.failures-findings__successes-status` -- status paragraph for loading/failed/malformed; `margin-top: var(--space-8)` (reuses `.failures-findings__status` for color/size).
- `.sr-only` -- screen-reader-only class for `<caption>` accessible name (standard sr-only pattern; not a token).

**No new tokens (binding §19.11 posture):** All CSS rules use only tokens already defined in `tokens.css`. No new `--*` custom properties introduced by this section.

**New copy strings (all CDA SME N1-N5 approved, exported from `copy/failures_findings.ts`):**
- `RECORDS_SECTION_HEADING` -- section `<h2>` text (CDA SME N1).
- `RECORDS_COL_MODEL`, `RECORDS_COL_PROVIDER`, `RECORDS_COL_RUNS`, `RECORDS_COL_QA_PASS`, `RECORDS_COL_VERSION` -- column labels (CDA SME N2).
- `RECORDS_EMPTY_OBSERVATION` -- zero-runs first-class observation (CDA SME N3).
- `RECORDS_LINK_OUT_CAPTION` -- link-out caption below table (CDA SME N4).
- `RECORDS_LOADING_TEXT`, `RECORDS_FETCH_FAILED_TEXT`, `RECORDS_MALFORMED_TEXT` -- status strings (CDA SME N5).

**TAXONOMY_BLOCK update (binding, SME N6 conditional revision):** `TAXONOMY_BLOCK.topLevel[0].description` updated in same commit: drops stale "when the successes section ships" phrasing (section has now shipped). New text: "LSB parsed primary-step output from the session. Surfaced in the per-model summary section below. The per-domain summary artifact is at /data/records/{slug}.json."

**Vitest cases (binding, AC13):**
- Case 20: records section heading (`RECORDS_SECTION_HEADING`) renders byte-for-byte under `recordsFamilyJson` fixture.
- Case 21: `framing_note` from `recordsFamilyJson` fixture renders byte-for-byte.
- Case 22: all 17 family `model_id` values render as `<code>` elements in row order matching the fixture's `by_model` array order.
- Case 23: records section renders zero-runs observation under a `by_model: []` fixture; table absent.
- Case 24: records section renders `RECORDS_FETCH_FAILED_TEXT` when records fetch returns ok=false (HTTP 404).
- Case 25: records section heading absent in loading state (never-resolving fetch; mirrors case 13/19 pattern).
- Case 26: records section renders BELOW `EMPTY_CAPTION` in DOM order when `failures.n_records === 0` (foodJson + recordsFoodJson); asserted via `compareDocumentPosition`.
- Case 9 (existing, extended): chrome-isolation DOM-walk now fetches both failures and records fixtures; extended DOM includes table headers, cells, captions, empty-state observation, framing_note, link-out caption. Forbidden-substring scan passes over the extended DOM.
- Case 10 (existing, updated): domain switch now asserts 2 fetches per domain (failures + records = 4 total calls after domain switch).

**Accessible landmark (binding):** `aria-labelledby="records-summary-heading"` on the `<section>` provides a named landmark. `id="records-summary-heading"` on the `<h2>` is required and must be present in the rendered DOM.

### 19.16 Counts caption template (binding, CR-T6, v0.19.5)

The counts caption is a single `<p className="failures-findings__counts">` rendered at step 6 in §19.4 content order. It names the parsed-primary-step-response count alongside the failure and decline counts. No leading total (CDA SME N1 BINDING: Option C -- summing parsed responses and failure-side records would be a category error with no defensible denominator).

**Caption template (CDA SME N2 BINDING, byte-identical):**

All-positive case (n_records > 0 AND nParsedResponses > 0):
> `{S} parsed primary-step responses, {F} collection {failure|failures}, {D} follow-up {interview|interviews}.`

Where `{S}` is `nParsedResponses`, `{F}` is `nFailure`, `{D}` is `nDecline`. Pluralization rules mirror the existing L158-159 pattern: "failure" vs "failures" on `nFailure === 1`; "interview" vs "interviews" on `nDecline === 1`. "responses" is always plural (S > 0 when this clause renders).

**Four-cell empty-state matrix (CDA SME N3 BINDING):**

| `n_records` | `nParsedResponses` | Caption renders as |
|---|---|---|
| > 0 | > 0 | Full three-clause: `{S} parsed primary-step responses, {F} collection {failure|failures}, {D} follow-up {interview|interviews}.` |
| > 0 | 0 or undefined | Failure-clause-only: `{F} collection {failure|failures}, {D} follow-up {interview|interviews}.` |
| 0 | > 0 | S-clause-only: `{S} parsed primary-step responses.` |
| 0 | 0 or undefined | Caption omitted (empty string returned by `countsCaptionText()`; `<p>` not rendered) |

Each cell is a first-class state. No "no parsed responses yet" / "no failures yet" / "available soon" framing. Absence is an observation (ARCHITECTURE.md §1.5.5 / CLAUDE.md Pitfall 4).

**Records-not-ready state (CDA SME N4 BINDING):** When `recordsFetchState.kind !== 'ready'` (loading, fetch-failed, malformed, or idle), `nParsedResponses` is `undefined`. The caption renders the failure-clause-only form (same as the `nParsedResponses === 0` column above). Independent fetches must not couple: failures caption must not be suppressed by a records-side error.

**`nParsedResponses` parameter (CDA SME N5 BINDING):** The parameter is `number | undefined`. It mirrors the surface vocabulary ("parsed primary-step responses") rather than the raw field name (`n_informants`). Undefined means records side is not ready; 0 means records side resolved with no informants.

**Function signature (AC1):**

```ts
export function countsCaptionText(
  nRecords: number,
  nFailure: number,
  nDecline: number,
  nParsedResponses?: number,
): string
```

Parameter order: existing parameters first (no reorder); `nParsedResponses` appended last.

**Render condition in component (AC4):**

```tsx
{(() => {
  const nParsedResponses =
    recordsFetchState.kind === "ready"
      ? recordsFetchState.data.n_informants
      : undefined;
  const captionText = countsCaptionText(
    data.n_records,
    data.n_failure_records,
    data.n_decline_interview_records,
    nParsedResponses,
  );
  return captionText ? (
    <p className="failures-findings__counts">{captionText}</p>
  ) : null;
})()}
```

**No new CSS class (binding):** Reuses `.failures-findings__counts` (existing class from v0.15.0). No new tokens.

**Vitest cases (binding, AC7):**
- Case 27: byte-identity assertion on full three-clause caption under `familyJson` + `recordsFamilyJson` (both non-zero); caption contains "parsed primary-step responses" and does NOT contain "successful" or "successfully".
- Case 28: DOM-presence assertion -- caption `<p>` in DOM when n_records > 0 and n_informants > 0 (same fixtures as case 27).
- Case 29: S-clause-only caption under `foodJson` (n_records === 0) + `recordsFoodJson` (n_informants=45 > 0); caption contains "parsed primary-step responses" and NOT "collection failure" or "follow-up interview".
- Case 30: failure-clause-only caption under `familyJson` + mocked `by_model: []` records (n_informants=0); caption does NOT contain "parsed primary-step responses".
- Case 31: caption `<p>` NOT in DOM under `foodJson` + mocked n_informants=0 records (both zero); asserts via `querySelectorAll('.failures-findings__counts').length === 0`.
- Case 32: failure-clause-only caption when records fetch returns HTTP 404 (records side fetch-failed, nParsedResponses = undefined); caption present and does NOT contain "parsed primary-step responses".
- Case 9 (existing, extended with N6 binding check): chrome-isolation walk affirmatively confirms "parsed primary-step responses" IS present in chrome text AND "successful"/"successfully" is absent.

---

### 19.17 Per-record raw-exchange detail surface (binding, CR-T7, v0.20.2)

The per-record detail surface adds an expand affordance to each row of the §19.15 per-model summary table. Expanding a row lazy-fetches `/data/records/{slug}/{informant_id}.json` and renders the three CDA step exchanges plus a provenance block.

**Navigation pattern (binding NOTE-1):**

The §19.15 per-model summary table gains one new column: an expand column to the right of the five existing data columns. Total column count: 6.

- New `<th>` for the expand column: visually empty, `aria-label="Expand record details"`, class `.failures-findings__successes-th`.
- New `<td>` in each data row: contains one `<button>` per informant row (see expand button spec below). Class `.failures-findings__successes-td`.
- When expanded: a sibling `<tr className="failures-findings__detail-row">` follows the data row. It contains a single `<td className="failures-findings__detail-cell" colSpan={6}>`. When collapsed: `display: none` on the detail row.

Do NOT use `<details>/<summary>` inside `<tr>`. That is invalid HTML structure.

**Expand button spec (binding):**

```tsx
<button
  className="failures-findings__expand-btn"
  aria-expanded={isExpanded}
  aria-label={`Expand raw exchange for ${informantId}`}
  onClick={() => handleToggle(informantId)}
>
  {isExpanded ? '▼' : '▶'}
</button>
```

CSS class `.failures-findings__expand-btn`:
- `background: transparent`
- `border: var(--border-width) solid var(--color-border)`
- `border-radius: var(--border-radius-sm)`
- `padding: var(--space-1) var(--space-2)`
- `cursor: pointer`
- `font-size: var(--font-size-xs)`
- `color: var(--color-text-secondary)`
- `min-height: 44px` (WCAG 2.5.5 touch target floor)
- `min-width: 44px`
- Focus ring: `outline: 2px solid var(--color-info); outline-offset: 2px` on `:focus-visible`

**Detail row CSS (binding):**

CSS class `.failures-findings__detail-row`: no additional styling beyond inherited table row rules. The collapsed state is controlled by `display: none` applied inline or via a CSS class toggle; use whichever pattern is consistent with the component's existing state management.

CSS class `.failures-findings__detail-cell`:
- `padding: var(--space-4)`
- `background: var(--color-surface)`
- `border-bottom: var(--border-width) solid var(--color-border)`

**Lazy-fetch state machine (binding NOTE-4):**

Each row has independent fetch state: `idle | loading | fetch-failed | malformed | ready`. Fetch fires on first expand click only; subsequent opens reuse cached data. One AbortController per row, cancelled in React cleanup.

- `idle`: detail row not yet visible; no fetch initiated.
- `loading`: detail row visible; renders `RECORDS_DETAIL_LOADING` as `<p className="failures-findings__status">`.
- `fetch-failed`: detail row visible; renders `RECORDS_DETAIL_FETCH_FAILED` as `<p className="failures-findings__status">`.
- `malformed`: detail row visible; renders `RECORDS_DETAIL_MALFORMED` as `<p className="failures-findings__status">`.
- `ready`: detail row visible; renders the step exchanges and provenance block.

**Detail body structure (binding):**

Inside `.failures-findings__detail-cell`, when `ready`, content renders in this order:

1. Free-list step section (if `freelist` is non-null in the detail JSON).
2. Pile-sort step section (if `pile_sort` is non-null).
3. Pile-interview step section (if `pile_interview` is non-null).
4. Provenance block (always rendered when state is `ready`).

When a top-level step is null (not present on this informant), that step's entire section is suppressed. Do NOT render an empty section or a "not available" placeholder. Absence is a first-class state (§19.9 posture carried forward).

**Step section structure (binding CDA SME N4):**

Each step section uses a two-level label structure. The outer level names the CDA step (using `BLOCK_FREELIST_EXCHANGE`, `BLOCK_PILESORT_EXCHANGE`, or `BLOCK_PILE_INTERVIEW_EXCHANGE`). The inner level names each verbatim sub-block using the per-step sub-label constants (CDA SME N4, superseding UI/UX NOTE-7): `BLOCK_FREELIST_PROMPT` / `BLOCK_FREELIST_RESPONSE` / `BLOCK_FREELIST_REASONING` (and equivalents for pile-sort and pile-interview). The reasoning sub-block renders only when `thinking_verbatim` is non-empty.

```tsx
<div className="failures-findings__detail-step">
  <p className="failures-findings__detail-step-heading">
    {BLOCK_FREELIST_EXCHANGE}  {/* or PILESORT or PILE_INTERVIEW */}
  </p>
  {/* Prompt sub-block */}
  <p className="failures-findings__block-label">{BLOCK_FREELIST_PROMPT}</p>
  <pre className="failures-findings__pre">{step.prompt_verbatim}</pre>
  {/* Response sub-block */}
  <p className="failures-findings__block-label">{BLOCK_FREELIST_RESPONSE}</p>
  <pre className="failures-findings__pre">{step.response_verbatim}</pre>
  {/* Reasoning sub-block -- only when thinking_verbatim is non-empty */}
  {step.thinking_verbatim && (
    <>
      <p className="failures-findings__block-label">{BLOCK_FREELIST_REASONING}</p>
      <pre className="failures-findings__pre">{step.thinking_verbatim}</pre>
    </>
  )}
</div>
```

CSS class `.failures-findings__detail-step`:
- `display: flex`
- `flex-direction: column`
- `gap: var(--space-2)`
- `margin-bottom: var(--space-6)`

CSS class `.failures-findings__detail-step-heading`:
- `font-size: var(--font-size-sm)`
- `font-weight: var(--font-weight-bold)`
- `color: var(--color-text-primary)`
- `line-height: var(--line-height-tight)`
- `margin-bottom: var(--space-2)`

Reuses `.failures-findings__block-label` (existing) for sub-block labels. Reuses `.failures-findings__pre` (existing, §19.7) for all `<pre>` blocks. No new tokens.

**Pre horizontal overflow (binding NOTE-5):**

`.failures-findings__pre` already has `white-space: pre-wrap` and `word-break: break-word`. These handle horizontal overflow for verbatim text. Do NOT add `overflow-x: auto` to these elements or wrap them in a separate horizontal scroll container. The existing 320px `max-height` with `overflow-y: auto` is the only scroll behavior on `<pre>` blocks.

**Provenance block (binding):**

Below the three step sections, a provenance block renders using the existing pattern from the decline-interview provenance block:

```tsx
<p className="failures-findings__block-label">{BLOCK_DETAIL_PROVENANCE}</p>
<p className="failures-findings__framing-note">{BLOCK_DETAIL_PROVENANCE_NOTE}</p>
<ul className="failures-findings__provenance-list">
  <li className="failures-findings__provenance-item">
    provider_request_id: <code>{provenance.provider_request_id ?? '(none)'}</code>
  </li>
  <li className="failures-findings__provenance-item">
    model_id: <code>{provenance.model_id}</code>
  </li>
  <li className="failures-findings__provenance-item">
    model_version_returned: <code>{provenance.model_version_returned}</code>
  </li>
  {/* One <li> per sha256_manifest key, eight total */}
  {Object.entries(provenance.sha256_manifest).map(([key, val]) => (
    <li key={key} className="failures-findings__provenance-item">
      {key}: <code>{val}</code>
    </li>
  ))}
</ul>
```

Reuses `.failures-findings__block-label`, `.failures-findings__provenance-list`, `.failures-findings__provenance-item`, `.failures-findings__provenance-item code` (all existing from §19). No new CSS classes required for the provenance block.

**CSS summary -- new classes only (all token-only, no new tokens):**

| Class | Rule summary |
|---|---|
| `.failures-findings__detail-row` | No new rules required (inherits table row behavior; collapsed via `display: none` toggle) |
| `.failures-findings__detail-cell` | `padding: var(--space-4)`; `background: var(--color-surface)`; `border-bottom: var(--border-width) solid var(--color-border)` |
| `.failures-findings__expand-btn` | See expand button spec above |
| `.failures-findings__detail-step` | `display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-6)` |
| `.failures-findings__detail-step-heading` | `font-size: var(--font-size-sm); font-weight: var(--font-weight-bold); color: var(--color-text-primary); line-height: var(--line-height-tight); margin-bottom: var(--space-2)` |

All other rendering reuses existing classes. No new tokens introduced.

**No new tokens (binding §19.11 posture):** All CSS rules use only tokens already defined in `tokens.css`. No new `--*` custom properties introduced by this section.

**Accessible landmark:** The detail cell does not require its own `aria-labelledby` because its accessible name is provided by the expand button's `aria-label` (which names the informant_id). The detail row has no separate section landmark.

**Chrome-isolation extension (binding):** Case 9 extension must walk the expanded detail DOM (excluding `<pre>` nodes per §19.13 convention) and confirm zero instances of: `worldview`, `believes`, `thinks`, `understands`, `cooperative` (outside counterfactual context), bare `refusal` in LSB chrome text. The CDA SME N5 affirmative zero-count assertions apply.

**Vitest cases (binding):**
- Case 33: byte-identity on all new SME-bound strings (RECORDS_DETAIL_EXPAND_LABEL, RECORDS_DETAIL_FRAMING, RECORDS_DETAIL_LOADING, RECORDS_DETAIL_FETCH_FAILED, RECORDS_DETAIL_MALFORMED, BLOCK_FREELIST_EXCHANGE, BLOCK_PILESORT_EXCHANGE, BLOCK_PILE_INTERVIEW_EXCHANGE, BLOCK_DETAIL_PROVENANCE).
- Case 34: each row of the per-model summary table contains an expand button with aria-expanded="false" in initial state.
- Case 35: clicking an expand button triggers a fetch to `/data/records/family/{informant_id}.json` (mocked fetch); ready-state DOM contains the three step-heading labels and all eight sha256_manifest keys rendered inside `<code>` elements.
- Case 36: expand loading state renders RECORDS_DETAIL_LOADING byte-identical.
- Case 37: expand fetch-failed state renders RECORDS_DETAIL_FETCH_FAILED byte-identical.
- Case 38: expand malformed state renders RECORDS_DETAIL_MALFORMED byte-identical.
- Case 39: a fixture record with a null step does not render that step section heading or its sub-blocks; other steps are present.
- Case 40: case 9 chrome-isolation extended over the expanded detail DOM (excluding `<pre>` nodes); affirmative zero-count assertions pass for all six forbidden substrings. CR-T8 further extends this case to materialise the attempts block (open `<details>`) and scan attempts chrome for the same forbidden substrings and `\bthink` regex.

---

### 19.18 Per-attempt retry-transcript block (binding, CR-T8, v0.20.3)

Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T8 section); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-10-collection-records-rework-verdicts.md` T8 section).

The retry-attempts block renders inside the expanded body of a `FailureRecord` accordion row (and defensively inside `DeclineInterviewRecord`) when the record's `retry_attempts` field is a non-empty array. If the array is empty, null, or absent, the block does NOT render; this is correct behavior, not a loading state.

**Placement (binding):** The attempts block appears AFTER the originating-context block and BEFORE the `error_message` block inside the failure record body.

**Block structure (binding):**

```
<div class="failures-findings__attempts">
  <div class="failures-findings__block-label">{BLOCK_ATTEMPTS}</div>
  <p class="failures-findings__attempts-framing">{ATTEMPTS_FRAMING}</p>
  {/* one card per attempt, sorted ascending by attempt_index */}
  <div class="failures-findings__attempt">
    <p class="failures-findings__attempt-heading">
      attempt_index: <code>{String(attempt.attempt_index)}</code>
    </p>
    <pre class="failures-findings__pre">{attempt.response_verbatim}</pre>
    {/* optional provenance list: only if stop_reason or parse_error_message non-null */}
    <ul class="failures-findings__provenance-list">
      <li class="failures-findings__provenance-item">
        stop_reason: <code>{attempt.stop_reason}</code>
      </li>
      <li class="failures-findings__provenance-item">
        {ATTEMPTS_PARSE_ERROR_LABEL}: <code>{attempt.parse_error_message}</code>
      </li>
    </ul>
  </div>
</div>
```

**Attempt sort order (binding, CDA SME N1):** Attempts are sorted by `attempt_index` ascending before render. `attempt_index` is 0-indexed for JSON-byte audit alignment; this must not be presented as "attempt 1 of N" framing.

**Register lock on `BLOCK_ATTEMPTS` and `ATTEMPTS_FRAMING` (binding, CDA SME N3):**

- PIPELINE retry language only (no per-record refusal framing)
- Parser-state language only for `parse_error_message` label ("LSB parser-state diagnosis")
- No bare "refusal" in either string
- No "cooperative" or cognition attribution
- Shared-prompt register: the framing confirms the prompt is shared across all attempts and shown once above

**Prompt register lock (binding, CDA SME N2 / AC11):** No per-attempt `prompt_verbatim` is rendered. The parent record's prompt is shown once. The ATTEMPTS_FRAMING string makes this explicit. This is not a UI omission; it is a register decision.

**Token rules (binding, WCAG AA):**

All five new CSS classes use only tokens already defined in `tokens.css` as of v0.20.3. No new tokens were added.

| Class | Key token decisions |
|---|---|
| `.failures-findings__attempts` | `--space-2` gap, `--space-4` bottom margin |
| `.failures-findings__attempts-framing` | `--color-text-secondary` (framing paragraph only; passes 4.5:1 at this font size+weight) |
| `.failures-findings__attempt` | `--color-surface` background, `--color-border` border, `--border-radius-sm` |
| `.failures-findings__attempt-heading` | **`--color-text-primary`** (NOT `--color-text-secondary`; WCAG AA ruling: 14px regular-weight heading must pass 4.5:1; `--color-text-secondary` fails at this size+weight) |
| `.failures-findings__attempt-heading code` | `--color-text-primary` (same as heading, `--font-mono` font family) |

**WCAG AA ruling (UI/UX gate-time, binding):** The attempt heading (`attempt_index: <code>N</code>`) is 14px regular weight. `--color-text-secondary` fails the 4.5:1 contrast requirement at this size+weight. `.failures-findings__attempt-heading` MUST use `--color-text-primary`. The framing paragraph (`.failures-findings__attempts-framing`) is a longer paragraph at small size, and `--color-text-secondary` is acceptable for that role. This distinction is binding and must not be collapsed.

**Test cases (binding, CR-T8 AC16-AC17):**

- Case 41: `BLOCK_ATTEMPTS` byte-identity (approved string: `"Pipeline retry attempts"`).
- Case 42: `ATTEMPTS_FRAMING` byte-identity (approved string per CDA SME N3).
- Case 43: attempts block renders for a fixture failure record with non-empty `retry_attempts` (exactly one `.failures-findings__attempts` in DOM after `<details>` expand).
- Case 44: attempts block absent when `retry_attempts` is `[]`.
- Case 45: attempts block absent when `retry_attempts` is null or the field is omitted.
- Case 46: attempts render in `attempt_index` ascending order when fixture supplies indices out of order.
- Case 40 (extended): case 9 chrome-isolation walk opens `<details>` to materialise the attempts block before the scan; forbidden-substring list and `\bthink` regex both pass on attempts chrome (excluding `<pre>` nodes).

---

### 19.19 Chart-to-record provenance pivot (binding, G7-FOLLOWUP-T1, v0.21.0)

Gate verdicts: CDA SME PASS-WITH-NOTES (`.claude/agent-memory/cda_sme/project_g7_followup_t1_plan_verdict.md`); UI/UX PASS-WITH-NOTES (this update, 2026-06-11).

#### 19.19.1 Purpose and scope

A researcher hovering or selecting a model on the Model Map (MDSPlot tooltip), or viewing a model in Focus 1 (individual-model header), can click an affordance that pivots the app to the Collection records tab, scrolled to and visually highlighting the matching row in the per-model summary table for the current domain. The pivot uses in-app `NavTab` state only. No URL query-state serialization (deferred to a future Permalink task per §3.8).

Two surfaces only this cycle: MDSPlot tooltip and Focus 1 individual-model view header. Term Map, Heatmap, Centrality, Cluster Tree, Free Lists, Pile Structure pivot affordances are deferred.

#### 19.19.2 Copy strings (CDA SME-bound, byte-identical)

All four strings imported from `apps/dashboard/src/copy/failures_findings.ts`. No inline string literals in component files (N7 binding).

| Constant | Type | Value |
|---|---|---|
| `PIVOT_TO_RECORDS_LABEL` | string | `"See the collection records for this model"` |
| `pivotToRecordsAriaLabel(modelLabel, domainLabel)` | function | `"See the collection records for ${modelLabel} on the ${domainLabel} domain"` |
| `pivotToRecordsArrivalCaption(modelLabel, domainLabel)` | function | `"Showing the collection records LSB produced when running the ${domainLabel} protocol with ${modelLabel} as the informant."` |
| `pivotToRecordsNoMatchNotice(modelLabel, domainLabel)` | function | `"The Collection records tab has no successful-run summary for ${modelLabel} on the ${domainLabel} domain. The per-model summary table only lists models that produced a parseable session in this domain."` |

Anti-attribution note (CDA SME G1 binding): the affordance must NOT be visually coupled to a Smith's S / Sutrop CSI / OCI / centrality numeric in a way that implies the per-model summary records explain that numeric. The button copy and aria-label MUST NOT be parameterized on any metric value. No "high-concentration" / "low-concentration" variant; the copy is invariant on R1 state, OCI value, centrality, or any other numeric.

#### 19.19.3 MDSPlot tooltip placement (binding, N5)

The pivot button renders AFTER the `.chart-tooltip__terms` block, preceded by a second `.chart-tooltip__sep` separator. DOM order inside `.chart-tooltip`:

```
.chart-tooltip__name
.chart-tooltip__sub
[R1 state divs if applicable]
[Centrality div if applicable]
[Position div if applicable]
.chart-tooltip__sep    (existing separator before terms)
.chart-tooltip__terms  (existing top terms block)
.chart-tooltip__sep    (NEW second separator)
button.chart-tooltip__pivot-btn  (NEW pivot affordance)
```

Renders only when the `onPivotToRecords` prop is non-null (pointer-enhancement-only; N4 ruling). Does NOT render adjacent to the Centrality numeric or OCI explainer lines (CDA SME G1 anti-coupling rule).

#### 19.19.4 Focus 1 header placement (binding, N5)

The pivot button renders in `Focus1SelfConsistencyOverview.tsx` between the `.f1-hint` paragraph and the `.f1-overview` div. Renders only when `selectedModelId` is non-null AND `onPivotToRecords` prop is non-null. NOT inside any `.f1-model-card`. This is the keyboard-accessible pivot path (N4 keyboard/SR ruling).

#### 19.19.5 App.tsx state wiring (binding, AC1)

`App.tsx` carries a single transient pivot-target state shape `{ modelId: string; domainSlug: DomainSlug } | null`. Default null. `handlePivotToRecords(modelId)` reads `activeDomain`, sets the target, then calls `handleTabChange('collection-records')`. The target is cleared by `FailuresFindings` after the highlight has been applied via the `onPivotTargetConsumed` callback.

#### 19.19.6 FailuresFindings pivot-target consumption (binding, AC2)

`FailuresFindings` accepts optional `pivotTarget: { modelId: string; domainSlug: DomainSlug } | null` and `onPivotTargetConsumed: () => void` props. On a non-null `pivotTarget`:

1. Set internal `domain` state to `pivotTarget.domainSlug` if not already aligned.
2. After the records summary fetch resolves to `ready`, locate the `<tr>` whose `row.model_id === pivotTarget.modelId`.
3. Call `scrollIntoView({ block: 'center', behavior: 'smooth' })` on it.
4. Apply `.failures-findings__successes-tr--pivot-arrival` class for 2000ms; remove after.
5. Render the arrival caption (`.failures-findings__pivot-arrival-caption`) above the highlighted row for the same duration using `pivotToRecordsArrivalCaption(modelLabel, domainLabel)`.
6. Call `onPivotTargetConsumed()` to clear the state.
7. If no matching row exists, render the no-match notice (`.failures-findings__pivot-arrival-notice`) using `pivotToRecordsNoMatchNotice(modelLabel, domainLabel)` for the same duration; then call `onPivotTargetConsumed()`.

Duration: 2000ms (2 seconds). The arrival caption and the no-match notice both render as siblings inside `.failures-findings__successes`, scoped to the triggered event.

#### 19.19.7 CSS classes (binding, pitfall 15 pre-check complete)

All new CSS classes use only tokens already defined in `tokens.css`. No new tokens.

| Class | File | Key token decisions |
|---|---|---|
| `.chart-tooltip__pivot-btn` | `app.css` | Renders inside `.chart-tooltip` (dark-bg variant). `color: var(--color-background)` (white text on dark tooltip bg). `background: transparent`. `border: var(--border-width) solid var(--color-background)`. `border-radius: var(--border-radius-sm)`. `font-size: var(--font-size-xs)`. `padding: var(--space-1) var(--space-2)`. `font-family: var(--font-body)`. `cursor: pointer`. `font-weight: var(--font-weight-regular)`. `line-height: var(--line-height-data)`. `margin-top: var(--space-2)`. `width: 100%`. `text-align: left`. Min touch target 44px enforced by `min-height: 44px` on mobile. |
| `@keyframes pivot-arrival-fade` | `failures-findings.css` | `from { background: var(--color-info); } to { background: transparent; }`. Uses `--color-info` (#3360a9) as the arrival highlight color, fading to transparent over the 2000ms duration via CSS animation. |
| `.failures-findings__successes-tr--pivot-arrival` | `failures-findings.css` | `animation: pivot-arrival-fade 2000ms ease-out forwards`. Applied to the target `<tr>` element. |
| `.failures-findings__pivot-arrival-caption` | `failures-findings.css` | Arrival caption rendered above the highlighted row. `font-size: var(--font-size-sm)`. `color: var(--color-text-primary)`. `line-height: var(--line-height-body)`. `padding: var(--space-2) var(--space-4)`. `max-width: var(--max-prose-width)`. `font-family: var(--font-body)`. `font-weight: var(--font-weight-regular)`. |
| `.failures-findings__pivot-arrival-notice` | `failures-findings.css` | No-match notice. `font-size: var(--font-size-sm)`. `color: var(--color-text-caption)` (NOT `--color-text-secondary`; WCAG AA 4.60:1 correction per N3). `line-height: var(--line-height-body)`. `padding: var(--space-2) var(--space-4)`. `max-width: var(--max-prose-width)`. `font-family: var(--font-body)`. `font-weight: var(--font-weight-regular)`. |

#### 19.19.8 Keyboard and SR interaction (binding, N4)

MDSPlot tooltip affordance is pointer-enhancement-only. The Coder MUST NOT add `tabindex` to SVG circles or a keyboard-tooltip activation mechanism for this cycle. Focus 1 header affordance is the keyboard-accessible path (standard `<button>` semantics, focus ring on focus-visible using `--color-info` outline).

#### 19.19.9 Mobile accessibility (binding)

Mobile layout for the `.failures-findings__successes-tr--pivot-arrival` highlight must work correctly inside the `display: block` mobile scroll layout established by CR-T5. The `.chart-tooltip__pivot-btn` must meet WCAG 2.5.5 minimum 44px touch target (`min-height: 44px` on mobile via media query or always). Focus ring on `.chart-tooltip__pivot-btn:focus-visible`: `outline: 2px solid var(--color-background); outline-offset: 2px`.

#### 19.19.10 Test cases (binding, G7-FOLLOWUP-T1 AC7)

- Case 47: Byte-identity on all four PIVOT_TO_RECORDS_* strings/templates.
- Case 48: `MDSPlot` with `onPivotToRecords` prop non-null renders a `.chart-tooltip__pivot-btn` inside the tooltip DOM (mouse-hover simulation).
- Case 49: Clicking `.chart-tooltip__pivot-btn` fires `onPivotToRecords` with the correct `modelId`.
- Case 50: `FailuresFindings` with `pivotTarget` matching a row in the summary table applies `.failures-findings__successes-tr--pivot-arrival` to that row and calls `onPivotTargetConsumed` after consuming.
- Case 51: `FailuresFindings` with `pivotTarget` matching no row renders `.failures-findings__pivot-arrival-notice` and calls `onPivotTargetConsumed`.
- Case 52: Chrome-isolation walk: MDSPlot tooltip pivot button text and Focus 1 pivot button text both pass zero-count assertions for `worldview`, `believes`, `thinks`, `understands`, `cooperative` (outside counterfactual), bare `refusal`.

Existing MDSPlot test suite byte-untouched (R1-a/R1-b/R1-c markers, ellipse logic, label placement). Existing SimilarityHeatmap R10 CI-crosses-null treatment byte-untouched.

---

## 20. Data Page visual specification (v0.16.0 — Phase 9a task 6, 2026-06-09)

Gate verdicts: CDA SME PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md`); UI/UX PASS-WITH-NOTES (`docs/status/2026-06-08-phase9a-data-tab-ui-ux-verdict.md`).

### 20.1 Layout and container (binding)

`<main aria-label="Data download">` with `.data-page` as the flex child (fills remaining height below NavBar, `overflow-y: auto`). Container `.data-page__container` uses `max-width: var(--max-prose-width)` centered. Bare `<section>` blocks — no card chrome. `.data-page*` rules appended to `app.css`, mirroring `.methodology-page*`.

`<h2>` per section using `font-size: var(--font-size-xl)` + `color: var(--color-text-primary)`. No `<h1>` (NavBar is the landmark).

### 20.2 Section render order (binding, NOT alphabetical)

B (HF Get-the-data) → D (Cite) → A (header/framing) → C (tarball+warning) → E (GitHub) → F (what's-in-bundle) → G (licenses) → H (provenance pointer).

Rationale: B+D first for the 30-second journalist test and researcher reproduce-and-cite flow; A (framing) after the primary CTAs; C-E-F-G-H in usage-logic order.

### 20.3 Header framing block — CDA SME binding

The header section (A) lifts the FULL 3-sentence framing block verbatim from `data/open_bundle/README.md` (beginning "The mismatch is the finding" through "Every domain in v1 is model-to-model. There are no human baselines."). The bare "There are no human baselines." must NOT appear without the "model-to-model" anchor co-located in the same visual block (CLAUDE.md §9 pitfall #4). No new framing prose written by the Coder.

### 20.4 Size-warning callout (binding)

Class `.data-page__note`, `role="note"`. Rendered BEFORE the tarball anchor in reading order.

Token set:
- `background: var(--color-surface-note)` (NEW semantic alias; see §1.2 addendum below)
- `border-left: 4px solid var(--color-warning)`
- `border-radius: var(--border-radius-sm)`
- `padding: var(--space-3) var(--space-4)`
- `font-size: var(--font-size-sm)`
- `color: var(--color-text-primary)` (NOT secondary — secondary fails 4.5:1 on this tint background)
- `line-height: var(--line-height-body)`

Text: "Approx. 1.55 GB. Direct download starts when you click."

### 20.5 Code blocks (binding)

Class `data-page__code-block` applied to both `<pre>` and its child `<code>`. Token set:
- `background: var(--color-surface)`
- `border: var(--border-width) solid var(--color-border)`
- `border-radius: var(--border-radius-sm)`
- `font-family: var(--font-mono)`
- `font-size: var(--font-size-sm)`
- `color: var(--color-text-primary)`
- `overflow-x: auto`
- `white-space: pre`
- `padding: var(--space-3) var(--space-4)`

Copy-button DEFERRED (out of scope per UI/UX verdict).

### 20.6 External-link contract (binding, every external `<a>`)

Every external `<a>` must carry ALL four parts:
1. `target="_blank"`
2. `rel="noopener noreferrer"`
3. Nested `<span className="sr-only">(opens <destination> in new tab)</span>`
4. Self-describing visible text

Exception: B2 tarball anchor sr-only text = "(starts 1.55 GB download in new tab)" (conveys size per WCAG G91).

Precedent: `ProvenanceFooter.tsx:96-101`, `MethodologyPage.tsx:50-58`.

### 20.7 Token addendum — `--color-surface-note` (§1.2)

New semantic alias added to `tokens.css`:

```css
/* Semantic alias for note/callout backgrounds (Data page size warning).
   Same hex as --color-surface (#f8f9fa). Use this alias — NOT --color-surface
   directly — for .data-page__note backgrounds, per UI/UX verdict §20. */
--color-surface-note: #f8f9fa;
```

The `.data-page__note` rule uses `var(--color-surface-note)`, NOT `var(--color-surface)` directly, NOT a hex literal. This creates an explicit semantic link between the note callout concept and its background token, making future theming or contrast adjustments traceable.

### 20.8 Verbatim-source requirement

All prose in `DataPage.tsx` is lifted verbatim from:
- `data/open_bundle/README.md` (header framing block, files table, citation, reproducibility)
- `data/open_bundle/huggingface_dataset_card.md` (bundle-stats sentence, SHA256, HF description)
- `ARCHITECTURE.md` §6.6 (license table and split-licensing rationale)

The Coder writes NO new framing prose. The Reviewer enforces via spot-grep against sources.

### 20.9 No new tokens beyond `--color-surface-note`

Beyond the single new `--color-surface-note` alias, §20 introduces no new CSS custom properties. All other styling uses existing `tokens.css` definitions.

---

## §21 .chart-lede binding token spec (v0.17.0 — Phase 9a T2, 2026-06-09)

### 21.1 Color token (BINDING)

`.chart-lede` MUST use `color: var(--color-text-caption)` (#6c757d, ~4.60:1 on white, WCAG AA compliant). Do NOT use `var(--color-text-secondary)` (#7f8c8d, ~3.40:1, fails AA at 13px regular weight). The WCAG 1.4.3 minimum is 4.5:1 for text below 18px regular weight; `--color-text-caption` clears this at 4.60:1.

### 21.2 Render spec for the Focus-3 lede strip (BINDING)

The Focus-3 lede strip in `ContentArea.tsx` MUST render as:

```tsx
<p className="chart-lede" aria-live="polite">{domain.generated_lede}</p>
```

Rules:
- **Verbatim render.** `domain.generated_lede` is rendered verbatim — no client-side string transformation, no conditional branching on `selectedModelIds`, no inline Smith's S computation.
- **Single continuous paragraph.** The published lede may contain two sentences (the main finding + the R1-b low-output-concentration disclosure). Do NOT split them into separate elements. Do NOT style the R1-b sentence differently. It is a first-class finding, not a footnote.
- **No "Consensus baseline" label.** The published lede self-identifies; the prefixed label is dropped.
- **`aria-live="polite"` kept.** The lede changes on domain switch; screen readers must announce the new content.
- **No inline lede logic.** No component may reconstruct a lede client-side. The lede generator lives in `cdb_publish` (CLAUDE.md §6 rule 11 / ARCHITECTURE.md §4.2 boundary). Any future lede change goes through a `cdb_publish` re-generation, not a component edit.

### 21.3 "--" clause separator note

The published `generated_lede` contains "--" (double-hyphen ASCII) as a clause separator, e.g. "their position on the map is shown without a confidence ellipse -- signaling that the runs did not converge". This is NOT a Unicode em dash (U+2014) and does NOT violate the no-em-dash rule. It is approved published copy. Any change to "--" separators in the published lede requires a `lede_v2.py` template update in `cdb_publish` (per CLAUDE.md §6 rule 7 prompt-template versioning) and is out of scope for T2. Render verbatim.

### 21.4 Scope boundary

This section governs ONLY the Focus-3 lede strip (`ContentArea.tsx` around the `!isFocus1 && !isFocus2 && domain` block). The Focus-1 and Focus-2 lede strips (ContentArea.tsx:114, 119 loading/error `<div className="chart-lede">` elements) are out of scope for §21.

---

## 22. About page (v0.19.0, M2, 2026-06-10)

`AboutPage.tsx` is a static long-form article for the fifth NavBar tab. It renders Mark-authored text verbatim. No interactive elements, no data fetching, no new CSS.

Gate verdicts: CDA SME PASS-WITH-NOTES; UI/UX PASS-WITH-NOTES (both: `docs/status/2026-06-10-site-copy-verdicts.md` M2 section).

### 22.1 Purpose and positioning (binding)

The About page is a demonstration piece: it establishes authorship, perspective, and professional context for the benchmark. It is NOT a portfolio page, services page, consulting offering, or contact page.

**NavBar positioning constraint (binding).** "About" is the rightmost (fifth) tab. It uses the same `.nav__tab` class as every other tab: no bolding, no badging, no color accent, no visual distinction. The benchmark and data presentation remain primary; the About entry is present but must not dominate the nav. Any future Coder who wants to visually distinguish the About tab must route to UI/UX before adding any class-name divergence.

**No sales or contact affordances (binding).** The page must not contain: a "hire me" CTA, a "Contact" section or link, a "Services" or "Consulting" heading, a contact form, a `mailto:` link, a LinkedIn or social link, a list of testimonials, a "Recent clients" or "Selected work" section, a portrait or photo, a CV download link, or any sales or availability language. These constraints match the content of the Mark-authored source text; nothing analogous should be invented. If a future need for any of these surfaces, route to a new plan cycle through the Architect.

### 22.2 Class reuse pattern (binding)

`AboutPage.tsx` deliberately shares the `.methodology-page*` class structure with `MethodologyPage.tsx`. This is intentional: the About prose typographic posture should be identical to the Methodology page. There is NO `.about-page__*` parallel class tree. Introducing a new `.about-page__*` class is a stop condition: pause and route to UI/UX.

Classes used (verbatim, same as `MethodologyPage.tsx`):
- `.methodology-page`: `<main>` wrapper
- `.methodology-page__container`: inner container
- `.methodology-page__section`: `<section>` wrapper
- `.methodology-page__heading`: `<h2>` heading
- `.methodology-page__text`: `<p>` body paragraphs

No new tokens, no new CSS files.

### 22.3 Section structure (binding)

Single `<section>` containing:
- `<main className="methodology-page" aria-label="About">` outer wrapper
- `<div className="methodology-page__container">` inner container
- One `<section className="methodology-page__section" aria-labelledby="about-mark-dawson-heading">`
- `<h2 id="about-mark-dawson-heading" className="methodology-page__heading">About Mark Dawson</h2>` (heading-case normalized from the source markdown h1; h2 matches MethodologyPage section heading pattern)
- Eight `<p className="methodology-page__text">` elements, one per source paragraph, in source order, verbatim

### 22.4 Cite-to-disclaim handling (binding, CDA SME M2-N1)

The Mark-authored source text contains TWO protected cite-to-disclaim occurrences. The header comment block in `AboutPage.tsx` must enumerate BOTH (CDA SME M2-N1 BINDING; original Architect plan §3.1 described only one):

- **Occurrence 1 (paragraph 2):** "I use culture in that broad sense: not just nationality or tradition, but the patterned ways people classify, interpret, value, and act." This is Mark defining the broad anthropological sense of `culture` as a human practice, NOT attributing culture to a model. Register-clean (CDA SME M2 verdict). Parallel to `MethodologyPage.tsx` Section 6 scare-quoted repudiation pattern.

- **Occurrence 2 (paragraph 6):** "The benchmark does not claim that models have beliefs, intentions, lived experience, or culture in the human sense." This is the canonical §1.5 cite-to-disclaim move: the disclaimer sentence explicitly repudiates cognition attribution and must not be flagged by the Reviewer's forbidden-vocab grep. Parallel to `MethodologyPage.tsx` Section 3 "not because they have beliefs or lived experience" cite-to-disclaim.

The Reviewer's forbidden-vocab sweep treats both occurrences as protected by the header comment. Pattern mirrors `MethodologyPage.tsx` lines 134-141 and 217-223. The disclaim text is the section's substance, not a violation.

### 22.5 What this page is not (negative spec, binding)

This list is a mirror of §22.1. It is repeated here for explicitness when a Coder is reading §22 in isolation:

- No contact form
- No `mailto:` link
- No portfolio listings ("Recent clients," "Selected work," etc.)
- No consulting or services language
- No photo or portrait
- No "hire me" or availability CTA
- No LinkedIn, social media, or external profile links
- No CV download link

The test suite (`AboutPage.test.tsx`) enforces several of these mechanically (cases 6 and 7). The Reviewer enforces the remainder on inspection.

---

## 23. Consensus override badge, CI-disclosure line, and heatmap exclusion caption (v0.23.0 -- PROMOTE-FOOD-V02, 2026-06-11)

Gate verdicts: CDA SME PASS-WITH-NOTES (`.claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md` round 3); UI/UX PASS-WITH-NOTES (this update, 2026-06-11).

This section specifies three new visual patterns introduced by the food v0.2 promotion (PROMOTE-FOOD-V02). All three patterns render in `ContentArea.tsx` or its immediate child `SimilarityHeatmap.tsx`. No new tokens are introduced; all styling uses tokens confirmed present in `tokens.css`.

### 23.1 Consensus-type override badge (binding)

**When to render:** the override badge renders whenever `domain.consensus_type_override` is a non-null, non-empty string that differs from `domain.consensus_type`. In v1 this means: food domain at v0.2 where `consensus_type_override = 'WEAK_CONSENSUS'` and auto-derived `consensus_type = 'STRONG_CONSENSUS'`.

**Placement (binding):** the override badge renders in `ContentArea.tsx` co-located with the existing consensus-type display surface (wherever `domain.consensus_type` or `domain.consensus_type_override ?? domain.consensus_type` is shown to the user). It MUST appear on the same visual line as or immediately below the classification label. It MUST NOT be placed in a separate section, footnote, or tooltip-only surface. Visible without user interaction (U1 binding).

**CSS class (binding):** `.content-area__override-badge`

**Element structure (binding):**
```tsx
<span className="content-area__override-badge" aria-label={`Classification override: ${domain.consensus_type_override}`}>
  {domain.consensus_type_override ?? domain.consensus_type}
</span>
```

The `aria-label` uses the plain string 'Classification override: WEAK_CONSENSUS' -- no jargon, no schema identifiers in the primary label.

**CSS spec (binding, no new tokens):**
```css
.content-area__override-badge {
  display: inline-block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-left: 3px solid var(--color-warning);
  border-radius: var(--border-radius-sm);
  padding: var(--space-1) var(--space-2);
  line-height: var(--line-height-data);
}
```

**WCAG AA ruling (binding):**
- Badge text uses `--color-text-primary` (#2c3e50) on `--color-surface` (#f8f9fa): contrast 12.34:1, WCAG AA PASS.
- Left accent border `--color-warning` (#f39c12) on `--color-surface` (#f8f9fa): 2.73:1 -- below WCAG 1.4.11 3:1 standalone threshold. Acceptable because: (a) the accent is a decorative reinforcement of the text label, not the sole information carrier; (b) the badge text 'WEAK_CONSENSUS' is the primary signal; (c) the aria-label provides the classification without color dependency. No information is conveyed by the warning color alone.
- The badge does NOT use a background color change to signal the override. Background is always `--color-surface`. Shape discrimination (left-accent border) plus text are the dual signals.

**Methodology page link (U3 binding):** the badge must carry a sibling `<a>` element (one click from the badge, per U3) that navigates to the methodology page footnote section for food. Exact affordance: an `<a>` element with `href="/methodology#food-v02-footnote"` rendered immediately after the badge in the DOM. The anchor text is 'See methodology note' at `--font-size-xs`, `--color-text-caption`. The anchor carries `aria-label="See methodology footnote for food v0.2 classification"`. No `target="_blank"` (in-app SPA route per §6.3 ruling).

**Food methodology footnote anchor target (binding):** `MethodologyPage.tsx` must add `id="food-v02-footnote"` to the `<p>` element that renders F3-R3-E. The heading for the food footnotes section (FOOD-FIX-A + F3-R3-E together) should carry `id="food-methodology-footnotes"` as an alternative deep-link target. Either id satisfies U3.

**Pitfall 15 token pre-check (confirmed):** `--font-size-sm`, `--font-weight-medium`, `--color-text-primary`, `--color-surface`, `--color-border`, `--color-warning`, `--border-radius-sm`, `--border-width`, `--space-1`, `--space-2`, `--line-height-data`. All confirmed in `tokens.css`. No new tokens.

### 23.2 CI-disclosure line and small-n line (binding)

**When to render:**
- CI-disclosure line: whenever `domain.consensus_type_override` is set. Renders adjacent to the override badge, visible without interaction (U1).
- Small-n line: whenever `domain.romney_small_n_warning === true`. Renders below the CI-disclosure line when both are present.

**Placement (binding):** both lines render in `ContentArea.tsx` immediately below the override badge in the classification cluster. They are NOT inside the badge element. They are NOT in a tooltip. They render as sibling block elements in the same visual grouping as the badge.

**CSS classes (binding):**
- `.content-area__ci-disclosure` -- for the CI-disclosure line
- `.content-area__small-n-line` -- for the small-n line

**Byte-identical display strings (binding, CDA SME F3-R3-C and F3-R3-D verbatim):**
- `CI_DISCLOSURE_TEXT` (F3-R3-C): 'Romney CCM eigenratio 9.48, 95 percent bootstrap interval [4.91, 10.34], B=500. The interval crosses the 5.0 strong/weak threshold.'
- `SMALL_N_TEXT` (F3-R3-D): 'The slate is 12 models, below the 15-model floor where Romney CCM eigenratios become statistically reliable. Read the classification with that floor in mind.'

Both strings are exported from a dedicated copy module: `apps/dashboard/src/copy/consensus_disclosure.ts`.

**Implementation note on numeric sourcing (SME P1 / STOP-#5 resolution):** the eigenratio value '9.48' and the CI bracket '[4.91, 10.34]' in CI_DISCLOSURE_TEXT are CONSTANTS in the copy module, not computed from `domain.consensus_ci` at runtime. There is no `romney_eigenratio_ci` field in the schema. These numbers are inline constants that match the SME-bound F3-R3-C string byte-for-byte. The `consensus_ci` field on `DomainResultPublished` carries the CI on the consensus *score* (different quantity). Any attempt to derive the eigenratio CI from `consensus_ci` is INCORRECT and is a stop condition that routes back to the CDA SME.

**CSS spec (binding, no new tokens):**
```css
.content-area__ci-disclosure {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-regular);
  color: var(--color-text-caption);
  line-height: var(--line-height-body);
  margin-top: var(--space-1);
  margin-bottom: 0;
  max-width: var(--max-prose-width);
}

.content-area__small-n-line {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-regular);
  color: var(--color-text-caption);
  line-height: var(--line-height-body);
  margin-top: var(--space-1);
  margin-bottom: 0;
  max-width: var(--max-prose-width);
}
```

**WCAG AA ruling (binding):**
- Both lines use `--color-text-caption` (#6c757d, 4.60:1 on white, WCAG AA PASS at 12px regular weight per §1.2 annotation). PASS.

**Pitfall 15 token pre-check (confirmed):** `--font-size-xs`, `--font-weight-regular`, `--color-text-caption`, `--line-height-body`, `--space-1`, `--max-prose-width`. All confirmed present. No new tokens.

### 23.3 SimilarityHeatmap model-exclusion caption (binding)

**When to render:** whenever the current domain's similarity heatmap excludes one or more models that are in the `domain.models` array but absent from the similarity matrix. For food v0.2, this is `meta-llama/llama-4-maverick`. The component determines excluded models by computing the set difference between `domain.models.map(m => m.model_id)` and the model_ids that appear in `domain.mds_coordinates` (the mode-coherent model set).

**Placement (binding):** the exclusion caption renders as a `<p>` element IMMEDIATELY BELOW the similarity heatmap chart container, inside `ContentArea.tsx` (NOT inside `SimilarityHeatmap.tsx`). It renders at the same DOM level as the existing `chart-wrap__desc` paragraph (the CI caption from §12.8). The exclusion caption is a SECOND caption paragraph, after the CI caption. It does not replace or modify the §12.8 CI caption.

**CSS class (binding):** `.heatmap-exclusion-caption`

**Visible text pattern (binding):** The visible text names the excluded model using `displayModel()` (§18.4 canonical transform) and gives the reason.

For food v0.2 the rendered visible text is (binding, must match this exactly for food):
'llama-4-maverick is not shown in the similarity matrix because it has no single-pass collection records for this domain.'

General pattern for future domains (non-binding template):
'[displayModel(model_id)] is not shown in the similarity matrix because [reason].'

When multiple models are excluded, one sentence per model, rendered as separate `<p>` elements each with `.heatmap-exclusion-caption` class (not a comma-joined list).

**aria-label on the caption `<p>` (binding, U6):**
```tsx
<p
  className="heatmap-exclusion-caption"
  aria-label={`Similarity matrix exclusion: ${model_id} is not shown because it has no single-pass collection records for this domain.`}
>
  {visibleText}
</p>
```

The aria-label uses the FULL `model_id` ('meta-llama/llama-4-maverick'), not the displayModel() form, per §18.5 SimilarityHeatmap ruling (full model_id in aria-labels for cell-level SR navigation context). The visible text uses displayModel().

**CSS spec (binding, no new tokens):**
```css
.heatmap-exclusion-caption {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-regular);
  color: var(--color-text-caption);
  line-height: var(--line-height-data);
  margin-top: var(--space-2);
  max-width: var(--max-chart-width);
}
```

**WCAG AA ruling (binding):**
- `--color-text-caption` (#6c757d, 4.60:1 on white, WCAG AA PASS at 12px regular weight). PASS.

**Pitfall 15 token pre-check (confirmed):** `--font-size-xs`, `--font-weight-regular`, `--color-text-caption`, `--line-height-data`, `--space-2`, `--max-chart-width`. All confirmed present. No new tokens.

**T3 vitest test binding:** the test asserts that for a food-domain fixture with `meta-llama/llama-4-maverick` absent from the similarity matrix, a `.heatmap-exclusion-caption` element renders with visible text containing 'llama-4-maverick' (displayModel form) and an aria-label containing 'meta-llama/llama-4-maverick' (full model_id form).

---

*End of DESIGN_SYSTEM.md v0.23.0. This document is a living specification. Update it before building any new component that requires a visual decision not covered here.*

*Binding rule: no visual decision is made by the Coder agent alone. If DESIGN_SYSTEM.md does not cover a case, the UI/UX agent resolves it before the Coder proceeds.*
