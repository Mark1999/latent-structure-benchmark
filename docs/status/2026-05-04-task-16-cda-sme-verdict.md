# Task #16 — Adaptive max_tokens Across All Adapters: CDA SME Verdict

**Date:** 2026-05-04
**Reviewer:** CDA SME agent (Opus)
**Task ID:** #16 (Adaptive max_tokens across all adapters)
**Plan reviewed:** `/opt/lsb-agent/docs/status/2026-05-04-task-16-architect-plan.md`
**Slack channel:** `#lsb-cda-sme`
**Posted:** 2026-05-04

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS-WITH-NOTES |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

The Coder is authorized to start Task 16.A and Task 16.B in the order specified in the plan, conditional on the binding notes (S1–S5 below) being applied to Task 16.B's data-dictionary copy and the disposition table's reframing language. The notes are scoped — none of them alter the schema additions, the cap values, or the sequencing the Architect proposed. They tighten the methodological framing of the diagnostic invariant and the Note K cross-reference language so the dictionary, comments, and any future text about Phase 4a's failure attribution remain coherent with §1.5 and the Phase 4a.1 disposition record.

---

## Executive summary

The plan is well-grounded in three independent Stage 1.5/1.5b/1.6 probes and proposes an additive, backward-compatible schema change with a clean diagnostic invariant. The Architect did the right thing in surfacing six explicit questions plus the cross-cutting reframing implication (Phase 4a failures as max_tokens artifact rather than refusal). My rulings on Q1–Q6 are confirmations with one tightening on the diagnostic invariant; the more important observations are on the framing claims (Axis 3) and on what the reframe does and does not imply for Note K (which I do not re-litigate here, but flag for the upcoming T4-redo task).

---

## Axis-by-axis findings

### Axis 1 — Protocol validity: PASS

- The proposed change is purely an adapter parameter change. It does not touch the CDA three-step protocol (free list → pile sort → pile interview), the truncation-k (25), the run-count (N=5), the reflexive card-deck design, or temperature conventions (T=0.7 for free list, T=0.3 for pile sort per ARCHITECTURE.md §4.1.3).
- Stage 1.6's empirical demonstration (10/10 valid informants on family + holidays at the bumped caps) is the right kind of evidence for protocol robustness — it ran the full three-step cycle, not a single-step probe in isolation.
- The plan explicitly preserves the v1 prompt template (Q3). The protocol is unchanged.

### Axis 2 — Analytical validity: PASS

