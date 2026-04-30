# Phase 4a.1 — Architect Plan Amendment 2 (task #21)

**Date:** 2026-04-30
**Planner:** Architect
**Task:** #21 (Phase 4a.1 decline-interview backfill) — AMENDMENT 2
**Supersedes partially:** `docs/status/2026-04-23-phase4a1-architect-plan.md` (T4 task body) and `docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md` (T4/T5 task bodies). T1, T1-update, T2, T3A, T3B all closed and unchanged.
**Carries forward:** Everything in prior plan + Amendment 1 not explicitly amended below, including **all 22 binding notes** in force after the 2026-04-23 T3B-detector SME verdict (8 original + 8 from Amendment 1 + 6 from B1–B6). This amendment is **additive**.

**Trigger:** T3B run log (`docs/status/2026-04-23-phase4a1-t3b-run-log.md`) filed a methodology STOP under CLAUDE.md §8: the v1 `_is_recursive_decline()` detector flagged 18/24 records but manual inspection showed 0/24 genuine recursive declines. CDA SME verdict (`docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md`, filed 2026-04-30) issued PASS-WITH-NOTES with three rulings and six new binding notes B1–B6. T4 was unblocked subject to those notes. This amendment decomposes B1, B2/B3, and B6 into Coder-sized sub-tasks.

**Predecessor gate verdicts (still binding, full chain):**
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings, T5 §8 public-copy guardrails)

**Gate verdict chain for this amendment:**
- Architect decomposition (this document)
- **CDA SME PASS / PASS-WITH-NOTES required** on T3C-manual-classification §3 schema choices (the 7-value enum is SME-prescribed; the file format and surrounding rules are not). Architect read: schema is methodology-adjacent enough that a quick SME re-review of the *plan* is the right gate before Coder starts. T4 and T5 plan bodies do **not** need fresh SME review — they are mechanical realizations of the prescribed B2/B3/B6 structure; the existing T3B-detector verdict is the methodology gate. T4 *output* and T5 *output* remain SME-gated per binding notes 4–6 + Ruling 3.

**No new schema changes.** No edits to `cdb_core/schemas.py`. No edits to `decline_detection.py` or `_is_recursive_decline()`. The manual classification artifact lives under `data/derived/`, is regenerable from `decline_interviews.jsonl` plus the rules, and is not append-only (per Ruling 1 step 2).

**Expected spend:** $0 — no API calls in T3C, T4, T5. Cumulative Phase 4a + 4a.1 spend stays at $5.16 from T3B.

---

## 1. Summary

The T3B run produced 24 substantive decline-interview narratives, of which the SME's spot-check found **11 substantive safety-event attributions across two providers (Google Gemini, z-ai/glm-5.1) on family and holidays**. The detector flag count (18/24) is a substring-matching artifact and is preserved as the v1 audit truth; the analytic truth comes from a manual classification overlay that joins to each record by `decline_interview_id`. T4 cross-tabs and the Note K disposition consume the manual classification, not the detector flag. T5 §8 reports both numbers under a structured five-subsection layout with public-copy guardrails baked in.

This amendment introduces three new sub-tasks that fit the existing T1 → T2 → T3A → T3B → T4 → T5 numbering with one insertion:

- **T3C-manual-classification** — scaffold the manual classification artifact format, validation, and load helpers; Mark performs the classification with SME spot-check; the artifact is committed before T4 runs.
- **T4** (replaces prior T4 body, retains numbering) — Note J cross-tab + Note K re-evaluation, now consuming the manual classification overlay as the secondary axis with cross-provider replication explicit.
- **T5** (replaces prior T5 body, retains numbering) — Completion report including the SME-mandated five-subsection §8 with public-copy guardrails enforced verbatim.

Detector v2 design is **deferred** per SME Ruling 1 + Note B5. Out of scope for this amendment; future Architect plan cycle when needed.

---

## 2. Architect dispositions for this amendment

