# Phase 5 — Publish Layer + Minimum Viable Dashboard — Architect Plan

**Date:** 2026-05-09
**Planner:** Architect agent (Opus)
**Target plan path:** `/opt/lsb-agent/docs/status/2026-05-09-phase5-architect-plan.md`
**Phase scope:** ARCHITECTURE.md §5.3 Phase 5 ("Publish layer + minimal dashboard") and DESIGN_SYSTEM.md §11 Phase 5 component inventory.
**Status:** Awaiting CDA SME and UI/UX gate verdicts before any Coder dispatch.

---

## §0. Reading list (mandatory before each Coder task)

Common to every task:

1. `ARCHITECTURE.md` §1 (commitments 3, 5, 6, 11), §1.5 (binding on every text artifact), §1.5.4 (forbidden vocabulary), §1.5.6 ("the website is the artifact"), §4.4 (publish layer contract), §4.5 (frontend contract), §5.3 Phase 5.
2. `CLAUDE.md` §6 (binding rules — especially R8, R9, R10, R11, R12, R13), §7 (forbidden vocabulary), §8 (one commit per task; direct-to-master default), §9 (pitfall 1 — `model_id` vs `model_version_returned`; pitfall 2 — no LLM in cdb_analyze; pitfall 7 — forbidden vocabulary; pitfall 8 — no points without uncertainty).
3. `docs/status/2026-05-09-phase4b-t4-partial-completion.md` — corpus state context.

Task-scoped reading on top of the common set is named per task in §6.

---

## §1. Decision summary — six open questions resolved

### §1.1. Re-analyse Phase 4b T4 partial corpus into `0.3.json` before Phase 5? — **NO, defer to Phase 6.**

Phase 5 ships against the **existing `data/results/{family,holidays}/0.2.json`** corpus (Phase 4a recovery output, 11 models on family / 9 on holidays). Reasons:

- Phase 5 is "minimum viable dashboard"; the bottleneck is publish-layer + frontend, not corpus breadth.
- The 0.3 re-analysis would touch `cdb_analyze` (uneven-coverage handling for the 60.6% partial), which is methodology-bound — that's a CDA-SME-gated workstream of its own and would block the dashboard ship.
- Phase 4b T4 also has a known follow-up campaign (~683 cells, ~3-4h) that brings 7 OpenRouter models from 0 to ≥90 cells; re-analysing now means re-analysing again after the follow-up. Better to land 0.3 once, after the follow-up, and swap into the dashboard via the publish layer.
- The dashboard's data-fetch contract (manifest.json + per-domain JSON) is built to swap analysis versions transparently — `0.2 → 0.3` is a one-line change in the publish step plus a re-deploy.

**Forward-carry:** Phase 6 schedules a "0.3 re-analysis after T4 follow-up campaign" task; until then Phase 5 ships 0.2.

### §1.2. Prototype as baseline vs. rebuild? — **(c) Cherry-pick into a fresh build, with the prototype designated as visual reference for UI/UX review.**

The uncommitted prototype demonstrates that a credible Phase 5 frontend is achievable in the budget, but it did not pass UI/UX or CDA SME gates. Three concrete cherry-pick anchors:

1. **Visual reference for the UI/UX gate.** The prototype renders the §3.3 MDS plot, §3.3.5 R1-state markers (R1-a filled circle, R1-b dashed, R1-c hollow triangle), the article-with-explorer page model, the design-token discipline, and the page-load reveal animation at full §1 design-token fidelity. The UI/UX agent reviews the prototype as the visual reference for the visual decisions implicit in DESIGN_SYSTEM.md but not laid out as code; it issues a verdict (PASS / PASS-WITH-NOTES / FAIL with required changes) that the Coder applies during the fresh build.
2. **The 175 KB / 55 KB gzipped bundle figure validates the §9 budget.** The Coder's fresh build inherits this as a target; if the fresh build crosses 400 KB gzipped, the Reviewer rejects.
3. **Component decomposition stays.** The 12 component files (`Header`, `ArticleHeader`, `KeyFinding`, `DomainPicker`, `DataExplorer`, `MDSPlot`, `ModelSelector`, `Legend`, `DownloadBar`, `MethodologySummary`, `Footer`, `App`) map cleanly onto the §11 Phase 5 inventory. The fresh build follows the same decomposition unless UI/UX directs otherwise.

**Working-tree disposition (binding):**

- The current uncommitted working tree (apps/dashboard prototype + react-dom 18→19 bump in package.json + postcss.config.js + index.html font additions + public/family.json) is **reverted to HEAD before Coder dispatch.** `git stash` it under a labelled stash (`stash@{phase5-prototype-reference}`) so it survives as a visual reference but is not part of the Phase 5 commit history.
- The four screenshots at the repo root (`lsb-prototype-fold-1.png`, `lsb-prototype-fullpage.png`, `lsb-prototype-explorer.png`, `lsb-prototype-tooltip.png`) are **moved to `docs/status/2026-05-09-phase5-prototype-screenshots/`** as visual reference material for the UI/UX gate. Those are not committed to the master branch directly; they are checked in alongside the architect plan in the same commit so the UI/UX agent can inspect them inline.
- The Coder builds Phase 5 components fresh, on top of the **clean Phase 0 scaffold** (`apps/dashboard/` + `cdb_publish/` skeletons), with the stash and the screenshots as references.

This avoids two failure modes simultaneously: (a) auditing a prototype that's already 12 files deep would be more reviewer-burden than rebuilding, and (b) discarding entirely loses the bundle-budget validation and the visual reference that informs the UI/UX gate.

### §1.3. Lede generator — LLM vs template for Phase 5? — **Template-based for Phase 5; LLM in Phase 6.**

The §4.2.3 lede generator is LLM-driven. Phase 5 ships a **deterministic template-based lede** in `cdb_publish` and defers the LLM lede generator to Phase 6.

Rationale:

- Phase 5 is two sessions. The LLM lede generator requires a versioned prompt template (`packages/cdb_publish/prompts/v1/lede.md`), the §1.5.4 forbidden-vocabulary system prompt, a Reviewer spot-check workflow, and prompt-version + cache-key plumbing into `DomainResult.generated_lede`. That's a session of its own, not a sub-task.
- A template-based lede is **methodology-safe by construction**: it picks from a fixed library of declarative sentence patterns, parameterised on numeric findings (consensus eigenratio, top diverging models, R1-c counts). Forbidden vocabulary cannot appear because the templates contain no LLM-generated text.
- The §3.8 "Conditional behavior" key-finding strip and the §3.3.5 item 6 "all-deterministic" edge-case copy are explicit, named lede cases. They are exactly the sentence patterns a template covers.
- The dashboard contract (`DomainResult.generated_lede: str`) is identical for template and LLM. The Phase 6 LLM swap is a `cdb_publish` internal change — no schema change, no frontend change.

**Phase 5 lede template specification (per CDA SME review):**

The Coder ships a `cdb_publish/lede.py` module with a deterministic function:

```
def generate_lede(domain_result: DomainResult) -> str: ...
```

It branches on three named cases, each with a fixed sentence pattern. CDA SME reviews the three patterns for §1.5.4 compliance and the corpus-lens framing:

1. **Strong-consensus case** — `consensus_type == STRONG_CONSENSUS` and `n_models >= 8`. Pattern names the two most-divergent models by short name, references the centroid models, uses the §1.5.4-safe form ("X's output organises ... distinctly from Y's").
2. **Weak/no-consensus case** — `consensus_type in {WEAK_CONSENSUS, NO_CONSENSUS}`. Pattern reports the absence of cross-model agreement as a substantive finding ("the models in this slice do not converge on one categorical structure"), without overclaim.
3. **All-deterministic edge case** — `all(w.deterministic_output for w in within_model_results)` (DESIGN_SYSTEM.md §3.3.5 item 6). Verbatim approved copy.

