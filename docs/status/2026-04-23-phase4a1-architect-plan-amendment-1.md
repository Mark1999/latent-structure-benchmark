# Phase 4a.1 — Architect Plan Amendment 1 (task #21)

**Date:** 2026-04-23
**Planner:** Architect
**Task:** #21 (Phase 4a.1 decline-interview backfill) — AMENDMENT 1
**Supersedes partially:** `docs/status/2026-04-23-phase4a1-architect-plan.md` (task list, D7, binding note 8, dependency chain)
**Carries forward:** Everything in the prior plan not explicitly amended below, including all 8 binding notes from the 2026-04-23 CDA SME verdict (`docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md`). This amendment is **additive**.

**Trigger:** T1 dry-run on real data (commits `3318023` + `24102fd` + `3c5f742`) surfaced 32 detected sessions (vs. ~5 expected under Note C). $1.60 projected spend at $0.05/call hit the 80%-of-$2-cap STOP threshold per SME binding note 8. Mark's decision (2026-04-23): option A (scope trim via exclusion criteria) + option D (batch split) + cap raise from $2 to $10.

**Gate verdict chain for this amendment:**
- Architect decomposition (this document)
- **CDA SME PASS / PASS-WITH-NOTES required** on the exclusion criteria rule (§2 below) before T1-update starts. Reviewer-only gating is insufficient; the inclusion/exclusion distinction is methodology-adjacent.
- Reviewer PASS on each code task.

**Revised expected spend:** ≤ $10 hard cap (D7-amended). Expected population post-exclusion: ~8–12 calls (3 informants-origin + approximately 5–9 safety-filter-origin Gemini records, pending the T1-update dry-run report). Target spend $0.40–$0.60. Architect's pre-SME estimate places post-exclusion count closer to 27 on conservative classification; SME ruling on Gemini empty-response disposition drives the final number.

---

## 1. What this amendment changes

| Item | Before | After |
|---|---|---|
| D7 hard cap | $2.00 | $10.00 |
| T1 dry-run pre-flight threshold | $1.60 (80% of $2) | $8.00 (80% of $10) |
| Population under backfill | All 32 detected sessions | Filtered population: informants-origin + failures-origin **minus** HTTP-infrastructure technical failures |
| Batch structure | Single batch T3 | Two sub-batches: T3A (informants-origin, authorized-now) then T3B (surviving failures-origin, separate Mark sign-off) |
| Detector (`decline_detection.py`) | v1-frozen | **Unchanged.** Exclusion is a post-detection filter at consume time. |
| Prior 8 SME binding notes | Binding | **Still binding.** Amendment is additive. |

**What this amendment does NOT change:**
- No schema changes. `DeclineInterview` / `InformantRecord` untouched.
- No edits to `decline_detection.py`. The detector remains v1-frozen. SME binding note on append-only-for-the-decline-instrument binds; the filter is at the **consumer** layer (T1 reporter + T2 runner), not inside the detector.
- `failures.jsonl` remains append-only. Exclusion is filter-at-consume, not delete.
- The 8 grok-4 Check-5-only records stay under Note C "not triggered" disposition (RISK 5, v2 allowlist amendment territory). Not part of this amendment.
- All 8 SME binding notes from the 2026-04-23 verdict remain in force.

---

## 2. Exclusion criteria rule (requires CDA SME PASS-WITH-NOTES before T1-update begins)

### Intent

The decline-interview prompt asks the model *"describe what happened in that exchange"* — it presumes a generation path at the informant model. Records where **no model-generated exchange occurred** (the request failed in transport, the payload was malformed, the adapter crashed before the model responded) have no exchange to describe. Interviewing them produces hallucinated narratives, not audit data. Those are technical failures, not refusals, and must be excluded.

Records where the **provider's safety / content-policy layer** returned an error in lieu of generation **are** refusals — they carry information about the provider's effective corpus-lens framing, which is exactly what the decline-interview instrument exists to capture. Those must be included.

The landed failures.jsonl shape (per `append_failure` in `packages/cdb_collect/cdb_collect/jsonl.py`) gives us `error_type` (Python exception classname) and `error_message` (full error text). The detector already maps `error_type` → `originating_outcome_class` deterministically (see `_map_error_type_to_outcome_class` in `decline_detection.py`). The filter piggybacks on that mapping plus a small set of explicit message-substring tests.

