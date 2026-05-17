---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T2 — Trigger detectors (pure functions over the published results store)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T2 — CDA SME verdict on the trigger-detector design

**VERDICT: PASS-WITH-NOTES**

The T2 design specified in the Phase 7 kickoff §3 T2 is **methodologically
coherent at the algorithmic level** with the §1.5 / §1.5.4 / §1.5.7 framing
and with the T1 schema landed at commit `57745bd`. The five `detect_*`
functions correctly stay inside `cdb_social/` (the §4.6 social-publishing
layer); none of them perform Register-1/Register-2/Register-3 computation,
all of them consume already-published numerics read-only from
`apps/dashboard/public/data/`; and the dedupe / first-run-bootstrap
posture preserves the §5.8 / §5.9 T1 advisories.

The eight CDA-SME questions surfaced in the Orchestrator's invocation are
answered below in §2 (questions 1–7) plus the §5.6 evidence-enforcement
recommendation (question 8). The headline rulings:

1. **`DRIFT_THRESHOLD = 0.15` placeholder is OK to ship as a code
   constant** because the cron's `enable_drift=False` flag is the
   load-bearing lockout. T2 **must** add a runtime guard (§4.1) that
   raises if `detect_drift` is called with `enable_drift=True` and the
   underlying data contains fewer than the §4.2 register-3 minimum
   intersection (≥ 8 items) per `model_version_returned × collection_date`
   pair. The guard surfaces a re-SME-review prompt the first time real
   multi-date data is presented to the detector. See §5.1.

2. **`detect_divergence` "new high" semantics need a minimum-delta floor**
   (`MIN_DIVERGENCE_DELTA = 0.02` on the bootstrap-mean similarity scale
   per §4.2.6) **and** the comparison must be CI-aware in a specific
   non-statistically-strong sense — the divergence detector consumes
   bootstrap mean values, not full bootstrap distributions, because
   `apps/dashboard/public/data/{domain}.json` is the read substrate
   (cdb_publish-produced point estimates with CIs). The detector compares
   point-mean to point-mean, then applies the min-delta floor as the
   noise-band guard. This is **deliberately not** a hypothesis test —
   LSB does not make hypothesis-confirming claims (§1.5.7). See §5.2.

3. **First-run bootstrap semantics for `detect_new_model` /
   `detect_new_domain`:** **state-file absence ≠ first run.** First run is
   defined by an explicit sentinel — a `bootstrapped_at: datetime` key
   inside each state file. State-file absence is treated as state-loss
   (an operator-recoverable error, NOT silently bootstrapping). On
   state-loss the detector raises `StateFileMissingError` and the cron
   surfaces the error to the operator. See §5.3.

4. **`detect_monthly_roundup` firing time:** **first cron run on or after
   the 1st of the month** at 14:00 UTC (the kickoff §3 T7 cron schedule).
   No business-day weighting. `evidence['month'] = "YYYY-MM"` is the
   previous calendar month (the month being summarized), not the current
   one. The state file `state/monthly_roundup.json` records
   `last_fired_month: "YYYY-MM"`. See §5.4.

5. **Dedupe re-fire procedure for prompt-bump scenarios:** T2 adds an
   explicit docstring section on `detect_*` functions (or a module-level
   docstring) documenting the manual procedure — remove the entry from
   `state/posted_dedupe_keys.json`, the next cron run re-fires the
   trigger, the v2 drafter produces a fresh draft. This is **already**
   handled in the T1 schema docstring on `dedupe_key` (visible at
   schemas.py lines 706–716); T2 must cross-reference that contract in
   `triggers.py`'s module docstring so a future engineer reading
   `triggers.py` understands the dedupe scope. See §5.5.

6. **Divergence ∩ new-model interaction (§5.9 T1 advisory operationalized):**
   the suppression rule is **"per-domain new-model exclusion."** When
   `detect_new_model` emits one or more triggers for a domain in the
   current run, `detect_divergence` for that same domain **must
   recompute** the pairwise-max similarity gap *with the new-model
   informants excluded*, then compare that recomputed gap against the
   stored `divergence_highs.json` baseline. If the recomputed (new-models
   -excluded) gap exceeds the prior high by `≥ MIN_DIVERGENCE_DELTA`, the
   `DIVERGENCE` trigger fires (this is a real organic divergence). If
   not, the `DIVERGENCE` trigger is suppressed for this run (the new high
   is attributable to the new-model addition, which is already covered
   by `NEW_MODEL`). See §5.6.

7. **Per-trigger-type evidence enforcement: Option B (helper function).**
   See §5.7 for the rationale comparing Options A, B, C and the binding
   contract for the helper.

