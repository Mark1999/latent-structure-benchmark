# Phase 6 T0 — Operator Inspection Mode — Architect Plan

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T0 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` as "a page or route that surfaces every field in `public/data/{domain}.json` and `public/data/manifest.json` as flat tables so Mark can see exactly what the published data contains without needing to drop to JSON").
**Status:** Awaiting Mark's review. UI/UX (light-touch accessibility-floor only) dispatched after Mark's PASS on the plan. CDA SME not required (see §6).

---

## §0. Reading list (mandatory before Coder dispatch)

Common to T0:

1. `/opt/lsb-agent/CLAUDE.md` §6 (binding rules — especially R8 keys, R9 fixtures, R10 uncertainty, R13 design system), §7 (forbidden vocabulary), §9 (pitfalls 1, 7, 8).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact — including section headings on the inspect page; `corpus lens` framing applies to any prose the page generates beyond raw field names), §4.5 (R10 uncertainty pairing).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` §1 (tokens — fonts, spacing, color), §7 (accessibility floor; this is the only §7 obligation T0 carries).
4. Memory: `feedback_ui_polish_scope.md` (Phase 6 minimum-viable functional surface, not polished UI; UI/UX gating reduced to accessibility floor + R10 + tokens only), `feedback_inspection.md` (Mark prefers visual inspection over Claude-mediated reads), `feedback_visual_inspection.md` (Mark cannot evaluate raw JSON visually; tables are the artifact).
5. `/opt/lsb-agent/apps/dashboard/public/data/manifest.json` — actual top-level shape.
6. `/opt/lsb-agent/apps/dashboard/public/data/family.json` + `/opt/lsb-agent/apps/dashboard/public/data/holidays.json` — actual per-domain shape; treat the file as the authority over `data/types.ts` where they disagree (see §4).
7. `/opt/lsb-agent/apps/dashboard/src/data/types.ts` — TS shapes (note: incomplete and partially mismatched against actual JSON; do not narrow-type away unknown fields).
8. `/opt/lsb-agent/apps/dashboard/src/App.tsx`, `/opt/lsb-agent/apps/dashboard/src/components/DataExplorer.tsx`, `/opt/lsb-agent/apps/dashboard/src/api/client.ts` — entry-point and fetch wiring.
9. `/opt/lsb-agent/apps/dashboard/vite.config.ts` — single-entry Vite SPA; no router dep.

---

## §1. Mark's binding directives (carried verbatim from request)

1. **Operator inspection mode is a functional surface, not a polished one.** Plain HTML tables, default tokens, no microcopy work, no animation, no aesthetic blocking by UI/UX. UI/UX agent reviews accessibility floor (table semantics, headings, contrast) and that's it.
2. **Surface EVERY field in published data:** manifest top-level, per-domain JSON top-level, every nested object including `mds_coordinates`, `mds_uncertainty`, `similarity_matrix`, `similarity_ci`, `free_lists`, `consensus_*`, `bootstrap`, `oci`, R1 states, `models`, `model_version_returned` / `version_label`, `collection_date` / `release_date` / `generated_at`, prompt metadata where present. Nothing hidden. If the field exists in JSON, it appears on the page.
3. **Reachable from existing dashboard chrome without breaking the public-facing reader view.** Architect chooses placement; reasoning documented in §2.1.
4. **R10 still applies where uncertainty exists** — surface CIs alongside their points. Where no CI exists (e.g., raw `generated_at`), no synthesis needed.
5. **Forbidden vocabulary (§1.5.4)** still applies to any text the page generates beyond raw field names. Section headings are prose; field names are not.
6. **No API keys, webhook URLs, billing data, or `data/raw/*.jsonl` content.** T0 surfaces ONLY what's already been published through the publish layer. The publish layer is the redaction boundary.
7. **Bundle budget: T0 adds <15 KB gzipped.** Plain tables + a router decision. No new heavy dependencies. Prefer in-place HTML rendering of existing fetched JSON.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Placement decision — **`?inspect=<slug>` query-param on the existing route, not a new Vite entry, not `react-router-dom`.**

The inspect surface is reached by appending `?inspect=<slug>` to the canonical dashboard URL. Examples:

- `https://cogstructurelab.com/?inspect=family` — inspect family.
- `https://cogstructurelab.com/?inspect=holidays` — inspect holidays.
- `https://cogstructurelab.com/?inspect=manifest` — inspect manifest only.

