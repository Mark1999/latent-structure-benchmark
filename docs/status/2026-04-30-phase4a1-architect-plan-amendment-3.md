# Phase 4a.1 — Architect Plan Amendment 3 (task #21)

**Date:** 2026-04-30
**Planner:** Architect
**Task:** #21 (Phase 4a.1 decline-interview backfill) — AMENDMENT 3
**Scope of amendment:** Binding note **B11** (T3C SME verdict, 2026-04-30) only. This is a focused additive delta to the T4 task body in Amendment 2 §3. T3C is closed (commit `b81462d`, SME PASS at commit `13eff78`). T1, T2, T3A, T3B, T3C, T5 bodies are unchanged.
**Supersedes partially:** `docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md` §3 T4 sub-section — only the additions specified below. All other content of Amendment 2 (and prior plans) carries forward verbatim.
**Carries forward:** All **28** binding notes in force after the T3C SME spot-check verdict (8 original + A1–A8 + B1–B12). This amendment is **additive**.

**Trigger:** The T3C SME spot-check verdict (`docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md`) issued PASS on the 27-row manual classification artifact and added three new binding notes: B10 (soft, future batches), **B11 (binding on T4)**, B12 (binding precedent for future batches). B11 names an empirical sub-structure within the `safety_event_attribution` bucket that T4 is positioned to surface but Amendment 2 §3 does not yet plan. This amendment closes that gap.

