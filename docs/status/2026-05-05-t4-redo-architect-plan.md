# Phase 4a.1 T4 Redo — Architect Plan

**Date:** 2026-05-05
**Planner:** Architect agent (Opus)
**Task:** Phase 4a.1 T4 redo (replaces T4.1 + T4.2 + Amendment 4 work under the cap-exhaustion reframe)
**Supersedes (partially):**
- `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` §3.1, §3.2, §3.3 — D17–D22 are reframed; the safety_attribution_subtype hand-coding artifact is moot
- `docs/status/2026-05-01-phase4a1-architect-plan-amendment-4.md` — D23–D27 are moot under the new framing
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` and `docs/status/2026-05-01-phase4a1-amendment-4-cda-sme-verdict.md` — output gate findings are now mooted at the level of the *finding* (CONFIRMED → mechanism string), but their *audit trail value* (the reasoning chain that produced them) is preserved verbatim by leaving the verdict files unchanged on master

**Carries forward (still in force):**
- All 31 Phase 4a.1 binding notes (8 original + A1–A8 + B1–B15) — most carry forward unchanged; B11 is reframed below; B14 binds the eventual T5 redo's §8 architecture
- S5 (Task 16 SME verdict) — the gate this plan is *answering*
- R1–R6 (Phase 4a recovery verdict) — local to recovery operation; do not bind T4 redo, but R1's "replace as authoritative for the cell" framing is the canonical phrasing for the recovered records

**Companion docs:**
- `ARCHITECTURE.md` §1.5 (binding framing), §3.2 (schemas), §4.2 (cdb_analyze constraint), §4.5 (uncertainty in viz)
- `CLAUDE.md` §6 (binding rules), §7 (forbidden vocabulary), §8 (commit conventions), §9 (pitfalls)
- `SECURITY_AND_HARDENING.md` §9 (Reviewer rules)
- `docs/SME_REVIEW.md` (still binding for measure thresholds)
- `docs/BOOTSTRAP_DESIGN.md` (no Level 1/Level 2 implications for this task — sanity-checked)

**Gate chain (mandatory, in order):**
1. **CDA SME PASS or PASS-WITH-NOTES on this plan** — non-negotiable per S5
2. **Mark sign-off** on framing decisions (§5 Q1–Q3 are operator-level)
3. UI/UX agent gate — **NOT required** (see §1 Q4 disposition; this plan does not touch any frontend artifact, dashboard component, or copy that will appear on the website; the methodology page text is *prepared* by this plan as text-on-disk only, and the eventual frontend rendering of that text is a downstream Phase 5/6 task that gets its own UI/UX gate)
4. Coder → Reviewer PASS → Tester PASS per Coder commit
5. CDA SME PASS on T4-redo *outputs* (the reframing memo)

> **Status before Coder may start:** CDA SME PASS or PASS-WITH-NOTES on this plan + Mark sign-off on §5 framing decisions. Coder is NOT authorized to start any T4-redo task until both are recorded.

---

## §0. Why this plan exists

The May 1 T4.1/T4.2 work disposed Note K as "**CONFIRMED** — Gemini single-provider safety-layer activation, cross-domain (family + holidays), with bipartite K-frame/K-vocab trigger pattern (2 K-frame, 7 K-vocab)." That disposition was committed, SME-PASSed, and gate-chained.

The 2026-05-04 Stage 1.5/1.5b/1.6/1.7 probes and the 2026-05-05 recovery campaign falsified the *premise* underneath the disposition:

1. The 9 Gemini "safety_event_attribution" rows came from decline-interview follow-ups whose originating events were **`max_output_tokens=4096` cap-exhausted reasoning**, not safety-policy events. The model's self-reports of "internal safety protocols" were post-hoc confabulations under blind-spot conditions: Gemini saw an empty response on its own side and reasoned backward to "must have been safety," because the actual mechanical cause (the cap was reached during reasoning before any visible output emitted) was invisible to it.
2. The recovery campaign (commit `3634e52`, 100% recovery rate on Gemini; full recovery on glm-5.1 and llama-maverick) demonstrated that the underlying failure was an **instrument event**, not a model-side refusal.
3. The Note K hypothesis ("CN-origin model decline clustering") is now untestable from this data: the failure population collapsed from 29 to 9 (3 of the 9 are unexplained gpt-5.4-mini/mistral-small; 6 are phi-4 adapter-bug failures); none of the remaining 9 cluster on origin in any meaningful way.

**T4 redo is not a re-run of T4.2 with new data. It is a re-disposition of the question "what does Note K disposition look like under the corrected instrument framing?"** The answer is mostly: Note K's hypothesis is no longer the right question. The methodologically interesting finding has shifted from "CN-origin model decline clustering" to "**LLM confabulation of safety-mechanism explanations under blind-spot conditions when the actual cause is mechanical**." That is a different finding, and it requires its own framing.

This plan is gated by **S5** (Task 16 SME verdict): *"Note K re-classification under the new framing must route through CDA SME before any methodology-page text — gates the future T4-redo task."* This plan IS the artifact S5 binds.

---

## §1. Disposition table

| Concern | Disposition | Rationale |
|---|---|---|
| **Note K disposition** | **REPLACED** (not "NOT CONFIRMED," not "RETIRED") | The hypothesis as originally posed is mechanically untestable from the recovered corpus. But the data isn't *silent* — it shows something else (confabulation under blind-spot conditions) that subsumes the original Note K's purpose. REPLACED preserves the audit trail and renames the question; NOT CONFIRMED would falsely imply the question was tested and the answer was no; RETIRED would discard the methodologically interesting finding. **SME ruling required — see §6 Q3.** |
| **Note J cross-tab structure (`outcome_class × origin`)** | **RETIRED for the recovered corpus; preserved as a historical artifact for the original Phase 4a corpus** | With 20 of 29 failure cells recovered as successful informants, the Note J cross-tab no longer has a coherent denominator: 9 cells remain failures, 20 are now informants, and the "outcome_class" axis (completed / empty_output / parse_failure / etc.) collapses. The historical Note J cross-tab on the original 29-failure corpus remains a valid instrument-state artifact; it just no longer governs the methodology page. |
| **The May 1 hand-coded subtype data** (`data/derived/decline_interviews_safety_attribution_subtype.jsonl`) | **MARK-AS-SUPERSEDED** (not delete, not leave-with-warning) | The 9 hand-coded rows classify substantive decline-interview narrative content as k_frame / k_vocab. Under the new framing, those classifications are **classifications of confabulation content**, not safety event attribution. The verbatim narratives are still real data; the classifications are still real human judgment about how the narrative was framed. What changed is the *interpretation*: the narrative is the model's post-hoc attribution under a blind-spot condition, not the model's account of an actual safety event. Mark-as-superseded preserves the audit trail (the May 1 commits stand on master), names the artifact's new epistemic status, and keeps the verbatim text available for the new framing's analysis without destructive editing. **SME ruling required — see §6 Q1.** |
| **The T4.2 cross-tab script** (`scripts/phase4a1_note_j_crosstab.py`) | **MARK-AS-SUPERSEDED** at the script docstring + add a "do not run for methodology" header note. **Not deleted.** | The script implements a correct disposition arithmetic (the four-tier tree); the disposition output is mathematically right for the data it consumed. What's wrong is the *premise* the data carried into the script. The script remains useful as (a) a reference for the disposition tree implementation should it be reused on Phase 4b data, (b) audit trail for the May 1 work. Deleting it would erase the audit trail; leaving it without annotation would invite re-running it as if its output were authoritative. **SME ruling required — see §6 Q2.** |
| **The 24 T3B decline-interview records** (`data/raw/decline_interviews.jsonl`) | **PRESERVED VERBATIM** (append-only is binding); analytical interpretation reframed | The records are still valid AS decline-interview records. Per CLAUDE.md §9 pitfall 10, append-only is binding regardless of interpretation. Their *role* in the analysis layer changes: they are now the corpus for studying confabulation under blind-spot conditions, not the corpus for studying safety events. |
| **The T3C 27-row manual classification** (`data/derived/decline_interviews_manual_classification.jsonl`) | **PRESERVED VERBATIM**; reinterpreted | The 7-enum classifications are still valid descriptions of what the verbatim text says. What changed is the upstream attribution: a row classified as `safety_event_attribution` describes the *content of the model's narrative*, which is correct on a strict reading of the text. The new framing adds a layer above: those 9 rows are *narratives produced under blind-spot confabulation*, not *narratives describing real safety events*. |
| **Methodology-page text** | **PRODUCED BY THIS PLAN** (text-on-disk; not yet rendered to dashboard) | The reframing memo (§2 task RD-3) produces the canonical text-on-disk that the eventual methodology-page UI/UX work will quote. This plan is the artifact S5 binds; the SME PASS on this plan is the methodology-text gate. The downstream UI/UX rendering (Phase 5/6) is its own gate cycle. |
| **Schema changes** | **NONE** | Pydantic v0.1.11 InformantRecord is unchanged. No `cdb_core/schemas.py` edits. No `DATA_DICTIONARY.md` updates. |
| **Analytical artifacts (Smith's S, Romney CCM, MDS, Procrustes)** | **OUT OF SCOPE for T4 redo** | The recovered corpus unblocks them, but their production is the natural T5 successor task or a fresh Phase 4 closure plan. T4 redo's purpose is methodology re-disposition, not analytical computation. Scope creep here would entangle two distinct review surfaces. **SME ruling required — see §6 Q5.** |
| **Forbidden vocabulary** | **None used.** Confabulation framing uses "the model's output narrative attributes the failure to," not "the model believed the failure was caused by." Blind-spot framing uses "under blind-spot conditions" / "the model could not see the actual cause" as descriptive observations about the information available to the model, not as cognition claims. The Reviewer enforces. |

---

## §2. Tasks

### Task RD-1 — Audit annotation of superseded May 1 artifacts

**Owner:** Coder
**Files:**
- Read: `data/derived/decline_interviews_safety_attribution_subtype.jsonl`, `scripts/phase4a1_note_j_crosstab.py`, all the Phase 4a.1 verdict files
- Write (new): `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md` — a sibling annotation file naming the artifact superseded under the 2026-05-05 cap-exhaustion reframe. Cross-references this plan, the Task 16 verdict, the recovery report, and the original T4 SME verdict.
- Write (new): `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md` — sibling annotation file for the script. Same cross-references. Includes the explicit warning: "Do NOT re-run for methodology purposes. The script's premise (that the 9 safety rows are evidence of safety events) was falsified by the 2026-05-04 max_tokens finding. The script remains in-tree for audit and code-reference value only."
- Modify: top-of-file docstring of `scripts/phase4a1_note_j_crosstab.py` — prepend a banner block: `# SUPERSEDED 2026-05-05 — see scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`. **No logic changes, no behavior changes, no tests touched.** This is a docstring annotation only.
- Modify: top-of-file annotation in `data/derived/decline_interviews_safety_attribution_subtype.jsonl` — **NOT directly editable** (would violate append-only convention even though it's `data/derived/` not `data/raw/`; plan adopts append-only posture for `data/derived/` to preserve audit trail). The sibling `.SUPERSEDED.md` file is the annotation mechanism.

**Scope rationale.** The "mark-as-superseded" disposition (§1) is the right shape because (a) deletion erases the audit trail of the May 1 work and the SME verdicts that endorsed it, (b) leaving the artifacts un-annotated invites re-running them, (c) destructive editing of the JSONL would violate the append-only convention even though the file is in `data/derived/` rather than `data/raw/`. Sibling `.SUPERSEDED.md` files are the lowest-impact annotation primitive available.

**Behavior contract:**

1. The two new `.SUPERSEDED.md` files clearly state: (a) the artifact's original purpose, (b) the falsifying finding (Stage 1.5/1.5b/1.6/1.7 probes + recovery campaign), (c) the artifact's current epistemic status (verbatim data preserved; classifications reinterpreted), (d) the cross-references to this plan, the Task 16 verdict, the recovery report, and the original T4 SME verdict.

2. The docstring banner on `scripts/phase4a1_note_j_crosstab.py` is a one-line block at the top of the module docstring. The rest of the docstring is preserved verbatim (it correctly describes what the script does; it just no longer applies to the methodology under the new framing).

3. **No edits to existing JSONL lines.** The sibling annotation file is the mechanism.

**Acceptance criteria:**
- Two new `.SUPERSEDED.md` files exist and follow the format above.
- The script docstring banner is present and one-line.
- `git diff` shows the annotation banner addition is the only line change to `phase4a1_note_j_crosstab.py`.
- No changes to `data/derived/decline_interviews_safety_attribution_subtype.jsonl`, `data/derived/decline_interviews_manual_classification.jsonl`, `data/raw/decline_interviews.jsonl`, or any test file.
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green (no behavior change should affect any test).

**Test coverage (Tester):** None required for this task — it is annotation work only with no logic changes. The Tester confirms the existing test suite still passes (regression-free).

**Reading list for Coder:**
- `CLAUDE.md` §6, §7, §8, §9 (especially pitfall 10 — append-only)
- This plan (§0, §1, §2 RD-1)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5 source)
- `docs/status/2026-05-05-phase4a-recovery-report.md` (the recovery outcome)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (the work being annotated)
- `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (read-only)
- `scripts/phase4a1_note_j_crosstab.py` (read-only except for the docstring banner)

**Estimated cost:** $0 (no API calls)

**Gate verdicts required:**
- CDA SME PASS or PASS-WITH-NOTES on this plan
- Reviewer PASS on RD-1 commit
- Tester PASS on RD-1 commit (regression check only)

---

### Task RD-2 — Confabulation classification annotation (sibling artifact)

**Owner:** Coder (scaffold + tests) → Mark (hand-codes 9 rows) → Coder (consumer references in RD-3 memo)
**Files:**
- New: `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` — Pydantic model `ConfabulationClassification` and a `load_confabulation_classifications(path)` loader
- New: `scripts/build_confabulation_classification_seed.py` — seed-builder that reads the 9 superseded `safety_attribution_subtype` rows and emits a seed at `data/derived/decline_interviews_confabulation_classification.jsonl` with `confabulation_label="UNCLASSIFIED"` sentinel
- New: `tests/test_confabulation_classification.py` — fixture-driven unit tests
- Hand-coded by Mark (separate commit): `data/derived/decline_interviews_confabulation_classification.jsonl` — 9 rows, all with `confabulation_label` ∈ a tightly bounded enum (see schema below)

**Scope rationale.** The 9 originally-Gemini decline-interview rows are now the canonical corpus for studying confabulation under blind-spot conditions. The May 1 K-frame/K-vocab classification was a description of *the rationalization the model offered for an imagined safety event*; the new classification is a description of *the type of confabulation pattern the model produced when it could not see the actual mechanical cause*. These are different schemata even though they operate on the same verbatim text. The new classification is the methodologically interesting one under the corrected framing.

**Schema for `ConfabulationClassification`:**

| Field | Type | Required | Validation |
|---|---|---|---|
| `decline_interview_id` | `str` | yes | non-empty; must exist in `decline_interviews.jsonl` |
| `confabulation_label` | `Literal[...]` | yes | one of `safety_filter_confabulation`, `task_paradox_confabulation`, `topic_sensitivity_confabulation`, `mixed_attribution`, `not_confabulation` (sentinel `"UNCLASSIFIED"` allowed in seed only) |
| `confabulation_rationale` | `str` | yes | length ≤ 200 chars; references verbatim text from `response_verbatim` |
| `under_blind_spot` | `bool` | yes | True if the originating failure was a `max_output_tokens=4096` cap-exhaustion event (verifiable from `originating_informant_id` → cross-reference against the recovery campaign cell list); False otherwise |
| `classifier_id` | `str` | yes | non-empty; conventional value `"mark"` |

**Confabulation labels — provisional definitions (binding for hand-coding rationale; SME may refine in plan-review verdict):**

- `safety_filter_confabulation` — narrative attributes failure to "safety protocols," "policy filter," "internal safety mechanism," etc., when the originating failure was a cap-exhaustion event. The model is fabricating a safety-mechanism explanation under blind-spot conditions.
- `task_paradox_confabulation` — narrative attributes failure to logical / paradoxical conflict in the prompt ("act as a participant" vs. "I am an AI", "list every X" vs. impossibility of "every"), when the originating failure was a cap-exhaustion event. Different fabrication shape.
- `topic_sensitivity_confabulation` — narrative attributes failure to topic-sensitivity ("religious", "cultural", "biased", "uncurated"), when the originating failure was a cap-exhaustion event. Third fabrication shape.
- `mixed_attribution` — narrative blends two or more of the above without a single dominant attribution. Methodologically interesting because mixed attribution is consistent with confabulation (the model is searching for a plausible explanation) and distinct from a single coherent theory.
- `not_confabulation` — narrative correctly identifies the failure cause (e.g., "technical glitch," "mechanical error"), or genuinely doesn't claim to know. These rows are NOT confabulation under the new framing.

**Cross-walk from May 1 hand-coding (informational only, not binding):**

The May 1 distribution was 2 K-frame, 7 K-vocab. Under the new schema, the cross-walk is approximate:
- May-1 K-frame rows → likely `task_paradox_confabulation` (they invoke the AI-vs-human-research-subject framing as the trigger)
- May-1 K-vocab rows → likely `topic_sensitivity_confabulation` or `safety_filter_confabulation` (they invoke list-comprehensiveness/sensitivity as the trigger)
- Some rows may now classify as `mixed_attribution` once the new schema's discriminators are applied
- The K-frame/K-vocab dichotomy itself is **not** carried forward — it was a subdivision of "safety_event_attribution," which itself is now superseded

Mark hand-codes from scratch under the new schema rather than mechanically translating. The May 1 work is preserved as audit; it is not the source of the new labels.

**Acceptance criteria (Coder scaffold + tests):**
- `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` exists; exports `ConfabulationClassification` and `load_confabulation_classifications`
- `scripts/build_confabulation_classification_seed.py` reads the 9 rows from `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (the *id list*, not the labels) and emits the seed file at `data/derived/decline_interviews_confabulation_classification.jsonl` with all rows `confabulation_label="UNCLASSIFIED"`
- `tests/test_confabulation_classification.py` covers: valid for each enum value, sentinel rejected by loader, ≤200-char rationale boundary, `under_blind_spot` field validation, missing parent-id rejected, fixture round-trip
- No LLM imports in `cdb_analyze` (CI-enforced)
- `uv run pytest && uv run ruff check . && uv run mypy packages/` green

