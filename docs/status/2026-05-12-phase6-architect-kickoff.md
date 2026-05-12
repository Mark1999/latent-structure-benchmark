# Phase 6 — Full Dashboard + Methodology Page — Architect Kickoff

**Date:** 2026-05-12
**Author:** Architect agent (Opus)
**Status:** Kickoff (not a plan-for-review). No CDA SME or UI/UX dispatch yet. Mark reads, directs what becomes a full plan.
**Companion docs read before drafting:** `ARCHITECTURE.md` (v0.7, §4.5, §5.3 Phase 6), `CLAUDE.md` v1.0, `DESIGN_SYSTEM.md` v0.4.4 (§11 Phase 6 inventory, §3.4 FreeListCompare, §3.6 DateSlider, §3.3.5 R1 states, §6 Methodology Page, §7 Accessibility), `apps/dashboard/src/App.tsx`, `apps/dashboard/src/components/DataExplorer.tsx`, `apps/dashboard/src/components/VizSwitcher.tsx`, `apps/dashboard/src/data/types.ts`, `apps/dashboard/public/data/{manifest,family,holidays}.json`, `docs/status/2026-05-11-phase5-T13-uiux-verdict.md` (Phase 5 closing summary), `project_failures_are_findings.md` memory.

---

## §1. Phase 6 scope statement

**Phase 6 turns the minimum viable dashboard into the full publication.** Phase 5 (closed 2026-05-11) shipped the article shell, the MDS plot with R1-state-encoded markers, a model selector, downloads, embed, and the MethodologySummary block. The three placeholder visualization tabs (Free Lists, Similarity, Drift) are visible but disabled. The methodology page is referenced by a `methodologyPageUrl={null}` and does not yet exist. The dashboard hides its nav on mobile with no replacement. Failures and refusals — first-class findings per Mark's binding directive (2026-04-23, memory `project_failures_are_findings.md`) — are not exposed to the public reader.

**Phase 6 is "done" when:** (a) all three Phase-6 visualization tabs are interactive with full uncertainty rendering (FreeListCompare with per-term bootstrap inclusion-frequency bars, SimilarityHeatmap with cell-level CIs, DriftTracker with error bars and within-noise band) per ARCHITECTURE.md §4.5; (b) the full methodology page exists at a real route, written or reviewed personally by Mark per ARCHITECTURE.md §5.3 Phase 6, with CDA-ancestry citations and the §1.5 framing in plain English; (c) the "Read as table" toggle satisfies DESIGN_SYSTEM.md §7 on every visualization (no more T6/Phase-5-deferral posture); (d) the mobile hamburger menu replaces the `display: none` site-header nav from T13; (e) a failures-as-findings surface exposes the verbatim refusal/decline records that already exist in `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl`, per Mark's 2026-04-23 directive; (f) one new model or one new domain (Mark's call) has been added through the publish layer to prove the article-template extensibility; (g) the data dictionary, ARCHITECTURE.md, and DESIGN_SYSTEM.md are updated to match.

**Explicitly OUT of Phase 6:**

- The Phase 4b T4 follow-up campaign and 0.3 re-analysis (deferred from Phase 5; still deferred — `project_phase4b_t4_partial.md`).
- Researcher grounding submission UI (architectural debt from v0.7 §4.2.5 but moot under the 2026-05-07 amendment).
- The social pipeline (`cdb_social/`) — that is Phase 7.
- Backblaze B2 + Zenodo open-bundle publication — Phase 8.
- The "follow-up interview" *protocol design* (already designed and producing data; what is in scope is *displaying* those records). Any change to the protocol itself is CDA-SME-gated and remains a separate workstream.
- Public launch readiness (security headers, CSP audit, frame-ancestors relaxation hardening, robots.txt, SECURITY.md). Phase 8.
- Page routing framework choice if Mark decides methodology page is a single long-scroll page (then no router is needed; T1 changes shape — see Open Question 1).

---

## §2. Task decomposition

Sized for Coder one-feature-or-one-package PRs. Gates per task. Dependency edges noted.

