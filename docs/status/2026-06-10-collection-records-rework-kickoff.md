# Collection Records Rework Kickoff: Impact, Taxonomy, Successful Records, Raw Exchanges

**Status:** Decision surface for Mark. Planning doc, no CDA SME gate required for the kickoff itself; CDA SME gates apply to the per-task plans this kickoff decomposes into (copy work especially). Inherits from Phase 9a T1 (Collection records tab restored 2026-06-09) and Phase 9 kickoff gap G7 (per-finding provenance). §1.5 framing respected throughout; the §1.5.4 banned-term list is honored (terms referenced indirectly here so the Tier 1 vocabulary guard stays quiet).
**Date:** 2026-06-10
**Companion specs:** `docs/status/2026-06-10-collection-records-review-pin.md` (Mark's verbatim asks); `docs/status/2026-06-08-phase9-kickoff.md` §3.5, §4.3 G7; `DESIGN_SYSTEM.md` §19 (Collection records tab v0.15.0); `ARCHITECTURE.md` §1.5, §4.4; `docs/DATA_DICTIONARY.md` (InformantRecord, §12 published-failures shape); `packages/cdb_publish/cdb_publish/failures.py` and `schemas/failures.py`; `apps/dashboard/src/components/FailuresFindings.tsx`, `apps/dashboard/src/copy/failures_findings.ts`.
**Inherits from:** Phase 9a T1 closeout (Collection records tab live on master); Mark's pinned review note (2026-06-10).

> Authoring note: the Architect drafted this inline; the orchestrator persists it. Em dashes are not used (Mark's standing rule). No cost language. The CLAUDE.md §7 banned terms are avoided and referenced only indirectly.

> Orchestrator note (2026-06-10): persisted verbatim from the Architect's inline draft, with one correction: the Architect flagged the 1,291 record count as possibly conflated with a file byte size and marked it TBD. It is not TBD: the live Data page bundle stats state "1,291 informant records produced by 17 models across 3 domains (family, food, holidays); 36 sessions were preserved as failures and 27 as decline interviews." Per-task plans should still recompute exact per-domain counts from manifest.json at build time.

---

## 1. Goal

Mark visited the live Collection records tab (Phase 9a T1, shipped 2026-06-09) and surfaced four asks. Read together they say: the tab as built is structurally correct (failures-are-findings posture preserved, framing_note rendered verbatim, §1.5 chrome isolated) but it is *incomplete* as a surface. A cold visitor cannot yet answer four questions the page name implicitly promises:

1. **Why do these records matter?** The framing_note explains the LSB pipeline; it does not explain why a refusal or an unparseable response is interesting to a reader.
2. **Why only two record categories?** "Collection failure" and "Follow-up interview" read as a partial taxonomy.
3. **Where are the successful records?** The page is named "Collection records," not "Collection failures."
4. **Where is the raw elicitation exchange, per attempt?** The current surface shows the prompt and response for follow-up interviews but not for the canonical run, and not per-attempt for runs that retried.

This cycle closes those four asks. The framing connection: ask (1) is the "failures are findings" directive translated for a cold reader (Mark's binding directive, currently underweighted in tab copy); asks (2)+(3) expand the surface from a failure-only view to a complete collection-record view; ask (4) overlaps audit gap G7 (per-finding provenance) and, if folded together, closes G7 as a side effect.

Success condition: a cold visitor lands on Collection records, reads one paragraph, and can articulate (a) what an LSB collection record is, (b) why failures and follow-ups in particular are evidence rather than noise, (c) that the dashboard surfaces all attempted runs (not only the failed ones), (d) and can click through to the raw prompt/response for any record. A researcher can pivot from a finding on a chart to the raw exchange that produced it, via the provider_request_id and SHA256.

---

## 2. Out of scope (carry through to per-task plans)

1. No new analysis measures. Smith's S, Sutrop CSI, Romney, OCI, bootstrap CIs all unchanged. This cycle exposes existing fields better; it does not compute new ones.
2. No schema changes to `cdb_core/schemas.py` (`InformantRecord`, `GroundingRef`, `DeclineInterview`, `Failure` raw-dict shape). If a per-task plan surfaces a schema need (e.g., a new `attempt_index` field), the Architect bounces it for a separate cycle with the standard schema gate.
3. No LLM calls in `cdb_analyze`. The "impact" copy is either Mark-authored (preferred) or drafter-generated in `cdb_publish` and SME-gated, not `cdb_analyze`-side.
4. No re-introduction of human grounding (2026-05-07 amendment binding).
5. No re-introduction of autonomous LLM calls in production paths (Phase 7 §11.1 B-1 binding).
6. No new analytical visualizations (heatmaps, MDS, charts). This cycle is a record-browser cycle, not a chart cycle.
7. No spend gates, cost estimates, or authorization gates anywhere in the per-task plans or scripts (CLAUDE.md rule 14, R13).
8. No edits to the published `framing_note` byte-string in `cdb_publish/failures.py` without a CDA SME gate. The existing framing_note is verbatim-bound to the T9 verdict; any addition lives in *new* copy strings, not by mutating the existing one.

---

## 3. Audit: what the Collection records tab is and is not, as of 2026-06-09

### 3.1 What is correct (preserve)
- Tab label, nav order, page heading, framing_note rendering, badge tokens, `<details>`/`<summary>` pattern, `<pre>` container properties, block labels, empty-state copy. All bound by DESIGN_SYSTEM.md §19 and the T9/T10/T1 CDA SME and UI/UX verdicts. Do not paraphrase any of these strings.
- The byte-identity vitest assertion in `FailuresFindings.test.tsx` (case 9 DOM-walk chrome isolation) is binding. New copy must pass the same chrome-isolation check, or the test is updated with a CDA SME co-sign.
- The originating-context block surfacing `run_index`, `originating_outcome_class`, `originating_step`, `originating_informant_id`, `originating_failure_id`.

### 3.2 What is incomplete (this cycle's targets)
- **Impact copy.** The current framing_note is correct but technical; a cold visitor cannot connect "LSB-side detection rule" to "why does this matter." No "what a follow-up interview tells you about the model under the protocol" paragraph exists.
- **Taxonomy disclosure.** The tab shows two record kinds but does not name the full set of LSB outcome categories (parseable success, unparseable response, refusal-string match, transport failure, content-filter return, ...). A reader cannot tell whether the two visible categories are a curated subset or the only categories.
- **Successful records.** The Collection records tab today shows the failure side of `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl`. The success side, `data/raw/informants.jsonl`, is not surfaced. The open data bundle publishes the full file; the dashboard does not link to or browse it.
- **Raw prompt/response per attempt.** Follow-up interview records show `prompt_verbatim` + `response_verbatim` (the follow-up exchange). The *originating* informant's free-list and pile-sort `prompt_verbatim`/`response_verbatim` (`FreelistRecord`, `PileSortRecord`, `InterviewRecord` on `InformantRecord`) are not exposed for any record. Per-attempt retry transcripts (`retry_attempts` exists as a field on `PublishedFailureRecord`) are typed but not rendered.

### 3.3 Existing fields that already support the asks
- `InformantRecord.freelist.prompt_verbatim / response_verbatim / thinking_verbatim` (per-step verbatim, already in raw + bundle).
- `InformantRecord.pile_sort.{prompt_verbatim, response_verbatim, thinking_verbatim}`.
- `InformantRecord.interview.{prompt_verbatim, response_verbatim, thinking_verbatim}`.
- `InformantRecord.provider_request_id`, `sha256_manifest` (eight-key dict).
- `PublishedFailureRecord.retry_attempts: list[dict] | None` (already in publish schema).
- `manifest.json` per-domain `n_records` for failures only today; an analogous successful-record count per domain is computable but not yet emitted.

These are the building blocks. The decomposition below stays inside them.

---

## 4. Decomposition

Eight tasks. T1-T3 are copy-only (CDA SME + UI/UX). T4-T6 add the successful-records surface (publish-layer plumbing + dashboard). T7-T8 add raw-exchange visibility (mostly dashboard + publish-layer expansion). Tasks fall into three independent ship trains; see §6.

### Task 1: Impact paragraph for collection failures (ask 1, part A)

**Goal.** Add a Mark-voice paragraph above the current framing_note that explains *why* a collection failure is evidence, not noise. Concretely: a refusal under a benign elicitation prompt is a finding about how the model was trained to handle category-listing tasks; an unparseable response is a finding about output-format adherence; a transport failure is a finding about provider-side filtering. The paragraph names the connection while staying inside the §1.5.4 language guardrails (no cognition attribution).

**Files touched.**
- `apps/dashboard/src/copy/failures_findings.ts` (add `IMPACT_PARAGRAPH_FAILURES` export).
- `apps/dashboard/src/components/FailuresFindings.tsx` (render the new paragraph between heading and framing_note).
- `DESIGN_SYSTEM.md` §19.4 content order updated (one new step inserted).
- `apps/dashboard/src/__tests__/FailuresFindings.test.tsx` (byte-identity case for the new string + chrome-isolation re-run).

**Gates.** CDA SME on the copy (axes: claims validity, audience translation). UI/UX on layout (where in §19.4 it sits; does it break the empty-state path).

**Acceptance criteria sketch.**
- New `IMPACT_PARAGRAPH_FAILURES` string is byte-identical to the SME verdict.
- Paragraph renders above the framing_note for *all three* domains including the empty-state path (food).
- vitest case 9 chrome-isolation walk passes; forbidden-vocabulary list extended if the SME adds any banned phrases for this paragraph.
- DESIGN_SYSTEM.md §19.4 amended; v0.15.0 bumped to v0.15.1.

### Task 2: Impact paragraph for follow-up interviews (ask 1, part B)

**Goal.** A second Mark-voice paragraph explaining what a "why did you decline" follow-up tells a reader: it converts a refusal into an artifact about the model's stated reasoning under the protocol, without claiming the stated reasoning is the actual reasoning. The §1.5.4 language guardrails apply doubly here; follow-up interview text is the easiest place to slip into cognition attribution.

**Files touched.**
- `apps/dashboard/src/copy/failures_findings.ts` (add `IMPACT_PARAGRAPH_FOLLOWUPS` export).
- `apps/dashboard/src/components/FailuresFindings.tsx` (place near the first decline-interview record, *not* above the whole list, so the reader meets the framing where it applies). UI/UX picks placement.
- `DESIGN_SYSTEM.md` §19.4 update.
- vitest extended.

**Gates.** CDA SME on copy (this is the higher-risk paragraph; cognition attribution is the failure mode). UI/UX on placement.

**Acceptance criteria sketch.**
- Byte-identity assertion on the new string.
- The paragraph references the originating-outcome-class enum by name and explicitly says the enum names an LSB-side detection rule (consistent with the failures.py framing_note).
- Renders only when at least one decline_interview record is present (UI/UX call).
- No new tokens.

### Task 3: Taxonomy disclosure (ask 2)

**Goal.** A short "what categories of collection outcome LSB records, and which two are shown here" paragraph or table that names the complete set of LSB outcome categories. The reader sees that "Collection failure" and "Follow-up interview" are the two non-success surfaces and that the success surface is on its own (T4-T6 below).

**Files touched.**
- `apps/dashboard/src/copy/failures_findings.ts` (add `TAXONOMY_BLOCK` export; structure TBD by CDA SME and UI/UX, likely a small `<dl>` of category -> one-line description).
- `apps/dashboard/src/components/FailuresFindings.tsx`.
- `DESIGN_SYSTEM.md` §19.4 update.
- vitest extended.

**Gates.** CDA SME (the category list and its descriptions are the methodology surface). UI/UX (presentation as `<dl>` vs `<ul>` vs prose).

**Acceptance criteria sketch.**
- Category names match `originating_outcome_class` enum values in `cdb_core/schemas.py` byte-for-byte where applicable. If the enum is incomplete relative to the taxonomy, the Architect bounces the task and routes the enum reconciliation as a separate cycle (schema gate).
- Each row says what the category names and that LSB classified it (not what the model did).
- Forbidden-vocabulary scan passes.

### Task 4: Per-domain successful-record summary artifact (ask 3, publish layer)

**Goal.** Emit a per-domain `apps/dashboard/public/data/records/{slug}.json` that summarises the successful records. Shape (provisional pending §5 OPEN DECISIONS):

```
{
  "domain_slug": "family",
  "generated_at": "...",
  "n_informants": 437,
  "by_model": [
    { "model_id": "...", "n_runs": 30, "n_qa_passed": 30, "model_version_returned": "...", "provider": "..." },
    ...
  ],
  "framing_note": "<CDA-SME-approved>"
}
```

Note: this is a *summary*, not a full record browser. The full records remain in the open data bundle. The summary closes the "where are the successful records" gap without shipping a 100MB-per-domain JSON to a static Cloudflare Pages site. See OPEN DECISION D1 for the alternative postures.

**Files touched.**
- `packages/cdb_publish/cdb_publish/successes.py` (new module, mirrors `failures.py` posture: read-only over raw, sanitize, emit JSON).
- `packages/cdb_publish/cdb_publish/schemas/successes.py` (new schema, mirrors `schemas/failures.py`).
- `packages/cdb_publish/cdb_publish/build.py` (call into successes builder; mirror failures.py wiring).
- `docs/DATA_DICTIONARY.md` §12 extended with the new published-records shape (this is a *published* shape, not an `InformantRecord` schema change, so no cdb_core gate, per `schemas/failures.py` precedent).
- Unit tests in `packages/cdb_publish/tests/test_successes.py`.

**Gates.** CDA SME on the framing_note and on which fields surface in the summary (e.g., does QA-failure-rate per model belong here, or is that a separate viz). No UI/UX yet (no dashboard delta in T4).

**Acceptance criteria sketch.**
- New module is read-only over `data/raw/informants.jsonl`.
- All strings sanitized via `cdb_publish.sanitize.sanitize_record_strings` (R4 redaction).
- Per-domain JSON validates against new `PublishedSuccessesFile` schema.
- DATA_DICTIONARY §12 updated.
- vitest dashboard side: not in this task.

### Task 5: Successful-records section in Collection records tab (ask 3, dashboard)

**Goal.** Render the per-domain summary from T4 as a section inside the Collection records tab, below the existing failures/decline-interviews list. Section heading something like "Successful collection runs (summary)"; the section links out to the open data bundle / HF dataset / Zenodo DOI for the full records (via the Data tab; consistent with the Phase 9a Data tab pattern in §20).

**Files touched.**
- `apps/dashboard/src/components/FailuresFindings.tsx` (extends to fetch `/data/records/{slug}.json` in parallel with `/data/failures/{slug}.json`).
- `apps/dashboard/src/copy/failures_findings.ts` (new copy strings; CDA SME).
- `apps/dashboard/src/data/types.ts` (mirror the new published schema).
- `apps/dashboard/src/styles/failures-findings.css` (no new tokens).
- `DESIGN_SYSTEM.md` §19.4 updated; possibly a new §19.14 for the successes section.
- Tab name reconsideration: §19.3 heading currently reads "Collection records and follow-up interviews." If T5 ships a successes section under the same heading, the heading is more accurate, not less. No rename needed unless the CDA SME asks.
- vitest extended.

**Gates.** CDA SME (section heading + framing copy). UI/UX (placement, summary table presentation, mobile a11y, no new tokens).

**Acceptance criteria sketch.**
- Successes section renders below the failures/decline-interviews list.
- When summary JSON is absent (e.g., a domain with zero successful runs, which would itself be a first-class observation), the empty state is binding-equivalent to the existing failures empty state pattern.
- Per-model table is sortable by `n_runs` (UI/UX call on default sort).
- Chrome-isolation vitest case extended to cover the new section.

### Task 6: Counts caption update (ask 3, minor)

**Goal.** Update the counts caption near the heading from "N records: F failures, D follow-ups" to a phrasing that names the success count too. CDA SME picks the exact phrasing; provisional candidate (NOT verbatim, subject to SME edit): "N collection records: S successful runs, F collection failures, D follow-up interviews."

**Files touched.**
- `apps/dashboard/src/copy/failures_findings.ts` (`countsCaptionText` signature changes).
- `apps/dashboard/src/components/FailuresFindings.tsx`.
- vitest extended.

**Gates.** CDA SME on the new phrasing. UI/UX nominal (single string).

**Acceptance criteria sketch.**
- New caption byte-identity asserted.
- Empty-state path (food, n_records == 0) renders correctly with the new caption template, or omits the caption per the existing rule.

### Task 7: Raw-exchange exposure on InformantRecord-derived rows (ask 4, primary)

**Goal.** For each successful-record summary row in T5 (or independently, depending on D1), allow a click-through to a per-record detail view that shows the verbatim free-list, pile-sort, and interview prompt/response pairs, plus the provenance IDs (`provider_request_id`, `sha256_manifest`, `model_version_returned`). This closes ask 4 *and* gap G7 in one stroke. See OPEN DECISION D4 for whether T7 ships as a per-record JSON browser or a link-out to the bundle.

**Files touched (assuming the per-record-JSON posture; revise per D4).**
- `packages/cdb_publish/cdb_publish/successes.py` (extended to emit `apps/dashboard/public/data/records/{slug}/{informant_id}.json` per record; one file per informant, sanitized).
- `packages/cdb_publish/cdb_publish/schemas/successes.py` (new `PublishedInformantDetailRecord`).
- `apps/dashboard/src/components/FailuresFindings.tsx` (a `<details>`/`<summary>` per row matching the existing pattern, no new visual decisions).
- `apps/dashboard/src/copy/failures_findings.ts` (new block labels mirroring `BLOCK_PROMPT`, `BLOCK_RESPONSE`, `BLOCK_REASONING`, `BLOCK_PROVENANCE` for the three steps).
- DATA_DICTIONARY §12 extended.
- vitest extended.

**Gates.** CDA SME on framing (a verbatim free-list response on the dashboard is the canonical raw exchange; the framing must restate the LSB-side nature of the collection without slipping into cognition attribution). UI/UX on the three-step `<details>` structure and on mobile a11y (these expanded blocks will be long).

**Acceptance criteria sketch.**
- Per-record detail JSON is sanitized (R4 redaction passes).
- `provider_request_id` and the eight `sha256_manifest` keys are rendered in the provenance block, mirroring the existing decline-interview provenance block.
- `<pre>` container respects the existing `max-height: 320px` constraint.
- Chrome-isolation vitest case extended to exclude `<pre>` blocks (already the pattern).
- No new tokens.

### Task 8: Per-attempt retry-transcript exposure (ask 4, secondary)

**Goal.** For records that retried (`PublishedFailureRecord.retry_attempts` typed but unrendered today), render the per-attempt prompt/response pairs in chronological order with the attempt index visible. Only affects records that retried; most failures will have zero or one attempt.

**Files touched.**
- `packages/cdb_publish/cdb_publish/failures.py` (verify `retry_attempts` is being populated from raw; today the type is `list[dict[str, Any]] | None` and the publish path may be passing through None). If raw data does not carry the per-attempt history, this task surfaces it back to the Architect and stops, *no schema change inside this task*.
- `apps/dashboard/src/components/FailuresFindings.tsx` (extend `FailureRecordRow` and `DeclineInterviewRow` with an "Attempts" block when `retry_attempts` is non-empty).
- `apps/dashboard/src/copy/failures_findings.ts` (new `BLOCK_ATTEMPTS` label).
- vitest extended.

**Gates.** CDA SME on the framing of a retry (a retry is a pipeline retry, not a model retry; copy must say so). UI/UX on nested `<details>` (an attempts block inside a record body is a new pattern not in §19.6).

**Acceptance criteria sketch.**
- If `retry_attempts` is empty/None, no Attempts block renders (no empty-section noise).
- If non-empty, each attempt renders with attempt index, prompt, response, and a per-attempt error or stop_reason if present.
- Chrome-isolation vitest case extended.

---

## 5. OPEN DECISIONS for Mark

These are the architectural choices implied by the asks but not yet stated. The Architect declines to improvise. Each decision unblocks one or more tasks above.

### D1. Successful-record surface posture (blocks T4-T7)

Three viable postures, not mutually exclusive:

- **D1a. Per-domain summary JSON only.** T4-only; T5 renders the summary; raw records remain in the bundle. Payload per domain: KB-scale (one row per model, ~15 rows for family). Lightest. Loses ask 4 unless paired with link-outs.
- **D1b. Per-domain summary + per-record detail JSON.** T4 + T7. Per-record JSON one file per informant, served statically; on the order of 1,291 files total across the three domains. Total file count Cloudflare-feasible (Cloudflare Pages limit is 20,000 files in a single deploy, last published as of January 2026; the Coder verifies the current limit before shipping). Total payload moderate (KB per file).
- **D1c. Link-out only.** T4 + a Data-tab card linking to the HF dataset viewer / Zenodo / B2 for record-level browsing. No new dashboard JSON. Loses ask 4 on the dashboard; researcher reproduce-and-cite test relies on a third-party UI.

**Architect recommendation:** D1b. The per-record JSON posture closes ask 4 and G7 simultaneously, the file count is manageable, the precedent for verbatim raw bytes on the static site already exists (failures + decline-interview pre-blocks are exactly this pattern), and the bundle's CC0 license already gives republication rights so the verbatim-on-site question is settled (see D3). D1a is the smaller fallback if the file-count math turns out wrong.

**Mark, please pick a, b, or c.**

### D2. Impact-copy authorship (blocks T1, T2, partially T3, T5, T7)

Two authorship paths for the new impact paragraphs:

- **D2a. Mark-authored** (same posture as the methodology page). The Architect writes a stub, Mark writes the prose, the CDA SME gates the prose, the Coder pastes it into `copy/failures_findings.ts`.
- **D2b. Drafter-generated then SME-gated.** A `cdb_publish` drafter (not `cdb_analyze`, rule 11) takes the framing_note and outcome-category enum and produces candidate prose; the CDA SME edits to PASS; the Coder pastes.

**Architect recommendation:** D2a for T1 + T2 (impact paragraphs are the highest-leverage copy on this surface and most subject to Mark's voice). D2a-with-Architect-stub for T3 (taxonomy is structural; voice matters less). D2a or D2b interchangeably for T5 + T7 framing notes (these are operational descriptions, less voice-bound).

**Mark, please confirm a vs. b for T1/T2 specifically. T3/T5/T7 can be deferred to per-task plans.**

### D3. Republishing raw verbatim outputs on the site (blocks T7, T8)

The published bundle already contains the verbatim free-list, pile-sort, and interview responses under CC0 (per DATA_DICTIONARY §1.6 license). The Collection records tab today renders verbatim model outputs in `<pre>` blocks for follow-up interviews; the precedent is established.

Open question: do any of the provider terms-of-service for the in-corpus providers constrain LSB's republication of raw outputs *on the dashboard* beyond what is constrained in the bundle? The bundle posture treats this as settled (CC0, attribution to the provider via model_id and model_version_returned, no claim that the outputs are the provider's IP). The dashboard posture is presumed identical, but a per-provider TOS audit has not been run against this question specifically.

**Architect recommendation:** Treat dashboard republication as already-settled by the bundle's CC0 publication, since the dashboard is a downstream consumer of the bundle and not a separate publication event. Flag for Mark: a single-pass TOS skim per provider is cheap and worth doing before T7 ships, but is not load-bearing on the architecture.

**Mark, please confirm: proceed under the bundle-precedent assumption, or pause T7 for a TOS audit?**

### D4. T7 vs. G7 (Phase 9 audit gap)

Ask 4 ("raw prompt and responses per attempt") substantively overlaps audit gap G7 ("no per-finding provenance surface: provider_request_id + SHA256 exist per record, not linked from any chart or page") from Phase 9 kickoff §4.3. Two postures:

- **D4a. Fold G7 into this cycle.** T7 closes G7 as a side effect. Cleaner; one surface, one CDA SME pass.
- **D4b. Keep G7 separate.** This cycle exposes raw exchanges in the Collection records tab; G7 separately adds a "see provenance" affordance from each *chart* back to the originating records. The two surfaces serve different audiences (G7 is researcher-facing chart-side; this cycle is journalist-facing record-side).

**Architect recommendation:** D4a for the data plumbing (one per-record JSON shape, used by both surfaces). D4b for the dashboard affordance (chart-side "see provenance" deep-links are a separate UI/UX cycle, not this cycle). Net: this cycle builds the per-record JSON; a follow-up cycle builds the chart-side affordance that consumes it. G7 thereby half-closes here.

**Mark, please confirm: D4a (plumbing here, chart-side affordance later) or fully separate.**

### D5. Heading rename (low-stakes)

§19.3 heading is "Collection records and follow-up interviews." If T5 ships and the tab now shows successes too, the existing heading is still accurate. If T5 does *not* ship (D1c posture), the existing heading remains accurate. Architect recommendation: no rename. If the SME wants one, it lands in T1 or T5.

**Mark, please flag if you want a rename considered.**

---

## 6. Sequencing and independent ship trains

Three trains, partially parallel:

**Train A (copy-only): T1 -> T2 -> T3.** Self-contained. Ships independently as soon as Mark answers D2 and writes the paragraphs. No publish-layer dependency. Single Reviewer / Tester loop per task (one commit each per CLAUDE.md §8). Earliest, smallest, highest-leverage.

**Train B (successes surface): T4 -> T5 -> T6.** T4 (publish) can start the moment D1 is answered. T5 (dashboard) needs T4 published JSON in `apps/dashboard/public/data/records/`. T6 is trivially gated on T5 (caption template touches the same file). Train B can run in parallel with Train A; the only contention is `copy/failures_findings.ts`, which is small enough to merge cleanly.

**Train C (raw exchanges): T7 -> T8.** T7 depends on T4 (per-record JSON requires successes plumbing). T8 can run independently of T7 because it operates on the existing `retry_attempts` field in `PublishedFailureRecord`, not on the InformantRecord side. T8 verifies that `retry_attempts` is populated from raw; if it is not, the task stops and surfaces back to the Architect for a separate raw-collector cycle.

**Recommended first move:** T1 (impact paragraph for failures). It is the smallest, the highest-leverage for a cold visitor, and the most directly aligned with Mark's binding "failures are findings" directive.

**Alternative first move:** T3 (taxonomy disclosure). It is the most structurally clarifying ask for a cold reader and is fully Architect-stubable.

**Do NOT start first:** T4 (gated on D1), T7 (gated on D1+D3+D4), T8 (may surface a raw-collector gap that bounces the task).

---

## 7. Reading list for the next Architect per-task cycle

When the next Architect cycle expands one of these tasks into a Coder plan, the required reads per task:

| Task | Required reads |
|---|---|
| T1, T2 | `ARCHITECTURE.md` §1.5; `CLAUDE.md` §7; `apps/dashboard/src/copy/failures_findings.ts`; T9/T10/T1 CDA SME verdicts in `docs/status/`; this kickoff. |
| T3 | T1 reads + `packages/cdb_publish/cdb_publish/schemas/failures.py` for the `originating_outcome_class` enum + `cdb_core/schemas.py` for any wider failure taxonomy fields. |
| T4 | T3 reads + `packages/cdb_publish/cdb_publish/failures.py` as the structural template + `packages/cdb_publish/cdb_publish/sanitize.py` for the redaction pattern + `docs/DATA_DICTIONARY.md` §12. |
| T5 | T4 reads + `DESIGN_SYSTEM.md` §19 in full + `apps/dashboard/src/components/FailuresFindings.tsx`. |
| T6 | T5 reads + the byte-identity tests in `FailuresFindings.test.tsx`. |
| T7 | T4 + T5 reads + `cdb_core/schemas.py` `FreelistRecord` / `PileSortRecord` / `InterviewRecord` shapes + Phase 9 kickoff §4.3 G7 context. |
| T8 | T7 reads + `packages/cdb_publish/cdb_publish/schemas/failures.py` `retry_attempts` field + `data/raw/failures.jsonl` shape inspection (verify retry_attempts is populated). |

---

## 8. What is explicitly out of scope (restated)

- No analysis-measure changes. Smith's S, Sutrop CSI, OCI, Romney, bootstrap CIs unchanged.
- No schema changes to `cdb_core/schemas.py`. Publish-layer schemas (`cdb_publish/schemas/`) extend; cdb_core does not.
- No LLM calls in `cdb_analyze` (rule 11). Impact copy is Mark-authored (D2a) or `cdb_publish`-drafter (D2b), not `cdb_analyze`.
- No re-introduction of human grounding (2026-05-07 amendment).
- No autonomous LLM calls in production paths (Phase 7 §11.1 B-1).
- No new analytical visualizations on this tab.
- No spend gates, cost estimates, or authorization-gate language (CLAUDE.md rule 14, R13).
- No edits to existing CDA-SME-bound byte-identical strings (framing_note in `failures.py`, SECTION_HEADING, EMPTY_CAPTION, BADGE_*, BLOCK_*, the loading/error strings) without a fresh CDA SME gate.
- No rename of the Collection records tab label or heading without explicit Mark direction (D5).

---

## 9. Decision surface (summary)

**Asks (Mark):**

1. Impact of failures + follow-ups. -> Tasks T1, T2 (CDA SME copy gates; Mark authors; D2).
2. Why only two categories. -> Task T3 (CDA SME; Architect stubs taxonomy).
3. Successful records too. -> Tasks T4, T5, T6 (publish-layer plumbing + dashboard section; D1 posture decision required).
4. Raw prompt and responses, per attempt. -> Tasks T7, T8 (per-record JSON + per-attempt retry rendering; D3 TOS-check question, D4 G7 overlap).

**Open decisions for Mark:**

- D1 (successes surface posture): a / b / c. Recommended b.
- D2 (impact-copy authorship for T1 + T2): a / b. Recommended a.
- D3 (provider TOS audit before T7): proceed under bundle precedent / pause for audit. Recommended proceed.
- D4 (T7 / G7 overlap): plumbing-here / fully-separate. Recommended plumbing-here, chart-side affordance later.
- D5 (heading rename): no / yes. Recommended no.

**First move:** T1 if Mark wants impact landing first; T3 if Mark wants taxonomy landing first.

---

*End of Collection Records Rework kickoff. Decision surface, not an implementation plan. Architect awaits Mark's D1-D5 answers (and any reorderings) before decomposing the first task to the CDA SME and UI/UX gates.*