### The rule (Coder-mechanical)

Add a helper `should_include_failure(entry: dict) -> tuple[bool, str]` to `scripts/run_decline_backfill.py`. Returns `(include_bool, rationale_string)`. The rationale string is logged in both T1 Section 3b and T2 per-record skip log. The function is pure, deterministic, and exhaustively tested.

**Step 1 — classify by `error_type`:**

```
HTTP_INFRASTRUCTURE_EXCEPTION_TYPES = {
    "HTTPStatusError",          # httpx 4xx/5xx
    "ConnectError",             # httpx connection errors
    "ConnectTimeout",
    "ReadTimeout",
    "WriteTimeout",
    "PoolTimeout",
    "TimeoutError",             # stdlib
    "ConnectionError",          # stdlib
    "RemoteProtocolError",      # httpx
    "ReadError",                # httpx
    "WriteError",               # httpx
}

ADAPTER_PARSE_PRE_GENERATION_TYPES = {
    # Reserved for future use; empty in v1 because all observed ValueError
    # cases in failures.jsonl are post-generation parse exhaustion (see
    # step 2). If an adapter starts raising a pre-generation validation
    # error, add its classname here on a new Architect plan cycle.
}
```

**Step 2 — classify ambiguous cases by `error_message` substring:**

Among `error_type == "ValueError"` (which covers both post-generation parse failures and potentially safety-filter-surfaced-as-exception cases):

```
PARSE_EXHAUSTION_MARKERS = (
    "Pile sort parsing failed after 3 attempts",
    "Could not extract valid JSON from response",
    "Items missing from pile sort",
)
```

These all INCLUDE (the model generated, the generation was off-spec).

**Step 3 — safety-filter detection (by `error_message` substring, any `error_type`):**

```
SAFETY_FILTER_MARKERS = (
    "safety",
    "content policy",
    "content_policy",
    "blocked",
    "harmful",
    "prohibited",
    "policy_violation",
    "content_filter",
    "RECITATION",       # Gemini finish_reason for copyright block
    "SAFETY",           # Gemini finish_reason for safety block
    "PROHIBITED_CONTENT",
    "OTHER",            # Gemini's generic content-block finish_reason
)
```

If any marker matches (case-insensitive) in `error_message`, **INCLUDE regardless of `error_type`**. Safety-filter blocks surface through multiple channels across providers (sometimes HTTPStatusError, sometimes finish_reason, sometimes a custom exception). Message-substring is the reliable cross-provider detector.

**Step 4 — decision tree (apply in order, first match wins):**

```
def should_include_failure(entry: dict) -> tuple[bool, str]:
    error_type = entry.get("error_type", "")
    error_message = entry.get("error_message", "")
    msg_lower = error_message.lower()

    # 4.1 — Safety-filter blocks override the infrastructure exclusion.
    for marker in SAFETY_FILTER_MARKERS:
        if marker.lower() in msg_lower:
            return (True, f"safety_filter:matched:{marker!r}")

    # 4.2 — HTTP / network / timeout infrastructure failures: exclude.
    if error_type in HTTP_INFRASTRUCTURE_EXCEPTION_TYPES:
        return (False, f"http_infrastructure:{error_type}")

    # 4.3 — Adapter parse failure BEFORE generation: exclude (empty in v1).
    if error_type in ADAPTER_PARSE_PRE_GENERATION_TYPES:
        return (False, f"adapter_pre_generation_parse:{error_type}")

    # 4.4 — Post-generation parse exhaustion: include.
    for marker in PARSE_EXHAUSTION_MARKERS:
        if marker in error_message:
            return (True, f"parse_exhaustion:{marker[:30]}")

    # 4.5 — Everything else: include with "unclassified" rationale.
    return (True, f"unclassified:default_include:{error_type}")
```