- **D9 — Manual classification artifact path:** `data/derived/decline_interviews_manual_classification.jsonl`. Adopt the SME-suggested path verbatim. Rationale: keeps the convention symmetry with `data/raw/decline_interviews.jsonl` (one row per `decline_interview_id`, JSONL append-friendly format that round-trips through CLI tools and pandas). The file is *derived* (regenerable), not append-only.
- **D10 — Format choice — JSONL, not CSV.** Considered CSV for human round-trip ease, rejected. JSONL keeps `manual_classification_rationale` free-text safe across embedded commas/quotes/newlines without escaping pain, matches the existing `decline_interviews.jsonl` convention, and validates row-by-row through Pydantic the same way the source records do. Mark can edit JSONL in `vim` or in a Python helper script; CSV would force quoting decisions that introduce noise.
- **D11 — Who classifies.** Mark performs the human classification per SME ruling. SME spot-checks 5–8 records (SME chooses which) and records agree/disagree. The Coder builds the *scaffolding* (validator, schema, loader, fixture, single committed seed file with empty `manual_classification` and pre-populated `decline_interview_id` rows for all 27 records), so Mark's job is to fill in classifications, not to set up infrastructure.
- **D12 — SME spot-check disposition.** SME spot-check disagreements are **not** a separate sibling column; they are surfaced in the SME verdict that reviews the artifact. If a disagreement requires changing a row, Mark amends the row in place (the file is regenerable, not append-only) and re-commits. Two-pass classification is acceptable; the post-spot-check version is the one T4 reads.
- **D13 — Coder pre-pass on obvious cases.** **Rejected.** Considered seeding the artifact with detector-flag-derived guesses ("the 11 records the SME identified as safety-event-attribution"). Rejected because (a) the SME explicitly named "Mark performs the classification" and (b) any auto-classification overlay risks re-introducing the detector-trust failure that B5 closes. The Coder seeds the file with **empty classification fields** and `decline_interview_id` plus a copy of `response_verbatim` (verbatim, for review convenience); Mark fills in the rest.
- **D14 — Detector v2 deferral.** Detector v2 design is out of scope for this amendment. Binding note B5 binds the moment any future decline-interview batch is contemplated; Phase 4a.1 has no further batches planned, so the deferral is indefinite without methodology cost.
- **D15 — `manual_classifier_id` values.** Free-form short string. Conventional values: `"mark"`, `"sme-spotcheck"`. The artifact may carry both classifications for the SME-spot-checked rows; Mark's value is the analytic truth, the SME spot-check is the audit truth, and any disagreement is logged in the SME verdict (D12).
- **D16 — Public-copy guardrails are binding on §8 text and on the inline-CONFIRMED Note K methodology-page amendment** (T5 §7 if Note K disposition is CONFIRMED-with-mechanism). Both passages must pass the Use:/Do not say: lists in Ruling 3.

---

## 3. Task list

### T3C-manual-classification — scaffold + classify artifact

**Scope:** Build `scripts/build_manual_classification_seed.py` that reads `data/raw/decline_interviews.jsonl`, emits a seed file at `data/derived/decline_interviews_manual_classification.jsonl` with one row per `decline_interview_id`, classification fields empty, and the original `response_verbatim` carried over for review convenience. Add a Pydantic model `DeclineManualClassification` to a new module `packages/cdb_analyze/cdb_analyze/manual_classification.py` (analyze-side because T4 consumes it; no LLM imports). Add a loader `load_manual_classifications(path) -> dict[str, DeclineManualClassification]` keyed by `decline_interview_id`, with strict validation: every `decline_interview_id` in the source JSONL must have a corresponding row, every row must validate, no extra rows.

After Coder lands the scaffold (commit 1 of T3C):
- Mark runs `uv run python scripts/build_manual_classification_seed.py` to generate the seed (commit 2 of T3C, file content only).
- Mark fills in the 27 classifications + rationale, commits (commit 3 of T3C).
- SME spot-checks 5–8 records and posts verdict to `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md`.
- If SME flags disagreements, Mark amends rows in place and re-commits (commit 4 of T3C, optional).

**Schema for `DeclineManualClassification` (the Coder implements exactly this):**

| Field | Type | Required | Validation |
|---|---|---|---|
| `decline_interview_id` | `str` | yes | non-empty; must exist in `decline_interviews.jsonl` |
| `manual_classification` | `Literal[...]` | yes | one of the 7 SME-prescribed enum values |
| `manual_classification_rationale` | `str` | yes | length ≤ 200 chars (Pydantic `max_length=200`); empty string forbidden |
| `manual_classifier_id` | `str` | yes | non-empty short string (e.g., `"mark"`, `"sme-spotcheck"`) |
| `response_verbatim_excerpt` | `str` | yes (in seed) | first 400 chars of source `response_verbatim`, carried over for human review convenience; **not authoritative** — T4 re-reads from source |
| `detector_flag_v1` | `bool` | yes (in seed) | the v1 detector's verdict on this row; carried over so the human classifier sees the disagreement as they classify |

