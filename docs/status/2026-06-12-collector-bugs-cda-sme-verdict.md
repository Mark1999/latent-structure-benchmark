# COLLECTOR-BUGS BUG 3 implementation-diff verdict (CDA SME)

**Date:** 2026-06-12
**Reviewer:** CDA SME (Opus)
**Commit under review:** `bb85384` on branch `worktree-wf_4075b168-489-3`
**Plan verdict (this commit implements):** `docs/status/2026-06-12-collector-bugs-cda-sme-verdict.md` (originating PASS-WITH-NOTES; this file is the same status slot, now ratifying the implementation diff)
**Originating plan binding notes:** C1, C2, C3, C4, D1, D2, D3 from `.claude/agent-memory/cda_sme/project_collector_bugs_verdict.md`

---

## CDA SME VERDICT: PASS

```
Axis 1 - Protocol validity:      N/A  (no CDA protocol change; transport-event recording is operational metadata)
Axis 2 - Analytical validity:    PASS (BUG 3 correctly separates provider-transport events from decline-interview output classification; the `failure_scope="per_model"` context key reads as LSB-event-scoping at audit time)
Axis 3 - Claims validity:        PASS (C1/C2/C3 anti-attribution discipline satisfied at every added string surface; C4 absence-is-signal preserved)
Axis 4 - Audience translation:   PASS (commit body anti-attribution sentence reads as a skeptical-anthropologist disclaim; the four load-bearing nouns are present verbatim)

Register compliance:             PASS (failure records remain operational metadata, not Register 1/2/3 analytical output; no RWB-importing nouns introduced)
Vocabulary compliance:           PASS (no §1.5.4 forbidden vocabulary in any added string; em-dash discipline preserved on added text)
```

This verdict UNBLOCKS the Reviewer's prior procedural rejection. The implementation diff substantively complies with all four binding C-notes from the originating plan verdict. The remaining work in the pipeline is the Reviewer's standard pass and Tester verification, with no additional SME involvement required for this commit.

---

## Per-note compliance audit

### C1 (binding) - Failure-record language register

**Plan rule:** ALLOWED in any added log line, context key, or commit body: "transport-layer failure", "per-model boundary", "the adapter raised", "the API returned", "LSB recorded the failure". FORBIDDEN: "the model failed", "the model errored", "the model refused" (no decline-interview pipeline), "the model crashed", "the model's response", "model behavior" (applied to a transport event).

**Compliance:** PASS

Evidence (diff hunk):

- `scripts/collect.py` L417-420 (new logger.exception string):
  ```
  "The adapter raised an exception during cross-model sort for %s",
  adapter.model.model_id,
  ```
  Uses the allowed-list noun phrase "The adapter raised". No model-attribution verbs.

- `scripts/collect.py` L421-426 (new comment block):
  ```
  # LSB records the provider-transport event at the per-model boundary.
  # failure_scope="per_model" distinguishes model-level transport events
  # (the adapter raised before any pile-sort step completed) from
  # per-step failures written by run_cross_model_sort internally.
  # This is an LSB-side detection of a provider-transport event, not
  # an attribution of output or behavior to the model itself.
  ```
  Uses three allowed-list phrases ("LSB records", "the provider-transport event", "per-model boundary", "the adapter raised", "LSB-side detection"). The closing sentence explicitly rejects the forbidden reading ("not an attribution of output or behavior to the model itself") - this is a defensive disclaim, not an attribution.

