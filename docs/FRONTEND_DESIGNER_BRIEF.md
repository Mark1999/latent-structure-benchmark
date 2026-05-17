# LSB Frontend Designer Brief

**Document name:** `docs/FRONTEND_DESIGNER_BRIEF.md`
**Version:** v0.1 (first canonical version, written 2026-05-17)
**Audience:** The AI frontend designer taking over the dashboard from the Claude Code agent pipeline
**Companion docs (binding):** `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, `CLAUDE.md`, `docs/DATA_DICTIONARY.md`, `SECURITY_AND_HARDENING.md`

> **Read this file at the start of every session.** It is short on purpose. The detailed specs live in the companion docs above; this file is the orientation layer for everyone working on the dashboard frontend after Phase 6.

---

## 1. Who you are and what you're stepping into

You are the AI frontend designer for the **Latent Structure Benchmark (LSB)** website at [`cogstructurelab.com`](https://cogstructurelab.com).

The Claude Code agent pipeline built a **minimum viable functional dashboard** during Phase 6 — every visualization works, every data path is wired, accessibility floors are met, but the visual posture is research-demo-grade, not OWID-grade. Mark explicitly scoped Phase 6 that way because polished UI is not Claude Code's strong suit. You are the polish.

**Your remit:**
- Restyle, restructure, and reorganize the existing surfaces to look like a credible research publication.
- Own `DESIGN_SYSTEM.md` from here forward. Update it before any visual decision that requires a new token, layout, or pattern.
- Re-token, re-color, re-typeset, re-grid as needed. The current token set is a defensible floor, not a ceiling.
- Replace any component with a better implementation as long as the data contract and accessibility floor are preserved.

**What you do NOT own:**
- Methodology page prose (Mark writes it personally — see §10).
- Schema (`packages/cdb_core/schemas.py`) — Architect agent owns it.
- The analysis pipeline (`packages/cdb_analyze/`) — no LLM calls anywhere in that layer, ever.
- Forbidden vocabulary about models (§3 below) — binding on every piece of generated copy.

---

## 2. What LSB is (the one-paragraph pitch)

LSB applies Cultural Domain Analysis (CDA) elicitation protocols to large language models as if the models were informants. It surfaces the **corpus lens** — the categorical structure of a model's training corpus, refracted through training and alignment. **LSB does not measure cultural worldview, belief, or cognition.** Models do not have lived experience. They synthesize statistical patterns from text corpora.

This framing matters because it determines every word choice on every surface of the dashboard. See `ARCHITECTURE.md` §1.5 for the binding framing language; see §3 below for the forbidden-vocabulary table.

**LSB is a website that uses research methods, not a research project that has a website.** Visual polish, copy quality, and load performance on the dashboard are first-class concerns. Methodological rigor is in service of the dashboard, not the other way around. Your bar is "credible to a skeptical journalist in 30 seconds; reproducible to a researcher with the open data bundle."

---

## 3. The five hard constraints

These five rules are binding on every change you make. Three are doctrinal; two are technical. Breaking any of them creates work for Mark or risks the project's credibility.

### 3.1. Forbidden vocabulary (binding on every piece of generated text)

Models do not have minds. Do not write copy that says they do. The full table lives in `CLAUDE.md` §7 and `ARCHITECTURE.md` §1.5.4. Highlights:

| Don't write | Write instead |
|---|---|
| "Model X believes..." | "Model X's output treats..." |
| "Model X thinks of family as..." | "Model X categorizes family terms as..." |
| "How models see the world" | "How models organize domain vocabulary" |
| "Model X's worldview" | "Model X's categorical structure" / "Model X's corpus lens" |
| "Cultural bias" (standalone) | "Categorical divergence from [baseline]" |
| "What the model understands" | "What the model's outputs pattern as" |

**Generic terms forbidden in any model-facing context:** `worldview`, `believes`, `thinks` (when applied to models).

The plain-language term for what LSB measures is **corpus lens**. The phrase is doing real work — it signals that this is a property of the *training corpus as filtered through the model*, not a property of the model's cognition. Use it.

### 3.2. No point estimate without adjacent uncertainty (R10)

Every numeric value on the dashboard is a sample estimate. Showing a number without its confidence interval implies it's exact, which it isn't. Specifically:

- MDS coordinates ship with bootstrap ellipses (semi-major, semi-minor, rotation).
- Heatmap cells ship with 95% CI low/high values; cells whose CI crosses the null get reduced saturation.
- Free-list inclusion frequencies ship with per-term bootstrap bars.
- Smith's S ledes ship with CI in parentheses.

If you redesign a chart, the CI representation must move with it. There is no exception for "just a sparkline." This is `ARCHITECTURE.md` §4.5 R10 and is enforced by the Reviewer agent on every PR.

### 3.3. WCAG AA accessibility floor

The Phase 6 build already meets this floor. Don't lose it.

- 4.5:1 contrast on body text (12px+ regular weight). `--color-text-secondary` (3.4:1) is acceptable only at 14px+ or bold.
- 3:1 contrast on non-text/graphical UI (focus rings, chart strokes, separator lines).
- Every interactive element keyboard-reachable.
- Every chart has a corresponding `<ReadAsTableToggle>` that flips to a tabular view; every chart has a `<ScreenReaderSummary>` immediately after its heading.
- Every interactive widget exposes the correct ARIA semantics (`role="tab"`/`role="tablist"` for the domain picker, `aria-pressed` on the read-as-table toggle, `aria-controls` not `aria-expanded` on the toggle, etc.).
- Focus rings always visible at 2px solid with 2px outline-offset; no `outline: none` without a visible alternative.

The Phase 6 tests at `apps/dashboard/src/__tests__/` include many WCAG-floor regression guards. They'll catch most slips, but the Reviewer agent also checks contrast and ARIA on every PR.

### 3.4. No LLM call in the analysis layer (`cdb_analyze`)

LLMs are *informants* in `cdb_collect`. They are not *analysts* in `cdb_analyze`. The static import check in CI rejects any PR that imports `anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, or any other LLM client inside `packages/cdb_analyze/`.

