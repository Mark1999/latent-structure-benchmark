---
name: project-collector-bugs-verdict
description: COLLECTOR-BUGS Architect plan PASS-WITH-NOTES 2026-06-12; BUG 1 (--skip-collected scoping), BUG 2 (campaign_id threading), BUG 3 (transport-failure records), VERIFICATION 4 (lsb_inspect.py not-a-bug). Methodological binding notes on BUG 3 failure-record language and §1.5.4 framing.
metadata:
  type: project
---

# COLLECTOR-BUGS Architect plan verdict 2026-06-12 — PASS-WITH-NOTES

Surfaced by 2026-06-11 Phase 9b food campaign trail. Three collector defects + one not-a-bug verification, fix-forward in one commit.

**Why:** BUG 3 (transport-failure record append at the per-model boundary) introduces new failure-record language and `context` keys at sites the SME has not previously adjudicated. Per CLAUDE.md §1.5 binding-on-all-generated-text rule + §1.5.4 forbidden vocab, the language must classify the LSB-side detection event, not the model's behavior. `http_error` enum value on `DeclineInterview.originating_outcome_class` (schemas.py L769) is the taxonomy-correct value; raw failure records in `data/raw/failures.jsonl` use `error_type = type(error).__name__` via `append_failure` (jsonl.py L106) and are NOT schema-bound, so no cdb_core change is needed (correctly enforced as a stop-condition in plan §4 + §9).

**How to apply:** four binding C-notes on BUG 3 language + context keys; one carry-forward on BUG 1 tuple-key choice; one on the campaign-trail fix-trail section heading.

## Bound notes (verbatim required where strings are bound)

**C1 (binding, BUG 3 — failure-record language register).**
The plan's §3.1 AC18 / AC21–AC22 use the framing "model-level transport failure" and `context["model_level"] = True`. This is licit under §1.5.4 noun-class test (the right-hand noun is the LSB-side event class, not a model-attribution claim). The Coder must NOT introduce alternate phrasings that re-attribute the event to the model. Specifically:
- ALLOWED in any added log line, context key, or commit body: "transport-layer failure", "per-model boundary", "the adapter raised", "the API returned", "LSB recorded the failure".
- FORBIDDEN in any added log line, context key, commit body, or test fixture comment: "the model failed", "the model errored", "the model refused" (when no decline-interview pipeline is involved), "the model crashed", "the model's response", "model behavior" (when applied to a transport event).
The distinction is: a 400 Bad Request from microsoft/phi-4's provider is a provider-transport-layer event detected by LSB; it is not a model-output event. The decline-interview pipeline classifies model outputs, not transport events. Plan §5 already states this correctly; C1 promotes it from analysis-validity prose to binding string-text rule.

**C2 (binding, BUG 3 — context key naming).**
The plan suggests `context["model_level"] = True` as the per-model-boundary marker. The phrase "model_level" reads ambiguously — it could be read as "level of the model" (model-attribution) or "level at which LSB caught this" (LSB-event-scoping). The latter is the intended reading and is licit. To remove the ambiguity at audit time, the Coder picks ONE of:
- (a) `context["failure_scope"] = "per_model"` — explicit LSB-event-scoping noun.
- (b) `context["model_level"] = True` AND a one-line module-level comment immediately above the key's first call site reading verbatim:
  `# Marks an LSB-side per-model-boundary detection (transport event), not an attribution to the model. See CDA SME C1/C2 in docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md.`
SME preference: (a). Either resolves C2.

**C3 (binding, BUG 3 — anti-attribution sentence in commit body).**
Commit body MUST contain a verbatim anti-attribution sentence in the BUG 3 paragraph, one of:
- "These failure records classify LSB's detection of a provider-transport event (e.g., HTTP 400 from a model's API endpoint). They do not classify model output behavior and are not inputs to any decline-interview pipeline."
- The Coder may rephrase but the four load-bearing nouns are non-negotiable: "LSB's detection", "provider-transport event", "model output", "decline-interview pipeline". Forbidden-vocab grep extension applies (CLAUDE.md §7 spot check).

**C4 (advisory, BUG 3 — append_failure kwargs preservation).**
The plan's §3.1 AC18 invokes `append_failure(...)` with the existing kwargs contract. Verify on review that `prompt_verbatim`/`response_verbatim`/`thinking_verbatim` are passed when the per-model boundary has access to them (model-level transport failures typically don't have a response; that's correct — `None` defaults apply). The Coder must NOT synthesize a placeholder `response_verbatim = ""` when the response truly did not arrive; absence-is-signal per CLAUDE.md §9 pitfall 10 + the failures-are-findings memory.

## Carry-forward / non-blocking notes

