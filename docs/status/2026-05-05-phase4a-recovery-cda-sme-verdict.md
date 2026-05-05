# Phase 4a Recovery Campaign — CDA SME Verdict

**Date:** 2026-05-05
**Reviewer:** CDA SME agent (Opus)
**Plan reviewed:** `/opt/lsb-agent/docs/status/2026-05-05-phase4a-recovery-architect-plan.md`
**Slack channel:** `#lsb-cda-sme`
**Posted:** 2026-05-05

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (collection-layer task; no Register 1/2/3 statistics computed) |
| Vocabulary compliance | PASS |

The Coder is authorized to start Task R1 conditional on binding notes R1–R6 below. None of the notes block the recovery script's *behavior contract* (target list, retry budget, idempotence, campaign-id wiring, dry-run-first); they tighten the surrounding documentation, the recovery report copy, and the deferral language to keep S5 clean for the future T4-redo task.

---

## Executive summary

The plan is well-grounded. The Architect did the right thing by surfacing six explicit gating questions and proactively bounding scope (no T4-redo, no `cdb_core/schemas.py` change, no prompt-template change, no deviation from the v0.1.11 schema, no edits to existing JSONL lines). The recount of failures.jsonl (20 in-scope cells, 9 deferred) is correct — I verified all 20 lines individually against the §1 disposition table. The probe evidence chain (Stage 1.5 → 1.5b → 1.6 → 1.7) is the right empirical foundation for a corpus modification: three independent probes plus a cross-provider validation, with a residual ~10% per-cell failure rate that the plan handles by logging-not-crashing rather than papering over.

My rulings on Q1–Q6 are confirmations. The most important ruling is on Q5 (S5 binding): I confirm the Architect's read that **this recovery operation does NOT trigger S5**, and I explain in §B why. The reframe of the recovered records' epistemic status (instrument event → recovered substantive output) is a methodology-touching question that lands at the *T4-redo* task, not at the recovery operation that produces the records.

---

## Axis-by-axis findings

### Axis 1 — Protocol validity: PASS

- The recovery uses the production CDA pipeline post-Task-16: `GeminiAdapter` and `OpenRouterAdapter` at `max_tokens=16384`, with `thoughts_token_count` capture. The CDA three-step protocol (free list → pile sort → pile interview) is unchanged.
- v1 prompt templates are unchanged. Per Task 16 SME ruling on Q3, `max_tokens` is an adapter parameter, not a prompt-content change — no prompt-version bump is required and none is proposed.
- Temperature conventions (T=0.7 free list, T=0.3 pile sort per `ARCHITECTURE.md` §4.1.3) are preserved by the unchanged `run_informant` codepath.
- The `--dry-run` precondition in R1 behavior 7 is the right hygiene step. Stage 1.6 / Stage 1.7 used the same pattern at probe scale; reusing it for the canonical-corpus recovery is consistent.
- Truncation-k (25), N=5 per cell, reflexive card deck — all unchanged. The recovery script is a target-list-driven invocation of the existing protocol, not a re-implementation.

### Axis 2 — Analytical validity: PASS

