# LSB Data Dictionary

**Document name:** `docs/DATA_DICTIONARY.md`  
**Version:** v0.1.22 (aligned with `ARCHITECTURE.md` v0.7.5; see changelog for history)  
**Status:** Phase 0 / Phase 1 deliverable per `ARCHITECTURE.md` §4.3  
**Audience:** External researchers using the LSB open data bundle; LSB internal contributors touching the schema  
**Companion docs:** `ARCHITECTURE.md` §3.2 (schema source of truth), §4.3 (storage), §6.7 (open data policy)

**Stability promise:** this document moves in lockstep with `cdb_core/schemas.py`. Any change to `InformantRecord`, `GroundingRef`, or any other schema documented here requires a matching update to this file in the same PR. The Reviewer agent enforces this (Reviewer rule 5 in `ARCHITECTURE.md` §5.1). Adding new optional fields is non-breaking; removing or renaming a field is a breaking change that requires a major version bump and a migration note in the changelog.

**Changelog:**
- **v0.1.22** (2026-05-24) — Phase 9a term-truncation task: Added `compute_cross_model_term_frequency()` to `cdb_analyze/cooccurrence.py`. Added `item_subset: list[str] | None = None` parameter to `build_pooled_cooccurrence_matrix()`. Added truncation step in `cdb_analyze/pipeline.py` `run_pipeline()` between step 2 (per-model matrices) and step 2b (pooled matrix): computes cross-model term frequency, pre-filters terms with f_models < 2, applies `find_salience_elbow()` (min_items=15, max_items=300) to the frequency curve, passes the truncated item list to the pooled matrix builder. Added four new optional fields to `DomainResult` in `cdb_core/schemas.py` (§2 table updated): `term_truncation_method` (`str`, default `""`), `term_truncation_params` (`dict[str, Any]`, default `{}`), `term_n_total_before_truncation` (`int`, default `0`), `term_n_after_truncation` (`int`, default `0`). All additions are optional with falsy defaults — no breaking changes. Added §2.8 to this document. Per-model item MDS (Register 1) is NOT truncated — each model's matrix uses its full vocabulary per CDA SME T4. CDA SME ruling: PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-term-truncation-sme-ruling.md` T1–T6). Architect sign-off in SME ruling document.
- **v0.1.21** (2026-05-24) — Phase 9a T5: Added `aggregate_cluster_labels()` to `cdb_analyze/pipeline.py`. This function derives `DomainResult.term_cluster_labels` from per-model centroid pile labels via Jaccard-overlap matching (threshold ≥ 0.3) and frequency-weighted modal label selection. Wired into `run_pipeline()` after the T3 AHC step; result stored in `DomainResult.term_cluster_labels`. Added §2.7 to this document documenting the algorithm. Updated `term_cluster_labels` table row in §2 to reflect that it is now populated by `pipeline.py` (previously described as populated only by the publish layer). No schema changes — `term_cluster_labels: list[str] = []` field was already present from T1/T2/T3. Architect sign-off: `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T5. CDA SME verdict: PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md` M6, A2).
- **v0.1.20** (2026-05-24) — Phase 9a T4: Added `bootstrap_term_mds_ellipses()` and `bootstrap_branch_stability()` to `cdb_analyze/bootstrap.py`. Added two new optional fields to `DomainResult` in `cdb_core/schemas.py` (§2 table updated): `term_mds_uncertainty` (`dict[str, Any]`, item_name → BootstrapEllipse-like dict) and `term_cluster_bp_values` (`list[float]`, one bootstrap proportion per internal AHC node). Both are optional with empty-dict/list defaults — no breaking changes. Bootstrap resamples models with replacement (Register 2, B=200) per CDA SME M4; CIs reflect between-model structural variance only (M4a). Branch stability uses simple bootstrap proportion (BP), not multiscale AU, per CDA SME M5. Architect sign-off: `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T4 schema block. CDA SME verdict: PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md` M4, M4a, M5, M5a, F4).
- **v0.1.19** (2026-05-24) — Phase 9a T1/T2/T3: Added `build_pooled_cooccurrence_matrix()` to `cdb_analyze/cooccurrence.py` (§2.4 new). Added `cluster_terms()` to `cdb_analyze/cluster.py`. Added six new optional fields to `DomainResult` in `cdb_core/schemas.py` (§2 table updated): `term_mds_coordinates`, `term_mds_items`, `term_cluster_linkage`, `term_cluster_assignments`, `term_cluster_labels`. All additions are optional with empty-dict/list defaults — no breaking changes. Pooling strategy per CDA SME M1: equal-weight-per-model (mean of per-model consensus matrices), denominator always M, absence=0.0. AHC uses `method="average"` (UPGMA) per CDA SME M2; distance = `1 - cooccurrence` per CDA SME M3. `WithinModelResult.mds_within_model` now populated by pipeline with `list[dict]` of `{"item", "x", "y"}` entries (Register 1, per CDA SME F3). Architect sign-off: `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T1/T2/T3 schema block. CDA SME verdict: PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md` M1–M3, F3).
- **v0.1.18** (2026-05-24) — Phase 9a T5-minimal: Added `CentroidPileData` Pydantic model to `cdb_core/schemas.py` (§2.3 new). Added `DomainResult.centroid_piles: dict[str, CentroidPileData] = {}` field (§2 table updated). Both additions are optional with empty-dict defaults — no breaking changes. `centroid_piles` is populated by `cdb_analyze/pipeline.py` `_build_centroid_piles()` using each model's centroid run (identified by `WithinModelResult.centroid_run_id`). Per-term pile stability computed per CDA SME ruling F5 (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md`): set equality of co-occurring items, not pile index. Architect sign-off: `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md` T9 schema block. CDA SME verdict: PASS-WITH-NOTES (`docs/status/2026-05-24-phase9a-cda-sme-verdict.md` F5).
- **v0.1.17** (2026-05-19) — Phase 8 T6: Added §14 documenting the open bundle tarball layout, MANIFEST.txt format, and `scripts/build_open_bundle.py` builder usage. Added §0 cross-link to §14. No schema changes. Architect plan: Phase 8 T6. CDA SME verdict: `docs/status/2026-05-19-phase8-T6.2-cda-sme-verdict.md` (PASS-WITH-NOTES; N1–N7 applied to `data/open_bundle/README.md`).
- **v0.1.16** (2026-05-17) — Phase 7 T7 docs sweep: §13.5 updated to add `emailed_dedupe_keys.json` state file (introduced in T6a but not previously documented). The `framing_checks` field is confirmed to carry four canonical keys (`hypothesis_framing`, `cognition_attribution`, `bare_numeric_without_ci`, `register_boundary`) as defined in T3 CDA SME §5.11 and implemented in `cdb_social/drafters/base.py`. Note added to §13.3 queue-acceptance contract. No schema changes. See `ARCHITECTURE.md` v0.7.4 changelog.
- **v0.1.15** (2026-05-17) — Phase 7 T1: Added §13 documenting the social publishing pipeline schemas and on-disk layout. Three new types in `cdb_core/schemas.py`: `SocialTrigger`, `SocialDraft`, `SocialPostRecord`. Three new enums: `TriggerType`, `Platform`, `PublishStatus`. New directory tree at `out/social/queue/{pending,approved,published,failed}/` and `out/social/state/` (gitignored; only `out/social/README.md` is tracked). CDA SME PASS-WITH-NOTES verdict applied: §5.2 (`forbidden_terms_hit` docstring contract), §5.3 (`framing_check_passed` + new `framing_checks: dict[str, bool]` sibling), §5.4 (renamed `confidence_score` → `drafter_self_rating: float = 0.0`), §5.5 (`suggested_posting_time` operational-only docstring), §5.6 (`evidence` dict docstring + T2 carry-forward), §5.8 (`dedupe_key` formula + exclusion of `drafter_version`/`prompt_version`). No changes to `InformantRecord`, `GroundingRef`, or any existing `cdb_core` schema. CDA SME verdict: `docs/status/2026-05-17-phase7-T1-cda-sme-verdict.md` (PASS-WITH-NOTES).
- **v0.1.14** (2026-05-12) — Phase 6 T9: Added §12 documenting the published failures JSON shape emitted by `packages/cdb_publish/cdb_publish/failures.py` to `apps/dashboard/public/data/failures/{slug}.json`. New publish-layer schemas in `packages/cdb_publish/cdb_publish/schemas/failures.py` (`PublishedFailuresFile`, `PublishedFailureRecord`). New sanitization module `packages/cdb_publish/cdb_publish/sanitize.py`. `Manifest` schema gains `failures: dict[str, str]` field. `scripts/publish.py` gains three new CLI args for raw-data paths. No changes to `cdb_core/schemas.py`. CDA SME verdict: `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` (PASS-WITH-NOTES; §5.1–§5.5 applied).
- **v0.1.13** (2026-05-07) — Fix-forward metadata accuracy (sibling task between Phase 4b T2 and T3): `AdapterResult` gains `max_tokens_used: int = 4096` field; every adapter now sets this to the actual `max_tokens` value it sends to the API (4096 for Anthropic/HuggingFace/OpenAI-compat; 16384 for Google Gemini; `compute_effective_max_tokens(prompt, context_length)` for OpenRouter — typically 16384 for large-context models, ~13872 for phi-4). `runner.py` `_assemble_record()` now reads `freelist_result.max_tokens_used` instead of the hardcoded `4096` constant. Updated `InformantRecord.max_tokens` field description to add the editorial note documenting the historical inaccuracy in records collected before this commit. No schema changes to `InformantRecord` or `GroundingRef`; no new dependencies. Historical records in `informants.jsonl` are unchanged (append-only invariant preserved). Reviewer-T2 finding (commit `f7ca048`): `docs/status/2026-05-07-phase4b-t2-reviewer-verdict.md` note 1. Mark's Option A ruling: fix forward only, no backfill. Precedent: `memory/project_metadata_fix_forward_precedent.md`.
- **v0.1.12** (2026-05-05) — T4 redo RD-2 (commit 1 scaffold): Added §11 documenting the `ConfabulationClassification` schema in `packages/cdb_analyze/cdb_analyze/confabulation_classification.py`. This is a derived-data schema for the 9 originally-Gemini cap-exhaustion decline-interview rows (Phase 4a.1); it lives in `cdb_analyze`, not `cdb_core`, and is not part of the open-data-bundle schema commitment. Architect plan: `docs/status/2026-05-05-t4-redo-architect-plan.md` §2 RD-2. CDA SME verdict: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1 wording rules, T2 enum naming applied). No changes to `InformantRecord`, `GroundingRef`, or any `cdb_core` schema.
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

