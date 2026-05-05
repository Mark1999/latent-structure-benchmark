# SUPERSEDED — T4.2 Note J cross-tab script

**File:** `phase4a1_note_j_crosstab.py` (this directory)
**Status:** SUPERSEDED 2026-05-05 — the script's premise was falsified

## What the script does (still accurate)

`phase4a1_note_j_crosstab.py` implements the T4.2 analysis from the Phase 4a.1
decline-interview backfill. It loads four input files, builds a cross-tab of
`outcome_class × model_origin`, computes the Note K four-tier disposition tree,
and renders Markdown or JSON output. The disposition arithmetic is correct as
applied to the data it consumed. The logic remains in-tree for code-reference value
(the four-tier disposition tree may be reused on Phase 4b data with a corrected
framing).

## Why the script's premise is now falsified

The script's Note K disposition logic (Amendment 2 §3 T4, Amendment 3 §3.2) was
premised on the understanding that the 9 `safety_event_attribution` rows in
`data/derived/decline_interviews_manual_classification.jsonl` were first-order
evidence of safety-policy events in the originating Phase 4a collection run.

The 2026-05-04 max_tokens finding (commits `d06e64c`, `19d67f1`, `bef7660`) and
the 2026-05-05 recovery campaign (commit `3634e52`) demonstrated that the originating
failures were `max_output_tokens=4096` cap-exhaustion events, not safety-policy events.
The model's self-reports of "safety protocols" in the decline interviews are confabulation
patterns: the model's output narratives attributed failure to safety mechanisms under
conditions in which the actual mechanical cause was not surfaced in the inputs available
to the model at decline-interview time. The 100% Gemini recovery rate under the
corrected `max_tokens=16384` configuration confirmed the cap-exhaustion framing.

## Do NOT re-run this script for methodology purposes

The script's input contracts bind it to the original pre-recovery corpus:

- `data/raw/decline_interviews.jsonl` — 24 decline-interview records, of which 9
  originated from Gemini cap-exhaustion events that are now reframed as confabulation
  under blind-spot conditions, not safety events
- `data/raw/informants.jsonl` — the full informant file including the original failure
  records (pre-recovery cells are still present in the file; the recovery added new
  records but did not remove or overwrite the originals)
- `data/derived/decline_interviews_manual_classification.jsonl` — classifications
  that remain valid as descriptions of narrative content but are now reinterpreted
  under the confabulation framing
- `data/derived/decline_interviews_safety_attribution_subtype.jsonl` — **superseded**
  (see sibling `.SUPERSEDED.md` in `data/derived/`)

Re-running the script against the post-recovery corpus would produce output that
mixes recovered informant records with the original failure premise, producing
misleading Note K disposition output. The script must NOT be re-run on any modified
input set without a fresh Architect plan and CDA SME gate.

## What to use instead

The successor framing is:

- `docs/status/2026-05-05-t4-redo-architect-plan.md` — the T4 redo plan
- `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` — the SME ruling (T1–T7)
- RD-2: `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` +
  `data/derived/decline_interviews_confabulation_classification.jsonl` (not yet
  produced at this commit)
- RD-3: `docs/status/2026-05-05-phase4a1-t4-redo-reframing-memo.md` (not yet
  produced at this commit)

## References

- `docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md` §3 T4 (original
  plan; the disposition tree this script implements)
- `docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` §3.2 (Amendment 3
  adding the safety_attribution_subtype column; also superseded)
- `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (the original T4 SME
  verdict that endorsed this script's methodology; preserved as audit)
- `docs/status/2026-05-05-phase4a-recovery-report.md` (the recovery campaign)
- `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (S5; the gate that triggered
  the reframe)
- Mark's sign-off on Q2 (docstring banner + sibling `.SUPERSEDED.md`) recorded
  2026-05-05.
