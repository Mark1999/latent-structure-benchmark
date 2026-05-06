# CDA SME Verdict — Phase 4a T5 Redo Architect Plan (plan-level review)

**Filed:** 2026-05-06
**Reviewer:** CDA SME (Opus)
**Plan reviewed:** `docs/status/2026-05-06-t5-redo-architect-plan.md` (commit `2a4c6c2`)
**Slack channel:** `#lsb-cda-sme`
**Predecessor verdicts (still binding, in dependency order — abridged):**
- `docs/status/2026-04-23-phase4a-t5-cda-sme-verdict.md` (original T5 PASS-WITH-NOTES; Notes A, C, D, E, G, K)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S1–S5)
- `docs/status/2026-05-05-phase4a-recovery-cda-sme-verdict.md` (R1–R6)
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1–T7; B6 / B12 / B14 carry-forward; B11 REPLACED)
- `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` (S5-completing PASS-WITH-NOTES)

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS (Register 2 only; Register 1 within-model fields populated as per existing pipeline) |
| Vocabulary compliance | PASS |

The Coder is authorized to start RD-T5-1 immediately on this verdict. RD-T5-2 follows on RD-T5-1 PASS. RD-T5-3 follows on RD-T5-2 PASS. RD-T5-4 follows on RD-T5-3 PASS. The two-stage SME gate structure (this plan-pass verdict + the post-RD-T5-4 content verdict at `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`) is the right shape and matches the parent T4-redo precedent (B14 numerics-vs-interpretation separation).

