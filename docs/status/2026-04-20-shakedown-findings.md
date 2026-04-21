# Shakedown findings — 2026-04-20 cycle

**Campaign ID:** `shakedown-20260420`
**Data:** `data/shakedown/shakedown-20260420/` (non-canonical; see `docs/SHAKEDOWN_PROTOCOL.md` §2)
**Status:** Pre-Phase-4a diagnostic. **Findings are about the pipeline, not about the models.**

---

## 1. Collection summary

| Cell | Scope | Records | Adapter diversity |
|---|---|---|---|
| Primary | 4 models × 2 domains × N=8 | 56 | anthropic_api, google_ai, openrouter, openai_api (4 of 8 methods exercised — §4 minimum met) |
| Sensitivity | claude-sonnet-4.6 × family × 8 prompt variants × N=5 | +40 (1 QA_FAIL) | anthropic_api |
| Determinism | claude-sonnet-4.6 × family × N=5 @ T=0.0 | +4 (1 label-count ERROR) | anthropic_api |
| **Total** | | **100 records in JSONL** | |

Models used:
- `anthropic/claude-sonnet-4.6` (anthropic_api)
- `google/gemini-2.5-flash` (google_ai)
- `deepseek/deepseek-chat-v3.1` (openrouter)
- `openai/gpt-5.4-mini` (openai_api)

Per-domain record counts after pipeline filtering:
- family: 77 records / 4 models
- holidays: 23 records / 4 models

---

## 2. §8 sanity-check results

Check-by-check against `docs/SHAKEDOWN_PROTOCOL.md` §8.

| # | Check | Family | Holidays | Disposition |
|---|---|---|---|---|
| 1 | `consensus_type` populated from Caulkins typology | **None** | **None** | **FAIL — pipeline gap** |
| 2 | `romney_eigenratio` and per-model `oci` distinct | `romney=None`, `oci=present` | `romney=None`, `oci=present` | **FAIL — romney unwired** |
| 3 | Every `WithinModelResult` carries `underestimates_uncertainty=True` | 4/4 True | 4/4 True | **PASS** |
| 4 | `generated_lede` either empty or passes vocab regex | `''` (N/A, `cdb_publish` unwired) | `''` (N/A) | **PASS (vacuously)** |
| 5 | Negative-centrality entries flagged in `negative_centrality_models` | `ccs={}`, flag=False | `ccs={}`, flag=False | **FAIL — centrality unwired** |
| 6 | `truncation_type` populated on every `InformantRecord` | — | — | **FAIL — null on 100/100 raw records** |
| 7 | Split G1 fields distinct on sensitivity-cell result | all None | all None | **FAIL — G1 split unwired** |
| 8 | `consensus_type` and `negative_centrality_flag` logically consistent | N/A (ct None) | N/A (ct None) | N/A — cannot evaluate until #1 fixed |

**Summary:** 1 PASS, 1 vacuously-PASS, 5 FAIL, 1 N/A.

Per §8 last line: *"If any check fails, the shakedown result is a finding about the pipeline and the issue is logged. The shakedown does not 'fail' in a pass/fail sense — surfacing issues is its purpose."* These are findings. They are the expected output of a first shakedown.

---

## 3. What did work

- **Real four-model collection ran end-to-end.** 100 records across 4 architecturally distinct providers; adapter diversity §4 minimum met.
- **`--campaign-id` tagging worked.** Every record carries `campaign_id=shakedown-20260420` in `qa_notes`.
- **`--temperature 0.0` CLI flag worked** (determinism cell wrote 4 PASS records).
- **`--prompt-version v1_sN` loop worked** across all 8 variants (39/40 PASS, 1 QA_FAIL — a real QA detection, not a parser failure).
- **Pile-sort duplicate handling** (warn+skip, not raise) behaved correctly in v1_s2 runs 1 and 2 — the `chore/shakedown-blocker-fixes` change is now production-validated.
- **OpenAI `max_completion_tokens`** fix worked on gpt-5.4-mini — no HTTP 400s after the `fix/openai-max-completion-tokens` PR.
- **Bootstrap ran successfully** on both domains; `consensus_score` and `consensus_ci` are populated with sensible values (family 0.72 CI 0.58–0.87; holidays 0.76 CI 0.66–0.86).
- **Sutrop CSI populated for all 4 models** on both domains; agreement ρ range [0.976–0.988] family, [0.947–0.989] holidays.
- **`within_model_results` with `underestimates_uncertainty=True`** per Level-1 bootstrap binding — all 8 WMRs (4 models × 2 domains) set the flag correctly.
- **Two-cluster structure surfaced** on both domains (family 2 clusters, holidays 2 clusters) — clustering step wrote without errors.

---

## 4. Pipeline findings to resolve before Phase 4a

Each is a pre-Phase-4a blocker per `docs/SHAKEDOWN_PROTOCOL.md` §9 ("pipeline bugs surfaced by the shakedown are filed as issues against master and fixed *before* Phase 4a begins").

### Finding 1 — `consensus_type` (Caulkins typology) not populated

**Symptom:** Both `DomainResult.consensus_type` is `None` despite sufficient data (4 models, 77/23 records, full matrices present).

**Expected:** Value from the Caulkins & Hyatt six-state typology: one of `{STRONG_CONSENSUS, WEAK_CONSENSUS, SUBCULTURAL, TURBULENT, CONTESTED, DETERMINISTIC}`.