**Expected classification on the current `failures.jsonl` (per Mark's diagnostic):**

| Count | error_type | Message marker | Disposition | Rationale |
|---|---|---|---|---|
| 5 | HTTPStatusError | "400 Bad Request" (phi-4) | **EXCLUDE** | HTTP 400 = malformed request, model never responded |
| 10 | ValueError | "Could not extract valid JSON from response: " (empty string) Gemini | **INCLUDE** | Model returned empty string after 3 retries; this is a degenerate-output refusal signature. **Largest surviving cohort; SME-review priority.** |
| ~14 | ValueError | "Items missing from pile sort" / "Could not extract valid JSON" (non-empty partial) | **INCLUDE** | Post-generation parse exhaustion; model generated, was off-spec |

Approximate post-exclusion count: **~24 failures-origin + 3 informants-origin = ~27**. SME ruling on Gemini empty-response disposition drives the final number.

### Ambiguous cases requiring SME ruling (before T1-update code lands)

1. **`stop_reason="length"` cases.** Not represented in current failures.jsonl. Default: **INCLUDE**, because length-cutoff on a pile-sort response means the model attempted to comply. Flag for SME ruling.

2. **Gemini's 10 empty-response-after-3-retries cases.** `error_message = "Could not extract valid JSON from response: "` with literally empty response bytes. Could be: (a) Gemini silently safety-blocked without surfacing a finish_reason (likely — Gemini's T1 jailbreak refusal surfaced this way); (b) transport-level response stripping; (c) model genuinely returning nothing. Default: **INCLUDE** under `parse_exhaustion`. SME must bless or overrule.

3. **Streaming cut-offs (if any).** Same disposition as `stop_reason="length"`.

4. **Model-specific refusal flags in exception form.** Not currently represented. Default: **INCLUDE** on SAFETY_FILTER_MARKERS substring expansion.

### Where the rule lives

**T1-update (script):** `should_include_failure` is defined in `scripts/run_decline_backfill.py` as a module-level pure function. Unit-tested against every row class in the fixtures.

**T2 (script):** Same function, imported or re-used in the execute path. No divergence between T1 and T2 classification.

**Tests:** 12+ new unit tests covering each branch of the decision tree, the safety-filter override case, and the actual failures.jsonl row shapes.

### What lives where in the code path

| Stage | Responsibility |
|---|---|
| T1-update `--dry-run` | Report full detected-session count AND post-exclusion count. Section 3b audit listing: every excluded failures-origin record with `(identifier, error_type, first 120 chars of error_message, rationale_string)`. Section 3c: every `unclassified:default_include` record surfaced for SME eyes-on. Cost guard uses **post-exclusion** count against the new $8 pre-flight threshold. |
| T2 `--execute` | Filter DetectedSession list via `should_include_failure` before invoking `run_decline_interview`. Excluded records logged to stdout with rationale but not written to `decline_interviews.jsonl`. Per-sub-batch cost counter. |

---

## 3. Batch split mechanics

### CLI surface

Add `--source` flag to `scripts/run_decline_backfill.py`:

```
--source {informants, failures, all}   Default: 'all' (current behavior)
--dry-run                              (existing)
--execute                              (existing)
--cost-cap-usd FLOAT                   Default: 10.00 (new, replaces hardcoded constant)
```

Semantics:
- `--source informants`: Only informants-origin DetectedSessions processed. T3A uses this.
- `--source failures`: Only failures-origin DetectedSessions processed (with exclusion filter applied). T3B uses this.
- `--source all`: Both, with exclusion filter applied to failures-origin. Default for backward compatibility with the landed T1.

### T3A — informants-origin sub-batch (authorized now under this amendment)

**Scope:** Execute `uv run python scripts/run_decline_backfill.py --execute --source informants` on `lsb-agent-02`. Expected population: 3 records (z-ai/glm-5.1 × family empty-freelist). Expected spend: ~$0.15.

**Acceptance criteria:**
- 3 records written to `data/raw/decline_interviews.jsonl`.
- Each passes `DeclineInterview.model_validate_json`.
- xor invariant: `originating_informant_id` non-null, `originating_failure_id` null.
- `detection_timestamp` identical across all 3.
- Total spend < $8 (well under cap; target ~$0.15).
- B2 backup confirmed.
- Run log at `docs/status/2026-04-23-phase4a1-t3a-run-log.md` with: command invoked, CLI summary, spend, version_drift_flag count, recursive-decline cases.

**Commit message:** `data(collect): Phase 4a.1 decline-interview backfill T3A informants (task #21.T3A)`

**Verdicts required:** Reviewer PASS.

