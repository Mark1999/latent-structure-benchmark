# CDA SME Plan-Level Verdict — Phase 4b Architect Plan

**Filed:** 2026-05-07
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `docs/status/2026-05-07-phase4b-architect-plan.md` (commit `5e55ba6`)
**Slack channel:** `#lsb-cda-sme`

**Companion docs read in full or in relevant section before this verdict:**
- Source-of-truth philosophy doc: `docs/status/2026-05-07-lsb-philosophy-and-framing.md` (commit `d014112`)
- ARCHITECTURE.md v0.7.2 §1.5 (all sub-sections including new §1.5.7), §5.3 Phase 4 paragraph + Phase 4b runbook + Split G1
- The eight prompt-variant directories `packages/cdb_collect/cdb_collect/prompts/v1_s1` … `v1_s8` (free-list, pile-sort, pile-interview triples)
- The canonical v1 directory at `packages/cdb_collect/cdb_collect/prompts/v1/`
- `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` (parked v2 observation)
- `docs/status/2026-05-05-phase4a-recovery-report.md` §7 forward-carry items 3 and 4
- `packages/cdb_analyze/cdb_analyze/sensitivity.py` (four split-G1 variance functions confirmed present)
- `packages/cdb_analyze/cdb_analyze/gates.py` (`g1_stability_split` confirmed present at line 425)
- `packages/cdb_analyze/cdb_analyze/saturation.py` (`saturation_curve`, `identify_knee`, `SaturationPoint` confirmed present)
- `packages/cdb_core/cdb_core/schemas.py` `DomainResult` G1 fields lines 388–393 (six fields confirmed nullable)
- `data/models/registry.json` (8 added models confirmed present, with field values verified)
- `docs/status/2026-05-07-no-human-baseline-amendment-cda-sme-content-verdict.md` (closing PASS, A1–A6 SATISFIED, B6/T8/T9 carry-forward)
- `docs/status/2026-05-07-t5-redo-cda-sme-content-verdict.md` (T11–T15 SATISFIED at the T5 redo content, carry-forward to Phase 4b T6/T7)
- `docs/status/2026-05-06-t5-redo-cda-sme-plan-verdict.md` (T11–T15 binding text)

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (Register 1 within-model + Register 2 between-model registers preserved; OCI used as a within-model concentration descriptor in the saturation arm, not as consensus; G1 split-axis logic is unchanged at the analytic layer) |
| Vocabulary compliance | PASS on the plan body itself (zero §1.5.4 hits in the plan's own prose) |

The plan is methodologically sound and approved for Coder dispatch with eight binding notes (P1–P8 below). The structural decisions — 20-model slate, eight v1_s* variants, single soft-form v2 ride-along, 3-model saturation reference set, prompt-evolution log mechanism, ride-along ordering before the variance run, and the failures-as-findings G1-failure posture — all hold up under the four-axis review.

PASS-WITH-NOTES rather than PASS because three load-bearing methodology surfaces in the plan need explicit binding before T1 lands: (a) the prompt-evolution log's authorship-provenance row and a definitional clarity around "success rate" granularity (P1, P2, P5); (b) the within-family vs across-family stability framing under Q2 option (B) needs an explicit acknowledgment that the 9th variant is a single arm and therefore cannot sustain a within-v2 stability claim (P3); (c) the per-model G1 diagnostic must inherit the T11 framing-guard discipline at any text surface (P4); plus four smaller methodology disciplines (P6 saturation reference-set update, P7 forbidden-vocabulary discipline on the completion report, P8 carry-forward of B6 / T8 / T9 / T11–T15 to T7).

Coder is authorized to start T1 (prompt-evolution log scaffold + optional v2_soft1 directory creation) immediately. T2 and T3 may proceed after T1. T4 (the main 20×8 variance run) is gated only by T1 / T2 / T3 landing as plan-specified. T7 (the completion report) is methodology-bound text and gets its own SME content verdict at gate chain step 2.

---

## Q1–Q8 rulings

### Q1 — 20-model slate composition

**Ruling: AGREE.**

The eight added models preserve the three-axis spread (origin × openness × collection method) the SME approved for Phase 4a. I verified each of the eight against `data/models/registry.json`:

- All eight `model_id` values are present in the registry.
- The within-family drift surfaces (4.5↔4.6 Claude, 5.2↔5.4 GPT, 4↔4.20 Grok, scout↔maverick Llama, small↔large Mistral, flash↔pro Gemini) are scientifically interesting in their own right per philosophy doc §7 item 2 (drift detection is one of the genuinely valuable findings LSB produces) and ARCHITECTURE.md §1 commitment 10 (longitudinal model tracking).
- Cohere `command-a` adds a CA origin axis the Phase 4a slate lacked. This sharpens the origin-axis spread.
- Gemma-4-26b adds a Google open-weight tier distinct from Gemini, creating a within-vendor open/closed contrast that has no Phase 4a analog.
- Adapter-coverage check: all eight `collection_method` values (`anthropic_api`, `openai_api`, `google_ai`, `openrouter`, `xai_api`) match existing adapters used in Phase 4a. No new adapter work.

**Minor registry/plan discrepancy noted:** the plan §3 row 16 lists `x-ai/grok-4` with `collection_method: openrouter (via OpenRouter)`, but the registry has `collection_method: xai_api` for that model. This is a plan-vs-registry mismatch on a single row, not a methodology defect; the Coder either updates the plan row to match the registry value or the registry to match the operational reality of how Phase 4a reached `grok-4.20` (which in row 6 of the plan is listed as `xai_api (via OpenRouter)`). I leave this to the Coder/Reviewer at T4 dispatch as a procedural cleanup; not a binding methodology note.

The CLAUDE.md §9 pitfall 1 framing in plan §3 ("every cell records both `model_id` and `model_version_returned`; the variance arm groups by `model_id`; the longitudinal Phase 6 view groups by `model_version_returned`") is exactly the right discipline. PASS.

### Q2 — Variant composition

**Ruling: AGREE-WITH-CAVEAT — option (B) accepted with binding note P3.**

I verified the eight v1_s* variant directories on disk. The free-list bodies for v1_s1 through v1_s8 all preserve the imperative anchor pattern: "do not explain or categorize" (v1_s1, v1_s4, v1_s8 paraphrases use "Do not add explanations or group them by category", "no definitions, no commentary, no sub-groupings", "Refrain from adding any notes, explanations, or categorical headings" respectively); all eight retain the numbered-list + one-item-per-line + 200-cap structure; all eight are paraphrases not re-frames. The pile-sort variants similarly preserve the JSON output format and the "every item must appear in exactly one pile" constraint while paraphrasing the surrounding instruction. The pile-interview is identical across versions (and across v1_s7 vs v1 — confirmed as legitimately identical because the prompt is short and structurally tight, not because of a copy error).

The architectural motion of reusing pre-existing variants is methodologically clean. Per CLAUDE.md §6 R8, prompt templates are versioned and never edited in place; the v1_s* directories were authored before this plan and are read-only inputs to it. The Coder does not generate variant text. This is the correct discipline.

Option (B) — adding a single v2_soft1 ride-along — is the right call rather than (A) "8 variants only" or (C) "16 variants total." The reasoning:

- Option (A) defers the philosophy-doc §7 item 4 finding ("confabulation under blind-spot conditions") indefinitely. The 2026-05-06 v2 parked observation is real signal — the imperative phrasing functions as a categorical anchor that ~5/9 informants under cap-exhaustion conditions cited as a refusal trigger. Folding the soft-form into Phase 4b lets that signal be measured against the 8-variant within-imperative cohort while the campaign is running, at marginal cost.
- Option (C) doubles the cell count for diminishing return on the gate question. The within-v2 stability claim that 8 v2_s* would buy is not load-bearing for any current scientific claim.
- Option (B) gets the cross-family contrast at a single-arm cost (~225 cells: 20 models × 1 variant × 5 runs × 2 domains).

**Caveat — binding note P3 below.** With option (B), the 9th variant is a *single arm*, not 8 paraphrases of the soft form. The G1 split-axis stability ratios are computed across the 8 v1_s* variants as the binding gate; the v2_soft1 cluster is a *diagnostic contrast* with one prompt phrasing on each model. The plan §4 is correct that "within-family vs across-family salience stability becomes a diagnostic sub-finding, not the binding gate" — but any text in the completion report (T7) discussing the v1_s* / v2_soft1 contrast must be careful not to imply a within-v2-family stability measurement, because n=1 within v2 supports no such measurement. P3 binds this discipline at the T7 prose surface.

### Q3 — Per-model G1 reporting alongside aggregate

**Ruling: AGREE.**

The aggregate within-mean / between ratio remains the binding gate per ARCHITECTURE.md §5.3 line 1314. The per-model G1 stability vector is correctly characterized as a diagnostic, not a gate. Reporting per-model salience and spatial stability separately is informationally richer than the aggregate alone — a model whose output is salience-stable but spatially-unstable produces categorically different downstream behavior from one with the inverse profile, and surfacing that distinction is consistent with philosophy doc §7 item 3 ("stability under prompt rephrasing" as a genuinely valuable finding).

The per-model vector is **not** a shadow gate. The Coder does not introduce per-model thresholds. A model's per-model ratio above 0.5 does not "fail" that model out of the slate; it surfaces as a diagnostic in the per-model table. This binding discipline is captured in P4 below.

### Q4 — Saturation slate composition

**Ruling: AGREE — keep at 3 reference models.**

The saturation finding is operational-N for within-model Register 1 analysis. Three references span the closed-frontier / cross-vendor-frontier / open-weight axes. The plan's recommendation to substitute `meta-llama/llama-4-maverick` for the registry's existing `llama-3.1-70b` constant in `saturation.py::SATURATION_REFERENCE_MODELS` is correct because Llama 3.1 70B is no longer in the slate; maverick is the closest in-slate equivalent.

Expanding to 5 or 20 multiplies the cell count by 1.7×–6.7× for diminishing return. The saturation curves cluster tightly across vendors per the v0.7 prior (referenced in `docs/SME_REVIEW.md` §3.2). The 3-reference choice respects the methodology-page-named-contribution framing of saturation (per ARCHITECTURE.md §1.5.6 / §4.2.7).

P6 below binds the constant-update discipline: the Coder at T6 must update `SATURATION_REFERENCE_MODELS` from `("claude-opus-4-6", "gpt-4o", "llama-3.1-70b")` to `("claude-opus-4.6", "gpt-5.4", "llama-4-maverick")` (note the model-id-format change from `claude-opus-4-6` dash to `claude-opus-4.6` dot, matching the plan §3 row 1 and the registry). The constant-update is in-scope for T6.

### Q5 — Prompt-evolution log schema

**Ruling: AGREE-WITH-CAVEAT — schema accepted with binding notes P1, P2.**

The schema captures the three things Mark named: which version when, why a new version, success rate per cell. The integration with the existing `prompt_version` schema field on `InformantRecord` is correct — no new schema change needed.

Two refinements binding before T1 lands:

**P1 — `Authored by:` field discipline.** The schema's example v1_s1 entry says "Authored by: [Mark / Architect-as-author — fill at log creation]". This is a placeholder that the Coder must resolve at T1 dispatch *before* committing the log scaffold. The provenance of the v1_s1…v1_s8 prompts is methodologically load-bearing: a future researcher reading the open-data bundle needs to know whether the variants were human-authored, LLM-generated, or copy-paraphrased from a literature reference. CLAUDE.md §6 R12 spirit (no LLM analyst in the analysis pipeline) does not strictly forbid LLM-generated prompts as inputs to `cdb_collect`, but if any of v1_s1–v1_s8 was generated by an LLM rather than by Mark or the Architect, that fact must be recorded in the `Authored by:` field. The Coder asks Mark for the provenance at T1 dispatch; the answer goes into the log entry verbatim.

**P2 — Definitional clarity on success-rate granularity.** Plan §5 Q7 specifies the success rate is computed "per (model × variant × domain) at 5-of-5." The Coder must include the definition inline in the log preamble — what counts as a "successful" cell, and what counts as a "failed" cell, both directionally. My binding read: a cell is *successful* iff it produced a valid `InformantRecord` written to `informants.jsonl` with `qa_passed=True`; a cell is *failed* iff it landed in `failures.jsonl` OR it produced an `InformantRecord` with `qa_passed=False`. The QA-failed-but-not-hard-failed path is what makes this nontrivial: a record can be in `informants.jsonl` with `qa_passed=False` (e.g., a downstream pile-sort failure on a freelist-successful record). The success-rate definition must specify this case.

Three reasons this is binding before T1:

1. The Reviewer cannot verify the per-(model × variant × domain) success-rate computation in T4 acceptance criterion (b) without a definition.
2. A reader of the open-data bundle who recomputes the success rates against `informants.jsonl + failures.jsonl` needs the definition to reproduce the numbers.
3. The 0.80 alert / 0.60 flag thresholds are meaningful only against a defined denominator. If the denominator is "5 attempts" but a model's recovery cells got 6 attempts (per the recovery campaign's 2-attempt budget), the rate is no longer a clean 5-of-5 fraction.

