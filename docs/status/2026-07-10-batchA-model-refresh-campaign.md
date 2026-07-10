# Batch A Model Refresh Campaign: Status and Staged Rebaseline

**Date:** 2026-07-10
**Campaign id:** `new-model-refresh-2026h2-a-20260710`
**Plan:** `docs/proposed/2026-07-09-model-refresh-2026h2-plan.md` (Mark approved 2026-07-10, all eight batch A models)
**Runbook:** `docs/proposed/2026-06-08-new-model-incorporation-runbook.md`
**Status:** Collection complete; staged rebaseline complete, ALL GUARDS PASS. Promotion (runbook Step 5) NOT started; awaiting Mark.

## Slate outcome (target 5 passed records per model per domain)

| Model | family | holidays | food | Disposition |
|---|---|---|---|---|
| claude-opus-4-8 | 5 | 5 | 5 | in basis |
| claude-sonnet-5 | 5 | 5 | 5 | in basis |
| openai/gpt-5.5 | 5 | 5 | 5 | in basis (re-collected after T7 adapter fix) |
| deepseek/deepseek-v4-pro | 5 | 5 | 5 | in basis |
| z-ai/glm-5.2 | 5 | 5 | 4 | in basis (food at 4, within food v0.2 precedent) |
| google/gemini-3.5-flash | 5 | 5 | 5 | in basis |
| x-ai/grok-4.3 | 5 | 5 | 5 | in basis |
| claude-fable-5 | 0 | 0 | 1 | EXCLUDED per SME R1/R2; refused-informant finding (below) |

Passed counts are under the recalibrated QA rules (corpus-build re-QA, SME N5/N13). All failed/refused/partial records preserved verbatim per failures-are-findings.

## The batch A finding: claude-fable-5 refused the elicitation

claude-fable-5's provider deployment-side output filter returned stop_reason=refusal with empty content on 22 of 23 free-list elicitation attempts (10/10 family, 10/10 holidays, 2/3 food). The identical prompts produced zero refusals on claude-opus-4-8 and claude-sonnet-5 in the same hour under the same adapter. model_version_returned matched the pinned id on all 63 Claude-family records (no fallback contamination). Disposition per CDA SME verdict (R1-R4, `docs/status/2026-07-10-batchA-fable5-refusal-cda-sme-verdict.md`): excluded from all Register 2 bases, refusal counts reported as the finding, single passing food free-list preserved but not entered (parity of measurement, R2), three decline-interview probes approved (R3, pending), bound disclosure vocabulary (R4).

## Calibration rulings executed (all Tier 1 gated, all merged)

1. Forced-default sampling (gpt-5.5, Claude 5 family reject protocol temperatures): disclosure not exclusion; adapters omit temperature and record effective 1.0 + verbatim capacity notes. Verdict: `2026-07-10-batchA-gpt55-temperature-cda-sme-verdict.md` (N1-N7).
2. Reasoning-class QA recalibration (Checks 5/6 class-conditioned on thoughts_token_count) plus dense-tokenizer class (Claude 5 generation, expected 1.75 chars/token). Verdict + addendum: `2026-07-10-batchA-reasoning-qa-cda-sme-verdict.md` (N1-N14). Corpus-build re-QA (records as data, rules as code) implemented in `load_records`.
3. OpenAI adapter reasoning-token extraction gap fixed (T7); pre-fix gpt-5.5 records unrecoverable by re-QA (missing field is data), re-collected per the 2026-05-07 fix-forward precedent.

Commits: `8a894f0`, `a1ffb0f`, `1787d79`, `a230809`, `b73422d` (+ registry fixes `8c1a14d`, `7be73e9`).

## Staged rebaseline (runbook Step 3): ALL GUARDS PASS

Run 2026-07-10 15:48 to 20:09, pinned env, bootstrap B=500, staging root `out/rebaseline/`, provenance in `baseline_manifest.json`.

| Domain | models | consensus_score prior -> new | romney_eigenratio prior -> new | guard |
|---|---|---|---|---|
| family | 14 | 0.805 -> 0.805 | 19.14 -> 19.79 | pass |
| holidays | 16 | 0.880 -> 0.897 | 39.28 -> 40.23 | pass |
| food | 21 | 0.624 -> 0.504 | 9.48 -> 5.10 | pass |

Full field-level tables: `out/rebaseline/numeric-deltas-{domain}.md` (6/11/17 flagged rows respectively; per-model centrality shifts as expected when a slate widens).

Reading (§1.5 register): family and holidays categorical structure is stable to slightly stronger under the widened slate. Food moves substantially: with nine additional informants the food domain's consensus_score drops 0.12 and the eigenratio falls from 9.48 to 5.10, sitting just above the 5.0 boundary. No guard tripped (no published classification flipped; food remains in its published WEAK_CONSENSUS-with-disclosure state), but the food domain now reads as clearly more contested across the wider model set. This is a substantive slate-composition observation for the eventual lede/methodology copy at promotion time.

## Outstanding before/at promotion

- Decline-interview probes for fable-5 (SME R3, three probes; module exists but is not CLI-wired; small driver needed).
- SME N4/N12 methodology-page footnotes (deferred to the promotion copy pass by SME direction).
- Fable-5 refusal finding disclosure copy (R4 bound vocabulary) on whatever surface promotion touches.
- N11 density detector tuning (warn-only; currently over-broad, uses raw rather than visible ratios in some paths).
- Promotion itself: runbook Step 5, gated (Reviewer, CDA SME provenance, UI/UX footer), then Step 6 social trigger. Requires Mark's go.
