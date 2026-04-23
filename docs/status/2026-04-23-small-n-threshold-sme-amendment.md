# Small-N Threshold Reconciliation — CDA SME Amendment

**Date:** 2026-04-23
**Reviewer:** CDA SME (agent)
**Trigger:** T5 Coder correctly stopped on a conflict between two prior SME verdicts:

- **F2-T02 verdict (2026-04-20)** set `romney_small_n_warning` threshold at **n < 8** (implemented at `cdb_analyze/pipeline.py:302`, commit `60cae7f`).
- **Slate verdict Note A (2026-04-22)** stated the threshold is **n < 15**, citing `SME_REVIEW.md` §1.1.
- `SME_REVIEW.md` does not contain an explicit `n < 15` numeric claim. The citation in Note A was imprecise.

**Amends:**
- `docs/status/2026-04-20-f2-cda-sme-verdict.md` T02 threshold
- `docs/status/2026-04-22-phase4a-slate-cda-sme-verdict.md` Note A citation

---

## Binding ruling: **`n_models < 15`**

The binding threshold for `DomainResult.romney_small_n_warning` is **`n_models < 15`**. `n < 8` is superseded.

## Methodological grounding

`SME_REVIEW.md` §1.1 grounds the Romney 5.0 operational eigenratio threshold in the n=12 small-n regime, citing Anders & Batchelder 2015. The underlying argument: classical Romney-Weller-Batchelder 1986 CCT calibration used n=20–40 informants; below that range, the eigenratio distribution is no longer tight enough to distinguish true single-consensus from sampling artifact. The CCT literature's working small-n cutoff is ~n<15; within that range the `romney_small_n_warning` flag is required.

**Why `n < 8` was wrong:** it silently classified n=8–14 as "not small-n," contradicting §1.1's own premise that n=12 is already small-n. The F2-T02 threshold was set at T02 implementation time without the slate-level framing in view; the slate verdict extended it correctly, but the citation was imprecise.

## Citation going forward

Code comments and documentation should attribute the threshold to:

> "SME_REVIEW.md §1.1 small-n rationale (Anders & Batchelder 2015; Romney-Weller-Batchelder 1986 calibration at n=20–40)."

**NOT** a literal SME_REVIEW.md quote, since §1.1 does not state the `n < 15` numeric explicitly. This is a **doc-hygiene follow-up**: SME_REVIEW.md §1.1 should gain an explicit "small-n threshold: n < 15" subsection so future citations can be literal.

## Phase 4a effect

- **Family** (n_models = 10): `10 < 15 = True` → `romney_small_n_warning = True`.
- **Holidays** (n_models = 8): `8 < 15 = True` → `romney_small_n_warning = True`.

Both domains trigger the flag at n < 15, consistent with the Phase 4a "small-n canonical run by design" framing.

## Code impact (one small Coder task)

1. `packages/cdb_analyze/cdb_analyze/pipeline.py:302` — change `len(model_ids) < 8` to `len(model_ids) < 15`.
2. `packages/cdb_core/cdb_core/schemas.py` — the `romney_small_n_warning` field's docstring/comment, wherever it states `n < 8`, update to `n < 15` with the citation above.
3. `tests/unit/test_sme_measures.py` (or wherever the threshold is asserted) — update the constant and any test that checks `small_n_warning=True/False` at the boundary.
4. `docs/DATA_DICTIONARY.md` — if the threshold is documented there, update + `R7` co-update is automatic since schema docstring changes.

This is a **one-line behavioral change plus docstring/test updates**. No new pydantic model, no new dep.

## Architect sign-off

No Architect re-review needed beyond the standard Reviewer gate — this is a methodology-threshold correction, not a schema structure change. The `romney_small_n_warning: bool` field itself is unchanged in shape.

## T5 disposition

**T5 proceeds** once the Coder fix lands. With the threshold at `n < 15`:
- Both `DomainResult`s will carry `romney_small_n_warning=True` as expected.
- Slate SME Note A's expected outcome matches.
- The decline-interview SME verdict's Notes A/C/G/J remain binding on downstream copy.

## Retroactive impact on earlier verdicts

- **F2-T02 SME PASS-WITH-NOTES retroactively:** the F2 PASS at `n < 8` was correct at F2 scope (pre-Phase-4a; n=4 shakedown where either threshold triggers True equally). It does not become FAIL, but a forward note is warranted noting that the threshold is n<15 going forward.
- **Slate SME PASS-WITH-NOTES stands:** Note A's *ruling* was correct; only the *citation* needs refinement (addressed via the "doc-hygiene follow-up" below).
- **Decline-interview SME PASS-WITH-NOTES stands:** unaffected.

## Follow-up task

**SME_REVIEW.md §1.1 hygiene** — add an explicit subsection naming the `n < 15` small-n threshold with the Anders & Batchelder 2015 + RWB 1986 calibration citation. One-paragraph edit. Not a Phase 4a blocker; track as low-priority SME-authored doc work.

---

*End of amendment. Binding threshold: `n_models < 15`. T5 unblocks once `pipeline.py:302` is patched.*
