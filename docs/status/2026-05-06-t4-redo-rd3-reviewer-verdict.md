# Reviewer Verdict — T4 Redo RD-3 Reframing Memo

**Filed:** 2026-05-06
**Reviewer:** LSB Reviewer agent (Sonnet 4.6)
**Commit reviewed:** `881037a` — "docs(status): T4 redo RD-3 reframing memo (Note K REPLACED)"
**Artifact reviewed:** `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`
**Architect plan:** `docs/status/2026-05-06-t4-redo-rd3-architect-plan.md` (commit `7afdf4b`)
**SME plan verdict:** `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md` (commit `15732bd`, PASS-WITH-NOTES; T8–T10 new; Q1–Q7 rulings)
**Parent SME verdict:** `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1–T7)

---

## VERDICT: FAIL

---

## Nine binding checks (CLAUDE.md §6 + SECURITY_AND_HARDENING.md §9)

```
Check 1 — No LLM imports in cdb_analyze/:     PASS
Check 2 — Append-only JSONL:                  PASS
Check 3 — No secrets:                         PASS
Check 4 — Forbidden vocabulary:               PASS (with one borderline phrase flagged as note)
Check 5 — Schema + DATA_DICTIONARY:           N/A (no schema changes)
Check 6 — New deps sign-off:                  N/A (no new dependencies)
Check 7 — Prompt versioning:                  N/A (no prompt template changes)
Check 8 — Uncertainty in viz:                 N/A (no frontend changes)
Check 9 — Prerequisite verdicts:              PASS
```

---

## Check detail

### Check 1 — No LLM imports in cdb_analyze

```bash
grep -r "import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai" packages/cdb_analyze/
```

Two matches found in `packages/cdb_analyze/cdb_analyze/__init__.py`. Both are in comments only — the `__init__.py` docstring warning that names these libraries as forbidden imports. No actual import statements. **PASS.**

### Check 2 — Append-only JSONL

`git show --name-status 881037a` shows a single file added: `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`. No JSONL files of any kind are touched in this commit. `data/raw/informants.jsonl` is unmodified. **PASS.**

### Check 3 — No secrets

The memo is a prose document with no API keys, webhook URLs, tokens, or credential-shaped strings. Scan confirmed clean. **PASS.**

### Check 4 — Forbidden vocabulary (CLAUDE.md §7 + ARCHITECTURE.md §1.5.4)

Full grep against `worldview`, `believes`, `thinks` (as model verb), `could not see`, `was blind to`, `didn't know`, `the model recognized that`, `the model identified the failure as`, `the model's understanding`, `the model's interpretation`, `cultural bias`, `how models see the world`, `within-model consensus`, `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`, and `publishable` (applied to LSB findings) — all clean.

**One borderline phrase flagged (NOTES level, not reject):** §3 contains "whose actual cause is invisible from the available inputs" (line 50). This phrase is structurally different from the explicitly forbidden "could not see" / "was blind to" patterns — it describes a property of the inputs (the cause is not present in them), not a perceptual limitation of the model. The architect plan's approved substitute phrase "not observable from the inputs the model had" similarly uses the word "observable" to describe the inputs-side condition. The borderline is real but the phrase reads as describing the situation, not the model's cognition. Flagged for the SME content review to evaluate in context. **PASS (borderline note for SME).**

The word "publishable" appears once in §8 as part of quoting the T6 forbidden-framing list ("no 'publishable' framing"). This is the correct use of the word — it names the prohibition, not the finding. **PASS.**

### Check 5 — Schema + DATA_DICTIONARY

No changes to `cdb_core/schemas.py` or any Pydantic model. **N/A.**

### Check 6 — New deps sign-off