- No analysis is computed by this task. R1/R2 are collection-layer operations; they do not touch `cdb_analyze`, do not compute OCI / CCM / MDS / Procrustes / bootstrap CIs, and do not modify any `DomainResult`.
- The `thoughts_token_count` asymmetry between recovered records (non-zero where surfaced) and pre-Task-16 records (uniformly `0` because the field didn't exist at write time) is non-disruptive. Per Task 16 SME §C and S2: `0` already conflated three epistemic states (no reasoning happened / provider doesn't surface reasoning / field absent at write time). Adding a fourth case ("legacy record from a pre-field era") is captured by the same `0` and does not change downstream semantics. The diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` correctly will not fire on legacy records (intended; not a bug).
- The `--skip-already-recovered` idempotence check on `(model_id, domain_slug, run_index, campaign_id)` is sound. It is structurally equivalent to `collect.py`'s `--skip-collected`, but at cell granularity rather than model granularity, which is the correct primitive for a recovery operation.
- The `assert len(targets) == 20` defense against `failures.jsonl` drift is appropriate. It is a structural invariant the script can verify cheaply.

### Axis 3 — Claims validity: PASS-WITH-NOTES

- The recovery operation itself makes no model-comparative or methodology-page claims. Good.
- The plan correctly frames the recovered records as the same kind of artifact the original Phase 4a runs would have produced *had the cap been correctly set at collection time*. They are not "fixed" records, they are *the records that would have been collected under the corrected instrument configuration.* This is the right framing because it preserves the original Phase 4a as the first-instrument-configuration artifact while making the recovered records the corrected-instrument-configuration artifact. Both are real measurements; they are not in competition.
- **Hedge on "supersedes":** the §1 disposition table says "the historical failure rows are de-facto superseded but never edited." The word "superseded" is doing a lot of work — it carries a normative claim that the recovered records are *better* than the failure rows. They are not better in an absolute sense; they are different artifacts produced under a different (and corrected) instrument configuration. The recovery report should use **"replace as authoritative for the (model, domain, run_index) cell at downstream analysis time"** rather than "supersede" to keep the epistemics clean. See R1.
- **Hedge on the success threshold (≥85% / ≥17 of 20):** I am comfortable with this threshold *for the recovery operation as such* but want it explicit in the recovery report that ≥85% is the operational success criterion, not a methodological success criterion. The 1–3 residual cells that may fail at 16384 are themselves a finding — they are evidence of either (a) a deeper instrument bug than the cap accounts for, or (b) a model-deterministic failure mode at this prompt × this cap. Both are diagnostic. Logging as `recovery_failed=true` with the verbatim final response is the right disposition; do NOT bump to 32768 in-flight (the plan correctly defers this). See R2.
- The recovery operation does not re-classify any Phase 4a.1 decline-interview row, and does not move any of the 9 hand-coded `safety_event_attribution` rows. Those rows live in `decline_interviews.jsonl`, not in `informants.jsonl` / `failures.jsonl`, and they are downstream of the original `failures.jsonl` rows that the recovery does not edit. So the recovery operation's claims-validity surface is genuinely small. The methodology-page-text question (S5) lives in the T4-redo task, not here.

### Axis 4 — Audience translation: PASS-WITH-NOTES

- No forbidden vocabulary in the plan. I checked. No `worldview` / `believes` / `thinks` applied to models. No "publishable." No "closer to human is better."
- The plan's framing as "instrument fix" / "cap-exhausted reasoning" / "instrument event" is consistent with Task 16 SME notes S1/S3. Good.
- The recovery report itself has not yet been written (R2 produces it). The recovery report copy must inherit the same disciplined framing. See R3 for the exact phrasing the recovery report must use.
- The `qa_notes` campaign-id mechanism is purely operational; it is not user-facing copy. No vocabulary concern there.

---

## Q1–Q6 explicit rulings

### Q1 — Recovery target population: strict (only the 20 known-failed cells) or broad?

**Architect read:** Strict.
**SME ruling:** **CONFIRM.**

The 20 cells are the population for which the cap-bump remedy is established by Stages 1.5/1.5b/1.6/1.7. Broad targeting would conflate three distinct epistemic populations:
- Cells that succeeded at 4096 and might "improve" at 16384 — but "improve" is not a defined operation; the protocol is fixed; collecting more runs at a different cap is a separate methodological question (the saturation sweep, `ARCHITECTURE.md` §4.2.7).
- The 9 out-of-scope failures (phi-4, gpt-5.4-mini, mistral-small) — different root causes, not addressed by the cap fix.
- Cells that were never run in Phase 4a — that is full collection, not recovery.

A broad target would also break the `assert len(targets) == 20` invariant that defends against silent drift in `failures.jsonl`. Strict is correct.

### Q2 — Per-cell retry policy: 2 attempts max, then log `recovery_failed=true` and continue?

**Architect read:** 2 attempts max.
**SME ruling:** **CONFIRM.**

Stage 1.7 saw a ~10% first-attempt failure rate; a second attempt is courtesy and provides diagnostic value (a deterministic same-cell failure on attempt 2 is itself a finding — see R2). Three or more attempts inflates spend without commensurate signal; if a cell deterministically fails twice at 16384, it is unlikely a third attempt at the same configuration breaks the pattern. The right disposition for a 2-attempt failure is to log the verbatim final response in `failures.jsonl` with `recovery_failed=true` and let the Architect schedule a follow-on diagnostic (possibly a `max_tokens=32768` probe on the residual cells, possibly a deeper investigation if the failure mode is structurally different from cap exhaustion).

### Q3 — Inter-call delay for rate-limit safety?

**Architect read:** No explicit delay; reactive 30s on 429 only.
**SME ruling:** **CONFIRM.**

Rate-limit posture is not a methodological question; the Architect's empirical read (glm-5.1 and Gemini calls are slow naturally; OpenRouter has not surfaced 429s in probes) is operationally sound. Reactive 30s exponential backoff on observed 429 is the standard adapter behavior and that pattern is unchanged. The 5s inter-attempt courtesy gap (R1 behavior 3) is sensible and orthogonal to rate-limit concerns.

If during execution the script repeatedly trips reactive 429 backoff and total wall-clock blows past the 45-min projection, the recovery report should note this — but as an operational finding, not a methodological one.

### Q4 — One-shot vs. resumable?

**Architect read:** Resumable (idempotent on `(model_id, domain_slug, run_index, campaign_id)`).
**SME ruling:** **CONFIRM.**

The append-only convention on `informants.jsonl` (CLAUDE.md §9 pitfall 10) makes the idempotence check a 4-line implementation. Re-running after a 25-minute partial-completion abort and replaying minutes 0–25 is wasteful and increases the surface for inconsistent state. The idempotence key includes `campaign_id`, which means the recovery script will *not* skip a cell whose only existing record was the original (failed) attempt — only cells that already have a recovery-tagged record are skipped. That is the correct semantic.

**One sharpening — see R4.** The idempotence check should use the campaign-id substring in `qa_notes`, not parse the field. The campaign-id mechanism the plan inherits from SHAKEDOWN_PROTOCOL.md is a substring-in-`qa_notes` convention, not a structured field. The script must perform a substring match (`"campaign_id=phase4a-recovery-2026-05-05" in qa_notes`), not a regex with anchors that would falsely fail if the field was concatenated with other notes.

### Q5 — Does this recovery plan trigger the S5 binding (Task 16 SME verdict) on Note K reclassification?

**Architect read:** No.
**SME ruling:** **CONFIRM. The recovery operation does not trigger S5.**

S5 is forward-looking and gates the future T4-redo task — specifically, the methodology-page text describing the Phase 4a.1 disposition table under the cap-exhaustion reframe. The recovery operation:

1. Does not re-classify any Phase 4a.1 decline-interview row. The 9 hand-coded `safety_event_attribution` rows live in `decline_interviews.jsonl`, not in `informants.jsonl` / `failures.jsonl`. The recovery operation appends to the latter two files; it does not touch the former.
2. Does not modify the methodology-page text for Note K. No methodology page text is generated by this task.
3. Does not modify the disposition table for the 9 originally-Gemini safety-event-attribution rows. Those rows were classified on the *substantive content of the follow-up interview*, not on the empty primary-step output. The cap-exhaustion reframe affects the *attribution chain* but not the substantive classification — see Task 16 SME §B for the full argument.
4. Does not modify any analysis output (`DomainResult`, OCI, CCM, MDS, Procrustes). T4-redo will do that under its own SME PASS chain, gated by S5 explicitly.

The recovery records are added to the canonical corpus but not analyzed by this task. **Adding records to the corpus is a corpus-modifying operation; it is not yet a corpus-interpretation operation.** S5 binds the latter, not the former.

**However:** when T4-redo is scoped, S5 will require the T4-redo Architect plan to address points 1–3 of Task 16 SME §B verbatim. The recovery operation makes that future task possible (the recovered records are what T4-redo will analyze) but does not pre-decide its outcome.

The Architect's deferral here is therefore exactly correct.

### Q6 — `build_db.py` rerun timing?

**Architect read:** Yes, but as ops follow-up after recovery completes.
**SME ruling:** **CONFIRM.**

`lsb.sqlite` in `data/open_bundle/` is a derived artifact; the canonical truth is the JSONL. The bundle has no public DOI yet (Phase 4 G1/G2/G3 not yet evaluated, per `DATA_DICTIONARY.md` §0). The internal-only rebuild can happen after recovery without reproducibility consequences for any external consumer. Filing as a separate ops task is consistent with CLAUDE.md §8 "one commit per task." See R5 for the small clarification I want in the recovery report.

---

## Proactive checks

### A. Path segregation deviation from SHAKEDOWN_PROTOCOL — examined and accepted

`SHAKEDOWN_PROTOCOL.md` §2 establishes a four-layer non-canonical-data labeling regime: (1) path segregation under `data/shakedown/`, (2) gitignore, (3) `build_db.py` exclusion, (4) per-record campaign tag in `qa_notes`. The recovery plan reuses *only* layer (4) — path segregation, gitignore, and build-script exclusion are deliberately *not* applied because the recovery records are intended to be canonical.

This is the right choice and is consistent with the SHAKEDOWN_PROTOCOL precedent rather than a violation of it. The shakedown protocol's four layers exist precisely because shakedown data is *non-canonical* — it must be machine-prevented from being confused with canonical data. The recovery records are *canonical* — they are intended to replace the failure rows in downstream analysis. So the four-layer regime would actively obstruct the recovery's purpose; only the per-record campaign tag (which provides forensic filterability across the unified canonical stream) is the appropriate primitive to inherit.

The campaign-id substring-in-`qa_notes` mechanism is a stable contract:
- `scripts/qa_check.py` does not filter on `qa_notes` content (it operates on parsed fields), so the additional substring is invisible to QA.
- `scripts/build_db.py` writes `qa_notes` verbatim to the SQLite `qa_notes` column, so downstream SQL queries can filter on `qa_notes LIKE '%campaign_id=phase4a-recovery-2026-05-05%'` to isolate recovered records.
- Future T4-redo tooling that needs to distinguish recovered cells from original-Phase-4a cells has a stable filter primitive available.

The precedent applies cleanly. No methodology concern.

### B. Cross-record comparability post-recovery — examined and accepted

The asymmetry between recovered records (with non-zero `thoughts_token_count` where surfaced) and pre-Task-16 Phase 4a records (with `thoughts_token_count=0` because the field didn't exist at write time) is genuinely benign for downstream analysis:

1. **Note J cross-tab.** Note J operates on `freelist.parsed_items`, `pile_sort.parsed_piles`, `interview.parsed_pile_labels`, and outcome categories from decline-interview classification. It does not consume `thoughts_token_count`. Asymmetric population of that field is invisible to Note J.

2. **Note K disposition under the cap-exhaustion reframe.** The recovered records *replace* the failure rows for those 20 cells in T4-redo's analysis; the legacy 0-valued `thoughts_token_count` on the *successful* original Phase 4a records is not analytically relevant because T4-redo (per S5) will be analyzing the disposition of the failure-becomes-success population, not the successful-was-successful population.

3. **MDS / consensus measures.** OCI / CCM / Procrustes operate on `parsed_piles` co-occurrence matrices. They do not consume `thoughts_token_count`. Asymmetric population is invisible.

4. **The diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0`.** Pre-Task-16 records cannot trigger this invariant (both fields zero or absent). Recovered records that successfully produce output cannot trigger it either (`output_tokens > 0`). The invariant fires *only* on `failures.jsonl` rows from probes / future runs that exhibit the cap-exhausted-reasoning shape. That is the intended, narrow surface for the diagnostic — and it operates entirely on `failures.jsonl`, not on `informants.jsonl`. Asymmetric `informants.jsonl` is irrelevant.

