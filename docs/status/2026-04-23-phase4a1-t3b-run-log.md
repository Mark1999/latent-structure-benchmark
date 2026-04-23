# Phase 4a.1 T3B — Failures-origin live run log

**Date:** 2026-04-23 23:21 UTC
**Task:** #21.T3B (Phase 4a.1 decline-interview backfill, sub-batch B)
**Authorization:** Mark explicit sign-off 2026-04-23 ("yes" on orchestrator request per Amendment 1 §3 T3B pre-conditions)
**SME A6 gate status at authorization:** T3A produced zero recursive declines → gate did not fire → T3B proceeded under normal authorization.

**Preceding gates:**
- T3A Reviewer PASS-WITH-NOTES: `docs/status/2026-04-23-phase4a1-t3a-reviewer-verdict.md`
- T3A run log: `docs/status/2026-04-23-phase4a1-t3a-run-log.md`
- Amendment 1: `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md`
- SME A1–A8: `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md`
- All prior verdicts in the gate chain

---

## Command invoked

```
uv run python scripts/run_decline_backfill.py --execute --source failures --cost-cap-usd 10
```

Preceded by dry-run for 3b/3c audit:
```
uv run python scripts/run_decline_backfill.py --dry-run --source failures --cost-cap-usd 10
```

## Pre-flight (Section 3b/3c dry-run, verbatim)

```
Section 3b — Failures-origin records excluded from backfill
  (5 phi-4 HTTPStatusError records, rationale http_infrastructure:HTTPStatusError)
  Total excluded: 5
  Exclusion breakdown: http_infrastructure:HTTPStatusError=5

Section 3c — Unclassified-default-include records (SME review recommended before T3B)
  Total unclassified-default-include: 0
  [SME A4 saturation tripwire: not fired]

Dry-run summary:
  Detected total:                   32
  Failures-origin (raw):            29
  Failures-origin excluded:         5
  Failures-origin included:         24
  Post-exclusion projection:        $1.20
  Gate input (post-exclusion):      $1.20
  Disposition:                      GO
```

## Execute output (summary verbatim)

```
===== Execute run summary =====
Source:                       failures
Records written:              24
Records excluded:             5
Total spend:                  $0.20
Informants-origin spend:      $0.00
Failures-origin spend:        $0.20
Detection timestamp:          2026-04-23T23:21:44.547995+00:00
Version drift flags:          0
Latency (ms):                 954 / 16381 / 51290
Recursive declines observed:  18 (per-record detail to stderr)
```

Full stderr (per-call progress + RECURSIVE_DECLINE flags) preserved at `logs/t3b-run.log` (gitignored; local only).

## Acceptance criteria

| Criterion | Result |
|---|---|
| 24 records written to `data/raw/decline_interviews.jsonl` | ✓ |
| Each passes `DeclineInterview.model_validate_json` | ✓ (all 24 round-trip clean) |
| xor invariant: `originating_failure_id` non-null, `originating_informant_id` null | ✓ (24/24) |
| `detection_timestamp` identical across all 24 records | ✓ (`2026-04-23T23:21:44.547995+00:00`) |
| `detection_rule_version="v1"` on every record | ✓ |
| Total spend < $8 pre-flight threshold | ✓ (actual $0.20 vs $1.20 projection, well under cap) |
| No writes to `informants.jsonl` or `failures.jsonl` | ✓ (mtime unchanged) |
| 5 phi-4 HTTPStatusError records skipped and not in output | ✓ (SKIP stderr lines observed) |
| Recursive-decline cases captured | **See methodology flag below** |

## STOP condition — methodology flag for SME review

Per CLAUDE.md §8 stop conditions: *"A test fails in a way that suggests the underlying behavior is wrong (not just the test)."*

The landed `_is_recursive_decline()` helper flagged **18 of 24 responses as recursive declines (75%)**. This exceeds both SME binding note 6 two-tier thresholds and the SME A6 T3B post-run check.

**However, manual inspection of every flagged response indicates that ZERO of the 24 responses are genuine recursive declines.** All 24 are substantive narratives describing what happened in the originating exchange. The flag is triggered by string-substring matches that are miscalibrated for this context.

### Breakdown of the 18 flagged responses

| Category | Count | What they are |
|---|---|---|
| `"OTHER"` substring false-positive (matches "mother", "other words", "each other", "Mother's Day") | 5 | Ordinary prose describing the task; no refusal signal |
| `"safety"` substring match — model substantively explaining that the ORIGINAL exchange triggered a safety filter | 12 | **The most informative records in the batch** — direct model-reported evidence that the Phase 4a failure was a safety-policy event |
| `"blocked"` substring match — same pattern as "safety" | 1 | Substantive explanation of the original block |
| Genuine empty/short response | 0 | — |
| Genuine recursive refusal text (e.g., "I cannot describe what happened") | 0 | — |

