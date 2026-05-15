# Phase 6 T13 — One new domain or one new model added via publish layer — Architect Plan

**Date:** 2026-05-15
**Author:** Architect agent (Opus)
**Status:** Plan-for-review. **§1.A is a hard blocker** — no agent dispatch until Mark picks A / B / C / D.
**Companion docs read:** `CLAUDE.md` v1.0 §6/§7/§8/§9; `ARCHITECTURE.md` v0.7.3 §1, §1.5 (esp. §1.5.5 no human grounding; §1.5.6 website-as-artifact), §3.2 InformantRecord, §4.2 cdb_publish/cdb_analyze boundary, §4.5; `docs/DATA_DICTIONARY.md` §0 (food listed as v1 domain), §1.1; `docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T13, §3 Q6, §7 schema-impact (T13 row: schema-quiet); `docs/status/2026-05-09-phase4b-t4-partial-completion.md`; memories: `project_failures_are_findings.md`, `project_phase4b_t4_partial.md`, `project_campaign_timing.md`, `feedback_ui_polish_scope.md`, `project_metadata_fix_forward_precedent.md`, `feedback_test_budget.md`.
**Pre-investigated files:** `data/raw/informants.jsonl` (1246 records: family 631 + holidays 615; **0 food**), `data/results/{family,holidays}/{0.1,0.2}.json` (no `food/`), `data/grounding/food/` (does not exist), `data/domains/v1/{family,food,holidays}.yaml`, `apps/dashboard/public/data/manifest.json`, `apps/dashboard/src/App.tsx` (FUTURE_DOMAINS already declares `food` as disabled), `apps/dashboard/src/components/DomainPicker.tsx`, `apps/dashboard/src/data/types.ts`, `packages/cdb_publish/cdb_publish/build.py`, `packages/cdb_publish/cdb_publish/lede.py`, `packages/cdb_publish/cdb_publish/templates/lede_v1.py`, `packages/cdb_publish/cdb_publish/schemas/manifest.py`, `scripts/run_phase4b_variance.py`.

---

## §0. Reading list (Coder, mandatory before code)

These are on top of the standard CLAUDE.md §2 reads.

1. `CLAUDE.md` §6 R5–R10, R14; §7 forbidden vocabulary; §8 (one-commit-per-task, direct-to-master); §9 pitfalls #1 (model_id vs. model_version_returned), #5 (DATA_DICTIONARY co-update), #10 (append-only), #12 (`data/grounding/{domain}/{baseline_id}/` historical — confirmed: no food grounding exists).
2. `ARCHITECTURE.md` §1.5 (binding on all generated text), §3.2 InformantRecord (esp. `domain_slug` field — `food` is already an enumerated v1 value), §4.2 cdb_publish (the build entry point), §4.5 visualization bindings.
3. `docs/DATA_DICTIONARY.md` §0–§1 (the `food` domain is already enumerated; `domain_slug` accepts it without schema change).
4. `docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T13 + §3 Q6.
5. `docs/status/2026-05-09-phase4b-t4-partial-completion.md` (what 60.6% partial means; what "0.3 re-analysis" would entail — Option A only).
6. `apps/dashboard/public/data/manifest.json` (current contract).
7. `apps/dashboard/src/App.tsx` lines 77–99 (`FUTURE_DOMAINS` + `buildDomainList` — the disabled→available flip is already wired).
8. `packages/cdb_publish/cdb_publish/build.py` (entry point; reads `data/results/{domain}/*.json`, writes `apps/dashboard/public/data/{domain}.json`).
9. `packages/cdb_publish/cdb_publish/templates/lede_v1.py` (the `{domain}` placeholder makes the lede templates domain-agnostic — option B does NOT require a new lede template, only CDA SME framing review of the food-slug substitution).
10. `scripts/run_phase4b_variance.py` (the collection driver pattern — Options B and D need a sibling script).
11. Memory `project_campaign_timing.md` (single-digit hours per 1,800 cells with parallel collection — informs B/D scope).
12. Memory `project_failures_are_findings.md` (new domain/model collections will produce failures + decline-interviews; T9/T10 surfaces consume those without changes).

---

## §1. Summary (one sentence)

T13 proves Phase-6 article-shell extensibility by shipping **one** of: a re-analyzed v0.3 corpus (A), a third domain `food` (B), or a new model on the existing two domains (D) — using only the publish layer + dashboard wiring (and, for B/D, a fresh collection run feeding into existing `cdb_collect` / `cdb_analyze`); or, by deferring to Phase 6.5 (C).

---