The plan is methodologically sound. The Architect surfaced six explicit Q1–Q6 questions and bounded scope cleanly. The recompute-from-scratch posture, the no-`thoughts_token_count`-filter posture (verified mechanically by the Architect's grep on `pipeline.py`), the no-`collection_mode`-filter posture, and the B=500 reaffirmation are all correct. The 4-task split honors B14. The decision to sequence RD-T5-1 (build_db.py rerun) first is the right discipline for discharging recovery R5 cleanly.

PASS-WITH-NOTES rather than PASS for two reasons: (a) **the §7 predecessor-delta presentation needs an explicit framing guard** so a reader does not infer that the original T5 was "incorrect" — the framing in §8 is bound by B6, but §7 itself needs the same discipline at the table-introduction level since it sits in RD-T5-3 (numerics) which Reviewer-rejects interpretation; (b) **the §6 cell-coverage denominator has a Note G consequence that needs explicit handling under the new corpus state** — the original T5 §5 used the exact phrase "5 cells produced no interpretable primary-step output," and the redo §6 names a smaller post-recovery decline-interviewable cell count, so the §5/§6 carry-forward of Note G needs an explicit decision on whether to re-state the count or preserve the exact wording with a numeric update.

The five new binding notes (T11–T15 below) tighten the framing of these two areas plus three smaller items. None of the notes block the Coder from starting RD-T5-1.

---

## Q1–Q6 explicit rulings

### Q1 — Recompute from scratch vs. compute deltas from prior T5?

**Architect recommendation:** RECOMPUTE FROM SCRATCH; §7 is a tabular comparison only.

**SME ruling: AGREE.**

Three reasons:

1. **Determinism + clean audit primitive.** The pipeline is deterministic modulo bootstrap RNG. Recomputation against the canonical JSONL with the same parameters is the cleanest audit primitive: the new 0.2 file stands on its own input population, and a future reader can reconstruct it from the JSONL state at this commit without recourse to the 0.1 file.

2. **Bootstrap RNG seed is not fixed.** The Architect notes this explicitly. Computed deltas would inherit bootstrap-induced delta noise on top of corpus-induced delta, complicating any "what changed?" claim. A tabular comparison at §7 sidesteps this: the table reports population-level scalar deltas (n_models, consensus_score, romney_eigenratio) without claiming a CI-overlap analysis between 0.1 and 0.2 — which would require fixed seeds.

3. **§7 should explicitly disclaim the bootstrap-noise consideration** so a reader does not over-read the delta numbers. See T11 below.

I confirm RECOMPUTE FROM SCRATCH. The §7 tabular comparison is the right shape with the framing tightening in T11.

### Q2 — Legacy `thoughts_token_count=0` records (Task #16 S2 disposition)?

**Architect recommendation:** Pipeline does not consume `thoughts_token_count` as analytical input; legacy asymmetry does not bias measures; disclose in §8.4; no filter.

**SME ruling: AGREE — with one schema-of-disclosure refinement.**

I verified at verdict-write time that `packages/cdb_analyze/cdb_analyze/pipeline.py` contains zero references to `thoughts_token_count` (Grep result: 0 matches in pipeline.py; the only file in `packages/cdb_analyze/` that references the field is `confabulation_classification.py`, which is a different code path not exercised by `scripts/analyze.py`). The Architect's mechanical claim holds. The legacy-record / recovered-record asymmetry on this field cannot bias consensus, OCI, MDS, similarity, centrality, or Sutrop CSI under the current pipeline — none of those measures consume the field.

**Refinement (T12 below):** the Task #16 SME verdict S2 named **four** epistemic states for `0` (not three): (1) model produced no reasoning tokens, (2) provider does not surface reasoning tokens, (3) non-reasoning model on a reasoning-capable provider, (4) legacy record from a pre-field era. The user prompt to this review names "three forensic cases" — that is a paraphrase shorthand, but the actual S2 disposition is four-state. T5 redo §8.4 must enumerate **all four** states or cite S2 by reference to avoid under-claiming the disambiguation taxonomy.

The "no filter" disposition is correct. Filtering on `thoughts_token_count` would discard most of the original Phase 4a successful corpus (which carries `0` because the field did not exist at write time — state 4) and would defeat the purpose of "closing Phase 4a." I confirm no filter.

### Q3 — `collection_mode` filter at pipeline invocation?

**Architect recommendation:** NO `--mode` filter (matches original T5 invocation).

**SME ruling: AGREE.**

The original T5 used no `--mode` filter (per its §1.1 command line: `--input data/raw/informants.jsonl --output data/results/ --bootstrap 500`). The pipeline's `collection_mode` filter (`packages/cdb_analyze/cdb_analyze/pipeline.py:85-86`) is opt-in: only applies when `--mode` is passed. The recovered records carry `collection_mode="single_pass"` per recovery campaign convention, the same value the original Phase 4a records carry. Filtering would be a no-op functionally; not filtering preserves invocation symmetry with the predecessor.

I confirm no `--mode` filter. **Procedurally:** the RD-T5-2 commit body should explicitly note that the `--mode` flag was not passed (matching predecessor), so a future audit reader does not have to verify the absence. This is a documentation hygiene item, not a binding note.

### Q4 — Bootstrap design: B=500 reaffirmation, Level 1 / Level 2 split?

**Architect recommendation:** B=500 unchanged; no new Level 1 bootstrap pass.

**SME ruling: AGREE.**

`docs/BOOTSTRAP_DESIGN.md` §3 is binding for v1: Option 2 (annotated uncertainty) at the Level 2 layer is the v1 choice; B=500 was the predecessor T5's parameter; the wall-clock envelope was 12m37s combined and the new corpus is only 20% larger. Adding a Level 1 bootstrap pass for the redo would introduce the documented "underestimates uncertainty" annotation surface (BOOTSTRAP_DESIGN.md §2) and would need its own SME concurrence at the gate where it was reserved (Phase 4b sensitivity study). The redo is not the moment for that.

I confirm B=500 unchanged. The Phase 4b sensitivity study is the natural moment to revisit Level 1 if motivated by the OCI eigenratio diagnostics on the recovered corpus. **No B-bump for the redo.** The wall-clock stop condition (60 minutes per domain) is well-calibrated.

### Q5 — Domain coverage + recovery-cell flagging?

**Architect recommendation:** BOTH family + holidays; report-level recovery count only, no per-cell schema flag.

**SME ruling: AGREE.**

Three reasons:

1. **Both domains is the only defensible scope.** The recovered corpus added cells to both family and holidays (per the recovery report §2 table). Closing Phase 4a at the analytical layer requires both to land at v0.2; otherwise the project's Phase 4b readiness check has an asymmetric basis.

2. **Per-cell flagging is a schema change.** The Architect correctly notes that adding a per-record `is_recovered` flag would require editing `cdb_core/schemas.py` and a matching `DATA_DICTIONARY.md` update under R7. Scope creep. The recovery-affected records are traceable through `qa_notes` substring `phase4a-recovery-2026-05-05` (verified: 20 occurrences on master at this commit).

3. **Report-level count is sufficient transparency.** §6 names the count (which the redo will produce as a number derived from the JSONL); a future reader who needs per-cell identification has the JSONL grep path. This is the "what minimum information is sufficient?" question, and the answer is the report-level count, with the JSONL grep path documented in the report itself for traceability.

I confirm BOTH domains; no per-cell schema flag. **Refinement (T13 below):** the report §6 must include the verbatim grep command (`grep 'phase4a-recovery-2026-05-05' data/raw/informants.jsonl | wc -l`) so a future audit reader can reproduce the count without re-deriving the path.

### Q6 — B6 public-copy guardrails for §8?

**Architect recommendation:** Avoid (a) the original T5's "PLUS disproportionate CN-origin decline pattern" augmentation, (b) any framing that the original T5 was "incorrect" or "should not have been published," (c) cross-provider, cross-failure-mode, or cross-prompt-type generalization, (d) any internal-state claim. §1.5 forbidden vocabulary applies. RD-3 memo cited by path.

**SME ruling: AGREE — with one addition for completeness.**

The four (a)–(d) avoidances correctly identify the binding posture under B6 + parent T4-redo SME T6 + RD-3 memo §6. I want to add a fifth (e) for completeness:

(e) **No claim that the analytical findings constitute a "publication" or are "publishable."** Per CLAUDE.md §1 ("the bar for the methodology page is 'credible to a skeptical reader,' not 'publishable in *Nature*'") and parent T4-redo SME T6 ("no 'publishable' framing"), any phrasing that the redo's analytical results are "publishable" or "publication-ready" is a vocabulary violation. The redo §8 reports findings on the methodology page, not in any publication venue. The Reviewer's vocabulary scan catches this; the SME content verdict double-checks; the Coder's draft must avoid the phrasing.

Beyond (a)–(e), the §1.5 forbidden vocabulary list (worldview, believes, thinks, cultural bias, refused-as-agency) applies throughout, the parent T4-redo SME T9 phrasing exclusions (no "the model recognized," "the model identified," "the model's understanding," "the model's interpretation") apply to any §8 narrative that touches the recovered records' shape, and the RD-3 memo's §3 disposition language is the canonical citation for the cap-exhaustion reframe. I confirm Q6 with the (e) addition.

This is T14 below.

---

## (C) Carry-forward of original-T5 binding notes

The original T5 SME verdict's notes A, C, D, E, G, K. Each classified per the T10 five-category vocabulary from the parent T4-redo SME verdict.

### Note A — `romney_small_n_warning=True`; CCM caveat

**Status: CARRIES FORWARD (active).**

`docs/SME_REVIEW.md` §1.1 sets the small-n threshold at n < 15 (per the 2026-04-23 reconciliation). The post-recovery population is `n_models = 11` for family (10 original + 1 recovered: gemini-2.5-pro × family had 0 → 5 records added) — the exact `n_models` depends on QA-passed denominator at run time, but every plausible value falls below 15. The warning fires; the redo §8 narrates it correctly under `docs/SME_REVIEW.md` §1.1.

Note A is actively gating. The `romney_small_n_warning` field on the new 0.2 DomainResult will be `True`; the §8 narrative must not claim "consensus" without the small-n caveat.

### Note C — Cell-coverage denominator framing

**Status: CARRIES FORWARD (active) — with numeric update.**

The original T5 §6 named the denominator as "18 analyzable cells of the 12-model × 2-domain design; 5 cells produced decline-interviewable outputs." Under the recovered corpus, the denominator changes:

- More cells are analyzable (recovered records crossed `qa_passed=True`).
- Fewer cells are decline-interviewable (most cap-exhaustion-failed cells are now recovered).
- The unexplained-failure residuum (phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1) remains.

The §6 numerics produce the new denominator. Note C's framing posture (qualified denominator binds the consensus claim) survives; the specific numbers update. This is the right form of "active": the binding note is applied, with the new numbers, to the new corpus.

### Note D — No ceiling claims before Phase 4c

**Status: CARRIES FORWARD (active).**

Phase 4c human grounding has not landed. Any ceiling or proximity-to-human-baseline claim is forbidden. The redo §8 makes none; the redo §10 forward-carry references Phase 4c by name as out-of-scope.

### Note E — US-weighted composition caveat

**Status: CARRIES FORWARD (active) — REPLACED augmentation removed.**

Note E's standalone "US-weighted composition" framing carries forward unchanged. The original T5 SME verdict augmented Note E with the Note K "PLUS disproportionate CN-origin decline pattern" framing; that augmentation is now REPLACED per RD-3. Standalone Note E (US-weighted composition) is fine; the Note K augmentation is removed. The Architect's plan §1 disposition table and §2 RD-T5-4 8.5 explicitly handle this; confirmed.

### Note G — Exact wording for uninterviewed cells

**Status: CARRIES FORWARD (active) — with mandatory numeric update.**

Original T5 §5 used the exact wording: *"5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."*

Under the recovered corpus, the count "5" is wrong. Most of those 5 cells were recovered. The post-recovery count of cells producing no interpretable primary-step output is smaller (likely 0–3 cells, depending on QA outcomes on the recovery records and whether the unexplained-failure residuum is counted under "no interpretable primary-step output" or under a separate "unexplained failure" category).

**Two viable approaches:**

1. **Update the count, keep the verbatim shape.** Rephrase to *"N cells produced no interpretable primary-step output; follow-up decline-interview data for these cells was captured in Phase 4a.1 (now reframed per the RD-3 memo)."* The "N" is computed at report-write time. The verbatim "produced no interpretable primary-step output" survives.

2. **Cite the original Note G phrasing as the originating discipline; substitute a new sentence under the new corpus state.** A redo-specific sentence that does not pretend to be verbatim from the original.

I rule for **approach 1** with a small extension. T15 below codifies the binding language. The original Note G's discipline (no "refused" agency framing; descriptive only; cite Phase 4a.1 by name) survives; the count updates; the trailing clause acknowledges that Phase 4a.1's interpretation has been reframed per RD-3.

### Note K — CN-origin decline clustering

**Status: REPLACED (audit preserved).**

Per RD-3 memo §3 and parent T4-redo SME Q3. Note K is REPLACED, not RETIRED, not NOT CONFIRMED, not "superseded." The original Note K hypothesis is mechanically untestable from this corpus; the data shows a different methodologically interesting finding (the confabulation-pattern observation), which is the substantive replacement. No new "Note L" designation. The redo §8 references the RD-3 memo by path when interpretation touches the disposition; does not re-state. Confirmed by parent T4-redo SME B11 = REPLACED.

The redo §9 binding-note compliance table tracks Note K as REPLACED (audit preserved) and cites RD-3 memo. The Architect's plan §1 disposition table and §2 RD-T5-4 8.5 are correctly configured.

### Summary table (audit-friendly)

| Original T5 note | Status under T5 redo | Vocabulary |
|---|---|---|
| Note A (small-n caveat) | Active gating | CARRIES FORWARD (active) |
| Note C (cell-coverage denominator) | Active gating with numeric update | CARRIES FORWARD (active) |
| Note D (no ceiling claims pre-4c) | Active gating | CARRIES FORWARD (active) |
| Note E (US-weighted composition) | Active gating; Note K augmentation removed | CARRIES FORWARD (active) |
| Note G (uninterviewed cells wording) | Active gating with numeric update; verbatim phrase preserved | CARRIES FORWARD (active) |
| Note K (CN-origin clustering) | Mechanically untestable; substantive replacement is the confabulation observation | REPLACED (audit preserved) |

No original T5 note is VACUOUS or SATISFIED-then-extinguished. None has fallen out from under itself; none has been fully discharged at a specific deliverable. All five carrying-forward notes (A, C, D, E, G) actively gate the redo's §8 prose and the §6 numerics.

---

## (D) RD-T5-3 / RD-T5-4 split honors B14

**Verdict: YES, the 4-task split honors B14. Approve as proposed.**

B14 (parent T4-redo SME) carried forward as: *"the separation principle (interpretive content goes in §8.2, supporting numerics in §8.1) survives the change in what is being interpreted; it binds the eventual T5 redo §8 architecture."*

The Architect's split:

- **RD-T5-3** writes §1–§7 (numerics, tables, gate-status surfaces). Reviewer rejects any sentence in §1–§7 that interprets vs. states.
- **RD-T5-4** writes §8 (interpretation), §9 (binding-note compliance), §10 (closure verdict). The Reviewer also confirms RD-T5-4 does not back-edit §1–§7's numerics.

This is the correct shape. The Architect explicitly cites B14 as the rationale (§2 prelude). The two-commit split:

1. **Lets the Reviewer scope each pass cleanly.** RD-T5-3's Reviewer pass scopes to numerics; RD-T5-4's Reviewer pass scopes to interpretation. Each is bounded.

2. **Lets the SME content verdict (gate chain step 3) be issued against an artifact whose numerics have already passed Reviewer.** This is the load-bearing benefit. If §1–§7 and §8 were in the same commit, the SME content verdict would be reading interpretation against numerics that have not yet been Reviewer-confirmed. Splitting them means the SME's content review can take §1–§7 as Reviewer-bedrock.

3. **Lets the Tester run regression on each commit independently.** Each commit is a single Coder task per CLAUDE.md §8 ("one commit per task"). No bundling.

The 4-task structure (RD-T5-1 build_db → RD-T5-2 pipeline run → RD-T5-3 numerics report → RD-T5-4 interpretation report + completion report) is appropriate. **I do not see a case for collapsing to 3 tasks.** Each task has a distinct deliverable and a scope-bounded Reviewer surface; bundling any two would create exactly the audit-trail ambiguity B14 was designed to prevent.

**Confirm 4-task split as proposed.**

---

## (E) RD-T5-1 build_db.py rerun in scope

**Verdict: YES, IN-SCOPE as RD-T5-1 (sequenced first). Approve as proposed.**

R5 from the Phase 4a recovery SME verdict deferred the build_db.py rerun as "separate ops task." The Architect proposes discharging it as RD-T5-1 (the first task in the redo sequence), arguing:

1. **The corpus is fresh; no other pending appends are queued.** This is the cleanest moment to rebuild the open-data bundle SQLite from the canonical JSONL. If other Architect tasks (e.g., the unexplained-failure investigations) appended further records, the bundle would lag again — but at this commit, the JSONL state is stable.

2. **The pipeline at `cdb_analyze.pipeline.load_records()` reads JSONL directly, not SQLite.** Therefore the SQLite bundle staleness does not block the analytical computation in RD-T5-2. RD-T5-1's role is not gating; it is opportunistic.

3. **Mechanical task; one command.** No SME pass beyond this plan's PASS is required. Reviewer scope bounds to `data/open_bundle/lsb.sqlite` modification (binary file) plus Tester regression.

I confirm RD-T5-1 in scope, sequenced first. Three observations:

1. **R5's gate posture survives.** The R5 deferral was about discharging the rerun; this plan discharges it. The gate posture (open-data bundle should be in lockstep with the canonical JSONL state when the project is closing a phase) remains as a general principle for future recovery campaigns.

2. **The "spot-check query returns the recovery record(s)" acceptance criterion is methodologically right.** It verifies the bundle reflects the 20 recovery rows. The Coder should pick a recovery record from the recovery report §2 table and query by `informant_id` against the rebuilt SQLite.

3. **No SME gate on RD-T5-1.** The Architect correctly notes "does not require its own SME pass beyond this plan's PASS." Confirmed. The Reviewer + Tester gates apply per the standard pipeline.

**Sequencing first is correct.** The Architect's argument that RD-T5-1 is independent of T5 (it does not gate the analytical computation) but is the cleanest moment to discharge R5 cleanly, is sound. If RD-T5-1 produces an unexpected build_db.py error, the Coder pauses and surfaces to the Architect; do not improvise a fix. (This stop condition is implicit in the plan's general "Coder pauses on unexpected outcomes" posture; flagging it here for completeness.)

