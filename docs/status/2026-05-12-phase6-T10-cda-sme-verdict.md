---
filed: 2026-05-12
reviewer: CDA SME agent (Opus)
task: Phase 6 T10 — Failures-as-findings UI surface (`FailuresFindingsSection`)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 6 T10 — CDA SME verdict on the failures-as-findings UI surface plan

**VERDICT: PASS-WITH-NOTES**

The Architect's plan is approved with binding wording fixes on three of the
seven explicit binding questions the orchestrator routed (section heading,
no-records caption, accordion mechanism / labels), plus a binding revision
of the truncated-preview policy (the §10 risk 2 candidate), plus three
carry-forward notes affecting expanded-view block labels, the ARIA-label
surface, and `originating_outcome_class` rendering.

The §2.4 `framing_note` verbatim consumption — including byte-identical
regression assertion (acceptance criterion 3) — correctly honors the T9
verdict §5.1 binding. The defensive missing-`framing_note` and
fetch-failed cases are correctly first-class-state-framed (no
"pending"/"missing"/"placeholder" language reaching the reader). The H2
sibling heading hierarchy is approved as proposed. The `<details>` /
`<summary>` native-element decision is approved as proposed. The Architect's
inspect-mode extension (§2.8) is approved as proposed (operator surface;
honors `feedback_inspection.md`).

The truncated-preview policy in §2.4 (120 chars of `response_verbatim` /
`error_message` in the always-visible summary row) is **revised** under
S1 below: a 120-character preview of refusal-text or error-text in a
collapsed-by-default row is a quote-out-of-context hazard precisely of
the kind T9 §5.1's `framing_note` is meant to defend against, and the
mitigation (the framing_note paragraph) is several scroll-lines above the
summary row when a reader scans. The summary row must instead surface
**field-shape metadata** (field name + length), not bytes; verbatim bytes
appear only after the reader expands `<details>`. This is the same
"quotation pump" §1.5.4 hazard the T9 verdict §5.5 advisory anticipated
("attribute quotes to the model output, not to model intent") — moved
from JSON consumer to UI consumer.

