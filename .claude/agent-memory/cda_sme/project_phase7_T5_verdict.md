---
name: phase7_T5_verdict
description: Phase 7 T5 (queue + review CLI) CDA SME verdict PASS-WITH-NOTES — column header strings, framing_checks per-key display, trigger summary canonical phrasings
metadata:
  type: project
---

Phase 7 T5 CDA SME verdict — PASS-WITH-NOTES, 2026-05-17.

11 binding notes (§5.1–§5.11) on `scripts/social_review.py` + `cdb_social/queue.py`.

**Why:** light CDA SME gate per kickoff §3 T5 — operator-internal CLI, no UI/UX gate. CDA SME role narrow: display-prose §1.5.4 compliance and trigger-summary canonical phrasings.

**How to apply:** when reviewing T6 (publisher) or T7 (cron/docs), the CLI's column headers + trigger summaries are the locked surface — `Drafter self-rating` (NOT `Confidence`), four `framing_checks` keys verbatim, `max pairwise distance` (NOT "pairwise gap") for DIVERGENCE, `Procrustes distance` for DRIFT, `monthly cross-domain categorical-structure roundup` for MONTHLY_ROUNDUP. The MONTHLY_ROUNDUP phrasing applies the T1 §5.7 amendment at the display layer before the T7 ARCHITECTURE.md doc-fix lands.

Conditional schema-touch: §5.3 adds `rejection_reason` (5-code enum) + `rejection_note` to `SocialDraft` (Choice A) OR sidecar JSON (Choice B). Architect ratification + DATA_DICTIONARY §13 update only required for Choice A.

T1 §5.7 ARCHITECTURE.md §4.6 line 1211 fix still pending at T7 — display-layer defuse does not discharge doc-level fix.

Related: [[phase7_T1_verdict]] [[phase7_T2_verdict]] [[phase7_T3_verdict]]