---

## (F) §1.5 framing risks in the plan itself

I scanned the full plan for §1.5 / CLAUDE.md §7 violations. The plan itself is the Architect's text-on-disk, not the methodology-page-bound text the redo will produce, but the plan must already follow §1.5 because the Reviewer's spot-check on the plan commit was already at the standard threshold and any framing drift in the plan would propagate into the Coder's reading of it.

**Findings (full pass):**

- No `worldview`, `believes`, `thinks` (about models). Clean.
- No "publishable" framing. Clean.
- No "closer to human is better." Clean.
- No "within-model consensus" / "within-model CCM." Clean.
- The plan correctly uses "categorical structure," "corpus lens," "output narratives" where the equivalent claim is made. The §1 disposition table row on "Forbidden vocabulary" is well-disciplined.

**One observation that is not a finding but is worth surfacing:**

§2 RD-T5-3 §6 ("Cell-coverage denominator") describes "the analyzable population" and "the decline-interviewable / failed population" and "the unexplained-failure residuum." These are good population-level descriptors. The §6 also says "Cells with all records `qa_passed=False` (the decline-interviewable / failed population — which is now smaller than the original T5's '5 cells' because most of the cap-exhaustion cells were recovered)." That framing is borderline interpretive (the Reviewer would catch it under the "no interpretation in §1–§7" guard) but is fine in the plan itself because the plan is documenting the Coder's instructions, not the report's prose. Coder note: when writing §6, the smaller-than-original-5 framing is interpretation; only state the post-recovery count as a number.

