"""Collection orchestrator — runs the three-step CDA protocol for a (model, domain) pair.

See ARCHITECTURE.md §4.1.

Milestone A: free-list step only. Pile sort and pile interview are Phase 2.
Placeholder PileSortRecord and InterviewRecord are created with empty/zero values.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime

from cdb_core import Domain, InformantRecord, InterviewRecord, PileSortRecord

from cdb_collect.adapters.base import ModelAdapter
from cdb_collect.manifest import compute_manifest
from cdb_collect.protocol.free_list import run_free_list

logger = logging.getLogger(__name__)


def _informant_id(
    model_id: str, domain_slug: str, run_index: int, collection_date: str,
) -> str:
    """Deterministic informant ID: SHA256[:16] of the identity tuple."""
    key = f"{model_id}|{domain_slug}|{run_index}|{collection_date}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _placeholder_pilesort() -> PileSortRecord:
    """Placeholder PileSortRecord for Milestone A (not yet collected)."""
    return PileSortRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_piles=[],
        parsed_matrix=[],
    )


def _placeholder_interview() -> InterviewRecord:
    """Placeholder InterviewRecord for Milestone A (not yet collected)."""
    return InterviewRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_pile_labels=[],
    )


async def run_informant(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
) -> InformantRecord:
    """Run the CDA protocol and assemble an InformantRecord.

    Milestone A: runs free-list only. Pile sort and interview are placeholders.

    Args:
        adapter: The model adapter to use.
        domain: The domain definition.
        run_index: The 0-based run index.
        prompt_version: Prompt template version.
        system_prompt: System prompt used for all steps.

    Returns:
        A fully populated InformantRecord.
    """
    now = datetime.now()
    collection_date_str = now.strftime("%Y-%m-%dT%H:%M:%S")

    # Step 1: Free listing
    freelist_record, adapter_result = await run_free_list(
        adapter, domain, run_index, prompt_version=prompt_version,
    )

    # Steps 2 & 3: Placeholders for Milestone A
    pilesort_record = _placeholder_pilesort()
    interview_record = _placeholder_interview()

    # Compute SHA256 manifest
    request_params = {
        "model_id": adapter.model.model_id,
        "domain_slug": domain.slug,
        "run_index": run_index,
        "prompt_version": prompt_version,
        "temperature_freelist": 0.7,
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

    return InformantRecord(
        informant_id=informant_id,
        domain_slug=domain.slug,
        run_index=run_index,
        collection_date=now,
        model_id=adapter.model.model_id,
        model_version_returned=adapter_result.model_version_returned,
        family=adapter.model.family,
        provider=adapter.model.provider,
        provider_request_id=adapter_result.provider_request_id,
        knowledge_cutoff=None,
        open_weights=adapter.model.open_weights,
        origin_country=adapter.model.origin,
        alignment_method=None,
        collection_method=adapter.model.collection_method,
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt=system_prompt,
        freelist=freelist_record,
        pile_sort=pilesort_record,
        interview=interview_record,
        sha256_manifest=manifest,
        qa_passed=True,
        qa_notes="",
    )
