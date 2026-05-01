---
name: Phase 4a.1 Amendment 4 PASS
description: Amendment 4 small focused fix for stale D20 cross-provider wording — resolved with PASS. T4.2-followup unblocks immediately. 31 binding notes unchanged.
type: project
---

Amendment 4 issued 2026-05-01 to resolve T4 SME Required items (stale D20 mechanism string, defensive-guardrail asymmetry, §3.3 §1.5-clean rephrase canonicalization). Verdict: **PASS** at `/opt/lsb-agent/docs/status/2026-05-01-phase4a1-amendment-4-cda-sme-verdict.md`.

**Why:** T4 output gate found D20's "cross-provider replication" phrase factually wrong (cohort is single-provider Google). Amendment 4 templates provider name from `distinct_providers[0]`, binds conditional wording on `n_providers`, picks option (b) for guardrail symmetry, canonicalizes "not a claim about the model's internal state".

**How to apply:**
- Coder unblocks T4.2-followup immediately on this PASS — no further SME gate before the commit.
- D26 commit-bundling shape: Required #2 + Required #3 in one Coder commit (same render-branch code path; splitting has no review value).
- Regenerated T4.2 markdown does NOT need a fresh SME output review — Reviewer/Tester catch any regression; next SME gate is T5 output review.
- T5 §8.2 unblocks after T4.2-followup lands + Reviewer/Tester PASS.
- T5 §1, §8.1, §8.3, §8.4 already unblocked from T4 verdict; parallel work permitted.
- Carry-forward: 31 binding notes unchanged. No new notes added by this verdict.
- D17–D22 NOT re-opened. No schema changes. No DATA_DICTIONARY.md updates.
- Phase 4a.1 closes at T5; no Amendment 5 anticipated.

**Key methodological move:** when SME flags an Axis 3 falsifiability issue caused by data-refining-prediction, the right shape is a focused amendment that (a) revises the static wording AND (b) makes the script branch on the relevant predicate so future cohorts auto-route correctly. Architect upgraded my "optional but preferred" branch logic to binding — correct call to avoid a future Amendment 5 the moment a multi-provider safety cohort surfaces.
