---
name: phase7-T1-verdict
description: Phase 7 T1 social-pipeline schemas PASS-WITH-NOTES; confidence_score→drafter_self_rating rename + framing_checks dict + state-of-cultural-alignment prose fix
metadata:
  type: project
---

Phase 7 T1 (`SocialTrigger`/`SocialDraft`/`SocialPostRecord` + three enums) verdict 2026-05-17: **PASS-WITH-NOTES**.

**Why:** Schemas net-new and §1.5 type-level coherent, but three doctrinal corrections needed.

**How to apply:**

Binding at T1 Coder dispatch (eight notes):
- §5.2: `forbidden_terms_hit: list[str]` docstring — queue precondition `== []`; no richer match-metadata at T1
- §5.3: Add sibling `framing_checks: dict[str, bool] = {}` to `SocialDraft` alongside `framing_check_passed: bool` — bool is fast-grep contract, dict is forensic audit trail
- §5.4: **Rename `confidence_score: float` → `drafter_self_rating: float = 0.0`** — current name overclaims calibration (LSB does not claim calibration on this surface); docstring states "Not calibrated. Not used in any analysis"
- §5.5: `suggested_posting_time` docstring marks "operational hint, not methodological signal"
- §5.6: `evidence: dict[str, Any]` docstring contract + carry-forward to T2 (per-trigger-type evidence schemas reviewed at T2 SME gate)
- §5.8: `dedupe_key` docstring records SHA256[:16] formula + explicit exclusion of `drafter_version` / `prompt_version` (prompt bump ≠ re-fire)

Binding at T7 (Architect, ARCHITECTURE.md amendment):
- §5.7: **§4.6 line 1211 prose revision** — "state of cultural alignment roundup" → "monthly cross-domain categorical-structure roundup". The phrase is a §1.5 hazard: (a) collides with AI-alignment-field training-stage term-of-art (RLHF/Constitutional AI per §1.5.1/§1.5.2), (b) implies a normative axis ("state of X" presumes LSB has a position on what X should be — forbidden by §1.5.7). The enum value `MONTHLY_ROUNDUP` itself is fine; only the surrounding prose is the hazard.

Advisory to T2:
- §5.6: Per-trigger-type evidence schemas reviewed at T2 SME gate
- §5.9: `detect_divergence` must consume `state/seen_models.json` to suppress `DIVERGENCE` firing when a "new high" is caused by a model being added (to avoid double-firing with `NEW_MODEL`)

Methodology-page-link gap (kickoff §2 / §8 risk 4): no T1 binding action; `methodology_url: str` per-draft field is the right architecture; flips to `/methodology` via config when Phase 6 T1+T2 ships.

No `InformantRecord`/`GroundingRef` ripple. Register compliance N/A (T1 doesn't touch R1/R2/R3 surfaces). T2 is the higher-leverage gate (divergence semantics + monthly-roundup content scope + drift-threshold 0.15 placeholder).

Related: [[no-human-baseline-amendment]] (§1.5.5 framing the social pipeline inherits), [[phase6-T9-failures-publish-verdict]] (precedent that data-identifier enum values are §1.5.4-exempt — used here for `MONTHLY_ROUNDUP` ruling).