The fix is one paragraph in the log preamble. P2 binds the discipline.

### Q6 — campaign_id naming

**Ruling: AGREE.**

The four campaign_ids (`phase4b-real-2026-05-MM`, `phase4b-saturation-2026-05-MM`, `phase4b-phi4-rerun-2026-05-MM`, `phase4b-tail-rerun-2026-05-MM`) follow the established pattern from `phase4a-recovery-2026-05-05`. The campaign_id substring is the audit primitive for grep-based corpus inventory (per T13 from the T5 redo verdict, which set the precedent for verbatim grep commands as audit primitives). The four IDs are mutually unambiguous and non-overlapping.

One small operational note (not binding): the `2026-05-MM` placeholder must be resolved to the actual collection date at the moment of campaign launch, not at T1 dispatch. The recovery report uses `2026-05-05` because the campaign ran on that day. The Coder at T4 launch fills `MM` with the actual launch date's day-of-month. This is a Reviewer scope-discipline check, not an SME binding note.

### Q7 — Success-rate definition (90% / 80% / 60%)

**Ruling: AGREE-WITH-CAVEAT — see P2 above.**

The 0.80 alert / 0.60 flag thresholds are methodologically defensible as the alert / flag floors. They are non-gating per the failures-as-findings posture (philosophy doc §9, memory `project_failures_are_findings.md`), which is correct under the new framing — a model whose v1_s* variant produces a 0.40 success rate is itself a finding about that model's prompt sensitivity, not a kill-switch trigger.