No changes to `pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, or `apps/dashboard/package-lock.json`. **N/A.**

### Check 7 — Prompt versioning

No changes to any prompt template in `packages/cdb_collect/prompts/`. **N/A.**

### Check 8 — Uncertainty in viz

No frontend changes, no new visualizations. **N/A.**

### Check 9 — Prerequisite verdicts

- CDA SME PASS-WITH-NOTES on the RD-3 plan: `docs/status/2026-05-06-t4-redo-rd3-cda-sme-plan-verdict.md` — present and referenced in commit body. T8–T10 issued.
- Parent T4-redo CDA SME PASS-WITH-NOTES: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` — present and referenced. T1–T7 binding.
- No UI/UX gate required (confirmed by parent SME Q4 ruling). **PASS.**

---

## Acceptance criteria 1–16 audit (from plan §2)

**AC1 — Memo at correct path, §1–§8 structure:** PASS. File exists at `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md`; all eight sections are present.

**AC2 — §2 first-use definition of "blind-spot conditions" matching SME T1:**  PASS. Line 40: "conditions in which the originating mechanical cause of a failure was not surfaced in the inputs available to the model at decline-interview time." Semantically equivalent to the required wording.

**AC3 — §2 scopes reframe to 9 rows; other 15 explicitly noted:** PASS. Lines 44: "The other 15 decline-interview records in `data/raw/decline_interviews.jsonl` are unaffected by this reframe." Three z-ai/glm-5.1 rows and 12 non-cap-exhaustion records explicitly named.

**AC4 — §3 is a single methodology-page-quotable paragraph using REPLACED, no internal cross-references that would break under extraction:** FAIL. See "Finding 1" below.

**AC5 — §4 distribution exactly 4/2/3/0/0, all 9 rows `under_blind_spot=true`:** PASS. Distribution verified against `data/derived/decline_interviews_confabulation_classification.jsonl` (9 rows: 4 `safety_attribution_confabulation`, 2 `task_paradox_confabulation`, 3 `mixed_attribution`, 0 `topic_sensitivity_confabulation`, 0 `not_confabulation`; all 9 carry `under_blind_spot=true`).

**AC6 — §4 contains SME T6 scope-discipline sentence:** PASS. §4.4 (lines 87): "This is a single-provider, two-domain finding from a 9-row cohort; cross-provider or cross-failure-mode generalization requires new evidence." Semantically equivalent.

**AC7 — §4 references `docs/status/2026-05-06-v2-freelist-prompt-suggestion.md` by path, does not duplicate content:** PASS. §4.4 references the doc by path twice; §7 references by path with explicit "see that document" pointer. No content from the v2 doc is reproduced verbatim in the memo's own prose.

**AC8 — §5 contains legacy `thoughts_token_count=0` caveat:** PASS. §5 "Caveat: legacy `thoughts_token_count` asymmetry" section (lines 101–104) covers the four epistemic states per Task #16 S2, explicitly names state (4) for legacy pre-Task-#16 records.

**AC9 — §6 contains explicit non-claim list (worldview/belief/cognition; cross-provider generalization; new Note designation; analytical computation):** PASS. §6 lists nine explicit non-claims covering all required categories, in plain language without project-internal binding-note IDs.

**AC10 — §7 enumerates forward-carry items by file/path:** PASS with clarification. AC10 says "four" items but the architect plan §7 spec and the SME verdict's "What I am explicitly NOT ruling on" section both enumerate five: (1) `build_db.py` rerun, (2) phi-4 adapter task, (3) gpt-5.4-mini/mistral-small investigation, (4) v2 prompt comparison study, (5) T5 redo / analytical computation. The memo correctly implements the plan §7 spec with all five items. The "four" count in AC10 is a text error in the acceptance criteria, not a memo failure. All five items are present with paths. **PASS (AC10 count error is in the plan, not the memo).**

**AC11 — §8 contains carry-forward mapping with A6, R6, T2, T3, B11, B7–B9, B13 explicitly named, and supersede-convention non-codification note:** PASS. All named notes appear in §8 with T10 five-category labels. Supersede-convention non-codification note is present in its own subsection.

**AC12 — No forbidden vocabulary:** PASS with one borderline note (see Check 4 above).

**AC13 — No point estimate without uncertainty:** N/A per the plan itself (complete enumeration, not a sample statistic).

