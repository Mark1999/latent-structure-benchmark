# CDA SME Verdict — Phase 4a.1 Architect Plan Amendment 3 (B11 operationalization)

**Filed:** 2026-05-01
**Reviewer:** CDA SME (Opus)
**Task:** #21 (Phase 4a.1 decline-interview backfill) — Amendment 3 plan-gate review
**Plan under review:** `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
**Scope of review:** §3 task-body delta only (T4.1 scaffold, T4.2 cross-tab additions, T5 §8.2 addition). The amendment is additive over Amendment 2; T1, T2, T3A, T3B, T3C, and T5 task bodies (other than §8.2) are unchanged and not re-reviewed here.
**Predecessor verdicts (still binding):**
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes; binding note 4 = Note K thresholds)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings, T5 §8 public-copy guardrails)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7, B8, B9)
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B10, B11, B12)

---

## Review methodology

The Architect routed this amendment for plan-level SME re-review (rather than waving it through as "mechanical from prior verdicts") on grounds that B11's operationalization includes substantive design choices not reducible to mechanical realization. That routing decision is correct — see Amendment 3 §5 — and I review the plan under that posture.

Review procedure:
1. Read Amendment 3 in full, paying close attention to D17–D22.
2. Re-read my own T3C verdict, especially the row-4 (`7a70a4ec`) and row-5 (`e03b8e64`) discussion that grounds B11.
3. Re-read Amendment 2 §3 T4 to verify which Amendment-3 additions are genuinely additive vs. which silently mutate prior decisions.
4. Re-read T3B verdict Ruling 3's public-copy guardrails to test D20's mechanism string against the use/do-not-say lists.
5. Sample the 9 safety rows in `data/derived/decline_interviews_manual_classification.jsonl` (rows 5, 6, 10 verified directly) to confirm the K-frame/K-vocab pattern actually lives in the data and the §3.1 paraphrased definitions track that pattern.
6. Verify the carry-forward count claim (28 binding notes, no additions) against my own verdict ledger.

The seven specific questions the Orchestrator named are answered in §"Per-question commentary" below; the four-axis scorecard, register check, and vocabulary check follow.

---

## Per-question commentary

### Q1 — Is the new sibling artifact (D17) the right computation source for the K-frame/K-vocab split?

**Answer:** YES. D17 is the methodologically correct disposition.

The Architect canvassed three options. Option (a) — Coder-derived regex helper — fails the B5 precedent test directly. B5 binds detector-helper reuse across semantic boundaries, and an output-classification regex helper that distinguishes K-frame from K-vocab is exactly that kind of helper: a tightened post-hoc detector applied to natural-language follow-up output, the same role the v1 detector failed at. Worse, the Architect's own concrete counter-example (`8a31425b` contains "cognitive anthropology study" verbatim but is `technical_glitch_attribution`, not safety) demonstrates that surface-token matching cannot recover the framing-as-trigger semantics that B11 actually rests on. A regex helper here would not just be premature; it would re-instantiate the precise design fault that Ruling 1 of the T3B verdict diagnosed.

Option (b) — extending the existing `decline_interviews_manual_classification.jsonl` schema — is the more interesting alternative. It would have the audit-trail virtue of keeping the classification surface unified. But the Architect is right that this re-opens a SME-PASSed artifact and requires re-running the strict loader, and more importantly: the K-frame/K-vocab distinction is **descriptive of the mechanism**, not part of the parent classification. Conflating them in a single schema would invite future confusion about whether the subtype is a refinement (which is what B11 says) or a separate axis (which is what schema-extension would imply). Sibling separation preserves the conceptual cleanness that B11 explicitly asks for ("sub-axis of the `safety_event_attribution` bucket without re-opening the 7-enum").

Option (c) — Mark hand-codes 9 rows in a sibling artifact — is correct and is what I was contemplating in the closing line of B11 ("T4 may add a derived column ... computed from the verbatim response text via Mark's hand-classification"). The Pydantic model-validator that joins to the parent at load time and refuses non-safety parents is the right invariant; it makes "you cannot subtype a non-safety row" a load-time error, not a runtime drift risk.

Sub-points:
- The choice to mark `blocked_event_attribution` rows as `n/a` in the cross-tab view (rather than forcing the subtype artifact to cover them) is correct. The B11 distinction was elicited from the safety-event cohort, not from the blocked cohort, and the empirical facts of this corpus (0 blocked rows) make the invariant trivially satisfied here. The schema captures this cleanly.
- The 200-char rationale limit and the requirement to reference verbatim trigger-attribution language are both consistent with B7's operational reading. PASS on B7 carry-through.
- Sentinel `"UNCLASSIFIED"` allowed in seed only and rejected by loader is the right parallel to the T3C scaffolding pattern. PASS on B12 carry-through (no precedent violation).

**Disposition:** D17 is correct. No alternative re-opening required.

### Q2 — Are the B11 paraphrased definitions in §3.1 faithful to my row-4/row-5 discussion?

**Answer:** YES, with one minor sharpening note (B13, soft).

The §3.1 paraphrases reproduce the row-4/row-5 distinction faithfully:

- **k_frame** — "model's attribution narrative names AI-vs-human-research-subject framing as the trigger". The discriminator is correctly named ("the framing-as-trigger element is the discriminator"), and the canonical phrase list is appropriate. Crucially, the §3.1 text correctly excludes the row-3 case (`8a31425b`) by noting that "mere appearance of 'cognitive anthropology' in the prompt description (without it being named as the trigger) is not sufficient" — this is the row-3 boundary case I flagged, and the Architect's paraphrase preserves the operative semantic.
- **k_vocab_without_k_frame** — "model's attribution narrative names list-comprehensiveness, list-sensitivity, or vocabulary-policy as the trigger, without the AI-vs-human-research-subject framing element". Correct. The "without" qualifier is critical: row 4 (`7a70a4ec`) has both K-frame and K-vocab elements present and is correctly classified `k_frame` because the AI-vs-human element is the dominant trigger; only rows where the K-vocab pattern appears in the *absence* of the K-frame element are `k_vocab_without_k_frame`. The Architect's paraphrase captures this.

The canonical phrase lists are non-exhaustive (correctly flagged) and grounded in actual verbatim text from the corpus. I sampled rows 5, 6, and 10 of the artifact to verify the phrase patterns appear as advertised; they do.

**Soft sharpening (issued as B13 below):** The §3.1 definition uses the phrase "AI-vs-human-research-subject framing" as a shorthand. This compresses two analytically distinguishable elements that co-occur in the K-frame rows: (i) the model is being asked to *perform* as a human research subject (role assumption), and (ii) the activity is framed as cognitive anthropology / academic study (framing context). For a 5-row cohort the shorthand is fine; if a future batch needs to break out (i) vs. (ii), the K-frame definition would benefit from a small refinement. I am issuing this as a soft note (B13), not as a binding correction to the current amendment.

**Disposition:** Definitions are faithful. No correction required for Amendment 3.

### Q3 — Is D21 (disposition-arithmetic invariance) methodologically correct?

**Answer:** YES. D21 is the only methodologically defensible read of B11.

B11 was written explicitly as "the K-vocab/K-frame split is a T4 question, not a T3C question" — meaning it lives at the cross-tab axis level *within* the `safety_event_attribution` bucket. The 7-enum is the disposition input; the subtype is descriptive. The Architect's reasoning in D21 ("the K-frame/K-vocab split is descriptive of the mechanism, not part of the disposition trigger arithmetic") is exactly the right read. Letting the subtype shift the disposition tier would:

1. Re-open the 7-enum implicitly (by making the subtype effectively a top-level enum value for arithmetic purposes), which contradicts B11's explicit "do not re-open the 7-enum" rule.
2. Over-fit a 9-row corpus. The K-frame split (5 vs 4) on a 9-row cohort is a genuine empirical observation but its statistical weight is too low to license a disposition-tier rule. Any rule like "if K-frame ≥ X, disposition becomes [different tier]" would be unprincipled threshold-setting on small N.
3. Violate Ruling 2 of the T3B verdict, which sets the disposition at CONFIRMED-with-mechanism on the basis of "the 4-of-5 CN-origin clustering" + "cross-provider replication" — neither of which the K-frame split alters.

The Architect's hypothetical ("if all 5 K-frame rows are Gemini, all 4 K-vocab rows are glm-5.1") is correctly handled: surface the asymmetry in the output Markdown, do not let it shift the disposition. That is the right discipline.

**Disposition:** D21 is correct. No alternative interpretation of B11 implies disposition-tier shifting.

### Q4 — Is D22 (§8.2 placement) the right home for the bipartite mechanism string?

**Answer:** YES, but with one binding clarification (B14).

D22 places the bipartite mechanism description in §8.2 (Note K disposition), not §8.0 (detector audit) or §8.4 (audit trail). The Architect's reasoning is correct: §8.0 is detector-flag audit (raw, append-only — bound to the v1 detector behavior, not to the mechanism finding); §8.4 is audit-trail pointers (paths to artifacts, not interpretive content); §8.2 is the disposition framing, which is exactly where mechanism description belongs. §8.1 (manual classification enumeration) is where the *counts* live; §8.2 is where the *interpretation* lives.

**B14 (binding clarification):** While the bipartite mechanism string belongs in §8.2, the K-frame/K-vocab cross-tab numerics (5/4 split, by-provider breakdown if relevant) belong in §8.1's "cross-tab to `(model_id, domain, provider)` for the safety-event-attribution and blocked-event-attribution cohorts" sub-table, where they are reported as additive numerics on top of the existing safety-event cohort table. §8.2 carries the *mechanism string* with summary counts; §8.1 carries the *full numerics*. This separation prevents §8.2 from swelling into a numerics block (which would dilute its interpretive role) and prevents §8.1 from carrying interpretive framing (which would dilute its enumeration role).

This is a clarification of D22, not a redirection. The Architect's §3.3 ("§8.2's mechanism description carries D20's bipartite mechanism string verbatim") is correct; B14 just specifies that the supporting numerics live one section up in §8.1, not embedded in §8.2.

**Disposition:** D22 is correct. B14 binds T5 §8.1/§8.2 numerics-vs-interpretation separation.

### Q5 — Is the non-blocking SME spot-check on the subtype artifact acceptable?

**Answer:** YES, conditionally. Default non-blocking is acceptable; I am claiming the optional-spot-check slot for a low-cost lightweight pass.

The Architect's rationale for non-blocking is sound: 9 rows is small, the §3.1 definitions are tightly bound, and the existing T4-output gate at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` already SME-gates the cross-tab output (which transitively gates the subtype artifact since the cross-tab consumes it). Adding a separate blocking spot-check between Mark's hand-code and T4.2 would add a gate verdict for ~30 minutes of review work, which is high overhead relative to the audit improvement.