**Predecessor gate verdicts (still binding, full chain):**
- `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md` (Notes F, G, H, I, J)
- `docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md` (8 binding notes; binding note 4 = Note K thresholds)
- `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (A1–A8)
- `docs/status/2026-04-23-phase4a1-t3b-detector-sme-verdict.md` (B1–B6, three rulings, T5 §8 public-copy guardrails)
- `docs/status/2026-04-30-phase4a1-amendment-2-cda-sme-verdict.md` (B7, B8, B9)
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B10, B11, B12)

**Gate verdict chain for this amendment:**
- Architect decomposition (this document)
- **CDA SME PASS / PASS-WITH-NOTES required** on §3 T4 delta. Architect read: B11 is a methodology rule introduced by the SME at the T3C spot-check; T4's operationalization of B11 — both the *what* (sub-axis content) and the *how* (computation source, output surface, Note K disposition framing) — is the SME's call. The mechanical-from-prior-verdict reasoning that exempted Amendment 2 §3 T4 from a fresh plan re-review does **not** apply here: B11 is novel to T3C and its translation into a T4 deliverable is a methodology decision, not a mechanical realization. Verdict path: `docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md`.

**No new schema changes.** No edits to `cdb_core/schemas.py`. No edits to `decline_detection.py`. The K-vocab/K-frame sub-axis is computed at T4 analysis time and lives in the T4 output (Markdown + JSON) plus, optionally, a small derived artifact under `data/derived/`.

**No `DATA_DICTIONARY.md` update.** Per the no-`cdb_core` rule above and Reviewer rule R7 (which fires on `cdb_core/schemas.py` changes only).

**Expected spend:** $0 — no API calls. Cumulative Phase 4a + 4a.1 spend stays at $5.16.

---

## 1. Summary

The T3C manual classification artifact, plus the SME spot-check, surfaced a sub-structure within the 9 `safety_event_attribution` rows: 5 of 9 carry **AI-vs-human-research-subject framing** language ("cognitive anthropology study", "act as a participant", "I am a tool, not a person"); 4 of 9 carry **safety vocabulary keyed to list-comprehensiveness/sensitivity** without the AI-vs-human framing ("uncurated comprehensive list", "potentially unsafe raw data dump", "sensitive topics"). The SME calls these **K-frame** (the 5) and **K-vocab without K-frame** (the 4). B11 binds T4 to surface this split as a sub-axis of the `safety_event_attribution` bucket without re-opening the 7-enum.

This amendment adds **one new sub-deliverable** to T4 (the `safety_attribution_subtype` cross-tab + Note K mechanism refinement) and updates the Note K disposition framing accordingly. T4's other components from Amendment 2 §3 (primary view, secondary view A, secondary view B, reconciliation table, Note K disposition logic for the four-disposition tree) are unchanged.

Mark's signal in auto-memory ("T4 = Note J cross-tab + Note K re-eval (split K-vocab vs K-frame per B11)") is the disposition driver: include the split in T4, do not defer.

---

## 2. Architect dispositions for this amendment (continuing numbering from D16)

- **D17 — K-vocab/K-frame computation source: hand-coded by Mark, recorded in a sibling derived artifact.** Considered three options:
  1. **Coder-derived from verbatim text via keyword/regex helper.** Rejected. The K-frame trigger is a semantic distinction ("the model attributes the safety event to AI-vs-human-research-subject framing" vs. "the model attributes the safety event to list-comprehensiveness/sensitivity"). Keyword matching ("cognitive anthropology", "research subject", "act as a participant") would catch the obvious K-frame rows but would risk false negatives where the framing is paraphrased and false positives where the phrase appears in the *prompt* description but not as the *trigger attribution* (cf. row `8a31425b` — contains "cognitive anthropology study" verbatim but is `technical_glitch_attribution`, not safety). The B5 precedent — output-classification detectors are gated for fresh SME review — also weighs against unilaterally adding a regex classifier here.
  2. **Mark hand-codes a K-frame label in a new column on the existing `decline_interviews_manual_classification.jsonl`.** Rejected. The artifact is committed, SME-PASSed, and frozen. Adding a column re-opens the schema, requires reloading the strict loader, and risks invalidating the existing PASS verdict's audit trail.
  3. **Mark hand-codes the K-frame labels in a new sibling derived artifact, keyed by `decline_interview_id`.** **Adopted.** Path: `data/derived/decline_interviews_safety_attribution_subtype.jsonl`. One row per `decline_interview_id` for each of the 9 `safety_event_attribution` rows (and only those — the artifact is sparse; non-safety rows are absent). Schema: `{decline_interview_id, safety_attribution_subtype, subtype_rationale, subtype_classifier_id}` where `safety_attribution_subtype ∈ {"k_frame", "k_vocab_without_k_frame"}`. The artifact is derived (regenerable, not append-only), small enough to be tractable for hand-coding, and isolated from the primary classification artifact so the existing T3C verdict is unaffected.

- **D18 — Coder scaffolds the new sibling artifact under T4, before the cross-tab script consumes it.** The Coder's T4 work splits into two ordered commits:
  - **T4.1 (scaffold):** A new module `cdb_analyze/safety_subtype.py` exporting `SafetyAttributionSubtype` (Pydantic model) and `load_safety_attribution_subtypes(path) -> dict[str, SafetyAttributionSubtype]`. A small seed-builder `scripts/build_safety_subtype_seed.py` that reads `data/derived/decline_interviews_manual_classification.jsonl`, filters to the 9 `safety_event_attribution` rows, and emits a seed with `safety_attribution_subtype="UNCLASSIFIED"` (sentinel). Tests under `tests/test_safety_subtype.py`.
  - **Mark hand-codes the 9 rows** between T4.1 and T4.2.
  - **T4.2 (cross-tab):** The `scripts/phase4a1_note_j_crosstab.py` script (Amendment 2 §3 T4 body) is extended to consume the subtype artifact and emit the new sub-axis output specified in §3 below. If the subtype artifact is absent or has any `"UNCLASSIFIED"` rows, the script errors with a clear message naming the missing rows by `decline_interview_id`.

- **D19 — Where the sub-axis enters the T4 output: a new sub-table within secondary view A, plus an additive note on the Note K disposition string.** The sub-axis is *not* a top-level T4 view; it is a refinement within the existing secondary view A's safety/blocked cohort sub-table. Specifically: the cross-provider replication sub-table that breaks `safety_event_attribution + blocked_event_attribution` rows by provider gets a new column `safety_attribution_subtype` (values: `k_frame`, `k_vocab_without_k_frame`, `n/a` for `blocked_event_attribution` rows). Counts are reported by `(provider, subtype)`. The Note K disposition string in T4's output is amended per D20 below to name the mechanism split.

- **D20 — Note K disposition framing in T4 output: name the K-frame/K-vocab mechanism split in the disposition string itself.** Per Ruling 2 of the T3B verdict + B11, the expected disposition is **CONFIRMED-with-mechanism**. The mechanism string from Amendment 2 ("provider-safety-layer-on-anthropology-vocabulary, cross-provider, intersecting with CN-origin coverage") is amended to name the bipartite mechanism explicitly: **"provider-safety-layer activation with two co-present trigger patterns — (a) AI-vs-human-research-subject framing (K-frame; N=5), (b) list-comprehensiveness/sensitivity vocabulary without K-frame (K-vocab; N=4) — cross-provider replication on the family and holidays domains."** T4 emits this mechanism string as part of its Note K disposition output; T5 §8.2 carries it through to the methodology-page amendment, gated by the public-copy guardrails from Ruling 3.

- **D21 — Disposition arithmetic does not change.** The Note K disposition logic from Amendment 2 (CONFIRMED ≥5 substantive safety attributions across providers; CONFIRMED-with-mechanism if cross-provider sub-table shows ≥2 distinct providers) operates on the *parent* `safety_event_attribution + blocked_event_attribution` count (9 + 0 = 9, exceeds 5; cross-provider ≥2 confirmed, both Google Gemini and z-ai/glm-5.1 represented). The K-frame/K-vocab split is **descriptive of the mechanism**, not part of the disposition trigger arithmetic. T4 does not introduce a "K-frame ≥ N triggers a different disposition" rule — that would be over-fitting to a 9-row corpus. If the K-frame split is asymmetric across providers (e.g., all 5 K-frame rows are Gemini, all 4 K-vocab rows are glm-5.1, hypothetical), T4 surfaces that observation in the output Markdown but does not let it shift the disposition tier.

- **D22 — T5 §8 framing for the K-vocab/K-frame distinction: in §8.2 (Note K disposition), not §8.0 (detector audit) or §8.4 (audit trail).** The mechanism description is part of the disposition framing, where it belongs methodologically. §8.0 is detector-flag audit; §8.4 is audit-trail pointers; neither is the right place. T5 §8.2's mechanism string carries D20's revised wording verbatim, with the K-frame and K-vocab counts (5 and 4) reported. **T5 §8 structure is otherwise unchanged from Amendment 2.**

---

## 3. T4 task body delta (additive only)

The following are additions to Amendment 2 §3 T4. Everything in Amendment 2 §3 T4 not amended below carries forward verbatim. Numbering of the bullets in Amendment 2 §3 T4 is preserved; the additions are interleaved as new bullets and clearly marked as **ADDITION (Amendment 3)**.

### 3.1 New sub-task T4.1 — Safety attribution subtype scaffold (precedes T4.2 cross-tab)

**Scope (ADDITION):** Build the scaffolding for the sibling derived artifact `data/derived/decline_interviews_safety_attribution_subtype.jsonl` per D17. Coder lands the scaffold and tests; Mark hand-codes the 9 rows; T4.2 consumes.

**Schema for `SafetyAttributionSubtype`:**

| Field | Type | Required | Validation |
|---|---|---|---|
| `decline_interview_id` | `str` | yes | non-empty; must exist in `decline_interviews_manual_classification.jsonl` AND have `manual_classification == "safety_event_attribution"` in that file |
| `safety_attribution_subtype` | `Literal["k_frame", "k_vocab_without_k_frame"]` | yes | one of the two values; sentinel `"UNCLASSIFIED"` allowed in seed only, rejected by loader |
| `subtype_rationale` | `str` | yes | length ≤ 200 chars (Pydantic `max_length=200`); empty string forbidden |
| `subtype_classifier_id` | `str` | yes | non-empty short string; conventional value `"mark"` |

The Pydantic model includes a model-validator that joins to the parent `decline_interviews_manual_classification.jsonl` at load time and refuses to load if any row's `decline_interview_id` does not have `manual_classification == "safety_event_attribution"` in the parent. This is the "you can't subtype a non-safety row" invariant.

**B11-driven definitions for the two subtypes (binding on hand-coding rationale):**

- **`k_frame`** — The model's attribution narrative names AI-vs-human-research-subject framing as the trigger. Canonical phrases (non-exhaustive): "cognitive anthropology study", "act as a participant", "human research subject", "I am a tool, not a person", "act like a human". The framing-as-trigger element is the discriminator; mere appearance of "cognitive anthropology" in the prompt description (without it being named as the trigger) is **not** sufficient.
- **`k_vocab_without_k_frame`** — The model's attribution narrative names list-comprehensiveness, list-sensitivity, or vocabulary-policy as the trigger, **without** the AI-vs-human-research-subject framing element. Canonical phrases (non-exhaustive): "uncurated comprehensive list", "potentially unsafe raw data dump", "list will start to include sensitive...topics", "massive and culturally sensitive", "biased, incomplete, or otherwise problematic".

These definitions are paraphrased from the SME's row-level discussion in the T3C verdict (rows 4 and 5). Mark refers to that discussion when hand-coding; rationales should follow the operational B7 reading (reference the verbatim framing language present in the source `response_verbatim`).

**Acceptance criteria (T4.1):**

*Coder commit (scaffold + tests):*
- `packages/cdb_analyze/cdb_analyze/safety_subtype.py` exports `SafetyAttributionSubtype` and `load_safety_attribution_subtypes`.
- `scripts/build_safety_subtype_seed.py` reads the manual classification artifact, filters to `safety_event_attribution` rows, emits seed at `data/derived/decline_interviews_safety_attribution_subtype.jsonl` with 9 rows, all `safety_attribution_subtype="UNCLASSIFIED"`, deterministic (byte-identical on repeat runs).
- `tests/test_safety_subtype.py` covers: valid for both subtype values, sentinel rejected by loader, parent-classification join enforced (row with non-safety parent rejected), missing parent-classification artifact errors clearly, ≤200-char rationale boundary, empty rationale rejected, the build script emits exactly the 9 rows for the in-tree fixture.
- The fixture has 4–5 hand-rolled `manual_classification` rows (mix of safety and non-safety) + 2–3 matching subtype rows + invalid-row variants.
- No LLM imports in `cdb_analyze` (CI-enforced).
- `uv run ruff check . && uv run mypy packages/ && uv run pytest tests/test_safety_subtype.py` green.

*Mark hand-codes commit:*
- All 9 rows have `safety_attribution_subtype` ∈ `{"k_frame", "k_vocab_without_k_frame"}`.
- All 9 rows have non-empty `subtype_rationale` ≤ 200 chars, referencing the verbatim trigger-attribution language present in the source `response_verbatim`.
- `subtype_classifier_id` is `"mark"` for all rows.
- `load_safety_attribution_subtypes` returns 9 entries with no errors.
- Commit body cross-references this amendment, the T3C SME verdict (B11), and the Amendment 2 plan.
- **Expected distribution per the SME verdict:** 5 `k_frame`, 4 `k_vocab_without_k_frame`. Drift from this distribution is acceptable but should be noted in the commit body for SME spot-check awareness.

**Inputs:**
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (read-only)
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl` (read-only — the source `response_verbatim` for hand-coding reference)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (binding for definitions, especially the row-4 and row-5 discussion)