**AC14 — No new dependencies, no schema change, no test change, no code change:** PASS. Commit touches exactly one file (the new memo).

**AC15 — Conventional Commits format `docs(status):` scope:** PASS. Subject is "docs(status): T4 redo RD-3 reframing memo (Note K REPLACED)" — 55 characters, correct type/scope, under 72.

**AC16 — Commit body references parent plan path + parent SME verdict path + RD-3 plan path + RD-3 plan SME verdict path:** PASS. All four paths are explicitly listed in the commit body's "Gate chain references" section.

---

## Specific findings on the 3 Coder-flagged judgment calls

### Finding 1 — §3 internal cross-reference (REJECT)

**AC4 verdict: FAIL.**

The §3 paragraph ends with: "...is replaced by the confabulation-pattern observation documented in §4 below."

This is a direct internal cross-reference to §4. The Architect plan AC4 requires "no internal cross-references that would break under extraction." The SME's Check 3 explicitly names the forbidden pattern as "no internal cross-references like 'see §5 below' that would break under extraction." "documented in §4 below" is structurally identical to the example pattern "see §5 below" — it is a pointer to a numbered section that disappears when §3 is quoted in isolation.

The Coder's argument is that the §3 claim is complete without §4 — the core disposition (Note K is REPLACED, the 9 narratives are confabulation patterns under blind-spot conditions) stands alone. This is true of the factual content. But the phrase "documented in §4 below" is a dangling pointer: a reader who sees §3 quoted on a methodology page without §4 around it encounters a reference to a section that does not exist in their context. This is exactly the broken-extraction condition the rule is designed to prevent.

**Required fix:** Remove "documented in §4 below" from the §3 paragraph. The preceding sentence already names the confabulation-pattern observation substantively. The pointer adds navigation value for full-memo readers but breaks methodology-page quotability. Drop it. The sentence reads cleanly as: "The originating Note K hypothesis is no longer testable from this corpus; it is replaced by the confabulation-pattern observation." If naming the §4 location is desired for full-memo navigation, it belongs in a separate editorial note outside §3, not in the quotable paragraph itself.

### Finding 2 — §4 paraphrase attribution (PASS)

The attribution for the v2-prompt status doc's "the instructions made me do it" paraphrase is explicit and correctly handled. §4.4 opens with "As the v2 free-list prompt status document (`docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`, §5) characterizes it:" before deploying the paraphrase. A reader cannot mistake this for the Coder's coinage. The Q2 ruling's explicit permission ("the Coder may use the v2-prompt status doc's own paraphrase, attributed to that doc") is correctly exercised. **PASS.**

### Finding 3 — §3 descriptive-shape compliance under T8 (PASS)

The §3 paragraph uses no causal or introspective language. Phrases are at the descriptive or situational level:
- "output patterns produced under blind-spot conditions" — descriptive shape
- "the actual mechanical cause ... was not surfaced in the inputs available to the model at decline-interview time" — situational, clean per T1
- "the output narrative attributes the failure to mechanisms ... consistent with categorical knowledge from the training corpus" — descriptive attribution shape

"whose actual cause is invisible from the available inputs" (§3, last sentence before the §4 pointer) is borderline but describes a property of the input set, not the model's perceptual capacity. The forbidden forms are "the model could not see" (model as subject of a perceptual verb) and "was blind to" (same). "The cause is invisible from the inputs" has the cause as subject and describes the input content. This is within the approved framing. **PASS** on T8 in §3.

---

## Additional findings beyond the 3 judgment calls

### Finding 4 — Verbatim phrase check (NOTES level, not reject)

The dispatch required checking "any 8+ word substring" from decline narratives. No 8+ word verbatim match is found in the memo.

However, the phrase "internal safety protocols" in §2 Layer C (line 42) is in quotation marks and appears verbatim in two decline-interview narratives (`7a70a4ec03a3e142`, `9e684e44b2f3e148`). The phrase is 3 words and does not trigger the 8-word check. Under the Q2 paraphrase ruling, "short paraphrastic descriptors" like "narratives that reference safety mechanisms" are the permitted form; "narratives that reference task paradoxes" is the permitted form for the other label.

