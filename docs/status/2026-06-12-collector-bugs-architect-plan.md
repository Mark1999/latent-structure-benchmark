# COLLECTOR-BUGS Architect Plan (2026-06-12)

**Task ID:** COLLECTOR-BUGS
**Source:** Phase 9b food campaign fast-follow (phase9b-food-campaign.md §9, "collector bug batch")
**Gate path:** Architect → CDA SME → Coder → Reviewer → Tester. No UI/UX gate (no dashboard touch).
**CDA SME verdict:** PASS-WITH-NOTES -- `.claude/agent-memory/cda_sme/project_collector_bugs_verdict.md`
**Fix-trail location:** `docs/status/2026-06-11-phase9b-food-campaign.md` §COLLECTOR-BUGS fix trail

---

## 1. Context

Four issues surfaced during the Phase 9b food campaign (2026-06-11):

- **BUG 1** (`--skip-collected` domain scoping): `_load_collected_model_ids()` returned a
  set of model IDs with no domain key, so a model collected for family was incorrectly skipped
  for food. The early-exit skip guard also fired before the cross_model branch, making
  `--skip-collected --mode cross_model` a no-op.

- **BUG 2** (campaign_id threading): `run_two_pass`, `run_cross_model_sort`, and
  `run_baseline_sort` did not accept a `campaign_id` kwarg, so records produced by those
  paths never carried the campaign tag in `qa_notes`. The CLI only threaded `args.campaign_id`
  to the single_pass dispatch site.

- **BUG 3** (transport-failure records at per-model boundary): The existing `except Exception`
  handler in `collect_cross_model` appended failure records, but the context dict lacked a
  key to distinguish model-level transport events from per-step failures. The log message
  also used language that could be read as attributing behavior to the model rather than
  scoping to LSB's detection of the adapter raising.

- **VERIFICATION 4** (lsb_inspect.py field reads): Suspected read of a legacy field name
  for cross-model records. Ruled not-a-bug after inspection; `lsb_inspect.py` L120-121
  already uses `freelist.parsed_items` and `pile_sort.parsed_piles` correctly.

---

## 2. Scope

One commit. File scope:

| File | Change |
|---|---|
| `scripts/collect.py` | BUG 1: `_load_collected_model_domain_pairs()`, domain-aware skip guards; BUG 2: campaign_id kwargs + dispatch sites + help text; BUG 3: failure_scope context key + attribution-clean log message |
| `packages/cdb_collect/cdb_collect/runner.py` | BUG 2: campaign_id kwarg on run_two_pass / run_cross_model_sort / run_baseline_sort |
| `tests/unit/test_collect_skip_collected.py` | new: BUG 1 fixture-based tests |
| `tests/unit/test_collect_campaign_id.py` | new: BUG 2 fixture-based tests |
| `tests/unit/test_collect_failure_record.py` | new: BUG 3 fixture-based tests |
| `docs/status/2026-06-11-phase9b-food-campaign.md` | fix-trail section appended |

No changes to `cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`, `apps/dashboard/`, or
`data/raw/informants.jsonl`. The `http_error` enum value in `DeclineInterview.originating_outcome_class`
(schemas.py L769) is not touched: failure records appended by `append_failure` in
`data/raw/failures.jsonl` are not schema-bound (no cdb_core type; rule 6 stop-condition
does not apply). See §4 for the schema non-change rationale.

---

## 3. Acceptance criteria

### BUG 1

**AC1.** `_load_collected_model_domain_pairs()` added to scripts/collect.py, returning
`set[tuple[str, str]]` keyed on `(model_id, domain_slug)`. 2-tuple chosen over 3-tuple
per CDA SME advisory D1: AC7 encodes the cross-mode collision semantic.

**AC2.** `_load_collected_model_ids()` retained unchanged for `--list-models` display.

**AC3.** The `--mode single_pass` / `--mode two_pass` / `--mode baseline` early-exit skip
guard uses `_load_collected_model_ids()` (model-only), unchanged semantics for single-model
modes.

**AC4.** The `--mode single_pass` / `--mode two_pass` / `--mode baseline` single-model skip
guard is moved inside the `else` branch so it does not fire for cross_model mode.

**AC5.** The `--mode cross_model` per-model skip guard uses `_load_collected_model_domain_pairs()`
with 2-tuple `(ref.model_id, args.domain)`.

**AC6.** The 2-tuple key choice is documented in the commit body per plan AC15.

**AC7.** Test: a model with a family-domain record IS skipped for family (same domain),
but is NOT skipped for food (different domain).

**AC8.** Test: `--skip-collected --mode cross_model` correctly skips models that have
cross_model records for the target domain.

**AC9.** Test: `--skip-collected --mode cross_model` does NOT skip models that have
records only for a different domain.

**AC10.** Test: the early single-model skip guard does not interfere with cross_model
dispatch.

### BUG 2

**AC11.** `run_two_pass`, `run_cross_model_sort`, `run_baseline_sort` in runner.py each
gain `campaign_id: str | None = None` keyword-only parameter.

**AC12.** Each of those three functions passes `campaign_id=campaign_id` to all
`_assemble_record(...)` calls within their body.

**AC13.** `collect_two_pass`, `collect_cross_model`, `collect_baseline` in scripts/collect.py
gain `campaign_id: str | None = None` keyword-only parameter and pass it to the runner.

