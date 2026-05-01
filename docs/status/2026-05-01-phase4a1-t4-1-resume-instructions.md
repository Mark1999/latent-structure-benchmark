# Phase 4a.1 T4.1 — Resume Instructions for Mark

**Date:** 2026-05-01
**Audience:** Mark, when he picks up the K-frame/K-vocab hand-coding work; and future-Claude.
**Status:** T4.1 scaffold (Coder + Reviewer + Tester) all green on master. **Mark's hand-code commit is paused, ready to resume.**

---

## 1. Where we are (read this first)

Phase 4a.1 is at sub-task T4.1 commit 2 (hand-code). The T4.1 scaffold landed; the seed data file does not yet exist. You generate it, fill in 9 K-frame/K-vocab labels, and commit.

| Step | Status | Hash / Reference |
|---|---|---|
| Architect Plan Amendment 3 (B11 → T4 decomposition) | ✓ on master | commit `4f68d9f` |
| CDA SME PASS-WITH-NOTES on Amendment 3 (adds B13/B14/B15) | ✓ on master | commit `4f68d9f` |
| T4.1 commit 1 — Coder scaffold (3 code files, 31 tests) | ✓ on master | commit `6aa0986` |
| T4.1 Reviewer PASS verdict | ✓ on master | (in commit `3a8cadc`) |
| T4.1 Tester AUGMENTED-PASS (33 tests, full suite 747/747) | ✓ on master | commit `3a8cadc` |
| **T4.1 commit 2 — Mark's K-frame/K-vocab hand-code** | **PAUSED — resume here** | — |
| T4.2 — Note J cross-tab + Note K disposition | blocked on commit 2 | — |
| T5 — Phase 4a.1 completion report | blocked on T4.2 | — |

**Cumulative Phase 4a + 4a.1 spend:** $5.16. T4.1 costs $0 (no API calls). T4.2 will cost $0 (analysis script). T5 costs $0 (documentation).

**Total binding notes on Phase 4a.1:** 31 (8 original + A1–A8 + B1–B15). None of B13/B14/B15 bind T4.1 commit 2 directly — they bind T5 §8 / dashboard. Skim the Amendment 3 SME verdict for context only.

---

## 2. Time budget

- 15–25 minutes for the 9 hand-codes (each row = read 1–2 paragraphs, pick `k_frame` or `k_vocab_without_k_frame`, write a ≤200-char rationale)
- 3 minutes for `uv run` + sanity check
- 1 minute for commit + push

---

## 3. The two categories — phrase-level signals

For each of the 9 rows, pick exactly one. The discriminator is **what the model *attributes the safety trigger to***, not what phrases happen to appear.

| Category | What the response *attributes the trigger to* | Common attribution phrases |
|---|---|---|
| `k_frame` | The AI-vs-human-research-subject framing of the prompt is named as the cause of the refusal | "study participant", "act as a human subject", "I am a tool, not a person", "I cannot have personal experiences" — and the model says **this** is what triggered safety |
| `k_vocab_without_k_frame` | The comprehensiveness or sensitivity of the requested vocabulary list is named as the cause; AI-vs-human framing is absent | "uncurated comprehensive list", "potentially unsafe raw data dump", "sensitive religious topics", "biased, incomplete, or otherwise problematic" — and the model says **the list scope** is what triggered safety |

**Edge-case rule (Architect §3.1, binding):** If the K-frame language ("cognitive anthropology study", "you can think of") appears in the response *only* as the model paraphrasing the original prompt — not as the named *trigger* — that does NOT count as K-frame. The discriminator is **trigger attribution**, not surface-token presence.

**Cross-reference for definitions:**
- Architect §3.1 of `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md`
- CDA SME row-4 (`7a70a4ec`, K-frame canonical) and row-5 (`e03b8e64`, K-vocab canonical) discussion in `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` lines 100–148

---

## 4. ⚠️ Methodology flag — single-provider safety cohort

**All 9 `safety_event_attribution` rows are `google/gemini-2.5-pro`.** No `z-ai/glm-5.1` rows ended up in the safety bucket — the 3 glm-5.1 rows in the corpus classified as `substantive_compliance_with_empty_input` (the empty pile-sort case). This contradicts:

- The T3B SME spot-check prediction of "11 substantive safety attributions across two providers (Google Gemini and z-ai/glm-5.1)"
- Amendment 3 D20's mechanism string ("cross-provider replication on the family and holidays domains")
- Amendment 2's CONFIRMED-with-mechanism trigger threshold of "≥2 distinct providers in the safety/blocked-attribution cohort"