**The plan's §0 prose ("Three things make T5 redo the correct successor task today") is descriptive and survives §1.5.** It uses "instrument artifact, not signal" (correct phrasing from RD-3), "100% recovery rate" (descriptive), "small-n caveat still binds" (methodological hedge). Clean.

**The plan's §1 disposition table, §2 task contracts, §3 dependency chain, §4 Q1–Q6 surface, §5 non-goals, §6 verifier surfaces, §7 forward carry, §8 audit-trail one-liner are all §1.5-clean.** No violations.

PASS on §1.5 framing for the plan itself.

---

## (G) New binding notes

Numbered T11–T15 to continue the parent T4-redo's T-series cleanly. Total binding-note inventory after this verdict:

- 8 original Phase 4a.1 notes (5 vacuous: B7, B8, B9, B11 REPLACED, B13)
- A1–A8 (8 notes; all CARRIES FORWARD active)
- B1–B15 (15 notes; B7/B8/B9/B13 vacuous, B11 REPLACED)
- S1–S5 (5 notes; S5 SATISFIED at RD-3 content verdict)
- R1–R6 (6 notes; R6 SATISFIED, R5 SATISFIED at RD-T5-1)
- T1–T10 (10 notes; all SATISFIED at RD-3 content verdict; gate postures preserved)
- **T11–T15 (5 notes; new at this verdict)**