### T1 — Routing decision + methodology page skeleton + nav wiring

**One-line:** Decide single-page-scroll vs. multi-route methodology; ship the skeleton (component template, anchor links if single-page, react-router-dom v6 routes if multi-page); wire site-header nav `Methodology` / `Data` / `About` to real anchors or routes; set `methodologyPageUrl` on `MethodologySummary` to point to the real page.

**Gates:** CDA SME (page structure, ancestry-citation placement, plain-English framing of §1.5 — methodology page is *the* defensibility document; the lede generator on every chart is downstream of these words). UI/UX (DESIGN_SYSTEM.md §6 page structure, typography on long-form prose, citation block visual). **No prose written yet** — that is T2.

**Dependencies:** Mark must answer Open Question 1 (routing shape) and Open Question 2 (long-scroll vs. multi-section) before this is planned in full.

**Sequencing:** Must precede T2 (Mark writes prose into the skeleton) and T12 (hamburger nav targets real routes/anchors).

---

### T2 — Methodology page prose

**One-line:** Mark writes (or personally reviews and finalizes) the methodology page prose for the seven sections in DESIGN_SYSTEM.md §6.1. The Coder builds *zero* prose for this — the Coder builds the template at T1, ports Mark's writing into TSX, and ensures the citation block and limitation cards render the Markdown that Mark approves verbatim.

**Gates:** CDA SME on the four axes (this is the single most claims-validity-sensitive surface in the whole project). UI/UX on the rendered result.

**Dependencies:** T1 (template). Blocking dependency on Mark's writing time — not a Coder-only task.

**Sequencing:** Serial after T1.

---

### T3 — `cdb_publish` drift data layer (`drift/{model_family}.json`)

