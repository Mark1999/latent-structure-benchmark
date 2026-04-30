# CDA SME Verdict — Phase 4a.1 Architect Plan Amendment 2 (T3C §3 schema)

**Filed:** 2026-04-30
**Reviewer:** CDA SME (Opus)
**Scope:** Methodology review of Architect Plan Amendment 2 §3 T3C-manual-classification only — schema choices, seed-file approach, validation rules, gate chain. T4 and T5 plan bodies are mechanical realizations of B2/B3/B6 and are not re-reviewed at the plan level (their *outputs* remain SME-gated per binding notes 4–6 and Ruling 3).
**Plan under review:** `docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md`
**Predecessor verdicts (still binding):**
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings, T5 §8 public-copy guardrails)
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)

---

## Verdict

**CDA SME VERDICT: PASS-WITH-NOTES**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS-WITH-NOTES |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | N/A (instrument calibration / derived artifact, no register claim) |
| Vocabulary compliance | PASS (plan body and schema choices are clean) |

The amendment correctly decomposes B1, B2/B3, and B6 into Coder-sized sub-tasks, honors the append-only invariant on `decline_interviews.jsonl`, places the derived artifact under `data/derived/`, and routes T3C commit 1 (the scaffold + schema) for SME plan re-review while leaving T4 and T5 plan bodies as mechanical realizations of the prior Ruling 3 / B2 / B3 / B6 prescriptions. The gate-chain decision in §0 is correct: my prior verdict's Ruling 3 binds the *outputs* of T4 and T5, not the plan bodies. Two binding notes (B7, B8) are added below to address (a) excerpt-vs-source authority risk on the seed file and (b) detector-flag carry-over anchoring risk. One soft note (B9) tightens the rationale length policy for one of the seven categories where 200 chars is genuinely tight.

---

## Schema choices ruled on (Amendment 2 §3 questions 1–8)

### 1. Seven-enum `manual_classification` — closed and complete: PASS

I have re-read the seven enum values against my T3B spot-check of the 24 follow-up records plus the 3 T3A records (27 total). The seven categories cover every record I observed without residue:

| Category | Coverage in the 27-record corpus |
|---|---|
| `safety_event_attribution` | ~10 records (Gemini family + holidays; glm-5.1 family + holidays) |
| `blocked_event_attribution` | 1 record disambiguates as a sub-cohort of safety-event ("blocked from negotiating") — see B9 below for whether this is reliably distinguishable from `safety_event_attribution` at classification time |
| `technical_glitch_attribution` | ~1–3 records (some glm-5.1 + mistral-small-2603 records read as backend technical-glitch attribution rather than safety) |
| `no_prior_context_acknowledgment` | ~2 records (llama-4-maverick) |
| `substantive_compliance_with_empty_input` | exactly 3 records (the T3A z-ai/glm-5.1 records) |
| `other_substring_false_positive` | ~3–5 records (gpt-5.4-mini "in other words", llama-4-maverick "Mother's Day" / "in other words") |
| `genuine_recursive_decline` | 0 records (preserved as a real category for future batches; correctly empty here) |

I deliberately considered three candidate eighth categories and rejected them:

- **"ambiguous_between_categories"** — rejected. An ambiguity escape hatch in a seven-category taxonomy would dilute the analytic axis exactly when the audit trail needs it sharpest. Mark must commit to a primary classification; ambiguity belongs in `manual_classification_rationale`, not in the enum. See B9 for the specific safety-vs-blocked ambiguity edge case (which is the only one I think will recur in this corpus).
- **"insufficient_response_for_classification"** — rejected. All 27 records are substantive; no record in this corpus is so short or empty that classification is impossible. (The empty-output events were the *originating* exchanges, not the follow-up responses, which are uniformly multi-paragraph.)
- **"mixed_safety_and_technical_attribution"** — rejected for the same reason as "ambiguous": pick the dominant attribution and document the secondary in rationale.

**The seven-enum is closed and complete for this corpus.** Confirmed.

### 2. `"UNCLASSIFIED"` sentinel approach — PASS

The sentinel (`"UNCLASSIFIED"`) outside the enum, with the loader rejecting it explicitly with a "Mark must classify all 27 rows before T4 runs" error, is preferable to the empty-string alternative for three reasons:

- It is grep-able (`rg UNCLASSIFIED data/derived/`) so Mark can resume mid-classification without scanning JSON.
- It is type-safe at the Pydantic level (the loader's enum membership check fires immediately on a sentinel row, with a precise error).
- It is not a member of the closed seven-enum, so it cannot be confused with a real category if a row leaks into T4.

This is methodology-OK and cleanly enforces the B1 gate "all 27 must be classified before T4."

### 3. `manual_classification_rationale` ≤ 200 chars — PASS-WITH-NOTE (B9)

200 chars is the right number for six of the seven categories. The one category where 200 is genuinely tight is `blocked_event_attribution` (and the safety-vs-blocked edge case more generally), where a faithful rationale needs to (a) cite the verbatim "blocked"-framing language from the response and (b) explain why this row classifies as `blocked_event_attribution` rather than the parent category `safety_event_attribution`. That second clause alone can run 80–120 chars. See B9 for the soft tightening.

For the other six categories, 200 is correct: it forces concision, which is a feature rather than a bug for an audit-trail rationale that another reviewer (the SME spot-check) needs to read 27 of in one sitting.

**No revision to the 200-char limit. B9 below clarifies the policy for the safety-vs-blocked edge case without raising the limit.**

### 4. `response_verbatim_excerpt` 400-char carry-over — PASS-WITH-NOTE (B7)

The Architect's risk read is correct and is the reason for B7. The risk: Mark classifies on the 400-char excerpt rather than reading the full record, and the excerpt happens to truncate exactly the framing language that would have flipped the classification. The mitigation in the plan ("excerpt is not authoritative; T4 re-reads from source") protects T4 but does not protect Mark's classification at commit-3 time, which is where the actual classification decision is made.

I am not going to recommend removing the excerpt entirely — the convenience of having the verbatim text inline during classification is real, and forcing Mark to context-switch between the seed file and the source JSONL for every row would meaningfully increase the chance of attribution errors for a different reason (he loses his place). The right intervention is procedural, not structural.

**B7 below requires Mark to read the full `response_verbatim` from `data/raw/decline_interviews.jsonl` for any row whose 400-char excerpt does not visibly contain the framing language that justifies the chosen category.** The classification rationale must reference the verbatim framing language (per the soft validator rule the Architect surfaced under question 6 below) — if the framing language is not in the 400-char excerpt, Mark has read the source. The B7 phrasing is operational, not schema-level, and lives in the rationale convention rather than as a schema field.

### 5. `detector_flag_v1` carry-over — PASS-WITH-NOTE (B8)

The Architect's anchoring-bias risk is real and serious. The detector v1 flagged 18 of 24 records as recursive declines, when 0 of 24 are recursive declines. If the detector's flag is surfaced inline during classification, the cognitive pressure is to either agree (classifier underweights the disagreement signal) or systematically disagree (classifier overcorrects against an instrument they have been told is broken). Both failure modes are real. The trade-off is the audit-trail value: surfacing the flag during classification produces a richer record of *which detector errors were caught and which were not* than surfacing the flag after the fact.

I am persuaded that the audit-trail value outweighs the anchoring risk **conditional on a procedural mitigation**: the classifier (Mark) must commit to the classification *before reading* the `detector_flag_v1` value on any given row. This is a behavioral protocol, not a schema constraint, and B8 below codifies it.

**Schema decision: keep `detector_flag_v1` as a seed-file field. B8 below adds the procedural classify-before-reading-flag rule.**

If Mark prefers a stronger version where the seed file is split into two passes — pass 1 (classification) writes without the flag visible, pass 2 (audit) re-emits with the flag for the spot-check verdict — that is a defensible alternative. Architect's call. Either of the two is methodologically acceptable; the one currently in the plan is acceptable with B8 attached.

### 6. Soft validator advisory for `blocked_event_attribution` — PASS (drop)

The Architect's recommendation to drop the soft validator advisory in favor of surfacing the same constraint through the SME spot-check verdict is correct. Pydantic model-validators that emit advisory fields rather than rejecting rows produce noisy schemas and noisy diffs; the rule is better expressed as a rationale convention enforced by the human reviewer. The rule survives in B9 below as a rationale-convention requirement (not a validator).

**Drop the soft validator advisory. Methodology OK.**

### 7. Loader rejects `"UNCLASSIFIED"` rows with a clear error — PASS

This is the operational realization of B1's "all 27 must be classified before T4" gate. The loader's strict validation (every source `decline_interview_id` matched, no extras, no `"UNCLASSIFIED"` sentinels, all rationale non-empty and ≤200 chars) is exactly what B1 requires. Methodology OK.

### 8. Two-pass classification (commit 3 + optional commit 4) — PASS

This realizes D12 cleanly. The post-spot-check version is the analytic truth (T4 reads it); the pre-spot-check version is the audit truth (it is in git history). The commit-4 amendments leave a per-row diff that the SME spot-check verdict cross-references explicitly. Methodology OK.

---

## Other points checked

### Public-copy guardrails carried into T5 §8 spec — PASS

I read Amendment 2 §3 T5 against my prior verdict's Ruling 3 verbatim. The five §8 subsections are reproduced in the correct order (§8.0 detector flag audit → §8.1 manual classification → §8.2 Note K disposition → §8.3 detector v2 forward note → §8.4 audit trail pointers). The "Use:" / "Do not say:" lists in the plan (§3 T5 lines 251–256) are reproduced verbatim from Ruling 3 with no semantic loss. The "mismatch is the finding" framing requirement is preserved (line 258). The "publishable" prohibition is preserved (line 256). No drift detected.

### Derived-vs-raw distinction (`DeclineManualClassification` in `cdb_analyze`, not `cdb_core`) — PASS

The Architect's placement is correct. `DeclineManualClassification` is a derived type computed from raw data plus a classification rule, not a raw schema. It belongs in `cdb_analyze` because (a) T4 consumes it, (b) it does not propagate to the open-data bundle as a schema commitment, and (c) regenerability is a first-class property of derived data. No `DATA_DICTIONARY.md` update is needed because the dictionary tracks raw-data schemas (`InformantRecord`, `GroundingRef`, `DeclineInterview`), not derived-data schemas. The derived data itself ships in the open-data bundle as a JSONL artifact, which is the correct exposure surface. Methodology OK.

### Append-only on `decline_interviews.jsonl` — PASS

Honored. The manual artifact is at `data/derived/decline_interviews_manual_classification.jsonl`, which is regenerable, not append-only. No edits to the source JSONL.

### Detector v2 deferral (D14, B5) — PASS

Honored. Indefinite deferral is methodology-acceptable because no future decline-interview batch is planned for Phase 4a.1. B5 binds future batches independently. No detector edits in this verdict.

---

## Required before T3C commit 1 begins (binding notes B7, B8, B9)

These extend B1–B6 from my prior verdict and continue the B-numbering. None of them require a re-review of this amendment; the Coder may proceed directly with the schema as written, and Mark applies B7 + B8 during commit 3 (the classification pass).

### B7 — Source-read requirement when the excerpt does not contain the framing language

For any row Mark classifies, the rationale must reference the verbatim framing language that justifies the chosen category. If the framing language is not present in the 400-char `response_verbatim_excerpt`, Mark must read the full `response_verbatim` from `data/raw/decline_interviews.jsonl` before classifying. This is a behavioral protocol, not a schema field. The SME spot-check at commit 3 will verify that the rationale's verbatim quote is in fact present in the source `response_verbatim` (not only in the excerpt). This closes the truncation-attribution-error risk surfaced in question 4.

**Operationalization:** Mark may use `scripts/inspect.py` (or any equivalent CLI) to pull the full `response_verbatim` for any row by `decline_interview_id`. The rationale field should then quote the framing language directly (e.g., `"safety filter false positive"` for record 22, or `"blocked from negotiating"` for record 16).

### B8 — Classify-before-reading-flag protocol

For each of the 27 rows, Mark commits to a classification decision **before reading** the `detector_flag_v1` value on that row. The simplest realization is sequential: classify row → record classification → look at the flag → move to next row. An alternative is to classify all 27 rows in one pass without consulting the flag column at all, then audit the flag column after. Either is acceptable.

The audit-trail value of the inline `detector_flag_v1` field survives because the final commit-3 file carries both columns; the procedural rule only constrains the *order* in which Mark reads them. The SME spot-check verdict will note any rows where the classification rationale appears to have been authored to agree-with or disagree-with the detector flag rather than authored from the verbatim source language; B8 violations surface as rationale-quality issues at the spot-check.

### B9 — Safety-vs-blocked rationale convention

When `manual_classification == "blocked_event_attribution"`, the rationale must explicitly state why this row classifies as `blocked_event_attribution` rather than the parent `safety_event_attribution`. The bar is concrete: the model's response uses "blocked"-framing as the dominant attribution language (not safety/policy/filter as the dominant language with "blocked" mentioned in passing). The rationale should quote the dominant framing language verbatim. If the row is genuinely ambiguous between the two categories (e.g., record 16, "I was blocked from negotiating" — see my T3B spot-check), it classifies as `safety_event_attribution` (the parent category) rather than `blocked_event_attribution`, and the rationale notes the alternative reading.

This is a rationale-convention rule, not a Pydantic validator. The Coder does not implement it in code. The SME spot-check verdict at commit 3 will check `blocked_event_attribution` rows against this convention.

The 200-char rationale limit (schema question 3) is **not raised**; B9 is realizable within 200 chars for every row I expect to see in the 27-record corpus.

---

## Carry-forward — all 22 prior binding notes still in force

This amendment does not supersede any prior binding note. It decomposes B1, B2/B3, B6 into Coder tasks and adds B7, B8, B9 as procedural rules for the classification pass.

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force; B1, B2/B3, B6 are decomposed into T3C/T4/T5; B4 + B5 are binding precedents with no Phase 4a.1 action |
| B7, B8, B9 (this verdict) | New, binding on T3C commit 3 (Mark's classification pass) and the SME spot-check at commit 3 |

Total binding notes on Phase 4a.1 after this verdict: **25.**

---

## Constraint checks (explicit)

| Constraint | Status |
|---|---|
| No detector edits in this verdict | **Honored.** B5 deferral carried forward. |
| Append-only on `decline_interviews.jsonl` | **Honored.** Derived artifact under `data/derived/`. |
| Public-copy guardrails (Ruling 3) carried forward into T5 §8 spec | **Honored.** Verified verbatim in §3 T5 of the amendment. |
| No new schema in `cdb_core/schemas.py` | **Honored.** `DeclineManualClassification` is in `cdb_analyze`. |
| No re-ruling on B1–B6 | **Honored.** B1 schema is confirmed; B2/B3/B6 are unchanged. |

All five constraints from the review prompt are satisfied.

---

## Forward action for Architect / Coder

Before Coder starts T3C commit 1, no changes to Amendment 2 §3 schema are required. The amendment passes methodology review as written. The Coder may proceed with the schema in §3 verbatim. The procedural binding notes B7, B8, B9 attach to **commit 3** (Mark's classification pass), not commit 1 (the Coder scaffold), and do not change the Coder's task surface.

**For the Architect:**

1. Reference this verdict (`docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md`) in the gate-chain section of any future Phase 4a.1 verdicts; include it in the "Predecessor verdicts (still binding)" lists.
2. Add B7, B8, B9 to the Coder's reading list for T3C commit 3 (Mark's classification pass), not commit 1. The Coder's reading list for commit 1 is unchanged from §3 T3C of the amendment.
3. The SME spot-check verdict at T3C commit 3 (`docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md`) will check rows against B7, B8, B9 in addition to the seven-enum coverage and the 200-char rationale limit. No change to Mark's task surface needed; the constraints are already what a careful classifier would do.
4. No change to T4 plan body. No change to T5 plan body. The T4 and T5 *output* SME gates remain as specified.

**For the Coder (T3C commit 1, no plan changes required):**

The schema in Amendment 2 §3 is approved verbatim. Implement exactly as written:

- Seven-enum `manual_classification` (closed, no eighth category).
- `"UNCLASSIFIED"` sentinel for seed; loader rejects with the "Mark must classify all 27 rows before T4 runs" error.
- `manual_classification_rationale` ≤ 200 chars; empty rejected.
- `response_verbatim_excerpt` 400 chars carried in seed; non-authoritative.
- `detector_flag_v1` carried in seed.
- No soft validator advisory.
- `manual_classifier_id` defaults to `"mark"`; per-row override permitted.
- Loader is strict: every source ID matched, no extras, no sentinels at load time.

The Coder may proceed to commit 1 immediately upon this verdict landing.

---

*Posted to `#lsb-cda-sme`. Binding for T3C through T5 unless superseded by a subsequent Architect plan cycle with SME re-review. B7, B8, B9 attach to commit 3 (Mark's classification pass) and the spot-check at commit 3; commit 1 schema is approved verbatim.*
