---
name: project_cr_t4_successes_artifact
description: CR-T4 successes-summary artifact verdict 2026-06-10. PASS-WITH-NOTES; framing_note byte-identical; rejects "answered correctly" framing.
metadata:
  type: project
---

CR-T4 Architect plan PASS-WITH-NOTES 2026-06-10. Per-domain successful-record SUMMARY artifact at `apps/dashboard/public/data/records/{slug}.json`, mirroring [[project_phase6_T9_failures_publish_verdict]] failures-publish posture. Publish-layer schema only; no `cdb_core` edit.

**Load-bearing framing_note** (byte-identical from this verdict into `_FRAMING_NOTE` in `cdb_publish/successes.py`; Coder copy-pastes, no paraphrase):

> These records summarise collection sessions for which the LSB pipeline parsed a primary-step response. Each row reports the run count, the QA-pass count, and the provider-returned model-version string for a single `model_id` in this domain. A row is a property of the LSB collection pipeline's parsing outcome, not a quality judgment on the model output. The full per-record bytes are available in the open data bundle under CC0; the unsuccessful counterpart sessions are surfaced under `data/failures/{slug}.json`. See the methodology page for the corpus-lens framing.

(Architect-stubbed candidate accepted with one edit: "available in" inserted in the bundle clause for parallelism with the failures `_FRAMING_NOTE` clause structure. No em dashes; "summarise" UK spelling retained to match the failures note's `_FRAMING_NOTE` formality register — verify against failures.py before commit; if failures uses US spelling, switch to "summarize" for project-wide consistency.)

**Why:** Successful is a parser-state property of the pipeline, not a quality judgment. Anti-attribution sentence ("not a quality judgment on the model output") is the symmetric twin of failures' "not a claim about the model's intent or state-of-mind." Cross-link to failures artifact preserves the matched-pair posture.

**How to apply:** Any future amendment to this string requires fresh SME verdict. Any T5/T7 surface that re-displays the note must inherit it byte-identical (no per-surface rewording). Any change to phrase "successful" anywhere in dashboard copy must NOT use "correct," "right," "good," or "high-quality" — those slip into quality judgment.

**Open methodological calls resolved in this verdict:**
- §3 `model_version_returned` per row: ACCEPT Architect's lex-greatest + sibling `model_version_returned_count: int` count of distinct strings. Rationale: faithful to the snapshot-roll reality from CLAUDE.md §9 pitfall #1 without ballooning row width with full lists; the count surfaces the rolled-snapshot case for any downstream consumer that needs to disambiguate. Alternative considered (full list per row) deferred to T7 per-record JSON where the full per-informant version string is available anyway.
- §8 `n_qa_passed` inclusion: KEEP in summary. The gap between `n_runs` and `n_qa_passed` is itself a finding under "failures are findings." Removing it from the summary would force the dashboard (T5) to fetch the per-record T7 detail JSON for what is a single integer per row.
- §8 row order: lexicographic by `model_id` ascending APPROVED. Deterministic, no implicit ranking signal. NOT `n_runs` desc (implies ranking) and NOT `provider` first (implies provider partition is the primary cut).

**Binding notes (Coder must apply):**
- N1: `framing_note` is byte-identical to the quoted string above. No paraphrasing, no copy-edits at code time.
- N2: The docstring at the top of `successes.py` MUST NOT contain the phrase "successful answer," "correct answer," "answered correctly," "good response," or any variant attributing quality to the model output. Use "parsed primary-step response" or "parser succeeded on primary-step output."
- N3: Empty-domain `by_model: []` files MUST still carry the full `framing_note`. Empty is not absent.
- N4: `provider` per-row aggregation: the plan's "lex-smallest with WARNING log on multi-provider" is fine but the WARNING message MUST NOT say "model lied about its provider" or any anthropomorphic phrasing. Recommended wording: "model_id X in domain Y has multiple provider strings in raw informants — lexicographically smallest selected for summary row; full per-informant provider strings remain in the open data bundle."
- N5: `DATA_DICTIONARY.md` §12 new subsection MUST state explicitly: "Successful here means the LSB pipeline parsed a primary-step response. It is NOT a quality judgment on the model output." Same anti-attribution clause that lives in the JSON's `framing_note` is mirrored in the dictionary prose.
- N6: Manifest field name `records: dict[str, str]` is approved. Mirrors `failures: dict[str, str]` posture. No `successes` plural in the dict key — would conflate with the artifact's framing_note posture.

**Carry forward to T5 (dashboard) and T7 (per-record detail):**
- T5: any prose label rendering "n_qa_passed" to the reader uses "QA-pass count" or "runs that passed software-only QA," NOT "valid runs" / "good runs" / "successful answers."
- T7: per-record detail JSON inherits the framing-note posture; any per-record file MUST carry the same anti-attribution sentence at the file-level.

Linked: [[project_phase6_T9_failures_publish_verdict]] (matched-pair precedent), [[project_phase9a_T1_failures_restore_verdict]] (top-level Collection-records tab placement context).
