# v2 free-list prompt — forward-carry suggestion (Mark, 2026-05-06)

**Status:** Forward-carry note. Not actioned. Not in any current task scope.
**Author:** Mark (originating observation), captured by orchestration.
**Origin:** Conversation 2026-05-06, surfaced while reviewing the 9 hand-coded confabulation rows in `data/derived/decline_interviews_confabulation_classification.jsonl` (T4 redo RD-2).
**Disposition:** Park as a Phase 5+ candidate. v1 stays canonical for the current project trajectory.

---

## §1 — The observation

The current v1 free-list prompt at `packages/cdb_collect/cdb_collect/prompts/v1/free_list.md`:

```
You are participating in a cognitive anthropology study. Please list every
{{domain_seed}} you can think of. Do not stop early. Do not explain or
categorize. Just produce a numbered list, one item per line. List as many
as you can, up to 200 items.
```

The hand-coded RD-2 confabulation distribution (9 rows total, all under `max_output_tokens=4096` blind-spot conditions): **4 safety-attribution + 2 task-paradox + 3 mixed + 0 not-confabulation**. 5/9 confabulations carry a "the instruction structure forced my refusal" flavor — informants citing the prompt's own phrasing as the reason for declining. Multiple decline-interview transcripts contain language like *"The instruction to *not* explain or categorize prevented me from mitigating these risks. I couldn't ensure the list was balanced, respectful, or informative."*

Mark's reading: the imperative phrasing ("do not explain or categorize") is not stylistically neutral. It functions as a categorical anchor that some informants treat as itself an explanation-worthy stimulus, producing the very commentary the instruction was meant to suppress.

## §2 — Mark's proposed alternative

> "this is a silent task, please try to avoid interjecting commentary as you make the list"

Softer, request-shaped, frames the constraint as a stylistic preference rather than a prohibition. Hypothesis: lower task-paradox-confabulation rate without sacrificing list quality.

## §3 — Why this is parked, not actioned

Three reasons, in priority order:

1. **CLAUDE.md §6 rule 8 makes this a v2 event, not a v1 patch.** Prompt templates are versioned; in-place edits to v1 are forbidden. A v2 free-list prompt would require its own directory at `packages/cdb_collect/cdb_collect/prompts/v2/` and a comparison-study design.

2. **Cross-comparability cost.** All Phase 4a data — including the 20 cells recovered yesterday at $1.29 — was collected against v1. Switching to v2 mid-project would sever the longitudinal frame. The comparison study would need to *retain* v1 as one arm and add v2 as another arm, not replace it.

3. **The current v1 finding is informative *because* the stimulus is sharp.** The confabulation pattern hand-coded in RD-2 is not a defect in the data; it is a finding about how the prompt design itself becomes a categorical anchor. Smoothing the prompt to suppress the commentary risks throwing out the same signal we are trying to study. This is an explicit instance of the failures-as-findings posture (`memory/project_failures_are_findings.md`) — when an informant cites the instruction structure as their reason, that citation is data.

Mark accepts (1) and (2) for the current project trajectory. He does **not** accept that v1 is therefore the optimal phrasing — only that swapping it now would break more than it would buy.

## §4 — When this should come back on the table

Likely Phase 5 or later. Trigger conditions:

- The corpus has stabilized at v1 across enough domains that the v2 vs v1 contrast becomes a viable comparison study (not a methodology break).
- A planned new domain or new model-slate addition gives a natural surface to introduce a v2 arm without retroactively invalidating v1 cells.
- Architect schedules a "prompt-stimulus sensitivity" sub-study, with the SME concurring that the cross-comparability cost is acceptable.

Mark's note for the Architect: when the v2 sub-study is greenlit, the design **must** keep v1 as a parallel arm (not a replacement) so that the v1 vs v2 *delta* in confabulation rate becomes the finding.

## §5 — Connection to T4-redo RD-3 (the reframing memo)

This observation belongs in RD-3 §4. SME T5 originally conditioned the §4 substantive-content discussion on `not_confabulation` rows; with 0 such rows in the hand-coded set, §4 was going to be skipped. Mark's stimulus-as-anchor observation gives §4 something genuinely worth saying:

> Across 9 hand-coded confabulations, 5 (2 task-paradox + 3 mixed) carry a "the instructions made me do it" flavor. The v1 free-list prompt's imperative phrasing ("do not explain or categorize") appears to function as a categorical anchor that ~5/9 informants under blind-spot conditions treated as itself an explanation-worthy stimulus. Whether this pattern persists under softer phrasing (a v2 prompt comparison study, deferred to Phase 5+) is an open empirical question this corpus cannot answer.

The Coder writing RD-3 should reference this status doc when drafting §4. The wording above is suggestive, not prescriptive — the SME will rule on the final framing during the RD-3 review pass.

## §6 — Audit trail

- Originating exchange: 2026-05-06 conversation, immediately after Mark posted the 9-of-9 hand-coding completion.
- File state at capture: `data/derived/decline_interviews_confabulation_classification.jsonl` is dirty in the working tree (uncommitted), 9/9 classified, distribution as in §1.
- v1 prompt unchanged. v2 directory does not exist.
- This document is the canonical record. Do not capture this suggestion elsewhere.

---

*End of forward-carry note.*