T10 proceeds to UI/UX dispatch (light-touch per `feedback_ui_polish_scope.md`)
on this verdict. Coder dispatch follows on UI/UX PASS / PASS-WITH-NOTES.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | The UI's representation is faithful to the CDA-protocol output it surfaces. The two record types (`"failure"` = LSB pipeline could not produce a parseable primary-step response; `"decline_interview"` = LSB's follow-up structured elicitation about a prior decline) are both first-class protocol artifacts per the 2026-04-23 directive, and the §2.4 rendering preserves the full audit trail (model_id distinct from model_version_returned per CLAUDE.md §9 pitfall #1; sha256_manifest; prompt_verbatim of the decline-interview prompt). The paired-record decline-interview layout (§2.4 expanded view ordering: original failure context first, follow-up Q+A below) is the correct representation of the two-step protocol — see §3.7. The `<pre>` block preservation of verbatim bytes (no markdown, no syntax highlighting, no HTML transformation) is the correct fidelity floor. |
| Analytical validity | PASS | A reader can reproduce the "failures-as-findings" claim from what is rendered: the summary row (after S1 revision) names the record type + model + collection date; the expanded view exposes every published field including `sha256_manifest` for byte-identity verification against the source `data/raw/decline_interviews.jsonl`. The `?inspect=failures-{slug}` mode (§2.8) provides the operator-surface table view per `feedback_inspection.md`. The decision to render `originating_outcome_class` verbatim from the schema enum (no LSB-authored translation layer) preserves the T9 §3 per-value compliance reasoning at the UI surface. |
| Claims validity | PASS-WITH-NOTES | Two sub-findings: (i) the truncated-preview policy as proposed (120-char `response_verbatim` slice in the always-visible summary row) creates an out-of-context partial-quotation hazard that **the framing_note paragraph cannot fully counteract** because a screen-reader user or a quick visual scanner will encounter the partial bytes adjacent to a `model_id` without the framing in their working memory. Mitigation S1 below replaces the verbatim slice with field-shape metadata. (ii) The "Outcome class" block label in the expanded view (§2.4 expanded-view table row 7) inherits T9 §5.2's documentation requirement — see S3 below. |
| Audience translation | PASS-WITH-NOTES | The three target audiences (journalist, AI engineer, curious general reader) navigate without misinterpreting **once S1 is applied**. As proposed, the journalist scanning the section would read a 120-char preview that reads like a quote and can be lifted as one ("GPT-4: 'I cannot assist with that…'" — a §1.5.4 attribution violation supported by a literal text artifact LSB published). After S1, the journalist sees `"response_verbatim, 312 chars"` and must expand to read the bytes — at which point the `<details>` open action is a deliberate act of inspection that puts the reader in the right cognitive posture. The decline-interview layout (§3.7) makes the two-step protocol intelligible to all three audiences without needing to read T9's plan. |

Register compliance: **PASS** — T10 is a UI rendering of T9's publish-layer
output. It does not perform Register 1, 2, or 3 analysis. No OCI, no
Romney CCM, no Procrustes is surfaced. Failure records carry no point
estimate; the R10 "uncertainty on every point estimate" rule is correctly
flagged N/A by both the Architect (§6 axis 8) and the orchestrator.

Vocabulary compliance: **PASS-WITH-NOTES** — the Architect's §2.5
LSB-authored prose surface is approved with binding wording revisions on
three strings (S1, S2, S4 below) and one block-label tightening (S3). No
forbidden vocabulary (`worldview`, `believes`, `thinks`-applied-to-models,
"refuses" in LSB-authored captions, "missing"/"pending"/"placeholder"
framing) appears in the Architect's proposed strings — the empty-state
caption is correctly first-class-state framed; the heading does not
psychologize. The S2 revision tightens the empty-state caption further
and the S4 revision tightens the badge labels.

---

## 2. Binding answers to the orchestrator's seven explicit questions

### 2.1. Section heading text

**Architect proposed:** `"Collection records and follow-up interviews"`

**CDA SME binding wording: `"Collection records and follow-up interviews"`** — **APPROVED as proposed.**

Rationale: technical/descriptive, parallel to MethodologySummary's "About
this measurement" register, names what the section *contains* (records of
LSB collection sessions + follow-up interviews), not what the section
*proves* or *claims*. No psychological-attribution language, no
"refusals," no "failures" in the heading (the word "failure" appears in
the badge label below, where it is a positively reclaimed pipeline-state
term per the 2026-04-23 directive). The heading title-cases nothing; the
ampersand is not introduced; the conjunction is "and."

Coder regression-test: the rendered `<h2 id="failures-findings-heading">`
text content equals the string `"Collection records and follow-up interviews"`
byte-for-byte.

### 2.2. Accordion labels

**Architect proposed:** native `<details>`/`<summary>` with no explicit
"expand" label (browser disclosure triangle is the affordance) plus a
summary row whose composition becomes the de facto accordion label.

**CDA SME binding wording:** No LSB-authored "expand" / "click to expand" /
"show details" / "view full response" / "show raw model output" string is
introduced. The native `<details>` element with the browser disclosure
triangle is the affordance. This is **§1.5-clean by construction** — the
forbidden framings ("View full response" implies the model "responded";
"Show raw model output" is acceptable but redundant with the badge label;
"Expand details" is acceptable but unnecessary given the native element)
are all avoided by emitting no LSB-authored disclosure prose at all.

This is the §2.6 decision, and it is correct.

**However**, the ARIA-label surface is a separate concern (carry-forward
note S5 below). The `<summary>` element's *accessible name* is what
screen readers announce, and that name is computed from the summary
row's text content — which under the Architect's §2.4 plan includes a
120-char `response_verbatim` preview. After S1's revision, the summary
row's accessible name will be `"{badge} {model_id} {collection_date}
{field-shape metadata}"` — entirely LSB-authored and §1.5.4-clean.

### 2.3. No-records caption

**Architect proposed:** `"No collection failures or follow-up interviews are published for this domain in this analysis version."`

**CDA SME binding wording (S2):** **`"This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."`**

Rationale for the revision:

1. The Architect's proposed caption is §1.5.4-compliant (no
   "pending"/"missing"/"yet") and is acceptable, but it leaves the reader
   in a passive state ("are published for") that subtly implies a publisher
   choice rather than a property of the collection run. The revision
   reframes the no-records state as a *positive observation* about the
   collection run, not a property of LSB's publication policy.