### T3B — failures-origin sub-batch (requires separate Mark sign-off)

**Scope:** Execute `uv run python scripts/run_decline_backfill.py --execute --source failures` on `lsb-agent-02`. Expected population: ~24 records post-exclusion (pending T1-update dry-run + SME ruling). Expected spend: ~$0.40–$1.20.

**Pre-conditions for T3B authorization:**
1. T3A completed cleanly (Reviewer PASS).
2. Mark reviews T3A run log.
3. Mark reviews T1-update's Section 3b (excluded records) and Section 3c (unclassified-default-include records).
4. Mark explicitly authorizes T3B in writing (commit message, Slack, or plan amendment addendum).
5. SME PASS on this amendment's exclusion criteria is already in place.

**If T3A surfaces recursive-decline or unexpected-output patterns**, T3B is paused until RISK 2 two-tier rule review completes.

**Commit message:** `data(collect): Phase 4a.1 decline-interview backfill T3B failures (task #21.T3B)`

**Verdicts required:** Reviewer PASS.

### How T4/T5 consume both batches

Single T4 run, single T5 report. `data/raw/decline_interviews.jsonl` accumulates T3A + T3B records (append-only). T4's cross-tab script reads the whole file. T5's completion report covers both sub-batches in one document.

- T5 §1 timeline: T3A run + T3B run as separate entries.
- T5 §3 artifacts: combined record count.
- T5 §4 cost accounting: T3A spend + T3B spend + cumulative.
- T5 §5 input-set reconciliation: new sub-section "Exclusion rule applied under Amendment 1" with rule summary, per-rationale bucket count, specific excluded identifiers.
- All other sections unchanged.

---

## 4. D7 amended + SME binding note 8 amended

**D7-amended:** Hard spend cap **$10.00**, configurable via `--cost-cap-usd` CLI flag. Abort on exceed; `decline_interviews.jsonl` stands (append-only). Per-sub-batch cost counters reported separately in the CLI summary.

**SME binding note 8 amended:** T1-update dry-run must report **both** full detected-session count and post-exclusion count before T3A/T3B commits to the $10 cap. Pre-flight threshold raised to $8.00 (80% of new cap). If projected post-exclusion batch cost ≥ $8.00, stop and escalate — D7 needs re-evaluation on a new plan cycle, not ad-hoc in T3A/T3B.

**The prior $2 cap's STOP has fired once and been resolved via this amendment.** Future escalations still require a new plan cycle — this amendment is not a license to raise the cap without methodology review. The exclusion-criteria decision is the substantive input that justifies the raise, not the raise itself.

---

## 5. Required changes to landed code

Coder's worklist for T1-update (single commit). None of this touches `decline_detection.py`.

### `scripts/run_decline_backfill.py`

1. Add module-level constants: `HTTP_INFRASTRUCTURE_EXCEPTION_TYPES`, `ADAPTER_PARSE_PRE_GENERATION_TYPES` (empty), `SAFETY_FILTER_MARKERS`, `PARSE_EXHAUSTION_MARKERS`.
2. Add helper `should_include_failure(entry: dict) -> tuple[bool, str]` implementing the §2 decision tree exactly.
3. Replace hardcoded cost cap. Prior `COST_CAP_USD = 2.00` becomes CLI-parameterized defaulting to `10.00`. Per-call estimate `$0.05` unchanged. Pre-flight threshold is `0.8 * cost_cap_usd`.
4. Add `--source` CLI flag with choices `{informants, failures, all}`, default `all`.
5. T1-update dry-run: Section 3b added (excluded failures-origin records with rationale).
6. T1-update dry-run: Section 3c added (unclassified-default-include records flagged for SME eyes-on).
7. Cost guard uses post-exclusion count.
8. T1-update dry-run CLI summary prints Detected / Informants / Failures (raw / excluded / included) / Post-exclusion total / Projected cost / Cap / Disposition.
9. T2 execute path: apply filter before invoking runner. Excluded records logged with rationale.
10. T2 execute path: per-sub-batch counters.

### `tests/test_run_decline_backfill.py`