**Outputs:**
- `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/safety_subtype.py` (Coder commit)
- `/opt/lsb-agent/scripts/build_safety_subtype_seed.py` (Coder commit)
- `/opt/lsb-agent/tests/test_safety_subtype.py` (Coder commit)
- `/opt/lsb-agent/data/derived/decline_interviews_safety_attribution_subtype.jsonl` (Coder seed commit + Mark hand-codes commit; 9 rows total)

**Touches `cdb_core/schemas.py`?** No.
**`DATA_DICTIONARY.md` update required?** No (the new schema lives in `cdb_analyze`, not `cdb_core`).
**Methodologically significant?** Yes — the schema implements an SME-prescribed sub-classification (B11). The plan needs CDA SME PASS via the gate verdict for this amendment before the Coder starts.

**Test fixture plan (Tester):** 4–5 synthetic manual-classification rows + 2–3 matching subtype rows; valid/invalid pairs across the validator (parent-join, sentinel rejection, length, enum); round-trip test (load → dict → re-emit → byte-equal).

**Gate chain for T4.1:**
```
Architect Amendment 3 (this document)
  ─► CDA SME PASS on §3 (verdict at docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md)
  ─► Coder: T4.1 scaffold + tests
  ─► Reviewer PASS
  ─► Tester PASS
  ─► Mark: hand-code 9 rows
  ─► [optional] CDA SME spot-check on the subtype artifact (Architect's call: this is parallel to the T3C spot-check pattern; recommended but not blocking T4.2 unless the spot-check is requested by the SME at gate-review time)
  ─► T4.2 unblocked
```