The lede generator is a deterministic Python function; it does NOT call any LLM. It lives in `cdb_publish` (NOT `cdb_analyze`) per the §4.2 binding constraint, even though Phase 5 doesn't yet exercise an LLM call there — the directory choice is forward-compatible with the Phase 6 LLM lede.

**Binding constraint:** the `data/results/{domain}/0.2.json` files have `"generated_lede": ""` (empty) at write time. The publish layer fills this string in at publish time and writes it into the dashboard JSON. The canonical analysis JSON in `data/results/` is **not** edited — `cdb_publish` reads it, generates the lede, and writes the dashboard JSON with the lede injected. Append-only invariant on `data/results/` is preserved.

### §1.4. PNG export approach — **Client-side canvas via SVG-to-canvas serialisation.**

DESIGN_SYSTEM.md §5 calls for 1600×900 social and 2000×2000 high-res with `tEXt` metadata. Architect call: **client-side**, using the browser's `canvas.drawImage(SVGImage)` path with an off-screen `<canvas>`.

Rationale:

- Phase 5 ships a static SPA on Cloudflare Pages with no backend. Server-side rendering would require either (a) a Node renderer in the build pipeline running headless Chrome — significant setup, breaks the "no server" simplicity — or (b) precomputing every viewState's PNG at build time, which doesn't work for arbitrary user-selected model subsets.
- SVG-to-canvas is well-trodden, runs in seconds in the browser, and the bundle cost is small (`canvas-blob-png` patterns, no library required).
- **`tEXt` metadata** for the spec-required fields (domain, models, versions, timestamp) is added via a lightweight PNG-chunk-injection step after the canvas blob: read the bytes, find the `IHDR` chunk, splice in a `tEXt` chunk, re-CRC. ~30 lines of TypeScript. The Coder writes this in `apps/dashboard/src/lib/png-metadata.ts` per the existing §4.5 component-tree pointer to `lib/watermark.ts`.
- Watermark ("cogstructurelab.com" bottom right at 3% opacity) is composited onto the canvas before the blob is captured.

**Phase 5 binding decision:** PNG export ships as part of Phase 5. CSV export is similarly client-side (build a CSV string from the in-memory `DomainResult`, blob+download).

### §1.5. Cloudflare Pages deployment — **Manual deploy in Phase 5; CI deferred to Phase 6.**

Per §4.4.3, manual is the documented Phase 5 trigger. Phase 5 includes:
- The `apps/dashboard/public/_headers` file (already present per Phase 0).
- A documented manual deploy procedure in `apps/dashboard/README.md` ("Deployment" section).
- Cloudflare Pages project config done through the Cloudflare UI by Mark, not in code. The repo-side bits (build command, publish dir, _headers) are static.

**CI-driven publish** (`.github/workflows/publish.yml`) is **explicitly out of Phase 5 scope** and lives in Phase 6 per §4.4.3 ("Phase 6+: GitHub Actions"). Reasons: it depends on `data/results/` git-tracking decisions, secret scoping for Cloudflare API tokens, and a stabilised `publish.py` CLI — all worth doing once the dashboard is live and the publish-layer interface is exercised.

**Staging URL:** Cloudflare Pages auto-provisions a staging URL on the first deploy. Phase 5's "ship to Cloudflare Pages staging URL" deliverable per §5.3 is met by Mark running `python scripts/publish.py && git add apps/dashboard/public/data/ && git commit && git push` once after Phase 5 lands; the staging URL becomes live within ~30s.

### §1.6. The 11 vs 12 model count — **family has 11, holidays has 9; both are correct for 0.2.**

Verified: `data/results/family/0.2.json` lists 11 unique `model_id` values (claude-opus-4-6, claude-sonnet-4-6, deepseek/deepseek-v3.2, google/gemini-2.5-pro, meta-llama/llama-4-maverick, microsoft/phi-4, mistralai/mistral-large-2512, mistralai/mistral-small-2603, openai/gpt-5.4, openai/gpt-5.4-mini, x-ai/grok-4) with MDS coordinates for all 11. Holidays has 9 — phi-4 was a family-only recovery target per `2026-05-05-phase4a-recovery-report.md`, and qwen/qwen-3.5-plus does not appear in either domain's 0.2.

**The dashboard reports the actual count from `len(domain_result.models)`, not a hardcoded 12 or 11.** The methodology summary text references "models tested" with the count derived from the data, not literal. Per-domain counts may differ; this is a normal first-class state and the UI must not present holidays' 9-model figure as a gap.

The "12 models tested" hero stat from DESIGN_SYSTEM.md §1.1 (`--font-size-3xl` example) is **not used as Phase 5 copy**. Phase 5 ships with the actual data-derived count and no hero stat figure.

### §1.7. Honest tagline placement — **Subtitle position in ArticleHeader, plus Methodology Summary.**

Per ARCHITECTURE.md §1.5 the canonical tagline is:

> *LSB measures what frontier LLMs produce when asked to categorise, in a way that's reproducible, comparable across models, and trackable across time.*

DESIGN_SYSTEM.md §2.1 specifies the article header has a "subtitle: one sentence on what the domain reveals." Architect call: the **first** sentence of the subtitle is the per-domain framing ("How [models] organise family-domain vocabulary in their output distributions"); the **second** sentence is the verbatim tagline. The tagline also appears in full in the Methodology Summary block (current prototype location). Two appearances, both prominent, both verbatim from §1.5.

**The Reviewer enforces:** the tagline is rendered as a single React string constant imported from `apps/dashboard/src/copy/framing.ts` so the verbatim version cannot drift across components. Adding a third occurrence requires a copy review — not auto-OK.

---

## §2. Phase 5 deliverable summary

**Publish layer (Python, `cdb_publish`):**

- `cdb_publish/build.py` — reads `data/results/{domain}/{version}.json`, writes `apps/dashboard/public/data/{domain}.json`, `{domain}.v{version}.json`, `models/index.json`, and `manifest.json`.
- `cdb_publish/lede.py` — deterministic template-based lede generator (CDA-SME-reviewed sentence patterns).
- `cdb_publish/derived.py` — computes display-only derived fields (`r1_state` per model, top free-list terms ranked by salience for tooltips, model-display short name from `cdb_core` or fallback).
- `scripts/publish.py` — CLI wrapper (`python scripts/publish.py [--domain family] [--analysis-version 0.2]`).
- `tests/cdb_publish/` — fixture-based tests (no real LLM calls; lede is deterministic so test snapshots are stable).

**Frontend (TypeScript / React, `apps/dashboard/`):**

The Phase 5 component inventory per DESIGN_SYSTEM.md §11:

- `DataExplorer.tsx`, `VizSwitcher.tsx`, `MDSPlot.tsx`, `ModelSelector.tsx`, `DomainPicker.tsx`, `KeyFinding.tsx`, `SourceAttribution.tsx`, `DownloadBar.tsx`, `CiteModal.tsx`, `EmbedModal.tsx`.

Plus the Phase 5 page-shell components implied by §2.1 and not explicitly in §11:

- `App.tsx`, `Header.tsx`, `ArticleHeader.tsx`, `MethodologySummary.tsx`, `Footer.tsx`, `Legend.tsx`.

Plus the API and lib modules per §4.5:

