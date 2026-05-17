---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T1 — Social pipeline schemas + queue layout
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T1 — CDA SME verdict on the social-pipeline schema additions

**VERDICT: PASS-WITH-NOTES**

The three Pydantic types (`SocialTrigger`, `SocialDraft`, `SocialPostRecord`)
and the three enums (`TriggerType`, `Platform`, `PublishStatus`) proposed in
the Phase 7 kickoff §5 land **methodologically-coherent at the type level**
with the §1.5 / §1.5.4 framing — the field names are predominantly
descriptive-technical (`evidence`, `dedupe_key`, `platform_post_id`), the
two §1.5.4-load-bearing fields (`forbidden_terms_hit`, `framing_check_passed`)
are correctly named and correctly purposed, and the schema is net-new (no
`InformantRecord`/`GroundingRef` ripple). The schemas are approved for T1
implementation subject to **eight binding-at-Coder-dispatch notes** (§5
below) and **one binding name change** that the Coder must apply before
landing T1 (§5.1 — the `TriggerType.MONTHLY_ROUNDUP` enum value's
*semantic*, not the enum value's *name*; the value-string is approved as
`MONTHLY_ROUNDUP`, but the §4.6 architectural text "state of cultural
alignment roundup" that documents it is a §1.5 hazard and must be revised
in the T7 ARCHITECTURE.md amendment).

The eight CDA-SME questions surfaced in the Orchestrator's invocation are
each answered below in §2, with the binding outputs collected in §5 for
Coder reference. The headline rulings:

1. **`forbidden_terms_hit: list[str]`** — name is correct as proposed
   (§1.5.4 is enforced at substring/phrase level via the §1.5.4 left-column
   table; the validator at T3 will scan for those phrases as substrings,
   so the noun "terms" is the operating substrate). The richer
   match-metadata structure proposed in the Orchestrator's framing is
   **deferred** — the simple `list[str]` is sufficient for the
   queue-acceptance contract (must be `[]`), and richer metadata would
   couple T1 to T3 implementation choices. See §5.2.

2. **`framing_check_passed: bool`** — single boolean is **insufficient**
   on its own for forensic audit, but a structured replacement at T1 would
   couple T1 to T3 implementation choices (we don't yet know which framing
   checks T3 will define). The binding outcome: the `bool` stays at T1 as
   the queue-acceptance signal, **plus** T1 adds a sibling field
   `framing_checks: dict[str, bool] = {}` that T3 will populate keyed by
   check name. The queue contract is "`framing_check_passed=True` AND
   every value in `framing_checks` is `True`." See §5.3.

3. **`confidence_score: float`** — methodologically defensible only if
   renamed and explicitly scoped. The current name implies it is a
   calibrated drafter-quality signal, which it is not (drafter LLMs
   self-rating their own output is methodologically unreliable; LSB does
   not claim calibration). **Binding rename:** `drafter_self_rating:
   float = 0.0` with the schema docstring making explicit that this is
   not a methodological signal, is not used in any analysis, and is
   surfaced only as a drafter-internal heuristic for human-review
   prioritization. See §5.4.

4. **`suggested_posting_time: datetime`** — purely operational, not
   methodological. Approved as-is, with a docstring note that this field
   encodes *engagement-optimization timing* (not a methodological signal
   about when a finding is "ready"). See §5.5.

5. **`SocialTrigger.evidence: dict[str, Any]`** — unstructured `dict[str,
   Any]` is acceptable at T1 because each trigger type's evidence schema
   is decided in T2 (not T1). T1 adds a docstring contract: "each
   trigger type's evidence payload is documented in T2's docstring on the
   corresponding `detect_*` function; the `dict[str, Any]` shape is the
   T1↔T2 type-system contract, not a license for unstructured drift." T2
   will need a per-trigger-type evidence-schema review at SME gate time.
   See §5.6.