**Commit messages:**
- Coder: `feat(analyze): safety attribution subtype scaffold (task #21.T4.1)`
- Mark: `data(analyze): hand-code k-frame/k-vocab subtype on 9 safety rows (task #21.T4.1)`

### 3.2 T4.2 — Note J cross-tab (Amendment 2 §3 T4) — additions only

Everything in Amendment 2 §3 T4 carries forward unchanged unless explicitly amended below.

**ADDITION to bullet 2 (secondary view A — manual classification × `(provider, model_id, domain)`):** The cross-provider replication sub-table that breaks `safety_event_attribution + blocked_event_attribution` rows by provider gets a new column `safety_attribution_subtype`. Cell values for `safety_event_attribution` rows are `k_frame` or `k_vocab_without_k_frame` (joined from the new artifact); cell values for `blocked_event_attribution` rows are `n/a` (the subtype does not apply to that bucket — the artifact only contains `safety_event_attribution` rows by D17 invariant). Counts are reported by `(provider, subtype)` in a small additional table immediately below the existing cross-provider sub-table.

**ADDITION to bullet 4 (Note K re-evaluation logic):** Per **D21**, the K-frame/K-vocab split does **not** affect the disposition arithmetic. The disposition tree (CONFIRMED / CONFIRMED-with-mechanism / INCONCLUSIVE-SUGGESTIVE / INCONCLUSIVE / NOT CONFIRMED) operates over `safety_event_attribution_count + blocked_event_attribution_count` as Amendment 2 specified. The Note K disposition string emitted by T4 is amended per **D20** to carry the bipartite mechanism description verbatim (see D20 for exact wording). The disposition string is the headline output line; the K-frame/K-vocab counts (5 and 4 expected) are reported in the supporting numerics line directly below the disposition.

