---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
authority: advisory (not binding)
scope: docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md §6 "Tone of voice" — worked-example block only
document_reviewed: docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md (v0.1, commit 1c47a55)
verdict: advisory PASS-WITH-NOTES (§6 worked-example specifically)
---

# CDA SME advisory — Appendix §6 worked example

**Authority:** advisory only. The appendix is taste-layer, not doctrinal.
Mark may decline these notes; the orchestrator's framing is defensible
as-is. This file exists because the orchestrator preemptively flagged the
worked-example block as a new exception context that the canonical
CLAUDE.md §7 / ARCHITECTURE.md §1.5.4 / brief §3.1 pattern did not
explicitly anticipate.

**Scope:** appendix §6 only, with focus on the Worked-example subsection
at lines 194–204. Other §6 prose (Dos / Don'ts lists, lines 178–192) is
not in scope for this advisory.

---

## VERDICT: advisory PASS-WITH-NOTES

The exception invocation at line 196–197 lands. The Right example is
methodologically clean. The Wrong example is a documented-exception use
of §1.5.4 forbidden vocabulary, parallel to how §1.5.4 itself names the
terms in order to forbid them. One advisory refinement on the Right
example (§3 below); one optional structural alternative (§4 below).
Nothing here rises to advisory-FAIL.

---

## 1. Exception invocation — does the annotation work?

**Yes, with one minor strengthening available.**

The annotation at line 196–197 reads:

> The "Wrong" example below uses §1.5.4 forbidden terms in order to
> demonstrate the failure mode (same documented exception class as the
> §3.1 forbidden-vocabulary table in the doctrinal brief: naming
> forbidden terms in order to forbid them).

This is a clean invocation of the canonical CLAUDE.md §7 exception
paragraph ("The forbidden vocabulary applies to text *about* the models
that LSB measures. It does not apply to general-purpose English usage
in unrelated contexts...the rule is about how LSB talks about its
subjects, not about whether the word 'think' can ever appear in the
codebase"), and of the §1.5.4 table's own use of the forbidden terms.

The Wrong/Right prose pair is structurally a new pattern type — the
canonical exception was crafted around tabular left-column entries
("Model X believes...") and around negation constructions ("LSB does
not measure cultural worldview..."). A prose example block where the
forbidden vocabulary appears in a fully-grammatical sentence is a
different surface than either. **However:** the *function* is
identical to the documented exception — enumerating forbidden
vocabulary in order to make the failure mode legible to the reader —
and the explicit annotation cites the canonical exception class. The
annotation is sufficient.

**Minor strengthening available** (advisory, optional): the annotation
could be reinforced by an inline tag inside the **Wrong:** block
itself — e.g., prefixing the Wrong block with `[Wrong — do not write
copy like this]` or appending `[end of wrong example]` after the
quoted sentence. This is belt-and-braces in case a future AI designer
loads the appendix in a context window where prior paragraphs are
truncated or de-prioritized. Not needed if Mark trusts the line-196
annotation to travel with the block.

## 2. Is the Wrong example safe even as a wrong-example?

**Yes, with the line-196 annotation in place.**

The orchestrator's framing question — whether a long-context AI designer
will absorb the wrong pattern even when polarity-marked — is the right
question to ask, and is the reason this advisory exists.

Concrete audit of the Wrong block:

- "AI models think about families" — bare `think` applied to models;
  forbidden per CLAUDE.md §7 "generic terms forbidden in any
  model-facing context" enumeration. **Inside the exception.**
- "GPT-5 sees family as fundamentally Western" — cognition attribution
  (`sees`); forbidden by the spirit of §1.5.4 row 3 ("How models see
  the world"). **Inside the exception.**
- "Claude views it through a more globalist lens" — cognition
  attribution (`views`) + value attribution (`globalist`). The cognition
  verb is forbidden by the spirit of §1.5.4; the value framing is a
  §1.5.4-row-4 ("worldview") variant. **Inside the exception.**
- "It's shocking how differently..." — `shocking` is forbidden by §6's
  own Don'ts list at line 188 ("No 'stunning,' 'remarkable,' 'shocking,'
  'surprising'"). Meta-loop: the same section that forbids it uses it as
  the Wrong example. **This is the cleanest pedagogical signal in the
  block** — the reader sees the forbidden marketing adjective inside a
  block explicitly labeled Wrong, immediately following a list that
  forbade it. The meta-loop reinforces the exception rather than
  undermining it.

Polarity-marking adequacy: the **Wrong:** label, the immediately-following
**Right:** counterpart, the closing sentence at line 204 ("The second is
twice as long and contains five times as much information. It also can't
get LSB sued or embarrassed."), and the line-196 annotation collectively
provide four independent polarity signals. This is more than the §1.5.4
canonical table provides (which relies solely on the "Don't say" /
"Say instead" header). The Wrong example is at least as safe as the
canonical table's left column.

## 3. Right example — methodological audit

**Substantively clean, with one advisory refinement.**

Line-by-line:

| Right-example phrase | Verdict |
|---|---|
| "produce different categorical structures when given the same family domain prompt" | PASS — describes outputs (`produce`, `responses`), Register-2 framing implicit, no cognition attribution |
| "GPT-5's free-list responses concentrate on terms from English-language nuclear-family vocabulary" | PASS — `responses concentrate on terms` is data-level description, not attribution-of-knowing; corpus-lens language consistent with §1.5.1 |
| "Claude's responses include a wider set of extended-family and culturally-marked terms" | PASS — same shape; describes the output distribution, not the model's intent or knowledge |
| "Smith's S for the cross-model consensus is 0.41 (95% CI [0.28, 0.55])" | PASS — Register-2 statement, with CI per R10; numeric value is illustrative, not asserted as a real corpus measurement |
| "moderate, not strong" | PASS — verbal CI characterization within the conventional CCM thresholding band; "moderate" is fine for S=0.41 |

**Advisory note** (non-binding, §3a): the Right example's *information
content* is structurally parallel to the Wrong example. Both make the
same comparative claim — GPT-5 outputs cluster on a narrower / more
canonically-English range; Claude outputs include a wider range — but
the Wrong version frames this as cognition ("Western worldview" /
"globalist lens") and the Right version frames it as output
distribution ("English-language nuclear-family vocabulary" / "wider
set of extended-family and culturally-marked terms"). This is the
intended pedagogical contrast, and it works: the Right example
demonstrates *how to say the same factual observation without
attributing intent*.

The residual question is whether a long-context AI designer will read
the Right example's binary structure (one model narrower-English; one
model wider-and-marked) and absorb the value-laden binary even though
the language is methodologically clean. I judge this risk to be small,
because the Right example does the work the Wrong example skipped:
it states *evidence* (free-list term composition) and *statistical
weight* (Smith's S with CI), so the reader leaves the example with the
correct mental model — "comparative observations require data, not
intuition." That is the right takeaway.

**§3a refinement available** (optional): the Right example could
further reduce the residual binary-framing risk by describing the
terms themselves rather than abstracting them into bucket-labels.
E.g.:

> "GPT-5's top free-list terms include 'mother, father, sister, brother,
> son, daughter'. Claude's top terms include those plus 'aunt, uncle,
> cousin, grandmother, godparent, in-law'."

This grounds the comparison in concrete terms instead of in
characterization-labels ("English-language nuclear-family" vs
"extended-family and culturally-marked"). Pedagogically slightly
stronger; loses some compactness. Mark's call.

## 4. Alternative Wrong/Right pair (option B)

If Mark prefers to remove the Wrong-example surface entirely, a
meta-language alternative exists that delivers the same pedagogical
lesson without using forbidden vocabulary at all:

> **Wrong shape:**
> > Copy that attributes thinking, seeing, or believing to a model;
> > characterizes one model's posture as more "globalist" or "Western"
> > than another's; uses marketing intensifiers ("shocking,"
> > "stunning," "remarkable") to dramatize a difference in outputs.
>
> **Right shape:**
> > Copy that names what the outputs look like, reports the consensus
> > statistic with its CI, and lets the magnitude of the statistic
> > carry the narrative load.
>
> **Concrete example of the right shape:**
> > "GPT-5 and Claude produce different categorical structures when
> > given the same family domain prompt. Smith's S for the cross-model
> > consensus is 0.41 (95% CI [0.28, 0.55]) — moderate, not strong."

This option-B variant:

- Removes the Wrong example's verbatim forbidden vocabulary; describes
  the failure modes meta-linguistically instead.
- Preserves the Right example's concrete data shape.
- Loses some pedagogical concreteness (a designer who has never seen
  a "Wrong" sentence may not recognize one in the wild).

**My judgment:** the current orchestrator pair (option A, with the
line-196 annotation) is acceptable. Option B is available if Mark
prefers maximally-conservative framing for the AI-designer audience.
The trade-off is concreteness (option A wins) versus exception-surface
elimination (option B wins). Neither is wrong.

## 5. Verdict and binding annotations

**Advisory verdict:** advisory PASS-WITH-NOTES on §6 specifically.

**Mark must apply:** nothing. This is advisory.

**Mark may apply, in descending order of impact:**

1. **(§1, optional)** Add an inline polarity tag inside the **Wrong:**
   block — e.g., `[Wrong — do not write copy like this]` prefix or
   `[end of wrong example]` suffix. Belt-and-braces for long-context
   AI designers; not needed if the line-196 annotation is trusted to
   travel with the block.

2. **(§3a, optional)** Replace the Right example's bucket-labels
   ("English-language nuclear-family vocabulary" / "extended-family
   and culturally-marked terms") with concrete term lists. Grounds the
   comparison in data rather than characterization; loses compactness.

3. **(§4, alternative)** Switch to the option-B meta-language Wrong/
   Right pair. Eliminates the forbidden-vocabulary surface entirely;
   loses concreteness.

**Mark may decline all three.** The current §6 worked example is
methodologically defensible as-is, given the line-196 annotation. The
appendix's own status as taste-layer (not doctrinal) further limits
the binding scope of this advisory.

## 6. Forbidden-vocabulary scan results

Grep on the §6 worked-example block (lines 194–204) returned the
following hits, all inside the documented exception class:

- Line 199 (Wrong block): `think` (bare, generic), `sees` (cognition
  attribution), `views` (cognition attribution), `worldview`-shape
  ("globalist lens"), `shocking` (forbidden marketing adjective per
  §6 line 188).
- Line 204 (closing sentence): no forbidden vocabulary.

All hits are inside the **Wrong:** quoted block, which is annotated at
line 196 as a documented-exception use. **No undocumented forbidden-
vocabulary usages were found in §6.**

The Right block (line 202) is clean: no forbidden vocabulary, no
cognition attribution, no value attribution. The Smith's S framing
with CI is consistent with R10 and §4.2 register language.

---

## 7. Summary for Mark

- **Advisory verdict:** PASS-WITH-NOTES on §6 worked-example.
- **Exception invocation works.** The line-196 annotation lands the
  exception class cleanly.
- **Wrong example is safe.** Four independent polarity signals;
  meta-loop with §6's own Don'ts list reinforces the lesson.
- **Right example is methodologically clean.** Register-2 framing,
  R10-compliant CI, no cognition attribution.
- **One residual concern, advisory only:** the Right example's
  bucket-label framing structurally mirrors the Wrong example's
  comparison shape. Concrete term lists (§3a) or the option-B
  alternative (§4) reduce this further. Neither is required.
- **You may decline all advisory notes** and ship the appendix as-is.
  The §6 worked example is methodologically defensible.

This advisory does **not** trigger a re-review of the doctrinal brief.
The 2026-05-17 PASS-WITH-NOTES verdict on `FRONTEND_DESIGNER_BRIEF.md`
stands independent of any change to this appendix.

---

*End of advisory. Appendix is taste-layer; this verdict does not gate
handoff to the future AI frontend designer.*