The cross-record comparability concern is therefore real but benign. No methodology concern.

### C. The 1.7 residual failures and the ≥85% threshold

Stage 1.7 saw 1 truncation residual on glm-5.1 and 1 coverage failure on llama-maverick (2 of 20 cells = 10%). The plan accepts ≥85% recovery (≥17 of 20) as success. **I am comfortable with this.**

Reasoning:
1. Pushing for closer to 100% via a pre-merge cap-bump probe to 32768 inflates this task's scope and turns it into "instrument tuning round 2," which is appropriate as a follow-on diagnostic but inappropriate inside an already-validated recovery campaign.
2. The 1–3 residual failures are themselves diagnostic findings. Logging them with verbatim final responses in `failures.jsonl` (with `recovery_failed=true` and `campaign_id=phase4a-recovery-2026-05-05`) preserves their finding-status without forcing them through a different remedy path. See R2.
3. The 4 recovery-failed-then-deeper-investigation guardrail in §4.2 ("If 4+ cells fail (target hit rate < 80%), the recovery report flags the under-performance and the Architect schedules a follow-on diagnostic") is the right escalation primitive.

If during execution the script produces a recovery rate of, e.g., 12 of 20 (60%), the recovery report must flag this as a methodology-relevant deviation and the Architect must route to me for re-review *before* T4-redo proceeds. See R6.

