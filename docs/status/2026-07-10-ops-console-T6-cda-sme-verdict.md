# CDA SME verdict, ops console T6 failure_signatures.py

**Date:** 2026-07-10
**Task:** T6 (Architect plan docs/status/2026-07-10-ops-console-panels123-architect-plan.md)
**File under review:** packages/cdb_social/cdb_social/admin_console/failure_signatures.py (uncommitted)
**Verdict:** PASS

## Findings

**Q1 (pitfall 13, input/output vocabulary separation):** PASS.
The four log-source patterns match HTTP status codes (401, 402, 404), provider
exception class names (AuthenticationError, PileSortParseError), and provider
error strings (credit balance, model not found). None of these tokens can plausibly
appear in an informant free-list, pile-sort, or interview output. The record-source
check reads only `freelist.stop_reason` via exact set membership against
`_REFUSAL_STOP_REASONS = {"refusal", "decline", "content_filter", "safety_filter"}`
(lines 105-107, 133-134). It never touches `response_verbatim` or any narrative
field (grep confirms absent). Exact-set membership on a structured enum, not
substring matching on prose, so the T3B-class miscalibration surface is closed.
The two source types are dispatched on independent code paths inside `scan()`
(log iteration lines 258-275, record dispatch line 278). Compliant.

**Q2 (Fable-5 R4 vocabulary):** PASS.
The label "Refusal streak (3+ consecutive)" and the description text use the
noun "refusal" tied to the LSB-side stop_reason field, matching the R4
load-bearing noun "stop_reason=refusal". No agentic verbs ("the model refused",
"declined"); no "safety" as a standalone noun (only inside `safety_filter` as a
structured enum key). The description explicitly attributes the classifier to
"the runner's decline-detection logic", not to model behavior. Collector-bugs C1
language register preserved.

**Q3 (scope creep):** PASS.
Exactly five entries in `FAILURE_SIGNATURES` (lines 160-211), each matching the
T6 spec ids. Two runtime asserts pin the count and id-uniqueness (lines 214-215).
Docstring and table header both bind "no entries beyond these five without a new
Architect plan". No stealth statistics, no LLM imports, no editorial claims.

## Four-axis scorecard

- Axis 1, Protocol validity: N/A (ops tooling, not elicitation).
- Axis 2, Analytical validity: N/A (no statistics; rule 15 preserved).
- Axis 3, Claims validity: PASS (labels target LSB-side events, not model behavior).
- Axis 4, Audience translation: PASS (label wording R4-compliant; description text
  self-documents the record-source vs log-source split for future reviewers).
- Register compliance: N/A (no cross-register inference).
- Vocabulary compliance: PASS (no §7 or R4 forbidden nouns in any user-visible
  string; enum keys are structured field values, not display copy).

## Follow-up

None. Reviewer/Tester should confirm separately that the runner actually emits
each of the four `_REFUSAL_STOP_REASONS` enum values in production, but that is
a data-truth concern, not an SME concern.
