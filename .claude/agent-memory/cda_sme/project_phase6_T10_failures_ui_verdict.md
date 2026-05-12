---
name: project-phase6-T10-failures-ui-verdict
description: 2026-05-12 T10 failures-as-findings UI surface verdict — PASS-WITH-NOTES; S1 removes 120-char summary-row preview (quotation pump); S2 rewords no-records caption; S4 renames badge "Decline follow-up"→"Follow-up interview" and block "Model response"→"Model output"; H2 sibling APPROVED; enum verbatim in mono APPROVED; T14 wires methodology-page links
metadata:
  type: project
---

**Fact:** Phase 6 T10 (FailuresFindingsSection UI surface) CDA SME verdict
issued 2026-05-12 as PASS-WITH-NOTES at
`/opt/lsb-agent/docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md`.

**Why:** T10 is the UI consumer of T9's published failures JSON. T9's
verdict §5.1 established the binding `framing_note` field; T10 must
consume it verbatim with byte-identity regression assertion. T10 introduces
substantial LSB-authored prose surface (section heading, badge labels,
empty-state caption, expanded-view block labels) that needs four-axis
review — distinct from T9's data-layer concern.

**How to apply:**
- Seven binding S-notes (S1–S7) carry forward to Coder dispatch.
- **S1 is the load-bearing change:** the Architect's 120-char
  `response_verbatim`/`error_message` preview in the always-visible
  summary row is rejected as a quotation-pump hazard (a partial-bytes
  preview adjacent to a `model_id` is liftable as a quote with LSB as
  implicit source; the `framing_note` paragraph cannot follow the bytes
  downstream). Replaced with field-shape metadata: `"error_message: {N}
  chars"` for failures, enum-value-only for decline_interviews.
- **S2:** No-records caption rewritten to first-class-state framing
  ("This domain's collection run produced no failure records... The
  absence is itself an observation about how this set of models
  responded to this domain's elicitation prompts."). Removes "are
  published for this domain in this analysis version" (passive +
  temporariness).
- **S4a:** badge label `"Decline follow-up"` → `"Follow-up interview"`
  (disambiguates noun "decline" — was readable as model state).
- **S4b:** expanded-view block label `"Model response"` → `"Model
  output"` (names the artifact, not the state); add " to the follow-up
  prompt" qualifier on decline_interview records.
- **S5:** Explicit `aria-label` on every `<summary>` per templates;
  no implicit name computation from row text.
- **S3 + S7 raise T14 doc-sweep flags** for methodology-page link
  wiring (from "Outcome class" block label and from `framing_note`
  paragraph's "See the methodology page" prose). T10 does not wire
  these — links are plain text until T14 ships.
- **H2 sibling heading hierarchy APPROVED** (Architect's proposal):
  failures are first-class evidence parallel to MethodologySummary's
  "About this measurement" — not subordinate methodology context.
- **Enum verbatim in mono font APPROVED** (Architect's proposal): the
  enum value forces careful reading by being slightly unfamiliar; a
  human-readable expansion would invite the state-of-mind reading
  ("model output matched a refusal phrase" reads as "the model emitted
  a refusal"). Mono-font signals "data identifier, not prose."
- **Decline-interview paired-record ordering APPROVED:** basic identity
  → follow-up prompt LSB sent → model output → reasoning trace →
  provenance. Cross-record visual pairing (linking a decline-interview
  record back to its originating failure) is out of scope for T10;
  `originating_failure_id` in provenance block is the textual bridge.
- No Mark escalation. UI/UX dispatch next; Coder dispatch on UI/UX
  PASS.

**Related memories:**
- [[project_phase6_T9_failures_publish_verdict]] — T9 data-layer verdict
  whose §5.1 framing_note binding T10 consumes verbatim.
- [[project_failures_are_findings]] — 2026-04-23 directive grounding the
  whole T9/T10 thread.

**Pattern note (for future SME reviews of UI consumers of T9-like data
layers):** when a UI surface displays verbatim model output adjacent to
model identity (model_id), audit the surface for "quotation pump"
hazards — partial-bytes previews that can be lifted as quotes with the
platform as implicit source. The §1.5.4 attribution framing in the
ambient prose layer (T9 framing_note, methodology page) cannot follow
the bytes into downstream quotation contexts; the UI must keep verbatim
bytes behind a deliberate inspection action (`<details>` open, click to
expand) so the reader's cognitive posture aligns with the bytes they
are reading.
