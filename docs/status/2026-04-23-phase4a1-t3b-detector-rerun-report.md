# Phase 4a.1 T-R2 — Corrected-detector re-classification of 24 T3B records

**Date:** 2026-05-04
**Task ID:** #21.T-R2
**Architect plan reference:** `docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md` §2 T-R2
**SME verdict (spec source):** `docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md` Q1.F

---

## 1. Header

This document records the read-only re-classification of the 24 T3B decline-interview records
against the corrected `_is_recursive_decline()` detector (post-T-R1 commit `ce3da31`).

The re-classification does NOT mutate `data/raw/decline_interviews.jsonl`. File mtime was
verified unchanged before and after execution (mtime `1776986890` both times).

The corrected detector is imported from `scripts.run_decline_backfill` via
`rerun_recursive_decline_check.py`. The detector logic is NOT re-implemented in the script.

---

## 2. Command invoked

```
cd /opt/lsb-agent && uv run python scripts/rerun_recursive_decline_check.py
```

Exit code: 0 (clean run).

---

## 3. Per-record table (verbatim from script stdout)

```
Phase 4a.1 T-R2 — corrected detector re-classification of 24 T3B records

idx   originating_failure_id                                                  model_id                                  domain      corrected_flag  trigger_reason                     
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
0     failure|microsoft/phi-4|family|4|2026-04-22T18:31:59.684133             microsoft/phi-4                           family      False                                              
1     failure|google/gemini-2.5-pro|family|0|2026-04-22T20:23:51.189181       google/gemini-2.5-pro                     family      False                                              
2     failure|google/gemini-2.5-pro|family|1|2026-04-22T20:25:49.080269       google/gemini-2.5-pro                     family      False                                              
3     failure|meta-llama/llama-4-maverick|family|1|2026-04-22T20:25:55.7772…  meta-llama/llama-4-maverick               family      False                                              
4     failure|openai/gpt-5.4-mini|family|0|2026-04-22T20:26:51.921647         openai/gpt-5.4-mini                       family      False                                              
5     failure|openai/gpt-5.4-mini|family|2|2026-04-22T20:27:20.849170         openai/gpt-5.4-mini                       family      False                                              
6     failure|google/gemini-2.5-pro|family|2|2026-04-22T20:27:47.411972       google/gemini-2.5-pro                     family      False                                              
7     failure|google/gemini-2.5-pro|family|3|2026-04-22T20:29:44.864405       google/gemini-2.5-pro                     family      False                                              
8     failure|google/gemini-2.5-pro|family|4|2026-04-22T20:31:40.674659       google/gemini-2.5-pro                     family      False                                              
9     failure|meta-llama/llama-4-maverick|family|4|2026-04-22T20:33:24.6468…  meta-llama/llama-4-maverick               family      False                                              
10    failure|google/gemini-2.5-pro|holidays|0|2026-04-22T20:33:47.253491     google/gemini-2.5-pro                     holidays    False                                              
11    failure|meta-llama/llama-4-maverick|holidays|0|2026-04-22T20:35:17.28…  meta-llama/llama-4-maverick               holidays    False                                              
12    failure|google/gemini-2.5-pro|holidays|1|2026-04-22T20:35:54.423304     google/gemini-2.5-pro                     holidays    False                                              
13    failure|google/gemini-2.5-pro|holidays|2|2026-04-22T20:37:55.955684     google/gemini-2.5-pro                     holidays    False                                              
14    failure|meta-llama/llama-4-maverick|holidays|1|2026-04-22T20:38:34.45…  meta-llama/llama-4-maverick               holidays    False                                              
15    failure|google/gemini-2.5-pro|holidays|3|2026-04-22T20:39:59.890810     google/gemini-2.5-pro                     holidays    False                                              
16    failure|google/gemini-2.5-pro|holidays|4|2026-04-22T20:42:02.559110     google/gemini-2.5-pro                     holidays    False                                              
17    failure|mistralai/mistral-small-2603|holidays|3|2026-04-22T20:55:22.2…  mistralai/mistral-small-2603              holidays    False                                              
18    failure|z-ai/glm-5.1|family|1|2026-04-22T22:31:17.084756                z-ai/glm-5.1                              family      False                                              
19    failure|z-ai/glm-5.1|family|3|2026-04-22T22:37:01.955489                z-ai/glm-5.1                              family      False                                              
20    failure|z-ai/glm-5.1|holidays|0|2026-04-22T22:47:06.547653              z-ai/glm-5.1                              holidays    False                                              
21    failure|z-ai/glm-5.1|holidays|2|2026-04-22T22:52:51.965938              z-ai/glm-5.1                              holidays    False                                              
22    failure|z-ai/glm-5.1|holidays|3|2026-04-22T22:57:29.951184              z-ai/glm-5.1                              holidays    False                                              
23    failure|z-ai/glm-5.1|holidays|4|2026-04-22T23:05:31.476586              z-ai/glm-5.1                              holidays    False                                              
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Corrected flags: 0 of 24
```

---

## 4. Summary count

| Metric | Count |
|---|---|
| Pre-correction detector flag count (T3B run) | **18 of 24** |
| Post-manual-inspection true rate (T3B run log §"Breakdown") | **0 of 24** |
| Post-correction detector flag count (this T-R2 re-run) | **0 of 24** |