Coder dispatch may proceed on T2 with the seven binding notes in §5
applied. The CDA SME's review of T3 (drafter base + Bluesky drafter
prompts, the forbidden-vocab validator, the framing-check definitions)
is the next gate point and is the higher-leverage review.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T2 is the trigger-detector layer; no CDA elicitation protocol surface is touched. The detectors consume already-published `apps/dashboard/public/data/` JSON, not raw `data/raw/informants.jsonl`. No free-list, pile-sort, or pile-interview protocol logic. |
| Analytical validity | PASS-WITH-NOTES | T2's `detect_drift` correctly defers to Register-3 (Procrustes) without re-implementing the metric — it consumes the precomputed `drift/{model_family}.json` substrate from `cdb_publish/build.py`. T2's `detect_divergence` correctly consumes Register-2 outputs (pairwise similarity in MDS distance) without re-implementing the matrix computation. The methodology hazard surface is **threshold-setting and noise-band handling** (§5.1, §5.2), **first-run sentinel semantics** (§5.3), and **divergence ∩ new-model suppression logic** (§5.6) — all addressable in the §5 binding notes. **No software-side spend gates** are introduced. |
| Claims validity | PASS-WITH-NOTES | T2 introduces no public-facing prose, but the `evidence` payloads it constructs are consumed by T3 drafters and may appear in social-post text. Two §1.5 hazards in the evidence payload shape are addressable in §5: (a) DRIFT evidence must carry `model_version_returned` (not `model_id`) per CLAUDE.md §9 pitfall #1 — §5.1 binds this; (b) DIVERGENCE evidence must record both the prior high and the gap delta so the drafter can construct a properly-bounded "increased from X to Y (delta = Z)" claim — §5.2 binds this. The §1.5.7 forbidden-prediction-framing posture is unaffected by T2 (no claim is made by the trigger detection itself; claims are constructed at T3 drafter time). |
| Audience translation | PASS-WITH-NOTES | T2 itself does not author audience-facing prose, but the evidence-dict keys become available to T3 drafter prompts. The evidence-key names listed in the T1 schema docstring (schemas.py lines 692–700) are predominantly developer-facing data identifiers (`first_seen_in_domain`, `model_pair`, `gap_delta`, `procrustes_distance`) — none are §1.5.4-loaded. The single audience-translation concern is the T7 ARCHITECTURE.md amendment to §4.6 line 1211 (the "state of cultural alignment roundup" prose), which is already covered by §5.7 of the T1 verdict and remains carry-forward to T7. |

**Register compliance: PASS.** T2 is a publish-layer consumer of
Register-2 (similarity / divergence) and Register-3 (Procrustes drift)
outputs. T2 does not perform register computation; the registers are
computed by `cdb_analyze` and persisted by `cdb_publish`. The boundary
is preserved.

**Vocabulary compliance: PASS.** Scanned every LSB-authored string
proposed in the kickoff §3 T2 + the T1 schema docstring's evidence-key
enumeration. No new §1.5.4 violations introduced. The T1 verdict's §5.7
(re. ARCHITECTURE.md §4.6 line 1211 "state of cultural alignment" prose)
remains binding on T7; T2 itself is clean.

---

## 2. Rationale on the eight binding-decision questions

### 2.1. Question 1 — DRIFT_THRESHOLD = 0.15 placeholder

The Orchestrator's framing is correct: the threshold is unvalidated, the
data does not yet exist that would let it be validated, and the cron's
`enable_drift=False` flag is the lockout. The kickoff §2 out-of-scope item
1 and §8 risk 5 both make this explicit.

The methodology question is: **what guard rail exists when the lockout is
lifted?**

**Ruling:** the lockout flag alone is insufficient because flipping it is
a one-line config change with no SME review hook. T2 must add a
**runtime guard** at the entry to `detect_drift` that:

1. Inspects the underlying data shape (specifically: count of distinct
   `(model_version_returned, collection_date)` tuples for each
   `model_family`).
2. Raises `DriftDataInsufficientError` if fewer than the §4.2 Register-3
   minimum (≥ 8 shared items between any version pair) is satisfied.
3. Logs a `DriftPreFireWarning` (Python `logging.warning`) whenever
   `detect_drift` is called with `enable_drift=True` for the first time
   on data that does meet the §4.2 minimum — the log message names the
   `(model_family, version_pair, n_shared_items, computed_distance)` tuple
   and reminds the operator to surface to the CDA SME before allowing
   the trigger to fire on production data.

The runtime guard is **not** a spend gate (CLAUDE.md R13/R14 are not
violated); it is a methodological pre-fire interlock that costs zero API
dollars to evaluate. <!-- noqa: spend-gate-check -->