- `tests/unit/test_collect_failure_record.py` L1-17 (new module docstring):
  Uses "transport-failure record", "the adapter raised" (L67 docstring, L65 function description), "LSB's detection of a provider-transport event" (L175), "the adapter raised" (L175), "LSB records the provider-transport event" (L317). The docstring at L11 cites the forbidden phrases in single quotes as a list of strings NOT checked here ("`('the model failed/refused/crashed') in any string checked here`"). This is a legitimate disclaim-by-quotation (analogous to the SME plan-verdict's own quotation of forbidden phrases in C1); the quotation is naming what is absent, not attributing.

- Forbidden-vocab grep on the full diff (`scripts/collect.py`, `tests/unit/test_collect_failure_record.py`, `tests/unit/test_collect_skip_collected.py`, commit body) for `model failed|model errored|model refused|model crashed|model's response|model behavior` (case-insensitive): single hit on the apologetic citation at L11 of `test_collect_failure_record.py`, ruled licit above. Zero hits for any other usage.

### C2 (binding) - Context key naming

**Plan rule:** Coder picks (a) `context["failure_scope"] = "per_model"` (SME preference) OR (b) `context["model_level"] = True` plus a one-line module-level anti-attribution comment.

**Coder choice:** (a). Implemented at `scripts/collect.py` L431: `"failure_scope": "per_model"`.

**Compliance:** PASS

Evidence:

- `scripts/collect.py` L427-432 (new context-dict body):
  ```python
  append_failure(e, {
      "model_id": adapter.model.model_id,
      "domain": domain_slug,
      "mode": "cross_model_consensus",
      "failure_scope": "per_model",
  }, FAILURES_JSONL)
  ```
  Key name `failure_scope` reads unambiguously as LSB-event-scoping. Value `"per_model"` reads as a scope label, not a model attribute.

- Test asserts the contract: `tests/unit/test_collect_failure_record.py` L249-251 asserts `ctx["failure_scope"] == "per_model"` with the inline comment "SME C2: failure_scope='per_model' distinguishes model-level transport events". The test fails LOUDLY if the key is renamed, locking the C2 contract into the suite.

### C3 (binding) - Anti-attribution sentence in commit body

**Plan rule:** Commit body MUST contain a verbatim anti-attribution sentence in the BUG 3 paragraph carrying four load-bearing nouns: "LSB's detection", "provider-transport event", "model output", "decline-interview pipeline".

**Compliance:** PASS

Evidence (commit body at `/opt/lsb-agent/.git/worktrees/wf_4075b168-489-3/COMMIT_EDITMSG` L26-28):

```
Anti-attribution sentence (CDA SME C3 four nouns): LSB's detection records the
provider-transport event in failures.jsonl. A transport failure is not a model
output event and does not enter the decline-interview pipeline.
```

Four load-bearing nouns present verbatim:
- "LSB's detection" - L26
- "provider-transport event" - L27
- "model output [event]" - L28 (lexeme "model output" present in compound construction)
- "decline-interview pipeline" - L28

The construction is a Coder rephrasing of the SME's plan-verdict canonical sentence, but the four-noun contract is preserved exactly. The two-sentence form ("LSB's detection records X. A transport failure is not Y.") is structurally an even clearer anti-attribution than the SME's original single-sentence form (it positively asserts the LSB-detection reading and negatively rejects the model-attribution reading in adjacent sentences). Licit.

A secondary appearance is in `tests/unit/test_collect_failure_record.py` L175-177:
```
LSB's detection of a provider-transport event (the adapter raised) is recorded
in failures.jsonl; no output from the model arrived. The record must not
attribute intent or behavior to the model itself per CDA SME C1.
```
This is a test docstring carrying the same anti-attribution disclaim. Not required by C3 (which binds the commit body only), but it ratchets the contract into the live test suite. Advisory plus.

### C4 (advisory) - append_failure kwargs preservation, absence-is-signal

**Plan rule:** `prompt_verbatim`/`response_verbatim`/`thinking_verbatim` passed when accessible; do NOT synthesize a placeholder `response_verbatim = ""` when no response arrived (absence-is-signal per CLAUDE.md §9 pitfall 10 + failures-are-findings).

**Compliance:** PASS

Evidence:

- `scripts/collect.py` L427-432: the new `append_failure(e, {...}, FAILURES_JSONL)` call passes ONLY `error`, `context`, `path`. No `response_verbatim=""` or `prompt_verbatim=""` synthesis. The kwargs default to None and `packages/cdb_collect/cdb_collect/jsonl.py` L110-115 correctly omits the field from the JSONL entry when None:
  ```python
  if response_verbatim is not None:
      entry["response_verbatim"] = response_verbatim
  ```
  The result: when the adapter raised before any response arrived, the failure record's JSON contains no `response_verbatim` key at all. Absence is materially distinguishable from empty string.

- Test enforces the contract: `tests/unit/test_collect_failure_record.py` L355-357:
  ```python
  assert "response_verbatim" not in entry, (
      "response_verbatim must be absent when no response arrived (CDA SME C4)"
  )
  ```
  Field absence is asserted, not empty-string equality. Locks C4 into the suite.

---

## Ambient framing-hygiene pass on BUG 1, BUG 2, VERIFICATION 4

Non-blocking per the plan-verdict's "SME does NOT re-review BUG 1, BUG 2, VERIFICATION 4 on methodology grounds" rule. SME ran a forbidden-vocab grep over the full diff to confirm no §1.5.4 leak landed in the bundled work.

### BUG 1 (`--skip-collected` domain-aware scoping)

- New helper `_load_collected_model_domain_pairs()` at `scripts/collect.py` L148-174: docstring, comments, and code use neutral language ("model-domain pairs", "domain-aware skip decisions"). No model-attribution. No forbidden vocab.
- D1 (2-tuple key choice) honored: docstring at L153-156 explicitly cites the SME advisory and the AC7 collision semantic. The choice is documented in the commit body per plan §3.1 AC15.
- Tests at `tests/unit/test_collect_skip_collected.py`: neutral test names ("test_load_pairs_multiple_domains", "test_ac7_food_record_with_any_mode_satisfies_skip"). No forbidden vocab.

### BUG 2 (campaign_id threading on non-single_pass modes)

- All four CLI dispatch sites (`scripts/collect.py` L702-705, L728-733) and three runner functions (`packages/cdb_collect/cdb_collect/runner.py` `run_two_pass` L411-413, `run_cross_model_sort` L601-603, `run_baseline_sort` L668-670) accept `campaign_id` and forward it. Docstrings describe the parameter neutrally ("Optional campaign identifier written into qa_notes"). No model-attribution.
- Fix-forward / no backfill posture explicit in commit body L15-16, consistent with `[[project_metadata_fix_forward_precedent]]`.

### VERIFICATION 4 (`lsb_inspect.py` not-a-bug)

- No code change. Disposition documented in `docs/status/2026-06-11-phase9b-food-campaign.md` L242-244 with the exact placeholder-semantic disclaim from the plan. The fix-trail section heading at L217 reads "COLLECTOR-BUGS fix trail (2026-06-12)" - matches plan §3.1 AC25 and the SME's D3 confirmation. No forbidden vocab.

Ambient verdict: clean. No §1.5.4 leak, no anti-attribution violation, no register confusion across the bundled work.

---

## Em-dash discipline

Grep for em-dash (U+2014) on added strings:
- `scripts/collect.py`: 7 hits, all pre-existing CLI status-print lines (L221, L238, L335, L440, L512, L623, L654). None in added comments, log strings, or context keys for BUG 3.
- `tests/unit/test_collect_failure_record.py`: 0 hits.
- `tests/unit/test_collect_skip_collected.py`: 0 hits.
- Commit body: 0 hits.

Em-dash discipline preserved on all added text.

---

## Required before merge

Nothing further required from the CDA SME. Reviewer's prior pass already confirmed substantive compliance; this verdict file closes the procedural gap that triggered the rejection.

The Reviewer may now re-issue PASS (or PASS-WITH-NOTES on non-methodology grounds the SME does not adjudicate) and route to Tester.

---

## Routing call

PASS. The implementation diff complies with C1, C2, C3, C4 in full. D1 (2-tuple key choice) honored with the SME-preferred option (a) and documented at code and commit-body level. D2 (VERIFICATION 4 disposition) and D3 (fix-trail heading) honored verbatim. No further SME involvement required for COLLECTOR-BUGS.

No carry-forward notes. The anti-attribution discipline established in this verdict applies to any future per-model transport-event handler the Coder adds; the canonical anti-attribution sentence template and the `failure_scope="per_model"` context-key contract become precedent.

[[project_collector_bugs_verdict]] is the plan-verdict ancestor of this implementation-diff verdict. [[project_metadata_fix_forward_precedent]] applies to BUG 2's no-backfill posture. [[project_failures_are_findings]] applies to BUG 3's transport-event recording (restoration of a previously-broken failure record path, not new claim-making).