Mark's "90% successful response" floor is preserved as the *expectation* threshold (the success-rate floor below which Mark wants to be alerted at the prompt-iteration level), with 0.80 as the operational alert and 0.60 as the methodology-page flag. This three-tier structure is consistent with the §6.2 three-tier spend-cap defense pattern and with the §5.3 dual G1 threshold (5.0 operational, 3.0 reported) pattern. The architectural symmetry is correct.

The non-gating discipline is binding at the Coder layer: T4 does not abort if a model's rate falls below 0.60. The cells continue collecting; the log records the rate; the methodology-page flag is set later by the T7 completion report. P5 below binds the non-gating discipline.

### Q8 — G1-failure response posture (THE MAJOR QUESTION)

**Ruling: AGREE — failures-as-findings reframe is accepted as the binding posture.**

This is the most consequential ruling in this verdict and I want to be explicit about the reasoning.

**The original §5.3 runbook's posture** (lines 1330–1331 of ARCHITECTURE.md) is *"if any gate fails: pause. Do not proceed to Phase 5. The Architect agent writes a diagnostic report, and Mark decides whether to redesign prompts, add runs, drop models, or shelve the project. This is the real decision point for whether the core idea works."* Plus *"we do not ship a pretty visualization layer over data we haven't validated."*

That posture predates the 2026-05-07 amendment. It was authored when LSB had:
1. A "no human baseline" question still open (Phase 4c grounding still in scope).
2. A thesis-shaped commitment (the project framing was "we will demonstrate that LLMs cluster differently from humans on cultural domains").
3. A go/no-go decision posture on the entire project.

The amendment landed today (commit `38f5740` content verdict PASS) removes (1) and (2) decisively. The exploratory framing in §1.5.7 ("LSB is **not hypothesis-testing.** It does not predict in advance what models will produce, then test whether they produce it. It does not have a falsifiable claim about model cognition, model bias, or model alignment that the data is designed to confirm or refute") is now binding on every public-facing piece of text the project produces.

Under that framing, "G1 failed" stops meaning "the project's hypothesis is refuted" because the project has no hypothesis. It starts meaning "here is a measurement of within-model variance vs between-model variance, on this data, with this protocol — and the measurement says the variance is comparable, which is itself a finding about how frontier LLMs respond to CDA stimuli."