The 7 enum values for `manual_classification` (verbatim from SME Ruling 1 and binding note B1):

```
- "safety_event_attribution"
- "blocked_event_attribution"
- "technical_glitch_attribution"
- "no_prior_context_acknowledgment"
- "substantive_compliance_with_empty_input"
- "other_substring_false_positive"
- "genuine_recursive_decline"
```

A Pydantic model-validator additionally enforces: if `manual_classification == "blocked_event_attribution"`, then the rationale must reference "blocked"-framing in a way the SME spot-check can verify. (This is a soft check — the validator allows the row, but adds a `validator_advisory` field if absent. The Coder may simplify to no validator advisory if it adds complexity disproportionate to the audit benefit; Architect's call: keep the type rule simple, surface advisories through the spot-check verdict, not the schema.)

**Acceptance criteria:**

*Commit 1 (Coder scaffold):*
- `scripts/build_manual_classification_seed.py` exists, runs, produces a 27-row seed file at `data/derived/decline_interviews_manual_classification.jsonl` deterministically (byte-identical on repeat runs given identical input).
- `packages/cdb_analyze/cdb_analyze/manual_classification.py` exports `DeclineManualClassification` and `load_manual_classifications`.
- `load_manual_classifications` raises a clear error if the artifact is missing a `decline_interview_id` present in source, has an extra ID, has an unrecognized enum value, has empty rationale, or has rationale > 200 chars.
- `tests/test_manual_classification.py` covers: schema valid/invalid for each enum value, rationale length boundary (200/201), empty rationale rejected, missing-row error, extra-row error, loader returns dict keyed by `decline_interview_id`.
- The test fixture has 3 hand-rolled `decline_interviews.jsonl` rows + 3 matching classification rows + a few invalid-row variants.
- The seed-builder writes `manual_classification = ""` (empty string, but validation enforces non-empty on load — the empty seed is regenerated, not loaded by T4 until Mark fills it in). Alternatively the Coder uses a sentinel like `"UNCLASSIFIED"` outside the enum and the loader rejects sentinels. Architect's preference: sentinel approach (`"UNCLASSIFIED"`) is cleaner; the loader rejects it explicitly with a "Mark must classify all 27 rows before T4 runs" error.
- No LLM imports in `cdb_analyze` (CI-enforced, but Coder verifies in unit test).
- `uv run ruff check . && uv run mypy packages/ && uv run pytest tests/test_manual_classification.py` green.

*Commit 2 (seed generation, file-only):*
- `data/derived/decline_interviews_manual_classification.jsonl` exists with 27 rows, one per `decline_interview_id` from `decline_interviews.jsonl`, all with `manual_classification == "UNCLASSIFIED"` (sentinel).
- Commit body documents that the seed is regeneration from source via `scripts/build_manual_classification_seed.py`.

*Commit 3 (Mark's classification):*
- All 27 rows have valid `manual_classification` in the 7-enum set.
- All 27 rows have non-empty `manual_classification_rationale` ≤ 200 chars.
- `manual_classifier_id` is `"mark"` for all rows (or per-row if Mark wants finer audit).
- `load_manual_classifications` returns 27 entries with no errors.
- Commit body cross-references the SME verdict at `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` Ruling 1 + Notes B1.

*Commit 4 (post-spot-check amendments, if any):*
- File diff shows only the row(s) the SME flagged, with rationale updated.
- Commit body cross-references the SME spot-check verdict file.

**Inputs:**
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl`
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (binding for enum values + classification semantics)

**Outputs:**
- `/opt/lsb-agent/scripts/build_manual_classification_seed.py` (commit 1)
- `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/manual_classification.py` (commit 1)
- `/opt/lsb-agent/tests/test_manual_classification.py` (commit 1)
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (commit 2 seed; commit 3 filled-in; optional commit 4 amendments)

**Touches `cdb_core/schemas.py`?** No. `DeclineManualClassification` lives in `cdb_analyze`, not `cdb_core`, because it is a *derived* type (computed from raw data, not raw itself). No `DATA_DICTIONARY.md` update required.

**Methodologically significant?** Yes — the schema choices implement an SME-prescribed taxonomy. The Coder plan needs CDA SME PASS before reaching the Coder. Architect routes commit 1 (the scaffold + schema) for SME plan re-review.

**Test fixture plan (Tester writes after Reviewer PASS on commit 1):**
- 3 synthetic source rows + 3 valid classification rows (one each for `safety_event_attribution`, `other_substring_false_positive`, `no_prior_context_acknowledgment`).
- Invalid-row fixtures: empty rationale, 201-char rationale, unknown enum, missing source ID, extra ID.
- Round-trip test: load → dict → re-emit → byte-equal.

**Gate chain for T3C:**
```
Architect plan (this document)
  ─► CDA SME PASS on §3 schema choices (verdict at docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md)
  ─► Coder: commit 1 (scaffold + tests)
  ─► Reviewer PASS commit 1
  ─► Tester PASS commit 1
  ─► Mark: commit 2 (seed generation, mechanical)
  ─► Reviewer PASS commit 2 (file-only review)
  ─► Mark: commit 3 (classification fill-in)
  ─► CDA SME spot-check on commit 3 (verdict at docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md)
  ─► [optional] Mark: commit 4 (amendments per SME spot-check)
  ─► Reviewer PASS final state
  ─► T4 unblocked
```

**Commit messages:**
- Commit 1: `feat(analyze): manual classification scaffold for decline interviews (task #21.T3C)`
- Commit 2: `data(analyze): seed manual classification artifact (27 rows) (task #21.T3C)`
- Commit 3: `data(analyze): manual classification of 27 decline interviews (task #21.T3C)`
- Commit 4 (if needed): `data(analyze): manual classification amendments per SME spot-check (task #21.T3C)`

**Reading list for Coder:**
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (binding — Ruling 1 + Note B1, in particular the 7-enum and the ≤200-char rationale)
- `docs/status/2026-04-23-phase4a1-t3b-run-log.md` (the substantive methodology finding context)
- `packages/cdb_core/cdb_core/schemas.py::DeclineInterview` (the source row shape)
- `CLAUDE.md` §6 rule 12 (no LLM imports in `cdb_analyze` — Coder must verify the new module is clean)
- `data/raw/decline_interviews.jsonl` (read 3–5 rows to understand the shape)

---

### T4 — Note J cross-tab + Note K re-evaluation (amended body)

**Scope:** Build `scripts/phase4a1_note_j_crosstab.py` per the prior plan, **amended** to consume the manual classification overlay for all decline-interview-derived secondary cross-tabs and to surface cross-provider replication explicitly. The primary view (`outcome_class × model_origin`) is unchanged from the prior plan and the corpus-attempt baseline + ≥2 floor + Note K re-eval logic carry forward verbatim.

**Amendments to the prior T4 body (binding notes B2, B3):**

1. **Primary view unchanged.** `outcome_class × model_origin` over the full informants + decline-interviews population, baseline = corpus collection-attempt distribution, flag if `observed >= 3 × expected AND observed >= 2`. Reads `data/raw/decline_interviews.jsonl` and `data/raw/informants.jsonl` only; does **not** consume the manual classification for the primary view.

2. **New secondary view A — manual classification × `(provider, model_id, domain)` (B2 + B3):** Cross-tab over the 27 decline-interview records, joined to `data/derived/decline_interviews_manual_classification.jsonl` by `decline_interview_id`. Rows = the 7 enum values; columns = `(provider, model_id, domain)` triples observed. Cell value = count. Surface the `safety_event_attribution` and `blocked_event_attribution` rows separately by `provider` (B3): the script emits a **named "cross-provider replication" sub-table** showing those two cohorts collapsed across models, broken out by provider. This sub-table is what T5 §8.1 cites for cross-provider replication.

3. **New secondary view B — manual classification × `model_origin`:** Same cohort, broken out by `model_origin` ∈ {us, eu, ca, cn, other}. This is the axis that lets T5 §8.2 update Note K's evidentiary basis from "CN-origin clustering" to "provider-safety-layer-on-anthropology-vocabulary, cross-provider, intersecting with CN-origin coverage."

4. **Note K re-evaluation logic — amended.** Replace `recursive_decline_count` with `safety_event_attribution_count + blocked_event_attribution_count` from the manual classification. The CONFIRMED ≥5 CN + ≥1 non-CN threshold (binding note 4) operates over the manual classification, not the detector flag. Per the SME spot-check, the expected disposition is **CONFIRMED-with-mechanism** (11 substantive safety attributions across two providers, exceeding the threshold). The Coder must implement all four dispositions (CONFIRMED / CONFIRMED-with-mechanism / INCONCLUSIVE-SUGGESTIVE / INCONCLUSIVE / NOT CONFIRMED); the actual disposition is computed by the script from the data. CONFIRMED-with-mechanism is a **new disposition** introduced by the T3B SME verdict and lives between CONFIRMED and INCONCLUSIVE-SUGGESTIVE — the trigger is "CONFIRMED thresholds met **and** the cross-provider sub-table shows ≥2 distinct providers in the safety/blocked-attribution cohort."

5. **Detector-flag-vs-manual-classification reconciliation table.** The script emits a small reconciliation table showing, for the 27 records: detector v1 flag (true/false) × manual classification (7 enums). This is the audit-trail evidence that T5 §8.0 cites verbatim.

**Acceptance criteria:**

- Script runs deterministically. Byte-equal output on a fixed input.
- Reads three files: `data/raw/decline_interviews.jsonl`, `data/raw/informants.jsonl`, `data/derived/decline_interviews_manual_classification.jsonl`. Errors clearly if the manual classification artifact is missing, has any `"UNCLASSIFIED"` rows, or fails `load_manual_classifications` validation.
- Emits the 2D primary cross-tab + secondary view A (manual × provider/model/domain) + secondary view A's cross-provider replication sub-table + secondary view B (manual × origin) + reconciliation table + Note K verdict line with supporting numerics.
- Output is human-readable Markdown to stdout (the same format T5 will quote verbatim) plus a `--json` flag that emits the same content as structured JSON for programmatic consumption.
- Fixture-based test: synthetic `decline_interviews.jsonl` + matching manual classification + a fixture `informants.jsonl`. Fixtures cover all four Note K dispositions across separate test cases.
- No LLM imports in `cdb_analyze`. Script lives in `scripts/`, imports from `cdb_analyze`, fine.

**Inputs:**
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl`
- `/opt/lsb-agent/data/raw/informants.jsonl`
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (T3C output)

**Outputs:**
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py`
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py`

**Touches `cdb_core/schemas.py`?** No.

**Methodologically significant?** **The plan body is mechanical from B2/B3.** No fresh SME re-review of the *plan*. The T4 *output* is SME-gated per binding note 4 and remains so — CDA SME PASS required on the script's output before T5 begins. SME verdict at `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`.

**Test fixture plan:**
- Synthetic 27-record source + matching classification.
- One fixture per Note K disposition (CONFIRMED-with-mechanism, INCONCLUSIVE-SUGGESTIVE, INCONCLUSIVE, NOT CONFIRMED).
- Cross-provider replication test: ensure ≥2 distinct providers in the safety/blocked cohort triggers the CONFIRMED-with-mechanism path.
- Reconciliation table test: detector_flag × manual_classification matrix is reported correctly.

**Gate chain for T4:**
```
Architect plan (this document; mechanical from B2/B3)
  ─► Coder
  ─► Reviewer PASS
  ─► Tester PASS
  ─► CDA SME PASS on output (verdict at docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md)
  ─► T5 unblocked
```

**Commit message:** `feat(scripts): T4 Note J cross-tab consuming manual classification (task #21.T4)`

**Reading list for Coder:**
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (binding — Rulings 1, 2 + Notes B2, B3, B4)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (binding notes 2, 3, 4 — primary view, baseline, Note K logic)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8, especially A3 empty-response cohort axis)
- `data/raw/decline_interviews.jsonl` (the 27 source rows)
- `data/derived/decline_interviews_manual_classification.jsonl` (the analytic axis — must exist before T4 runs)

---

### T5 — Completion report + Note K disposition (amended body)

**Scope:** Write `docs/status/2026-04-30-phase4a1-completion-report.md` (note the date update — the report is dated when T5 is written, not the original 2026-04-23 plan kickoff date). All 9 sections from the prior plan remain required. **Section 8 is replaced** by the SME-mandated 5-subsection structure from Ruling 3 + Note B6.

**Required structure for §8 (verbatim from Ruling 3, Coder cannot reorganize):**

1. **§8.0 — Detector flag audit (raw, append-only).** Quote the verdict's prescribed framing language directly. Cite the `(detector_flag × manual_classification)` reconciliation table from T4. State that "the stored flag values are preserved as the audit record of v1 behavior. Manual classification (§8.1) replaces the flag values for analytic purposes."

2. **§8.1 — Manual classification (analytic).** Enumerate the 27 records by `decline_interview_id` and classification category (per binding note A5's enumerate-by-identifier requirement). Counts per category. Cross-tab to `(model_id, domain, provider)` for the `safety_event_attribution` and `blocked_event_attribution` cohorts (the cross-provider sub-table from T4 secondary view A).

3. **§8.2 — Note K disposition.** Per Ruling 2. The expected disposition is CONFIRMED-with-mechanism, framed as provider-safety-layer-on-anthropology-vocabulary, cross-provider replication explicit, coverage-caveat framing per binding note 5 (carry-forward). The methodology-page amendment language goes here, gated by the public-copy guardrails (see below).

4. **§8.3 — Detector v2 forward note.** Brief paragraph: "The v1 recursive-decline detector requires a successor design for any future decline-interview batch. The successor is out of scope for Phase 4a.1 T5; binding note B5 binds any future batch to fresh SME methodology review of the output-classification detector before execution."

5. **§8.4 — Audit trail pointers.** Paths to: `data/derived/decline_interviews_manual_classification.jsonl`, `docs/status/2026-04-23-phase4a1-t3b-run-log.md`, `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md`, the binding-note 6 threshold-non-trigger reasoning (cite Ruling 2 directly).

**Public-copy guardrails (binding on §8 entire and §7 if Note K is CONFIRMED-with-mechanism). Reproduced verbatim from Ruling 3:**

- **Use:** "The v1 recursive-decline detector was miscalibrated for natural-language follow-up responses; manual classification of the 24 follow-up records replaces the detector flag for analytic purposes."
- **Use:** "Eleven of 24 follow-up responses contain direct, model-reported attribution of the original empty-response to the provider's safety or content-policy layer. This pattern surfaces across two providers (Google Gemini and z-ai glm-5.1) on the family and holidays domains."
- **Do not say:** "The model believes its safety filter was triggered." Replace with: "The model's follow-up output attributes the original empty-response to the provider's safety filter."
- **Do not say:** "75% of follow-ups were recursive declines." Replace with: "0 of 24 follow-up responses were themselves declines; the v1 detector's 75% flag rate was a substring-matching artifact and is preserved in the audit record but does not represent a methodological event."
- **Do not say:** "China-origin models have categorically different worldviews about family." Replace with the provider-safety-layer mechanism per Ruling 2.
- **Do not say:** "publishable" or "publishable finding." This is a methodology-page contribution.

**The "mismatch is the finding" framing must be present in §8.0** (per Ruling 3 final paragraph). The detector-flag-vs-actual-event mismatch is itself audit-trail evidence about how a v1-frozen instrument behaves when reused across semantic boundaries.

**Other §8 sections (unchanged from prior plan):**
- §1 Timeline
- §2 Gate summary (now includes T3B-detector verdict + this amendment + T3C SME verdicts + T4 SME verdict)
- §3 Artifacts (now includes `data/derived/decline_interviews_manual_classification.jsonl`)
- §4 Cost accounting (unchanged: $5.16 cumulative)
- §5 Input set reconciliation (now includes T3C scope and the 24+3 = 27 manual-classification population)
- §6 Note J cross-tab (T4 verbatim output)
- §7 Note K disposition (CONFIRMED-with-mechanism per Ruling 2; methodology-page amendment language passes the public-copy guardrails)
- §9 Re-analysis decision (carried forward from prior plan; specific numerics per binding note 7)

**Acceptance criteria:**

- Report at the named path; all 9 sections present; §8 has the 5 subsections in the prescribed order.
- §8.0 quotes the prescribed framing language verbatim or paraphrases without semantic loss.
- §8.0 explicitly names the "mismatch is the finding" framing.
- §8.1 enumerates the 27 records by `decline_interview_id` with classification category. Cross-provider sub-table reproduced from T4.
- §8.2 applies Ruling 2's CONFIRMED-with-mechanism framing.
- §8.3 names binding note B5 as the gate for any future detector-v2 work.
- §8.4 has all 4 path pointers.
- No forbidden vocabulary (CLAUDE.md §7 + ARCHITECTURE.md §1.5.4): "worldview", "believes", "thinks" applied to models all forbidden; SME guardrail Use:/Do not say: list enforced.
- Report passes a manual grep against the Do not say: list before commit.
- Cross-references complete: this amendment, T3C SME verdicts, T4 SME verdict, T3B detector SME verdict, prior amendment + plan + SME verdicts.

**Inputs:**
- T4 output (Markdown + JSON)
- All gate verdict files in the chain
- `data/derived/decline_interviews_manual_classification.jsonl`
- Prior completion-report drafts (none yet — this is the first)

**Outputs:**
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-completion-report.md`

**Touches `cdb_core/schemas.py`?** No.

**Methodologically significant?** Yes for §8 — output is SME-gated per binding note B6 and Ruling 3. Plan body is fully prescribed by Ruling 3, so no fresh SME plan re-review; T5 *output* SME gate at completion is binding. SME verdict at `docs/status/2026-04-30-phase4a1-t5-cda-sme-verdict.md` will check §8 against the verdict's binding notes and Ruling 3 guardrails.

**Test fixture plan:** Not applicable (this is a documentation task, not code).

**Gate chain for T5:**
```
Architect plan (this document; §8 fully prescribed by Ruling 3)
  ─► Coder (technical writing)
  ─► Reviewer PASS (vocabulary + cross-references + structure check)
  ─► CDA SME PASS on §8 + §7 against Ruling 3 guardrails (verdict at docs/status/2026-04-30-phase4a1-t5-cda-sme-verdict.md)
  ─► Phase 4a.1 closed
  ─► Memory update: project_cn_decline_clustering_phase4a.md per SME's "memory updates pending" note
```

**Commit message:** `docs(status): Phase 4a.1 completion report + Note K CONFIRMED-with-mechanism (task #21.T5)`

**Reading list for Coder:**
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (binding — Rulings 1, 2, 3 + Notes B1–B6, **Ruling 3 verbatim**)
- All prior verdicts in the chain
- `T4 output` (T5 quotes from it)
- `CLAUDE.md` §7 forbidden vocabulary
- `ARCHITECTURE.md` §1.5.4 language guardrails

---

## 4. Dependency graph

```
T3C commit 1 (scaffold + tests)
  ─► (CDA SME PASS on schema)
  ─► Coder, Reviewer, Tester
T3C commit 2 (seed file generation, mechanical)
T3C commit 3 (Mark classifies 27 rows)
  ─► (CDA SME spot-check verdict)
T3C commit 4 (optional, post-spot-check amendments)
  │
  ▼
T4 (Coder writes script consuming the artifact)
  ─► Reviewer, Tester
  ─► CDA SME PASS on T4 output
  │
  ▼
T5 (Coder writes completion report including §8)
  ─► Reviewer
  ─► CDA SME PASS on §8 + §7 guardrails
  │
  ▼
Phase 4a.1 closed
```

T3C commit 1 may not start until SME PASS on §3 schema choices in this amendment. T4 may not start until T3C commit 3 (or commit 4) is on master. T5 may not start until T4 SME PASS.

---

## 5. Open questions for Mark

1. **D11 — who classifies confirmation.** The SME mandated Mark; Architect concurs. Confirming you intend to do the classification yourself. If you want to delegate to the SME, that changes the gate chain (SME does commit 3, you spot-check on commit 4).

2. **D13 — Coder pre-pass rejection.** Architect has rejected seeding the artifact with detector-derived guesses. If you want a different policy (e.g., "Coder pre-fills the 5 obvious `other_substring_false_positive` rows the SME identified, Mark fills in the rest"), this is your call. Architect's recommendation is no pre-pass — keep the human classification clean.

3. **D15 — `manual_classifier_id` per-row vs. uniform.** Architect's default is `"mark"` for all 27 rows. If the SME spot-check changes any rows in commit 4, those rows get `"sme-spotcheck"`. If you'd prefer a different convention (e.g., concatenation `"mark|sme-confirmed"`), let the Architect know before T3C commit 1 lands.

4. **T3C commit count.** Architect's plan has up to 4 commits per the §8 "one commit per task" discipline. The CLAUDE.md §8 exception for "schema changes" applies to `cdb_core/schemas.py`; T3C lives in `cdb_analyze`, so direct-to-master is fine. If you want T3C bundled differently (e.g., commits 2+3 combined into a single commit with subject `data(analyze): seed + classify manual classification artifact`), that's a §8-defensible choice. Architect's recommendation: keep the 4-commit shape because commit 1 is Coder, commits 2–4 are Mark, and the role boundary makes review cleaner.

5. **Detector v2 deferral horizon.** Architect's read is "indefinite without methodology cost" because no future decline-interview batch is planned. If Phase 4b/4c/5 plans contemplate a future batch, the detector v2 design needs to land before that batch. Confirming you don't want detector v2 scoped into Phase 4a.1.

---

## 6. Carry-forward — all 22 binding notes still in force

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force, applied per prior plan |
| A1–A8 from Amendment 1 | All in force, applied per Amendment 1 |
| B1 manual classification artifact | Decomposed in this amendment as T3C |
| B2 T4 axis = manual classification, not detector flag | Decomposed in this amendment as T4 secondary view A |
| B3 T4 cross-provider replication explicit | Decomposed in this amendment as T4 cross-provider sub-table |
| B4 future detector-flag thresholds require precision-on-corpus | Binding precedent; no Phase 4a.1 action |
| B5 SME A6 gate extended to detector role-changes | Binding precedent; no Phase 4a.1 action |
| B6 T5 §8 5-subsection structure + public-copy guardrails | Decomposed in this amendment as T5 §8 |

Detector v2 design (item 4 of "Forward action for Architect" in the verdict) is **deferred** indefinitely per D14. Memory update (`project_cn_decline_clustering_phase4a.md`) per item 5 happens after T5 lands; not blocking T5.

---

## 7. Files (absolute paths)

Inputs:
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl` (27 rows; T3C reads)
- `/opt/lsb-agent/data/raw/informants.jsonl` (T4 reads)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (binding for T3C, T4, T5)
- All prior verdicts and plan documents in the gate chain

Outputs:
- `/opt/lsb-agent/scripts/build_manual_classification_seed.py` (T3C commit 1)
- `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/manual_classification.py` (T3C commit 1)
- `/opt/lsb-agent/tests/test_manual_classification.py` (T3C commit 1)
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (T3C commits 2–4)
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (T4)
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py` (T4)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-completion-report.md` (T5)

Gate verdict files (created as pipeline progresses):
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md` (this doc)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (required before T3C commit 1)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (SME spot-check on commit 3)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t3c-reviewer-verdict.md`
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t4-reviewer-verdict.md`
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t5-reviewer-verdict.md`
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t5-cda-sme-verdict.md`

---

## 8. Summary for Mark

- **Phase 4a.1 picks up at T3C** — a new sub-task that scaffolds + populates the manual classification artifact per SME Ruling 1 + Note B1.
- **T3C is 4 commits:** Coder scaffold + tests, mechanical seed-file generation, your 27-row classification, optional post-SME-spot-check amendments. Up to ~$0 spend.
- **T4 reads the manual classification** as the secondary axis (B2) and surfaces cross-provider replication explicitly (B3). Note K is expected to land at CONFIRMED-with-mechanism (a new disposition introduced by the T3B verdict).
- **T5 §8 has 5 subsections** with public-copy guardrails reproduced verbatim from Ruling 3. The "mismatch is the finding" framing is required.
- **Required gate before Coder starts T3C commit 1:** CDA SME PASS or PASS-WITH-NOTES on §3 schema choices in this amendment, especially the seed-file format (JSONL) and the `"UNCLASSIFIED"` sentinel approach.
- **No new schema changes; no `DATA_DICTIONARY.md` updates.** All work is in `cdb_analyze` + `scripts/` + `data/derived/`.
- **Detector v2 deferred indefinitely** — binding note B5 binds future batches; no future batch is planned.
- **Open questions §5** flagged for your call before T3C commit 1 lands.

---

*End of Architect Plan Amendment 2. Binding for T3C through T5 unless a subsequent amendment supersedes. All 22 prior binding notes remain in force; this amendment is additive. Coder may NOT start T3C commit 1 until CDA SME verdict on §3 is recorded.*