6. **`TriggerType.MONTHLY_ROUNDUP`** — the enum value name is approved.
   The methodological hazard is in the surrounding documentation text
   ("state of cultural alignment roundup" in ARCHITECTURE.md §4.6 line
   1211 and in the kickoff §3 T1 reference). "Cultural alignment" is
   §1.5-loaded for two reasons: (a) it collides with the AI-alignment
   field's term-of-art (RLHF, Constitutional AI, etc., which §1.5 uses as
   a *training-stage* descriptor — see ARCHITECTURE.md §1.5.1 line 100
   and §1.5.2 line 117); reusing the same word at a domain-output level
   blurs the construct. (b) The phrase "cultural alignment" plus a
   "state of" preamble implies a normative axis ("aligned with what?"),
   which §1.5.7 forbids — LSB ships exploratory measurements, not
   alignment scores. **Binding requirement at T7's ARCHITECTURE.md
   amendment** (not T1): the §4.6 line 1211 text is revised from
   "state of cultural alignment roundup" to "**monthly cross-domain
   categorical-structure roundup**" or equivalent §1.5-compliant phrasing.
   The enum value `MONTHLY_ROUNDUP` is fine; the prose around it is not.
   See §5.7.

7. **`SocialTrigger.dedupe_key: str`** — SHA256[:16] construction is
   stable for the current contract (one drafter per trigger per platform).
   The prompt-version-bump question is **deferred to T3+** because the
   drafter has not been implemented yet; T1's binding requirement is
   that the kickoff §3 T1 dedupe-key formula (trigger_type + domain +
   model + evidence-content-hash) **excludes** `drafter_version` and
   `prompt_version`. A prompt-version bump does not by itself justify
   re-firing a posted trigger; if a re-fire is wanted, that is a future
   manual operation. The schema does **not** need to encode this. See
   §5.8.

8. **`out/social/state/divergence_highs.json`** — first-run bootstrapping
   is approved (T2-level concern). The new-model-added interaction with
   the divergence baseline is a **real methodology hazard** but it lives
   in T2 (trigger logic), not T1 (schema). T1's only binding requirement
   is that the schema does **not** lock in a stale-baseline assumption.
   The `evidence: dict[str, Any]` shape per §5.6 above is permissive
   enough; T2 must surface the new-model-vs-baseline interaction at its
   SME gate. See §5.9 — advisory to T2.

Coder dispatch may proceed on T1 with the eight binding notes in §5
applied. The CDA SME's review of T2 (divergence detector, monthly roundup
trigger, evidence-payload schemas) and T3 (drafter validator forbidden-vocab
list, framing-check definitions) is the higher-leverage review and is the
next gate point.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T1 is a schema-only task; no CDA protocol surface is touched. The proposed schemas are net-new and do not interact with the free-list / pile-sort / pile-interview protocol or with the decline-interview follow-up protocol. |
| Analytical validity | N/A | T1 introduces no analytical computation. The §5.6 advisory routes the analytical-validity concern to T2's gate (the divergence detector's "new high" semantics, the drift-threshold placeholder of 0.15, and the monthly-roundup trigger's content scope). |
| Claims validity | PASS-WITH-NOTES | The schema-encoded fields that constrain claim-shape are `forbidden_terms_hit` (correctly enforces §1.5.4 left-column-table avoidance as a queue-entry precondition), `framing_check_passed` (correctly enforces hypothesis-framing avoidance per §1.5.7), and `confidence_score` (which currently overclaims calibration by its name — §5.4 binding rename to `drafter_self_rating`). The `MONTHLY_ROUNDUP` *enum value* is claims-compliant; the *surrounding ARCHITECTURE.md prose* ("state of cultural alignment") is not, and §5.7 binds a fix at T7. |
| Audience translation | PASS-WITH-NOTES | The field names are predominantly developer/data-engineer-facing and not exposed to journalists or researchers as prose. The methodology-page surface is unaffected by T1. The single audience-translation concern is the `confidence_score` field: even though it is an internal field, the open-data-bundle contract (if SocialDraft JSON is ever surfaced via the public site or via a data export) would surface "confidence_score: 0.87" as if it were a calibrated drafter quality metric, which a journalist could misread. §5.4's binding rename to `drafter_self_rating` defuses this. |

Register compliance: **PASS** — T1 is a publish-layer schema task that
does not touch Register 1 (OCI / output-distribution), Register 2 (Romney
CCM / between-model categorical structure), or Register 3 (Procrustes
drift). The drift-trigger function (T2) and the divergence-trigger
function (T2) consume Register 3 and Register 2 outputs respectively, but
the *consumption* is read-only against published JSON in
`apps/dashboard/public/data/` — no register computation happens at the
social-pipeline layer. The §5.6 advisory binds T2 (not T1) to keep this
boundary clean.

