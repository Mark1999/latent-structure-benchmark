# LSB Data Dictionary

**Document name:** `docs/DATA_DICTIONARY.md`  
**Version:** v0.1.11 (aligned with `ARCHITECTURE.md` v0.7; see changelog for history)  
**Status:** Phase 0 / Phase 1 deliverable per `ARCHITECTURE.md` §4.3  
**Audience:** External researchers using the LSB open data bundle; LSB internal contributors touching the schema  
**Companion docs:** `ARCHITECTURE.md` §3.2 (schema source of truth), §4.3 (storage), §6.7 (open data policy)

**Stability promise:** this document moves in lockstep with `cdb_core/schemas.py`. Any change to `InformantRecord`, `GroundingRef`, or any other schema documented here requires a matching update to this file in the same PR. The Reviewer agent enforces this (Reviewer rule 5 in `ARCHITECTURE.md` §5.1). Adding new optional fields is non-breaking; removing or renaming a field is a breaking change that requires a major version bump and a migration note in the changelog.

**Changelog:**
- **v0.1.11** (2026-05-04) — Task #16.B: Added `thoughts_token_count: int = 0` to `FreelistRecord`, `PileSortRecord`, and `InterviewRecord` step schemas. Field captures provider-reported reasoning/thoughts token count per step, enabling the cap-exhausted-reasoning diagnostic (`output_tokens == 0 AND thoughts_token_count > 0`). Default `0` (not `None`) preserves arithmetic ergonomics and prevents false-positives on providers that do not surface reasoning tokens (Anthropic, HuggingFace at this version). Added `thoughts_token_count` as an optional top-level field in `failures.jsonl` entries (§9.2) and to both `freelist` and `pile_sort` sub-objects in `partial_session` (§9.3). Added three new columns (`freelist_thoughts_token_count`, `pilesort_thoughts_token_count`, `interview_thoughts_token_count`) to the `informants` table DDL in `scripts/build_db.py`. Backward-compatible: Pydantic v2 with `int = 0` default loads old JSONL lines lacking the field with the value materialised as `0`. Architect sign-off: `docs/status/2026-05-04-task-16-architect-plan.md` §2 Task 16.B. CDA SME verdict: `docs/status/2026-05-04-task-16-cda-sme-verdict.md` (notes S1–S4 applied to field semantics below). Predecessor: Task 16.A (commit `7f8f7f7`) added `thoughts_token_count` to `AdapterResult` and both adapters.
- **v0.1.10** (2026-05-01) — Task #F2-T13: `cost_usd` field removed from `RawResponse` and `DeclineInterview`. The field was a token-count × table-rate estimate, not authoritative billing data; authoritative spend lives on provider dashboards per `ARCHITECTURE.md` §6.2. Pydantic v2 default `extra='ignore'` semantics handle existing on-disk records: the legacy field is silently dropped on read; no edits to existing JSONL lines. `cost_usd` column also removed from the `decline_interviews` table DDL in `scripts/build_db.py` and from `DATA_DICTIONARY.md` §10.2, §10.4, and §10.5. Reference: Task 1 commit `d491ad9` (§6.2 stub). Task 3 follows (delete `spend.py`, sweep adapter call-sites).
- **v0.1.9** (2026-04-23) — Task #15 (Phase 4a T7): Added §1.6 documenting stored-vs-rerun `qa_passed` semantics. `qa_passed` is a point-in-time snapshot; re-running `scripts/qa_check.py` may produce different results when pool-aggregation Check 2 (free-list cross-run uniqueness) flips as the cohort grows. The divergence materialized in the shakedown corpus (Position C replay, 2026-04-22) but NOT in Phase 4a (T6 QA sweep: zero divergences, 101 records, 12-model diversity distributes the pool). Downstream consumers wanting the "final" QA status against the full corpus should re-run the check battery. No schema change. Cross-reference: `docs/status/2026-04-22-position-c-replay-verdict.md`, `docs/status/2026-04-23-phase4a-t6-qa-sweep.md`.
- **v0.1.8** (2026-04-23) — Task #28: `romney_small_n_warning` threshold updated from `n < 8` to `n < 15` per CDA SME reconciliation (`docs/status/2026-04-23-small-n-threshold-sme-amendment.md`). Grounded in `SME_REVIEW.md` §1.1 small-n rationale (Anders & Batchelder 2015; Romney-Weller-Batchelder 1986 calibration at n=20-40). Field value changes for n=8-14 (previously False, now True). Pipeline, schema docstring, tests, and this doc co-updated.
- **v0.1.7** (2026-04-23) — Task #26: `DeclineInterview` pydantic schema added to `cdb_core/schemas.py`. New JSONL file `data/raw/decline_interviews.jsonl`. New `decline_interviews` table in `lsb.sqlite`. See §10 and `docs/DECLINE_INTERVIEW_PROTOCOL.md`. CDA SME verdict: `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`.
- **v0.1.6** (2026-04-23) — Task #24: `failures.jsonl` entry shape expanded per the failures-as-findings directive. Added `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `partial_session`, and `retry_attempts` to `append_failure`. No change to `InformantRecord`, `GroundingRef`, or any other pydantic schema. See §9 and `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A + Amendment A.
- **v0.1.5** (2026-04-21) — F2-T02: `DomainResult` gains `romney_small_n_warning: bool` (default `False`). Set `True` when n_models < 8 at Romney CCM computation time — dual-threshold pass/fail is statistically underpowered below n=8 per SME 2026-04-20 verdict. Non-breaking addition. Companion wiring populates the previously-null `romney_eigenratio`, `romney_consensus_pass`, and `romney_consensus_warning` fields.
- **v0.1.4** (2026-04-20) — Un-defer of SME §1.3 G1 split. `DomainResult` gains six new fields: `g1_salience_stability`, `g1_spatial_stability`, `g1_aggregate_stability`, `g1_salience_pass`, `g1_spatial_pass`, `g1_overall_pass`. All optional (default `None`); populated by the sensitivity study once it runs. The binding gate criterion is `g1_overall_pass` (True iff both salience and spatial axes are below the 0.5 threshold). The individual axis fields are diagnostic. No breaking changes. See ARCHITECTURE.md §5.3 Phase 4b for the split semantics.
- **v0.1.3** (2026-04-20) — Post-F1 SME-review follow-up: `WithinModelResult` gains `deterministic_output: bool` marker (defaults `False`). Register 1 analysis is now wired into `run_pipeline` — `DomainResult.within_model_results` is populated on every run rather than left empty. Triggers the Register 2 visual convention in `DESIGN_SYSTEM.md` §3.3.5 (hollow triangle, no ellipse) when a model's N runs produce near-identical pile-sort structure. No breaking changes.
- **v0.1.2** (2026-04-19) — Post-F1 SME-review: `InformantRecord` gains capacity-constrained truncation fields (`truncation_type`, `truncation_n`, `max_possible_n`, `context_window_exceeded`, `capacity_note`). All fields are optional or defaulted; no breaking changes. `context_window_exceeded = True` is a finding, not a QA failure. See `docs/SME_REVIEW.md` §1.7.
- **v0.1.1** (2026-04-19) — Post-F1 SME-review schema additions to `DomainResult` and `GroundingRef`. New measure result types (`SutropCSI`, `NolanIndexPair`, `MantelPair`, `WithinModelResult`). New `ConsensusType` Literal (`STRONG_CONSENSUS`, `WEAK_CONSENSUS`, `SUBCULTURAL`, `TURBULENT`, `CONTESTED`, `DETERMINISTIC`). Dual Romney thresholds (operational 5.0, classic 3.0). Cultural centrality scores per model. `GroundingRef.human_oci` placeholder for per-subject grounding submissions. All new fields are optional or defaulted — no breaking changes to the v0.1 schema contract. See `docs/SME_REVIEW.md` for the methodological rationale and `ARCHITECTURE.md` §4.2.0 for the three analytical registers.
- **v0.1** — first draft. Documents the v0.7 schemas: `InformantRecord` and its three step records (`FreelistRecord`, `PileSortRecord`, `InterviewRecord`), the SHA256 manifest, the v0.7 multi-baseline `GroundingRef`, the `DomainResult.groundings: list[GroundingRef]` field, and the target SQLite schema generated by `scripts/build_db.py`. Includes the relationship between the JSONL canonical layer and the SQLite researcher-friendly layer.

---

## 0. Overview

The Latent Structure Benchmark (LSB) publishes its full result set as open data under CC0. The published bundle contains:

- **`informants.jsonl`** — the canonical raw data of LSB. One `InformantRecord` per line. Append-only. UTF-8.
- **`lsb.sqlite`** — a SQLite database generated from `informants.jsonl` by `scripts/build_db.py`. Same data, different shape — flat tables for easy querying.
- **`build_db.py`** — the build script itself, included so the bundle is self-rebuilding.
- **`DATA_DICTIONARY.md`** — this file.
- **Prompt templates** — the v1 prompt templates from `packages/cdb_collect/prompts/v1/`, included for full reproducibility without cloning the repo.

The bundle is hosted on Backblaze B2, mirrored to HuggingFace Datasets, and DOI-minted via Zenodo after the LSB Phase 4 validation gates pass. Pre-validation, the bundle exists on Backblaze B2 without a DOI; researchers using pre-validation data are explicitly told it is preliminary.

**License:** the bundle is dedicated to the public domain under CC0 1.0 Universal. You can do anything you want with it without attribution. Attribution is strongly encouraged via the Zenodo DOI for citation purposes, but not legally required.

**Reproducibility guarantee:** any researcher with the bundle and a Python ≥ 3.11 environment can run `python build_db.py informants.jsonl lsb.sqlite` and produce a SQLite database byte-identical (modulo timestamps) to the one LSB itself uses internally. Combined with the prompt templates and the published code (Apache 2.0 on GitHub), every figure on the LSB dashboard can be reproduced from open inputs without any LSB-specific tooling beyond standard Python.

---

## 1. The InformantRecord schema