**AC14.** All four dispatch sites in `main()` (single_pass, two_pass, cross_model, baseline)
pass `args.campaign_id`.

**AC15.** `--campaign-id` help text updated: restriction "Applies only to --mode single_pass"
replaced with "Applies to all collection modes."

**AC16.** No backfill of historical records (fix-forward per CLAUDE.md §9 pitfall 10).

**AC17.** Test: a record produced via the two_pass dispatch path carries the correct
`campaign_id` in `qa_notes` when `--campaign-id` is supplied.

**AC18.** Test: a record produced via the cross_model dispatch path carries the correct
`campaign_id` in `qa_notes` when `--campaign-id` is supplied.

**AC19.** Test: a record produced via the baseline dispatch path carries the correct
`campaign_id` in `qa_notes` when `--campaign-id` is supplied.

**AC20.** Test: when `--campaign-id` is not supplied, `campaign_id=None` is passed and
no `campaign_id=None` tag appears in the record's `qa_notes`.

### BUG 3

**AC21.** The `except Exception` handler in `collect_cross_model`'s per-model loop calls
`append_failure(e, context, FAILURES_JSONL)` with `context["failure_scope"] = "per_model"`
(CDA SME C2 binding: option (a), preferred over `model_level=True`).

**AC22.** The `logger.exception` call at the per-model boundary uses the phrase "The adapter
raised an exception during cross-model sort for %s" (CDA SME C1 binding: no model-attribution
language; subject is the adapter, not the model).

**AC23.** Collection continues (via `continue`) past the failed model; subsequent models in
the loop are not skipped.

**AC24.** `response_verbatim` is NOT synthesized when no response arrived; `None` default
from `append_failure` kwargs is used (CDA SME C4 advisory: absence-is-signal).

**AC25.** Test: when the adapter raises a transport error for model A during cross_model sort,
a failure record is written to failures.jsonl with `context["failure_scope"] == "per_model"`,
`context["model_id"] == A`, `context["domain"] == <domain>`, `context["mode"] == "cross_model_consensus"`.

**AC26.** Test: collection continues past the failed model and subsequent models produce
records (AC23 test).

**AC27.** Test: `response_verbatim` is absent from the failure record when no response
arrived.

### VERIFICATION 4

**AC28.** `scripts/lsb_inspect.py` L120-121 reads `freelist.parsed_items` and
`pile_sort.parsed_piles`. Verified correct (not-a-bug). Disposition documented in
fix-trail. No code change required.

---

## 4. Schema non-change rationale

The `append_failure` function writes to `data/raw/failures.jsonl`, which is NOT governed by
`cdb_core` schemas (no `InformantRecord`, no `GroundingRef`, no `DomainResult` involved).
Failure records use the free-form dict contract in `packages/cdb_collect/cdb_collect/jsonl.py`.
Adding `"failure_scope": "per_model"` to the context dict is an operational-metadata key
addition, not a schema change. Reviewer rule R6 / CLAUDE.md rule 6 do not apply.

The `http_error` enum value in `DeclineInterview.originating_outcome_class` (schemas.py L769)
classifies decline-interview outcomes, not transport-layer failure records. No new enum values
are needed.

---

## 5. CDA SME notes (binding)

See `.claude/agent-memory/cda_sme/project_collector_bugs_verdict.md` for the full C1-C4 and
D1-D3 notes. Summary:

- **C1 (binding):** Log line must use "the adapter raised", "per-model boundary", or
  equivalent LSB-side event language. FORBIDDEN: "the model failed", "the model errored",
  "the model crashed".
- **C2 (binding):** Use `context["failure_scope"] = "per_model"` (SME preference, option a).
- **C3 (binding):** Commit body must contain an anti-attribution sentence with four nouns:
  "LSB's detection", "provider-transport event", "model output", "decline-interview pipeline".
- **C4 (advisory):** Do NOT synthesize `response_verbatim = ""` when no response arrived.
- **D1 (carry-forward):** 2-tuple key for BUG 1 is correct per AC7 semantics.

The routing call in the CDA SME verdict requires the SME to review the BUG 3 implementation
diff for C1/C2/C3 compliance before commit lands. That implementation-diff review is
documented at `docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md`.

---

## 6. Gates

No UI/UX gate: no dashboard change, no generated user-visible copy, no design-system surface.

No additional CDA SME plan review needed: the initial PASS-WITH-NOTES verdict covers the plan.
The BUG 3 implementation-diff review (`docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md`)
is the only post-plan CDA SME gate.

Standard Reviewer + Tester gates apply.

---

## 7. Tests

All tests use mock adapters and `tmp_path` temp files. No real API calls (CLAUDE.md rule 9 /
pitfall 9).

`uv run pytest tests/unit/test_collect_skip_collected.py tests/unit/test_collect_campaign_id.py tests/unit/test_collect_failure_record.py && uv run ruff check . && uv run mypy packages/` must pass before commit.

---

## Gate verdicts

**CDA SME plan review:** PASS-WITH-NOTES
Reference: `.claude/agent-memory/cda_sme/project_collector_bugs_verdict.md`
Full status doc: `docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md` (BUG 3
implementation-diff C1/C2/C3 compliance verification)

**Reviewer verdict:** PENDING (see Reviewer REJECT from 2026-06-12 worktree review --
two items required: this file + CDA SME implementation-diff compliance doc)

**Tester verdict:** PENDING