**Acceptance criteria (Mark hand-coded commit, separate):**
- All 9 rows have `confabulation_label` ∈ the four primary enum values (sentinel rejected)
- All 9 rows have `under_blind_spot=true` (these are all the originally-Gemini cells whose originating events were cap-exhaustion failures recovered on 2026-05-05)
- All 9 rows have non-empty `confabulation_rationale` ≤ 200 chars
- Commit body cross-references this plan, RD-1 superseded annotations, Task 16 verdict S5, recovery report

**Reading list for Coder:**
- This plan (§0, §1, §2 RD-2)
- `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` §3.1 (the May 1 schema this is succeeding — for reference only, not as canonical)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (the May 1 SME verdict, preserved as audit)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (the new framing source)
- `data/raw/decline_interviews.jsonl` (verbatim text source for hand-coding reference)
- `packages/cdb_analyze/cdb_analyze/safety_subtype.py` (the May 1 module — reference for the Pydantic + loader pattern; the new module follows the same shape)

**Estimated cost:** $0 (no API calls)

**Gate verdicts required:**
- CDA SME PASS on this plan (the schema is methodologically significant — it implements an SME-prescribed reframing of B11)
- Reviewer PASS on Coder commit
- Tester PASS on Coder commit
- **Optional CDA SME spot-check** on Mark's hand-coded artifact (Architect default: non-blocking — same posture as Amendment 3 §3.1 took for the May 1 hand-code; the SME may request a blocking spot-check at gate-review time)