When `?inspect=<slug>` is present, `App.tsx` renders `<InspectRoot>` instead of the article+explorer view. All other paths and the existing `?embed=true` mode are untouched.

**Rationale:**

- **Discoverability vs separation.** Reader-mode is the default at `/`; ops surface is opted-into via a query param. The query-param scheme is invisible to the public reader, indexable as a separate URL state (where indexing is controlled — see below), and survives reloads/permalinks for Mark's own bookmarking.
- **No new Vite entry.** Adding a second Vite entry would split the bundle into two HTML files (`index.html` + `inspect.html`), require a router decision for cross-linking, and complicate Cloudflare Pages deployment. Single-entry conditional render at `App.tsx` is simpler.
- **No `react-router-dom`.** Phase 6's larger T1 task (kickoff §2 T1) defers the router question to a Mark-answered open question. Locking T0 into a router framework now would foreclose that choice. A `window.location.search`-based conditional render is the lightest-possible mechanism and is consistent with the existing `?embed=true` precedent (`App.tsx::isEmbedMode`).
- **Indexability.** A `<meta name="robots" content="noindex">` tag is conditionally injected into `<head>` when `?inspect` is present, using `useEffect` against `document.head`. Inspect URLs do not get crawled. Reader-mode at the same path is unaffected.
- **No breakage of reader-mode.** When `?inspect` is absent, `App.tsx` behaves exactly as today; no existing code path is altered.

