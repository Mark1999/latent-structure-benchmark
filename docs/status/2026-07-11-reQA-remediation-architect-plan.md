# Plan: promotion-blocking remediation, batch A rebaseline (N15-N19)

**Author:** Architect (persisted by orchestrator; agent has no write access)
**Date:** 2026-07-11
**Owning gate:** CDA SME PASS-WITH-NOTES on the 2026-07-11 addendum in
docs/status/2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md, notes N15-N19 binding.
**Re-review routing:** SME not required (executes binding notes verbatim). No UI/UX
surface. Coder, then Reviewer, then Tester.
**Rule 15 boundary:** no estimator/measure/resampling code touched: partition of
collection QA scope, a mechanical monotonicity count guard, a per-domain slate
allowlist at rebaseline entry, and a version-string bump.
**Append-only boundary:** informants.jsonl untouched; persisted qa_passed/qa_notes
retained verbatim; the slate filter affects basis membership only.
**Precondition:** promotion halt in effect; current out/rebaseline/* staging outputs
are void and are cleared before the re-run.

## Task list

### R1. Partition + reference-set-safe recompute in load_records (N15)
Files: packages/cdb_analyze/cdb_analyze/pipeline.py; scripts/qa_check.py (docstrings only).
qa_check.py: tag check_2 as reference-dependent, Checks 1/3/4/5/6/7/8 as per-record;
module docstring gains a "Partition (CDA SME N15)" paragraph. No behavior change.
load_records: call run_record_checks with a single-record reference set so Check 2's
len(same_runs) < 2 self-guard mechanically disables it (verify against qa_check.py).
Inheritance predicate for persisted-False records: include iff per_record_failures == []
AND not has_check2_signature(qa_notes), where has_check2_signature matches any
";"-split qa_notes segment that fullmatches a bare percentage (Check 2's f.actual is
a percentage; no per-record check writes one; Coder verifies both claims against
runner.py and qa_check.py before relying on them). Persisted-True records: include iff
per-record checks pass now (failures feed R2).
Acceptance: four fixture cases (recover, stay-excluded-on-%-signature,
included-unchanged, excluded-feeding-guard) plus reference-set independence.

### R2. Monotonicity build-guard (N16)
File: pipeline.py. After the recompute loop, count persisted-True records excluded;
if nonzero raise RuntimeError enumerating per-model drops. Recoveries log INFO and
never raise. Acceptance: raises with per-model summary (1 and 2 model cases); silent
at zero drops; recoveries never trigger.

### R3. Approved-slate filter at rebaseline entry (N17)
File: scripts/rebaseline_corpus.py. DOMAIN_CONFIG gains approved_slate frozenset per
domain: published basis keys (data/results/family/0.3.json, holidays/0.3.json,
food/0.2.json cultural_centrality_scores) PLUS the seven batch A additions
(claude-opus-4-8, claude-sonnet-5, openai/gpt-5.5, deepseek/deepseek-v4-pro,
z-ai/glm-5.2, google/gemini-3.5-flash, x-ai/grok-4.3) MINUS claude-fable-5 (SME R1/R2).
qwen/qwen3.6-plus and z-ai/glm-5.1 NOT included; comment marks them pending Mark,
one-line add. Filter records after load_records by model_id membership; empty set is a
no-op; log dropped counts per model. informants.jsonl untouched.

### R4. Version bump (runbook gap)
File: rebaseline_corpus.py DOMAIN_CONFIG: family new_version 0.4 (prior 0.3),
holidays 0.4 (prior 0.3), food 0.3 (prior 0.2). Staging paths become 0.4/0.4/0.3;
no collision with citable published versions; guard still loads prior published.
Commit body notes the runbook Step 3 DOMAIN_CONFIG-bump gap as a separate docs task.

### R5. Tests (fixtures only, no real API calls)
Extend tests/unit/test_pipeline_load_records_recompute.py (R1 predicate cases, R2
guard cases, reference-set independence) and tests/scripts/test_rebaseline_domain_config.py
(slate filter, no-op empty set, new_version 0.4/0.4/0.3, prior_version unchanged).
Refresh any existing tests whose semantics changed.

## Dependency order and commits
R1, R2, R3, R4 in order; tests land with each task. Four commits per CLAUDE.md §8.

## Out of scope
Checks 1-8 arithmetic/thresholds (N1/N2/N8/N9 already landed); persisted-field
mutation; collection-time Check 2 (N19); re-collection; qwen/glm-5.1 slate decisions
(mechanism ready, pending Mark); runbook docs fix.