**Likely cause:** `classify_consensus` dispatch not invoked during `cdb_analyze/pipeline.py`'s final assembly step, or invoked-but-result-not-written. Also blocks check #8.

### Finding 2 — `romney_eigenratio` not computed

**Symptom:** `romney_eigenratio=None` on both domains. Per-model `oci` is present, so the naming separation is intact; the field is just unwired.

**Expected:** Numeric eigenratio for the cross-model consensus matrix, evaluated against both `romney_threshold_lsb=5.0` and `romney_threshold_classic=3.0`. Also sets `romney_consensus_pass` and `romney_consensus_warning`.

**Likely cause:** Romney CCM step not invoked in pipeline, OR invoked but result not persisted onto `DomainResult`.

### Finding 3 — `cultural_centrality_scores` empty dict

**Symptom:** `cultural_centrality_scores={}` on both domains. `negative_centrality_flag=False` is therefore vacuously False, not meaningfully False.

**Expected:** Per-model centrality scores populated; `negative_centrality_flag` set based on whether any are negative; `negative_centrality_models` lists the negative entries.

**Downstream impact:** Blocks check #8 (consistency) and blocks the §1.5.5 "negative-centrality first-class state" dashboard path from being reachable with real data.

### Finding 4 — `truncation_type` null on 100/100 raw records

**Symptom:** All 100 `InformantRecord.truncation_type` values are `None` (not `elbow`, `length_cap`, or any other label).

**Expected:** Populated per record with the reason the free list ended — usually `elbow`, occasionally `length_cap`.

**Likely cause:** The field is defaulted to None and nothing writes it during assembly in `cdb_collect.runner._assemble_record`. The truncation decision (where to cut the free list) is made *somewhere*, but the decision label is not being propagated onto the record.

### Finding 5 — Split G1 fields all None on sensitivity-cell result

**Symptom:** `g1_salience_stability`, `g1_spatial_stability`, `g1_salience_pass`, `g1_spatial_pass`, `g1_overall_pass`, `g1_aggregate_stability` are all `None` on the family DomainResult (which contains the sensitivity cell — 40 runs × 1 model across 8 prompt variants).

**Expected (SME §1.3, un-deferred):** Two distinct numbers (salience stability from Spearman ρ on Smith's S; spatial stability from Mantel on co-occurrence), two distinct pass booleans, and their conjunction `g1_overall_pass`. A single aggregated G1 number would also be a regression; the spec requires the split.

**Likely cause:** `g1_stability_split()` from `packages/cdb_analyze/cdb_analyze/gates.py` is not invoked by the pipeline on sensitivity-cell data. The analysis pipeline may not currently distinguish primary-cell data from sensitivity-cell data; fixing this requires adding that detection or invoking G1 unconditionally when multiple prompt versions are present in the record set.

### Finding 6 — `generated_lede` is empty (expected, noted here for completeness)

**Status:** Empty, which is vacuously PASS per §8 check 4. This is not a bug — `cdb_publish` is not yet wired into the analysis pipeline, and the shakedown does not require it. Noted only so the field's empty state is not misread as a missing value later.

---

## 5. Secondary findings (from collection log, not §8)

These are not §8 sanity-check failures but were visible in the collection run and should be filed.

- **Windows cp1252 encoding errors** on non-ASCII content (e.g., `'charmap' codec can't encode character '\u02bc'` in holidays). Triggered 4 run-level ERRORs during primary-cell collection. `PYTHONIOENCODING=utf-8` set at script level but does not propagate through all subprocess paths.
- **`qa_passed` hardcoded True at assembly** (pre-existing, flagged during shakedown). Records marked `qa_passed=True` even when `check_record` returns False. 1 QA_FAIL was logged via a different path during sensitivity v1_s3 run 2; worth confirming whether that record's `qa_passed` field reflects reality.
- **Check 5 latency threshold** (30s) triggers on Gemini/DeepSeek 200-item prompts under normal load. Not a model problem; a threshold problem.
- **Label-count mismatch parser failures**: the determinism cell run 1 failed with `Expected 21 labels, got 20` — the interviewer step sometimes returns one fewer label than piles (merged or dropped). Currently surfaces as ERROR; could be handled more gracefully.

---

## 6. Recommended disposition

The shakedown's purpose is surfacing findings; it has succeeded at that. Before Phase 4a:

1. **File one tracker issue per Finding 1–5** (Finding 6 is not a bug; Section 5 items are separate issues).
2. **Ship a batched "shakedown-findings-batch-2" PR** addressing Findings 1–5 plus the Section 5 items, each with a dedicated test using a subset of the shakedown records as a fixture (per §10 retention: "regression-test fixtures are the only shakedown artifacts that survive past Phase 4a").
3. **Re-run the shakedown Option A (primary cell only, N=5)** after that PR lands, to verify §8 checks 1–2, 5, 7, 8 now pass.
4. **Only then proceed to Phase 4a.** The B2 backup precondition is also still in effect per `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1.

The CDA SME should review §2, §4, and §5 of this document directly against `data/shakedown/shakedown-20260420/results/{family,holidays}/0.1.json`. Open questions 1, 4, 5 from post-F1 are partially resolved by this cycle's findings; open questions 2, 3 remain untouched.

---

*End of findings. `docs/status/2026-04-20-shakedown-findings.md`.*