2. The orchestrator's prompt explicitly flagged: "AVOID 'no failures yet'
   or 'no refusals found' framing — those imply temporariness or
   absence-as-defect. The no-records state is itself information (this
   domain didn't surface failures), not a placeholder." The revised
   wording explicitly names the absence as information.

3. The phrase "this analysis version" is removed because it implies a
   future analysis version might produce records — a temporariness
   framing the orchestrator asked to avoid. Each publication is a frozen
   record of one collection run; the absence is a property of that run.

4. The second sentence is the §1.5-framing the empty case needs *in
   addition to* the `framing_note` paragraph, because the framing_note
   discusses what records *are when present*; the empty case needs its
   own framing of what the absence *means*.

Coder regression-test: the rendered no-records `<p>` text content equals
the binding string above byte-for-byte.

### 2.4. Heading hierarchy — H2 vs H3

**Architect proposed:** `<h2>` sibling of MethodologySummary's `<h2>`.

**CDA SME binding decision: `<h2>` sibling.** — **APPROVED as proposed.**

Rationale from a CDA-methodology / claims-validity standpoint:

1. **Failures-as-findings are first-class observations, not subordinate
   methodology context.** The 2026-04-23 directive
   (`project_failures_are_findings.md`) is unambiguous: failures are
   findings, not a debug log. Nesting them under "About this measurement"
   as an H3 would semantically subordinate the records to the
   methodology summary, which inverts the directive. The failures are
   *evidence* (parallel to the successful-session evidence the DataExplorer
   surfaces); the methodology summary is *context for the evidence*.

2. **A11y heading-outline reasoning.** A screen-reader user navigating
   the article-bottom area should encounter two peer evidentiary blocks:
   "About this measurement" (LSB's methodology summary) and "Collection
   records and follow-up interviews" (verbatim outputs LSB collected).
   Both are evidence-class content. Nesting one under the other would
   imply asymmetric authority.

3. **The Architect's §2.3 reasoning is concurred.** The failures section
   is not semantically *about* methodology — it is a parallel evidence
   block. H2 sibling is the correct hierarchy.

### 2.5. Record summary preview truncation ellipsis

**Becomes moot under S1 below** — the truncated `response_verbatim` /
`error_message` preview is *removed* from the summary row entirely. There
is no LSB-authored ellipsis in the summary row after S1.

**For the expanded view**, the `<pre>` blocks render verbatim content
verbatim — no truncation, no LSB-authored ellipsis, content wraps via
`white-space: pre-wrap; word-break: break-word`. The reader sees the
exact bytes the model produced.

**Carry-forward (S5 below) advisory:** if any future Phase 6+ feature
re-introduces a truncated preview anywhere in this section (e.g., a
mobile-narrow viewport summary, an inspect-mode preview, a hover
tooltip), the truncation marker must be `"…"` (single Unicode horizontal
ellipsis U+2026, not three dot characters), placed at a sentence boundary
where possible. But: T10 introduces no such surface, so the question is
deferred.

### 2.6. `originating_outcome_class` rendering in summary row

**Architect proposed:** render the enum value verbatim in `--font-family-mono`,
suppressed when null (failure records).

**CDA SME binding decision:** **Render the enum value verbatim** in
`--font-family-mono`. **No tooltip, no human-readable label expansion in
the summary row.** This is the **Architect's proposal — APPROVED.**

Rationale:

1. The T9 verdict §3 per-value compliance reasoning concluded all seven
   enum values are §1.5.4-compliant *as data-identifier surfaces*
   precisely because they name *detection rules*, not model states. A
   human-readable expansion like "refusal_string_match — model output
   matched a known refusal phrase" reads naturally as "the model emitted
   a refusal" (a state-of-mind claim) rather than "the LSB pipeline
   classified the output via a string-matching detector" (the correct
   framing). The verbatim enum **forces the careful reading** by being
   slightly unfamiliar — a reader who wants to know what
   `refusal_string_match` means will look it up, and the lookup target is
   the DATA_DICTIONARY.md entry (T9 §5.2's anti-attribution sentence).

2. The mono-font typesetting visually signals "this is a data identifier,
   not prose" — consistent with how `model_id`, `domain_slug`, and other
   identifiers are typeset throughout the dashboard.

3. **However**, the data dictionary entry behind this rendering carries
   the binding T9 §5.2 anti-attribution sentence, and T14 doc-sweep must
   confirm that linkage is intact when the methodology page ships. See
   carry-forward note S3 below.

**Where the human-readable expansion lives:** the expanded `<details>`
view of each record renders the enum value in the "Outcome class" block
label (§2.4 expanded view row 7). The expanded view is also where a
methodology-page link (T1/T2/T14) will eventually wire to the
DATA_DICTIONARY.md anti-attribution sentence. Today, the verbatim enum
in the expanded view is sufficient; T14 wires the link.

### 2.7. Decline-interview paired-record layout

**Architect proposed:** in the expanded view, render fields ordered as:
(1) basic identity (model, version, collection_date, provider), (2)
"Follow-up prompt LSB sent" (`prompt_verbatim`), (3) "Model response"
(`response_verbatim`), (4) "Reasoning trace" (`thinking_verbatim` when
non-empty), (5) provenance IDs.

**CDA SME decision: APPROVED with one labeling refinement (S4).** The
ordering is correct: the reader sees *what LSB asked* before *what the
model produced*, which is the correct CDA-protocol order (the interviewer
asks; the informant answers). The block label for `prompt_verbatim` —
"Follow-up prompt LSB sent" — is good: it attributes authorship of the
prompt to LSB (not to the model) and names it as a follow-up (linking it
implicitly to the prior decline).

**S4 refinement** sharpens the "Model response" label to **"Model output
to the follow-up prompt"** — the original is grammatically ambiguous about
whether the "response" is a state (the model responded) or an artifact
(the bytes the model produced). The revised label names the artifact
(`Model output`) and the context (`to the follow-up prompt`), avoiding
the state-of-mind reading.

The pairing of the original-failure context with the follow-up Q+A is
**not** a separate rendered block in T10; rather, both records appear
in the same `<ol>` list, sorted by `collection_date` ascending — and a
decline-interview record's `originating_failure_id` field appears in its
"Provenance IDs" block, enabling a reader to find the originating
failure record by ID. The Architect's §2.4 paired-layout is the *content*
ordering inside a single decline-interview's expanded view, not a
cross-record visual pairing. **This is correct** for T10's
minimum-viable surface; a cross-record visual pairing (e.g., "this
follow-up interview originated from failure record X" with an inline
link) is **out of scope** and may be revisited in T14 doc-sweep or
later.

---

## 3. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T10 implementation. The
Reviewer enforces. They do not require re-planning by the Architect.

### S1. **Summary-row truncated-preview policy: replace verbatim bytes with field-shape metadata.** [Claims validity, Audience translation]

**Binding change to §2.4:** the summary row of every `<details>` element
renders, in a single horizontal row:

1. The `record_type` badge (text per §2.5 with the S4 refinement below).
2. The `model_id` in `--font-family-mono`.
3. The `collection_date` truncated to date-only (first 10 chars of ISO string).
4. For `decline_interview` records: the `originating_outcome_class` enum value verbatim in `--font-family-mono`.
5. **NOT** a truncated preview of `response_verbatim` or `error_message`.

The summary row's last visual element is:

- For `decline_interview` records: the enum value (item 4 above) — no
  additional preview.
- For `failure` records: an LSB-authored field-shape descriptor of the
  form **`error_message: {N} chars`** where `N` is `len(error_message)`.
  Rendered in `--color-text-secondary` at `--font-size-xs`, in
  `--font-family-base` (NOT mono — this is LSB-authored prose, not a
  data identifier).

**Rationale.** A 120-char preview of `response_verbatim` in an
always-visible row is a *quotation pump*: it lets a journalist (or a
hostile actor) lift a partial model-output string and present it as a
quote, with LSB as the implicit source. The T9 verdict §5.5 advisory
("attribute quotes to the model output, not to model intent") is
designed for the JSON-consumer case; this S1 revision applies the same
discipline at the UI consumer. The `framing_note` paragraph is the
ambient framing for the section, but it is several scroll-lines above the
summary row when a reader scans; the framing cannot follow the bytes
into a downstream quotation context. Removing the bytes from the summary
row puts the burden of accessing them on a deliberate `<details>` open
action — at which point the reader is in inspection posture, not
scanning posture.

The Architect's §10 risk 2 anticipated this CDA SME flag; the
mitigation chosen here is option (b) from that risk note ("replace with
field-name + length"). The Architect's §10 risk 2 candidate (a) (sentence
boundary truncation) is rejected because it still surfaces verbatim bytes
without expansion; option (c) (remove entirely) is essentially what S1
chooses for `response_verbatim`, with the addition of a field-shape
descriptor that gives the reader a sense of scale (so a 300-char failure
and a 12000-char failure are visually distinguishable in the list).

**Coder regression-test:** snapshot test of `FailureRecord.tsx` rendering
asserts no substring of `response_verbatim` or `error_message` appears
in the rendered `<summary>` element's text content. The full text appears
only inside the `<details>` content after expansion.

### S2. **Empty-state caption verbatim text.** [Audience translation]

The §2.5 `EMPTY_CAPTION` variable in `apps/dashboard/src/copy/failures_findings.ts`
must equal the binding string:

> **`"This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."`**

See §2.3 above for the rationale. Coder regression-test in
`FailuresFindingsSection.test.tsx` asserts byte-identical match against
this string when rendered against a fixture with `records: []`.

### S3. **Expanded-view "Outcome class" block label inherits T9 §5.2 framing.** [Claims validity]

The §2.4 expanded-view block label `"Outcome class"` (for
`originating_outcome_class` on decline_interview records) is approved as
proposed. **Carry-forward**: T14 doc-sweep must wire a methodology-page
link from this label (or from a "?" affordance adjacent to it) to the
section of the methodology page (when it ships at T1/T2) that contains
the T9 §5.2 anti-attribution sentence:

> Each enum value names the LSB-side detection rule that classified
> the record. The enum values do not attribute intent, belief, or
> state-of-mind to the model.

For T10, the label is rendered as plain text; the link is **not**
required at T10. The advisory is registered for T14.

### S4. **`record_type` badge labels — refine `"Decline follow-up"` → `"Follow-up interview"`; refine "Model response" → "Model output".** [Audience translation, Claims validity]

Two refinements to the §2.5 LSB-authored copy surface:

**S4a.** The `RECORD_TYPE_LABEL.decline_interview` badge text changes from
the proposed `"Decline follow-up"` to **`"Follow-up interview"`**.

Rationale: "Decline follow-up" reads naturally as "a follow-up about a
decline" — but "decline" here is a noun ambiguous between "decline" as a
model action (a state-of-mind reading) and "decline" as a classification
of an output. "Follow-up interview" is unambiguous: it names the LSB-side
workflow (an interview that follows the prior collection session), and
the originating context (what prompted the follow-up) is exposed inside
the expanded view via `originating_outcome_class` and the
`originating_failure_id` link in the provenance block.

**S4b.** The §2.4 expanded-view block label for `response_verbatim` on
`decline_interview` records changes from **"Model response"** to **"Model
output to the follow-up prompt"**.

Rationale: see §2.7 above. "Model output" names the artifact; "to the
follow-up prompt" names the context; together they avoid the state-of-mind
reading "the model responded."

For `failure` records' optional `response_verbatim` (when present in
partial-session data), the same label applies: **"Model output"** (the
"to the follow-up prompt" qualifier is omitted because there is no
follow-up prompt context for a top-level failure).

The §2.5 `RECORD_TYPE_LABEL.failure` badge text **`"Collection failure"`**
is approved as proposed (it names the LSB-pipeline outcome, not a model
state; the term "failure" is positively reclaimed per the 2026-04-23
directive).

### S5. **ARIA-label surface and accessible-name scan.** [Audience translation]

The `<summary>` element's accessible name (what screen readers
announce) is computed from the summary row's text content. After S1, this
becomes: `"{badge_label} {model_id} {collection_date} [enum_value | field_shape_descriptor]"`.

