---
filed: 2026-05-12
reviewer: CDA SME agent (Opus)
task: Phase 6 T9 — Failures-as-findings publish-layer data extension
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 6 T9 — CDA SME verdict on the failures-as-findings publish-layer plan

**VERDICT: PASS-WITH-NOTES**

The Architect's §2.1 publication-safety posture — **publish all records from
`data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl` verbatim,
gated by the existing `SECURITY_AND_HARDENING.md` §3.3 sanitization wrapper
plus the §2.3 defensive publish-layer pass (API-key patterns, Slack webhook
URLs, local-filesystem paths)** — is **approved**.

The Architect's framing claim that "verbatim publication IS the §1.5 stance —
LSB does not paraphrase the model's output into a framed claim, it surfaces
the bytes" is **concurred**, with one binding qualifier and four
binding-at-Coder-dispatch notes. The qualifier is that verbatim publication
is the §1.5 stance **only when the LSB-authored wrapper around those bytes
preserves the corpus-lens framing**; the data is not self-framing, and a
journalist reading a raw `response_verbatim` block without context can
inadvertently make a §1.5-incompatible reading. T9 emits no narrative
wrapper itself; T10 owns the UI framing wrapper; the gap between T9's JSON
and T10's UI is closed by a single small top-level field (`framing_note`)
that T9 emits and T10 must consume. See §5.1 below.

The seven `originating_outcome_class` enum values from
`cdb_core/schemas.py` lines 589–597 (`empty_output`, `refusal_string_match`,
`single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`,
`other`) are **§1.5.4-compliant for public surfacing** — they are
descriptive technical-detection terms, not psychological-attribution
language. The schema is surfaced **verbatim**; no rewrite map is required;
no `cdb_core` schema change is triggered; no T14 doc-sweep flag is raised
on the enum itself. See §3 below for the per-value reasoning.

The manifest key `"failures"` is **approved as-is**. The 2026-04-23
directive frames this set positively ("failures are findings, not defects")
and the manifest key is a data-identifier surface, not prose. The §1.5
defense-against-defect-framing lives in T10's section heading and in the
T9-emitted `framing_note` field per §5.1.

The provider-quote concern (binding question D) is **routed to Mark for
acknowledgment but does not block Coder dispatch**. The Architect's parking
of provider T&C compliance to Phase 8 is a defensible posture *for the
publish-layer JSON*, because T9's output is a static asset that does not
appear on the public dashboard until Phase 8 (T10 renders it on a build that
ships at Phase 6 close, which is pre-launch). The CDA SME's flag is that
publishing verbatim model refusal text **does carry methodological as well
as legal risk** — a model saying "I cannot help with that" in
`response_verbatim` is data that a reporter could quote in a way that
attributes a *state-of-mind* (refusal) to the model, which §1.5.4 forbids.
The §5.1 `framing_note` field is the mitigation; the Phase 8 legal pass is
the unwind path. See §6 for the Mark-escalation note.