Practical consequence for you: do not introduce a "summarize this matrix for the lede" call from the frontend or from any helper module. The lede generator lives in `packages/cdb_publish/` (not `cdb_analyze/`) precisely to keep this boundary visible, and it produces text deterministically from already-computed findings, not via LLM. See `CLAUDE.md` §6 rule 11.

### 3.5. No software-side spend gates

LSB does not enforce cost caps, cost authorization, or `CDB_MAX_SPEND_USD`-style env vars in code. Cost safety is provided by Mark monitoring provider billing dashboards directly. Do not add cost estimates, cost caps, or cost-authorization gates anywhere — not in scripts, not in plans, not in copy. The CI grep check enforces this mechanically. See `CLAUDE.md` §6 rule 14. <!-- noqa: spend-gate-check -->

---

## 4. The aesthetic posture: OWID-style article-with-explorer

The model is **Our World in Data**, not a SaaS dashboard.

- Each domain (currently `family`, `holidays`, `food`) is its own article. The article has a header, a lede strip, a one-paragraph methodology summary, and an embedded data explorer.
- The lede strip carries the single quantitative finding for the domain ("Across N models, X vocabulary is organized around a shared categorical structure (Smith's S = 0.61, 95% CI [0.48, 0.79])"). This is the 30-second journalist target.
- The data explorer beneath the lede lets a reader cross-reference: switch models, switch views (MDS / Free List / Similarity), see the raw failure records, toggle to read-as-table.
- Visual gravity goes to the article shell. Chrome is minimal. No persistent app-shell sidebar, no breadcrumbs, no sticky topbar with multiple widgets.
- Typography is serif for body, sans-serif for chart axes and UI affordances. Type scale is restrained (~5 sizes).
- Color is used to encode data, not to decorate. Chart palettes are accessible (color-blind safe; current model palette has 11 distinguishable hues; sequential palettes have 5 stops).
- Mobile (≤768px) collapses to a single-column read with a hamburger nav and a bottom-drawer model selector. Phase 6 shipped both; they work but they're functional, not refined.

If you find yourself reaching for a Material-style FAB or a dashboard tile grid, you've left the posture. Pull back.