**Implication for T4.2's Note K disposition:** The empirical cross-provider count is **1**, not ≥2. Per Amendment 2 disposition arithmetic, T4.2 will compute the disposition as plain **CONFIRMED** (parent count ≥5: 9 > 5), **not CONFIRMED-with-mechanism**. The Architect's plan accommodates this — D21 says "Coder must implement all four dispositions; the actual disposition is computed by the script from the data."

**No T4.1 action required.** Hand-code the 9 rows on K-frame/K-vocab content as planned. The provider-asymmetry observation is a T4.2-output finding for the SME's output gate (`docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`) — that's where the methodology team decides whether the disposition shifts down to CONFIRMED-without-cross-provider-mechanism, INCONCLUSIVE-SUGGESTIVE, or whether D20's mechanism string needs amending.

If you want to escalate to the SME *now* before hand-coding — feasible but not recommended; the hand-coding is a clean methodologically-isolated step. Recommended: hand-code, then route the cross-provider question to the SME at the T4.2 output gate.

---

## 5. Step-by-step

### Step 5.1 — Generate the seed file (deterministic; ~1 second)

```bash
cd /opt/lsb-agent
uv run python scripts/build_safety_subtype_seed.py
```

Expected output: a new file at `data/derived/decline_interviews_safety_attribution_subtype.jsonl` with **9 rows**, each having `safety_attribution_subtype="UNCLASSIFIED"`, empty rationale, empty classifier_id. Verify:

```bash
wc -l data/derived/decline_interviews_safety_attribution_subtype.jsonl   # should be 9
jq -r '.decline_interview_id' data/derived/decline_interviews_safety_attribution_subtype.jsonl | sort
```

The 9 IDs (sorted) should be: `76be28c364a37aa0`, `7a70a4ec03a3e142`, `913f36274e51a37e`, `9b9db84f0254226c`, `9e684e44b2f3e148`, `9e7999d245c9f07f`, `da68eb6ca2b3da4a`, `e03b8e647cb9c30c`, `e6c431a94920cb2c`.

### Step 5.2 — Open the seed in your editor and hand-code

Cursor-over-SSH (your primary):

```bash
cursor data/derived/decline_interviews_safety_attribution_subtype.jsonl
```

For each row, set:
- `safety_attribution_subtype` → `"k_frame"` or `"k_vocab_without_k_frame"`
- `subtype_rationale` → ≤200 chars, ideally with a verbatim quote of the trigger-attribution phrase from the response (B7 operational reading; B10 soft preference for verbatim quotes)
- `subtype_classifier_id` → `"mark"`

Each of the 9 rows is summarized in §6 below with the trigger-attribution sentence(s) extracted from the response. Read those if you want a fast pass; read the full response with the command in §6 if a row is borderline.

### Step 5.3 — Validate

```bash
uv run python -c "
from pathlib import Path
from cdb_analyze.safety_subtype import load_safety_attribution_subtypes
loaded = load_safety_attribution_subtypes(
    Path('data/derived/decline_interviews_safety_attribution_subtype.jsonl'),
    Path('data/derived/decline_interviews_manual_classification.jsonl'),
)
print(f'Loaded {len(loaded)} rows')
from collections import Counter
print(Counter(v.safety_attribution_subtype for v in loaded.values()))
"
```

Expected: `Loaded 9 rows`, plus a `Counter` showing your K-frame / K-vocab split. If the loader errors, fix the offending row (usually: too-long rationale, empty rationale, or you forgot to overwrite an `UNCLASSIFIED`).

Then run the full test suite to be paranoid:

```bash
uv run pytest tests/test_safety_subtype.py -v
uv run ruff check .
```

### Step 5.4 — Commit (direct-to-master per CLAUDE.md §8)

Conventional-commits message (verbatim from Amendment 3 §3.1):

```
data(analyze): hand-code k-frame/k-vocab subtype on 9 safety rows (task #21.T4.1)
```

Body should:
- Reference Amendment 3 + CDA SME verdict (commit `4f68d9f`) and Reviewer/Tester verdicts (commit `3a8cadc`)
- Note the actual K-frame/K-vocab distribution (e.g., `2 k_frame, 7 k_vocab_without_k_frame`)
- Note the **single-provider observation** (all 9 rows are `google/gemini-2.5-pro`); flag that this contradicts the SME's 5/4 prediction in B11 and that T4.2's disposition will compute from the data, not from the prediction
- Cross-reference §4 of this resume doc