---

### Task RD-3 — T4-redo reframing memo

**Owner:** Coder (scaffold + structured numerics) → Mark (final prose review and approval) → CDA SME (final PASS gate)
**Files:**
- New: `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` — the canonical memo describing what Note K disposition looks like under the corrected framing. **This is the artifact S5 binds.** Methodology-page text quotes from this memo (in a future Phase 5/6 task with its own UI/UX gate).

**Scope rationale.** Under S5, the methodology-page text describing Note K must be SME-PASSed before any frontend rendering. The most surgical way to satisfy S5 is to produce the canonical text-on-disk in `docs/status/`, get it SME-PASSed, and then have the eventual UI/UX rendering quote from it verbatim (or with explicit deltas that re-route through SME). This is the same pattern as Amendment 3 D20 → T5 §8.2 — the canonical text lives in a verdict/memo file, and downstream surfaces quote from it.

**Memo structure (binding):**

The memo MUST include the following sections in this order. SME spot-checks each section in the output gate.

1. **§1. Header.** Date, scope ("Phase 4a.1 T4 redo, replacing T4.2 Note K disposition under the 2026-05-04 cap-exhaustion reframe"), companion docs, audit trail.

2. **§2. What changed.** Plain-language description of the May 1 disposition, the 2026-05-04 finding, and the 2026-05-05 recovery campaign. ≤500 words. No forbidden vocabulary.