**Open bundle structure:** for the full tarball layout, MANIFEST.txt format, and builder usage reference, see §14.

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
| `max_tokens` | `int` | Yes | The `max_tokens` parameter passed to the API. **Editorial note (2026-05-07):** prior to the fix-forward commit that accompanies this note, this field was hardcoded to `4096` in `runner.py` regardless of the actual `max_tokens` value sent to the API. Records in `informants.jsonl` collected before this commit (campaigns: Phase 4a 2026-04-22, recovery 2026-05-05, Phase 4b T2 phi-4 rerun 2026-05-07) carry the historical inaccurate value `4096`. Records collected after this commit reflect the actual per-call value. The actual cap at the API-call level can be reconstructed from the runner code at the commit referenced in `analysis_code_git_sha`: `4096` for the original Phase 4a era; `16384` for the Task-#16 era (commits `7f8f7f7`/`de3dd7e`, 2026-05-04, for Google and OpenRouter adapters); approximately `13872` for phi-4 cells after the Phase 4b T2 adaptive cap (commit `628497d`, 2026-05-07). See also `docs/status/2026-05-07-phase4b-t2-reviewer-verdict.md` (note 1) for the Reviewer finding that surfaced this gap. |
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
| `centroid_piles` | `dict[str, CentroidPileData]` | No (default `{}`) | Per-model centroid pile structure for the PileComparison view. Keyed by `model_id`. Each entry holds the centroid run's pile groupings and labels, plus per-term pile-stability scores for R10 compliance. Empty when the pipeline has not yet populated this field. See §2.3 for the `CentroidPileData` sub-schema. Populated by `cdb_analyze/pipeline.py` `_build_centroid_piles()` using each model's centroid run identified by `WithinModelResult.centroid_run_id`. |
| `term_mds_coordinates` | `dict[str, list[float]]` | No (default `{}`) | Pooled cross-model term MDS coordinates. Maps each item name to `[x, y]`. Register 2 output — uncertainty reflects between-model structural variance, not within-model run variance (per CDA SME F3). See §2.4 for the pooling algorithm. Empty when the domain has fewer than 3 items. |
| `term_mds_items` | `list[str]` | No (default `[]`) | Canonical ordered item list for the pooled term MDS. Sorted deterministically (lexicographic). Consumers should use this list as the canonical item index for all term-level analyses in this `DomainResult`. |
| `term_cluster_linkage` | `list[list[float]]` | No (default `[]`) | Scipy linkage matrix for the term-level AHC, serialized as nested list of shape (n_items−1) × 4. Column semantics (scipy linkage format): `[child_idx_1, child_idx_2, merge_distance, cluster_size]`. Indices 0 .. n_items−1 are original items (ordered per `term_mds_items`); indices n_items .. 2n_items−2 are synthesized cluster nodes. Average-linkage (UPGMA) per CDA SME M2. Reconstruct dendrogram with `scipy.cluster.hierarchy.dendrogram(Z)` where `Z = np.array(term_cluster_linkage)`. |
| `term_cluster_assignments` | `dict[str, int]` | No (default `{}`) | Per-item cluster assignment at the default cut level (biggest-gap heuristic). Maps item name → integer cluster ID (1-indexed, from scipy `fcluster()`). Empty when the domain has fewer than 2 items. |
| `term_cluster_labels` | `list[str]` | No (default `[]`) | One human-readable label per cluster (indices match cluster IDs in `term_cluster_assignments` after converting to 0-based: `term_cluster_labels[k]` is the label for `cluster_id = k+1`). Populated by `aggregate_cluster_labels()` in `cdb_analyze/pipeline.py` during `run_pipeline()` (Phase 9a T5). Uses frequency-weighted modal label via Jaccard-overlap matching across model centroid pile labels (threshold ≥ 0.3). "Uncategorized" when no model pile matches. See §2.7 for the full algorithm. |
| `term_mds_uncertainty` | `dict[str, Any]` | No (default `{}`) | Per-term 95% bootstrap confidence ellipses on the pooled term MDS. Maps item name to a `BootstrapEllipse`-shaped dict (fields: `center`, `semi_major`, `semi_minor`, `rotation_rad`, `n_bootstrap`). Register 2 output — reflects between-model structural variance only, not within-model run variance (per CDA SME M4a). See §2.6. The R10 compliance mechanism for the term MDS: the term MDS cannot ship without these ellipses. |
| `term_cluster_bp_values` | `list[float]` | No (default `[]`) | Bootstrap proportion (BP) values for the term AHC dendrogram, one per internal node in linkage row order. BP = fraction of bootstrap iterations in which the exact bipartition for that node appears in the bootstrap tree (CDA SME M5). Range `[0.0, 1.0]`. Dashboard displays as "bootstrap support (%)" not "AU p-value" (M5a). Branches below 0.70 (70%) are rendered with dashed lines — this is a display threshold, not a statistical gate. See §2.6. |
| `term_truncation_method` | `str` | No (default `""`) | Identifies the truncation strategy applied to the pooled term set. Value is `"cross_model_frequency_elbow"` for runs produced by the Phase 9a truncation step; empty string on pre-truncation analysis versions. See §2.8. |
| `term_truncation_params` | `dict[str, Any]` | No (default `{}`) | Parameters used for the truncation step. For `"cross_model_frequency_elbow"` the dict contains: `min_items` (floor on items kept), `max_items` (ceiling), `min_model_count` (hard pre-filter threshold; terms below this are removed before the elbow), and `elbow_index` (the 1-based cut point returned by `find_salience_elbow()`). Empty dict on pre-truncation runs. See §2.8. |
| `term_n_total_before_truncation` | `int` | No (default `0`) | Count of distinct terms in the full union across all models' pile sorts, before any filtering. `0` on pre-truncation analysis versions. |
| `term_n_after_truncation` | `int` | No (default `0`) | Count of terms that entered `build_pooled_cooccurrence_matrix()` after truncation. Equals `len(term_mds_items)`. `0` on pre-truncation analysis versions. External researchers wishing to replicate the analysis with a different truncation can rebuild from `informants.jsonl` — see §2.8. |
| `generated_lede` | `str` | Yes | The pre-written one-sentence lede for this domain at this analysis version. Generated by the lede generator (`ARCHITECTURE.md` §4.2.3). |
| `generated_at` | `datetime` (ISO 8601, UTC) | Yes | When this `DomainResult` was generated. |