### D. Forbidden vocabulary skim — clear

I checked the plan for §1.5.4 / CLAUDE.md §7 violations:
- No `worldview` / `believes` / `thinks` applied to models.
- No "publishable" framing.
- No "closer to human is better."
- No "within-model consensus" / "within-model CCM."

The recovery report (R2 deliverable) has not yet been written. R3 below specifies the framing it must use.

---

## Binding notes

The following must be applied before the corresponding deliverable is committed. None block Coder from starting R1.

**R1. Replace "supersede" with "replace as authoritative for the cell" in the recovery report.**

The §1 disposition table says "the historical failure rows are de-facto superseded but never edited." The recovery report (R2 deliverable) must NOT use "supersede" — it carries an unwarranted normative claim that the recovered records are *better*. They are different artifacts produced under a different (and corrected) instrument configuration. Use phrasing like:

> "The 20 historical failure rows in `failures.jsonl` remain unchanged. The 20 recovered records in `informants.jsonl` are the canonical artifacts for the (model, domain, run_index) cells they cover, collected under the corrected `max_tokens=16384` instrument configuration. Both are real measurements: the failure rows reflect the original instrument configuration (`max_tokens=4096`) at 2026-04-22; the recovered rows reflect the post-Task-16 corrected instrument configuration at 2026-05-05. Downstream analysis uses the recovered rows for the cells they cover."