The Coder writes an explicit `aria-label` attribute on each `<summary>`
element to make the announcement deterministic across browsers and screen
readers. The `aria-label` template is:

For decline_interview records:
> **`"Follow-up interview record. Model: {model_id}. Collected: {collection_date_human_readable}. Outcome class: {originating_outcome_class}. Press Enter or Space to expand."`**

For failure records:
> **`"Collection failure record. Model: {model_id}. Collected: {collection_date_human_readable}. Error type: {error_type}. Message length: {N} characters. Press Enter or Space to expand."`**

Where `{collection_date_human_readable}` is the ISO date prefix rendered
as "April 22, 2026" via the existing date-formatting utility (or
equivalent — UI/UX may choose a tighter format under the
`feedback_ui_polish_scope.md` minimum-viable posture).

§1.5.4 vocabulary check on these aria-labels: passes — "record,"
"collected," "outcome class," "error type," "message length," "press
enter" are all descriptive/technical. No "refused," "declined" (as a
verb), "thinks," "believes," "intended." The word "Press" is an
imperative to the *user*, not a description of the model.

Coder regression-test: every `<summary>` element has an `aria-label`
attribute. Snapshot test asserts the aria-label values match the
templates.

### S6. **Block label refinements for expanded view §2.4.** [Audience translation]