3. **§3. Disposition: Note K is REPLACED.** The canonical disposition statement. Single paragraph, methodology-page-quotable. Suggested wording (Architect drafts; SME refines):

   > "Note K, originally framed as 'CN-origin model decline clustering,' is REPLACED under the 2026-05-04 cap-exhaustion reframe. The 9 decline-interview narratives that the May 1 disposition treated as 'safety_event_attribution' are now understood as model self-reports under blind-spot conditions: the model could not observe the actual mechanical cause of its empty output (a `max_output_tokens=4096` cap reached during reasoning before any visible output emitted) and produced a post-hoc attribution narrative consistent with the categorical knowledge available in its training corpus. The substantive narrative content remains real and analytically interesting — it characterizes the *shape* of attribution patterns LLMs produce when asked to interpret events whose true cause is invisible to them — but it does not constitute evidence of a safety-policy event in the originating Phase 4a collection run. The recovery campaign of 2026-05-05 (`docs/status/2026-05-05-phase4a-recovery-report.md`) re-collected those cells under the corrected `max_tokens=16384` configuration with a 100% Gemini recovery rate, replacing the failure rows with substantive informants. The originating Note K hypothesis is no longer testable from this corpus; it is replaced by a different finding whose methodology lives in §4 below."

4. **§4. The replacement finding: confabulation under blind-spot conditions.** A description of what the 9 narratives DO show under the corrected framing. References the RD-2 confabulation classification artifact. Names the four confabulation labels and reports the actual distribution from Mark's hand-code. Discusses the methodological interest of confabulation patterns (this is a finding about *attribution-narrative shape under blind-spot conditions*, which is itself a useful CDA-adjacent observation about LLM corpus lens). The §1.5 framing applies: "the model's output attributes" / "the narrative pattern is consistent with" / NEVER "the model believed" or "the model thought."

