# SUPERSEDED — May 1 hand-coding artifact

**File:** `decline_interviews_safety_attribution_subtype.jsonl` (this directory)
**Status:** SUPERSEDED 2026-05-05 — content is non-authoritative
**Reason:** the artifact was hand-coded under a now-falsified premise.

The May 1 hand-coding classified 9 decline-interview rows as `safety_event_attribution`
subtype (`k_frame` / `k_vocab_without_k_frame`), with the implicit understanding that
those rows were first-order evidence that the originating Phase 4a failures were
safety-policy events. The 2026-05-04 max_tokens finding (commits `d06e64c`, `19d67f1`,
`bef7660`, and the recovery campaign at commit `3634e52`) reframed those originating
failures as instrument-event artifacts (`max_output_tokens=4096` exhaustion). The
model's self-reports of "internal safety protocols" in the decline interviews are now
best understood as confabulation patterns: the model's output narratives attributed
failure to safety mechanisms under conditions in which the actual mechanical cause of
the empty output was not surfaced in the inputs available to the model at
decline-interview time.

**What this means in practice:**

- The JSONL itself is preserved on disk and in git history (audit trail).
- The hand-coded `k_frame` / `k_vocab_without_k_frame` subtype classifications are
  **non-authoritative** for any analytical purpose under the post-2026-05-05 framing.
- The successor artifact is the RD-2 hand-coding under the `safety_attribution_confabulation`
  framing (not yet produced at this commit).
- The successor analytical artifact is the RD-3 reframing memo at
  `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (not yet produced at
  this commit).

**What this is NOT:**

- This is not a deletion. The audit trail is preserved.
- This is not a destructive edit. The original JSONL is unmodified.
- This is not a methodological retraction of the *measurements* taken on May 1 —
  Mark's hand-coded classifications correctly describe what the decline-interview text
  says. What is superseded is the *interpretation* of those classifications as
  safety-event evidence.

**See:**

- `docs/status/2026-05-05-t4-redo-architect-plan.md` (the reframing plan for this
  artifact)
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (binding notes T1–T7; Q1
  sign-off; SME PASS-WITH-NOTES)
- `docs/status/2026-05-05-phase4a-recovery-report.md` (the recovery campaign whose
  findings reframe this artifact)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5 — the originating gate
  binding this reframe)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (the original T4 SME
  verdict that endorsed the May 1 methodology)
- Mark's sign-off on Q1 (mark-as-superseded, not delete) recorded 2026-05-05.

**Convention note:** the sibling `.SUPERSEDED.md` annotation pattern (new file
alongside the artifact, no destructive edits to the JSONL) is the project's
operational practice for marking superseded `data/derived/` artifacts. It is not
codified as a CLAUDE.md §9 pitfall; it is applied verdict-by-verdict. See SME verdict
T7 for the explicit ruling.
