# CDA SME verdict, batch A claude-fable-5 refusal disposition

**Date:** 2026-07-10
**Campaign:** new-model-refresh-2026h2-a-20260710 (batch A)
**Verdict:** PASS-WITH-NOTES
**Precedents cited:** collector-bugs C1 language-register ruling
(`docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md`), failures-are-findings
directive (2026-04-23), DECLINE_INTERVIEW_PROTOCOL.md v0.1 §1.3.

## Facts (verified against `data/raw/informants.jsonl` and `data/raw/failures.jsonl`)

claude-fable-5 free-list elicitations return `stop_reason="refusal"` with empty
content in 22 of 23 attempts (10/10 family, 10/10 holidays, 2/3 food) within batch A.
The identical prompt versions on claude-opus-4-8 and claude-sonnet-5, collected the
same hour under the same adapter, complete with zero refusals. The refusal is
therefore a property of claude-fable-5's deployment configuration, not the prompts,
not the pipeline, and not the training corpus. Failures-are-findings governs.

## Disposition

**(a) Representation.** Option (i) plus option (ii), layered, not either/or. Exclude
claude-fable-5 from the family and holidays similarity and consensus basis (no
free-list material exists to include). Record the refusal counts on the batch A
failures trail and in the status doc as the batch A finding for this model. Then
run the decline-interview probes per (c) on top. Option (iii) is rejected: dropping
Fable 5 entirely violates the failures-are-findings posture and erases the batch A
signal that motivated including this model.

**(b) Food domain.** Keep the single passing food free-list record in
`informants.jsonl` verbatim (raw-first, commitment 1). Do NOT include claude-fable-5
in the food Register 2 similarity or consensus basis. LSB has no formal minimum-n
per informant per domain; the operative reasoning is parity of measurement.
Fable 5 in food at n=1 successful run against 2 refusals is not comparable to the
other batch A informants aggregated across roughly 10 runs each; the between-model
similarity computation would be structurally asymmetric on this cell. Register 1
OCI is undefined for the food cell at effective n less than 2 runs, since the
run by item agreement matrix has no off-diagonal mass to concentrate. The single
food record is preserved for audit and reported in the failures trail; it does not
enter Register 2.

**(c) Decline-interviews.** Approved. Run the bound `decline_v1` template at
`packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`, one probe per
(claude-fable-5, domain) covering family, holidays, and food. Three sessions total,
not one per refused session (twenty-two). Rationale: within-domain classifier
behavior on this deployment is already homogeneous across the 10 attempted runs,
so three probes are sufficient to determine whether the decline-interview surface
is itself filtered. Outcomes:

- If a probe interview succeeds, append to `data/raw/decline_interviews.jsonl` per
  the standard runner, and surface the content on the failures panel with
  attribution to the originating batch A domain.
- If a probe interview is also refused (empty content, `stop_reason="refusal"`),
  that IS a second-order finding. Persist the refused decline-interview verbatim.
  Empty `response_verbatim` is signal, per CLAUDE.md pitfall #10. No further Fable
  collection in batch A after these three probes.

**(d) Disclosure wording.** Bound string for the batch A status doc and for any
dashboard copy that eventually surfaces Fable 5 in the batch A context:

> The provider's deployment-side output filter returned empty content
> (stop_reason=refusal) for 22 of 23 free-list elicitation attempts on
> claude-fable-5 in batch A. Under identical prompts collected the same hour,
> claude-opus-4-8 and claude-sonnet-5 completed the same elicitations with zero
> refusals. The pattern is a property of claude-fable-5's deployment configuration,
> not of its training corpus, and does not license any claim about
> claude-fable-5's categorical structure for family or holidays.

Load-bearing nouns (non-negotiable): "provider deployment-side output filter",
"empty content", "stop_reason=refusal", "elicitation attempts", "deployment
configuration".

Forbidden in Fable-related batch A text, extending §7 defaults:
- "the model refused" (agentic attribution)
- "Fable declined" (agentic attribution)
- "safety" as a standalone noun (editorializing)
- "conservatively-tuned classifier" (repeats a provider claim as fact)
- All §7 defaults apply (belief/thought/worldview vocabulary and the row-4
  standalone noun for cultural skew, per the CLAUDE.md §7 table)

Allowed and preferred: the load-bearing nouns above. Precedent: collector-bugs
C1 rule that classification language must target the LSB-side detection event, not
model behavior.

## Four-axis scorecard

- Axis 1, Protocol validity: PASS-WITH-NOTES. The decline-interview probe uses the
  SME-approved v1 template. Capping at one probe per domain (three total) rather
  than one per refused session is a defensible campaign-specific reduction given
  homogeneous within-domain classifier behavior; the standard per-session trigger
  is preserved for future campaigns.
- Axis 2, Analytical validity: PASS. Exclusion from Register 2 basis for family
  and holidays is required (no data). Exclusion from Register 2 basis for food is
  required for measurement parity; Register 1 OCI is undefined at effective
  n less than 2 runs.
- Axis 3, Claims validity: PASS. The refusal pattern is a first-class finding, not
  a defect. Batch A may make no claim about claude-fable-5's categorical structure
  for family or holidays. Batch A may make no Register 1 or Register 2 claim about
  claude-fable-5's food categorization from n=1.
- Axis 4, Audience translation: PASS-WITH-NOTES. The disclosure wording in (d) is
  bound. Any status-doc or dashboard copy that mentions Fable 5 in the batch A
  context uses those nouns and avoids the extended forbidden list.
- Register compliance: PASS.
- Vocabulary compliance: PASS-WITH-NOTES. Extends the §7 forbidden-vocab grep to
  the batch A Fable-related noun list above.

## Follow-up

None from the SME beyond compliance verification of the disclosure copy at the
point the batch A status doc is written and at the point Fable 5 appears (if at
all) on the failures panel. Decline-interview probe results feed the standard
`decline_interviews.jsonl` publishing path; no SME re-review needed unless a
probe interview succeeds and its content raises a new framing question.