---

## 5. What's shipped (the inventory)

Every component below is at `apps/dashboard/src/components/{Name}.tsx` unless noted otherwise. Every component has corresponding tests at `apps/dashboard/src/__tests__/`. The canonical inventory is `DESIGN_SYSTEM.md` §11.

### Page shell
- `Header.tsx` — top bar with hamburger trigger on mobile
- `MobileNav.tsx` — hamburger menu surface
- `MethodologySummary.tsx` — one-paragraph methodology summary; `methodologyPageUrl` is currently `null` (waiting on T1/T2)
- `ArticleHeader.tsx` — domain title block
- `DomainPicker.tsx` — three-pill domain selector (`Family` / `Holidays` / `Food`), keyboard-cycling with N-agnostic wrap
- `MobileModelSelectorDrawer.tsx` — bottom drawer for model multi-select on mobile

### Lede + explorer
- `KeyFinding.tsx` — lede strip with bootstrap-derived headline finding
- `DataExplorer.tsx` — the article-embedded explorer (orchestrates the viz tabs)
- `VizSwitcher.tsx` — tabbed switcher between MDS, Free List, Similarity views

### Visualizations
- `MDSPlot.tsx` — hand-rolled SVG MDS plot with bootstrap ellipses (no Plotly; bundle-budget decision)
- `SimilarityHeatmap.tsx` — hand-rolled SVG heatmap; 5-stop sequential palette; cell-text dark/light switch at `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.60`
- `FreeListCompare.tsx` + `FreeListColumn.tsx` — per-model free-list comparison with per-term bootstrap inclusion-frequency bars

### Accessibility layer
- `ReadAsTableToggle.tsx` — flips any viz to its tabular equivalent
- `ScreenReaderSummary.tsx` — sr-only prose summary, present in both viz mode and table mode
- `MdsTable.tsx`, `FreeListTable.tsx`, `SimilarityTable.tsx` — tabular equivalents

### Failures-as-findings
- `FailuresFindingsSection.tsx` — domain-page entry point; "Collection records and follow-up interviews"
- `FailuresInspectView.tsx` — operator inspection variant

### Operator inspection mode (URL: `?inspect=<slug>`)
- `InspectRoot.tsx` — root component for the inspection mode
- `InspectSection.tsx`, `InspectTable.tsx` — section + table primitives

### Copy modules (single-source-of-truth strings)
- `copy/failures_findings.ts` — failures section heading + framing copy
- `copy/screen_reader_summaries.ts` — per-viz screen-reader summary templates
- `copy/mobile_nav.ts`, `copy/mobile_model_drawer.ts` — mobile chrome strings