5. **§5. What the recovered corpus enables (and doesn't).** With 20 recovered Gemini/glm-5.1/llama-maverick informants, the Phase 4 analytical layer (Smith's S, Romney CCM, MDS, Procrustes, OCI) can now run on the corrected corpus. **This memo does NOT compute those statistics** — that is a separate task (Phase 4a closure or T5 redo, scoped separately per §6 Q5). The memo names the analytical work as unblocked.

6. **§6. What remains undetermined.** The 3 unexplained failures (gpt-5.4-mini ×2, mistral-small ×1) and the 6 phi-4 adapter failures are out-of-scope of this memo. Their disposition is in the recovery report's "forward carry" section.

7. **§7. Audit trail.** Cross-references to: the May 1 disposition (preserved), the cap-exhaustion finding (Task 16 verdict, S5), the recovery campaign (recovery report), the superseded artifacts (RD-1 annotations), the new confabulation classification (RD-2 artifact). The audit trail is the answer to "what did the project know and when did it know it" for any future researcher.

8. **§8. Carry-forward of binding notes.** Enumerates which of the 31 prior binding notes carry forward unchanged, which are reframed by this memo, and which are made vacuous. Architect's draft mapping (SME may refine):
   - All 8 original Phase 4a.1 binding notes: carry forward (most are about cross-tab structure and small-n thresholds, both still relevant)
   - A1–A8: carry forward
   - B1–B6: B5 (detector role-change SME review at code-review time) is reaffirmed and remains binding; B6 (T5 §8 public-copy guardrails) carries forward and binds the eventual T5 redo
   - B7–B9: vacuous under the new framing (they were about the disposition tier arithmetic that no longer applies)
   - B10: soft, carries forward
   - **B11: REPLACED** by the confabulation classification schema in RD-2. The K-frame/K-vocab dichotomy is superseded.
   - B12: carries forward as binding precedent for future batches
   - B13: not triggered (the K-frame N≥10 refinement question is moot under the new framing)
   - **B14: carries forward and binds the T5 redo §8 architecture** — the numerics-vs-interpretation separation is still load-bearing, just on different numerics
   - B15: soft, carries forward
   - **S5: SATISFIED by this memo's PASS verdict.** S5 is the gate this memo answers.
   - R1–R6 (recovery): local to the recovery operation; do not bind T4 redo

**Binding §1.5 framing for the entire memo.** The memo describes confabulation as **a property of the model's output narrative under blind-spot conditions**, not as a property of the model's cognition. Recommended phrasings (Architect draft; SME refines):
- "the model's output narrative attributes the failure to safety mechanisms, when the actual cause was mechanical"
- "the response pattern is consistent with post-hoc attribution under blind-spot conditions"
- "the model could not observe the cap-exhaustion event and produced an explanation consistent with categorical knowledge from its training corpus"

Forbidden in this memo (Reviewer enforces):
- "the model believed there was a safety event"
- "the model thought it had been blocked"
- "the model's worldview about safety"
- Any phrasing implying the model has introspective access to its own cause-of-failure

**Acceptance criteria:**
- Memo at `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` exists and follows §1–§8 structure above
- §3 disposition statement is methodology-page-quotable (single paragraph, no internal cross-references that would break when extracted)
- §4 references RD-2 confabulation classification artifact with concrete N values per label
- §7 audit trail cross-references all the verdicts in the predecessor chain (Task 16, recovery, original T4, May 1 amendments)
- No forbidden vocabulary anywhere in the memo (Reviewer scan)
- §1.5-clean rephrasings throughout (the memo's whole purpose is to re-state methodology under the corrected framing; getting this wrong undoes the gate)

**Test coverage (Tester):** None required (memo is prose). Tester confirms regression-free state of the existing test suite.

**Reading list for Coder:**
- This plan in full
- `ARCHITECTURE.md` §1.5 (especially §1.5.1 corpus lens, §1.5.4 forbidden vocabulary, §1.5.6 the website is the artifact)
- `CLAUDE.md` §7 forbidden vocabulary
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (especially §B "Note K implications for the T4-redo task")
- `docs/status/2026-05-05-phase4a-recovery-report.md`
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (the work being reframed; specifically Finding 1 Q1–Q4 and Finding 2)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (original Note K methodology, especially Ruling 6 on coverage-caveat framing)
- `data/raw/decline_interviews.jsonl` (the verbatim narratives — Coder needs to *read* the actual narratives to draft accurate reframing prose)
- `data/derived/decline_interviews_confabulation_classification.jsonl` (RD-2 output — Coder cites N values from here)

**Estimated cost:** $0

**Gate verdicts required:**
- CDA SME PASS-WITH-NOTES or PASS on this plan (gates the memo)
- Reviewer PASS on memo commit (forbidden-vocabulary scan; structure check)
- Tester PASS (regression check only)
- **CDA SME PASS on the memo itself** — this is the S5 output gate. The memo contains methodology-page-bound text; the SME's PASS on the memo is what unblocks any downstream UI/UX rendering of the methodology page.

---

## §3. Sequencing and dependencies

```
[Architect plan written]
        │
        ▼
[CDA SME review of THIS plan]  ← MANDATORY GATE per S5
        │
        ▼
   PASS / PASS-WITH-NOTES?
        │
        ▼
[Mark sign-off on §5 framing decisions Q1–Q3]
        │
        ▼
[Coder: Task RD-1 — annotation of superseded artifacts]
        │
        ▼
[Reviewer + Tester PASS on RD-1]
        │
        ▼
[Coder: Task RD-2 scaffold — confabulation classification module + tests]
        │
        ▼
[Reviewer + Tester PASS on RD-2 scaffold]
        │
        ▼
[Mark hand-codes 9 confabulation rows]
        │
        ▼
[Reviewer PASS on Mark hand-code commit]
        │   [Optional: CDA SME spot-check on hand-coded artifact]
        ▼
[Coder: Task RD-3 — reframing memo]
        │
        ▼
[Reviewer PASS on RD-3 commit (forbidden-vocab + structure)]
        │
        ▼
[CDA SME PASS on RD-3 memo content]  ← SATISFIES S5
        │
        ▼
[Architect schedules: Phase 4a closure / T5 redo as separate plan]
[Architect schedules: methodology-page UI/UX work as separate plan with UI/UX gate]
```

**Bundling boundaries (CLAUDE.md §8):**
- RD-1, RD-2 scaffold, Mark's hand-code, and RD-3 are **four separate commits** (plus tests in RD-2 scaffold = same commit). No bundling.
- RD-1 and RD-2 scaffold could be done in either order; Architect prefers RD-1 first because it makes the May 1 supersede-status visible to anyone reading the repo before RD-2's new schema lands.
- RD-2 scaffold and Mark's hand-code are explicitly two commits (CLAUDE.md §8 — Mark's data commit is its own task).