11. `TestShouldIncludeFailure` — ~14 unit tests covering every branch of the decision tree.
12. `TestSection3bExcludedAudit` — integration tests.
13. `TestSection3cUnclassified` — integration tests.
14. `TestCostGuardPostExclusion` — integration tests.
15. `TestSourceFlag` — CLI tests.
16. `TestCostCapCLIOverride` — CLI tests.

### Fixtures

17. Extend `tests/fixtures/` with failures.jsonl fixtures for each classification branch.

### No changes to

- `packages/cdb_collect/cdb_collect/decline_detection.py` (v1-frozen)
- `packages/cdb_collect/cdb_collect/run_decline_interview.py`
- `packages/cdb_collect/cdb_collect/jsonl.py`
- `packages/cdb_core/cdb_core/schemas.py`

---

## 6. Task list (ordered)

### T1-update — exclusion filter + Section 3b/3c audit + cost-cap CLI

Single commit covering all §5 changes.

**Commit message:** `feat(collect): T1-update exclusion filter + $10 cap + 3b/3c audit (task #21.T1-update)`

**Acceptance criteria:**
- Dry-run on fixtures exits 0; on real data exits 2 only if post-exclusion cost ≥ $8.00.
- All three sections (3, 3b, 3c) present in dry-run output.
- On real data: 32 detected, N excluded, M included, projected < $8, GO.
- Test suite green (new + existing).
- `uv run ruff check scripts/ tests/` green; `uv run mypy packages/` green.
- No LLM imports; no new deps.

**Verdicts required:**
- **CDA SME PASS / PASS-WITH-NOTES on §2 exclusion rule** (required before Coder starts). Verdict at `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md`.
- Reviewer PASS on commit.
- Tester PASS.

---

### T2 — execute path filter + per-source counters

Extend execute path to honor `--source` and `should_include_failure`. Per-sub-batch counters. Per-record skip logs. Fixture-based integration test.

**Commit message:** `feat(collect): T2 execute path with --source filter + exclusion (task #21.T2)`

**Verdicts required:** Reviewer PASS. Tester PASS. (No SME re-review — T2 is mechanical realization of §2 rule.)

---

### T3A — informants-origin sub-batch live run (authorized)

See §3. 3 records, ~$0.15.

---

### T3B — failures-origin sub-batch live run (requires Mark sign-off)

See §3. BLOCKED until T3A lands + Mark reviews Section 3b/3c + explicit Mark authorization + SME notes 6 (RISK 2) check on T3A output.

---

### T4 — Note J cross-tab + Note K re-evaluation

Unchanged from prior plan. Reads combined T3A+T3B output. CDA SME PASS required.

---

### T5 — Completion report + Note K disposition

Mostly unchanged; §1/§3/§4/§5 get additions for the sub-batch split + exclusion rule. CDA SME PASS required.

---

## 7. Revised dependency chain

```
(SME PASS on Amendment 1 §2 exclusion rule)
        │
        ▼
T1-update ──► T2 ──► T3A ──► (Mark authorizes T3B
                              after reviewing T3A
                              + 3b/3c audit)
                              │
                              ▼
                             T3B ──► T4 ──(SME gate)──► T5 ──(SME gate)
```

---

## 8. SME gates on this amendment

| Change | Gate | Rationale |
|---|---|---|
| Cost cap raise $2 → $10 | Reviewer sufficient | Infrastructure parameter. |
| Batch split (T3A / T3B) | Reviewer sufficient | Operational sequencing. |
| `--source` CLI flag | Reviewer sufficient | Mechanical enablement. |
| **Exclusion criteria rule (§2)** | **CDA SME PASS-WITH-NOTES required** | Methodology-adjacent. SME must bless: (a) general principle; (b) default-include for unclassified records; (c) Gemini empty-response disposition (largest surviving cohort); (d) safety-filter-override-of-infrastructure priority. |
| Note J cross-tab / Note K logic | CDA SME PASS (per prior plan) | Methodology-binding. |
| T5 Note K disposition language | CDA SME PASS (per prior plan) | Methodology-binding. |

SME verdict on this amendment saved to `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md`. T1-update cannot start until that verdict is PASS or PASS-WITH-NOTES; if FAIL, amendment returns to Architect for rework.

---

## 9. Carry-forward from prior SME verdict (all 8 binding notes remain binding)