**Forward-compatibility note:** If Phase 6 T1 chooses `react-router-dom`, the `?inspect=<slug>` scheme migrates trivially to `/inspect/<slug>` in one place (`App.tsx`'s mode detection). T0 does not lock that decision.

### §2.2. Architectural delta — **Conditional render in `App.tsx`, plus a small URL-state helper.**

Concretely:

- New helper `isInspectMode(): { slug: string | null } | null` adjacent to the existing `isEmbedMode()` in `App.tsx`, reading `?inspect=<slug>` and returning `{ slug }` where `slug ∈ { 'family', 'holidays', 'manifest' }` (or any future manifest slug). `null` means no inspect mode. Empty `slug` (e.g. `?inspect=`) returns `null` (treated as "no inspect mode").
- `App.tsx` adds, immediately after the `embedMode` early-return branch:
  ```
  const inspect = isInspectMode();
  if (inspect !== null) { return <InspectRoot mode={inspect.slug} manifest={manifest} />; }
  ```
- The inspect surface fetches its own manifest + domain JSON via the existing `api/client.ts::fetchManifest` and `fetchDomain` functions. **No new fetch helpers.** No retries, no `react-query`, no SWR.
- The inspect surface uses the same `tokens.css` + `app.css` already loaded. No new CSS file at the top level; inspect-specific layout lives in `apps/dashboard/src/styles/inspect.css` and consists of plain selectors against semantic `<table>` / `<th>` / `<td>` / `<section>` / `<h2>` elements using existing tokens (`--color-text-primary`, `--color-text-muted`, `--color-bg-surface`, `--space-*`, `--font-size-*`, `--font-family-mono` for numeric values).
- **No router dependency added** to `package.json`. Bundle budget protected.
- **`<meta robots>` injection** via `useEffect` in `InspectRoot.tsx`: appends `<meta name="robots" content="noindex">` to `document.head` on mount, removes on unmount.

### §2.3. Component breakdown — **3 components (`InspectRoot`, `InspectSection`, `InspectTable`).**

Flat, no nesting beyond the three. Each is a function component, no hooks beyond `useState` for fetch + `useEffect` for the `<meta robots>` lifecycle. No new utility libraries.

1. **`apps/dashboard/src/components/InspectRoot.tsx`**
   - Props: `mode: string` (the inspect slug), `manifest: Manifest | null` (passed through from `App.tsx`'s already-fetched manifest; if `null`, `InspectRoot` waits).
   - State: `domainResult: DomainResultPublished | null` (for slug-mode); error string; `meta` robots side-effect.
   - On mount: if `mode === 'manifest'`, no further fetch; render manifest sections. Else fetch the domain JSON via `fetchDomain(mode)` and render domain sections plus the manifest's row for that slug.
   - Layout: vertical stack of `<InspectSection>` blocks. Sticky simple header: `<h1>LSB published-data inspection</h1>` + a row of `<a>` links to `?inspect=family`, `?inspect=holidays`, `?inspect=manifest` for navigation between inspect modes.
   - Loading / error states render plain text (`Loading…` / `Could not load.`) matching the §12.2 pattern of `App.tsx`.

2. **`apps/dashboard/src/components/InspectSection.tsx`**
   - Props: `title: string` (section heading), `description?: string` (one-line ARCHITECTURE-aware caveat, optional), `children: ReactNode`.
   - Renders `<section aria-labelledby={id}><h2 id={id}>{title}</h2>{description && <p>{description}</p>}{children}</section>`.

3. **`apps/dashboard/src/components/InspectTable.tsx`**
   - Props: `caption: string` (visible `<caption>` for the table — accessibility binding); `columns: { key: string; label: string }[]`; `rows: Record<string, unknown>[]`.
   - Renders `<table><caption>{caption}</caption><thead><tr>{columns.map(c => <th scope="col">…</th>)}</tr></thead><tbody>{rows.map(...)}</tbody></table>`.
   - Cell rendering: `string`, `number`, `boolean`, `null` → stringified; arrays → JSON-stringified with `<pre>` for readability; objects → JSON-stringified `<pre>`. **No truncation, no ellipsis** — full content visible. Long pre-formatted JSON gets a `white-space: pre-wrap; word-break: break-word; max-width: 60ch` style so it does not overflow the viewport but is fully selectable for copy-paste.
   - CSV-style numeric values use `font-family: var(--font-family-mono)` for column alignment scanning.

That is the full component set. **3 files, ~250-350 LoC total.** No utility library expansion.

### §2.4. Field coverage table

Authority: the actual files at `/opt/lsb-agent/apps/dashboard/public/data/manifest.json`, `family.json`, `holidays.json` (see §4 for the disagreement between `data/types.ts` and the live files — T0 follows the files).

#### Manifest mode (`?inspect=manifest`)

| Section heading | Fields surfaced | Render |
|---|---|---|
| Manifest top-level | `built_at`, `oci_low_concentration_threshold` | 2-column scalar table |
| Domains in this manifest | one row per `manifest.domains[]` entry: `slug`, `analysis_version`, `n_models`, `generated_at`, `model_ids` (joined newline-separated cell or `<pre>`-rendered JSON list) | `<table>` |

#### Domain mode (`?inspect=family` and `?inspect=holidays`)

| Section heading | Source path in JSON | Render |
|---|---|---|
| Domain header | `domain_slug`, `analysis_version`, `generated_at`, `generated_lede` | 2-column scalar table |
| Models in this domain | `models[]` — one row per model with all 10 fields (`provider`, `model_id`, `family`, `origin`, `open_weights`, `collection_method`, `quantization`, `release_date`, `version_label`, `source_notes`) | `<table>` |
| Free lists (per model) | `free_lists[model_id]` — `items[]` and `raw_order[]` (same terms in canonical and produced order); total term count surfaced as a small caption per model. Family domain has 271–568 items per model across 11 models = 4,413 total — small enough for a normal DOM | one `<table>` per model with rank + term, rendered inline (no collapse). If a future domain exceeds ~1,000 items per model, a follow-up commit may add `<details>` then |
| MDS coordinates | `mds_coordinates[model_id]` → `[x, y]` (per the actual file shape — flat 2-tuple, not the wrapped `[[x,y]]` in `data/types.ts`; T0 displays what's there) | `<table>` with columns: `model_id`, `x`, `y` |
| MDS uncertainty (bootstrap ellipses) | `mds_uncertainty[model_id]` — `center`, `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap`, `ci_level` (null for R1-b/R1-c models) | `<table>` with columns: `model_id`, `center_x`, `center_y`, `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap`, `ci_level`. **R10 binding satisfied** — the ellipse parameters ARE the uncertainty paired with `mds_coordinates`; the inspect page presents both tables consecutively for visual joinability |
| Similarity matrix | `similarity_matrix[][]` (number[][], row/col indexed by `models[].model_id` order — the live JSON is `number[][]`, NOT the `Record<string, Record<string, number>>` claimed by `data/types.ts`) | `<table>` with first column `model_id` (row label from `models[i].model_id`), one column per other model, cell value = similarity. Mono font for cells |
| Similarity confidence intervals | `similarity_ci[][]` (paired with `similarity_matrix` — same indexing) | Mirror-table of similarity matrix, each cell rendering `[low, high]` (or `—` for null). **R10 binding:** this table is rendered immediately under the similarity matrix so a CI is visible alongside every point estimate |
| Consensus | `consensus_score`, `consensus_ci` (paired — R10), `consensus_type`, `romney_eigenratio`, `romney_threshold_classic`, `romney_threshold_lsb`, `romney_consensus_pass`, `romney_consensus_warning`, `romney_small_n_warning` | 2-column scalar table |
| Cultural centrality | `cultural_centrality_scores[model_id]`, `negative_centrality_flag`, `negative_centrality_models[]` | one `<table>` for the scores (model_id × score), plus a flag row |
| Cross-model agreement | `cross_model_mantel`, `cross_model_nolan` (these are `[]` in 0.2 — render the empty array verbatim with a `(empty — no cross-model statistics in this domain)` description in `InspectSection`) | `<pre>` block + count |
| Sutrop CSI (salience) | `sutrop_csi[model_id]` — array of `{item, csi, f_mentions, n_runs, mean_position}` per term | per-model `<table>` rendered inline; columns: `item`, `csi`, `f_mentions`, `n_runs`, `mean_position` |
| Salience index agreement | `salience_index_agreement[model_id]` → scalar | model_id × score table |
| Within-model results | `within_model_results[]` — per-model `{model_id, n_runs, oci, oci_ci, underestimates_uncertainty, deterministic_output, salience_stability_rho, elbow_stability, mds_procrustes_rmse, centrality_scores_by_run, centroid_run_id, mds_within_model}` | one row per model in a `<table>`; `centrality_scores_by_run` and `mds_within_model` rendered as inline `<pre>` blocks for the nested objects. **R10 binding:** `oci` and `oci_ci` columns are adjacent |
| G1 stability fields | `g1_spatial_stability`, `g1_aggregate_stability`, `g1_salience_pass`, `g1_spatial_pass`, `g1_overall_pass` | 2-column scalar table (all null in 0.2; render `null` verbatim, do not hide) |
| Groundings | `groundings[]` (always `[]` per 2026-05-07 amendment), `selected_baseline_id` (null) | `<pre>` block with one-line `InspectSection` description noting that v1 domains are model-to-model by design per ARCHITECTURE.md §1.5.5 (forbidden-vocab-safe wording — no "missing" / "placeholder" framing per CLAUDE.md §9 pitfall 4) |
| Display block (precomputed UI helpers) | `display.r1_states` (model_id → R1State); `display.top_terms` (model_id → ranked term list); `display.top_terms_metric` | two tables + one scalar row |

#### Universal coverage rule

The Coder shall NOT use a narrowed TypeScript type that drops unknown fields. The Coder iterates `Object.keys(domainResult)` once for the domain mode, renders every known section above, and at the bottom of the page renders a **"Other top-level fields"** section that lists every key of the JSON that did not match a recognized section name — rendered as `<pre>{JSON.stringify(value, null, 2)}</pre>` with the key as the section heading. This is the safety net: if `cdb_publish` adds a field in a future build, the inspect page surfaces it without code change. Mark's directive #2 ("Nothing hidden") is satisfied even under schema drift.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. Loading `<dev-server>/?inspect=family` renders every section in the §2.4 domain-mode table with no console errors.
3. Loading `<dev-server>/?inspect=holidays` renders every section in the §2.4 domain-mode table with no console errors.
4. Loading `<dev-server>/?inspect=manifest` renders the manifest-mode sections with no console errors.
5. Loading `<dev-server>/` (no inspect param) renders the existing reader view, byte-identical to pre-T0 behaviour (visual diff zero).
6. Loading `<dev-server>/?embed=true` renders embed mode, unchanged.
7. The Coder verifies that an unknown synthetic top-level field added to a local copy of `family.json` (e.g. `"foo_bar": [1,2,3]`) appears in the "Other top-level fields" section without code change.
8. WCAG AA: every `<table>` has a `<caption>`; every `<th>` has `scope`; the inspect page has a single `<h1>` and a heading order of `<h1>` → `<h2>` per section → no skipped heading levels; text contrast against `--color-bg-surface` is ≥ 4.5:1 (the existing tokens already satisfy this).
9. Bundle delta < 15 KB gzipped against the current `dist/` baseline. Coder reports the delta in the PR/commit body.
10. `<meta name="robots" content="noindex">` is verifiably present in `document.head` only when inspect mode is active; absent in reader-mode and embed-mode.
11. No forbidden vocabulary (§1.5.4 / CLAUDE.md §7) anywhere in the page's prose (headings, descriptions, error strings, link labels). Field names from the data — which are not LSB-authored prose — are exempt.
12. No new dependencies added to `package.json`. No new fetch helpers in `api/client.ts`. Existing `fetchManifest` + `fetchDomain` are reused.
13. No raw-data file paths (`data/raw/`, `data/results/`) referenced or surfaced by the page. Only `public/data/manifest.json` + `public/data/{slug}.json` reachable via `fetchManifest` / `fetchDomain`.
14. Reviewer rule R7 (`SECURITY_AND_HARDENING.md` §9) is not triggered — no `cdb_core/schemas.py` changes; no `DATA_DICTIONARY.md` co-update required.

---

## §4. Known shape disagreement (Coder note, not a blocker)

`apps/dashboard/src/data/types.ts` and the live published JSON disagree in three places:

1. `similarity_matrix` is typed as `Record<string, Record<string, number>>` but the live JSON is `number[][]` indexed by `models[].model_id` order.
2. `similarity_ci` is typed as `Record<string, Record<string, [number, number] | null>>` but the live JSON is `[number, number][][]` (also positional).
3. `mds_coordinates` is typed as `Record<string, [[number, number]]>` (wrapped in an outer array) but the live JSON is `Record<string, [number, number]>` (flat 2-tuple).

**T0 follows the files, not the types.** The Coder may either (a) cast through `unknown` at the inspect-page boundary (precedent: `DataExplorer.tsx` lines 152, 192, 229 already use `as unknown as Record<string, [number, number]>` for the same reason), or (b) declare local narrower interfaces in `InspectRoot.tsx` that match the live shape. **The Coder MUST NOT "fix" `data/types.ts` in T0** — that is a Phase 6 T14 documentation-sweep concern; touching it now would expand T0 scope per CLAUDE.md §8 ("No surprise scope creep"). The Coder surfaces this disagreement in the commit body for the doc-sweep follow-up.

---

## §5. Out of scope for T0

Explicitly excluded; do not partially address:

- **Failures-as-findings data.** Phase 6 T9 publishes `public/data/failures/{slug}.json`; Phase 6 T10 surfaces them. When T9 ships, the inspect page extends by adding a new `InspectSection` block to `InspectRoot` keyed off the failures fetch. **Out of scope now.** No placeholder, no "coming soon" affordance.
- `data/raw/*.jsonl` content. Off-limits — the publish layer is the redaction boundary.
- Methodology-page link. Phase 6 T1/T2.
- Styling polish beyond DESIGN_SYSTEM.md tokens. No new colors, no new fonts, no animation, no microcopy work.
- Search / filter / sort affordances on the tables. Plain `<table>` only.
- CSV / JSON export buttons. The page IS the inspection surface; raw JSON is at `/data/family.json` for anyone who wants it.
- Pagination. Tables render every row inline; no pagination, no collapse.
- Dark mode. Single light theme (matches reader-mode).
- Mobile-first design. The inspect page is desktop-first; mobile rendering is "tables overflow horizontally, no special treatment" per the `feedback_ui_polish_scope.md` memory's "functional surface" framing.
- `react-router-dom` or any router framework. Phase 6 T1 owns that decision; T0 does not foreclose it.
- A second Vite entry. Same reason.
- Touching `data/types.ts` to fix the §4 disagreements. T14 doc-sweep concern.

---

## §6. Gate routing

- **Architect:** this plan. Once Mark approves, the orchestrator dispatches the gates below.
- **CDA SME:** **not required.** Rationale: T0 surfaces fields that are already published — no methodology decisions, no new claims, no new generated text beyond section headings. The §1.5.4 forbidden-vocabulary spot-check on the small set of section headings is the Reviewer's standard responsibility (CLAUDE.md §7), not a CDA-SME-level gate. Routing this to CDA SME would burn the SME's review budget on a task with no methodology surface.
- **UI/UX agent:** **light-touch only — accessibility floor + R10 + token consistency.** Per `feedback_ui_polish_scope.md` memory, Phase 6 UI/UX gating is reduced. The UI/UX agent reviews:
  1. Every `<table>` has a `<caption>` and `<th scope>`; heading order is correct (H1 → H2 only, no skips).
  2. Text contrast on the inspect page meets WCAG AA against the chosen background token.
  3. R10 pairing: every point-estimate table is rendered adjacent to its CI table where a CI exists in the data.
  4. Tokens only: no hardcoded colors, fonts, or spacings; everything via `var(--color-…)` / `var(--space-…)` / `var(--font-…)`.
  UI/UX issues PASS / PASS-WITH-NOTES / FAIL on those four checks alone. **No design critique** beyond them. No "the page is ugly" verdict permitted.
- **Coder:** implements after UI/UX PASS or PASS-WITH-NOTES.
- **Reviewer:** standard. Includes the CLAUDE.md §7 forbidden-vocabulary spot-check on section headings, descriptions, and error strings.
- **Tester:** standard pytest/vitest. T0's testable surface is small — three component-level vitest tests (mode parsing, table rendering of a sample row, "unknown-field fallback" rendering) plus a snapshot test that `?inspect=family` renders every §2.4 section heading. No real network fetches; use a fixture domain JSON.

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? |
|---|---|---|
| `cdb_core/schemas.py` | No | No |
| `docs/DATA_DICTIONARY.md` | No (existing fields, no new published fields) | No |
| `ARCHITECTURE.md` | No | No |
| `DESIGN_SYSTEM.md` | No (inspect page intentionally has no §11 inventory entry — it is an ops surface, not a public component) | No |
| `apps/dashboard/src/data/types.ts` | **No** — the §4 disagreements are explicitly deferred to T14 | No |

**Architect sign-off needed:** none — T0 is schema-quiet.

---

## §8. Bundle budget watch

Phase 5 closed at 76.25 KB gzipped (19% of 400 KB cap). T0 estimate:

- `InspectRoot.tsx` + `InspectSection.tsx` + `InspectTable.tsx`: ~3–5 KB gzipped of TSX after tree-shaking.
- `inspect.css`: ~1–2 KB gzipped.
- Manifest-mode handling adds the equivalent of the existing manifest-fetch flow — no measurable bundle cost (already in `App.tsx`).
- No new dependency in `package.json` — zero bundle cost on the dep side.

**Expected delta: ~5–7 KB gzipped.** Well under the 15 KB ceiling Mark set.

The Coder reports the measured delta (`du -b dist/assets/*.js | gzip -c` or equivalent) in the commit body. Reviewer rejects if > 15 KB.

---

## §9. Dependency order

T0 is a single Coder task with no upstream dependencies inside Phase 6. It can be dispatched independently of T1 (routing) — in fact, dispatching T0 first proves the `?param=` URL-state pattern that T1 may or may not choose to keep when it later decides on `react-router-dom` vs anchor-based scrolling.

Other Phase 6 tasks (T9/T10 failures-as-findings) will extend `InspectRoot` by adding a new `<InspectSection>` block. That extension is a follow-up commit, not a re-architecture.

---

## §10. Risks and watch-items

1. **Free-list size on family domain.** Verified 2026-05-12 against the live `family.json`: 271–568 items per model across 11 models, 4,413 total. Normal DOM size; no collapse, no virtualization, no pagination needed. If a future domain produces >1,000 items per model, a follow-up commit can add `<details>` then.
2. **Mismatched `data/types.ts` (§4).** The Coder must not "fix" it. Reviewer rejects T0 commits that touch `data/types.ts`. Documented as a T14 doc-sweep concern.
3. **`<meta robots>` lifecycle.** If the user navigates inspect → reader-mode via clearing the query param manually (back button), the `<meta>` tag must be removed. `useEffect` cleanup handles this; the test asserts the absence after mode switch.
4. **No infinite re-fetch loop.** `InspectRoot` is mounted only when `?inspect=<slug>` is present. The fetch effect's dep is `[mode]` — stable across renders. No `selectedModels` state, no permalink writes, no URL mutation from inspect mode.
5. **Bundle creep from "just one more table feature".** The Coder MUST resist adding sort/filter/search. Phase 6 T0 is a viewer, not a tool. Add a comment at the top of `InspectRoot.tsx` calling out this constraint explicitly so future agents reading the file are reminded.

---

*End of T0 plan.*