The architect's recommendation — that G1 PASS / FAIL determines the dashboard's *framing* but not whether the project proceeds — is the right structural call. The §5.3 line "we do not ship a pretty visualization layer over data we haven't validated" remains binding *at a different location of the validation surface*: the validation now means "the variance is **measured and surfaced honestly**," not "the variance is **below threshold**."

**Concrete operational disposition I am binding:**

- **G1 PASS on both axes (both domains).** Dashboard ships with the §5.3-aligned "validated comparison is stable across prompt variants" framing, methodology page describes G1 as a binding gate.
- **G1 FAIL on one axis.** Methodology page surfaces the per-axis result honestly. Dashboard shows the per-model G1 ratios as a first-class diagnostic. The §5.3 variant-expansion runbook still triggers (Coder expands to 16+ variants on the affected model pair via OpenRouter / Hugging Face per ARCHITECTURE.md §5.3 Phase 4b) **before** finalizing the failure call. After variant expansion, if the gate still fails, the disposition shifts: the failure becomes a published finding, not a project-pause. Phase 5 still proceeds. The dashboard's lede on every visualization includes the G1 result.
- **G1 FAIL on both axes.** Same as above plus a methodology-page header note framing the within-model variance as itself a finding. Phase 5 still proceeds.

**Why I accept the reframe rather than holding the original posture:**

The original §5.3 posture line ("the real decision point for whether the core idea works") presupposes a thesis-shaped success criterion. The amendment binds the project to the exploratory framing. Holding the original posture would create a contradiction inside the project's own framing — the methodology page says "we don't test hypotheses," the §5.3 runbook says "if the validation gate fails, the project may need to be shelved." The reader reconciles those by inferring there *is* an unstated hypothesis (perhaps "models will be stable across prompts"), which is the exact framing the amendment removed.

The failures-as-findings posture is the only one that survives the amendment intact.

**However**, the reframe has a concrete prose-discipline cost. T7 (the completion report) and any Phase 6 dashboard lede that reports a G1 failure must be carefully framed. Specifically:

- The completion report must NOT say "the gate failed but the data is still useful" (this implies a thesis frame, with the data as a salvage).
- The completion report must NOT say "the methodology proved the variance was high" (this implies a hypothesis was confirmed).
- The completion report MUST say something like "G1 measured within-model salience variance at X.XX (95% CI [...]) and between-model variance at Y.YY (95% CI [...]) on the [domain] domain. The within/between ratio is Z.ZZ, above the 0.5 operational threshold; the methodology page surfaces this finding as a measurement of the [domain] domain's prompt-sensitivity profile."

P8 below binds this prose discipline at T7 by carry-forward of B6 (a)–(e) from the T4-redo / T5-redo verdicts, supplemented by a new note tied specifically to the failures-as-findings reframe.

**Note on the §5.3 doc text.** ARCHITECTURE.md §5.3 lines 1330–1331 currently say "pause. Do not proceed to Phase 5. The Architect agent writes a diagnostic report, and Mark decides whether to redesign prompts, add runs, drop models, or shelve the project." This text now contradicts the failures-as-findings posture this verdict establishes. The Architect at the close of Phase 4b (in the T7 completion report or in a separate amendment) will need to update §5.3 to reflect the new posture. **This is not a Phase 4b Coder task** — it's a future Architect amendment, post-Phase-4b. Phase 4b's T7 completion report is the surface where the new posture is exercised; the §5.3 doc-update follows. Recording this as forward-carry, not as a Phase 4b binding note.

T8 (the Coder task in plan §8) covers either branch of Q8 cleanly because it is a documentation task (the prompt-evolution log final pass + the closure note). The closure note will reflect whichever G1 outcome materializes. No T8 scope change required.

---

## Prompt-variant reuse — provenance and content ruling

**Ruling: ACCEPTABLE.**

Per the inspection summary above:
- All 8 v1_s* free-list variants are paraphrases preserving the imperative anchor pattern.
- All 8 v1_s* pile-sort variants preserve the JSON output schema and the partition constraint.
- The pile-interview prompt is structurally tight and survives across variants without semantic drift.

The variants cover the right register (free-list, pile-sort, pile-interview) at all three CDA protocol steps. The semantic equivalence is preserved while the lexical surface differs sufficiently to constitute a sensitivity test.

The provenance-recording discipline (P1 above) is the only outstanding question. If the variants were generated by a separate LLM call (not committed code, not the cdb_analyze pipeline — the §6 R12 boundary is preserved), that fact does not invalidate the methodology but must be recorded in the log. If they were human-authored or paraphrase-copied from a methodological reference, that is also fine but must also be recorded.

**My recommendation to Mark on the v1_s* provenance question:** ask the Architect (or recall directly) the actual authorship before T1 lands. The answer goes into the log scaffold's `Authored by:` field. If the answer is "LLM-generated for the sensitivity study," that is acceptable — the variants are inputs to the sensitivity test, not analytical artifacts; they are read-only versioned templates that happened to have an LLM in their authoring chain, and that chain is fully transparent in the log entry.

The pile-interview being identical across v1 and v1_s7 (and likely identical across all v1_s* variants — the prompt is short and structurally tight) is acceptable. Sensitivity at the pile-interview step is dominated by the upstream pile structure (which differs across variants because the pile-sort prompt differs); paraphrasing the interview prompt itself would add noise without separately probing the interview-step sensitivity.

---

## Prompt-evolution log mechanism — methodological soundness ruling

**Ruling: ACCEPTABLE with binding notes P1, P2, P5.**