This binding applies to the recovery report at `docs/status/2026-05-05-phase4a-recovery-report.md`. R1's script docstring is unaffected.

**R2. Verbatim final response capture on `recovery_failed=true` rows.**

For any cell that exhausts its 2-attempt retry budget, the new `failures.jsonl` row must capture the verbatim final response from attempt 2 (via the existing `prompt_verbatim` / `response_verbatim` / `thinking_verbatim` / `stop_reason` fields per `DATA_DICTIONARY.md` §9), NOT just the exception. The plan's §2 R1 behavior 3 ("the exception verbatim") is necessary but not sufficient. Stage 1.7's 2 residuals were diagnostically valuable precisely because the verbatim final response was retained — same standard applies here.

This is consistent with the post-v0.1.6 failures-as-findings directive (`DATA_DICTIONARY.md` §9, the `prompt_verbatim` / `response_verbatim` / `partial_session` / `retry_attempts` shape). The Coder should verify that `append_failure` is invoked with the post-v0.1.6 kwargs, not the legacy 2-arg form.

**R3. The recovery report copy must use this disciplined framing for the recovered records.**

When the recovery report (R2 deliverable) is written, it must:

a. Frame the recovery as a *measurement under corrected instrument configuration*, not a fix or a correction of the model's output.

b. Use phrasing like "cap-exhausted reasoning, recovered under the Task-16 cap fix" — methodologically clean and aligned with Task 16 SME notes S1/S3.

c. NOT use any of: `worldview`, `believes`, `thinks` (applied to models), `cultural bias` (standalone), `publishable`, `closer to human`, `the model finally responded properly`, `the model's true categorization`, or any phrase implying the model "had" a categorization that was previously hidden by the cap.

d. NOT make any model-comparative, consensus, or MDS claims. The recovery report is an instrument-event log: per-cell outcome, aggregate counts, cost reconciliation, pointer to verdict files. That's it.

The Reviewer must spot-check the recovery report against this list before merging.

**R4. The idempotence check must use substring matching on `qa_notes`, not regex with anchors.**

The campaign-id mechanism the plan inherits from `SHAKEDOWN_PROTOCOL.md` §2 layer 4 is a substring-in-`qa_notes` convention, not a structured field. The R1 script's idempotence check must perform:

```python
campaign_marker = "campaign_id=phase4a-recovery-2026-05-05"
already_recovered = any(
    record.qa_notes and campaign_marker in record.qa_notes
    for record in matching_records
)
```

NOT a regex with anchors that would falsely fail if `qa_notes` contains the campaign-id concatenated with other notes (a defensible future extension of the qa_notes contract).

**R5. The recovery report must explicitly state the build_db.py rerun is deferred to a separate ops task.**

Per Q6 ruling. The recovery report's "what's next" section must say: "lsb.sqlite rebuild is scheduled as a separate ops task (`scripts/build_db.py data/raw/informants.jsonl data/open_bundle/lsb.sqlite`); the bundle has no public DOI yet (Phase 4 G1/G2/G3 not yet evaluated), so the rebuild is internal-only and timing is at Architect discretion." This keeps the recovery commit self-contained per CLAUDE.md §8.

**R6. If recovery rate falls below 80%, route back to CDA SME before T4-redo proceeds.**

Per §4.2 of the plan and §C above: if 4+ cells fail (recovery rate < 80%), the recovery report must flag this as a methodology-relevant deviation and the Architect must route to me for re-review *before* the T4-redo task is scoped. The 80% threshold is the operational threshold; <80% is a finding that the cap-exhaustion reframe may not generalize as cleanly as Stages 1.5/1.5b/1.6/1.7 suggested at probe scale, and that finding must inform T4-redo scoping (in particular, the disposition language for what remains stuck at 16384).

This binding does NOT block the recovery commit itself — it gates the *next* gate, which is T4-redo's Architect plan.

---

## Carry-forward note

S5 (from Task 16 SME verdict, 2026-05-04) remains binding for the future T4-redo task. This recovery verdict does NOT trigger S5 (per Q5 ruling above) and does NOT consume it. R1–R6 in this verdict are local to the recovery operation and do not extend into T4-redo's scope; they will not be re-cited there.

Phase 4a.1 binding-note count remains at 31 (B-series notes from Phase 4a.1 verdicts and amendments). Task 16's S-series remains at S1–S5. This recovery verdict introduces an R-series (R1–R6) local to the Phase 4a recovery operation. Total binding-note inventories now: B1–B15 (Phase 4a.1, 31 notes counting amendments), S1–S5 (Task 16), R1–R6 (Phase 4a recovery).

---

## What I am explicitly NOT ruling on

- The 9 out-of-scope failures (phi-4 6, gpt-5.4-mini 2, mistral-small 1). Per the plan, these are deferred to separate Architect tasks. Their root causes are different from cap exhaustion (phi-4: 400-error adapter issue; gpt-5.4-mini: parser; mistral-small: coverage) and a different remedy path is appropriate.
- Whether to bump `max_tokens` beyond 16384 for any residual recovery failures. Out of scope per the plan; if needed, files as a follow-on Architect task.
- T4-redo scope, methodology-page text under the cap-exhaustion reframe, or any re-classification of the 9 originally-Gemini `safety_event_attribution` rows. Gated by S5; not part of this verdict.
- The build_db.py rerun timing or scheduling. Ops task per Q6.
- Whether `DeclineInterview` should also gain `thoughts_token_count`. Deferred per Task 16 SME Q5.

---

## Sign-off

The Coder is authorized to start Task R1 immediately on this PASS-WITH-NOTES verdict. The R1 script's behavior contract (target list, retry budget, idempotence, campaign-id wiring, dry-run-first) is approved as specified. R4 must be applied to the idempotence check. R2 must be applied to the `recovery_failed=true` row shape.

R2 (Task R2 — live execution and recovery report) is gated on Mark's cost sign-off per the plan's §5. The recovery report (deliverable from R2) must apply R1, R3, R5, R6 as specified.

Reviewer + Tester gates apply per-commit per the standard pipeline. No UI/UX gate (no frontend impact). No additional SME re-review required for the R1 commit unless the Reviewer surfaces a deviation from the behavior contract; the recovery report is a docs commit and is not re-routed through me unless §C / R6 triggers (recovery rate < 80%).

*End of verdict.*