- `thoughts_token_count` is metadata, not analysis input. It does not enter any consensus, OCI, MDS, or Procrustes calculation. Adding it cannot perturb Register 1 or Register 2 statistics.
- The plan's note in §7 (Architect's read of `BOOTSTRAP_DESIGN.md`) is correct: the field has no Level 1 / Level 2 bootstrap implications.
- The proposed diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` is well-formed for Gemini and OpenRouter responses where the provider surfaces reasoning tokens. See S2 below for the boundary case where the invariant *cannot* fire (Anthropic / HuggingFace / non-reasoning OpenRouter models) and how the dictionary should describe that.
- The default `int = 0` (rather than `int | None`) is the right call: it preserves arithmetic ergonomics and keeps the diagnostic invariant from false-positiving on non-reasoning providers (since `0 > 0` is False, the invariant collapses safely).

### Axis 3 — Claims validity: PASS-WITH-NOTES

- The headline reframe — **"the 29 Phase 4a failures are predominantly a `max_output_tokens=4096` configuration artifact, not corpus-lens or refusal events"** — is methodologically defensible *and* important. Without the reframe, the disposition table inherits the original collection's mistaken implicit claim that the model itself produced an `output_tokens=0` response (a refusal-shaped event). With the reframe, the failure becomes an instrument event: the cap was reached during reasoning and the model never got to surface output. That is a property of the LSB measurement instrument, not of the model.
- The reframe is supported by Stage 1.5 (Gemini cap-bump on the same prompt that produced empty output at 4096 succeeds at 16384), Stage 1.5b (same pattern reproduced for glm-5.1, llama-4-maverick), and Stage 1.6 (end-to-end full cycle, 10/10 success). Three independent probes is the right standard of evidence to overturn the prior implicit attribution.
- **However:** the framing must not over-claim. The plan's word "predominantly" is correctly hedged; the corpus-recovery follow-on task may show that some of the 29 failures persist after the cap bump. The plan correctly documents this for gpt-5.4-mini ×3 and mistral-small ×1, and correctly defers them to a separate investigation. The dictionary text must inherit the same hedge — "diagnostic signature of cap-exhausted reasoning failures" is correct phrasing; "diagnostic signature of refusal" or "diagnostic signature of the model declining" would be the wrong reframe in the other direction. See S1.
- The reframe has implications for Phase 4a.1 Note K (the safety-event row classification underlying Mark's hand-coding of the 9 originally-Gemini safety_event_attribution rows). Stage 1.6's success at the bumped caps re-raises the question of whether those 9 rows should still be classified as safety events under the original detector, or whether the cap-exhaustion reframe shifts the attribution. **I do not re-litigate Note K in this verdict** — that is the upcoming T4-redo task. But see "Note K implications" below for what the new framing will require when that task arrives.

### Axis 4 — Audience translation: PASS-WITH-NOTES

- No forbidden vocabulary in the plan or the proposed dictionary entries.
- The plan correctly avoids the model-anthropomorphizing language that would have crept in had the reframe been written carelessly ("the model couldn't think enough"). The actual proposed phrasing — "model spent everything on thinking, nothing on output" in the AdapterResult rationale — is on the borderline of `believes`/`thinks` framing; replace with "reasoning tokens consumed the cap" or "cap exhausted by reasoning before any visible output emitted." See S3.
- The dictionary entry as drafted is legible to a researcher reading the open data bundle. The cross-provider-comparability caveat (R6 in §4 of the plan) is correctly noted; the dictionary must say "as reported by the provider" without claiming numerical comparability across providers. See S4.
- The data-dictionary changelog entry must cite this verdict path and the three probe commits, per CLAUDE.md §6 R7. The plan's draft of the changelog does this; confirming.

---

## Q1–Q6 explicit rulings

### Q1 — Single global cap vs. per-step adaptive caps

**Architect recommendation:** single global cap.
**SME ruling:** **CONFIRM.**

Stage 1.6 ran all three CDA steps at `max_output_tokens=16384, thinking_budget=1024` and produced 10/10 valid informants. That is direct empirical evidence that one cap suffices end-to-end. Per-step adaptive sizing is a real improvement *if* a future probe shows it is needed, but standing it up now would (a) introduce per-step branching logic that complicates the adapter contract for no measured benefit, (b) increase the surface area the Reviewer has to audit, and (c) couple the adapter parameter choice to the prompt template version (since per-step sizing implies prompt-template awareness in the adapter, which violates the §4.1.2 separation of concerns). Single global cap is correct for v1.

If Phase 4b introduces a domain that empirically requires per-step variation (the phi-4 forward path is one such candidate, addressed separately), the right move is a new task, not a retrofit of this one.

### Q2 — Default value for `thoughts_token_count` on providers that don't expose it

**Architect recommendation:** `0` (matching the existing `output_tokens: int` convention).
**SME ruling:** **CONFIRM, with sharper field semantics — see S2.**

`int = 0` is the right pydantic default because:
1. It matches the existing `input_tokens: int` and `output_tokens: int` convention — the schema does not use `int | None` for token counts.
2. It avoids `int | None` arithmetic gymnastics on every consumer side.
3. It preserves the diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` cleanly: providers that do not surface reasoning tokens cannot trigger the invariant by accident (`0 > 0` is False).

