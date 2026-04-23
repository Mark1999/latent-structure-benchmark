# Decline-Interview Protocol — Design Note

**Document name:** `docs/DECLINE_INTERVIEW_PROTOCOL.md`
**Version:** v0.1 (design note pending CDA SME review)
**Status:** Proposed — blocks Phase 4a T5 analysis on its narrative side. Does NOT block T5 data side (see Architect verdict).
**Audience:** CDA SME (for PASS/PASS-WITH-NOTES/FAIL on methodology); Architect (for schema sign-off post SME); Coder (for implementation post SME and Architect PASS).
**Companion docs:** `ARCHITECTURE.md` §1.5 framing (binding on prompt wording), §4.1 CDA step definitions, §5.3 Phase 4; `docs/SME_REVIEW.md`; `docs/SHAKEDOWN_PROTOCOL.md` §1/§3 (protocol-versioning precedent); `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream B.

---

## 0. What this document is

A methodological design note for a new CDA protocol step: when a model **declines** or **responds unexpectedly** on a primary step (free-list, pile-sort, or interview), the collector runs a follow-up elicitation asking the model to describe what happened. The captured transcript becomes part of the open bundle and feeds the Phase 6+ dashboard failure-display surface.

**Trigger:** Mark's binding directive of 2026-04-23, captured at `memory/project_failures_are_findings.md`:

> If the LLM responds in an unexpected manner or for some reason refuses to do the task, then interview the LLM informant as follow up questions.

**Methodological grounding:** anthropological fieldwork convention — when an informant declines a task, the ethnographer asks about the decline rather than treating the non-response as null. The parallel is not exact (an LLM has no lived experience of "declining"), but the data practice is appropriate: preserve the refusal surface, elicit explanatory text, treat the combined object as a first-class finding.

**Scope boundary:** this protocol captures and preserves. It does **not** analyze the decline-interview content into Register 1 or Register 2 structure in v1 (see §5 below). Register 3 discourse analysis over decline transcripts is Phase 7+, explicitly out of scope.

---

## 1. The 6 design decisions

Per the Architect's Stream B decomposition, there are six questions. I record my orchestrator-level proposals below, clearly marking which are **SME territory** (SME rules) vs **Architect-ruled** (Architect has already ruled; SME may concur or refuse but cannot silently override).

### 1.1 Prompt design — **SME TERRITORY**

The SME must rule on the prompt wording. Three draft candidates for their consideration; none is binding until SME PASS.

**Candidate A — neutral observational.**

> "The preceding step produced [no output | output that did not parse | empty output]. Could you say what happened?"

Notes: uses "could you say" rather than "why," avoids "refuse" and "decline" (both presuppose agency). Observational rather than diagnostic.

**Candidate B — task-framed.**

> "The task I just asked you to perform was [task description]. The output I received was [verbatim quote or 'none']. What does that tell us about the task or your response?"

Notes: frames the non-response as a data point about the interaction, not an attribute of the model. Can be run on the original domain slug (family or holidays) without naming the "refusal."

**Candidate C — minimal.**

> "Please describe what happened when I asked you to [task description]."

Notes: shortest. Invites free-form explanation without any framing at all.

**§1.5 compliance:** all three candidates avoid "worldview," "believes," "thinks," "refuse" (applied to the model as an agent), "cultural bias." The SME should grep their chosen final form against `ARCHITECTURE.md` §1.5.4.

**Temperature:** proposed 0.7 (same as free-list step per §4.1.3). The decline-interview is free-text elicitation, not a structured task; higher temperature is appropriate.

### 1.2 Synchronous vs asynchronous — **ARCHITECT-RULED: asynchronous**

The Architect verdict §Stream B ruled: **asynchronous Phase 4a.1 remediation pass, not synchronous**.

Rationale (from Architect verdict):
- Synchronous couples the decline-interview into `run_informant`, forcing a schema change on the primary step path and inflating every run's latency.
- Async decouples the protocol; model-version drift between the original session and the follow-up is auditable via `model_version_returned` on each record.
- Async lets us decide per-session whether to re-interview (some cells may not warrant follow-up).

SME concern to address: is model-version drift between the original session and the follow-up a methodological problem? Phase 4a.1 happens hours-to-days after Phase 4a, during which provider-side model snapshots may update. The follow-up's `model_version_returned` captures whatever version actually responded; the analyst can confirm (or refute) continuity. If the SME finds the drift unacceptable, the alternative is synchronous and the Architect will re-scope.

### 1.3 Refusal detection — **JOINT SME + ARCHITECT: deterministic rules only**

**Binding constraint:** no LLM classifier. `CLAUDE.md` §6 rule 12 forbids LLM imports in `cdb_analyze`, and while `cdb_collect` is allowed LLM calls for collection, using an LLM to classify another LLM's output is a classifier-pattern the rule's spirit disallows. Deterministic Python rules only.

**Proposed detection (two triggers, OR-combined):**

1. **Session landed in `failures.jsonl`** with any non-transient error class. Transient (rate-limit, 5xx) errors are retried by the existing runner; non-transient errors (parse failures, HTTP 4xx with no retry, timeouts that exhausted retries) are candidates for decline-interview.

2. **Session landed in `informants.jsonl` with `qa_passed=False`** AND one of:
   - (a) Pile-sort `parsed_piles` has **0 items** (matches the Gemini-pile-sort-empty pattern).
   - (b) Pile-sort `response_verbatim` matches a refusal-string allowlist (proposed seed list: `"I can't"`, `"I cannot"`, `"I'm not able"`, `"I am unable"`, `"I won't"`, `"I decline"`, `"I refuse"`, case-insensitive, word-boundary). The list lives in `packages/cdb_collect/cdb_collect/decline_detection.py` and is auditable; new entries require Architect sign-off per Reviewer.
   - (c) Free-list `parsed_items` has **0 items**.
   - (d) Interview `parsed_labels` has **0 items** AND interview `response_verbatim` non-empty (i.e., the model produced text but it didn't structure as labels).

The SME rules on the allowlist seed and on the item-count thresholds. Future refinements require Architect sign-off.

**Against which sessions does the rule fire?** Applied once at detection time (end of T4-class collection), producing a list of `(informant_id-or-failure-id, detected_reason)` pairs. The Phase 4a.1 remediation pass iterates over this list and issues one follow-up call per pair.

### 1.4 Data model — **SME TERRITORY, Architect preference: new sibling type**

**Architect preference (non-binding on the SME):** create a new sibling type `DeclineInterview` persisted to `data/raw/decline_interviews.jsonl`, keyed by the `informant_id` of the originating session (or a synthetic ID for sessions that failed before `informant_id` was assigned).

**Rationale:**
- A 4th step on `InformantRecord` would force the append-only record to be mutated (violates R10 / R2) or force every record everywhere to carry an empty 4th step.
- Sibling type keeps `InformantRecord` v0.7 stable.
- A decline-interview is methodologically distinct from the three CDA steps — it's about the session, not a cognitive-domain elicitation.

**Proposed schema** (for Architect sign-off after SME PASS on methodology):

```python
class DeclineInterview(BaseModel):
    decline_interview_id: str                       # hash of (originating_id, prompt_version, sha256_manifest)
    originating_informant_id: str | None            # informant_id of the InformantRecord being followed up on
    originating_failure_id: str | None              # failure-entry ID if the origin was in failures.jsonl
    originating_outcome_class: Literal[...]          # per §1.3 trigger (gemini-empty, refusal-string, exception, etc.)
    detection_timestamp: datetime
    followup_timestamp: datetime
    model_id: str                                    # what model ran the follow-up (should match origin unless drift)
    model_version_returned: str                      # as returned by the follow-up API call
    provider: str
    api_endpoint: str
    prompt_version: str                              # e.g., "decline_v1"
    sha256_manifest: str                             # hash of the decline prompt
    prompt_verbatim: str                             # the exact decline prompt used
    response_verbatim: str                           # the exact bytes the model returned
    thinking_verbatim: str                           # reasoning trace if surfaced, else ""
    input_tokens: int
    output_tokens: int
    latency_ms: int
    stop_reason: str
    cost_usd: float
    qa_notes: str = ""