**D1 (carry-forward, BUG 1 tuple-key choice).**
Plan §3.1 AC1 offers 2-tuple `(model_id, domain_slug)` or 3-tuple `(model_id, domain_slug, collection_mode)`. The SME does not block on this choice — it is implementation-detail. But: if the Coder picks 2-tuple, a model already collected for food/single_pass would be skipped for food/cross_model under `--skip-collected`. Plan §3.1 AC7 actually depends on this collision behavior (it asserts model A IS skipped for food cross_model when A has a food single_pass record). The 2-tuple is consistent with AC7. The 3-tuple is more conservative for future hygiene (separate runs per mode). SME preference: 2-tuple, since AC7 already locks the semantic. The 3-tuple is future-proof but contradicts AC7. The Coder picks; document choice in commit body per plan AC15.

**D2 (advisory, VERIFICATION 4 disposition wording).**
Plan §3.1 AC25 prescribes the verbatim disposition string. Methodologically clean (it accurately describes placeholder semantic without attributing intent). No SME redraft needed.

**D3 (advisory, fix-trail section heading).**
Plan AC25 specifies the section title "COLLECTOR-BUGS fix trail". SME confirms — neutral, no model-attribution risk.

## Axes summary

- Axis 1 (Protocol validity): N/A — no CDA protocol change.
- Axis 2 (Analytical validity): PASS — BUG 3's separation of transport events from decline-interview output classification is correct (C1 promotes plan §5 prose to binding rule).
- Axis 3 (Claims validity): PASS-WITH-NOTES — C1/C2/C3 enforce anti-attribution at log-string + commit-body + context-key level.
- Axis 4 (Audience translation): PASS-WITH-NOTES — C3 commit-body sentence reads as a skeptical-anthropologist disclaim; required.
- Register compliance: PASS (failure records are operational metadata, not Register 1/2/3 analytical output).
- Vocabulary compliance: PASS-WITH-NOTES (C1 extends forbidden grep to BUG 3 added strings).

## Routing call

PASS-WITH-NOTES. Hand to Coder. No UI/UX gate (plan §6 correctly skips). No cdb_core schema change. No DATA_DICTIONARY change. CDA SME does NOT re-review BUG 1, BUG 2, or VERIFICATION 4 on methodology grounds; SME reviews BUG 3 implementation diff for C1/C2/C3 compliance before commit lands.

[[project_metadata_fix_forward_precedent]] applies to BUG 2 (no backfill). [[project_failures_are_findings]] applies to BUG 3 (restoration, not new claim-making).

## Implementation-diff verdict 2026-06-12 (commit bb85384) — PASS

Re-adjudicated after Reviewer procedural rejection (verdict file did not exist). Now persisted at `docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md`. All four binding C-notes substantively satisfied at the diff level:

- **C1 (language register):** `scripts/collect.py` L417-420 new logger.exception uses "The adapter raised an exception during cross-model sort"; L421-426 new comment block uses "LSB records the provider-transport event at the per-model boundary" + explicit closing disclaim "not an attribution of output or behavior to the model itself". Forbidden-vocab grep on full diff: one apologetic citation in `tests/unit/test_collect_failure_record.py` L11 (quoting forbidden phrases as a list of NOT-checked strings) — licit disclaim-by-quotation. Zero substantive hits.
- **C2 (context key):** Coder chose SME-preferred option (a) — `context["failure_scope"] = "per_model"` at L431. Test asserts the contract at `tests/unit/test_collect_failure_record.py` L249-251 with inline C2 citation. Lock-in via test suite.
- **C3 (commit body anti-attribution):** COMMIT_EDITMSG L26-28 carries all four load-bearing nouns verbatim ("LSB's detection", "provider-transport event", "model output", "decline-interview pipeline"). The Coder used a two-sentence form (positive assertion + negative disclaim) that reads as a stronger anti-attribution than the SME's single-sentence template. Licit.
- **C4 (absence-is-signal):** New `append_failure(e, {...}, FAILURES_JSONL)` call at L427-432 passes only error/context/path, never synthesizes empty `response_verbatim`. `jsonl.py` L110-115 correctly omits None fields. Test asserts `"response_verbatim" not in entry` (not equality to empty string), locking C4.

Ambient framing-hygiene pass on BUG 1 / BUG 2 / VERIFICATION 4 portions of the bundled diff: clean. No §1.5.4 leak. D1 (2-tuple key) honored with documentation in code and commit body. D2 + D3 honored verbatim in campaign-trail update. Em-dash discipline preserved on all added text (7 pre-existing print-line em-dashes in scripts/collect.py unchanged; zero in added strings).

Reviewer's prior procedural rejection now unblocked. No further SME involvement on COLLECTOR-BUGS. The anti-attribution sentence template + `failure_scope="per_model"` context-key contract become precedent for any future per-model transport-event handler.