But the *semantic ambiguity* of `0` requires careful field-doc wording. `0` could mean either (a) the model produced no reasoning tokens (e.g., a non-reasoning model on Anthropic/HuggingFace), or (b) the provider does not expose the field. These are different epistemic states. The dictionary text the plan proposes — "for providers that do not surface reasoning tokens (Anthropic, HuggingFace at this commit), the value is `0`" — is *almost* correct but conflates the two. See S2 for the wording fix.

### Q3 — Prompt-template version bump per CLAUDE.md §6 R8

**Architect recommendation:** No, prompt templates unchanged; R8 applies to prompt content only.
**SME ruling:** **CONFIRM.**

R8 reads: "Prompt templates are versioned. Never edit a published prompt template in place; copy it to a new version directory under `packages/cdb_collect/prompts/v{N}/`." The rule scope is the *content* of the prompt template (the words sent to the model). `max_tokens` and `temperature` are adapter parameters; they are recorded on `InformantRecord` (§3.2 collection conditions) and the SHA256 manifest's `request_params` already covers them — so any change to them is forensically traceable without a template version bump. Bumping `prompts/v{N}/` for a `max_tokens` change would conflate two distinct version surfaces (template content vs. request parameters) and would create the wrong incentive (researchers reading `prompt_version="v1"` records would assume the v1 protocol invariant; in fact the protocol is invariant — the cap change is orthogonal).

The forensic record of *which cap was active when this record was collected* is the `max_tokens` field on `InformantRecord` (already present, top-level §1.1 in the dictionary). That is sufficient. No version bump.

### Q4 — Backward compatibility for old Phase 4a records lacking `thoughts_token_count`

**Architect recommendation:** pydantic `int = 0` default, no migration.
**SME ruling:** **CONFIRM.**

Pydantic v2 with the field declared as `int = 0` accepts JSONL lines that lack the field — it materialises as `0` on read. This matches the v0.1.10 `cost_usd` removal precedent in reverse: there, an old field was silently dropped on read; here, a missing new field is silently filled with the default. Both rely on the same pydantic configuration posture and both preserve the open-data reproducibility guarantee (`build_db.py` rebuilds correctly from the JSONL regardless of which schema version wrote each line).

The acceptance criterion 16.B.6 (round-trip test on an old fixture line) is the right test for this. Confirm.

**One small point for the Coder (not a binding note):** when populating `thoughts_token_count=0` on legacy Phase 4a records via re-read, downstream analysis must NOT treat `0` as evidence that no reasoning occurred. It is evidence that the field was not captured at collection time. The dictionary must state this clearly — see S2.

### Q5 — Should `DeclineInterview` schema also gain `thoughts_token_count`?

**Architect recommendation:** Out of scope for this task.
**SME ruling:** **CONFIRM out-of-scope, with directional preference noted for the future.**

The Architect's reasoning is correct: `DeclineInterview` is the follow-up call's record; the per-record context is different from the primary three-step session, and its analytical role (Phase 4a.1 disposition reasoning) does not currently turn on cap-exhaustion diagnostics. Adding the field there is a small additional task that can be filed separately.

**Directional preference:** symmetry across the schema is generally a good thing, and once Task 16 lands, a small follow-on PR adding `thoughts_token_count: int = 0` to `DeclineInterview` would close the small inconsistency. But it is not blocking Task 16, and it is not blocking Note K's T4-redo. File it as a backlog item.

### Q6 — Is `thinking_budget=1024` (down from 8192) a valid Gemini default?

**Architect recommendation:** Yes per Stage 1.6 empirical evidence.
**SME ruling:** **CONFIRM, with a watch-flag for Phase 4b.**

The 8192 figure was not based on probe data (the Architect notes this explicitly). Stage 1.6's 10/10 success at 1024 is direct empirical evidence that 1024 is sufficient for the most reasoning-intensive of the three steps (pile-sort) on the two domains tested (family, holidays).