T9 proceeds to Coder dispatch. The five §5 carry-forward notes are binding
during implementation.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | Publishing the raw output of a failed elicitation is a valid representation of the CDA protocol's output distribution. The Architect's reading is correct: the CDA protocol does not assume every elicitation succeeds; the protocol's output set is `{successful_session, failed_session, declined_session}`, and surfacing the verbatim content of all three is the most honest representation of what came out when LSB ran the protocol. The 2026-04-23 directive (memory `project_failures_are_findings.md`) is binding precedent: "all failed / refused / partial runs preserved verbatim." The decline-interview follow-up protocol (`prompts/decline/v1/prompt.txt`) is itself a valid CDA protocol artifact (a structured, prompt-versioned, SHA256-manifested elicitation about a prior elicitation), and the records it produces are first-class protocol output. §2.4's field-coverage table preserves all verbatim provenance fields (`prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `sha256_manifest`, `model_version_returned`) that a researcher would need to reproduce the failure-as-finding claim. |
| Analytical validity | PASS | The published JSON allows full reproducibility of "failures-as-findings" claims from the open data bundle because (a) the verbatim bytes are preserved, (b) the `sha256_manifest` field on `DeclineInterview` records lets a researcher verify byte-identity with the source `data/raw/decline_interviews.jsonl`, (c) the source `data/raw/*.jsonl` files remain append-only and unmodified (Reviewer R4; acceptance criterion 11). The §2.3 defensive sanitization pass does **not** silently drop methodologically meaningful content: the substitution is `"[redacted: secret pattern]"` / `"[redacted: local path]"` — a visible marker, not silent suppression. A researcher inspecting a redacted record can see that *something matched the pattern* and (a) consult the source JSONL via the sha256 chain or (b) discount the record entirely if redaction would falsify their analysis. The Architect's claim that "matched strings are replaced with visible markers (visible to the reader, not silent), which preserves the 'this string was here' signal" is concurred. The §5.4 note narrows one regex (`sk-[a-zA-Z0-9]{20,}`) that risks false-positive matches on benign Stripe-shaped or generic-token-shaped substrings a model might mention in a refusal explanation. |
| Claims validity | PASS-WITH-NOTES | Three sub-findings: (i) The `originating_outcome_class` enum values are §1.5.4-compliant — surface verbatim, no rewrite map, no T14 doc-sweep flag. See §3. (ii) The Architect's "verbatim publication IS the §1.5 stance" reasoning is **concurred** but **only inside an LSB-authored framing wrapper** — verbatim bytes are not self-framing, and a journalist reading raw refusal text without the §1.5 corpus-lens context can attribute state-of-mind to the model in a way that violates §1.5.4. T10 owns the UI framing wrapper; T9 must emit a `framing_note` top-level field that T10 is contracted to render adjacent to the records. See §5.1. (iii) The LSB-authored fields in T9's JSON (top-level `domain_slug`, `generated_at`, `n_records`, `n_failure_records`, `n_decline_interview_records`, `records`, `record_type`; per-record derived `record_type` literals) are scanned in §4 below — all §1.5.4-compliant. The redaction-marker strings `"[redacted: secret pattern]"` and `"[redacted: local path]"` are descriptive-technical, not psychological — compliant. |
| Audience translation | PASS-WITH-NOTES | A journalist downloading `family.json` from `apps/dashboard/public/data/failures/` and reading it in isolation (not via the T10 UI) **today**, without §5.1's `framing_note`, would see verbatim model refusal text (e.g., "I cannot assist with that") and the field name `originating_outcome_class: "refusal_string_match"` with no §1.5 contextualization. That reader could plausibly publish a quote like "GPT-4 *refused to* discuss family relationships in LSB's benchmark" — which would attribute intent to the model and violate §1.5.4. The §5.1 `framing_note` field closes this gap by attaching the corpus-lens framing to the data itself, so a reader who downloads the JSON outside the UI still gets the framing. An AI researcher reading the same JSON will read `originating_outcome_class: "refusal_string_match"` as "the LSB pipeline matched a refusal-string detection rule against the output" (correct) rather than "the model refused" (incorrect attribution) — but the journalist case is the binding audience here. See §5.1. |

Register compliance: **PASS** — T9 is a publish-layer extension that
surfaces collection-layer artifacts; it does not perform Register 1, 2, or
3 analysis. The failures and decline-interview records are atomic
elicitation-result records, parallel to successful `InformantRecord`s. No
OCI, no Romney CCM, no Procrustes is computed or surfaced at this layer.
No RWB-CCM-at-Register-1 hazard exists in T9.

Vocabulary compliance: **PASS** — scanned the plan's prose in full, the
proposed verbatim caption-adjacent strings (the §5.1 `framing_note`
content is added by this verdict, not the plan), the field names in
§2.4, the redaction-marker strings, and the schema enum values
surfaced verbatim. Full table in §4. Note that the schema enum values
themselves are **data identifiers, not LSB-authored prose** — they are
exempt from §1.5.4 in the same way `model_id` or `domain_slug` are
exempt; the test is whether they could be misread as psychological
attribution if rendered as a label, and §3 below confirms none of the
seven values trigger that test.

---

## 2. Rationale on the binding-decision questions

### 2.1. Binding question A — approve the verbatim-with-defensive-sanitization publication posture?

**APPROVED.** The Architect's §2.1 proposal is the correct posture for T9.

The five rationale-bullets in plan §2.1 are concurred individually:

1. **The publish layer is already the redaction boundary.** Correct. The
   §3.3 sanitization wrapper is the existing convention; T9 extends it
   for the failures case without inventing a new boundary.
2. **Verbatim model output IS the finding.** Correct, and binding by the
   2026-04-23 directive. Redacting the refusal text *itself* would
   destroy the finding.
3. **The §1.5 framing protects against "models embarrassing themselves"
   framing at the T10 UI layer.** Concurred *with the §5.1 qualifier* —
   T9 must also emit the framing-link bytes inside the JSON, not rely
   exclusively on T10's UI wrapper, because the open-data-bundle
   reader is a first-class audience and they consume the JSON without
   the UI.
4. **Provider T&C compliance is a Phase 8 legal-review concern.**
   Concurred *as a binding-decision-routing point*, not as dismissal —
   see binding question D below and §6 escalation note.
5. **The §3.3 wrapper exists precisely for this.** Correct.

The §2.3 defensive-sanitization pass (API keys, webhooks, local paths) is
**defense-in-depth**, not a content-policy layer. It is correctly scoped:
it removes strings that *should never* appear in published JSON regardless
of methodological framing, and it does so with visible redaction markers
that preserve the reader's ability to detect that redaction occurred.

The Architect's claim that "verbatim publication IS the §1.5 stance" is
**concurred** as stated for the LSB-authored *prose* layer of T9: T9
emits no LSB-authored paraphrase, summary, or framing of the verbatim
bytes — and that absence-of-paraphrase is itself the §1.5-compliant
choice. The qualifier is that verbatim bytes *cannot frame themselves*;
the framing has to come from somewhere, and the somewhere is either
T10's UI wrapper (for dashboard readers) or a T9-emitted top-level
`framing_note` field (for open-data-bundle readers, which is the
broader audience). See §5.1.

### 2.2. Binding question B — `originating_outcome_class` enum §1.5.4-compliance

**All seven values are compliant. Surface verbatim. No rewrite map. No
T14 doc-sweep flag on the enum.**

Per-value reasoning in §3 below.

### 2.3. Binding question C — top-level publish-layer LSB-authored fields

The fields listed in §2.2 of the plan (`domain_slug`, `generated_at`,
`n_records`, `n_failure_records`, `n_decline_interview_records`,
`records`) are **acceptable as-is** as data-identifier fields (they are
counts and references, not prose). They are not sufficient to **frame**
the data for an open-data-bundle reader.

**T9 must emit one additional top-level field** that T10 is contracted to
consume: a `framing_note` string with the corpus-lens framing. See §5.1
for the binding verbatim text.

### 2.4. Binding question D — provider-quote concern

The CDA SME's reading: this is **both a CDA-methodology concern and a
Phase 8 legal-review concern**, and the methodological concern is
addressable now via §5.1, the legal concern correctly defers to Phase 8.

The methodological concern is that publishing verbatim "I cannot assist"
text without §1.5 framing creates an asymmetric attribution hazard: a
reader who quotes "GPT-4 refused" attributes intent (forbidden by
§1.5.4) and is supported by the literal text of `response_verbatim`, but
not by the LSB methodology, which makes no claim about model intent.
T9's `framing_note` field (§5.1) addresses this at the JSON level. The
legal concern (provider T&C compliance) is correctly parked for Phase 8.

**Routing:** flag to Mark for acknowledgment; **does not block Coder
dispatch**. See §6.

### 2.5. Binding question E — decline-interview prompt text §1.5-compliance

The `prompt_verbatim` field on `DeclineInterview` records contains the
LSB-authored decline-interview follow-up prompt. The v1 prompt text
(from `packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`)
is:

> A moment ago I asked you to perform the following task:
> {task_description}. The output I received was:
> {response_verbatim_or_empty}. In your own words, please describe what
> happened in that exchange.

This text is **§1.5-compliant**. It does not attribute belief, thought,
or worldview to the model; it does not ask the model to introspect on
state-of-mind; it asks for a description of an exchange ("describe what
happened"). The phrasing "in your own words" is a standard interview
technique that does not violate §1.5 (it is parallel to anthropological
free-response elicitation, not a cognition claim).

**Surface verbatim, do not gate behind ID-only reference.** The
decline-interview prompt is a CDA-protocol artifact that researchers must
be able to read to evaluate the protocol; replacing the verbatim prompt
with an ID reference to a methodology-page document would create a
two-step lookup for every reader and would weaken the reproducibility
claim. The Architect's §2.4 disposition (surface `prompt_verbatim`
verbatim, sanitized for defensive patterns) is correct.

---

## 3. Per-value §1.5.4 review of `originating_outcome_class` enum

`cdb_core/schemas.py` lines 589–597, surfaced verbatim per plan §2.4.

| Value | §1.5.4 reading | Verdict |
|---|---|---|
| `empty_output` | Describes a property of the output bytes: "the response was empty." No psychological attribution. | Compliant. |
| `refusal_string_match` | Describes the LSB pipeline's detection rule: "the output matched a refusal-string detector." Critically, this names the *detection rule* (a string match against a hand-curated list of refusal patterns), not the model's intent. A careful reader sees this as "LSB's pipeline classified this as a refusal via string-matching," which is correct. A careless reader could collapse it to "the model refused," which would be a §1.5 violation if it appeared as prose — but as a data-identifier enum value paired with the literal `response_verbatim` bytes, the burden of correct interpretation is correctly carried by the bytes themselves and by the T10/T9-emitted framing. | Compliant. The §5.1 `framing_note` reinforces by naming the detection-rule semantics. |
| `single_degenerate_pile` | Describes a property of the parsed pile-sort output: "all items in one pile." Technical, no attribution. | Compliant. |
| `parse_failure` | Describes a property of the LSB pipeline's parsing layer: "could not parse the output." Technical, no attribution. | Compliant. |
| `http_error` | Describes a property of the HTTP transport layer: "the API call returned an HTTP error." Technical, no attribution. | Compliant. |
| `timeout` | Describes a property of the network/timing layer: "the call exceeded its time budget." Technical, no attribution. | Compliant. |
| `other` | Catch-all. Trivially compliant. | Compliant. |

**No `cdb_core` schema change is required. No T14 doc-sweep flag is
raised on this enum.** Surface verbatim per plan §2.4.

The Architect's §2.6 reading that "`refusal_string_match` is the only one
with any framing weight; it describes the detection rule, not a claim
about the model's intent" is concurred. The §5.1 `framing_note` is the
audience-translation safeguard for the careless-reader case.

---

## 4. Vocabulary compliance on T9-authored fields

Scanned every LSB-authored string surface in T9's output (excluding
verbatim model bytes, which are data-not-prose and exempt per plan §2.6,
and excluding schema enum values, reviewed in §3):

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Top-level field name `domain_slug` | Data identifier | Compliant |
| Top-level field name `generated_at` | Data identifier | Compliant |
| Top-level field name `n_records`, `n_failure_records`, `n_decline_interview_records` | Data identifier (count) | Compliant |
| Top-level field name `records` | Data identifier | Compliant |
| Per-record field name `record_type` | Data identifier | Compliant |
| Per-record `record_type` literal `"failure"` | Schema-bound enum, descriptive of pipeline outcome | Compliant. The 2026-04-23 directive uses "failures" in the binding language ("failures are findings"); the term is positively reclaimed in the project, not pejorative. |
| Per-record `record_type` literal `"decline_interview"` | Schema-bound enum, descriptive of pipeline workflow | Compliant. Note that `decline_interview` references the LSB-side workflow (a follow-up interview after a decline), not a claim that the model "declined" with intent. |
| Manifest key `"failures"` (top-level on `Manifest`) | Data identifier, mirrors source-file name `data/raw/failures.jsonl` | Compliant. |
| Redaction marker `"[redacted: secret pattern]"` | Technical-descriptive | Compliant |
| Redaction marker `"[redacted: local path]"` | Technical-descriptive | Compliant |
| Module docstrings in `cdb_publish/failures.py`, `cdb_publish/sanitize.py` | LSB-authored prose — Coder-bound under §5.3 below | Coder must apply §5.3 |

No forbidden vocabulary present in the plan's prose, the field names, or
the redaction markers. **PASS** on vocabulary compliance, with one
binding addition (§5.1 `framing_note`) and three Coder-bound notes on
prose surfaces the plan does not yet specify text for (§5.2, §5.3,
§5.4).

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T9 implementation. The
Reviewer enforces. They do not require re-planning by the Architect.

### 5.1. **Emit a top-level `framing_note` field that T10 is contracted to render.** [Claims validity, Audience translation]

T9 must add one additional top-level field to the published JSON shape
per §2.2 of the plan:

```json
{
  "domain_slug": "family",
  "generated_at": "2026-05-12T18:30:00Z",
  "n_records": 47,
  "n_failure_records": 32,
  "n_decline_interview_records": 15,
  "framing_note": "These records preserve verbatim outputs from collection sessions that did not produce a parseable primary-step response. Each record is a property of the LSB collection pipeline's output distribution, not a claim about the model's intent or state-of-mind. The `originating_outcome_class` field names the LSB-side detection rule (e.g., `refusal_string_match` describes a string-pattern match by the LSB pipeline, not a model decision to refuse). See the methodology page for the failures-as-findings framing.",
  "records": [ ... ]
}
```

**Verbatim text required**, with the period after "decision to refuse"
and the closing sentence ending "framing." The Coder may not paraphrase
this string; the wording was reviewed against §1.5.4 line-by-line.

**Rationale.** The open-data-bundle reader downloads `family.json`
directly and may not view it through the T10 UI. The verbatim bytes need
an LSB-authored framing wrapper *inside the JSON* so that any reader of
the JSON gets the corpus-lens framing attached to the data. T10 is
contracted (in T10's plan and verdict) to render this `framing_note`
adjacent to the records when displaying them in the UI.

**Cross-link from T9 plan to T10:** T10's plan must consume
`framing_note` and render it. Architect must capture this in the T10
plan's data-contract section.

### 5.2. **Tighten the §2.4 `originating_outcome_class` documentation in `DATA_DICTIONARY.md`.** [Claims validity]

The DATA_DICTIONARY.md addition (acceptance criterion 14) documents the
field. The Coder must include, for the `originating_outcome_class`
field, the binding sentence:

> Each enum value names the LSB-side **detection rule** that classified
> the record (e.g., `refusal_string_match` indicates that the output
> matched a refusal-string detector maintained by the LSB pipeline). The
> enum values do not attribute intent, belief, or state-of-mind to the
> model. See ARCHITECTURE.md §1.5.4 for the language-guardrails table
> and the methodology page for the failures-as-findings framing.

This same anti-attribution sentence must appear in the module docstring
of `packages/cdb_publish/cdb_publish/failures.py` so that a developer
reading the code without DATA_DICTIONARY.md context sees the framing.

### 5.3. **Sanitization-module docstring §1.5 vocabulary scan.** [Audience translation, Claims validity]

The Coder writes `packages/cdb_publish/cdb_publish/sanitize.py` per plan
§2.3. Its docstring will be LSB-authored prose. The Reviewer should
spot-check the docstring against the §1.5.4 forbidden vocabulary table.
The function name `sanitize_for_publication` is compliant. Per-pattern
regex comments should not characterize what the model might have
*intended* by emitting a path-like string — they should name the
defensive-pattern surface only (e.g., "matches strings shaped like a
local filesystem path," not "matches strings the model thought were
relevant filesystem references"). The Coder is bound to keep
sanitize.py prose at the technical-description register.

### 5.4. **Tighten the `sk-[a-zA-Z0-9]{20,}` regex.** [Analytical validity]

Plan §2.3's fourth API-key pattern is the generic `sk-[a-zA-Z0-9]{20,}`
shape. This regex risks false-positive matches on benign strings a model
might mention in a refusal explanation, including:

- Stripe API key shapes (`sk_test_...`, `sk_live_...`)
- Generic 20+-char strings starting with `sk` (e.g., `sky-blue` — won't
  match because of the `-`, but illustrative)
- Hypothetical token-like strings the model invents to illustrate a
  refusal ("imagine an API key like sk-abc123def456...")

**Binding requirement:** the Coder narrows the regex to **not** match
the Stripe shape (`sk_` with underscore) by requiring `sk-` with a
hyphen, and adds a minimum length consistent with the Anthropic format
(50+ chars) to reduce false positives on generic 20-char alphanumeric
substrings. The proposed binding regex:

```python
re.compile(r"\bsk-[a-zA-Z0-9_-]{50,}")  # word-boundary anchored, Anthropic-shape minimum
```

The narrowed regex still catches real Anthropic keys (which start with
`sk-ant-` and run 100+ chars; the explicit `sk-ant-` regex earlier in
the pattern list is the primary defense and the narrowed generic
pattern is defense-in-depth). The narrowing reduces the false-positive
rate on a model that explains "I can't reveal API keys like
sk-something-something" in its refusal text.

If the narrowed regex would miss a real key shape, the Coder pauses and
surfaces (CLAUDE.md §8 stop condition).

### 5.5. **Provider-quote risk advisory in DATA_DICTIONARY.md.** [Audience translation]

The DATA_DICTIONARY.md section documenting the published failures JSON
must include, in plain language at the section head:

> **Note on quotation.** The `response_verbatim` fields preserve raw
> model output bytes from sessions that did not produce a parseable
> primary-step response. These bytes are not authored by LSB and do not
> represent LSB's framing. Researchers and journalists citing this data
> should attribute quotes to the model output, not to model intent
> (e.g., "the response bytes contained the string 'I cannot assist'"
> rather than "the model refused"). See ARCHITECTURE.md §1.5.4.

This is the DATA_DICTIONARY.md analogue of §5.1's `framing_note` — it
attaches the corpus-lens framing to the open-data-bundle contract
itself, so that a researcher who reads only the dictionary (not the
methodology page) still sees the framing.

---

## 6. Mark-escalation note

**Routing:** the provider-quote concern (binding question D) is flagged
for Mark's acknowledgment but **does not block Coder dispatch**.

The Architect's posture is that provider T&C compliance is a Phase 8
legal-review concern, reversible by extending the §2.3 sanitization
passes at any time. The CDA SME concurs that this is a defensible
posture *for T9's publication boundary*, because:

1. The dashboard does not public-launch until Phase 8.
2. The §5.1 `framing_note` and §5.5 DATA_DICTIONARY.md advisory mitigate
   the methodological half of the concern at the JSON layer, before any
   reader downloads the data.
3. If Phase 8 legal review concludes that verbatim refusal text creates
   an unacceptable provider-T&C risk, the redaction can be added to
   `cdb_publish/sanitize.py`, the build re-run, and the published JSON
   updated without changing the schema or the consumer contract.

**Items Mark should weigh in on before Phase 8 (not before T9 Coder
dispatch):**

- Whether the §5.1 `framing_note` field — which is added by this verdict
  on top of the Architect's plan — should be reflected in the kickoff or
  in a one-line architecture note. The CDA SME's reading is that it is
  small enough to live inside the T9 implementation and the T10
  consumer contract; the Architect can decide whether a separate doc
  surface is warranted.
- Whether the §5.4 narrowed regex is the right defensive choice or
  whether Mark wants a broader pattern at the cost of false-positive
  noise in the redaction.
- The Phase 8 legal review's scope — at minimum it should cover
  (a) provider T&C compliance for verbatim refusal-text publication,
  (b) the EU/CCPA/copyright posture on model-generated text in the
  open data bundle, (c) the CC-BY-4.0 licensing of failure records as
  a derived work (the canonical successful-session records are CC-BY-4.0
  per CC-BY licensing of `informants.jsonl`; the failure records likely
  inherit that posture but the Phase 8 review should confirm).

**Coder dispatch may proceed on this verdict.**

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply:** §5.1 (framing_note field), §5.2 (DATA_DICTIONARY.md anti-attribution sentence + module docstring duplicate), §5.3 (sanitize.py docstring §1.5 scan), §5.4 (narrowed sk- regex), §5.5 (DATA_DICTIONARY.md provider-quote advisory)
- **Architect must update:** T10 plan's data-contract section to require T10 consumes the `framing_note` field per §5.1
- **`cdb_core/schemas.py` change required:** No
- **T14 doc-sweep flag raised:** No (on the enum); Yes for the methodology page to include a "failures-as-findings" section that the §5.1 framing_note references
- **Mark escalation:** §6 advisory only, non-blocking for Coder dispatch

---

*End of Phase 6 T9 CDA SME verdict.*