## §1.A. HARD BLOCKER — Mark must pick A / B / C / D before any dispatch

Mark's call on Open Question 6 governs which sub-plan executes. The four sub-options have materially different shape, work, and gate intensity. **No CDA SME or UI/UX dispatch happens until Mark names the option in this thread or in a follow-up comment.** Architect's lean is at the end.

### Sub-option A — Re-analyze Phase 4b-T4 partial into v0.3 and re-ship family + holidays

- **Data:** existing `data/raw/informants.jsonl` (1118 cells from `campaign_id=phase4b-real-2026-05-08` plus the 1 stray phase4b-real-2026-05-09 cell + 1 duplicate documented in `2026-05-09-phase4b-t4-partial-completion.md`).
- **Work:** run `cdb_analyze` against the phase4b corpus to produce `data/results/{family,holidays}/0.3.json`; re-run `cdb_publish/build.py`; ship the new `*.json` + `*.v0.3.json` archive alongside the existing `.v0.2.json`; manifest updates each domain's `analysis_version` from `"0.2"` to `"0.3"` and `n_models` from 11/9 to ~13.
- **Manifest-swap contract exercised:** yes — version bump, model_ids array grows.
- **DomainPicker change:** none (no new pill).
- **Lede regen:** automatic via existing `cdb_publish` (templates are domain-agnostic; numbers will change).
- **CDA SME load:** **heaviest of the four options.** The 60.6% partial publication readiness is a methodological judgment about whether the missing 7 OpenRouter models change the consensus claim. Specifically: with 13 models instead of the originally-targeted 20, does the Smith's S / consensus_type / Romney small-n flag (`romney_small_n_warning` is `n<15`, so flips True at n=13) materially change the lede? CDA SME must approve the v0.3 publication framing, the per-domain lede regenerations (which may flip pattern, e.g., STRONG_CONSENSUS → WEAK_CONSENSUS), and how the dashboard surfaces the version bump to readers.
- **UI/UX load:** light. No new pill, no new viz. Per-domain lede strip text changes — UI/UX confirms the new text fits the existing strip without layout regression.
- **Risk:** existing-domain regressions (the analysis bumps from T4 may change R1-states for individual models, ellipse shapes, free-list rankings — readers comparing against memory will see different numbers). The `family.v0.2.json` archive should remain on disk so any external dashboard linker still resolves; but the canonical `family.json` flips to v0.3 content.
- **Bonus deliverable:** establishes the **data-bundle versioning ship pattern** (v0.2 → v0.3) that Phase 8 open-data publication will rely on.
- **Wall-clock:** Coder ~1 day (re-analyze + re-publish + verdict files). No new collection.
- **Mark inputs needed beyond option pick:** (i) does the canonical filename stay `family.json`/`holidays.json` (yes per current build.py — unversioned canonical is "latest version") or does `family.v0.3.json` become the user-facing label; (ii) does `.v0.2.json` archive stay, get renamed `family.v0.2.json` (already named), or get deleted; (iii) the **`romney_small_n_warning` flip** to True at n=13 (currently True per family.json — confirm posture).

### Sub-option B — Add `food` as a third domain