**Watch-flag.** Phase 4b adds a third domain (food, currently planned). If the food domain has more contested categorical structure than family or holidays — i.e., if pile-sort on food requires more reasoning than family/holidays did — `thinking_budget=1024` could become limiting. The right way to handle this is *not* to bump the budget pre-emptively; it is to run a Stage 1.6-equivalent probe on the third domain before Phase 4b collection begins, and adjust if the probe shows it's needed. Surfacing this as a Phase 4b prep task, not a current blocker.

R5 in the plan correctly anticipates this. Confirming the disposition.

---

## Proactive checks

### A. Disposition table reframing — accurate and well-hedged

The plan's disposition table reframes the 29 Phase 4a failures as "predominantly a max_output_tokens=4096 configuration artifact, not corpus-lens or refusal events." This is correct given the Stage 1.5/1.5b/1.6 evidence. The hedge "predominantly" is doing important work — it preserves the 4 known unrecoverable cases (gpt-5.4-mini ×3, mistral-small ×1) as a separate, undetermined-cause population.

**One sharpening (S1).** The sentence "the failures are predominantly a max_output_tokens=4096 configuration artifact" is true at the population level. At the individual-record level, it is unknown whether any *given* one of the 25 fixable failures was definitely a cap-exhaustion event vs. some other cause that the cap bump happens to also resolve. The corpus-recovery follow-on task will produce per-record evidence (the rerun either succeeds or it doesn't), but until it runs, the population-level claim is the strongest claim defensible. The dictionary entry and any comments in the adapter must use phrasing that supports the population-level claim without implying per-record certainty. See S1.

### B. Prior Note K rulings — implications for the T4-redo task

I previously issued binding rulings on Note K (the Phase 4a.1 safety-event attribution analysis) under the implicit assumption that the 9 hand-coded safety_event_attribution rows reflected genuine model-side safety filtering — i.e., that the model produced safety-shaped output text, which Mark then hand-coded as evidence of safety-event behavior. Stage 1.5/1.6 reframes the underlying empty-output failures as cap-exhaustion artifacts, which raises a question about whether the rows that Mark *did* hand-code as safety_event_attribution were classified on the basis of substantive response text (not the empty-output failures themselves) and therefore remain valid under the new framing.

**My read of the record:** the 9 hand-coded safety_event_attribution rows in Phase 4a.1 came from `decline_interviews.jsonl`, not directly from `failures.jsonl`. They are the *follow-up* responses where the model was asked "why did you decline" after a primary-step failure, and Mark hand-coded the follow-up text as describing safety behavior. So the substantive classification was on the follow-up, not on the empty primary-step output. **The cap-exhaustion reframe affects what we say about the *originating* primary-step failures, not what we say about the substantive content of the follow-up interviews.** That means the 9 hand-coded safety_event_attribution rows themselves are not directly invalidated by the reframe.

**However:** the *attribution chain* is affected. Under the original framing, the chain read: "model produced empty output → model declined for safety reasons → follow-up confirms safety framing → 9 hand-coded rows." Under the new framing, the chain reads: "model exhausted cap on reasoning → no visible output emitted → follow-up was asked to interpret an outcome whose true cause was a measurement-instrument event → 9 hand-coded rows now describe the model's *post-hoc* explanation of an instrument event, not its actual reasoning at the original session." That is a meaningfully different epistemic claim about what the 9 rows *mean*.

**Disposition for Task 16.** I do **not** issue a parallel retroactive clarification here, because Task 16 does not re-litigate Note K. The plan correctly defers that to the upcoming T4-redo task.

**Disposition for the upcoming T4-redo task.** When the T4-redo task arrives, it must address:
1. Whether the 9 hand-coded safety_event_attribution rows should be re-classified as safety_event_attribution_under_cap_exhaustion (i.e., the model retrospectively rationalized an instrument event as safety).
2. Whether the cross-provider-replication threshold from D20 (already falsified by single-provider data) interacts with the cap-exhaustion reframe — possibly the single-provider concentration is itself an instrument artifact (Gemini's reasoning tokens billed against the cap interacting with the original 4096 setting more aggressively than other providers' models did at the same cap).
3. Whether any of the 31 binding notes from Phase 4a.1 need to be re-stated under the new framing.

I will issue a parallel retroactive clarification (analogous to the R7 clarifications appended to the original SME verdict + Amendment 1 verdict for the detector miscalibration) **when the T4-redo task is scoped and brought to me for review**, not pre-emptively. Pre-emptive re-rulings would risk getting ahead of empirical evidence the corpus-recovery task will produce.

**This deferral is itself a binding note (S5).** The T4-redo task must explicitly route through me on the Note K re-classification question before any methodology-page text or dashboard copy is written under the new framing.

### C. Diagnostic invariant — sharpening the field semantics

The plan's proposed dictionary text says: "Detecting `output_tokens == 0 AND thoughts_token_count > 0` is the diagnostic signature of cap-exhausted reasoning failures."

This is correct *as a sufficient condition for one population* (Gemini and reasoning-capable OpenRouter models), but it is **not** the only diagnostic shape:

1. **Cap-exhausted reasoning where reasoning was not surfaced.** If a provider does not expose `thoughts_token_count` (Anthropic, HuggingFace, non-reasoning OpenRouter models, or future reasoning models that disable reasoning surfacing), `thoughts_token_count == 0` is reported but the actual underlying behavior could still be cap exhaustion. The diagnostic invariant `output_tokens == 0 AND thoughts_token_count > 0` cannot fire, but the underlying event may have happened. The diagnostic test is therefore *one-sided*: when it fires, you have high-confidence cap-exhausted reasoning; when it does not fire, you have either (a) no reasoning happened, (b) reasoning happened but the provider did not surface it, or (c) the failure was something else entirely (e.g., refusal, network error, parse error).

2. **Non-zero output but cap exhaustion.** A model could produce *some* visible output and *also* hit the cap on reasoning. `output_tokens > 0` does not rule out cap exhaustion partway through.

3. **Zero output and zero thoughts via a different path.** A network failure, an empty-string response (e.g., a refusal that returns "" rather than a refusal sentence), or a provider-side filter that strips content can all produce `output_tokens == 0 AND thoughts_token_count == 0`. The invariant correctly does not fire on these — they are *not* cap-exhausted-reasoning events.

The dictionary text must therefore describe the invariant as **a sufficient diagnostic signature, not a complete one** — see S2 for the wording. A separate diagnostic for "cap-exhausted reasoning where the provider did not surface thoughts" would require pairing `output_tokens == 0 AND stop_reason == 'MAX_TOKENS'` (or equivalent finish-reason check), which is out of scope for Task 16 but worth filing as a follow-on data-dictionary clarification once the corpus-recovery task produces evidence.

---

## Binding notes

The following must be applied before Task 16.B is committed. None of them block Task 16.A. They tighten the data-dictionary and adapter-comment language so the open-data bundle and any future text remain coherent with §1.5 and the Phase 4a.1 disposition record.

**S1. Hedge the cap-attribution language at the population level, not the per-record level.**

The data-dictionary entry for `thoughts_token_count` (proposed in §1.2/§1.3/§1.4) currently reads: "Detecting `output_tokens == 0 AND thoughts_token_count > 0` is the diagnostic signature of cap-exhausted reasoning failures (see task #16)." Replace with: "When `output_tokens == 0 AND thoughts_token_count > 0`, the model consumed reasoning tokens against the `max_tokens` budget without producing visible output — a sufficient diagnostic signature of cap-exhausted reasoning. The converse does not hold: `thoughts_token_count == 0` does not rule out cap exhaustion when the provider does not surface reasoning tokens (see field semantics below)."

**S2. Distinguish "no reasoning happened" from "provider does not surface reasoning" in the field semantics.**

The proposed text "for providers that do not surface reasoning tokens (Anthropic, HuggingFace at this commit), the value is `0`" conflates two epistemic states. Replace with: "The value `0` is reported in two distinct cases that are not separable from this field alone: (a) the model produced no reasoning tokens (e.g., a non-reasoning model or a reasoning model that bypassed reasoning for this call), or (b) the provider does not surface reasoning-token usage in its API response (Anthropic, HuggingFace, and non-reasoning OpenRouter models at this commit). Downstream analysis treating `thoughts_token_count == 0` as evidence of non-reasoning must additionally verify that the provider exposes the field for the model in question; see the per-provider notes in `cdb_collect/adapters/` for current coverage."

**S3. Replace the adapter-comment phrase "model spent everything on thinking, nothing on output."**

In the AdapterResult rationale comment in `adapters/base.py` (and any equivalent text in adapter code), the proposed phrase "captures provider-side reasoning-token usage so QA and downstream analysis can detect 'model spent everything on thinking, nothing on output'" sits on the borderline of §1.5.4 forbidden vocabulary (`thinks` applied to models). Replace with: "captures provider-side reasoning-token usage so QA and downstream analysis can detect cap-exhausted reasoning (reasoning tokens consumed the entire `max_tokens` budget before any visible output was emitted)."

**S4. Make the cross-provider non-comparability explicit in the dictionary.**

Per R6 in the plan's risk section, `thoughts_token_count` is provider-reported and is not numerically comparable across providers. The dictionary entry must include a one-line caveat: "Values are as reported by the provider and are not numerically comparable across providers — provider definitions of 'reasoning tokens' may differ in what they include (cached prefixes, internal scratchpad, hidden chain-of-thought, etc.). Within-provider comparisons are valid; cross-provider comparisons require provider-internal context."

**S5. The Note K re-classification question must route through CDA SME review before any methodology-page text is written under the new framing.**

The cap-exhaustion reframe changes the epistemic status of the 9 hand-coded safety_event_attribution rows from Phase 4a.1 — the substantive follow-up classifications remain valid, but the *attribution chain* (originating event → safety-shaped follow-up → safety_event_attribution row) must be re-stated under the new framing. The T4-redo task must be scoped to address points 1–3 in §B above, and must route to me before any methodology-page text or dashboard copy is generated under the new framing. This note does **not** block Task 16; it gates the future T4-redo task.

---

## What I am explicitly NOT ruling on

- The corpus-recovery follow-on task (re-collecting the 19 fixable Phase 4a failures against the new caps). The plan correctly scopes this as a separate task with its own gate chain.
- The gpt-5.4-mini ×3 and mistral-small ×1 unexplained failures. Out of scope per the plan.
- The phi-4 forward path. Out of scope per the plan.
- Note K re-classification specifics. Deferred to the T4-redo task per S5.
- Whether `DeclineInterview` should also gain `thoughts_token_count` (Q5). Confirmed out-of-scope; directionally preferred as a follow-on.

---

## Carry-forward note

Phase 4a.1 binding-note count remains at 31 (from prior verdicts). This Task 16 verdict introduces a fresh S-numbered note series (S1–S5) because Task 16 is methodologically distinct from Phase 4a.1 (adapter parameter change vs. disposition analysis). The S-series is local to Task 16 scope; if the future T4-redo task surfaces a need for Phase 4a.1-amendment notes, those will continue the B-series numbering.

---

## Sign-off

The Coder is authorized to start Task 16.A immediately on this PASS-WITH-NOTES verdict. Task 16.B's data-dictionary copy must apply S1–S4 verbatim (or equivalent wording approved by the Architect on a re-routed plan amendment). S5 is a forward-looking gate on the T4-redo task and does not block the Task 16 commit chain.

Reviewer + Tester gates apply per-commit per the standard pipeline. No UI/UX gate (no frontend impact). No additional Mark sign-off required (per the plan's §5).

*End of verdict.*