Vocabulary compliance: **PASS-WITH-NOTES** — scanned every LSB-authored
string proposed in the kickoff §3 T1 + §5 (field names, enum values,
docstrings implied by the kickoff text, the on-disk path components).
Full table in §3. Single violation surfaced: the §4.6 line 1211 prose
"state of cultural alignment roundup" — load-bearing as the source of
the `MONTHLY_ROUNDUP` enum's *intent*. §5.7 binds the fix at T7's
ARCHITECTURE.md amendment.

---

## 2. Rationale on the eight binding-decision questions

### 2.1. Question 1 — `forbidden_terms_hit: list[str]` name + contract

The Orchestrator surfaced three sub-questions: (a) name (`terms` vs
`phrases`); (b) match metadata (which §1.5.4 row matched); (c) queue
contract (must be `[]` for entry).

**Ruling on (a):** `forbidden_terms_hit` is the correct name. The §1.5.4
left-column table mixes phrase-level entries ("Model X believes...") and
token-level entries ("worldview," "believes," "thinks"). The validator at
T3 will substring-match against both; the substrate is mixed-granularity
strings. "Terms" is the standard ML/NLP gloss for this mixed-granularity
substrate (cf. "term-document matrix," "term frequency"). "Phrases" would
imply phrase-only matching and exclude the single-token entries.

**Ruling on (b):** richer match-metadata structure (e.g., `list[tuple[str,
int, str]]` for `(matched_term, row_index_in_§1.5.4_table,
matching_rule_id)`) is **deferred**. Two reasons: (i) the queue-acceptance
contract is binary ("`forbidden_terms_hit == []` ⇒ admit; else reject")
and a `list[str]` carries enough information for the human reviewer to
search for the offending term in the draft text; (ii) richer metadata
couples T1 to T3 implementation choices that have not been made. If T3's
validator produces match-metadata that exceeds `list[str]`, the structure
can be added as a sibling field (`forbidden_term_matches: list[dict]`)
without breaking the T1 contract.

**Ruling on (c):** queue-entry precondition `forbidden_terms_hit == []`
is correct and binding. See §5.2 for the validator wording the Coder
applies in the schema docstring.

### 2.2. Question 2 — `framing_check_passed: bool` granularity

The Orchestrator surfaced: single boolean vs structured `dict[str, bool]`.