Three sub-questions to address:

**(a) Is `docs/PROMPT_EVOLUTION_LOG.md` the right place for this data?**

YES, with one structural observation. The data is methodology-page-bound human-readable text describing prompt-version provenance and per-(version × campaign × model × domain) success rates. The success-rate fields are derivable from `informants.jsonl + failures.jsonl` by the Coder's T4 success-rate computation, but the *narrative context* (which campaign produced which version, which model failed at which rate, why a version was created) is not derivable from the JSONL alone. The log is the authoritative narrative surface.

The schema is human-readable markdown, which is correct for a methodology surface (per the philosophy-doc §9 release-for-community-analysis posture — the open-data bundle's README and the methodology page are markdown-readable). A SQLite or JSONL representation would be machine-friendlier but harder to read for a methodology-page reader.

The log is a documentation artifact, not an analysis artifact. It does not import any cdb_analyze code. CLAUDE.md §6 R12 is preserved.

**(b) Is the 0.90 success-rate threshold methodologically defensible as the alert floor?**

YES, with the caveat that it is not the alert floor in the plan as written — the plan §5 Q7 sets 0.80 as the alert floor and 0.60 as the methodology-page flag. The 0.90 number Mark named is the *expectation* — the rate at which a prompt is producing the outputs the protocol asks for. A 0.80 alert and 0.60 flag relative to a 0.90 expectation is a reasonable two-tier degradation profile.

I rule the 0.80 / 0.60 thresholds defensible. They are operational alert thresholds, not methodology-page truth claims. The methodology page reports the actual rates; the log records them in tabular form; the thresholds gate alerts to Mark, not analytical decisions.

**(c) Is the rule "no mid-Phase-4b iteration" correct?**

YES, decisively. The plan §5 specifies that a v2 iteration triggered by below-threshold success rates is a separate post-Phase-4b campaign with its own Architect plan. This is the right discipline because:

1. Mid-campaign prompt iteration corrupts the variance arm. If 4 v1_s* variants were collected on day 1 and a v2 iteration replaced 2 of them on day 5, the resulting cohort is no longer a clean within-imperative-family sample.
2. The G1 split-axis variance computation requires uniform prompt-version coverage across the cohort — different variants for different models would conflate prompt variance with model variance.
3. The failures-as-findings posture means low success rate is itself data, not a defect requiring mid-flight repair.

P5 below binds the no-mid-flight-iteration discipline at the Coder layer.

The mechanism overall is methodologically sound. The three caveats (P1 provenance, P2 success-rate definition, P5 non-gating + no-mid-flight-iteration) bind the disciplines that the plan as written leaves implicit.

---

## Carry-forward of prior binding notes

| Note | Origin | Binding scope on Phase 4b |
|---|---|---|
| **B6 (a)–(e)** (T4-redo public-copy guardrails: no "incorrect" framing for predecessor work; no cross-provider/cross-failure-mode/cross-prompt-type generalization without evidence; no internal-state claims about models; no "PLUS disproportionate CN-origin decline pattern" augmentation; no "publishable" framing) | T4-redo SME verdict chain, B6 element (e) added at T14 of the T5-redo plan-pass verdict | **BINDING on T7 (completion report) and any methodology-page-bound text Phase 4b produces.** The completion report is the methodology surface; B6 (a)–(e) are the public-copy guardrails. |
| **T8** (RD-3 descriptive-shape discipline: no causal language, no introspective language, no stimulus-as-cause framing) | T4-redo RD-3 SME content verdict | **BINDING on T7 prose.** Every methodology-bound sentence in T7 must pass T8. |
| **T9** (RD-3 forbidden softer-than-thinks/believes verbs: no "recognizes," "identifies," "interprets," "comprehends," "perceives" applied to models) | T4-redo RD-3 SME content verdict | **BINDING on T7 prose.** Reviewer's vocabulary scan at T7 includes T9 list. |
| **T11** (numerics-vs-interpretation framing-guard sentences at table boundaries) | T5-redo SME plan verdict | **BINDING on T6 numerics report (if it has tabular comparison surfaces) and T7 (for any §6/§7 cross-domain or cross-model tables).** |
| **T12** (S2 four-state enumeration or S2 citation by file path for any `thoughts_token_count=0` discussion) | T5-redo SME plan verdict | **BINDING on T7** (the post-recovery corpus T4 is built on includes Task #16 reasoning-token records; any `thoughts_token_count` discussion in the completion report inherits T12). |
| **T13** (verbatim grep command for cell-coverage denominators in audit-trail surfaces) | T5-redo SME plan verdict | **BINDING on T7** (any cell-coverage statement in the completion report includes the grep command for the relevant campaign_id substring — `phase4b-real`, `phase4b-saturation`, etc.). |
| **T14** (no "publishable" framing in any methodology-bound text) | T5-redo SME plan verdict, B6 (e) | **BINDING on T7 prose.** Reviewer's vocabulary scan includes "publishable" / "publication." |
| **T15** (Note G verbatim wording preservation if Phase 4a Note G surfaces are quoted) | T5-redo SME plan verdict | **APPLIES IF Phase 4a Note G surfaces are quoted in T7.** If T7 references Phase 4a's "produced no interpretable primary-step output" language, T15 binds. If T7 doesn't quote that language, T15 is N/A for Phase 4b. |
| **A1–A6** (no-human-baseline + §1.5-deepening amendment binding notes) | 2026-05-07 amendment plan verdict, all SATISFIED at content verdict | **SATISFIED globally.** Permanently encoded in the doc state. T7 prose must respect the §1.5 framing established by A1–A6 but does not need to re-encode the amendment's structural disciplines. |
| **Note D** (no ceiling claims pre-Phase-4c) | F1 SME review | **SATISFIED-by-amendment** (Phase 4c removed; ceiling-claim-prevention is now structural, not gate-based). Phase 4b prose does not need to disclaim Phase-4c-pending; the amendment removed that anticipated state. |
| **Note A** (small-n caveat) | F1 SME review | **BINDING on T6/T7.** With 20 models, n_models for the variance-arm Romney CCM is 20 (above the 15 small-n threshold). The small-n warning may not fire on the variance arm. But the per-(model × variant) cell counts are still 5; per-domain bootstrap CIs at n=20 should be reported with their CIs explicitly per ARCHITECTURE.md §4.5. |

---

## New binding notes — Phase 4b inventory (P1–P8)

The Phase 4b campaign introduces methodology obligations not yet in the binding-note inventory. Numbered P1–P8 to keep the Phase 4b series distinct from the parent T4-redo / T5-redo / amendment series. None of P1–P8 require schema changes or code changes outside what's already in the plan.

**P1 — Prompt-variant authorship-provenance recording at T1.**

Before the Coder commits the T1 prompt-evolution log scaffold, the `Authored by:` field for each v1_s* entry must be filled with the actual provenance (Mark / Architect-as-author / LLM-generated-by-[model] / paraphrase-from-[reference]). The Coder asks Mark for the authoritative provenance at T1 dispatch. The placeholder text "[Mark / Architect-as-author — fill at log creation]" must not survive into the committed scaffold.

If the variants were LLM-generated, the log entry records that fact (which model, which prompt was used to generate them, when). This does not violate CLAUDE.md §6 R12 because the variants are inputs to `cdb_collect`, not artifacts of `cdb_analyze`. But the open-data bundle's reproducibility guarantee requires that any LLM step in the methodology chain be transparently recorded.

**Reviewer enforcement:** at T1 commit review, reject if any `Authored by:` row contains placeholder text or empty content. SME content verdict (none gating T1; this is Reviewer-only) double-checks at T7.

**P2 — Success-rate definitional clarity in the log preamble.**

The Coder at T1 includes a definition section in the log preamble specifying:
- A cell is **successful** iff it produced a valid `InformantRecord` written to `data/raw/informants.jsonl` with `qa_passed=True`.
- A cell is **failed** iff it landed in `data/raw/failures.jsonl` OR produced an `InformantRecord` with `qa_passed=False`.
- The per-(model × variant × domain) success rate is `n_successful / n_attempts_targeted`, where `n_attempts_targeted=5` for the variance arm and `n_attempts_targeted=30` for the saturation arm (both per the plan §2 deliverable counts).
- If a cell required a retry under the 2-attempt budget, the cell counts as one attempt regardless of the number of provider calls (consistent with the recovery-report §2 retry-pattern interpretation).

**Reviewer enforcement:** at T1 commit review, reject if the definition section is missing.

**P3 — v2_soft1 single-arm framing discipline at T7.**

If Q2 option (B) is exercised (the v2_soft1 single arm is added), T7 prose discussing the v1_s* / v2_soft1 contrast must:
- NOT imply a within-v2-family stability measurement (n=1 within v2 supports no such measurement).
- Frame the contrast as "the v2_soft1 single-arm cluster sits at MDS coordinates {...} relative to the within-imperative cohort" or equivalent positional language.
- Use the descriptive frame "the within-imperative-family cohort (n=8) shows salience-stability ratio X.XX; the cross-family contrast against the single soft-form arm shows positional shift Y.YY" rather than "v2 is more stable than v1" or "v1 produces more variance than v2."

**Reviewer enforcement:** vocabulary scan at T7 for "more stable than" / "less stable than" / "v2 family" / "within-v2" applied to the v2_soft1 arm.

**P4 — Per-model G1 diagnostic table prose discipline.**

T6 produces the per-model G1 stability vector (per Q3). T7 reports it. The prose surface must:
- Frame the per-model vector as a *diagnostic*, not a per-model gate.
- Not introduce per-model thresholds (e.g., "model X failed at 0.55 above threshold" — there is no per-model threshold).
- Apply T11 framing-guard discipline at the table boundary: the table introduction sentence must explicitly state "per-model salience and spatial stability ratios are diagnostic; the binding gate is the aggregate ratio reported above."

**Reviewer enforcement:** at T7 commit review, the per-model G1 table introduction sentence must include the diagnostic framing.

**P5 — No-mid-flight-iteration + non-gating discipline at T4 dispatch.**

The Coder at T4 does not iterate prompt versions mid-campaign. If a model's per-(variant × domain) success rate falls below 0.60 during T4 collection:
- The campaign continues. The cells continue to be appended to `informants.jsonl` (or `failures.jsonl`).
- The Coder logs the rate in the prompt-evolution log under the standing campaign entry.
- The Coder does NOT create a new prompt version, does NOT modify v1_s*, does NOT pause T4.
- A post-Phase-4b v2 iteration is a separate Architect plan if Mark / the Architect decides one is warranted after T7 lands.

**Reviewer enforcement:** at T4 commit review, the commit must not include any new prompt-version directories. Any new directory under `packages/cdb_collect/cdb_collect/prompts/` triggers Reviewer rejection of T4.

**P6 — `SATURATION_REFERENCE_MODELS` constant update at T6.**

The `saturation.py::SATURATION_REFERENCE_MODELS` tuple currently reads `("claude-opus-4-6", "gpt-4o", "llama-3.1-70b")`. T6 updates this to match the in-slate references per the plan §6: `("claude-opus-4.6", "gpt-5.4", "llama-4-maverick")`. The dash-vs-dot format change in the Claude id reflects the plan §3 model_id format. The update is in scope for T6.

**Reviewer enforcement:** T6 commit review confirms the constant has been updated, with corresponding tests updated to use the new constants.

**P7 — Forbidden-vocabulary discipline scan at T7.**

T7 is methodology-bound text. Reviewer's standing vocabulary scan applies (CLAUDE.md §7, ARCHITECTURE.md §1.5.4 12-row table). The amendment-added rows 11–12 ("LSB hypothesizes that..." / "LSB predicted X and the data confirmed/refuted it") are particularly load-bearing for Phase 4b because the campaign produces gate verdicts (G1) that the original §5.3 text framed as hypothesis-testing-shaped. T7 prose must use "LSB measures..." / "LSB reports..." / "LSB observes..." rather than the §1.5.4 left-column phrasings.

**Reviewer enforcement:** vocabulary scan at T7 includes the full 12-row table.

**P8 — G1-failure-finding prose discipline at T7 (failures-as-findings reframe surface).**

If G1 fails on either axis on either domain, the T7 completion report's framing of that failure must:
- Frame the failure as a *measurement finding*, not a *project-pause trigger* (per Q8 ruling above).
- NOT use language like "the gate failed but the data is still useful" (implies thesis-with-salvage frame).
- NOT use language like "the methodology proved the variance was high" (implies hypothesis-confirmed frame).
- USE descriptive measurement language: "G1 measured within-model salience variance at X.XX (95% CI [...]) and between-model variance at Y.YY (95% CI [...]). The within/between ratio is Z.ZZ, above the 0.5 operational threshold. The methodology page surfaces this finding as a measurement of [domain]'s prompt-sensitivity profile." (or similar).
- Acknowledge the §5.3 variant-expansion runbook as an option Mark decides on after the completion report lands (the completion report does not pre-dispose the variant-expansion call).

**Reviewer enforcement:** at T7 commit review, prose pattern scan for the forbidden phrasings; if G1 failed, the completion report's G1 sub-section must be flagged for SME content verdict at gate chain step 2.

**SME content verdict double-check:** P3, P4, P7, P8 are SME-content-verdict-bound at T7. T11–T15 are SME-content-verdict-bound at T7. The SME content verdict on T7 is the closing gate for Phase 4b at the methodology-bound text surface.

---

## Proactive checks

### Check 1 — n_models on the variance arm vs Romney small-n threshold

The variance arm produces 20 models per (variant × domain). The Romney CCM's small-n threshold is `n_models < 15` (per the project memory `project_romney_small_n_threshold.md`). With n=20, the small-n warning does not fire on the variance arm. This is the first time in the LSB project that the Romney threshold is comfortably above the small-n floor. The methodology improvement is real.

The saturation arm produces 3 models per (domain × N), which is below the small-n floor. But the saturation analysis is *not* a Romney CCM analysis — it is an OCI-stability + salience-rank-stability + Procrustes-RMSE analysis. The Romney threshold does not apply. The saturation curves are plotted at the (model, domain) level, not aggregated across models.

### Check 2 — Forbidden-vocabulary scan of the plan body

I scanned the full plan body (325 lines) for §1.5.4 / CLAUDE.md §7 violations, including the new amendment rows (11–12). Zero hits. The plan stays clean on:

- "worldview" / "believes" / "thinks" applied to models — zero occurrences.
- "within-model consensus" / "within-model cultural consensus" / "within-model eigenratio" / "within-model CCM" — zero occurrences. The plan correctly uses "within-model variance" (the variance computation, not consensus) and refers to OCI by name in the saturation arm.
- "publishable" — zero occurrences.
- "closer to human = better" — N/A (no human baseline in scope).
- "LSB hypothesizes" / "LSB tested whether" / "LSB confirms" / "LSB found that [hypothesis]" / "LSB predicted X" — zero occurrences. The plan correctly uses "Phase 4b is the variance-and-saturation arm of [the exploratory question]" rather than "Phase 4b tests the hypothesis that..."

The plan body itself passes vocabulary compliance.

### Check 3 — Register compliance scan

The plan is consistent with the three-register framework:

- **Register 1 (within-model output distribution analysis):** the saturation arm operates here (OCI, elbow-position stability, Spearman salience stability — all within-model). The plan correctly does NOT call this "within-model consensus."
- **Register 2 (between-model categorical structure analysis):** the variance-arm G1 split-axis is here (within-model variance ÷ between-model variance, with both informed by the 8 v1_s* variants × 20 models). The plan correctly attributes G1 to between-model space.
- **Register 3 (longitudinal drift):** out of scope for Phase 4b. The plan correctly defers the within-family drift surfaces (4.5↔4.6 etc.) to Phase 6's DriftTracker view.

OCI is used consistently as a within-model concentration descriptor in the saturation arm. The plan does not apply RWB CCM at Register 1. PASS on register compliance.

### Check 4 — Cost transparency (per the user-prompt §F)

I do not block on cost. The $120–$300 estimate is a real campaign per the failures-as-findings posture (the philosophy doc §9 release-for-community-analysis intent applies — this data is canonical and intended for the open-data bundle). Mark's standing $10 rule (`memory/feedback_test_budget.md`) is for probes; this is not a probe. Mark sees the $120–$300 number in plan §9 and acts if the upper bound is too high.

The `CDB_MAX_SPEND_USD=50` per-session export is the operational guard. The $300/month cap (ARCHITECTURE.md §6.2) is the upper boundary. The wall-clock estimate (3–5 days distributed across ~1 week) is operationally reasonable.

### Check 5 — Philosophy doc §9 release-for-community-analysis posture survival

I scanned the plan for thesis-shaped framing drift. The plan §1 cleanly anchors at philosophy doc §2 + §9 verbatim. Plan §10 (the Q8 discussion) explicitly cites philosophy doc §9 ("the data is more valuable than our interpretation of it") as the binding rationale for the failures-as-findings reframe. Plan §11 enumerates forbidden scope creep (Phase 5 work, methodology-page UI rendering, cross-amendment scope). Plan §13 consolidates the Q1–Q8 questions cleanly.

The plan body's voice is consistent with the philosophy doc: descriptive ("Phase 4b is the variance-and-saturation arm"), not predictive ("Phase 4b will demonstrate"). The exploratory framing survives contact with the Phase 4b operational realities. PASS.

### Check 6 — Schema field availability for G1 reporting at T6

I confirmed in `cdb_core/schemas.py` lines 388–393 that `DomainResult` carries the six G1 fields (`g1_salience_stability`, `g1_spatial_stability`, `g1_aggregate_stability`, `g1_salience_pass`, `g1_spatial_pass`, `g1_overall_pass`) all as `Optional[float | bool] = None`. T6's acceptance criterion (a) — populating the six fields in `data/results/{family,holidays}/0.3.json` — is schema-supported with no schema change required. R7 (DATA_DICTIONARY lockstep) is vacuously satisfied because no schema change is in scope.

### Check 7 — Saturation reference-model name format consistency

The plan §6 references `anthropic/claude-opus-4.6` (with dot), `openai/gpt-5.4` (with dot), `meta-llama/llama-4-maverick` (with dash). The current `SATURATION_REFERENCE_MODELS` constant uses dash format (`claude-opus-4-6`, `gpt-4o`, `llama-3.1-70b`). The plan's recommended constant update at T6 (per P6 above) must respect the actual model_id format used in `informants.jsonl` records — the records use the dot format (`claude-opus-4.6`, `gpt-5.4`, `llama-4-maverick`). Coder/Reviewer at T6 verify the match between the constant and the records' `model_id` field.

### Check 8 — campaign_id as audit primitive consistency

The four campaign_ids follow the established `phase{N}{X}-{descriptor}-2026-MM-DD` pattern. The recovery campaign's `phase4a-recovery-2026-05-05` is the precedent. The Phase 4b ids drop the day component (`2026-05-MM` rather than `2026-05-05`) because the variance arm runs across multiple days. This is acceptable per the plan §2 specification — the audit primitive is the substring match, and `phase4b-real-2026-05` matches all dates within May 2026.

### Check 9 — Small-n vs Romney threshold reconciliation on the saturation arm

The saturation arm has 3 models. The Romney CCM is not run on the saturation arm (the analysis is OCI + salience-rank stability, not consensus). The small-n threshold does not apply.

The variance arm has 20 models. The Romney threshold is comfortably above n_models < 15 small-n cutoff. The methodology page can report Romney CCM at n=20 with the small-n warning *not* fired. This is a Phase 4b first.

### Check 10 — G1 split-axis variance functions in `sensitivity.py`

I confirmed via grep that `sensitivity.py` has all four split-axis variance functions: `compute_within_model_salience_variance`, `compute_between_model_salience_variance`, `compute_within_model_spatial_variance`, `compute_between_model_spatial_variance`. The plan's assumption that these exist (per ARCHITECTURE.md §5.3 line 1316) is verified. T6's acceptance criterion (a) is structurally supported; the Coder runs the existing pipeline against the post-T4 corpus.

---

## Final disposition

**Verdict:** PASS-WITH-NOTES.

**Phase 4b Coder dispatch:** AUTHORIZED.

The Coder may begin T1 (prompt-evolution log scaffold + optional v2_soft1 directory creation) immediately. T2 and T3 follow after T1. T4 follows after T1/T2/T3 land. T5 follows T4. T6 follows T5. T7 follows T6. T8 follows T7.

**Binding notes summary table:**

| Note | Trigger | Reviewer-enforced or SME-content-enforced |
|---|---|---|
| P1 | T1 | Reviewer |
| P2 | T1 | Reviewer |
| P3 | T7 | SME content verdict + Reviewer vocabulary scan |
| P4 | T7 (if T6 produces per-model table) | SME content verdict |
| P5 | T4 | Reviewer (rejects new prompt-version directories at T4 commit) |
| P6 | T6 | Reviewer |
| P7 | T7 | Reviewer (vocabulary scan) + SME content verdict |
| P8 | T7 (if G1 fails on either axis on either domain) | SME content verdict (closing gate) |

**Carry-forward summary:** B6 (a)–(e) BINDING on T7; T8/T9 BINDING on T7 prose; T11–T15 BINDING on T6/T7 as scoped; A1–A6 SATISFIED-globally; Note D SATISFIED-by-amendment; Note A BINDING on T6/T7.

**Forward-carry to post-Phase-4b:**

- A future Architect amendment must update ARCHITECTURE.md §5.3 lines 1330–1331 to reflect the failures-as-findings G1-failure posture established by this verdict's Q8 ruling. Not a Phase 4b Coder task; a forward-carry Architect plan after Phase 4b closes.
- The provenance answer for v1_s* (Mark's response to P1) becomes part of the open-data bundle's reproducibility surface.
- The plan §3 row 16 `grok-4` collection_method discrepancy with the registry is a procedural cleanup at T4 dispatch.

**Posted to `#lsb-cda-sme`. Binding for Phase 4b. The Coder is authorized to start T1.**

---

*End of CDA SME plan-level verdict. Phase 4b proceeds. The next SME gate is the content verdict on T7 (the completion report) at gate chain step 2.*
