---
name: Phase 4a recovery PASS-WITH-NOTES
description: 2026-05-05 corpus recovery campaign verdict — 20 cells, R1–R6 binding, S5 confirmed not triggered (gates only future T4-redo)
type: project
---

PASS-WITH-NOTES on `docs/status/2026-05-05-phase4a-recovery-architect-plan.md`.
Q1–Q6 all confirmed Architect's reads. S5 (from Task 16 verdict) confirmed
NOT triggered — adding records to canonical corpus is corpus-modifying, not
corpus-interpreting. T4-redo remains the S5 gate.

R-series binding notes added (R1–R6):
- R1: replace "supersede" with "replace as authoritative for cell" in recovery report
- R2: verbatim final response capture on recovery_failed=true rows (post-v0.1.6 append_failure kwargs)
- R3: recovery report copy framing rules (instrument event, not fix)
- R4: idempotence check uses substring match on qa_notes, not regex with anchors
- R5: build_db.py rerun deferred to separate ops task; recovery report says so explicitly
- R6: if recovery rate < 80%, route back to SME before T4-redo

Verified the 20 in-scope cell recount matches failures.jsonl exactly (Gemini 10 + glm-5.1 6 + llama-maverick 4). Out-of-scope 9 (phi-4 6 + gpt-5.4-mini 2 + mistral-small 1).

**Why:** Recovery is collection-layer modification of canonical corpus; the
pre-Task-16 records and recovered records are both real measurements under
different (corrected) instrument configurations — neither is "better."

**How to apply:** When T4-redo is scoped, S5 still gates it; this verdict's
R-series does NOT extend into T4-redo. Note J / Note K / OCI / CCM are
unaffected by `thoughts_token_count` asymmetry between recovered and legacy
records (none of those measures consume that field).

Total binding-note inventory: B1–B15 (Phase 4a.1, 31 with amendments),
S1–S5 (Task 16), R1–R6 (Phase 4a recovery).
