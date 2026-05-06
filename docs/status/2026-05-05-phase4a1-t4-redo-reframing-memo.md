# Phase 4a.1 T4 Redo — Reframing Memo (Note K REPLACED)

**Memo date:** 2026-05-06 (commit date; filename retains 2026-05-05 anchor date per parent plan §1 disposition table)
**Scope:** Phase 4a.1 T4 redo, replacing the T4.2 Note K disposition under the 2026-05-04 cap-exhaustion reframe
**Status:** Draft — pending Reviewer PASS and CDA SME content verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`

**Audit-trail one-liner:** This memo replaces the May 1 "CONFIRMED — Gemini single-provider safety-layer activation" disposition of Note K, produced under parent T4-redo plan (`docs/status/2026-05-05-t4-redo-architect-plan.md`, SME PASS-WITH-NOTES at `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`, T1–T7 binding), implementing RD-3 via the RD-3 architect plan (`docs/status/2026-05-06-t4-redo-rd3-architect-plan.md`, commit `7afdf4b`) and its SME verdict (`docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md`, commit `15732bd`, T8–T10 binding), after RD-1 (commit `ad5f975`) and RD-2 (commits `148a620`, `5172b0d`) closed.

**Companion documents:**
- Task #16 CDA SME verdict (S5 originator): `docs/status/2026-05-04-task-16-cda-sme-verdict.md`
- Phase 4a recovery report: `docs/status/2026-05-05-phase4a-recovery-report.md`
- v2 free-list prompt forward-carry: `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`
- RD-2 confabulation classification module: `packages/cdb_analyze/cdb_analyze/confabulation_classification.py`
- RD-2 hand-coded artifact: `data/derived/decline_interviews_confabulation_classification.jsonl`

---

## §1 Header

**Date:** 2026-05-06
**Scope:** Phase 4a.1 T4 redo, replacing T4.2 Note K disposition under the 2026-05-04 cap-exhaustion reframe
**Filename anchor:** The memo's filename uses the 2026-05-05 date because that is the date of the Phase 4a recovery campaign and the parent T4-redo plan; the memo's own commit date is 2026-05-06. The 2026-05-05 anchor preserves the binding path set by the parent plan. See §6.5 of the RD-3 architect plan.

**Gate chain:** CDA SME PASS-WITH-NOTES on the RD-3 architect plan (T8–T10 new binding; Q1–Q7 rulings) → this Coder commit → Reviewer PASS → Tester PASS → CDA SME content verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` (completes S5 from Task #16).

---

## §2 What Changed

### Layer A — The May 1 disposition (the superseded claim)

The May 1 T4.1/T4.2 work disposed Note K as "CONFIRMED — Gemini single-provider safety-layer activation, cross-domain (family + holidays), with bipartite K-frame/K-vocab trigger pattern (2 K-frame, 7 K-vocab)." That disposition was committed in good faith under a PASSed gate chain. The 9 Gemini decline-interview rows classified as `safety_event_attribution` in `data/raw/decline_interviews.jsonl` were treated as evidence that the underlying Phase 4a Gemini failures were safety-policy events. The originating hand-coded artifact is preserved at `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (non-authoritative; annotated by sibling `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`, RD-1 commit `ad5f975`).

### Layer B — The 2026-05-04 cap-exhaustion finding

Three independent probes (Stage 1.5, Stage 1.5b, Stage 1.6; commits `d06e64c`, `19d67f1`, `bef7660`) and the 2026-05-05 recovery campaign (commit `3634e52`) demonstrated that the originating Phase 4a Gemini failures were instrument events. The `max_output_tokens=4096` cap was reached during reasoning before any visible output emitted — the model exhausted the cap on reasoning tokens and produced no visible output. The Task #16 cap fix (`max_tokens=16384`) recovered all 10 Gemini cells at a 100% rate. The failure was a property of the measurement instrument's configuration, not of the model's safety policy.

### Layer C — What this means for the 9 rows (scoping)

This reframe applies to the **9 originally-Gemini rows** whose `under_blind_spot=true` — conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time. The model received the empty-output text and the decline-interview prompt; it did not receive the API-level diagnostic that would have shown the cap exhaustion (`output_tokens == 0 AND thoughts_token_count > 0`). Subsequent uses of "blind-spot conditions" in this memo use this shorthand.

The 9 narratives in which the model's outputs attribute the failure to safety mechanisms, task paradoxes, or topic sensitivity are now best understood as confabulation patterns: the output narrative attributes failure to a mechanism consistent with categorical knowledge from the training corpus, when the actual mechanical cause was invisible from the inputs available at decline-interview time.

**The other 15 decline-interview records in `data/raw/decline_interviews.jsonl` are unaffected by this reframe.** Three z-ai/glm-5.1 family-domain rows involve an empty-freelist-propagation upstream bug (a different mechanical cause). The remaining 12 records have non-cap-exhaustion upstream causes with their own classifications. This memo is local to the 9 originally-Gemini cap-exhaustion rows.

---

## §3 Disposition: Note K is REPLACED

Note K, originally framed as "CN-origin model decline clustering," is REPLACED under the 2026-05-04 cap-exhaustion reframe. The 9 decline-interview narratives that the May 1 disposition treated as safety-event evidence are now understood as output patterns produced under blind-spot conditions: the actual mechanical cause of the empty output (a `max_output_tokens=4096` cap reached during reasoning before any visible output emitted) was not surfaced in the inputs available to the model at decline-interview time, and the output narrative attributes the failure to mechanisms — safety protocols, task paradoxes, topic sensitivity — consistent with categorical knowledge from the training corpus rather than with the actual mechanical cause. The substantive narrative content remains real and analytically informative: it characterizes the shape of attribution patterns the model's outputs produce when asked to interpret an event whose actual cause is invisible from the available inputs. The recovery campaign of 2026-05-05 (`docs/status/2026-05-05-phase4a-recovery-report.md`) re-collected those cells under the corrected `max_tokens=16384` configuration with a 100% Gemini recovery rate, replacing the failure rows with substantive informants. The originating Note K hypothesis is no longer testable from this corpus; it is replaced by the confabulation-pattern observation.

---

## §4 Substantive Observation Under Post-Recovery Conditions

### 4.1 Distribution report

The 9 originally-Gemini decline-interview rows have been hand-classified under the RD-2 confabulation classification schema by `classifier_id="mark"`. The artifact is at `data/derived/decline_interviews_confabulation_classification.jsonl`; the schema and loader are at `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` (`ConfabulationClassification` class, `ConfabulationLabelValue` enum, `load_confabulation_classifications` loader).

The distribution across the five `ConfabulationLabelValue` labels is:

| Label | Count |
|---|---:|
| `safety_attribution_confabulation` | 4 |
| `task_paradox_confabulation` | 2 |
| `mixed_attribution` | 3 |
| `topic_sensitivity_confabulation` | 0 |
| `not_confabulation` | 0 |
| **Total** | **9** |

All 9 rows carry `under_blind_spot=true`. All 9 rows carry `classifier_id="mark"`.

### 4.2 Schema-scope note (unused label)

The `topic_sensitivity_confabulation` label was defined a priori in the RD-2 schema alongside `safety_attribution_confabulation` and `task_paradox_confabulation` as a third primary confabulation shape: narratives attributing failure to topic-sensitivity considerations ("religious," "cultural," "biased," "uncurated"). Under the v1-prompt and cap-exhaustion-condition cohort, this label was not exercised by any of the 9 rows. This is not a schema defect; it is a scope boundary. The schema admitted three primary attribution shapes plus a blended shape and an escape hatch; under the present cohort's conditions, two of the three primary shapes appeared (plus the mixed-attribution escape). Cross-prompt or cross-condition cohorts may yield the third primary shape, and the schema accommodates it.

### 4.3 No `not_confabulation` rows (SME T5 else clause)

The schema's `not_confabulation` escape hatch was defined a priori: rows in which the output narrative correctly identifies the failure cause (a mechanical error, a technical glitch) or genuinely does not claim to know — rows that are not confabulation under this framing. Under the present cohort's conditions (all 9 rows produced under blind-spot conditions, all 9 originating from cap-exhaustion failures), the escape hatch was not triggered. No row's narrative correctly identifies the cap-exhaustion cause; the attribution in every row is non-mechanical. The blind-spot conditions framing applies uniformly across the 9 rows.

### 4.4 Stimulus-as-anchor observation

Five of the 9 confabulation rows — the 2 `task_paradox_confabulation` rows and 3 of the `mixed_attribution` rows — carry a secondary attribution shape alongside their primary label. As the v2 free-list prompt status document (`docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`, §5) characterizes it: across 9 hand-coded confabulations, 5 (2 task-paradox + 3 mixed) carry a "the instructions made me do it" flavor, and the v1 free-list prompt's imperative phrasing ("do not explain or categorize") appears as a categorical anchor those 5 narratives cite as their proximate attribution.

To be precise about what this claim is: 5 of 9 confabulation narratives reference the v1 prompt's imperative phrasing as their stated reason for declining. The narratives cite it as a proximate attribution; the v1 prompt's imperative phrasing serves as a categorical anchor for those 5 rows in the sense that the narratives cite it as their reason. This is a descriptive observation about what the narratives reference, not a causal claim about what the prompt mechanically produced. Whether this stimulus-citation pattern persists under softer phrasing — as the v2 prompt forward-carry doc §2 proposes — is an open empirical question this corpus cannot answer. This corpus has no comparison arm: all 9 rows were collected under v1-prompt conditions. The forward-carry pointer in `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` names a Phase 5+ comparison-study candidate, and that document is the canonical record for the v2 prompt suggestion. The observation is referenced here by path; this memo does not duplicate the v2 prompt status document's content.

**Scope discipline (SME T6).** This is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence. The observation is reported here as a descriptive property of the confabulation corpus under its specific collection conditions, not as a claim about the model's categorical-reasoning behavior in general.

---

## §5 What the Recovered Corpus Enables (and Doesn't)

### Enables

With 20 recovered informants from the 2026-05-05 campaign (10 Gemini, 6 glm-5.1, 4 llama-maverick; all appended to `data/raw/informants.jsonl` per the recovery report), the Phase 4 analytical layer — Smith's S, Romney CCM, MDS, Procrustes, OCI — can now run on the corrected corpus. That analytical work is the natural T5 / Phase 4a closure deliverable. This memo names it as unblocked at the data layer; it does not compute any of those statistics.

### Does not compute

The statistical computation (Smith's S, Romney CCM, MDS, Procrustes, OCI) is out of scope for this memo per parent SME Q5. It is a distinct review surface requiring its own Architect plan with full SME review.

### Caveat: legacy `thoughts_token_count` asymmetry

Downstream analytical work consuming `thoughts_token_count` will need to address the legacy `thoughts_token_count=0` records explicitly. The field was added by Task #16; original Phase 4a successful records pre-date it. A value of `0` in a legacy record means the field was not captured at collection time — it does not indicate the model produced no reasoning tokens. Task #16 SME verdict S2 established the four epistemic states the value `0` represents; state (4), the legacy-record case, applies to the original Phase 4a pre-Task-#16 records.

---

## §6 What This Memo Does Not Claim

This memo does not claim:

- That the confabulation pattern or the stimulus-as-anchor observation reflects the model's categorical structure, cognition, or any internal reasoning state. The §1.5 framing applies throughout: these are observations about the shape of output narratives, not claims about the model.
- That the confabulation pattern generalizes beyond the 9-row, single-provider, two-domain, v1-prompt cohort. Any cross-provider, cross-model, cross-failure-mode, or cross-prompt-type generalization requires new evidence.
- That the v1 prompt templates are modified. They are unchanged. A potential v2 prompt modification is a Phase 5+ forward-carry pointer referenced in a separate status document.
- That the CDA protocol is modified in any way.
- That any schema in `cdb_core/schemas.py` is modified.
- That any statistical analysis is computed from the recovered corpus. No Smith's S, Romney CCM, MDS, Procrustes, or OCI calculation is performed here.
- That this confabulation finding carries a new Note designation. The observation is the replacement for Note K; it is not "Note L" or any other separately designated hypothesis.
- That any Note other than Note K is reframed. This memo is local to Note K and the cap-exhaustion reframe.
- That the v2 prompt sub-study is proposed or initiated. The v2 prompt status document parks the suggestion as a Phase 5+ candidate; this memo references it by path only.

---

## §7 Forward Carry

These are all enumerated and documented elsewhere. This memo is the single index point for the current state.

- **`build_db.py` rerun** — separate ops task, deferred per recovery report §5 / SME R5. The SQLite open-bundle at `data/open_bundle/lsb.sqlite` is stale relative to `informants.jsonl`. Command in recovery report §5.

- **phi-4 ×6 adapter task** — separate Architect task per recovery report §7 item 4. The phi-4 failures (5 HTTPStatusError + 1 ValueError) are a separate adapter issue unaddressed by the cap fix.

- **gpt-5.4-mini ×2 + mistral-small ×1 unexplained-failure investigation** — separate task per recovery report §7 item 3. These failures are not cap-exhaustion; root cause unknown.

- **v2 prompt comparison study** — Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. Trigger conditions are in that document §4. Design must retain v1 as a parallel arm; see that document for Mark's notes on the comparison-study design requirements.

- **T5 redo / Phase 4a closure analytical computation** — separate Architect plan with full SME review surface per parent SME Q5. The recovered corpus enables this; the analytical work is unblocked at the data layer and requires its own plan.

---

## §8 Audit Trail

### Predecessors (superseded, audit preserved)

- May 1 hand-coded artifact: `data/derived/decline_interviews_safety_attribution_subtype.jsonl` — annotated by `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`, RD-1 commit `ad5f975`.
- T4.2 cross-tab script: `scripts/phase4a1_note_j_crosstab.py` — annotated by `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`, RD-1 commit `ad5f975`. Script preserved for code-reference value only; do not re-run for methodology purposes.
- Original Note K hypothesis statement: preserved verbatim in the prior verdict files. Not edited.

### Falsifying evidence chain

- `docs/status/2026-05-04-task-16-architect-plan.md`
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5 originator)
- `docs/status/2026-05-05-phase4a-recovery-architect-plan.md`
- `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md`
- `docs/status/2026-05-05-phase4a-recovery-report.md`

### Replacement evidence

- `data/derived/decline_interviews_confabulation_classification.jsonl` (RD-2 hand-code, commit `5172b0d`)
- `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` (RD-2 schema, commit `148a620`)

### Gate verdicts

- Parent T4-redo plan SME verdict: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1–T7)
- RD-3 architect plan SME verdict: `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md` (T8–T10 new; Q1–Q7 rulings)
- RD-3 content SME verdict (pending, S5-completing): `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md`

### Carry-forward of binding notes (SME T7, T10)

Per T10 (RD-3 plan SME verdict), each binding note is categorized as exactly one of: **CARRIES FORWARD (active)** / **CARRIES FORWARD (latent)** / **REPLACED (audit preserved)** / **VACUOUS (audit preserved)** / **SATISFIED (specific deliverable; gate posture preserved)**.

**Original Phase 4a.1 binding notes (1–8):**
- Notes 1, 2, 3, 5, 6, 7, 8: CARRIES FORWARD (active) — structural concerns (enumeration discipline, expected-rate baseline, cross-tab structure, audit-trail requirements, recursive-decline rule) survive the reframe.
- Note 4 (Note K count thresholds ≥5/2–4/1/0): CARRIES FORWARD (latent) — the threshold tree is no longer applied to any active Note K hypothesis, but is preserved as available for future hypotheses.

**A-series (Amendment 1, A1–A8):**
- A1–A5, A7, A8: CARRIES FORWARD (active).
- **A6 (T3A pre-T3B gate — decline-interview detection precedes subtype refinement):** CARRIES FORWARD (active) — explicitly named per SME T7. The sequencing posture is not affected by this reframe.

**B-series (B1–B15):**
- B1, B2, B3, B4, B6: CARRIES FORWARD (active).
- **B5 (detector role-change SME review at code-review time precedent — CLAUDE.md §9 pitfall 13):** CARRIES FORWARD (active) — reaffirmed. Any future detector helper development that involves cross-boundary reuse routes through the CDA SME at code-review time.
- **B7, B8, B9 (Amendment 2 disposition arithmetic):** VACUOUS (audit preserved) — the count-threshold disposition arithmetic these notes governed (K-frame ≥5 / 2–4 / 1 / 0) is no longer applied because Note K is REPLACED. The arithmetic is preserved as audit at the Amendment 2 SME verdict; those historical decisions remain in the record.
- B10: CARRIES FORWARD (active) — soft, future batches.
- **B11 (K-frame/K-vocab subtype binding):** REPLACED (audit preserved) — the K-frame/K-vocab dichotomy is superseded by the RD-2 confabulation classification schema (`safety_attribution_confabulation` / `task_paradox_confabulation` / `topic_sensitivity_confabulation` / `mixed_attribution` / `not_confabulation`). The May-1 schema is preserved as audit at `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`.
- B12: CARRIES FORWARD (active) — binding precedent for future batches.
- **B13 (soft, K-frame definition refinement at N≥10):** VACUOUS (audit preserved) — the K-frame N≥10 refinement question is moot because the K-frame/K-vocab dichotomy is not carried into the new schema. The refinement question is preserved as audit.
- **B14 (T5 §8.1/§8.2 numerics-vs-interpretation separation):** CARRIES FORWARD (active) — the separation principle (interpretive content in §8.2, supporting numerics in §8.1) survives the change in what is being interpreted; it binds the eventual T5 redo §8 architecture.
- B15: CARRIES FORWARD (active) — soft, dashboard glossing.

**S-series (Task #16, S1–S5):**
- S1–S4: CARRIES FORWARD (active) — local to Task #16 scope; unchanged.
- **S5 (Note K re-classification under new framing must route through CDA SME before any methodology-page text):** SATISFIED (specific deliverable; gate posture preserved) — the specific deliverable S5 required (this memo, reviewed by CDA SME at the content verdict) is landed by this commit; the gate posture — that future methodology-page-bound text on Note K routes through the CDA SME — survives as a general principle and is not extinguished by this specific deliverable.

**R-series (Phase 4a recovery, R1–R6):**
- R1–R5: CARRIES FORWARD (active) — local to the recovery operation; do not bind T4 redo, but R1's "replace as authoritative for the cell" framing is canonical for the recovered records.
- **R6 (recovery rate <80% threshold):** SATISFIED (specific deliverable; gate posture preserved) — explicitly named per SME T7. The 2026-05-05 recovery achieved 100% recovery rate, well above the 80% threshold. The threshold itself remains available for future recovery campaigns; R6's gating role on this campaign was fully satisfied without triggering.

**T-series (T4 redo, T1–T10):**
- **T1 (blind-spot first-use definition + vocabulary discipline):** SATISFIED (specific deliverable; gate posture preserved) — §2 defines "blind-spot conditions" on first use with the required wording. The vocabulary discipline (§1.5-clean phrasings throughout) applies as a continuing gate posture.
- **T2 (RD-2 enum rename `safety_filter_confabulation` → `safety_attribution_confabulation`):** SATISFIED (specific deliverable; gate posture preserved) — discharged at RD-2 commit `148a620`.
- **T3 (RD-1 docstring banner — two-line, including re-run warning):** SATISFIED (specific deliverable; gate posture preserved) — discharged at RD-1 commit `ad5f975`.
- **T4 (9-row scoping in §2; `thoughts_token_count=0` caveat in §5):** SATISFIED (specific deliverable; gate posture preserved) — §2 scopes the reframe to the 9 originally-Gemini rows; §5 includes the legacy `thoughts_token_count=0` caveat.
- **T5 (else clause: not-confabulation escape not triggered; blind-spot framing applies uniformly):** SATISFIED (specific deliverable; gate posture preserved) — §4.3 explicitly states the escape hatch was not triggered.
- **T6 (§4 scope discipline: descriptive + distribution claims only; no generalization; no Note designation; no "publishable" framing):** SATISFIED (specific deliverable; gate posture preserved) — §4 reports the distribution, the schema-scope note, the no-`not_confabulation` note, and the stimulus-as-anchor observation at the descriptive-shape level. §4.4 includes the required scope-discipline sentence.
- **T7 (§8 explicitly names A6 and R6; supersede-convention not codified as CLAUDE.md §9 pitfall):** SATISFIED (specific deliverable; gate posture preserved) — A6 and R6 explicitly named above. Supersede-convention note below.
- **T8 (§4 stimulus-as-anchor observation at descriptive-shape level only):** SATISFIED (specific deliverable; gate posture preserved) — §4.4 uses descriptive-shape language ("narratives cite," "narratives reference") throughout. No causal or introspective framing.
- **T9 (two phrasing additions to the §1.5 forbidden list):** SATISFIED (specific deliverable; gate posture preserved) — phrasings that smuggle introspective access via softer verbs (citing recognition, identification, understanding, or interpretation as model properties) have been excluded throughout; the narrative-shape substitutes are used in their place (e.g., "the narrative attributes," "the response text identifies," "the output narrative's framing").
- **T10 (active/latent/replaced/vacuous/satisfied classification in §8):** SATISFIED (specific deliverable; gate posture preserved) — this §8 mapping applies the five-category structure.

### Supersede-convention note (SME T7 second clause)

The sibling `.SUPERSEDED.md` annotation pattern (a new file alongside the artifact, with no destructive edits to the JSONL itself) is the project's *operational* practice for marking superseded `data/derived/` artifacts. It is applied verdict-by-verdict, not blanket-binding, and is **not** codified as a CLAUDE.md §9 pitfall. The convention is governed by the SME's Q1 ruling in the parent T4-redo verdict (`docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`).

### Section-to-binding-note mapping (audit-friendly)

| Memo section | Binding notes satisfied |
|---|---|
| §1 Header | (cross-references parent plan + parent SME verdict + RD-1 + RD-2 commits) |
| §2 What changed | **T1** (blind-spot first-use definition); **T4** (9-row scoping) |
| §3 Disposition | parent SME Q3 (REPLACED is binding); **T1** (vocabulary discipline) |
| §4 Substantive observation | **T5** (else clause: no `not_confabulation` rows); **T6** (scope discipline); **T8** (descriptive-shape level); **T9** (phrasing exclusions applied) |
| §5 What the corpus enables | parent SME Q5 (analytical work out of scope); **T4 extended** (`thoughts_token_count=0` caveat) |
| §6 What this memo does not claim | parent §1.5 framing; **T6** (forbidden generalizations) |
| §7 Forward carry | parent SME "What I am explicitly NOT ruling on"; recovery report §7 |
| §8 Audit trail | **T7** (A6 + R6 explicit; supersede-convention not codified); **T10** (five-category classification) |

---

*End of reframing memo. This memo is the canonical S5 artifact. CDA SME PASS on the memo's content at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` fully satisfies S5 from the Task #16 verdict and unblocks downstream methodology-page UI rendering (which still requires its own UI/UX gate).*