**ADDITION to acceptance criteria:**
- T4.2 reads four files (was three): `data/raw/decline_interviews.jsonl`, `data/raw/informants.jsonl`, `data/derived/decline_interviews_manual_classification.jsonl`, **and `data/derived/decline_interviews_safety_attribution_subtype.jsonl`**. Errors clearly if the subtype artifact is missing, has any `"UNCLASSIFIED"` rows, fails `load_safety_attribution_subtypes` validation, or has a `decline_interview_id` not present in the manual classification artifact.
- The cross-provider replication sub-table includes the `safety_attribution_subtype` column for safety rows.
- A new "Note K mechanism breakdown" sub-section in the output Markdown reports `(provider, subtype)` counts for the safety cohort. Two-row format minimum: one row per subtype, columns are providers represented in the cohort.
- The Note K disposition string in the output names both subtypes and their counts per D20.
- Test fixture coverage adds a synthetic 9-row safety cohort split 5/4 across the two subtypes, distributed across two providers, to exercise the new sub-table and the disposition string.

**ADDITION to inputs:**
- `/opt/lsb-agent/data/derived/decline_interviews_safety_attribution_subtype.jsonl` (T4.1 output)

**Methodological significance unchanged.** Per Amendment 2: "the plan body is mechanical from B2/B3" — that read is preserved for the bulk of T4.2. The Amendment-3 additions are mechanical from B11 + D17–D22 (i.e., the methodology decisions in this amendment); the SME PASS on this amendment is the gate, no separate fresh review of the *T4.2 plan* is needed. **The T4.2 *output* is SME-gated per binding note 4 and remains so** — CDA SME PASS required on the script's output before T5 begins. Output verdict path is unchanged from Amendment 2: `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md`.