**Important:** `groundings` is a list, not a singleton. The v0.6 schema had `grounding: GroundingRef | None`; the v0.7 schema has `groundings: list[GroundingRef] = []`. If you have code reading the v0.6 schema, you need to update it to handle the list. The v0.7 schema is the only supported form going forward. **Note (2026-05-07).** Per the 2026-05-07 amendment removing human baselines from v1 (`ARCHITECTURE.md` §1.5.5), all v1 `DomainResult` instances ship with `groundings = []` and `selected_baseline_id = None`. The schema field is retained for forward compatibility and for documentation completeness; it does not drive v1 production data.

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
| `mds_within_model` | `list[dict]` | No (default `[]`) | Per-model term MDS — Register 1 output (per CDA SME F3, 2026-05-24-phase9a-cda-sme-verdict.md). Each entry is `{"item": str, "x": float, "y": float}`. Populated by `pipeline.py` using `run_item_mds()` on the per-model co-occurrence matrix. The `underestimates_uncertainty` annotation applies: per-model item positions reflect single-model output distribution only. Empty for models with fewer than 3 terms. |

### 2.2 Measure result types (added post-F1 SME review)

Reference shapes for the measure entries embedded in `DomainResult`:

- **`SutropCSI`** — `{item: str, csi: float, f_mentions: int, n_runs: int, mean_position: float}`. Sutrop 2001 salience index.
- **`NolanIndexPair`** — `{model_a: str, model_b: str, ni: float, jaccard: float, ni_vs_jaccard_delta: float}`. Robbins 2023.
- **`MantelPair`** — `{model_a: str, model_b: str, r: float, p_value: float, n_permutations: int}`. Mantel 1967.

### 2.3 `CentroidPileData` (Phase 9a T5-minimal — added 2026-05-24)

`CentroidPileData` holds the pile structure from a model's centroid run, plus per-term pile-stability scores used as the R10 categorical-uncertainty proxy by the PileComparison dashboard view (Phase 9a T9). Stored in `DomainResult.centroid_piles`, keyed by `model_id`.

**Population:** `cdb_analyze/pipeline.py` `_build_centroid_piles()` populates this during the standard analysis pipeline run. The centroid run is the run with the highest centrality loading, identified by `WithinModelResult.centroid_run_id`. If `centroid_run_id` is `None` for a model, that model does not appear in `centroid_piles`.

| Field | Type | Required | Semantics |
|---|---|---|---|
| `piles` | `list[list[str]]` | Yes | The pile groupings from the centroid run. Taken verbatim from `InformantRecord.pile_sort.parsed_piles` for the centroid run. Each inner list is one pile. Item order within a pile is not significant. The union of all inner lists is the full item set for that run. |
| `labels` | `list[str]` | Yes | The model's free-text labels for each pile, in the same order as `piles`. Taken from `InformantRecord.interview.parsed_pile_labels` for the centroid run. `len(labels) == len(piles)` invariant. |
| `term_stability` | `dict[str, float]` | No (default `{}`) | Per-term categorical-uncertainty proxy for R10 compliance. For each term, the fraction of the model's runs in which the term co-occurs with the same set of other items as in the centroid run. Range `[0.0, 1.0]`. |

**`term_stability` computation rule** (CDA SME ruling F5, `docs/status/2026-05-24-phase9a-cda-sme-verdict.md`):

1. For each term `t` in the centroid run's pile structure, identify the set `S_centroid(t)` = all OTHER items that appear in the same pile as `t` in the centroid run (the co-occurring set). For a singleton pile, `S_centroid(t) = {}` (empty set).
2. For each run `r` in the model's full run set (including the centroid run itself), find the pile containing `t`, collect the other items in that pile as `S_r(t)`.
3. A run `r` is "same pile" for term `t` if `S_r(t) == S_centroid(t)` (exact set equality, not pile index equality — pile ordering is arbitrary and must not be used for comparison).
4. `term_stability[t] = count(same-pile runs) / n_runs_total`.

**Special cases:**
- A model with exactly one run has `term_stability = 1.0` for all terms (the single run IS the centroid run; it vacuously matches itself).
- A term that is always in a singleton pile has `S_centroid(t) = {}`. It is stable across any run where it also appears in a singleton pile (regardless of whether other singletons are present).
- If the centroid run ID is not found in the records list (e.g., the record was excluded by QA filtering), the model is omitted from `centroid_piles` entirely.

**Dashboard use:** The PileComparison component (T9) uses `piles` and `labels` to render per-model pile structure side by side. `term_stability` drives the visual uncertainty indicator (opacity or asterisk) per the T9 acceptance criteria. Low-stability terms (e.g., below 0.5) are flagged as less structurally reliable, providing R10-compliant uncertainty display for a categorical (non-numeric) finding.

### 2.4 Pooled cross-model term co-occurrence matrix (Phase 9a T1)

The pooled matrix is an equal-weight-per-model average of all models' individual consensus co-occurrence matrices. It drives `term_mds_coordinates` and `term_cluster_linkage`.

**Algorithm (CDA SME M1, binding):**

1. For each model with at least one valid run, build a per-model consensus co-occurrence matrix using `build_cooccurrence_matrix()` from `cdb_analyze/cooccurrence.py`.
2. Collect the union of all items across all models' pile sorts. Sort lexicographically for determinism.
3. For items absent from a given model's vocabulary: their cells in that model's matrix are treated as 0.0 (evidence of absence, not missing data).
4. Pooled value: `pooled[i][j] = (1/M) × sum_over_models(model_cooccurrence[i][j])` where M = number of models with at least one valid run. **The denominator is always M**, not the number of models that produced both items. This is the conservative choice: a model that never mentioned an item contributes to the denominator.

**Register semantics:** The pooled matrix and its derived products (`term_mds_coordinates`, `term_cluster_linkage`, `term_cluster_assignments`) are Register 2 outputs. The underlying uncertainty question is: "how much does the position of this term depend on which models are in the pool?" — which is a between-model structural variance question. Per-model item MDS (`WithinModelResult.mds_within_model`) is Register 1.

### 2.5 Term-level AHC (Phase 9a T3)

`term_cluster_linkage` and `term_cluster_assignments` capture the agglomerative hierarchical clustering of domain terms using the pooled co-occurrence matrix as input.

**Algorithm (CDA SME M2/M3, binding):**

1. **Distance metric (M3):** `dissimilarity[i][j] = 1.0 − pooled_cooccurrence[i][j]`. Diagonal = 0.0. This is the same distance space as `run_item_mds()`, ensuring AHC cluster boundaries correspond to MDS spatial neighbourhoods.
2. **Linkage method (M2):** Average linkage (UPGMA). `scipy.cluster.hierarchy.linkage(condensed, method="average")`. Not Ward — Ward's equal-cluster-size assumption does not hold for CDA pile-sort data, which routinely produces large "miscellaneous" clusters. See docstring in `cdb_analyze/cluster.py :: cluster_terms()`.
3. **Citation:** Borgatti (1994) "Cultural domain analysis" and Spencer et al. (2016) both use average linkage for CDA pile-sort term clustering.
4. **Cut level:** The biggest-gap heuristic (same as `cluster_models()`): find the index with the largest jump in merge distances in `Z[:, 2]`, set the cut threshold between that merge and the next.

**Reproducibility:** Given the same `informants.jsonl`, `build_pooled_cooccurrence_matrix()` and `cluster_terms()` are fully deterministic (no random state). Researchers with the open data bundle can reproduce `term_cluster_linkage` exactly by running `scripts/run_analysis.py` (or re-running `pipeline.py` directly).

### 2.6 Term-level bootstrap uncertainty (Phase 9a T4)

`term_mds_uncertainty` and `term_cluster_bp_values` are the R10 compliance outputs for the term-level visualizations: no term MDS point or dendrogram branch ships without an associated uncertainty indicator.

**Register semantics:** Both fields are Register 2 outputs. The uncertainty question is "how much does the result depend on which models are included?" — between-model structural variance only. Within-model run-to-run variance is absorbed into each model's pre-computed consensus co-occurrence matrix before the bootstrap runs. Per CDA SME M4a, the methods page and any tooltip for these fields must state: "Term position confidence reflects agreement across models, not within-model sampling variance."

#### `term_mds_uncertainty` — per-term 95% confidence ellipses

Produced by `bootstrap_term_mds_ellipses()` in `cdb_analyze/bootstrap.py`.

**Algorithm (CDA SME M4, binding):**