Two minor refinements to the §2.4 expanded-view block label table beyond
S4b:

- **"Reasoning trace (when provider surfaced it)"** → **"Reasoning trace
  the provider surfaced"** (parallel parenthetical removal; the
  conditional rendering takes care of the "when provider surfaced it"
  case — the label appears only when the field is non-empty). This is a
  minor copy-edit, not a §1.5 concern.

- **"Provenance IDs"** is approved as proposed.

- **All other §2.4 expanded-view block labels** (Model, Model version
  returned, Provider, Collected at, Prompt version, Originating step,
  Outcome class, Error type, Run index, Error message, Follow-up prompt
  LSB sent, Partial session, Retry attempts) are approved as proposed.

### S7. **No methodology-page link rendered at T10.** [Audience translation]

T10's `framing_note` paragraph (T9-emitted) contains the substring "See
the methodology page for the failures-as-findings framing." The
methodology page does not yet exist (T1/T2 are in flight). T10 **does
not** wire this as a hyperlink. The string is rendered as plain prose;
when T14 doc-sweep ships, the link target is established and T14 wires
the anchor. This is the Architect's §5 "out of scope" disposition and is
correct.

**Risk:** a reader today reads "See the methodology page" and finds no
clickable link. Mitigation: this is acceptable for Phase 6 pre-launch.
The Phase 8 launch hardening pass will not ship until both T1/T2 and
T14 have run; the link will be live by public launch.