| SME note | Status under this amendment |
|---|---|
| 1. T1 per-record not-triggered reasoning | Still binding. Section 3 in T1-update unchanged. |
| 2. T4 cross-tab baseline = corpus attempt distribution + ≥ 2 floor | Still binding. T4 unchanged. |
| 3. T4 primary view = `outcome_class × origin`, no factorial | Still binding. T4 unchanged. |
| 4. Note K taxonomy (INCONCLUSIVE-SUGGESTIVE, CONFIRMED ≥ 5 CN + ≥ 1 non-CN + Check-6) | Still binding. |
| 5. T5 §9 CONFIRMED = coverage-caveat framing | Still binding. |
| 6. RISK 2 two-tier rule (any non-CN recursive → narrow; ≥ 33% → broad) | Still binding. Applies at T3A and T3B. T3B blocked if T3A surfaces recursive-decline per this rule. |
| 7. T5 §9 specific numerics per denominator scenario | Still binding. Denominator analysis covers combined T3A + T3B. |
| 8. T1 dry-run reports Gemini failures count before T3 commits | **Amended** (§4): reports full + post-exclusion counts; pre-flight $8; prior STOP fired once and resolved; future escalations still require re-plan. |

---

## 10. Pre-conditions for T1-update

- [ ] `docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` exists with PASS or PASS-WITH-NOTES on §2.
- [ ] Prior T1 code at `scripts/run_decline_backfill.py` is at commit `24102fd` or later.
- [ ] `data/raw/failures.jsonl` readable, 30 entries.
- [ ] `decline_detection.py` `_map_error_type_to_outcome_class` unchanged since amendment written.
- [ ] `.env` spend cap configuration has ≥ $10 headroom.

---

## 11. Files (absolute paths)

Inputs (unchanged):
- `/opt/lsb-agent/data/raw/informants.jsonl`
- `/opt/lsb-agent/data/raw/failures.jsonl`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/decline_detection.py`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/run_decline_interview.py`
- `/opt/lsb-agent/packages/cdb_collect/cdb_collect/jsonl.py`

Outputs (amended):
- `/opt/lsb-agent/scripts/run_decline_backfill.py` (T1-update, T2 — extended in place)
- `/opt/lsb-agent/tests/test_run_decline_backfill.py` (T1-update, T2 — new test classes)
- `/opt/lsb-agent/tests/fixtures/` (new failures fixtures)
- `/opt/lsb-agent/data/raw/decline_interviews.jsonl` (T3A, T3B — accumulates)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t3a-run-log.md` (T3A)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-t3b-run-log.md` (T3B)
- `/opt/lsb-agent/scripts/phase4a1_note_j_crosstab.py` (T4 — unchanged)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-completion-report.md` (T5)

Gate verdicts:
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md` (this doc)
- `/opt/lsb-agent/docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md` (to be created — required before T1-update)
- Per-task reviewer verdicts at `docs/status/2026-04-23-phase4a1-t*-reviewer-verdict.md`
- T4/T5 SME verdicts per prior plan

---

## 12. Summary for Mark

- **T1 is closed.** 32 detected, $1.60 → 80% cap STOP fired correctly, resolved via this amendment.
- **Amendment route:** A (exclusion filter) + D (batch split) + cap raise ($2 → $10).
- **New Coder task:** T1-update — one commit adding `should_include_failure`, Section 3b/3c audit, `--source` flag, CLI-parameterized cost cap, 20+ new tests.
- **Then T2:** execute path honors filter + `--source`. Per-sub-batch counters.
- **Then T3A (informants, 3 records, ~$0.15)** runs under your standing authorization.
- **Then you review T3A + Section 3b/3c, then authorize T3B.**
- **T4 / T5 unchanged** — still CDA SME gated.
- **Required gate before Coder starts T1-update:** CDA SME PASS or PASS-WITH-NOTES on §2 exclusion rule, especially Gemini-empty-response disposition and default-include-unclassified policy.

The exclusion rule is the methodology-substantive piece. The cap raise and batch split are operational plumbing.

---

*End of Architect Plan Amendment 1. Binding for T1-update through T5 unless a subsequent amendment supersedes. All 8 prior SME binding notes remain in force; this amendment is additive. Coder may NOT start T1-update until CDA SME verdict on §2 is recorded.*
