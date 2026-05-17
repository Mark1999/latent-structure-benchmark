---
name: project-phase7-T2-verdict
description: Phase 7 T2 trigger detectors CDA SME verdict 2026-05-17 — PASS-WITH-NOTES, 7 binding notes, Option B evidence enforcement, DRIFT_THRESHOLD + MIN_DIVERGENCE_DELTA placeholders
metadata:
  type: project
---

Phase 7 T2 (trigger detectors in `cdb_social/triggers.py`) — CDA SME PASS-WITH-NOTES on 2026-05-17.

**7 binding notes (§5.1–§5.7):**
- §5.1 DRIFT_THRESHOLD=0.15 placeholder + DRIFT_MIN_ITEM_INTERSECTION=8 + DriftDataInsufficientError + pre-fire warning log (lockout is data-shaped, not just flag-shaped)
- §5.2 MIN_DIVERGENCE_DELTA=0.02 noise floor; point-mean comparison (NOT CI-overlap hypothesis test — §1.5.7 forbids that frame)
- §5.3 First-run sentinel `bootstrapped_at: datetime` inside state files; file-absence = StateFileMissingError, NOT silent first-run. Explicit `bootstrap_state` function/CLI subcommand for initial install.
- §5.4 detect_monthly_roundup fires first cron run on/after 1st of month at 14:00 UTC; evidence['month'] = previous calendar month (YYYY-MM)
- §5.5 triggers.py module docstring documents dedupe re-fire procedure (cross-ref to T1 schema docstring lines 706–716)
- §5.6 Divergence ∩ new-model: per-domain new-model exclusion algorithm (recompute gap excluding new models, compare against baseline). State baseline updated only when DIVERGENCE fires.
- §5.7 Option B evidence enforcement: `_validate_evidence_for_trigger_type(trigger)` helper in triggers.py + EvidenceContractError. NOT Option A (field_validator — too rigid) or Option C (discriminated union — T1 rewrite).

**Why:** T2 lands trigger detectors as pure functions over published data store. Methodology hazards are (a) unvalidated thresholds, (b) first-run vs state-loss conflation, (c) divergence ∩ new-model double-firing, (d) evidence-payload drift over time.

**How to apply:** When reviewing T2 implementation, T3 drafter prompts (which consume evidence payloads), or future drift-threshold revalidation, anchor on these 7 notes. Carry-forward to T7: DRIFT_THRESHOLD + MIN_DIVERGENCE_DELTA both require empirical-distribution review when real multi-date data lands; ARCHITECTURE.md §4.6 line 1211 "state of cultural alignment roundup" prose still binding (from T1 §5.7).

Related: [[project-phase7-T1-verdict]]