```

Exact field list subject to SME/Architect refinement. The `originating_*` pair is an xor (one or the other), not both.

**R7 co-update:** `docs/DATA_DICTIONARY.md` gets a new section documenting `DeclineInterview` and `data/raw/decline_interviews.jsonl`. Same-PR with the schema change per Reviewer rule R7.

**Gitignore:** `data/raw/decline_interviews.jsonl` is already covered by the `data/raw/` gitignore rule.

**Build-db:** `scripts/build_db.py` must know to include the new JSONL in the open bundle SQLite. Add a `decline_interviews` table keyed by `decline_interview_id` with FK to `informants.informant_id` where applicable.

### 1.5 Analysis integration — **SME TERRITORY, Architect preference: reported but not analyzed**

**Architect preference:** in v1, decline-interviews are **reported** (dashboard, methodology page, open bundle) but **not analyzed** into Register 1/2 structure.

**Rationale:**
- Register 2 consumes pile-sort matrices; a decline-interview has no pile-sort matrix.
- Register 1 (within-model variance) could theoretically compute over decline-interview lexical features, but doing so would require a qualitative→quantitative step (embedding, topic modeling, clustering) that is Phase 7+ Register 3 territory.
- Surfacing the raw transcripts on the dashboard (Stream C) is the v1 analytical commitment.

**SME ruling question:** is "reported but not analyzed" an acceptable disposition, or does v1 require at least a typology (e.g., "this refusal was a safety policy hit; this was a capability limitation; this was a parse-format mismatch")? If the latter, that's a new analysis task with its own Coder decomposition and is not Phase 4a scope.

### 1.6 Backfill timing — **ARCHITECT-RULED: NO backfill before T5**

The Architect verdict §Stream B ruled: **T5 proceeds on 101 records + failures.jsonl + 19 missing cells. Decline-interview applies to Phase 4a.1 remediation (after Stream A closes and Stream B design lands) and to Phase 4b onward.**

Rationale:
- Backfilling now blocks T5 on a protocol that hasn't been SME-reviewed yet.
- The 19 missing cells are already a finding per the 2026-04-23 directive; T5 can report them as-is.
- Phase 4a.1 is a clearly-scoped follow-up task that applies the full decline-interview protocol retroactively once the protocol is SME-approved and implemented.

SME concern to surface: is the T5 narrative weakened by reporting "X cells refused, we have no further context" instead of "X cells refused, here's what they said when asked to explain"? If the SME wants the richer narrative before T5, they'll need to either (a) reverse this ruling and block T5 on full decline-interview implementation, or (b) approve a narrower synchronous version that runs during T5 prep. This is worth naming explicitly in the SME verdict.

---

## 2. Out of scope

The following are explicitly NOT in this protocol's v1 and require separate Architect decomposition if they ever land:

- **LLM-based classifier for refusal detection.** Deterministic rules only. A classifier drifts toward the §6 rule 12 boundary.
- **Retroactive decline-interviews on T3 shakedown records.** Only Phase 4a canonical + Phase 4b onward.
- **Cross-linking decline-interview content into Register 1/2 analysis.** Phase 7+.
- **Human coding / thematic analysis of decline transcripts.** Phase 7+ methods-page contribution.
- **Real-time refusal surfacing to the dashboard during live collection.** Phase 6+ and only after the base failure-display surface is built.

---

## 3. What the SME is asked to rule on

Per Architect gate table, this note goes to the CDA SME for a **four-axis verdict**:

- **Protocol validity** — is the decline-interview methodologically legitimate as a CDA-adjacent step? Is "interview a declining informant" the right frame, and does the LSB adaptation respect §1.5 framing?
- **Analytical validity** — is "reported but not analyzed in v1" correct, or must a typology exist? Are the detection triggers deterministic enough for SME comfort?
- **Claims validity** — what public-copy claims can v1 make from decline-interview data? What claims are forbidden? If the 19 missing Phase 4a cells remain uninterviewed at T5 time, what does T5's copy say about them?
- **Audience translation** — how does the decline-interview surface on the dashboard without implying defect (§1.5 compliance)? What methodology-page content must accompany it?

**Specific asks for the SME:**

1. **Pick or refine** the prompt candidate in §1.1.
2. **Concur or dissent** on the async-Phase-4a.1 sync/async ruling (§1.2).
3. **Approve or refine** the refusal-detection rule set in §1.3, including the seed allowlist.
4. **Concur or dissent** on the sibling-type data model in §1.4.
5. **Concur or dissent** on reported-but-not-analyzed in §1.5.
6. **Concur or dissent** on no-backfill-before-T5 in §1.6.

PASS / PASS-WITH-NOTES / FAIL on each axis. Overall verdict PASS, PASS-WITH-NOTES, or FAIL.

If FAIL on any single item, state what must change before re-review. PASS-WITH-NOTES is acceptable; notes flow into the #26 implementation Coder brief.

---

## 4. Downstream dependencies

If the SME issues PASS or PASS-WITH-NOTES:

1. Architect re-reviews the exact schema for `DeclineInterview` (a short follow-up; mostly mechanical given §1.4).
2. Coder implements (#26): `schemas.DeclineInterview`, `cdb_collect/decline_detection.py` with the deterministic rules, `cdb_collect/run_decline_interview.py` for the follow-up API call, `DATA_DICTIONARY.md` update, `build_db.py` update, unit tests on fixtures.
3. Coder runs Phase 4a.1 pass (#21): detect + follow-up on every Phase 4a session matching the rules, write to `data/raw/decline_interviews.jsonl`, report.
4. Phase 4a T5 and T6 proceed in parallel with #26/#21. T5 narrative can reference the existence of the decline-interviews without requiring them in hand.

---

*End of design note. Awaiting SME review.*