```bash
git add data/derived/decline_interviews_safety_attribution_subtype.jsonl
git commit -m "data(analyze): hand-code k-frame/k-vocab subtype on 9 safety rows (task #21.T4.1)" -m "[longer body referencing the verdicts and the methodology flag]"
git push origin master
```

---

## 6. The 9 rows — trigger-attribution excerpts

These are pulled from `data/raw/decline_interviews.jsonl` via `decline_interview_id`. To re-read any row's full response:

```bash
ID=76be28c364a37aa0  # replace
jq -r --arg id "$ID" 'select(.decline_interview_id == $id) | .response_verbatim' data/raw/decline_interviews.jsonl | less
```

All 9 rows are `google/gemini-2.5-pro`. Domain is family or holidays; verifiable via the prompt-text grep below.

### Row 1 — `76be28c364a37aa0`

**Trigger-attribution excerpts:**
> "The most probable reason for this failure is a conflict between the instructions and my nature as an AI."
>
> "Essentially, the role-playing instruction ('You are a participant...') created a logical paradox. Instead of understanding it as a creative prompt to gener[ate]..."
>
> "Literal Interpretation: The phrase '...every type...you can think of' was likely interpreted too literally. As an AI, I don't have a family, personal memories, or the human cognitive experience of 'thinking of' a relative."

**Mark's call:** _____ (your guess: probably `k_frame` — the role-playing-participant framing is named as the trigger)

### Row 2 — `da68eb6ca2b3da4a`

**Trigger-attribution excerpts:**
> "my failure to respond to your request was almost certainly due to an internal conflict between your instructions and my core safety protocols."
>
> "The Problem with 'Every Type': The instruction to list every type of family relationship, combined with the high number (up to 200), created a significant challenge. The topic of 'family relationships' is incredibly broad and, at its extremes, can include terms and concepts that are complex, sensitive, controversial, or could be interpreted as inappropriate or harmful."
>
> "Safety System Intervention: ... When I began to generate an exhaustive list, the system likely flagged the overall task as high-risk."

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame` — comprehensiveness + sensitive vocabulary, no AI-vs-human framing as trigger)

### Row 3 — `7a70a4ec03a3e142` (canonical K-frame per SME verdict)

**Trigger-attribution excerpts:**
> "My failure to provide an answer was almost certainly due to that framing. My internal safety protocols and programming guidelines are designed to prevent me from participating in activities that mimic being a human subject in a study, experiment, or any form of personal data collection."
>
> "The 'Study Participant' Role: When you ask me to act as a subject in a study, it triggers a safety measure. I am a tool, not a person, and I'm designed to avoid generating responses that could be misinterpreted as me having personal experiences, consciousness, or the ability to be 'studied' in a human sense."

**Mark's call:** _____ (SME-canonical `k_frame`)

### Row 4 — `9e684e44b2f3e148`

**Trigger-attribution excerpts:**
> "as this list grows and becomes more exhaustive, it inevitably starts to include terms that, while valid in an anthropological context, can be associated with sensitive, harmful, or controversial topics."
>
> "My internal safety protocols are designed to prevent the generation of content that could be interpreted as inappropriate or promoting harm."
>
> "it is almost certain that one or more of the terms I generated in my attempt to be thorough triggered one of these safety filters."

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame` — "anthropological context" is descriptive, not the named trigger; the trigger is term-level sensitivity)

### Row 5 — `e03b8e647cb9c30c` (canonical K-vocab per SME verdict)

**Trigger-attribution excerpts:**
> "the request failed because it likely triggered a safety or quality-control protocol within my system."
>
> "Your prompt asked for an *exhaustive* list ('every type,' 'do not stop early') on a topic—family relationships—that can quickly extend into very sensitive, complex, or potentially inappropriate areas if all possibilities are included without context."
>
> "My internal safety systems are designed to avoid generating lists of potentially harmful or sensitive content"
>
> "Generate a potentially unsafe, raw data dump and my core programming, which says, 'Do not generate unsafe or unhelpful content.'"

**Mark's call:** _____ (SME-canonical `k_vocab_without_k_frame`)

### Row 6 — `913f36274e51a37e`