- `api/client.ts` (typed fetch helpers for static JSON), `lib/png-metadata.ts` (tEXt chunk injection), `lib/csv-export.ts`, `lib/watermark.ts`, `data/types.ts` (TS shapes mirroring `DomainResult`), `copy/framing.ts` (canonical tagline + framing strings), `config/analysis.ts` (`OCI_LOW_CONCENTRATION_THRESHOLD = 3.0` per §3.3.5 item 7).

**Out of Phase 5 scope** (per Mark's Phase-5 brief and DESIGN_SYSTEM.md §11 Phase 6 row):

- `FreeListCompare.tsx`, `SimilarityHeatmap.tsx`, `DriftTracker.tsx`, `DateSlider.tsx`, `ModelDetailPanel.tsx`, `AccessibilityTableToggle.tsx`, `ScreenReaderSummary.tsx`.
- The Methodology page (`MethodologyPage.tsx`, `CitationBlock.tsx`, `LimitationCard.tsx`).
- The full §6 Methodology page is Phase 6, Mark writes prose. Phase 5 ships only the **MethodologySummary block** specified in §2.1 (the inline article block, ~5-7 sentences, not a separate page). The Phase 5 Methodology Summary content is CDA-SME-reviewed.
- Drift view, DriftTracker, date slider, free-list compare, similarity heatmap, model detail panel, all accessibility-table-toggle features.
- Researcher grounding submission (already removed from v1 per 2026-05-07 amendment).
- New domains beyond family + holidays.
- CI-driven publish workflow.
- LLM-driven lede generator.

---

## §3. Pre-flight: working-tree clean-up (before Coder dispatch)

This is one task by Mark or by the Architect, not a Coder task. Done before Coder T1 starts.

**T0 — Working-tree clean-up.**
1. `cd /opt/lsb-agent`
2. `git stash push -u -m "phase5-prototype-reference" -- apps/dashboard/ public/family.json` (the `-u` includes untracked files like screenshots if they're under apps/dashboard).
3. The four screenshots at the repo root (`lsb-prototype-fold-*.png`, `lsb-prototype-fullpage.png`, etc.) are **moved** (not stashed): `mkdir -p docs/status/2026-05-09-phase5-prototype-screenshots && mv lsb-prototype-*.png docs/status/2026-05-09-phase5-prototype-screenshots/`. These are added to the architect-plan commit.
4. Verify `git status --short` is clean apart from the new screenshots directory and (when this plan is committed) the plan file.
5. The architect-plan commit (Mark or Architect, this commit, message `docs(arch): Phase 5 architect plan`) bundles: `docs/status/2026-05-09-phase5-architect-plan.md` + `docs/status/2026-05-09-phase5-prototype-screenshots/*.png`. This is one commit; the screenshots are reference material co-located with the plan that describes them.
6. The stashed prototype is preserved by name; the UI/UX agent inspects `git stash show -p stash@{...}` against the relevant stash entry during the gate review.

After T0 the working tree is clean and the Coder starts from a known baseline (Phase 0 scaffold + `data/results/0.2.json` + the architect plan).

---

## §4. Task decomposition (one commit per task)

13 Coder tasks. Each one is independently reviewable; dependencies are explicit in §5.

### T1 — `cdb_publish` skeleton + manifest writer (no schema change)

**Scope.** Wire up `cdb_publish.build.build()` to read `data/results/{domain}/{version}.json`, validate them against the existing `cdb_core.schemas.DomainResult` type, and write a `manifest.json` listing available domains and versions. No domain JSON copy yet — that's T3.

**Deliverables.**
- `packages/cdb_publish/cdb_publish/build.py` — `build(results_dir, output_dir) -> Manifest`. Pure Python, deterministic.
- `packages/cdb_publish/cdb_publish/schemas/manifest.py` — Pydantic `Manifest` (built_at, domains list with `slug`, `analysis_version`, `n_models`, `model_ids`, `generated_at`).
- `packages/cdb_publish/cdb_publish/__init__.py` exports `build`, `Manifest`.
- `scripts/publish.py` — CLI wrapper.
- `tests/cdb_publish/test_build.py` — fixture: a synthetic `DomainResult` written to a temp dir; assert manifest shape.
- `apps/dashboard/public/data/manifest.json` is **not** committed yet — the test asserts on a temp dir; the real publish step is run by Mark at deploy time.

**Acceptance criteria.**
1. `python scripts/publish.py --results-dir data/results --output-dir apps/dashboard/public/data` runs without error against the real 0.2 corpus.
2. `manifest.json` contains exactly the domains listed in `data/results/{family,holidays}/0.2.json` with the correct `analysis_version` and `n_models` (11 and 9 respectively).
3. `pytest tests/cdb_publish/` passes.
4. `ruff check packages/cdb_publish/ scripts/publish.py` passes.
5. `mypy packages/cdb_publish/` passes.
6. `python scripts/check_no_llm_imports.py` passes — `cdb_publish` may import LLM client libraries in a future task, but T1 introduces none.
7. `cdb_publish` does not import `cdb_collect` (boundary rule).

**Gate.** No CDA SME (no methodology surface). No UI/UX (backend only). Reviewer + Tester.

**Reading list addition.** ARCHITECTURE.md §3 (`DomainResult` schema), §4.4 in full.

### T2 — Lede template generator (`cdb_publish/lede.py`) — CDA SME PASS REQUIRED

**Scope.** Implement the deterministic template-based lede generator per §1.3. This task is methodology-bound; the CDA SME reviews the three sentence patterns before any code is written.

**Deliverables.**
- `packages/cdb_publish/cdb_publish/lede.py` — `generate_lede(domain_result: DomainResult) -> str`. Branches on `consensus_type` and `all_deterministic`. Three named patterns. No LLM calls.
- `packages/cdb_publish/cdb_publish/templates/lede_v1.py` — the three sentence patterns as a versioned constant. (Versioned per §6 R7 — even template-based ledes are versioned so the Phase 6 LLM swap can carry a new version.)
- `tests/cdb_publish/test_lede.py` — fixtures cover all three branches: (a) the family 0.2 corpus produces the strong-consensus pattern; (b) a synthetic `DomainResult` with `consensus_type=NO_CONSENSUS` produces the no-consensus pattern; (c) a synthetic `DomainResult` with all `deterministic_output=True` produces the verbatim §3.3.5 item 6 copy.

**Acceptance criteria.**
1. Lede generator is **deterministic** — same input produces byte-identical output.
2. Output strings contain **none** of the §1.5.4 forbidden phrases. Test asserts this directly with a substring check across the test fixtures.
3. The all-deterministic case produces verbatim the DESIGN_SYSTEM.md §3.3.5 item 6 approved copy.
4. The lede generator does **not** import any LLM client library.
5. `pytest tests/cdb_publish/test_lede.py` passes.
6. CDA SME PASS or PASS-WITH-NOTES verdict on the three sentence patterns saved at `docs/status/2026-05-09-phase5-T2-cda-sme-verdict.md`.

**Gate.** **CDA SME PASS required** (methodology + claims validity + forbidden vocabulary + audience translation). Then Reviewer + Tester.

**Reading list addition.** ARCHITECTURE.md §1.5 in full, §1.5.4 forbidden vocabulary, §4.2.3 lede generator, §4.2 binding constraint. DESIGN_SYSTEM.md §3.3.5 item 6 (all-deterministic case), §3.8 conditional behavior.

### T3 — `cdb_publish` domain-JSON writer + derived fields

**Scope.** Extend T1's build step to (a) compute and inject the lede string from T2 into each `DomainResult`'s `generated_lede` field, (b) compute display-only derived fields (`r1_state` per model, top-5 free-list terms ranked by salience for tooltips), and (c) write the domain JSON files (`{domain}.json` and `{domain}.v{version}.json`) to `apps/dashboard/public/data/`.

**Deliverables.**
- `packages/cdb_publish/cdb_publish/derived.py` — pure functions: `r1_state_for(within: WithinModelResult) -> str`, `top_freelist_terms(free_list: FreeList, k: int = 5) -> list[str]`. The `r1_state` logic mirrors `DESIGN_SYSTEM.md` §3.3.5 (uses the `OCI_LOW_CONCENTRATION_THRESHOLD = 3.0` constant — defined in `cdb_publish` as the source of truth for the publish step; the dashboard `config/analysis.ts` imports the same constant value documented in the published manifest).
- Updated `cdb_publish/build.py` calls `generate_lede()` and writes each `DomainResult` JSON with the lede injected. Adds a `display` sub-object to the JSON (`{ r1_states: dict[model_id, str], top_terms: dict[model_id, list[str]] }`) so the frontend doesn't recompute these.
- Updated `manifest.json` writes carry `oci_low_concentration_threshold` (the published threshold value, per DESIGN_SYSTEM.md §3.3.5 item 7 — methodology page reads this from the manifest).
- `tests/cdb_publish/test_build_domain_json.py` — fixture-based integration test: synthetic `DomainResult` → published JSON; assert lede is injected, display fields are correct, manifest carries threshold.

**Acceptance criteria.**
1. Running `python scripts/publish.py` against the real 0.2 corpus produces:
   - `apps/dashboard/public/data/family.json` (== `family.v0.2.json` for 0.2)
   - `apps/dashboard/public/data/holidays.json` (== `holidays.v0.2.json`)
   - `apps/dashboard/public/data/family.v0.2.json`
   - `apps/dashboard/public/data/holidays.v0.2.json`
   - `apps/dashboard/public/data/manifest.json`
2. Each domain JSON has a non-empty `generated_lede` string.
3. Each domain JSON has a `display` sub-object with `r1_states` and `top_terms` keyed by `model_id`.
4. The 11 family models all appear in `r1_states`; the 9 holidays models all appear.
5. The `manifest.json` carries `oci_low_concentration_threshold: 3.0`.
6. **Append-only invariant on `data/results/`** — `data/results/family/0.2.json` and `data/results/holidays/0.2.json` are byte-identical before and after `publish.py` runs. Test asserts file SHA256 unchanged.
7. `pytest`, `ruff`, `mypy`, `check_no_llm_imports.py` all pass.

**Gate.** No CDA SME (uses lede output from T2 — already SME-approved). No UI/UX (backend only). Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §3.3.5 (R1-state logic), §5 (CSV column spec — derived `r1_state` mirrors that contract).

### T4 — Dashboard: scaffold + design tokens + page-load shell

**Scope.** Bring the `apps/dashboard/` tree up from the Phase 0 scaffold to a fully-loading SPA that fetches the manifest and renders the page chrome (Header, ArticleHeader stub, Footer). No data explorer yet — that's T6+. This is the foundation for everything else.

**Deliverables.**
- `apps/dashboard/src/styles/tokens.css` — full DESIGN_SYSTEM.md §1 token set (typography, color palette, spacing, elevation). **Self-hosted fonts**, not Google Fonts CDN — see CSP issue note below.
- `apps/dashboard/src/styles/app.css` — page chrome and reveal animation per the prototype.
- `apps/dashboard/src/copy/framing.ts` — `TAGLINE`, `TAGLINE_LONG`, the canonical strings from ARCHITECTURE.md §1.5 as TS constants. Imported by all components that render framing copy.
- `apps/dashboard/src/config/analysis.ts` — `OCI_LOW_CONCENTRATION_THRESHOLD = 3.0` per DESIGN_SYSTEM.md §3.3.5 item 7.
- `apps/dashboard/src/data/types.ts` — TS interfaces mirroring `DomainResult` (the published shape — includes the `display` sub-object from T3).
- `apps/dashboard/src/api/client.ts` — `fetchManifest()`, `fetchDomain(slug, version?)`. Uses native `fetch`, same-origin only.
- `apps/dashboard/src/App.tsx` — page shell. Loads manifest at mount, renders Header / ArticleHeader / Footer. Body = "Loading…" placeholder.
- `apps/dashboard/src/components/Header.tsx`, `Footer.tsx`, `ArticleHeader.tsx` (stub — domain-driven content fills in T6).
- `apps/dashboard/index.html` — title, meta description, **font links removed** (replaced with self-hosted fonts loaded via tokens.css `@font-face` referring to `apps/dashboard/public/fonts/lato/*.woff2` and `apps/dashboard/public/fonts/jetbrains-mono/*.woff2`).
- `apps/dashboard/public/fonts/` — Lato 400/700 and JetBrains Mono 400/700 self-hosted woff2 files. (Lato is SIL OFL; JetBrains Mono is SIL OFL — both redistributable. The Coder downloads from Google Fonts and commits the woff2 files. Adds an attribution comment in `tokens.css`.)
- `apps/dashboard/postcss.config.js` updated per the prototype (autoprefixer only; Tailwind v4 plugin removed since the project uses CSS variables, not utilities).
- `apps/dashboard/package.json` — react / react-dom / @types upgrades to v19.x. **Bump rationale documented in commit body.** Per CLAUDE.md §8 a dependency bump is allowed inside a Coder task as long as it's necessary; here the upgrade is from `react@18.x` (Phase 0 scaffold) to `react@19.x` to match the type definitions of the scaffold's dev dependencies — this is a **fix**, not a new dependency. The Reviewer verifies the bump is necessary by running `npm install` against both old and new versions and confirming the type errors that were present at v18 are resolved at v19.
- `apps/dashboard/src/main.tsx` — React 19 root.

**CSP issue (caught by Architect during planning):** the prototype's `index.html` links Google Fonts CDN, which violates `apps/dashboard/public/_headers`'s strict CSP (`font-src 'self'`, `style-src 'self' 'unsafe-inline'`, no allowance for fonts.googleapis.com or fonts.gstatic.com). Self-hosting the woff2 files in `apps/dashboard/public/fonts/` is the binding fix and is encoded in T4's deliverables.

**Acceptance criteria.**
1. `cd apps/dashboard && npm install && npm run build` succeeds; output is `apps/dashboard/dist/`.
2. `npm run lint` passes.
3. `npm run test` passes (vitest, no real fetch).
4. The built bundle's gzipped JS size is **< 100 KB** at this stage (this is just shell + tokens; the budget for the full app is < 400 KB per §9). The Reviewer runs `gzip -k -9 apps/dashboard/dist/assets/*.js && du -sh` and confirms.
5. Loading the built site (e.g. via `npm run preview`) renders Header, ArticleHeader (stub), Loading placeholder, Footer with the canonical tagline visible in the right places.
6. The CSP `_headers` file is **not** edited — the self-hosted fonts mean the existing CSP works without modification.
7. The dashboard does not import any `cdb_*` Python package (boundary rule). Reviewer's static check passes.
8. No real model API calls in any test (R9).
9. **No forbidden vocabulary** — Reviewer greps the source for `worldview`, `believes`, `thinks` (in model-facing context).

**Gate.** **UI/UX PASS required** (frontend task). Verdict at `docs/status/2026-05-09-phase5-T4-uiux-verdict.md`. UI/UX reviews the design-token implementation, the page-shell composition, the self-hosted-font choice, the framing.ts canonical strings, and the WCAG AA contrast on the rendered chrome. Then Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §1 in full, §2.1 page architecture, §2.2 navigation, §7 accessibility, §9 performance budget, §10 UI/UX agent responsibilities. SECURITY_AND_HARDENING.md §3.1 CSP.

### T5 — Dashboard: DomainPicker + KeyFinding

**Scope.** Add the per-domain pill-button picker (DESIGN_SYSTEM.md §2.3) and the key-finding strip (§3.8) that consumes the `generated_lede` from the published JSON. Hooks domain switching state into App.tsx so the data fetch re-runs.

**Deliverables.**
- `apps/dashboard/src/components/DomainPicker.tsx` — horizontal pill buttons, "available" vs "coming soon" states.
- `apps/dashboard/src/components/KeyFinding.tsx` — renders `domain_result.generated_lede` per §3.8 styling.
- `App.tsx` updated to wire domain state to data fetch. Manifest determines which domains are "available" (those with a JSON published).
- Vitest: KeyFinding renders the lede; DomainPicker handles selection/keyboard navigation.

**Acceptance criteria.**
1. Loading the site renders the family domain by default.
2. Clicking the "Holidays" pill triggers a fetch for `holidays.json` and re-renders the KeyFinding.
3. KeyFinding shows the deterministic lede from T2/T3.
4. Domains not in the manifest render as disabled pills with "coming soon" affordance per §2.3.
5. Keyboard navigation works (tab to pills, arrow keys between, Enter activates) per §7.
6. Screen-reader users hear domain name + state via aria-label per §7.
7. No forbidden vocabulary; Reviewer spot-checks the rendered KeyFinding output for the family + holidays cases.
8. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required. Verdict at `docs/status/2026-05-09-phase5-T5-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §2.3 domain navigation, §3.8 key finding, §7 keyboard navigation.

### T6 — Dashboard: MDSPlot (R1-state rendering, ellipses, hover tooltip)

**Scope.** The signature visualisation. Hand-rolled SVG (per the prototype's approach — no D3 dependency yet), with the §3.3.5 R1-state rendering binding (R1-a filled circle, R1-b dashed-stroke circle 60% fill 100% stroke, R1-c hollow triangle 3px stroke), bootstrap ellipses for R1-a only, and the hover tooltip with OCI badge + top-5 free-list terms.

This is the most visually load-bearing component in Phase 5. UI/UX reviews against the prototype reference and DESIGN_SYSTEM.md §3.3 + §3.3.5 line-by-line.

**Deliverables.**
- `apps/dashboard/src/components/MDSPlot.tsx` — full implementation per DESIGN_SYSTEM.md §3.3 + §3.3.5 binding rules.
- The `r1_state` value comes from the `display.r1_states` sub-object in the published JSON (T3). The OCI threshold value is read from `config/analysis.ts` (sanity-check) — never as a numeric literal anywhere else.
- Tooltip uses the §3.3.5 item 5 binding copy for R1-c verbatim. R1-b tooltip uses the binding copy from the §3.3.5 R1-b row verbatim. R1-a tooltip is the standard "OCI: X.X" with one-line explanation on first hover.
- Legend: **inline** §3.3.5 item 4 binding requirement — rendered marker samples (filled circle, dashed circle, hollow triangle) with text labels. Each sample passes 3:1 contrast against the legend background.
- Hover state, click-to-select model state, ARIA labels on the SVG container per §7.
- Vitest: MDSPlot renders 11 points for family corpus; renders an R1-c marker as `<path>` (triangle) for any `deterministic_output=True` model; renders an R1-b marker as dashed-stroke circle for any `oci < 3.0` model; renders ellipses only for R1-a models.

**Acceptance criteria.**
1. Family corpus renders 11 model points; holidays renders 9.
2. The §3.3.5 item 6 all-deterministic edge case is **not** triggered by either domain (family + holidays both have at least one R1-a model). Test fixture exercises an all-deterministic synthetic case and confirms KeyFinding falls back to the all-deterministic copy.
3. Hovering a point shows the tooltip with: model short name, model_id, OCI value with state badge, top-5 free-list terms.
4. R1-b and R1-c points render **without** ellipses (binding invariant 1, §3.3.5).
5. R1-c marker is a hollow triangle at 3px stroke (binding §3.3.5 implementation requirement 2). Visual diff against the prototype screenshot in `docs/status/2026-05-09-phase5-prototype-screenshots/lsb-prototype-explorer.png` — UI/UX reviews this.
6. WCAG AA: the §7 + §3.3.5 item 2 stroke-width fix at 3px gives all model-color stroke samples ≥ 3:1 on white.
7. Component is interpretable in grayscale (§7) — shape encoding (filled/dashed/triangle) carries the R1 state independently of color.
8. No `dangerouslySetInnerHTML`, no `eval`, CSP-clean.
9. `npm run build && npm run test && npm run lint` all pass.

**Gate.** **UI/UX PASS required** (the most visual-decision-heavy task in Phase 5). Verdict at `docs/status/2026-05-09-phase5-T6-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §3.3 (full), §3.3.5 (full, all binding implementation requirements), §7 accessibility. ARCHITECTURE.md §4.2.6 (bootstrap uncertainty mandatory).

### T7 — Dashboard: ModelSelector + Legend integration

**Scope.** The control panel (DESIGN_SYSTEM.md §3.7) — checkbox per model with origin badge, open/closed weights indicator, "select all" / "clear all" links, max-6-selected enforcement with inline warning. Wires into MDSPlot's selection state.

**Deliverables.**
- `apps/dashboard/src/components/ModelSelector.tsx`.
- `apps/dashboard/src/components/Legend.tsx` — already partially in T6's MDSPlot scope; T7 separates it into a standalone component used by both MDSPlot and (future) other vizzes.
- Origin badges use `--color-origin-*` tokens from §1.2.
- Vitest: max-6 enforcement; select-all / clear-all; keyboard accessibility.

**Acceptance criteria.**
1. All 11 family / 9 holidays models render with checkboxes.
2. Origin badge `[US]` / `[EU]` / `[CN]` rendered next to each model in the correct color.
3. Open vs closed weights indicator visible.
4. "Select all" / "Clear all" links work.
5. Max 6 selected enforced with inline warning at attempt 7.
6. Keyboard accessible (tab, space to toggle).
7. Selected models drive MDSPlot's `selectedModels` prop — points only render for selected.
8. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required. Verdict at `docs/status/2026-05-09-phase5-T7-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §3.7 model selector, §1.2 color palette (origin tokens).

### T8 — Dashboard: VizSwitcher (placeholder for Phase 6 tabs)

**Scope.** The §3.2 tab bar — but in Phase 5, only the MDS Plot tab is active. The other three (Free Lists, Similarity, Drift) are rendered as **disabled** tabs with a "coming in Phase 6" affordance. This is intentional: it tells visitors that more views are planned without claiming they exist.

**Deliverables.**
- `apps/dashboard/src/components/VizSwitcher.tsx`.
- Active tab: MDS Plot. Disabled tabs: Free Lists, Similarity, Drift. Disabled-tab tooltip: "Coming in Phase 6 — see methodology summary below."
- URL state: only `#mds` fragment is exercised. The other tabs' `#freelist`, `#similarity`, `#drift` are not yet wired.
- Vitest: enabled-tab activates; disabled-tab is `aria-disabled` and not focusable.

**Acceptance criteria.**
1. Tab bar renders four tabs; only MDS Plot is active.
2. Disabled tabs show tooltip on hover/focus.
3. URL fragment updates to `#mds` on activation; refresh preserves state.
4. Keyboard accessible.

**Gate.** UI/UX PASS required (the "coming in Phase 6" copy is methodology-adjacent — see §1.5.7 exploratory framing — but architect's call is that this is a UI affordance, not a methodology claim, so CDA SME is **not** required; UI/UX reviews the copy choice). Verdict at `docs/status/2026-05-09-phase5-T8-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §3.2 visualisation switcher.

### T9 — Dashboard: DataExplorer container + integration

**Scope.** Compose VizSwitcher + MDSPlot + ModelSelector + Legend into the DataExplorer container per DESIGN_SYSTEM.md §3.1. Connects all the pieces from T6, T7, T8.

**Deliverables.**
- `apps/dashboard/src/components/DataExplorer.tsx` — composition only; no new logic. Manages model-color palette assignment per §1.2 (stable ordering by sorted `model_id`, palette-cycling for >6 models).
- App.tsx routes the loaded `DomainResult` through DataExplorer.
- Vitest: full integration test — synthetic `DomainResult` → DataExplorer → all sub-components render.

**Acceptance criteria.**
1. Loading family or holidays renders the full data explorer area: tab bar at top, visualisation in centre, control panel right, legend below.
2. The full bundle gzipped JS size at this stage is **< 350 KB** (leaves headroom for T10–T13 — must hit < 400 KB per §9 by T13).
3. Page load time on a simulated 4G connection is **< 3 seconds** per §9. Reviewer measures with Lighthouse.
4. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required. Verdict at `docs/status/2026-05-09-phase5-T9-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §3.1 explorer layout, §9 performance.

### T10 — Dashboard: SourceAttribution + DownloadBar (CSV + permalink)

**Scope.** The §5 affordances below the chart — source line, CSV download, permalink. PNG + Cite + Embed are split out to T11 to keep the commit sizes bounded.

**Deliverables.**
- `apps/dashboard/src/components/SourceAttribution.tsx` — the source line per §5 (model list, domain, prompt version, analysis version, collection month).
- `apps/dashboard/src/components/DownloadBar.tsx` — CSV + permalink buttons.
- `apps/dashboard/src/lib/csv-export.ts` — pure function: `domainResultToCsv(data, selectedModels): string`. Includes the §5 binding columns: model_id, family, origin, mds_x, mds_y, semi_major, semi_minor, rotation_rad, n_bootstrap, oci, deterministic_output, r1_state. Null-handling explicit per §5: ellipse params null for R1-b and R1-c rows.
- `apps/dashboard/src/lib/permalink.ts` — encodes/decodes view state (domain, models, viz tab) into a URL hash. On load, decodes hash and restores state.
- Vitest: CSV column shape exact match against §5 binding spec; permalink round-trip test.

**Acceptance criteria.**
1. Source line shows correct attribution: 11 models for family / 9 for holidays, prompt v1, analysis v0.2, "Collected April–May 2026" (string from manifest).
2. CSV download has the binding columns from §5; ellipse params are null for R1-b and R1-c rows.
3. Permalink button copies a URL; pasting that URL into a new tab restores the same domain + selected-models + viz tab.
4. Bundle gzipped JS < 380 KB.
5. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required. Verdict at `docs/status/2026-05-09-phase5-T10-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §5 download and attribution.

### T11 — Dashboard: PNG export (canvas + tEXt metadata + watermark)

**Scope.** Client-side PNG export per §1.4 of this plan. Two sizes: 1600×900 social, 2000×2000 high-res. tEXt metadata: domain, models, analysis_version, generated_at. Watermark "cogstructurelab.com" bottom-right at 3% opacity.

**Deliverables.**
- `apps/dashboard/src/lib/png-export.ts` — `renderToPng(svgElement, { size: 'social' | 'highres' }) -> Promise<Blob>`. Uses canvas + `XMLSerializer` on the SVG.
- `apps/dashboard/src/lib/png-metadata.ts` — pure function `injectTextMetadata(blob, kv: Record<string, string>) -> Promise<Blob>`. Splices a `tEXt` chunk into the PNG. Re-CRCs the chunk.
- DownloadBar updated with a PNG button that calls `renderToPng()` then `injectTextMetadata()` then triggers the file download.
- Vitest: `injectTextMetadata` produces a PNG that, when re-parsed, has the tEXt fields readable.

**Acceptance criteria.**
1. Clicking the PNG button on the family MDSPlot produces a 1600×900 PNG with the watermark bottom-right and the tEXt fields populated.
2. The 2000×2000 high-res variant renders identically (same content, larger).
3. PNG content matches the on-screen MDSPlot at the moment of export (same selected models, same viz tab).
4. PNG file size < 500 KB for the 1600×900, < 2 MB for the 2000×2000.
5. Bundle gzipped JS < 400 KB (the §9 binding budget).
6. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required (visual: watermark size/placement, edge cases of the SVG-to-canvas serialisation). Verdict at `docs/status/2026-05-09-phase5-T11-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §5 PNG export spec.

### T12 — Dashboard: CiteModal + EmbedModal

**Scope.** Two modal dialogs per §5: citation in APA / MLA / Chicago / BibTeX, and an `<iframe>` embed snippet.

**Deliverables.**
- `apps/dashboard/src/components/CiteModal.tsx`.
- `apps/dashboard/src/components/EmbedModal.tsx`.
- Modals are accessible per §7: focus trap, Escape closes, ARIA dialog role.
- Citation strings are generated client-side; "LSB" canonical name and "Cognitive Structure Lab" website name used appropriately per §1.6 (binding implication 4).
- Vitest: modal open/close, citation string snapshot, embed snippet snapshot, focus trap.

**Acceptance criteria.**
1. Cite button opens the modal; four citation tabs render with accurate domain + analysis_version.
2. Copy-to-clipboard works on each citation.
3. Embed button opens a modal with a working `<iframe src="...">` snippet that, when pasted into a third-party page, embeds the current view (TBD: this requires a `?embed=true` URL flag that hides chrome — included in T12).
4. Both modals are keyboard-accessible per §7.
5. Bundle gzipped JS < 400 KB.
6. `npm run build && npm run test && npm run lint` all pass.

**Gate.** UI/UX PASS required. Citation strings touch the §1.6 naming convention — the UI/UX agent reviews the APA/MLA/Chicago/BibTeX strings for correctness. Verdict at `docs/status/2026-05-09-phase5-T12-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** DESIGN_SYSTEM.md §5 cite modal, §7 modal accessibility. ARCHITECTURE.md §1.6 project naming.

### T13 — Dashboard: MethodologySummary block + tagline placement + final integration

**Scope.** The §2.1 article methodology summary block — short prose (~5–7 sentences) explaining CDA elicitation, the corpus-lens concept, the tagline (placed verbatim per §1.7 of this plan), and a placeholder link to the (Phase 6) full methodology page. CDA SME reviews the prose word-by-word.

**Deliverables.**
- `apps/dashboard/src/components/MethodologySummary.tsx`.
- The prose draft lives in `apps/dashboard/src/copy/methodology_summary.ts` and is reviewed by the CDA SME alongside this task. The prose is **not** Coder-generated narrative — the Coder ports the CDA-SME-approved draft from the verdict file into the TS constant.
- Final integration polish: page-load reveal staggering per the prototype reference, mobile-readable layout per §8, a final pass on accessibility (focus indicators on every interactive element, "Read as table" toggle is **not** in Phase 5 — this is called out in the methodology summary's "coming in Phase 6" footnote).

**Acceptance criteria.**
1. MethodologySummary renders below the data explorer per §2.1 page architecture, max-width 680px.
2. The tagline appears verbatim in MethodologySummary AND in ArticleHeader subtitle, both pulled from `copy/framing.ts` (single source of truth).
3. CDA SME PASS on the methodology summary prose.
4. Mobile (< 768px) layout: control panel collapses to bottom drawer per §8; methodology summary still readable at full width.
5. WCAG AA contrast pass on every text element.
6. Bundle gzipped JS < 400 KB.
7. Cumulative Phase 5 acceptance: a fresh `npm run build && npm run preview` against the published 0.2 corpus renders the full article-with-explorer page model exactly as specified in DESIGN_SYSTEM.md §2.1.

**Gate.** **CDA SME PASS required** (the methodology summary prose is methodology-bound and the CDA SME reviews on all four axes). Verdict at `docs/status/2026-05-09-phase5-T13-cda-sme-verdict.md`. **UI/UX PASS required** for the rest of the integration. Verdict at `docs/status/2026-05-09-phase5-T13-uiux-verdict.md`. Reviewer + Tester.

**Reading list addition.** ARCHITECTURE.md §1.5.1 corpus-lens five-link chain (the methodology summary names this), §1.5.7 exploratory framing. DESIGN_SYSTEM.md §2.1, §6 methodology page (only the outline for the page; Phase 5 ships the in-article summary, not the page), §8 mobile, §9 performance final.

---

## §5. Dependency graph

```
T0 (clean working tree, prep architect-plan commit, screenshots)
  │
  ▼
T1 (cdb_publish skeleton + manifest)
  │
  ├──▶ T2 (lede generator) — [CDA SME gate]
  │
  ▼
T3 (cdb_publish domain JSON writer + derived fields) ◀── depends on T1 + T2
  │
  ▼ ──── (publish layer is now self-sufficient; frontend can begin in parallel) ────
  │
T4 (dashboard scaffold + tokens + page shell) — [UI/UX gate]
  │
  ▼
T5 (DomainPicker + KeyFinding) — [UI/UX gate]
  │
  ▼
T6 (MDSPlot — R1-state rendering) — [UI/UX gate]
  │
  ▼
T7 (ModelSelector + Legend) — [UI/UX gate]
  │
  ▼
T8 (VizSwitcher) — [UI/UX gate]
  │
  ▼
T9 (DataExplorer composition) — [UI/UX gate]
  │
  ▼
T10 (SourceAttribution + DownloadBar — CSV + permalink) — [UI/UX gate]
  │
  ▼
T11 (PNG export) — [UI/UX gate]
  │
  ▼
T12 (CiteModal + EmbedModal) — [UI/UX gate]
  │
  ▼
T13 (MethodologySummary + tagline + integration) — [CDA SME gate + UI/UX gate]
  │
  ▼
Mark deploys to Cloudflare Pages staging URL.
Phase 5 complete.
```

**Critical-path observations:**

- T2 (lede) is a CDA-SME-gated mini-blocker that runs in parallel with T1 (skeleton). T1 + T2 → T3 then unblocks the frontend.
- T3 outputs the published JSON the frontend fetches; T4 can start as soon as T3 is committed (or even in parallel using fixture data; the Coder writes test fixtures regardless).
- T4–T13 are sequential: each task depends on the prior one's components.
- T13 is the only frontend task with a CDA SME gate (in addition to UI/UX) because it ships methodology-bound prose.
- The whole chain is ~13 commits. If any UI/UX or CDA SME gate FAILs, the chain pauses and the Architect reworks the affected plan section before re-dispatching.

---

## §6. Acceptance criteria and gate verdict file paths (summary)

| Task | CDA SME | UI/UX | Verdict files (in `docs/status/`) |
|---|---|---|---|
| T1 | — | — | `2026-05-09-phase5-T1-reviewer-verdict.md`, `-tester-verdict.md` |
| T2 | **PASS** | — | `2026-05-09-phase5-T2-cda-sme-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T3 | — | — | `2026-05-09-phase5-T3-reviewer-verdict.md`, `-tester-verdict.md` |
| T4 | — | **PASS** | `2026-05-09-phase5-T4-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T5 | — | **PASS** | `2026-05-09-phase5-T5-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T6 | — | **PASS** | `2026-05-09-phase5-T6-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T7 | — | **PASS** | `2026-05-09-phase5-T7-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T8 | — | **PASS** | `2026-05-09-phase5-T8-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T9 | — | **PASS** | `2026-05-09-phase5-T9-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T10 | — | **PASS** | `2026-05-09-phase5-T10-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T11 | — | **PASS** | `2026-05-09-phase5-T11-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T12 | — | **PASS** | `2026-05-09-phase5-T12-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |
| T13 | **PASS** | **PASS** | `2026-05-09-phase5-T13-cda-sme-verdict.md`, `-uiux-verdict.md`, `-reviewer-verdict.md`, `-tester-verdict.md` |

Slack channels per CLAUDE.md §5: T2 + T13 SME verdicts post to `#lsb-cda-sme`. T4–T13 UI/UX verdicts post to `#lsb-ui-ux`.

---

## §7. Schema changes — **none**

This plan does **not** modify `cdb_core/schemas.py`. The existing `DomainResult` schema is sufficient for Phase 5. No `DATA_DICTIONARY.md` update required for this plan.

The publish layer's `display` sub-object (`r1_states`, `top_terms`) is a **derived field stored in the dashboard JSON only**, not in the canonical analysis JSON or the schema. It is documented in `cdb_publish/README.md` (updated as part of T3) but does not enter `cdb_core/schemas.py`.

If during T6 or T13 a UI/UX or CDA SME gate identifies a schema gap (e.g., the lede generator needs an extra metadata field), the Architect plan is paused and a separate schema-change plan with explicit Architect sign-off + DATA_DICTIONARY.md co-update is opened.

---

## §8. CDA SME review request — methodology-bound items

**This plan is dispatched to `#lsb-cda-sme` for verdicts on the following methodology-bound items before Coder dispatch:**

1. **The three lede sentence patterns in T2.** SME reviews on protocol validity (do the patterns correctly describe what the analysis measures?), analytical validity (do they reference the right statistics — `consensus_type`, `romney_eigenratio`, `deterministic_output`?), claims validity (no §1.5.4 forbidden vocabulary; corpus-lens framing applied; exploratory framing per §1.5.7), and audience translation (legible to a journalist; defensible to a skeptical reader). The full sentence patterns are written in the T2 verdict file when the verdict is requested.

2. **The MethodologySummary block prose in T13.** SME reviews the ~5–7 sentence draft on the same four axes. The draft includes the verbatim §1.5 tagline, names the CDA tradition (Romney, D'Andrade, Weller, Borgatti, Batchelder per §1.5.5 / §1.5.6 binding) without forbidden vocabulary.

3. **The disabled-tab "coming in Phase 6" copy in T8.** SME does **not** gate this (it is UI affordance, not methodology), but I flag it here so the SME has the option to flag it if any current draft language overclaims about Phase 6 functionality. Default is no SME review unless flagged.

The full SME-review packet (lede patterns + MethodologySummary prose draft) is provided when this plan is dispatched to the CDA SME channel.

---

## §9. UI/UX review request — frontend items

**This plan is dispatched to `#lsb-ui-ux` for verdicts on each of T4–T13 before Coder dispatch.** UI/UX reviews on the four binding questions per DESIGN_SYSTEM.md §10:

1. **OWID design fidelity** — does each component match DESIGN_SYSTEM.md §1 tokens, §2 page architecture, §3 explorer pattern?
2. **Journalist 30-second test** — can a journalist arriving cold understand the family domain in 30 seconds?
3. **Researcher reproduce-and-cite test** — does the researcher have CSV download, permalink, citation, and a clear path to the raw data?
4. **WCAG AA accessibility** — color + shape together, keyboard nav, ARIA, focus indicators.

UI/UX additionally reviews:

- **The prototype as visual reference** (`docs/status/2026-05-09-phase5-prototype-screenshots/*.png`) — verdict on whether the rendered fold-1, full-page, explorer, and tooltip screenshots are an acceptable visual baseline. PASS-WITH-NOTES anywhere here flows into the corresponding Coder task as required modifications. FAIL anywhere bounces the plan back to the Architect.
- **The CSP-driven self-hosted-fonts decision in T4** — UI/UX confirms this does not cost any visual fidelity (Lato + JetBrains Mono are SIL OFL and render identically self-hosted vs from Google Fonts CDN).
- **The §3.3.5 binding R1-state visual treatment in T6** — line-by-line against items 1–8 of the binding implementation requirements.
- **The §3.3.5 item 6 all-deterministic edge-case copy in T2** — UI/UX confirms the lede generator's verbatim copy matches DESIGN_SYSTEM.md.
- **The §1.7 tagline placement in T13** — UI/UX confirms two-occurrence rule (ArticleHeader subtitle + MethodologySummary).

`DESIGN_SYSTEM.md` itself is **not** edited by this Phase 5 plan. If a Coder task in T4–T13 surfaces a visual decision the design system does not yet cover, the Coder pauses, surfaces the question to the UI/UX agent, the UI/UX agent updates `DESIGN_SYSTEM.md` (one PR with the update), and only then resumes.

---

## §10. Forbidden scope reaffirmed (no scope creep)

Out of Phase 5 — these are explicit Phase 6 deliverables and the Coder may **not** implement any of them as part of T1–T13:

- Free-list compare (`FreeListCompare.tsx`)
- Similarity heatmap (`SimilarityHeatmap.tsx`)
- Drift tracker / drift view (`DriftTracker.tsx`, `DateSlider.tsx`)
- Model detail panel (`ModelDetailPanel.tsx`)
- Accessibility table toggle (`AccessibilityTableToggle.tsx`)
- Screen reader summary (`ScreenReaderSummary.tsx`)
- Methodology page proper (`MethodologyPage.tsx`, `CitationBlock.tsx`, `LimitationCard.tsx`) — Mark writes the prose in Phase 6
- Researcher grounding submission (already removed from v1 per 2026-05-07 amendment — not Phase 6 either)
- New domains: food, emotion, justice
- LLM-driven lede generator (Phase 6)
- CI-driven publish workflow (Phase 6)
- 0.3 re-analysis with Phase 4b T4 partial corpus (Phase 6 after follow-up campaign)
- Phase 4b T4 follow-up campaign (separate operational track)
- Server-side rendering of any kind

If during Phase 5 a Coder feels they need any of these to satisfy a task acceptance criterion, that is a sign the Architect plan is wrong, not a sign that scope should expand. Coder pauses and asks. CLAUDE.md §8 "no surprise scope creep" applies.

---

## §11. Working-tree disposition (final)

After T0:
- `apps/dashboard/` — reverted to HEAD (Phase 0 scaffold).
- `data/results/family/0.2.json` and `data/results/holidays/0.2.json` — unchanged. (Append-only invariant maintained throughout Phase 5.)
- `docs/status/2026-05-09-phase5-architect-plan.md` — this plan, committed.
- `docs/status/2026-05-09-phase5-prototype-screenshots/` — 4 PNG files, committed alongside the plan.
- `git stash@{phase5-prototype-reference}` — the prototype tree, preserved as visual reference.

The architect-plan commit is `docs(arch): Phase 5 architect plan` per CLAUDE.md §8 conventional commits, scope `arch`. Body references this plan path and the four open architectural decisions (§1.1–§1.7). One commit.

---

## §12. Dispatch sequence

1. **This plan committed** to `docs/status/2026-05-09-phase5-architect-plan.md` + screenshots, by Architect or Mark.
2. **Architect posts the plan to `#lsb-cda-sme`** for the T2 lede patterns + T13 methodology summary prose draft. Awaits PASS / PASS-WITH-NOTES / FAIL on the methodology-bound items.
3. **Architect posts the plan to `#lsb-ui-ux`** for the T4–T13 frontend review. Awaits PASS / PASS-WITH-NOTES / FAIL on the four UI/UX questions and the visual-reference review of the prototype screenshots.
4. **If both gates PASS** (or PASS-WITH-NOTES with notes documented and applicable to the Coder), Architect dispatches T0 → T1 → T2 → T3 → T4 → … → T13 in order, one commit each.
5. **If any gate FAILs**, the plan returns to the Architect for rework. The whole plan does not necessarily restart; the Architect identifies which sections need amendment and re-dispatches just the changed portions.
6. **Phase 5 complete** when T13 is committed, all gate verdicts PASS, the dashboard renders the article-with-explorer page model on a Cloudflare Pages staging URL, and Mark personally walks through the family + holidays domains and confirms the 30-second-journalist test and the reproduce-and-cite-test on the deployed site.

---

*End of Phase 5 architect plan. This document is binding for T1–T13 and supersedes any prior Phase 5 framing in `ARCHITECTURE.md` §5.3 (which describes Phase 5 at a high level; this plan is the operational decomposition).*

---

**Files referenced in this plan (absolute paths):**

- `/opt/lsb-agent/ARCHITECTURE.md`
- `/opt/lsb-agent/CLAUDE.md`
- `/opt/lsb-agent/DESIGN_SYSTEM.md`
- `/opt/lsb-agent/SECURITY_AND_HARDENING.md`
- `/opt/lsb-agent/docs/status/2026-05-09-phase4b-t4-partial-completion.md`
- `/opt/lsb-agent/docs/status/2026-05-07-no-human-baseline-amendment-architect-plan.md` (referenced as plan-format model)
- `/opt/lsb-agent/data/results/family/0.2.json` (11 models)
- `/opt/lsb-agent/data/results/holidays/0.2.json` (9 models)
- `/opt/lsb-agent/packages/cdb_core/cdb_core/schemas.py` (DomainResult, WithinModelResult)
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/build.py` (currently a one-line stub)
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/README.md`
- `/opt/lsb-agent/scripts/publish.py` (currently `raise NotImplementedError`)
- `/opt/lsb-agent/apps/dashboard/index.html` (CSP issue with Google Fonts links — fixed in T4 by self-hosting)
- `/opt/lsb-agent/apps/dashboard/postcss.config.js`
- `/opt/lsb-agent/apps/dashboard/package.json` (react 18 → 19 bump rationalised in T4)
- `/opt/lsb-agent/apps/dashboard/public/_headers` (existing CSP, unchanged in Phase 5)
- `/opt/lsb-agent/apps/dashboard/src/App.tsx` (prototype, reverted in T0; rebuilt in T4)
- `/opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx` (prototype, reverted in T0; rebuilt in T6)
- `/opt/lsb-agent/apps/dashboard/src/data/types.ts` (prototype, reverted in T0; rebuilt in T4)
- `/opt/lsb-agent/apps/dashboard/public/family.json` (prototype dev-server stub, reverted in T0; replaced by published JSON from T3)
- Screenshots at repo root, moved to `/opt/lsb-agent/docs/status/2026-05-09-phase5-prototype-screenshots/` in T0.

---

**Final note on tooling.** I do not have Write / Edit / Bash tools available in this Architect-agent invocation, so this plan is delivered as the assistant's final message rather than written directly to `docs/status/2026-05-09-phase5-architect-plan.md`. The orchestrating agent (or Mark) saves this content to that path and commits it as `docs(arch): Phase 5 architect plan`. The plan is otherwise complete and ready for CDA SME + UI/UX dispatch.