The `0.15` value stays as a top-of-module constant for now. When real
multi-date data lands, the threshold should be revisited at a dedicated
SME review against the empirical distribution of Procrustes distances.

The evidence payload for `DRIFT` triggers (schemas.py line 698) correctly
encodes `model_version_returned` (not `model_id`), which avoids the
CLAUDE.md §9 pitfall #1 hazard — the temporal anchor is the version
string, never the user-supplied alias.

### 2.2. Question 2 — divergence "new high" semantics

The Orchestrator surfaced three sub-questions: (a) bare-max vs CI-aware
comparison; (b) minimum-delta floor; (c) per-domain baseline scope.

**Ruling on (a) — CI-aware comparison:** the detector consumes
`apps/dashboard/public/data/{domain}.json`, which is a `cdb_publish`-
produced point-estimate-plus-CI substrate. The detector does **not**
re-run a bootstrap. The comparison is point-mean to point-mean. This is
**deliberately not** a hypothesis test — LSB does not make
hypothesis-confirming claims per §1.5.7 ("worldview" / "believes" /
"thinks" / "publishable" are the §1.5.4 forbidden vocabulary; the
analogous §1.5.7 forbidden frame is "the data confirms" / "the result
proves"). A bootstrap-CI-overlap test would frame divergence as a
hypothesis-testing surface, which is the wrong register.

**Ruling on (b) — minimum-delta floor:** add `MIN_DIVERGENCE_DELTA = 0.02`
as a top-of-module constant alongside `DRIFT_THRESHOLD`. The `0.02` floor
is set against the typical bootstrap-CI half-width visible on the
existing dashboard data (rough order: bootstrap mean similarity values
have CI half-widths in the 0.01–0.05 range; 0.02 is at the lower end of
that band — conservative). A new "high" that exceeds the prior high by
less than 0.02 is within noise and should not fire.

The 0.02 floor is itself a placeholder pending empirical-distribution
review on real data. Like `DRIFT_THRESHOLD`, it is a top-of-module
constant; revision is a future SME review.

**Ruling on (c) — per-domain baseline scope:** the baseline is the
per-domain maximum-pairwise-similarity-gap value, stored in
`state/divergence_highs.json` keyed by `domain_slug`. Median + N stddev
would be richer but couples the detector to a moment-statistic
assumption the data may not support (12 informants → poor moment
estimates). Maximum is appropriate at small n.

The detector's `evidence` payload (per the schemas.py docstring lines
696–697) carries `old_high`, `new_high`, `gap_delta`, and `model_pair`.
T2 must enforce that `gap_delta = new_high - old_high` and that
`gap_delta >= MIN_DIVERGENCE_DELTA` before emitting the trigger.

### 2.3. Question 3 — first-run bootstrap semantics

The Orchestrator surfaced: state-file-missing → first run or → state-lost.

**Ruling: state-file absence ≠ first run.** First run is defined by an
explicit sentinel inside the state file, not by file presence/absence.
The semantics:

- **State file present, contains `bootstrapped_at: datetime`:** normal
  operation. The detector compares the current observation against the
  stored baseline.
- **State file present, missing `bootstrapped_at` (legacy or corrupted):**
  raise `StateFileSchemaError`.
- **State file absent entirely:** raise `StateFileMissingError`. The
  cron orchestrator catches this and surfaces it to the operator — the
  operator must explicitly invoke a `bootstrap` subcommand to initialize
  the state file.

**Rationale:** if state-file-absence is treated as "first run," a state
deletion (accidental, malicious, or operator-error) silently re-emits
every model and every domain as "new." That's not a methodological event;
it's a data corruption. The right posture is fail-loud.

The kickoff §3 T2 acceptance sketch says "first-run bootstrap writes the
state file with current models and emits no triggers" — this is correct
*if* the operator explicitly triggers it. T2 must expose this as a
distinct entry point (CLI subcommand or function arg), not as the default
fallback when the file is missing.

### 2.4. Question 4 — `detect_monthly_roundup` firing time

The Orchestrator surfaced: first of month / last business day / specific
hour.

**Ruling: first cron run on or after the 1st of the month at 14:00 UTC.**
(The kickoff §3 T7 schedules the cron at `0 14 * * *`, so the first
cron firing of any given month is the natural anchor.) No business-day
weighting — LSB is a research-methodology project, not a marketing
calendar. The simplest rule that produces "one roundup per month"
deterministically is the right rule.

**Evidence-payload contract:** `evidence['month'] = "YYYY-MM"` is the
**previous** calendar month (the month being summarized), **not** the
current one. The state file `state/monthly_roundup.json` records:

```json
{
  "bootstrapped_at": "2026-05-17T14:00:00Z",
  "last_fired_month": "2026-05"
}
```