**Commit message (T4.2):** `feat(scripts): T4 Note J cross-tab + K-frame/K-vocab subtype (task #21.T4.2)` (Amendment 2's `feat(scripts): T4 Note J cross-tab consuming manual classification (task #21.T4)` is superseded by this Amendment-3 version.)

**Reading list for Coder (additions):**
- `docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (binding — B11 in particular; row-4 and row-5 row-level discussion ground the K-frame/K-vocab definitions)
- This document (the Amendment 3 plan)

### 3.3 T5 §8 task body — additive only

Amendment 2 §3 T5 §8 structure is unchanged. Per **D22**, the only addition is to §8.2:

**ADDITION to §8.2 acceptance criteria:** §8.2's mechanism description carries D20's bipartite mechanism string verbatim ("provider-safety-layer activation with two co-present trigger patterns — (a) AI-vs-human-research-subject framing (K-frame; N=5), (b) list-comprehensiveness/sensitivity vocabulary without K-frame (K-vocab; N=4) — cross-provider replication on the family and holidays domains"), with N values updated from the actual T4 output if Mark's hand-coding produces a different distribution. The mechanism description is gated by the existing Ruling 3 public-copy guardrails — no "worldview/believes/thinks" applied to models, no claim that K-frame "is what the model thinks". The framing is **what the model's output *attributes* the safety event to**, not what the model believes.

**No changes to T5 §8.0, §8.1, §8.3, §8.4** beyond what Amendment 2 already specifies.

---

## 4. Acceptance criteria additions (cumulative for T4 under Amendment 3)

For the T4 stage to be considered complete (covering both T4.1 and T4.2):

- T4.1 scaffold lands with Reviewer PASS + Tester PASS.
- Mark's hand-coded subtype artifact is on master.
- T4.2 cross-tab script lands and produces output that:
  - Includes the cross-provider replication sub-table from Amendment 2.
  - **Adds the `safety_attribution_subtype` column to the safety/blocked rows in that sub-table.**
  - **Adds a "Note K mechanism breakdown" sub-section reporting `(provider, subtype)` counts.**
  - **Emits the Note K disposition with the bipartite mechanism string (D20) as the headline.**
- T4.2 output passes the CDA SME output-gate per binding note 4 and Ruling 3.
- All test fixtures cover the new subtype axis (synthetic 9-row safety cohort split 5/4 across subtypes, distributed across two providers).
- No forbidden vocabulary in any output text (Reviewer enforces).

---

## 5. Gate chain for this amendment

**B11 is methodologically significant** (it is a methodology rule introduced by the SME at T3C, and its T4 operationalization includes non-mechanical decisions D17–D22 about computation source, output surface, and disposition framing). Therefore:

```
Architect Amendment 3 (this document)
  ─► CDA SME PASS or PASS-WITH-NOTES on §3 (verdict at docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md)
  ─► Coder: T4.1 scaffold + tests, then Mark hand-codes, then Coder T4.2
  ─► Reviewer + Tester PASS on T4.1 and T4.2
  ─► CDA SME PASS on T4.2 output (verdict at docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md, unchanged from Amendment 2)
  ─► T5 unblocked
```

**Why fresh SME plan review here, when Amendment 2 §3 T4 was waved through as "mechanical from B2/B3":** B11 is novel methodology surfaced *after* Amendment 2; the T4 operationalization of B11 includes substantive design decisions (artifact source, output surface, disposition framing) that are not mechanical. Per Amendment 2's own gate-chain logic ("schema choices that implement an SME-prescribed taxonomy require CDA SME plan review before reaching the Coder"), this amendment qualifies for the same treatment.

---

## 6. Summary for Mark

- **Phase 4a.1 picks up at T4.** Amendment 3 is a **focused additive delta** on the T4 task body in Amendment 2 §3. T1, T2, T3A, T3B, T3C, and the T5 plan body are unchanged.
- **T4 is now two ordered Coder commits** (T4.1 scaffold + T4.2 cross-tab) with a Mark hand-code between them. Up to ~$0 spend.
- **T4.1 scaffolds a small sibling artifact** at `data/derived/decline_interviews_safety_attribution_subtype.jsonl` (9 rows, one per `safety_event_attribution` decline-interview).
- **You hand-code 9 rows** as either `k_frame` or `k_vocab_without_k_frame`. SME's expected split is 5/4. Definitions are paraphrased into §3.1 from the T3C verdict's row-4 and row-5 discussion.
- **T4.2 cross-tab adds:** (a) a `safety_attribution_subtype` column to the cross-provider sub-table, (b) a new "Note K mechanism breakdown" sub-section, (c) a revised Note K disposition string that names both subtypes and their counts.
- **Note K disposition is still expected at CONFIRMED-with-mechanism.** The K-frame/K-vocab split refines the *mechanism description*, not the disposition tier. Disposition arithmetic does not change (D21).
- **T5 §8.2 carries the bipartite mechanism string** verbatim from T4's output, gated by the existing Ruling 3 public-copy guardrails.
- **No new schema changes; no `DATA_DICTIONARY.md` updates.** Same as Amendment 2.
- **Required gate before Coder starts T4.1:** CDA SME PASS or PASS-WITH-NOTES on §3 in this amendment.
- **Concrete next step after CDA SME PASS:** Coder invocation on T4.1 scaffold. Mark hand-codes after T4.1 lands.

---

## 7. Open questions for Mark

1. **D17 subtype computation source confirmation.** Architect adopted "Mark hand-codes in a sibling derived artifact" over (a) Coder regex helper and (b) extending the existing classification artifact. Confirming you intend to do the 9 hand-codes yourself; alternative is to delegate to the SME (changes the gate chain — SME does the hand-code, you spot-check).

2. **D17 SME spot-check on the subtype artifact: blocking T4.2 or parallel?** Amendment 2 made the T3C SME spot-check **blocking** on T4 (Mark commits 27 rows, SME spot-checks, Mark optionally amends, then T4 starts). For T4.1's subtype artifact (9 rows), Architect's default is **non-blocking** — T4.2 may proceed in parallel, with the SME spot-check happening at the T4 *output* gate (the existing `docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` gate, which already SME-gates the output). Rationale: 9 rows is small, the definitions are tightly bound by the T3C verdict's row-4/row-5 discussion, and the cost of a separate spot-check gate is high relative to the audit improvement. If you'd prefer a blocking spot-check on the subtype artifact (mirroring T3C), say so; the gate chain in §5 needs updating accordingly.

3. **D21 disposition-arithmetic invariance.** Architect rules that the K-frame/K-vocab split does not shift disposition tier. If a future re-classification changed Mark's distribution (e.g., 9 K-frame, 0 K-vocab — hypothetical), Architect's read is the disposition stays at CONFIRMED-with-mechanism with mechanism string updated. If you'd prefer a "if K-frame ≥ X, disposition becomes [different tier]" rule, that needs to be specified now and routed through SME.

4. **D22 §8.2 vs. §8.3 placement of mechanism description.** Architect placed the bipartite mechanism in §8.2 (Note K disposition) on methodological grounds — it *is* the disposition framing. Alternative placement would be a new sub-paragraph in §8.4 (audit-trail) where the K-frame examples could be enumerated by `decline_interview_id`. If you prefer the audit-trail placement (or both), say so.

5. **Coder commit count for T4.** Amendment 3 makes T4 = T4.1 (scaffold, 1 Coder commit) + Mark hand-code (1 commit) + T4.2 (cross-tab, 1 Coder commit) = 3 commits. CLAUDE.md §8 "one commit per task" applies per *task*, so T4.1 and T4.2 are separate tasks under §8 — this is fine. If you'd prefer T4.1 + T4.2 bundled into one Coder commit (with Mark's hand-code in between still its own commit), that's a §8-defensible choice; Architect's recommendation is the 3-commit shape because T4.1 and T4.2 have different review surfaces (T4.1 = schema/scaffold, T4.2 = analytic script).

---

## 8. Carry-forward — all 28 binding notes still in force

| Note set | Status |
|---|---|
| 8 original Phase 4a.1 plan binding notes | All in force |
| A1–A8 from Amendment 1 | All in force |
| B1–B6 from T3B-detector verdict | All in force; B1 closed (artifact landed); B2/B3/B6 still binding on T4/T5 outputs |
| B7, B8, B9 from Amendment 2 verdict | All in force; B7 + B8 verified at T3C spot-check; B9 vacuously satisfied (no blocked_event rows) |
| B10 (soft, future batches) from T3C verdict | Carried forward; soft, no Phase 4a.1 action |
| **B11 (binding on T4) from T3C verdict** | **Decomposed in this amendment as T4.1 + T4.2 additions per D17–D22** |
| B12 (binding precedent for future batches) from T3C verdict | Carried forward; binding precedent, no Phase 4a.1 action |

This amendment adds no new binding notes. The decomposition of B11 is the work of the Architect, not the SME; if the CDA SME identifies new methodology constraints during gate review, those become binding notes added to the amendment-3 verdict and carry forward as B13+.

Total binding notes on Phase 4a.1 after this amendment: **28** (unchanged; this amendment decomposes B11 rather than adding new notes).

---

## 9. Files (absolute paths)

Inputs (this amendment reads):
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md` (the doc being amended)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md` (B11 source)
- `/opt/lsb-agent/data/derived/decline_interviews_manual_classification.jsonl` (T3C output; T4.1 inputs derive from it)

Outputs (this amendment introduces):
- `/opt/lsb-agent/packages/cdb_analyze/cdb_analyze/safety_subtype.py` (T4.1 Coder commit)
- `/opt/lsb-agent/scripts/build_safety_subtype_seed.py` (T4.1 Coder commit)
- `/opt/lsb-agent/tests/test_safety_subtype.py` (T4.1 Coder commit)
- `/opt/lsb-agent/data/derived/decline_interviews_safety_attribution_subtype.jsonl` (T4.1 Mark hand-code commit)
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (T4.2; Amendment 2 specified file, Amendment 3 augments scope)
- `/opt/lsb-agent/tests/test_phase4a1_note_j_crosstab.py` (T4.2; Amendment 2 specified file, Amendment 3 augments fixture)

Gate verdict files:
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md` (this doc)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md` (required before T4.1 commit 1)
- `/opt/lsb-agent/docs/status/2026-04-30-phase4a1-t4-cda-sme-verdict.md` (existing, unchanged from Amendment 2; gates T4.2 output)

---

*End of Architect Plan Amendment 3. Binding for T4.1 and T4.2 unless a subsequent amendment supersedes. All 28 prior binding notes remain in force; this amendment decomposes B11 rather than adding new notes. Coder may NOT start T4.1 until CDA SME verdict on §3 is recorded.*