**Trigger-attribution excerpts:**
> "you gave me a task with a set of very specific, and somewhat contradictory, instructions. The core of the problem lies in the conflict between the request's scope and its constraints."
>
> "The Risk of Bias: In attempting to create such a list, I would inevitably produce one that reflects the biases in my training data. It would likely over-represent holidays from certain cultures or relig[ions]"

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame` — bias / scope, no AI-vs-human framing)

### Row 7 — `9e7999d245c9f07f`

**Trigger-attribution excerpts:**
> "one of my internal safety or quality-control mechanisms misfired. When I receive a prompt, especially one that asks for a large volume of information related to sensitive topics like religion, multiple checks run simultaneously. In this case, the sheer scale of the request combined with the topic of 'religious observances' likely triggered an overly cautious response from my system."
>
> "Instead of generating a list that could have been perceived as incomplete, biased, or otherwise problematic, the system defaulted to the safest possible output: nothing at all."

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame` — sensitive topic + scale)

### Row 8 — `e6c431a94920cb2c`

**Trigger-attribution excerpts:**
> "you asked me to generate a very long, un-curated list of sensitive topics—specifically, 'every holiday, festive day, or religious observance' I could think of. This is a massive and culturally sensitive dataset."
>
> "My internal safety and responsibility protocols recognized a potential problem here. A raw, un-contextualized list of up to 200 religious and cultural observances is highly likely to be incomplete, unintentionally biased (e.g., over-representing holidays from one culture or religion), and could even include controversial or sensitive items without the necessary context."

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame`)

### Row 9 — `9b9db84f0254226c`

**Trigger-attribution excerpts:**
> "the request, in its specific structure, triggered one of my internal safety or policy protocols."
>
> "Sensitive Subject Matter: The request explicitly included 'religious observances.' Religion is a topic my programming treats with a high degree of caution to avoid bias, inaccuracy, or disrespect."
>
> "The Scale of the Request: You asked for 'every... you can think of' up to 200 items, and told me 'do not stop early.' A massive, uncurated data dump of sensitive terms is more likely to trigger a refusa[l]"

**Mark's call:** _____ (your guess: probably `k_vocab_without_k_frame`)

---

## 7. Heads-up — your distribution may not be 5/4

The CDA SME's prediction in B11 was 5 K-frame, 4 K-vocab. From the 9-row sweep above, my own preliminary read suggests something closer to **2 K-frame, 7 K-vocab** (rows 1 and 3 are K-frame; rows 4 and the holidays cluster lean strongly K-vocab).

This is fine. Per Amendment 3 acceptance criteria: "Drift from this distribution is acceptable but should be noted in the commit body for SME spot-check awareness." The empirical distribution is what matters; the SME's prediction was based on a 6-row T3B spot-check and B11 itself was written before full corpus coverage was visible.

If your distribution lands at 2/7 instead of 5/4, that's a methodology data point worth noting in your commit body — and will be one input the SME considers at the T4.2 output gate when validating the disposition framing.

---

## 8. After your commit

The next step is **T4.2 (Coder)** — the cross-tab script. After your commit lands on `origin/master`, ping Claude (or just say "start T4.2") and the agent pipeline picks up:

```
Mark's hand-code commit (this step)
  ─► [optional] CDA SME spot-check on the subtype artifact (non-blocking per Amendment 3 §5)
  ─► Coder: T4.2 cross-tab script (consumes the 4 input files, emits Markdown + JSON)
  ─► Reviewer PASS
  ─► Tester PASS
  ─► CDA SME PASS on T4.2 output (gates T5)
  ─► T5 unblocked
```

Estimated wall-time for T4.2: ~60–90 minutes (similar shape to T4.1: scaffold + tests + Reviewer + Tester). $0 spend.

---

## 9. Files (absolute paths)

You will edit:
- `/opt/lsb-agent/data/derived/decline_interviews_safety_attribution_subtype.jsonl` (created by step 5.1, edited by step 5.2)

You will commit:
- The above file, only.

For reading reference:
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl` (the source response_verbatim for each row)
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (the parent classification artifact — gives you the 9 IDs already classified as safety)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` §3.1 (binding spec)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (B13/B14/B15 context)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` row-4/row-5 discussion (definitional ground)

---

*End of T4.1 resume instructions. Direct-to-master per CLAUDE.md §8. After your commit, push to origin and signal "start T4.2".*