When the cron runs at 14:00 UTC on 2026-06-01, the detector reads
`last_fired_month: "2026-05"`, compares to "current month minus 1" =
`"2026-05"`, and **does not fire** (already fired for May). On 2026-07-01
the detector reads `"2026-05"`, compares to `"2026-06"`, fires the
trigger with `evidence['month'] = "2026-06"`, and updates
`last_fired_month` to `"2026-06"`.

**Dedupe-key construction:** `MONTHLY_ROUNDUP` triggers must include
`evidence['month']` in the canonical-JSON hash (per the schemas.py line
702–705 formula), which they will automatically because `evidence` is
part of the hash. This makes the dedupe key stable per month and prevents
double-firing within the same calendar month even if the state file is
corrupted.

### 2.5. Question 5 — dedupe re-fire procedure documentation

The Orchestrator surfaced: is the prompt-bump re-fire procedure
documented at T2 (in code or docstring)?

**Ruling:** the T1 schema docstring already documents the procedure at
schemas.py lines 706–716. T2 **must** cross-reference this in a module-
level docstring on `triggers.py`. Suggested wording:

> Trigger dedupe is keyed on `SocialTrigger.dedupe_key`, which is stable
> across `drafter_version` and `prompt_version` bumps. If the operator
> wants to re-fire a posted event under a new drafter prompt (e.g., to
> re-publish under a v2 prompt that produces clearer language), the
> manual procedure is:
>
> 1. Remove the relevant key from
>    `out/social/state/posted_dedupe_keys.json`.
> 2. The next cron run will re-fire the trigger (the `detect_*` function
>    re-emits the SocialTrigger; the orchestrator no longer skips it
>    because the key is gone from the dedupe state).
> 3. A new `SocialDraft` is produced with the bumped `prompt_version`.
>
> See cdb_core/schemas.py docstring on `SocialTrigger.dedupe_key` for
> the construction formula. See `docs/status/2026-05-17-phase7-T1-cda-
> sme-verdict.md` §5.8 for the methodological rationale.

This is documentation only; no code change beyond the module docstring.

### 2.6. Question 6 — divergence ∩ new-model interaction (§5.9 operationalized)

The Orchestrator surfaced: what is the right suppression rule? In
particular: if a new model is added AND an organic divergence event also
fires in the same run, should the divergence trigger be suppressed
entirely or fired with the new model excluded?

**Ruling: per-domain new-model exclusion.** The algorithm:

```
for each domain in published_data:
    new_model_triggers_this_run = detect_new_model(domain) ∩ this run
    new_models_added = {t.model_id for t in new_model_triggers_this_run}

    if new_models_added:
        # Recompute the pairwise-max similarity gap excluding the new
        # models for this domain. This isolates whether the new high
        # is attributable to organic drift in pre-existing models or to
        # the new-model addition.
        gap_excl = max_pairwise_gap(
            domain.similarity_matrix,
            exclude_models=new_models_added,
        )
    else:
        gap_excl = max_pairwise_gap(domain.similarity_matrix)

    stored_high = state.divergence_highs[domain.slug]
    if (gap_excl - stored_high) >= MIN_DIVERGENCE_DELTA:
        emit DIVERGENCE trigger with old_high=stored_high,
             new_high=gap_excl, gap_delta=(gap_excl - stored_high),
             model_pair=(argmax pairwise pair, excluding new models)
        update state.divergence_highs[domain.slug] = gap_excl
    # else suppressed; new high is attributable to new-model addition,
    # which is already covered by the NEW_MODEL trigger
```