**Active binding-note count after this verdict: ≈47** (carrying forward from the RD-3 content verdict, plus the 5 new T-series notes; offset by R5/R6 SATISFIED).

**T11. The §7 predecessor-delta table must include an explicit framing-guard line.**

§7 of the redo report is in RD-T5-3 (numerics-only). The Reviewer rejects any §1–§7 sentence that interprets vs. states. But the §7 table introduction needs an explicit framing-guard sentence — without it, a methodology-page reader scanning §7 for "what changed" could naturally infer that "the original T5 was wrong, the redo is right." That inference is the B6-violation §8 is bound against; §7 must not enable it, even structurally.

**Required §7 introduction language (Coder picks one of the three):**

a) *"The following table reports the scalar field deltas between original T5 (0.1) and T5 redo (0.2). Both DomainResults are correct against their input populations. The deltas reflect the population shift introduced by the 2026-05-05 recovery campaign (see §1, recovery report §1)."*

b) *"§7 reports the population-level deltas between 0.1 and 0.2. The 0.1 numerics are correct against the 2026-04-22 corpus; the 0.2 numerics are correct against the post-recovery corpus. §7 reports the deltas without interpretation; the interpretation is in §8 under the RD-3 framing."*

c) *"Population-level scalar deltas (n_models, n_records, consensus_score, romney_eigenratio, romney_small_n_warning, negative_centrality_flag, MDS coordinate count) between original T5 and T5 redo. Both are correct against their respective input populations; the deltas reflect the recovery campaign's population shift, not a methodological correction. Interpretation is deferred to §8."*

Any of the three lands the framing guard at the §7 table boundary. Coder picks; Reviewer confirms; no SME gate on the choice. The Reviewer-rejected interpretation rule (no §1–§7 sentence that says what numbers *mean*) still applies; the framing-guard sentence is *bounding* interpretation, not introducing it.

**Why this is binding at the §7 level (not §8):** §7 is in RD-T5-3; §8 is in RD-T5-4. The Coder's RD-T5-3 commit may land before RD-T5-4 is written. A reader of the report between RD-T5-3 land and RD-T5-4 land would see §7 without §8's framing context. The framing guard is in §7 because §7 must stand alone under partial-report-state visibility.

**T12. The §8.4 disclosure of `thoughts_token_count=0` legacy records must enumerate all four S2 epistemic states or cite S2 by reference.**

The user prompt to this review names "three forensic cases" for the legacy `thoughts_token_count=0` value. The actual Task #16 SME verdict S2 names **four** epistemic states for `0`:

