---
name: phase7-T3-verdict
description: 2026-05-17 Phase 7 T3 verdict — drafter framework + Bluesky drafter; PASS-WITH-NOTES with 18 binding notes (§5.1–§5.18) operationalizing all 10 Orchestrator methodology questions; heaviest CDA SME gate of Phase 7.
metadata:
  type: project
---

# Phase 7 T3 — Drafter framework + Bluesky drafter PASS-WITH-NOTES

**Verdict file:** `/opt/lsb-agent/docs/status/2026-05-17-phase7-T3-cda-sme-verdict.md`

**Why:** T3 is the highest-leverage methodology gate in Phase 7 — every word of `cdb_social/drafters/prompts/v1/bluesky.md` is methodology copy, and every regex in `validate_draft()` decides whether a §1.5.4 violation reaches the queue. The Orchestrator surfaced 10 methodology questions; this verdict lands 18 binding notes operationalizing all 10.

**How to apply:** Future Phase 7 verdicts (T4 X/LinkedIn drafters, T5 review CLI, T7 cron) inherit from this verdict's design. Key non-obvious decisions:

1. **Validator (1) substring scan** is the §1.5.4 left-column phrases verbatim + small word-stem set (`worldview`, `believes`, `thinks`); phrases match phrase-level (literal regex), stems match `\b...\b` (word boundary) to avoid "disbelieves" matching "believes."

2. **Validator (2) numeric+CI adjacency** uses K=12 token window and five exemption categories (model version strings, year tokens, char-count metadata, URL components stripped before scan, "across N models" constructions).

3. **Validator (3) hypothesis-framing** is a CLOSED list of 14 phrases (§1.5.4 rows 11–12 + 3 Orchestrator-surfaced subtler patterns + §1.5.7 explicit frames). Closed at T3; new entries require SME re-review.

4. **Bluesky cached system prompt is ~1100 tokens in 6 blocks:** Role/task; §1.5.1 corpus-lens anchor (3 sentences); full §1.5.4 table verbatim; R10 numeric+CI rule + 4 canonical patterns; Register-1/2 anchor + 4 substitutions from §1.5.4 rows 7–10; Bluesky 3-line canonical structure + per-trigger-type lede patterns.

5. **Methodology-page-link labeling:** drafter labels URL as "details" or "more" until Phase 6 T1+T2 land — labeling the article-shell URL "methodology" is the §1.5 framing hazard.

6. **`drafter_self_rating` fixed at 0.5** (NOT 0.0, NOT LLM-prompted, NOT calibrated). Distinguishes "drafter ran" from the schema default 0.0 ("drafter didn't self-rate").

7. **Pattern A (3 lines) default, Pattern B (4 lines) fallback** when finding+CI exceeds ~80 chars. Target ≤ 270 chars; hard limit 300 chars; URLs count full length toward limit.

8. **v2-prompt-bump trigger:** ≥ 2 rejections in any 10-draft window on real (non-test) triggers post-launch. Audit log at `out/social/state/drafter_rejections.jsonl`. **Never silently tighten the validator instead** — validator is gate, not band-aid.

9. **Pass-rate observational, not enforced.** No SLA percentage; binary "this draft passed" is the only quality gate.

10. **System-prompt-vs-per-call split is strict:** methodology copy stays cached; per-call payload is data-only (trigger evidence + DomainResult numerics + URLs + IDs). Reviewer checks for §1.5.4 literals inside per-call payload construction code.

**Related:**
- [[phase7-T1-verdict]] — schemas + queue layout (forbidden_terms_hit, framing_checks, drafter_self_rating, MONTHLY_ROUNDUP→T7 prose fix)
- [[phase7-T2-verdict]] — trigger detectors (Option B evidence enforcement, divergence ∩ new-model interaction)
- [[phase6-T9-cda-sme-verdict]] — failures `framing_note` precedent (verbatim CDA-SME-reviewed framing text attached to data)

**Carry-forward to T4 (X + LinkedIn drafters):**
- Same DrafterBase + validator framework; T4 inherits §5.1–§5.4 unchanged
- X thread format runs validator per-segment (not per-thread); each segment ≤ 280 chars
- LinkedIn longer-form post; same §5.4 cached prompt scope; LinkedIn 3000-char hard limit; canonical structure flexes
- T7 ARCHITECTURE.md amendment still owes §5.7 of T1 verdict (the §4.6 line 1211 "state of cultural alignment" prose fix)