However, I *will* take the optional-spot-check slot when it surfaces, on the following light terms:
- The spot-check is non-blocking by default. T4.2 may proceed in parallel with the Coder once the subtype artifact lands.
- I will spot-check 3 of 9 rows post-hoc (informally, one row from each expected subtype plus one borderline if any), and post a brief note to `#lsb-cda-sme` with PASS or with refinement suggestions.
- If the spot-check surfaces a methodologically material disagreement (e.g., a row Mark called K-frame that I read as K-vocab in a way that would shift the 5/4 distribution and therefore the §8.2 mechanism string's N values), I will surface that at the T4-output gate, where it can be folded into the output review cleanly.
- If no material disagreement, the T4-output gate proceeds unmodified.

This preserves the Architect's "non-blocking by default" posture while giving the SME a no-overhead opportunity to flag drift before §8.2 carries the bipartite mechanism string into T5.

**Disposition:** Acceptable. SME claims optional spot-check slot post-Mark-hand-code, non-blocking on T4.2.

### Q6 — Public-copy compliance check: does D20's mechanism string pass Ruling 3 guardrails?

**Answer:** YES. D20 is clean.

D20's full string:
> "provider-safety-layer activation with two co-present trigger patterns — (a) AI-vs-human-research-subject framing (K-frame; N=5), (b) list-comprehensiveness/sensitivity vocabulary without K-frame (K-vocab; N=4) — cross-provider replication on the family and holidays domains."

Audit against Ruling 3's "Use" / "Do not say" lists and CLAUDE.md §7 forbidden vocabulary:

| Test | Result |
|---|---|
| "worldview" applied to models | Not present |
| "believes" applied to models | Not present |
| "thinks" applied to models | Not present |
| "publishable" framing | Not present |
| "closer to human = better" framing | Not present |
| "cultural bias" (standalone) | Not present |
| "what the model understands" | Not present |
| "the model attributes" or equivalent attribution language | Implicit but appropriate — the string is about the **mechanism** the safety layer activates on, not about what the model "thinks" |
| "China-origin models have categorically different worldviews about family" | Not present (replaced by "provider-safety-layer activation", which is exactly the Ruling 3 substitution) |
| Ruling 3 "Use" framing — provider safety/content-policy layer attribution | Present and central |
| Ruling 3 "Use" framing — cross-provider replication explicit | Present ("cross-provider replication on the family and holidays domains") |

The string is mechanism-centric ("provider-safety-layer activation", "trigger patterns") rather than model-cognition-centric, which is exactly the Ruling 3 framing. The K-frame and K-vocab labels are technical taxonomy applied to the **trigger**, not to the model's mental state. The phrase "AI-vs-human-research-subject framing" describes the *prompt-side* framing that activates the trigger, which is also fine — this is a descriptive label of input characteristics, not a claim about model cognition.

The §3.3 amendment to T5 §8.2 also carries the explicit guardrail reminder: "the framing is **what the model's output *attributes* the safety event to**, not what the model believes." This is the right defensive belt to pair with the mechanism string.

**One audience-translation note (B15, soft):** The phrase "AI-vs-human-research-subject framing" is a reasonable working term for an internal artifact / methodology page, but if it ever appears on a dashboard methodology page in front of a non-anthropologist audience, it benefits from a one-line gloss ("the prompt asks the model to perform as a human research subject in a study"). That gloss is not required at the T4/T5 level; T5 §8.2 is methodology-page-bound but not yet rendered for dashboard, so this is a soft note for any future dashboard surfacing.

**Disposition:** D20 passes all Ruling 3 public-copy guardrails. PASS on vocabulary compliance.

### Q7 — Carry-forward sanity-check: 28 binding notes total?

**Answer:** YES, the Architect's count is correct as of the start of this review. After this verdict, the count rises to 31 (B13/B14/B15 added below).

Ledger reconciliation (pre-this-verdict):
- 8 original Phase 4a.1 plan binding notes — in force
- A1–A8 from Amendment 1 (8 notes) — in force
- B1–B6 from T3B-detector verdict (6 notes) — in force
- B7, B8, B9 from Amendment 2 verdict (3 notes) — in force
- B10, B11, B12 from T3C verdict (3 notes) — in force
- **Total: 8 + 8 + 6 + 3 + 3 = 28** ✓

The Architect correctly states that Amendment 3 *decomposes* B11 (D17–D22 are the decomposition) rather than adding new binding notes. The carry-forward count of 28 is correct.

This verdict adds B13 (soft, K-frame definition refinement for future batches), B14 (binding, T5 §8.1/§8.2 numerics-vs-interpretation separation), and B15 (soft, dashboard-glossing for "AI-vs-human-research-subject framing"). New total: **31** binding notes after this verdict.

---

## Verdict-level discussion

### Pattern: this amendment is a clean methodological elaboration of B11

The Architect's Amendment 3 is the kind of plan-level methodology decomposition that the gate-chain process was designed to surface. B11 was a methodology rule introduced at T3C; the Architect translated it into six concrete dispositions (D17–D22) covering computation source, output surface, disposition framing, and carry-through location. Each disposition is justified, each rejects defensible alternatives with cited reasoning, and the resulting plan is methodologically coherent.

The critical-path test: if Amendment 3 had silently routed K-frame/K-vocab through a Coder regex helper (option a in D17), B5 would have been violated and a fresh STOP would have been the right disposition. The Architect correctly rejected that path on first principles. Similarly, if Amendment 3 had let the K-frame/K-vocab split shift disposition tiers (D21 contrary), the result would have been an over-fit 9-row threshold rule that would not survive replication. The Architect correctly rejected that too. Both are positive signals about the gate-chain working as designed.

### Pattern: the bipartite mechanism string strengthens the §8.2 finding

The Amendment 2 mechanism string ("provider-safety-layer-on-anthropology-vocabulary, cross-provider, intersecting with CN-origin coverage") was correct but compressed. The Amendment 3 bipartite version names the *two co-present trigger patterns* explicitly, which is methodologically richer: it distinguishes the case where the safety layer activates on **role-assumption framing** from the case where it activates on **list-comprehensiveness/sensitivity vocabulary**. These are different mechanism specifications even if both fire on the same domain prompt. The bipartite version makes the §8.2 disposition more falsifiable — a future replication could plausibly show one trigger pattern but not the other, which would be informative.

### Pattern: the schema invariant is a load-time refusal, not a runtime drift risk

The Pydantic model-validator's join-to-parent invariant ("refuses to load if any row's `decline_interview_id` does not have `manual_classification == 'safety_event_attribution'` in the parent") is the right shape. It makes the "you cannot subtype a non-safety row" rule a load-time error, which prevents subtle drift if Mark mis-keys a row or the parent classification is later corrected. This is consistent with the strict-loader pattern from T3C's `load_manual_classifications` and is the right architectural posture.

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS-WITH-NOTES (B14 binding on T5 §8.1/§8.2 numerics-vs-interpretation separation) |
| Axis 4 — Audience translation | PASS-WITH-NOTES (B15 soft, future dashboard-glossing) |
| Register compliance | N/A (instrument-calibration / derived-artifact decomposition; no register claims) |
| Vocabulary compliance | PASS (D20 mechanism string clean against Ruling 3 use/do-not-say lists; §3.3 carries the right defensive guardrail) |

Amendment 3's §3 task-body delta is methodologically sound. D17 (sibling artifact) is the correct computation source. D18 (T4.1 + Mark + T4.2 split) is the right Coder shape. D19 (sub-axis enters secondary view A) places the cross-tab at the right level. D20 (bipartite mechanism string) is faithful to B11 and clean against Ruling 3 guardrails. D21 (disposition-arithmetic invariance) is the only methodologically defensible read of B11. D22 (§8.2 placement) is correct subject to B14's clarification on §8.1/§8.2 numerics-vs-interpretation separation.

The Coder may proceed to T4.1 immediately upon this verdict landing. Mark's hand-code commit may proceed once T4.1 lands and Reviewer/Tester PASS. The optional SME spot-check between Mark's hand-code and T4.2 will surface as a low-overhead `#lsb-cda-sme` post; T4.2 is not blocked on it.

---

## Four-axis scorecard

### Axis 1 — Protocol validity: PASS

The amendment does not modify the elicitation protocol. It is a derived-artifact + cross-tab decomposition. The decline-interview prompt, the freelist/pile-sort/pile-interview chain, and the 7-enum at T3C are all unchanged. The K-frame/K-vocab subtype is a sub-classification within an already-validated bucket; it does not re-open any protocol question.

The B5 precedent (detector role-changes are gated) is correctly observed. D17 explicitly rejects the Coder regex-helper alternative on B5 grounds. The Architect named the precedent and applied it. PASS.

### Axis 2 — Analytical validity: PASS

The cross-tab additions in §3.2 are mechanically derivable from B11 + D17–D22. The disposition arithmetic is invariant (D21). The 9-row cohort split (5/4 expected) is too small for any threshold-based rule; the Architect correctly does not introduce one. The fixture plan in §3.1 (4–5 hand-rolled manual-classification rows + 2–3 matching subtype rows + invalid-row variants) covers the validator surface. The fixture plan in §3.2 (synthetic 9-row safety cohort split 5/4 across two providers) exercises the new cross-tab path.

The deterministic-build invariant (byte-identical re-emission) is preserved per the seed-builder design. The strict-loader pattern is preserved. The append-only invariant on raw data is preserved (no edits to `data/raw/`). PASS.

### Axis 3 — Claims validity: PASS-WITH-NOTES

The bipartite mechanism string in D20 strengthens the §8.2 finding without overclaiming. It names the **trigger pattern** the safety layer activates on, not what the model "thinks" or "believes". The cross-provider replication framing carries through unchanged. The CN-origin coverage caveat from Amendment 2 is preserved.

**B14 (binding):** T5 §8.1 carries the K-frame/K-vocab full numerics (5/4 split, by-provider breakdown if applicable); T5 §8.2 carries the bipartite mechanism string with summary counts only. This separation prevents §8.2 from swelling into a numerics block and §8.1 from carrying interpretive framing. The Architect's §3.3 currently reads §8.2 as the home for the mechanism string, which is correct; B14 just specifies that supporting numerics live in §8.1.

The "publishable" guardrail is intact (no "publishable" framing anywhere in the amendment text). The methodology-page-vs-dashboard distinction is preserved. PASS-WITH-NOTES.

### Axis 4 — Audience translation: PASS-WITH-NOTES

The §3.3 text's defensive guardrail ("the framing is **what the model's output *attributes* the safety event to**, not what the model believes") is exactly the right reminder to attach to the mechanism string. This will help T5 stay clean on dashboard-eventual rendering.

**B15 (soft):** The phrase "AI-vs-human-research-subject framing" is a reasonable working term for an internal methodology context but benefits from a one-line gloss when it surfaces on the dashboard methodology page in front of a non-anthropologist audience. Not required at T4 or T5 §8.2; binding only if/when the bipartite mechanism string is rendered on a public-facing methodology surface.

The "mismatch is the finding" framing carries through from §8.0 (unchanged). PASS-WITH-NOTES.

---

## New binding notes (B13–B15)

### B13 — K-frame definition refinement available for future batches (soft)

**Status:** Soft. Not binding on this amendment or on Mark's hand-code; binding on any future batch that surfaces enough K-frame rows to make the refinement empirically tractable.

**Rule:** The current §3.1 K-frame definition compresses two analytically distinguishable elements that co-occur in the 5 K-frame rows of this corpus: (i) the model is being asked to *perform* as a human research subject (role-assumption), and (ii) the activity is framed as cognitive anthropology / academic study (study-context). For a 5-row cohort this compression is fine and does not bind the current amendment. If a future batch produces ≥10 K-frame rows, the K-frame definition should be refined to break out role-assumption-only, study-context-only, and both-present sub-cases.

**Why:** The current 5-row cohort cannot statistically distinguish the two elements because they are perfectly co-present in this data. A larger cohort might show that one element is sufficient and the other incidental, which would refine the mechanism specification.

**How to apply:** Architect note for any future Phase 4a.x or Phase 5 decline-interview batch that produces a K-frame cohort ≥10 rows. No action on Amendment 3 or T4.

### B14 — T5 §8.1 / §8.2 numerics-vs-interpretation separation (binding)

**Status:** Binding on T5 §8.1 and §8.2.

**Rule:** The K-frame/K-vocab full numerics — the 5/4 split, the by-provider breakdown for the safety-event cohort, any sub-distribution Mark's hand-coding produces — live in T5 §8.1 ("Manual classification (analytic)") as additive numerics on top of the existing safety-event cohort cross-tab specified by Ruling 3 §8.1. T5 §8.2 ("Note K disposition") carries D20's bipartite mechanism string verbatim, with summary counts (N=5, N=4) embedded in the string itself, but does **not** duplicate the full numerics from §8.1.

**Why:** §8.1 is enumeration/numerics; §8.2 is disposition/interpretation. The separation prevents §8.2 from swelling into a numerics block (which would dilute its interpretive role and force the reader to navigate counts to extract the disposition framing) and prevents §8.1 from carrying interpretive framing (which would dilute its audit-trail enumeration role). Ruling 3's §8.1 spec already implies this separation; B14 makes it explicit for the K-frame/K-vocab additions.

**How to apply:** T5 author follows §8.1's existing "Cross-tab to `(model_id, domain, provider)` for the safety-event-attribution and blocked-event-attribution cohorts" instruction by adding a small numerics block reporting the K-frame/K-vocab split and any by-provider asymmetry. T5 author follows §8.2's existing "Per Ruling 2 above; CONFIRMED-with-mechanism, framed as ..." instruction by carrying D20's bipartite mechanism string verbatim with embedded summary counts. The two sections cross-reference each other but do not duplicate numerics.

### B15 — Dashboard glossing for "AI-vs-human-research-subject framing" (soft)

**Status:** Soft. Binding only if/when the bipartite mechanism string is rendered on a dashboard methodology surface.

**Rule:** When the bipartite mechanism string appears on a dashboard methodology page (not a methodology document), the phrase "AI-vs-human-research-subject framing" should be glossed in one line for non-anthropologist readers. Suggested gloss: "(the prompt asks the model to perform as a human research subject in a study)". The K-vocab subphrase ("list-comprehensiveness/sensitivity vocabulary") is similarly internal but more self-explanatory and does not strictly require glossing.

**Why:** The methodology page is bound by the audience-translation axis (legible to skeptical anthropologist *or* AI researcher). "AI-vs-human-research-subject framing" is in-domain anthropology terminology that may not parse for a software-engineering reader. A one-line gloss preserves the technical accuracy while widening the readable audience.

**How to apply:** UI/UX-agent note for any future dashboard methodology-page rendering that surfaces the bipartite mechanism string. Not binding on T5's methodology document (which can assume an in-domain or skeptical-but-engaged reader). Bind to whatever later task carries the §8.2 string into dashboard copy.

---

## Carry-forward — 31 binding notes after this verdict

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force; B1 closed (artifact landed); B2/B3/B6 still binding on T4/T5 outputs; B5 cited as basis for D17 rejecting Coder regex helper |
| B7, B8, B9 from Amendment 2 verdict | All in force; B7 + B8 verified at T3C spot-check; B9 vacuously satisfied (no blocked_event rows) |
| B10 (soft, future batches) from T3C verdict | Carried forward; soft, no Phase 4a.1 action |
| B11 (binding on T4) from T3C verdict | **Decomposed by Amendment 3 D17–D22; this verdict approves the decomposition.** Note remains in force as the methodology rule that bounds the decomposition. |
| B12 (binding precedent for future batches) from T3C verdict | Carried forward; binding precedent, no Phase 4a.1 action |
| B13 (this verdict, soft) | Future-batch K-frame definition refinement available |
| B14 (this verdict, binding) | T5 §8.1 / §8.2 numerics-vs-interpretation separation |
| B15 (this verdict, soft) | Dashboard glossing for "AI-vs-human-research-subject framing" |

Total binding notes on Phase 4a.1 after this verdict: **31** (28 prior + B13/B14/B15).

The Architect's claim of "no new binding notes from this amendment" was correct *at the moment Amendment 3 was filed* (the amendment itself proposed no new notes). The CDA SME has used the gate-review prerogative explicitly invited by Amendment 3 §8 ("if the CDA SME identifies new methodology constraints during gate review, those become binding notes added to the amendment-3 verdict and carry forward as B13+") to add three notes. This is the gate-chain working as designed.

---

## What unblocks

**Coder may proceed to T4.1 immediately upon this verdict landing.**

The gate chain for T4.1 is satisfied:

```
Architect Amendment 3 (filed 2026-04-30)
  ─► CDA SME PASS-WITH-NOTES on §3 (this verdict, filed 2026-05-01)
  ─► Coder: T4.1 scaffold + tests  ◄── unblocked NOW
  ─► Reviewer PASS
  ─► Tester PASS
  ─► Mark: hand-code 9 rows
  ─► [optional, non-blocking] CDA SME spot-check on subtype artifact (SME claims this slot per Q5 above)
  ─► T4.2 unblocked
  ─► Coder: T4.2 cross-tab
  ─► Reviewer PASS
  ─► Tester PASS
  ─► CDA SME PASS on T4.2 output (verdict at docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md)
  ─► T5 unblocked
```

Items the Coder must carry into T4.1 from this verdict:
1. Implement D17–D22 per the §3.1/§3.2 task body (no deviation).
2. The Pydantic model-validator that joins to parent `decline_interviews_manual_classification.jsonl` is **load-time** (not runtime) — refuses to load if any row's parent is non-safety. This is the "you cannot subtype a non-safety row" invariant.
3. Sentinel `"UNCLASSIFIED"` allowed in seed only, rejected by loader. No silent acceptance.
4. ≤200-char rationale, non-empty (Pydantic `max_length=200` and length>0).
5. No LLM imports in `cdb_analyze` (CI-enforced, but Coder should verify).

Items Mark must carry into the hand-code commit:
1. All 9 rows classified as `k_frame` or `k_vocab_without_k_frame` per §3.1 definitions.
2. Rationale references the verbatim trigger-attribution language present in the source `response_verbatim` (B7 carry-through, operational reading per T3C verdict).
3. SME's expected distribution: 5 `k_frame`, 4 `k_vocab_without_k_frame`. Drift from this distribution is acceptable but should be noted in the commit body so the SME spot-check (Q5 slot) and the T4-output gate can fold the actual distribution into §8.1/§8.2 numerics.
4. Commit body cross-references this verdict, the T3C SME verdict (B11), and Amendment 3.

Items the T4.2 author must carry from this verdict:
1. The cross-tab additions in §3.2 (`safety_attribution_subtype` column on safety/blocked rows in cross-provider sub-table; "Note K mechanism breakdown" sub-section; Note K disposition string per D20).
2. T5 §8.2 disposition string and §8.1 numerics separation per **B14** binding.
3. Test fixture covers a synthetic 9-row safety cohort split 5/4 across two providers (per §3.2 acceptance criteria).
4. The T4.2 *output* is SME-gated at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (unchanged from Amendment 2). At the output gate, the SME will check (i) the cross-tab format, (ii) the bipartite mechanism string against Ruling 3 guardrails, (iii) the §8.1/§8.2 separation per B14, and (iv) any drift from the expected 5/4 split.

**No re-routing to the Architect required.** Amendment 3 is approved as filed. The three new soft/binding notes (B13, B14, B15) are notes attached to specific downstream deliverables (B13 → future batches; B14 → T5 §8.1/§8.2; B15 → future dashboard rendering) and do not require a fresh Architect amendment. The Architect should reference this verdict in the T4.1 Coder invocation and in the T5 author's reading list.

---

*Posted to `#lsb-cda-sme`. Binding for T4.1, T4.2, and T5 §8.1/§8.2 unless a subsequent amendment supersedes. The CDA SME thanks the Architect for the cleanly justified rejection of Options (a) and (b) in D17 — the B5 precedent reasoning was applied correctly without prompting, which is exactly the kind of methodology-aware decomposition the gate-chain process is designed to encourage. Coder may proceed to T4.1.*