The single boolean is **necessary but insufficient.** It is necessary as
the queue-acceptance signal (T5's review CLI and T6's publisher need a
single fast check). It is insufficient as a forensic audit trail
(post-mortem on a bad draft needs "did the hypothesis-framing check pass?
the bare-numeric check? the cognition-attribution check?").

**Ruling:** T1 adds **both**. `framing_check_passed: bool` is the
queue-acceptance signal (default `False`; T3 sets to `True` only after
all framing checks pass). `framing_checks: dict[str, bool] = {}` is the
forensic audit field (T3 populates with check-name → pass/fail). The
queue-acceptance contract becomes: `framing_check_passed == True` AND
all values in `framing_checks` are `True`. The `bool` is redundant given
the `dict`, but redundancy is the right posture for a methodology-gated
field — the `bool` is the simple-to-grep contract; the `dict` is the
audit trail. See §5.3.

### 2.3. Question 3 — `confidence_score: float` defensibility

The Orchestrator surfaced three options: (a) keep as `confidence_score`;
(b) rename to `drafter_self_rating`; (c) drop entirely.

LSB does not claim calibration on any analytical surface. Bootstrap CIs
are calibrated (we run N=1000 bootstrap replicates and report the
empirical-quantile-derived 95% interval). A drafter LLM self-rating its
own output is **not** calibrated — the LLM has no access to the
ground-truth distribution of "good drafts" vs "bad drafts" from which
its rating could be calibrated. Calling this field `confidence_score`
implies the same calibrated-statistic register as `mds_x_ci_high` or
`smith_s_95ci`, which it is not.

**Ruling: rename to `drafter_self_rating: float = 0.0`.** Rationale
in the docstring: "Drafter's self-reported heuristic score for ordering
human-review queue priority. Not calibrated. Not used in any analysis.
Surfaced only to the human reviewer at T5. Drafters that do not produce
a self-rating set this to `0.0`." See §5.4.

The Orchestrator's "(c) drop entirely" option is **not** taken because
the human-review CLI (T5) needs a stable priority signal for ordering
oldest-first-by-default; allowing the reviewer to also re-order by
self-rating is a useful affordance. The field's *existence* is fine;
the field's *name* is not.

### 2.4. Question 4 — `suggested_posting_time: datetime` methodology

The Orchestrator surfaced: operational vs methodological.

**Ruling: operational.** Posting-time recommendations encode
engagement-optimization heuristics (post during high-engagement windows
for the platform's audience), not methodological signals about when a
finding is "ready." T3's drafter prompt may set this field by
platform-specific logic (e.g., Bluesky has different peak-engagement
windows from X/LinkedIn) and that logic is platform-marketing, not
methodology.

The Coder must include in the schema docstring: "Operational hint for
when the platform's audience is most active. Not a methodological signal
about the finding's readiness. The human reviewer at T5 may override or
ignore." See §5.5.

### 2.5. Question 5 — `SocialTrigger.evidence: dict[str, Any]` schema rigor

The Orchestrator surfaced: unstructured `dict` vs per-trigger-type
minimum schema.

A per-trigger-type schema at T1 would couple T1 to T2 implementation
choices (which evidence fields each trigger needs). T2 has not been
designed yet (it ships after T1).

**Ruling: unstructured `dict[str, Any]` at T1**, **plus a docstring
contract** that names the trigger-evidence-schema-design responsibility
as a T2 deliverable. T2's gate (CDA SME review of `triggers.py`) is the
correct enforcement point. The kickoff already lists T2 as CDA-SME-gated
(kickoff §3 T2 gates row).

See §5.6 for the docstring wording and the advisory carry-forward to T2.

### 2.6. Question 6 — `TriggerType.MONTHLY_ROUNDUP` content scope

The Orchestrator surfaced: is the enum value name OK; is the content
scope safe to enumerate now.

**Ruling on the enum value name:** `MONTHLY_ROUNDUP` is **approved as-is**.
The enum value is a data-identifier-shaped token; it does not surface as
prose to the audience. (Cf. the Phase 6 T9 verdict §3 ruling that
`originating_outcome_class` enum values are surfaced verbatim without
§1.5.4 risk because they are data identifiers.)

**Ruling on the content scope:** the content scope lives in T3 (drafter
prompt) and is reviewed at T3's SME gate, not now. The Orchestrator's
binding constraint to me ("the roundup *content* is T3 drafter
territory") is correct.

**The §1.5 hazard is** the prose in ARCHITECTURE.md §4.6 line 1211 that
calls this trigger a "state of cultural alignment roundup." The phrase
"cultural alignment" is loaded:

- **AI-alignment-field collision.** §1.5.1 line 100 and §1.5.2 line 117
  use "alignment" as a *training-stage* descriptor (RLHF, Constitutional
  AI, post-training). Reusing the same word to label a roundup of model
  *outputs* invites the reader to fuse two distinct constructs:
  alignment-as-training-stage (an upstream process) and
  alignment-as-output-property (a §1.5.4-loaded metric of "how aligned
  models' outputs are with each other" or "with human values"). LSB
  measures *neither* of those — it measures categorical structure of
  model output distributions.

- **Normative-axis implication.** "State of [X] alignment" is a
  Strategic-Survey-shaped phrase (cf. "state of AI safety," "state of
  alignment research"). It implies a single normative axis along which
  models are measured. §1.5.7 forbids LSB from making any
  prediction-then-confirm claim; "state of cultural alignment" implies
  exactly such a claim ("models are/are not converging to a desired
  state").

**Binding requirement:** the T7 ARCHITECTURE.md amendment that records
the §4.6 / §2 path-conflict resolution must **also** revise the §4.6
line 1211 prose. Suggested replacement (Architect may iterate): "monthly
cross-domain categorical-structure roundup — a once-monthly digest
post that surveys the most recent measurements across domains, models,
and runs." The kickoff §5 schema additions stay; the prose around them
changes. See §5.7.

### 2.7. Question 7 — `dedupe_key` stability across prompt-version bumps

The Orchestrator surfaced: does a prompt-version bump warrant re-firing
an already-posted trigger.

The kickoff §5 line 167 specifies `dedupe_key: str` as `SHA256[:16](
trigger_type + domain + model + evidence content-hash)`. This formula
**correctly excludes** `drafter_version` and `prompt_version`.

**Ruling:** the exclusion is correct. A prompt-version bump means we
have rewritten the drafter (T3) such that the *style* of the output
changes; it does not mean the underlying finding has changed. Re-firing
a posted trigger because the drafter's prompt rev'd would (a) duplicate
the finding on the platform (bad audience experience), (b) implicitly
claim the new prompt produces a "better" finding (a calibration claim
LSB does not make), (c) couple the post stream to drafter-internal
versioning that the audience has no context for.

If a re-fire is wanted (e.g., because a v2 drafter produces a much more
readable post that the operator wants to re-publish), that is a future
*manual* operation — the human operator removes the dedupe-key entry
from `state/posted_dedupe_keys.json` and the next cron run re-fires the
trigger. The schema does not need to encode this affordance.

**Binding requirement at T1:** the schema docstring on
`SocialTrigger.dedupe_key` records the formula and explicitly notes the
exclusion of `drafter_version` and `prompt_version`. See §5.8.

### 2.8. Question 8 — divergence baseline + new-model interaction

The Orchestrator surfaced: when a new model is added to the slate, the
divergence baseline shifts — does the new-model event invalidate the
baseline?

This is a **real methodology hazard** but it lives in T2 (the
`detect_divergence` function), not T1 (the schema).

**Ruling:** T1 places no constraint that would prevent T2 from doing the
right thing. The `evidence: dict[str, Any]` field per §5.6 is permissive
enough for T2 to record (a) the baseline value at the time of detection,
(b) the new value, (c) the gap delta, (d) whether the gap is new-because
-of-a-model-add (which would suppress the divergence trigger) vs
new-because-of-a-real-finding-shift (which would fire it).

**Advisory carry-forward to T2:** the divergence detector must
distinguish between "new high because a new model was added with extreme
output" and "new high because existing models' outputs drifted further
apart." The former is a new-model event (already covered by the
`NEW_MODEL` trigger type) and should suppress the `DIVERGENCE` trigger
to avoid double-firing. The latter is a legitimate divergence event.
T2's `detect_divergence` function needs to consume `state/seen_models.
json` (already in the kickoff's state file list) to make this
distinction. See §5.9.

---

## 3. Vocabulary compliance on T1-authored strings

Scanned every LSB-authored string surface implied by the kickoff §3 T1 + §5:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Pydantic class name `SocialTrigger` | Data identifier (post-worthy event) | Compliant |
| Pydantic class name `SocialDraft` | Data identifier (queued draft) | Compliant |
| Pydantic class name `SocialPostRecord` | Data identifier (publish outcome) | Compliant |
| Enum class `TriggerType` | Data identifier | Compliant |
| Enum value `NEW_MODEL` | Data identifier | Compliant |
| Enum value `NEW_DOMAIN` | Data identifier | Compliant |
| Enum value `DRIFT` | Data identifier; Register 3 construct (Procrustes), §1.5-compliant in this register | Compliant |
| Enum value `DIVERGENCE` | Data identifier; describes a measurable property of pairwise model similarity (Register 2 output), §1.5-compliant | Compliant |
| Enum value `MONTHLY_ROUNDUP` | Data identifier; the enum value name is fine. The surrounding ARCHITECTURE.md §4.6 prose "state of cultural alignment roundup" is the §1.5 hazard, addressed at T7 per §5.7. | Compliant (enum value); the surrounding prose is not (§5.7) |
| Enum class `Platform` | Data identifier | Compliant |
| Enum value `BLUESKY`, `X`, `LINKEDIN` | Data identifiers | Compliant |
| Enum class `PublishStatus` | Data identifier | Compliant |
| Enum value `PUBLISHED`, `FAILED`, `DRY_RUN`, `RETRY_PENDING` | Technical descriptors of pipeline outcome | Compliant |
| Field name `trigger_type` | Data identifier | Compliant |
| Field name `detected_at` | Data identifier (timestamp) | Compliant |
| Field name `domain_slug`, `model_id` | Data identifiers (cross-reference to existing schemas) | Compliant |
| Field name `evidence` | Data identifier (trigger payload) | Compliant |
| Field name `dedupe_key` | Data identifier (idempotency token) | Compliant |
| Field name `draft_id` | Data identifier | Compliant |
| Field name `trigger` | Data identifier (back-reference) | Compliant |
| Field name `platform` | Data identifier | Compliant |
| Field name `text` | Data identifier (draft content) | Compliant |
| Field name `text_history` | Data identifier (edit audit trail) | Compliant |
| Field name `image_path` | Data identifier | Compliant |
| Field name `suggested_posting_time` | Operational hint. Compliant. See §5.5 docstring requirement. | Compliant |
| Field name `confidence_score` | **Overclaims calibration.** §5.4 binding rename to `drafter_self_rating`. | **Not compliant. Binding rename required.** |
| Field name `methodology_url` | Data identifier (configurable link target) | Compliant |
| Field name `dashboard_url` | Data identifier | Compliant |
| Field name `forbidden_terms_hit` | §1.5.4-gate identifier; correctly names the queue-acceptance precondition | Compliant |
| Field name `framing_check_passed` | §1.5.7-gate identifier; correctly names the boolean queue-acceptance signal | Compliant. **Plus** §5.3 sibling field `framing_checks: dict[str, bool]` required. |
| Field name `drafter_version` | Data identifier (versioning) | Compliant |
| Field name `prompt_version` | Data identifier (versioning, per CLAUDE.md §6 R7) | Compliant |
| Field name `created_at` | Data identifier (timestamp) | Compliant |
| Field name `published_at`, `platform_post_id`, `platform_post_url`, `publish_status`, `error_message` | Data identifiers (publish outcome) | Compliant |
| On-disk path component `out/social/queue/{pending,approved,published,failed}/` | Workflow-state directories; technical descriptors | Compliant |
| On-disk path component `out/social/state/{divergence_highs, seen_models, seen_domains, monthly_roundup, posted_dedupe_keys}.json` | State-file identifiers; technical descriptors | Compliant |
| ARCHITECTURE.md §4.6 line 1211 prose "state of cultural alignment roundup" | **§1.5 hazard.** Conflates training-stage "alignment" with output-property "alignment"; implies a normative axis. | **Not compliant. Binding T7 fix per §5.7.** |
| Kickoff §3 T1 reference "monthly state of cultural alignment roundup" | Inherited from §4.6 | Will be fixed by §5.7's T7 amendment |

Two violations surfaced. Both are addressable inside the existing Phase 7
task graph (T1 for the `confidence_score` rename; T7 for the §4.6 prose
amendment).

---

## 4. The methodology-page-link concern (cross-reference to existing decisions)

The kickoff §2 out-of-scope item 2 and §8 risk 4 both flag the
methodology-page deep-link gap (Phase 6 T1+T2 are blocked on Mark-authored
prose; drafters will link to `cogstructurelab.com/{domain}` instead).

T1's schema field `methodology_url: str` correctly makes this a
configurable per-draft field; once Mark's methodology prose ships, a
config change on the drafter sets `methodology_url =
"cogstructurelab.com/methodology"` (or whatever the canonical path is)
and every future draft links there.

**No CDA SME binding action at T1.** The field's existence as a
per-draft string (rather than a global constant baked into the drafter)
is the right architecture; the field's value at run time is operational.

The T7 cron's first invocation will set the field; the Reviewer at T7
must verify the field is read from config (not hardcoded) and that the
default value points to the per-domain article shell.

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T1 implementation. The
Reviewer enforces. They do not require re-planning by the Architect,
with the single exception of §5.7 (which binds T7's ARCHITECTURE.md
amendment, not T1 itself).

### 5.1. **`MONTHLY_ROUNDUP` enum value name approved; surrounding prose deferred to §5.7.**
The enum value name is approved as `MONTHLY_ROUNDUP`. No change to the
enum at T1. The §1.5 hazard in the *surrounding ARCHITECTURE.md prose*
is addressed at T7 per §5.7 below.

### 5.2. **`forbidden_terms_hit: list[str]` — docstring contract.** [Claims validity]

The Coder includes in the `SocialDraft` schema docstring (Pydantic
class-level docstring) for this field:

> Substrings from the §1.5.4 language-guardrails table (ARCHITECTURE.md
> §1.5.4) that the drafter's output matched during the T3 post-generation
> validation pass. A draft with any matched terms **must not** be admitted
> to the queue; the queue-acceptance precondition is
> `forbidden_terms_hit == []`. The T5 review CLI and the T6 publisher
> both enforce this precondition. Populated by T3's `validate_draft()`.

The Coder must **not** add richer match-metadata at T1 (e.g., per-match
row indices, per-match rule IDs). If T3 produces richer metadata, T3
adds a sibling field at T3 implementation time.

### 5.3. **`framing_check_passed: bool` + new sibling `framing_checks: dict[str, bool] = {}`.** [Claims validity]

The Coder adds **both** fields to `SocialDraft`:

```python
framing_check_passed: bool = False
framing_checks: dict[str, bool] = {}
```

Docstring on `framing_check_passed`:

> Single-boolean queue-acceptance signal for the §1.5 / §1.5.7 framing
> checks. Default `False`; the T3 drafter sets to `True` only after
> every per-check entry in `framing_checks` is `True`. The queue-acceptance
> precondition is `framing_check_passed == True` AND every value in
> `framing_checks` is `True` (the redundancy is intentional: the bool
> is the fast-grep contract; the dict is the forensic audit trail).

Docstring on `framing_checks`:

> Per-check audit trail keyed by framing-check name (e.g.,
> `"hypothesis_framing"`, `"cognition_attribution"`,
> `"bare_numeric_without_ci"`). Each value is `True` if that check
> passed. The T3 drafter populates this dict; T5 reviewers and post-mortem
> analyses consume it. The exact set of check names is defined by T3.

The Coder does **not** define the check-name set at T1 — that is a T3
deliverable. T1 only defines the type-system contract.

### 5.4. **Rename `confidence_score: float` → `drafter_self_rating: float = 0.0`.** [Claims validity, Audience translation]

The Coder applies this rename and updates the field's docstring:

```python
drafter_self_rating: float = 0.0
```

Docstring:

> Drafter's self-reported heuristic score for ordering the
> human-review queue (T5's review CLI may sort by this field). **Not
> calibrated.** Not used in any analysis. Not surfaced on the public
> dashboard or in the open data bundle. Drafters that do not produce a
> self-rating set this to `0.0`. The score is not a methodological
> signal about draft quality; it is an internal drafter heuristic for
> operator convenience.

The Coder updates `docs/DATA_DICTIONARY.md` §13 to match: the field name
is `drafter_self_rating`, not `confidence_score`, throughout the
dictionary entry.

### 5.5. **`suggested_posting_time: datetime` — operational-only docstring.** [Audience translation]

The Coder adds to the field's docstring:

> Platform-specific operational hint for posting time based on
> audience-engagement windows. Not a methodological signal about the
> finding's readiness. The T5 reviewer may override or ignore. T3
> drafters compute this field per platform; the algorithm is
> platform-marketing-internal and is not part of LSB's methodological
> claims.

### 5.6. **`SocialTrigger.evidence: dict[str, Any]` — docstring contract + T2 carry-forward.** [Analytical validity, advisory]

The Coder adds to `SocialTrigger.evidence`'s docstring:

> Trigger-type-specific evidence payload. The expected shape of this
> dict for each `TriggerType` value is documented in T2's
> `cdb_social/triggers.py` module on the corresponding `detect_*`
> function. The `dict[str, Any]` shape is the T1↔T2 type-system
> contract, not a license for unstructured drift. T2's CDA SME gate
> reviews the per-trigger-type evidence-payload schema.

**Advisory carry-forward to T2:** the per-trigger-type evidence schema
will be reviewed at T2's SME gate. The CDA SME's expectation is that
each `detect_*` function's docstring enumerates exactly which keys
appear in the evidence dict and what they mean.

### 5.7. **T7 ARCHITECTURE.md amendment must revise §4.6 line 1211 prose.** [Vocabulary compliance]

The T7 ARCHITECTURE.md amendment is already scoped to bump §4.6 to
record the `out/social/queue/` path resolution. T7 **must also** revise
the §4.6 line 1211 text:

- **Current text (violates §1.5):**
  > 5. Scheduled: monthly "state of cultural alignment" roundup.

- **Replacement text (§1.5-compliant):**
  > 5. Scheduled: monthly cross-domain categorical-structure roundup —
  >    a once-monthly digest post that surveys recent measurements across
  >    domains, models, and runs.

Rationale: the phrase "state of cultural alignment" (a) collides with
the AI-alignment-field's term-of-art for training-stage processes
(RLHF, Constitutional AI), which §1.5.1 line 100 and §1.5.2 line 117
use as a *training-stage* descriptor, and (b) implies a normative axis
that §1.5.7 forbids ("state of X" implies LSB has a position on what X
*should* be).

The Architect must also update the kickoff §3 T1 reference at
docs/status/2026-05-17-phase7-architect-kickoff.md line ~52 (if Mark
elects to amend the kickoff for consistency) and any T3-prompt-content
references that inherit this phrase. The kickoff amendment is
recommended but not blocking on T1; the T7 ARCHITECTURE.md fix is
binding.

### 5.8. **`SocialTrigger.dedupe_key: str` — docstring records the formula and the exclusions.** [Claims validity, Audience translation]

The Coder adds to `SocialTrigger.dedupe_key`'s docstring:

> Stable idempotency key for the trigger event. Construction:
> `SHA256(trigger_type + "|" + (domain_slug or "") + "|" +
> (model_id or "") + "|" + canonical_json(evidence))[:16]`.
>
> The formula intentionally **excludes** `drafter_version` and
> `prompt_version`. A drafter-prompt bump does not by itself justify
> re-firing a posted trigger; if a re-fire is needed (e.g., to
> re-publish under a new drafter), that is a manual operation —
> the operator removes the entry from
> `out/social/state/posted_dedupe_keys.json` and the next cron run
> emits a fresh draft.

The exact canonicalization (sort dict keys, normalize whitespace, etc.)
is a Coder implementation detail; the docstring must specify "canonical
JSON serialization" as the formula's contract.

### 5.9. **Divergence-trigger / new-model-add interaction — advisory to T2.** [Analytical validity, advisory]

T1 has no binding constraint here. The schema's `evidence: dict[str,
Any]` shape is permissive enough for T2 to record whatever it needs.

**Advisory carry-forward to T2:** the `detect_divergence` function must
distinguish between (a) a new high caused by adding a new model to the
slate (which should suppress the `DIVERGENCE` trigger to avoid
double-firing with the `NEW_MODEL` trigger that fires on the same
event), and (b) a new high caused by drift in existing models' outputs
(which should fire the `DIVERGENCE` trigger).

T2's `detect_divergence` must consume `state/seen_models.json` (already
in the kickoff's state file list) to make this distinction.
T2's SME gate will review the suppression logic.

---

## 6. Mark-escalation note

**No Mark escalation is required for T1 Coder dispatch.**

Two items Mark should be aware of before T7 ships:

1. **§5.7's ARCHITECTURE.md amendment to §4.6 line 1211** is a small
   prose change that the Architect can roll into the T7 amendment
   batch. The fix is required (the current prose is a §1.5 hazard) but
   the timing is at T7, not at T1.

2. **§5.4's rename `confidence_score` → `drafter_self_rating`** is the
   only field rename in the §5 binding notes; the Coder applies it at
   T1 implementation. If Mark would prefer to keep `confidence_score`
   for any reason (e.g., consistency with an external convention), the
   CDA SME's position is that the rename is binding for §1.5
   audience-translation reasons; an override would need a documented
   architectural decision (CLAUDE.md §4 row 4).

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T1:** §5.2 (forbidden_terms_hit docstring),
  §5.3 (framing_check_passed + new framing_checks sibling),
  §5.4 (rename confidence_score → drafter_self_rating + docstring),
  §5.5 (suggested_posting_time docstring),
  §5.6 (evidence docstring + T2 carry-forward note),
  §5.8 (dedupe_key formula + exclusions docstring)
- **Architect must apply at T7:** §5.7 (ARCHITECTURE.md §4.6 line 1211
  prose revision)
- **Advisory to T2:** §5.6 (per-trigger-type evidence schemas reviewed at
  T2's SME gate); §5.9 (divergence-trigger / new-model-add interaction)
- **`cdb_core/schemas.py` change required:** Yes — the schema additions
  in kickoff §5, with the §5.3 sibling field added and the §5.4 rename
  applied
- **`docs/DATA_DICTIONARY.md` §13 update required in same PR:** Yes
  (already in the kickoff's acceptance criteria; the §5.4 rename and
  §5.3 sibling field flow through)
- **T14 doc-sweep flag raised:** Yes — §5.7's ARCHITECTURE.md §4.6 prose
  revision is the T7-bound doc-sweep item
- **Mark escalation:** §6 advisory only, non-blocking for Coder dispatch

---

*End of Phase 7 T1 CDA SME verdict.*