**Rationale:** the alternative ("suppress divergence entirely for any
domain with a new-model event this run") is too coarse — it would lose
real organic divergence findings that happen to coincide with model
additions. The exclusion-then-recompare approach surfaces both events
where both are real and suppresses the divergence event only when the
new high is genuinely attributable to the new-model addition.

**Evidence-payload contract:** the `DIVERGENCE` trigger's `model_pair`
field (schemas.py line 696) must be the argmax pair *after* new-model
exclusion. The `evidence` may optionally include a `new_models_excluded:
list[str]` key for forensic transparency; T2 may add this if it surfaces
naturally in the implementation, but it is not binding.

**State-update ordering:** `state.divergence_highs[domain.slug]` is
updated only when the trigger fires (i.e., the gap exceeded the prior
high by ≥ MIN_DIVERGENCE_DELTA). If the new high is suppressed (because
it's attributable to new-model addition), the baseline is **not**
updated — the rationale being that the next run, with the new model now
in `seen_models`, will see the full gap including the new model and
should be allowed to compare against the original (pre-new-model)
baseline. Only an organic divergence updates the baseline.

### 2.7. Question 7 — Per-trigger-type evidence enforcement: Option A vs B vs C

The Orchestrator surfaced three options:
- **A:** `field_validator` on `SocialTrigger.evidence` that branches on
  `trigger_type`. Tightest; rigid.
- **B:** Helper function `validate_evidence_for_trigger_type(trigger)`
  called at trigger-emission sites in `triggers.py`. Looser; easier to
  extend.
- **C:** Pydantic discriminated union — five sub-types of
  `SocialTrigger`. Strictest; T1 rewrite.

**Ruling: Option B.** Rationale:

**Why not C:** Option C is a T1 schema rewrite. The T1 schemas have
already landed at commit `57745bd`; rewriting them now is high-friction
for marginal benefit. Discriminated unions also introduce serialization
gotchas (Pydantic discriminator-tag handling) that surface only when the
JSON is deserialized in non-Python contexts (e.g., a future tool that
reads the queue JSON outside of `cdb_social`). Future readers of the
queue JSON would need to understand the discriminator tag; the current
`evidence: dict[str, Any]` is more portable.

**Why not A:** Option A puts the validation inside the Pydantic model,
which means every consumer of `SocialTrigger` (including potential
future consumers in `cdb_publish` or future tooling) is forced to
validate evidence at construction time. This is too aggressive: future
tooling may want to construct a `SocialTrigger` from partial data (for
testing, for analysis, for replay), and the field-validator would block
those uses. The schema is supposed to be a transport contract, not a
business-logic gate.

**Why B (binding):** Option B places the validation at the *emission
site* — inside each `detect_*` function in `triggers.py`. Each function
calls `_validate_evidence(trigger)` immediately before appending to its
return list. The helper raises `EvidenceContractError` on miss. This:

1. Keeps the schema portable (no business-logic gates in the type).
2. Keeps the validation co-located with the function that knows the
   contract.
3. Is easy to test (each `detect_*` has its own emission-site test).
4. Is easy to extend (add a new trigger type → add a new validation
   branch).

**Helper signature contract (binding):**

```python
def _validate_evidence_for_trigger_type(trigger: SocialTrigger) -> None:
    """Validate that trigger.evidence contains the minimum keys required
    for trigger.trigger_type per the contract in schemas.py:684-701.

    Raises:
        EvidenceContractError: if any required key is missing or has the
            wrong type. The error message names the trigger_type, the
            missing/wrong key, and the expected shape.
    """
    minimum_keys_by_type = {
        TriggerType.NEW_MODEL: {
            "first_seen_in_domain": str,
        },
        TriggerType.NEW_DOMAIN: {
            "domain_slug": str,
            "n_models": int,
        },
        TriggerType.DIVERGENCE: {
            "domain_slug": str,
            "model_pair": list,  # list[str] of length 2
            "old_high": float,
            "new_high": float,
            "gap_delta": float,
        },
        TriggerType.DRIFT: {
            "model_version_returned": str,
            "procrustes_distance": float,
            "date_pair": list,  # list[str] of length 2
        },
        TriggerType.MONTHLY_ROUNDUP: {
            "month": str,  # YYYY-MM format
        },
    }
    # ... validation body
```

`EvidenceContractError` is a new exception type in `cdb_social/triggers.
py` (subclass of `ValueError`). The exception is **not** silenced; if
the contract is violated, the trigger emission fails loud and the cron
surfaces the error.

The Architect's ratification follow-up referenced in the Orchestrator's
invocation is **not needed** — Option B requires no schema change.

### 2.8. Question 8 — covered above as the §5.6 / §5.9 T1 advisories operationalization

(Treated as §2.6 above.)

---

## 3. Vocabulary compliance on T2-authored strings

Scanned every LSB-authored string surface implied by the kickoff §3 T2 +
the schemas.py evidence-key enumeration:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Top-of-module constant `DRIFT_THRESHOLD` | Technical descriptor (Procrustes distance threshold) | Compliant |
| Top-of-module constant `MIN_DIVERGENCE_DELTA` | Technical descriptor (similarity-gap noise floor) | Compliant |
| Function name `detect_new_model` | Technical descriptor | Compliant |
| Function name `detect_new_domain` | Technical descriptor | Compliant |
| Function name `detect_drift` | Technical descriptor (Register 3) | Compliant |
| Function name `detect_divergence` | Technical descriptor (Register 2 output) | Compliant |
| Function name `detect_monthly_roundup` | Technical descriptor | Compliant |
| Helper name `_validate_evidence_for_trigger_type` | Technical descriptor | Compliant |
| Exception name `EvidenceContractError` | Technical descriptor | Compliant |
| Exception name `DriftDataInsufficientError` | Technical descriptor | Compliant |
| Exception name `DriftPreFireWarning` (logging warning class, not exception) | Technical descriptor | Compliant |
| Exception name `StateFileMissingError` | Technical descriptor | Compliant |
| Exception name `StateFileSchemaError` | Technical descriptor | Compliant |
| State-file key `bootstrapped_at` | Data identifier (sentinel) | Compliant |
| State-file key `last_fired_month` | Data identifier | Compliant |
| Evidence key `first_seen_in_domain` (NEW_MODEL) | Data identifier | Compliant |
| Evidence key `n_models` (NEW_DOMAIN) | Data identifier | Compliant |
| Evidence keys `old_high`, `new_high`, `gap_delta`, `model_pair` (DIVERGENCE) | Technical descriptors | Compliant |
| Evidence keys `model_version_returned`, `procrustes_distance`, `date_pair` (DRIFT) | Technical descriptors; CLAUDE.md §9 pitfall #1 honored (`model_version_returned`, not `model_id`) | Compliant |
| Evidence key `month` (MONTHLY_ROUNDUP) | Data identifier | Compliant |
| Evidence key `new_models_excluded` (optional, DIVERGENCE) | Data identifier (forensic transparency) | Compliant |

No new §1.5.4 violations introduced.

---

## 4. The state-file-failure-mode landscape (cross-reference)

T2's state files (`out/social/state/{divergence_highs, seen_models,
seen_domains, monthly_roundup, posted_dedupe_keys}.json`) are
operator-recoverable but the failure modes matter:

| State file | Absence | Schema error | Stale entry |
|---|---|---|---|
| `seen_models.json` | Raise `StateFileMissingError` (per §5.3) | Raise `StateFileSchemaError` | Normal — drives next-run NEW_MODEL detection |
| `seen_domains.json` | Raise `StateFileMissingError` | Raise `StateFileSchemaError` | Normal — drives next-run NEW_DOMAIN detection |
| `divergence_highs.json` | Raise `StateFileMissingError` | Raise `StateFileSchemaError` | Normal — drives next-run DIVERGENCE detection; baseline updated only when DIVERGENCE fires |
| `monthly_roundup.json` | Raise `StateFileMissingError` | Raise `StateFileSchemaError` | Normal — drives next-run MONTHLY_ROUNDUP idempotency |
| `posted_dedupe_keys.json` | Treat as empty (the orchestrator owns this file, not the detectors; detectors don't read it) | n/a | Normal — accumulates over time |

The **single exception** to fail-loud-on-absence is
`posted_dedupe_keys.json`, which is owned by the orchestrator (not the
detectors) and is allowed to be absent on first run because its
absence does not imply state-loss of analytical baseline — it implies
"no posts have been emitted yet," which is a normal first-run state. The
distinction matters: `posted_dedupe_keys.json` is a *publish-side* state
file, not an *analytical-baseline* state file.

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T2 implementation. The
Reviewer enforces.

### 5.1. **DRIFT_THRESHOLD = 0.15 + runtime pre-fire interlock.** [Analytical validity, Claims validity]

The Coder adds the following to `cdb_social/triggers.py`:

```python
# Placeholder threshold per ARCHITECTURE.md §4.6 line 1209 ("start at 0.15,
# tune later"). The value is unvalidated against real multi-date data;
# the cron's enable_drift=False flag is the load-bearing lockout. When
# real multi-date data first lands, the threshold should be revisited at
# a dedicated CDA SME review against the empirical distribution of
# Procrustes distances.
DRIFT_THRESHOLD: float = 0.15

# Register-3 minimum item intersection per docs/SME_REVIEW.md (≥ 8 shared
# items between any version pair for Procrustes drift to be meaningful).
DRIFT_MIN_ITEM_INTERSECTION: int = 8

class DriftDataInsufficientError(ValueError):
    """Raised when detect_drift is invoked on data that does not satisfy
    the Register-3 minimum (≥ DRIFT_MIN_ITEM_INTERSECTION shared items
    between version pair). The lockout is data-shaped, not flag-shaped."""
```

The `detect_drift` function:

1. Inspects the data for each `(model_family, version_pair)` and counts
   the shared-item intersection.
2. Raises `DriftDataInsufficientError` if the count is below
   `DRIFT_MIN_ITEM_INTERSECTION`.
3. On the first call where data does meet the minimum, logs a
   `logging.warning("DRIFT_PRE_FIRE: ...")` naming the
   `(model_family, version_pair, n_shared_items, computed_distance)`
   and reminding the operator to surface to the CDA SME before allowing
   the trigger to fire on production data.

The `DRIFT_THRESHOLD = 0.15` and `DRIFT_MIN_ITEM_INTERSECTION = 8`
constants are top-of-module and have a comment-block above them
documenting their placeholder status and the SME re-review trigger.

The evidence payload (schemas.py line 698: `{'model_version_returned':
str, 'procrustes_distance': float, 'date_pair': [str, str]}`) is
correctly anchored on `model_version_returned`, not `model_id`. The
Coder must enforce this at emission time — `detect_drift` reads
`drift/{model_family}.json` and constructs evidence entries keyed on
`model_version_returned`, never falling back to `model_id`.

### 5.2. **`detect_divergence` MIN_DIVERGENCE_DELTA + point-mean comparison.** [Analytical validity]

The Coder adds:

```python
# Minimum-delta floor on divergence-gap increases. Placeholder pending
# empirical-distribution review. A new "high" within MIN_DIVERGENCE_DELTA
# of the prior high is within bootstrap-CI-noise and does not fire.
MIN_DIVERGENCE_DELTA: float = 0.02
```

`detect_divergence` consumes the bootstrap-mean pairwise similarity
values from `apps/dashboard/public/data/{domain}.json` — point-mean to
point-mean comparison, **not** a CI-overlap hypothesis test (LSB does
not make hypothesis-confirming claims per §1.5.7). The min-delta floor
is the noise-band guard.

The trigger fires when:

```
gap_excl - stored_high >= MIN_DIVERGENCE_DELTA
```

where `gap_excl` is the pairwise-max similarity gap **after** excluding
any newly-added models per §5.6 below.

The evidence payload contract (already in schemas.py line 696):

```python
evidence = {
    "domain_slug": str,
    "model_pair": [model_a, model_b],  # argmax pair, after new-model exclusion
    "old_high": float,                  # stored_high before this run
    "new_high": float,                  # gap_excl this run
    "gap_delta": float,                 # new_high - old_high
}
```

T2 must enforce `gap_delta == new_high - old_high` (a self-consistency
check at emission time) and `gap_delta >= MIN_DIVERGENCE_DELTA` (the
firing condition).

### 5.3. **First-run sentinel semantics; state-file absence ≠ first run.** [Analytical validity, Protocol-adjacent]

State files use an explicit sentinel `bootstrapped_at: datetime` to mark
first-run state. Semantics:

- Sentinel present → normal operation. Compare against stored baseline.
- Sentinel missing in an otherwise-present file → raise
  `StateFileSchemaError`.
- File entirely absent → raise `StateFileMissingError`. The cron
  orchestrator must catch this and surface to the operator. An explicit
  `bootstrap` subcommand initializes the file.

The Coder adds an explicit `bootstrap_state(state_dir)` function (or CLI
subcommand) that the operator invokes once on first install. The
function writes initial state files with current `seen_models`,
`seen_domains`, and `divergence_highs` from the current
`apps/dashboard/public/data/` snapshot, and stamps each with
`bootstrapped_at: <now>`. After bootstrap, the detectors operate
normally.

The kickoff §3 T2 acceptance sketch's "first-run bootstrap writes the
state file with current models and emits no triggers" is preserved —
but only when invoked explicitly via `bootstrap_state`, not silently on
file-absence.

### 5.4. **`detect_monthly_roundup` firing rule and evidence-payload contract.** [Analytical validity, Audience translation]

The detector fires on the first cron run on or after the 1st of each
calendar month at 14:00 UTC (the kickoff §3 T7 cron schedule).

Algorithm:

```python
def detect_monthly_roundup(state, today: datetime) -> list[SocialTrigger]:
    target_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    if state.last_fired_month == target_month:
        return []
    trigger = SocialTrigger(
        trigger_type=TriggerType.MONTHLY_ROUNDUP,
        detected_at=today,
        domain_slug=None,
        model_id=None,
        evidence={"month": target_month},
        dedupe_key=<computed>,
    )
    return [trigger]
```

`evidence['month']` is the **previous** calendar month (the month being
summarized), in `YYYY-MM` format. The state file records
`last_fired_month: YYYY-MM`.

No business-day weighting. No special-day handling. The simplest rule
that produces "one roundup per month" deterministically.

### 5.5. **`triggers.py` module docstring documents the dedupe re-fire procedure.** [Audience translation]

The Coder adds a module-level docstring to `cdb_social/triggers.py` that
cross-references the T1 schema docstring contract:

> Trigger dedupe is keyed on `SocialTrigger.dedupe_key`, which is stable
> across `drafter_version` and `prompt_version` bumps. If the operator
> wants to re-fire a posted event under a new drafter prompt, the
> manual procedure is to remove the relevant key from
> `out/social/state/posted_dedupe_keys.json`; the next cron run will
> re-fire the trigger and a new draft will be produced with the bumped
> `prompt_version`.
>
> See `cdb_core/schemas.py` docstring on `SocialTrigger.dedupe_key` for
> the construction formula. See
> `docs/status/2026-05-17-phase7-T1-cda-sme-verdict.md` §5.8 for the
> methodological rationale.

### 5.6. **Divergence ∩ new-model interaction: per-domain new-model exclusion.** [Analytical validity]

When `detect_new_model` emits one or more triggers for a domain in the
current run, `detect_divergence` for that same domain must recompute
the pairwise-max similarity gap **with the new-model informants
excluded**, then compare against the stored baseline using the
MIN_DIVERGENCE_DELTA floor.

Pseudocode in §2.6 above is binding. Key invariants:

1. `model_pair` in the emitted evidence is the argmax pair *after*
   exclusion (i.e., over pre-existing models only).
2. `state.divergence_highs[domain.slug]` is updated **only when the
   trigger fires** — suppressed-divergence runs do not update the
   baseline.
3. The new-model triggers (from `detect_new_model`) fire independently;
   the suppression rule only affects the DIVERGENCE trigger.

T2 may optionally include `evidence['new_models_excluded']: list[str]`
for forensic transparency. Not binding but advisory.

The orchestrator must call `detect_new_model` **before**
`detect_divergence` so the exclusion list is available. This is an
ordering constraint on the orchestrator, not on the detectors
themselves; T2 documents the constraint in a module-level note.

### 5.7. **Per-trigger-type evidence enforcement: Option B (helper function at emission sites).** [Analytical validity, Claims validity]

The Coder implements `_validate_evidence_for_trigger_type(trigger:
SocialTrigger) -> None` per the contract in §2.7 above. The helper:

1. Lives in `cdb_social/triggers.py` (not in `cdb_core/schemas.py` —
   this is business-logic, not transport-contract).
2. Branches on `trigger.trigger_type` and validates the minimum-keys
   contract from schemas.py lines 692–701.
3. Raises `EvidenceContractError` (new exception type, subclass of
   `ValueError`) on miss. The error message names the trigger_type,
   the missing/wrong key, and the expected shape.
4. Is called by each `detect_*` function immediately before appending
   to its return list.

The helper is fully unit-testable with synthetic `SocialTrigger`
instances per trigger type.

**No T1 schema rewrite required.** Option C is rejected; Option A is
rejected. See §2.7 for rationale.

---

## 6. Mark-escalation note

**No Mark escalation is required for T2 Coder dispatch.**

Two items Mark should be aware of for the T3 / T4 / T7 horizon:

1. The DRIFT_THRESHOLD = 0.15 and MIN_DIVERGENCE_DELTA = 0.02 constants
   are both placeholders. When real multi-date data lands (post the
   next collection campaign), a dedicated SME review against the
   empirical distribution is required before either threshold should
   be considered validated.

2. The T1 verdict §5.7 (re. ARCHITECTURE.md §4.6 line 1211 "state of
   cultural alignment roundup" prose) remains carry-forward to T7's
   ARCHITECTURE.md amendment. T2 does not introduce any new instance
   of that phrase; T7 must still execute the original §5.7 fix.

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T2:**
  - §5.1 (DRIFT_THRESHOLD constant + DriftDataInsufficientError +
    pre-fire warning log)
  - §5.2 (MIN_DIVERGENCE_DELTA constant + point-mean comparison +
    self-consistency check)
  - §5.3 (first-run sentinel semantics; explicit `bootstrap_state`
    function; fail-loud on file absence)
  - §5.4 (monthly_roundup firing rule + evidence-payload contract)
  - §5.5 (triggers.py module docstring documenting dedupe re-fire
    procedure)
  - §5.6 (divergence ∩ new-model per-domain exclusion algorithm + state-
    update ordering)
  - §5.7 (Option B evidence-enforcement helper +
    EvidenceContractError)
- **`cdb_core/schemas.py` change required:** **No.** Option B requires
  no schema change. The T1 schema docstring already enumerates the
  per-trigger-type minimum keys (schemas.py lines 692–701); T2 just
  enforces them at emission time.
- **`docs/DATA_DICTIONARY.md` change required:** **No.** Evidence-key
  enumerations live in the schema docstring; the Data Dictionary §13
  entry (landed at T1) is sufficient.
- **T7 doc-sweep flag carry-forward:** the T1 §5.7 ARCHITECTURE.md §4.6
  line 1211 prose revision remains binding on T7.
- **Architect ratification required:** **No.** The recommended Option B
  for evidence enforcement requires no schema change and no
  re-architecture.
- **Mark escalation:** §6 advisory only, non-blocking for T2 Coder
  dispatch.

---

*End of Phase 7 T2 CDA SME verdict.*