---

## 4. Vocabulary compliance scan on T10-authored strings

Scanned every LSB-authored string in the plan's §2.5 surface table plus
the strings added/revised by §2 and §3 above:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| `SECTION_HEADING` = `"Collection records and follow-up interviews"` | Technical/descriptive | Compliant |
| `RECORD_TYPE_LABEL.failure` = `"Collection failure"` | Positively reclaimed pipeline state | Compliant |
| `RECORD_TYPE_LABEL.decline_interview` = `"Follow-up interview"` (revised from `"Decline follow-up"` per S4a) | LSB-workflow naming | Compliant |
| `COUNTS_CAPTION_TEMPLATE` = `"{n_records} records published for this domain — {n_failure_records} collection failures and {n_decline_interview_records} follow-up interviews."` | Counts, technical | Compliant |
| `EMPTY_CAPTION` (revised per S2) | First-class state | Compliant |
| `ERROR_FRAMING_MISSING` = `"Collection records are unavailable for this domain."` | Defensive | Compliant |
| `ERROR_FETCH_FAILED` = `"Collection records could not be loaded for this domain."` | Defensive | Compliant |
| Block label "Model" | Data identifier | Compliant |
| Block label "Model version returned" | Data identifier | Compliant |
| Block label "Provider" | Data identifier | Compliant |
| Block label "Collected at" | Technical | Compliant |
| Block label "Prompt version" | Data identifier | Compliant |
| Block label "Originating step" | Pipeline-state descriptor | Compliant |
| Block label "Outcome class" | Detection-rule classifier | Compliant — see S3 |
| Block label "Error type" | Pipeline-state descriptor | Compliant |
| Block label "Run index" | Data identifier | Compliant |
| Block label "Error message" | Field name | Compliant |
| Block label "Follow-up prompt LSB sent" | Attributes prompt to LSB | Compliant |
| Block label "Model output" (revised from "Model response" per S4b) | Names artifact, not state | Compliant |
| Block label "Reasoning trace the provider surfaced" (revised per S6) | Technical | Compliant |
| Block label "Partial session" | Data identifier | Compliant |
| Block label "Retry attempts" | Data identifier | Compliant |
| Block label "Provenance IDs" | Data identifier | Compliant |
| Summary-row field-shape descriptor `"error_message: {N} chars"` (added per S1) | Technical | Compliant |
| `aria-label` template (decline_interview) per S5 | Technical, no attribution | Compliant |
| `aria-label` template (failure) per S5 | Technical, no attribution | Compliant |
| `framing_note` (T9-emitted, verbatim consumed) | Reviewed at T9 verdict §5.1 | Compliant (exempt from re-review) |