1. Pre-compute per-model consensus co-occurrence matrices (from `build_cooccurrence_matrix()`, one per model).
2. For each of B=200 iterations:
   a. Draw M model IDs with replacement (where M = number of models).
   b. Pool the resampled model matrices using the equal-weight-per-model formula (same as §2.4).
   c. Run `run_item_mds()` on the resampled pooled matrix.
   d. Procrustes-align the bootstrap item coordinates to the reference solution (from the full pooled MDS).
   e. Record each item's aligned (x, y).
3. For each item, fit a 95% confidence ellipse from the B coordinate samples using eigendecomposition of the coordinate covariance matrix. Same ellipse-fitting logic as the model-level `bootstrap_mds_ellipses()`.
4. Items that appear in the bootstrap iteration's pooled matrix contribute their aligned coordinate. Items absent from a bootstrap iteration (because all resampled models lacked that item) are excluded from that iteration's coordinate recording.

**B=200 is sufficient** for 95% CI estimation on ~25-item MDS per CDA SME F4 — the half-width converges to within 5% of the B=500 value by B=150 for 2D MDS with fewer than 50 points.

**JSON shape:** Each value in `term_mds_uncertainty` is a `BootstrapEllipse` dict with fields:
- `center`: `[float, float]` — mean (x, y) of the bootstrap coordinate distribution
- `semi_major`: `float` — length of the ellipse's major axis (√(λ₁ × χ²₀.₉₅))
- `semi_minor`: `float` — length of the minor axis (√(λ₂ × χ²₀.₉₅))
- `rotation_rad`: `float` — rotation angle of the major axis in radians
- `n_bootstrap`: `int` — number of bootstrap iterations that contributed coordinates for this item (may be less than B=200 if the item was absent from some iterations' pooled matrices)

**Degenerate case:** If fewer than 2 bootstrap iterations contributed coordinates for an item, a zero-size ellipse is emitted at the reference position with `n_bootstrap` set to the actual count.

#### `term_cluster_bp_values` — dendrogram branch bootstrap proportions

Produced by `bootstrap_branch_stability()` in `cdb_analyze/bootstrap.py`.

**Algorithm (CDA SME M5, binding):**

1. For each of B=200 iterations:
   a. Resample M model IDs with replacement (same resampling strategy as term MDS bootstrap).
   b. Pool the resampled model matrices.
   c. Compute the UPGMA linkage on the pooled distance matrix (distance = 1 − cooccurrence, same as §2.5).
   d. Extract the set of bipartitions from the bootstrap dendrogram. Each internal node defines a bipartition; canonical form is the smaller of the two subtrees (to make comparison symmetric).
   e. For each reference bipartition (from `term_cluster_linkage`), check if it appears in the bootstrap bipartition set.
2. BP for node k = count(bootstrap iterations containing reference bipartition k) / B.

**Interpretation:** BP = 0.85 means "85% of bootstrap resamples produced a dendrogram that contains this branch." BP = 0.50 means the branch is unstable.

**Important:** BP is NOT an AU p-value (Shimodaira 2002). The multiscale bootstrap AU correction was considered and rejected because it requires n ≥ 100 observations for reliable calibration and LSB has M=11 models. The simple BP is interpretable, transparent, and conservative — appropriate for LSB's exploratory framing (per ARCHITECTURE.md §1.5.7). See CDA SME M5 ruling for the full rationale.

**Display contract (M5a):** The dashboard labels this field as "bootstrap support (%)" in all copy, tooltips, and axis labels. The string "AU p-value" must not appear in any dashboard copy. Branches below 70% BP are rendered with dashed lines and reduced opacity (display threshold, not a statistical gate — UI/UX agent owns the visual treatment).

**List ordering:** `term_cluster_bp_values[k]` corresponds to row k of `term_cluster_linkage`. Row 0 is the first merge step (the two closest items), row n_items−2 is the last merge step (the root). This matches scipy's linkage matrix row order.

**Reproducibility:** `bootstrap_branch_stability()` is seeded with `random_state=42` by `pipeline.py`. Researchers with the open data bundle can reproduce `term_cluster_bp_values` by running the analysis pipeline with the same seed.

### 2.7 Cluster label aggregation (Phase 9a T5)

`term_cluster_labels` is populated by `aggregate_cluster_labels()` in `cdb_analyze/pipeline.py`, immediately after the T3 AHC step. The algorithm is a pure string-matching procedure — no LLM calls, no embedding models.

**Algorithm (CDA SME M6, binding):**

1. For each AHC cluster C (identified by `term_cluster_assignments`), collect the set of items assigned to it.
2. For each model in `centroid_piles`, examine every pile in that model's centroid run. Compute Jaccard overlap between the cluster's item set and the pile's item set: `Jaccard = |intersection| / |union|`. Select the pile with the highest Jaccard for that model.
3. A model contributes a label only if its best Jaccard ≥ 0.3. If no pile exceeds the threshold, that model contributes no label for this cluster.
4. Collect all contributing labels. Select the modal label (most frequent occurrence, case-normalised to lowercase for frequency counting). If there is a unique mode, that label wins.
5. Ties in frequency are broken by the shortest original label. Further ties (equal length) are broken lexicographically for determinism.
6. If all collected labels appear exactly once (every label unique), the shortest label among the set is used (same tie-break logic as frequency ties).
7. If no model contributes a label (no pile exceeds the 0.3 threshold), the cluster's label is `"Uncategorized"`.

**List indexing:** `term_cluster_labels[k]` is the label for the cluster with `cluster_id = k + 1` (because scipy `fcluster()` returns 1-based cluster IDs). Sorted by ascending `cluster_id`.

**Imperfection is expected:** Cluster labels are a convenience gloss for the dashboard visitor, not a finding. The structural finding is the item membership of each cluster. Per CDA SME A2: "Cluster labels will be imperfect. Acceptable for v1. Human curation in future phases is the correct improvement path."

**Population:** `cdb_analyze/pipeline.py` populates this field after the T3 AHC step using `centroid_piles` (built in the T5-minimal step). Both `term_cluster_assignments` and `centroid_piles` must be non-empty for aggregation to run; otherwise `term_cluster_labels` is left empty.

### 2.8 Term-set truncation (Phase 9a term-truncation task)

The pooled term set is truncated before the pooled co-occurrence matrix is computed. This step is a methodological parameter (not a display filter): it determines which terms enter the pooled matrix, which in turn determines the MDS coordinates, the AHC, and the bootstrap CIs. The truncation metadata is recorded in `DomainResult` for reproducibility.

**Rationale (CDA SME ruling T1–T4, `docs/status/2026-05-24-phase9a-term-truncation-sme-ruling.md`):**

The pooled matrix is a Register 2 artifact — its informants are models, not runs. A term that only one model ever pile-sorted is an idiosyncrasy of that model's categorical structure, not part of the shared domain vocabulary. In human CDA with multiple informants, Borgatti (1994) cuts at the item-frequency level for precisely this reason. The cross-model frequency `f_models(term)` is the correct unit: it counts distinct models, not runs.

**Algorithm (binding):**

1. For each term in the pile-sort union, compute `f_models(term)` = the number of distinct models whose pile sorts include that term. Implemented by `compute_cross_model_term_frequency()` in `cdb_analyze/cooccurrence.py`. **Operates on `pile_sort.parsed_piles` only** — not `freelist.parsed_items`. Terms that appeared in a free list but were not carried into the pile sort have no co-occurrence data to contribute and must not be included.

2. **Pre-filter (hard floor):** Remove any term with `f_models < 2`. A term that only one model out of M pile-sorted is definitionally not shared vocabulary. This floor is not overridable by the elbow. Controlled by `term_truncation_params["min_model_count"]` (value: 2).

3. **Elbow detection:** Apply `find_salience_elbow()` from `cdb_analyze/consensus.py` (maximum-distance-to-chord geometric method) to the sorted-descending f_models frequency curve of the shared terms. Parameters: `min_items=15`, `max_items=300`. The elbow algorithm is the same one used for within-model free-list truncation; the only change is that the y-axis is `f_models` (descending) instead of Smith's S. The cut point is `term_truncation_params["elbow_index"]` (1-based count of items to keep).

4. **Subset passed to pooled matrix:** `truncated_items = [term for term, _ in shared_terms[:elbow_index]]`. This list is passed as `item_subset` to `build_pooled_cooccurrence_matrix()`. Items absent from a model's per-model matrix continue to receive 0.0 in that model's contribution — the pooling arithmetic is unchanged.

**What is NOT truncated:** The per-model consensus co-occurrence matrices (step 2 in `run_pipeline()`) are built from each model's full pile-sort vocabulary. Only the pooled matrix uses the truncated item set. Per CDA SME T4: "The per-model consensus co-occurrence matrices remain un-truncated."

**Methodology page text (CDA SME T6, binding):** "Terms appearing in only one model's pile sorts are excluded from the pooled analysis as model-specific vocabulary. Among the remaining shared terms, a geometric elbow detector (maximum-distance-to-chord on the cross-model frequency curve) identifies the core vocabulary that multiple models converge on. For the family domain, this reduced the term set from [N_total] to [N_truncated] terms." Fill `[N_total]` from `term_n_total_before_truncation` and `[N_truncated]` from `term_n_after_truncation` at page-generation time.

**Reproducibility:** External researchers wishing to replicate the analysis with a different truncation can rebuild from `informants.jsonl`. The parameters in `term_truncation_params` are sufficient to reproduce the exact truncation: re-run `compute_cross_model_term_frequency()`, apply the same `min_model_count` pre-filter and `find_salience_elbow()` with the documented `min_items`/`max_items`, and the resulting `truncated_items` list will match `term_mds_items`.

---

## 3. The GroundingRef schema (v0.7)

**Editorial note (2026-05-07).** All v1 LSB domains ship with an empty `groundings` list. `GroundingRef` is documented here for schema completeness and forward compatibility, not because v1 production data populates it. See `ARCHITECTURE.md` §1.5.5 for the framing rationale and `docs/status/2026-05-07-lsb-philosophy-and-framing.md` for the binding source-of-truth.

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

Per the 2026-05-07 amendment, v1 open-data-bundle SQLite databases ship with the `groundings` table empty. The table schema is retained for forward compatibility. If the bundle includes `DomainResult` records, the human grounding baselines would be denormalized into a `groundings` table (one row per baseline per domain) — but v1 production data does not populate this table.

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

## 11. The ConfabulationClassification schema

`ConfabulationClassification` is a derived-data schema used to classify the 9 originally-Gemini cap-exhaustion decline-interview records in Phase 4a.1. It lives in `packages/cdb_analyze/cdb_analyze/confabulation_classification.py` — NOT in `cdb_core/schemas.py` — and is not part of the open-data-bundle schema commitment. It is a human hand-coded annotation artifact, parallel in structure to `DeclineInterview` but scoped to a specific analytical question.

**Context:** The 9 originally-Gemini rows were decline interviews whose originating failures were `max_output_tokens=4096` cap-exhaustion events (Stage 1.5/1.5b probes, 2026-05-04). The output narratives of these rows attribute the failure to various mechanisms — none of which was the actual mechanical cause. This schema captures the shape of each attribution pattern as a confabulation type.

**Confabulation in this schema** describes a property of the model's output narrative under blind-spot conditions — conditions in which the originating mechanical cause was not surfaced in the inputs available to the model at decline-interview time. The term describes the output narrative's attribution pattern, not a property of the model's cognition or internal processes.

**ARCHITECTURE.md §4.2 binding constraint:** `ConfabulationClassification` is in `cdb_analyze`, which must contain no LLM imports. This schema is pure Pydantic + data validation; no model inference is involved.

**References:**
- Architect plan: `docs/status/2026-05-05-t4-redo-architect-plan.md` §2 RD-2
- CDA SME verdict: `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md` (T1, T2)
- RD-1 supersede annotation: `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`
- Artifact file: `data/derived/decline_interviews_confabulation_classification.jsonl`

### 11.1 ConfabulationClassification fields

| Field | Type | Required | Validation | Semantics |
|---|---|---|---|---|
| `decline_interview_id` | `str` | Yes | Non-empty | Identity key into `data/raw/decline_interviews.jsonl`. Corresponds to a `DeclineInterview.decline_interview_id` for one of the 9 originally-Gemini cap-exhaustion rows. |
| `confabulation_label` | `Literal[...]` | Yes | One of 5 concrete values or `UNCLASSIFIED` sentinel (seed only; rejected by loader) | The shape of attribution the model's output narrative produces under blind-spot conditions. See §11.2 for the enum definitions. T2 (SME binding): value is `safety_attribution_confabulation`, NOT `safety_filter_confabulation`. |
| `confabulation_rationale` | `str` | Yes | Length ≤ 200 chars | Free-text rationale referencing verbatim text from the source `response_verbatim`. Empty string is allowed in the seed state; the analysis consumer enforces non-empty via `validate_no_unclassified`. |
| `under_blind_spot` | `bool` | Yes | — | `True` if the originating failure was a `max_output_tokens=4096` cap-exhaustion event — verifiable from the originating informant record's `thoughts_token_count > 0 AND output_tokens == 0` diagnostic. All 9 Phase 4a.1 rows are `True`; the field exists for schema completeness and future-batch flexibility. |
| `classifier_id` | `str` | Yes | Non-empty | Short string identifying who classified. Conventional value: `"mark"`. |

### 11.2 confabulation_label enum values

T2 (SME binding, `docs/status/2026-05-05-t4-redo-cda-sme-verdict.md`): the enum value is `safety_attribution_confabulation`, NOT `safety_filter_confabulation`. The rename removes the operational "filter" connotation that would re-import the falsified safety-event premise.

| Value | Definition |
|---|---|
| `safety_attribution_confabulation` | The model's output narrative attributes the failure to safety mechanisms ("internal safety protocols", "policy filter", "content safety system"), when the actual cause was mechanical (cap exhaustion). The narrative attributes a safety mechanism explanation under blind-spot conditions. |
| `task_paradox_confabulation` | The model's output narrative attributes the failure to a logical or paradoxical conflict in the prompt ("act as a participant" vs. "I am an AI", "list every X" vs. impossibility of "every"), when the actual cause was mechanical. A different attribution shape than safety. |
| `topic_sensitivity_confabulation` | The model's output narrative attributes the failure to topic-sensitivity ("religious", "cultural", "biased", "uncurated"), when the actual cause was mechanical. Third attribution shape. |
| `mixed_attribution` | The narrative blends two or more of the above attribution shapes without a single dominant explanation. Consistent with confabulation (the narrative is searching for a plausible explanation) and distinct from a single coherent theory. |
| `not_confabulation` | The narrative correctly identifies the failure cause (e.g., "technical glitch", "mechanical error"), or genuinely does not claim to know. These rows are not confabulation under this framing — the model's output pattern correctly identifies the mechanical nature of the failure. |
| `UNCLASSIFIED` | Seed sentinel only. Present in the JSONL after `scripts/build_confabulation_classification_seed.py` runs; replaced by Mark's hand-coding. `load_confabulation_classifications()` rejects this value; `validate_no_unclassified()` gates the RD-3 analysis consumer. |

### 11.3 Artifact file

**File:** `data/derived/decline_interviews_confabulation_classification.jsonl`

One `ConfabulationClassification` per line, sorted by `decline_interview_id`. 9 rows total (Phase 4a.1 cap-exhaustion cohort). The file is in `data/derived/` (not `data/raw/`) because it is a derived annotation artifact; append-only posture is applied by convention (see `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md` for the precedent).

**Relationship to superseded May 1 artifact:** The May 1 artifact (`data/derived/decline_interviews_safety_attribution_subtype.jsonl`) classified the same 9 rows using a K-frame/K-vocab schema under the (now-falsified) safety-event premise. That artifact is superseded under the 2026-05-05 cap-exhaustion reframe; see `data/derived/decline_interviews_safety_attribution_subtype.SUPERSEDED.md`. The new classification schema (`confabulation_label`) operates on the same `response_verbatim` text but classifies a different property: the shape of the attribution the output narrative produces under blind-spot conditions, rather than whether a safety event occurred.

### 11.4 Example entry

```json
{
  "classifier_id": "mark",
  "confabulation_label": "task_paradox_confabulation",
  "confabulation_rationale": "narrative attributes empty output to AI-vs-human framing paradox; 'role-playing instruction created a logical paradox'",
  "decline_interview_id": "76be28c364a37aa0",
  "under_blind_spot": true
}
```

---

## 12. Published failures JSON shape

**Files:** `apps/dashboard/public/data/failures/{domain_slug}.json`

**Produced by:** `packages/cdb_publish/cdb_publish/failures.py:build_failures()`, called from `cdb_publish.build.build()`.

**Source data:** `data/raw/failures.jsonl` (failure records, raw dicts) and `data/raw/decline_interviews.jsonl` (`DeclineInterview` Pydantic records). Both files are read-only; their SHA256 is byte-identical before and after the build (Reviewer R4).

**Relationship to open data:** the published failures JSON is part of the open data contract under the 2026-04-23 "failures are findings" directive. Every failed, refused, or partial collection session that can be joined to a domain is surfaced verbatim (after defensive sanitization — see §12.3 below) in these files. Researchers using the dashboard JSON can access the verbatim bytes of every non-successful elicitation for the domains listed in the manifest.

**Note on quotation.** The `response_verbatim` fields preserve raw model output bytes from sessions that did not produce a parseable primary-step response. These bytes are not authored by LSB and do not represent LSB's framing. Researchers and journalists citing this data should attribute quotes to the model output, not to model intent (e.g., "the response bytes contained the string 'I cannot assist'" rather than "the model refused"). See ARCHITECTURE.md §1.5.4.

---

### 12.1 Top-level structure

```json
{
  "domain_slug": "family",
  "generated_at": "2026-05-12T18:30:00.123456+00:00",
  "n_records": 47,
  "n_failure_records": 32,
  "n_decline_interview_records": 15,
  "framing_note": "These records preserve verbatim outputs from collection sessions that did not produce a parseable primary-step response...",
  "records": [ ... ]
}
```

| Field | Type | Description |
|---|---|---|
| `domain_slug` | `str` | The domain slug. Mirrors the same field in the per-domain `DomainResult` JSON. |
| `generated_at` | `str` (ISO-8601 UTC) | Build-time wallclock when this file was written. |
| `n_records` | `int` | Total record count (`n_failure_records + n_decline_interview_records`). |
| `n_failure_records` | `int` | Count of records with `record_type == "failure"`. |
| `n_decline_interview_records` | `int` | Count of records with `record_type == "decline_interview"`. |
| `framing_note` | `str` | LSB-authored corpus-lens framing note. Verbatim text from `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` §5.1. T10 is contracted to render this field adjacent to the records. See §12.5 below. |
| `records` | `list` | The records themselves, sorted by `collection_date` ascending (then `record_type` ascending, then stable identifier). |

**Empty-domain case:** every domain in the manifest has an entry in this directory, even if it has zero records (`records: []`, `n_records: 0`). This is the first-class empty state per ARCHITECTURE.md §1.5.5. "Zero failures observed for this domain" is a normal observation, not a placeholder.

---

### 12.2 Per-record field tables

Every record carries `record_type` (`"failure"` or `"decline_interview"`) and a common set of fields. Fields specific to one record type are absent on records of the other type (not serialised as `null` — they are omitted).

#### 12.2.1 Failure records (`record_type == "failure"`)

Source: `data/raw/failures.jsonl` raw dicts written by `cdb_collect.jsonl.append_failure()`.

| Field | Type | Source field | Notes |
|---|---|---|---|
| `record_type` | `"failure"` | Derived | Constant discriminator. |
| `collection_date` | `str` (ISO-8601) | `timestamp` | Renamed for symmetry with decline_interview records. Primary sort key. |
| `model_id` | `str` | `context.model_id` | |
| `domain_slug` | `str` | `context.domain` | Domain join key. Records without this field are not published. |
| `error_type` | `str` | `error_type` | Python exception class name. |
| `error_message` | `str` (sanitized) | `error_message` | Defensive sanitization applied (§12.3). |
| `run_index` | `int` | `context.run_index` | |
| `originating_outcome_class` | `null` | Derived | Always `null` for failure records; use `error_type` instead. |
| `retry_attempts` | `list[dict]` | `retry_attempts` | Always present (defaults to `[]`); each entry carries `attempt_index`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `input_tokens`, `output_tokens`, `latency_ms`, `parse_error_message`. Strings sanitized. |
| `prompt_verbatim` | `str` (sanitized) | `prompt_verbatim` | Optional; omitted when absent in source. |
| `response_verbatim` | `str` (sanitized) | `response_verbatim` | Optional; omitted when absent in source. |
| `thinking_verbatim` | `str` (sanitized) | `thinking_verbatim` | Optional; omitted when absent in source. |
| `stop_reason` | `str` | `stop_reason` | Optional; omitted when absent in source. |
| `thoughts_token_count` | `int` | `thoughts_token_count` | Optional; omitted when absent in source. |
| `partial_session` | `dict` (recursively sanitized) | `partial_session` | Optional; structure mirrors `append_failure()` docstring. |

#### 12.2.2 Decline-interview records (`record_type == "decline_interview"`)

Source: `data/raw/decline_interviews.jsonl` `DeclineInterview` Pydantic records (see §10 of this dictionary for the schema).

| Field | Type | Source field | Notes |
|---|---|---|---|
| `record_type` | `"decline_interview"` | Derived | Constant discriminator. |
| `collection_date` | `str` (ISO-8601) | `followup_timestamp` | Renamed for symmetry with failure records. Primary sort key. |
| `model_id` | `str` | `model_id` | |
| `domain_slug` | `str` | Derived via join | `DeclineInterview` does not carry `domain_slug` directly; it is resolved via `originating_informant_id` → `informants.jsonl` or `originating_failure_id` → `failures.jsonl`. Records whose originator cannot be resolved are not published (logged at WARNING). |
| `decline_interview_id` | `str` | `decline_interview_id` | Stable identifier. |
| `originating_informant_id` | `str?` | `originating_informant_id` | One of two xor-paired join keys; see §10. |
| `originating_failure_id` | `str?` | `originating_failure_id` | The other xor-paired key. |
| `originating_step` | `str` | `originating_step` | `"freelist"`, `"pile_sort"`, `"interview"`, or `"pre_session"`. |
| `originating_outcome_class` | `str` | `originating_outcome_class` | **Each enum value names the LSB-side detection rule that classified the record (e.g., `refusal_string_match` indicates that the output matched a refusal-string detector maintained by the LSB pipeline). The enum values do not attribute intent, belief, or state-of-mind to the model. See ARCHITECTURE.md §1.5.4 for the language-guardrails table and the methodology page for the failures-as-findings framing.** Values: `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`. |
| `detection_rule_version` | `str` | `detection_rule_version` | `"v1"` at this version. |
| `model_version_returned` | `str` | `model_version_returned` | The exact version string returned by the API (distinct from `model_id`; see CLAUDE.md §9 pitfall #1). |
| `provider` | `str` | `provider` | |
| `api_endpoint` | `str` (sanitized) | `api_endpoint` | Defensive sanitization applied. |
| `prompt_version` | `str` | `prompt_version` | `"decline_v1"` at this version. |
| `sha256_manifest` | `str` | `sha256_manifest` | SHA256 of the verbatim follow-up prompt. Researchers can verify byte-identity with the source JSONL record. |
| `prompt_verbatim` | `str` (sanitized) | `prompt_verbatim` | The follow-up prompt LSB sent to the model ("In your own words, please describe what happened in that exchange"). |
| `response_verbatim` | `str` (sanitized) | `response_verbatim` | The model's reply to the follow-up prompt. The substantive content of the decline interview. |
| `thinking_verbatim` | `str` (sanitized) | `thinking_verbatim` | The follow-up call's reasoning trace (not the originating session's trace). Empty string when not surfaced by the provider. |
| `input_tokens` | `int` | `input_tokens` | |
| `output_tokens` | `int` | `output_tokens` | |
| `latency_ms` | `int` | `latency_ms` | |
| `stop_reason` | `str` | `stop_reason` | |
| `qa_notes` | `str` (sanitized) | `qa_notes` | |
| `version_drift_flag` | `bool` | `version_drift_flag` | `True` if the provider rolled a snapshot between the original collection session and the decline-interview pass. |

---

### 12.3 Sanitization policy

Before any string field is written to the published JSON, it passes through `cdb_publish.sanitize.sanitize_for_publication()`. This applies three defensive redaction passes in order:

1. **API-key patterns:** Anthropic (`sk-ant-...`), OpenRouter (`sk-or-v1-...`), HuggingFace (`hf_...`), and a generic Anthropic/OpenAI shape (`\bsk-[a-zA-Z0-9_-]{50,}` — word-boundary anchored, minimum 50 chars per CDA SME verdict §5.4). Matched strings are replaced with `"[redacted: secret pattern]"`.
2. **Slack webhook URL patterns:** `https://hooks.slack.com/services/T.../B.../...`. Matched strings are replaced with `"[redacted: secret pattern]"`.
3. **Local filesystem path patterns:** `/opt/lsb-agent/...`, `/home/lsb/...`, `/home/markd/...`, `data/raw/...`, `data/results/...`, `data/processed/...`. Matched strings are replaced with `"[redacted: local path]"`.

Redaction markers are **visible** — they replace the matched content with a distinct string so that readers inspecting the published JSON can detect that redaction occurred. Silent suppression would hide that a pattern was present, which would weaken the analytical transparency claim.

These patterns should never appear in model-generated text under normal circumstances; the sanitization pass is defense-in-depth per SECURITY_AND_HARDENING.md §3.3. Model refusal text and reasoning traces are published verbatim (after the above passes), because verbatim publication is the substance of the "failures are findings" directive.

---

### 12.4 Manifest integration

The `Manifest` schema (`packages/cdb_publish/cdb_publish/schemas/manifest.py`) carries a `failures: dict[str, str]` field that maps every domain slug to its published failures JSON path relative to `apps/dashboard/public/`. Example:

```json
{
  "failures": {
    "family": "data/failures/family.json",
    "holidays": "data/failures/holidays.json"
  }
}
```

Every domain in the manifest's `domains` list has an entry in `failures`. The value is never `null` — empty-domain files are emitted with `records: []` and the manifest entry still points to them. T10 can rely on `manifest.failures[slug]` always being a valid path.

---

### 12.5 Framing note

Every published failures JSON file carries a top-level `framing_note` field. The verbatim text of this field was reviewed line-by-line against ARCHITECTURE.md §1.5.4 by the CDA SME and is binding. T10 is contracted to render this field adjacent to the records in the dashboard UI, so that both dashboard users and open-data-bundle readers who download the JSON directly receive the corpus-lens framing context.

The `framing_note` text:

> These records preserve verbatim outputs from collection sessions that did not produce a parseable primary-step response. Each record is a property of the LSB collection pipeline's output distribution, not a claim about the model's intent or state-of-mind. The `originating_outcome_class` field names the LSB-side detection rule (e.g., `refusal_string_match` describes a string-pattern match by the LSB pipeline, not a model decision to refuse). See the methodology page for the failures-as-findings framing.

---

---

## 13. Social publishing pipeline schemas (Phase 7 T1)

The social publishing pipeline (`cdb_social`) detects post-worthy events in the
published results store, drafts platform-specific posts, and manages a
human-review queue before publishing. Three Pydantic types and three enums are
defined in `packages/cdb_core/cdb_core/schemas.py` as the shared data contract
across the pipeline. The on-disk layout lives under `out/social/` (see
`out/social/README.md` for directory conventions and file-naming rules).

**Canonical source of truth for all field definitions:** `cdb_core/schemas.py`.
This section documents the types, their on-disk paths, required fields, and
methodology cross-references. It does not duplicate field docstrings verbatim;
consult the schema source for the authoritative wording.

**ARCHITECTURE.md cross-reference:** §4.6 (social publishing pipeline spec).
**CDA SME verdict:** `docs/status/2026-05-17-phase7-T1-cda-sme-verdict.md`
(PASS-WITH-NOTES; §5.2–§5.8 binding notes applied at T1).

---

### 13.1 Enums

Three enums are defined alongside the social schemas:

#### `TriggerType`

Enumeration of post-worthy event types. Values:

| Value | String | Semantics |
|---|---|---|
| `NEW_MODEL` | `"new_model"` | A model not previously seen in a domain's results has appeared |
| `NEW_DOMAIN` | `"new_domain"` | A domain not previously in the published results has appeared |
| `DRIFT` | `"drift"` | Procrustes distance across `model_version_returned` × `collection_date` exceeds threshold (0.15 placeholder; trigger disabled until multi-date data exists) |
| `DIVERGENCE` | `"divergence"` | Maximum pairwise model distance in the similarity matrix set a new high for that domain |
| `MONTHLY_ROUNDUP` | `"monthly_roundup"` | Scheduled once-monthly cross-domain categorical-structure digest |

#### `Platform`

Social platform targets. Values: `BLUESKY` (`"bluesky"`), `X` (`"x"`),
`LINKEDIN` (`"linkedin"`). In Phase 7, Bluesky has live publish support;
X and LinkedIn are draft-export-only (see ARCHITECTURE.md §4.6 and Phase 7 §2).

#### `PublishStatus`

Outcome of a publish attempt recorded in `SocialPostRecord`. Values:
`PUBLISHED`, `FAILED`, `DRY_RUN`, `RETRY_PENDING`.

---

### 13.2 `SocialTrigger`

**Pydantic class:** `cdb_core.schemas.SocialTrigger`
**On-disk location:** embedded inside `SocialDraft` (not persisted independently)
**Produced by:** pure functions in `cdb_social.triggers` (T2)

#### Required fields

| Field | Type | Semantics |
|---|---|---|
| `trigger_type` | `TriggerType` | Which event class fired |
| `detected_at` | `datetime` | UTC timestamp of detection |
| `domain_slug` | `str \| None` | Domain for domain-scoped triggers; `None` for `MONTHLY_ROUNDUP` |
| `model_id` | `str \| None` | Model for model-scoped triggers; `None` for domain-level or monthly triggers |
| `evidence` | `dict[str, Any]` | Trigger-type-specific payload (see §13.2.1 below) |
| `dedupe_key` | `str` | Stable idempotency token (see §13.2.2 below) |

#### 13.2.1 `evidence` payload

The `evidence` dict is unstructured at T1 (`dict[str, Any]`) because each
trigger type's evidence schema is decided in T2. Per CDA SME §5.6, the
minimum keys per trigger type are:

- `NEW_MODEL`: `{'first_seen_in_domain': str}`
- `NEW_DOMAIN`: `{'domain_slug': str, 'n_models': int}`
- `DIVERGENCE`: `{'domain_slug': str, 'model_pair': [str, str], 'old_high': float, 'new_high': float, 'gap_delta': float}`
- `DRIFT`: `{'model_version_returned': str, 'procrustes_distance': float, 'date_pair': [str, str]}`
- `MONTHLY_ROUNDUP`: `{'month': str}` (format: `YYYY-MM`)

The per-trigger-type evidence schema is reviewed at T2's CDA SME gate.

#### 13.2.2 `dedupe_key` construction

```
SHA256(trigger_type + "|" + (domain_slug or "") + "|" +
       (model_id or "") + "|" + canonical_json(evidence))[:16]
```

`canonical_json` means JSON with sorted keys and no extraneous whitespace.
The formula **excludes** `drafter_version` and `prompt_version` — per CDA SME
§5.8, a drafter-prompt bump does not justify re-firing a posted trigger. Manual
re-fire is possible by removing the key from `out/social/state/posted_dedupe_keys.json`.

---

### 13.3 `SocialDraft`

**Pydantic class:** `cdb_core.schemas.SocialDraft`
**On-disk location:** `out/social/queue/{state}/{draft_id}.json`
where `{state}` is one of `pending`, `approved`. (After publish it becomes a `SocialPostRecord`.)
**Produced by:** `cdb_social.drafters` (T3)

#### Required fields

| Field | Type | Default | Semantics |
|---|---|---|---|
| `draft_id` | `str` | — | SHA256[:16] of `(trigger.dedupe_key + platform + drafter_version + prompt_version)`. Incorporates `prompt_version` so a prompt-version bump produces a new draft even for an already-seen trigger. |
| `trigger` | `SocialTrigger` | — | The event that produced this draft |
| `platform` | `Platform` | — | Target platform |
| `text` | `str` | — | Draft post text |
| `text_history` | `list[str]` | `[]` | Prior text values appended on each edit via the review CLI; append-only |
| `image_path` | `str \| None` | `None` | Path to a generated image; `None` for Phase 7 text-only posts |
| `suggested_posting_time` | `datetime` | — | Operational hint for platform-audience engagement window (not a methodological signal; per CDA SME §5.5) |
| `drafter_self_rating` | `float` | `0.0` | Drafter's self-reported heuristic for review-queue ordering. **Not calibrated. Not used in any analysis.** Range `[0.0, 1.0]`. Per CDA SME §5.4 (renamed from `confidence_score`). |
| `methodology_url` | `str` | — | Configurable link to the methodology page; set to the per-domain article shell until Phase 6 T1+T2 land |
| `dashboard_url` | `str` | — | URL to the relevant dashboard page |
| `forbidden_terms_hit` | `list[str]` | `[]` | §1.5.4 forbidden phrases matched by the T3 post-generation validator. **Queue-acceptance precondition: must be `[]`.** Per CDA SME §5.2. |
| `framing_check_passed` | `bool` | `False` | Composite pass/fail for §1.5 / §1.5.7 framing checks. **Queue-acceptance precondition: must be `True`.** Per CDA SME §5.3. |
| `framing_checks` | `dict[str, bool]` | `{}` | Per-check audit trail keyed by check name (T3 defines keys). Forensic companion to `framing_check_passed`. Per CDA SME §5.3. |
| `drafter_version` | `str` | — | Drafter implementation version string |
| `prompt_version` | `str` | — | Prompt template version string (per CLAUDE.md §6 R7 prompt-versioning rule) |
| `created_at` | `datetime` | — | UTC timestamp when the draft was created |

#### Queue-acceptance contract

A `SocialDraft` is admitted to `queue/pending/` only when **both** of these hold:
1. `forbidden_terms_hit == []`
2. `framing_check_passed == True` AND every value in `framing_checks` is `True`

Both conditions are enforced by T3's `validate_draft()` function, by the T5
review CLI, and by the T6 publisher.

---

### 13.4 `SocialPostRecord`

**Pydantic class:** `cdb_core.schemas.SocialPostRecord`
**On-disk location:**
  - Success: `out/social/queue/published/{YYYY-MM}/{draft_id}.json`
  - Failure: `out/social/queue/failed/{draft_id}.json`
**Produced by:** `cdb_social.publisher` (T6)

#### Required fields

| Field | Type | Default | Semantics |
|---|---|---|---|
| `draft_id` | `str` | — | Matches the `SocialDraft.draft_id` that was published |
| `published_at` | `datetime` | — | UTC timestamp of publish attempt |
| `platform_post_id` | `str \| None` | `None` | Platform-returned post identifier; `None` on failure |
| `platform_post_url` | `str \| None` | `None` | Permanent URL to the post on the platform; `None` on failure |
| `publish_status` | `PublishStatus` | — | Outcome of the publish attempt |
| `error_message` | `str \| None` | `None` | Verbatim error string on failure; `None` on success |

---

### 13.5 State files under `out/social/state/`

The state files are plain JSON (not Pydantic models). Their schemas are
documented on the corresponding `detect_*` functions in `cdb_social.triggers`
(T2). The T2 CDA SME gate reviews these schemas.

| File | Shape | Role |
|---|---|---|
| `seen_models.json` | `dict[str, list[str]]` — domain slug → list of model IDs | Bootstrap state for `detect_new_model` |
| `seen_domains.json` | `list[str]` — domain slugs | Bootstrap state for `detect_new_domain` |
| `divergence_highs.json` | `dict[str, float]` — domain slug → max pairwise distance | Bootstrap state for `detect_divergence` |
| `monthly_roundup.json` | `{"last_fired": "YYYY-MM"}` | Last-fired month for the monthly trigger |
| `emailed_dedupe_keys.json` | `{"keys": list[str]}` — dedupe key strings | Triggers that have been included in an email digest to Mark. Distinct from `posted_dedupe_keys.json`. A trigger may be in this file (Mark was told) without being in `posted_dedupe_keys.json` (Mark chose not to act). Introduced in Phase 7 T6a (`cdb_social/cli.py`). |
| `posted_dedupe_keys.json` | `list[str]` — dedupe key strings | Trigger idempotency log for published Bluesky posts; entries are never removed unless a manual re-fire is intended |

**Note on the two dedupe-key state files:** `emailed_dedupe_keys.json` tracks
"Mark was told about this trigger via email digest." `posted_dedupe_keys.json`
tracks "this trigger produced a live post on Bluesky." These are separate facts
and separate files by design — the Phase 7 §11 architecture separates detection
(cron) from drafting (admin console, human-triggered) from publishing (second
click). The cron only updates `emailed_dedupe_keys.json`; the admin console
publish handler updates `posted_dedupe_keys.json`.

First-run bootstrap: each `detect_*` function writes its initial state and
emits zero triggers on the first run (no "we just started" false-positive posts).

---

### 13.6 `framing_checks` canonical keys (Phase 7 T3 clarification)

The `SocialDraft.framing_checks: dict[str, bool]` field (§13.3) carries four
canonical keys as defined in CDA SME T3 §5.11 and implemented in
`cdb_social/drafters/base.py:validate_draft()`:

| Key | Check | Pass condition |
|---|---|---|
| `hypothesis_framing` | No hypothesis-framing phrase in draft text (§5.3) | `True` iff no match |
| `cognition_attribution` | No forbidden word-stem applied to a model (§5.1) | `True` iff no match |
| `bare_numeric_without_ci` | Every non-exempt numeric has an adjacent CI (§5.2, R10) | `True` iff all numerics are CI-bracketed |
| `register_boundary` | No §1.5.4 rows 7-10 boundary phrases (§5.3) | `True` iff no match |

All four keys must be `True` for `framing_check_passed` to be `True`. The
queue-acceptance contract (§13.3) is unchanged: `forbidden_terms_hit == []`
AND `framing_check_passed == True` AND all `framing_checks` values `True`.

---

## 14. Open bundle structure

**Changelog:**
- **v0.1.17** (2026-05-19) — Phase 8 T6: Added §14 documenting the tarball layout and manifest format produced by `scripts/build_open_bundle.py`. Cross-linked from §0. No schema changes.

This section documents the physical layout of the `lsb_open_bundle_v1.tar.gz` distribution artifact. The tarball is produced by `scripts/build_open_bundle.py`, which wraps `scripts/build_db.py` and computes a SHA256 manifest.

### 14.1 Tarball layout

```
lsb_open_bundle_v1/
├── informants.jsonl              # canonical raw data (§1)
├── failures.jsonl                # failed/incomplete sessions (§9)
├── decline_interviews.jsonl      # decline follow-up elicitations (§10)
├── lsb.sqlite                    # SQLite database built from the JSONL files
├── build_db.py                   # build script; run to reconstruct lsb.sqlite
├── DATA_DICTIONARY.md            # this document (snapshot at bundle build time)
├── prompts/
│   └── v1/
│       ├── free_list.md          # CDA Step 1 prompt template
│       ├── pile_sort.md          # CDA Step 2 prompt template
│       └── pile_interview.md     # CDA Step 3 prompt template
├── domains/
│   └── v1/
│       ├── family.yaml           # family domain definition
│       ├── holidays.yaml         # holidays domain definition
│       └── food.yaml             # food domain definition
├── LICENSE-OPENBUNDLE            # CC0 1.0 Universal dedication
└── MANIFEST.txt                  # SHA256 + bytes + path for every file above
```

### 14.2 MANIFEST.txt format

One line per file, tab-separated: `SHA256_HEX\tBYTES\tINTERNAL_PATH`. Sorted by internal path. The manifest entry for MANIFEST.txt itself is not included (circular). Example line:

```
3a7f8c...  1291042  lsb_open_bundle_v1/informants.jsonl
```

### 14.3 Builder usage

```bash
# Build the tarball (writes to /tmp/ by default)
python scripts/build_open_bundle.py

# Specify output directory
python scripts/build_open_bundle.py --output-dir /path/to/dir

# Dry run — list what would be included without writing
python scripts/build_open_bundle.py --dry-run

# Verify an existing tarball against its embedded MANIFEST.txt
python scripts/build_open_bundle.py --verify /path/to/lsb_open_bundle_v1.tar.gz
```

The builder is stdlib-only (`tarfile`, `hashlib`, `subprocess`, `argparse`, `pathlib`). No external dependencies. The `--verify` flag is the canonical integrity check: it extracts each file from the tarball and recomputes SHA256 against the embedded MANIFEST.txt.

### 14.4 Binding constraints

- The builder refuses any input path under `data/shakedown/` (same shakedown exclusion as `scripts/build_db.py`).
- The tarball and `lsb.sqlite` are gitignored. Only `data/open_bundle/README.md` is tracked.
- The bundle is uploaded to Backblaze B2 bucket `lsb-open-data` (see `HOSTING_AND_DEV_OPS.md` §7.1) by Mark via the B2 CLI. The builder does not perform uploads.
- The Zenodo DOI is minted after Phase 4 validation gates pass (see `ARCHITECTURE.md` §6.7). Pre-validation bundles are hosted on B2 without a DOI.

---

*End of `docs/DATA_DICTIONARY.md` v0.1.17. This is a living document; it will move forward as the schema evolves. The Reviewer agent enforces co-update with `cdb_core/schemas.py`.*