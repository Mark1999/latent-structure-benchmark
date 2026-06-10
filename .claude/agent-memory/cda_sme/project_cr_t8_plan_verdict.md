---
name: cr-t8-plan-verdict
description: 2026-06-10 CDA SME plan verdict for CR-T8 (per-attempt retry-transcript exposure on Collection records tab) — PASS-WITH-NOTES with 4 binding notes
metadata:
  type: project
---

# CR-T8 plan verdict — PASS-WITH-NOTES (2026-06-10)

Per-attempt retry-transcript exposure for `PublishedFailureRecord.retry_attempts` (and defensively `DeclineInterviewRecord`) on the Collection records tab.

**Verdict shape.** Plan correctly delegates byte-identical draft of `BLOCK_ATTEMPTS` and `ATTEMPTS_FRAMING` to CDA SME at gate review (CR-T7 pattern). Plan does NOT pre-author the strings; it specifies the register constraints they must satisfy. SME owns drafts before Coder dispatch.

**STEP ZERO confirmed in-tree.** Spot-checked `apps/dashboard/public/data/failures/family.json` line 617+: `retry_attempts` populated with per-attempt dicts carrying `attempt_index`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `input_tokens`, `output_tokens`, `thoughts_token_count`, `latency_ms`, `parse_error_message`. NO per-attempt `prompt_verbatim` — confirms PIPELINE-retry-same-prompt register at the data-shape level. Publish schema (`packages/cdb_publish/cdb_publish/schemas/failures.py` line 55) types the field correctly.

**Binding notes (4):**

- **N1 (binding):** CDA SME owns the `attempt_index` display-offset decision (literal `attempt_index` 0-indexed for JSON-byte audit-alignment vs prose-readable "Attempt 1" 1-indexed). This is methodological auditability, NOT visual design. AC9's "or whatever the UI/UX-approved phrasing is" caveat must redirect to SME at gate. Recommendation surface: literal `attempt_index` 0-indexed keeps the dashboard string byte-aligned with the published JSON, which strengthens the audit trail.

- **N2 (binding):** `parse_error_message` surfaces method-internal LSB classification logic verbatim ("Items missing from pile sort: {...}"). A cold reader can misread the set-difference language as a finding about the model rather than as an LSB parser-state classifier output. CDA SME drafts a short framing label or in-line phrase clarifying that this field names what the LSB parser detected, mirroring the `originating_outcome_class` framing precedent (T3 N4, T9 framing_note posture).

- **N3 (binding) — register locks carried forward into BLOCK_ATTEMPTS + ATTEMPTS_FRAMING:**
  1. PIPELINE retry not model retry ("the pipeline re-issued the prompt").
  2. Parser-state language only (no "the model attempted/retried").
  3. No bare "refusal" (T3 N4 carry-forward).
  4. No "cooperative" outside CR-T1's counterfactual frame (T1 N1 carry-forward).
  5. No cognition attribution (worldview/believes/thinks/understands/wants).
  6. The shared-prompt register lock is preserved by rendering parent `prompt_verbatim` ONCE, not per attempt (AC11).

- **N4 (binding):** Case 9 chrome-isolation walk extension must open the `<details>` to materialise the attempts block before walking, AND must extend the forbidden-substring scan to cover BOTH new strings. SME-approved drafts ship in `LSB_CHROME_TEXT` test seed if they contain methodologically-load-bearing phrases that should not appear elsewhere in the rendered chrome.

**Carry-forwards (advisory, already in plan):**
- T1 N1 "cooperative" rule.
- T3 N4 no-bare-refusal.
- T7 N1-N8 (BLOCK_*_EXCHANGE naming, sub-label register, anti-attribution-in-DATA_DICTIONARY pattern).
- Em-dash zero-tolerance grep at Reviewer (AC23).
- Pitfall 15 token-grep at UI/UX (every `var(--...)` defined in `tokens.css`).

**Out-of-scope (correctly excluded):**
- `cdb_core/schemas.py` (R6 not triggered).
- `cdb_publish/failures.py` (field already passed through unconditionally at line 237).
- `cdb_publish/schemas/failures.py` (field already typed at line 55).
- `docs/DATA_DICTIONARY.md` (R7 not triggered).
- Any per-record JSON (T7's surface, not T8's).

**Four-axis scorecard:**

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | N/A (no analysis surface; record-browser only) |
| Axis 3 — Claims validity | PASS-WITH-NOTES (N2: parse_error_message framing; N3: register locks on strings) |
| Axis 4 — Audience translation | PASS-WITH-NOTES (N1: attempt-index audit alignment; N2: cold-reader misread risk) |

**Register compliance:** PASS (Register 1/2/3 N/A; this is a records browser surface, not an analytical surface).
**Vocabulary compliance:** PASS (plan body avoids §1.5.4 forbidden vocab; uses banned phrases only as negative examples for SME-draft constraints).

**Dispatch decision:** SME drafts BLOCK_ATTEMPTS + ATTEMPTS_FRAMING (and addresses N1/N2) before UI/UX gate; UI/UX consumes SME-approved copy and delivers §19.18 spec; Coder dispatches.

Related: [[cr-t7-plan-verdict]], [[cr-t7-sme-bound-strings]], [[cr-t1-impact-paragraph]], [[cr-t2-followups-impact-paragraph]], [[cr-t4-successes-artifact]].