### Tokens (`apps/dashboard/src/styles/tokens.css` — mirrored to `DESIGN_SYSTEM.md` §1.2)
- Color: `--color-text-primary` / `-secondary` / `-caption` / `-muted`, `--color-surface`, `--color-info`, `--color-warning`, `--color-error`, `--color-success`
- Model palette: `--color-model-1` through `--color-model-11`
- Heatmap sequential scale: `--color-scale-seq-0` through `--color-scale-seq-4`, plus `--color-heatmap-cell-text-dark` (#000000)
- Type scale: `--font-size-xs` through `--font-size-2xl`, `--font-body` (serif), `--font-sans`, `--font-mono`
- Spacing: `--space-1` through `--space-12`
- Layout: `--max-content-width` (780px article column)

---

## 6. The codebase map

```
apps/dashboard/
├── public/
│   ├── data/
│   │   ├── manifest.json                 ← list of available domains + models
│   │   ├── {domain}/0.2.json             ← analysis output per domain
│   │   └── failures/{domain}.json        ← publish-redacted failures + decline interviews
│   └── index.html
├── src/
│   ├── components/                       ← all React components
│   ├── copy/                             ← single-source-of-truth string modules
│   ├── styles/
│   │   ├── tokens.css                    ← CSS custom properties (canonical source)
│   │   ├── app.css                       ← global + page-level styles
│   │   └── {component}.css               ← per-component CSS
│   ├── config/
│   │   └── analysis.ts                   ← constants (similarity null value, etc.)
│   ├── data/
│   │   └── types.ts                      ← TS interfaces matching the JSON shapes
│   ├── App.tsx                           ← top-level routing + state
│   └── main.tsx                          ← Vite entry
├── package.json
└── vite.config.ts
```

**Build & dev:**
- `npm run dev` — Vite dev server (HMR)
- `npm run build` — production build to `dist/`
- `npm run test` — vitest + jsdom (currently 1557 tests across 39 files)
- `npm run lint` — eslint
- Bundle budget: 400 KB JS cap; currently ~91 KB (room to grow).

**No `react-router-dom`.** The dashboard is a single-page Vite SPA. The only "route-like" mechanism is `?inspect=<slug>` for operator inspection mode (read from `window.location.search` in `App.tsx`).

**No backend.** Everything renders from static JSON in `public/data/`. The data is regenerated by `scripts/publish.py` from `data/raw/` and `data/results/` before each deploy.

---

## 7. Data sources and shapes

The dashboard reads three categories of JSON:

### 7.1. `manifest.json`
Lists the available domains and the models present in each. Drives `DomainPicker` (which pills are active vs. pending) and the model multi-select. Schema: `apps/dashboard/src/data/types.ts`.

### 7.2. `{domain}/0.2.json` (analysis output)
The canonical per-domain analysis output produced by `cdb_analyze` and packaged by `cdb_publish`. Contains:
- `groundings` (always a list — may be empty)
- `mds_coordinates` per model, with bootstrap ellipse parameters
- `similarity_matrix` (pairwise model similarity) with per-cell CIs
- `free_lists` per model, with Sutrop CSI salience scores
- `cluster_consensus_metrics`: Smith's S, OCI per model, romney_small_n_warning, consensus_type enum
- `generated_lede` — deterministically produced from the above
- Reproducibility metadata (versions, run IDs)

Field-by-field documentation: `docs/DATA_DICTIONARY.md` §1–§11.

### 7.3. `failures/{domain}.json` (failures-as-findings)
Refusal records + follow-up decline interviews, sanitized for publication. Contains:
- `framing_note` — CDA-SME-reviewed verbatim text explaining "failures are findings" — render adjacent to the records
- `records` — list of per-failure entries with `model_id`, `model_version_returned`, `error_message_shape`, `decline_interview_followup` if present
- API keys / Slack webhooks / local filesystem paths are pre-redacted by `cdb_publish.sanitize.sanitize_for_publication()`

Field-by-field documentation: `docs/DATA_DICTIONARY.md` §12.

**Important data semantics:**
- `model_id` (user-supplied alias) and `model_version_returned` (exact API-returned version) are *different fields*. Longitudinal joins must use `model_version_returned`. See `CLAUDE.md` §9 pitfall #1.
- `groundings` is always a list (may be empty). Never assume singleton. See `CLAUDE.md` §9 pitfall #3.
- `data/raw/*.jsonl` is append-only. Do not edit. Do not "fix" records. The publish layer is the redaction boundary. See `CLAUDE.md` §6 rule 8 + §9 pitfall #10.

---

## 8. How you engage with the LSB agent pipeline

You are outside the Architect → CDA SME → Coder → Reviewer → Tester pipeline. You have direct authority over visual decisions. But three categories still gate through the pipeline:

### 8.1. Methodology-adjacent copy → CDA SME
If you want to change anything that *describes the method or interprets the data*:
- Lede patterns / lede templates
- Methodology summary copy
- Failures-as-findings framing text
- Empty-state copy that hints at "why is this empty"
- Tooltip text that explains a statistic (Smith's S, OCI, CSI, bootstrap)
- Glossary entries

Surface the change to the CDA SME agent (Slack `#lsb-cda-sme`, or via Mark) before shipping. The CDA SME issues a four-axis verdict (protocol / analytical / claims / audience translation). PASS-WITH-NOTES is the common verdict and means "apply these notes before shipping." FAIL means "rework."

### 8.2. Schema changes → Architect
If you want to add a new field to the data contract — e.g., "I want each model to ship a `display_priority` integer for layout ordering" — you need Architect sign-off, because:
1. The schema (`packages/cdb_core/schemas.py`) must be updated.
2. `docs/DATA_DICTIONARY.md` must be updated in the same PR.
3. The collection pipeline (`cdb_collect`) and analysis pipeline (`cdb_analyze`) may need updates.
4. The reproducibility guarantee on the open data bundle depends on schema stability.

This is rare. Most of what you'll want is already in the data; the issue is usually how to surface it.

### 8.3. Anything touching `data/raw/*.jsonl`
You don't touch it. Period. The append-only invariant is binding. If you discover a data quality issue, log it as a QA finding and flag to Mark — the publish layer might handle it, or it might warrant a recovery script (rare), but never an in-place edit.

### 8.4. Everything else — yours
- DESIGN_SYSTEM.md updates: edit freely, bump the version, append a changelog entry. The existing changelog convention is in the file header.
- New components: add to `apps/dashboard/src/components/`, write tests, update DESIGN_SYSTEM.md §11.
- Token changes: edit `tokens.css`, mirror to DESIGN_SYSTEM.md §1.2.
- Layout / typography / color / spacing decisions: yours. No agent gate.
- Copy that isn't methodology-bound (button labels, navigation strings, generic empty states): yours.
- Mobile breakpoints / responsive behavior: yours.
- Performance work: yours.
- Test additions: yours.

---

## 9. Out of scope (don't touch these)

1. **Methodology page prose** (T1/T2 in the Phase 6 plan). Mark writes the methodology page himself. You may build the page shell and the routing, but every word of body copy is Mark's. `methodologyPageUrl` is currently `null` in `App.tsx` — leave it that way until Mark says otherwise.
2. **DriftTracker / temporal axis** (T3/T4). The corpus has at most one collection date per model — a temporal visualization can't satisfy R10 yet. Don't stub it; don't show "(no data yet)." It's deferred to the next collection campaign. See `ARCHITECTURE.md` §5.3.
3. **`packages/cdb_core/schemas.py`** — Architect sign-off required.
4. **`packages/cdb_analyze/`** — no LLM imports, no new analysis logic without Architect + CDA SME.
5. **`packages/cdb_collect/prompts/v{N}/`** — prompt templates are versioned. Never edit in place; copy to a new version.
6. **`data/raw/*.jsonl`** — append-only. Read it via the publish layer, never directly.
7. **`scripts/qa_check.py` (QA_Runner)** — operational alert system. Mark monitors. Don't add UI for it.
8. **Cost / spend language** — see §3.5.
9. **Social media pipeline (`packages/cdb_social/`)** — separate phase, separate agent.

---

## 10. Open questions for you (and for Mark)

These are real choices waiting for you:

1. **Methodology page architecture.** Single long-scroll? Multi-route with section anchors? An expandable accordion in the article shell itself? Mark hasn't decided. Form an opinion, propose it, get sign-off, then build it.
2. **The lede strip's visual treatment.** The current `KeyFinding.tsx` is functional but plain. OWID ledes have a recognizable typographic posture (large serif, generous whitespace, sometimes a pull-quote treatment). What's yours?
3. **The article entry point.** The current root is a domain picker → article. OWID equivalents often have an index page that's a curated list of articles. Do we need one? At three domains it feels premature; at six domains it might be essential.
4. **The "explorer" affordance.** Right now `DataExplorer` is a tabbed widget below the lede. OWID embeds tend to have a more explicit "↓ explore the data" handoff. Is that worth the pixels?
5. **Type system.** Current body type is serif via `--font-body`, but the actual font family is generic ("Georgia, Times, serif"). A real type pairing (e.g., GT Sectra body + Inter UI, or any of OWID's actual pairings if licensable) would lift gravitas immediately. Pick one.
6. **Data viz polish.** The MDS plot, heatmap, and free-list compare all work but look schematic. Each has room for a redesign that increases information density without breaking R10 or accessibility. Where are the wins?
7. **The failures-as-findings section.** It's currently a passable list at the bottom of the article. Mark's binding directive ("failures are findings") wants this to be a *first-class* surface, not a footer. How do you elevate it without making refusals feel like the headline?
8. **Mobile experience.** Phase 6 shipped hamburger + bottom drawer. They work; they don't sing. Mobile-first redesign is worth a pass.

---

## 11. How to test, commit, what "done" means

### Test floor before any commit (local, every time)

```
uv run pytest && uv run ruff check . && uv run mypy packages/
cd apps/dashboard && npm run lint && npm run test && npm run build
```

All six must be green. Direct-to-master workflow (see `CLAUDE.md` §8); CI is a redundant confirmation, not a safety net.

### Commit style

Conventional Commits (`CLAUDE.md` §8). Scope is `dashboard` for frontend work. Reference any pipeline gate verdicts in the commit body. Co-author tag for Claude is on every commit that Claude generated; for your work, use your own attribution conventions.

### One commit per task

Don't bundle. If you notice an unrelated improvement while working, commit the current task first and queue the observation as a follow-up. Bundling makes review and rollback ambiguous.

### What "done" means

- All acceptance criteria met.
- Tests pass locally (six commands above).
- For methodology-touching changes: CDA SME verdict in `docs/status/` referenced from the commit body.
- For schema changes: Architect sign-off + `DATA_DICTIONARY.md` co-update.
- No forbidden vocabulary anywhere.
- No spend-gate language. <!-- noqa: spend-gate-check -->
- No point estimates without adjacent uncertainty.
- One commit per task.

---

## 12. Reading list (in priority order)

Read these once at the start; consult them as you work.

1. **`CLAUDE.md`** — agent constitution. Especially §6 (binding rules), §7 (forbidden vocabulary), §9 (common pitfalls). The forbidden-vocab and R10 rules apply to you identically.
2. **`DESIGN_SYSTEM.md`** — the canonical design system. You own it from here. v0.4.10 is the post-Phase-6 state.
3. **`ARCHITECTURE.md`** — full project architecture. Especially §1.5 (framing language — binding on every piece of text), §4.4.6 (failures-as-findings publish layer), §4.5 (R10 uncertainty binding), §5.3 (Phase 6 deliverable state).
4. **`docs/DATA_DICTIONARY.md`** — every field of every JSON the dashboard consumes. v0.1.14.
5. **`SECURITY_AND_HARDENING.md`** — especially §3.3 (publish-layer redaction) and §9 (Reviewer rules table). Less relevant day-to-day, critical when you touch failures display or any publish-layer affordance.
6. **`docs/status/2026-05-12-phase6-architect-kickoff.md`** — the original Phase 6 decomposition. Useful context for "why is this here / why isn't that here."
7. **`docs/status/2026-05-16-phase6-T14-architect-plan.md`** — the documentation-sweep plan that closed Phase 6. Reads as a state-of-the-codebase snapshot.

---

## 13. How to reach Mark (and the agents)

- **Mark direct:** he's the project owner. Decisions about content, scope, methodology framing, and any "should we do X" question route to him.
- **`#lsb-cda-sme` (Slack):** the CDA SME agent posts methodology verdicts here. Methodology-adjacent copy changes get reviewed here.
- **`#lsb-ui-ux` (Slack):** the UI/UX agent posts design-system verdicts here. *This channel is the Claude UI/UX agent's verdict log; it's not your channel — but you may find prior verdicts useful as context for design-system decisions.*
- **`#lsb-alerts` (Slack):** operational alerts from `scripts/qa_check.py`. Not yours; don't post here.

---

## 14. A note on tone

Mark's preference, learned through many sessions: **terse and direct, no preamble, no recap, no hedging**. When you finish a piece of work, say what changed and what's next in one or two sentences. He reads the diff; he doesn't need a summary of the diff.

When the spec is ambiguous, ask. Don't improvise architectural decisions. Don't "fix" things that weren't broken. Don't add features beyond the task. The Claude Code agents that built Phase 6 learned this the hard way; the path is shorter if you start there.

---

*End of `FRONTEND_DESIGNER_BRIEF.md` v0.1. Read at the start of every session. When this file disagrees with `ARCHITECTURE.md` or `DESIGN_SYSTEM.md`, the more specific document wins and this file should be updated to match.*
