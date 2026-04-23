"""Collection orchestrator — runs the CDA protocol for a (model, domain) pair.

Supports three collection modes:
- single_pass: each run generates and sorts its own items (end-to-end model behavior)
- two_pass: free lists first → consensus item list → pile sorts on consensus items
- baseline_items: pile sorts on a provided human baseline item list

See ARCHITECTURE.md §4.1.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Literal

from cdb_core import Domain, FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

from cdb_collect.adapters.base import AdapterResult, ModelAdapter
from cdb_collect.adapters.openai_compat import PROVIDER_CONFIGS
from cdb_collect.exceptions import PartialSessionError, PileSortParseError
from cdb_collect.manifest import compute_manifest
from cdb_collect.protocol.free_list import run_free_list
from cdb_collect.protocol.pile_interview import run_pile_interview
from cdb_collect.protocol.pile_sort import run_pile_sort

# Stop reasons (raw strings from providers) that signal a context-window cap.
# Each entry is the exact string stored in AdapterResult.stop_reason:
#   - Anthropic Messages API:  "max_tokens"
#   - OpenAI / xAI / DeepSeek / Mistral (chat completions): "length"
#   - OpenRouter (proxies OpenAI format):  "length"
#   - HuggingFace Inference Providers (OpenAI-compat):  "length"
#   - Google Gemini (FinishReason enum .name): "MAX_TOKENS"
_CONTEXT_WINDOW_STOP_REASONS: frozenset[str] = frozenset({
    "max_tokens",   # Anthropic
    "length",       # OpenAI-compat, OpenRouter, HuggingFace, xAI, DeepSeek, Mistral
    "MAX_TOKENS",   # Google Gemini (FinishReason enum name)
})


def _is_context_window_exceeded(stop_reason: str) -> bool:
    """Return True when the provider stop reason indicates a context-window cap."""
    return stop_reason in _CONTEXT_WINDOW_STOP_REASONS

logger = logging.getLogger(__name__)


_ENDPOINT_MAP: dict[str, str] = {
    "anthropic_api": "https://api.anthropic.com/v1/messages",
    "google_ai": "https://generativelanguage.googleapis.com/v1beta/models",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "huggingface": "https://router.huggingface.co/v1/chat/completions",
}
# Merge OpenAI-compatible provider endpoints
for _method, _cfg in PROVIDER_CONFIGS.items():
    _ENDPOINT_MAP[_method] = _cfg["base_url"]


def _resolve_endpoint(collection_method: str) -> str:
    """Return the API endpoint URL for a given collection method."""
    return _ENDPOINT_MAP.get(collection_method, collection_method)


def _informant_id(
    model_id: str, domain_slug: str, run_index: int, collection_date: str,
) -> str:
    """Deterministic informant ID: SHA256[:16] of the identity tuple."""
    key = f"{model_id}|{domain_slug}|{run_index}|{collection_date}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _placeholder_freelist() -> tuple[FreelistRecord, AdapterResult]:
    """Placeholder for two-pass/baseline modes where free list is not run."""
    record = FreelistRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_items=[],
        parsed_raw_order=[],
    )
    result = AdapterResult(
        text="", raw_response={}, latency_ms=0, cost_usd=0.0,
        input_tokens=0, output_tokens=0, provider_request_id="",
        model_version_returned="", stop_reason="not_collected",
    )
    return record, result


def _assemble_record(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    freelist_record: FreelistRecord,
    freelist_result: AdapterResult,
    pilesort_record: PileSortRecord,
    interview_record: InterviewRecord,
    collection_mode: Literal["single_pass", "two_pass", "baseline_items", "cross_model_consensus"],
    prompt_version: str = "v1",
    system_prompt: str = "",
    *,
    temperature: float | None = None,
    campaign_id: str | None = None,
    truncation_type: Literal[
        "elbow", "capacity", "prompt_ceiling", "context_window_exceeded",
    ] | None = None,
    truncation_n: int | None = None,
) -> InformantRecord:
    """Assemble an InformantRecord from step records.

    Args:
        temperature: When set, overrides the default per-step temperatures
            (free_list 0.7, pile_sort 0.3, interview 0.3 per §4.1.3) and
            the single value is recorded in both ``request_params`` and
            the top-level ``InformantRecord.temperature`` field. Used by
            the shakedown determinism cell (``--temperature 0.0``).
        campaign_id: When set, written verbatim into ``qa_notes`` as
            ``campaign_id=<value>`` at construction time. Used by the
            pre-Phase-4a shakedown protocol (§2 four-layer non-canonical
            labeling). Null for canonical Phase 4a runs.
    """
    now = datetime.now()
    collection_date_str = now.strftime("%Y-%m-%dT%H:%M:%S")

    # When a temperature override is provided, all three steps used the
    # same value. When None, each step used its per-step default from
    # ARCHITECTURE.md §4.1.3. Record both so the request_params remain
    # auditable either way.
    if temperature is not None:
        temp_freelist = temperature
        temp_pilesort = temperature
        temp_interview = temperature
        record_temperature = temperature
    else:
        temp_freelist = 0.7
        temp_pilesort = 0.3
        temp_interview = 0.3
        record_temperature = 0.7  # the dominant step's temp

    request_params = {
        "model_id": adapter.model.model_id,
        "domain_slug": domain.slug,
        "run_index": run_index,
        "prompt_version": prompt_version,
        "collection_mode": collection_mode,
        "temperature_freelist": temp_freelist,
        "temperature_pilesort": temp_pilesort,
        "temperature_interview": temp_interview,
    }

    manifest = compute_manifest(
        freelist_prompt=freelist_record.prompt_verbatim,
        freelist_response=freelist_record.response_verbatim,
        pilesort_prompt=pilesort_record.prompt_verbatim,
        pilesort_response=pilesort_record.response_verbatim,
        interview_prompt=interview_record.prompt_verbatim,
        interview_response=interview_record.response_verbatim,
        request_params=request_params,
    )

    informant_id = _informant_id(
        adapter.model.model_id, domain.slug, run_index, collection_date_str,
    )

    # Use freelist result for model version when available, fall back to model_id
    model_version = freelist_result.model_version_returned
    provider_req_id = freelist_result.provider_request_id
    if not model_version:
        model_version = adapter.model.model_id
    if not provider_req_id:
        provider_req_id = f"two_pass_{run_index}"

    campaign_id_tag = f"campaign_id={campaign_id}" if campaign_id else ""

    # Detect context-window overflow across all three CDA steps.
    # A step's stop_reason of "not_collected" means the step was a placeholder
    # (skipped in two_pass / baseline_items modes) and must not trigger the flag.
    cwe_freelist = _is_context_window_exceeded(freelist_record.stop_reason)
    cwe_pilesort = _is_context_window_exceeded(pilesort_record.stop_reason)
    cwe_interview = _is_context_window_exceeded(interview_record.stop_reason)
    cwe_any = cwe_freelist or cwe_pilesort or cwe_interview

    # Build capacity_note when context window was hit.
    if cwe_any:
        steps_hit = [
            name for name, flag in (
                ("freelist", cwe_freelist),
                ("pile_sort", cwe_pilesort),
                ("interview", cwe_interview),
            )
            if flag
        ]
        capacity_note_value = "context window exceeded at step(s): " + ", ".join(steps_hit)
    else:
        capacity_note_value = ""

    # context_window_exceeded on the freelist overrides the caller-supplied
    # truncation_type, because the provider cut the response short before the
    # model finished listing — the elbow / capacity label is no longer correct.
    resolved_truncation_type = truncation_type
    if cwe_freelist:
        resolved_truncation_type = "context_window_exceeded"

    # truncation_n: number of items kept after whatever truncation was applied.
    # Use the passed value if provided; otherwise derive from parsed_items length.
    resolved_truncation_n = truncation_n if truncation_n is not None else (
        len(freelist_record.parsed_items) if freelist_record.parsed_items else None
    )

    # Build the record with qa_passed=True initially so run_qa_checks can
    # inspect the fully-assembled record (check_8 reads parsed_piles and
    # parsed_pile_labels from the step sub-records).
    record = InformantRecord(
        informant_id=informant_id,
        domain_slug=domain.slug,
        run_index=run_index,
        collection_date=now,
        model_id=adapter.model.model_id,
        model_version_returned=model_version,
        family=adapter.model.family,
        provider=adapter.model.provider,
        provider_request_id=provider_req_id,
        knowledge_cutoff=None,
        open_weights=adapter.model.open_weights,
        origin_country=adapter.model.origin,
        alignment_method=None,
        collection_method=adapter.model.collection_method,
        collection_mode=collection_mode,
        api_endpoint=_resolve_endpoint(adapter.model.collection_method),
        api_version="",
        temperature=record_temperature,
        top_p=None,
        max_tokens=4096,  # see docs/status/2026-04-22-phase4a-adapter-fix-verdict.md
        system_prompt=system_prompt,
        freelist=freelist_record,
        pile_sort=pilesort_record,
        interview=interview_record,
        truncation_type=resolved_truncation_type,
        truncation_n=resolved_truncation_n,
        context_window_exceeded=cwe_any,
        capacity_note=capacity_note_value,
        sha256_manifest=manifest,
        qa_passed=True,      # will be overwritten below
        qa_notes="",         # will be overwritten below
    )

    # Run QA checks on the assembled record and wire the result back.
    # Function-scope import mirrors the pattern used in run_two_pass for
    # cdb_analyze. This is ADDITIVE to the post-collection CLI sweep in
    # scripts/qa_check.py main() — that sweep remains useful for
    # re-checking records written by older runner versions or for manual
    # inspection passes.
    #
    # scripts/ is a package (has __init__.py) but is only on sys.path in
    # pytest runs (pyproject.toml pythonpath=["."]). When cdb_collect is
    # invoked by scripts/collect.py at runtime, scripts/ sibling dir is
    # not automatically on sys.path — add the project root defensively so
    # the function-level import resolves either way. Proper fix: move
    # run_qa_checks into cdb_collect.qa; deferred per CLAUDE.md §8 no-
    # scope-creep. See the F2-T10 re-shakedown surfacing.
    try:
        from scripts.qa_check import run_qa_checks  # noqa: PLC0415
    except ModuleNotFoundError:
        import sys as _sys  # noqa: PLC0415
        from pathlib import Path as _Path  # noqa: PLC0415
        _project_root = str(_Path(__file__).resolve().parents[3])
        if _project_root not in _sys.path:
            _sys.path.insert(0, _project_root)
        from scripts.qa_check import run_qa_checks  # noqa: PLC0415
    failures = run_qa_checks(record)
    qa_passed = len(failures) == 0

    failure_notes = "; ".join(f.actual for f in failures) if failures else ""
    qa_notes_parts = [p for p in (failure_notes, campaign_id_tag) if p]
    qa_notes_value = "; ".join(qa_notes_parts)

    return record.model_copy(update={
        "qa_passed": qa_passed,
        "qa_notes": qa_notes_value,
    })


async def run_informant(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
    temperature: float | None = None,
    campaign_id: str | None = None,
) -> InformantRecord:
    """Run the full single-pass CDA protocol and assemble an InformantRecord.

    Each run generates its own free list, sorts its own items, and names
    its own piles. This captures end-to-end model behavior.

    Args:
        temperature: Optional single temperature used for all three CDA
            steps. When None, the per-step defaults from
            ARCHITECTURE.md §4.1.3 are used (0.7 / 0.3 / 0.3).
        campaign_id: Optional campaign identifier written into
            ``qa_notes`` per docs/SHAKEDOWN_PROTOCOL.md §2.
    """
    # ── Step 1: Free list ──────────────────────────────────────────────────
    try:
        freelist_record, freelist_result = await run_free_list(
            adapter, domain, run_index,
            prompt_version=prompt_version,
            temperature=temperature,
        )
    except Exception as exc:
        raise PartialSessionError(
            cause=exc,
            failed_step="freelist",
            partial_session={},
            # No completed steps to carry; prompt was built inside run_free_list
        ) from exc

    partial: dict = {"freelist": freelist_record.model_dump()}

    # ── Step 2: Pile sort ──────────────────────────────────────────────────
    try:
        pilesort_record, _ = await run_pile_sort(
            adapter,
            items=freelist_record.parsed_items,
            domain_seed=domain.prompt_seed,
            run_index=run_index,
            prompt_version=prompt_version,
            temperature=temperature,
        )
    except PileSortParseError as exc:
        # All retries exhausted — map attempts[:-1] to retry_attempts,
        # and attempts[-1] to top-level verbatim fields.
        attempts = exc.attempts
        errors = exc.per_attempt_errors
        retry_attempts: list[dict] = [
            {
                "attempt_index": idx,
                "response_verbatim": r.text,
                "thinking_verbatim": r.thinking_text,
                "stop_reason": r.stop_reason,
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "latency_ms": r.latency_ms,
                "parse_error_message": str(errors[idx]),
            }
            for idx, r in enumerate(attempts[:-1])
        ]
        final = attempts[-1]
        raise PartialSessionError(
            cause=exc,
            failed_step="pile_sort",
            partial_session=partial,
            prompt_verbatim=exc.prompt_verbatim or None,
            response_verbatim=final.text,
            thinking_verbatim=final.thinking_text,
            stop_reason=final.stop_reason,
            retry_attempts=retry_attempts,
        ) from exc
    except Exception as exc:
        raise PartialSessionError(
            cause=exc,
            failed_step="pile_sort",
            partial_session=partial,
        ) from exc

    partial["pile_sort"] = pilesort_record.model_dump()

    # ── Step 3: Pile interview ─────────────────────────────────────────────
    try:
        interview_record, _ = await run_pile_interview(
            adapter,
            piles=pilesort_record.parsed_piles,
            run_index=run_index,
            prompt_version=prompt_version,
            temperature=temperature,
        )
    except Exception as exc:
        raise PartialSessionError(
            cause=exc,
            failed_step="interview",
            partial_session=partial,
        ) from exc

    return _assemble_record(
        adapter, domain, run_index,
        freelist_record, freelist_result,
        pilesort_record, interview_record,
        collection_mode="single_pass",
        prompt_version=prompt_version,
        system_prompt=system_prompt,
        temperature=temperature,
        campaign_id=campaign_id,
    )


async def run_two_pass(
    adapter: ModelAdapter,
    domain: Domain,
    n_free_lists: int = 10,
    n_pile_sorts: int = 10,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
) -> list[InformantRecord]:
    """Run two-pass CDA protocol: free lists → consensus → pile sorts.

    Pass 1: Collect n_free_lists free lists to build a consensus item list.
    Pass 2: Run n_pile_sorts pile sort + interview calls using the consensus items.

    This is the standard CDA methodology (Borgatti): all pile sorts use the
    same item list, enabling clean cross-run aggregation.

    Returns:
        List of InformantRecords (n_free_lists + n_pile_sorts total).
        Free-list-only records have collection_mode="two_pass" and placeholder
        pile sort/interview. Pile sort records have the consensus items.
    """
    from cdb_analyze.consensus import compute_consensus_free_list, find_salience_elbow

    # ── Pass 1: Collect free lists ──────────────────────────────────
    freelist_records: list[tuple[FreelistRecord, AdapterResult]] = []
    all_informant_records: list[InformantRecord] = []

    for i in range(n_free_lists):
        fl_record, fl_result = await run_free_list(
            adapter, domain, i, prompt_version=prompt_version,
        )
        freelist_records.append((fl_record, fl_result))

        # Create a free-list-only InformantRecord for provenance.
        # truncation_type is left None here — it will be retroactively set to
        # "elbow" (or kept as "context_window_exceeded" if the freelist hit the
        # context window) after find_salience_elbow() is computed below.
        placeholder_ps = PileSortRecord(
            prompt_verbatim="", prompt_version=prompt_version,
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="not_collected",
            parsed_piles=[], parsed_matrix=[],
            item_source="own_freelist",
        )
        placeholder_iv = InterviewRecord(
            prompt_verbatim="", prompt_version=prompt_version,
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="not_collected",
            parsed_pile_labels=[],
        )

        record = _assemble_record(
            adapter, domain, i,
            fl_record, fl_result,
            placeholder_ps, placeholder_iv,
            collection_mode="two_pass",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )
        all_informant_records.append(record)

    # ── Compute consensus item list ─────────────────────────────────
    consensus = compute_consensus_free_list(all_informant_records)
    elbow_k = find_salience_elbow(consensus)
    consensus_items = [item for item, _ in consensus[:elbow_k]]

    item_source = f"consensus:{adapter.model.model_id}"
    logger.info(
        "Consensus free list: %d items (from %d free lists, elbow at %d by Smith's S)",
        len(consensus_items), n_free_lists, elbow_k,
    )

    # Retroactively stamp truncation_type on the freelist-only records.
    # If _assemble_record already set "context_window_exceeded" (because the
    # freelist step hit the context window), preserve that. Otherwise, apply
    # "elbow" now that we know the elbow k.
    stamped_freelist_records: list[InformantRecord] = []
    for rec in all_informant_records:
        if rec.truncation_type != "context_window_exceeded":
            rec = rec.model_copy(update={
                "truncation_type": "elbow",
                "truncation_n": elbow_k,
            })
        stamped_freelist_records.append(rec)

    # ── Pass 2: Pile sorts on consensus items ───────────────────────
    # Deviation from Architect Amendment A §Stream A brief (2026-04-23):
    # the per-iteration handler stops on first failure rather than
    # continuing to the next iteration. Continue-after-failure would
    # require a return-type change or failure-callback parameter and was
    # deferred. Verbatim is still preserved on the failure via
    # PartialSessionError (strictly better than the pre-fix behavior
    # where a single failure lost all verbatim). Continue-after-failure
    # is tracked as a follow-up for Architect ruling. See
    # docs/status/2026-04-23-phase4a-task23-reviewer-verdict.md Note 1.
    pile_sort_records: list[InformantRecord] = []
    for i in range(n_pile_sorts):
        run_idx = n_free_lists + i  # Offset to avoid ID collision

        try:
            pilesort_record, ps_result = await run_pile_sort(
                adapter,
                items=consensus_items,
                domain_seed=domain.prompt_seed,
                run_index=run_idx,
                prompt_version=prompt_version,
            )
        except PileSortParseError as exc:
            attempts = exc.attempts
            errors = exc.per_attempt_errors
            retry_attempts: list[dict] = [
                {
                    "attempt_index": idx,
                    "response_verbatim": r.text,
                    "thinking_verbatim": r.thinking_text,
                    "stop_reason": r.stop_reason,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "latency_ms": r.latency_ms,
                    "parse_error_message": str(errors[idx]),
                }
                for idx, r in enumerate(attempts[:-1])
            ]
            final = attempts[-1]
            raise PartialSessionError(
                cause=exc,
                failed_step="pile_sort",
                partial_session={},
                prompt_verbatim=exc.prompt_verbatim or None,
                response_verbatim=final.text,
                thinking_verbatim=final.thinking_text,
                stop_reason=final.stop_reason,
                retry_attempts=retry_attempts,
            ) from exc
        except Exception as exc:
            raise PartialSessionError(
                cause=exc,
                failed_step="pile_sort",
                partial_session={},
            ) from exc

        # Set item_source on the pile sort record
        pilesort_record = pilesort_record.model_copy(
            update={"item_source": item_source},
        )

        try:
            interview_record, _ = await run_pile_interview(
                adapter,
                piles=pilesort_record.parsed_piles,
                run_index=run_idx,
                prompt_version=prompt_version,
            )
        except Exception as exc:
            raise PartialSessionError(
                cause=exc,
                failed_step="interview",
                partial_session={"pile_sort": pilesort_record.model_dump()},
            ) from exc

        # Use placeholder free list (free lists were in pass 1).
        # The item set for this pile sort was elbow-truncated at elbow_k.
        fl_placeholder, fl_result_placeholder = _placeholder_freelist()

        record = _assemble_record(
            adapter, domain, run_idx,
            fl_placeholder, ps_result,
            pilesort_record, interview_record,
            collection_mode="two_pass",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
            truncation_type="elbow",
            truncation_n=elbow_k,
        )
        pile_sort_records.append(record)

    return stamped_freelist_records + pile_sort_records


async def run_cross_model_sort(
    adapter: ModelAdapter,
    domain: Domain,
    consensus_items: list[str],
    n_pile_sorts: int = 10,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
) -> list[InformantRecord]:
    """Run pile sorts on a cross-model consensus item list.

    This is the CDA cultural consensus method: all models sort the same
    shared item list (derived from pooling all models' free lists),
    making their similarity matrices directly comparable.

    The consensus_items should come from compute_cross_model_consensus()
    + find_salience_elbow() — computed externally so the caller controls
    which records are pooled.

    Returns:
        List of n_pile_sorts InformantRecords with
        collection_mode="cross_model_consensus".
    """
    item_source = "cross_model_consensus"
    records: list[InformantRecord] = []

    for i in range(n_pile_sorts):
        pilesort_record, ps_result = await run_pile_sort(
            adapter,
            items=consensus_items,
            domain_seed=domain.prompt_seed,
            run_index=i,
            prompt_version=prompt_version,
        )
        pilesort_record = pilesort_record.model_copy(
            update={"item_source": item_source},
        )

        interview_record, _ = await run_pile_interview(
            adapter,
            piles=pilesort_record.parsed_piles,
            run_index=i,
            prompt_version=prompt_version,
        )

        fl_placeholder, fl_result_placeholder = _placeholder_freelist()

        record = _assemble_record(
            adapter, domain, i,
            fl_placeholder, ps_result,
            pilesort_record, interview_record,
            collection_mode="cross_model_consensus",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )
        records.append(record)

    return records


async def run_baseline_sort(
    adapter: ModelAdapter,
    domain: Domain,
    items: list[str],
    baseline_id: str,
    n_sorts: int = 10,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
) -> list[InformantRecord]:
    """Run pile sorts on a provided baseline item list.

    The model sorts items from a human baseline (e.g., Romney 1996) to
    enable direct model-to-human structural comparison.

    Returns:
        List of n_sorts InformantRecords with collection_mode="baseline_items".
    """
    item_source = f"baseline:{baseline_id}"
    records: list[InformantRecord] = []

    # Deviation from Architect Amendment A §Stream A brief (2026-04-23):
    # per-iteration handler stops on first failure rather than continuing.
    # Same trade-off as run_two_pass Pass 2 above — verbatim is preserved
    # on failure via PartialSessionError, but the loop does not continue
    # to remaining iterations. Continue-after-failure deferred as a
    # follow-up for Architect ruling. See
    # docs/status/2026-04-23-phase4a-task23-reviewer-verdict.md Note 1.
    for i in range(n_sorts):
        try:
            pilesort_record, ps_result = await run_pile_sort(
                adapter,
                items=items,
                domain_seed=domain.prompt_seed,
                run_index=i,
                prompt_version=prompt_version,
            )
        except PileSortParseError as exc:
            attempts = exc.attempts
            errors = exc.per_attempt_errors
            retry_attempts_bl: list[dict] = [
                {
                    "attempt_index": idx,
                    "response_verbatim": r.text,
                    "thinking_verbatim": r.thinking_text,
                    "stop_reason": r.stop_reason,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "latency_ms": r.latency_ms,
                    "parse_error_message": str(errors[idx]),
                }
                for idx, r in enumerate(attempts[:-1])
            ]
            final = attempts[-1]
            raise PartialSessionError(
                cause=exc,
                failed_step="pile_sort",
                partial_session={},
                prompt_verbatim=exc.prompt_verbatim or None,
                response_verbatim=final.text,
                thinking_verbatim=final.thinking_text,
                stop_reason=final.stop_reason,
                retry_attempts=retry_attempts_bl,
            ) from exc
        except Exception as exc:
            raise PartialSessionError(
                cause=exc,
                failed_step="pile_sort",
                partial_session={},
            ) from exc

        pilesort_record = pilesort_record.model_copy(
            update={"item_source": item_source},
        )

        try:
            interview_record, _ = await run_pile_interview(
                adapter,
                piles=pilesort_record.parsed_piles,
                run_index=i,
                prompt_version=prompt_version,
            )
        except Exception as exc:
            raise PartialSessionError(
                cause=exc,
                failed_step="interview",
                partial_session={"pile_sort": pilesort_record.model_dump()},
            ) from exc

        fl_placeholder, fl_result_placeholder = _placeholder_freelist()

        record = _assemble_record(
            adapter, domain, i,
            fl_placeholder, ps_result,
            pilesort_record, interview_record,
            collection_mode="baseline_items",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )
        records.append(record)

    return records