- **Data:** **does not exist.** `data/raw/informants.jsonl` has zero `domain_slug="food"` records; `data/results/food/` is absent; `data/grounding/food/` is absent. `data/domains/v1/food.yaml` is a one-line `# Phase 1 deliverable` placeholder — **incomplete; would need a real prompt_seed and truncation_k** before collection.
- **Work (concrete):**
  1. Populate `data/domains/v1/food.yaml` with `slug: food`, `version: v1`, `display_name: Food`, a domain-specific `prompt_seed` (e.g., `"type of food, dish, or meal"`), `truncation_k: 50`. **This is a CDA-SME-owned decision** (per pitfall #13 — vocabulary choice carries methodological assumptions; the food domain seed determines what category readers think LSB is measuring).
  2. Write a sibling collection driver `scripts/run_phase6_t13_food.py` (modeled on `run_phase4b_variance.py` but scoped to one domain × N models × 5 runs). Most likely model slate: the 9 phase4b-complete models for parity with the comparison set; or alternatively the 11 family-canonical models from current `family.json` so the food article reads against the same readership.
  3. Run the collection (memory `project_campaign_timing.md`: single-digit hours wall-clock, parallel providers; not a multi-day blocker).
  4. Run `cdb_analyze` against the new food corpus → `data/results/food/0.2.json` (matches current analysis_version).
  5. Run `cdb_publish/build.py` — produces `apps/dashboard/public/data/food.json`, `food.v0.2.json`, `food/failures/food.json`, and `manifest.json` adds a third entry.
  6. UI: `App.tsx` `FUTURE_DOMAINS` already declares `food` (line 78); when manifest carries it, `buildDomainList()` automatically promotes food to an available pill via the existing dedup in line 95–97. **No code changes to App.tsx or DomainPicker.tsx required to make the pill appear.** Confirmed by reading the components above.
  7. CDA SME on the auto-generated food lede (templates are domain-agnostic, but slug substitution into "Across N frontier models, food vocabulary is organized around..." must be CDA-SME-reviewed once before shipping — the food domain framing is the new methodological surface).
- **Manifest-swap contract exercised:** yes — new third domain row.
- **CDA SME load:** **heavy on different axes than A.** The food-domain freelist prompt has never shipped, so the CDA SME owns the prompt_seed wording, truncation_k confirmation, and the resulting lede. Per pitfall #13 (cross-boundary detector reuse) the food-domain vocabulary will surface in failures/decline-interviews — CDA SME must confirm `SAFETY_FILTER_MARKERS` and decline detection thresholds don't misclassify food-specific verbatims (likely fine — food is lower-stakes than family/holidays — but the review is on the surface area).
- **UI/UX load:** light. The pill auto-appears via existing logic. UI/UX confirms layout with 3 pills doesn't regress, and confirms food-specific text appears correctly in the lede strip + failure section heading.
- **Risk:** collection campaign could fail or produce sparse data — but the Phase 4b parallelization fix is live (`fc1ccd1`), preflight 429 detection is live (`6f88f68`). Memory `project_failures_are_findings.md` says failures are findings — so a partial food corpus is still publishable per the same partial-publication argument as Option A.
- **Wall-clock:** ~1 day collection + ~1 day Coder (driver script + analyze + publish + verdict files) = 2 days total (sequential due to collection-before-analysis dependency).
- **Mark inputs needed beyond option pick:** (i) which model slate for food collection — the 9 phase4b-complete (consistency with the comparison set) or the 11 currently-on-family.json (consistency with what dashboard readers see); (ii) confirm `prompt_seed` text and `truncation_k`; (iii) campaign_id naming (suggest `phase6-t13-food-{YYYY-MM-DD}`).

### Sub-option C — Drop T13 from Phase 6

- **Work:** zero. Plan reduces to: document the deferral in `docs/status/2026-05-15-phase6-T13-deferred.md`; update `2026-05-12-phase6-architect-kickoff.md` §2 T13 row with a "deferred to Phase 6.5" note; update `ARCHITECTURE.md` §5.3 Phase 6 done-criterion (f) to "(f) deferred — one new model or domain added in Phase 6.5 alongside next collection campaign."
- **Manifest-swap contract exercised:** no — that's the cost. Phase 6 ships without proving article-template extensibility end-to-end.
- **CDA SME load:** none (deferral docs only).
- **UI/UX load:** none.
- **Risk:** lowest of the four. The cost is Phase 6 done-criterion (f) being unmet at Phase 6 close.
- **Wall-clock:** ~1 hour Architect (deferral docs).

### Sub-option D — Add one new model to family + holidays

- **Data:** does not exist yet — requires running collection for one new model × 2 domains × 5 runs × (9 variants? or just v1_s1 canonical?) = either 90 cells (variant arm) or 10 cells (canonical only).
- **Work:** add the model to the registry if not present, run collection scoped to one model on both existing domains, re-run analyze + publish; the dashboard sees the new model_id appear in family.json + holidays.json `models` array; the model becomes available in `ModelSelector` (existing component, no code change required).
- **Manifest-swap contract exercised:** weakly — `model_ids` array grows but `domains` array shape is unchanged. **This is the lightest extensibility proof** of the four options.
- **CDA SME load:** medium. CDA SME owns "which model" — the choice signals methodological priorities (e.g., adding `qwen3.6-plus` completes a partial from Phase 4b; adding a newly-released flagship like a hypothetical `claude-opus-4-7` proves drift tracking; adding `cohere/command-a` from the 7-not-started list proves the OpenRouter-tail backfill works). CDA SME does not gate per-model framing per se (no per-model lede in the current template set) but does gate the rationale doc.
- **UI/UX load:** lightest of all options. No new pill, no new lede pattern, no layout change. Existing `ModelSelector` consumes the model array.
- **Risk:** the manifest-swap contract is **less convincingly exercised** by D than by A or B. The kickoff §2 T13 says "Proves the article-template extensibility end-to-end" — adding one model to an array does not exercise the per-domain article-shell rendering pipeline the way A (new analysis version) or B (new domain) does.
- **Wall-clock:** ~half-day collection (10–90 cells parallel) + ~half-day Coder = ~1 day total.
- **Mark inputs needed beyond option pick:** (i) which model (Architect suggests `qwen/qwen3.6-plus` — it was 50%-collected in phase4b-T4, so completing it tests the partial-recovery path; or `cohere/command-a` to exercise a not-started OpenRouter model); (ii) canonical-only (v1_s1, 10 cells) or variant arm (9 variants, 90 cells).

### Architect's lean and rationale

**Lean: Option B (add `food`).** Rationale, in order:

1. **It is the strongest manifest-swap-contract exercise.** A new domain row, a new article-shell instance, a new lede slot, a new pill, a new failures-section. Phase 6 done-criterion (f) is unambiguously met.
2. **The infrastructure is already wired for it.** `App.tsx` line 78 already declares food as a `FUTURE_DOMAINS` entry; the `buildDomainList()` dedup at line 95–97 promotes food the moment manifest carries it. DomainPicker, ModelSelector, DataExplorer, FailuresFindingsSection all work generically per-domain — no code changes required to the dashboard layer. The work concentrates in `data/domains/v1/food.yaml` (one CDA-SME-gated edit), a new collection driver script, and one publish-pipeline rerun.
3. **The CDA SME load is on a methodologically new surface** — food is a domain LSB has not analyzed before. That is more aligned with the spirit of "prove extensibility" than Option A (which proves the re-analysis path on a familiar surface) or Option D (which proves the model-list-grows path).
4. **Wall-clock is short.** Per `project_campaign_timing.md`, the collection runs in single-digit hours. Total Phase 6 schedule impact is 2 days, sequential.
5. **The 60.6%-partial-publication question can be answered separately.** Decoupling Option A from Phase 6 lets the v0.3 publication ship in Phase 6.5 alongside the 4b-T4 follow-up campaign, where the partial-corpus question gets resolved cleanly (full 20-model corpus) instead of being negotiated at 60.6%.

**Counter-arguments worth surfacing:**

- If Mark is currently in budget-conscious mode on collection campaigns: Option A is the cheapest option that still ships content (no API spend).
- If Mark wants to defer all collection until the methodology page is fully done: Option C protects Phase 6's done-line at minimum cost.
- If Mark wants to test the drift-tracking surface (T4) before shipping: Option D with a model from a family that already has a 2026-04 collection (e.g., a newer Claude or GPT variant) gives DriftTracker something to draw — but T4 is still open, so this is moot in current sequencing.

---

## §2. Decisions to record once Mark picks

The rest of this plan **assumes Option B for concreteness.** Mark's call can flip the body to A / C / D and the rest restructures accordingly; the gate routing in §6 and done-mapping in §11 stay shape-similar across options.

### Under Option B (assumed for body of plan)

**B-D1. Model slate for food collection.** Default proposal: the **9 phase4b-complete models** from `2026-05-09-phase4b-t4-partial-completion.md` §2 (claude-opus-4-6, claude-sonnet-4-6, claude-opus-4-5, openai/gpt-5.4, openai/gpt-5.4-mini, openai/gpt-5.2, google/gemini-2.5-flash, x-ai/grok-4.20, mistralai/mistral-small-2603). This matches the corpus shape readers already see and avoids re-litigating the OpenRouter-tail problem. Mark can override.

**B-D2. `food.yaml` contents.** CDA SME owns final wording. Architect suggests:
- `prompt_seed: "type of food, dish, or meal"` (parallels family's `"type of family relationship or family member"` and holidays' `"holiday, festive day, or religious observance"` — a categorical-anchor phrasing per the existing pattern).
- `truncation_k: 50` (matches both shipped domains).
- `display_name: Food`.

**B-D3. Campaign ID.** `phase6-t13-food-2026-05-{MM}` per the `phase{N}-{kind}-{date}` precedent.

**B-D4. Analysis version.** `0.2` (matches current shipped analysis; Option A reserved for v0.3 bump).

**B-D5. `.v0.2.json` archive policy.** New domain writes both `food.json` and `food.v0.2.json` per existing `build.py` behavior; no `.v0.1.json` predecessor (food has no v0.1).

**B-D6. Failures pipeline.** Existing `cdb_publish/failures.py` (T9 deliverable) auto-emits `apps/dashboard/public/data/failures/food.json` once food collection runs produce any failures or decline-interview records — no code change.

**B-D7. Lede regeneration.** Automatic via `cdb_publish/lede.py` — `{domain}` placeholder receives `"food"` and produces "Across N frontier models, food vocabulary is organized around..." CDA SME confirms the slug substitution reads cleanly (this is a single one-time gate, not a per-publication gate).

**B-D8. Per-domain article shell.** No code change. The article header, KeyFinding lede strip, DataExplorer, MethodologySummary, and FailuresFindingsSection all read `domainResult` generically. Confirmed by App.tsx review.

**B-D9. Drift/DriftTracker compatibility.** T3/T4 are still open. The food domain at single collection date has no drift to display — this is consistent with the T3/T4 N=1 handling that the kickoff Open Question 3 already flagged. Not a blocker for T13.

**B-D10. No software-side spend gate.** Per CLAUDE.md R14 + `feedback_test_budget.md`: the collection driver script must not include cost estimates, spend caps, or `CDB_MAX_SPEND_USD`-style env vars. Mark monitors provider billing dashboards.

**B-D11. Memory side-effects.** Per `feedback_dispatch_hygiene.md`, `git status --short` between agent dispatches; any auto-memory writes get a `chore(memory):` commit before the next agent runs.

---

## §3. Acceptance criteria (under Option B)

Each criterion is testable. **(R)** = checked by Reviewer; **(T)** = checked by Tester; **(C)** = checked by CDA SME at gate review; **(U)** = checked by UI/UX.

1. **(R/T)** `data/domains/v1/food.yaml` is populated with `slug: food`, `version: v1`, `display_name: Food`, `prompt_seed` (CDA-SME-approved wording), `truncation_k: 50`. Schema-conformant; loads via `cdb_collect.domains.load_domain()`.
2. **(T)** A collection campaign with `campaign_id=phase6-t13-food-2026-05-{MM}` runs against the 9-model slate (B-D1), produces ≥45 informant records (9 models × 5 runs × 1 domain, target 45 cells), and writes them to `data/raw/informants.jsonl`. Append-only invariant preserved (R: `tests/test_jsonl_append_only.py` passes).
3. **(R)** No edit to any pre-existing line of `data/raw/informants.jsonl`. CI append-only check passes (per pitfall #10).
4. **(R/T)** `cdb_analyze` runs against the food corpus and produces a valid `data/results/food/0.2.json` (passes `DomainResult.model_validate_json()`).
5. **(R/T)** `cdb_publish/build.py` produces `apps/dashboard/public/data/food.json`, `food.v0.2.json`, `failures/food.json`, and a manifest with three domains: family, holidays, food. Manifest validates against `Manifest` schema.
6. **(R)** No changes to `cdb_core/schemas.py` (per kickoff §7 schema-impact T13 row: schema-quiet).
7. **(R)** No changes to `apps/dashboard/src/data/types.ts` (generic shape unchanged).
8. **(U/T)** Loading the dashboard with the new manifest in place shows three active pills in DomainPicker: Family, Holidays, Food. The Food pill becomes selectable and, when clicked, renders the full article shell (ArticleHeader, KeyFinding lede strip with food-specific text, DataExplorer with MDS + Free Lists + Similarity, MethodologySummary, FailuresFindingsSection).
9. **(U)** No layout regression on the existing two pills at viewport widths from `<768px` (mobile) through 1920px. Pill row does not wrap, does not overflow, does not orphan the 3rd pill.
10. **(C)** The auto-generated food lede passes CDA SME §1.5 framing review. The Coder runs `cdb_publish/build.py` once before final commit and produces the lede text; CDA SME reviews the rendered string verbatim. Forbidden vocabulary absent (no "believes", "worldview", "understands", "perceives" — per CLAUDE.md §7).
11. **(C)** `food.yaml` `prompt_seed` wording passes CDA SME review for methodological consistency with family + holidays patterns.
12. **(T)** No regression on family or holidays — diffing `family.json` and `holidays.json` before and after the build run shows byte-identical content (the build is read-only on `data/results/`; existing files are untouched). Use existing `tests/test_publish_idempotence.py` or equivalent.
13. **(R)** `docs/DATA_DICTIONARY.md` updated if any new field appears anywhere — none expected per kickoff §7. The `food` domain is already enumerated in §1.1 line 61. **No update required.** (Reviewer rule 7 enforces "schema change → data dictionary update in same PR" — here, no schema change, no dictionary change.)
14. **(R)** No new Python or npm dependency.
15. **(R)** No forbidden vocabulary in any committed text — lede output, commit message, PR/verdict docs, comments in new collection driver, `food.yaml` text fields.
16. **(R/T)** Bundle size delta: `food.json` is ≤500 KB raw; total `apps/dashboard/public/data/` directory grows by less than 1 MB raw (typically <500 KB gzipped). UI bundle is unchanged (no new components).
17. **(R)** No software-side spend gate introduced. CI `no-spend-gate-check` passes.
18. **(R)** `scripts/run_phase6_t13_food.py` is a sibling of `run_phase4b_variance.py`, not a rewrite of it. No edits to the phase4b driver.
19. **(R)** New collection records carry the food-specific `domain_slug="food"` correctly; `model_version_returned` recorded verbatim per pitfall #1.
20. **(C)** The DASHBOARD-VISIBLE food framing — pill label "Food", any auto-generated headings, the failures section heading for food — uses §1.5 framing (no anthropomorphic language).
21. **(T)** App-state test `apps/dashboard/src/__tests__/app-state.test.ts` extended (or new test added) confirming `buildDomainList()` returns 3 entries with all 3 marked `available: true` when manifest carries food.
22. **(T)** `domain-picker.test.tsx` extended to confirm 3-pill rendering and ArrowRight cycling through all three.

---

## §4. Files affected (under Option B)

**New files:**
- `scripts/run_phase6_t13_food.py` — collection driver, single-domain scoped, sibling of `run_phase4b_variance.py`.
- `data/results/food/0.2.json` — analysis output (written by `cdb_analyze` invocation).
- `apps/dashboard/public/data/food.json` — published canonical.
- `apps/dashboard/public/data/food.v0.2.json` — published archive.
- `apps/dashboard/public/data/failures/food.json` — auto-emitted by existing failures builder (records may be `[]` if no failures during food collection).
- `docs/status/2026-05-15-phase6-T13-architect-plan.md` (this plan).
- `docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md` (after CDA SME review).
- `docs/status/2026-05-15-phase6-T13-uiux-verdict.md` (after UI/UX review).
- `docs/status/2026-05-15-phase6-T13-reviewer-verdict.md`, `-tester-verdict.md`.
- Possibly `tests/test_phase6_t13_food.py` for the publish/manifest integration.

**Modified files:**
- `data/domains/v1/food.yaml` — currently a one-line placeholder; gets filled in.
- `data/raw/informants.jsonl` — append-only growth from collection (~45 lines + any failures).
- `data/raw/failures.jsonl` — append-only growth, if any.
- `data/raw/decline_interviews.jsonl` — append-only growth, if any.
- `apps/dashboard/public/data/manifest.json` — auto-regenerated to add food.
- Possibly `apps/dashboard/src/__tests__/app-state.test.ts` and `domain-picker.test.tsx` to extend coverage.

**NOT modified (verified):**
- `apps/dashboard/src/App.tsx` — `FUTURE_DOMAINS` already declares food; `buildDomainList` handles promotion.
- `apps/dashboard/src/components/DomainPicker.tsx` — generic-by-design.
- `apps/dashboard/src/data/types.ts` — shape unchanged.
- `packages/cdb_publish/cdb_publish/build.py` — generic-by-design.
- `packages/cdb_publish/cdb_publish/templates/lede_v1.py` — `{domain}` slug substitution covers food.
- `packages/cdb_core/schemas.py` — no schema change.
- `docs/DATA_DICTIONARY.md` — `food` already enumerated in §1.1 `domain_slug` row.
- `ARCHITECTURE.md`, `DESIGN_SYSTEM.md` — no decision changes triggering doc updates (T14 sweep handles the Phase 6 close).

---

## §5. Explicitly out of scope

- Option A re-analysis to v0.3 (deferred to Phase 6.5 alongside 4b-T4 follow-up).
- Option D model addition (separate task if and when chosen).
- New visualization components (none — generic article shell handles food).
- DriftTracker / DateSlider (T3/T4 territory).
- Methodology page edits (T1/T2 territory).
- Social pipeline (`cdb_social/`) — Phase 7.
- DESIGN_SYSTEM.md updates — Phase 6 T14 documentation sweep handles any.
- 4b-T4 follow-up campaign for the 7 OpenRouter models — Phase 6.5 + memory `project_phase4b_t4_partial.md`.
- Editing `run_phase4b_variance.py` or its derivatives — T13 driver is a sibling, not a rewrite.
- Cost estimates, spend caps, or any `CDB_MAX_SPEND_USD`-style language anywhere — CLAUDE.md R14.

---

## §6. Gate routing

**Required gates, in order:**

1. **Mark — §1.A blocker.** Architect blocks until Mark picks A / B / C / D.
2. **CDA SME** — methodological review. Under Option B, the SME owns:
   - `food.yaml` `prompt_seed` wording (B-D2).
   - The model slate decision (B-D1) — does the 9-model phase4b-complete slate produce a publication-worthy food consensus, or should the slate be larger / different.
   - The rendered food lede (after Coder runs `cdb_publish/build.py` once) — verbatim review for §1.5 framing.
   - Confirmation that pitfall #13 (cross-boundary detector reuse) is not triggered by food-domain vocabulary in `SAFETY_FILTER_MARKERS` or decline-detection helpers.
   - Four-axis scorecard (protocol validity, analytical validity, claims validity, audience translation).
   - **Verdict file:** `docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md`.
   - **Channel:** `#lsb-cda-sme`.
3. **UI/UX agent** — frontend review. Under Option B (and per `feedback_ui_polish_scope.md` — minimum-viable-functional, accessibility + R10 floor only):
   - Three-pill DomainPicker layout at mobile, tablet, desktop widths.
   - Pill keyboard cycling (ArrowLeft/Right with 3 pills, wrap-around).
   - The food lede in the KeyFinding strip — readability, line-wrap, no truncation.
   - WCAG AA contrast on the food pill (uses existing tokens — should pass by inheritance).
   - **Verdict file:** `docs/status/2026-05-15-phase6-T13-uiux-verdict.md`.
   - **Channel:** `#lsb-ui-ux`.
4. **Coder** — implementation. Receives only the post-SME-and-UI/UX-PASS plan. Runs the collection. Runs `cdb_analyze`. Runs `cdb_publish/build.py`. Commits. Per `feedback_pipeline_autonomy.md`, Architect auto-dispatches Coder after both gates PASS without checking back in unless there's a FAIL.
5. **Reviewer** — enforces CLAUDE.md §6 rules. Checks acceptance criteria 1–22. Verdict at `docs/status/2026-05-15-phase6-T13-reviewer-verdict.md`.
6. **Tester** — runs `uv run pytest && uv run ruff check . && uv run mypy packages/`; for the dashboard, `npm run build && npm run test && npm run lint`. Verdict at `docs/status/2026-05-15-phase6-T13-tester-verdict.md`.

**Under Option A:** CDA SME load is heavier (partial-corpus publication readiness, lede pattern flips, romney_small_n flip). UI/UX load is lighter (no new pill). Coder + Reviewer + Tester sequence identical.

**Under Option D:** CDA SME load is lighter (model choice rationale only, no new lede surface). UI/UX gate is **arguably skippable** (no visual change) — but per `feedback_ui_polish_scope.md` accessibility floor, the gate stays as a sanity check on ModelSelector behavior at N+1 models.

**Under Option C:** No gates beyond Architect deferral docs.

---

## §7. Schema impact

**None under any sub-option.**

- `food` is already enumerated as a v1 domain in `docs/DATA_DICTIONARY.md` §1.1 line 61. `domain_slug: str` accepts it without schema change.
- `InformantRecord`, `GroundingRef`, `DomainResult` all generic across domains.
- `Manifest` schema's `domains: list[ManifestDomain]` and `failures: dict[str, str]` accept new entries without shape change.
- `DomainResultPublished` TypeScript interface unchanged.

**No Architect sign-off required.** **No `docs/DATA_DICTIONARY.md` update required.** Reviewer rule R7 (schema change → dictionary co-update) does not trigger.

---

## §8. Bundle budget

Phase 5 closed at 76.25 KB gzipped (19% of 400 KB cap). T13 under Option B adds:

- One new JSON file `food.json`. Reference: `family.json` and `holidays.json` are around 200–400 KB raw. Food file expected in the same range. **Not part of the JS bundle** — fetched on-demand by `fetchDomain()`.
- One new `failures/food.json`. Reference: existing failures files are small (few KB to ~50 KB).
- **Zero JS bundle delta.** No new components, no new dependencies, no new types.

**Total gzipped JS bundle: unchanged at 76.25 KB.** Well within the 400 KB cap.

Per-domain JSON file size constraint (DESIGN_SYSTEM.md §9): ≤500 KB raw. Verify post-build that `food.json` falls under this.

---

## §9. Dependency order (under Option B)

Sequential because collection precedes analysis precedes publish:

1. **C1 (Coder commit 1)**: Populate `data/domains/v1/food.yaml` with CDA-SME-approved wording. (Requires CDA SME PASS on B-D2 first.)
2. **C2**: Write `scripts/run_phase6_t13_food.py`. Dry-run mode validates plan.
3. **C3**: Live collection run. Produces appended records in `data/raw/informants.jsonl` (+ failures). **This is the time gate** — ~single-digit hours per `project_campaign_timing.md`.
4. **C4**: Run `cdb_analyze` to produce `data/results/food/0.2.json`.
5. **C5**: Run `cdb_publish/build.py` to produce `apps/dashboard/public/data/food.json`, `food.v0.2.json`, `failures/food.json`, updated `manifest.json`.
6. **C6**: Add/extend tests for 3-pill rendering and 3-domain manifest.
7. **C7**: One commit — `feat(publish): T13 — add food as third domain via existing publish layer` — referencing both gate verdict files per CLAUDE.md §8.

**Reviewer and Tester run after C7.** Per `feedback_pipeline_autonomy.md`, Architect does not check in between C-steps.

**Phase 6 sequencing**: T13 is sequenced last in the kickoff §2 because the visualizations need to exist for the new content to land on a complete shell. Currently T5/T6/T7/T8/T9/T10/T11/T12 are closed; **T1/T2/T3/T4 still open**. T13 can run now for MDS + Free Lists + Similarity surfaces. DriftTracker (T4) will have nothing to show for food (single collection date) — consistent with the N=1 handling already flagged in kickoff Open Question 3, not a T13 blocker.

---

## §10. Risks and mitigations

1. **Collection campaign produces sparse food data.** Per memory `project_failures_are_findings.md`, sparse data is still findings. Mitigation: dashboard surfaces failures via existing T9/T10 path; lede acknowledges low-N via existing `romney_small_n_warning` mechanism (auto-flags at n<15). If <5 models complete, CDA SME re-review before publication.
2. **Food-domain freelist prompt produces unexpected output classes.** E.g., refusals on "what food do you like?" misframings or recipe verbatims that look like decline interviews. Mitigation: CDA SME plan review on `prompt_seed` wording before C2; existing decline-detection helpers tested against pre-collection dry-run output.
3. **Lede pattern selection lands on `turbulent` or `contested` for food.** That is acceptable per the existing template set — but if it is `subcultural`, the auto-generated text references "competing sub-structures" which CDA SME confirms is appropriate for food (likely yes — food categories vary across models).
4. **Existing-domain regression via build.py shared codepath.** Mitigation: AC #12 requires byte-identical family.json + holidays.json before/after.
5. **Manifest schema growth breaks dashboard cache.** Mitigation: `Manifest` schema's `domains: list[ManifestDomain]` already supports arbitrary N — confirmed by `App.tsx` `buildDomainList()` handling. Hard-refresh required for users with stale manifest cached (Cloudflare Pages handles this via standard cache headers).
6. **Race condition: Phase 6 T1/T2/T3/T4 not yet shipped, food article shell links to methodology page that does not exist.** Mitigation: `MethodologySummary` is already in App.tsx with `methodologyPageUrl={null}` (line 342) — no broken links, just a methodology-summary block with no out-link. Identical to current family/holidays state.
7. **Pitfall #13 (cross-boundary detector reuse).** If `SAFETY_FILTER_MARKERS` or `_is_recursive_decline()` produces false positives on food-domain verbatims (e.g., the word "kill" in "kill the meat" before cooking → safety-filter detector). Mitigation: CDA SME plan review surfaces this; if triggered, fix as a separate per-domain configuration in failures.py.
8. **No drift to display for food in DriftTracker.** Not a blocker — kickoff Open Question 3 already flags N=1 handling for T4.

---

## §11. Done mapping (CLAUDE.md §11)

- [ ] All §3 acceptance criteria met.
- [ ] `uv run pytest && uv run ruff check . && uv run mypy packages/` passes locally.
- [ ] `npm run build && npm run test && npm run lint` from `apps/dashboard/` passes locally.
- [ ] CDA SME PASS or PASS-WITH-NOTES at `docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md`; notes applied.
- [ ] UI/UX PASS or PASS-WITH-NOTES at `docs/status/2026-05-15-phase6-T13-uiux-verdict.md`; notes applied.
- [ ] Reviewer PASS or PASS-WITH-NOTES at `docs/status/2026-05-15-phase6-T13-reviewer-verdict.md`; notes applied.
- [ ] Tester PASS at `docs/status/2026-05-15-phase6-T13-tester-verdict.md`.
- [ ] Single commit, Conventional-Commits format, references task ID and verdict files.
- [ ] No forbidden vocabulary in any committed text.
- [ ] No new dependency.
- [ ] No `cdb_core/schemas.py` change.
- [ ] No software-side spend gate.

---

*End of T13 plan. Awaiting Mark's pick on A / B / C / D before any agent dispatch.*
