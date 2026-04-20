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
from cdb_collect.manifest import compute_manifest
from cdb_collect.protocol.free_list import run_free_list
from cdb_collect.protocol.pile_interview import run_pile_interview
from cdb_collect.protocol.pile_sort import run_pile_sort

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

    qa_notes_value = f"campaign_id={campaign_id}" if campaign_id else ""

    return InformantRecord(
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
        max_tokens=16384,
        system_prompt=system_prompt,
        freelist=freelist_record,
        pile_sort=pilesort_record,
        interview=interview_record,
        sha256_manifest=manifest,
        qa_passed=True,
        qa_notes=qa_notes_value,
    )


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
    freelist_record, freelist_result = await run_free_list(
        adapter, domain, run_index,
        prompt_version=prompt_version,
        temperature=temperature,
    )

    pilesort_record, _ = await run_pile_sort(
        adapter,
        items=freelist_record.parsed_items,
        domain_seed=domain.prompt_seed,
        run_index=run_index,
        prompt_version=prompt_version,
        temperature=temperature,
    )

    interview_record, _ = await run_pile_interview(
        adapter,
        piles=pilesort_record.parsed_piles,
        run_index=run_index,
        prompt_version=prompt_version,
        temperature=temperature,
    )

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

        # Create a free-list-only InformantRecord for provenance
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

    # ── Pass 2: Pile sorts on consensus items ───────────────────────
    for i in range(n_pile_sorts):
        run_idx = n_free_lists + i  # Offset to avoid ID collision

        pilesort_record, ps_result = await run_pile_sort(
            adapter,
            items=consensus_items,
            domain_seed=domain.prompt_seed,
            run_index=run_idx,
            prompt_version=prompt_version,
        )
        # Set item_source on the pile sort record
        pilesort_record = pilesort_record.model_copy(
            update={"item_source": item_source},
        )

        interview_record, _ = await run_pile_interview(
            adapter,
            piles=pilesort_record.parsed_piles,
            run_index=run_idx,
            prompt_version=prompt_version,
        )

        # Use placeholder free list (free lists were in pass 1)
        fl_placeholder, fl_result_placeholder = _placeholder_freelist()

        record = _assemble_record(
            adapter, domain, run_idx,
            fl_placeholder, ps_result,
            pilesort_record, interview_record,
            collection_mode="two_pass",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )
        all_informant_records.append(record)

    return all_informant_records


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

    for i in range(n_sorts):
        pilesort_record, ps_result = await run_pile_sort(
            adapter,
            items=items,
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
            collection_mode="baseline_items",
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )
        records.append(record)

    return records