`InformantRecord` is the canonical raw data atom of LSB. **One `InformantRecord` per `(model, domain, run_index)` tuple.** It captures everything an outside researcher would need to reproduce, audit, or challenge that run: who the informant was, under what conditions it was queried, the verbatim prompts and responses for all three CDA steps, the parsed outputs, the cryptographic provenance, and the QA verdict.

`informants.jsonl` is an append-only stream of `InformantRecord` objects, one per line. New runs append; existing records are never edited or deleted. The append-only property is what makes the longitudinal `DriftTracker` view (`ARCHITECTURE.md` §4.5) possible — historical runs from earlier model versions are retained forever and the temporal dimension is reconstructible from the file.

### 1.1 Top-level fields

#### Identity

| Field | Type | Required | Semantics |
|---|---|---|---|
| `informant_id` | `str` | Yes | SHA256[:16] of `(model_id, domain_slug, run_index, collection_date)`. Stable across machines; deterministic. Used as the primary key in `lsb.sqlite`. |
| `domain_slug` | `str` | Yes | The LSB domain this run was conducted on. v1 domains: `family`, `holidays`, `food`. |
| `run_index` | `int` | Yes | 0-indexed run number within the `(model, domain)` tuple. Default `N=5` runs per tuple, so `run_index` is `0..4`. |
| `collection_date` | `datetime` (ISO 8601, UTC) | Yes | The timestamp the run was *initiated*, not when it completed. Used as the temporal anchor for the longitudinal view. |

#### Model identity

| Field | Type | Required | Semantics |
|---|---|---|---|
| `model_id` | `str` | Yes | The exact API model string, provider-canonical. Examples: `claude-opus-4-6`, `gpt-4o-2025-01-15`, `deepseek-v3`. |
| `model_version_returned` | `str` | Yes | **The exact version string returned by the API in the response**, which may differ from `model_id` when providers silently roll snapshots under a moving alias. This is the unit of analysis for the temporal view (`DriftTracker.tsx`). NOT the same as `model_id`. If a query asks "how did model X drift over time," join on this field, not on `model_id`. |
| `family` | `str` | Yes | Model family — `claude`, `gpt`, `gemini`, `qwen`, `llama`, `mistral`, `deepseek`, `cohere`, etc. Used for cross-version aggregation. |
| `provider` | `Literal` | Yes | One of `anthropic`, `openai`, `google`, `xai`, `cohere`, `openrouter`, `huggingface`. |
| `provider_request_id` | `str` | Yes | The provider-issued request ID returned in the API response. Examples: Anthropic's `x-request-id` header, OpenAI's `id` field. **This is the independent audit path through the provider's own logs** — combined with `sha256_manifest`, it gives two independent ways to verify a run's authenticity. |
| `knowledge_cutoff` | `date \| None` | No | Provider-declared training cutoff date, when known. Many providers don't expose this in the API; expect `None` for those. |
| `open_weights` | `bool` | Yes | `True` if the model's weights are downloadable. License nuances (Llama commercial restrictions, Mistral mixed line) are handled separately and not captured in this Boolean. |
| `origin_country` | `Literal` | Yes | One of `us`, `eu`, `ca` (Canada — Cohere), `cn`, `other`. The production region of the model. New origin values require an architecture decision. |
| `alignment_method` | `str \| None` | No | Free text — `RLHF`, `Constitutional AI`, `DPO`, `unknown`, etc. Best-effort field; not all providers disclose. |

#### Collection conditions

| Field | Type | Required | Semantics |
|---|---|---|---|
| `collection_method` | `Literal` | Yes | One of `anthropic_api`, `openrouter`, `huggingface`, `google_ai`, `xai_api`, `openai_api`, `deepseek_api`, `mistral_api`. Which remote integration point served this run. Direct API methods (`*_api`) are preferred over OpenRouter where available — they provide better thinking trace capture and lower latency. The same logical model may appear under multiple methods if invoked through multiple gateways; those rows differ by `collection_method` and possibly by `model_id`. |
| `collection_mode` | `Literal` | No | One of `single_pass`, `two_pass`, `baseline_items`, `cross_model_consensus`. Default `single_pass`. Specifies the collection strategy: `single_pass` = each run generates and sorts its own free list items (end-to-end model behavior); `two_pass` = free lists are collected first, aggregated into a consensus item list via Smith's S, then pile sorts use that consensus list (standard CDA methodology per Borgatti); `baseline_items` = pile sort uses items from a human baseline (e.g., Romney 1996) for direct model-to-human comparison; `cross_model_consensus` = pile sort uses items from a cross-model consensus free list pooled across all models. |
| `api_endpoint` | `str` | Yes | Full URL of the endpoint actually called. Includes the path. |
| `api_version` | `str` | Yes | Provider API version header. Anthropic example: `2023-06-01`. |
| `temperature` | `float` | Yes | Sampling temperature used. LSB uses `0.7` for free listing and `0.3` for pile sorting per `ARCHITECTURE.md` §4.1.3. |
| `top_p` | `float \| None` | No | Top-p sampling parameter, when set. |
| `max_tokens` | `int` | Yes | The `max_tokens` parameter passed to the API. |
| `system_prompt` | `str` | Yes | **Verbatim** system prompt used for all three steps in this run. Stored in full because the system prompt is part of what the alignment pipeline applies and changing it changes the corpus lens. |

#### CDA step records

| Field | Type | Required | Semantics |
|---|---|---|---|
| `freelist` | `FreelistRecord` | Yes | The CDA Step 1 record. See §1.2. |
| `pile_sort` | `PileSortRecord` | Yes | The CDA Step 2 record. See §1.3. |
| `interview` | `InterviewRecord` | Yes | The CDA Step 3 record. See §1.4. |

#### Capacity-constrained truncation (post-F1 SME review)

LLMs do not fatigue the way human informants do. The natural end of a free list for a model is bounded by its context window rather than by cognitive exhaustion. These fields record which termination mode ended the free listing. `context_window_exceeded = true` is **not** a QA failure — it is a finding about the model's categorical-processing capacity and must be preserved in the record. See `docs/SME_REVIEW.md` §1.7.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `truncation_type` | `Literal \| None` | No (default `None`) | One of `elbow`, `capacity`, `prompt_ceiling`, `context_window_exceeded`. `elbow` means the data-driven elbow cut (the normal case). `capacity` means the model stopped on its own. `prompt_ceiling` means the prompt's "aim for ≥ 30" floor was the active cap — lift the ceiling to measure natural capacity. `context_window_exceeded` means the provider truncated at `max_tokens` / context limit. |
| `truncation_n` | `int \| None` | No (default `None`) | Items kept after truncation. |
| `max_possible_n` | `int \| None` | No (default `None`) | The longest list the model could return under the no-ceiling condition, if known. Populated by the optional no-ceiling experiment (`ARCHITECTURE.md` §5.3 / SME §3.1); null for records collected under the standard protocol. |
| `context_window_exceeded` | `bool` | No (default `False`) | True when at least one step was truncated by the provider's context window. See `capacity_note` for which step. |
| `capacity_note` | `str` | No (default `""`) | Free-text detail. Example: `"model returned 487 items before context limit at step 2"`. |

#### Provenance

| Field | Type | Required | Semantics |
|---|---|---|---|
| `sha256_manifest` | `dict[str, str]` | Yes | Maps manifest keys to hex SHA256 digests. See §1.5 for the exact key list. |

#### QA

| Field | Type | Required | Semantics |
|---|---|---|---|
| `qa_passed` | `bool` | Yes | Set by `scripts/qa_check.py` (the QA_Runner per `ARCHITECTURE.md` §4.1.6). `True` means all six deterministic QA checks passed. `False` means at least one failed; the failure is documented in `qa_notes` and a Slack alert was posted to `#lsb-alerts`. Records with `qa_passed=False` are retained for the audit trail; downstream analysis MAY filter them out, but the canonical JSONL keeps them. **A `context_window_exceeded = True` value does *not* set `qa_passed = False` on its own** — context-window truncation is a finding, not a QA failure. See §1.6 for stored-vs-rerun semantics. |
| `qa_notes` | `str` | No (default `""`) | Free text — failure reasons, threshold values, manual overrides. |

### 1.6 Stored-vs-rerun `qa_passed` semantics

**`qa_passed` is a point-in-time snapshot recorded at collection time.** It reflects the QA battery result as of the moment the record was written into `informants.jsonl`, against the pool of same-`(model, domain)` peers that existed at that moment. It is NOT a global truth about the record in isolation.

**Re-running `scripts/qa_check.py` on the corpus MAY produce different results** when pool-aggregation checks flip records as the cohort grows. Specifically, Check 2 (free-list cross-run uniqueness) computes the ratio of unique items to total items across all same-`(model, domain)` records in the file at the time of the run. A record written when its `(model, domain)` pool contained only 1–2 prior runs may pass Check 2 at collection time; re-running the check once the full N=5 pool is present may produce a different verdict (in either direction) if later runs pushed the uniqueness ratio above or below the 15% threshold.

**This divergence was observed in practice** during the 2026-04-22 shakedown corpus replay (Position C, `docs/status/2026-04-22-position-c-replay-verdict.md`): a single dominant model (`claude-sonnet-4-6`, 54 records) drove the cross-run uniqueness ratio to 8.6%, causing stored-True records to rerun-FAIL once the full pool was present. The mechanism is documented there.

**Phase 4a T6 QA sweep (2026-04-23) found zero divergences** in either direction on the 101-record Phase 4a corpus (`docs/status/2026-04-23-phase4a-t6-qa-sweep.md`). The explanation is that Phase 4a's per-cell N=5 structure distributes across 12 distinct models; no cell accumulates enough same-model-same-domain siblings for Check 2 to fire. The pool-aggregation mechanism that produced divergence in the shakedown did not materialize at Phase 4a's model-diversity level.

**For downstream consumers:** the stored `qa_passed` value is the authoritative collection-time record and is correct as a snapshot of QA state at write time. If your analysis requires the "final" QA verdict against the full corpus as it now stands — rather than the point-in-time verdict — re-run `scripts/qa_check.py --file informants.jsonl` and use its output. Do not assume the stored value and the re-run value are always identical; they may differ on corpora where one `(model, domain)` cell dominates by volume.

