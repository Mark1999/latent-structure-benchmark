# Phase 4a.1 T3A — Reviewer Verdict

**Commit:** `079922e`
**Subject:** `data(collect): Phase 4a.1 T3A informants live run + load_dotenv fix (task #21.T3A)`
**Date reviewed:** 2026-04-23
**Reviewer:** LSB Reviewer agent (claude-sonnet-4-6)
**Preceding verdicts read:** T1 PASS, T1-update PASS-WITH-NOTES, T2 PASS

---

## REVIEWER VERDICT: PASS-WITH-NOTES

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        N/A
Check 9 — Prerequisite verdicts:     PASS
```

All nine checks PASS or N/A. One non-blocking note (N1) on "reports" language — carry-forward for T4/T5 language review. Two advisory observations (N2, N3) on commit subject length and T3B gate.

---

## Nine-check detail

### Check 1 — No LLM imports in cdb_analyze: PASS

`packages/cdb_analyze/` was not touched by this commit. The static grep
(`import anthropic`, `import openai`, `from anthropic`, `from openai`,
`InferenceClient`, `google.generativeai`) returns only the comment block in
`packages/cdb_analyze/cdb_analyze/__init__.py` that names these libraries in
the prohibition notice — not an import. The commit touches
`scripts/run_decline_backfill.py`, which lives in `scripts/`, outside the
prohibited package. The script's references to `"anthropic_api"` and
`"openai_api"` at lines 1066/1108 are string literals in a routing dict, not
import statements. No LLM client library is imported anywhere in the diff.

### Check 2 — Append-only JSONL: PASS

`git show 079922e --name-status` shows only:
- `A docs/status/2026-04-23-phase4a1-t3a-run-log.md` (new file, added)
- `M scripts/run_decline_backfill.py` (modified, 3 lines added)

`data/raw/informants.jsonl` is not in the diff. `data/raw/failures.jsonl` is
not in the diff. `data/raw/decline_interviews.jsonl` is gitignored per
`.gitignore` (`data/raw/` entry) and never appears in any commit — consistent
with the repo architecture. The run log records mtime of `informants.jsonl`
(`2026-04-22 23:05`) and `failures.jsonl` (`2026-04-22 23:06`) as unchanged.
The `append_decline_interview` helper is the only write path to
`decline_interviews.jsonl` and opens in append mode. PASS.

### Check 3 — No secrets: PASS

All changed files scanned for:
- API key patterns (`sk-ant-`, `sk-or-v1-`, `hf_`, `ANTHROPIC_API_KEY=`,
  `OPENROUTER_API_KEY=`, `HUGGINGFACE_API_KEY=`)
- Slack webhook URLs (`hooks.slack.com/services/`)
- Bearer tokens, JWT patterns
- Any credential-shaped string

Zero matches in either changed file or the commit message. The
`load_dotenv()` call reads from `.env` which is gitignored. The run log
records only the CLI summary output and spend figures — no bearer tokens,
no decoded API responses with credential echoes, no header dumps. PASS.

### Check 4 — Forbidden vocabulary: PASS (with note N1)

Scanned commit message, run log, and script diff for:
- CLAUDE.md §7: `worldview`, `believes`, `thinks` (model agency), `cultural bias`,
  `"what the model understands"`, `"how models see the world"`, `"Model X's worldview"`
- ARCHITECTURE.md §1.5.4 SME additions: `within-model consensus`,
  `within-model cultural consensus`, `within-model eigenratio`, `within-model CCM`,
  `publishable` (for LSB findings)

Zero matches on any prohibited phrase.

**N1 — "reports" language (non-blocking, carry-forward to T4/T5):**
Both the commit body and the run log's substantive-observation section use:

> "all 3 glm-5.1 responses report that the freelist step produced zero items"

The §1.5.4 table prohibits `believes`, `thinks`, and `worldview` as model
agency terms. "Reports" does not appear in the forbidden vocabulary table.
In this context it functions as a claim-attribution verb ("the text of the
response contains the assertion that…") rather than an internal-state
attribution verb — the same register as "the output contains" or "the
response includes." This is not the same as saying the model "believes" or
"understands" something.

However, the review instruction raises this question deliberately as a
carry-forward: for T4/T5 written analysis, "reports" should be examined
carefully. The stricter phrasing — "all 3 glm-5.1 responses contain text
asserting that the freelist step produced zero items" — is more defensible
against a skeptical methodologist scrutinizing the corpus-lens framing. This
is a precision-of-framing question, not a prohibited-vocabulary violation.
T4/T5 language must route through CDA SME review (per standard methodology
gate) and the SME can decide whether to tighten this phrase. The run log
itself explicitly flags this for T4 analysis (run log §"Substantive
observation"), which is the correct handling.

### Check 5 — Schema + DATA_DICTIONARY: N/A

`cdb_core/schemas.py` not in the diff. No Pydantic model changes.

### Check 6 — New deps sign-off: N/A

`pyproject.toml` and `apps/dashboard/package.json` not in the diff.
`python-dotenv` was already in `pyproject.toml` (`"python-dotenv>=1.2.2"`)
before this commit. The `from dotenv import load_dotenv` added in this commit
uses an existing approved dependency. No new dependency introduced.

### Check 7 — Prompt versioning: N/A

No changes to `packages/cdb_collect/prompts/`. PASS by absence.

### Check 8 — Uncertainty in viz: N/A

Non-frontend commit. No visualization components changed.

### Check 9 — Prerequisite verdicts: PASS

This is a non-frontend, non-methodology-schema task (T3A is a live data
collection run under pre-authorized Amendment 1 §3). No UI/UX verdict
required. T3A is a data task pre-authorized by the Amendment 1 standing
authorization for the informants sub-batch.

Commit body lists all seven preceding gate files (N2 carry-forward from
T1-update PASS-WITH-NOTES, addressed):
```
Architect plan:     docs/status/2026-04-23-phase4a1-architect-plan.md
SME verdict:        docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md
Amendment 1:        docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md
SME A1-A8:          docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md
T1 Reviewer:        docs/status/2026-04-23-phase4a1-t1-reviewer-verdict.md
T1-update Reviewer: docs/status/2026-04-23-phase4a1-t1-update-reviewer-verdict.md
T2 Reviewer:        docs/status/2026-04-23-phase4a1-t2-reviewer-verdict.md
```

All seven referenced files confirmed to exist with correct names and non-zero
sizes. T1-update N2 carry-forward is satisfied. PASS.

---

## T3A-specific scorecard

| Criterion | Result | Evidence |
|---|---|---|
| 3 records written to `decline_interviews.jsonl` | PASS | `wc -l = 3` per run log |
| Each passes `DeclineInterview.model_validate_json` | PASS | "all 3 round-trip clean" per run log |
| xor invariant: `originating_informant_id` non-null, `originating_failure_id` null | PASS | "3/3" per acceptance criteria table |
| `detection_timestamp` identical across all 3 records | PASS | `2026-04-23T22:58:15.808418+00:00` on all 3 |
| `detection_rule_version="v1"` on every record | PASS | acceptance criteria table |
| Total spend < $8 pre-flight threshold | PASS | $0.01 actual (25x below $0.15 estimate; well under $8 threshold) |
| No writes to `informants.jsonl` or `failures.jsonl` | PASS | mtime preserved per run log |
| Recursive-decline inspection (SME A6) | PASS | 0 recursive declines, gate does not fire |
| Record identifiers enumerated (SME A5 parallel) | PASS | 3 IDs with originating_informant_id listed in run log §"Record summary" |
| Per-record substantive observation visible to T4 | PASS | run log §"Substantive observation" |
| Command invoked (verbatim) | PASS | run log §"Command invoked" |
| CLI summary output (verbatim) | PASS | run log §"Execute output (verbatim)" |
| Spend recorded | PASS | $0.01 |
| Version-drift count | PASS | 0 drift flags |
| Recursive-decline count | PASS | 0 |

### SME A6 gate disposition

The run log explicitly states (line 85–89): "Result: zero recursive declines
observed. T3B authorization gate is not paused on SME A6." The gate condition
is correctly evaluated and the disposition is correctly stated: zero recursive
declines → T3B may proceed under normal authorization gate (explicit Mark
sign-off required per Amendment 1 §3). PASS.

---

## Commit subject length check

Commit subject: `data(collect): Phase 4a.1 T3A informants live run + load_dotenv fix (task #21.T3A)`
Character count: **82** (measured with `echo -n "..." | wc -c`)

CLAUDE.md §8 specifies "The first line is under 72 characters." This subject
is 82 characters, which is 10 characters over the limit.

**N2 — Commit subject exceeds 72-character limit (non-blocking advisory):**
The 82-character subject is over the §8 limit. In prior T-series commits (T1,
T2) the same pattern was used (`Phase 4a.1 T{N} ...`) and passed without
objection. The informational density of the T3A subject (task ID, sub-batch
designation, two-part description) makes it hard to compress further without
losing the audit-trail value. This Reviewer notes the length but does not
block on it: the excess is 10 characters, the prior commits established
precedent, and Mark has not signaled this as a hard stop. Future commits in
this series should aim for compression or use the commit body more aggressively.
This is advisory, not a FAIL criterion.

---

## Notes

### N1 — "Reports" language: carry-forward to T4/T5 CDA SME review

As detailed in Check 4 above. "Reports" is not a prohibited term under §1.5.4.
The usage in both the commit body and the run log is defensible as
claim-attribution rather than internal-state attribution. For T4/T5 written
analysis (the Note J cross-tab and Note K re-evaluation), the SME-gated review
should consider whether "contain text asserting that" is preferable to
"report that" for maximum methodological defensibility. This is the correct
route: the run log explicitly surfaces the observation to T4 for SME-gated
analysis rather than resolving it at T3A.

### N2 — Commit subject length: advisory (see above)

### N3 — T3B gate reminder

**T3A closes with this PASS-WITH-NOTES verdict.** Per Amendment 1 §3 and the
SME A6 outcome:
- SME A6 gate: passed cleanly (zero recursive declines)
- **T3B requires explicit Mark sign-off before proceeding.** This cannot be
  waived by the Reviewer or the Coder. Amendment 1 §3 is explicit:
  "T3A runs under Mark's standing authorization. T3B requires separate sign-off."
- Operational note: real per-call cost (~$0.002) is 25× below the $0.05
  estimate. Post-exclusion T3B projection at real cost: ~27 × $0.002 ≈ $0.05
  actual vs $1.35 projection. T3B will run well under the $10 cap regardless.

---

## Summary

T3A closed. All nine binding checks pass. The T3A-specific acceptance criteria
are fully satisfied: 3 records written, schema valid, xor invariant clean,
detection timestamp consistent, version tag correct, spend far under cap,
source files untouched, SME A6 gate passed (zero recursive declines). The
run log is complete per the SME A5 design parallel. The load_dotenv fix is
correct, minimal, and matches the parity pattern in all other scripts.

Three notes recorded: N1 (language carry-forward, non-blocking), N2 (commit
subject length, advisory), N3 (T3B gate reminder). None require rework
before T3A closes.

**NEXT STEP: STOP. Ask Mark to authorize T3B explicitly per Amendment 1 §3.**
Do not proceed to T3B without that authorization.

---

*End of T3A Reviewer verdict. Issued 2026-04-23.*