---

## §4. Risks

### 4.1 Methodology drift between this plan and the recovery report

**Risk:** The recovery report (`docs/status/2026-05-05-phase4a-recovery-report.md`) describes the recovery as an "instrument event" with the framing "cap-exhausted reasoning, recovered under the Task-16 cap fix." This plan reframes the *same data* with a different lens (confabulation under blind-spot conditions). If the two framings are incompatible, the project's audit trail becomes incoherent.

**Mitigation:** They are not incompatible — they describe different layers of the same finding. The recovery report describes the *instrument event* (the cap exhaustion); this plan describes the *model output produced under the instrument event* (the confabulation narrative). The RD-3 memo §2 explicitly bridges the two: the cap exhaustion is the originating mechanical fact; the confabulation is what the model produced *in response to* not being able to see the cap exhaustion. The SME spot-checks this bridge in the plan-review verdict.

### 4.2 The "blind-spot" framing is itself a non-trivial cognition claim

**Risk:** Saying "the model could not see the actual cause" sounds like a cognition claim ("the model has perception that has limits"). This brushes against §1.5.4 forbidden vocabulary even if it doesn't tokenwise match.

**Mitigation:** The §1.5-clean reformulation is "the actual mechanical cause was not surfaced in the information available to the model at decline-interview time." This is descriptive of the information flow (the model received the empty-output text + the prompt asking it to describe what happened; it did not receive the API-level `output_tokens=0 AND thoughts_token_count > 0` diagnostic), not introspective. The SME spot-checks the memo prose for this distinction; if Architect's draft prose at §3 above slips into cognition-shaped phrasing, SME flags it in the gate verdict.

### 4.3 The confabulation classification schema is novel and may be miscalibrated

**Risk:** The four confabulation labels in RD-2 (`safety_filter_confabulation`, `task_paradox_confabulation`, `topic_sensitivity_confabulation`, `mixed_attribution`) are the Architect's proposal. They may not be the most useful slicing. Mark's hand-coding may surface labels that don't fit, or distributions that suggest a different schema is needed.

**Mitigation:** The schema is provisional and the SME may refine it in plan review. If Mark's hand-coding produces (e.g.) all 9 rows as `mixed_attribution`, that is itself a finding (the model's confabulation is not cleanly divisible into single-attribution buckets) and the schema is updated in a follow-up amendment with SME review. Same precedent as B11's evolution from the T3B SME spot-check to Amendment 3 D17–D22.

### 4.4 Cross-contamination with eventual Phase 5/6 UI/UX work

**Risk:** This plan produces methodology-page-bound text. The eventual UI/UX rendering of the methodology page is downstream and has its own UI/UX gate. If the text-on-disk in RD-3 is treated as final UI copy, the UI/UX agent's review surface is bypassed.

**Mitigation:** RD-3's memo is text-on-disk for the SME gate (S5). The eventual UI/UX rendering is a separate task with its own UI/UX gate (CLAUDE.md §3). The memo §3 disposition statement is *quotable* by the UI rendering, but the UI rendering may need to gloss it for audience translation, add visualizations, etc. — all of those are UI/UX-gated decisions. The Reviewer flag for any future PR that merges the memo content into `apps/dashboard/` without a UI/UX verdict is binding.

### 4.5 Append-only convention extension to `data/derived/`

