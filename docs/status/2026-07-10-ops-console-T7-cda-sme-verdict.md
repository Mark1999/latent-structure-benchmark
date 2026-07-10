# Ops Console T7 (QA modules) CDA SME verdict 2026-07-10

**Verdict: PASS**

Scope: `packages/cdb_social/cdb_social/admin_console/qa/dispatch_templates.py`,
`qa/divergence.py`, `templates/qa.html`. Reviewed against §1.5 vocabulary, N5
records-as-data / rules-as-code framing, and the batch A Fable R4 refusal
vocabulary (relevant if refusal-signature rows ever route through these
templates via T6; T7 as written does not).

## Findings

Dispatch templates present counts and rows as computed facts. Summary block
lists totals; per-model block emits a check-number table; divergence block
carries the boundary label verbatim. No cognition attribution, no "refused" or
"declined" agentic verbs, no editorializing, no "safety" as standalone. No
sentence asks the recipient to rule a particular way; the templates supply
evidence and stop. Rule 15 preserved (recomputation invokes existing
`run_record_checks`, no new math). Rule 14 preserved (no cost text).

The divergence boundary label ("persisted = qa_passed at collection time;
recomputed = current run_record_checks rules") matches the N5 posture
byte-for-byte in both `divergence.py` docstring, `dispatch_templates.py`
`_build_divergence_template`, and `qa.html`. Persisted refers to the stored
`qa_passed` field, recomputed refers to current rules; nothing in the copy
implies the record was mutated. Append-only invariant intact.

No em-dashes in any of the three files.

## Scorecard

Axis 1 (Protocol validity): PASS
Axis 2 (Analytical validity): PASS
Axis 3 (Claims validity): PASS
Axis 4 (Audience translation): PASS
Register compliance: N/A (no register claims in these panels)
Vocabulary compliance: PASS