No forbidden vocabulary detected across all T10-authored strings.
**PASS** on vocabulary compliance after S1–S6 are applied.

---

## 5. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at dispatch:**
  - S1: replace 120-char summary-row preview with `record_type`-specific field-shape descriptor (`error_message: {N} chars` for failure records; no preview for decline_interview records — enum value already serves as the trailing element).
  - S2: empty-state caption verbatim text per §2.3.
  - S3: "Outcome class" block label is plain text at T10; T14 wires methodology-page link.
  - S4a: badge label `"Decline follow-up"` → `"Follow-up interview"`.
  - S4b: block label `"Model response"` → `"Model output"` (with " to the follow-up prompt" qualifier on decline_interview records only).
  - S5: explicit `aria-label` on every `<summary>` element per templates.
  - S6: minor block-label copy-edit (`"Reasoning trace the provider surfaced"`).
  - S7: no methodology-page hyperlink at T10 (T14 wires).
- **Section heading:** `"Collection records and follow-up interviews"` (Architect's proposal — APPROVED).
- **Accordion labels:** none — native `<details>`/`<summary>` is the affordance; no LSB-authored disclosure prose (APPROVED).
- **No-records caption (verbatim binding):** `"This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."`
- **Heading hierarchy:** **H2 sibling** of MethodologySummary's H2 (APPROVED — failures are first-class evidence, not subordinate methodology).
- **Truncation ellipsis:** moot under S1 (no LSB-authored truncation in T10's surface).
- **`originating_outcome_class` rendering:** verbatim enum in mono font; no tooltip, no human-readable label expansion in summary row; the expanded-view "Outcome class" block label is the explanatory surface; T14 wires methodology-page link (S3).
- **Decline-interview paired layout:** APPROVED — content ordering inside a single decline-interview's expanded view (basic identity → follow-up prompt → model output → reasoning trace → provenance) is the correct CDA-protocol order. Cross-record visual pairing (linking a decline-interview record back to its originating failure record visually) is out of scope for T10; the `originating_failure_id` exposed in the provenance block is the textual bridge.
- **`framing_note` verbatim consumption:** APPROVED — byte-identity regression test per acceptance criterion 3 honors T9 verdict §5.1.
- **Architect must update:** nothing (the §2.5 copy surface revisions are Coder-bound; no plan re-planning required).
- **T14 doc-sweep flag raised:** Yes for the methodology-page link from "Outcome class" block label (S3) and the methodology-page link from `framing_note` paragraph (S7); the link wiring is T14's territory, not T10's.
- **UI/UX dispatch:** T10 proceeds to UI/UX agent (light-touch — accessibility floor + WCAG AA + tokens + mobile per `feedback_ui_polish_scope.md`).
- **Coder dispatch:** follows UI/UX PASS / PASS-WITH-NOTES.
- **Mark escalation:** none required — the S1 truncated-preview revision was anticipated by the Architect's §10 risk 2 and the plan accommodates the revision via the single-file copy module. No load-bearing §1.5 reframing.

---

*End of Phase 6 T10 CDA SME verdict.*