**Risk:** RD-1 adopts an "append-only by convention" posture for `data/derived/` (no destructive edits to the May 1 hand-coded artifact, even though it's in `data/derived/` not `data/raw/` and CLAUDE.md §9 pitfall 10 only explicitly binds `data/raw/`). This is an extension of the convention.

**Mitigation:** The extension is conservative — it preserves the audit trail without creating new constraints anyone has to remember. The sibling `.SUPERSEDED.md` annotation pattern is the lowest-impact way to communicate the supersede status. If the SME prefers a different posture (e.g., an editable annotation in the artifact's first non-data line), this is open for SME ruling — see §6 Q1.

### 4.6 The replacement finding (confabulation under blind-spot conditions) is itself novel

**Risk:** The May 1 work was disposing a hypothesis that was already in the project's binding notes (Note K = CN-origin clustering). The replacement finding (LLM confabulation under blind-spot conditions) is *new*; it doesn't have a Note designation and hasn't been gate-reviewed before. If the SME doesn't think the replacement finding is methodologically interesting enough to publish, the memo §4 should be cut.

**Mitigation:** This is exactly the kind of question the SME PASS gate exists to settle. Architect's read is that the finding is methodologically interesting and project-relevant (it characterizes a behavior LLMs produce that future LSB collection runs need to be aware of), but the SME may rule otherwise and bound §4 to "out of scope of this memo; defer to a future task." Either ruling is defensible.

---

## §5. What Mark must sign off on

These are operator-level decisions, not pure methodology. Mark's sign-off is requested before Coder starts RD-1.

1. **Q1 — Disposition of May 1 hand-coded artifacts: MARK-AS-SUPERSEDED via sibling `.SUPERSEDED.md` files.** (Architect adopted this over delete or leave-with-warning per §1 disposition table.) Mark may override to "delete" if he prefers a clean-tree posture; the Architect's recommendation is supersede because the audit trail is load-bearing.

2. **Q2 — Disposition of `scripts/phase4a1_note_j_crosstab.py`: docstring banner + sibling `.SUPERSEDED.md`.** (Architect adopted this over delete.) Same as Q1; Mark may override.

3. **Q3 — Note K disposition: REPLACED (not RETIRED, not NOT CONFIRMED).** This is the highest-leverage framing decision in this plan. Mark and the SME both have a vote. If Mark prefers a different framing (e.g., "Note K is RETIRED; the confabulation finding is its own new note designation, e.g., Note L"), the plan re-routes through SME with the new framing.

4. **Estimated cost: $0.** No API calls. No spend approval needed.

5. **Time estimate.** RD-1 is a few hours of Coder work. RD-2 scaffold is half a day of Coder work + tests. Mark's hand-coding of 9 rows is 1–2 hours. RD-3 memo is a full day of Coder draft work plus Mark prose review. Total wall-clock: ~3–5 days at typical pace.

6. **No deferral of the methodology-page UI/UX work.** This plan does NOT include the UI/UX rendering of the methodology page. That is a separate Phase 5/6 task with its own UI/UX gate. Mark should confirm he does not expect the UI/UX work to be bundled here.

Mark's sign-off is requested as a `+1` in `#lsb-cda-sme` after the SME PASS, OR a docs/status commit comment, OR a direct message — operator's choice.

---

## §6. Open questions for SME ruling

These are routed to the CDA SME explicitly. The plan cannot advance to Coder until the SME issues a verdict that addresses each.

### Q1 — May 1 hand-coded artifact disposition

**Architect read:** MARK-AS-SUPERSEDED via sibling `.SUPERSEDED.md` annotation file. Append-only convention extends to `data/derived/`. No destructive edits to the May 1 JSONL.

**SME confirm or override.** Alternatives: (a) delete the artifact (loses audit trail), (b) leave-with-warning (no annotation; relies on commit history alone), (c) destructive-edit annotation in the artifact's first row (violates append-only convention). Architect rejects all three; SME may rule otherwise.

### Q2 — T4.2 cross-tab script disposition

**Architect read:** Docstring banner + sibling `.SUPERSEDED.md` file. Script preserved for code-reference value (the disposition tree implementation may be reused on Phase 4b data); `.SUPERSEDED.md` warns against re-running for methodology purposes.

**SME confirm or override.** Alternatives: (a) delete the script, (b) move to `scripts/archive/`, (c) leave un-annotated. Architect's preference is the docstring banner because it is visible at code-reading time without requiring a separate file lookup.

### Q3 — Note K disposition: REPLACED, RETIRED, or NOT CONFIRMED?

**Architect read:** **REPLACED.** The hypothesis as originally framed is mechanically untestable from the recovered corpus; but the data does show a different methodologically interesting finding (confabulation under blind-spot conditions) that subsumes Note K's purpose. REPLACED preserves the audit trail and renames the question.

**SME confirm or override.** Alternatives:
- **NOT CONFIRMED** would falsely imply the original question was tested and the answer was no (it was *not tested* — the data needed to test it doesn't exist anymore)
- **RETIRED** would discard the methodologically interesting replacement finding
- **REPLACED-WITH-NEW-NOTE-DESIGNATION** (e.g., the confabulation finding becomes "Note L") is a defensible alternative that preserves the Note K history more cleanly. Architect is open to this; the SME's ruling is requested.

### Q4 — UI/UX agent gate: required or not?

**Architect read:** **NOT REQUIRED for this plan.** The plan produces text-on-disk in `docs/status/`, not frontend artifacts. No `apps/dashboard/` files are touched. No `DESIGN_SYSTEM.md` files are touched. No charts, components, or copy that will appear on the dashboard are produced *by this plan*. The eventual UI/UX rendering of the methodology page is downstream and gets its own UI/UX gate.

**SME confirm or override.** The borderline case is RD-3's memo §3 disposition statement, which is *intended* to be quotable by the eventual UI rendering. If the SME considers "text drafted with intent to be quoted on the dashboard" to be a UI/UX surface, the plan re-routes through UI/UX. Architect's read is that text-on-disk is text-on-disk; the UI rendering is what makes it a UI/UX surface, and that rendering is a separate task. Per CLAUDE.md §3 frontend-vs-non-frontend test ("touches `apps/dashboard/`, `DESIGN_SYSTEM.md`, or any visual artifact"), this plan is non-frontend.

### Q5 — Should this plan include the analytical artifacts (Smith's S, Romney CCM, MDS, Procrustes)?

**Architect read:** **OUT OF SCOPE for T4 redo.** The recovered corpus unblocks them, and they are the natural T5 successor task / Phase 4a closure deliverable. T4 redo's job is methodology re-disposition; bundling analytical computation conflates two distinct review surfaces (methodology re-framing vs. statistical computation). The RD-3 memo §5 names the analytical work as unblocked but does not produce it.

**SME confirm or override.** If the SME prefers to bundle (e.g., "the methodology re-disposition is incomplete without the Romney eigenratio computation on the recovered corpus"), the plan expands to include those tasks and the gate chain lengthens. Architect's preference is to keep T4 redo focused.

### Q6 — Which artifacts trigger S5?

**Architect read:** **The RD-3 memo IS the S5 artifact.** S5 binds "any methodology-page text" describing Note K under the new framing. The RD-3 memo §3 disposition statement is the canonical methodology-page-quotable text; SME PASS on the memo content satisfies S5.

**SME confirm or override.** Alternatives:
- This plan itself is also S5-bound (Architect agrees — that is why this plan is gated by SME PASS before Coder starts; SME PASS on the *plan* is a precondition for SME PASS on the *memo*)
- The recovery report's framing already partially answered S5 (Architect disagrees — the recovery report explicitly *defers* to T4 redo per its §6 Q5 SME ruling)
- The eventual T5 redo's completion report is also S5-bound (Architect agrees — but that is downstream of this memo and gets its own SME gate)

### Q7 — Retroactive clarifications to prior binding notes

**Architect read:** Binding notes 6, A6, B5 (the detector role-change at code-review time precedent — see CLAUDE.md §9 pitfall 13) carry forward unchanged. B7–B9 are vacuous under the new framing. B11 is REPLACED by the RD-2 confabulation classification schema. B14 carries forward and binds the eventual T5 redo. The §8 of the RD-3 memo enumerates the carry-forward mapping.

**SME confirm or override.** The R7-style retroactive clarification work that was done for binding notes 6 and A6 (the detector miscalibration appended-clarifications in the original SME verdict + Amendment 1 verdict) is the precedent. The SME may decide that this T4 redo requires similar appended retroactive clarifications to (e.g.) the T3B detector verdict, the T3C verdict, the T4 SME verdict. Architect's read is that the RD-3 memo §8 carry-forward mapping is sufficient and the prior verdict files do not need to be retroactively edited; the SME's PASS on the memo establishes the new mapping. But if the SME prefers retroactive verdict clarifications, that is a separate work item that the SME schedules.

---

## §7. Boundaries explicitly affirmed

- **The Architect writes plans, not code.** This plan is a plan only.
- **CDA SME PASS or PASS-WITH-NOTES on this plan is mandatory** before Coder starts RD-1. Per S5 from the Task 16 verdict.
- **Mark sign-off on §5 framing decisions Q1–Q3** is mandatory before Coder starts RD-1. These are operator-level calls, not pure methodology.
- **No UI/UX agent gate** for this plan (per §6 Q4 ruling). The downstream methodology-page UI rendering gets its own UI/UX gate as a separate Phase 5/6 task.
- **No `cdb_core/schemas.py` edits.** Pydantic v0.1.11 is unchanged.
- **No `DATA_DICTIONARY.md` edits.** No `cdb_core` schema motion.
- **No `data/raw/*.jsonl` edits.** Append-only is binding (CLAUDE.md §9 pitfall 10). The 24 decline-interview records, the 29 historical failure rows, and the 20 recovery records are preserved verbatim.
- **`data/derived/*.jsonl` is treated as append-only by extension** (Architect convention; SME may rule otherwise — see §6 Q1). No destructive edits to the May 1 hand-coded subtype artifact. New artifact (`decline_interviews_confabulation_classification.jsonl`) is the supplementary mechanism.
- **No prompt-template change.** v1 prompts unchanged.
- **No `cdb_analyze` change** beyond adding `confabulation_classification.py` (which is a Pydantic schema + loader, no analysis logic, no LLM imports — same shape as the existing `safety_subtype.py`). The §4.2 binding constraint (no LLM imports in `cdb_analyze`) is preserved.
- **No analytical computation in this plan.** Smith's S, Romney CCM, MDS, Procrustes are all out of scope per §6 Q5. They are the natural T5 successor.
- **No forbidden vocabulary** in any text produced by this plan, the Coder's RD-1/RD-2/RD-3 commits, or any verdict file. The Reviewer's spot-check enforces. The §1.5 framing is binding throughout, with special attention to the "blind-spot" framing risk in §4.2.
- **No bundling.** RD-1, RD-2 scaffold, Mark's hand-code, and RD-3 are four separate commits per CLAUDE.md §8.
- **The RD-3 memo IS the S5 artifact.** SME PASS on the memo's content satisfies S5 and unblocks any downstream methodology-page UI rendering (which still gets its own UI/UX gate).
- **This plan supersedes Architect Plan Amendment 3, Architect Plan Amendment 4, and the May 1 T4.1/T4.2/T4.2-followup work to the extent that those depend on the now-falsified safety-event premise.** The audit trail (the verdict files, the commits, the SME rulings) is preserved verbatim on master; the supersede is *interpretive*, not destructive.

---

*End of Architect Plan. This plan is gated by S5 from the 2026-05-04 Task 16 SME verdict and requires CDA SME PASS or PASS-WITH-NOTES before Coder starts RD-1. It additionally requires Mark's sign-off on §5 framing decisions Q1–Q3. The plan does NOT trigger a UI/UX agent gate (§6 Q4). Estimated total cost: $0. Estimated wall-clock: 3–5 days. The RD-3 memo is the canonical S5 artifact; SME PASS on the memo's content unblocks downstream methodology-page rendering.*