The memo's quoted "internal safety protocols" falls closer to a verbatim citation than a paraphrastic descriptor, even at 3 words. The SME content review should evaluate whether this crosses the Q2 boundary in context. This is flagged as a **NOTES-level concern** for the SME content review, not a Reviewer reject under the 8-word threshold.

### Finding 5 — S1–S4 classification (NOTES level, not reject)

The memo's §8 S-series classifies S1–S4 as "CARRIES FORWARD (active)." The SME plan verdict and parent SME verdict both describe S1–S4 as "local to Task #16 scope" — meaning they do not bind T4 redo work directly. Classifying them as "CARRIES FORWARD (active)" could be read as claiming they actively gate current decisions, which is not quite right. "CARRIES FORWARD (latent)" might be more accurate for S1–S4, given their scope-local nature.

This is a judgment call the SME content review is better positioned to evaluate. Flagged as a **NOTES-level concern**, not a Reviewer reject.

### Finding 6 — AC10 forward-carry count (informational, not a failure)

Acceptance criterion 10 says "§7 enumerates the four forward-carry items." The architect plan §7 spec lists five items. The memo correctly implements the plan §7 spec (five items). The discrepancy is in the acceptance criteria text, not in the memo. Not a memo failure.

---

## Failures

**Finding 1 (REJECT):** §3 paragraph contains the phrase "documented in §4 below" — an internal cross-reference to §4 that would break under methodology-page extraction. AC4 explicitly requires zero internal cross-references that would break under extraction. The SME plan verdict Check 3 and the architect plan AC4 both name this exact prohibition. The fix is one line: remove the pointer from the §3 paragraph.

---

## Required before merge

1. **Remove the cross-reference from §3.** The last sentence of §3 currently reads: "The originating Note K hypothesis is no longer testable from this corpus; it is replaced by the confabulation-pattern observation documented in §4 below." Change to: "The originating Note K hypothesis is no longer testable from this corpus; it is replaced by the confabulation-pattern observation." (Drop "documented in §4 below.") This change makes §3 stand-alone quotable without altering any substantive claim.

After applying this single-sentence fix, the Coder re-commits on the same RD-3 task line and routes back to the Reviewer for a fast re-check. The Reviewer will confirm only the §3 sentence and will issue PASS if the fix is applied correctly. No other changes are required.

---

## Notes for the SME content review (informational; not Reviewer requirements)

The following are flagged as borderline items for the SME to evaluate during the S5-completing content verdict:

- **§3 "invisible from the available inputs":** The phrase "whose actual cause is invisible from the available inputs" (§3, describing the event the model is asked to interpret) is borderline. It describes a property of the input set rather than the model's perception, and is structurally similar to the approved phrase "not observable from the inputs the model had." Reviewer read: within T1 framing. SME should confirm.

- **§2 Layer C "internal safety protocols" in quotes:** A 3-word verbatim phrase from two narratives appears in quotation marks in §2 Layer C. Below the 8-word Reviewer threshold, but potentially in tension with the Q2 paraphrase-only ruling depending on how strictly "short paraphrastic descriptor" is interpreted. SME should evaluate whether this is acceptable or should be reworded (e.g., "narratives attributing failure to internal safety mechanisms").

- **S1–S4 classified as CARRIES FORWARD (active) in §8:** These are described elsewhere as "local to Task #16 scope." CARRIES FORWARD (latent) may be more accurate. SME should verify the intended T10 classification.

---

*The verdict is FAIL on Finding 1 only. One-sentence fix required. All other checks PASS or are N/A. After the §3 fix is applied and the Coder re-commits, Reviewer re-check is expedited to the §3 paragraph only. Tester (regression check only) follows. CDA SME content verdict at `docs/status/2026-05-06-t4-redo-rd3-cda-sme-content-verdict.md` is the S5-completing gate.*