The pre-correction count (18) arose from `SAFETY_FILTER_MARKERS` substring matching on
`response_verbatim` text, which flagged substantive narratives describing safety events as
if they were recursive declines. The post-manual-inspection true rate of 0/24 confirmed
all 18 flags were false positives. The corrected detector confirms 0 of 24, matching the
manual-inspection finding.

---

## 5. Comparison to pre-correction — per-record deltas for the 18 originally flagged records

The pre-correction detector applied `SAFETY_FILTER_MARKERS` as a substring scan against
`response_verbatim`. The 18 originally flagged records and their deltas are:

| idx | originating_failure_id | original_flag | original_trigger | corrected_flag | delta |
|---|---|---|---|---|---|
| 1 | failure\|google/gemini-2.5-pro\|family\|0\|2026-04-22T20:23:51.189181 | True | marker:'OTHER' | False | True → False |
| 2 | failure\|google/gemini-2.5-pro\|family\|1\|2026-04-22T20:25:49.080269 | True | marker:'safety' | False | True → False |
| 5 | failure\|openai/gpt-5.4-mini\|family\|2\|2026-04-22T20:27:20.849170 | True | marker:'OTHER' | False | True → False |
| 6 | failure\|google/gemini-2.5-pro\|family\|2\|2026-04-22T20:27:47.411972 | True | marker:'safety' | False | True → False |
| 7 | failure\|google/gemini-2.5-pro\|family\|3\|2026-04-22T20:29:44.864405 | True | marker:'safety' | False | True → False |
| 8 | failure\|google/gemini-2.5-pro\|family\|4\|2026-04-22T20:31:40.674659 | True | marker:'safety' | False | True → False |
| 9 | failure\|meta-llama/llama-4-maverick\|family\|4\|2026-04-22T20:33:24.646846 | True | marker:'OTHER' | False | True → False |
| 10 | failure\|google/gemini-2.5-pro\|holidays\|0\|2026-04-22T20:33:47.253491 | True | marker:'OTHER' | False | True → False |
| 11 | failure\|meta-llama/llama-4-maverick\|holidays\|0\|2026-04-22T20:35:17.284077 | True | marker:'OTHER' | False | True → False |
| 12 | failure\|google/gemini-2.5-pro\|holidays\|1\|2026-04-22T20:35:54.423304 | True | marker:'blocked' | False | True → False |
| 13 | failure\|google/gemini-2.5-pro\|holidays\|2\|2026-04-22T20:37:55.955684 | True | marker:'safety' | False | True → False |
| 15 | failure\|google/gemini-2.5-pro\|holidays\|3\|2026-04-22T20:39:59.890810 | True | marker:'safety' | False | True → False |
| 16 | failure\|google/gemini-2.5-pro\|holidays\|4\|2026-04-22T20:42:02.559110 | True | marker:'safety' | False | True → False |
| 18 | failure\|z-ai/glm-5.1\|family\|1\|2026-04-22T22:31:17.084756 | True | marker:'safety' | False | True → False |
| 19 | failure\|z-ai/glm-5.1\|family\|3\|2026-04-22T22:37:01.955489 | True | marker:'safety' | False | True → False |
| 20 | failure\|z-ai/glm-5.1\|holidays\|0\|2026-04-22T22:47:06.547653 | True | marker:'safety' | False | True → False |
| 21 | failure\|z-ai/glm-5.1\|holidays\|2\|2026-04-22T22:52:51.965938 | True | marker:'safety' | False | True → False |
| 23 | failure\|z-ai/glm-5.1\|holidays\|4\|2026-04-22T23:05:31.476586 | True | marker:'safety' | False | True → False |

**Per-record disagreement count: 18 of 18** (all 18 originally-flagged records changed from
True to False under the corrected detector).

**Original trigger breakdown:**
- `marker:'safety'` — 12 records (substantive narratives describing safety-filter events in the originating exchange)
- `marker:'OTHER'` — 5 records (ordinary prose containing "mother", "other words", "each other", etc.)
- `marker:'blocked'` — 1 record (substantive narrative reporting a content-policy block)

Records NOT originally flagged (6 records at idx 0, 3, 4, 14, 17, 22): unchanged at False
in both the pre-correction and corrected detector.

---

## 6. Disposition

**Corrected flag count: 0 of 24.**

T4 unblocks. Binding note 6 / A6 do not fire on the corrected detector (the two-tier rule
applies to the true recursive-decline rate, which is 0/24 — per SME T3B-detector verdict R7
clarification). Proceed to T-R3 (folded into T4) and T4.

---

## 7. Cross-references

- SME T3B-detector verdict: `docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md`
  (Q1.F is the spec for this re-run task)
- T3B run log: `docs/status/2026-04-23-phase4a1-t3b-run-log.md`
  (source of the pre-correction 18-flag count and manual-inspection true rate 0/24)
- T-R1 commit: `ce3da31`
  (`fix(scripts): correct _is_recursive_decline output classification (T-R1)`)
- Amendment 2: `docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md` §2 T-R2

---

*End of T-R2 re-classification report. Corrected flags: 0 of 24. T4 unblocked.*