1. The model produced no reasoning tokens (e.g., a non-reasoning model or a reasoning model that bypassed reasoning for this call).
2. The provider does not surface reasoning-token usage in its API response (Anthropic, HuggingFace, non-reasoning OpenRouter models at this commit).
3. A non-reasoning model on a reasoning-capable provider.
4. Legacy record from a pre-field era (Phase 4a pre-Task-#16 successful records).

The §8.4 prose must not under-claim the disambiguation. **Required:** §8.4 either (a) enumerates all four states explicitly, or (b) cites S2 by file path (`docs/status/2026-05-04-task-16-cda-sme-verdict.md` Q2/S2) and states which state(s) apply to the original Phase 4a corpus (state 4) and which apply to the recovered records (state 1, 2, or 3 depending on provider). The pipeline-no-consume claim ("`packages/cdb_analyze/cdb_analyze/pipeline.py` does not reference `thoughts_token_count`; therefore the legacy state-(4) records co-exist in the analytical input without bias") follows the enumeration.

The Reviewer confirms the four-state enumeration or the S2 reference in §8.4. The SME content verdict double-checks.

**T13. The §6 cell-coverage denominator must include a verbatim grep command for the recovery-affected cell count.**

Per Q5 ruling: per-cell flagging is out of scope; report-level count is sufficient transparency. The transparency posture requires that a future audit reader can reproduce the count without re-deriving the path. The §6 must include the verbatim Bash command:

```
grep 'phase4a-recovery-2026-05-05' data/raw/informants.jsonl | wc -l
```

This command produces the recovery-row count (= 20 at this commit; per-domain breakdowns are derivable by adding `| grep '\"domain_slug\":\"family\"'` or `| grep '\"domain_slug\":\"holidays\"'`). The §6 prose can cite the command output verbatim. Future audit readers running the command at later JSONL states will see the count grow if subsequent recovery campaigns append further `phase4a-recovery-2026-05-05` rows (which they should not — the substring is campaign-specific and append-only) or stay at 20 if the campaign is closed.

The grep command is the audit primitive, not the count itself. The §6 must state both the count and the command.

**T14. The §8 public-copy guardrails include the addition (e): "no 'publishable' framing."**

Per Q6 SME ruling. The Architect's recommended (a)–(d) avoidances (no Note K augmentation, no "incorrect" framing for original T5, no cross-provider/cross-failure-mode/cross-prompt-type generalization, no internal-state claim) are correct. Add (e): no claim that the analytical findings constitute a "publication" or are "publishable." The redo §8 reports findings on the methodology page, not in any publication venue; CLAUDE.md §1 is unambiguous.

The §8 prose, the §10 closure verdict, the completion-redo report all pass the "publishable" vocabulary scan. The Reviewer enforces; the SME content verdict double-checks.

**T15. Note G's verbatim wording is preserved with a numeric update; the original phrase ("produced no interpretable primary-step output") survives; the trailing clause acknowledges Phase 4a.1's reframing.**

Per the Note G carry-forward analysis above. The original T5 §5 language was: *"5 cells produced no interpretable primary-step output; follow-up decline-interview data for these cells will be captured in Phase 4a.1."*

The redo §6 (numerics) reports the new count as a number. The redo §8 (interpretation) restates the verbatim discipline. The required redo §8 language for Note G compliance is:

*"N cells produced no interpretable primary-step output; follow-up decline-interview data for these cells was captured in Phase 4a.1 and is now interpreted under the framing of `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (RD-3 memo)."*

Where N is the post-recovery count derived from §6. The verbatim phrase "produced no interpretable primary-step output" survives. The trailing clause acknowledges that Phase 4a.1's interpretation has been reframed (Note K REPLACED), citing the RD-3 memo by path. No "refused" agency framing. No claim that the cells were "fixed" by Phase 4a.1; the Phase 4a.1 work characterized them under the original framing, and that framing is now reframed per RD-3.

**Alternative wording the Coder may use** (any of these lands the discipline):

- *"N cells produced no interpretable primary-step output; follow-up decline-interview data was captured in Phase 4a.1, and the interpretation of those follow-ups is in the RD-3 reframing memo."*
- *"After the 2026-05-05 recovery campaign, N cells still produced no interpretable primary-step output (the unexplained-failure residuum and any residual cap-exhaustion cells); the Phase 4a.1 follow-up data for the originally-affected cells is interpreted under the RD-3 framing."*

The Coder picks; Reviewer confirms the verbatim phrase + RD-3 path are present; SME content verdict checks.

---

## Proactive checks

### Check 1 — n_models + small-n threshold under recovered corpus

The recovered corpus adds gemini-2.5-pro (×10 cells across both domains), llama-4-maverick (×4 cells), and glm-5.1 (×6 cells) to the QA-passed population. The `n_models` for family is likely 11 (10 original + 1 new model that crossed `qa_passed=True` post-recovery: gemini-2.5-pro). The `n_models` for holidays is likely 11 or 12 depending on QA outcomes (8 original + new models crossing qa_passed: gemini, glm-5.1, possibly grok-4 if its holidays cells move from decline-interviewable to QA-passed, though grok-4's holidays cells are in the decline-interview corpus, not the recovery corpus — so grok-4 likely stays at 0 for holidays). All plausible values are below 15. The small-n caveat still binds.

The redo §3 stop-condition checks should specifically include `n_models < 15` as a fired warning, not a blocked stop condition. The pipeline already produces `romney_small_n_warning = True` automatically at n < 15. No code change.

### Check 2 — Romney threshold under recovered corpus

`docs/SME_REVIEW.md` §1.1 sets the operational threshold at λ₁/λ₂ > 5.0, with the small-n warning at n < 15. The original T5 had eigenratios of 10.79 (family) and 9.22 (holidays), both well above 5.0. The redo eigenratios are likely in the same order of magnitude — adding ~3 models to a population of 10–8 should not collapse the dominant eigenvalue ratio below 5.0 unless one of the new models is a strong outlier on the similarity matrix. If the redo eigenratio falls below 5.0 on either domain, the disposition shifts from STRONG_CONSENSUS to a different consensus_type and §8 must narrate that shift carefully (still no "incorrect for original T5" framing; the population shifted). The pipeline produces the consensus_type classification automatically; no §8 narrative drift.

This is a forward-looking concern; not blocking. If the redo eigenratio collapses below 3.0, the Coder pauses and surfaces to the Architect (the dispositions are different and the §8 framing decision is non-trivial).

### Check 3 — MDS coordinate stability under recovered corpus

The original T5 MDS placed Gemini, glm-5.1 (× holidays), and grok-4 (× holidays) at the periphery (MDS dim2 ranges of [-0.52, 0.56] for some cells); the recovered records change the coordinate field. The redo MDS may show different coordinates for these models. This is expected and not a finding — MDS reorientations under population shifts are mathematically normal. The redo §8 must not interpret coordinate shifts as evidence about the models themselves; the shifts reflect population recomposition, not model behavior.

The R11 uncertainty (mds_uncertainty per model) is the right surface for displaying the ellipses. The Reviewer's R11 confirmation in RD-T5-2 acceptance criteria is correct.

### Check 4 — Forbidden vocabulary skim of the plan

I checked the plan in full for §1.5 / CLAUDE.md §7 / parent T4-redo SME T9 violations. Findings reported in (F) above. The plan itself is PASS on vocabulary compliance. The Reviewer's spot-check on each Coder commit catches any drift in the actual report prose; my SME content verdict on RD-T5-4 double-checks the §8/§9/§10 prose.

### Check 5 — RD-T5-2's `--mode` flag absence vs. predecessor symmetry

The original T5 invocation used `--input data/raw/informants.jsonl --output data/results/ --bootstrap 500` (no `--mode`). The Architect's RD-T5-2 invocation matches: `--domain {family,holidays} --input data/raw/informants.jsonl --output data/results --bootstrap 500 --analysis-version 0.2`. The `--analysis-version 0.2` is the only deliberate departure from the predecessor invocation; that is necessary to write to the new 0.2 path. Confirmed symmetric.

The pipeline log for the original T5 read "10 models, 41 total records" (family) and "8 models, 33 total records" (holidays). The redo's pipeline log will show different numbers but the same shape ("N models, M total records"). The §2 of the redo report records the verbatim log per the predecessor convention.

### Check 6 — The completion-redo report mirrors the original's structure

Per RD-T5-4 §2: the completion-redo report mirrors the original's structure (§1 timeline, §2 gate status, §3 data artifacts, §4 cost summary, §5 B2 backup, §6 DATA_DICTIONARY addendum (none), §7 outstanding carry-forward, §8 Phase 4b readiness, §9 verdict). The plan correctly notes "no DATA_DICTIONARY addendum" for the redo (no schema change). The original is preserved as audit; the new completion report is the successor with cross-references at §1 timeline.

This is the right shape. No SME gate beyond the SME content verdict on the analysis report. The completion-redo report is methodology-text under SME PASS-WITH-NOTES; the Reviewer enforces the §1.5 vocabulary scan; the SME content verdict double-checks.

---

## What I am explicitly NOT ruling on

- **The eventual T5 redo numerics (the actual values that will appear in the 0.2 DomainResults).** I am ruling on the plan, not on the analytical output. The SME content verdict on the redo analysis report (gate chain step 3) reviews the actual prose against the actual numerics.

- **The phi-4 ×6, gpt-5.4-mini ×2, mistral-small ×1 unexplained-failure investigations.** Out-of-scope per recovery report §7 and the redo plan's §5 non-goals. Separate Architect tasks.

- **The v2 prompt comparison sub-study.** Phase 5+ candidate per `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`. The redo §8 may reference the document by path but does not propose a v2 arm.

- **Phase 4b sensitivity study (G1 stability).** The redo's PASS is one input to Phase 4b's go/no-go decision; the other inputs are the unexplained-failure dispositions and any v2 prompt arm. Phase 4b is a separate Architect task.

- **Phase 4c human grounding.** Out-of-scope per Note D.

- **Phase 5/6 methodology-page UI rendering.** Out-of-scope per the plan's §1 disposition table. The redo §8 is text-on-disk; the UI rendering is a separate Phase 5/6 task with its own UI/UX gate.

- **Drift / longitudinal Procrustes.** Multiple version snapshots required; out-of-scope until Phase 6+.

- **DeclineInterview schema gaining `thoughts_token_count`.** Task #16 SME Q5 directional preference. Backlog.

- **Lede generation for Phase 4a results.** `cdb_publish` territory; the post-T5-redo DomainResults are an input. Separate task per CLAUDE.md §6 R12.

---

## Carry-forward note

This verdict establishes T11–T15 (5 new binding notes). The notes apply to:

- **T11 (§7 framing guard):** RD-T5-3 (numerics report). Coder applies; Reviewer confirms; no SME content verdict pass on T11 specifically (Reviewer rejects if missing).
- **T12 (§8.4 four-state enumeration or S2 citation):** RD-T5-4 (interpretation). Coder applies; Reviewer confirms; SME content verdict double-checks.
- **T13 (§6 grep command):** RD-T5-3. Coder applies; Reviewer confirms.
- **T14 (§8 (e) "no publishable framing"):** RD-T5-4. Coder applies; Reviewer confirms vocabulary scan; SME content verdict double-checks.
- **T15 (Note G verbatim phrase + RD-3 trailing clause):** RD-T5-4 §8. Coder applies; Reviewer confirms verbatim phrase present + RD-3 path cited; SME content verdict double-checks.

T11–T15 are local to the T5 redo scope. Each is a memo-content discipline (numerics-vs-interpretation separation per B14, scope discipline per parent T4-redo SME T6, vocabulary discipline per §1.5, audit-trail transparency per CLAUDE.md §9 pitfall 5/10). None require schema changes. None require code changes outside what's already in the plan.

The original T5 binding notes (A, C, D, E, G, K) are classified above (Section C). The parent T4-redo binding notes (T1–T7 SATISFIED at RD-3 content verdict; T8–T10 SATISFIED at RD-3 content verdict; gate postures preserved) are not re-litigated here. B6 / B12 / B14 from the parent T4-redo verdict carry forward (active) and bind T5 redo §8 architecture; B14 specifically binds the 4-task split, which is honored. R5 (Phase 4a recovery) is SATISFIED at RD-T5-1.

S5 (Task #16) was fully consumed at the RD-3 content verdict; the gate posture (future methodology-page-bound text on Note K routes through CDA SME) survives. The T5 redo §8 prose is methodology-page-bound text; this very plan-pass verdict and the future RD-T5-4 content verdict together satisfy the S5 gate posture for the analytical-layer methodology-page-bound text.

---

## Gate disposition

**RD-T5-1 (build_db.py rerun):** **AUTHORIZED** to start immediately on this verdict. Reviewer + Tester gates per the standard pipeline. No further SME re-review on RD-T5-1 unless Reviewer surfaces a deviation.

**RD-T5-2 (run analysis pipeline):** **AUTHORIZED** to start after RD-T5-1 lands. Coder uses the invocation from the plan §2 RD-T5-2 (`--bootstrap 500 --analysis-version 0.2`, no `--mode` filter). Reviewer + Tester gates per the standard pipeline.

**RD-T5-3 (numerics report §1–§7):** **AUTHORIZED** to start after RD-T5-2 lands. Coder applies T11 (§7 framing guard) and T13 (§6 grep command). Reviewer rejects any §1–§7 sentence that interprets vs. states; rejects any §7 table without a framing-guard sentence; rejects any §6 cell-coverage denominator without the grep command verbatim.

**RD-T5-4 (interpretation §8–§10 + completion report):** **AUTHORIZED** to start after RD-T5-3 lands. Coder applies T12 (§8.4 four-state enumeration or S2 citation), T14 (§8 (e) "no publishable framing"), T15 (Note G verbatim + RD-3 trailing clause). The §8 prose passes the §1.5 forbidden-vocabulary scan throughout. The Reviewer rejects any back-edit of RD-T5-3's §1–§7 numerics. The Reviewer enforces vocabulary; the SME content verdict at `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md` reviews §8/§9/§10 prose against §1.5, B6, B14, T11–T15, and the four-axis scorecard.

**SME content verdict (gate chain step 3):** **PENDING** until RD-T5-4 lands. Verdict file: `docs/status/2026-05-06-phase4a-t5-redo-cda-sme-content-verdict.md`. Verdict can be PASS, PASS-WITH-NOTES (with required Coder follow-up commit), or FAIL (returns to Architect for re-plan).

**No UI/UX gate** on this plan or its four Coder tasks (analytical-layer; per parent T4-redo SME Q4 precedent).

**No additional Mark sign-off required.** The §5 framing decisions on the parent T4-redo plan are already on master via the RD-1/RD-2/RD-3 commits; the T5 redo inherits that framing.

---

## Sign-off

The Architect's plan is methodologically sound. The 4-task decomposition honors B14 (numerics-vs-interpretation separation). The RD-T5-1 sequencing discharges R5 cleanly at the cleanest possible moment in the project's audit-trail topology. The Q1–Q6 surface is well-bounded; my rulings on Q1–Q6 are AGREE on Q1, Q3, Q4, Q5, AGREE-WITH-REFINEMENT on Q2 (four-state, not three), AGREE-WITH-ADDITION on Q6 ((e) "no publishable" framing).

The original T5 binding notes carry forward correctly: A, C, D, E, G as CARRIES FORWARD (active) — with Note C and Note G requiring numeric updates under the new corpus state, and Note E with the Note K augmentation removed. K is REPLACED (audit preserved) per RD-3 memo and parent T4-redo SME B11.

The plan is PASS-WITH-NOTES. T11–T15 are the new binding notes; T11 (§7 framing guard) and T14 (§8 (e) "no publishable") are the most load-bearing for B6 public-copy discipline. T12 (§8.4 four-state enumeration), T13 (§6 grep command), T15 (Note G verbatim) are smaller but real disciplines.

Coder may start RD-T5-1 immediately. RD-T5-2 follows. RD-T5-3 follows after RD-T5-2 lands; Coder applies T11 + T13. RD-T5-4 follows after RD-T5-3 lands; Coder applies T12 + T14 + T15. The SME content verdict at gate chain step 3 closes Phase 4a at the analytical layer.

*Posted to `#lsb-cda-sme`. Binding for RD-T5-1 (gate authorization), RD-T5-2 (gate authorization), RD-T5-3 (T11, T13), RD-T5-4 (T12, T14, T15), and the SME content verdict gate. The CDA SME thanks the Architect for the unusually clean structure of this plan, the proactive grep verification on `pipeline.py`'s non-consumption of `thoughts_token_count` (Q2), the explicit B14 invocation in the §2 prelude (the 4-task split is structurally correct), and the careful preservation of original-T5 audit trail (no edit to 0.1 JSONs, no edit to the original analysis report, no `.SUPERSEDED.md` annotation — successor with cross-reference is the right discipline given both reports are correct against their respective input populations).*