**One-line:** Extend `cdb_publish/build.py` to emit `apps/dashboard/public/data/drift/{model_family}.json` per ARCHITECTURE.md §4.5 spec. Each file contains, per `(domain, model_version_returned, collection_date)`, MDS coordinates, Procrustes drift vs. first observation, and bootstrap CI. Unit of analysis: `model_version_returned` × `collection_date`, **not** `model_id` (CLAUDE.md §9 pitfall #1). Update `data/types.ts` with the new `DriftJson` interface.

**Gates:** CDA SME (drift score = Procrustes distance per §4.5; threshold 0.15 for divergence event matches social-trigger threshold; bootstrap CI propagation through MDS; what counts as "first observation" if a model family has only one observation date in the current 0.2 corpus). **No UI/UX** — this is backend.

**Dependencies:** none code-side, but Mark must answer Open Question 3 (temporal axis convention: collection_date vs. version index?) before plan finalization.

**Sequencing:** T3 (data) must precede T4 (DriftTracker UI). Can run in parallel with T5 / T7 / T8.

---

### T4 — `DriftTracker.tsx` + `DateSlider.tsx`

**One-line:** Build the third Phase-6 viz tab. Longitudinal D3 (or React+SVG hand-rolled per Phase 5 precedent) chart with collection date on the x-axis and Procrustes drift score on the y-axis. Bootstrap CI bands on every point. Date slider scrubs MDS plot model positions in the explorer's MDS tab. `VizSwitcher` enables the "Drift" tab and removes its `aria-disabled`. Reads `/data/drift/{model_family}.json`.

**Gates:** CDA SME (drift visualization claims, the within-noise band derived from the §5.3 prompt-sensitivity study; how to handle a model with only one collection date — show as "no drift data yet" or hide the model? The R10 binding is no point estimates without uncertainty, so a one-observation model has no drift line to draw and must be handled cleanly). UI/UX (chart layout, DateSlider per DESIGN_SYSTEM.md §3.6, accessibility of the scrub interaction).

**Dependencies:** T3 (data). Independent of T5 / T7.

**Sequencing:** After T3.

---

### T5 — `SimilarityHeatmap.tsx`

**One-line:** Build the Plotly (or hand-rolled-SVG — see Open Question 4) heatmap viz tab. Cells show similarity from `similarity_matrix`; hover tooltip shows `similarity ± 95% CI` from `similarity_ci` (both already in published JSON). Cells whose CI crosses null shown with reduced saturation per ARCHITECTURE.md §4.5. `VizSwitcher` enables the "Similarity" tab.

**Gates:** CDA SME (what is the "null" threshold for the reduced-saturation rule? `0.5` per the diagonal pattern in the 0.2 data? Mark needs to confirm or CDA SME proposes). UI/UX (heatmap color scale — Phase 5 design tokens have no diverging or sequential scale defined; UI/UX adds one to DESIGN_SYSTEM.md §1.2 before Coder dispatch).

**Dependencies:** none — data already published. Independent of T3 / T4 / T7.

**Sequencing:** Can parallelize with T3, T7.

---

### T6 — Heatmap color scale design system update

**One-line:** UI/UX agent extends DESIGN_SYSTEM.md §1.2 with a sequential or diverging color scale token set (3–5 stops). Mark approves the palette choice.

**Gates:** UI/UX (owns this), CDA SME notes only (sequential scale must encode the "CI crosses null" reduced-saturation rule visually without color-confusing R1-state markers).

**Dependencies:** none. Precedes T5 (so T5 has tokens to consume).

**Sequencing:** Before T5.

---

### T7 — `FreeListCompare.tsx`

**One-line:** Build the side-by-side ranked-term-list viz tab per DESIGN_SYSTEM.md §3.4. Each column = one selected model. Terms ranked by Sutrop CSI salience (already in published JSON as `sutrop_csi`). Per-term bootstrap inclusion-frequency bar next to each pill (ARCHITECTURE.md §4.5 binding — uncertainty mandatory). Hover on a term highlights it across all columns. `VizSwitcher` enables the "Free Lists" tab.

**Gates:** CDA SME (the per-term bootstrap inclusion-frequency is **not yet** in the published JSON — `free_lists` is the consensus list, no per-bootstrap-sample data. Either `cdb_publish` adds that field, or CDA SME approves a fallback uncertainty representation. This is a binding R10 concern. Plan must resolve this before Coder dispatch). UI/UX (column layout, pill design, mobile horizontal-scroll behavior per §8).

**Dependencies:** possibly T7a — a `cdb_publish` extension to emit `freelist_bootstrap_inclusion.json` or fold inclusion frequencies into the existing domain JSON. CDA SME plan review will resolve this.

**Sequencing:** After T7a if T7a is required.

---

### T7a — `cdb_publish` freelist bootstrap inclusion frequencies (conditional on CDA SME)

**One-line:** Extend `cdb_publish/build.py` to emit per-term, per-model bootstrap inclusion frequency (the fraction of bootstrap samples in which a term appeared in that model's free list). New field on `DomainResultPublished` or new sibling file.

**Gates:** CDA SME (only if T7 plan review determines existing JSON is insufficient for R10 compliance).

**Dependencies:** none code-side.

**Sequencing:** Before T7 if required.

---

### T8 — `AccessibilityTableToggle.tsx` + `ScreenReaderSummary.tsx`

**One-line:** Build the "Read as table" toggle per DESIGN_SYSTEM.md §7 — every viz renders accessible HTML table when toggled. Build `ScreenReaderSummary.tsx` for hidden prose descriptions of each chart's key finding. This closes the §7 binding and the §12.6 Phase-5 deferral.

**Gates:** UI/UX (table format per viz; the four tables — MDS coords, Free Lists, Similarity, Drift — have different shapes; UI/UX specifies). CDA SME on the screen-reader summary copy (it is generated text *about* the models; §1.5.4 forbidden vocabulary applies; reusing the lede generator is one option but ScreenReaderSummary may need its own template).

**Dependencies:** T4 (Drift), T5 (Heatmap), T7 (FreeList) — toggle needs all four viz to exist before it makes sense to ship.

**Sequencing:** After T4, T5, T7. Can parallelize with T11.

---

### T9 — Failures-as-findings data layer

**One-line:** Extend `cdb_publish/build.py` to emit `apps/dashboard/public/data/failures/{domain_slug}.json` — verbatim records from `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl`, joined by `domain_slug`, with the §1.5 framing applied (this is a finding, not a defect). Surfaces refusal `response_verbatim`, follow-up `prompt_verbatim` + `response_verbatim`, and `originating_outcome_class`. Sanitization wrapper per `SECURITY_AND_HARDENING.md` §3.3.

**Gates:** CDA SME (this is the single most claims-validity-sensitive new surface in Phase 6 — Mark's 2026-04-23 directive said framing matters; "model X refused" is one decision, "model X declined to categorize" is another, "model X produced no parseable output" is a third. CDA SME owns the taxonomy and the framing copy. Also: which records are public-eligible? The failures file is currently un-redacted developer data — CDA SME confirms it is safe to publish verbatim, or specifies redaction rules.) **No UI/UX gate on this task** — backend only.

**Dependencies:** none code-side. Schema-touch: probably none if it reads existing schemas, but Architect sign-off if any `cdb_core/schemas.py` change is needed.

**Sequencing:** Before T10 (UI surface).

---

### T10 — `FailuresAsFindings.tsx` + dashboard entry point

**One-line:** Build the public-facing failures-as-findings display. Per ARCHITECTURE.md §1.5.6, this is first-class evidence — not a debug log. The dashboard entry point is either (a) a per-domain `FailuresFindingsSection` rendered below the MethodologySummary, or (b) a separate `/failures/{domain}` route, or (c) inline annotations on model markers in the MDS plot ("model X declined; click to see why"). Mark answers Open Question 5.

**Gates:** CDA SME (framing copy: the heading, the per-record label vocabulary, the §1.5 binding). UI/UX (layout, expandable raw-log accordion, "View raw response" pattern, no decorative animation per §0).

**Dependencies:** T9. Possibly T1 if option (b) is chosen and routing is required.

**Sequencing:** After T9.

---

### T11 — Mobile hamburger nav

**One-line:** Replace the T13 `display: none` site-header nav with a real hamburger menu at `<768px`. Closes the T13 mobile-deferral note. Includes focus trap, ARIA dialog semantics, and close-on-outside-tap per WCAG.

**Gates:** UI/UX (DESIGN_SYSTEM.md §8 needs a hamburger spec section — currently only one sentence; UI/UX extends it before Coder dispatch). CDA SME not required (no methodology surface).

**Dependencies:** T1 (so the menu targets real routes or anchors, not dead links).

**Sequencing:** After T1. Independent of T3 / T4 / T5 / T7.

---

### T12 — Mobile bottom-drawer for ModelSelector (DESIGN_SYSTEM.md §8 deferred from T13)

**One-line:** Replace the T13 stacked-below-on-mobile layout with a true bottom-drawer overlay for the model-selector panel at `<768px`. Includes scroll management, focus trap, overlay positioning. T13 verdict deferred this to Phase 6 explicitly.

**Gates:** UI/UX (drawer animation, dismiss interactions, focus management).

**Dependencies:** none — independent of viz tabs.

**Sequencing:** Can parallelize with T3 / T4 / T5 / T7 / T11.

---

### T13 — One new domain or one new model added via publish layer

**One-line:** Adds either (a) a new domain (e.g., `food`) from existing 0.2 raw data through `cdb_publish`, or (b) one new model added to family + holidays. Proves the article-template extensibility end-to-end and exercises the manifest-swap contract. **Not a backend-pipeline task** — uses existing raw data; if no new collection has happened, T13 either uses Phase 4b-T4 partial data (per CDA SME approval) or is dropped from Phase 6 and rescheduled.

**Gates:** CDA SME (which domain; partial-data publication readiness; the per-domain lede). UI/UX (DomainPicker pill addition; lede strip update).

**Dependencies:** none in code; depends on Mark's call about data availability (Open Question 6).

**Sequencing:** Last, after the visualizations exist so the new content lands on a complete article shell.

---

### T14 — Documentation sweep

**One-line:** Update `ARCHITECTURE.md` (Phase 6 deliverables checked off; drift methodology section if §4.5 needs sharpening from T3/T4 review; failure-display section if T10 introduces new conventions), `DESIGN_SYSTEM.md` (component inventory §11, any new tokens, any new sections — heatmap palette, hamburger spec, failures display, table-toggle spec), `docs/DATA_DICTIONARY.md` (drift file fields; failures-display fields; any schema changes), `CLAUDE.md` (new pitfalls — e.g., the temporal-axis convention from T3).

**Gates:** CDA SME (any §1.5 / §1.5.4 update). UI/UX (any visual decision codification).

**Dependencies:** all prior tasks; this is the closing task.

**Sequencing:** Last.

---

## §3. Open questions for Mark (must be answered before Architect finalizes the plan)

1. **Methodology page: single long-scroll page or multi-route with anchors?**
   Single-page-scroll keeps the bundle simple, avoids adding `react-router-dom`, and matches the OWID convention of one-article-per-page. Multi-route gives sections their own permalinks but introduces a routing dependency the dashboard currently does not have. *Recommendation:* single long-scroll with anchor IDs (`#what-is-cda`, `#how-we-collect`, `#limitations`), reachable via `methodologyPageUrl='/methodology'` and an HTML page that's a separate Vite entry — no `react-router-dom` needed. Mark confirms or overrides.

2. **Methodology page: single page or multiple pages (e.g., separate /methodology and /data and /about)?**
   Related to Q1. The site-header nav currently has `[Explore] [Methodology] [Data] [About]`. Three separate pages = three routes = react-router. One page with three sections = one route, three anchors. Mark's call.

3. **DriftTracker temporal axis convention: collection_date (real wall-clock) or version index (1st, 2nd, 3rd observation)?**
   ARCHITECTURE.md §4.5 says "collection date on the x-axis" but the 0.2 corpus has at most one observation per model so this is hypothetical until a second collection campaign runs. If we ship DriftTracker in Phase 6 against the 0.2 data, every model has exactly one point — there is no drift to display. Options: (a) defer DriftTracker until a second collection campaign produces multi-date data; (b) ship the empty DriftTracker with a clear "no temporal data yet — drift visualization activates when the next collection round completes" affordance; (c) build a synthetic-data demo mode for Phase 6 launch and switch to real data on the next collection.

4. **SimilarityHeatmap: Plotly (per ARCHITECTURE.md §4.5) or hand-rolled SVG (per the Phase 5 MDSPlot precedent)?**
   Plotly was the original choice for "fast to build, good defaults, built-in error bars." Phase 5 demonstrated that hand-rolled SVG meets the bundle-size cap and is fully accessible. Plotly adds ~80 KB gzipped — pushes the dashboard from 76 KB → 156 KB, still well under the 400 KB cap. Mark's call: budget room for Plotly's convenience, or hold the line on hand-rolled?

5. **Failures-as-findings dashboard entry point:**
   (a) per-domain `FailuresFindingsSection` below the MethodologySummary on each domain page; (b) standalone `/failures/{domain}` route; (c) inline markers on the MDS plot — refused/declined models appear with a distinct visual treatment, click to expand verbatim record. Option (c) is the most "the mismatch is the finding" interpretation but is the most design-intensive. Option (a) is the lowest-friction. Memory `project_failures_are_findings.md` says "the dashboard must call out failed runs and allow the website viewer to review the reasons why and the raw logs" — that supports (a) or (b) over (c), with raw logs reachable from the entry point.

6. **T13 new content: which domain or which model, and what data?**
   Phase 4b-T4 has a 60.6% partial corpus; the Phase 5 plan deferred the 0.3 re-analysis. Phase 6's T13 has three sub-options: (a) re-analyze 4b-T4 partial into 0.3 and ship the same two domains with the new corpus (less interesting, more re-analysis work); (b) add `food` as a third domain from existing raw data (if any 0.2-vintage food collection exists) or schedule a new food-domain collection now (delays Phase 6 by collection time); (c) drop T13 from Phase 6 and reschedule with the next collection campaign. Mark decides.

7. **(Bonus question, not blocking)** — **`AccessibilityTableToggle.tsx`** scope: does the toggle stay inside each viz component (per the §7 spec — "every visualization has a toggle") or does it become a single explorer-level toggle that switches the entire DataExplorer to table mode? Per-viz is more standard; explorer-level is one fewer toggle for the journalist to discover. UI/UX agent has authority here but Mark's preference would shortcut the back-and-forth.

---

## §4. Recommended T1 and rationale

**Recommended T1: T2 (methodology page prose) — preceded by T1 (skeleton) only as a same-PR adjunct.**

The full ordering recommendation is **T1 → T2 first**, before any visualization work, for three reasons:

1. **The methodology page is the project's defensibility document.** ARCHITECTURE.md §5.3 Phase 6 + §1.5.6 + DESIGN_SYSTEM.md §6 say "Mark writes or reviews personally — not Coder-generated" and "load-bearing for the project's defensibility." Every Phase 6 visualization links to this page from a tooltip or footnote. Shipping a DriftTracker tooltip that says "see methodology page for drift score definition" before the methodology page exists creates dead links and locks in copy that may need to change once the page is written.

2. **It is Mark's calendar bottleneck, not the Coder's.** Every other Phase 6 task is Coder-rate-limited. T2 is Mark-rate-limited. Front-loading it means Mark's writing time happens in parallel with Coder work on T3/T5/T7 (data-and-viz tasks that don't depend on T2), and the page is finished by the time T8/T10/T14 need to link into it.

3. **It tightens the §1.5 framing for the lede generator.** The lede generator in `cdb_publish` produces copy that the methodology page contextualizes. If the methodology page rewrites how LSB describes "corpus lens" or how it frames the OCI / R1-state distinction in plain English, those framing improvements will propagate back into the lede templates as a bonus side effect, before Phase 7 social-pipeline drafters lock in further generated copy.

**If T1 (routing + skeleton) and T2 (prose) cannot be one PR**, the actual Coder T1 is the skeleton, and T2 is a follow-up Mark-authored PR that ports prose into the skeleton. The recommendation stands either way: methodology page first.

**Parallel track from day one:** T3 (drift data layer) and T6 (heatmap color tokens) are gate-light and Coder-independent of T1/T2. They can run in parallel with T2's Mark-writing window. So the practical dispatch order for the Coder agent is:

- **PR 1:** T1 — routing + methodology page skeleton (UI/UX-gated; CDA SME gates Mark's prose at T2, not the skeleton).
- **PR 2 (parallel):** T3 — drift data layer (CDA SME plan-gated).
- **PR 3 (parallel):** T6 — heatmap color tokens (UI/UX-gated).
- **PR 4:** T2 — methodology page prose (CDA SME + UI/UX gates; Mark-authored).
- Then T4 / T5 / T7 / T7a after their dependencies clear.

---

## §5. ARCHITECTURE.md / DESIGN_SYSTEM.md sections to draft or update during Phase 6

| Section | Doc | Status | Triggered by |
|---|---|---|---|
| §4.5 DriftTracker | ARCHITECTURE.md | Update — sharpen "first observation" semantics, what to do when N=1 collection date, prompt-sensitivity "within-noise" band derivation | T3 / T4 plan review |
| §4.5 FreeListCompare uncertainty | ARCHITECTURE.md | Update — explicit bootstrap-inclusion-frequency field or sibling JSON | T7 plan review |
| **New §4.5.x Failures-as-findings dashboard surface** | ARCHITECTURE.md | **New section** | T9 / T10 plan |
| §5.3 Phase 6 task list | ARCHITECTURE.md | Update — Phase 6 deliverables checked off as tasks complete | T14 |
| §1 Component Inventory (§11) | DESIGN_SYSTEM.md | Update — move Phase 6 components out of the inventory backlog, add `FailuresAsFindings.tsx` | T14 |
| §1.2 Color Palette | DESIGN_SYSTEM.md | Update — heatmap sequential or diverging scale tokens | T6 |
| **New §8.x Mobile hamburger menu** | DESIGN_SYSTEM.md | **New section** | T11 plan review |
| §8 Mobile bottom-drawer | DESIGN_SYSTEM.md | Update — full spec replacing the T13 deferral note | T12 plan review |
| §6 Methodology page | DESIGN_SYSTEM.md | Update — confirm or override final structure, citation-block visual, limitation-card visual | T1 / T2 |
| §7 Accessibility — table toggle | DESIGN_SYSTEM.md | Update — per-viz table formats, single-toggle-vs-per-viz resolution | T8 plan review |
| §12.8 (new) Heatmap visual | DESIGN_SYSTEM.md | **New §12.x subsection** | T5 plan review |
| §12.9 (new) Drift visual + DateSlider | DESIGN_SYSTEM.md | **New §12.x subsection** | T4 plan review |
| §12.10 (new) Free List visual | DESIGN_SYSTEM.md | **New §12.x subsection** | T7 plan review |
| §12.11 (new) Failures-as-findings visual | DESIGN_SYSTEM.md | **New §12.x subsection** | T10 plan review |
| **New methodology section: "Drift score methodology"** | Methodology page (T2) | **New** | T2 |
| **New methodology section: "How we handle refusals and declines"** | Methodology page (T2) | **New** | T2 |
| §10 DATA_DICTIONARY.md | docs/DATA_DICTIONARY.md | Update — drift JSON file shape; failures JSON file shape | T3 / T9 |

---

## §6. Reading list bundled per task

(Coder must read these on top of the common `ARCHITECTURE.md` + `CLAUDE.md` + `DESIGN_SYSTEM.md` set per CLAUDE.md §2.)

- **T1:** `ARCHITECTURE.md` §5.3 Phase 6, `DESIGN_SYSTEM.md` §6, T13 verdict for nav posture.
- **T2:** All of `ARCHITECTURE.md` §1.5 (binding on every word), `docs/SME_REVIEW.md`, `docs/BOOTSTRAP_DESIGN.md` (for the bootstrap section), Romney/D'Andrade/Weller/Borgatti citation list (Mark already has these).
- **T3:** `ARCHITECTURE.md` §4.5 DriftTracker, §3.2 InformantRecord (`model_version_returned`, `collection_date` fields), `cdb_analyze/drift.py` (if extant), `CLAUDE.md` §9 pitfall #1.
- **T4:** T3 task plus `DESIGN_SYSTEM.md` §3.6 DateSlider, §3.3.5 R1 states (composes with drift markers).
- **T5:** `DESIGN_SYSTEM.md` §3.3 (Plotly-or-not — see Open Question 4), `ARCHITECTURE.md` §4.5 Heatmap binding.
- **T6:** `DESIGN_SYSTEM.md` §1.2 color tokens, §7 accessibility (WCAG AA 3:1 graphical contrast on chart cells).
- **T7:** `DESIGN_SYSTEM.md` §3.4 FreeListCompare, `ARCHITECTURE.md` §4.5 FreeListCompare uncertainty binding.
- **T7a:** `cdb_publish/build.py`, `cdb_analyze` bootstrap code, `docs/BOOTSTRAP_DESIGN.md`.
- **T8:** `DESIGN_SYSTEM.md` §7 + §12.6 deferral note.
- **T9:** `data/raw/failures.jsonl`, `data/raw/decline_interviews.jsonl`, `cdb_core/schemas.py` `DeclineInterview` (line 555), memory `project_failures_are_findings.md`, `ARCHITECTURE.md` §1.5.6, `SECURITY_AND_HARDENING.md` §3.3 (LLM-output sanitization).
- **T10:** T9 plus `DESIGN_SYSTEM.md` §1.5, §6 (cross-references to methodology).
- **T11:** `DESIGN_SYSTEM.md` §2.2, §8, T13 verdict (current `display: none` posture).
- **T12:** `DESIGN_SYSTEM.md` §8, T13 verdict (current stacked posture).
- **T13:** `docs/status/2026-05-09-phase4b-t4-partial-completion.md`, `cdb_publish/build.py`, manifest schema.
- **T14:** all of the above.

---

## §7. Schema impact summary

| Task | `cdb_core/schemas.py` touched? | DATA_DICTIONARY.md co-update required? |
|---|---|---|
| T1 | no | no |
| T2 | no | no |
| T3 | possibly — new `DriftPoint` published-only schema in `cdb_publish/schemas/` (NOT in cdb_core) → no Architect-sign-off-required | yes (drift JSON shape documented) |
| T4 | no (read-only) | no |
| T5 | no | no |
| T6 | no | no |
| T7 | no | no |
| T7a | possibly — new bootstrap-inclusion field on `DomainResultPublished` (NOT `cdb_core`) | yes |
| T8 | no | no |
| T9 | **no expected — reads existing `Failure` + `DeclineInterview`**. If `DeclineInterview` needs a `publish_redacted` boolean or similar, that is a `cdb_core` change requiring Architect sign-off + DATA_DICTIONARY.md update in the same PR per CLAUDE.md R6 | conditional |
| T10 | no | no |
| T11 | no | no |
| T12 | no | no |
| T13 | no | no |
| T14 | n/a | yes (this is the doc sweep) |

**Architect sign-off needed:** T9 *only if* CDA SME plan review determines a redaction field is required on `DeclineInterview`. Otherwise Phase 6 is schema-quiet.

---

## §8. Bundle budget watch

Phase 5 closed at 76.25 KB gzipped (19% of 400 KB cap). Phase 6 adds three components and a methodology page. Rough estimates (gzipped):

- FreeListCompare ~6 KB
- SimilarityHeatmap (hand-rolled) ~7 KB; (Plotly) ~80 KB
- DriftTracker + DateSlider ~10 KB
- AccessibilityTableToggle + ScreenReaderSummary ~4 KB
- FailuresAsFindings ~6 KB
- Hamburger nav + bottom-drawer ~5 KB
- Methodology page (separate Vite entry — not in main bundle if Open Question 1 goes single-entry; otherwise ~8 KB)

**Hand-rolled heatmap path:** ~115 KB total — well within cap.
**Plotly heatmap path:** ~190 KB total — within cap but uses 47% of the budget for one viz.

Recommend hand-rolled to preserve room for Phase 7/8 surfaces (citation modals expansion, embed iframe sandbox, social-pipeline preview cards).

---

## §9. Risks and watch-items

1. **Methodology page is Mark-rate-limited.** Phase 6 cannot close until T2 prose is finished. Schedule slip on T2 = schedule slip on T8 (Read-as-table screen-reader summaries reference methodology), T10 (failures display links to methodology framing), and the lede-generator framing dependency. Front-load.

2. **DriftTracker may be premature.** If the 0.2 corpus has one collection date per model, the drift chart has nothing to draw. Mark's answer to Open Question 3 decides whether T3/T4 ship in Phase 6 at all or defer to a "Phase 6.5 after next collection campaign."

3. **Failures-as-findings raw-log publication is a privacy-and-claims-sensitive surface.** The `data/raw/failures.jsonl` was developer-facing until now. Public publication means: (a) provider response bodies become reader-visible (legal review? T&C compliance with providers?); (b) refusal copy from models becomes quotable text that may embarrass providers (the §1.5 framing is the protection — but the CDA SME owns whether the framing is sufficient). T9 plan review must surface this explicitly; if Mark wants legal review before publication, T10 defers.

4. **§6.2 prompt caching obligation.** Any new prompt the lede generator or any agent-orchestration path adds in Phase 6 (e.g., a per-domain methodology-page lede helper) must use Anthropic prompt caching per ARCHITECTURE.md §6.2 binding. Architect plans will call this out per-task where applicable; Reviewer enforces.

5. **No software-side spend gates.** CLAUDE.md R14 / memory `feedback_test_budget.md` — no Phase 6 task is allowed to introduce cost estimates, spend caps, or `CDB_MAX_SPEND_USD`-style code. The CI grep check enforces. Architect plans will not include cost-cap paragraphs.

---

*End of kickoff. Mark reads this, answers §3 open questions, directs which subset becomes the first Phase 6 plan-for-review. The Architect drafts the full plan with CDA SME + UI/UX dispatch only after Mark's direction.*