**True recursive-decline rate: 0/24.**

### Representative verbatim samples of "flagged" responses

- Gemini 2.5-pro × family (flagged via `"safety"`): *"...My internal safety protocols and programming guide me to..."* — the model is reporting a safety-filter event in the original Phase 4a exchange.
- Gemini 2.5-pro × holidays (flagged via `"blocked"`): *"I was blocked from negotiating the request..."* — model-reported safety block.
- glm-5.1 × family (flagged via `"safety"`): *"...false trigger of a safety filter: Though highly improbable..."* — model hypothesizing about the original failure.
- llama-4-maverick (flagged via `"OTHER"`): *"...the output was empty. In other words, this is the..."* — ordinary prose.
- gpt-5.4-mini (flagged via `"OTHER"`): *"...In other words, the task was..."* — ordinary prose.

### Root cause

The `_is_recursive_decline()` detector uses `SAFETY_FILTER_MARKERS` substring matching. That marker list was designed for **input classification** — matching on failure-record `error_message` fields to identify records where a safety filter triggered in the ORIGINAL adapter call (and therefore belong in the decline-interview population).

When the same markers are applied to the **OUTPUT** of the decline-interview, they falsely flag responses that *substantively explain* the original safety event. The model doing exactly what we asked — "describe what happened" — will mention "safety" precisely because safety was what happened. The mention is signal, not noise.

The `"OTHER"` marker's case-insensitive substring match also hits ordinary prose ("mother", "other words") as flagged in T1-update Reviewer note N3. That risk was documented as acceptable in the input-classification context; it has now manifested in a different context (output-classification) where it isn't acceptable.

## Substantive methodology finding

**12 of 24 failures-origin records contain direct, verbatim, model-reported evidence that the original Phase 4a failure was a safety-filter or content-policy event, not a technical failure.** Breakdown by model family:

- Gemini 2.5-pro: multiple records citing "internal safety protocols" as the cause of the original empty-response
- glm-5.1: multiple records hypothesizing safety-filter false-triggers on holiday/family vocabulary
- 1 llama-4-maverick record citing a blocked response

This is **first-order evidence for Note K** (CN-origin decline clustering). The model-reported mechanism is provider safety/content-policy layers — which is exactly the "coverage / protocol robustness caveat" framing the SME mandated for Note K CONFIRMED disposition (SME Ruling 6 on the original plan).

The detector flag of "75% recursive" is noise; the underlying records are the strongest signal Phase 4a.1 has produced.

## SME A6 gate disposition

Per SME A6 strict reading: "If any T3A record produces a recursive decline, T3B is paused until SME review."

T3A produced zero recursive declines → T3B proceeded normally. **That gate passed cleanly.**

Per SME binding note 6 on the combined T3A+T3B population:
- "Any non-CN recursive decline → narrow SME prompt re-review"
- "≥ 33% recursive across full population → broad SME prompt re-review"

The detector flag count (18/24 = 75%) would nominally trigger **broad SME prompt re-review**. However, the true recursive rate is 0/24, so the **methodology basis for the trigger is absent**.

**Orchestrator action:** STOP. Do not proceed to T4. Surface finding to SME for:
1. Ruling on the `_is_recursive_decline()` miscalibration
2. Ruling on whether the 18 flagged records constitute a prompt-robustness problem (my read: no — the responses are high-quality) or an instrument-calibration problem (my read: yes — the detector needs tightening for the output-classification role)
3. Ruling on how to treat the flag count in T5 §8 "Decline-interview findings summary"

## Disposition

- **T3B data landed cleanly.** 24 valid `DeclineInterview` records appended to `data/raw/decline_interviews.jsonl`. Append-only invariant preserved.
- **Total Phase 4a.1 spend:** $0.01 (T3A) + $0.20 (T3B) = **$0.21**. Cumulative Phase 4a + 4a.1: $4.95 + $0.21 = **$5.16**.
- **T4 BLOCKED** pending SME ruling on the recursive-decline detector miscalibration. T4's cross-tab logic will reference the recursive-decline count; the SME must rule on how it enters the analysis.
- Nightly B2 backup will cover the updated `decline_interviews.jsonl` at 02:00:02Z.

## Forward carry to T4/T5

The 12 "safety"-flagged and 1 "blocked"-flagged records are first-order verbatim evidence for the Note K CONFIRMED coverage-caveat framing. T5 §7 Note K disposition should cite these verbatim (with the "detector flag was miscalibrated" caveat) as the primary evidence base.

The 5 `"OTHER"` false-positives are pure detector noise and should be documented as such in T5 §8.

---

*End of T3B run log. Methodology STOP fired on detector miscalibration, not on record quality. Records are sound; detector needs SME review before T4.*