### 1.2 FreelistRecord (CDA Step 1)

The free listing step asks the model to enumerate every item it can think of in the target domain.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `prompt_verbatim` | `str` | Yes | The exact text sent to the model after template substitution. Stored verbatim — the same prompt across runs of the same `prompt_version` should be byte-identical. |
| `prompt_version` | `str` | Yes | Semantic version of the prompt template, e.g. `v1`, `v1.1`. Bumps when the template changes per `ARCHITECTURE.md` §5.2 rule 8. |
| `response_verbatim` | `str` | Yes | The exact text returned by the model. Stored verbatim — never normalized, never trimmed. |
| `thinking_verbatim` | `str` | No (default `""`) | The verbatim reasoning/thinking trace produced by the model, if the model supports extended thinking (e.g., Claude's thinking blocks, Grok's extended thinking, Gemini's thinking mode). Empty string for models that do not produce thinking traces. Stored verbatim — never normalized, never trimmed. This is part of the raw record and is analytically valuable: how a model reasons about categorization is data. |
| `response_object_json` | `dict` | Yes | The full provider response object, including all metadata fields the provider returned (token counts, stop reason, model version string, request IDs, etc.). Stored as a JSON object. |
| `input_tokens` | `int` | Yes | Provider-reported input token count. |
| `output_tokens` | `int` | Yes | Provider-reported output token count. |
| `thoughts_token_count` | `int` | No (default `0`) | Provider-reported reasoning/thoughts token count for this step, as reported by the provider. When `output_tokens == 0 AND thoughts_token_count > 0`, the model consumed reasoning tokens against the `max_tokens` budget without producing visible output — a sufficient diagnostic signature of cap-exhausted reasoning at the cohort level for distinguishing cap-exhausted reasoning from a substantively empty response, but not a deterministic per-record proof of cap exhaustion. A value of `0` is ambiguous: it can mean either (a) the provider does not surface reasoning tokens at all (Anthropic, HuggingFace at v0.1.11), or (b) the model did not engage internal reasoning on this call. The field cannot distinguish these two cases. Values are as reported by the provider and are NOT directly comparable across providers — Gemini's `thoughts_token_count` and OpenRouter's `completion_tokens_details.reasoning_tokens` may be measured under different conventions. Within-provider comparisons are valid; cross-provider comparisons require provider-internal context. |
| `latency_ms` | `int` | Yes | Wall-clock latency from request send to response received, in milliseconds. |
| `stop_reason` | `str` | Yes | Provider-reported stop reason. Examples: `end_turn`, `max_tokens`, `stop_sequence`. |
| `parsed_items` | `list[str]` | Yes | The parsed, normalized, deduplicated item list, truncated to `domain.truncation_k` (default 25). Lowercase, punctuation stripped, whitespace collapsed, deduped preserving first-occurrence order. |
| `parsed_raw_order` | `list[str]` | Yes | The full pre-truncation order, used for salience analysis (earlier items are more salient in the cognitive anthropology literature). |

### 1.3 PileSortRecord (CDA Step 2)

The pile sort step asks the model to group items into similarity-based piles. The items may come from the model's own free list (single-pass), a consensus free list aggregated across multiple free-list runs (two-pass), or a human baseline item set (baseline-items mode). The `item_source` field records which source was used.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `prompt_verbatim` | `str` | Yes | Same semantics as `FreelistRecord.prompt_verbatim`. |
| `prompt_version` | `str` | Yes | Same semantics. |
| `response_verbatim` | `str` | Yes | Same semantics. |
| `thinking_verbatim` | `str` | No | Same semantics as `FreelistRecord.thinking_verbatim`. |
| `response_object_json` | `dict` | Yes | Same semantics. |
| `input_tokens` | `int` | Yes | Same semantics. |
| `output_tokens` | `int` | Yes | Same semantics. |
| `thoughts_token_count` | `int` | No (default `0`) | Same semantics as `FreelistRecord.thoughts_token_count`. |
| `latency_ms` | `int` | Yes | Same semantics. |
| `stop_reason` | `str` | Yes | Same semantics. |
| `parsed_piles` | `list[list[str]]` | Yes | Each inner list is one pile. Item order within a pile is not significant. The union of all inner lists must equal the input item set (the model is required to put every item somewhere). |
| `parsed_matrix` | `list[list[int]]` | Yes | Binary symmetric item × item co-occurrence matrix derived from `parsed_piles`. `matrix[i][j] == 1` iff items `i` and `j` are in the same pile. Diagonal is `1`. Symmetric. |
| `item_source` | `str` | No | Default `own_freelist`. Records where the pile sort items came from. Values: `own_freelist` (single-pass: items from this run's free list), `consensus:{model_id}` (two-pass: items from the consensus free list of that model's free-list runs, ranked by Smith's S), `baseline:{baseline_id}` (items from a human baseline's `items.txt`, e.g., `baseline:romney_1996`). |

### 1.4 InterviewRecord (CDA Step 3)

The pile interview step asks the model to name each pile from Step 2. This is the step that distinguishes LSB from naive similarity benchmarks — the label reveals the *organizing principle* the model used.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `prompt_verbatim` | `str` | Yes | Same semantics as the prior records. |
| `prompt_version` | `str` | Yes | Same. |
| `response_verbatim` | `str` | Yes | Same. |
| `thinking_verbatim` | `str` | No | Same semantics as `FreelistRecord.thinking_verbatim`. |
| `response_object_json` | `dict` | Yes | Same. |
| `input_tokens` | `int` | Yes | Same. |
| `output_tokens` | `int` | Yes | Same. |
| `thoughts_token_count` | `int` | No (default `0`) | Same semantics as `FreelistRecord.thoughts_token_count`. |
| `latency_ms` | `int` | Yes | Same. |
| `stop_reason` | `str` | Yes | Same. |
| `parsed_pile_labels` | `list[str]` | Yes | One label per pile, in the same order as `PileSortRecord.parsed_piles`. The label is the model's free-text name for the pile. |

### 1.5 The SHA256 manifest

Every `InformantRecord` carries a `sha256_manifest` dict mapping eight required keys to hex SHA256 digests. The manifest is computed at write time and stored alongside the raw record. Any later challenge to the data ("did you really get that response from that model on that date?") is answered by recomputing the SHA256 from the verbatim fields and comparing to the stored manifest.

| Manifest key | What is hashed | Why it matters |
|---|---|---|
| `freelist_prompt` | UTF-8 bytes of `freelist.prompt_verbatim` | Verifies the prompt wasn't edited after the fact |
| `freelist_response` | UTF-8 bytes of `freelist.response_verbatim` | Verifies the response wasn't edited |
| `pilesort_prompt` | UTF-8 bytes of `pile_sort.prompt_verbatim` | Same as above for Step 2 |
| `pilesort_response` | UTF-8 bytes of `pile_sort.response_verbatim` | Same |
| `interview_prompt` | UTF-8 bytes of `interview.prompt_verbatim` | Same for Step 3 |
| `interview_response` | UTF-8 bytes of `interview.response_verbatim` | Same |
| `request_params` | JSON-canonicalized form of `{temperature, top_p, max_tokens, system_prompt, api_endpoint, api_version, model_id}` | Verifies the request configuration wasn't tampered with |
| `informant_record_total` | The full serialized `InformantRecord` minus the `sha256_manifest` field itself | Verifies the entire record as a unit |

The eight keys are mandatory and the order is fixed (alphabetical by key name when serialized, for canonical hashing). Researchers verifying provenance should compute all eight independently and check each against the stored manifest. A failure on any one key indicates tampering or corruption.

The `provider_request_id` is a *separate* audit path: it lets a researcher (or LSB itself, or a provider) verify the run against the provider's own logs without trusting LSB's stored data at all. The two paths together — provider-side log lookup and local SHA256 verification — give independent confirmation of authenticity.

---

## 2. The DomainResult schema (open bundle subset)

`DomainResult` is the analysis output that the dashboard reads. It is *not* the canonical raw data — `InformantRecord` is — but it is the form most readers will interact with via the dashboard. The open bundle includes `DomainResult` records as a convenience for researchers who want to use LSB's analysis outputs without re-running the analysis pipeline.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `domain_slug` | `str` | Yes | The LSB domain. |
| `analysis_version` | `str` | Yes | Semantic version of the analysis pipeline that produced this result. `0.1`, `0.2`, etc. |
| `models` | `list[ModelRef]` | Yes | The models included in this analysis. |
| `free_lists` | `dict[str, FreeList]` | Yes | Per-model consensus free lists, keyed by `model_id`. |
| `mds_coordinates` | `dict[str, tuple[float, float]]` | Yes | Per-model MDS coordinates in 2D cultural space. |
| `mds_uncertainty` | `dict[str, BootstrapEllipse]` | Yes | Per-model 95% bootstrap confidence ellipses. |
| `similarity_matrix` | `list[list[float]]` | Yes | Model × model similarity, ordered by `models`. |
| `similarity_ci` | `list[list[tuple[float, float]]]` | Yes | Per-cell 95% CI from the bootstrap. |
| `consensus_score` | `float` | Yes | Cultural consensus eigenvalue ratio (Romney/Weller/Batchelder). **Retained as an alias for `romney_eigenratio`** — new analyses write both; old analyses only populate this field. New code should prefer `romney_eigenratio`. |
| `consensus_ci` | `tuple[float, float]` | Yes | 95% CI on the consensus score. |
| `romney_eigenratio` | `float \| None` | No | The λ₁/λ₂ ratio of the inter-model agreement matrix (Romney et al. 1986). Same value as `consensus_score` when both are populated. Post-F1 field (SME_REVIEW.md §1.1). |
| `romney_threshold_classic` | `float` | No | The classic RWB threshold (3.0). Reported for cross-study comparability. |
| `romney_threshold_lsb` | `float` | No | The LSB operational threshold (5.0) — binding for pass/fail. Calibrated for small-n (≈12 models) per SME §1.1. |
| `romney_consensus_pass` | `bool \| None` | No | True when `romney_eigenratio >= romney_threshold_lsb`. |
| `romney_consensus_warning` | `bool \| None` | No | True when `romney_threshold_classic <= romney_eigenratio < romney_threshold_lsb` (warning zone: passes classic, fails operational). |
| `romney_small_n_warning` | `bool` | No (default `False`) | True when `n_models < 15` at the time of Romney CCM computation. Small-n dual-threshold evaluation (operational 5.0, classic 3.0) is statistically underpowered below n=15; the CCT literature's working small-n cutoff derives from Anders & Batchelder 2015 (grounding the Romney 5.0 threshold in the n=12 small-n regime) and Romney-Weller-Batchelder 1986 (calibrated at n=20-40). Flag is the honest representation, not an edge case. Always `False` for `n_models >= 15` (SME binding threshold, 2026-04-23 reconciliation verdict — supersedes the original 2026-04-20 n<8 threshold). Also `False` when Romney was not computed at all (single-model degenerate case, n < 2). Dashboard consumers must display a visible small-n caveat alongside `romney_consensus_pass` / `romney_consensus_warning` whenever this flag is True. |
| `consensus_type` | `ConsensusType \| None` | No | One of `STRONG_CONSENSUS`, `WEAK_CONSENSUS`, `SUBCULTURAL`, `TURBULENT`, `CONTESTED`, `DETERMINISTIC`. See `docs/SME_REVIEW.md` §1.6 and `ARCHITECTURE.md` §4.2 for the decision table. `DETERMINISTIC` is reserved for future deterministic architectures (neurosymbolic, zero-temperature). |
| `cultural_centrality_scores` | `dict[str, float]` | No (default `{}`) | Per-model centrality scores from the first eigenvector of the inter-model similarity matrix (Caulkins 1999). Positive = contributes to dominant structure, negative = systematically inverts it. Labeled *centrality*, not *competence* — see `ARCHITECTURE.md` §4.2. |
| `negative_centrality_flag` | `bool` | No (default `False`) | True when any model has a negative centrality score. Signals a SUBCULTURAL or CONTESTED typology and prompts QA review per `docs/SME_REVIEW.md` Q6 — not a failure, a finding. |
| `negative_centrality_models` | `list[str]` | No (default `[]`) | The model_ids with negative centrality. |
| `cross_model_mantel` | `list[MantelPair]` | No (default `[]`) | Pairwise classical Mantel test results (Mantel 1967) per `docs/SME_REVIEW.md` §1.2. Complements the full-matrix `g2_signal` gate; tests pairwise matrix correlation. Each entry has `model_a`, `model_b`, `r`, `p_value`, `n_permutations`. |
| `cross_model_nolan` | `list[NolanIndexPair]` | No (default `[]`) | Pairwise Nolan Index (Robbins 2023) per `docs/SME_REVIEW.md` §2.2. Tests proportional-frequency similarity — catches "same items, different weights" that Jaccard misses. Each entry has `model_a`, `model_b`, `ni`, `jaccard`, `ni_vs_jaccard_delta`. |
| `sutrop_csi` | `dict[str, list[SutropCSI]]` | No (default `{}`) | Per-model Sutrop composite salience index (Sutrop 2001). More robust to list-length variance than Smith's S. Keyed by `model_id`; each list is sorted descending by CSI. |
| `salience_index_agreement` | `dict[str, float]` | No (default `{}`) | Per-model Spearman ρ between Smith's S and Sutrop CSI rankings. Values below 0.85 are a warning — list-length variance is affecting the salience order. |
| `within_model_results` | `list[WithinModelResult]` | No (default `[]`) | Register 1 results per model. One entry per model in `models`. Populated by the two-level pipeline (Phase 4b). Carries OCI and Register 1 stability diagnostics. See `WithinModelResult` schema below. |
| `g1_salience_stability` | `float \| None` | No | Within/between variance ratio on Smith's S rank ordering across prompt variants (SME §1.3 split G1, un-deferred 2026-04-20). Lower = more stable. Populated after a sensitivity study runs; null otherwise. See `ARCHITECTURE.md` §5.3 Phase 4b. |
| `g1_spatial_stability` | `float \| None` | No | Within/between variance ratio on pile-sort co-occurrence structure across prompt variants. Lower = more stable. Can diverge from salience stability — reporting both axes separately is more diagnostic than a single aggregate. |
| `g1_aggregate_stability` | `float \| None` | No | Mean of the two axis ratios above. Legacy single-axis composite retained for cross-study comparability. **Not the binding metric** — use `g1_overall_pass` instead. |
| `g1_salience_pass` | `bool \| None` | No | True iff `g1_salience_stability < 0.5`. Diagnostic. |
| `g1_spatial_pass` | `bool \| None` | No | True iff `g1_spatial_stability < 0.5`. Diagnostic. |
| `g1_overall_pass` | `bool \| None` | No | **Binding G1 gate criterion.** True iff both `g1_salience_pass` AND `g1_spatial_pass`. A model-domain pair that fails on only one axis is a more informative finding than a global failure — see ARCHITECTURE.md §5.3 for the split's rationale. |
| **`groundings`** | **`list[GroundingRef]`** | **Yes** | **Zero or more human baselines for this domain. Empty list = ungrounded domain (a normal first-class state).** See §3 for the `GroundingRef` schema. |
| **`selected_baseline_id`** | **`str \| None`** | **Yes (may be `None`)** | **Which baseline the dashboard displays by default.** `None` when `groundings` is empty. The user can toggle to any baseline in the list via the dashboard UI. |
| `generated_lede` | `str` | Yes | The pre-written one-sentence lede for this domain at this analysis version. Generated by the lede generator (`ARCHITECTURE.md` §4.2.3). |
| `generated_at` | `datetime` (ISO 8601, UTC) | Yes | When this `DomainResult` was generated. |

**Important:** `groundings` is a list, not a singleton. The v0.6 schema had `grounding: GroundingRef | None`; the v0.7 schema has `groundings: list[GroundingRef] = []`. If you have code reading the v0.6 schema, you need to update it to handle the list. The v0.7 schema is the only supported form going forward.

### 2.1 `WithinModelResult` (Register 1 — added post-F1 SME review)

One entry per model in `within_model_results`. Captures the model's **Output Concentration Index (OCI)** — a concentration statistic on the within-model output distribution — and Register 1 stability diagnostics. See `ARCHITECTURE.md` §4.2.0 for the three-register framework and `docs/BOOTSTRAP_DESIGN.md` §2 for the Level 1 underestimation caveat that accompanies every R1 CI.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `model_id` | `str` | Yes | The model this R1 block describes. |
| `n_runs` | `int` | Yes | Number of runs contributing to the within-model analysis. |
| `oci` | `float` | Yes | Output Concentration Index — λ₁/λ₂ of the within-model agreement matrix. **Not a cultural consensus ratio.** The N rows are iid samples from one stochastic process; OCI is a concentration statistic. |
| `oci_ci` | `tuple[float, float] \| None` | No | 95% bootstrap CI on OCI. **Systematically underestimates uncertainty** — same-model same-temperature runs have effective N smaller than nominal N. See `docs/BOOTSTRAP_DESIGN.md`. |
| `underestimates_uncertainty` | `bool` | No (default `True`) | Always True for Register 1 CIs. Any display must carry this caveat. |
| `deterministic_output` | `bool` | No (default `False`) | True when the model's run × run agreement matrix has effectively zero second eigenvalue — the model produced near-identical pile-sort structure on every run. Triggers `ConsensusType = DETERMINISTIC` classification and the distinct Register 2 visual marker in `DESIGN_SYSTEM.md` §3.3.5 (hollow square, no ellipse). **The mismatch is the finding** — this flags zero-variance output as a property of the architecture, not a high-confidence signal. Does not trigger on any current transformer model at T > 0. |
| `salience_stability_rho` | `float \| None` | No | Spearman ρ of Smith's S salience ordering across runs. |
| `elbow_stability` | `bool \| None` | No | Whether the elbow position is stable across N sweeps. |
| `mds_procrustes_rmse` | `float \| None` | No | Within-model MDS Procrustes RMSE across runs. |
| `centrality_scores_by_run` | `dict[str, float]` | No (default `{}`) | Per-run centrality loadings; used to pick the centroid run for the dashboard's Option B display. |
| `centroid_run_id` | `str \| None` | No | `informant_id` of the run with the highest centrality score. The dashboard model-profile page renders this run's free list as the concrete Option B representation. |
| `mds_within_model` | `list[list[float]]` | No (default `[]`) | Per-item (n_items × 2) coordinates in the within-model MDS — Register 1's "this model's map of the domain." |

### 2.2 Measure result types (added post-F1 SME review)

Reference shapes for the measure entries embedded in `DomainResult`:

- **`SutropCSI`** — `{item: str, csi: float, f_mentions: int, n_runs: int, mean_position: float}`. Sutrop 2001 salience index.
- **`NolanIndexPair`** — `{model_a: str, model_b: str, ni: float, jaccard: float, ni_vs_jaccard_delta: float}`. Robbins 2023.
- **`MantelPair`** — `{model_a: str, model_b: str, r: float, p_value: float, n_permutations: int}`. Mantel 1967.

---

## 3. The GroundingRef schema (v0.7)

`GroundingRef` represents one human CDA baseline treated as a virtual informant in the MDS plot. **A domain can have zero, one, or many `GroundingRef` instances.** Each instance represents one human population studied with the CDA protocol.

The distinction between published baselines (extracted from peer-reviewed academic literature by LSB staff) and researcher-submitted baselines (contributed via the GitHub PR workflow per `ARCHITECTURE.md` §4.2.5) is encoded in `baseline_kind` and drives the visual treatment in `DESIGN_SYSTEM.md` §3.3 — published baselines render as black stars (★), researcher baselines as gray diamonds (◆).

### 3.1 Identity

| Field | Type | Required | Semantics |
|---|---|---|---|
| `baseline_id` | `str` | Yes | Stable slug, e.g. `romney_1996` or `tanaka_2026_kyoto_kinship`. Used in URLs, filenames, and `DomainResult.selected_baseline_id`. ASCII, lowercase, underscores. Unique within a domain. |
| `baseline_kind` | `Literal["published","researcher"]` | Yes | `published` for baselines extracted by LSB from the academic literature; `researcher` for baselines contributed via the GitHub PR workflow. Drives visual treatment. |
| `domain_slug` | `str` | Yes | Which LSB domain this baseline belongs to. |

### 3.2 Source

| Field | Type | Required | Semantics |
|---|---|---|---|
| `source_citation` | `str` | Yes | Full bibliographic citation (for published baselines) or full researcher attribution string (for researcher submissions). |
| `source_url` | `str \| None` | No | DOI, PMC link, or researcher project URL. |
| `collected_year` | `int` | Yes | The year the human data was *collected*, NOT the year of publication. For Romney et al. (1996) the collected year is 1990, even though publication is 1996. |

### 3.3 Population

| Field | Type | Required | Semantics |
|---|---|---|---|
| `n_human_informants` | `int` | Yes | Number of human subjects in the original study. |
| `population_description` | `str` | Yes | Free text describing who, when, how many, where. Example: `"US college students, ages 18–22, n=122, recruited 1990–1991, University of California, Irvine"`. Surfaces in the dashboard's grounding detail panel. |

### 3.4 Method

| Field | Type | Required | Semantics |
|---|---|---|---|
| `method` | `str` | Yes | Free text describing the CDA protocol used. Examples: `"pairwise similarity judgments"`, `"pile sort (Romney protocol)"`, `"free list + pile sort"`. |
| `irb_status` | `Literal["approved","exempt","not_applicable","unknown"]` | Yes (default `"unknown"`) | `approved` for contemporary research with explicit IRB review; `exempt` for IRB-determined exempt studies; `not_applicable` for historical published data whose ethics framework predates IRB review; `unknown` only as a temporary state during PR review (any merged baseline should have a definite value). |

### 3.5 Submitter (researcher baselines only)

These fields are `None` for `baseline_kind="published"` and required for `baseline_kind="researcher"`.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `submitter_name` | `str \| None` | Yes for researcher | Submitting researcher's full name. `None` for published baselines. |
| `submitter_institution` | `str \| None` | Yes for researcher | Affiliation. |
| `submitter_contact` | `str \| None` | Yes for researcher | Email or ORCID. Appears on the dashboard's grounding detail panel. |
| `submission_date` | `date \| None` | Yes for researcher | The date the PR was merged into LSB. Set by Mark at merge time, not by the researcher. |

### 3.6 Position in cultural space

These fields are populated by the LSB analysis pipeline at merge time. **Researchers submitting via the PR workflow leave these as placeholders** (`[0.0, 0.0]`, `null`, `0.0`, `""`) — the pipeline overwrites them.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `mds_coordinate` | `tuple[float, float]` | Yes | The baseline's position in the cross-model MDS space. |
| `mds_uncertainty` | `BootstrapEllipse \| None` | No | Set only when raw subject-level data (`pile_sort_raw.csv` in the submission) is available. Most published baselines provide only the aggregate matrix and so have `None` here; researcher submissions that include per-subject pile assignments do get a bootstrap ellipse. |
| `distance_to_nearest_model` | `float` | Yes | Mantel-style similarity to the closest model in the slate. |
| `nearest_model_id` | `str` | Yes | The `model_id` of the nearest model. |

### 3.7 Item-set alignment

| Field | Type | Required | Semantics |
|---|---|---|---|
| `item_intersection_size` | `int` | Yes | Number of items shared between this human baseline's item set and the LSB v1 item set for the domain. |
| `item_intersection_total` | `int` | Yes | Size of the LSB v1 item set for the domain. The ratio `item_intersection_size / item_intersection_total` is the coverage ratio displayed in the dashboard's grounding detail panel. A small intersection means a weaker comparison and the UI flags it. |

### 3.8 Register 1 cross-species extension (post-F1 SME review)

Populated only when the baseline ships with per-subject raw pile-sort data (`pile_sort_raw.csv`). Allows the human subject pool to be analyzed at Register 1 alongside models, producing a human Output Concentration Index directly comparable to model OCI. The majority of published baselines ship only the aggregate co-occurrence matrix and so leave these fields null. See `ARCHITECTURE.md` §4.2.5.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `human_oci` | `float \| None` | No | Output Concentration Index computed on the raw per-subject pile-sort data. Comparable to model OCI in `DomainResult.within_model_results`. Enables the claim "this model's OCI is within the range observed across human subject pools." |
| `human_oci_ci` | `tuple[float, float] \| None` | No | 95% bootstrap CI on `human_oci`. Resamples subjects with replacement. **Caveat:** a purposive or convenience sample from one community carries the opposite underestimation direction — the CI does not reflect cross-population variance. |
| `n_subjects_with_raw_data` | `int \| None` | No | Number of human subjects whose raw pile-sort data contributed to `human_oci`. May be less than `n_human_informants` if only a subset provided consent for raw-data release. |

---

## 4. The SQLite schema

`scripts/build_db.py` reads `informants.jsonl` and writes a SQLite database with the following tables. The database is regeneratable from the JSONL at any time; the JSONL is the source of truth and the SQLite is a query convenience.

**Tables:**

### `informants`

One row per `InformantRecord`. Top-level fields are denormalized into columns; the three step records are stored in joined tables (`freelist_items`, `pilesort_cells`, `interview_labels`).

```sql
CREATE TABLE informants (
  informant_id TEXT PRIMARY KEY,
  domain_slug TEXT NOT NULL,
  run_index INTEGER NOT NULL,
  collection_date TEXT NOT NULL,            -- ISO 8601 UTC

  model_id TEXT NOT NULL,
  model_version_returned TEXT NOT NULL,
  family TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_request_id TEXT NOT NULL,
  knowledge_cutoff TEXT,                    -- ISO 8601 date or NULL
  open_weights INTEGER NOT NULL,            -- 0 or 1
  origin_country TEXT NOT NULL,
  alignment_method TEXT,

  collection_method TEXT NOT NULL,
  api_endpoint TEXT NOT NULL,
  api_version TEXT NOT NULL,
  temperature REAL NOT NULL,
  top_p REAL,
  max_tokens INTEGER NOT NULL,
  system_prompt TEXT NOT NULL,

  freelist_prompt_verbatim TEXT NOT NULL,
  freelist_response_verbatim TEXT NOT NULL,
  freelist_input_tokens INTEGER NOT NULL,
  freelist_output_tokens INTEGER NOT NULL,
  freelist_thoughts_token_count INTEGER NOT NULL DEFAULT 0,  -- v0.1.11; 0 for legacy records
  freelist_latency_ms INTEGER NOT NULL,
  freelist_stop_reason TEXT NOT NULL,

  pilesort_prompt_verbatim TEXT NOT NULL,
  pilesort_response_verbatim TEXT NOT NULL,
  pilesort_input_tokens INTEGER NOT NULL,
  pilesort_output_tokens INTEGER NOT NULL,
  pilesort_thoughts_token_count INTEGER NOT NULL DEFAULT 0,  -- v0.1.11; 0 for legacy records
  pilesort_latency_ms INTEGER NOT NULL,
  pilesort_stop_reason TEXT NOT NULL,

  interview_prompt_verbatim TEXT NOT NULL,
  interview_response_verbatim TEXT NOT NULL,
  interview_input_tokens INTEGER NOT NULL,
  interview_output_tokens INTEGER NOT NULL,
  interview_thoughts_token_count INTEGER NOT NULL DEFAULT 0, -- v0.1.11; 0 for legacy records
  interview_latency_ms INTEGER NOT NULL,
  interview_stop_reason TEXT NOT NULL,

  sha256_manifest_json TEXT NOT NULL,       -- the full dict serialized as JSON

  qa_passed INTEGER NOT NULL,               -- 0 or 1
  qa_notes TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_informants_domain ON informants(domain_slug);
CREATE INDEX idx_informants_model ON informants(model_id);
CREATE INDEX idx_informants_model_version ON informants(model_version_returned);
CREATE INDEX idx_informants_collection_date ON informants(collection_date);
CREATE INDEX idx_informants_provider ON informants(provider);
CREATE INDEX idx_informants_qa_passed ON informants(qa_passed);
```

### `freelist_items`

Long-format normalization of `FreelistRecord.parsed_items`. One row per item per informant, with rank preserved.

```sql
CREATE TABLE freelist_items (
  informant_id TEXT NOT NULL,
  rank INTEGER NOT NULL,                    -- 0-indexed; rank 0 is most salient
  item TEXT NOT NULL,
  is_truncated_in INTEGER NOT NULL,         -- 1 if item is in parsed_items (post-truncation), 0 if only in parsed_raw_order
  PRIMARY KEY (informant_id, rank),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_freelist_items_informant ON freelist_items(informant_id);
CREATE INDEX idx_freelist_items_item ON freelist_items(item);
```

### `pilesort_cells`

Long-format normalization of `PileSortRecord.parsed_matrix`. One row per non-zero cell. Diagonal cells (i == j) are stored. Symmetric — both `(i, j)` and `(j, i)` are stored to make queries simpler.

```sql
CREATE TABLE pilesort_cells (
  informant_id TEXT NOT NULL,
  item_a TEXT NOT NULL,
  item_b TEXT NOT NULL,
  in_same_pile INTEGER NOT NULL,            -- 1 if items a and b are in the same pile, else 0
  PRIMARY KEY (informant_id, item_a, item_b),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_pilesort_cells_informant ON pilesort_cells(informant_id);
CREATE INDEX idx_pilesort_cells_item_a ON pilesort_cells(item_a);
```

### `interview_labels`

One row per pile per informant. Pile order matches `PileSortRecord.parsed_piles`.

```sql
CREATE TABLE interview_labels (
  informant_id TEXT NOT NULL,
  pile_index INTEGER NOT NULL,              -- 0-indexed pile number
  label TEXT NOT NULL,
  PRIMARY KEY (informant_id, pile_index),
  FOREIGN KEY (informant_id) REFERENCES informants(informant_id)
);

CREATE INDEX idx_interview_labels_informant ON interview_labels(informant_id);
```

### `groundings` (when present)

If the bundle includes `DomainResult` records, the human grounding baselines are denormalized into a `groundings` table. One row per baseline per domain.

```sql
CREATE TABLE groundings (
  baseline_id TEXT NOT NULL,
  domain_slug TEXT NOT NULL,
  baseline_kind TEXT NOT NULL,              -- 'published' or 'researcher'
  source_citation TEXT NOT NULL,
  source_url TEXT,
  collected_year INTEGER NOT NULL,
  n_human_informants INTEGER NOT NULL,
  population_description TEXT NOT NULL,
  method TEXT NOT NULL,
  irb_status TEXT NOT NULL,
  submitter_name TEXT,
  submitter_institution TEXT,
  submitter_contact TEXT,
  submission_date TEXT,                     -- ISO 8601 date or NULL
  mds_x REAL NOT NULL,
  mds_y REAL NOT NULL,
  distance_to_nearest_model REAL NOT NULL,
  nearest_model_id TEXT NOT NULL,
  item_intersection_size INTEGER NOT NULL,
  item_intersection_total INTEGER NOT NULL,
  PRIMARY KEY (domain_slug, baseline_id)
);

CREATE INDEX idx_groundings_domain ON groundings(domain_slug);
CREATE INDEX idx_groundings_kind ON groundings(baseline_kind);
```

---

## 5. Example queries

```sql
-- All Claude Opus runs on family terms, ordered by collection date
SELECT informant_id, model_version_returned, collection_date, qa_passed
FROM informants
WHERE family = 'claude' AND domain_slug = 'family'
ORDER BY collection_date;

-- Free list items most frequently produced by US-origin models on holidays
SELECT fi.item, COUNT(*) as occurrences
FROM freelist_items fi
JOIN informants i ON fi.informant_id = i.informant_id
WHERE i.origin_country = 'us'
  AND i.domain_slug = 'holidays'
  AND i.qa_passed = 1
  AND fi.is_truncated_in = 1
GROUP BY fi.item
ORDER BY occurrences DESC
LIMIT 25;

-- All human baselines (published and researcher) for the family domain
SELECT baseline_id, baseline_kind, source_citation, n_human_informants, collected_year
FROM groundings
WHERE domain_slug = 'family'
ORDER BY baseline_kind, collected_year;

-- Find QA failures by model and the failure reasons
SELECT model_id, model_version_returned, COUNT(*) as failure_count, qa_notes
FROM informants
WHERE qa_passed = 0
GROUP BY model_id, model_version_returned, qa_notes
ORDER BY failure_count DESC;

-- Items where Claude Opus and DeepSeek-V3 disagree on co-occurrence
-- (one model puts them in the same pile, the other doesn't)
SELECT pc1.item_a, pc1.item_b
FROM pilesort_cells pc1
JOIN informants i1 ON pc1.informant_id = i1.informant_id
JOIN pilesort_cells pc2 ON pc1.item_a = pc2.item_a AND pc1.item_b = pc2.item_b
JOIN informants i2 ON pc2.informant_id = i2.informant_id
WHERE i1.model_id = 'claude-opus-4-6'
  AND i2.model_id = 'deepseek-v3'
  AND i1.domain_slug = 'family'
  AND i2.domain_slug = 'family'
  AND i1.run_index = 0 AND i2.run_index = 0
  AND pc1.in_same_pile != pc2.in_same_pile;
```

---

## 6. How to reproduce the SQLite database

```bash
# Download the open data bundle from Backblaze B2 (URL in the bundle's README)
curl -O https://[backblaze-b2-bucket-url]/lsb_open_bundle_v1.tar.gz
tar -xzf lsb_open_bundle_v1.tar.gz
cd lsb_open_bundle_v1/

# Verify you have all the files
ls -la
# Should show: informants.jsonl, lsb.sqlite, build_db.py, DATA_DICTIONARY.md, prompts/

# Rebuild the SQLite database from the canonical JSONL
python build_db.py informants.jsonl lsb_rebuilt.sqlite

# Verify byte-equivalence (modulo build timestamps)
sqlite3 lsb.sqlite "SELECT COUNT(*) FROM informants;"
sqlite3 lsb_rebuilt.sqlite "SELECT COUNT(*) FROM informants;"
# Both numbers should match. The two SQLite files should be functionally identical.
```

The `build_db.py` script is intentionally minimal — pure stdlib + `sqlite3` + `pydantic`. No external dependencies beyond what ships with Python 3.11+. If your reproduction fails, check that you're using Python 3.11 or later and that you haven't modified `informants.jsonl`.

---

## 7. Versioning and stability

**LSB data dictionary versioning is semantic.**

- **Patch (v0.1.X):** documentation clarifications, typos, added examples. No schema change.
- **Minor (v0.X.0):** new optional fields added to a schema. Old consumers continue to work; new consumers gain access to the new fields. Non-breaking.
- **Major (vX.0.0):** removing a field, renaming a field, changing a field's type, changing a `Literal` enum's allowed values. Breaking change. Requires a migration note in the changelog and a major version bump on the open data bundle.

**Co-update rule.** Per `ARCHITECTURE.md` §5.1 Reviewer rule 5, any change to `cdb_core/schemas.py` that touches `InformantRecord`, `GroundingRef`, `DomainResult`, or any of the three step records must include a matching update to this file in the same PR. The Reviewer agent rejects PRs that violate this rule.

**Stability promises.**

- The eight `sha256_manifest` keys are stable. Adding new keys is allowed (and will be additive — old verifiers ignore unknown keys); renaming or removing a key is a breaking change.
- The four `irb_status` values are stable. Adding a new value requires an architecture decision.
- The seven `provider` values are stable. Adding a new value requires an architecture decision.
- The five `origin_country` values are stable. Adding a new value requires an architecture decision.
- The eight `collection_method` values are stable. Adding a new value requires an architecture decision (this would correspond to LSB integrating a new API surface). Direct API methods (`openai_api`, `xai_api`, `deepseek_api`, `mistral_api`) are preferred over `openrouter` for providers that support them.
- The two `baseline_kind` values (`published`, `researcher`) are stable. Future work may add a third (e.g., `synthetic` for synthetically generated CDA data, if such a thing becomes useful), but that requires an architecture decision.

**What happens if you're using an older version of the bundle.** Each Zenodo DOI corresponds to one data dictionary version. If you're using a v0.1 bundle and the current data dictionary is v0.3, the v0.1 dictionary is the authoritative spec for *your* bundle — pull the matching version from the Zenodo entry rather than reading the latest version of this file. The latest version of this file describes the latest schema; older bundles use older schemas. Both are valid.

---

## 8. Where to ask questions

- **Bug in the data:** open an issue on the LSB GitHub repo with the title `Data bug: {informant_id}` and a description of the discrepancy. Include the SHA256 manifest verification result if you've run it.
- **Schema clarification:** open a Discussion on the LSB GitHub repo. Mark and the CDA SME agent monitor.
- **Reproducibility failure:** open an issue with the title `Reproducibility: {build_db.py error}` and the full error output. LSB takes reproducibility failures very seriously — they violate the project's headline guarantee.
- **Citation help:** see the citation section of the LSB `README.md` and the methodology page on `cogstructurelab.com`.

---

## 9. The failures.jsonl file

**Changelog:**
- **v0.1.6** (2026-04-23) — Task #24: `failures.jsonl` entry shape expanded per the failures-as-findings directive and Architect Amendment A. Added `prompt_verbatim`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `partial_session`, and `retry_attempts`. See `docs/status/2026-04-23-failures-as-findings-architect-verdict.md` §Stream A + Amendment A and `docs/status/2026-04-23-verbatim-capture-audit.md` §5.

### 9.1 Purpose and provenance

`data/raw/failures.jsonl` captures every session the collection pipeline attempted but could not complete into an `InformantRecord`. It is **append-only**: existing lines are never edited or deleted. A bad entry stays in place with whatever fields were captured at failure time — the audit trail is inviolable.

The file is **gitignored** (production data, not source-controlled). It is part of the open data bundle alongside `informants.jsonl`.

**The invariant:** every session the API handled is traceable to either `informants.jsonl` (all three CDA steps completed, regardless of QA outcome) or `failures.jsonl` (at least one step did not complete). There is no third path.

One entry per failed session. A session that is retried at the runner level (e.g., `run_pile_sort` retrying up to three times on parse failure) produces one entry — the per-retry bytes are captured in `retry_attempts`.

### 9.2 Top-level fields

| Field | Type | Always present | Semantics |
|---|---|---|---|
| `timestamp` | `str` (ISO 8601) | Yes | Wall-clock time the failure was appended. Not the time the session started. |
| `error_type` | `str` | Yes | Python exception class name. Examples: `"ValueError"`, `"RuntimeError"`, `"httpx.HTTPStatusError"`. |
| `error_message` | `str` | Yes | `str(error)` — the exception message. May include partial context (e.g., pile-sort parse failures include the truncated response text in the message). |
| `context` | `dict` | Yes | At minimum `{model_id: str, domain: str, run_index: int}`. May include additional fields from the caller. |
| `prompt_verbatim` | `str \| None` | No | The exact prompt sent to the step that failed (or the prompt sent on the final retry for pile-sort parse-retry exhaustion). Absent when no prompt was constructed before the exception (e.g., a pre-request setup error). |
| `response_verbatim` | `str \| None` | No | The exact response text returned by the provider on the failing step (or final retry). May be an empty string `""` for HTTP 200 empty-body failures (Gemini/GLM class). Absent when the request never completed (e.g., HTTP 4xx raised before a response was received). |
| `thinking_verbatim` | `str \| None` | No | The reasoning trace from the failing step, if the adapter surfaced one. Empty string `""` for models that do not produce thinking traces. Absent when no response was received. |
| `stop_reason` | `str \| None` | No | The provider stop reason on the failing step (e.g., `"STOP"`, `"MAX_TOKENS"`, `"end_turn"`, `"unknown"`). Absent when no response was received. |
| `thoughts_token_count` | `int \| None` | No | Provider-reported reasoning/thoughts token count for the failing step (or final retry), as reported by the provider. When `output_tokens == 0 AND thoughts_token_count > 0`, the model consumed reasoning tokens against the `max_tokens` budget without producing visible output — a sufficient diagnostic signature of cap-exhausted reasoning at the cohort level, but not a deterministic per-record proof of cap exhaustion. A value of `0` is ambiguous: it can mean either (a) the provider does not surface reasoning tokens at all (Anthropic, HuggingFace at v0.1.11), or (b) the model did not engage internal reasoning on this call. Absent when the request never completed (e.g., HTTP error before any response was received). Values are as reported by the provider and are NOT directly comparable across providers — Gemini's `thoughts_token_count` and OpenRouter's `completion_tokens_details.reasoning_tokens` may be measured under different conventions. Within-provider comparisons are valid; cross-provider comparisons require provider-internal context. |
| `partial_session` | `dict \| None` | No | Step records for any CDA steps that completed **before** the failure. Shape described in §9.3. **Omitted entirely** (not written as `null`) when nothing completed before the failure — keeps entries compact for the common Class 5 / 6 cases where the failure is at step 1. |
| `retry_attempts` | `list[dict]` | Yes (min `[]`) | Per-retry dicts for pile-sort parse-retry exhaustion. Empty list `[]` for all failure modes that do not involve a parse-retry loop (all non-pile-sort failures, all HTTP-layer failures). Shape described in §9.4. **Always written**, even when empty, to make entries machine-parseable without a presence check. |

**Field order** in the JSONL line (for human readability of `tail -f` output):
`timestamp` → `error_type` → `error_message` → `context` → `prompt_verbatim` (if present) → `response_verbatim` (if present) → `thinking_verbatim` (if present) → `stop_reason` (if present) → `thoughts_token_count` (if non-None) → `partial_session` (if present) → `retry_attempts` (always).

### 9.3 partial_session shape

`partial_session` is a JSON object with up to three optional keys, one per CDA step:

```json
{
  "freelist": { ... },
  "pile_sort": { ... },
  "interview": { ... }
}
```

Only the keys for steps that **completed** before the failure are present. A step that did not start is simply absent (not `null`). Example: if the failure occurred at step 2, only `"freelist"` is present.

Each step sub-object carries the full step-record shape matching the corresponding schema type in `cdb_core/schemas.py`:

**`freelist` sub-object** — mirrors `FreelistRecord`:

| Key | Type | Semantics |
|---|---|---|
| `prompt_verbatim` | `str` | Exact prompt sent to the free-listing step. |
| `response_verbatim` | `str` | Exact response from the free-listing step. |
| `thinking_verbatim` | `str` | Thinking trace (empty string if not surfaced). |
| `stop_reason` | `str` | Provider stop reason. |
| `parsed_items` | `list[str]` | Parsed, normalized item list (may be empty if parsing was partial). |
| `input_tokens` | `int` | Provider-reported input token count. |
| `output_tokens` | `int` | Provider-reported output token count. |
| `thoughts_token_count` | `int` | Provider-reported reasoning/thoughts token count. `0` for providers that do not surface reasoning tokens or when no reasoning occurred. Same semantics and non-comparability caveats as `FreelistRecord.thoughts_token_count` in §1.2. |
| `latency_ms` | `int` | Wall-clock latency in ms. |

**`pile_sort` sub-object** — mirrors `PileSortRecord` (carried when step 2 completed before failure at step 3):

| Key | Type | Semantics |
|---|---|---|
| `prompt_verbatim` | `str` | Exact prompt sent to the pile-sort step. |
| `response_verbatim` | `str` | Exact response from the pile-sort step. |
| `thinking_verbatim` | `str` | Thinking trace (empty string if not surfaced). |
| `stop_reason` | `str` | Provider stop reason. |
| `input_tokens` | `int` | Provider-reported input token count. |
| `output_tokens` | `int` | Provider-reported output token count. |
| `thoughts_token_count` | `int` | Provider-reported reasoning/thoughts token count. `0` for providers that do not surface reasoning tokens or when no reasoning occurred. Same semantics and non-comparability caveats as `FreelistRecord.thoughts_token_count` in §1.2. |
| `latency_ms` | `int` | Wall-clock latency in ms. |

**`interview` sub-object** — mirrors `InterviewRecord` (carried when step 3 completed but a post-assembly step raised):

| Key | Type | Semantics |
|---|---|---|
| `prompt_verbatim` | `str` | Exact prompt sent to the interview step. |
| `response_verbatim` | `str` | Exact response from the interview step. |
| `thinking_verbatim` | `str` | Thinking trace (empty string if not surfaced). |
| `stop_reason` | `str` | Provider stop reason. |
| `input_tokens` | `int` | Provider-reported input token count. |
| `output_tokens` | `int` | Provider-reported output token count. |
| `latency_ms` | `int` | Wall-clock latency in ms. |

### 9.4 retry_attempts shape

`retry_attempts` is present in every entry. It is non-empty **only** for pile-sort parse-retry exhaustion failures — where `run_pile_sort` retried the adapter call up to `_MAX_PARSE_RETRIES=3` times and all attempts failed to produce parseable JSON. It is `[]` for all other failure modes.

The list is ordered: index 0 is the first attempt, index 1 is the second, etc. The final attempt's bytes are also captured at the top level in `response_verbatim`, `thinking_verbatim`, and `stop_reason` — the per-attempt list carries the diagnostic forensics; the top-level fields carry the "what did the model finally say" bytes at a glance.

Each entry in the list:

| Key | Type | Semantics |
|---|---|---|
| `attempt_index` | `int` | 0-indexed attempt number. `0` = first attempt, `1` = second, etc. |
| `response_verbatim` | `str` | Exact response text from this attempt. May be `""` for empty-body HTTP 200 responses. |
| `thinking_verbatim` | `str` | Thinking trace from this attempt (empty string if not surfaced). |
| `stop_reason` | `str` | Provider stop reason for this attempt. |
| `input_tokens` | `int` | Provider-reported input token count. |
| `output_tokens` | `int` | Provider-reported output token count. |
| `latency_ms` | `int` | Wall-clock latency for this attempt in ms. |
| `parse_error_message` | `str` | The `str(parse_error)` that caused this attempt to fail. Useful for distinguishing "empty response" from "truncated JSON" from "items-missing" failure modes. |

**Why `retry_attempts` is always written (even as `[]`):** downstream consumers (dashboard failure viewer, analysis scripts) can unconditionally read `entry["retry_attempts"]` without a presence check. An absent key would force every consumer to guard with `.get("retry_attempts", [])`. Consistency reduces consumer error surface.

### 9.5 No pydantic model

Per Amendment A.3 of the Architect verdict, `failures.jsonl` entries are dict-shaped JSONL and are not represented by a pydantic type in `cdb_core/schemas.py`. The `append_failure` function in `cdb_collect/jsonl.py` accepts the new fields as kwargs and serializes them as-is. A type-checked read model (`FailureEntry` / `RetryAttempt`) may be added to `cdb_core` if the Stream C dashboard work (Phase 6+) requires it.

### 9.6 Example entry

A pile-sort parse-retry exhaustion failure on a Gemini model that completed step 1 before failing at step 2 on all three retries:

```json
{
  "timestamp": "2026-04-23T14:32:01.123456",
  "error_type": "PileSortParseError",
  "error_message": "Pile sort parsing failed after 3 attempts: Could not extract valid JSON from response: ",
  "context": {"model_id": "google/gemini-2.5-pro", "domain": "family", "run_index": 2},
  "prompt_verbatim": "Sort the following 25 family terms into piles...",
  "response_verbatim": "",
  "thinking_verbatim": "",
  "stop_reason": "STOP",
  "partial_session": {
    "freelist": {
      "prompt_verbatim": "List every family term you can think of...",
      "response_verbatim": "1. Mother\n2. Father\n3. Sister\n...",
      "thinking_verbatim": "",
      "stop_reason": "STOP",
      "parsed_items": ["mother", "father", "sister"],
      "input_tokens": 85,
      "output_tokens": 312,
      "latency_ms": 4201
    }
  },
  "retry_attempts": [
    {
      "attempt_index": 0,
      "response_verbatim": "",
      "thinking_verbatim": "",
      "stop_reason": "STOP",
      "input_tokens": 430,
      "output_tokens": 0,
      "latency_ms": 1843,
      "parse_error_message": "Could not extract valid JSON from response: "
    },
    {
      "attempt_index": 1,
      "response_verbatim": "",
      "thinking_verbatim": "",
      "stop_reason": "STOP",
      "input_tokens": 445,
      "output_tokens": 0,
      "latency_ms": 1901,
      "parse_error_message": "Could not extract valid JSON from response: "
    },
    {
      "attempt_index": 2,
      "response_verbatim": "",
      "thinking_verbatim": "",
      "stop_reason": "STOP",
      "input_tokens": 445,
      "output_tokens": 0,
      "latency_ms": 1755,
      "parse_error_message": "Could not extract valid JSON from response: "
    }
  ]
}
```

A simpler HTTP-layer failure (adapter raised before any response was received):

```json
{
  "timestamp": "2026-04-23T15:10:44.987654",
  "error_type": "httpx.HTTPStatusError",
  "error_message": "Client error '400 Bad Request' for url ...",
  "context": {"model_id": "microsoft/phi-4", "domain": "family", "run_index": 0},
  "retry_attempts": []
}
```

---

## 10. The DeclineInterview schema and decline_interviews.jsonl

**Changelog:**
- **v0.1.7** (2026-04-23) — Task #26: new entity. Implements the Phase 4a.1 decline-interview protocol per CDA SME verdict PASS-WITH-NOTES (2026-04-23). See `docs/DECLINE_INTERVIEW_PROTOCOL.md`.

### 10.1 Purpose and provenance

When a primary collection step (free listing, pile sorting, or pile interview) produces no interpretable output — or when the session terminates as a failure entry in `failures.jsonl` — the decline-interview protocol issues a follow-up elicitation asking the model to describe what happened. This parallels the anthropological fieldwork convention of interviewing a declining informant.

`data/raw/decline_interviews.jsonl` captures each follow-up call. It is **append-only** (like `informants.jsonl`) and is part of the open data bundle alongside `informants.jsonl` and `failures.jsonl`.

**Xor invariant:** every `DeclineInterview` record references exactly one originating session — either via `originating_informant_id` (for sessions that completed into `informants.jsonl` with `qa_passed=False`) or via `originating_failure_id` (for sessions that landed in `failures.jsonl`). Both cannot be set simultaneously; neither can both be null. The pydantic `_xor_originator` validator enforces this at write time.

**File path:** `data/raw/decline_interviews.jsonl` — gitignored via the `data/raw/` parent gitignore rule.

**Prompt version:** `decline_v1`. Prompt template at `packages/cdb_collect/cdb_collect/prompts/decline/v1/prompt.txt`. Per `CLAUDE.md` §6 rule 8, the template is immutable; any wording change requires a new version directory (`decline/v2/`) and a new `DECLINE_INTERVIEW_PROTOCOL.md` version.

**Temperature:** 0.7 — same as the free-list step per `ARCHITECTURE.md` §4.1.3.

**Design note:** `docs/DECLINE_INTERVIEW_PROTOCOL.md`.
**CDA SME verdict:** `docs/status/2026-04-23-decline-interview-protocol-sme-verdict.md`.
**Architect verdict (Stream B):** `docs/status/2026-04-23-failures-as-findings-architect-verdict.md`.

### 10.2 DeclineInterview fields

#### Identity

| Field | Type | Required | Semantics |
|---|---|---|---|
| `decline_interview_id` | `str` | Yes | SHA256[:16] of `(originating_id, prompt_version, sha256_manifest)`. Deterministic. Primary key in `lsb.sqlite`. |
| `originating_informant_id` | `str \| None` | XOR | `informant_id` of the `InformantRecord` being followed up. `None` when the origin is a `failures.jsonl` entry. |
| `originating_failure_id` | `str \| None` | XOR | Synthetic identifier for the `failures.jsonl` entry being followed up. `None` when the origin is an `InformantRecord`. |

**XOR invariant:** exactly one of `originating_informant_id` / `originating_failure_id` must be non-null. The pydantic `model_validator` raises `ValueError` if both are set or both are null.

#### Origin characterisation

| Field | Type | Required | Semantics |
|---|---|---|---|
| `originating_step` | `Literal` | Yes | Which CDA step the decline occurred on. One of `freelist`, `pile_sort`, `interview`, `pre_session`. `pre_session` covers sessions that failed before any step ran. |
| `originating_outcome_class` | `Literal` | Yes | Detection trigger class. One of `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`. Derived from the deterministic ruleset in `cdb_collect/decline_detection.py` — not from any LLM classifier. |
| `detection_rule_version` | `str` | Yes | The `DECLINE_ALLOWLIST_VERSION` constant at detection time (currently `"v1"`). Allows analysts to reproduce detection runs against frozen rulesets. Future allowlist extensions increment this version. |

#### Timestamps

| Field | Type | Required | Semantics |
|---|---|---|---|
| `detection_timestamp` | `datetime` (ISO 8601, UTC) | Yes | When the detection pass ran. Supplied by the caller (Phase 4a.1 runner) rather than computed inside the runner so it is consistent across a batch. |
| `followup_timestamp` | `datetime` (ISO 8601, UTC) | Yes | When the follow-up API call completed. Computed inside `run_decline_interview`. |

#### Model identity

| Field | Type | Required | Semantics |
|---|---|---|---|
| `model_id` | `str` | Yes | The API model string used for the follow-up call. Should match the originating session's `model_id` unless an explicit substitution was made. |
| `model_version_returned` | `str` | Yes | The exact version string returned by the provider for the follow-up call. May differ from the originating session's `model_version_returned` if the provider rolled a snapshot between the original run and the Phase 4a.1 remediation pass. See `version_drift_flag`. |
| `provider` | `str` | Yes | Provider name. |
| `api_endpoint` | `str` | Yes | Full URL of the endpoint called for the follow-up. |

#### Prompt provenance

| Field | Type | Required | Semantics |
|---|---|---|---|
| `prompt_version` | `str` | Yes | Always `"decline_v1"` for records collected under this protocol version. Immutable per version. |
| `sha256_manifest` | `str` | Yes | Single SHA256 hex digest covering `(prompt_verbatim, response_verbatim)` for the follow-up call. |
| `prompt_verbatim` | `str` | Yes | The exact follow-up prompt sent to the model. Built by substituting `task_description` and `response_verbatim_or_empty` into the `decline/v1/prompt.txt` template. |
| `response_verbatim` | `str` | Yes | The exact bytes the model returned in the follow-up call. |
| `thinking_verbatim` | `str` | No (default `""`) | The reasoning/thinking trace from the **follow-up call** (not from the originating session). Empty string for models that do not surface a thinking trace. |

#### Token / cost accounting

| Field | Type | Required | Semantics |
|---|---|---|---|
| `input_tokens` | `int` | Yes | Provider-reported input token count for the follow-up call. |
| `output_tokens` | `int` | Yes | Provider-reported output token count. |
| `latency_ms` | `int` | Yes | Wall-clock latency for the follow-up call in milliseconds. |
| `stop_reason` | `str` | Yes | Provider stop reason. |

#### QA / drift

| Field | Type | Required | Semantics |
|---|---|---|---|
| `qa_notes` | `str` | No (default `""`) | Free-text QA annotation. Written by the Phase 4a.1 runner or by manual inspection. |
| `version_drift_flag` | `bool` | No (default `False`) | `True` when the follow-up call's `model_version_returned` differs from the originating session's `model_version_returned`. Indicates that the provider rolled a snapshot between the original collection run and the Phase 4a.1 remediation pass. Records with `version_drift_flag=True` must be surfaced in the Phase 4a.1 run report per SME Note F (2026-04-23). |

### 10.3 originating_outcome_class values

| Value | Trigger | Source |
|---|---|---|
| `empty_output` | `parsed_piles` is empty (trigger a), `parsed_items` is empty (trigger c), or `parsed_pile_labels` is empty AND `response_verbatim` non-empty (trigger d) | `informants.jsonl` |
| `refusal_string_match` | `pile_sort.response_verbatim` matches the `DECLINE_ALLOWLIST` (trigger b) | `informants.jsonl` |
| `single_degenerate_pile` | `len(parsed_piles)==1` AND `items_in_pile / total_freelist_items >= 0.95` (trigger e) | `informants.jsonl` |
| `parse_failure` | Error type name contains "parse", "json", or "value" | `failures.jsonl` |
| `http_error` | Error type name contains "http", "status", or "connect" | `failures.jsonl` |
| `timeout` | Error type name contains "timeout" | `failures.jsonl` |
| `other` | Fallback for unclassified failure types | `failures.jsonl` |

The detection rules live in `packages/cdb_collect/cdb_collect/decline_detection.py`. The allowlist version is `DECLINE_ALLOWLIST_VERSION = "v1"`. New entries require Architect sign-off per Reviewer rules.

### 10.4 The decline_interviews table in lsb.sqlite

`scripts/build_db.py` ingests `decline_interviews.jsonl` when it exists at the auto-detected path `data/raw/decline_interviews.jsonl` (sibling to `informants.jsonl`) or when passed via `--decline-interviews`. The table mirrors the `DeclineInterview` schema:

```sql
CREATE TABLE decline_interviews (
  decline_interview_id TEXT PRIMARY KEY,
  originating_informant_id TEXT,           -- NULL for failures.jsonl origins
  originating_failure_id TEXT,             -- NULL for informants.jsonl origins
  originating_step TEXT NOT NULL,
  originating_outcome_class TEXT NOT NULL,
  detection_rule_version TEXT NOT NULL,
  detection_timestamp TEXT NOT NULL,
  followup_timestamp TEXT NOT NULL,
  model_id TEXT NOT NULL,
  model_version_returned TEXT NOT NULL,
  provider TEXT NOT NULL,
  api_endpoint TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  sha256_manifest TEXT NOT NULL,
  prompt_verbatim TEXT NOT NULL,
  response_verbatim TEXT NOT NULL,
  thinking_verbatim TEXT NOT NULL DEFAULT '',
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  latency_ms INTEGER NOT NULL,
  stop_reason TEXT NOT NULL,
  qa_notes TEXT NOT NULL DEFAULT '',
  version_drift_flag INTEGER NOT NULL DEFAULT 0,  -- 0=False, 1=True
  FOREIGN KEY (originating_informant_id) REFERENCES informants(informant_id)
);
```

`originating_failure_id` has no FK constraint because `failures.jsonl` entries are dict-shaped and not represented by a pydantic type or a separate SQLite table in v1.

### 10.5 Example entry

```json
{
  "decline_interview_id": "a1b2c3d4e5f60001",
  "originating_informant_id": "abc12345def67890",
  "originating_failure_id": null,
  "originating_step": "pile_sort",
  "originating_outcome_class": "empty_output",
  "detection_rule_version": "v1",
  "detection_timestamp": "2026-04-24T09:00:00+00:00",
  "followup_timestamp": "2026-04-24T09:00:02.341000+00:00",
  "model_id": "google/gemini-2.5-pro",
  "model_version_returned": "gemini-2.5-pro-20260401",
  "provider": "openrouter",
  "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "prompt_version": "decline_v1",
  "sha256_manifest": "e3b0c44298fc1c149afb...",
  "prompt_verbatim": "A moment ago I asked you to perform the following task: Sort the following 25 family terms into piles based on how similar they are to each other... The output I received was: (empty). In your own words, please describe what happened in that exchange.",
  "response_verbatim": "In that exchange, I received a request to sort family relationship terms into groups based on similarity. The output field being empty suggests that I either...",
  "thinking_verbatim": "",
  "input_tokens": 312,
  "output_tokens": 148,
  "latency_ms": 2341,
  "stop_reason": "end_turn",
  "qa_notes": "",
  "version_drift_flag": false
}
```

---

*End of `docs/DATA_DICTIONARY.md` v0.1. This is a living document; it will move forward as the schema evolves. The Reviewer agent enforces co-update with `cdb_core/schemas.py`.*